#!/usr/bin/env python3

"""
Test configuration and fixtures.
Tri says: Good tests are like good accounting - everything needs to balance! ⚖️
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import our test fixtures
import pytest
from typing import Dict, Any

@pytest.fixture
def mock_context_data() -> Dict[str, Any]:
    """Provide mock context data for tests"""
    return {
        "test_name": "example_test",
        "test_result": "passed",
        "timestamp": "2025-01-12T12:00:00Z"
    }

@pytest.fixture
def mock_tool_data() -> Dict[str, Any]:
    """Provide mock tool context data"""
    return {
        "tool_name": "example_tool",
        "tool_state": "ready",
        "last_execution": "2025-01-12T12:00:00Z"
    } 