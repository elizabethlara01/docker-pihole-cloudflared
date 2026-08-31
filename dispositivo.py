"""
Simulador de Tráfico IoT y Telemetría para Pi-hole
-------------------------------------------------
Este script simula las peticiones DNS que realizan diversos dispositivos IoT
(Smart TVs, electrodomésticos inteligentes, trackers) y sitios de prueba,
enviando las consultas directamente a tu servidor Pi-hole (127.0.0.1).
"""

import subprocess
import time
import sys

# Definición de dominios a simular por categoría
IOT_DEVICES = [
    # Telemetría Smart TV Samsung & LG
    {"device": "Samsung Smart TV", "domain": "lcprd1.samsungcloudsolution.net", "type": "Telemetría"},
    {"device": "Samsung Smart TV", "domain": "log-config.samsungcloudsolution.net", "type": "Rastreo"},
    {"device": "LG WebOS TV", "domain": "sng.smartshare.lgtvcommon.com", "type": "Telemetría"},
    
    # Domótica Xiaomi & Tuya
    {"device": "Aspiradora Xiaomi", "domain": "api.ad.xiaomi.com", "type": "Publicidad/Rastreo"},
    {"device": "Enchufe Inteligente", "domain": "tracking.miui.com", "type": "Telemetría"},
    
    # Streaming & Streaming Sticks (Roku / Amazon Fire)
    {"device": "Roku Streaming Stick", "domain": "logs.roku.com", "type": "Analytics"},
    {"device": "Amazon Fire TV", "domain": "device-metrics-us.amazon.com", "type": "Telemetría"},

    # Sitios maliciosos / Phishing (para probar listas de seguridad)
    {"device": "Navegador Web", "domain": "triple-x-stream.com", "type": "Sitio Sospechoso"},
    
    # Tráfico Legítimo
    {"device": "Portátil Work", "domain": "google.com", "type": "Legítimo"},
    {"device": "Portátil Work", "domain": "github.com", "type": "Legítimo"},
    {"device": "Portátil Work", "domain": "wikipedia.org", "type": "Legítimo"},
]

# Códigos de color ANSI para la consola
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def query_dns_powershell(domain, dns_server="127.0.0.1"):
    """
    Ejecuta una consulta DNS contra el servidor especificado usando Resolve-DnsName en PowerShell.
    """
    cmd = [
        "powershell", "-Command",
        f"try {{ (Resolve-DnsName -Name '{domain}' -Server '{dns_server}' -ErrorAction Stop).IPAddress }} catch {{ 'BLOCKED_OR_FAILED' }}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        output = result.stdout.strip()
        if not output or "BLOCKED_OR_FAILED" in output or "0.0.0.0" in output:
            return None, "0.0.0.0 (Bloqueado)"
        # Si devuelve una o más IPs
        ips = output.splitlines()
        return ips[0], ips[0]
    except Exception as e:
        return None, f"Error: {e}"

def main():
    print(f"{BOLD}{CYAN}======================================================{RESET}")
    print(f"{BOLD}{CYAN}   SIMULADOR DE TRÁFICO IoT & TELEMETRÍA (PI-HOLE)    {RESET}")
    print(f"{BOLD}{CYAN}======================================================{RESET}\n")
    print(f"Enviando consultas DNS al servidor local: {BOLD}127.0.0.1:53{RESET}\n")
    
    blocked_count = 0
    allowed_count = 0
    
    for item in IOT_DEVICES:
        device = item["device"]
        domain = item["domain"]
        traffic_type = item["type"]
        
        print(f"[{YELLOW}{device}{RESET}] Consultando {BOLD}{domain}{RESET} ({traffic_type})...")
        
        ip, status_str = query_dns_powershell(domain)
        
        if ip is None or ip == "0.0.0.0":
            blocked_count += 1
            print(f"  └─► Estado: {BOLD}{RED}[BLOQUEADO 🛡️]{RESET} -> Resp: {status_str}")
        else:
            allowed_count += 1
            print(f"  └─► Estado: {BOLD}{GREEN}[PERMITIDO 🌐]{RESET} -> IP: {ip}")
            
        print("-" * 54)
        time.sleep(0.8)  # Pequeña pausa para simular tráfico real

    total = len(IOT_DEVICES)
    block_rate = (blocked_count / total) * 100 if total > 0 else 0

    print(f"\n{BOLD}{CYAN}======================================================{RESET}")
    print(f"{BOLD}RESUMEN DE RESULTADOS DE SIMULACIÓN{RESET}")
    print(f"{BOLD}{CYAN}======================================================{RESET}")
    print(f"Total de peticiones simuladas : {total}")
    print(f"Peticiones permitidas         : {GREEN}{allowed_count}{RESET}")
    print(f"Peticiones bloqueadas         : {RED}{blocked_count}{RESET}")
    print(f"Tasa de bloqueo simulada      : {BOLD}{CYAN}{block_rate:.1f}%{RESET}")
    print(f"{BOLD}{CYAN}======================================================{RESET}\n")
    print("👉 Revisa ahora tu panel de administración en http://localhost/admin para ver las métricas reflejadas en tiempo real.")

if __name__ == "__main__":
    main()