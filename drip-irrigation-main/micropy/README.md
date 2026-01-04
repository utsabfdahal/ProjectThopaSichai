#  MicroPython ESP32 Development Environment

Professional development setup for ESP32 with MicroPython.

##  Quick Start

### 1. Flash Firmware (First Time Only)
```bash
uv run flash
```

This automatically erases and flashes MicroPython firmware to your ESP32.

### 2. Upload Your Code
```bash
uv run upload
```

Or press **Ctrl+Shift+B** in VS Code!

### 3. Monitor Output
```bash
uv run repl
```

Press **Ctrl+]** to exit REPL.

##  All Commands

| Command | Description |
|---------|-------------|
| `uv run flash` | Flash MicroPython firmware to ESP32 |
| `uv run upload` | Upload `src/` to ESP32 and reset |
| `uv run download` | Download all files from ESP32 to `src/` |
| `uv run repl` | Open interactive REPL console |
| `uv run ls` | List files on ESP32 |
| `uv run reset` | Soft reset ESP32 |

## ⌨️ VS Code Shortcuts

- **Ctrl+Shift+B** - Upload src/ and reset ESP32
- **Ctrl+Shift+P** → "Tasks: Run Task" - More options

##  Project Structure

```
micropy/
├── src/              # Your MicroPython code (auto-uploads)
│   ├── main.py       # Main entry point
│   ├── boot.py       # Boot configuration
│   └── library.py    # Your modules
├── firmware/         # ESP32 firmware (.bin files)
├── examples/         # Example code
└── .vscode/          # VS Code tasks
```

##  Development Workflow

1. **Write code** in `src/` folder
2. **Upload** with `uv run upload` or **Ctrl+Shift+B**
3. **Monitor** with `uv run repl`
4. **Backup** from device with `uv run download`

##  Tips

- All files in `src/` upload together
- Use `from library import myfunction` to import modules
- REPL: Press **Ctrl+]** to exit
- Check device: `uv run ls`

---

##  Firmware Flashing Guide

### When to Flash Firmware

Flash new firmware if you see:
- `flash read err, 1000` errors
- Device not responding
- MicroPython version update needed
- Fresh install

### Automatic Method (Recommended)

```bash
uv run flash
```

This automatically:
1. Erases flash memory
2. Flashes MicroPython firmware
3. Verifies installation

### Manual Method

If you need more control:

#### 1. Download Firmware
Visit: https://micropython.org/download/ESP32_GENERIC/

Or use the one in `firmware/` folder.

**Firmware Downloads by Board Type:**
- **ESP32 Generic**: https://micropython.org/download/ESP32_GENERIC/
- **ESP32-S2**: https://micropython.org/download/ESP32_GENERIC_S2/
- **ESP32-S3**: https://micropython.org/download/ESP32_GENERIC_S3/
- **ESP32-C3**: https://micropython.org/download/ESP32_GENERIC_C3/

Choose the latest stable `.bin` file.

#### 2. Erase Flash
```bash
esptool --port /dev/ttyUSB0 erase-flash
```

#### 3. Flash Firmware
```bash
esptool --chip esp32 --port /dev/ttyUSB0 write-flash -z 0x1000 firmware/esp32_firmware.bin
```

#### 4. Verify Installation
```bash
uv run repl
```

You should see:
```
MicroPython v1.xx on 2024-xx-xx; ESP32 module with ESP32
Type "help()" for more information.
>>>
```

Press **Ctrl+]** to exit.

### Common Issues

#### Port Busy Error
```bash
# Find process using the port
fuser /dev/ttyUSB0

# Kill it
sudo kill -9 <PID>
```

#### Permission Denied
```bash
sudo usermod -a -G dialout $USER
# Then logout and login
```

#### Wrong Port
Check available ports:
```bash
python -m serial.tools.list_ports -v
```

Your ESP32 is typically `/dev/ttyUSB0` or `/dev/ttyACM0`.

---

##  Dependencies

Already installed via `uv`:
- `esptool` - Firmware flashing
- `mpremote` - File transfer & REPL
- `pyserial` - Serial communication

##  Hardware Configuration

- **Port**: `/dev/ttyUSB0` (configured in scripts)
- **Board**: ESP32-D0WDQ6 (revision v1.0)
- **Features**: Wi-Fi, BT, Dual Core, 240MHz
- **Built-in LED**: GPIO 2

##  Resources

- [MicroPython Docs](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [Firmware Downloads](https://micropython.org/download/ESP32_GENERIC/)
- [ESP32 Quick Reference](QUICK_REFERENCE.md)

---

**Not reinventing the wheel** - this is a proper dev environment! 
