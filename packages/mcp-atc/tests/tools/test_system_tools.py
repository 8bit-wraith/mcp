import pytest
from typing import Dict, Any
from ...src.tools.system_tools import SystemTools

@pytest.fixture
async def system_tool():
    """Create a system tool instance"""
    return SystemTools()

@pytest.mark.asyncio
async def test_system_tool_creation(system_tool, test_participant):
    """Test basic tool creation and session management"""
    # Create a new session
    session_id = "test-session-1"
    context = await system_tool.create_session(session_id, test_participant)
    
    assert context.session_id == session_id
    assert test_participant.id in context.participants
    assert len(context.history) == 0
    assert len(context.feelings) == 0

@pytest.mark.asyncio
async def test_system_status(system_tool, test_participant):
    """Test system status command"""
    session_id = "test-session-2"
    await system_tool.create_session(session_id, test_participant)
    
    result = await system_tool.execute(
        session_id=session_id,
        command="status",
        params={},
        participant_id=test_participant.id
    )
    
    assert result["platform"] is not None
    assert result["python_version"] is not None
    assert result["cpu_count"] > 0
    assert result["memory_total"] > 0
    assert result["context_participants"] == 1

@pytest.mark.asyncio
async def test_resource_monitoring_with_feelings(system_tool, test_participant):
    """Test resource monitoring and contextual feelings"""
    session_id = "test-session-3"
    context = await system_tool.create_session(session_id, test_participant)
    
    # Execute resource monitoring
    await system_tool.execute(
        session_id=session_id,
        command="resources",
        params={},
        participant_id=test_participant.id
    )
    
    # Check if feelings were recorded
    assert len(context.feelings) > 0
    latest_feeling = context.get_participant_mood("system")
    assert latest_feeling is not None
    assert latest_feeling.mood in ["stressed", "relaxed"]
    assert latest_feeling.confidence > 0
    assert isinstance(latest_feeling.insights, list) 