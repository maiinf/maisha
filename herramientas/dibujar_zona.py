"""
ZONAS INFECTADAS: «el nudo de raíces de piedra».

Giza se agarra a las raíces del mundo, les bebe la vida y las convierte en piedra. Cada zona
infectada es eso: raíces de piedra que salen de un corazón agrietado (el Núcleo), con la luz
violeta de Giza corriendo por las grietas. Al purgarla, la piedra vuelve a ser madera viva.

Uso:  python3 herramientas/dibujar_zona.py          (también lo llama construir_mapa.py)
Genera:
  arte/zonas/<mapa>_<zona>.png        el suelo de cada zona: 2 fotogramas (de piedra, viva)
  datos/zonas/<mapa>_<zona>.json      el recorrido de cada raíz (para animar la luz que corre por ellas)
  arte/zonas/<variante>/espinas.png   raíces-espina del borde: 4 alturas de 12x22
  (el Corazón de Giza, los Petrinos y Mzizi están en herramientas/dibujar_criaturas.py)

<variante> es el mundo («raiz»). Cada mundo tendrá su versión (en el agua, algas de piedra...).
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from dibujar_aldea import Lienzo, MAT, c, tira

MAT.update({
    "gris": ["Piedra 1", "Piedra 2", "Piedra 3", "Piedra 4"],
    "giza": ["Giza 1", "Giza 2", "Giza 3", "Giza 4"],
    "madera": ["Madera 1", "Madera 2", "Madera 3", "Madera 4"],
    "musgo": ["Hierba 1", "Hierba 2", "Hierba 3", "Hierba 4"],
    "brote": ["Follaje 2", "Brote 1", "Brote 2", "Maisha 4"],
    "blanco": ["Extremos 1", "Extremos 2", "Extremos 2", "Extremos 2"],
    "tierra": ["Tierra 1", "Tierra 2", "Tierra 3", "Tierra 4"],
})

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASILLA = 16


# ---------------------------------------------------------------------------
# El recorrido de las raíces (el mismo para la zona de piedra y la viva)
# ---------------------------------------------------------------------------

def forma_de(semilla):
    """La forma natural de una zona: cuánto se aleja el borde en cada dirección (armónicos 2, 3, 4 y 5).
    Devuelve [a2, a3, a4, a5, fase2, fase3, fase4, fase5]. La usa también el juego (zona_corrupta.gd)."""
    azar = random.Random(semilla * 7 + 3)
    amplitudes = [azar.uniform(0.07, 0.13), azar.uniform(0.05, 0.1), azar.uniform(0.03, 0.07), azar.uniform(0.02, 0.05)]
    fases = [azar.uniform(0, math.tau) for _ in range(4)]
    return [round(v, 4) for v in amplitudes + fases]


def factor(forma, a):
    if not forma:
        return 1.0
    return 1.0 + sum(forma[i] * math.sin((i + 2) * a + forma[i + 4]) for i in range(4))


def recorridos(rx, ry, semilla, forma=None):
    """Raíces que salen del centro hasta el borde de la zona.
    Devuelve listas de (x, y, grosor, fuera): fuera=False en los tramos que se hunden bajo tierra."""
    azar = random.Random(semilla)
    n = max(8, min(14, int((rx + ry) / 16)))
    grueso = 5.0 + min(rx, 220) / 60.0
    raices = []

    def trazar(x0, y0, a, largo_x, largo_y, g0, hundir):
        puntos = []
        fase, onda = azar.uniform(0, 6.3), azar.uniform(1.5, 3.5)
        # tramos bajo tierra: la raíz se mete en el suelo y vuelve a salir
        tramos = []
        if hundir:
            for _ in range(azar.randint(1, 2)):
                t0 = azar.uniform(0.35, 0.8)
                tramos.append((t0, t0 + azar.uniform(0.06, 0.12)))
        t, x, y = 0.0, x0, y0
        while t < 1.0:
            lado = math.sin(t * onda * 3.0 + fase) * 0.22
            nx = x + math.cos(a + lado) * largo_x * 0.01
            ny = y + math.sin(a + lado) * largo_y * 0.01
            paso = math.hypot(nx - x, ny - y)
            sub = max(1, int(paso / 0.8))
            for k in range(sub):
                u = (k + 1) / sub
                tt = t + 0.01 * u
                # grosor: se estrecha hasta la punta, con algún nudo más gordo
                g = g0 * max(0.0, 1.0 - tt) ** 0.7 + 1.0 + (0.8 if math.sin(tt * 37 + fase) > 0.93 else 0.0)
                fuera = not any(a0 <= tt <= a1 for (a0, a1) in tramos)
                puntos.append((x + (nx - x) * u, y + (ny - y) * u, g, fuera))
            x, y = nx, ny
            t += 0.01
        return puntos

    for i in range(n):
        a = i / n * math.tau + azar.uniform(-0.15, 0.15)
        fin = azar.uniform(0.86, 1.0) * factor(forma, a)
        principal = trazar(0, 0, a, rx * fin, ry * fin, grueso * azar.uniform(0.85, 1.15), True)
        raices.append(principal)
        # una o dos ramas
        for _ in range(azar.choice((0, 1, 1, 2))):
            k = int(len(principal) * azar.uniform(0.3, 0.6))
            bx, by, bg, _f = principal[k]
            b = a + azar.choice((-1, 1)) * azar.uniform(0.4, 0.75)
            largo = azar.uniform(0.2, 0.32)
            raices.append(trazar(bx, by, b, rx * largo, ry * largo, bg * 0.55, False))
    return raices


def dibujar_suelo(rx, ry, semilla, viva, forma=None):
    """El suelo de la zona: el nudo y sus raíces (de piedra o vivas), hasta el borde natural de la zona."""
    margen = 10
    fmax = max(factor(forma, k / 90 * math.tau) for k in range(90))
    W, H = int(rx * 2 * fmax + margen * 2), int(ry * 2 * fmax + margen * 2)
    cx, cy = W / 2, H / 2
    l = Lienzo(W, H)
    l.sin_contorno = {"giza", "brote", "tierra"}
    cuerpo = "madera" if viva else "gris"
    azar = random.Random(semilla + 7)
    raices = recorridos(rx, ry, semilla, forma)
    # grietas finas en el suelo entre las raíces (solo en la de piedra)
    if not viva:
        for _ in range(int((rx + ry) / 5)):
            a = azar.uniform(0, math.tau)
            t = azar.uniform(0.15, 0.9) * factor(forma, a)
            x, y = cx + math.cos(a) * rx * t, cy + math.sin(a) * ry * t
            for _ in range(azar.randint(3, 8)):
                l.px(x, y, "giza", 0)
                x += math.cos(a) + azar.choice((-0.6, 0, 0.6))
                y += math.sin(a) * 0.6 + azar.choice((-0.5, 0, 0.5))
    # montoncitos de tierra donde la raíz entra y sale del suelo
    for raiz in raices:
        for k in range(1, len(raiz)):
            if raiz[k][3] != raiz[k - 1][3]:
                x, y, g, _f = raiz[k]
                l.ovalo(cx + x, cy + y + 1, g * 0.8 + 1, g * 0.45 + 1, "tierra", plano=1)
                l.ovalo(cx + x, cy + y + 0.5, g * 0.6 + 0.5, g * 0.3 + 0.6, "tierra", plano=2)
    # cuerpo de cada raíz: sombra abajo, cuerpo, luz arriba
    for capa in ("sombra", "cuerpo", "luz"):
        for raiz in raices:
            for (x, y, g, fuera) in raiz:
                if not fuera:
                    continue
                px, py = cx + x, cy + y
                r = g / 2
                if capa == "sombra":
                    l.ovalo(px, py + 1, r, r * 0.8, cuerpo, plano=1)
                elif capa == "cuerpo":
                    l.ovalo(px, py, r, r * 0.7, cuerpo, plano=2)
                elif g > 2.4:
                    l.px(px - r * 0.25, py - r * 0.5, cuerpo, 3)
    # surcos de la corteza (anillos), la grieta de Giza o la vida que vuelve
    for n, raiz in enumerate(raices):
        for k, (x, y, g, fuera) in enumerate(raiz):
            if not fuera:
                continue
            px, py = cx + x, cy + y
            if k % 6 == 0 and g > 3:
                # un surco que cruza la raíz
                l.px(px, py + g * 0.15, cuerpo, 1)
            if viva:
                if k % 11 == 5 and g > 2.5:
                    l.px(px, py - 1, "musgo", 2)
                    l.px(px + 1, py - 1, "musgo", 3)
                if k % 17 == 9:
                    l.px(px, py - g * 0.4 - 1, "brote", 2)
            elif g > 2.8:
                # la grieta violeta, en tramos largos que se cortan
                tramo = (k + n * 7) % 26
                if tramo < 15:
                    l.px(px, py, "giza", 3 if tramo % 5 == 2 else 2)
                    l.px(px, py + 1, "giza", 0)
    # el nudo del centro: donde se juntan las raíces (el corazón va encima)
    rnx, rny = 15 + rx * 0.03, 8.5 + ry * 0.03
    l.ovalo(cx, cy + 2, rnx + 1, rny + 1, cuerpo, plano=1)
    l.ovalo(cx, cy + 1, rnx, rny, cuerpo)
    for k in range(9):
        a = k / 9 * math.tau + 0.3
        l.linea(cx + math.cos(a) * 5, cy + math.sin(a) * 3, cx + math.cos(a) * (rnx - 2), cy + 1 + math.sin(a) * (rny - 2), cuerpo, 1)
    if not viva:
        for k in range(5):
            a = k / 5 * math.tau
            l.linea(cx + math.cos(a) * 3, cy + math.sin(a) * 2, cx + math.cos(a) * (rnx - 4), cy + 1 + math.sin(a) * (rny - 3), "giza", 2)
    # piedrecitas sueltas (o brotes, si está viva)
    for _ in range(int((rx + ry) / 8)):
        a = azar.uniform(0, math.tau)
        t = math.sqrt(azar.uniform(0.05, 0.9)) * factor(forma, a)
        x, y = cx + math.cos(a) * rx * t, cy + math.sin(a) * ry * t
        if l.get(int(x), int(y)) is None and l.get(int(x) + 1, int(y)) is None:
            if viva:
                l.px(x, y, "brote", 2)
                l.px(x + 1, y - 1, "brote", 1)
            else:
                l.px(x, y, "gris", 2)
                l.px(x + 1, y, "gris", 1)
    img = l.imagen()
    return img, [[(round(x, 1), round(y, 1)) for (x, y, g, f) in raiz[::3]] for raiz in raices]


# ---------------------------------------------------------------------------
# Raíces-espina del borde (4 alturas)
# ---------------------------------------------------------------------------

def espina(alto):
    W, H = 12, 22
    l = Lienzo(W, H)
    l.sin_contorno = {"giza"}
    base = H - 2
    if alto > 0:
        # una raíz que sale del suelo curvándose hacia arriba, terminada en punta
        for j in range(alto):
            t = j / max(1, alto - 1)
            x = 6 + math.sin(t * 2.4) * 2.0 - 1
            ancho = 3.4 * (1 - t) + 0.6
            l.ovalo(x, base - j, ancho / 2 + 0.3, 0.9, "gris", plano=2 if t < 0.7 else 3)
            l.px(x - ancho / 2 + 0.5, base - j, "gris", 3 if t < 0.8 else 2)
            if 0.25 < t < 0.75 and j % 3 != 1:
                l.px(x + 0.3, base - j, "giza", 3 if j % 3 == 0 else 2)
        # una raicilla lateral
        if alto > 6:
            for j in range(alto // 3):
                l.px(9 + j // 3, base - 1 - j, "gris", 2)
    # terrón de tierra y piedra
    l.ovalo(6, base + 0.5, 4.5, 1.6, "gris", plano=1)
    l.px(4, base, "gris", 2)
    l.px(8, base, "gris", 2)
    return l.imagen()


# ---------------------------------------------------------------------------

# zonas puestas a mano en una escena (sin mapa de texto): (nombre, clave, ancho, alto en píxeles, variantes)
ZONAS_SUELTAS = [("prueba", "combate", 240, 176, 1)]     # escenas/prueba_combate.tscn
VARIANTES_PRACTICA = 3     # formas distintas de cada zona de práctica (cada partida elige una)


def zonas_de_los_mapas():
    """Todas las zonas de datos/mapas/*.json: (mapa, clave, radios en píxeles)."""
    yield from ZONAS_SUELTAS
    carpeta = os.path.join(RAIZ, "datos", "mapas")
    for nombre in sorted(os.listdir(carpeta)):
        if nombre.endswith(".json"):
            datos = json.load(open(os.path.join(carpeta, nombre), encoding="utf-8"))
            for clave, z in datos.get("zonas", {}).items():
                variantes = VARIANTES_PRACTICA if z.get("grupo") == "practica" else 1
                yield nombre[:-5], clave, z["radios"][0] * CASILLA, z["radios"][1] * CASILLA, variantes


def dibujar_zonas_de(mapa=None):
    os.makedirs(os.path.join(RAIZ, "arte", "zonas"), exist_ok=True)
    os.makedirs(os.path.join(RAIZ, "datos", "zonas"), exist_ok=True)
    for (m, clave, rx, ry, variantes) in zonas_de_los_mapas():
        if mapa and m != mapa:
            continue
        for v in range(variantes):
            nombre = f"{m}_{clave}" if variantes == 1 else f"{m}_{clave}_{v}"
            semilla = sum(ord(ch) for ch in m) * 13 + sum(ord(ch) for ch in clave) + v * 101
            forma = forma_de(semilla)
            piedra, raices = dibujar_suelo(rx, ry, semilla, False, forma)
            viva, _ = dibujar_suelo(rx, ry, semilla, True, forma)
            tira([piedra, viva]).save(os.path.join(RAIZ, "arte", "zonas", nombre + ".png"))
            with open(os.path.join(RAIZ, "datos", "zonas", nombre + ".json"), "w", encoding="utf-8") as f:
                json.dump({"raices": raices, "forma": forma}, f)
            print(f"Zona dibujada: {nombre} ({rx}x{ry})")


def dibujar_variante(variante="raiz"):
    carpeta = os.path.join(RAIZ, "arte", "zonas", variante)
    os.makedirs(carpeta, exist_ok=True)
    tira([espina(a) for a in (4, 9, 14, 20)]).save(os.path.join(carpeta, "espinas.png"))
    print("Raíces-espina de", variante)


if __name__ == "__main__":
    dibujar_variante("raiz")
    dibujar_zonas_de()
