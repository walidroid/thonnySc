#!/bin/bash
# Run Thonny from source (Linux/macOS)

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting Thonny 4.1.7 from source..."
python3 "$SCRIPT_DIR/launch_thonny.py"
