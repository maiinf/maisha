#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ia_3d_client.py
Cliente y herramienta CLI para convertir Concept Art (2D) en modelos 3D (.glb)
utilizando las APIs de Meshy AI y Tripo3D.

Uso:
  python herramientas/ia_3d_client.py --imagen <ruta_imagen> --salida <ruta_glb> [--servicio meshy|tripo] [--api-key <clave>]
"""

import os
import sys
import time
import json
import base64
import argparse
import urllib.request
import urllib.error

# Intentar cargar variables desde .env si existe
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

MESHY_API_URL = "https://api.meshy.ai/openapi/v1/image-to-3d"
TRIPO_API_URL = "https://api.tripo3d.ai/v2/openapi/task"

def imagen_a_data_uri(ruta_imagen):
    """Convierte un archivo de imagen local a un data URI base64."""
    with open(ruta_imagen, "rb") as f:
        data = f.read()
    ext = os.path.splitext(ruta_imagen)[1].lower().lstrip(".")
    mime = "image/png" if ext == "png" else "image/jpeg"
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def generar_con_meshy(ruta_imagen, ruta_salida, api_key):
    """Genera un modelo 3D usando la API de Meshy AI."""
    print(f"[*] Iniciando generación Image-to-3D con Meshy AI...")
    data_uri = imagen_a_data_uri(ruta_imagen)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "image_url": data_uri,
        "enable_pbr": True,
        "surface_mode": "hard",  # estilo diorama / estilizado
        "ai_model": "meshy-4"
    }
    
    req = urllib.request.Request(MESHY_API_URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            task_id = data.get("result")
    except urllib.error.HTTPError as e:
        print(f"[!] Error de API Meshy: {e.code} - {e.read().decode('utf-8')}")
        return False
        
    print(f"[+] Tarea creada en Meshy con ID: {task_id}")
    print("[*] Esperando a que el modelo 3D termine de hornearse...")
    
    task_url = f"https://api.meshy.ai/openapi/v1/image-to-3d/{task_id}"
    while True:
        time.sleep(5)
        req_check = urllib.request.Request(task_url, headers=headers)
        try:
            with urllib.request.urlopen(req_check) as resp:
                status_data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[*] Esperando respuesta ({e})...")
            continue
            
        status = status_data.get("status")
        progress = status_data.get("progress", 0)
        print(f"  -> Progreso: {progress}% ({status})")
        
        if status == "SUCCEEDED":
            glb_url = status_data.get("model_urls", {}).get("glb")
            if not glb_url:
                print("[!] Error: No se encontró URL de descarga del .glb")
                return False
            print(f"[+] Descargando archivo .glb desde {glb_url}...")
            os.makedirs(os.path.dirname(os.path.abspath(ruta_salida)), exist_ok=True)
            urllib.request.urlretrieve(glb_url, ruta_salida)
            print(f"[✓] Modelo 3D guardado con éxito en: {ruta_salida}")
            return True
        elif status in ["FAILED", "EXPIRED"]:
            print(f"[!] La tarea en Meshy falló: {status_data.get('task_error')}")
            return False

def generar_con_tripo(ruta_imagen, ruta_salida, api_key):
    """Genera un modelo 3D usando la API de Tripo3D."""
    print(f"[*] Iniciando generación Image-to-3D con Tripo3D...")
    data_uri = imagen_a_data_uri(ruta_imagen)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "type": "image_to_model",
        "file": {
            "type": "png" if ruta_imagen.lower().endswith(".png") else "jpg",
            "data": data_uri
        }
    }
    
    req = urllib.request.Request(TRIPO_API_URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            task_id = data.get("data", {}).get("task_id")
    except urllib.error.HTTPError as e:
        print(f"[!] Error de API Tripo: {e.code} - {e.read().decode('utf-8')}")
        return False
        
    print(f"[+] Tarea creada en Tripo con ID: {task_id}")
    print("[*] Esperando a que el modelo 3D termine de hornearse...")
    
    task_url = f"https://api.tripo3d.ai/v2/openapi/task/{task_id}"
    while True:
        time.sleep(5)
        req_check = urllib.request.Request(task_url, headers=headers)
        try:
            with urllib.request.urlopen(req_check) as resp:
                status_data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[*] Esperando respuesta ({e})...")
            continue
            
        task_info = status_data.get("data", {})
        status = task_info.get("status")
        progress = task_info.get("progress", 0)
        print(f"  -> Progreso: {progress}% ({status})")
        
        if status == "success":
            glb_url = task_info.get("output", {}).get("model")
            if not glb_url:
                print("[!] Error: No se encontró URL de descarga del .glb")
                return False
            print(f"[+] Descargando archivo .glb desde {glb_url}...")
            os.makedirs(os.path.dirname(os.path.abspath(ruta_salida)), exist_ok=True)
            urllib.request.urlretrieve(glb_url, ruta_salida)
            print(f"[✓] Modelo 3D guardado con éxito en: {ruta_salida}")
            return True
        elif status in ["failed", "cancelled"]:
            print(f"[!] La tarea en Tripo falló.")
            return False

def main():
    parser = argparse.ArgumentParser(description="Conversor de Concept Art a Modelo 3D (.glb) con Meshy o Tripo.")
    parser.add_argument("--imagen", required=True, help="Ruta a la imagen de referencia (PNG o JPG)")
    parser.add_argument("--salida", required=True, help="Ruta donde se guardará el modelo .glb resultante")
    parser.add_argument("--servicio", choices=["meshy", "tripo"], default="meshy", help="Servicio a utilizar (meshy o tripo)")
    parser.add_argument("--api-key", help="API Key opcional (si no se proporciona se buscará en MESHY_API_KEY o TRIPO_API_KEY)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.imagen):
        print(f"[!] Archivo de imagen no encontrado: {args.imagen}")
        sys.exit(1)
        
    api_key = args.api_key
    if not api_key:
        var_name = "MESHY_API_KEY" if args.servicio == "meshy" else "TRIPO_API_KEY"
        api_key = os.environ.get(var_name)
        
    if not api_key:
        print(f"[!] Falta la clave de API para {args.servicio.capitalize()}.")
        print(f"    Puedes definirla en la variable de entorno {var_name}")
        print(f"    o añadirla en un archivo .env en la raíz del proyecto.")
        sys.exit(1)
        
    if args.servicio == "meshy":
        ok = generar_con_meshy(args.imagen, args.salida, api_key)
    else:
        ok = generar_con_tripo(args.imagen, args.salida, api_key)
        
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
