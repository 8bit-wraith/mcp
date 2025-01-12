#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Check if a commit message was provided
if [ -z "$1" ]; then
    echo -e "${PURPLE}Tri says: Don't forget to tell me what we're committing! 📝${NC}"
    exit 1
fi

# Handle optional tag
if [ -n "$2" ]; then
    TAG_MESSAGE="${2}"
    echo -e "${BLUE}Tri says: Adding tag: ${TAG_MESSAGE} 🏷️${NC}"
fi

echo -e "${BLUE}Tri's Pre-Commit Checklist:${NC}"
echo -e "${GREEN}📋 Staging changes...${NC}"
git add .

echo -e "${GREEN}🔍 Checking what we're about to commit...${NC}"
git status

echo -e "${GREEN}💫 Making it official...${NC}"
git commit -m "${1}"

# Add tag if provided
if [ -n "$2" ]; then
    echo -e "${GREEN}🏷️ Adding tag...${NC}"
    git tag -a "${2}" -m "${2}" HEAD || {
        echo -e "${PURPLE}Tri says: Oops, tagging didn't work! 😅${NC}"
        exit 1
    }
    echo -e "${PURPLE}Tri says: Tagged and bagged! 🎯${NC}"
fi

# Update context from Git history
echo -e "${GREEN}📚 Updating context from Git history...${NC}"
./scripts/generate_context.sh

echo -e "${PURPLE}Tri says: Another beautiful commit in the books! 🎉${NC}" 