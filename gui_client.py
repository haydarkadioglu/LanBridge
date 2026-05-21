"""
LanBridge GUI Client
tkinter-based graphical interface for LAN messaging
"""

import socket
import threading
import json
import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox


class LanBridgeGUI:
    """GUI Client for LanBridge chat application."""

    COLORS = {
        "bg_dark": "#1a1a2e",
        "bg_medium": "#16213e",
        "bg_light": "#0f3460",
        "accent": "#e94560",
        "accent2": "#533483",
        "text": "#eaeaea",
        "text_dim": "#8899aa",
        "green": "#2ecc71",
        "yellow": "#f1c40f",
        "orange": "#e67e22",
        "cyan": "#00d2ff",
        "user_colors": ["#2ecc71", "#00d2ff", "#f1c40f", "#e67e22", "#9b59b6", "#1abc9c", "#e74c3c", "#3498db"]
    }

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LanBridge 🚀")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        self.root.configure(bg=self.COLORS["bg_dark"])

        # State
        self.sock = None
        self.username = None
        self.server_ip = None
        self.server_port = 12345
        self.running = False
        self.users = []
        self.message_log = []  # [(time, sender, msg, type)]

        self.setup_styles()
        self.build_connection_screen()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background=self.COLORS["bg_dark"])
        style.configure("TLabel", background=self.COLORS["bg_dark"], foreground=self.COLORS["text"])
        style.configure("TButton", background=self.COLORS["accent"], foreground="white",
                        borderwidth=0, focusthickness=0, font=("Segoe UI", 10, "bold"))
        style.map("TButton",
                  background=[("active", self.COLORS["accent2"])],
                  foreground=[("active", "white")])

        style.configure("Accent.TButton", background=self.COLORS["accent"], foreground="white")
        style.configure("Connect.TButton", background=self.COLORS["green"], foreground="white")
        style.map("Connect.TButton",
                  background=[("active", "#27ae60")])

    def build_connection_screen(self):
        """Build the initial connection/join screen."""
        self.clear_window()

        main = tk.Frame(self.root, bg=self.COLORS["bg_dark"])
        main.pack(expand=True, fill="both")

        # Center container
        center = tk.Frame(main, bg=self.COLORS["bg_medium"], padx=40, pady=40)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / Title
        title = tk.Label(center, text="🌉 LanBridge",
                        font=("Segoe UI", 28, "bold"),
                        bg=self.COLORS["bg_medium"],
                        fg=self.COLORS["cyan"])
        title.pack(pady=(0, 5))

        subtitle = tk.Label(center, text="Real-time LAN Messaging",
                           font=("Segoe UI", 11),
                           bg=self.COLORS["bg_medium"],
                           fg=self.COLORS["text_dim"])
        subtitle.pack(pady=(0, 25))

        # Server IP
        ip_frame = tk.Frame(center, bg=self.COLORS["bg_medium"])
        ip_frame.pack(fill="x", pady=5)

        tk.Label(ip_frame, text="Server IP",
                font=("Segoe UI", 10),
                bg=self.COLORS["bg_medium"],
                fg=self.COLORS["text"]).pack(anchor="w")

        self.ip_var = tk.StringVar(value="127.0.0.1")
        ip_entry = tk.Entry(ip_frame, textvariable=self.ip_var,
                           font=("Segoe UI", 11),
                           bg=self.COLORS["bg_dark"],
                           fg=self.COLORS["text"],
                           insertbackground=self.COLORS["text"],
                           relief="flat", bd=8, width=25)
        ip_entry.pack(fill="x", pady=(3, 0))
        ip_entry.bind("<Return>", lambda e: username_entry.focus())

        # Username
        user_frame = tk.Frame(center, bg=self.COLORS["bg_medium"])
        user_frame.pack(fill="x", pady=5)

        tk.Label(user_frame, text="Username",
                font=("Segoe UI", 10),
                bg=self.COLORS["bg_medium"],
                fg=self.COLORS["text"]).pack(anchor="w")

        import os
        self.user_var = tk.StringVar(value=os.getlogin())
        username_entry = tk.Entry(user_frame, textvariable=self.user_var,
                                 font=("Segoe UI", 11),
                                 bg=self.COLORS["bg_dark"],
                                 fg=self.COLORS["text"],
                                 insertbackground=self.COLORS["text"],
                                 relief="flat", bd=8, width=25)
        username_entry.pack(fill="x", pady=(3, 0))
        username_entry.bind("<Return>", lambda e: self.do_connect())

        # Connect button
        self.connect_btn = tk.Button(center, text="🚀 Connect to Server",
                                    font=("Segoe UI", 12, "bold"),
                                    bg=self.COLORS["green"],
                                    fg="white",
                                    activebackground="#27ae60",
                                    activeforeground="white",
                                    relief="flat", bd=0,
                                    cursor="hand2",
                                    padx=20, pady=10,
                                    command=self.do_connect)
        self.connect_btn.pack(fill="x", pady=(20, 0))

        # Status
        self.status_label = tk.Label(center, text="",
                                    font=("Segoe UI", 9),
                                    bg=self.COLORS["bg_medium"],
                                    fg=self.COLORS["text_dim"])
        self.status_label.pack(pady=(10, 0))

        # Hover effects
        for btn in [self.connect_btn]:
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#27ae60" if b == self.connect_btn else None))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.COLORS["green"] if b == self.connect_btn else None))

    def build_chat_screen(self):
        """Build the main chat interface."""
        self.clear_window()

        # Main container
        main = tk.Frame(self.root, bg=self.COLORS["bg_dark"])
        main.pack(expand=True, fill="both")

        # --- Top bar ---
        top_bar = tk.Frame(main, bg=self.COLORS["bg_medium"], height=50)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        tk.Label(top_bar, text=f"🌉 LanBridge",
                font=("Segoe UI", 14, "bold"),
                bg=self.COLORS["bg_medium"],
                fg=self.COLORS["cyan"]).pack(side="left", padx=15, pady=10)

        self.user_count_label = tk.Label(top_bar, text="👤 0 online",
                                        font=("Segoe UI", 10),
                                        bg=self.COLORS["bg_medium"],
                                        fg=self.COLORS["text_dim"])
        self.user_count_label.pack(side="left", padx=10)

        tk.Label(top_bar, text=f"@{self.username}",
                font=("Segoe UI", 10),
                bg=self.COLORS["bg_medium"],
                fg=self.COLORS["green"]).pack(side="right", padx=15, pady=10)

        disconnect_btn = tk.Button(top_bar, text="✕ Disconnect",
                                  font=("Segoe UI", 9),
                                  bg=self.COLORS["accent"],
                                  fg="white",
                                  activebackground="#c0392b",
                                  activeforeground="white",
                                  relief="flat", bd=0,
                                  cursor="hand2",
                                  padx=10,
                                  command=self.do_disconnect)
        disconnect_btn.pack(side="right", padx=(0, 10), pady=10)

        # --- Content area (chat + sidebar) ---
        content = tk.Frame(main, bg=self.COLORS["bg_dark"])
        content.pack(expand=True, fill="both", padx=5, pady=(5, 0))

        # --- Chat area (left) ---
        chat_frame = tk.Frame(content, bg=self.COLORS["bg_medium"])
        chat_frame.pack(side="left", expand=True, fill="both", padx=(0, 5))

        # Chat display
        self.chat_display = tk.Text(chat_frame,
                                    bg=self.COLORS["bg_dark"],
                                    fg=self.COLORS["text"],
                                    font=("Consolas", 10),
                                    relief="flat", bd=5,
                                    wrap="word",
                                    state="disabled",
                                    cursor="arrow")
        self.chat_display.pack(expand=True, fill="both", padx=5, pady=(5, 0))

        # Scrollbar for chat
        chat_scroll = tk.Scrollbar(chat_frame, command=self.chat_display.yview,
                                  bg=self.COLORS["bg_medium"],
                                  troughcolor=self.COLORS["bg_dark"],
                                  width=8)
        chat_scroll.pack(side="right", fill="y", pady=(5, 0))
        self.chat_display.configure(yscrollcommand=chat_scroll.set)

        # Tag configurations for chat
        self.chat_display.tag_config("system", foreground=self.COLORS["text_dim"], font=("Consolas", 9, "italic"))
        self.chat_display.tag_config("time", foreground=self.COLORS["text_dim"], font=("Consolas", 8))
        self.chat_display.tag_config("me", foreground=self.COLORS["cyan"], font=("Consolas", 10, "bold"))
        self.chat_display.tag_config("server", foreground=self.COLORS["orange"], font=("Consolas", 10, "bold"))

        # --- User list sidebar (right) ---
        self.sidebar = tk.Frame(content, bg=self.COLORS["bg_medium"], width=180)
        self.sidebar.pack(side="right", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="🟢 Online Users",
                font=("Segoe UI", 10, "bold"),
                bg=self.COLORS["bg_medium"],
                fg=self.COLORS["text"]).pack(pady=(10, 5))

        self.users_listbox = tk.Listbox(self.sidebar,
                                        bg=self.COLORS["bg_dark"],
                                        fg=self.COLORS["green"],
                                        font=("Segoe UI", 10),
                                        relief="flat", bd=5,
                                        selectbackground=self.COLORS["accent"],
                                        selectforeground="white",
                                        highlightthickness=0,
                                        activestyle="none")
        self.users_listbox.pack(expand=True, fill="both", padx=8, pady=(0, 10))

        # --- Input area (bottom) ---
        input_area = tk.Frame(main, bg=self.COLORS["bg_medium"], height=60)
        input_area.pack(fill="x", side="bottom", pady=(5, 0))
        input_area.pack_propagate(False)

        self.msg_var = tk.StringVar()
        self.msg_entry = tk.Entry(input_area, textvariable=self.msg_var,
                                 font=("Segoe UI", 12),
                                 bg=self.COLORS["bg_dark"],
                                 fg=self.COLORS["text"],
                                 insertbackground=self.COLORS["text"],
                                 relief="flat", bd=8)
        self.msg_entry.pack(side="left", expand=True, fill="x", padx=(10, 5), pady=10)
        self.msg_entry.bind("<Return>", lambda e: self.send_message())

        send_btn = tk.Button(input_area, text="➤ Send",
                            font=("Segoe UI", 11, "bold"),
                            bg=self.COLORS["accent"],
                            fg="white",
                            activebackground=self.COLORS["accent2"],
                            activeforeground="white",
                            relief="flat", bd=0,
                            cursor="hand2",
                            padx=20,
                            command=self.send_message)
        send_btn.pack(side="right", padx=(0, 10), pady=10)

        # Focus entry
        self.msg_entry.focus()

    def clear_window(self):
        """Remove all widgets from the window."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def do_connect(self):
        """Attempt to connect to the server."""
        ip = self.ip_var.get().strip()
        username = self.user_var.get().strip()

        if not ip:
            self.status_label.config(text="❌ Please enter a server IP", fg=self.COLORS["accent"])
            return
        if not username:
            self.status_label.config(text="❌ Please enter a username", fg=self.COLORS["accent"])
            return

        self.status_label.config(text="🔄 Connecting...", fg=self.COLORS["yellow"])
        self.connect_btn.config(state="disabled")

        # Connect in a thread
        self.server_ip = ip
        self.username = username
        threading.Thread(target=self._connect_thread, daemon=True).start()

    def _connect_thread(self):
        """Threaded connection logic."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((self.server_ip, self.server_port))
            sock.settimeout(None)

            # Send username
            sock.sendall(json.dumps({"username": self.username}).encode("utf-8"))

            # Wait for welcome
            data = sock.recv(65535)
            init_msg = json.loads(data.decode("utf-8"))

            self.sock = sock
            self.running = True

            if init_msg.get("type") == "userlist":
                self.users = init_msg.get("users", [])
                welcome_msg = init_msg.get("message", "")

            # Build UI on main thread
            self.root.after(0, self._on_connected)

        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            self.root.after(0, lambda: self._on_connect_failed(str(e)))

    def _on_connected(self):
        """Called on main thread after successful connection."""
        self.build_chat_screen()
        self.add_system_message(f"✅ Connected to {self.server_ip}:{self.server_port}")
        self.add_system_message(f"👋 Welcome {self.username}!")
        self.user_count_label.config(text=f"👤 {len(self.users)} online")
        self.update_users_listbox()

        # Start listener thread
        threading.Thread(target=self._listen_thread, daemon=True).start()

    def _on_connect_failed(self, error):
        """Called on main thread after connection failure."""
        self.status_label.config(text=f"❌ Connection failed: {error}", fg=self.COLORS["accent"])
        self.connect_btn.config(state="normal")

    def _listen_thread(self):
        """Background thread to receive messages."""
        while self.running:
            try:
                data = self.sock.recv(65535)
                if not data:
                    break

                msg = json.loads(data.decode("utf-8"))
                msg_type = msg.get("type", "")

                if msg_type == "message":
                    self.root.after(0, self.add_message,
                                   msg.get("sender", ""),
                                   msg.get("message", ""),
                                   msg.get("time", ""))

                elif msg_type == "system":
                    self.root.after(0, self.add_system_message,
                                   msg.get("message", ""))

                elif msg_type == "userlist":
                    self.users = msg.get("users", [])
                    self.root.after(0, self.update_users_listbox)

            except (ConnectionResetError, ConnectionAbortedError, json.JSONDecodeError, OSError):
                break

        self.running = False
        self.root.after(0, self._on_disconnected)

    def send_message(self):
        """Send a message from the input field."""
        text = self.msg_var.get().strip()
        if not text or not self.sock or not self.running:
            return

        try:
            self.sock.sendall(json.dumps({
                "type": "message",
                "message": text
            }).encode("utf-8"))

            # Show on local chat
            now = datetime.datetime.now().strftime("%H:%M:%S")
            self.add_message(self.username, text, now, is_self=True)
            self.msg_var.set("")
            self.msg_entry.focus()

        except:
            self.add_system_message("❌ Failed to send message")

    def add_message(self, sender, text, timestamp, is_self=False):
        """Add a message to the chat display."""
        self.chat_display.config(state="normal")

        # Timestamp
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "time")

        # Sender
        if is_self:
            self.chat_display.insert(tk.END, f"{sender}: ", "me")
        elif sender == "SERVER":
            self.chat_display.insert(tk.END, f"{sender}: ", "server")
        else:
            # Pick color for user
            color_idx = hash(sender) % len(self.COLORS["user_colors"])
            user_color = self.COLORS["user_colors"][color_idx]
            tag_name = f"user_{sender}"
            self.chat_display.tag_config(tag_name, foreground=user_color, font=("Consolas", 10, "bold"))
            self.chat_display.insert(tk.END, f"{sender}: ", tag_name)

        # Message
        self.chat_display.insert(tk.END, f"{text}\n")

        # Auto-scroll
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def add_system_message(self, text):
        """Add a system message to the chat display."""
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"  {text}\n", "system")
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def update_users_listbox(self):
        """Update the online users list."""
        self.users_listbox.delete(0, tk.END)

        # Show self first with a green dot
        self.users_listbox.insert(tk.END, f"🟢 {self.username} (you)")
        self.users_listbox.itemconfig(0, fg=self.COLORS["cyan"])

        for user in self.users:
            self.users_listbox.insert(tk.END, f"🟢 {user}")
            idx = self.users_listbox.size() - 1
            self.users_listbox.itemconfig(idx, fg=self.COLORS["green"])

        # Update user count
        if hasattr(self, 'user_count_label'):
            self.user_count_label.config(text=f"👤 {len(self.users)} online")

    def do_disconnect(self):
        """Disconnect from the server."""
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        self.build_connection_screen()

    def _on_disconnected(self):
        """Handle unexpected disconnection."""
        if hasattr(self, 'chat_display'):
            if self.chat_display.winfo_exists():
                self.add_system_message("🔴 Disconnected from server")
                self.add_system_message("💡 Click 'Disconnect' to return to the connection screen")

    def on_close(self):
        """Handle window close event."""
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.root.destroy()

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = LanBridgeGUI()
    app.run()
