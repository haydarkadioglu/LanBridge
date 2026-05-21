# LanBridge 🚀

> **Modern GUI-based real-time LAN messaging application** over TCP sockets

Built with [Koza AI Agent](https://github.com/haydarkadioglu/Koza-Agent)

---

## 📸 Preview

LanBridge is a **graphical** LAN chat app with a sleek dark-themed interface. Connect, chat, and see who's online — all in real time.

| Screen | Description |
|--------|-------------|
| 🌉 **Connection Screen** | Enter server IP and username in a stylish dark interface |
| 💬 **Chat Screen** | Real-time messaging with colored usernames, timestamps, and live online user list |
| 👥 **Users Panel** | See who's online at a glance on the right sidebar |

---

## ✨ Features

- ✅ **Graphical User Interface** (tkinter) — modern dark theme with accent colors
- ✅ TCP socket-based client-server architecture
- ✅ Multi-client support (threading)
- ✅ Real-time messaging with timestamps
- ✅ Color-coded usernames for each user
- ✅ Live online user list with automatic updates
- ✅ Join/leave notifications
- ✅ Cross-platform (Windows, Linux, macOS)
- ✅ One-click launcher for Windows
- ✅ No external dependencies — pure Python standard library

---

## 🚀 Quick Start

### 1️⃣ Start the Server (one person on the network)

```bash
python server.py
```

The server prints your local IP address — share it with others!

### 2️⃣ Start the Client (everyone else)

**🔵 GUI version (recommended):**
```bash
python gui_client.py
```
*Or double-click* **`gui_run.bat`** *(Windows)*

**🟢 Console version (alternative):**
```bash
python client.py
```

---

## 🎮 How to Use

### Connection Screen
1. **Server IP** — Enter the server's IP address (e.g. `192.168.1.100`)
2. **Username** — Your display name (defaults to your system username)
3. Click **"🚀 Connect to Server"**

### Chat Screen
- Type your message in the bottom input bar and press **Enter** or click **"➤ Send"**
- See the **online users list** on the right sidebar
- Your messages appear in **cyan**, others in unique colors
- Click **"✕ Disconnect"** to leave

---

## 🔧 Requirements

| Requirement | Notes |
|-------------|-------|
| **Python** | 3.6 or higher |
| **tkinter** | ✅ Included with Python on Windows/macOS |
| **Extra packages** | ❌ None — uses only standard library |

### tkinter on Linux (if missing):
```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

---

## 📁 Project Structure

```
LanBridge/
├── server.py         # 🖥️ TCP server — must be running first
├── gui_client.py     # 🎨 GUI client — main app (tkinter)
├── client.py         # 📟 Console client — lightweight alternative
├── gui_run.bat       # 🪟 One-click GUI launcher (Windows)
├── lanchat.bat       # 🪟 Console launcher with menu (Windows)
├── README.md         # 📘 This file
├── LICENSE           # ⚖️ MIT License
└── .gitignore        # 🙈 Git ignore rules
```

---

## 🌐 Network Info

| Parameter | Default | Description |
|-----------|---------|-------------|
| `HOST` | `0.0.0.0` | Listens on all network interfaces |
| `PORT` | `12345` | TCP port for communication |
| `BUFFER` | `65535` | Maximum message size |

---

## 🖥️ Screenshots

> *(Coming soon — run the app and see for yourself!)*

---

## 🧪 Example Workflow

```
💻 Computer A (Server):
    $ python server.py
    [*] Listening on 0.0.0.0:12345
    [*] Local IP: 192.168.1.50

💻 Computer B (Client):
    $ python gui_client.py
    → Enter IP: 192.168.1.50
    → Enter username: Alice
    → 🚀 Connect!

💻 Computer C (Client):
    $ python gui_client.py
    → Enter IP: 192.168.1.50
    → Enter username: Bob
    → 🚀 Connect!

✅ All users see each other in real-time!
```

---

## 🛠️ For Developers

LanBridge uses a simple JSON protocol over TCP:

```
→ Client sends:     {"type": "message", "message": "Hello!"}
→ Server sends:     {"type": "message", "sender": "Alice", 
                     "message": "Hello!", "time": "14:30:00"}
→ Server system:    {"type": "system", "message": "Alice joined!"}
→ User list:        {"type": "userlist", "users": ["Alice", "Bob"]}
```

---

## ⚖️ License

MIT License — free to use, modify, and distribute.

---

## 🙏 Credits

Built and maintained by **Koza AI Agent** — an autonomous coding assistant.
