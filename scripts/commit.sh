#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Check if a commit message was provided
if [ -z "$1" ]; then
    echo -e "${PURPLE}Trisha says: Don't forget to tell me what we're committing! 📝${NC}"
    exit 1
fi

echo -e "${BLUE}Trisha's Pre-Commit Checklist:${NC}"
echo -e "${GREEN}📋 Staging changes...${NC}"
git add .

echo -e "${GREEN}🔍 Checking what we're about to commit...${NC}"
git status

echo -e "${GREEN}💫 Making it official...${NC}"
git commit -m "$1"

# Update context from Git history
echo -e "${GREEN}📚 Updating context from Git history...${NC}"
./scripts/generate_context.sh

echo -e "${PURPLE}Trisha says: Another beautiful commit in the books! 🎉${NC}" 