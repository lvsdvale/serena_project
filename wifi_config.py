import os
import time
import json
import bluetooth
import subprocess
import socket

def is_connected():
    """Verifica se há uma conexão Wi-Fi ativa."""
    try:
        # Tenta resolver um host externo (Google DNS)
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

def update_wifi(ssid, password):
    config = f'''
network={{
    ssid="{ssid}"
    psk="{password}"
}}
'''
    print("[*] Atualizando Wi-Fi...")
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as f:
        f.write(config)

    subprocess.run(["sudo", "wpa_cli", "-i", "wlan0", "reconfigure"])
    print("[+] Wi-Fi atualizado, tentando conectar...")

def start_bt_wifi_config():
    print("[*] Iniciando modo de configuração via Bluetooth...")
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    port = 1
    server_sock.bind(("", port))
    server_sock.listen(1)

    print(f"[*] Aguardando conexão Bluetooth na porta {port}...")
    client_sock, client_info = server_sock.accept()
    print(f"[+] Conexão recebida de {client_info}")

    try:
        data = client_sock.recv(1024).decode("utf-8")
        print(f"[>] Dados recebidos: {data}")
        credentials = json.loads(data)
        update_wifi(credentials["ssid"], credentials["senha"])
        client_sock.send("Wi-Fi configurado com sucesso.\n".encode())
    except Exception as e:
        print(f"[!] Erro: {e}")
        client_sock.send(f"Erro: {str(e)}\n".encode())
    finally:
        client_sock.close()
        server_sock.close()

def ensure_wifi_connected():
    print("[*] Verificando conexão Wi-Fi...")
    if is_connected():
        print("[✓] Conectado ao Wi-Fi.")
        return

    print("[!] Sem conexão. Iniciando modo de configuração Bluetooth...")
    start_bt_wifi_config()

    # Espera o Wi-Fi reconectar
    time.sleep(10)

    if is_connected():
        print("[✓] Wi-Fi configurado com sucesso.")
    else:
        print("[x] Falha ao conectar. Verifique as credenciais.")
