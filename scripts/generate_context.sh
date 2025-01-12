#!/bin/bash

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Function to get the latest Git history and append to context.md
update_context_from_git() {
    echo -e "${BLUE}Updating context from Git history...${NC}"
    
    # Get the current date
    current_date=$(date +"%Y-%m-%d")
    
    # Create a temporary file for the new content
    temp_file=$(mktemp)
    
    # Add header to temp file
    cat > "$temp_file" << EOL
# Project Context

## Git History (Auto-generated ${current_date})

### Recent Changes
$(git log --pretty=format:"- **%ad**: %s" --date=short | head -n 10)

### Active Files
$(git ls-files | sed 's/^/- /')

### Contributors
$(git shortlog -sn --all | sed 's/^[0-9 \t]*/-/')

EOL

    # Append existing context if it exists (excluding the old header)
    if [ -f "context.md" ]; then
        # Skip the first line (old header) and append the rest
        sed '1d' context.md >> "$temp_file"
    fi
    
    # Replace the old context file with the new one
    mv "$temp_file" "context.md"
    
    echo -e "${GREEN}Context updated successfully!${NC}"
    echo -e "${PURPLE}Tri says: Git history is like a well-maintained ledger - every entry tells a story! 📚${NC}"
}

# Run the update function
update_context_from_git 