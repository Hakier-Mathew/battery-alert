# Battery Alert for Hyprland

A lightweight low battery notification daemon for Hyprland.

## Features

- 🔋 Monitors battery every 5 minutes
- 📢 Desktop notification when battery < 20%
- 🔌 No notifications while charging
- ⏱️ Notifies every 15 minutes while critically low
- 🚀 Runs as systemd user service

## Installation

```bash
cd ~/projects/battery-alert
chmod +x main.py install.sh
./install.sh
```

## Usage

**Check status:**
```bash
systemctl --user status battery-alert.service
```

**View logs:**
```bash
tail -f ~/.local/share/battery-alert.log
```

**Manual start/stop:**
```bash
systemctl --user start battery-alert.service
systemctl --user stop battery-alert.service
```

## Configuration

Edit [main.py](main.py) to change:
- `BATTERY_THRESHOLD`: Battery percentage threshold (default: 20%)
- `CHECK_INTERVAL`: How often to check battery in seconds (default: 300 = 5 minutes)
- `NOTIFICATION_INTERVAL`: How often to notify in seconds (default: 900 = 15 minutes)

