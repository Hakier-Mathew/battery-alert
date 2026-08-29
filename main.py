#!/usr/bin/env python3
"""Low Battery Notification Daemon for Hyprland"""

import subprocess
import time
import sys
import os
from pathlib import Path



class BatteryMonitor:
    BATTERY_THRESHOLD = 20  # Percentage
    CHECK_INTERVAL = 300    # 5 minutes
    NOTIFICATION_INTERVAL = 900  # 15 minutes
    
    def __init__(self):
        self.battery_path = self._find_battery_path()
        self.last_notification_time = 0
        self.log_file = Path.home() / ".local" / "share" / "battery-alert.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _find_battery_path(self):
        power_supply_dir = Path("/sys/class/power_supply")
        for bat_name in ["BAT0", "BAT1", "BAT", "Battery"]:
            bat_path = power_supply_dir / bat_name
            if bat_path.exists():
                return bat_path
        raise FileNotFoundError("No battery found in /sys/class/power_supply/")
    
    def _is_charging(self):
        """Check if battery is charging"""
        try:
            status_file = self.battery_path / "status"
            with open(status_file, 'r') as f:
                status = f.read().strip().lower()
                return status in ["charging", "full"]
        except:
            return False
    
    def _log(self, message):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_msg = f"{timestamp} - {message}"
        print(log_msg)
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_msg + "\n")
        except:
            pass
    
    def _read_file(self, filename):
        try:
            with open(self.battery_path / filename, 'r') as f:
                return int(f.read().strip())
        except:
            return None
    
    def get_battery_info(self):
        capacity = self._read_file("capacity")
        if capacity is None:
            energy_full = self._read_file("energy_full")
            energy_now = self._read_file("energy_now")
            if energy_full and energy_now:
                capacity = int((energy_now / energy_full) * 100)
            else:
                return None
        
        return capacity
    
    def send_notification(self, title, message):
        try:
            env = os.environ.copy()
            if "DBUS_SESSION_BUS_ADDRESS" not in env:
                dbus_addr = self._find_dbus_address()
                if dbus_addr:
                    env["DBUS_SESSION_BUS_ADDRESS"] = dbus_addr
            
            subprocess.run(
                ["notify-send", "-u", "critical", title, message],
                check=True,
                timeout=5,
                env=env
            )
            self._log(f"Notification sent: {title}")
        except Exception as e:
            self._log(f"Failed to send notification: {e}")
    
    def _find_dbus_address(self):
        try:
            result = subprocess.run(
                ["pgrep", "-u", str(os.getuid()), "dbus-daemon"],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                pid = result.stdout.strip().split('\n')[0]
                env_file = f"/proc/{pid}/environ"
                with open(env_file, 'rb') as f:
                    for item in f.read().split(b'\0'):
                        if b'DBUS_SESSION_BUS_ADDRESS' in item:
                            return item.decode().split('=', 1)[1]
        except:
            pass
        return None
    
    def check_battery(self):
        capacity = self.get_battery_info()
        
        if capacity is None:
            return
        
        if capacity <= self.BATTERY_THRESHOLD and not self._is_charging():
            current_time = time.time()
            if current_time - self.last_notification_time >= self.NOTIFICATION_INTERVAL:
                message = f"Battery is at {capacity}%"
                self.send_notification("🔋 Low Battery", message)
                self.last_notification_time = current_time
    
    def run(self):
        self._log("Battery Alert Daemon Started")
        try:
            while True:
                self.check_battery()
                time.sleep(self.CHECK_INTERVAL)
        except KeyboardInterrupt:
            self._log("Battery Alert Daemon Stopped")
            sys.exit(0)


if __name__ == "__main__":
    monitor = BatteryMonitor()
    monitor.run()
