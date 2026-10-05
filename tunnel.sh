#!/usr/bin/env bash
# ==============================================================================
# SuperIndia.ai - Instant Public HTTPS Tunnel Launcher
# Hack in Hills Manali 2026 (AI Systems & National Infra Track)
# ==============================================================================

echo "================================================================"
echo "  SuperIndia.ai - Instant Public HTTPS Tunnel Launcher"
echo "  Hack in Hills Manali 2026 (AI Systems & National Infra Track)"
echo "================================================================"
echo ""

export PATH="/c/Users/DRONA/nodejs:$PATH":$PATH

# Trap Ctrl+C to terminate background jobs cleanly
trap 'kill $(jobs -p) 2>/dev/null; exit' SIGINT SIGTERM EXIT

# 1. Start backend if not already running
if ! lsof -i:8000 -t >/dev/null 2>&1 && ! netstat -ano 2>/dev/null | grep -q ":8000.*LISTEN"; then
    echo "[1/3] Starting FastAPI Backend on port 8000..."
    python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
    sleep 2
else
    echo "[1/3] FastAPI Backend is already running on port 8000."
fi

# 2. Start frontend if not already running
if ! lsof -i:5173 -t >/dev/null 2>&1 && ! netstat -ano 2>/dev/null | grep -q ":5173.*LISTEN"; then
    echo "[2/3] Starting Vite Frontend on port 5173..."
    cd frontend && npm run dev -- --host 127.0.0.1 --port 5173 &
    cd ..
    sleep 3
else
    echo "[2/3] Vite Frontend is already running on port 5173."
fi

# 3. Launch tunnel
echo "[3/3] Establishing instant public HTTPS tunnel..."
echo "----------------------------------------------------------------"

if command -v cloudflared >/dev/null 2>&1; then
    echo "[Tunnel Provider] Using Cloudflare Quick Tunnel (cloudflared)..."
    echo ""
    echo "================================================================"
    echo " Copy the generated https://*.trycloudflare.com URL below!"
    echo "================================================================"
    cloudflared tunnel --url http://127.0.0.1:5173 --http-host-header localhost:5173
elif command -v npx >/dev/null 2>&1; then
    echo "[Tunnel Provider] Using localtunnel (npx localtunnel)..."
    echo ""
    echo "================================================================"
    echo " Copy the generated https://*.loca.lt URL below!"
    echo "================================================================"
    npx localtunnel --port 5173 --local-host 127.0.0.1
else
    echo "Error: Neither cloudflared nor npx localtunnel found."
    exit 1
fi
