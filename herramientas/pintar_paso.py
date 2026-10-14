"""EL PASO DE PIEDRA, pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_paso.py

Genera en arte/mundos/raiz/paso/:
  casa_nungu.png        la CASA DE NUNGU, abandonada (176×144; la base de la puerta en (88, 142)): casa de piedra con
                        el tejado de lajas hundido por un lado (se ven las vigas), un observatorio pequeño con su
                        cúpula de cobre y el catalejo, la chimenea rota, ventanas tapiadas, la puerta entornada,
                        hiedra seca, cajas de muestras de roca con etiquetas y una carretilla volcada
  interior_nungu.png    la casa por dentro (320×208; suelo de (32, 72) a (288, 184), puerta abajo en x 148-172): el
                        taller de un científico abandonado: estanterías con piedras etiquetadas, la mesa con papeles
                        y un microscopio de latón, una pizarra con dibujos de la piedra de Giza, telarañas, hojas
                        secas por el suelo y, al fondo, el ARMARIO grande cerrado con una cerradura de hierro
  bloque.png            2 × 28×24 bloques de piedra cortados en la cantera (con marcas de cincel y cuñas)
  y el icono de la LLAVE del armario (16×16), el 26.º de arte/interfaz/objetos.png
  armario.png           2 × 56×64 el armario: 0 cerrado (cerradura de Corteza) · 1 abierto (dentro, una escalera
                        que baja a oscuras)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa, RAIZ  # noqa: E402
from cinematicas import PIEDRA, HIERBA, COBRE, MADERA, piedras, flores  # noqa: E402
from pintar_casa_shamba import vetas, rect, TRONCO, PIEDRA_C  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "mundos", "raiz", "paso")
LUZ = (-0.6, -0.7, 0.5)
LAJA = ["#121418", "#1e2228", "#2c3139", "#3c434d", "#4f5762", "#656e7a", "#808a95"]
PIEDRA_P = ["#2a2622", "#433d36", "#5e564c", "#7a7064", "#978b7d", "#b5a998", "#d2c7b5"]
LATON = ["#3a2a10", "#6a4e1e", "#9a7430", "#c89a44", "#e8c46a", "#fbe6a2"]
COBRE_V = ["#1e3a32", "#2e5a4a", "#447a62", "#62987a", "#88b496"]          # cobre viejo, verdoso
HIEDRA = ["#2a2614", "#443c1e", "#5e5428", "#7a6e36", "#988a48"]           # hiedra seca


def _tablas(lz, x0, y0, x1, y1, n=3, semilla=0):
    """Tablas clavadas de cualquier manera sobre un hueco (ventana tapiada)."""
    rng = np.random.default_rng(semilla)
    for k in range(n):
        yy = y0 + (k + 0.5) * (y1 - y0) / n + rng.uniform(-1, 1)
        inc = rng.uniform(-1.6, 1.6)
        t = lz.poligono([(x0 - 2, yy - 1.6 + inc), (x1 + 2, yy - 1.6 - inc), (x1 + 2, yy + 1.4 - inc), (x0 - 2, yy + 1.4 + inc)])
        lz.sombrear(t, MADERA[1:], 1, LUZ, textura=vetas(lz, 0.5, 9, semilla=semilla + k), fuerza_tex=0.4)
        for cx in (x0, x1):
            lz.pintar(lz.circulo(cx, yy - 0.1 + (inc if cx == x0 else -inc), 0.45), "#a3a4a6")


def _hiedra(lz, puntos, semilla=0, grosor=0.6):
    rng = np.random.default_rng(semilla)
    tallo = lz.trazo(puntos, grosor, grosor * 0.5)
    lz.pintar(tallo, HIEDRA[1])
    hojas = np.zeros((lz.H, lz.W))
    for (a, b) in zip(puntos, puntos[1:]):
        for t in np.linspace(0, 1, 5):
            x = a[0] + (b[0] - a[0]) * t + rng.uniform(-1.5, 1.5)
            y = a[1] + (b[1] - a[1]) * t + rng.uniform(-1, 1)
            hojas = np.maximum(hojas, lz.elipse(x, y, 1.2, 0.8, rng.uniform(0, 180)))
    lz.sombrear(hojas, HIEDRA, 0.6, LUZ)


def casa_nungu():
    lz = Lienzo(176, 144, s=4, semilla=901)
    x0, x1 = 24, 152
    suelo = 136
    # --- el observatorio, detrás a la derecha: una torrecilla de piedra con la cúpula de cobre abierta y el catalejo
    torre = rect(lz, 116, 10, 144, 70)
    piedras(lz, torre, tam=3.8, semilla=902, luz=LUZ, mortero="#2a2622", rampa_p=PIEDRA_P)
    lz.pintar(np.clip((lz.x - 128) / 16, 0, 1) * torre, "#120e0c", 0.4)
    cupula = lz.poligono([(113, 14)] + [(130 + np.cos(a) * 17, 14 - np.sin(a) * 12) for a in np.linspace(np.pi, 0, 30)] + [(147, 14)])
    lz.sombrear(cupula, COBRE_V, 5, LUZ, textura=lz.ruido(0.8, 2, semilla=903), fuerza_tex=0.35)
    for k in range(-3, 4):                                         # las costillas de la cúpula
        lz.pintar(lz.trazo([(130 + k * 4.6, 14), (130 + k * 1.6, 3)], 0.4) * cupula, COBRE_V[0], 0.7)
    rendija = lz.poligono([(127, 14), (126.5, 3.5), (133, 2.5), (133.5, 14)])
    lz.pintar(rendija, "#0a0a10")
    tubo = lz.trazo([(130, 9), (145, 1)], 1.5, 1.1)               # el catalejo, apuntando al cielo
    lz.sombrear(tubo, LATON[:4], 0.8, LUZ)
    lz.pintar(lz.circulo(145, 1.2, 0.9), "#0a0a10")
    for (a, b) in (((136, 6), (136.4, 8)), ((142, 3), (142.4, 5))):
        lz.pintar(lz.trazo([a, b], 1.0), LATON[1])
    # --- la chimenea rota, a la izquierda
    chim = rect(lz, 38, 18, 48, 50)
    piedras(lz, chim, tam=3.2, semilla=904, luz=LUZ, mortero="#2a2622", rampa_p=PIEDRA_P)
    for (x, y) in ((40, 17), (45, 16.5)):                       # ladrillos sueltos arriba (está rota)
        lz.sombrear(lz.elipse(x, y, 2, 1.3), PIEDRA_P[1:], 0.6, LUZ)
    # --- paredes de piedra
    muro = rect(lz, x0, 64, x1, suelo)
    piedras(lz, muro, tam=7.5, semilla=905, luz=LUZ, mortero="#1e1a16", rampa_p=PIEDRA_P)
    lz.pintar(np.clip((lz.x - 110) / 50, 0, 1) * muro, "#120e0c", 0.25)
    # manchas de humedad y líquenes
    liquen = (lz.ruido(2.4, 3, semilla=906) > 0.72) * muro
    lz.pintar(lz.desenfocar(liquen, 0.4), rampa(["#5e5a3a", "#7a7648", "#9a9658"], lz.ruido(0.7, 2)), 0.55)
    lz.pintar(np.clip((lz.y - 120) / 16, 0, 1) * muro, "#1a1814", 0.35)
    # --- el tejado de lajas: entero a la izquierda, hundido a la derecha (se ven las vigas y el cielo oscuro dentro)
    tejado = lz.poligono([(14, 68), (52, 26), (124, 26), (162, 68)])
    lajas_tex = ((lz.y - 26) % 5 < 0.7) * 1.0 + (np.abs(np.sin((lz.x + np.floor((lz.y - 26) / 5) * 3.1) * 0.9)) < 0.08) * 1.0
    lz.sombrear(tejado, LAJA, 6, LUZ, textura=1 - np.clip(lajas_tex, 0, 1) * 0.7 + lz.ruido(0.8, 2, semilla=907) * 0.3, fuerza_tex=0.5)
    musgo = (lz.ruido(2.0, 3, semilla=908) > 0.66) * tejado
    lz.pintar(lz.desenfocar(musgo, 0.5), rampa(["#2a3a1e", "#3e5228", "#566c34"], lz.ruido(0.6, 2)), 0.7)
    rngh = np.random.default_rng(914)
    borde_h = []
    for k in range(26):                                            # un agujero de bordes rotos, a trozos
        a = k / 26 * 2 * np.pi
        r = 1.0 + (0.28 if k % 2 else -0.12) + rngh.uniform(-0.12, 0.12)
        borde_h.append((110 + np.cos(a) * 17 * r, 46 + np.sin(a) * 12 * r))
    hueco = lz.poligono(borde_h)
    lz.pintar(hueco, "#08080c")
    lz.pintar(lz.desenfocar(hueco, 2) * (1 - hueco), "#08080c", 0.4)
    # lajas rotas y levantadas alrededor del agujero
    for k in range(10):
        a = k / 10 * 2 * np.pi + 0.2
        lx, ly = 110 + np.cos(a) * 19, 46 + np.sin(a) * 13.5
        lz.sombrear(lz.poligono([(lx - 2.6, ly - 1.2), (lx + 2.4, ly - 1.8), (lx + 2.8, ly + 1.2), (lx - 2.2, ly + 1.6)]), LAJA[2:], 0.8, LUZ)
    for (a, b) in (((95, 40), (126, 52)), ((98, 52), (125, 42)), ((104, 35), (116, 58))):   # vigas rotas
        v = lz.trazo([a, b], 1.8, 1.2) * np.clip(lz.desenfocar(hueco, 1.5) * 3, 0, 1)
        lz.sombrear(v, TRONCO, 0.8, LUZ, textura=vetas(lz, 0.5, 7), fuerza_tex=0.3)
    for (lx, ly, ang) in ((128, 66, 20), (104, 68, -15), (138, 70, 40)):    # lajas caídas por el suelo, delante
        laja = lz.elipse(lx, ly + 66, 4, 1.6, ang)
        lz.sombrear(laja, LAJA, 1, LUZ)
    # el alero: una tabla gruesa a lo largo
    alero = rect(lz, 12, 66, 164, 70)
    lz.sombrear(alero, TRONCO, 1.2, LUZ, textura=vetas(lz, 0.5, 13), fuerza_tex=0.35)
    lz.pintar(lz.desenfocar(rect(lz, x0, 70, x1, 76), 1.4) * muro, "#120e0c", 0.5)
    # --- ventanas tapiadas
    for vx in (36, 122):
        hueco_v = rect(lz, vx, 82, vx + 18, 102)
        lz.pintar(hueco_v, "#0c0a0a")
        dintel = rect(lz, vx - 2, 79, vx + 20, 82)
        lz.sombrear(dintel, PIEDRA_P[1:], 1, LUZ)
        _tablas(lz, vx, 82, vx + 18, 102, n=3, semilla=vx)
        lz.pintar(lz.trazo([(vx + 4, 89), (vx + 7, 91)], 0.4), "#d2c7b5", 0.6)                # un cristal roto asomando
    # --- la puerta entornada: el marco de piedra, la hoja abierta hacia dentro y la oscuridad
    marco = rect(lz, 75, 92, 101, suelo)
    lz.sombrear(marco, PIEDRA_P, 1.5, LUZ)
    vano = rect(lz, 78, 95, 98, suelo)
    lz.pintar(vano, "#060506")
    hoja = lz.poligono([(78, 95), (86, 97), (86, suelo - 1), (78, suelo)])
    lz.sombrear(hoja, MADERA[1:], 2, LUZ, textura=vetas(lz, 0.5, 13, False), fuerza_tex=0.45)
    lz.pintar(lz.circulo(84.5, 116, 0.8), LATON[3])
    # telaraña en la esquina de la puerta
    for r in (2.5, 4.5, 6.5):
        tela = np.clip(1 - np.abs(np.hypot(lz.x - 98, lz.y - 95) - r) / 0.25, 0, 1) * (lz.x < 98) * (lz.y > 95)
        lz.pintar(tela, "#d8d8e0", 0.45)
    for a in np.linspace(np.pi / 2, np.pi, 4):
        lz.pintar(lz.trazo([(98, 95), (98 + np.cos(a) * 7, 95 + np.sin(a) * 7)], 0.2), "#d8d8e0", 0.45)
    # el cartel de Nungu sobre la puerta: una tabla con una N y un martillo de geólogo
    cartel = rect(lz, 79, 84, 97, 91)
    lz.sombrear(cartel, MADERA[2:], 1, LUZ, textura=vetas(lz, 0.5, 9), fuerza_tex=0.35)
    lz.pintar(lz.trazo([(83, 89.5), (83, 85.5), (86, 89.5), (86, 85.5)], 0.6), "#1a120c")
    lz.pintar(lz.trazo([(90, 89.5), (94, 85.5)], 0.6), "#3a3028")
    lz.pintar(lz.trazo([(92.5, 85), (95.5, 86.5)], 0.9), "#6a6c6f")
    lz.pintar(lz.trazo([(80, 84), (78, 81)], 0.3) + lz.trazo([(96, 84), (98, 81)], 0.3), "#3a3028")       # colgado de dos clavos
    # escalón
    esc = rect(lz, 72, suelo - 1, 104, suelo + 3)
    lz.sombrear(esc, PIEDRA_P, 1.2, LUZ, textura=lz.ruido(0.7, 2), fuerza_tex=0.3)
    # --- hiedra seca trepando por la pared
    _hiedra(lz, [(28, 134), (30, 118), (27, 104), (32, 92), (30, 78)], semilla=909)
    _hiedra(lz, [(150, 134), (147, 120), (150, 108), (146, 96)], semilla=910)
    _hiedra(lz, [(104, 134), (106, 124), (103, 114)], semilla=911, grosor=0.5)
    # --- cajas de muestras de roca, con etiquetas, y una carretilla volcada
    for (cx_, cy_, w_, h_) in ((108, 124, 14, 12), (118, 128, 12, 9)):
        caja = rect(lz, cx_, cy_, cx_ + w_, cy_ + h_)
        lz.sombrear(caja, COBRE, 2, LUZ, textura=vetas(lz, 0.5, 11, semilla=cx_), fuerza_tex=0.35)
        lz.pintar(rect(lz, cx_ + 3, cy_ + 3, cx_ + w_ - 3, cy_ + 6), "#efe0bf")
        lz.pintar(lz.trazo([(cx_ + 4, cy_ + 4.5), (cx_ + w_ - 4, cy_ + 4.5)], 0.25), "#5a3a22")
        for k in range(3):
            p = lz.elipse(cx_ + 3 + k * (w_ - 6) / 2, cy_ - 0.8, 1.8, 1.4)
            lz.sombrear(p, [PIEDRA_P[2:], ["#3a3048", "#6a5a88", "#9a86c0"], LAJA[2:]][k % 3], 0.8, LUZ)
    # una piedra con una veta violeta de Giza, sobre la caja (lo que estudiaba)
    gz = lz.elipse(114, 121.6, 2.6, 1.8)
    lz.sombrear(gz, PIEDRA_P[1:], 1, LUZ)
    lz.pintar(lz.trazo([(112.5, 121), (115.5, 122.2)], 0.4), "#b070e0")
    lz.sumar_luz(lz.desenfocar(lz.trazo([(112.5, 121), (115.5, 122.2)], 0.4), 1.5), "#a855d6", 0.5)
    carro = lz.poligono([(44, 130), (62, 126), (64, 134), (46, 137)])
    lz.sombrear(carro, MADERA[1:], 2, LUZ, textura=vetas(lz, 0.5, 9), fuerza_tex=0.4)
    rueda = np.clip(lz.elipse(52, 136, 3.4, 3.4) - lz.elipse(52, 136, 2.2, 2.2), 0, 1)
    lz.sombrear(rueda, TRONCO, 0.8, LUZ)
    for (a, b) in (((60, 128), (70, 120)), ((62, 132), (72, 126))):
        lz.sombrear(lz.trazo([a, b], 0.9), MADERA[2:], 0.6, LUZ)
    for k in range(5):                                             # piedras derramadas
        p = lz.elipse(38 + k * 3.4, 137 + (k % 2), 1.6, 1.1)
        lz.sombrear(p, PIEDRA_P[1:], 0.8, LUZ)
    # hierba seca al pie de la casa
    rng = np.random.default_rng(912)
    hierba = np.zeros((lz.H, lz.W))
    for k in range(160):
        hx = 14 + rng.random() * 152
        if 70 < hx < 106 and rng.random() < 0.8:
            continue
        hy = 134 + rng.random() * 6
        hierba = np.maximum(hierba, lz.trazo([(hx, hy), (hx + (rng.random() - 0.5) * 2.4, hy - 2 - rng.random() * 3.5)], 0.7, 0.3))
    lz.sombrear(hierba, ["#3a3418", "#5a5024", "#7a6e36", "#9a8c4c", "#b8aa66"], 0.5, LUZ)
    flores(lz, 5, (16, 136, 70, 140), [["#6a5a88", "#9a86c0", "#c8b8e8"]], semilla=913, tam=0.6)
    return lz


def bloque(k):
    """Un bloque de piedra cortado en la cantera (28×24): de caras planas, con las marcas de los cinceles y las
    cuñas de madera que se quedaron metidas. k: 0 un bloque grande; 1 dos bloques apilados."""
    W, H = 28, 24
    lz = Lienzo(W, H, s=6, semilla=941 + k)
    def cubo(x0, y0, w, h, alto):
        cara = rect(lz, x0, y0 + alto * 0.45, x0 + w, y0 + h)
        tapa = lz.poligono([(x0, y0 + alto * 0.45), (x0 + 2, y0), (x0 + w + 2, y0), (x0 + w, y0 + alto * 0.45)])
        lado = lz.poligono([(x0 + w, y0 + alto * 0.45), (x0 + w + 2, y0), (x0 + w + 2, y0 + h - alto * 0.45), (x0 + w, y0 + h)])
        marcas = ((lz.x * 1.3 + lz.y * 0.4) % 2.2 < 0.35) * 1.0
        lz.sombrear(cara, PIEDRA_P, 2, LUZ, textura=1 - marcas * 0.5 + lz.ruido(0.5, 2, semilla=x0) * 0.3, fuerza_tex=0.4)
        lz.sombrear(tapa, PIEDRA_P[2:], 1.5, LUZ, textura=lz.ruido(0.6, 2, semilla=y0), fuerza_tex=0.3)
        lz.pintar(lado, PIEDRA_P[1])
    if k == 0:
        cubo(2, 6, 22, 17, 8)
        for x in (8, 15):                                              # cuñas de madera en una grieta
            lz.sombrear(lz.poligono([(x, 6.5), (x + 2, 6.5), (x + 1, 11)]), MADERA[2:], 0.6, LUZ)
        lz.pintar(lz.trazo([(6, 7), (20, 7.5)], 0.35), "#1a1814")
    else:
        cubo(1, 11, 20, 12, 6)
        cubo(6, 2, 14, 10, 5)
    musgo = (lz.ruido(1.5, 2, semilla=943 + k) > 0.72) * (lz.y > 14)
    lz.pintar(musgo, "#5a6a34", 0.6)
    return lz.sprite(contorno=0.4)


def armario(abierto):
    """El armario del fondo del taller de Nungu: alto, de madera oscura con molduras, y una cerradura de hierro
    grande (hecha por Corteza: lleva su marca, un martillo sobre un yunque). Abierto: las puertas de par en par y
    dentro, en vez de ropa, una trampilla con una escalera de piedra que baja a oscuras y huele a setas."""
    W, H = 56, 64
    lz = Lienzo(W, H, s=4, semilla=921 + abierto)
    lz.pintar(lz.desenfocar(rect(lz, 4, 58, 52, 64), 1.5), "#050404", 0.5)
    cuerpo = rect(lz, 6, 4, 50, 62)
    lz.sombrear(cuerpo, MADERA, 4, LUZ, textura=vetas(lz, 0.5, 15, False, semilla=922), fuerza_tex=0.35)
    corona = lz.poligono([(4, 6), (8, 1), (48, 1), (52, 6)])
    lz.sombrear(corona, MADERA[2:], 1.5, LUZ, textura=vetas(lz, 0.5, 13), fuerza_tex=0.3)
    lz.pintar(rect(lz, 4, 6, 52, 7.4), MADERA[1])
    if not abierto:
        for (a, b) in ((9, 27), (29, 47)):
            p = rect(lz, a, 9, b, 57)
            lz.sombrear(p, MADERA[1:], 2, LUZ, textura=vetas(lz, 0.5, 15, False, semilla=a), fuerza_tex=0.4)
            mold = np.clip(rect(lz, a + 2.5, 12, b - 2.5, 30) - rect(lz, a + 3.5, 13, b - 3.5, 29), 0, 1)
            mold = np.maximum(mold, np.clip(rect(lz, a + 2.5, 34, b - 2.5, 54) - rect(lz, a + 3.5, 35, b - 3.5, 53), 0, 1))
            lz.pintar(mold, MADERA[5], 0.6)
        lz.pintar(rect(lz, 27.6, 9, 28.4, 57), "#0a0606")
        # la cerradura de hierro de Corteza, grande, con su marca
        cerr = rect(lz, 23, 28, 33, 40)
        lz.sombrear(cerr, ["#1b1c1f", "#2e3034", "#4a4c50", "#6a6c6f", "#9a9c9f"], 1.2, LUZ)
        lz.pintar(lz.elipse(28, 34.5, 1.1, 1.6), "#050505")
        lz.pintar(rect(lz, 27.6, 35, 28.4, 37.6), "#050505")
        lz.pintar(lz.trazo([(25, 30.5), (27.4, 30.5)], 0.35) + lz.trazo([(26.2, 29.6), (26.2, 32)], 0.35), "#e6a852")   # la marca: un martillo
        for (x, y) in ((24, 29), (32, 29), (24, 39), (32, 39)):
            lz.pintar(lz.circulo(x, y, 0.5), "#9a9c9f")
        lz.pintar(lz.trazo([(18, 33), (23, 34)], 1.6) + lz.trazo([(33, 34), (38, 33)], 1.6), "#2e3034")          # cadena
    else:
        dentro = rect(lz, 9, 9, 47, 57)
        lz.pintar(dentro, "#0a0708")
        # la trampilla abierta y la escalera que baja
        for k in range(6):
            y = 30 + k * 4.4
            esc = rect(lz, 14 + k * 1.2, y, 42 - k * 1.2, y + 2.6)
            lz.sombrear(esc, PIEDRA_P[: 5 - min(k, 3)], 0.8, LUZ)
            lz.pintar(rect(lz, 14 + k * 1.2, y + 2.6, 42 - k * 1.2, y + 4.4), "#050404", 0.9)
        lz.pintar(lz.desenfocar(rect(lz, 14, 50, 42, 57), 2), "#000000", 0.8)
        # un brillo violeta de setas que sube de abajo
        lz.sumar_luz(lz.desenfocar(lz.elipse(28, 56, 10, 3), 4), "#a855d6", 0.6)
        for (x, y) in ((20, 44), (34, 47), (26, 51)):
            lz.pintar(lz.circulo(x, y, 0.5), "#e6c8ff")
        # las dos puertas abiertas, de canto
        for (a, b) in ((0, 7), (49, 56)):
            p = rect(lz, a, 6, b, 60)
            lz.sombrear(p, MADERA[1:], 1, LUZ, textura=vetas(lz, 0.5, 15, False, semilla=a), fuerza_tex=0.4)
        lz.pintar(rect(lz, 1, 32, 6, 38), "#3a3c40")                                        # la cerradura, abierta
    return lz.sprite(contorno=0.4)


def interior():
    """El taller de Nungu por dentro (320×208, como las demás casas): suelo de tablas polvorientas, paredes de
    piedra, el armario al fondo en el centro, estanterías con piedras etiquetadas, la mesa con papeles y un
    microscopio, una pizarra con dibujos de la veta violeta, telarañas, hojas secas y un rayo de luz del tejado roto."""
    lz = Lienzo(320, 208, s=2, semilla=931)
    lz.pintar(rect(lz, 0, 0, 320, 208), "#0a0808")
    # la pared del fondo (de piedra) y las laterales
    fondo = rect(lz, 24, 8, 296, 74)
    piedras(lz, fondo, tam=7.0, semilla=932, luz=LUZ, mortero="#1e1a16", rampa_p=PIEDRA_P)
    lz.pintar(np.clip((74 - lz.y) / 66, 0, 1) * fondo, "#0a0808", 0.35)
    for (a, b) in ((24, 32), (288, 296)):
        lat = rect(lz, a, 8, b, 190)
        piedras(lz, lat, tam=5.0, semilla=933 + a, luz=LUZ, mortero="#1e1a16", rampa_p=PIEDRA_P)
        lz.pintar(lat, "#0a0808", 0.45)
    # el suelo de tablas, con polvo
    suelo = rect(lz, 32, 72, 288, 190)
    fila_t = np.floor((lz.y - 72) / 9)
    junta_h = ((lz.y - 72) % 9) < 0.9
    junta_v = ((lz.x + fila_t * 37) % 64) < 0.9
    tono_t = (np.sin(fila_t * 12.9898 + np.floor((lz.x + fila_t * 37) / 64) * 78.233) * 43758.5453) % 1.0
    v = 0.35 + (tono_t - 0.5) * 0.25 + (vetas(lz, 0.5, 21, semilla=934) - 0.5) * 0.35 - junta_h * 0.4 - junta_v * 0.3
    lz.pintar(suelo, rampa(["#1e140e", "#2e2016", "#45301f", "#5a3f28", "#6e4e32", "#845e3c"], np.clip(v, 0, 1)))
    polvo = lz.desenfocar((lz.ruido(10, 3, semilla=935) > 0.55) * suelo, 3)
    lz.pintar(polvo, "#8a7a62", 0.12)
    # el rayo de luz que entra por el tejado roto (a la derecha)
    rayo = lz.poligono([(214, 8), (244, 8), (262, 170), (206, 170)])
    lz.sumar_luz(lz.desenfocar(rayo, 6), "#f0dca8", 0.18)
    luz_suelo = lz.elipse(232, 160, 34, 12)
    lz.sumar_luz(lz.desenfocar(luz_suelo, 6), "#f0dca8", 0.25)
    for k in range(18):                                          # motas de polvo en el rayo
        rng = np.random.default_rng(936 + k)
        x, y = rng.uniform(214, 256), rng.uniform(20, 160)
        lz.pintar(lz.circulo(x, y, 0.6), "#fff4d0", 0.6)
    # estanterías a la izquierda, con piedras etiquetadas
    est = rect(lz, 40, 18, 100, 72)
    lz.sombrear(est, MADERA, 3, LUZ, textura=vetas(lz, 0.5, 13, False, semilla=937), fuerza_tex=0.3)
    for k, y in enumerate((30, 44, 58, 70)):
        lz.pintar(rect(lz, 42, y - 1.5, 98, y), MADERA[4])
        lz.pintar(rect(lz, 42, y, 98, y + 1.2), "#0a0606")
        if y < 70:
            for j in range(5):
                rx = 47 + j * 11
                col = [PIEDRA_P[2:], LAJA[2:], ["#3a3048", "#6a5a88", "#9a86c0"], COBRE[2:], PIEDRA_P[3:]][(j + k) % 5]
                p = lz.elipse(rx, y - 4.5, 3.6, 3)
                lz.sombrear(p, col, 1.2, LUZ)
                lz.pintar(rect(lz, rx - 3, y - 1.3, rx + 3, y - 0.2), "#efe0bf")
    lz.pintar(lz.trazo([(56, 58 - 4), (60, 56)], 0.5), "#b070e0")                     # la que tiene la veta violeta
    # la pizarra a la derecha del armario, con dibujos de tiza
    piz = rect(lz, 196, 22, 252, 58)
    lz.sombrear(piz, MADERA[2:], 1.5, LUZ)
    lz.pintar(rect(lz, 199, 25, 249, 55), "#1c2420")
    for pts in ([(204, 46), (212, 34), (220, 44), (228, 30), (236, 42)], [(206, 50), (244, 50)],
                [(238, 32), (244, 28), (246, 36), (240, 38), (238, 32)]):
        lz.pintar(lz.trazo(pts, 0.6), "#d8dcd0", 0.8)
    lz.pintar(lz.trazo([(212, 34), (218, 40), (226, 36)], 0.6), "#c890f0", 0.8)          # la veta, en tiza violeta
    # el armario lo pone el juego encima (armario.png), en el centro del fondo
    # la mesa con papeles y el microscopio, a la derecha
    mesa = rect(lz, 214, 92, 280, 116)
    lz.sombrear(mesa, MADERA, 3, LUZ, textura=vetas(lz, 0.5, 17, semilla=938), fuerza_tex=0.35)
    for (x, y) in ((218, 116), (276, 116)):
        lz.sombrear(rect(lz, x, y, x + 4, y + 18), MADERA[1:], 1, LUZ)
    for k in range(5):
        rng = np.random.default_rng(939 + k)
        x, y = rng.uniform(220, 250), rng.uniform(95, 108)
        hoja = lz.poligono([(x, y), (x + 9, y - 1), (x + 10, y + 6), (x + 1, y + 7)])
        lz.sombrear(hoja, ["#a8987a", "#d8c8a6", "#efe0bf"], 0.6, LUZ)
        lz.pintar(lz.trazo([(x + 2, y + 2), (x + 7, y + 1.6)], 0.25) + lz.trazo([(x + 2, y + 4), (x + 8, y + 3.6)], 0.25), "#5a4a3a", 0.7)
    mic = lz.trazo([(262, 108), (262, 96), (266, 92)], 1.6, 1.2)
    lz.sombrear(mic, LATON, 0.8, LUZ)
    lz.sombrear(lz.elipse(262, 109, 5, 1.6), LATON[:4], 0.8, LUZ)
    lz.pintar(lz.circulo(266.6, 91.4, 1.1), "#0a0a10")
    # telarañas en las esquinas de arriba
    for (cx, cy, sx) in ((32, 8, 1), (288, 8, -1)):
        for r in (5, 10, 15, 20):
            tela = np.clip(1 - np.abs(np.hypot(lz.x - cx, lz.y - cy) - r) / 0.35, 0, 1) * ((lz.x - cx) * sx > 0) * (lz.y > cy)
            lz.pintar(tela, "#d8d8e0", 0.35)
        for a in np.linspace(0, np.pi / 2, 5):
            lz.pintar(lz.trazo([(cx, cy), (cx + sx * np.cos(a) * 22, cy + np.sin(a) * 22)], 0.3), "#d8d8e0", 0.35)
    # hojas secas que han entrado por el tejado
    rng = np.random.default_rng(940)
    for k in range(26):
        x, y = rng.uniform(40, 280), rng.uniform(80, 184)
        h = lz.elipse(x, y, 1.8, 1.0, rng.uniform(0, 180))
        lz.sombrear(h, [["#5a3a1a", "#8a5a2a", "#b07a3a"], ["#4a4020", "#7a6a30", "#9a8a44"]][k % 2], 0.6, LUZ)
    # una silla volcada y una alfombra raída
    alf = lz.elipse(160, 140, 46, 18)
    lz.sombrear(alf, ["#3a1e1e", "#5a2e2a", "#7a443a", "#94584a"], 4, LUZ, textura=(np.sin(lz.x * 0.8) * np.sin(lz.y * 0.8) > 0.4) * 1.0, fuerza_tex=0.25)
    lz.pintar((lz.ruido(3, 2, semilla=941) > 0.7) * alf, "#1e140e", 0.6)
    silla = lz.poligono([(70, 150), (86, 146), (88, 152), (72, 156)])
    lz.sombrear(silla, MADERA[1:], 1, LUZ)
    for (a, b) in (((72, 156), (68, 164)), ((86, 152), (90, 160))):
        lz.pintar(lz.trazo([a, b], 1.2), MADERA[2])
    # el hueco de la puerta, abajo
    lz.pintar(rect(lz, 148, 186, 172, 208), "#050404")
    vineta = np.clip((np.abs(lz.x - 160) / 160) ** 2 + (np.abs(lz.y - 120) / 120) ** 2, 0, 1)
    lz.pintar(vineta * suelo, "#050404", 0.35)                   # viñeta: rincones oscuros
    return lz


def llave():
    """El icono de la llave del armario (16×16): hierro con hollín, con el martillo de Corteza grabado en el ojo."""
    lz = Lienzo(16, 16, s=8, semilla=951)
    aro = np.clip(lz.circulo(5, 5, 4.2) - lz.circulo(5, 5, 1.9), 0, 1)
    cana = lz.trazo([(7.6, 7.6), (14, 14)], 1.8)
    dientes = np.maximum(lz.trazo([(11.2, 11.2), (9.2, 13.2)], 1.4), lz.trazo([(13.2, 13.2), (11.4, 15)], 1.4))
    hierro = np.clip(aro + cana + dientes, 0, 1)
    lz.sombrear(hierro, ["#2a2a30", "#4a4a52", "#6e6e78", "#9a9aa4", "#cfcfd8"], 1.2, LUZ)
    lz.pintar(hierro * (lz.ruido(0.6, 1, semilla=952) > 0.6), "#1e1a18", 0.5)             # hollín
    lz.pintar(lz.circulo(5, 5, 1.0), "#e6a852")                                          # el martillito, en oro
    return lz.sprite(contorno=0.6)


def main():
    from PIL import Image
    os.makedirs(SALIDA, exist_ok=True)
    casa = casa_nungu()
    Image.fromarray(casa.sprite(contorno=0.4), "RGBA").save(os.path.join(SALIDA, "casa_nungu.png"))
    Image.fromarray(np.concatenate([bloque(0), bloque(1)], axis=1), "RGBA").save(os.path.join(SALIDA, "bloque.png"))
    hoja = np.concatenate([armario(0), armario(1)], axis=1)
    Image.fromarray(hoja, "RGBA").save(os.path.join(SALIDA, "armario.png"))
    Image.fromarray(interior().sprite(contorno=0.0), "RGBA").save(os.path.join(SALIDA, "interior_nungu.png"))
    # el icono de la llave en la mochila: el 26.º de objetos.png (índice 25)
    ruta = os.path.join(RAIZ, "arte", "interfaz", "objetos.png")
    viejos = Image.open(ruta).convert("RGBA")
    n = max(26, viejos.width // 16)
    iconos = Image.new("RGBA", (16 * n, 16), (0, 0, 0, 0))
    iconos.alpha_composite(viejos.crop((0, 0, min(viejos.width, 16 * 25), 16)), (0, 0))
    if viejos.width > 16 * 26:
        iconos.alpha_composite(viejos.crop((16 * 26, 0, viejos.width, 16)), (16 * 26, 0))
    iconos.alpha_composite(Image.fromarray(llave(), "RGBA"), (16 * 25, 0))
    iconos.save(ruta)
    print("Paso de Piedra pintado en", SALIDA)


if __name__ == "__main__":
    main()
