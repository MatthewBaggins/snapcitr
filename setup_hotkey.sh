#!/bin/bash
# Setup script for snapcitr hotkey listener

set -e

SERVICE_NAME="snapcitr-hotkey"
SERVICE_FILE="$HOME/.config/systemd/user/${SERVICE_NAME}.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting up snapcitr hotkey listener..."

# Create user systemd directory if it doesn't exist
mkdir -p "$HOME/.config/systemd/user"

# Copy service file and substitute repo path
sed "s|REPO_PATH|${SCRIPT_DIR}|g" "${SCRIPT_DIR}/snapcitr-hotkey.service" > "$SERVICE_FILE"

# Reload systemd
systemctl --user daemon-reload

# Enable and start the service
systemctl --user enable "${SERVICE_NAME}.service"
systemctl --user start "${SERVICE_NAME}.service"

# Check status
systemctl --user status "${SERVICE_NAME}.service" --no-pager

echo ""
echo "✓ Hotkey listener installed and started!"
echo "  Hotkey: Ctrl+PrintScreen"
echo ""
echo "Commands:"
echo "  Status:  systemctl --user status ${SERVICE_NAME}"
echo "  Stop:    systemctl --user stop ${SERVICE_NAME}"
echo "  Start:   systemctl --user start ${SERVICE_NAME}"
echo "  Disable: systemctl --user disable ${SERVICE_NAME}"
echo "  Logs:    journalctl --user -u ${SERVICE_NAME} -f"