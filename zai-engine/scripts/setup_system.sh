#!/bin/bash

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS system"
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    echo "Installing libmagic..."
    brew install libmagic
    brew link libmagic

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Ubuntu/Debian
    echo "Detected Linux system"
    if [ -f /etc/debian_version ]; then
        echo "Installing libmagic1..."
        sudo apt-get update
        sudo apt-get install -y libmagic1
    else
        echo "This script only supports Ubuntu/Debian Linux distributions"
        exit 1
    fi
else
    echo "Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "System dependencies installed successfully" 