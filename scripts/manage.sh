#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Fun messages from Trisha
TRISHA_QUOTES=(
    "Time to balance those test books! 📊"
    "Let's audit those contexts! 🔍"
    "Testing is like accounting - everything must add up! ✨"
    "Ready to crunch some test numbers! 🧮"
    "Let's make these tests as clean as my spreadsheets! 📈"
    "Dependencies are like expense reports - keep them organized! 📋"
    "Time to reconcile those environments! 🔄"
)

# Get a random Trisha quote
trisha_says() {
    RANDOM_INDEX=$((RANDOM % ${#TRISHA_QUOTES[@]}))
    echo -e "${PURPLE}Trisha says: ${TRISHA_QUOTES[$RANDOM_INDEX]}${NC}"
}

# Error handling
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    trisha_says
    echo -e "${YELLOW}Need help? Check the README or ask Trisha!${NC}"
    exit 1
}

# Check for required tools
check_requirements() {
    echo -e "${BLUE}Checking requirements...${NC}"
    
    command -v python3 >/dev/null 2>&1 || handle_error "Python 3.11+ is required"
    command -v node >/dev/null 2>&1 || handle_error "Node.js is required"
    command -v pnpm >/dev/null 2>&1 || handle_error "pnpm is required"
    command -v pdm >/dev/null 2>&1 || handle_error "pdm is required"
    
    # Check Python version
    PY_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if (( $(echo "$PY_VERSION < 3.11" | bc -l) )); then
        handle_error "Python 3.11+ is required (found $PY_VERSION)"
    fi
    
    echo -e "${GREEN}All requirements met!${NC}"
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

# Run all tests
run_all_tests() {
    trisha_says
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
        trisha_says
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
    trisha_says
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

# Start development servers
start_dev() {
    echo -e "${GREEN}Starting development servers...${NC}"
    
    # Start Python API
    echo -e "${BLUE}Starting Python API...${NC}"
    pdm run uvicorn src.api.main:app --reload --port 8000 &
    
    # Start SSH server
    echo -e "${BLUE}Starting SSH server...${NC}"
    cd packages/mcp-server-enhanced-ssh
    pnpm run dev &
    cd ../..
    
    # Wait for both
    wait
}

# Show the menu
show_menu() {
    echo -e "\n${CYAN}=== Essential MCP Management Script ===${NC}"
    echo -e "${BLUE}1.${NC} Setup everything (Python + Node)"
    echo -e "${BLUE}2.${NC} Setup Python only"
    echo -e "${BLUE}3.${NC} Setup Node only"
    echo -e "${BLUE}4.${NC} Run all tests"
    echo -e "${BLUE}5.${NC} Run specific test"
    echo -e "${BLUE}6.${NC} Check test coverage"
    echo -e "${BLUE}7.${NC} Run linting"
    echo -e "${BLUE}8.${NC} Run type checking"
    echo -e "${BLUE}9.${NC} Start development servers"
    echo -e "${BLUE}10.${NC} Clean everything"
    echo -e "${BLUE}q.${NC} Quit"
    echo -e "${CYAN}=====================================${NC}"
}

# Main loop
while true; do
    show_menu
    read -r choice
    case $choice in
        1) check_requirements && setup_python && setup_node ;;
        2) check_requirements && setup_python ;;
        3) check_requirements && setup_node ;;
        4) run_all_tests ;;
        5) run_specific_test ;;
        6) check_coverage ;;
        7) run_linting ;;
        8) run_type_checking ;;
        9) start_dev ;;
        10) clean_all ;;
        q) echo -e "${GREEN}Goodbye! Trisha waves goodbye! 👋${NC}"; exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac
    echo -e "\nPress enter to continue..."
    read -r
done 