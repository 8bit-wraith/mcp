from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import asyncio
from ..core.plugin import PluginManager

app = FastAPI(title="MCP Awesome Tool Collection")
plugin_manager = PluginManager()

@app.on_event("startup")
async def startup_event():
    """Load all tools on startup"""
    await plugin_manager.load_tools()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Execute a specific tool command"""
    result = await plugin_manager.execute_tool(tool_name, command, params)
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