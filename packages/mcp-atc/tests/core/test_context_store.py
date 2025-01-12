import pytest
from datetime import datetime
from ...src.core.test_context_store import (
    ContextualTestStore,
    TestContext,
    ModelMetadata
)

@pytest.fixture
async def context_store():
    store = ContextualTestStore()
    # Register test models
    await store.register_model(ModelMetadata(
        name="test-model",
        type="embedding",
        description="Test embedding model for context analysis",
        dimensions=384,
        best_for=["test_similarity", "context_matching"],
        version="1.0.0"
    ))
    return store

@pytest.mark.asyncio
async def test_context_storage_and_retrieval(context_store):
    """Test storing and retrieving test contexts"""
    # Create a test context
    test_context = TestContext(
        test_name="test_example",
        description="Testing basic functionality",
        related_tools=["tool1"],
        expected_behavior="Should pass without errors",
        participants=["user1"],
        timestamp=datetime.now(),
        metadata={}
    )
    
    # Store it
    await context_store.store_test_context(test_context)
    
    # Find similar tests
    similar = await context_store.find_similar_tests(
        "basic functionality test"
    )
    
    assert len(similar) > 0
    assert similar[0].test_name == "test_example" 