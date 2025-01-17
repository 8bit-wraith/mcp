from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import torch
from pydantic import BaseModel, Field
from enum import Enum
import json
import hashlib
from .model_explorer import AutoModelSelector

class ContextType(str, Enum):
    TEST = "test"
    TOOL = "tool"
    PARTICIPANT = "participant"
    FEELING = "feeling"
    CONVERSATION = "conversation"
    SYSTEM = "system"

class EmbeddingModel(BaseModel):
    """Metadata about an embedding model"""
    name: str
    type: str
    description: str
    dimensions: int
    best_for: List[ContextType]
    version: str
    model_path: str
    
    class Config:
        use_enum_values = True

class UnifiedContext(BaseModel):
    """Base model for all context types"""
    context_id: str
    context_type: ContextType
    timestamp: datetime
    content: Dict[str, Any]
    relationships: List[str] = Field(default_factory=list)  # Other context IDs this is related to
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding_model: str  # Name of the model used for embedding

class ContextManager:
    """Unified context management system"""
    
    def __init__(self, qdrant_url: str = "localhost", qdrant_port: int = 6333):
        self.client = QdrantClient(qdrant_url, port=qdrant_port)
        self.models: Dict[str, EmbeddingModel] = {}
        self.embedding_cache: Dict[str, torch.Tensor] = {}
        self.model_selector = AutoModelSelector()
        
        # Initialize with default models
        self._init_default_models()
        self._init_collections()
    
    def _init_default_models(self):
        """Initialize default embedding models for different context types"""
        default_models = [
            EmbeddingModel(
                name="general-context",
                type="embedding",
                description="General purpose context embedding",
                dimensions=384,
                best_for=[ContextType.TOOL, ContextType.SYSTEM],
                version="1.0.0",
                model_path="all-MiniLM-L6-v2"
            ),
            EmbeddingModel(
                name="sentiment-context",
                type="embedding",
                description="Emotion and sentiment aware embeddings",
                dimensions=768,
                best_for=[ContextType.FEELING, ContextType.PARTICIPANT],
                version="1.0.0",
                model_path="sentence-transformers/all-mpnet-base-v2"
            ),
            EmbeddingModel(
                name="test-context",
                type="embedding",
                description="Test specific context embeddings",
                dimensions=384,
                best_for=[ContextType.TEST],
                version="1.0.0",
                model_path="all-MiniLM-L6-v2"
            )
        ]
        
        for model in default_models:
            self.register_model(model)
    
    def _init_collections(self):
        """Initialize Qdrant collections for different context types"""
        # Main context collection with different vector sizes
        self.client.recreate_collection(
            collection_name="unified_contexts",
            vectors_config={
                "general": models.VectorParams(size=384, distance=models.Distance.COSINE),
                "sentiment": models.VectorParams(size=768, distance=models.Distance.COSINE),
                "test": models.VectorParams(size=384, distance=models.Distance.COSINE)
            }
        )
    
    def register_model(self, model: EmbeddingModel):
        """Register a new embedding model"""
        self.models[model.name] = model
        self.embedding_cache[model.name] = SentenceTransformer(model.model_path)
    
    def _get_best_model(self, context_type: ContextType) -> EmbeddingModel:
        """Get the best model for a context type"""
        for model in self.models.values():
            if context_type in model.best_for:
                return model
        return self.models["general-context"]  # Fallback to general model
    
    def _create_embedding(self, text: str, model_name: str) -> torch.Tensor:
        """Create embedding using specified model"""
        model = self.embedding_cache[model_name]
        return model.encode(text, convert_to_tensor=True)
    
    async def store_context(self, context: UnifiedContext):
        """Store a context with appropriate embeddings"""
        # Get the appropriate model
        model = self._get_best_model(context.context_type)
        context.embedding_model = model.name
        
        # Create context text based on type
        if context.context_type == ContextType.TEST:
            context_text = f"{context.content.get('name', '')} {context.content.get('description', '')} {context.content.get('expected_behavior', '')}"
        elif context.context_type == ContextType.FEELING:
            context_text = f"{context.content.get('mood', '')} {' '.join(context.content.get('insights', []))}"
        else:
            context_text = json.dumps(context.content)
        
        # Create embedding
        embedding = self._create_embedding(context_text, model.name)
        
        # Store in Qdrant
        self.client.upsert(
            collection_name="unified_contexts",
            points=[
                models.PointStruct(
                    id=hash(context.context_id),
                    vector={model.type: embedding.tolist()},
                    payload=context.dict()
                )
            ]
        )
    
    async def find_similar_contexts(
        self,
        query: str,
        context_type: Optional[ContextType] = None,
        limit: int = 5
    ) -> List[UnifiedContext]:
        """Find similar contexts based on semantic similarity"""
        # Determine which model to use
        model = self._get_best_model(context_type) if context_type else self.models["general-context"]
        
        # Create query embedding
        embedding = self._create_embedding(query, model.name)
        
        # Search Qdrant
        results = self.client.search(
            collection_name="unified_contexts",
            query_vector={model.type: embedding.tolist()},
            limit=limit,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="context_type",
                        match=models.MatchValue(value=context_type.value)
                    )
                ]
            ) if context_type else None
        )
        
        return [UnifiedContext(**hit.payload) for hit in results]
    
    async def get_related_contexts(
        self,
        context_id: str,
        limit: int = 5
    ) -> List[UnifiedContext]:
        """Get contexts related to a specific context"""
        # First get the original context
        original = await self.get_context(context_id)
        if not original:
            return []
        
        # Get related contexts by ID
        related = []
        for related_id in original.relationships:
            related_context = await self.get_context(related_id)
            if related_context:
                related.append(related_context)
        
        # Also find semantically similar contexts
        similar = await self.find_similar_contexts(
            json.dumps(original.content),
            context_type=original.context_type,
            limit=limit - len(related)
        )
        
        return related + similar 
    
    async def discover_new_models(self):
        """Discover and evaluate new models for all context types"""
        for context_type in ContextType:
            try:
                model = await self.model_selector.select_optimal_model(context_type)
                print(f"Found optimal model for {context_type}: {model.model_path}")
                self.register_model(model)
            except Exception as e:
                print(f"Error finding model for {context_type}: {str(e)}") 