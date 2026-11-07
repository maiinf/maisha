"""Boceto de ambiente de ASTERHAUL (mundo 3), para decidir con Iam antes de construir nada.
La Ciudad-Cráter de los canteros y forjadores de ámbar, al este de Kitovu: terrazas de basalto negro
talladas en la pared de un cráter antiguo, viaductos con vías de vagonetas, geodas de ámbar estelar
que brillan en la roca, y peñascos de hierro meteórico flotando sobre el núcleo magnético del centro
sujetos con cadenas gigantes. Maisha llega por el desfiladero de roca, abajo a la izquierda.
Sale en documentacion/boceto_asterhaul.png (600×256)."""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from pintor import Lienzo, rampa  # noqa: E402
import cinematicas as ci  # noqa: E402

W, H = 600, 256
BASALTO = ["#0e0d14", "#181722", "#252334", "#36334a", "#4c4866", "#686284", "#8a84a6"]
OCRE = ["#28170c", "#462814", "#6e401e", "#9c5e2c", "#c88240", "#e6a860", "#f8cfa0"]
AMBAR = ["#421c04", "#7c3808", "#be6010", "#f0941e", "#ffc842", "#ffe888", "#fff9d6"]
COBRE = ["#241814", "#482c22", "#784834", "#aa6a48", "#d49062", "#f0ba88"]
MAGNETO = ["#0c2834", "#164c5e", "#247e92", "#42b8c8", "#84ecee", "#dcffff"]
LUZ = (-0.6, -0.55, 0.58)


def edificio_terraza(lz, x, base, alto, ancho, rng, lejos=0.0):
    """Un taller-forja de basalto y adobe ocre con tejado escalonado de bronce y horno encendido."""
    cuerpo = lz.poligono([
        (x - ancho, base),
        (x - ancho * 0.9, base - alto),
        (x + ancho * 0.9, base - alto),
        (x + ancho, base),
    ])
    hiladas = ((lz.y % 4) < 0.7) * 1.0
    lz.sombrear(cuerpo, BASALTO, ancho * 0.85, LUZ, textura=1 - hiladas * 0.45, fuerza_tex=0.25)
    # franja de bronce a media altura
    yf = base - alto * 0.65
    faja = lz.poligono([
        (x - ancho * 1.05, yf),
        (x + ancho * 1.05, yf),
        (x + ancho * 1.02, yf + 2.5),
        (x - ancho * 1.02, yf + 2.5),
    ])
    lz.sombrear(faja, COBRE, 1.5, LUZ)
    # tejado escalonado de placas de cobre/ámbar
    tejado = np.maximum(
        lz.poligono([
            (x - ancho * 1.12, base - alto),
            (x - ancho * 0.75, base - alto - ancho * 0.55),
            (x + ancho * 0.75, base - alto - ancho * 0.55),
            (x + ancho * 1.12, base - alto),
        ]),
        lz.poligono([
            (x - ancho * 0.6, base - alto - ancho * 0.55),
            (x, base - alto - ancho * 1.15),
            (x + ancho * 0.6, base - alto - ancho * 0.55),
        ]),
    )
    lz.sombrear(tejado, COBRE, ancho * 0.7, LUZ)
    # chimenea o diapasón en el tejado
    lz.pintar(lz.trazo([(x - ancho * 0.3, base - alto - ancho * 0.4), (x - ancho * 0.3, base - alto - ancho * 1.2)], 1.2), BASALTO[1])
    # ventanas y boca de horno encendidas
    for fila in range(max(1, int(alto / 14))):
        yv = base - 6 - fila * 13
        for dx in (-0.42, 0.42) if ancho > 9 else (0.0,):
            if rng.random() < 0.78:
                vx = x + dx * ancho
                v = np.maximum(
                    lz.elipse(vx, yv - 2, 1.8, 2.0),
                    lz.poligono([(vx - 1.8, yv - 2), (vx + 1.8, yv - 2), (vx + 1.8, yv + 2), (vx - 1.8, yv + 2)]),
                )
                lz.pintar(v, "#ffd468")
                lz.sumar_luz(lz.desenfocar(v, 4.5), "#f08820", 0.38)
    if lejos > 0:
        lz.pintar(np.maximum(cuerpo, tejado), "#3a2428", lejos)


def geoda_ambar(lz, x, y, r, ang=-15):
    """Un cristal o geoda de ámbar estelar que brota de la roca y da luz cálida."""
    a = np.radians(ang)
    ca, sa = np.cos(a), np.sin(a)
    pts = [
        (x - ca * r * 0.5, y - sa * r * 0.5),
        (x - ca * r * 0.35 + sa * r * 1.6, y - sa * r * 0.35 - ca * r * 1.6),
        (x + sa * r * 2.2, y - ca * r * 2.2),
        (x + ca * r * 0.45 + sa * r * 1.4, y + sa * r * 0.45 - ca * r * 1.4),
        (x + ca * r * 0.5, y + sa * r * 0.5),
    ]
    cristal = lz.poligono(pts)
    lz.sombrear(cristal, AMBAR[1:], r * 0.6, LUZ)
    arista = lz.trazo([(x, y), (x + sa * r * 2.1, y - ca * r * 2.1)], 0.7) * cristal
    lz.pintar(arista, "#fff9d6", 0.85)
    lz.sumar_luz(lz.desenfocar(cristal, r * 1.4), "#f0941e", 0.45)
    return cristal


def penasco_flotante(lz, cx, cy, rx, ry, rng, cadena_hasta=None):
    """Un fragmento de hierro meteórico magnetizado que flota sobre el cráter con vetas de luz."""
    pts = []
    for k in range(10):
        a = k * 2 * np.pi / 10
        f = 0.78 + 0.32 * rng.random()
        pts.append((cx + np.cos(a) * rx * f, cy + np.sin(a) * ry * f))
    roca = lz.poligono(pts)
    lz.sombrear(roca, BASALTO, min(rx, ry) * 0.75, LUZ, textura=lz.ruido(4, 2, semilla=int(cx)), fuerza_tex=0.35)
    # grietas magnéticas turquesas y ámbar
    grieta1 = lz.trazo([(cx - rx * 0.45, cy - ry * 0.1), (cx, cy + ry * 0.15), (cx + rx * 0.5, cy - ry * 0.2)], 0.9) * roca
    lz.sumar_luz(lz.desenfocar(grieta1, 3), "#42b8c8", 0.65)
    lz.pintar(grieta1, "#dcffff", 0.9)
    # halo magnético debajo
    aro = lz.elipse(cx, cy + ry * 0.95, rx * 0.75, 2.2) - lz.elipse(cx, cy + ry * 0.95, rx * 0.5, 1.2)
    aro = np.clip(aro, 0, 1)
    lz.sumar_luz(lz.desenfocar(aro, 2.5), "#42b8c8", 0.55)
    # cadena tensa que lo ancla al cráter
    if cadena_hasta is not None:
        ox, oy = cadena_hasta
        c = lz.trazo([(cx, cy + ry * 0.6), (ox, oy)], 1.1)
        eslabon = ((np.hypot(lz.x - cx, lz.y - cy) % 4) < 2.2) * 1.0
        lz.pintar(c, BASALTO[1])
        lz.pintar(c * eslabon, COBRE[3], 0.7)


def boceto():
    lz = Lienzo(W, H, semilla=700)
    rng = np.random.default_rng(701)

    # 1. Cielo de ocaso cobrizo-estelar: índigo arriba, carmín y ámbar ardiente hacia el cráter
    lz.pintar(
        np.ones((lz.H, lz.W)),
        lz.gradiente(["#090814", "#18142c", "#38203e", "#6e3240", "#b85a32", "#eaa044", "#fce088"], desde=0, hasta=168),
    )
    ci.estrellas(lz, 110, 88, semilla=702, color="#fff4dc")

    # Estela antigua en el cielo (eco de la estrella caída) y ondas magnéticas
    for k in range(3):
        onda = lz.elipse(410, 148, 95 + k * 36, 48 + k * 18) - lz.elipse(410, 148, 92 + k * 36, 45 + k * 18)
        onda = np.clip(onda, 0, 1) * (lz.y < 145)
        lz.sumar_luz(lz.desenfocar(onda, 2.5), "#ffc842" if k % 2 == 0 else "#42b8c8", 0.25)

    # 2. Cordilleras basálticas y borde lejano del Gran Cráter
    for (base, amp, col, sem) in ((124, 34, "#3c2434", 704), (140, 26, "#281826", 705)):
        m = ci.mascara_bajo(lz, ci.linea_horizonte(lz, base - amp * 0.4, amp, 65, sem))
        lz.pintar(m, col)

    # Pared curva del Gran Cráter al fondo-derecha (anfiteatro escalonado)
    crater_fondo = lz.poligono([(170, 198), (205, 132), (320, 118), (520, 114), (600, 126), (600, 198)])
    estratos = ((lz.y + np.sin(lz.x * 0.03) * 6) % 9 < 1.8) * 1.0
    lz.sombrear(crater_fondo, OCRE[:5], 28, LUZ, textura=1 - estratos * 0.45, fuerza_tex=0.3)
    lz.pintar(crater_fondo, "#341e28", 0.35)

    # 3. Peñascos de hierro meteórico flotando sobre el corazón del cráter + el Gran Diapasón central
    penasco_flotante(lz, 355, 62, 16, 10, rng, cadena_hasta=(370, 136))
    penasco_flotante(lz, 465, 52, 22, 13, rng, cadena_hasta=(448, 132))
    penasco_flotante(lz, 535, 76, 13, 8, rng, cadena_hasta=(518, 144))
    penasco_flotante(lz, 292, 82, 11, 7, rng, cadena_hasta=(312, 144))

    # El Gran Diapasón / Aguja del Núcleo en el centro del cráter (x=410)
    aguja_izq = lz.poligono([(394, 180), (390, 86), (398, 72), (403, 180)])
    aguja_der = lz.poligono([(417, 180), (422, 72), (430, 86), (426, 180)])
    base_forja = lz.poligono([(376, 194), (384, 136), (436, 136), (444, 194)])
    lz.sombrear(np.maximum(aguja_izq, aguja_der), BASALTO, 6, LUZ)
    lz.sombrear(base_forja, BASALTO, 18, LUZ, textura=1 - ((lz.y % 5) < 0.8) * 0.5, fuerza_tex=0.25)
    # núcleo de ámbar y magnetismo suspendido entre las dos puntas del diapasón
    nucleo = lz.circulo(410, 92, 9.5)
    lz.sumar_luz(lz.desenfocar(nucleo, 18), "#f0941e", 0.75)
    lz.sumar_luz(lz.desenfocar(nucleo, 7), "#ffe888", 0.85)
    lz.pintar(nucleo, "#fff9d6")
    # rayos entre las puntas del diapasón y el núcleo
    for dy in (-6, 0, 6):
        rayo = lz.trazo([(395, 92 + dy), (410, 92 + dy * 0.3), (425, 92 - dy)], 0.9)
        lz.sumar_luz(lz.desenfocar(rayo, 2.5), "#42b8c8", 0.7)
        lz.pintar(rayo, "#dcffff", 0.9)
    # gran boca de la forja al pie de la torre central
    boca = lz.elipse(410, 178, 10, 14) * (lz.y < 192)
    lz.pintar(boca, "#ffc842")
    lz.sumar_luz(lz.desenfocar(boca, 14), "#f06818", 0.65)

    # 4. Terrazas de la ciudad (Mji-Jiwe) y talleres escalonados
    for k in range(8):
        edificio_terraza(lz, 235 + k * 44 + rng.uniform(-6, 6), 156 + (k % 2) * 8, rng.uniform(28, 48), rng.uniform(7, 11), rng, lejos=0.35)

    # Viaducto de piedra con arcos y vía de vagonetas cruzando a media altura
    viaducto_y = 152
    viaducto = lz.poligono([(210, viaducto_y), (600, viaducto_y - 6), (600, viaducto_y + 18), (210, viaducto_y + 18)])
    for ax in range(230, 590, 32):
        vy = viaducto_y - (ax - 210) * 6.0 / 390.0
        arco = np.maximum(
            lz.elipse(ax, vy + 9, 10, 9),
            lz.poligono([(ax - 10, vy + 9), (ax + 10, vy + 9), (ax + 10, vy + 22), (ax - 10, vy + 22)]),
        )
        viaducto = np.clip(viaducto - arco, 0, 1)
    lz.sombrear(viaducto, OCRE[:6], 6, LUZ, textura=1 - ((lz.y % 4) < 0.7) * 0.4, fuerza_tex=0.25)
    # vagoneta con ámbar brillante sobre el viaducto
    for vx in (278, 492):
        vy = viaducto_y - (vx - 210) * 6.0 / 390.0 - 3
        vag = lz.poligono([(vx - 5, vy - 3), (vx + 5, vy - 3), (vx + 4, vy + 2), (vx - 4, vy + 2)])
        lz.sombrear(vag, BASALTO[:5], 2, LUZ)
        carga = lz.elipse(vx, vy - 4, 3.8, 2.2)
        lz.pintar(carga, "#ffc842")
        lz.sumar_luz(lz.desenfocar(carga, 5), "#f0941e", 0.5)

    # Edificios cercanos en la terraza baja
    edificio_terraza(lz, 330, 192, 64, 14, rng)
    edificio_terraza(lz, 472, 188, 72, 15, rng)
    edificio_terraza(lz, 558, 194, 58, 13, rng)

    # Río de escoria fundida / ámbar líquido que baja desde la forja hacia la derecha
    t_r = np.clip((lz.y - 186) / 70, 0, 1)
    cx_r = 410 + np.sin(t_r * 3.5) * 28 + t_r * 85
    rio = (lz.y > 186) * (np.abs(lz.x - cx_r) < 3.5 + t_r * 16)
    lz.pintar(rio, rampa(["#421208", "#8e280c", "#d85c14", "#f8a828", "#fff090"], np.clip(0.85 - np.abs(lz.x - cx_r) / (4 + t_r * 16), 0, 1)))
    lz.sumar_luz(lz.desenfocar(rio * 1.0, 6), "#f07818", 0.45)

    # 5. El suelo rocoso del desfiladero en primer plano, con vías antiguas y geodas de ámbar
    suelo = ci.mascara_bajo(lz, ci.linea_horizonte(lz, 190, 5, 65, 706))
    suelo_izq = ((lz.y > 174 + (lz.x / 260) * 26 + np.sin(lz.x * 0.08) * 3) * (lz.x < 280)).astype(float)
    suelo = np.maximum(suelo, suelo_izq)
    lz.pintar(
        suelo * (1 - rio * 0.85),
        rampa(
            ["#16121c", "#282030", "#423244", "#664852", "#8e6660"],
            np.clip(0.3 + (lz.y - 185) / 85 + (lz.ruido(18, 2, semilla=707) - 0.5) * 0.3, 0, 1),
        ),
    )
    # Escalones y grietas de carga sísmica en el suelo
    grietas = suelo * (1 - rio) * (np.abs(np.sin(lz.x * 0.45 + lz.y * 0.25 + lz.ruido(4, 2, semilla=708) * 4)) < 0.05)
    lz.pintar(grietas, "#f0941e", 0.65)
    lz.sumar_luz(lz.desenfocar(grietas, 3), "#f0941e", 0.3)

    # Geodas de ámbar estelar brotando en el cañón
    geoda_ambar(lz, 42, 224, 9, ang=18)
    geoda_ambar(lz, 54, 228, 6, ang=32)
    geoda_ambar(lz, 196, 214, 7.5, ang=-16)
    geoda_ambar(lz, 206, 218, 5, ang=8)
    geoda_ambar(lz, 310, 236, 8, ang=-22)

    # Monolitos de resonancia junto al camino de Maisha
    for (mx, my, mh) in ((162, 216, 24), (248, 206, 20)):
        mono = lz.poligono([(mx - 4, my), (mx - 3, my - mh), (mx, my - mh - 5), (mx + 3, my - mh), (mx + 4, my)])
        lz.sombrear(mono, BASALTO, 3.5, LUZ)
        runa_m = lz.circulo(mx, my - mh * 0.55, 1.8)
        lz.sumar_luz(lz.desenfocar(runa_m, 4), "#42b8c8", 0.7)
        lz.pintar(runa_m, "#dcffff")

    # 6. Maisha en el risco del desfiladero, abajo a la izquierda, contemplando Asterhaul
    ci.maisha_luz(lz, 114, 222, e=1.8)
    lz.pintar(lz.desenfocar(lz.elipse(116, 224, 14, 2.5), 1.5), "#140e18", 0.55)

    # Chispas de forja y polvo de ámbar flotando en el aire cálido
    chispas = np.zeros((lz.H, lz.W))
    polvo_mag = np.zeros((lz.H, lz.W))
    for k in range(120):
        px, py = rng.random() * W, rng.random() * H
        r = 0.4 + rng.random() * 0.55
        if k % 4 == 0 and py < 170:
            polvo_mag = np.maximum(polvo_mag, lz.circulo(px, py, r) * rng.uniform(0.4, 0.9))
        else:
            chispas = np.maximum(chispas, lz.circulo(px, py, r) * rng.uniform(0.4, 1.0))
    lz.sumar_luz(chispas, "#ffd878", 0.75)
    lz.sumar_luz(polvo_mag, "#84ecee", 0.65)
    return lz


if __name__ == "__main__":
    salida = os.path.join(os.path.dirname(__file__), "..", "documentacion", "boceto_asterhaul.png")
    boceto().guardar(salida)
    print("hecho", os.path.abspath(salida))
