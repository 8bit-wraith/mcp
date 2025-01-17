#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "${BLUE}🔍 Analyzing Git Repository...${NC}"

# Get recent commits
echo "\n${GREEN}Recent Commits:${NC}"
git log --pretty=format:"%h - %s (%cr) <%an>" --no-merges -n 5

# Get branch information
echo "\n${GREEN}Branch Information:${NC}"
git branch -v

# Get repository status
echo "\n${GREEN}Repository Status:${NC}"
git status -s

# Get contribution statistics
echo "\n${GREEN}Contribution Statistics:${NC}"
git shortlog -sn --no-merges

# Get file statistics
echo "\n${GREEN}File Statistics:${NC}"
git ls-files | wc -l

echo "\n${BLUE}✨ Analysis Complete!${NC}"