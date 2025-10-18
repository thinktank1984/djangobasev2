#!/bin/bash

echo "=== PGQ-Cmd Setup Test ==="

# Test 1: Check if script exists and is executable
if [ -f "./pgq-cmd" ] && [ -x "./pgq-cmd" ]; then
    echo "✅ pgq-cmd script exists and is executable"
else
    echo "❌ pgq-cmd script not found or not executable"
    exit 1
fi

# Test 2: Check configuration file
if [ -f "./config.json" ]; then
    echo "✅ config.json exists"
    echo "Configuration:"
    cat config.json | python3 -m json.tool
else
    echo "❌ config.json not found"
fi

# Test 3: Check logs directory
if [ -d "./logs" ]; then
    echo "✅ logs directory exists"
else
    echo "❌ logs directory not found"
fi

# Test 4: Check example scripts
if [ -f "./examples/heartbeat.sh" ] && [ -f "./examples/greet_user.sh" ]; then
    echo "✅ Example scripts exist"
    echo "Testing heartbeat.sh:"
    ./examples/heartbeat.sh
    echo ""
    echo "Testing greet_user.sh:"
    ./examples/greet_user.sh --user '{"name":"Test User","email":"test@example.com"}'
else
    echo "❌ Example scripts not found"
fi

# Test 5: Check documentation
if [ -f "./pgq-cmd-tasks-queue.md" ]; then
    echo "✅ Documentation exists"
    echo "Documentation length: $(wc -l < ./pgq-cmd-tasks-queue.md) lines"
else
    echo "❌ Documentation not found"
fi

echo ""
echo "=== Setup Test Complete ==="