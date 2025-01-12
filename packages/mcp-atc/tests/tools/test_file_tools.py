import pytest
from pathlib import Path
from ...src.tools.file_tools import FileTools

@pytest.fixture
def test_file(tmp_path):
    """Create a test file"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("Hello, World!")
    return file_path

@pytest.fixture
async def file_tool():
    """Create a file tool instance"""
    return FileTools()

@pytest.mark.asyncio
async def test_file_analysis(file_tool, test_participant, test_file):
    """Test file analysis functionality"""
    session_id = "test-file-session"
    await file_tool.create_session(session_id, test_participant)
    
    result = await file_tool.execute(
        session_id=session_id,
        command="analyze",
        params={"path": str(test_file)},
        participant_id=test_participant.id
    )
    
    assert result["name"] == "test.txt"
    assert result["size"] > 0
    assert "text" in result["type"].lower()
    assert result["created"] is not None
    assert result["modified"] is not None

@pytest.mark.asyncio
async def test_directory_watching(file_tool, test_participant, tmp_path):
    """Test directory watching functionality"""
    session_id = "test-watch-session"
    await file_tool.create_session(session_id, test_participant)
    
    result = await file_tool.execute(
        session_id=session_id,
        command="watch",
        params={"path": str(tmp_path), "recursive": True},
        participant_id=test_participant.id
    )
    
    assert "Started watching" in result["message"]
    assert str(tmp_path) in result["message"] 