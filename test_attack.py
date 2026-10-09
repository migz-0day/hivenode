 # GNU nano 8.7.1                                                                                            stillhoney/test_attack.py *                                                                                                    
import paramiko

client =paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
  client.connect('127.0.0.1',port=2222,username='root',password='password123',timeout=5)
except Exception as e:
  print(f"Attack sent,server response {e}")