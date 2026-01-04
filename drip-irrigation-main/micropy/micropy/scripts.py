#!/usr/bin/env python3
"""
MicroPython ESP32 Development Scripts
Convenient CLI commands for ESP32 development
"""
import subprocess
import sys
from pathlib import Path

# Configuration
PORT = "/dev/ttyUSB0"
FIRMWARE_PATH = "firmware/esp32_firmware.bin"
SRC_DIR = "src"

def run_command(cmd: list[str], description: str) -> int:
    """Run a command and handle errors"""
    print(f" {description}...")
    try:
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            print(f" {description} complete!")
        else:
            print(f" {description} failed with exit code {result.returncode}")
        return result.returncode
    except FileNotFoundError:
        print(f" Command not found. Make sure dependencies are installed.")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 130


def flash_firmware():
    """Flash MicroPython firmware to ESP32"""
    firmware = Path(FIRMWARE_PATH)
    if not firmware.exists():
        print(f" Firmware not found at {FIRMWARE_PATH}")
        print(" Download from: https://micropython.org/download/ESP32_GENERIC/")
        return 1
    
    # Erase flash
    print("\n🗑️  Step 1: Erasing flash...")
    erase_cmd = ["esptool", "--port", PORT, "erase-flash"]
    if run_command(erase_cmd, "Flash erase") != 0:
        return 1
    
    # Flash firmware
    print("\n Step 2: Flashing firmware...")
    flash_cmd = [
        "esptool", "--chip", "esp32", "--port", PORT,
        "write-flash", "-z", "0x1000", str(firmware)
    ]
    return run_command(flash_cmd, "Firmware flash")


def upload_code():
    """Upload src/ directory to ESP32 and reset"""
    src = Path(SRC_DIR)
    if not src.exists():
        print(f" Source directory '{SRC_DIR}' not found")
        return 1
    
    cmd = [
        "mpremote", "connect", PORT,
        "fs", "cp", "-r", f"{SRC_DIR}/", ":",
        "+", "reset"
    ]
    return run_command(cmd, f"Upload {SRC_DIR}/ and reset")


def download_code():
    """Download all files from ESP32 to src/ directory"""
    src = Path(SRC_DIR)
    src.mkdir(exist_ok=True)
    
    print(" Downloading files from ESP32...")
    
    # List files on device
    list_cmd = ["mpremote", "connect", PORT, "fs", "ls"]
    try:
        result = subprocess.run(list_cmd, capture_output=True, text=True, check=True)
        files = []
        for line in result.stdout.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('ls '):
                continue
            
            parts = line.split()
            # Format is: "    SIZE filename" or "SIZE filename"
            # Skip if it's a directory (ends with /) or just ":"
            if len(parts) >= 2:
                filename = parts[-1]  # Last part is always filename
                if not filename.endswith('/') and filename != ':':
                    files.append(filename)
        
        if not files:
            print("⚠️  No files found on ESP32")
            return 0
        
        print(f" Found {len(files)} file(s): {', '.join(files)}")
        
        # Download each file
        for filename in files:
            download_cmd = [
                "mpremote", "connect", PORT,
                "fs", "cp", f":{filename}", f"{SRC_DIR}/{filename}"
            ]
            print(f"  ⬇️  Downloading {filename}...")
            subprocess.run(download_cmd, check=True)
        
        print(f" Downloaded {len(files)} file(s) to {SRC_DIR}/")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f" Download failed: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 130


def open_repl():
    """Open MicroPython REPL console"""
    print(" Opening REPL (Press Ctrl+] to exit)...")
    cmd = ["mpremote", "connect", PORT, "repl"]
    return subprocess.run(cmd).returncode


def list_files():
    """List files on ESP32"""
    cmd = ["mpremote", "connect", PORT, "fs", "ls"]
    return run_command(cmd, "List files on ESP32")


def reset_device():
    """Soft reset ESP32"""
    cmd = ["mpremote", "connect", PORT, "reset"]
    return run_command(cmd, "Reset ESP32")


if __name__ == "__main__":
    # For testing
    if len(sys.argv) > 1:
        func = sys.argv[1]
        if func in globals():
            sys.exit(globals()[func]())
        else:
            print(f"Unknown command: {func}")
            sys.exit(1)
