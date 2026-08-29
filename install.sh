#!/usr/bin/env bash
# Setup script for battery-alert daemon

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="battery-alert"
SERVICE_FILE="$SCRIPT_DIR/$SERVICE_NAME.service"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "🔋 Setting up Battery Alert Daemon..."

# Make script executable
chmod +x "$SCRIPT_DIR/main.py"
echo "✓ Script is executable"

# Check if notify-send is installed
if ! command -v notify-send &> /dev/null; then
    echo "⚠️  Warning: notify-send not found. Install it with:"
    echo "   Ubuntu/Debian: sudo apt install libnotify-bin"
    echo "   Fedora: sudo dnf install libnotify"
    echo "   Arch: sudo pacman -S libnotify"
fi

# Create systemd user directory if needed
mkdir -p "$SYSTEMD_USER_DIR"
echo "✓ Systemd user directory exists"

# Copy and customize service file
if [ -f "$SERVICE_FILE" ]; then
    cp "$SERVICE_FILE" "$SYSTEMD_USER_DIR/$SERVICE_NAME.service"
    
    # Update the path in the service file
    sed -i "s|%h|$HOME|g" "$SYSTEMD_USER_DIR/$SERVICE_NAME.service"
    echo "✓ Service file installed"
fi

# Enable the service
systemctl --user daemon-reload
systemctl --user enable "$SERVICE_NAME.service"
echo "✓ Service enabled"

# Start the service
systemctl --user start "$SERVICE_NAME.service"
echo "✓ Service started"

# Check status
echo ""
echo "📊 Service Status:"
systemctl --user status "$SERVICE_NAME.service" --no-pager || true

echo ""
echo "✅ Setup complete!"
echo ""
echo "To view logs:"
echo "  journalctl --user -u $SERVICE_NAME.service -f"
echo ""
echo "To stop the service:"
echo "  systemctl --user stop $SERVICE_NAME.service"
echo ""
echo "To disable auto-start:"
echo "  systemctl --user disable $SERVICE_NAME.service"
