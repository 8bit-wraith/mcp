#!/bin/bash

# 🎭 The Magical Git Commit Script 🎭
# Approved by Trisha from Accounting! 

if [ -z "$1" ]; then
    echo "❌ Please provide a commit message!"
    echo "Usage: ./commit.sh 'Your amazing commit message'"
    exit 1
fi

# Fun prefix array
PREFIXES=(
    "🚀"
    "✨"
    "🎨"
    "🔧"
    "📝"
    "🐛"
    "🎉"
)

# Get random prefix
RANDOM_PREFIX=${PREFIXES[$RANDOM % ${#PREFIXES[@]}]}

# Add all changes
git add .

# Commit with random prefix and message
git commit -m "$RANDOM_PREFIX $1"

echo "🎉 Changes committed successfully!"
echo "Trisha says: 'Great job on keeping the codebase clean!'" 