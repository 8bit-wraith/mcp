# 🚀 MCP Enhanced SSH Server

A powerful SSH server that makes your terminal feel like home, complete with TMUX integration and smart session management.

## Core Features

### 🖥️ Terminal Sessions
- Persistent TMUX sessions
- Multi-window support
- Session sharing capabilities
- Smart session recovery

### 🔐 Authentication
- Key-based auth
- Voice pattern recognition (coming soon)
- Location-based trust factors
- Session persistence

### 🎮 Commands
```bash
# Start a new session
mcp-ssh new "session-name"

# List active sessions
mcp-ssh ls

# Attach to existing session
mcp-ssh attach "session-name"

# Share session with another user
mcp-ssh share "session-name" "user@example.com"

# Create a new window in current session
mcp-ssh window "window-name"
```

### 🔧 Configuration
```json
{
  "port": 8889,
  "tmux": {
    "enabled": true,
    "defaultLayout": "main-vertical",
    "autoRecover": true
  }
}
``` 