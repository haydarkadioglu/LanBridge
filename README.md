# LanBridge 🚀

> Real-time LAN messaging application over TCP sockets

## Features

- ✅ TCP socket-based client-server architecture
- ✅ Multi-client support (threading)
- ✅ Colorful console interface
- ✅ Real-time messaging
- ✅ Join/leave notifications
- ✅ Online user list
- ✅ Windows support (`msvcrt` for keyboard input)
- ✅ Easy launcher (`lanchat.bat`)

## Installation

```bash
git clone https://github.com/haydarkadioglu/LanBridge.git
cd LanBridge
```

## Usage

### Start the server:
```bash
python server.py
```

### Start a client:
```bash
python client.py
```

### Quick menu (Windows):
```
lanchat.bat
```

## Connection

Default port: **12345**

| Parameter | Description |
|-----------|----------|
| `HOST` | `0.0.0.0` (all network interfaces) |
| `PORT` | `12345` |
| `BUFFER` | `65535` |

## Requirements

- Python 3.6+
- Standard library only (no extra dependencies)

## License

MIT License
