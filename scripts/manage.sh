#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Check for required tools
check_requirements() {
    command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed."; exit 1; }
    command -v git >/dev/null 2>&1 || { echo "Git is required but not installed."; exit 1; }
}

# Setup Python environment
setup_python() {
    echo -e "${BLUE}Setting up Python environment...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install pdm
    pdm install
}

# Run the visualizer
run_visualizer() {
    echo -e "${BLUE}Starting Git Context Visualizer...${NC}"
    source .venv/bin/activate
    
    # Install required packages if not already installed
    pip install gradio plotly pandas networkx GitPython

    # Run the visualizer
    python src/tools/git_context_visualizer.py
}

# Main menu
while true; do
    echo -e "\n${PURPLE}=== Git Context Management System ===${NC}"
    echo -e "${BLUE}1) Setup Python Environment${NC}"
    echo -e "${BLUE}2) Run Git Context Visualizer${NC}"
    echo -e "${BLUE}3) Run Tests${NC}"
    echo -e "${BLUE}4) Check Coverage${NC}"
    echo -e "${BLUE}5) Run Linting${NC}"
    echo -e "${BLUE}6) Clean All${NC}"
    echo -e "${BLUE}7) Exit${NC}"
    
    read -p "Enter your choice: " choice
    
    case $choice in
        1)
            setup_python
            ;;
        2)
            run_visualizer
            ;;
        3)
            run_tests
            ;;
        4)
            check_coverage
            ;;
        5)
            run_linting
            ;;
        6)
            clean_all
            ;;
        7)
            echo -e "${PURPLE}Tri says: See you next time! 👋${NC}"
            exit 0
            ;;
        *)
            echo -e "${PURPLE}Tri says: That's not a valid option! Try again. 😅${NC}"
            ;;
    esac
done 