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
)

# Get a random Trisha quote
trisha_says() {
    RANDOM_INDEX=$((RANDOM % ${#TRISHA_QUOTES[@]}))
    echo -e "${PURPLE}Trisha says: ${TRISHA_QUOTES[$RANDOM_INDEX]}${NC}"
}

# Show the menu
show_menu() {
    echo -e "\n${CYAN}=== Essential MCP Management Script ===${NC}"
    echo -e "${BLUE}1.${NC} Run all tests"
    echo -e "${BLUE}2.${NC} Run specific test"
    echo -e "${BLUE}3.${NC} Check test coverage"
    echo -e "${BLUE}4.${NC} Run linting"
    echo -e "${BLUE}5.${NC} Run type checking"
    echo -e "${BLUE}6.${NC} Run all checks"
    echo -e "${BLUE}q.${NC} Quit"
    echo -e "${CYAN}=====================================${NC}"
}

# Run all tests
run_all_tests() {
    trisha_says
    echo -e "${GREEN}Running all tests...${NC}"
    poetry run pytest -v tests/
}

# Run specific test
run_specific_test() {
    echo -e "${YELLOW}Enter test path (e.g., tests/core/test_tof_system.py):${NC}"
    read -r test_path
    if [ -f "$test_path" ]; then
        trisha_says
        echo -e "${GREEN}Running $test_path...${NC}"
        poetry run pytest -v "$test_path"
    else
        echo -e "${RED}Test file not found!${NC}"
    fi
}

# Check test coverage
check_coverage() {
    trisha_says
    echo -e "${GREEN}Checking test coverage...${NC}"
    poetry run pytest --cov=src tests/
}

# Run linting
run_linting() {
    echo -e "${GREEN}Running black...${NC}"
    poetry run black src/ tests/
    echo -e "${GREEN}Running flake8...${NC}"
    poetry run flake8 src/ tests/
}

# Run type checking
run_type_checking() {
    echo -e "${GREEN}Running mypy...${NC}"
    poetry run mypy src/ tests/
}

# Run all checks
run_all_checks() {
    trisha_says
    echo -e "${CYAN}Running all checks...${NC}"
    run_linting
    run_type_checking
    check_coverage
    run_all_tests
}

# Main loop
while true; do
    show_menu
    read -r choice
    case $choice in
        1) run_all_tests ;;
        2) run_specific_test ;;
        3) check_coverage ;;
        4) run_linting ;;
        5) run_type_checking ;;
        6) run_all_checks ;;
        q) echo -e "${GREEN}Goodbye! Trisha waves goodbye! 👋${NC}"; exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac
    echo -e "\nPress enter to continue..."
    read -r
done 