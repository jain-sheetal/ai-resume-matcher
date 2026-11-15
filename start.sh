#!/usr/bin/env bash

# MatchPro AI - Startup Script
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo "=========================================================="
echo " Starting MatchPro AI Resume Matching System"
echo " Location: $DIR"
echo "=========================================================="

# Cleanup previous background processes on exit
cleanup() {
  echo ""
  echo "Shutting down servers..."
  kill $(jobs -p) 2>/dev/null || true
  exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 1. Start Backend
echo "-> Starting Backend API (FastAPI) on http://localhost:8000..."
cd "$DIR/backend"
if [ -f "venv/bin/python" ]; then
  PYTHON_BIN="venv/bin/python"
elif [ -f "venv/bin/python3" ]; then
  PYTHON_BIN="venv/bin/python3"
else
  PYTHON_BIN="python3"
fi

$PYTHON_BIN -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to initialize..."
sleep 2

# 2. Start Frontend
echo "-> Starting Frontend (React + Vite) on http://localhost:3000..."
cd "$DIR/frontend"
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!

echo ""
echo "=========================================================="
echo " MatchPro AI is Running!"
echo " Web UI:     http://localhost:3000"
echo " API Docs:   http://localhost:8000/docs"
echo " Press Ctrl+C to stop both servers."
echo "=========================================================="

# Wait for background jobs
wait
