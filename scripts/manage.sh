#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Trisha's quotes
QUOTES=(
    "Time to build some context! 📚"
    "Git histories are like accounting ledgers - every entry tells a story! 📖"
    "Finding patterns in repos is like finding patterns in spreadsheets... but more fun! 🎯"
    "Cross-repo relationships are like connecting the dots between coffee expenses... I mean, codebases! ☕"
    "Building context is an investment in understanding! 💡"
    "Let's visualize some Git patterns - it's like a dance party for your code! 💃"
    "These graphs are prettier than my pivot tables! 📊"
    "Testing is like accounting - everything must add up! ✨"
    "Dependencies are like expense reports - keep them organized! 📋"
    "Context building is like tax season - thorough analysis required! 🔎"
)

# Function to display a random quote
show_quote() {
    RANDOM_QUOTE=${QUOTES[$RANDOM % ${#QUOTES[@]}]}
    echo -e "${PURPLE}Trisha says: ${RANDOM_QUOTE}${NC}"
}

# Error handling
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    show_quote
    echo -e "${YELLOW}Need help? Check the README or ask Trisha!${NC}"
    exit 1
}

# Function to check if Qdrant is running
ensure_qdrant() {
    if ! docker ps | grep -q qdrant; then
        echo -e "${YELLOW}Starting Qdrant container...${NC}"
        docker run -d -p 6333:6333 -p 6334:6334 \
            -v $(pwd)/qdrant_storage:/qdrant/storage:z \
            qdrant/qdrant
        sleep 5  # Wait for Qdrant to start
    fi
}

# Setup Python environment
setup_python() {
    echo -e "${BLUE}Setting up Python environment...${NC}"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv || handle_error "Failed to create virtual environment"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate || handle_error "Failed to activate virtual environment"
    
    # Upgrade pip
    python -m pip install --upgrade pip || handle_error "Failed to upgrade pip"
    
    # Install dependencies with PDM
    pdm install || handle_error "Failed to install Python dependencies"
    
    echo -e "${GREEN}Python environment ready!${NC}"
}

# Setup Node environment
setup_node() {
    echo -e "${BLUE}Setting up Node environment...${NC}"
    
    cd packages/mcp-server-enhanced-ssh || handle_error "SSH server directory not found"
    
    # Install dependencies with pnpm
    pnpm install || handle_error "Failed to install Node dependencies"
    
    # Build TypeScript
    pnpm run build || handle_error "Failed to build TypeScript"
    
    cd ../..
    
    echo -e "${GREEN}Node environment ready!${NC}"
}

# Clean everything
clean_all() {
    echo -e "${BLUE}Cleaning all build artifacts...${NC}"
    
    # Clean Python
    rm -rf .venv build dist *.egg-info .pytest_cache .coverage htmlcov .pdm-python
    find . -type d -name "__pycache__" -exec rm -rf {} +
    
    # Clean Node
    cd packages/mcp-server-enhanced-ssh
    pnpm run clean
    rm -rf node_modules
    cd ../..
    
    echo -e "${GREEN}Everything is squeaky clean!${NC}"
}

# Function to build context from a repository
build_context() {
    show_quote
    ensure_qdrant
    
    read -p "Enter the repository path: " REPO_PATH
    read -p "Enter a name for this context: " CONTEXT_NAME
    read -p "Is this part of a multi-repo context? (y/N): " MULTI_REPO
    
    MULTI_FLAG=""
    if [[ $MULTI_REPO =~ ^[Yy]$ ]]; then
        MULTI_FLAG="--multi-repo"
    fi
    
    echo -e "${YELLOW}Building context from ${REPO_PATH}...${NC}"
    python src/tools/git_context_builder.py \
        --repo-path "$REPO_PATH" \
        --context-name "$CONTEXT_NAME" \
        $MULTI_FLAG
}

# Function to build relationships between repositories
build_relationships() {
    show_quote
    ensure_qdrant
    
    read -p "Enter the context name to build relationships for: " CONTEXT_NAME
    
    echo -e "${YELLOW}Building relationships for ${CONTEXT_NAME}...${NC}"
    python src/tools/git_context_builder.py \
        --context-name "$CONTEXT_NAME" \
        --build-relationships
}

# Function to list available contexts
list_contexts() {
    show_quote
    ensure_qdrant
    
    echo -e "${YELLOW}Listing available contexts...${NC}"
    python src/tools/git_context_builder.py --list-contexts
}

# Function to analyze a context
analyze_context() {
    show_quote
    ensure_qdrant
    
    read -p "Enter the context name to analyze: " CONTEXT_NAME
    
    echo -e "${YELLOW}Analyzing context ${CONTEXT_NAME}...${NC}"
    python src/tools/git_context_builder.py \
        --context-name "$CONTEXT_NAME" \
        --analyze
}

# Function to start the visualizer
start_visualizer() {
    show_quote
    ensure_qdrant
    
    echo -e "${YELLOW}Starting Git Context Visualizer...${NC}"
    echo -e "${GREEN}Gradio interface will be available at: http://localhost:7860${NC}"
    echo -e "${GREEN}Live visualization will be available at: http://localhost:7860/visualizer${NC}"
    
    # Create templates directory if it doesn't exist
    mkdir -p src/tools/templates
    
    # Start the visualizer
    python src/tools/git_context_visualizer.py
}

# Run all tests
run_all_tests() {
    show_quote
    echo -e "${GREEN}Running all tests...${NC}"
    
    # Python tests
    echo -e "${BLUE}Running Python tests...${NC}"
    pdm run pytest -v tests/ || handle_error "Python tests failed"
    
    # Node tests
    echo -e "${BLUE}Running Node tests...${NC}"
    cd packages/mcp-server-enhanced-ssh
    pnpm test || handle_error "Node tests failed"
    cd ../..
}

# Run specific test
run_specific_test() {
    echo -e "${YELLOW}Enter test path (e.g., tests/core/test_tof_system.py):${NC}"
    read -r test_path
    if [ -f "$test_path" ]; then
        show_quote
        echo -e "${GREEN}Running $test_path...${NC}"
        
        if [[ "$test_path" == *".py" ]]; then
            pdm run pytest -v "$test_path"
        else
            cd packages/mcp-server-enhanced-ssh
            pnpm test "$test_path"
            cd ../..
        fi
    else
        echo -e "${RED}Test file not found!${NC}"
    fi
}

# Check test coverage
check_coverage() {
    show_quote
    echo -e "${GREEN}Checking test coverage...${NC}"
    
    # Python coverage
    echo -e "${BLUE}Python coverage:${NC}"
    pdm run pytest --cov=src tests/
    
    # Node coverage
    echo -e "${BLUE}Node coverage:${NC}"
    cd packages/mcp-server-enhanced-ssh
    pnpm test -- --coverage
    cd ../..
}

# Run linting
run_linting() {
    echo -e "${GREEN}Running linters...${NC}"
    
    # Python linting
    echo -e "${BLUE}Running Python linters...${NC}"
    pdm run black src/ tests/
    pdm run flake8 src/ tests/
    
    # Node linting
    echo -e "${BLUE}Running Node linters...${NC}"
    cd packages/mcp-server-enhanced-ssh
    pnpm run lint
    cd ../..
}

# Run type checking
run_type_checking() {
    echo -e "${GREEN}Running type checkers...${NC}"
    
    # Python type checking
    echo -e "${BLUE}Running Python type checking...${NC}"
    pdm run mypy src/ tests/
    
    # TypeScript type checking
    echo -e "${BLUE}Running TypeScript type checking...${NC}"
    cd packages/mcp-server-enhanced-ssh
    pnpm run build --noEmit
    cd ../..
}

# Function to check requirements
check_requirements() {
    local missing_deps=()
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("Python 3")
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("Docker")
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        missing_deps+=("Git")
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("Node.js")
    fi
    
    # Check pnpm
    if ! command -v pnpm &> /dev/null; then
        missing_deps+=("pnpm")
    fi
    
    # Check pdm
    if ! command -v pdm &> /dev/null; then
        missing_deps+=("pdm")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}Missing required dependencies:${NC}"
        printf '%s\n' "${missing_deps[@]}"
        exit 1
    fi
}

# Main menu
show_menu() {
    echo -e "\n${GREEN}=== Essential MCP Management ===${NC}"
    echo -e "${BLUE}=== Environment Management ===${NC}"
    echo "1. Setup everything (Python + Node)"
    echo "2. Setup Python only"
    echo "3. Setup Node only"
    echo "4. Clean everything"
    echo -e "${BLUE}=== Git Context Management ===${NC}"
    echo "5. Build context from repository"
    echo "6. Build relationships between repositories"
    echo "7. List available contexts"
    echo "8. Analyze context"
    echo "9. Start visualizer"
    echo -e "${BLUE}=== Testing & Quality ===${NC}"
    echo "10. Run all tests"
    echo "11. Run specific test"
    echo "12. Check test coverage"
    echo "13. Run linting"
    echo "14. Run type checking"
    echo -e "${BLUE}=== Maintenance ===${NC}"
    echo "15. Clean up (stop Qdrant)"
    echo "q. Quit"
    echo -e "${YELLOW}Choose an option:${NC} "
}

# Main loop
check_requirements

while true; do
    show_menu
    read -r choice
    
    case $choice in
        1) setup_python && setup_node ;;
        2) setup_python ;;
        3) setup_node ;;
        4) clean_all ;;
        5) build_context ;;
        6) build_relationships ;;
        7) list_contexts ;;
        8) analyze_context ;;
        9) start_visualizer ;;
        10) run_all_tests ;;
        11) run_specific_test ;;
        12) check_coverage ;;
        13) run_linting ;;
        14) run_type_checking ;;
        15)
            show_quote
            echo -e "${YELLOW}Stopping Qdrant container...${NC}"
            docker stop $(docker ps -q --filter ancestor=qdrant/qdrant)
            ;;
        q|Q) 
            echo -e "${GREEN}Goodbye! Don't forget to commit your contexts! 👋${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            ;;
    esac
    
    echo -e "\nPress Enter to continue..."
    read -r
done 