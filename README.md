# LanBridge 🚀

> Real-time LAN messaging application over TCP sockets

**Built with [Koza AI Agent](https://github.com/haydarkadioglu/Koza-Agent)**

---

## Features

- ✅ TCP socket-based client-server architecture
- ✅ Multi-client support (threading)
- ✅ **Graphical UI** (tkinter) — modern dark theme
- ✅ Colorful console interface (alternative)
- ✅ Real-time messaging
- ✅ Join/leave notifications
- ✅ Online user list with live updates
- ✅ Windows, Linux, macOS support
- ✅ Easy launchers

## Quick Start

### 1. Start the server (one person):
```bash
python server.py
```

### 2. Start a client (everyone else):

**🔵 GUI version (recommended):**
```bash
python gui_client.py
```
or double-click `gui_run.bat` (Windows)

**🟢 Console version (lightweight):**
```bash
python client.py
```

## GUI Screens

| Screen | Description |
|--------|-------------|
| 🌉 **Connection** | Enter server IP and username in a sleek dark interface |
| 💬 **Chat** | Real-time messaging with colored usernames, timestamps, and online user list sidebar |
| 👥 **Users Panel** | See who's online at a glance |

## Connection

Default port: **12345**

| Parameter | Description |
|-----------|-------------|
| `HOST` | `0.0.0.0` (all network interfaces) |
| `PORT` | `12345` |
| `BUFFER` | `65535` |

## Requirements

- Python 3.6+
- Standard library only (no extra dependencies)
- tkinter (included with Python on most platforms)

### tkinter on Linux:
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

## Launchers

| File | Description |
|------|-------------|
| `gui_run.bat` | Launch GUI client (Windows) |
| `lanchat.bat` | Launch console client (Windows) |

## Project Structure

```
LanBridge/
├── server.py       # TCP server
├── client.py       # Console client
├── gui_client.py   # GUI client (tkinter)
├── lanchat.bat     # Console launcher
├── gui_run.bat     # GUI launcher
└── README.md
```

## License

MIT License
