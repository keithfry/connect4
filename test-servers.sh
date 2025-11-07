#!/bin/bash
# Test script to manually start servers for debugging

echo "Starting backend server..."
cd backend && ../.venv/bin/python manage.py runserver &
BACKEND_PID=$!

echo "Starting frontend server..."
cd frontend && python3 -m http.server 8080 &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"

echo "Waiting for servers to start..."
sleep 5

echo "Testing backend..."
curl -s -o /dev/null -w "Backend status: %{http_code}\n" http://localhost:8000/

echo "Testing frontend..."
curl -s -o /dev/null -w "Frontend status: %{http_code}\n" http://localhost:8080/

echo ""
echo "Servers are running. Press Ctrl+C to stop."
echo "To stop manually: kill $BACKEND_PID $FRONTEND_PID"

wait

