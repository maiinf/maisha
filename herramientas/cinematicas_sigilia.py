"""Ilustraciones del Reino de Sigilia (con el pintor de las cinemáticas; se pintan junto a las demás):

    python3 herramientas/cinematicas.py 24_sigilia_libre

  24_sigilia_libre  EL FINAL DE SIGILIA. La noche sobre Maandiko se abre en una aurora violeta y dorada. Al fondo se alza
                    la gran cúpula del Gran Archivo con sus ventanales encendidos. El hielo negro se ha fundido y por el
                    canal principal la tinta vuelve a correr líquida, cálida y llena de reflejos dorados y nombres vivos
                    que flotan como luciérnagas de caligrafía. En el puente de piedra en primer término, Maisha sostiene
                    en alto la Pluma del Primer Nombre junto a Mauti y al viejo armiño Kalamu.
"""
import numpy as np

from pintor import Lienzo, rampa  # noqa: F401
import cinematicas as ci
import cinematicas_sendero as cs

W, H = ci.W, ci.H
LUZ = (0.35, -0.78, 0.55)
PIEDRA_M = ["#161826", "#25293e", "#3a405e", "#565e82", "#7c84aa", "#aab2d4", "#dce0f2"]
ORO_M = ["#4a3210", "#7c561c", "#b8842c", "#e6b44c", "#fbe088", "#fff6d2"]
TINTA_VIVA = ["#100a22", "#1e123c", "#341e62", "#522e90", "#7c4cc0", "#b882ea", "#f6d67a"]


def _armino_escriba(lz, x, y, e=1.0, mira=1, kalamu=False):
    """Un armiño escriba de Maandiko (o Kalamu con su manto púrpura y anteojos de oro) mirando el canal."""
    sombra = lz.desenfocar(lz.elipse(x, y + 1.5 * e, 7 * e, 2.2 * e), 1.5)
    lz.pintar(sombra, "#090712", 0.55)
    # Manto de escriba
    manto = lz.poligono([
        (x - 6.5 * e, y),
        (x - 5.0 * e, y - 14 * e),
        (x + 5.0 * e, y - 14 * e),
        (x + 6.5 * e, y),
    ])
    col_manto = ["#1c1030", "#341d56", "#543088", "#7848b8"] if kalamu else ["#1a2238", "#2c3858", "#465682", "#687cb0"]
    lz.sombrear(manto, col_manto, 4 * e, LUZ)
    # Ribete dorado del manto
    borde = lz.trazo([(x - 6.2 * e, y - 1 * e), (x + 6.2 * e, y - 1 * e)], 1.1 * e)
    lz.pintar(borde, "#e6b44c", 0.9)
    # Cuello y cabeza blanca de armiño (alargada y esbelta)
    cuello = lz.trazo([(x, y - 12 * e), (x + 1.2 * e * mira, y - 19 * e)], 3.8 * e, 3.2 * e)
    cabeza = lz.elipse(x + 2.2 * e * mira, y - 20.5 * e, 4.5 * e, 3.3 * e, -8 * mira)
    oreja1 = lz.elipse(x - 0.5 * e * mira, y - 23.5 * e, 1.4 * e, 2.2 * e, -15 * mira)
    oreja2 = lz.elipse(x + 1.5 * e * mira, y - 23.8 * e, 1.4 * e, 2.2 * e, 10 * mira)
    cuerpo_b = np.clip(cuello + cabeza + oreja1 + oreja2, 0, 1)
    lz.sombrear(cuerpo_b, ["#9aa2bc", "#c4cce0", "#e6eaf6", "#ffffff"], 3 * e, LUZ,
                recorte=("#ffe39a", 0.75), recorte_dir=(0.4, -0.8))
    # Cola de armiño con la punta negra asomando detrás
    cola = lz.trazo(lz.curva((x - 4 * e * mira, y - 2 * e), (x - 10 * e * mira, y - 4 * e), (x - 12 * e * mira, y - 8 * e), n=16), 2.4 * e, 1.4 * e)
    lz.sombrear(cola, ["#b8c0d8", "#e6eaf6", "#ffffff"], 1.5 * e, LUZ)
    punta_negra = lz.elipse(x - 12 * e * mira, y - 8 * e, 2.0 * e, 1.4 * e, 25 * mira)
    lz.pintar(punta_negra, "#12101c")
    # Ojo y nariz
    lz.pintar(lz.circulo(x + 3.8 * e * mira, y - 21.0 * e, 0.7 * e), "#161020")
    lz.pintar(lz.circulo(x + 6.4 * e * mira, y - 20.2 * e, 0.65 * e), "#241828")
    if kalamu:
        # Anteojos de oro y pluma al hombro
        aro = np.clip(lz.circulo(x + 3.8 * e * mira, y - 21.0 * e, 1.5 * e) - lz.circulo(x + 3.8 * e * mira, y - 21.0 * e, 0.9 * e), 0, 1)
        lz.pintar(aro, "#fbe088")
        pluma = lz.trazo(lz.curva((x + 3 * e * mira, y - 8 * e), (x + 8 * e * mira, y - 15 * e), (x + 11 * e * mira, y - 22 * e), n=16), 1.5 * e, 0.4 * e)
        lz.pintar(pluma, "#fbe088")
        lz.sumar_luz(lz.desenfocar(pluma, 2 * e), "#f6d67a", 0.5)


def _farol(lz, x, y, e=1.0):
    """Farolillo de latón encendido junto al canal."""
    poste = lz.trazo([(x, y), (x, y - 18 * e), (x + 4 * e, y - 18 * e)], 1.2 * e)
    lz.sombrear(poste, ["#1c1a24", "#3a3648", "#6e6478"], 1.0 * e, LUZ)
    globo = lz.elipse(x + 4 * e, y - 14.5 * e, 2.6 * e, 3.4 * e)
    lz.sumar_luz(lz.desenfocar(globo, 16 * e), "#f9a83a", 0.55)
    lz.sumar_luz(lz.desenfocar(globo, 4 * e), "#fde27e", 0.75)
    lz.pintar(globo, "#fff6d2")


def sigilia_libre():
    """«La tinta vuelve a correr, tibia y dorada, por los canales de Maandiko. Ningún nombre volverá a quedarse en blanco.»"""
    lz = Lienzo(W, H, semilla=240)
    rng = np.random.default_rng(241)
    HZ = 138

    # 1. Cielo nocturno de Sigilia con aurora boreal dorada y violeta
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#090b1a", "#141834", "#26244e", "#443468", "#74527a", "#b88882"], desde=0, hasta=HZ))
    ci.estrellas(lz, 130, HZ - 12, semilla=242, color="#eef2ff")

    # Cortinas de aurora en el cielo (ondas suaves de luz turquesa-lila y oro)
    for k, (y0, col_a, fuerza) in enumerate(((34, "#7ce8d8", 0.26), (52, "#b882ea", 0.30), (68, "#fbe088", 0.32))):
        onda = y0 + 10 * np.sin(lz.x / 58.0 + k * 1.4) + 5 * np.cos(lz.x / 23.0 - k)
        banda = np.clip(1.0 - np.abs(lz.y - onda) / 18.0, 0, 1) ** 1.6 * (lz.y < HZ - 10)
        estrias = 0.65 + 0.35 * np.sin(lz.x / 4.5 + lz.ruido(3, 2, semilla=250 + k) * 4)
        lz.sumar_luz(lz.desenfocar(banda * estrias, 3.0), col_a, fuerza)

    # 2. Silueta de los tejados de pizarra de Maandiko y el Gran Archivo al fondo
    cx_arch = 300
    # Cúpula y cuerpo central del Gran Archivo
    cupula = lz.elipse(cx_arch, HZ - 34, 68, 48) * (lz.y < HZ - 30)
    cuerpo_arch = lz.poligono([(cx_arch - 76, HZ), (cx_arch - 72, HZ - 34), (cx_arch + 72, HZ - 34), (cx_arch + 76, HZ)])
    torre_izq = lz.poligono([(cx_arch - 96, HZ), (cx_arch - 92, HZ - 58), (cx_arch - 82, HZ - 74), (cx_arch - 72, HZ - 58), (cx_arch - 70, HZ)])
    torre_der = lz.poligono([(cx_arch + 70, HZ), (cx_arch + 72, HZ - 58), (cx_arch + 82, HZ - 74), (cx_arch + 92, HZ - 58), (cx_arch + 96, HZ)])
    archivo = np.clip(cupula + cuerpo_arch + torre_izq + torre_der, 0, 1)
    lz.sombrear(archivo, PIEDRA_M, 14, LUZ, textura=lz.ruido(2.0, 2, semilla=243), fuerza_tex=0.25)

    # Costillas doradas de la cúpula y aguja astral
    for dx in (-44, -22, 0, 22, 44):
        arco_c = lz.trazo(lz.curva((cx_arch + dx, HZ - 34), (cx_arch + dx * 0.6, HZ - 66), (cx_arch, HZ - 82), n=24), 1.2) * cupula
        lz.pintar(arco_c, "#e6b44c", 0.75)
    aguja = lz.trazo([(cx_arch, HZ - 80), (cx_arch, HZ - 102)], 1.6, 0.5)
    lz.pintar(aguja, "#fbe088")
    lz.sumar_luz(lz.desenfocar(lz.circulo(cx_arch, HZ - 102, 4), 10), "#fbe088", 0.8)

    # Ventanales góticos del Gran Archivo encendidos con luz cálida (los 12 atriles brillando dentro)
    for k in range(-3, 4):
        vx = cx_arch + k * 18
        vy = HZ - 16
        vent = np.maximum(lz.poligono([(vx - 4, vy + 10), (vx - 4, vy - 4), (vx + 4, vy - 4), (vx + 4, vy + 10)]),
                          lz.circulo(vx, vy - 4, 4))
        lz.sumar_luz(lz.desenfocar(vent, 8), "#f9a83a", 0.65)
        lz.pintar(vent, rampa(["#e68a2e", "#fbe088", "#fff8dc"], np.clip(1 - (lz.y - (vy - 8)) / 18, 0, 1)))

    # Casas de escribas a ambos lados del canal con tejados empinados y nieve que se deshace
    for lado, xs in ((-1, (28, 72, 118, 162)), (1, (438, 482, 528, 572))):
        for idx, bx in enumerate(xs):
            ancho_c = 22 + (idx % 2) * 4
            alto_c = 28 + (idx % 3) * 8
            fachada = lz.poligono([(bx - ancho_c, HZ + 6), (bx - ancho_c, HZ - alto_c),
                                   (bx + ancho_c, HZ - alto_c), (bx + ancho_c, HZ + 6)])
            tejado = lz.poligono([(bx - ancho_c - 3, HZ - alto_c), (bx, HZ - alto_c - 22), (bx + ancho_c + 3, HZ - alto_c)])
            lz.sombrear(fachada, PIEDRA_M[1:6], 6, LUZ)
            lz.sombrear(tejado, ["#121424", "#222640", "#383e62", "#58628e"], 5, LUZ)
            # Ventanitas encendidas
            for wx in (bx - 8, bx + 8):
                w_m = lz.poligono([(wx - 2.5, HZ - alto_c + 14), (wx - 2.5, HZ - alto_c + 6),
                                   (wx + 2.5, HZ - alto_c + 6), (wx + 2.5, HZ - alto_c + 14)])
                lz.sumar_luz(lz.desenfocar(w_m, 5), "#f9a83a", 0.45)
                lz.pintar(w_m, "#fbe088")

    # 3. El Gran Canal de Maandiko: la tinta corre líquida, violeta y dorada, reflejando el Archivo
    Y_PUENTE = 208
    canal = (lz.y >= HZ) * (lz.y <= Y_PUENTE + 10)
    # Muelles laterales en perspectiva hacia el centro
    m_izq = lz.poligono([(0, HZ), (190, HZ), (95, Y_PUENTE + 6), (0, Y_PUENTE + 6)])
    m_der = lz.poligono([(410, HZ), (600, HZ), (600, Y_PUENTE + 6), (505, Y_PUENTE + 6)])
    agua = np.clip(canal - m_izq - m_der, 0, 1)

    # Reflejo suave del cielo y del Gran Archivo sobre la tinta líquida
    antes = lz.img.copy()
    filas = lz.img.shape[0]
    yy = np.arange(filas)
    eje = int(HZ * lz.s)
    refl = antes[np.clip(2 * eje - 1 - yy, 0, filas - 1)].copy()
    for f in range(eje, min(filas, int((Y_PUENTE + 10) * lz.s))):
        d = (f / lz.s - HZ) / max(1.0, Y_PUENTE - HZ)
        desp = int(round(np.sin(f / lz.s * 0.75) * (0.8 + d * 2.8) * lz.s))
        refl[f] = np.roll(refl[f], desp, axis=0)
    hondo = np.clip((lz.y - HZ) / (Y_PUENTE - HZ), 0, 1)
    tinte_tinta = np.array([0.14, 0.08, 0.28])
    lz.pintar(agua, np.clip(refl * (0.55 - hondo[..., None] * 0.20) + tinte_tinta * (0.75 + hondo[..., None] * 0.35), 0, 1))

    # Vetas de tinta dorada y caligrafía viva fluyendo por la corriente hacia delante
    for k in range(7):
        t_v = np.linspace(0, 1, 60)
        offset_x = (k - 3) * 24
        curva_x = cx_arch + offset_x * (0.35 + 0.95 * t_v) + np.sin(t_v * 6.0 + k) * (6 + 8 * t_v)
        curva_y = HZ + 2 + t_v * (Y_PUENTE - HZ)
        veta = lz.trazo(np.stack([curva_x, curva_y], axis=1), 0.8, 2.4) * agua
        col_v = "#fbe088" if k % 2 == 0 else "#c892ff"
        lz.sumar_luz(lz.desenfocar(veta, 3.0), col_v, 0.45)
        lz.pintar(veta, "#fff4c8" if k % 2 == 0 else "#e2c4ff", 0.65)

    # Muelles de piedra con nieve tibia, faroles y dos escribas armiño mirando el agua
    for muelle, x_borde0, x_borde1 in ((m_izq, 190, 95), (m_der, 410, 505)):
        ci.piedras(lz, muelle, tam=7, semilla=244, rampa_p=PIEDRA_M, luz=LUZ, mortero="#101220")
        borde_m = lz.trazo([(x_borde0, HZ), (x_borde1, Y_PUENTE + 6)], 2.2)
        lz.pintar(borde_m, "#dce0f2", 0.8)
    _farol(lz, 152, 168, e=0.85)
    _farol(lz, 444, 168, e=0.85)
    _armino_escriba(lz, 134, 184, e=0.95, mira=1, kalamu=False)
    _armino_escriba(lz, 466, 184, e=0.95, mira=-1, kalamu=False)

    # 4. El Puente del Índice en primer plano, donde están Maisha, Mauti y Kalamu
    puente = lz.poligono([(0, Y_PUENTE + 2), (160, Y_PUENTE - 8), (300, Y_PUENTE - 12),
                          (440, Y_PUENTE - 8), (600, Y_PUENTE + 2), (600, 256), (0, 256)])
    ci.piedras(lz, puente, tam=9, semilla=245, rampa_p=PIEDRA_M, luz=LUZ, mortero="#0e101c")
    pretil = lz.trazo(lz.curva((0, Y_PUENTE + 2), (300, Y_PUENTE - 22), (600, Y_PUENTE + 2), n=60), 4.5, 4.5)
    lz.sombrear(pretil, PIEDRA_M[2:], 2.5, LUZ)
    lz.pintar(pretil * (lz.y < Y_PUENTE - 6), "#fbe088", 0.35)

    # Faroles del puente
    _farol(lz, 118, Y_PUENTE - 4, e=1.25)
    _farol(lz, 476, Y_PUENTE - 4, e=1.25)

    # Personajes en el puente mirando cómo despierta Sigilia:
    # Mauti a la izquierda de Maisha, Maisha en el centro con la Pluma del Primer Nombre en alto, y Kalamu a la derecha
    cs._mauti_luz(lz, 254, 232, e=1.75, mira=1)
    ci.maisha_luz(lz, 304, 234, e=1.80)
    _armino_escriba(lz, 358, 234, e=1.45, mira=-1, kalamu=True)

    # La Pluma del Primer Nombre brillando sobre las manos de Maisha
    px, py = 304, 184
    pluma_oro = lz.trazo(lz.curva((px - 5, py + 8), (px + 2, py - 4), (px + 9, py - 14), n=20), 2.6, 0.6)
    lz.sumar_luz(lz.desenfocar(lz.circulo(px + 2, py - 2, 14), 16), "#fbe088", 0.85)
    lz.sumar_luz(lz.desenfocar(pluma_oro, 4), "#f9a83a", 0.9)
    lz.pintar(pluma_oro, "#fff8dc")

    # 5. Glifos y sílabas de luz dorada que se alzan desde el canal hacia el cielo
    glifos = np.zeros((lz.H, lz.W))
    for k in range(55):
        gx = 90 + rng.random() * 420
        gy = 30 + rng.random() * 195
        r_g = 0.7 + rng.random() * 1.1
        glifos = np.maximum(glifos, lz.circulo(gx, gy, r_g))
        if k % 3 == 0:
            trazo_g = lz.trazo(lz.curva((gx - 2.5, gy), (gx, gy - 3), (gx + 2.5, gy + 1), n=8), 0.55)
            glifos = np.maximum(glifos, trazo_g)
    lz.sumar_luz(lz.desenfocar(glifos, 2.2), "#f9b947", 0.7)
    lz.sumar_luz(glifos, "#fff8dc", 0.95)

    # Viñeta suave nocturna
    vin = np.clip(np.hypot((lz.x - 300) / 350, (lz.y - 132) / 185) - 0.72, 0, 1) ** 1.4
    lz.pintar(vin, "#05060f", 0.50)
    return lz


PIEZAS = {"24_sigilia_libre": sigilia_libre}
