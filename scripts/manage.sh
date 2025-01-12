#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Trisha's quotes
QUOTES=(
    "Time to build some context! 📚"
    "Git histories are like accounting ledgers - every entry tells a story! 📖"
    "Finding patterns in repos is like finding patterns in spreadsheets... but more fun! 🎯"
    "Cross-repo relationships are like connecting the dots between coffee expenses... I mean, codebases! ☕"
    "Building context is an investment in understanding! 💡"
)

# Function to display a random quote
show_quote() {
    RANDOM_QUOTE=${QUOTES[$RANDOM % ${#QUOTES[@]}]}
    echo -e "${BLUE}Trisha says: ${RANDOM_QUOTE}${NC}"
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
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}Missing required dependencies:${NC}"
        printf '%s\n' "${missing_deps[@]}"
        exit 1
    fi
}

# Main menu
show_menu() {
    echo -e "\n${GREEN}=== Git Context Builder Management ===${NC}"
    echo "1. Build context from repository"
    echo "2. Build relationships between repositories"
    echo "3. List available contexts"
    echo "4. Analyze context"
    echo "5. Run tests"
    echo "6. Clean up (stop Qdrant)"
    echo "q. Quit"
    echo -e "${YELLOW}Choose an option:${NC} "
}

# Main loop
check_requirements

while true; do
    show_menu
    read -r choice
    
    case $choice in
        1) build_context ;;
        2) build_relationships ;;
        3) list_contexts ;;
        4) analyze_context ;;
        5)
            show_quote
            echo -e "${YELLOW}Running tests...${NC}"
            pytest tests/tools/test_git_context_builder.py -v
            ;;
        6)
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