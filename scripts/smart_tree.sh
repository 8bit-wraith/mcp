#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🌳 Generating Smart Tree...${NC}"
python3 src/tools/smart_tree.py "$@" 