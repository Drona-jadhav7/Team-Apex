#!/usr/bin/env bash
# ==============================================================================
# SuperIndia.ai - Unified Startup Script
# Hack in Hills Manali 2026 (AI Systems & National Infrastructure Track)
# ==============================================================================

echo "=========================================================="
echo "⚡ Starting SuperIndia.ai Decision Intelligence Engine ⚡"
echo "=========================================================="

# Ensure Node.js and Python are in PATH if installed in user directory
export PATH="/c/Users/DRONA/nodejs:$PATH":$PATH

# Trap Ctrl+C to terminate background jobs cleanly
trap 'kill $(jobs -p) 2>/dev/null; exit' SIGINT SIGTERM EXIT

# 1. Start FastAPI Backend
echo "Starting Backend API on http://127.0.0.1:8000 ..."
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait briefly for backend to initialize
sleep 2

# 2. Start Vite Frontend
echo "Starting Vite Frontend on http://localhost:5173 ..."
cd frontend
npm run dev -- --host &
FRONTEND_PID=$!

echo ""
echo "=========================================================="
echo " SuperIndia.ai is RUNNING!"
echo " Frontend: http://localhost:5173"
echo " Backend API: http://127.0.0.1:8000"
echo " Interactive API Docs: http://127.0.0.1:8000/docs"
echo "=========================================================="
echo "Press Ctrl+C to stop all services."

wait $BACKEND_PID $FRONTEND_PID
