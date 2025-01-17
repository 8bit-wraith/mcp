from typing import Dict, Any, List, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import json
from pydantic import BaseModel

class ModelMetadata(BaseModel):
    """Metadata about an embedding model"""
    name: str
    type: str  # embedding, ranking, etc.
    description: str
    dimensions: int
    best_for: List[str]
    version: str

class TestContext(BaseModel):
    """Rich context for a test"""
    test_name: str
    description: str
    related_tools: List[str]
    expected_behavior: str
    participants: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]

class ContextualTestStore:
    """Manages test contexts using Qdrant"""
    
    def __init__(self):
        # Initialize Qdrant client
        self.client = QdrantClient("localhost", port=6333)
        
        # Initialize our default embedding model
        self.default_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Track our models
        self.models: Dict[str, ModelMetadata] = {}
        
        # Ensure collections exist
        self._init_collections()
    
    async def _init_collections(self):
        """Initialize Qdrant collections"""
        # Collection for test contexts
        self.client.recreate_collection(
            collection_name="test_contexts",
            vectors_config=models.VectorParams(
                size=384,  # Default model dimensions
                distance=models.Distance.COSINE
            )
        )
        
        # Collection for model metadata
        self.client.recreate_collection(
            collection_name="model_metadata",
            vectors_config=models.VectorParams(
                size=384,
                distance=models.Distance.COSINE
            )
        )
    
    async def register_model(self, metadata: ModelMetadata):
        """Register a new embedding/ranking model"""
        # Store model metadata
        self.models[metadata.name] = metadata
        
        # Create embedding for model description
        embedding = self.default_model.encode(metadata.description)
        
        # Store in Qdrant
        self.client.upsert(
            collection_name="model_metadata",
            points=[
                models.PointStruct(
                    id=hash(metadata.name),
                    vector=embedding.tolist(),
                    payload=metadata.dict()
                )
            ]
        )
    
    async def store_test_context(self, context: TestContext, model_name: Optional[str] = None):
        """Store a test context with its embedding"""
        # Use specified model or default
        model = self.models.get(model_name) if model_name else None
        embedding_model = self.default_model  # We could switch based on model type
        
        # Create context embedding
        context_text = f"{context.test_name} {context.description} {context.expected_behavior}"
        embedding = embedding_model.encode(context_text)
        
        # Store in Qdrant
        self.client.upsert(
            collection_name="test_contexts",
            points=[
                models.PointStruct(
                    id=hash(f"{context.test_name}_{context.timestamp.isoformat()}"),
                    vector=embedding.tolist(),
                    payload=context.dict()
                )
            ]
        )
    
    async def find_similar_tests(self, query: str, limit: int = 5) -> List[TestContext]:
        """Find similar tests based on semantic similarity"""
        # Create query embedding
        embedding = self.default_model.encode(query)
        
        # Search Qdrant
        results = self.client.search(
            collection_name="test_contexts",
            query_vector=embedding.tolist(),
            limit=limit
        )
        
        # Convert results to TestContext objects
        return [TestContext(**hit.payload) for hit in results]
    
    async def find_related_contexts(self, test_name: str, limit: int = 5) -> List[TestContext]:
        """Find related test contexts"""
        # Get original test context
        original = await self.get_test_context(test_name)
        if not original:
            return []
            
        # Search for similar contexts
        return await self.find_similar_tests(
            f"{original.test_name} {original.description}",
            limit=limit
        ) 