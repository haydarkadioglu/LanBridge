import socket
import threading
import json
import sys
import os
import msvcrt
import time

# Renk kodlari
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
        """Kullanici adina gore renk sec"""
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
        
        # Windows console renk ayari
        if os.name == "nt":
            os.system("color")
    
    def connect(self):
        """Sunucuya baglan"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)
            self.sock.connect((self.server_ip, self.server_port))
            self.sock.settimeout(None)
            
            # Kullanici adi gonder
            self.sock.sendall(json.dumps({"username": self.username}).encode("utf-8"))
            
            # Hosgeldin mesajini bekle
            data = self.sock.recv(65535)
            init_msg = json.loads(data.decode("utf-8"))
            if init_msg.get("type") == "userlist":
                self.users = init_msg.get("users", [])
                self.messages.append(("SISTEM", "SERVER", init_msg.get("message", ""), "system"))
            
            return True
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            print(f"{Colors.RED}[HATA] Baglanti basarisiz: {e}{Colors.RESET}")
            return False
    
    def listen(self):
        """Sunucudan mesajlari dinle"""
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
                        "SISTEM",
                        msg.get("message", ""),
                        "system"
                    ))
                    self.refresh_display()
                
                elif msg.get("type") == "userlist":
                    self.users = msg.get("users", [])
                
                elif msg.get("type") == "pong":
                    pass  # ping yaniti
                    
            except (ConnectionResetError, ConnectionAbortedError, json.JSONDecodeError):
                break
        
        self.running = False
        self.refresh_display()
        # Baglanti koptu bilgisi
        print(f"\n{Colors.RED}[!] Sunucu baglantisi koptu.{Colors.RESET}")
    
    def refresh_display(self):
        """Ekrani yenile - altta yazma alani, uste mesajlar"""
        if not self.input_active:
            return
            
        # Konsol boyutunu al
        try:
            cols = os.get_terminal_size().columns
            rows = os.get_terminal_size().lines
        except:
            cols = 80
            rows = 24
        
        # Imleci yukari cek ve temizle
        sys.stdout.write("\033[H")  # imlec en uste
        sys.stdout.write("\033[J")  # asagisini temizle
        
        # Baslik
        title = f" LAN CHAT - [{self.username}] - Sunucu: {self.server_ip}:{self.server_port} "
        sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}{'=' * cols}{Colors.RESET}\n")
        sys.stdout.write(f"{Colors.BOLD}{Colors.WHITE}{title:<{cols}}{Colors.RESET}\n")
        sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}{'=' * cols}{Colors.RESET}\n")
        
        # Online kullanicilar
        user_str = ", ".join(self.users) if self.users else "Henuz kimse yok"
        sys.stdout.write(f"{Colors.GRAY}[Online: {len(self.users)}] {user_str}{Colors.RESET}\n")
        sys.stdout.write(f"{Colors.BOLD}{Colors.CYAN}{'-' * cols}{Colors.RESET}\n")
        
        # Mesaj alani (kalan satirlar - 4 satir ayir)
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
        
        # Imleci en alta indir
        input_prompt = f"{Colors.GREEN}>>{Colors.RESET} "
        sys.stdout.write(f"\n{Colors.CYAN}{'-' * cols}{Colors.RESET}\n")
        sys.stdout.write(f"{input_prompt}{self.input_buffer}")
        sys.stdout.flush()
    
    def send_message(self, text):
        """Mesaj gonder"""
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
        """Ana dongu"""
        if not self.connect():
            input(f"\n{Colors.YELLOW}Devam etmek icin Enter'a basin...{Colors.RESET}")
            return
        
        # Dinleme threadi
        listener = threading.Thread(target=self.listen, daemon=True)
        listener.start()
        
        # Ilk ekrani goster
        time.sleep(0.1)
        self.refresh_display()
        
        # Klavye girdisi
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
                        if ord(char) >= 32:  # Yazdirilabilir karakter
                            self.input_buffer += char
                            self.refresh_display()
                
                time.sleep(0.05)
        
        except KeyboardInterrupt:
            pass
        finally:
            self.running = False
            if self.sock:
                self.sock.close()
            print(f"\n{Colors.YELLOW}[*] Cikis yapildi.{Colors.RESET}")

def find_server():
    """LAN'da server ara (broadcast ile)"""
    print(f"{Colors.CYAN}[*] LAN'da sunucu araniyor...{Colors.RESET}")
    # Basit yaklasim: dogrudan IP sor
    return None

def main():
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
    server_ip = input(f"{Colors.YELLOW}Sunucu IP'si{Colors.RESET} (bos = localhost): ").strip()
    if not server_ip:
        server_ip = "127.0.0.1"
    
    # Kullanici adi
    default_user = os.getlogin()
    username = input(f"{Colors.YELLOW}Kullanici adin{Colors.RESET} (bos = {default_user}): ").strip()
    if not username:
        username = default_user
    
    print(f"\n{Colors.GREEN}[*] {server_ip}:12345 sunucusuna baglaniliyor...{Colors.RESET}\n")
    
    client = LANChatClient(server_ip, 12345, username)
    client.run()

if __name__ == "__main__":
    main()