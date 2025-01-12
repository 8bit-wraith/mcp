import pytest
from datetime import datetime, timedelta
from ...src.core.tof_manager import ToFManager
from ...src.core.context import ToolContext, Participant

@pytest.fixture
async def tof_manager():
    return ToFManager()

@pytest.fixture
def test_context(test_participant):
    return ToolContext(
        tool_id="test-tool",
        session_id="test-session",
        participants={test_participant.id: test_participant},
        history=[],
        feelings=[],
        shared_state={}
    )

@pytest.mark.asyncio
async def test_context_integrity(tof_manager, test_context):
    """Test context integrity checking"""
    await tof_manager.register_context(test_context)
    results = await tof_manager.run_context_tests(test_context.session_id)
    
    integrity_result = next(r for r in results if r.name == "context_integrity")
    assert integrity_result.passed
    
    # Test with corrupted context
    test_context.tool_id = None  # type: ignore
    results = await tof_manager.run_context_tests(test_context.session_id)
    integrity_result = next(r for r in results if r.name == "context_integrity")
    assert not integrity_result.passed 