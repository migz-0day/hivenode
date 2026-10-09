#!/usr/bin/env python3
import socket,threading,json,time,os
from datetime import datetime
import paramiko

HOST ="0.0.0.0"
PORT =2222
LOG_FILE ="logs/attacks.json"
KEY_FILE ="host.key"

banned_ips ={}
attempts ={}

if os.path.exists(KEY_FILE):
    HOST_KEY =paramiko.RSAKey(filename=KEY_FILE)
else:
    HOST_KEY =paramiko.RSAKey.generate(2048)
    HOST_KEY.write_private_key_file(KEY_FILE)
    print(f"[*] Created permanent {KEY_FILE}")

def log_attack(ip,username,password):
    entry ={"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"ip":ip,"username":username,"password":password}
    os.makedirs("logs",exist_ok=True)
    with open(LOG_FILE,"a") as f:
        f.write(json.dumps(entry) +"\n")
    print(f"[LOGGED] {ip} tried {username}:{password}")

class hiveServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip

    def check_channel_request(self,kind,chanid):
        return paramiko.OPEN_SUCCEEDED if kind == "session" else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self,username,password):
        log_attack(self.client_ip,username,password)
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self,username):
        return "password"

def handle_client(client_socket,client_ip):
    try:
        transport= paramiko.Transport(client_socket)
        transport.add_server_key(HOST_KEY)
        server= hiveServer(client_ip)
        transport.start_server(server=server)
        channel= transport.accept(20)
        if channel:
            while transport.is_active():
                time.sleep(0.5)
    except:
        pass
    finally:
        try: transport.close()
        except: pass
        client_socket.close()

def main():
    print(f"[*] Hive listening on {HOST}:{PORT} with permanent key")
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(100)
    try:
        while True:
            client,addr = sock.accept()
            ip = addr[0]
            print(f"[CONN] Connection from {ip}")
            t = threading.Thread(target=handle_client,args=(client, ip))
            t.daemon = True
            t.start()
    except KeyboardInterrupt:
        sock.close()

if __name__ == "__main__":
    main()