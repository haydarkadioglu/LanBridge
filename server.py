import socket
import threading
import json
import datetime

HOST = "0.0.0.0"
PORT = 12345
BUFFER = 65535

clients = {}
lock = threading.Lock()


def broadcast(sender, message, msg_type="message"):
    """Send a message to all connected clients except the sender."""
    payload = json.dumps({
        "type": msg_type,
        "sender": sender,
        "message": message,
        "time": datetime.datetime.now().strftime("%H:%M:%S")
    }).encode("utf-8")

    with lock:
        disconnected = []
        for username, (conn, addr) in clients.items():
            if username == sender:
                continue
            try:
                conn.sendall(payload)
            except:
                disconnected.append(username)

        for u in disconnected:
            del clients[u]
            print(f"[!] {u} disconnected, removed from list.")


def handle_client(conn, addr):
    """Handle an individual client connection."""
    username = None
    try:
        data = conn.recv(BUFFER)
        if not data:
            conn.close()
            return

        init_data = json.loads(data.decode("utf-8"))
        username = init_data.get("username", f"User_{addr[1]}")

        with lock:
            clients[username] = (conn, addr)

        print(f"[+] {username} connected ({addr[0]}:{addr[1]})")
        broadcast("SERVER", f"{username} joined!", "system")

        userlist = [u for u in clients.keys() if u != username]
        conn.sendall(json.dumps({
            "type": "userlist",
            "users": userlist,
            "message": f"Welcome {username}! {len(userlist)} user(s) online."
        }).encode("utf-8"))

        while True:
            data = conn.recv(BUFFER)
            if not data:
                break

            msg = json.loads(data.decode("utf-8"))

            if msg.get("type") == "message":
                text = msg.get("message", "").strip()
                if text:
                    print(f"[{username}]: {text}")
                    broadcast(username, text, "message")

            elif msg.get("type") == "ping":
                conn.sendall(json.dumps({"type": "pong"}).encode("utf-8"))

    except (ConnectionResetError, ConnectionAbortedError, json.JSONDecodeError, BrokenPipeError):
        pass
    finally:
        with lock:
            if username and username in clients:
                del clients[username]
        if username:
            broadcast("SERVER", f"{username} left.", "system")
        conn.close()
        print(f"[-] {username or addr} disconnected.")


def main():
    """Main server entry point."""
    print("=" * 50)
    print("  LAN CHAT SERVER v1.0")
    print("=" * 50)
    print(f"  Listening on: {HOST}:{PORT}")
    print(f"  Hostname    : {socket.gethostname()}")
    print(f"  Local IP    : {socket.gethostbyname(socket.gethostname())}")
    print("=" * 50)
    print("  Press Ctrl+C to stop.\n")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)

    print("[*] Waiting for clients...\n")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\n[*] Shutting down server...")
    finally:
        server.close()
        print("[*] Server closed.")


if __name__ == "__main__":
    main()
