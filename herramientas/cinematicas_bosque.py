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
    """Pembe libre, de lado, mirando a la izquierda (hacia Maisha), con la cabeza baja: se inclina."""
    G = 214
    pelo = ci.pelo(lz, 31)
    # sombra en el suelo
    lz.pintar(lz.desenfocar(lz.elipse(400, G + 2, 66, 7), 2.0), "#120a06", 0.55)
    # patas del otro lado (más oscuras): delantera y trasera (con el corvejón)
    for pts in ([(372, 176), (370, 196), (368, G - 1)], [(436, 170), (446, 190), (440, 204), (442, G - 1)]):
        m = lz.trazo(pts, 8, 4)
        lz.sombrear(m, PELO[:5], 3.0, LUZ, textura=pelo, fuerza_tex=0.25)
        lz.pintar(lz.elipse(pts[-1][0], G - 1, 3.6, 2.2), "#140c0a")
    # cuerpo: grupa, tronco y pecho hondo
    cuerpo = np.maximum(np.maximum(lz.elipse(438, 156, 27, 23), lz.elipse(402, 160, 42, 21)), lz.elipse(364, 162, 26, 25))
    lz.sombrear(cuerpo, PELO, 20, LUZ, textura=pelo, fuerza_tex=0.35, recorte=("#ffd98a", 0.8), recorte_dir=(1, -0.6),
                rebote=("#4a2a16", 0.35))
    vientre = lz.elipse(400, 176, 36, 7) * cuerpo
    lz.pintar(lz.desenfocar(vientre, 2.0), "#c79a78", 0.3)
    lz.pintar(lz.desenfocar(lz.elipse(452, 150, 10, 12) * cuerpo, 2.0), "#ecd09a", 0.35)      # la grupa clara
    # musgo y hojitas donde estaban las placas de hierro
    for k, x in enumerate((372, 392, 412, 432)):
        lz.sombrear(lz.elipse(x, 139 + (k % 2) * 2, 7, 3.0), ci.HIERBA[3:8], 2.0, LUZ, textura=lz.ruido(0.6, 2), fuerza_tex=0.5)
    # patas de este lado
    for pts in ([(360, 178), (358, 198), (356, G)], [(428, 172), (436, 192), (428, 205), (430, G)]):
        m = lz.trazo(pts, 9, 4.5)
        lz.sombrear(m, PELO[1:7], 3.2, LUZ, textura=pelo, fuerza_tex=0.25, recorte=("#ffd98a", 0.5), recorte_dir=(1, 0))
        lz.pintar(lz.elipse(pts[-1][0], G + 0.5, 4, 2.4), "#140c0a")
    # rabo
    lz.sombrear(lz.trazo([(462, 142), (468, 146), (467, 154)], 5, 3), PELO[2:7], 2.0, LUZ)
    lz.pintar(lz.elipse(467, 153, 2.6, 3), "#ecd09a", 0.8)
    # cuello grueso que baja hasta la cabeza
    cuello = lz.poligono([(372, 138), (352, 140), (322, 178), (330, 196), (350, 182), (378, 166)])
    lz.sombrear(cuello, PELO, 12, LUZ, textura=pelo, fuerza_tex=0.3, recorte=("#ffd98a", 0.6), recorte_dir=(0.6, -1))
    # melena del cuello (pelo más largo)
    for k in range(7):
        y = 160 + k * 4
        lz.pintar(lz.trazo([(338 + k * 1.5, y), (334 + k * 1.5, y + 7)], 1.4, 0.4), PELO[2], 0.8)
    # cabeza y hocico (casi rozando el suelo)
    cabeza = np.maximum(lz.elipse(318, 194, 15, 10, 25), lz.elipse(302, 203, 9, 6.5, 30))
    lz.sombrear(cabeza, PELO, 8, LUZ, textura=pelo, fuerza_tex=0.25, recorte=("#ffd98a", 0.6), recorte_dir=(1, -1))
    lz.pintar(lz.elipse(296, 206, 3.4, 2.6), "#1b100b")                         # nariz
    lz.pintar(lz.trazo([(314, 189), (321, 190)], 1.1), "#140c0a")               # ojo cerrado (en paz)
    lz.pintar(lz.trazo([(314, 191), (320, 192)], 0.6), "#ecd09a", 0.4)
    oreja = lz.poligono([(330, 186), (344, 178), (334, 192)])
    lz.sombrear(oreja, PELO[2:8], 2.5, LUZ)
    # las astas: grandes, de madera viva, con hojas cobrizas y rojizas y brotes que brillan
    for k, (dx, sombra) in enumerate(((-8, True), (0, False))):
        base = (322 + dx, 184)
        tronco = [base, (332 + dx * 1.4, 160), (340 + dx * 1.8, 134), (338 + dx * 2.2, 108), (328 + dx * 2.6, 84)]
        cols = ci.MADERA[0:4] if sombra else ["#251812", "#3a2418", "#5a3826", "#7d5034", "#a0704a"]
        ci.hebra(lz, tronco, 9.0, 4.0, cols, LUZ, semilla=40 + k)
        for i, largo in enumerate((26, 30, 22)):
            bx, by = tronco[i + 1]
            fin = (bx - largo * 0.55, by - largo * 0.8)
            punta = lz.curva((bx, by), (bx - largo * 0.15, by - largo * 0.5), fin, n=14)
            ci.hebra(lz, punta, 4.6, 1.8, cols, LUZ, semilla=50 + i + k * 5)
        # hojas en las puntas (más en las de delante)
        rng = np.random.default_rng(60 + k * 7)
        puntas = [tronco[-1]] + [(tronco[i + 1][0] - l * 0.55, tronco[i + 1][1] - l * 0.8) for i, l in enumerate((26, 30, 22))]
        for (fx, fy) in puntas:
            for h in range(7 if not sombra else 4):
                hx, hy = fx + (rng.random() - 0.5) * 14, fy + (rng.random() - 0.5) * 9
                col = [COBRE[4:8], ROJIZO[3:7], COBRE[3:7]][h % 3]
                lz.sombrear(lz.elipse(hx, hy, 5.5, 2.6, rng.random() * 180), col, 2.0, LUZ, textura=lz.ruido(0.5, 1), fuerza_tex=0.3)
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
