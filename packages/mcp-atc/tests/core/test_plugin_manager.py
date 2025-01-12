import pytest
from ...src.core.plugin import PluginManager

@pytest.mark.asyncio
async def test_plugin_loading():
    """Test plugin manager loads tools correctly"""
    manager = PluginManager()
    await manager.load_tools()
    
    # Check if our tools were loaded
    assert "system" in manager.tools
    assert "file" in manager.tools
    
    # Verify tool properties
    system_tool = manager.tools["system"]
    assert system_tool.name == "system"
    assert system_tool.description is not None
    assert system_tool.tool_id is not None

@pytest.mark.asyncio
async def test_tool_execution(plugin_manager, test_participant):
    """Test executing tools through plugin manager"""
    # Try to execute a system status command
    result = await plugin_manager.execute_tool(
        "system",
        "status",
        {},
        "test-session",
        test_participant.id
    )
    
    assert result["status"] == "success"
    assert "platform" in result["result"] 