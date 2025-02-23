#!/bin/bash

# 🎨 Colors make life better!
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 🎵 More Elvis quotes because why not?
COMMIT_QUOTES=(
    "Wise men say only fools rush in... but this commit looks good!"
    "A little less conversation, a little more committing!"
    "It's now or never... to commit these changes!"
    "Return to sender... pushing code to remote!"
    "Thank you, thank you very much... for this awesome code!"
)

# 🎲 Get a random commit quote
random_quote() {
    echo "${COMMIT_QUOTES[$RANDOM % ${#COMMIT_QUOTES[@]}]}"
}

# 🚀 Show help message
show_help() {
    echo -e "${MAGENTA}"
    echo "╔══════════════════════════════════════╗"
    echo "║  📝 MCP Commit Script                 ║"
    echo "╚══════════════════════════════════════╝"
    echo -e "${NC}"
    echo -e "${CYAN}Usage:${NC}"
    echo -e "  $0 \"Your commit message\""
    echo
    echo -e "${YELLOW}Example:${NC}"
    echo -e "  $0 \"feat: Add awesome new feature 🚀\""
    exit 1
}

# Check if commit message was provided
if [ $# -eq 0 ]; then
    show_help
fi

# Combine all arguments into commit message
commit_msg="$*"

# 🎭 Format the commit message
formatted_msg="[Type]: $commit_msg 🌟\n"

# Get list of changes
echo -e "${CYAN}Analyzing changes...${NC}"
added_files=$(git diff --cached --name-only --diff-filter=A)
modified_files=$(git diff --cached --name-only --diff-filter=M)
deleted_files=$(git diff --cached --name-only --diff-filter=D)

# Add file changes to commit message
if [ ! -z "$added_files" ]; then
    formatted_msg+="- Added:\n$added_files\n"
fi
if [ ! -z "$modified_files" ]; then
    formatted_msg+="- Updated:\n$modified_files\n"
fi
if [ ! -z "$deleted_files" ]; then
    formatted_msg+="- Removed:\n$deleted_files\n"
fi

# Add pro tip
formatted_msg+="\n- Pro Tip of the Commit: $(random_quote)\n"
formatted_msg+="\nAye, Aye! 🚢"

# Show the formatted message
echo -e "${YELLOW}Commit message preview:${NC}"
echo -e "$formatted_msg"
echo

# Confirm commit
read -p "$(echo -e ${CYAN}"Proceed with commit? [Y/n] "${NC})" confirm
confirm=${confirm:-Y}

if [[ $confirm =~ ^[Yy]$ ]]; then
    # Stage all changes if nothing is staged
    if [ -z "$(git diff --cached --name-only)" ]; then
        echo -e "${YELLOW}No changes staged. Staging all changes...${NC}"
        git add .
    fi
    
    # Commit changes
    echo -e "$formatted_msg" | git commit -F -
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Changes committed successfully! 🎸${NC}"
        echo -e "${BLUE}$(random_quote)${NC}"
    else
        echo -e "${RED}Failed to commit changes! 😱${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}Commit cancelled. Elvis has left the building! 👋${NC}"
    exit 0
fi 