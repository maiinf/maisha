"""Ilustraciones del Bosque Cobrizo (con el pintor de las cinemáticas; se pintan junto a las demás):

    python3 herramientas/cinematicas.py 9_pembe_libre

  9_pembe_libre   Pembe, ya libre del hierro, inclina la cabeza ante Maisha en un claro del bosque, al atardecer.
                  La luz entra entre las copas cobrizas; por el suelo quedan los trozos de hierro, apagándose.
"""
import cv2
import numpy as np

from pintor import Lienzo, rampa  # noqa: F401
import cinematicas as ci

W, H = ci.W, ci.H
COBRE = ["#24180f", "#3d3214", "#5a3f1c", "#704f25", "#a37036", "#c68756", "#e2a978", "#f3cf9e"]
ROJIZO = ["#2a140c", "#472b14", "#794123", "#ab5031", "#cc6351", "#e48a72", "#f4b39a"]
PELO = ci.PELO
LUZ = (0.65, -0.65, 0.5)          # el sol, arriba a la derecha


def _hojas_suelo(lz, n, zona, semilla):
    rng = np.random.default_rng(semilla)
    x0, y0, x1, y1 = zona
    for _ in range(n):
        x, y = x0 + rng.random() * (x1 - x0), y0 + rng.random() * (y1 - y0)
        e = 0.6 + (y - y0) / max(1, (y1 - y0)) * 1.2           # más grandes cerca
        col = [COBRE[3:7], ROJIZO[2:6], COBRE[4:8]][rng.integers(3)]
        lz.sombrear(lz.elipse(x, y, 2.2 * e, 1.0 * e, rng.random() * 180), col, 0.8 * e, LUZ)


def _ciervo(lz):
    """Pembe libre, de lado, mirando a la izquierda (hacia Maisha): un ciervo esbelto, de patas largas, que baja la
    cabeza en una reverencia (el hocico a la altura del pecho). Sus astas, de madera viva, suben con hojas cobrizas."""
    G = 214
    pelo = ci.pelo(lz, 31)
    ilum = dict(recorte=("#ffd98a", 0.7), recorte_dir=(1, -0.7))
    # sombra en el suelo
    lz.pintar(lz.desenfocar(lz.elipse(404, G + 2, 62, 6), 2.0), "#120a06", 0.55)

    def pata(pts, g0, g1, oscura):
        m = lz.trazo(pts, g0, g1)
        cols = PELO[:5] if oscura else PELO[1:7]
        lz.sombrear(m, cols, 2.4, LUZ, textura=pelo, fuerza_tex=0.12, **({} if oscura else ilum))
        x_, y_ = pts[-1]
        pezuna = lz.poligono([(x_ - 3.2, G + 0.5), (x_ + 3.2, G + 0.5), (x_ + 2.4, G - 3.5), (x_ - 2.4, G - 3.5)])
        lz.sombrear(pezuna, ["#0a0606", "#1e1410", "#3a2a22"], 1.2, LUZ)
        lz.pintar(lz.trazo([(x_ - 2.6, G - 4.2), (x_ + 2.6, G - 4.2)], 0.9), "#e8d0a8", 0.5)
    # las patas del otro lado (más oscuras): delantera recta, trasera con el corvejón hacia atrás
    pata([(378, 164), (377, 186), (376, 198), (375, G - 3)], 8.0, 3.0, True)
    pata([(444, 158), (452, 180), (446, 194), (448, G - 3)], 10.0, 3.0, True)
    # el cuerpo: tronco esbelto, el pecho hondo delante y el anca redonda detrás
    tronco = lz.elipse(408, 151, 37, 17, -3)
    pecho = lz.elipse(372, 152, 18, 18, 10)
    anca = lz.elipse(442, 148, 18, 17)
    paleta = lz.elipse(374, 160, 11, 15, 10)
    muslo = lz.elipse(442, 162, 13, 17, -15)
    cuerpo = np.clip(tronco + pecho + anca + paleta + muslo, 0, 1)
    lz.sombrear(cuerpo, PELO, 18, LUZ, textura=pelo, fuerza_tex=0.14, rebote=("#4a2a16", 0.3), **ilum)
    lz.pintar(lz.desenfocar(lz.elipse(408, 163, 32, 5) * cuerpo, 2.0), "#e8cfa8", 0.35)        # la tripa, clara
    lz.pintar(lz.desenfocar(lz.elipse(455, 146, 8, 11) * cuerpo, 1.6), "#f2e2c4", 0.55)        # la grupa blanca
    # musgo y hojitas donde estaban las placas de hierro (manchitas irregulares, no rectángulos)
    rng = np.random.default_rng(33)
    for k in range(5):
        cx_, cy_ = 386 + k * 14 + rng.normal(0, 2), 136 + rng.normal(0, 1)
        musgo = lz.elipse(cx_, cy_, 5 + rng.random() * 2, 2.2, rng.normal(0, 10)) * (lz.ruido(0.5, 2, semilla=70 + k) > 0.35)
        lz.sombrear(musgo, ci.HIERBA[3:8], 1.4, LUZ)
    # las patas de este lado
    pata([(370, 166), (368, 188), (367, 200), (365, G)], 9.0, 3.2, False)
    pata([(438, 164), (446, 186), (440, 199), (441, G)], 11.0, 3.2, False)
    for (x_, y_) in ((368, 188), (446, 186)):
        lz.sombrear(lz.circulo(x_, y_, 2.6), PELO[1:7], 1.6, LUZ)          # la rodilla y el corvejón
    # el rabo, corto y claro por debajo
    lz.sombrear(lz.trazo([(458, 140), (463, 144), (462, 150)], 4.2, 2.6), PELO[2:7], 1.6, LUZ)
    lz.pintar(lz.elipse(461, 149, 2.4, 2.6), "#f2e2c4", 0.85)
    # el cuello, largo, que baja en la reverencia
    cuello = lz.trazo(lz.curva((374, 146), (346, 144), (326, 168), n=30), 20, 10)
    lz.sombrear(cuello, PELO, 9, LUZ, textura=pelo, fuerza_tex=0.14, **ilum)
    lz.pintar(lz.desenfocar(lz.elipse(340, 162, 6, 9, 35) * cuello, 2.0), "#f0dcb0", 0.4)      # la garganta clara
    for k in range(6):
        y_ = 148 + k * 4
        lz.pintar(lz.trazo([(352 - k * 3, y_), (349 - k * 3, y_ + 6)], 1.2, 0.3), PELO[2], 0.6)   # la melena
    # la cabeza: el cráneo y el hocico largo, bajados; la oreja hacia atrás; el ojo cerrado (en paz)
    craneo = lz.elipse(321, 172, 12.5, 9.5, 35)
    hocico = lz.elipse(307, 185, 7.5, 5.6, 40)
    cabeza = np.clip(craneo + hocico + lz.trazo([(318, 176), (309, 184)], 8, 6), 0, 1)
    lz.sombrear(cabeza, PELO, 6, LUZ, textura=pelo, fuerza_tex=0.12, **ilum)
    lz.pintar(lz.desenfocar(lz.elipse(310, 185, 5, 3.6, 40) * cabeza, 1.0), "#e8d0a8", 0.45)
    lz.pintar(lz.elipse(304, 188, 3.0, 2.2, 40), "#1b100b")                                   # la nariz
    lz.pintar(lz.circulo(303.4, 187.4, 0.6), "#c8b8a8", 0.8)
    lz.pintar(lz.trazo([(318, 171), (324, 173)], 0.9), "#140c0a")                             # el ojo cerrado
    lz.pintar(lz.trazo([(318, 172.5), (323, 174.5)], 0.5), "#ecd09a", 0.4)
    oreja = lz.poligono([(328, 166), (343, 160), (339, 165), (330, 171)])
    lz.sombrear(oreja, PELO[2:8], 2.0, LUZ, **ilum)
    lz.pintar(lz.poligono([(331, 167), (340, 162.5), (337, 165.5)]), "#c8987a", 0.6)
    # las astas: de madera viva, que salen de la cabeza y suben, con hojas cobrizas y rojizas y brotes que brillan
    for k, (dx, sombra) in enumerate(((-7, True), (0, False))):
        base = (326 + dx * 0.5, 165)
        tronco = [base, (330 + dx, 146), (334 + dx * 1.4, 124), (330 + dx * 1.8, 102), (322 + dx * 2.2, 80)]
        cols = ci.MADERA[0:4] if sombra else ["#251812", "#3a2418", "#5a3826", "#7d5034", "#a0704a"]
        ci.hebra(lz, tronco, 6.5, 2.8, cols, LUZ, semilla=40 + k)
        for i, largo in enumerate((22, 26, 18)):
            bx, by = tronco[i + 1]
            fin = (bx - largo * 0.55 + (i % 2) * largo * 0.9, by - largo * 0.75)
            punta = lz.curva((bx, by), (bx - largo * 0.1 + (i % 2) * largo * 0.4, by - largo * 0.45), fin, n=14)
            ci.hebra(lz, punta, 3.4, 1.4, cols, LUZ, semilla=50 + i + k * 5)
        rng = np.random.default_rng(60 + k * 7)
        puntas = [tronco[-1]] + [(tronco[i + 1][0] - l * 0.55 + (i % 2) * l * 0.9, tronco[i + 1][1] - l * 0.75) for i, l in enumerate((22, 26, 18))]
        for (fx, fy) in puntas:
            for h in range(7 if not sombra else 4):
                hx, hy = fx + (rng.random() - 0.5) * 13, fy + (rng.random() - 0.5) * 8
                col = [COBRE[4:8], ROJIZO[3:7], COBRE[3:7]][h % 3]
                lz.sombrear(lz.elipse(hx, hy, 4.8, 2.3, rng.random() * 180), col, 1.8, LUZ, textura=lz.ruido(0.5, 1), fuerza_tex=0.25)
            if not sombra:
                lz.sumar_luz(lz.desenfocar(lz.circulo(fx, fy - 3, 3), 4), "#fde27e", 0.6)
                lz.pintar(lz.circulo(fx, fy - 3, 1.5), "#fff3c4")


def pembe_libre():
    """«El hierro se le cae a trozos. Debajo, sus astas vuelven a ser ramas con hojas de cobre.
    Pembe, el guardián del bosque, inclina la cabeza ante Maisha... y se pierde entre los árboles.»"""
    lz = Lienzo(W, H, semilla=91)
    # el fondo: el bosque al atardecer, con luz dorada que llega de arriba a la derecha
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#1f140d", "#3a2414", "#6b4321", "#b07a3c", "#e8b56c", "#f6d89a"],
                                                  eje="x", desde=0, hasta=640))
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#120b07", "#3a2414"], desde=0, hasta=120), 0.35)
    # árboles lejanos en la neblina (pintados aparte y desenfocados, como si hubiera polvo de luz)
    fondo = Lienzo(W, H, semilla=97)
    fondo.img = lz.img.copy()
    for k in range(18):
        x = -10 + k * 37 + (k % 3) * 7
        ci.arbol(fondo, x, 172 + (k % 2) * 5, 160, 46, luz=LUZ, rampa_copa=COBRE[1:7] if k % 3 else ROJIZO[1:7], semilla=200 + k, sombra=False)
    neblina = lz.gradiente(["#5a3a20", "#b07a3c", "#f3cf9e"], eje="x", desde=0, hasta=620)
    borroso = cv2.GaussianBlur(fondo.img.astype(np.float32), (0, 0), 1.6)
    lz.pintar(np.ones((lz.H, lz.W)), borroso)
    lz.pintar(np.ones((lz.H, lz.W)), neblina, 0.45)
    # dos árboles grandes y viejos que enmarcan el claro (a contraluz)
    ci.arbol_grande(lz, 40, 222, 330, 190, luz=LUZ, semilla=241, rampa_copa=COBRE[0:7], rampa_tronco=ci.MADERA[0:6])
    ci.arbol_grande(lz, 585, 226, 320, 170, luz=LUZ, semilla=242, rampa_copa=ROJIZO[0:7], rampa_tronco=ci.MADERA[0:6])
    # el suelo del claro: musgo y hojarasca, más claro donde da el sol
    suelo = ci.mascara_bajo(lz, ci.linea_horizonte(lz, 196, 4, 260, 92))
    lz.pintar(suelo, rampa(["#1f1a10", "#33301a", "#4f4a26", "#7c6a34", "#c39a58"], np.clip(0.3 + (lz.x / 600) * 0.45 + (lz.ruido(6, 3) - 0.5) * 0.3, 0, 1)))
    _hojas_suelo(lz, 260, (0, 200, 600, 256), 93)
    # rayos de sol entre las copas
    # (haces rectos en diagonal, desde arriba a la derecha)
    for (x0, ancho_h, fuerza) in ((330, 18, 0.22), (400, 30, 0.3), (470, 14, 0.2), (520, 24, 0.25), (250, 10, 0.12)):
        haz = lz.poligono([(x0 + 60, -10), (x0 + 60 + ancho_h, -10), (x0 - 40 + ancho_h * 1.8, 260), (x0 - 40, 260)])
        lz.sumar_luz(lz.desenfocar(haz, 4) * np.clip(1 - lz.y / 300, 0.2, 1), "#ffe2a0", fuerza)
    # Pembe libre, inclinándose
    _ciervo(lz)
    # trozos de hierro por el suelo, con la luz violeta que se apaga
    rng = np.random.default_rng(95)
    for k in range(9):
        x, y = 300 + rng.random() * 170, 214 + rng.random() * 22
        trozo = lz.poligono([(x - 5, y), (x - 1, y - 4 - rng.random() * 3), (x + 5, y - 1), (x + 2, y + 2)])
        lz.sombrear(trozo, ci.PIEDRA[1:6], 2.0, LUZ)
        if k % 3 == 0:
            lz.sumar_luz(lz.desenfocar(lz.circulo(x, y - 1, 2), 3), "#a24fd0", 0.35)
    # Maisha, de tres cuartos, mirándole con el cetro
    ci.maisha(lz, 172, 238, 2.2, "lado", 1, luz=LUZ, recorte=("#ffd98a", 0.8), recorte_dir=(1, -0.5), brillo=0.7)
    # hojas que caen
    rng = np.random.default_rng(96)
    for k in range(34):
        x, y = rng.random() * 600, rng.random() * 200
        col = [COBRE[4:8], ROJIZO[3:7]][k % 2]
        lz.sombrear(lz.elipse(x, y, 2.6, 1.1, rng.random() * 180), col, 0.9, LUZ)
    # luz cálida general y viñeta
    vin = np.clip(np.hypot((lz.x - 330) / 360, (lz.y - 140) / 190) - 0.72, 0, 1) ** 1.5
    lz.pintar(vin, "#0a0605", 0.5)
    return lz


PIEZAS = {"9_pembe_libre": pembe_libre}
