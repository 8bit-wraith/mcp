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

# Commit prefixes
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

# Get a random Trisha commit message
get_trisha_message() {
    echo "${COMMIT_MESSAGES[$RANDOM % ${#COMMIT_MESSAGES[@]}]}"
}

# Speak using Trisha's voice
trisha_speak() {
    message="$1"
    # Escape single quotes for Python
    escaped_message=$(echo "$message" | sed "s/'/\\\'/g")
    poetry run python -c "
import asyncio
from src.core.voice import speak, AIPersonality
async def say():
    await speak('$escaped_message', AIPersonality.TRISHA)
asyncio.run(say())
"
}

# Show usage
usage() {
    echo -e "${BLUE}Usage: $0 [-p PREFIX_NUM] \"<commit message>\"${NC}"
    echo -e "${YELLOW}Available prefixes:${NC}"
    for i in "${!PREFIXES[@]}"; do
        echo -e "  $((i+1))) ${PREFIXES[$i]}"
    done
    exit 1
}

# Parse command line arguments
prefix_num=8  # Default to "✨ BONUS:"
while getopts ":p:h" opt; do
    case $opt in
        p) prefix_num="$OPTARG";;
        h) usage;;
        \?) echo -e "${RED}Invalid option: -$OPTARG${NC}"; usage;;
    esac
done
shift $((OPTIND-1))

# Check if message is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Commit message is required!${NC}"
    usage
fi

# Combine all remaining arguments into message
message="$*"

# Validate prefix number
if ! [[ "$prefix_num" =~ ^[0-9]+$ ]] || [ "$prefix_num" -lt 1 ] || [ "$prefix_num" -gt "${#PREFIXES[@]}" ]; then
    echo -e "${RED}Invalid prefix number! Using default (✨ BONUS:)${NC}"
    prefix_num=8
fi

# Get selected prefix
prefix="${PREFIXES[$((prefix_num-1))]}"

# Format commit message
formatted_message="$prefix $message"

# Show preview
echo -e "\n${YELLOW}Preview:${NC}"
echo -e "${GREEN}$formatted_message${NC}"

# Get Trisha's approval message
trisha_message=$(get_trisha_message)
echo -e "\n${PURPLE}Tri says: Let's make sure these changes are properly accounted for! 📚${NC}"

# Auto-confirm if using default prefix
if [ "$prefix_num" == "8" ]; then
    do_commit=true
else
    # Ask for confirmation for non-default prefixes
    read -p "Proceed with commit? (Y/n): " confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        do_commit=false
    else
        do_commit=true
    fi
fi

if $do_commit; then
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