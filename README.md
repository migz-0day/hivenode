# Hive
ssh honeypot
low-interaction SSH honeypot built with paramiko

**Captures :** IP,username,password,time and stores in a json file

## How to run
pip3 install -r requirements.txt
python3 lapot.py

Test: ssh -p 2222 root@127.0.0.1

## Logs
logs/attacks.json shows attacker attempts
