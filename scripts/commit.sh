#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Trisha's commit prefixes
PREFIXES=(
    "📊 BALANCE:" # For major changes
    "💰 CREDIT:" # For additions
    "📈 DEBIT:" # For removals
    "🧮 AUDIT:" # For fixes
    "📝 LEDGER:" # For documentation
    "🎯 BUDGET:" # For features
    "🔍 REVIEW:" # For tests
    "✨ BONUS:" # For improvements
)

# Show usage
usage() {
    echo -e "${BLUE}Usage: $0 \"<commit message>\"${NC}"
    echo -e "${YELLOW}Available prefixes:${NC}"
    for prefix in "${PREFIXES[@]}"; do
        echo -e "  $prefix"
    done
    exit 1
}

# Check if message is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Commit message is required!${NC}"
    usage
fi

# Combine all arguments into one message
message="$*"

# Show prefix menu
echo -e "${PURPLE}=== Trisha's Commit Categorization System ===${NC}"
echo -e "${BLUE}Select a prefix for your commit:${NC}"

for i in "${!PREFIXES[@]}"; do
    echo -e "${BLUE}$((i+1))) ${PREFIXES[$i]}${NC}"
done

# Get prefix choice
read -p "Enter your choice (1-${#PREFIXES[@]}): " choice

# Validate choice
if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt "${#PREFIXES[@]}" ]; then
    echo -e "${RED}Invalid choice! Trisha says: 'That's not how we balance books!' 😅${NC}"
    exit 1
fi

# Get selected prefix
prefix="${PREFIXES[$((choice-1))]}"

# Format commit message
formatted_message="$prefix $message"

# Show preview
echo -e "\n${YELLOW}Preview:${NC}"
echo -e "${GREEN}$formatted_message${NC}"
echo -e "\n${PURPLE}Tri says: Let's make sure these changes are properly accounted for! 📚${NC}"

# Confirm commit
read -p "Proceed with commit? (y/n): " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    # Stage all changes
    git add .
    
    # Commit with message
    if git commit -m "$formatted_message"; then
        echo -e "${GREEN}Changes committed successfully! 🎉${NC}"
        echo -e "${PURPLE}Tri says: Another perfectly balanced transaction! 💫${NC}"
    else
        echo -e "${RED}Failed to commit changes! 😱${NC}"
        echo -e "${PURPLE}Tri says: Looks like we need an audit! 🔍${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Commit cancelled. Tri says: Better safe than sorry! 😌${NC}"
    exit 0
fi 