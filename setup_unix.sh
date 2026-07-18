#!/bin/bash
# Unix System Framework Environment Installation Script
set -e

echo -e "\033[0;36m=== Drawffyfish Linux/macOS Environmental Setup Utility ===\033[0m"

# Build core virtual target dependencies
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "\033[0;32mCreated isolated Python virtual environment inside .venv\033[0m"
fi

# Activate local project core layers
source .venv/bin/activate

# Elevate script processing tools
echo -e "\033[0;33mUpgrading package installer components...\033[0m"
pip install --upgrade pip

# Create default dependencies baseline if missing
if [ ! -f "requirements.txt" ]; then
    echo -e "\033[0;34mGenerating structural requirements.txt configuration...\033[0m"
    cat << EOF > requirements.txt
python-chess>=2.1.1
requests>=2.31.0
pyyaml>=6.0.1
EOF
fi

# Run installations
echo -e "\033[0;33mDownloading requirements mapping layout tree...\033[0m"
pip install -r requirements.txt

# Grant execution rights to the companion launch script automatically
chmod +x launch_unix.sh

echo -e "\033[0;32mSetup complete! Execute './launch_unix.sh' to activate the bot pipeline.\033[0m"
