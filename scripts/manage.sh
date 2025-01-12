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
    command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed."; exit 1; }
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

# Setup Node environment and GAK
setup_node() {
    echo -e "${BLUE}Setting up Node environment...${NC}"
    cd src/tools/gak
    npm install
    npm link
    cd ../../..
    echo -e "${GREEN}GAK installed and linked! Try 'gak --help' to get started${NC}"
}

# Run the visualizer
run_visualizer() {
    echo -e "${BLUE}Starting Git Context Visualizer...${NC}"
    source .venv/bin/activate
    python src/tools/git_context_visualizer.py
}

# Run GAK search
run_gak() {
    echo -e "${BLUE}Running GAK search...${NC}"
    read -p "Enter search terms: " search_terms
    gak "$search_terms"
}

# Main menu
while true; do
    echo -e "\n${PURPLE}=== Git Context Management System ===${NC}"
    echo -e "${BLUE}1) Setup Python Environment${NC}"
    echo -e "${BLUE}2) Setup Node & GAK${NC}"
    echo -e "${BLUE}3) Run Git Context Visualizer${NC}"
    echo -e "${BLUE}4) Run GAK Search${NC}"
    echo -e "${BLUE}5) Run Tests${NC}"
    echo -e "${BLUE}6) Check Coverage${NC}"
    echo -e "${BLUE}7) Run Linting${NC}"
    echo -e "${BLUE}8) Clean All${NC}"
    echo -e "${BLUE}9) Exit${NC}"
    
    read -p "Enter your choice: " choice
    
    case $choice in
        1)
            setup_python
            ;;
        2)
            setup_node
            ;;
        3)
            run_visualizer
            ;;
        4)
            run_gak
            ;;
        5)
            run_tests
            ;;
        6)
            check_coverage
            ;;
        7)
            run_linting
            ;;
        8)
            clean_all
            ;;
        9)
            echo -e "${PURPLE}Tri says: See you next time! 👋${NC}"
            exit 0
            ;;
        *)
            echo -e "${PURPLE}Tri says: That's not a valid option! Try again. 😅${NC}"
            ;;
    esac
done 