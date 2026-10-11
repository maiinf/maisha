"""LAS RUINAS DEL KITOVU, pintadas con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_ruinas.py

Mismas medidas y fotogramas que los de antes (el juego no cambia), en arte/mundos/kitovu/:
  ruina_casa.png     2 × 60×50   casas de la aldea antigua: muros de piedra rotos, vigas caídas, paja podrida
  pozo.png           30×38       el pozo seco: brocal de piedra, tejadillo roto, la cuerda partida y el cubo
  torre.png          44×92       la torre de la campana: piedra agrietada, la campana muda arriba, hiedra seca
  monumento.png      44×72       el monumento de la leyenda: obelisco con el brote tallado, raíces y escalones
  raiz_gigante.png   2 × 100×30  raíces gigantes secas, tumbadas
  portal.png         2 × 72×88   el Arco de Raíz: dormido (oscuridad y espinas de Giza) / abierto (los Prados)
  farol_apagado.png  10×28       farol de la aldea, apagado (píxel a píxel)
  crater.png         56×26       el cráter donde cae Maisha
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa, hex2, RAIZ  # noqa: E402
from pintar_casa_shamba import TRONCO, CORTE, vetas, rect, paja  # noqa: E402
from cinematicas import piedras, hebra, HIERBA  # noqa: E402
from pintar_granja import mapa_pixeles, tira, HOJA  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "kitovu")
LUZ = (-0.6, -0.7, 0.5)
CONTORNO = 0.38
ROCA = ["#2a2b26", "#3d3f37", "#525549", "#686c5d", "#7f8472", "#989c8a", "#b3b6a5", "#ccceBF".lower()]
MORTERO = "#3a3b33"
MADERA_GRIS = ["#1b1714", "#2e2621", "#433830", "#5a4c41", "#716254", "#8a7b6a"]
PAJA_PODRIDA = ["#1f1a12", "#332a1a", "#4a3d24", "#635230", "#7d6a40", "#978452"]
HIEDRA_SECA = ["#1f1a12", "#3b3220", "#5a4a2c", "#7a663c", "#957e4a"]
BRONCE = ["#1e1a12", "#3a2f1a", "#5c4a26", "#7e6634", "#a08548", "#c4a868", "#e2cc90"]
RAIZ_SECA = ["#1c1714", "#2e2620", "#43382e", "#5a4b3d", "#716050", "#8a7764", "#a5927c"]


def musgo_seco(lz, m, semilla, umbral=0.76, abajo=True):
    zona = (lz.ruido(1.6, 3, semilla=semilla) > umbral) * m
    if abajo:
        zona = zona * np.clip((lz.y - lz.y.min()) / max(1, lz.h) * 1.6, 0, 1)
    lz.pintar(lz.desenfocar(zona, 0.3), rampa(["#24301c", "#3a4a2a", "#556640", "#6e7d52"], lz.ruido(0.5, 2, semilla=semilla + 1)), 0.85)


def grietas(lz, m, semilla, n=3, color="#141410"):
    rng = np.random.default_rng(semilla)
    ys, xs = np.nonzero(m > 0.5)
    if len(xs) == 0:
        return
    for _ in range(n):
        i = rng.integers(len(xs))
        x0, y0 = xs[i] / lz.s, ys[i] / lz.s
        pts = [(x0, y0)]
        for k in range(6):
            x0 += (rng.random() - 0.5) * 3
            y0 += 1 + rng.random() * 2
            pts.append((x0, y0))
        lz.pintar(lz.trazo(pts, 0.6, 0.2) * m, color, 0.85)


def hiedra(lz, x0, y0, largo, semilla, m=None):
    """Hiedra seca que cuelga por un muro: tallos ondulados con hojitas marchitas."""
    rng = np.random.default_rng(semilla)
    tallos = np.zeros((lz.H, lz.W))
    hojas = np.zeros((lz.H, lz.W))
    for k in range(3):
        x, y = x0 + (k - 1) * 1.6, y0
        pts = [(x, y)]
        for j in range(int(largo)):
            x += np.sin(j * 0.9 + k + semilla) * 0.7
            y += 1
            pts.append((x, y))
            if rng.random() < 0.45:
                hojas = np.maximum(hojas, lz.elipse(x + (rng.random() - 0.5) * 2, y, 0.9, 0.6, rng.random() * 180))
        tallos = np.maximum(tallos, lz.trazo(pts, 0.45, 0.3))
    if m is not None:
        tallos, hojas = tallos * m, hojas * m
    lz.pintar(tallos, "#2e2416")
    lz.sombrear(hojas, HIEDRA_SECA, 0.5, LUZ)


def escombros(lz, x0, x1, y, n, semilla, tam=(1.2, 3.0)):
    rng = np.random.default_rng(semilla)
    for _ in range(n):
        x = x0 + rng.random() * (x1 - x0)
        yy = y - rng.random() * 3
        t = tam[0] + rng.random() * (tam[1] - tam[0])
        pts = [(x + np.cos(a) * t * (0.7 + rng.random() * 0.5), yy + np.sin(a) * t * 0.6 * (0.7 + rng.random() * 0.5))
               for a in np.linspace(0, 2 * np.pi, 7)[:-1] + rng.random()]
        lz.sombrear(lz.poligono(pts), ROCA, t * 0.5, LUZ, textura=lz.ruido(0.4, 2), fuerza_tex=0.25)


def hierba_al_pie(lz, x0, x1, y, n, semilla, seca=True):
    rng = np.random.default_rng(semilla)
    m = np.zeros((lz.H, lz.W))
    for _ in range(n):
        x = x0 + rng.random() * (x1 - x0)
        m = np.maximum(m, lz.trazo([(x, y), (x + (rng.random() - 0.5) * 2, y - 1.5 - rng.random() * 3)], 0.6, 0.25))
    cols = ["#2e2a1c", "#4a4430", "#6a6244", "#8a805a"] if seca else HIERBA[1:6]
    lz.sombrear(m, cols, 0.3, LUZ)


# ---------------------------------------------------------------- casas en ruinas
def ruina_casa(v):
    lz = Lienzo(60, 50, s=6, semilla=30 + v)
    rng = np.random.default_rng(31 + v)
    base = 47.5
    # la sombra del interior (se ve por dentro, sin tejado)
    # muro del fondo, con el borde de arriba roto
    borde = [(4, base)]
    xs = np.linspace(4, 56, 26)
    for i, x in enumerate(xs):
        # un muro que se ha ido cayendo: alto en una esquina, bajando a escalones de piedra
        alto = 30 - abs(x - (14 if v == 0 else 46)) * 0.42 + np.sin(i * 2.1 + v) * 1.6 + (rng.random() < 0.3) * -2.5
        if v == 1 and 30 < x < 44:
            alto -= 10                                   # un gran boquete
        borde.append((x, base - alto))
    borde.append((56, base))
    muro = lz.poligono(borde)
    piedras(lz, muro, tam=4.6, semilla=32 + v, rampa_p=ROCA, luz=LUZ, mortero=MORTERO)
    lz.pintar(np.clip((lz.y - (base - 6)) / 6, 0, 1) * muro, "#16140f", 0.35)
    # puerta y ventana (huecos oscuros con dintel de madera)
    for (a, b, c, d) in [(23, base - 15, 31, base), (39 - v * 26, base - 22, 45 - v * 26, base - 15)]:
        hueco = rect(lz, a, b, c, d)
        lz.pintar(hueco, lz.gradiente(["#0a0907", "#16140f"], desde=b, hasta=d))
        dintel = rect(lz, a - 1.5, b - 2, c + 1.5, b)
        lz.sombrear(dintel, MADERA_GRIS, 0.9, LUZ, textura=vetas(lz, 0.3, 9), fuerza_tex=0.4)
    # la viga del tejado caída en diagonal y otra rota
    for (p0, p1, g) in [((2, base - 24 + v * 4), (40 - v * 6, base - 6), 2.4), ((50, base - 26), (58, base - 10), 2.0)]:
        viga = lz.trazo([p0, p1], g, g * 0.9)
        lz.sombrear(viga, MADERA_GRIS, g * 0.5, LUZ, textura=vetas(lz, 0.3, 11), fuerza_tex=0.45)
    # restos de paja podrida colgando de un lado
    pj = lz.poligono([(4, base - 27 + v * 3), (16, base - 33 + v * 3), (19, base - 22), (12, base - 17), (4, base - 19)])
    paja(lz, pj, semilla=33 + v, capas=3.0, y0=base - 33, oscuro=0.0)
    lz.pintar(pj, rampa(PAJA_PODRIDA, lz.ruido(0.5, 2, semilla=34 + v)), 0.75)
    # hiedra seca, musgo y grietas
    hiedra(lz, 48 - v * 30, base - 22, 14, 35 + v, muro)
    musgo_seco(lz, muro, 36 + v)
    grietas(lz, muro, 37 + v, 3)
    # escombros y hierba al pie
    escombros(lz, 2, 58, base + 1.5, 14, 38 + v)
    hierba_al_pie(lz, 1, 59, base + 2, 30, 39 + v)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- pozo seco
def pozo():
    lz = Lienzo(30, 38, s=7, semilla=40)
    # postes y el tejadillo roto (detrás)
    for x in (4.5, 25.5):
        p = rect(lz, x - 1.2, 4, x + 1.2, 28)
        lz.sombrear(p, MADERA_GRIS, 0.7, LUZ, textura=vetas(lz, 0.3, 9, False), fuerza_tex=0.4)
    eje = lz.trazo([(3, 9), (27, 9)], 1.6)
    lz.sombrear(eje, MADERA_GRIS, 0.7, LUZ)
    tejado = lz.poligono([(1, 6), (15, 0.5), (22, 3.4), (20, 5.2), (15, 3), (2.6, 8)])
    lz.sombrear(tejado, MADERA_GRIS, 1.2, LUZ, textura=(np.abs(np.sin(lz.x * 1.8)) < 0.2).astype(float) * -1 + 1, fuerza_tex=0.4)
    tabla_caida = lz.trazo([(22, 4), (27.5, 12)], 1.2)
    lz.sombrear(tabla_caida, MADERA_GRIS, 0.5, LUZ)
    # la cuerda partida y el cubo colgando de lado
    lz.pintar(lz.trazo(lz.curva((13, 9), (12.4, 14), (13.4, 17), n=10), 0.45), "#8a7454")
    cubo = lz.poligono([(10.6, 17), (16.4, 17.6), (15.8, 22.4), (11.2, 22)])
    lz.sombrear(cubo, MADERA_GRIS, 1.4, LUZ, textura=(np.abs(np.sin(lz.x * 2.2)) < 0.2).astype(float) * -1 + 1, fuerza_tex=0.3)
    for yy in (18.2, 21):
        lz.pintar(lz.trazo([(10.8, yy), (16.2, yy + 0.4)], 0.45), "#3d3f43")
    # el brocal: piedras en anillo, con la boca negra
    brocal = np.maximum(lz.elipse(15, 26, 13, 4.5), rect(lz, 2, 26, 28, 34))
    brocal = np.maximum(brocal, lz.elipse(15, 34, 13, 3))
    piedras(lz, brocal, tam=3.6, semilla=41, rampa_p=ROCA, luz=LUZ, mortero=MORTERO)
    boca = lz.elipse(15, 26, 10, 3)
    lz.pintar(boca, lz.gradiente(["#050403", "#16140f"], desde=23, hasta=29))
    lz.pintar(np.clip(lz.elipse(15, 26, 11.5, 3.9) - boca, 0, 1), "#989c8a", 0.6)
    musgo_seco(lz, brocal, 42)
    grietas(lz, brocal * (lz.y > 28), 43, 2)
    hierba_al_pie(lz, 1, 29, 37.6, 18, 44)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- torre de la campana
def torre():
    lz = Lienzo(44, 92, s=5, semilla=50)
    base = 90
    # el cuerpo, que se estrecha un poco hacia arriba, con la cima rota
    cuerpo = lz.poligono([(6, base), (9, 22), (14, 18), (17, 20), (21, 14), (26, 17), (30, 13), (34, 21), (35, base)])
    piedras(lz, cuerpo, tam=4.4, semilla=51, rampa_p=ROCA, luz=LUZ, mortero=MORTERO)
    # sombra lateral (es redonda)
    lz.pintar(np.clip((lz.x - 23) / 13, 0, 1) * cuerpo, "#16140f", 0.45)
    lz.pintar(np.clip((14 - lz.x) / 8, 0, 1) * cuerpo, "#d8dacb", 0.12)
    # cornisas
    for y in (60, 36):
        c = rect(lz, 7, y, 35, y + 2.2)
        lz.sombrear(c * cuerpo, ROCA, 1, LUZ)
        lz.pintar(rect(lz, 7, y + 2.2, 35, y + 3.2) * cuerpo, "#16140f", 0.6)
    # el campanario: un arco abierto con la campana dentro
    arco = lz.poligono([(14, 34), (14, 27)] + [(21 + np.cos(a) * 7, 27 - np.sin(a) * 6) for a in np.linspace(np.pi, 0, 16)] + [(28, 27), (28, 34)])
    lz.pintar(arco, lz.gradiente(["#0a0907", "#2a2d4c"], desde=21, hasta=34))
    lz.pintar(lz.trazo([(14.5, 24.5), (27.5, 24.5)], 1.0), "#433830")
    campana = lz.poligono([(17.4, 33), (18.6, 27.4), (21, 25.6), (23.4, 27.4), (24.6, 33)])
    lz.sombrear(campana, BRONCE, 2, LUZ)
    lz.pintar(lz.elipse(21, 33, 3.6, 0.8), "#3a2f1a")
    lz.pintar(np.clip(lz.elipse(21, 28, 4, 4) - lz.elipse(20, 28, 3.6, 4.2), 0, 1) * campana, "#5c7a5a", 0.45)   # verdín
    # ventanas estrechas y la puerta
    for (y0, y1) in [(44, 52), (66, 74)]:
        v_ = lz.poligono([(19.5, y1), (19.5, y0 + 1.5), (21, y0), (22.5, y0 + 1.5), (22.5, y1)])
        lz.pintar(v_, "#0a0907")
    puerta = lz.poligono([(16, base), (16, 80)] + [(21 + np.cos(a) * 5, 80 - np.sin(a) * 4) for a in np.linspace(np.pi, 0, 12)] + [(26, 80), (26, base)])
    lz.pintar(puerta, "#0a0907")
    hoja = lz.poligono([(16.4, base), (16.4, 81), (19, 79), (20.5, 80.5), (20.5, base)])
    lz.sombrear(hoja, MADERA_GRIS, 1.4, LUZ, textura=(np.abs(np.sin(lz.x * 2)) < 0.2).astype(float) * -1 + 1, fuerza_tex=0.4)
    # hiedra seca trepando, grietas y musgo
    hiedra(lz, 9, 40, 46, 52, cuerpo)
    hiedra(lz, 31, 58, 28, 53, cuerpo)
    grietas(lz, cuerpo, 54, 6)
    musgo_seco(lz, cuerpo, 55, umbral=0.7)
    # piedras caídas de la cima, al pie
    escombros(lz, 2, 42, base + 1, 14, 56, tam=(1.4, 3.6))
    hierba_al_pie(lz, 1, 43, base + 1.5, 30, 57)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- monumento de la leyenda
def monumento():
    lz = Lienzo(44, 72, s=5, semilla=60)
    base = 70
    # escalones
    for (y0, y1, x0, x1) in [(64, base, 2, 42), (58, 64, 6, 38), (53, 58, 10, 34)]:
        e = rect(lz, x0, y0, x1, y1)
        lz.sombrear(e, ROCA, 2.4, LUZ, textura=lz.ruido(0.6, 2), fuerza_tex=0.25)
        lz.pintar(rect(lz, x0, y0, x1, y0 + 0.8), "#ccceBF".lower(), 0.4)
        grietas(lz, e, 61 + y0, 1)
    # el obelisco
    ob = lz.poligono([(14, 53), (16, 12), (22, 6), (28, 12), (30, 53)])
    lz.sombrear(ob, ROCA, 6, LUZ, textura=lz.ruido(0.5, 3, semilla=62), fuerza_tex=0.25)
    lz.pintar(np.clip((lz.x - 22) / 8, 0, 1) * ob, "#16140f", 0.35)
    # el brote tallado (hundido: sombra arriba, luz abajo) y el corazón de luz apagado
    tallo = lz.trazo(lz.curva((22, 40), (21.6, 33), (22, 26), n=12), 1.2, 0.9)
    hojas_t = np.maximum(lz.elipse(19, 25, 3.4, 1.6, 30), lz.elipse(25, 24, 3.4, 1.6, -30))
    tallado = np.clip(tallo + hojas_t, 0, 1)
    lz.pintar(tallado, "#3d3f37", 0.9)
    lz.pintar(np.clip(tallado - (lambda m: np.roll(m, -lz.s, axis=0))(tallado), 0, 1), "#16140f", 0.6)
    gema = lz.circulo(22, 44, 2.2)
    lz.sombrear(gema, ["#3a2f1a", "#5c4a26", "#7e6634", "#a08548"], 1.4, LUZ)
    lz.pintar(lz.circulo(21.4, 43.4, 0.5), "#c4a868", 0.6)
    # letras gastadas en una placa
    placa = rect(lz, 15, 55, 29, 57.6)
    lz.pintar(placa, "#525549")
    rng = np.random.default_rng(63)
    for k in range(9):
        x = 16 + k * 1.4
        lz.pintar(rect(lz, x, 55.6, x + 0.7 + rng.random() * 0.4, 57), "#2a2b26", 0.8)
    # raíces secas que abrazan el obelisco
    for (p0, p1, p2, p3, g) in [((8, 66), (6, 50), (16, 40), (20, 30), 2.4), ((38, 64), (40, 46), (28, 40), (25, 22), 2.2)]:
        hebra(lz, lz.curva(p0, p1, p2, p3, n=40), g, g * 0.4, RAIZ_SECA, LUZ, semilla=int(p0[0]))
    musgo_seco(lz, ob, 64, umbral=0.72)
    grietas(lz, ob, 65, 3)
    escombros(lz, 0, 44, base + 1, 6, 66)
    hierba_al_pie(lz, 0, 44, base + 1.5, 26, 67)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- raíces gigantes secas
def raiz_gigante(v):
    lz = Lienzo(100, 30, s=5, semilla=70 + v)
    rng = np.random.default_rng(71 + v)
    if v == 0:
        cam = lz.curva((-4, 22), (30, 15), (70, 23), (104, 18), n=60)
    else:
        cam = lz.curva((-4, 24), (34, 26), (60, 10), (104, 14), n=60)
    hebra(lz, cam, 19, 15, RAIZ_SECA, LUZ, semilla=72 + v, fuerza_tex=0.6)
    # raicillas que se hunden en la tierra
    for k in range(6):
        i = 6 + k * 9
        x, y = cam[i]
        hebra(lz, lz.curva((x, y + 2), (x + (rng.random() - 0.5) * 6, y + 6), (x + (rng.random() - 0.5) * 10, 29.5), n=12), 2.2, 0.6, RAIZ_SECA, LUZ, semilla=k)
    m = lz.trazo(cam, 19, 15)
    grietas(lz, m, 73 + v, 5, "#100d0b")
    # el corazón seco de la raíz: grietas con un resto de luz violeta de Giza
    venas = np.clip(1 - np.abs(lz.ruido(5, 2, semilla=74 + v) - 0.5) * 30, 0, 1) * m * (lz.ruido(9, 2, semilla=75 + v) > 0.6)
    lz.pintar(venas, "#4d1a6b", 0.8)
    musgo_seco(lz, m, 76 + v, umbral=0.72, abajo=False)
    hierba_al_pie(lz, 0, 100, 29.6, 40, 77 + v)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- el Arco de Raíz
def portal(abierto):
    lz = Lienzo(72, 88, s=5, semilla=80)
    cx, base = 36, 86
    dentro = lz.poligono([(cx - 22, base - 2)] + [(cx + np.cos(a) * 22, base - 30 - np.sin(a) * 46) for a in np.linspace(np.pi, 0, 30)] + [(cx + 22, base - 2)])
    if abierto:
        # al otro lado: los Prados del Eco, con luz
        lz.pintar(dentro, lz.gradiente(["#97c1bf", "#c4ddd0", "#e8f0dc", "#f8e1a6"], desde=8, hasta=60))
        colina = dentro * np.clip((lz.y - (60 + 4 * np.sin(lz.x / 6))) * 2, 0, 1)
        lz.pintar(colina, rampa(HIERBA[3:7], lz.ruido(1.2, 2)))
        colina2 = dentro * np.clip((lz.y - (70 + 3 * np.sin(lz.x / 5 + 1))) * 2, 0, 1)
        lz.pintar(colina2, rampa(HIERBA[2:6], lz.ruido(1.0, 2)))
        for (tx, ty) in [(24, 62), (48, 60), (30, 61)]:
            lz.sombrear(lz.circulo(tx, ty - 3, 2.6), ["#24401f", "#355029", "#5d793e", "#8aa152"], 1.5, LUZ)
        lz.pintar(dentro * np.clip(1 - np.abs(lz.y - (base - 6)) / 2, 0, 1), "#fde27e", 0.3)
        lz.sumar_luz(lz.desenfocar(dentro, 4) * dentro, "#fff4d6", 0.35)
        cols = ["#2a160c", "#4a2a16", "#73432a", "#96603b", "#b7814f", "#d6a76c"]
    else:
        # dormido: oscuridad con el latido violeta de Giza y espinas que lo cierran
        lz.pintar(dentro, lz.gradiente(["#0d0716", "#170c26", "#2a0f3d"], desde=10, hasta=base))
        lz.sumar_luz(lz.desenfocar(lz.circulo(cx, 46, 8), 10) * dentro, "#4d1a6b", 0.8)
        rng = np.random.default_rng(81)
        esp = np.zeros((lz.H, lz.W))
        for k in range(14):
            a = np.pi * (0.05 + 0.9 * rng.random())
            p0 = (cx + np.cos(a) * 21, base - 30 - np.sin(a) * 44)
            p2 = (cx + (rng.random() - 0.5) * 30, base - 4 - rng.random() * 40)
            esp = np.maximum(esp, lz.trazo(lz.curva(p0, (cx + (rng.random() - 0.5) * 20, 50), p2, n=16), 1.6, 0.3))
        lz.pintar(esp * dentro, "#05030a")
        lz.pintar(np.clip(esp - np.roll(esp, lz.s, axis=0), 0, 1) * dentro, "#7a3aa3", 0.6)
        cols = RAIZ_SECA
    # el arco: raíces que suben trenzadas y se juntan arriba
    rng = np.random.default_rng(82)
    for k in range(4):
        fase = k / 4 * 2 * np.pi
        pts = []
        for a in np.linspace(-0.05, np.pi + 0.05, 70):
            tr = np.sin(a * 3 + fase) * 2.2
            pts.append((cx + np.cos(a) * (27 + tr), base - 30 - np.sin(a) * (50 + tr) if a > 0 and a < np.pi else base - 30))
        pts = [(x, y) for (x, y) in pts]
        pts = [(pts[0][0], base)] + pts + [(pts[-1][0], base)]
        hebra(lz, pts, 8.4 - k * 0.8, 6.8 - k * 0.6, cols, LUZ, semilla=83 + k)
        lz.pintar(np.clip(lz.trazo(pts, 8.6 - k * 0.8, 7.0 - k * 0.6) - lz.trazo(pts, 7.6 - k * 0.8, 6.0 - k * 0.6), 0, 1), cols[0], 0.7)
    # pies que se agarran al suelo
    for lado in (-1, 1):
        for k in range(2):
            x0 = cx + lado * 27
            hebra(lz, lz.curva((x0, base - 4), (x0 + lado * (4 + k * 3), base - 1), (x0 + lado * (7 + k * 5), base + 1), n=10), 3, 0.8, cols, LUZ, semilla=90 + k)
    if abierto:
        # la vida corriendo por las raíces y brotes nuevos
        vida = lz.trazo([(cx + np.cos(a) * 27, base - 30 - np.sin(a) * 50) for a in np.linspace(0, np.pi, 40)], 0.8)
        lz.sumar_luz(lz.desenfocar(vida, 1.2), "#f9b947", 0.7)
        for (bx, by) in [(10, 40), (34, 3), (60, 30), (14, 60)]:
            lz.sombrear(np.maximum(lz.elipse(bx - 1.4, by, 1.6, 0.8, 30), lz.elipse(bx + 1.4, by - 0.6, 1.6, 0.8, -30)),
                        ["#1f4a1a", "#3e9a35", "#6fcf4f", "#b8ef8e"], 0.6, LUZ)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- cráter
def crater():
    lz = Lienzo(56, 26, s=6, semilla=95)
    borde = lz.elipse(28, 13, 27, 12)
    tierra = ["#1d140f", "#2b1e17", "#3f2c21", "#533b2d", "#684937", "#7c5843"]
    dif, _ = lz.volumen(borde, 6, (0.6, 0.7, 0.5))
    lz.pintar(borde, rampa(tierra, np.clip(0.25 + dif * 0.6 + (lz.ruido(0.6, 2) - 0.5) * 0.3, 0, 1)))
    hondo = lz.elipse(28, 14, 18, 7)
    d = np.hypot((lz.x - 28) / 18, (lz.y - 14) / 7)
    lz.pintar(hondo, rampa(["#0a0706", "#1d140f", "#2b1e17", "#3f2c21"], np.clip(d * 1.1 - 0.1 + (lz.y - 14) / 30, 0, 1)))
    # una chispa de luz que queda en el fondo (donde cayó Maisha)
    lz.sumar_luz(lz.desenfocar(lz.circulo(28, 15, 2), 4) * hondo, "#f9b947", 0.5)
    lz.pintar(lz.circulo(28, 15, 0.8), "#fde27e")
    escombros(lz, 3, 53, 24, 12, 96, tam=(1.0, 2.4))
    escombros(lz, 6, 50, 4.5, 8, 97, tam=(0.8, 2.0))
    hierba_al_pie(lz, 2, 54, 25.5, 16, 98, seca=False)
    return lz.sprite(contorno=CONTORNO)


# ---------------------------------------------------------------- farol apagado (píxel a píxel)
L_FAROL = {"k": "#141410", "g": "#3d3f37", "G": "#686c5d", "L": "#989c8a", "c": "#2a2b26", "v": "#4a5240", "V": "#6e7d64",
           "o": "#1e1a12", "h": "#3b3220"}
FAROL = [
    "...kk.....",
    "..kGGk....",
    ".kGLLGk...",
    "kkkkkkkk..",
    "kVcvcVck..",
    "kvc.cvck..",
    "kVcvcVck..",
    "kkkkkkkk..",
    "..kGGk....",
    "...kGk....",
    "...kGkh...",
    "...kGkh...",
    "...kGk.h..",
    "...kGk....",
    "...kLk....",
    "...kGk....",
    "...kGk....",
    "...kGk....",
    "...kGk....",
    "...kGk....",
    "...kLk....",
    "...kGk....",
    "...kGk....",
    "...kGk....",
    "..kGGGk...",
    ".kGLLLGk..",
    ".kgggggk..",
    "..kkkkk...",
]


def main():
    from PIL import Image
    def guardar(nombre, arr):
        Image.fromarray(arr, "RGBA").save(os.path.join(SALIDA, nombre + ".png"))
        print("pintado", nombre, arr.shape[1], "×", arr.shape[0])
    guardar("ruina_casa", tira([ruina_casa(0), ruina_casa(1)]))
    guardar("pozo", pozo())
    guardar("torre", torre())
    guardar("monumento", monumento())
    guardar("raiz_gigante", tira([raiz_gigante(0), raiz_gigante(1)]))
    guardar("portal", tira([portal(False), portal(True)]))
    guardar("crater", crater())
    guardar("farol_apagado", mapa_pixeles(FAROL, L_FAROL))


if __name__ == "__main__":
    main()
