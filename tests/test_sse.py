import pytest
from fastapi.testclient import TestClient
from mcp_atc.api.main import app
import asyncio
import json
from datetime import datetime, timedelta

client = TestClient(app)

def test_sse_connection():
    """Test SSE connection establishment"""
    with client.websocket_connect("/ws") as websocket:
        data = {"type": "connection_test"}
        websocket.send_json(data)
        response = websocket.receive_json()
        assert response["status"] == "ok"

@pytest.mark.asyncio
async def test_sse_events():
    """Test SSE event broadcasting"""
    # Create test event data
    test_event = {
        "type": "test_event",
        "data": "Hello SSE!",
        "timestamp": datetime.now().isoformat()
    }
    
    # Connect to SSE endpoint
    with client.get("/events/test_client", stream=True) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        
        # Broadcast test event
        await app.broadcast_event(test_event, "test_client")
        
        # Read SSE response
        for line in response.iter_lines():
            if line:
                if line.startswith(b"data: "):
                    event_data = json.loads(line.decode("utf-8").replace("data: ", ""))
                    assert event_data["type"] == "test_event"
                    assert event_data["data"] == "Hello SSE!"
                    break

@pytest.mark.asyncio
async def test_tool_execution_sse():
    """Test tool execution with SSE updates"""
    test_params = {
        "param1": "value1",
        "param2": "value2"
    }
    
    # Connect to SSE endpoint
    with client.get("/events/test_client", stream=True) as sse_response:
        assert sse_response.status_code == 200
        
        # Execute tool
        tool_response = client.post(
            "/tool/test_tool/test_command",
            json=test_params
        )
        assert tool_response.status_code == 200
        
        # Verify SSE event
        for line in sse_response.iter_lines():
            if line:
                if line.startswith(b"data: "):
                    event_data = json.loads(line.decode("utf-8").replace("data: ", ""))
                    assert event_data["type"] == "tool_execution"
                    assert event_data["tool"] == "test_tool"
                    assert event_data["command"] == "test_command"
                    break

@pytest.mark.asyncio
async def test_sse_cleanup():
    """Test SSE connection cleanup"""
    # Connect first client
    with client.get("/events/client1", stream=True) as response1:
        assert response1.status_code == 200
        assert "client1" in app.event_subscribers
        
        # Connect second client
        with client.get("/events/client2", stream=True) as response2:
            assert response2.status_code == 200
            assert "client2" in app.event_subscribers
        
        # Wait a bit and verify client2 was cleaned up
        await asyncio.sleep(0.1)
        assert "client2" not in app.event_subscribers
    
    # Wait a bit and verify client1 was cleaned up
    await asyncio.sleep(0.1)
    assert "client1" not in app.event_subscribers 