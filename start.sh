#!/bin/bash

# Install Mega SDK dependencies if not already installed
if ! python3 -c "import mega" &>/dev/null; then
    echo "Installing Mega SDK..."
    pip install mega.py>=1.0.8
fi

# Make the script more resilient
python3 update.py
if [ $? -eq 0 ]; then
    echo "Update successful, starting bot..."
    python3 -m bot
else
    echo "Update failed, starting bot anyway..."
    python3 -m bot
fi
