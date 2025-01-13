#!/bin/bash

# Colors for pretty output
GREEN="\033[0;32m"
BLUE="\033[0;34m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m"

# Authentication token
AUTH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImMxYzA1YzBkLTQyNzktNDcyYS1hNjY3LTBhZTdjNTYxZTBkZCJ9.FZKZURnRt_iVg5pcGJ4SdLsFXK-XKydyVPlWpMhoqyQ"

echo -e "${BLUE}Fetching available models...${NC}"
curl -s "https://c.2ai.me/api/models" \
  -H "Authorization: Bearer $AUTH_TOKEN" | jq '.'

echo -e "\n${GREEN}Done! 📊${NC}" 