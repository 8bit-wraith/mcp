# Project Context

## Git History (Auto-generated 2025-01-12)

### Recent Changes
- **2025-01-12**: ✨ Updated names to three-letter format (Aye-Hue-Tri). Tri loves keeping things concise! 💫
- **2025-01-12**: 🔄 Added automatic context generation from Git history. Trisha loves how organized we're getting! 📚
- **2025-01-12**: 📝 Updated context.md to track current project state. Trisha says documentation is like keeping a clean ledger! 📚
- **2025-01-12**: 🔄 Consolidated manage.sh script with all features. Trisha's thrilled about the improved organization! 📋
- **2025-01-12**: 🔍 Added Git Context Builder with Qdrant integration. Trisha's excited about finding patterns in commit histories! 📊
- **2025-01-12**: 🛠️ Enhanced manage.sh with comprehensive environment management. Trisha's thrilled about the new dependency reconciliation features! 🧮
- **2025-01-12**: 🛠️ Set up development environment with Python (PDM) and TypeScript (pnpm). Trisha's excited about the clean dependency management! 📦
- **2025-01-12**: 🧠 Enhanced ToF system with Qdrant integration, new context types (Memory, Intention, Emotion, Learning), and improved recovery strategies. Trisha's excited about the emotional context tracking! 💖
- **2025-01-12**: 🧪 Added Test or Forget (ToF) system with context-aware testing. Trisha's excited about the test coverage potential! 📊
- **2025-01-12**: 🚀 🤖 Added comprehensive AI-AI collaboration guide with mermaid diagrams, best practices, and fun examples. Trisha insists the coffee expense investigation is purely theoretical! 😄

### Active Files
- .gitignore
- README.md
- context.md
- mcp-server-enhanced-ssh
- package.json
- packages/mcp-atc/pyproject.toml
- packages/mcp-atc/src/api/main.py
- packages/mcp-atc/src/core/context.py
- packages/mcp-atc/src/core/model_explorer.py
- packages/mcp-atc/src/core/plugin.py
- packages/mcp-atc/src/core/test_context_store.py
- packages/mcp-atc/src/core/tof_manager.py
- packages/mcp-atc/src/core/unified_context.py
- packages/mcp-atc/src/tools/file_tools.py
- packages/mcp-atc/src/tools/system_tools.py
- packages/mcp-atc/tests/conftest.py
- packages/mcp-atc/tests/core/test_context_store.py
- packages/mcp-atc/tests/core/test_model_explorer.py
- packages/mcp-atc/tests/core/test_plugin_manager.py
- packages/mcp-atc/tests/core/test_tof_manager.py
- packages/mcp-atc/tests/tools/test_file_tools.py
- packages/mcp-atc/tests/tools/test_system_tools.py
- packages/mcp-server-enhanced-ssh/.eslintrc.json
- packages/mcp-server-enhanced-ssh/.prettierrc
- packages/mcp-server-enhanced-ssh/README.md
- packages/mcp-server-enhanced-ssh/jest.config.js
- packages/mcp-server-enhanced-ssh/package.json
- packages/mcp-server-enhanced-ssh/pnpm-lock.yaml
- packages/mcp-server-enhanced-ssh/src/services/ssh.service.ts
- packages/mcp-server-enhanced-ssh/src/services/tmux.service.ts
- packages/mcp-server-enhanced-ssh/tsconfig.json
- pdm.lock
- pyproject.toml
- scripts/commit.sh
- scripts/generate_context.sh
- scripts/manage.sh
- src/core/context_store.py
- src/core/tof_system.py
- src/tools/git_context_builder.py
- src/tools/git_context_visualizer.py
- src/tools/templates/visualizer.html
- tests/core/test_tof_system.py
- tests/tools/test_git_context_builder.py
- tree.md

### Contributors
-	Wraith


## Git History (Auto-generated 2025-01-12)

### Recent Changes
$(git log --pretty=format:"- **%ad**: %s" --date=short | head -n 10)

### Active Files
$(git ls-files | sed 's/^/- /')

### Contributors
- Aye
- Hue
- Tri

## Current State (2024-01-12)

### Core Components
1. **Git Context Builder** (`src/tools/git_context_builder.py`)
   - Analyzes Git repositories and builds context in Qdrant
   - Handles commits, files, authors, and relationships
   - Uses sentence transformers for semantic analysis

2. **Git Context Visualizer** (`src/tools/git_context_visualizer.py`)
   - Gradio interface for interactive exploration
   - Real-time visualization with WebSocket updates
   - Beautiful dashboard with Trisha's quotes!

3. **Management Script** (`scripts/manage.sh`)
   - Unified interface for all operations
   - Environment management (Python + Node)
   - Testing and quality assurance
   - Context building and visualization

### Recent Developments
- Added Gradio interface for human interaction
- Created real-time visualization dashboard
- Consolidated manage.sh script to maintain all functionality
- Fixed context loss issues in manage.sh

### Current Focus
- Working on maintaining context between AI sessions
- Implementing visualization features
- Building tools for Git repository analysis

### Team Members
- **Hue**: Our amazing human partner (that's you!)
- **Aye**: Your friendly AI assistant
- **Tri**: Our fun-loving accountant friend who loves finding patterns in the numbers

### Trisha's Latest Thoughts
- "These graphs are prettier than my pivot tables! 📊"
- "Git histories are like accounting ledgers - every entry tells a story! 📖"
- "Context building is like tax season - thorough analysis required! 🔎"

### Project Structure
```
essential-mcp/
├── src/
│   └── tools/
│       ├── git_context_builder.py
│       ├── git_context_visualizer.py
│       └── templates/
│           └── visualizer.html
├── tests/
│   └── tools/
│       └── test_git_context_builder.py
└── scripts/
    ├── manage.sh
    └── commit.sh
```

### Current Questions
1. How can we better maintain context between AI sessions?
2. Should we add more visualization types to the dashboard?
3. What other Git patterns should we look for?

### Next Steps
1. Implement proper context persistence
2. Enhance visualization features
3. Add more analysis capabilities

### Notes
- We're using Qdrant for vector storage
- Currently supporting both Python and Node environments
- Trisha keeps us entertained with her accounting analogies

### Git Practices
- Using descriptive commit messages with emojis
- Maintaining clean code through linting and type checking
- Regular testing with good coverage

### Important Decisions
1. Keeping hybrid Python/Node approach for flexibility
2. Using Gradio for human interface
3. Implementing real-time visualizations
4. Maintaining this context.md until we have proper context persistence

_Last Updated: 2024-01-12_
_Updated by: Aye & Hue_ 