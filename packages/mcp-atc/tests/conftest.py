import pytest
import asyncio
from typing import Dict, Any
from pathlib import Path
import shutil
from ..src.core.context import Participant
from ..src.core.plugin import PluginManager

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def clean_test_data():
    """Clean up test data before and after tests"""
    test_data_dir = Path("data/contexts")
    if test_data_dir.exists():
        shutil.rmtree(test_data_dir)
    test_data_dir.mkdir(parents=True, exist_ok=True)
    yield
    shutil.rmtree(test_data_dir)

@pytest.fixture
async def plugin_manager():
    """Create a plugin manager instance"""
    manager = PluginManager()
    await manager.load_tools()
    return manager

@pytest.fixture
def test_participant():
    """Create a test participant"""
    return Participant(
        id="test-user-1",
        name="Test User",
        type="human",
        personality={
            "style": "technical",
            "humor": "high"
        }
    ) 