"""
RELIEVE (prueba de 2.5D): calcula el «mapa de normales» de un dibujo, es decir, hacia dónde mira cada píxel.
Con él, Godot ilumina el dibujo como si tuviera volumen: la luz del sol y de los faroles resbala por los tejados,
las piedras y las copas de los árboles. No cambia nada del juego (colisiones ni movimiento): solo cómo se ve.

Cómo se calcula la altura de cada píxel:
  - objetos (con transparencia): los bordes bajan y el centro sube (un bisel suave) y, encima, lo claro sube un poco
    (el pixel art ya está pintado con la luz arriba a la izquierda, así que la claridad dice dónde está el volumen);
  - suelos (sin transparencia): solo la claridad, muy suave (piedras y matas apenas se levantan).
Luego la normal sale de la pendiente de esa altura.

Uso:  python3 herramientas/relieve.py ruta/al/dibujo.png [más dibujos...]
      python3 herramientas/relieve.py --aldea      (los dibujos de Cuna de Musgo)
      python3 herramientas/relieve.py --todo       (todos los dibujos de arte/mundos menos los suelos)
  (hay que volver a lanzarlo cuando se repinte un dibujo del mundo)
Genera:  <dibujo>_n.png al lado de cada dibujo (Godot lo usa si existe: scripts/mundo/relieve.gd)
"""
import os
import sys
import numpy as np
from PIL import Image, ImageFilter

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALDEA = [
    "arte/mundos/raiz/aldea/casa_seta.png", "arte/mundos/raiz/aldea/cocina.png", "arte/mundos/raiz/aldea/farol.png",
    "arte/mundos/raiz/aldea/gran_arbol.png", "arte/mundos/raiz/aldea/puesto.png", "arte/mundos/raiz/aldea/setitas.png",
    "arte/mundos/raiz/aldea/taller.png", "arte/mundos/raiz/aldea/valla.png",
    "arte/mundos/raiz/objetos/arbol_a.png", "arte/mundos/raiz/objetos/arbol_b.png", "arte/mundos/raiz/objetos/cartel.png",
    "arte/mundos/raiz/objetos/matorral.png", "arte/mundos/raiz/objetos/roca_grande.png", "arte/mundos/raiz/objetos/roca_pequena.png",
]


def _desenfoque(a, radio):
    img = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(img.filter(ImageFilter.GaussianBlur(radio)), dtype=np.float32) / 255.0


def normales(ruta):
    im = Image.open(ruta).convert("RGBA")
    a = np.asarray(im, dtype=np.float32) / 255.0
    alfa = a[..., 3]
    claridad = a[..., 0] * 0.3 + a[..., 1] * 0.55 + a[..., 2] * 0.15
    opaco = alfa.min() > 0.99
    if opaco:
        altura = _desenfoque(claridad, 0.8) * 1.2
        fuerza = 1.6
    else:
        # un abombado a varias escalas: el borde (2 px), las formas medianas (6 px) y la masa entera (14 px),
        # para que una copa o un tejado grande se abomben enteros y no solo en el contorno
        bisel = _desenfoque(alfa, 2.0) * 0.35 + _desenfoque(alfa, 6.0) * 0.45 + _desenfoque(alfa, 14.0) * 0.6
        # y las manchas de luz y sombra del pixel art (las copas de hojas, las tejas) se levantan
        altura = bisel + (_desenfoque(claridad, 0.7) * 0.35 + _desenfoque(claridad, 2.0) * 0.45) * alfa
        fuerza = 3.6
    # la pendiente (diferencias centrales)
    dx = np.zeros_like(altura)
    dy = np.zeros_like(altura)
    dx[:, 1:-1] = (altura[:, 2:] - altura[:, :-2]) * 0.5
    dy[1:-1, :] = (altura[2:, :] - altura[:-2, :]) * 0.5
    # Godot usa normales con la Y hacia arriba (convenio OpenGL); en la imagen la y baja
    nx = -dx * fuerza
    ny = dy * fuerza
    nz = np.ones_like(altura)
    largo = np.sqrt(nx * nx + ny * ny + nz * nz)
    n = np.stack([nx / largo, ny / largo, nz / largo], axis=-1)
    rgb = np.clip((n * 0.5 + 0.5) * 255, 0, 255).astype(np.uint8)
    rgb[alfa < 0.01] = (128, 128, 255)
    salida = os.path.splitext(ruta)[0] + "_n.png"
    Image.fromarray(rgb, "RGB").save(salida)
    return salida


if __name__ == "__main__":
    rutas = sys.argv[1:]
    if "--aldea" in rutas:
        rutas = [os.path.join(RAIZ, r) for r in ALDEA]
    elif "--todo" in rutas:
        rutas = []
        for carpeta, _, archivos in os.walk(os.path.join(RAIZ, "arte", "mundos")):
            if carpeta.endswith("suelos"):
                continue   # los suelos no: su relieve es ruido (la hierba), ocupa muchísimo y apenas se nota
            rutas += [os.path.join(carpeta, a) for a in sorted(archivos) if a.endswith(".png") and not a.endswith("_n.png")]
    for r in rutas:
        print("relieve:", os.path.relpath(normales(r), RAIZ))
