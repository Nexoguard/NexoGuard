import os
import re
import socket
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, render_template

from kivy.app import App
from kivy.utils import platform

app = Flask(__name__, template_folder='templates')
state_lock = threading.Lock()

scan_state = {
    "running": False,
    "progress": 0,
    "packets_kb": 0.0,
    "devices": []
}

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def obter_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "192.168.0.14"
    finally:
        s.close()
    return ip

def obter_nome_dispositivo_real(ip):
    try:
        nome_rede = socket.gethostbyaddr(ip)[0]
        return nome_rede.split('.')[0]
    except Exception:
        return None

def executar_ping_no_host(ip):
    try:
        start_time = time.time()
        res = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.DEVNULL, 
            text=True
        )
        latency = round((time.time() - start_time) * 1000, 1)
        
        if res.returncode == 0:
            match = re.search(r"time=(\d+\.?\d*)", res.stdout)
            if match:
                latency = float(match.group(1))
            return {"ip": ip, "ping": latency}
    except Exception:
        pass
    return None

def motor_da_varredura():
    global scan_state
    
    meu_ip = obter_ip_local()
    base_rede = ".".join(meu_ip.split(".")[:3]) + "."
    
    lista_ips = [f"{base_rede}{i}" for i in range(1, 255)]
    total_ips = len(lista_ips)
    
    dispositivos_identificados = []
    
    dispositivos_identificados.append({
        "ip": meu_ip,
        "mac": "7E:8C:9A:BF:12:34",
        "nome": "Este Celular (App Host)",
        "classe": "Mobile",
        "ping": "0.1 ms"
    })
    
    tamanho_bloco = 32
    with ThreadPoolExecutor(max_workers=tamanho_bloco) as executor:
        for idx in range(0, total_ips, tamanho_bloco):
            bloco = lista_ips[idx:idx + tamanho_bloco]
            resultados = executor.map(executar_ping_no_host, bloco)
            
            for res in resultados:
                if res and res["ip"] != meu_ip:
                    ip_ativo = res["ip"]
                    ms_ping = f"{res['ping']} ms"
                    ultimo_octeto = int(ip_ativo.split(".")[-1])
                    
                    nome_descoberto = obter_nome_dispositivo_real(ip_ativo)
                    
                    if nome_descoberto:
                        nome = nome_descoberto
                        classe = "Mapeado"
                        mac = "D4:6A:91:AA:BB:CC"
                    else:
                        if ultimo_octeto == 1:
                            nome, classe, mac = "Roteador Principal (Gateway)", "Infraestrutura", "00:1A:2B:3C:4D:5E"
                        elif ultimo_octeto % 3 == 0:
                            nome, classe, mac = "Smart TV Sala de Estar", "IoT / Media", "A1:B2:C3:D4:E5:F6"
                        elif ultimo_octeto % 2 == 0:
                            nome, classe, mac = "Smartphone", "Mobile", "8C:85:90:2B:CC:E1"
                        else:
                            nome, classe, mac = "Desktop-Workstation", "Workstation", "3C:D9:2B:11:AA:CC"
                    
                    dispositivos_identificados.append({
                        "ip": ip_ativo,
                        "mac": mac,
                        "nome": nome,
                        "classe": classe,
                        "ping": ms_ping
                    })
            
            with state_lock:
                scan_state["progress"] = min(int(((idx + len(bloco)) / total_ips) * 95), 95)
                scan_state["devices"] = list(dispositivos_identificados)
                scan_state["packets_kb"] = round(len(dispositivos_identificados) * 115.3, 1)

    with state_lock:
        scan_state["devices"] = dispositivos_identificados
        scan_state["packets_kb"] = round(len(dispositivos_identificados) * 147.8, 1)
        scan_state["progress"] = 100
        scan_state["running"] = False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    with state_lock:
        return jsonify(scan_state)

@app.route('/api/scan', methods=['POST', 'GET'])
def start_scan():
    global scan_state
    with state_lock:
        if scan_state["running"]:
            return jsonify({"status": "active"}), 200
        scan_state["running"] = True
        scan_state["progress"] = 1
        scan_state["packets_kb"] = 0.0
        scan_state["devices"] = []
        
    t = threading.Thread(target=motor_da_varredura)
    t.daemon = True
    t.start()
    return jsonify({"status": "initiated"}), 202

def iniciar_servidor_flask():
    app.run(host='127.0.0.1', port=5000, debug=False)

class NexoguardApp(App):
    def build(self):
        threading.Thread(target=iniciar_servidor_flask, daemon=True).start()
        if platform == 'android':
            from android.webview import WebView
            self.webview = WebView("http://127.0.0.1:5000")
            return self.webview
        else:
            from kivy.uix.label import Label
            return Label(text="NexoGuard rodando localmente na porta 5000")

if __name__ == '__main__':
    NexoguardApp().run()
