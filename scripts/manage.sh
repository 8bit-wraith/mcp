#!/bin/bash

# 🎭 The Amazing MCP-SSH Management Script 🎭
# Trisha from Accounting approved this script! 

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

show_menu() {
    echo -e "${PURPLE}🌟 Welcome to the MCP-SSH Manager! 🌟${NC}"
    echo -e "${BLUE}1)${NC} Start Server"
    echo -e "${BLUE}2)${NC} Run Tests"
    echo -e "${BLUE}3)${NC} Build Project"
    echo -e "${BLUE}4)${NC} Clean Build"
    echo -e "${BLUE}5)${NC} Check Dependencies"
    echo -e "${RED}q)${NC} Quit"
}

start_server() {
    echo -e "${GREEN}🚀 Launching the server to infinity and beyond!${NC}"
    npm run start
}

run_tests() {
    echo -e "${GREEN}🧪 Running tests - Trisha is watching!${NC}"
    npm run test
}

build_project() {
    echo -e "${GREEN}🏗️  Building project - With extra love!${NC}"
    npm run build
}

clean_build() {
    echo -e "${GREEN}🧹 Cleaning up - Making it sparkle!${NC}"
    rm -rf dist/
    rm -rf node_modules/
    npm install
}

check_deps() {
    echo -e "${GREEN}📦 Checking dependencies - Making sure we're up to date!${NC}"
    npm outdated
}

# Handle command line arguments
if [ $# -gt 0 ]; then
    case "$1" in
        "start") start_server ;;
        "test") run_tests ;;
        "build") build_project ;;
        "clean") clean_build ;;
        "check") check_deps ;;
        *) echo "Invalid argument. Use: start|test|build|clean|check" ;;
    esac
    exit 0
fi

# Interactive menu
while true; do
    show_menu
    read -p "Choose your destiny (1-5 or q): " choice
    case $choice in
        1) start_server ;;
        2) run_tests ;;
        3) build_project ;;
        4) clean_build ;;
        5) check_deps ;;
        q) echo "👋 See you in Omni's Hot Tub!"; exit 0 ;;
        *) echo "Invalid choice! Try again!" ;;
    esac
    echo
done 