#!/usr/bin/env python3

"""
Context storage management using Qdrant.
Tri says: Good storage is like a well-organized filing cabinet! 📁
"""

import logging
from typing import Dict, List, Optional, Any
import numpy as np
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from .types import Context, ContextType

logger = logging.getLogger(__name__)

class ContextStore:
    """Manages context storage and retrieval using Qdrant"""
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        """Initialize the context store"""
        self.collection_name = "contexts"
        self.client = QdrantClient(host=host, port=port)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the contexts collection exists"""
        collections = self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # Dimension of the encoder model
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
    
    def _encode_context(self, context: Context) -> np.ndarray:
        """Encode a context into a vector embedding"""
        # Convert context data to string representation
        text = f"{context.metadata.context_type.value} "
        text += f"{' '.join(context.metadata.tags)} "
        text += f"{str(context.data)}"
        
        # Get vector embedding
        vector = self.encoder.encode(text)
        return vector
    
    async def store_context(self, context: Context):
        """Store a context in Qdrant"""
        try:
            vector = self._encode_context(context)
            
            # Prepare payload
            payload = {
                "context_id": context.context_id,
                "context_type": context.metadata.context_type.value,
                "tags": context.metadata.tags,
                "data": context.data,
                "version": context.metadata.version,
                "created_at": context.metadata.created_at.isoformat(),
                "last_validated": context.metadata.last_validated.isoformat() if context.metadata.last_validated else None
            }
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=hash(context.context_id),
                        vector=vector.tolist(),
                        payload=payload
                    )
                ]
            )
            logger.debug(f"Stored context: {context.context_id}")
            
        except Exception as e:
            logger.error(f"Error storing context {context.context_id}: {str(e)}")
            raise
    
    async def find_similar_contexts(
        self,
        context: Context,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find contexts similar to the given one"""
        try:
            vector = self._encode_context(context)
            
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector.tolist(),
                limit=limit,
                score_threshold=score_threshold
            )
            
            return [point.payload for point in results]
            
        except Exception as e:
            logger.error(f"Error finding similar contexts: {str(e)}")
            return []
    
    async def get_context_by_id(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a context by its ID"""
        try:
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
            
            if results:
                return results[0].payload
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving context {context_id}: {str(e)}")
            return None
    
    async def find_contexts_by_type(
        self,
        context_type: ContextType,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find contexts by type"""
        try:
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="context_type",
                            match=models.MatchValue(value=context_type.value)
                        )
                    ]
                ),
                limit=limit
            )[0]
            
            return [point.payload for point in results]
            
        except Exception as e:
            logger.error(f"Error finding contexts by type: {str(e)}")
            return []
    
    async def find_contexts_by_tags(
        self,
        tags: List[str],
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Find contexts by tags"""
        try:
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
            
            return [point.payload for point in results]
            
        except Exception as e:
            logger.error(f"Error finding contexts by tags: {str(e)}")
            return []