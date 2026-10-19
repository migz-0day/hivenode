#!/usr/bin/env python3
"""
Hivenode V4
you can run python test_attack.py which automates the attack with the user name root and password
password123 which you can change to any of your choice 

"""



import socket,threading,json,time,os
from datetime import datetime
import paramiko 
import requests

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

def get_loc(ip):
    if ip.startswith("127.") or ip.startswith("192.168") or ip.startswith("10."):
        return "local /kali"
    try:
        r=requests.get(f"http://ip-api.com/json{ip}?fields=country,city",timeout=2).json()
        return f"{r.get('country','?')} /{r.get('city','?')}"
    except:
        return "Unknown"

def log_attack(ip,username,password):
    entry ={"time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip":ip,
            "location":get_loc(ip),
            "username":username,
            "password":password
            }
    os.makedirs("logs",exist_ok=True)
    with open(LOG_FILE,"a") as f:
        f.write(json.dumps(entry) +"\n")
    print(f"[LOGGED] {ip}({entry['location']}) tried {username}:{password}")

class hiveServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.event=threading.Event()

    def check_channel_request(self,kind,chanid):
        return paramiko.OPEN_SUCCEEDED if kind == "session" else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self,username,password):
        log_attack(self.client_ip,username,password)
        return paramiko.AUTH_FAILED

    def get_allowed_auths(self,username):
        return "password"

def handle_client(client_socket,client_ip):
    ip=client_ip[0]
    try:
        transport= paramiko.Transport(client_socket)
        transport.add_server_key(HOST_KEY)
        server= hiveServer(client_ip)
        transport.start_server(server=server)
        channel= transport.accept(20)
        if channel:
            while transport.is_active():
                time.sleep(0.5)
    except Exception as e:
        print(f"[!]Error {ip}:{e}")
    finally:
        try: 
            transport.close()
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
    