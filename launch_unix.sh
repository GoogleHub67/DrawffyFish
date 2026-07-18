#!/bin/bash
# Unix Runtime Core Engine Execution Launcher Script

echo "===================================================="
echo "    Drawffyfish Bot Platform Bootstrapping Core     "
echo "===================================================="

# Validate runtime components are available
if [ ! -f ".venv/bin/activate" ]; then
    echo -e "\033[0;31m[ERROR] Active .venv runtime layer not found.\033[0m"
    echo "Please execute './setup_unix.sh' first to compile the system properties."
    exit 1
fi

# Parse credential sets securely without console stdout leakage
if [ -f ".env" ]; then
    echo "[INFO] Injecting secure authentication variables from local .env profile..."
    export $(cat .env | xargs)
fi

# Connect virtual layer mapping profiles
source .venv/bin/activate

echo "[LAUNCH] Booting main event loops..."
python3 main.py

echo "===================================================="
echo "[SHUTDOWN] Event framework runtime loop stopped."
