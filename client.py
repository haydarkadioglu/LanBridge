import socket
import threading
import json
import sys
import os
import msvcrt
import time

# Color codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    @staticmethod
    def user_color(name):
        """Pick a color based on the username."""
        colors = [Colors.GREEN, Colors.CYAN, Colors.YELLOW, Colors.MAGENTA, Colors.BLUE]
        idx = hash(name) % len(colors)
        return colors[idx]


class LANChatClient:
    def __init__(self, server_ip, server_port=12345, username=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.username = username or f"User_{os.getlogin()}"
        self.sock = None
        self.running = True
        self.messages = []  # [(time, sender, message, type)]
        self.users = []
        self.input_buffer = ""
        self.input_active = True

        # Enable ANSI colors on Windows
        if os.name == "nt":
            os.system("color")

    def connect(self):
        """Connect to the server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)
            self.sock.connect((self.server_ip, self.server_port))
            self.sock.settimeout(None)

            # Send username
            self.sock.sendall(json.dumps({"username": self.username}).encode("utf-8"))

            # Wait for welcome message
            data = self.sock.recv(65535)
            init_msg = json.loads(data.decode("utf-8"))
            if init_msg.get("type") == "userlist":
                self.users = init_msg.get("users", [])
                self.messages.append(("SYSTEM", "SERVER", init_msg.get("message", ""), "system"))

            return True
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            print(f"{Colors.RED}[ERROR] Connection failed: {e}{Colors.RESET}")
            return False

    def listen(self):
        """Listen for messages from the server."""
        while self.running:
            try:
                data = self.sock.recv(65535)
                if not data:
                    break

                msg = json.loads(data.decode("utf-8"))

                if msg.get("type") == "message":
                    self.messages.append((
                        msg.get("time", ""),
                        msg.get("sender", ""),
                        msg.get("message", ""),
                        "message"
                    ))
                    self.refresh_display()

                elif msg.get("type") == "system":
                    self.messages.append((
                        msg.get("time", ""),
                        "SYSTEM",
                        msg.get("message", ""),
                        "system"
                    ))
                    self.refresh_display()

                elif msg.get("type") == "userlist":
                    self.users = msg.get("users", [])

                elif msg.get("type") == "pong":
                    pass  # ping response

            except (ConnectionResetError, ConnectionAbortedError, json.JSONDecodeError):
                break

        self.running = False
        self.refresh_display()
        print(f"\n{Colors.RED}[!] Connection to server lost.{Colors.RESET}")

    def refresh_display(self):
        """Redraw the screen with messages at the top and input at the bottom."""
        if not self.input_active:
            return

        # Get terminal size
        try:
            cols = os.get_terminal_size().columns
            rows = os.get_terminal_size().lines
        except:
            cols = 80
            rows = 24

        # Move cursor to top and clear below
        sys.stdout.write("\033[H")
        sys.stdout.write("\033[J")

        # Header
        title = f" LAN CHAT - [{self.username}] - Server: {self.server_ip}:{self.server_port} "
        sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}{'=' * cols}{Colors.RESET}\n")
        sys.stdout.write(f"{Colors.BOLD}{Colors.WHITE}{title:<{cols}}{Colors.RESET}\n")
        sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}{'=' * cols}{Colors.RESET}\n")

        # Online users
        user_str = ", ".join(self.users) if self.users else "No one online yet"
        sys.stdout.write(f"{Colors.GRAY}[Online: {len(self.users)}] {user_str}{Colors.RESET}\n")
        sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}{'-' * cols}{Colors.RESET}\n")

        # Messages area (rows - 6 lines for UI)
        max_messages = rows - 6
        start = max(0, len(self.messages) - max_messages)

        for i in range(start, len(self.messages)):
            t, sender, msg, mtype = self.messages[i]
            remaining = cols - 4

            if mtype == "system":
                sys.stdout.write(f"{Colors.GRAY}[{t}] {msg:<{remaining}}{Colors.RESET}\n")
            else:
                c = Colors.user_color(sender)
                prefix = f"[{t}] "
                sender_part = f"{c}{sender}:{Colors.RESET} "
                msg_part = msg[:remaining - len(prefix) - len(sender_part) + 20]
                sys.stdout.write(f"{Colors.GRAY}[{t}]{Colors.RESET} {c}{sender}:{Colors.RESET} {msg_part}\n")

        # Input line at the bottom
        input_prompt = f"{Colors.GREEN}>>{Colors.RESET} "
        sys.stdout.write(f"\n{Colors.CYAN}{'-' * cols}{Colors.RESET}\n")
        sys.stdout.write(f"{input_prompt}{self.input_buffer}")
        sys.stdout.flush()

    def send_message(self, text):
        """Send a message to the server."""
        if not text.strip():
            return
        try:
            self.sock.sendall(json.dumps({
                "type": "message",
                "message": text
            }).encode("utf-8"))
        except:
            self.running = False

    def run(self):
        """Main client loop."""
        if not self.connect():
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.RESET}")
            return

        # Start listener thread
        listener = threading.Thread(target=self.listen, daemon=True)
        listener.start()

        # Initial screen render
        time.sleep(0.1)
        self.refresh_display()

        # Keyboard input loop
        try:
            while self.running:
                if msvcrt.kbhit():
                    char = msvcrt.getwch()

                    if char == '\r':  # Enter
                        self.send_message(self.input_buffer)
                        self.input_buffer = ""
                        self.refresh_display()

                    elif char == '\b':  # Backspace
                        if self.input_buffer:
                            self.input_buffer = self.input_buffer[:-1]
                        self.refresh_display()

                    elif char == '\x03':  # Ctrl+C
                        self.running = False
                        break

                    else:
                        if ord(char) >= 32:  # Printable character
                            self.input_buffer += char
                            self.refresh_display()

                time.sleep(0.05)

        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            if self.sock:
                self.sock.close()
            print(f"\n{Colors.YELLOW}[*] Exited.{Colors.RESET}")


def find_server():
    """Broadcast discovery on LAN (placeholder)."""
    print(f"{Colors.CYAN}[*] Searching for server on LAN...{Colors.RESET}")
    return None


def main():
    """Main entry point."""
    print(f"{Colors.BOLD}{Colors.MAGENTA}")
    print(r"  _    _  _____  _   _   _____ _           _   ")
    print(r" | |  | |/  __ \| \ | | /  __ \ |         | |  ")
    print(r" | |  | | / /  |  \| | | /  \/ |__   __ _| |_ ")
    print(r" | |/\| | | |  | . ` | | |   | '_ \ / _` | __|")
    print(r" \  /\  / \_/  | |\  | | \__/\ | | | (_| | |_ ")
    print(r"  \/  \/ \____/|_| \_|  \____/_| |_|\__,_|\__|")
    print(f"{Colors.RESET}")
    print(f"{Colors.CYAN}LAN Console Chat v1.0{Colors.RESET}")
    print("-" * 50)

    # Server IP
    server_ip = input(f"{Colors.YELLOW}Server IP{Colors.RESET} (blank = localhost): ").strip()
    if not server_ip:
        server_ip = "127.0.0.1"

    # Username
    default_user = os.getlogin()
    username = input(f"{Colors.YELLOW}Your username{Colors.RESET} (blank = {default_user}): ").strip()
    if not username:
        username = default_user

    print(f"\n{Colors.GREEN}[*] Connecting to {server_ip}:12345...{Colors.RESET}\n")

    client = LANChatClient(server_ip, 12345, username)
    client.run()


if __name__ == "__main__":
    main()
