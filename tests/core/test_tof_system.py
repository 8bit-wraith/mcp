import pytest
from datetime import datetime
import asyncio
from src.core.tof_system import (
    ToFManager,
    Context,
    ContextType,
    ValidationResult
)

# Fixtures
@pytest.fixture
async def tof_manager():
    return ToFManager(qdrant_host="localhost", qdrant_port=6333)

@pytest.fixture
def test_context_data():
    return {
        "test_name": "sample_test",
        "test_result": "passed",
        "timestamp": datetime.now().isoformat()
    }

@pytest.fixture
def tool_context_data():
    return {
        "tool_name": "sample_tool",
        "tool_state": "ready",
        "last_execution": datetime.now().isoformat()
    }

@pytest.fixture
def memory_context_data():
    return {
        "memory_type": "conversation",
        "content": "Important discussion about AI",
        "timestamp": datetime.now().isoformat(),
        "importance": 0.8
    }

@pytest.fixture
def intention_context_data():
    return {
        "actor": "AI Assistant",
        "intention": "help user with coding",
        "confidence": 0.9,
        "timestamp": datetime.now().isoformat()
    }

@pytest.fixture
def emotion_context_data():
    return {
        "emotion_type": "excitement",
        "intensity": 0.7,
        "trigger": "successful code execution",
        "timestamp": datetime.now().isoformat()
    }

@pytest.fixture
def learning_context_data():
    return {
        "topic": "context management",
        "progress": 0.6,
        "mastery_level": "intermediate",
        "last_update": datetime.now().isoformat()
    }

# Tests
@pytest.mark.asyncio
async def test_context_registration_with_parent(tof_manager: ToFManager, test_context_data: dict):
    """Test if we can register a context with a parent"""
    parent = await tof_manager.register_context(
        "parent-123",
        test_context_data,
        ContextType.TEST
    )
    
    child = await tof_manager.register_context(
        "child-123",
        test_context_data,
        ContextType.TEST,
        parent_id=parent.context_id
    )
    
    assert child.metadata.parent_id == parent.context_id

@pytest.mark.asyncio
async def test_memory_context_validation(tof_manager: ToFManager, memory_context_data: dict):
    """Test if memory context validation works"""
    context = await tof_manager.register_context(
        "memory-123",
        memory_context_data,
        ContextType.MEMORY,
        ["important", "conversation"]
    )
    result = await tof_manager.validate_context(context.context_id)
    assert result.passed is True
    assert context.metadata.validation_count == 1

@pytest.mark.asyncio
async def test_intention_context_validation(tof_manager: ToFManager, intention_context_data: dict):
    """Test if intention context validation works"""
    context = await tof_manager.register_context(
        "intention-123",
        intention_context_data,
        ContextType.INTENTION
    )
    result = await tof_manager.validate_context(context.context_id)
    assert result.passed is True
    assert context.metadata.validation_count == 1

@pytest.mark.asyncio
async def test_emotion_context_validation(tof_manager: ToFManager, emotion_context_data: dict):
    """Test if emotion context validation works"""
    context = await tof_manager.register_context(
        "emotion-123",
        emotion_context_data,
        ContextType.EMOTION
    )
    result = await tof_manager.validate_context(context.context_id)
    assert result.passed is True
    assert context.metadata.validation_count == 1

@pytest.mark.asyncio
async def test_learning_context_validation(tof_manager: ToFManager, learning_context_data: dict):
    """Test if learning context validation works"""
    context = await tof_manager.register_context(
        "learning-123",
        learning_context_data,
        ContextType.LEARNING
    )
    result = await tof_manager.validate_context(context.context_id)
    assert result.passed is True
    assert context.metadata.validation_count == 1

@pytest.mark.asyncio
async def test_context_state_tracking(tof_manager: ToFManager, test_context_data: dict):
    """Test if context state changes are tracked"""
    context = await tof_manager.register_context(
        "test-123",
        test_context_data,
        ContextType.TEST
    )
    
    # First validation should create a state
    await tof_manager.validate_context(context.context_id)
    assert len(context._previous_states) == 1
    assert context.metadata.version == 2
    
    # Modify the context
    context.data["test_result"] = "failed"
    await tof_manager.validate_context(context.context_id)
    assert len(context._previous_states) == 2
    assert context.metadata.version == 3

@pytest.mark.asyncio
async def test_context_recovery_from_state(tof_manager: ToFManager, test_context_data: dict):
    """Test if we can recover context from previous state"""
    context = await tof_manager.register_context(
        "test-123",
        test_context_data,
        ContextType.TEST
    )
    
    # Create a valid state
    await tof_manager.validate_context(context.context_id)
    original_data = context.data.copy()
    
    # Corrupt the context
    context.data = {"invalid": "data"}
    result = await tof_manager.validate_context(context.context_id)
    assert result.passed is False
    
    # Recover
    recovered = await tof_manager.recover_context(context.context_id)
    assert recovered is not None
    assert recovered.data == original_data

@pytest.mark.asyncio
async def test_similar_context_search(tof_manager: ToFManager, test_context_data: dict):
    """Test if we can find similar contexts"""
    # Create original context
    original = await tof_manager.register_context(
        "test-123",
        test_context_data,
        ContextType.TEST,
        ["important"]
    )
    await tof_manager.validate_context(original.context_id)
    
    # Create similar context
    similar_data = test_context_data.copy()
    similar_data["test_name"] = "similar_test"
    similar = await tof_manager.register_context(
        "test-456",
        similar_data,
        ContextType.TEST,
        ["important"]
    )
    
    # Corrupt original and try to recover
    original.data = {"invalid": "data"}
    recovered = await tof_manager.recover_context(original.context_id)
    assert recovered is not None
    assert recovered.data != {"invalid": "data"}

@pytest.mark.asyncio
async def test_context_version_tracking(tof_manager: ToFManager, test_context_data: dict):
    """Test if context versions are tracked correctly"""
    context = await tof_manager.register_context(
        "test-123",
        test_context_data,
        ContextType.TEST
    )
    
    assert context.metadata.version == 1
    
    # Multiple validations should increment version
    await tof_manager.validate_context(context.context_id)
    assert context.metadata.version == 2
    
    await tof_manager.validate_context(context.context_id)
    assert context.metadata.version == 3 