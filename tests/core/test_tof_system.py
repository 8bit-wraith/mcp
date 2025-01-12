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
    return ToFManager()

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

# Tests
@pytest.mark.asyncio
async def test_context_registration(tof_manager: ToFManager, test_context_data: dict):
    """Test if we can register a new context"""
    context = await tof_manager.register_context(
        "test-123",
        test_context_data,
        ContextType.TEST,
        ["sample", "test"]
    )
    assert context.context_id == "test-123"
    assert context.data == test_context_data
    assert context.metadata.context_type == ContextType.TEST
    assert "sample" in context.metadata.tags
    assert "test" in context.metadata.tags

@pytest.mark.asyncio
async def test_test_context_validation(tof_manager: ToFManager, test_context_data: dict):
    """Test if test context validation works"""
    context = await tof_manager.register_context(
        "test-123",
        test_context_data,
        ContextType.TEST
    )
    result = await tof_manager.validate_context(context.context_id)
    assert result.passed is True
    assert context.metadata.last_validated is not None
    assert context.metadata.validation_count == 1

@pytest.mark.asyncio
async def test_tool_context_validation(tof_manager: ToFManager, tool_context_data: dict):
    """Test if tool context validation works"""
    context = await tof_manager.register_context(
        "tool-123",
        tool_context_data,
        ContextType.TOOL
    )
    result = await tof_manager.validate_context(context.context_id)
    assert result.passed is True
    assert context.metadata.validation_count == 1

@pytest.mark.asyncio
async def test_invalid_test_context(tof_manager: ToFManager):
    """Test validation of invalid test context"""
    context = await tof_manager.register_context(
        "test-123",
        {"invalid": "data"},
        ContextType.TEST
    )
    result = await tof_manager.validate_context(context.context_id)
    assert result.passed is False
    assert context.metadata.validation_count == 0

@pytest.mark.asyncio
async def test_context_history(tof_manager: ToFManager, test_context_data: dict):
    """Test if context history is maintained"""
    context = await tof_manager.register_context(
        "test-123",
        test_context_data,
        ContextType.TEST
    )
    
    # Run multiple validations
    await tof_manager.validate_context(context.context_id)
    await tof_manager.validate_context(context.context_id)
    
    history = tof_manager.get_context_history(context.context_id)
    assert len(history) == 2
    assert all(result.passed for result in history)

@pytest.mark.asyncio
async def test_context_recovery(tof_manager: ToFManager, test_context_data: dict):
    """Test if we can recover a context"""
    context = await tof_manager.register_context(
        "test-123",
        test_context_data,
        ContextType.TEST
    )
    
    # First validation should pass
    result = await tof_manager.validate_context(context.context_id)
    assert result.passed is True
    
    # Corrupt the context data
    context.data = {"invalid": "data"}
    result = await tof_manager.validate_context(context.context_id)
    assert result.passed is False
    
    # Try to recover
    recovered = await tof_manager.recover_context(context.context_id)
    assert recovered is not None
    assert recovered.context_id == context.context_id 