# Project Context

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