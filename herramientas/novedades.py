# -*- coding: utf-8 -*-
"""
Novedades del otro agente desde la última vez que miraste.

Claude y Gemini trabajan a la vez en Maisha. En vez de confirmar cada cambio, cada uno lanza esto al
empezar y ve en pocas líneas qué ha hecho el otro:

    python herramientas/novedades.py claude     (lo lanza Claude: enseña lo de Gemini)
    python herramientas/novedades.py gemini     (lo lanza Gemini: enseña lo de Claude)

Enseña:
  - los commits nuevos del otro (en este repositorio, en todas sus ramas, y en la carpeta
    maisha-revision si existe), reconocidos por el prefijo [claude] / [gemini] del mensaje;
  - las líneas nuevas del «Diario» de documentacion/coordinacion.md que no son tuyas;
  - los «Pedidos» abiertos para ti.
La marca de «última vez» se guarda dentro de .git, así que nunca se sube.
"""

import os
import re
import subprocess
import sys
from datetime import datetime

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OTRA_CARPETA = os.path.join(os.path.dirname(RAIZ), "maisha-revision")
TABLON = os.path.join(RAIZ, "documentacion", "coordinacion.md")


def git(carpeta, *args):
    r = subprocess.run(["git", "-C", carpeta, *args], capture_output=True, text=True, encoding="utf-8")
    return r.stdout.strip() if r.returncode == 0 else ""


def marca(yo):
    return os.path.join(git(RAIZ, "rev-parse", "--absolute-git-dir") or os.path.join(RAIZ, ".git"),
                        f"novedades_{yo}")


def commits_del_otro(carpeta, desde, yo):
    """Commits desde la fecha dada que no llevan mi prefijo."""
    salida = git(carpeta, "log", "--all", f"--since={desde}", "--format=%h|%ad|%s", "--date=format:%Y-%m-%d %H:%M")
    mios = f"[{yo}]"
    return [linea.split("|", 2) for linea in salida.splitlines()
            if linea and not linea.split("|", 2)[2].lower().startswith(mios)]


def seccion(texto, titulo):
    m = re.search(rf"^## [^\n]*{titulo}[^\n]*\n(.*?)(?=^## |\Z)", texto, re.S | re.M)
    return m.group(1) if m else ""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    yo = (sys.argv[1] if len(sys.argv) > 1 else "").lower()
    if yo not in ("claude", "gemini"):
        print(__doc__)
        return
    otro = "gemini" if yo == "claude" else "claude"
    ruta_marca = marca(yo)
    desde = open(ruta_marca, encoding="utf-8").read().strip() if os.path.exists(ruta_marca) else "1 day ago"

    print(f"=== Novedades de {otro.capitalize()} desde {desde} ===")
    commits = {}
    for carpeta in (RAIZ, OTRA_CARPETA):
        if not os.path.exists(os.path.join(carpeta, ".git")):
            continue
        for h, fecha, asunto in commits_del_otro(carpeta, desde, yo):
            commits.setdefault(h, (fecha, asunto))
    lista = sorted(commits.items(), key=lambda c: c[1][0], reverse=True)
    for h, (fecha, asunto) in lista[:12]:
        print(f"  {fecha[5:]}  {h}  {asunto[:110]}")
    if len(lista) > 12:
        print(f"  ... y {len(lista) - 12} más (git log --all)")
    if not lista:
        print("  (ningún commit nuevo)")

    if os.path.exists(TABLON):
        texto = open(TABLON, encoding="utf-8").read()
        dia = desde[:10] if re.match(r"\d{4}-\d{2}-\d{2}", desde) else ""
        diario = [l for l in seccion(texto, "Diario").splitlines()
                  if l.startswith("- ") and f"· {otro}" in l.lower() and l[2:12] >= dia]
        if diario:
            print(f"\n--- Diario de {otro.capitalize()} ---")
            for l in diario[-15:]:
                print("  " + l[2:])
        pedidos = [l for l in seccion(texto, "Pedidos").splitlines()
                   if l.startswith("- [ ]") and f"para {yo}" in l.lower()]
        print(f"\n--- Pedidos abiertos para ti ({len(pedidos)}) ---")
        for l in pedidos:
            print("  " + l[6:])

    with open(ruta_marca, "w", encoding="utf-8") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M"))


if __name__ == "__main__":
    main()
