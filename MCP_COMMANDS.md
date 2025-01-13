# 🎮 MCP Commands Reference

## 🌟 Overview

This document provides a comprehensive guide to the Model Context Protocol (MCP) commands available in this project. The MCP system consists of several integrated components:

1. Enhanced SSH Server (Terminal Management)
2. Awesome Tool Collection (ATC) Server (Tool & Context Management)
3. Context Store (Qdrant-based Knowledge Management)
4. Test or Forget (ToF) System (Context Validation)
5. Model Explorer (AI Model Management)

## 📡 Enhanced SSH Server

### Terminal Commands
The SSH server provides advanced terminal session management through WebSocket connections and Tmux integration.

```typescript
// Connect to terminal session
{
  "type": "terminal",
  "data": "<command string>"
}

// Create new tmux window
{
  "type": "tmux",
  "command": "new-window",
  "name": "window-name"
}
```

### Tmux Integration
```typescript
// Create new session
tmux.createSession("session-name");

// List active sessions
tmux.listSessions();

// Create new window
tmux.createWindow("session-id", "window-name");

// Attach to session
tmux.attachToSession("session-id");
```

## 🧠 Context Management

### Context Types
The system supports various context types, each with specific validation rules:

1. TEST: Test execution contexts
   ```python
   {
     "test_name": "auth_test",
     "test_result": "passed"
   }
   ```

2. TOOL: Tool execution contexts
   ```python
   {
     "tool_name": "git_analyzer",
     "tool_state": "running"
   }
   ```

3. MEMORY: Long-term storage contexts
4. INTENTION: Goal and planning contexts
5. EMOTION: Sentiment analysis contexts
6. LEARNING: Training and adaptation contexts
7. SYSTEM: System state contexts

### Context Store Operations
```python
# Store new context
await context_store.store_context(context)

# Find similar contexts
results = await context_store.find_similar_contexts(context)

# Find by type
contexts = await context_store.find_contexts_by_type(ContextType.TEST)

# Find by tags
contexts = await context_store.find_contexts_by_tags(["git", "analysis"])
```

## 🤖 Model Management

### Model Explorer
```python
# Discover models for context type
models = await explorer.discover_models(ContextType.TEST)

# Evaluate model performance
metrics = await explorer.evaluate_model("model-id", ContextType.TEST)

# Auto-select optimal model
model = await selector.select_optimal_model(ContextType.TEST)
```

### Model Metrics
- Accuracy
- Latency (ms)
- Memory Usage (MB)
- Sample Score

## 🛠️ ATC Server Commands

### WebSocket Endpoints

#### Terminal WebSocket
```
ws://localhost:8000/ws/terminal/{session_id}
```

Supports command types:

1. Tool Commands:
```json
{
  "type": "tool",
  "tool": "tool_name",
  "params": {
    // Tool-specific parameters
  }
}
```

2. TMUX Commands:
```json
{
  "type": "tmux",
  "command": "command_string"
}
```

### REST API Endpoints

#### List Available Tools
```
GET /tools
```
Returns available tools and descriptions.

Response format:
```json
{
  "tools": [
    {
      "name": "tool_name",
      "description": "tool description"
    }
  ]
}
```

#### Execute Tool Command
```
POST /tool/{tool_name}/{command}
```
Execute tool command with parameters.

## 🎭 Voice System

### AI Personalities
Three distinct AI personalities with unique characteristics:

1. **Aye** (en-US-ChristopherNeural)
   - Clear and friendly male voice
   - Slightly faster pace (+10%)
   - Enhanced volume for clarity

2. **Trisha** (en-US-JennyNeural)
   - Professional female voice
   - Enthusiastic pace (+5%)
   - Perfect for financial insights!

3. **Omni** (en-GB-SoniaNeural)
   - Sophisticated British female voice
   - Measured pace for wisdom
   - Natural pitch for authority

### Voice Commands
```bash
# Test all AI voices
./scripts/manage.sh voices

# Voice integration in scripts
python -c "from src.core.voice import speak, AIPersonality; speak('Hello!', AIPersonality.TRISHA)"
```

## 📊 Script Commands

### Model Management
```bash
# List available AI models
./scripts/list_models.sh
```
Features:
- Real-time model availability checking
- Colorized output
- Authentication handling

### Git Integration

#### Commit System
```bash
# Standard commit
./scripts/commit.sh "Your commit message"

# Commit with specific prefix
./scripts/commit.sh -p <prefix_number> "Your commit message"

# Available prefixes:
1) 📊 BALANCE: # For major changes
2) 💰 CREDIT:  # For additions
3) 📈 DEBIT:   # For removals
4) 🧮 AUDIT:   # For fixes
5) 📝 LEDGER:  # For documentation
6) 🎯 BUDGET:  # For features
7) 🔍 REVIEW:  # For tests
8) ✨ BONUS:   # For improvements
```

#### Git Summary
```bash
# Get Trisha's insights on recent commits
./scripts/git_summary.sh
```
Features:
- AI-powered commit analysis
- Voice feedback from Trisha
- Colorized output
- Integration with voice system

### Project Management
```bash
# Interactive menu
./scripts/manage.sh menu

# Direct commands
./scripts/manage.sh <command>

Available commands:
- start:         Start all services
- stop:          Stop all services
- restart:       Restart all services
- status:        Check services status
- test:          Run tests
- test-coverage: Check code coverage
- format:        Format code
- doctor:        Run system check
- clean:         Clean up project
- voices:        Test AI voices
```

Features:
- Service management (Qdrant, SSH server, API server)
- Testing and coverage reports
- Code formatting (black + isort)
- System health checks
- Voice system testing
- Trisha's accounting jokes! 🎯

### Smart Tree
```bash
# Generate tree structure
./scripts/smart_tree.sh
```
Features:
- Respects .gitignore rules
- Colorized output
- Directory statistics
- Custom filtering options

## 🔧 Tool Categories

### Git Context Builder
```bash
# Build context from a repository
python src/tools/git_context_builder.py --repo-path /path/to/repo --context-name my-context

# List available contexts
python src/tools/git_context_builder.py --list-contexts

# Analyze a context
python src/tools/git_context_builder.py --context-name my-context --analyze

# Build relationships between multiple repos
python src/tools/git_context_builder.py --context-name my-context --build-relationships
```

Features:
- Commit analysis and vectorization
- File content processing
- Author pattern recognition
- Cross-repository relationship building
- Context analytics and insights

### Context Generation
```bash
# Generate/update context.md
./scripts/generate_context.sh
```

Features:
- Git history tracking
- Tag documentation
- Recent changes log
- Active files listing
- Contributor tracking

### ATC Plugin System
The ATC server supports various tool types:

1. File Tools
   - File operations
   - Directory management
   - Path resolution

2. System Tools
   - Process management
   - Environment variables
   - System information

3. Context Tools
   - Context storage
   - Context retrieval
   - Context relationships

## 🔐 Authentication

Modern authentication methods:
- Voice pattern recognition
- Location-based trust factors
- Behavioral patterns
- Text pattern analysis

## 🚀 Best Practices

1. Always use session IDs that are unique and meaningful
2. Handle WebSocket disconnections gracefully
3. Check tool availability before execution
4. Validate parameters before sending commands
5. Monitor command responses for errors
6. Use Trisha's commit prefixes for clear history
7. Run system checks regularly with `manage.sh doctor`
8. Keep services monitored with `manage.sh status`
9. Validate contexts regularly using ToF system
10. Use appropriate context types for different data

## 🐛 Troubleshooting

Common issues and solutions:

1. Connection Refused
   - Check if servers are running
   - Verify port availability
   - Check network connectivity

2. Authentication Failures
   - Verify credentials
   - Check authentication method compatibility
   - Ensure required context is available

3. Tool Execution Errors
   - Validate parameter format
   - Check tool availability
   - Verify required permissions

4. Voice System Issues
   - Check audio device availability
   - Verify edge-tts installation
   - Test with `manage.sh voices`

5. Context Store Issues
   - Verify Qdrant is running
   - Check context validation
   - Monitor storage capacity

## 📝 Notes

- All commands execute in current session context
- Tools may have dependencies on other components
- Some commands require specific permissions
- WebSocket connections maintain real-time updates
- Voice system caches audio for performance
- Context validation runs on regular intervals
- Model selection adapts to usage patterns
- Trisha loves to vocally approve your commits! 📊

---
Last Updated: 2025-01-12
By: Aye (with Trisha's seal of approval! 📊)
