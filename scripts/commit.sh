#!/bin/bash

# Colors for output
PURPLE='\033[0;35m'
GREEN='\033[0;32m'
NC='\033[0m'

# Check if a commit message was provided
if [ $# -eq 0 ]; then
    echo -e "${PURPLE}Trisha says: We need a commit message! How else will we track our changes? 📝${NC}"
    exit 1
fi

# Trisha's pre-commit checklist
echo -e "${PURPLE}Trisha's Pre-Commit Checklist:${NC}"
echo -e "📋 Staging changes..."
git add .

echo -e "🔍 Checking what we're about to commit..."
git status

echo -e "💫 Making it official..."
git commit -m "$1"

echo -e "${GREEN}Trisha says: Another beautiful commit in the books! 🎉${NC}" 