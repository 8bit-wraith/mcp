#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Commit prefixes with Trisha's flair
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

# Show usage with Trisha's style
usage() {
    echo -e "${BLUE}📚 Trisha's Commit Guide${NC}"
    echo -e "${YELLOW}Usage: $0 [-p PREFIX_NUM] [-y] \"<commit message>\"${NC}"
    echo -e "\nOptions:"
    echo -e "  -p NUM    Select prefix number"
    echo -e "  -y        Auto-confirm commit"
    echo -e "  -h        Show this help message"
    echo -e "\n${GREEN}Available prefixes:${NC}"
    for i in "${!PREFIXES[@]}"; do
        echo -e "  $((i+1))) ${PREFIXES[$i]}"
    done
    echo -e "\n${YELLOW}Example: $0 -p 1 -y \"Updated the balance sheet calculations\"${NC}"
    exit 1
}

# Parse command line arguments
prefix_num=8  # Default to "✨ BONUS:"
auto_confirm=false
while getopts ":p:hy" opt; do
    case $opt in
        p) prefix_num="$OPTARG";;
        y) auto_confirm=true;;
        h) usage;;
        \?) echo -e "${RED}Invalid option: -$OPTARG${NC}"; usage;;
    esac
done
shift $((OPTIND-1))

# Check if a commit message was provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Commit message is required!${NC}"
    usage
fi

# Get the commit message from arguments
message="$*"

# Validate prefix number
if ! [[ "$prefix_num" =~ ^[0-9]+$ ]] || [ "$prefix_num" -lt 1 ] || [ "$prefix_num" -gt "${#PREFIXES[@]}" ]; then
    echo -e "${RED}Invalid prefix number! Using default (✨ BONUS:)${NC}"
    prefix_num=8
fi

# Get selected prefix and format message
prefix="${PREFIXES[$((prefix_num-1))]}"
formatted_message="$prefix $message"

# Function to have Trisha speak using git_summary.sh
trisha_speak() {
    local message="$1"
    # Store current git log
    local old_log=$(git log -n 1 --pretty=format:"%ad | %s" 2>/dev/null)
    
    # Perform the git operations
    git add . && git commit -m "$message"
    
    # Run git_summary to have Trisha review the changes
    ./scripts/git_summary.sh
}

# Show preview
echo -e "\n${YELLOW}Preview:${NC}"
echo -e "${GREEN}$formatted_message${NC}"

# Determine if we should commit
do_commit=true
if ! $auto_confirm && [ "$prefix_num" != "8" ]; then
    # Ask for confirmation for non-default prefixes when not auto-confirming
    read -p "Proceed with commit? (Y/n): " confirm
    if [[ $confirm =~ ^[Nn]$ ]]; then
        do_commit=false
    fi
fi

if $do_commit; then
    echo -e "${GREEN}📝 Committing changes...${NC}"
    trisha_speak "$formatted_message"
else
    echo -e "${YELLOW}Commit cancelled. Tri says: Better to double-check those numbers! 📊${NC}"
    exit 0
fi 