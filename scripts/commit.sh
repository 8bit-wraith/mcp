#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if a commit message was provided
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Please provide a commit message!${NC}"
    exit 1
fi

# Get the commit message from arguments
commit_message="$*"

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

# Execute the commit with Trisha's commentary
echo -e "${GREEN}📝 Committing changes with message:${NC} $commit_message"
trisha_speak "$commit_message" 