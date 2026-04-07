#!/bin/bash

# Demo script for Insurance Policy Review Agent Web API

echo "=== Insurance Policy Review Agent Web API Demo ==="
echo

# Start the server in background
echo "Starting web server..."
cd /Users/dattatraychaugule/Projects/insurance-policy-review-agent/insurance-policy-review-agent
source ../../../.venv/bin/activate
python web.py &
SERVER_PID=$!

# Wait for server to start
sleep 2

echo "Server started with PID: $SERVER_PID"
echo

# Test health endpoint
echo "Testing health endpoint:"
curl -s http://localhost:8000/health | python -m json.tool
echo

# Test root endpoint
echo "Testing root endpoint:"
curl -s http://localhost:8000/ | python -m json.tool
echo

# Create a sample policy file
echo "Creating sample policy file..."
cat > sample_policy.txt << 'EOF'
Policy Number: DEMO-123
Policy type: Health insurance
Issuer: Demo Insurance Co.
Sum insured: $500000
Effective date: 2024-01-01
Expiry date: 2024-12-31
Exclusions: pre-existing conditions not declared, cosmetic procedures
Claims process: submit documents within 30 days
EOF

echo "Sample policy created."
echo

# Test API with the sample file
echo "Testing policy analysis API:"
curl -s -X POST "http://localhost:8000/analyze" \
     -F "file=@sample_policy.txt" | python -m json.tool

echo
echo "Demo completed. Stopping server..."

# Stop the server
kill $SERVER_PID 2>/dev/null

# Clean up
rm -f sample_policy.txt

echo "Demo finished."