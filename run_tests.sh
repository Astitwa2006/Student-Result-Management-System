#!/usr/bin/env bash
# Student Result Management System - Unit Test Suite Launcher
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "Running Unit Testing Suite (Payal Kansal - Testing & Error Checking)..."
if [ -f "../venv/bin/python" ]; then
    ../venv/bin/python -m unittest tests/test_result_system.py -v
else
    python3 -m unittest tests/test_result_system.py -v
fi
