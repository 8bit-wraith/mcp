essential-mcp/
├── packages/
│   ├── mcp-server-enhanced-ssh/    # TypeScript: SSH/Terminal interface
│   ├── mcp-atc/                    # Python: Core API & Tool Collection
│   │   ├── src/
│   │   │   ├── api/               # FastAPI implementation
│   │   │   ├── tools/             # Individual tools
│   │   │   │   ├── tmux_tools.py
│   │   │   │   ├── file_tools.py
│   │   │   │   ├── auth_tools.py
│   │   │   │   └── voice_tools.py
│   │   │   └── core/              # Core functionality
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── mcp-shared/                 # Shared types and utilities 