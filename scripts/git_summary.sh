#!/bin/bash

# Colors for pretty output
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Authentication token
AUTH_TOKEN="sk-1c55ccb06c02440ebbabb5603d987001"

echo "Asking Trisha to review the git log..."

# Get the git log and create JSON payload
GIT_LOG=$(git log -n 2 --pretty=format:"%ad | %s")
echo -e "\n${RED}Git Log:${NC}"
echo "$GIT_LOG"

# Create JSON payload using Python to handle escaping
PAYLOAD=$(python3 -c "
import json
git_log = '''$GIT_LOG'''
payload = {
    'model': 'trisha-git',
    'messages': [{
        'role': 'user',
        'content': f'Please review this git log and give me your thoughts:\n\n{git_log}'
    }]
}
print(json.dumps(payload))
")

echo -e "\n${RED}JSON Payload:${NC}"
echo "$PAYLOAD" | python3 -m json.tool

# Send to Trisha's endpoint and capture response
RESPONSE=$(curl -s -X POST "https://c.2ai.me/api/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -d "$PAYLOAD")

# Debug output
echo -e "\n${RED}Debug - API Response:${NC}"
echo "$RESPONSE" | python3 -c 'import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))'

# Extract Trisha's message from the response with error handling
MESSAGE=$(echo "$RESPONSE" | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, str):
        print(data.strip())
    elif "choices" in data and len(data["choices"]) > 0:
        if "text" in data["choices"][0]:
            print(data["choices"][0]["text"].strip())
        elif "message" in data["choices"][0]:
            print(data["choices"][0]["message"]["content"].strip())
        else:
            print("Hmm, let me check my ledger... I seem to be having trouble reading the git log format.")
    else:
        print("Hmm, let me check my ledger... I seem to be having trouble accessing the git log.")
except Exception as e:
    print(f"Oh dear, there seems to be an error in my calculations! {str(e)}")
')

echo -e "\nTrisha's response:"
echo -e "${YELLOW}$MESSAGE${NC}"

# Use the voice system to speak the message
echo -e "\n🎙️ Trisha says:"
python3 -c "
import asyncio, json
from src.core.voice import speak, AIPersonality

async def say_message():
    message = '''$MESSAGE'''
    await speak(message, AIPersonality.TRISHA)

asyncio.run(say_message())
"

echo -e "\nReview complete! 📊"