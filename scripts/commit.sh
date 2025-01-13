#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Trisha's commit messages
COMMIT_MESSAGES=(
    "Another perfectly balanced transaction! The books are looking lovely!"
    "I've double-entered this commit into our ledger. Everything checks out!"
    "The Git balance sheet is growing nicely. I love a good asset!"
    "This commit passes all my accounting standards. And I'm very strict!"
    "I've audited this commit, and it's absolutely brilliant!"
    "Adding this to our Git ledger. The numbers don't lie - it's perfect!"
)

# Get a random Trisha commit message
get_trisha_message() {
    echo "${COMMIT_MESSAGES[$RANDOM % ${#COMMIT_MESSAGES[@]}]}"
}

# Speak using Trisha's voice
trisha_speak() {
    message="$1"
    poetry run python -c "
import asyncio
from src.core.voice import speak, AIPersonality
async def say():
    await speak('$message', AIPersonality.TRISHA)
asyncio.run(say())
"
}

# Check if message is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Commit message is required!${NC}"
    echo -e "${BLUE}Usage: $0 \"<commit message>\"${NC}"
    exit 1
fi

# Combine all arguments into one message
message="$*"

# Show prefix menu
echo -e "${PURPLE}=== Trisha's Commit Categorization System ===${NC}"
echo -e "${BLUE}Select a prefix for your commit:${NC}"

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

# Get Trisha's approval message
trisha_message=$(get_trisha_message)
echo -e "\n${PURPLE}Tri says: Let's make sure these changes are properly accounted for! 📚${NC}"

# Confirm commit
read -p "Proceed with commit? (y/n): " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    # Stage all changes
    git add .
    
    # Commit with message
    if git commit -m "$formatted_message"; then
        echo -e "${GREEN}Changes committed successfully! 🎉${NC}"
        # Have Trisha speak her approval
        trisha_speak "$trisha_message"
    else
        echo -e "${RED}Failed to commit changes! 😱${NC}"
        trisha_speak "Oh dear, we seem to have an accounting error. Let's audit this and try again!"
        exit 1
    fi
else
    echo -e "${YELLOW}Commit cancelled. Tri says: Better safe than sorry! 😌${NC}"
    trisha_speak "No worries! Better to double-check our figures first!"
    exit 0
fi 