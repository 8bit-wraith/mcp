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
    """Manages context storage and retrieval using Qdrant vector database.
    
    This class provides a high-level interface for storing and retrieving contexts
    using vector embeddings for similarity search. It uses the Qdrant vector database
    for efficient storage and retrieval of context data.
    
    Attributes:
        collection_name (str): Name of the Qdrant collection for contexts
        client (QdrantClient): Client instance for Qdrant operations
        encoder (SentenceTransformer): Model for encoding contexts into vectors
        
    Example:
        ```python
        # Initialize context store
        store = ContextStore(host="localhost", port=6333)
        
        # Store a context
        context = Context(
            context_id="test-1",
            data={"test_name": "auth_test"},
            context_type=ContextType.TEST
        )
        await store.store_context(context)
        
        # Find similar contexts
        similar = await store.find_similar_contexts(context)
        ```
    """
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        """Initialize the context store with Qdrant connection.
        
        Args:
            host (str): Hostname of the Qdrant server. Defaults to "localhost".
            port (int): Port number of the Qdrant server. Defaults to 6333.
            
        Note:
            The initialization process includes:
            1. Establishing connection to Qdrant
            2. Loading the sentence transformer model
            3. Ensuring the required collection exists
        """
        self.collection_name = "contexts"
        self.client = QdrantClient(host=host, port=port)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Ensure the contexts collection exists in Qdrant.
        
        Creates a new collection if it doesn't exist with appropriate vector configuration
        for the sentence transformer model being used.
        
        Note:
            Collection configuration includes:
            - Vector size: 384 (matches encoder model dimensions)
            - Distance metric: Cosine similarity
        """
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
        """Encode a context into a vector embedding using the sentence transformer.
        
        Args:
            context (Context): The context object to encode
            
        Returns:
            np.ndarray: Vector embedding of the context
            
        Note:
            The encoding process combines:
            1. Context type
            2. Tags
            3. Data content
            Into a single text representation before encoding
        """
        # Convert context data to string representation
        text = f"{context.metadata.context_type.value} "
        text += f"{' '.join(context.metadata.tags)} "
        text += f"{str(context.data)}"
        
        # Get vector embedding
        vector = self.encoder.encode(text)
        return vector
    
    async def store_context(self, context: Context):
        """Store a context in Qdrant with its vector embedding.
        
        Args:
            context (Context): The context object to store
            
        Raises:
            Exception: If there's an error during encoding or storage
            
        Note:
            The storage process:
            1. Encodes the context into a vector
            2. Prepares payload with metadata
            3. Upserts into Qdrant collection
            
        Example:
            ```python
            context = Context(
                context_id="test-1",
                data={"result": "passed"},
                context_type=ContextType.TEST
            )
            await store.store_context(context)
            ```
        """
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
        """Find contexts similar to the given one using vector similarity.
        
        Args:
            context (Context): The context to find similar matches for
            limit (int): Maximum number of results to return. Defaults to 5.
            score_threshold (float): Minimum similarity score (0-1). Defaults to 0.7.
            
        Returns:
            List[Dict[str, Any]]: List of similar contexts with their metadata
            
        Note:
            Similarity is computed using cosine similarity between vector embeddings.
            Higher score_threshold means more similar results.
            
        Example:
            ```python
            similar = await store.find_similar_contexts(
                context,
                limit=10,
                score_threshold=0.8
            )
            ```
        """
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
        """Retrieve a specific context by its unique identifier.
        
        Args:
            context_id (str): Unique identifier of the context
            
        Returns:
            Optional[Dict[str, Any]]: Context data if found, None otherwise
            
        Example:
            ```python
            context = await store.get_context_by_id("test-1")
            if context:
                print(f"Found context: {context['data']}")
            ```
        """
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
        """Find all contexts of a specific type.
        
        Args:
            context_type (ContextType): Type of contexts to find
            limit (int): Maximum number of results. Defaults to 100.
            
        Returns:
            List[Dict[str, Any]]: List of matching contexts with their metadata
            
        Example:
            ```python
            test_contexts = await store.find_contexts_by_type(
                ContextType.TEST,
                limit=50
            )
            for ctx in test_contexts:
                print(f"Found test context: {ctx['data']}")
            ```
        """
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