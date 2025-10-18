#!/bin/bash
if [ "$1" = "--user" ]; then
    USER_JSON="$2"
    NAME=$(echo "$USER_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('name', 'Unknown'))")
    EMAIL=$(echo "$USER_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('email', 'no-email'))")
    echo "Hello $NAME ($EMAIL)! Greeting sent at $(date)"
else
    echo "Usage: $0 --user '<user_json>'"
    exit 1
fi