#!/usr/bin/env bash
# Startup script for MFHelper on Linux
# Features:
# - Checks/starts Ollama server (nohup)
# - Ensures tinyllama model downloaded
# - Starts backend (uvicorn) in background
# - Optionally opens browser (xdg-open)

set -e

FORCE_KILL=0
NO_BROWSER=0

usage() {
  echo "Usage: $0 [--kill] [--no-browser]"
  echo "  --kill        : kill any existing processes on required ports"
  echo "  --no-browser  : do not open browser"
  exit 1
}

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --kill) FORCE_KILL=1; shift ;;
    --no-browser) NO_BROWSER=1; shift ;;
    -h|--help) usage ;;
    *) echo "Unknown arg: $1"; usage ;;
  esac
done

PORT_OLLAMA=11434
PORT_BACKEND=8000

function is_listening() {
  local port=$1
  ss -ltn 2>/dev/null | awk '{print $4}' | grep -q ":${port}$" && return 0 || return 1
}

function kill_on_port() {
  local port=$1
  pids=$(lsof -t -i tcp:${port} || true)
  if [[ -n "$pids" ]]; then
    echo "Found processes on port ${port}: $pids"
    if [[ $FORCE_KILL -eq 1 ]]; then
      echo "Killing: $pids"
      kill -9 $pids || true
    else
      read -p "Kill these pids? [y/N] " ans
      if [[ "$ans" =~ ^[Yy]$ ]]; then kill -9 $pids || true; fi
    fi
  fi
}

echo "=== MFHelper Linux Startup ==="

# Kill existing if requested
if [[ $FORCE_KILL -eq 1 ]]; then
  kill_on_port $PORT_OLLAMA
  kill_on_port $PORT_BACKEND
fi

# Start Ollama if not listening
if is_listening $PORT_OLLAMA; then
  echo "Ollama already listening on ${PORT_OLLAMA}"
else
  if command -v ollama >/dev/null 2>&1; then
    echo "Starting Ollama (background)..."
    nohup ollama serve > ~/.ollama_serve.log 2>&1 &
    # wait for service
    for i in {1..30}; do
      sleep 1
      if is_listening $PORT_OLLAMA; then break; fi
    done
    if is_listening $PORT_OLLAMA; then echo "Ollama started"; else echo "Ollama did not start"; fi
  else
    echo "ollama not found in PATH. Please install Ollama."; exit 1
  fi
fi

# Ensure tinyllama model present
if curl -s http://localhost:${PORT_OLLAMA}/api/tags | grep -q tinyllama; then
  echo "tinyllama present"
else
  echo "Pulling tinyllama model (may take minutes)..."
  ollama pull tinyllama
fi

# Start backend in background
BACKEND_DIR="$(pwd)/backend"
if [[ ! -d "$BACKEND_DIR" ]]; then echo "Backend dir not found: $BACKEND_DIR"; exit 1; fi

if is_listening $PORT_BACKEND; then
  echo "Backend already listening on $PORT_BACKEND"
  if [[ $FORCE_KILL -eq 1 ]]; then kill_on_port $PORT_BACKEND; fi
fi

echo "Starting backend (uvicorn) in background..."
cd "$BACKEND_DIR"
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT_BACKEND} > ../uvicorn.log 2>&1 &

if [[ $NO_BROWSER -eq 0 ]]; then
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:${PORT_BACKEND}"
  else
    echo "Open http://localhost:${PORT_BACKEND} in your browser. (xdg-open not found)"
  fi
fi

echo "Startup finished. Check logs: ~/.ollama_serve.log and uvicorn.log"
