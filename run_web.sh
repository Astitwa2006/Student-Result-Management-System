#!/usr/bin/env bash
# Student Result Management System - Web Dashboard Launcher
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=========================================================="
echo " Starting Student Result Management System Web Dashboard"
echo "=========================================================="

if [ -f "../venv/bin/python" ]; then
    echo "Using Python virtual environment (FastAPI backend)..."
    ../venv/bin/python app.py
else
    echo "Using Python standard library server (zero dependencies)..."
    python3 server.py 8000
fi
