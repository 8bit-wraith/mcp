from fastapi import FastAPI, WebSocket, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import asyncio
from sse_starlette.sse import EventSourceResponse
from datetime import datetime

from ..core.plugin_manager import PluginManager

app = FastAPI(title="MCP Awesome Tool Collection")
plugin_manager = PluginManager()

@app.on_event("startup")
async def startup_event():
    """Load all tools on startup"""
    await plugin_manager.load_tools()

# Enable CORS with specific origins for SSE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event store for SSE
event_subscribers: Dict[str, asyncio.Queue] = {}

async def event_generator(request: Request, client_id: str):
    """Generate events for SSE streaming"""
    if client_id not in event_subscribers:
        event_subscribers[client_id] = asyncio.Queue()
    
    try:
        while True:
            if await request.is_disconnected():
                break
                
            # Get message from queue
            message = await event_subscribers[client_id].get()
            
            # Yield message in SSE format
            yield {
                "event": "message",
                "data": message,
                "id": datetime.now().isoformat()
            }
    except asyncio.CancelledError:
        pass
    finally:
        # Cleanup when client disconnects
        if client_id in event_subscribers:
            del event_subscribers[client_id]

@app.get("/events/{client_id}")
async def sse_endpoint(request: Request, client_id: str):
    """SSE endpoint for real-time updates"""
    event_source = EventSourceResponse(
        event_generator(request, client_id),
        ping=20000  # Send ping every 20 seconds to keep connection alive
    )
    return event_source

async def broadcast_event(event_data: Dict[str, Any], target_client: str = None):
    """Broadcast event to all or specific client"""
    if target_client and target_client in event_subscribers:
        await event_subscribers[target_client].put(event_data)
    else:
        for queue in event_subscribers.values():
            await queue.put(event_data)

# WebSocket connection store
websocket_connections: Dict[str, WebSocket] = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = f"session_{len(websocket_connections)}"
    websocket_connections[session_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_json()
            # Echo back the received data for now
            await websocket.send_json({"status": "ok", "data": data})
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if session_id in websocket_connections:
            del websocket_connections[session_id]

# Active sessions store
sessions: Dict[str, Any] = {}

@app.websocket("/ws/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    # Register the session
    sessions[session_id] = {
        "websocket": websocket,
        "tmux_session": None,
        "tools": {}
    }
    
    try:
        while True:
            data = await websocket.receive_json()
            # Handle different command types
            if data["type"] == "tool":
                result = await handle_tool_command(session_id, data["tool"], data["params"])
                await websocket.send_json(result)
            elif data["type"] == "tmux":
                result = await handle_tmux_command(session_id, data["command"])
                await websocket.send_json(result)
    finally:
        del sessions[session_id]

@app.post("/tool/{tool_name}/{command}")
async def execute_tool(tool_name: str, command: str, params: Dict[str, Any]):
    """Execute a specific tool command and broadcast result via SSE"""
    result = await plugin_manager.execute_tool(tool_name, command, params)
    
    # Broadcast tool execution result to all clients
    await broadcast_event({
        "type": "tool_execution",
        "tool": tool_name,
        "command": command,
        "result": result
    })
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/tools")
async def list_tools():
    """List all available tools with their commands"""
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in plugin_manager.tools.values()
        ]
    } 