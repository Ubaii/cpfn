#!/bin/bash

SCRIPT_NAMES=("cpfn.py" "cpfp.py")
CURRENT_DIR=$(pwd)
TARGET_DIR="/usr/local/bin"

for SCRIPT_NAME in "${SCRIPT_NAMES[@]}"; do
    PYTHON_SCRIPT="$CURRENT_DIR/$SCRIPT_NAME"
    SYMLINK_NAME="${SCRIPT_NAME%.*}"

    chmod +x "$PYTHON_SCRIPT"

    if [ -L "$TARGET_DIR/$SYMLINK_NAME" ]; then
        echo "Removing existing symlink for $SYMLINK_NAME..."
        sudo rm "$TARGET_DIR/$SYMLINK_NAME"
    fi

    echo "Creating symlink for $SYMLINK_NAME..."
    sudo ln -s "$PYTHON_SCRIPT" "$TARGET_DIR/$SYMLINK_NAME"

    echo "Symlink created: $TARGET_DIR/$SYMLINK_NAME -> $PYTHON_SCRIPT"
    echo "You can now run the script with the command: $SYMLINK_NAME"
done
