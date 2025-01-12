from typing import List, Dict, Optional, Any
import asyncio
from datetime import datetime
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import json
import logging
from dataclasses import asdict
from .tof_system import Context, ContextType, ValidationResult

logger = logging.getLogger(__name__)

class ContextEncoder:
    """Handles encoding of contexts into vector embeddings"""
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
    
    def encode_context(self, context: Context) -> np.ndarray:
        """Convert context to vector embedding"""
        # Create a rich text representation of the context
        context_text = f"""
        ID: {context.context_id}
        Type: {context.metadata.context_type.value}
        Tags: {','.join(context.metadata.tags)}
        Data: {json.dumps(context.data)}
        """
        return self.model.encode(context_text)

class ContextStore:
    """Manages context storage and similarity search using Qdrant"""
    def __init__(
        self,
        collection_name: str = "contexts",
        host: str = "localhost",
        port: int = 6333
    ):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.encoder = ContextEncoder()
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the Qdrant collection exists"""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # Size of the MiniLM model embeddings
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
    
    async def store_context(self, context: Context):
        """Store a context in Qdrant"""
        # Convert context to vector
        vector = self.encoder.encode_context(context)
        
        # Store metadata
        payload = {
            "context_id": context.context_id,
            "type": context.metadata.context_type.value,
            "tags": context.metadata.tags,
            "created_at": context.metadata.created_at.isoformat(),
            "last_validated": context.metadata.last_validated.isoformat() if context.metadata.last_validated else None,
            "validation_count": context.metadata.validation_count,
            "data": context.data
        }
        
        # Store in Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[models.PointStruct(
                id=hash(context.context_id),  # Use hash as Qdrant requires numeric IDs
                vector=vector.tolist(),
                payload=payload
            )]
        )
        logger.info(f"Stored context in Qdrant: {context.context_id}")
    
    async def find_similar_contexts(
        self,
        context: Context,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find similar contexts based on vector similarity"""
        vector = self.encoder.encode_context(context)
        
        # Search in Qdrant
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector.tolist(),
            limit=limit,
            score_threshold=score_threshold
        )
        
        return [
            {
                "context_id": r.payload["context_id"],
                "similarity": r.score,
                "type": r.payload["type"],
                "data": r.payload["data"]
            }
            for r in results
        ]
    
    async def get_context_by_id(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a context by its ID"""
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="context_id",
                        match=models.MatchValue(value=context_id)
                    )
                ]
            ),
            limit=1
        )[0]
        
        if not results:
            return None
            
        return results[0].payload
    
    async def find_contexts_by_type(
        self,
        context_type: ContextType,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find contexts by type"""
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="type",
                        match=models.MatchValue(value=context_type.value)
                    )
                ]
            ),
            limit=limit
        )[0]
        
        return [r.payload for r in results]
    
    async def find_contexts_by_tags(
        self,
        tags: List[str],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find contexts by tags"""
        results = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="tags",
                        match=models.MatchAny(any=tags)
                    )
                ]
            ),
            limit=limit
        )[0]
        
        return [r.payload for r in results] 