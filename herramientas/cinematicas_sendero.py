"""Ilustraciones de los caminos de Raíz (con el pintor de las cinemáticas; se pintan junto a las demás):

    python3 herramientas/cinematicas.py 12_eco_puente

  12_eco_puente   EL PRIMER ECO (Sendero del Puente). Un recuerdo de hace muchísimo tiempo: el Río Lento al amanecer
                  y el puente de piedra a medio hacer, con su arco de madera (la cimbra) aún debajo. Castores, una tortuga
                  y otros seres de Raíz suben piedras con cuerdas y poleas. Al fondo, sobre una colina, el PRIMER ÁRBOL:
                  enorme, con la copa dorada que da luz como un sol; las piedras que llegan de allí brillan un poco.
                  Todo tiene el tono verde-agua y la niebla clara de los recuerdos.
  13_eco_pasarelas EL SEGUNDO ECO (Las Pasarelas). Una noche de luna en el prado inundado: una garza vieja y su cría,
                  con un farolillo, miran el agua desde la pasarela. Bajo el agua brillan las raíces doradas del Primer
                  Árbol, como una red, y entre ellas se desliza Kimya, el Silencio: una forma plateada, larga y tranquila.
  14_eco_cobrizo  EL TERCER ECO (Camino Cobrizo). Una tarde de otoño en la loma: un árbol enorme de hojas de cobre
                  que caen despacio. Bajo él, sentados en la hierba llena de hojas, dos espíritus de luz pequeños:
                  Maisha (dorada, con su brote) y MAUTI (plateada y lila, con una hoja seca en lo alto), que recoge una
                  hoja que cae. Al fondo, colinas de árboles cobrizos y el sol bajo.
  16_eco_canada   EL QUINTO ECO (Cañada del Eco). Atardecer en la garganta: el sol se pone en el hueco entre las
                  dos paredes de peña. En una cornisa, Maisha (dorada) y Mauti (plateada y lila) gritan sus nombres
                  hacia la pared de enfrente, y sus ondas (doradas y lilas) vuelven rebotadas. A su lado, KIMYA, el
                  Silencio, flota en silencio mirando abajo: de ella no sale ninguna onda. Abajo, el arroyo está
                  quieto como un espejo y solo refleja a Kimya.
  17_kimya_lago   KIMYA EN EL LAGO ESPEJO (no es un recuerdo: pasa ahora). La hora azul sobre el lago, quieto como un
                  espejo. Maisha, en la orilla de la isla, mira el agua; Kimya se alza del lago, plateada. En el agua,
                  bajo Maisha, su reflejo no es ella: es MAUTI, del revés, mirándola.
  15_eco_surcos   EL CUARTO ECO (Senda de los Surcos). La fiesta de la última siega, de noche: campos con gavillas,
                  guirnaldas de farolillos, una hoguera en el centro y los seres de Raíz bailando a contraluz. En la
                  colina, el Primer Árbol dorado. Junto al fuego, Maisha y Mauti bailan de la mano.
"""
import math

import numpy as np

from pintor import Lienzo, rampa  # noqa: F401
import cinematicas as ci

W, H = ci.W, ci.H
LUZ = (0.3, -0.8, 0.5)                    # la luz viene del Primer Árbol, al fondo y arriba
HORIZONTE = 132
AGUA = ["#0f2626", "#1c3a3a", "#285050", "#346161", "#4c8d8d", "#6db0b0", "#9fd0d0", "#d8f0ec"]
PIEDRA_R = ["#1d1f1c", "#2e302a", "#41443a", "#5c6052", "#7a806d", "#9aa08a", "#c0c4ae", "#e2e2d4"]
DORADO = ["#7a5a1a", "#b8862a", "#e6b54a", "#f9d77a", "#fff1c0"]
SILUETA = ["#122020", "#1a2c2c", "#243b3a", "#2f4a48", "#3d5c58"]


def _primer_arbol(lz, x, y, alto):
    """El Primer Árbol en la colina: tronco ancho y retorcido, ramas como brazos y una copa enorme de luz dorada."""
    # la luz que da (como un sol detrás de la copa)
    halo = np.clip(1 - np.hypot((lz.x - x) / 190, (lz.y - (y - alto * 0.72)) / 120), 0, 1)
    lz.sumar_luz(halo ** 1.6, "#ffe9a8", 0.75)
    tronco = lz.poligono([(x - 9, y), (x - 6, y - alto * 0.3), (x - 3, y - alto * 0.55), (x + 3, y - alto * 0.55),
                          (x + 7, y - alto * 0.3), (x + 11, y)])
    for (a, b, c) in (((x - 2, y - alto * 0.5), (x - 22, y - alto * 0.62), (x - 38, y - alto * 0.66)),
                      ((x + 2, y - alto * 0.5), (x + 20, y - alto * 0.66), (x + 40, y - alto * 0.7)),
                      ((x, y - alto * 0.52), (x - 4, y - alto * 0.7), (x + 2, y - alto * 0.82))):
        tronco = np.maximum(tronco, lz.trazo(lz.curva(a, b, c, n=20), 3.2, 1.0))
    lz.sombrear(tronco, ["#2a3a30", "#3d4f40", "#566a52", "#7a8c66"], 4, LUZ, textura=lz.ruido(2, 3, semilla=121), fuerza_tex=0.3)
    # la copa: muchas nubes de hojas doradas, más claras arriba
    rng = np.random.default_rng(122)
    copa = np.zeros((lz.H, lz.W))
    for k in range(26):
        a = rng.random() * math.pi
        r = 20 + rng.random() * 46
        cx, cy = x + math.cos(a) * r * 1.4, y - alto * 0.74 - math.sin(a) * r * 0.55
        copa = np.maximum(copa, lz.elipse(cx, cy, 14 + rng.random() * 12, 9 + rng.random() * 7))
    lz.sombrear(copa, DORADO + ["#fffbe8"], 10, (0.0, -1.0, 0.6), textura=lz.ruido(2.5, 3, semilla=123), fuerza_tex=0.35)
    lz.sumar_luz(lz.desenfocar(copa, 10), "#ffe39a", 0.5)
    # hojas de luz que caen de la copa
    hojas = np.zeros((lz.H, lz.W))
    for k in range(40):
        hx, hy = x + (rng.random() - 0.5) * 220, y - alto * 0.6 + rng.random() * 70
        hojas = np.maximum(hojas, lz.elipse(hx, hy, 1.4, 0.7, rng.random() * 180) * rng.random())
    lz.sumar_luz(hojas, "#fff1c0", 0.9)


def _constructor(lz, x, y, e, mira, carga=False, tortuga=False, sem=0):
    """Un ser de Raíz trabajando, en silueta con el filo iluminado por la luz del árbol (castor o tortuga)."""
    if tortuga:
        m = lz.elipse(x, y - 7 * e, 10 * e, 7 * e)
        m = np.maximum(m, lz.circulo(x + 10 * e * mira, y - 9 * e, 3.2 * e))
        m = np.maximum(m, lz.elipse(x - 5 * e, y - 1 * e, 2 * e, 2.5 * e))
        m = np.maximum(m, lz.elipse(x + 5 * e, y - 1 * e, 2 * e, 2.5 * e))
    else:
        m = ci.castor_silueta(lz, x, y, e, mira)
    lz.sombrear(np.clip(m, 0, 1), SILUETA, 3 * e, LUZ, recorte=("#ffe39a", 0.9), recorte_dir=(0.3, -1))
    if carga:
        p = lz.elipse(x + 2 * e * mira, y - 30 * e, 7 * e, 5 * e, sem * 13 % 30)
        lz.sombrear(p, PIEDRA_R[2:], 3 * e, LUZ, textura=lz.ruido(1.2, 2, semilla=sem), fuerza_tex=0.3)
        lz.sumar_luz(lz.desenfocar(p, 3), "#f9d77a", 0.35)


def eco_puente():
    """«Esta piedra nos la dio el Primer Árbol. Para que nadie quedara solo en una orilla.»
    Vista desde la orilla, de lado: el río cruza la imagen de izquierda a derecha y el puente lo salta con tres
    arcos (el del medio, a medio hacer, con la cimbra de madera y la grúa subiendo una piedra). Detrás, en una
    colina, el Primer Árbol, enorme y dorado, que da luz como un sol de amanecer."""
    lz = Lienzo(W, H, semilla=120)
    HZ = 112
    # cielo del amanecer: verde-agua arriba, dorado alrededor del árbol
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#24403f", "#3f6663", "#7d9c8c", "#c5c9a0", "#f0dcaa"], desde=0, hasta=HZ))
    calido = np.clip(1 - np.hypot((lz.x - 440) / 260, (lz.y - 60) / 120), 0, 1)
    lz.sumar_luz(calido ** 1.4, "#ffe2a0", 0.65)
    ci.cumulos(lz, [(80, 34, 60, 8), (210, 22, 46, 6), (300, 48, 50, 7)], luz=(0.8, -0.5),
               colores=("#56766f", "#8fa896", "#d2d4b0", "#fff4d6"), semilla=124, alfa=0.75, suave=1.2)
    # colinas lejanas en la neblina y la colina del árbol
    lejos = ci.mascara_bajo(lz, ci.linea_horizonte(lz, HZ - 4, 8, 150, 125))
    lz.pintar(lejos, "#7d9886")
    colina = lz.elipse(440, HZ + 10, 150, 40) * (lz.y < HZ + 12)
    lz.sombrear(colina, ["#4d6a55", "#66845f", "#86a072", "#a9bb8a"], 24, (0.2, -1, 0.5))
    # el PRIMER ÁRBOL: grande, viejo, con la copa dorada que brilla
    ci.arbol_grande(lz, 440, HZ + 2, 150, 210, luz=(0.0, -1.0, 0.6), semilla=129,
                    rampa_copa=["#5a4a1a", "#8a6a22", "#b8862a", "#e6b54a", "#f9d77a", "#fff1c0", "#fffbe8"],
                    rampa_tronco=["#26302a", "#36443a", "#4a5a4c", "#66785f", "#8a9a7a"])
    copa = np.clip(1 - np.hypot((lz.x - 440) / 120, (lz.y - (HZ - 108)) / 60), 0, 1)
    lz.sumar_luz(copa ** 1.2, "#ffeab0", 0.55)
    rng = np.random.default_rng(130)
    hojas = np.zeros((lz.H, lz.W))
    for k in range(60):
        hx, hy = 440 + (rng.random() - 0.5) * 300, 30 + rng.random() * 110
        hojas = np.maximum(hojas, lz.elipse(hx, hy, 1.3, 0.6, rng.random() * 180) * (0.4 + rng.random() * 0.6))
    lz.sumar_luz(hojas, "#fff1c0", 0.9)
    # la orilla de enfrente (con juncos) y el agua
    Y_AGUA0, Y_AGUA1 = 150, 214
    otra = (lz.y > HZ + 8) * (lz.y < Y_AGUA0 + 2)
    lz.pintar(otra, rampa(ci.HIERBA[2:7], np.clip(0.55 + (lz.ruido(6, 3, semilla=131) - 0.5) * 0.4, 0, 1)))
    agua = (lz.y >= Y_AGUA0) * (lz.y < Y_AGUA1)
    ondas = np.sin(lz.y * 1.4 + (lz.ruido(14, 3, semilla=127) - 0.5) * 12) * 0.5 + 0.5
    lz.pintar(agua, rampa(AGUA, np.clip(0.35 + (ondas - 0.5) * 0.18 + (lz.y - Y_AGUA0) / 160, 0, 1)))
    # el reflejo dorado del árbol en el agua
    refl = agua * np.clip(1 - np.abs(lz.x - 440) / 110, 0, 1) * (ondas > 0.55)
    lz.sumar_luz(refl, "#f9d77a", 0.5)
    # el PUENTE, de lado: tablero, pretil, tres arcos (el del medio sin cerrar) y los pilares en el agua
    X0, X1, YT = 40, 520, 130                       # extremos y altura del tablero
    arcos = [(120, 54), (280, 64), (440, 54)]       # centro y semiancho de cada arco
    base = Y_AGUA0 + 20                             # la línea del agua bajo el puente
    muro = lz.poligono([(X0, YT), (X1, YT), (X1 + 4, base), (X0 - 4, base)])
    huecos = np.zeros((lz.H, lz.W))
    for (cx, r) in arcos:
        huecos = np.maximum(huecos, lz.elipse(cx, base, r, 34) * (lz.y > YT + 6))
    # el tramo del medio aún no tiene tablero: solo las piedras del arco que suben desde cada lado
    falta = lz.poligono([(232, YT - 2), (328, YT - 2), (328, base - 24), (232, base - 24)])
    hecho = np.clip(muro - huecos - falta, 0, 1)
    ci.piedras(lz, hecho, tam=9, semilla=132, rampa_p=PIEDRA_R[1:], luz=(0.2, -1, 0.5), mortero="#1a2420")
    lz.pintar(np.clip(hecho * (1 - lz.desenfocar(hecho, 1.0)) * 3, 0, 1), "#1a2420", 0.6)
    # dovelas de los arcos (claras, en abanico)
    for (cx, r) in arcos:
        anillo = np.clip(lz.elipse(cx, base, r + 5, 39) - lz.elipse(cx, base, r, 34), 0, 1) * (lz.y > YT + 2) * (lz.y < base)
        if cx == 280:
            anillo *= (np.abs(lz.x - 280) > 16)     # en el arco del medio faltan las de arriba
        lz.pintar(anillo, rampa(PIEDRA_R[3:7], np.clip(0.4 + (lz.ruido(1, 2, semilla=cx) - 0.5) * 0.4, 0, 1)))
        lz.pintar(anillo * ((np.floor(np.arctan2(lz.y - base, lz.x - cx) * 14) % 2) == 0), "#2e302a", 0.5)
    # pretil encima del tablero (con albardilla clara)
    pretil = lz.poligono([(X0, YT - 7), (232, YT - 7), (232, YT), (X0, YT)]) + lz.poligono([(328, YT - 7), (X1, YT - 7), (X1, YT), (328, YT)])
    lz.pintar(np.clip(pretil, 0, 1), rampa(PIEDRA_R[2:6], np.clip(0.4 + (lz.ruido(1, 2, semilla=133) - 0.5) * 0.4, 0, 1)))
    lz.pintar(np.clip(pretil, 0, 1) * (lz.y < YT - 5), PIEDRA_R[6], 0.9)
    # la cimbra de madera bajo el arco del medio, con sus puntales
    cimbra = lz.trazo(lz.curva((222, base), (280, base - 70), (338, base), n=60), 3, 3)
    lz.sombrear(cimbra, ci.MADERA[1:6], 1.5, (0.2, -1, 0.5))
    for k in range(7):
        t = (k + 0.5) / 7
        bx = (1 - t) ** 2 * 222 + 2 * (1 - t) * t * 280 + t ** 2 * 338
        by = (1 - t) ** 2 * base + 2 * (1 - t) * t * (base - 70) + t ** 2 * base
        lz.pintar(lz.trazo([(bx, by), (bx, base + 4)], 1.0), ci.MADERA[2], 0.9)
    # la grúa de palos sobre el tramo ya hecho y la piedra del Primer Árbol que sube (brilla)
    lz.pintar(lz.trazo([(214, YT - 6), (262, YT - 74)], 2.2), ci.MADERA[3])
    lz.pintar(lz.trazo([(200, YT - 6), (214, YT - 6)], 1.6), ci.MADERA[2])
    lz.pintar(lz.trazo([(262, YT - 74), (276, YT - 40)], 0.5), "#c9b77d")
    piedra = lz.elipse(278, YT - 33, 8, 7)
    lz.sombrear(piedra, PIEDRA_R[3:], 3, (0.2, -1, 0.5))
    lz.sumar_luz(lz.desenfocar(piedra, 5), "#f9d77a", 0.7)
    lz.sumar_luz(piedra, "#f9d77a", 0.35)
    # piedras doradas ya puestas, aquí y allá
    for (px_, py_) in ((150, YT + 10), (380, YT + 16), (470, YT + 8), (90, YT + 22)):
        lz.sumar_luz(lz.desenfocar(lz.elipse(px_, py_, 4, 3), 3), "#f9d77a", 0.45)
    # el reflejo del puente en el agua: el muro volteado bajo la línea del agua, oscuro y temblón
    fila_base = int(base * lz.s)
    alto_r = min(fila_base - int(YT * lz.s), lz.H - fila_base)
    refl_p = np.zeros((lz.H, lz.W), np.float32)
    refl_p[fila_base:fila_base + alto_r] = np.clip(hecho + np.clip(cimbra, 0, 1), 0, 1)[fila_base - 1:fila_base - 1 - alto_r:-1]
    temblor = (np.sin(lz.y * 2.2 + lz.ruido(3, 2, semilla=135) * 6) > -0.3)
    lz.pintar(refl_p * agua * temblor * np.clip(1 - (lz.y - base) / 50, 0, 1), "#162e2e", 0.55)
    lz.pintar(agua * (np.abs(lz.y - base) < 1.0) * (lz.ruido(1, 2, semilla=136) > 0.4), "#9fd0d0", 0.6)
    # los constructores sobre el puente y en la orilla, a contraluz (filo dorado)
    for (x, y, e, m, kw) in ((150, YT - 7, 0.75, 1, dict(carga=True, sem=1)), (186, YT - 7, 0.6, 1, dict(sem=2)),
                             (360, YT - 7, 0.72, -1, dict(tortuga=True)), (402, YT - 7, 0.7, -1, dict(carga=True, sem=5)),
                             (300, YT - 46, 0.5, -1, dict(sem=7))):
        _constructor(lz, x, y, e, m, **kw)
    # la orilla de aquí (delante), con piedras esperando y dos constructores tirando de la cuerda
    delante = (lz.y >= Y_AGUA1)
    borde = lz.desenfocar(delante.astype(np.float32), 1.5)
    lz.pintar(delante, rampa(ci.HIERBA[1:6], np.clip(0.45 + (lz.ruido(5, 3, semilla=134) - 0.5) * 0.45 - (lz.y - Y_AGUA1) / 160, 0, 1)))
    lz.pintar(np.clip(borde - delante, 0, 1) * 2, "#9fd0d0", 0.5)
    lz.pintar(lz.trazo([(262, YT - 74), (180, 226), (130, 236)], 0.5), "#c9b77d", 0.85)
    for (x, y, e, m, kw) in ((118, 244, 1.5, 1, dict(sem=3)), (150, 248, 1.3, 1, dict(sem=4)), (520, 246, 1.6, -1, dict(carga=True, sem=6))):
        _constructor(lz, x, y, e, m, **kw)
    for k, (x, y) in enumerate(((40, 238), (62, 248), (560, 236), (586, 246), (470, 250))):
        p = lz.elipse(x, y, 9, 6, k * 20)
        lz.sombrear(p, PIEDRA_R[1:], 3, (0.2, -1, 0.5), textura=lz.ruido(1.4, 2, semilla=40 + k), fuerza_tex=0.3)
        if k % 2 == 0:
            lz.sumar_luz(lz.desenfocar(p, 4), "#f9d77a", 0.4)
    # el tono de los ecos: todo bañado en verde-agua, con la niebla clara de los recuerdos
    lz.pintar(np.ones((lz.H, lz.W)), "#3e8a86", 0.14)
    ci.marco_recuerdo(lz, color="#d8f0ec", semilla=128)
    return lz


def _garza(lz, x, y, e, mira=1, cria=False):
    """Una garza en silueta (de lado), con el filo iluminado por el farolillo."""
    cuerpo = lz.elipse(x, y - 14 * e, 7 * e, 5 * e, -15 * mira)
    cuello = lz.trazo(lz.curva((x + 4 * e * mira, y - 17 * e), (x + 2 * e * mira, y - 26 * e), (x + 7 * e * mira, y - 30 * e), n=16), 2.0 * e, 1.6 * e)
    cabeza = lz.elipse(x + 8 * e * mira, y - 31 * e, 2.6 * e, 2.0 * e)
    pico = lz.poligono([(x + 9.5 * e * mira, y - 32 * e), (x + 17 * e * mira, y - 29.5 * e), (x + 9.5 * e * mira, y - 30 * e)])
    patas = lz.trazo([(x - 1 * e, y - 10 * e), (x - 1.5 * e, y)], 0.7 * e) + lz.trazo([(x + 2 * e, y - 10 * e), (x + 2.5 * e, y)], 0.7 * e)
    if cria:
        cuerpo = lz.elipse(x, y - 7 * e, 5 * e, 4.5 * e)
        cuello = lz.trazo([(x + 2 * e * mira, y - 10 * e), (x + 3 * e * mira, y - 14 * e)], 2.2 * e)
        cabeza = lz.circulo(x + 3.5 * e * mira, y - 16 * e, 3 * e)
        pico = lz.poligono([(x + 5.5 * e * mira, y - 16.5 * e), (x + 10 * e * mira, y - 15.5 * e), (x + 5.5 * e * mira, y - 15 * e)])
        patas = lz.trazo([(x, y - 3 * e), (x, y)], 0.7 * e) + lz.trazo([(x + 2 * e, y - 3 * e), (x + 2 * e, y)], 0.7 * e)
    forma = np.clip(cuerpo + cuello + cabeza + patas, 0, 1)
    lz.sombrear(forma, ["#0c1416", "#142024", "#1d2c32", "#2a3c44"], 3 * e, (0.8, -0.3, 0.5), recorte=("#f9c46a", 0.9), recorte_dir=(mira, -0.3))
    lz.pintar(pico, "#c08a2a")
    return forma


def eco_pasarelas():
    """«Mira abajo, pequeña. Esas luces son las raíces del Primer Árbol.» / «Es Kimya. El Silencio.»"""
    lz = Lienzo(W, H, semilla=140)
    HZ = 78
    # cielo de noche con luna llena y estrellas
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#060a12", "#0c1626", "#142438", "#1d3448", "#2a4658"], desde=0, hasta=HZ))
    ci.estrellas(lz, 110, HZ - 6, semilla=141, color="#d8f0ec")
    luna = lz.circulo(470, 30, 13)
    lz.sumar_luz(lz.desenfocar(luna, 18), "#9fd0d0", 0.45)
    lz.pintar(luna, rampa(["#c8d8d0", "#e8f0e4", "#fffbe8"], np.clip(1 - np.hypot(lz.x - 465, lz.y - 26) / 14, 0, 1)))
    # juncos y sauces lejanos a contraluz en el horizonte
    lejos = ci.mascara_bajo(lz, ci.linea_horizonte(lz, HZ, 4, 40, 142))
    lz.pintar(lejos, "#0e1a1e")
    rng = np.random.default_rng(143)
    juncos = np.zeros((lz.H, lz.W))
    for k in range(160):
        x = rng.random() * 600
        juncos = np.maximum(juncos, lz.trazo([(x, HZ + 2), (x + (rng.random() - 0.5) * 3, HZ - 6 - rng.random() * 12)], 0.6))
    lz.pintar(juncos, "#0e1a1e")
    # el agua: oscura y lisa como un espejo, con el reflejo de la luna
    agua = lz.y > HZ
    prof = np.clip((lz.y - HZ) / (H - HZ), 0, 1)
    lz.pintar(agua, rampa(["#03080c", "#081218", "#0e1c24", "#142834"], np.clip(0.7 - prof * 0.5 + (lz.ruido(30, 3, semilla=144) - 0.5) * 0.15, 0, 1)))
    reflejo = agua * np.clip(1 - np.abs(lz.x - 470) / (6 + prof * 30), 0, 1) * (np.sin(lz.y * 1.8 + lz.ruido(4, 2, semilla=145) * 5) > 0.2)
    lz.sumar_luz(reflejo * np.clip(1 - prof * 1.4, 0, 1), "#c8e0dc", 0.6)
    # bajo el agua: la red de raíces doradas del Primer Árbol, curvas y gruesas (más borrosas cuanto más hondas)
    raices = np.zeros((lz.H, lz.W))
    for k in range(7):
        x0 = 40 + k * 85 + rng.random() * 30
        p0 = (x0, HZ + 4)
        p1 = (x0 + (rng.random() - 0.5) * 120, HZ + 60 + rng.random() * 30)
        p2 = (x0 + (rng.random() - 0.5) * 200, H + 10)
        tronco = lz.curva(p0, p1, p2, n=40)
        raices = np.maximum(raices, lz.trazo(tronco, 5.0, 1.5))
        for j in (10, 20, 30):
            bx, by = tronco[j]
            d_ = 1 if rng.random() < 0.5 else -1
            rama = lz.curva((bx, by), (bx + d_ * 30, by + 10), (bx + d_ * (50 + rng.random() * 40), by + 30 + rng.random() * 30), n=24)
            raices = np.maximum(raices, lz.trazo(rama, 2.2, 0.5))
    raices = raices * agua
    hondo = np.clip((lz.y - HZ) / 140, 0, 1)
    raices_v = lz.desenfocar(raices, 1.0) * (1 - hondo * 0.5) + lz.desenfocar(raices, 3.0) * hondo * 0.5
    lz.sumar_luz(lz.desenfocar(raices, 10), "#8a6a22", 0.5)
    lz.sumar_luz(raices_v, "#d8901e", 0.6)
    lz.sumar_luz(lz.desenfocar(raices, 0.6) * (1 - hondo), "#ffd98a", 0.15)
    # Kimya, el Silencio: un ser largo de luz plateada (cabeza serena, cuerpo que se afina en una cola de niebla y
    # dos hilos de luz como astas), que se desliza entre las raíces
    kimya = np.zeros((lz.H, lz.W))
    for k in range(40):
        t = k / 39
        cx = 170 + t * 330
        cy = 196 + np.sin(t * 4.0 + 0.5) * 10
        r = 13 * (1 - t) ** 0.8 + 1.5
        kimya = np.maximum(kimya, lz.elipse(cx, cy, r * 1.4, r * 0.75))
    cabeza = lz.elipse(160, 193, 13, 9, -8)
    kimya = np.maximum(kimya, cabeza)
    astas = lz.trazo(lz.curva((158, 186), (150, 160), (132, 150), n=24), 1.4, 0.3) + lz.trazo(lz.curva((166, 186), (176, 158), (196, 148), n=24), 1.4, 0.3)
    kimya = lz.desenfocar(kimya, 1.5) * agua
    lz.sumar_luz(lz.desenfocar(kimya, 16), "#6db0b0", 0.45)
    lz.sumar_luz(kimya, "#d8ece8", 0.55)
    lz.sumar_luz(lz.desenfocar(np.clip(astas, 0, 1) * agua, 1.0), "#e8f4f0", 0.7)
    lz.sumar_luz(lz.desenfocar(cabeza * agua, 3), "#ffffff", 0.25)
    for (ox, oy) in ((153, 191), (164, 190)):                  # los ojos, cerrados (dos rayitas curvas)
        lz.pintar(lz.trazo([(ox - 2.6, oy - 0.4), (ox, oy + 0.8), (ox + 2.6, oy - 0.4)], 0.7), "#346161", 0.9)
    # la pasarela en primer plano (de lado), con sus pilotes que se meten en el agua
    YT = 128
    tablero = lz.poligono([(0, YT), (600, YT - 6), (600, YT + 3), (0, YT + 10)])
    lz.sombrear(tablero, ci.MADERA[0:5], 2, (0.8, -0.3, 0.5), textura=((lz.x % 9) < 1) * 1.0, fuerza_tex=-0.6)
    for x in range(20, 600, 64):
        y_ = YT - x / 600 * 6
        p = lz.poligono([(x - 2.5, y_ + 6), (x + 2.5, y_ + 6), (x + 2.5, y_ + 52), (x - 2.5, y_ + 52)])
        lz.sombrear(p, ci.MADERA[0:4], 2, (0.8, -0.3, 0.5))
    # la garza vieja y su cría, asomadas al agua, con el farolillo
    gx, gy = 330, YT - 3
    _garza(lz, gx, gy, 2.3, -1)
    _garza(lz, gx - 46, gy + 1, 1.6, -1, cria=True)
    lz.pintar(lz.trazo([(gx + 6, gy - 30), (gx + 18, gy - 36), (gx + 20, gy - 24)], 0.7), "#3a261d")
    farol = lz.elipse(gx + 20, gy - 20, 3.2, 4.2)
    lz.pintar(farol, "#f9c46a")
    lz.sumar_luz(lz.desenfocar(farol, 18), "#f9a83a", 0.5)
    lz.sumar_luz(lz.desenfocar(farol, 4), "#fde27e", 0.6)
    lz.sumar_luz(agua * np.clip(1 - np.hypot((lz.x - gx - 20) / 5, (lz.y - 160) / 20), 0, 1) * (np.sin(lz.y * 2.4) > 0), "#f9c46a", 0.5)
    # luciérnagas
    luc = np.zeros((lz.H, lz.W))
    for k in range(18):
        luc = np.maximum(luc, lz.circulo(rng.random() * 600, 60 + rng.random() * 50, 0.6 + rng.random() * 0.5))
    lz.sumar_luz(lz.desenfocar(luc, 2), "#d8f08a", 0.6)
    lz.sumar_luz(luc, "#f8ffd0", 0.9)
    lz.pintar(np.ones((lz.H, lz.W)), "#3e8a86", 0.12)
    ci.marco_recuerdo(lz, color="#d8f0ec", semilla=146)
    return lz


def _mauti_luz(lz, x, y, e=1.0, mira=-1):
    """Mauti hecha de luz: la misma forma que Maisha (son hermanos), pero plateada y lila, y en lo alto, en vez del
    brote, una hoja seca de cobre. Tiende una mano (hacia donde mira: -1 izquierda, 1 derecha)."""
    figura = np.maximum.reduce([lz.elipse(x, y - 15 * e, 9 * e, 8.5 * e), lz.elipse(x, y - 4.5 * e, 5 * e, 5 * e),
                                lz.trazo([(x - 2.2 * e, y - 1 * e), (x - 2.4 * e, y + 2 * e)], 2.2 * e),
                                lz.trazo([(x + 2.2 * e, y - 1 * e), (x + 2.4 * e, y + 2 * e)], 2.2 * e),
                                lz.trazo([(x + 4 * e * mira, y - 5 * e), (x + 10 * e * mira, y - 6.5 * e)], 1.7 * e, 1.3 * e)])
    lz.sumar_luz(lz.desenfocar(figura, 6 * e), "#b8a8e0", 0.7)
    lz.pintar(figura, rampa(["#8e86b4", "#c4c0e0", "#eeeaf8"], lz.volumen(figura, 6 * e, (-0.5, -0.7, 0.6))[0]))
    rabito = lz.trazo(lz.curva((x, y - 23 * e), (x - 0.5 * e, y - 26 * e), (x - 1 * e, y - 27.5 * e), n=8), 0.9 * e)
    hoja = lz.elipse(x + 1.5 * e, y - 29 * e, 3.6 * e, 1.7 * e, -35)
    lz.pintar(np.maximum(rabito, hoja), "#c06a32")
    lz.pintar(lz.trazo([(x - 1 * e, y - 27.5 * e), (x + 3.5 * e, y - 30.5 * e)], 0.4 * e), "#f4b470", 0.8)
    corazon = lz.circulo(x - 0.5 * e, y - 5 * e, 1.4 * e)
    lz.sumar_luz(lz.desenfocar(corazon, 2 * e), "#a28ae0", 0.9)
    lz.pintar(lz.elipse(x + 3.5 * e * mira, y - 15 * e, 1.0 * e, 1.6 * e), "#2a2440", 0.85)
    return figura


def eco_cobrizo():
    """«¿Por qué se ponen del color del cobre, Mauti?» / «Porque se despiden. Lo más bonito de una hoja es cómo cae.»"""
    lz = Lienzo(W, H, semilla=150)
    HZ = 120
    rng = np.random.default_rng(151)
    # cielo de tarde de otoño: melocotón y ámbar, con el sol bajo a la derecha
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#5a4a6a", "#a8707a", "#e09a6a", "#f4c27a", "#f9dca0"], desde=0, hasta=HZ))
    sol = lz.circulo(470, 96, 16)
    lz.sumar_luz(lz.desenfocar(sol, 40), "#f9b947", 0.55)
    lz.sumar_luz(lz.desenfocar(sol, 10), "#ffe8b0", 0.6)
    lz.pintar(sol, "#fff4d6")
    ci.cumulos(lz, [(120, 40, 60, 14), (300, 26, 80, 12), (520, 50, 50, 10)], colores=("#8a6a7a", "#c88a80", "#f0b88a", "#ffe0b0"), semilla=152, alfa=0.7)
    # colinas lejanas con árboles cobrizos, en capas (cuanto más lejos, más pálidas)
    for k, (base, amp, col) in enumerate(((HZ - 4, 10, "#b27a62"), (HZ + 8, 12, "#8a4a34"), (HZ + 22, 9, "#6a3424"))):
        linea = ci.linea_horizonte(lz, base, amp, 70 - k * 15, 153 + k)
        colina = ci.mascara_bajo(lz, linea)
        lz.pintar(colina, col)
        copas = np.zeros((lz.H, lz.W))
        for j in range(60):
            cx = rng.random() * 600
            cy = base - amp * 0.3 + (rng.random() - 0.5) * amp
            copas = np.maximum(copas, lz.elipse(cx, cy, 6 + k * 3 + rng.random() * 4, 5 + k * 2 + rng.random() * 3))
        lz.pintar(copas * (lz.y < base + amp + 6), rampa([col, "#c06a32" if k == 2 else col, "#e0904e"], np.clip(lz.ruido(6, 2, semilla=160 + k), 0, 1)), 0.9 - k * 0.1)
    lz.pintar(np.ones((lz.H, lz.W)) * np.clip(1 - (lz.y - 80) / 80, 0, 1), "#f4c27a", 0.12)
    # la loma de delante: hierba dorada cubierta de hojas
    loma = ci.mascara_bajo(lz, ci.linea_horizonte(lz, 176, 10, 120, 170))
    lz.pintar(loma, rampa(["#3a3418", "#5a5224", "#7c7034", "#a49448", "#c8b866"], np.clip(0.5 + (lz.ruido(8, 3, semilla=171) - 0.5) * 0.6 - (lz.y - 176) / 200, 0, 1)))
    # el árbol de cobre, a la izquierda
    ci.arbol_grande(lz, 150, 196, 170, 180, luz=(0.7, -0.6, 0.5), semilla=172,
                    rampa_copa=["#2a1208", "#4a1e10", "#7a3418", "#a84e24", "#c86a32", "#e0904e", "#f4b470", "#ffe0a0"])
    # hojas en el suelo
    hojas_s = np.zeros((lz.H, lz.W))
    colores = np.zeros((lz.H, lz.W, 3))
    pal = ["#a84e24", "#c86a32", "#e0904e", "#cc6351", "#f4b470", "#8a3a1a"]
    from pintor import hex2
    import cv2
    for j in range(900):
        x, y = rng.random() * 600, 180 + rng.random() * 80
        if y < 176 + 10 * np.sin(x * 0.02):
            continue
        cx_, cy_ = int(x * lz.s), int(y * lz.s)
        r1, r2 = int((1.4 + rng.random()) * lz.s), int((0.7 + rng.random() * 0.4) * lz.s)
        ang = rng.random() * 180
        cv2.ellipse(hojas_s, (cx_, cy_), (r1, r2), ang, 0, 360, 1.0, -1)
        cv2.ellipse(colores, (cx_, cy_), (r1, r2), ang, 0, 360, tuple(float(c) for c in hex2(pal[rng.integers(len(pal))])), -1)
    lz.pintar(hojas_s, colores, 0.9)
    # los dos espíritus, sentados en la loma, mirándose
    lz.pintar(lz.desenfocar(lz.elipse(300, 214, 50, 5), 2), "#2a1a0c", 0.35)
    maisha = ci.maisha_luz(lz, 276, 214, e=1.5)
    _mauti_luz(lz, 330, 214, e=1.5)
    # la hoja que cae hacia la mano de Mauti, con su estela
    for k in range(6):
        t = k / 5
        hx, hy = 318 - t * 3 + np.sin(t * 5) * 6, 160 + t * 34
        lz.pintar(lz.elipse(hx, hy, 3.2, 1.6, 30 + k * 25), "#e0904e", 0.25 + t * 0.75)
    lz.sumar_luz(lz.desenfocar(lz.circulo(315, 200, 4), 6), "#f4b470", 0.5)
    # hojas cayendo por todo el cuadro
    for j in range(70):
        x, y = rng.random() * 600, rng.random() * 230
        lz.pintar(lz.elipse(x, y, 1.6 + rng.random(), 0.8 + rng.random() * 0.4, rng.random() * 180), pal[rng.integers(len(pal))], 0.85)
    # la luz del sol que entra rasante desde la derecha
    lz.sumar_luz(np.clip((lz.x - 300) / 300, 0, 1) * np.clip(1 - np.abs(lz.y - 150) / 120, 0, 1), "#f9b947", 0.15)
    lz.pintar(np.ones((lz.H, lz.W)), "#e0a070", 0.08)
    ci.marco_recuerdo(lz, color="#f9e2c0", semilla=173)
    return lz


def eco_surcos():
    """«Lo que se siembra, Maisha lo despierta. Lo que se siega, Mauti lo guarda. Y el campo nunca está quieto.»"""
    lz = Lienzo(W, H, semilla=160)
    rng = np.random.default_rng(161)
    HZ = 112
    # cielo de noche de fin de verano, con estrellas y una luna de cosecha grande y anaranjada
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#070914", "#0e1226", "#1a1e3a", "#2c2a48", "#4a3a50"], desde=0, hasta=HZ))
    ci.estrellas(lz, 140, HZ - 10, semilla=162, color="#f0e8d0")
    luna = lz.circulo(90, 46, 15)
    lz.sumar_luz(lz.desenfocar(luna, 24), "#f9a83a", 0.35)
    lz.pintar(luna, rampa(["#d8883a", "#f4b060", "#fde0a0"], np.clip(1 - np.hypot(lz.x - 86, lz.y - 42) / 16, 0, 1)))
    # la colina con el Primer Árbol, a la derecha
    lejos = ci.mascara_bajo(lz, ci.linea_horizonte(lz, HZ, 5, 80, 164))
    lz.pintar(lejos, "#141a24")
    loma = np.clip((lz.y - (HZ - 16 + 0.0012 * (lz.x - 470) ** 2)) / 1.5, 0, 1)
    lz.pintar(loma, "#1a2224")
    _primer_arbol(lz, 470, HZ - 14, 70)
    # los campos: franjas de rastrojo y gavillas en hileras, iluminadas por la hoguera
    campo = lz.y > HZ
    lz.pintar(campo, rampa(["#1a140c", "#2a2010", "#3e2e16", "#5a4420"], np.clip((lz.y - HZ) / 140 + (np.sin(lz.y * 0.9 + lz.x * 0.05) * 0.5 + 0.5) * 0.25, 0, 1)))
    gav = np.zeros((lz.H, lz.W))
    for fila in range(4):
        y = HZ + 10 + fila * 9
        for k in range(14):
            x = 20 + k * 42 + (fila % 2) * 21 + rng.random() * 6
            if abs(x - 300) < 70 and fila > 0:
                continue
            e = 0.6 + fila * 0.15
            gav = np.maximum(gav, lz.poligono([(x - 4 * e, y), (x, y - 12 * e), (x + 4 * e, y)]))
            gav = np.maximum(gav, lz.elipse(x, y - 8 * e, 3 * e, 2 * e))
    lz.sombrear(gav, ["#2a1e0c", "#5a4420", "#8a6a2a", "#c09a40", "#e8c868"], 2, (0.6, -0.4, 0.6))
    # la hoguera en el centro, con chispas
    fx, fy = 300, 214
    for k in range(5):
        lz.pintar(lz.trazo([(fx - 14 + k * 7, fy + 2), (fx - 6 + k * 3, fy - 6)], 2.2), "#3a2416")
    fuego = np.zeros((lz.H, lz.W))
    for k in range(9):
        a = (k - 4) * 3.0
        fuego = np.maximum(fuego, lz.trazo(lz.curva((fx + a, fy), (fx + a * 0.6 + (rng.random() - 0.5) * 6, fy - 14), (fx + a * 0.2, fy - 26 - rng.random() * 10), n=16), 5.0, 0.5))
    lz.sumar_luz(lz.desenfocar(fuego, 40), "#f97a1a", 0.6)
    lz.pintar(fuego, rampa(["#c8401a", "#f9a83a", "#fde27e", "#fffbe8"], np.clip(1 - (fy - lz.y) / 34, 0, 1) * 0.3 + lz.desenfocar(fuego, 2) * 0.7))
    chispas = np.zeros((lz.H, lz.W))
    for k in range(40):
        chispas = np.maximum(chispas, lz.circulo(fx + (rng.random() - 0.5) * 70, fy - 30 - rng.random() * 90, 0.5 + rng.random() * 0.4))
    lz.sumar_luz(chispas, "#ffd27a", 0.9)
    # el suelo iluminado alrededor del fuego
    lz.sumar_luz(np.clip(1 - np.hypot((lz.x - fx) / 160, (lz.y - fy) / 40), 0, 1) * campo, "#f9a83a", 0.35)
    # guirnaldas de farolillos de un poste a otro
    for (x0, x1, yb) in ((40, 250, 128), (350, 580, 126)):
        for xx in (x0, x1):
            lz.pintar(lz.trazo([(xx, yb + 40), (xx, yb - 4)], 1.4), "#2a1a10")
        cuerda = lz.curva((x0, yb), ((x0 + x1) / 2, yb + 18), (x1, yb), n=60)
        lz.pintar(lz.trazo(cuerda, 0.5), "#1a120c")
        for k in range(3, 57, 5):
            px, py = cuerda[k]
            col = ["#f9c46a", "#de6771", "#e6a852", "#9fd0d0"][k % 4]
            f = lz.elipse(px, py + 3, 2.0, 2.6)
            lz.sumar_luz(lz.desenfocar(f, 6), col, 0.45)
            lz.pintar(f, col)
    # los seres de Raíz bailando alrededor del fuego, a contraluz
    for (x, e, mira) in ((228, 1.0, 1), (254, 0.85, 1), (352, 0.95, -1), (378, 1.05, -1), (200, 0.8, 1), (404, 0.8, -1)):
        _constructor(lz, x, 224 - (1 - e) * 10, e, mira, sem=int(x))
    # Maisha y Mauti, bailando de la mano delante del fuego
    ci.maisha_luz(lz, 288, 238, e=1.2)
    _mauti_luz(lz, 314, 238, e=1.2)
    lz.sumar_luz(lz.desenfocar(lz.elipse(301, 230, 6, 4), 4), "#fff1c0", 0.6)
    lz.pintar(np.ones((lz.H, lz.W)), "#e09a5a", 0.06)
    ci.marco_recuerdo(lz, color="#f9e2c0", semilla=165)
    return lz


def _kimya_pie(lz, x, y, e=1.0):
    """Kimya, el Silencio, pequeña y flotando: una figura de luz plateada, casi transparente, con la cabeza redonda
    y serena (ojos cerrados, mirando abajo), dos hilos de luz largos que ondean hacia atrás como cintas y el cuerpo
    que se deshace en niebla. Devuelve su figura (para el reflejo)."""
    cuerpo = np.zeros((lz.H, lz.W))
    for k in range(26):
        t = k / 25
        cuerpo = np.maximum(cuerpo, lz.elipse(x - np.sin(t * 2.5) * 3 * e, y - 22 * e + t * 30 * e, (6.0 - t * 4.5) * e, 3.0 * e))
    cabeza = lz.circulo(x + 1 * e, y - 27 * e, 5.6 * e)
    figura = lz.desenfocar(np.maximum(cuerpo * np.clip(1 - (lz.y - (y - 4 * e)) / (12 * e), 0.1, 1), cabeza), 1.0)
    lz.sumar_luz(lz.desenfocar(figura, 12 * e), "#6db0b0", 0.45)
    lz.sumar_luz(figura, "#d8ece8", 0.55)
    lz.sumar_luz(lz.desenfocar(cabeza, 2 * e), "#ffffff", 0.25)
    # los hilos de luz: salen de la nuca y ondean hacia atrás, largos y finos (no son cuernos)
    hilos = np.zeros((lz.H, lz.W))
    for k, d in enumerate((-1.0, 1.0)):
        pts = [(x - 3 * e - t * 30 * e, y - 30 * e - d * 2 * e + np.sin(t * 6 + k) * 3 * e - t * 6 * e) for t in np.linspace(0, 1, 30)]
        hilos = np.maximum(hilos, lz.trazo(pts, 0.7 * e, 0.15 * e))
    lz.sumar_luz(lz.desenfocar(hilos, 0.8), "#e8f4f0", 0.6)
    # los ojos cerrados, mirando abajo, y una sonrisa leve
    for ox in (x - 0.8 * e, x + 3.2 * e):
        lz.pintar(lz.trazo([(ox - 1.2 * e, y - 26.5 * e), (ox, y - 25.6 * e), (ox + 1.2 * e, y - 26.5 * e)], 0.45 * e), "#346161", 0.85)
    return figura


def _ondas(lz, cx, cy, radios, ang0, ang1, color, alfa):
    """Arcos de una onda de sonido (centrados en cx, cy), de ang0 a ang1 (en grados)."""
    m = np.zeros((lz.H, lz.W))
    for r in radios:
        pts = [(cx + np.cos(np.radians(a)) * r, cy + np.sin(np.radians(a)) * r) for a in np.linspace(ang0, ang1, 24)]
        m = np.maximum(m, lz.trazo(pts, 1.2))
    lz.sumar_luz(lz.desenfocar(m, 3), color, alfa * 0.5)
    lz.sumar_luz(m, color, alfa)


def _pared_garganta(lz, borde, lado, semilla):
    """Una pared de la garganta, de roca a contraluz. borde(y) da el filo interior; lado -1 = pared izquierda.
    Caras planas (facetas), estratos, grietas verticales y el filo encendido por el sol poniente."""
    ys = np.arange(lz.H) / lz.s
    filo_x = np.array([borde(y) for y in ys])[:, None]
    dentro = (lz.x < filo_x) if lado < 0 else (lz.x > filo_x)
    m = dentro.astype(float)
    dist = np.abs(lz.x - filo_x)                                    # lo lejos que está del filo
    faceta = np.floor(lz.ruido(26, 2, semilla=semilla) * 6) / 6     # caras planas de la roca
    estratos = np.sin((lz.y + (lz.ruido(30, 2, semilla=semilla + 1) - 0.5) * 10) * 0.42) * 0.5 + 0.5
    v = 0.18 + faceta * 0.22 + (estratos - 0.5) * 0.08 + np.clip(1 - dist / 70, 0, 1) * 0.25
    lz.pintar(m, rampa(["#120a14", "#1e1220", "#2e1c2e", "#44283a", "#5e3646", "#80485a", "#a8606a"], np.clip(v, 0, 1)))
    # la cara que mira al sol (cerca del filo) se enciende de naranja
    lz.sumar_luz(m * np.clip(1 - dist / 26, 0, 1) * (faceta > 0.4), "#e08050", 0.35)
    grietas = np.abs(np.sin(lz.x * 0.21 + lz.ruido(8, 2, semilla=semilla + 2) * 6)) < 0.05
    lz.pintar(m * grietas * (lz.ruido(12, 2, semilla=semilla + 3) > 0.45), "#0c060e", 0.8)
    lz.pintar(m * (np.abs(estratos - 0.5) < 0.035), "#0c060e", 0.5)
    filo = m * (dist < 1.6)
    lz.sumar_luz(lz.desenfocar(filo, 1.0), "#f9b070", 0.9)
    # matas de hierba en los salientes
    matas = np.clip((lz.ruido(2.5, 2, semilla=semilla + 4) - 0.74) * 6, 0, 1) * m * (estratos > 0.85)
    lz.pintar(matas, "#2e3a24", 0.9)
    return m


def eco_canada():
    """«¡Maisha!» … «¡Maisha!» — «¡Mauti!» … «¡Mauti!» — «Kimya, grita tú.» — «El Silencio no tiene eco.»"""
    lz = Lienzo(W, H, semilla=180)
    rng = np.random.default_rng(181)
    # cielo de atardecer: violeta arriba, rosa y naranja en el hueco de la garganta, donde se pone el sol
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#2a1e3e", "#5a3458", "#a8506a", "#e0805a", "#f9c27a"], desde=0, hasta=150))
    sol = lz.circulo(318, 112, 15)
    lz.sumar_luz(lz.desenfocar(sol, 50), "#f9a03a", 0.6)
    lz.sumar_luz(lz.desenfocar(sol, 12), "#ffe0a0", 0.6)
    lz.pintar(sol, "#fff0c8")
    ci.cumulos(lz, [(200, 30, 70, 9), (360, 22, 90, 8), (470, 46, 60, 7)], colores=("#5a3458", "#8a4a62", "#d0706a", "#f9b080"), semilla=182, alfa=0.6)
    lejos = ci.mascara_bajo(lz, ci.linea_horizonte(lz, 122, 6, 40, 183))
    lz.pintar(lejos, "#a8607a")
    lejos2 = ci.mascara_bajo(lz, ci.linea_horizonte(lz, 134, 5, 30, 184))
    lz.pintar(lejos2, "#7a4060")
    # las dos paredes: el hueco se abre hacia arriba, con salientes escalonados
    _pared_garganta(lz, lambda y: 250 - y * 0.32 + 12 * np.floor(y / 46) - 6 * np.sin(y * 0.09), -1, 185)
    _pared_garganta(lz, lambda y: 372 + y * 0.30 - 10 * np.floor(y / 52) + 5 * np.sin(y * 0.08 + 1), 1, 186)
    # el fondo de la garganta y el arroyo, quieto como un espejo, que serpentea hacia nosotros
    HZ_A = 196
    t_ = np.clip((lz.y - HZ_A) / 60, 0, 1)
    centro_a = 334 + np.sin(t_ * 3.2 + 0.4) * 22 + (lz.ruido(6, 2, semilla=190) - 0.5) * 4
    ancho_a = 6 + t_ * 40 + np.sin(lz.y * 0.35) * 2
    agua = np.clip(lz.desenfocar(((lz.y > HZ_A) * (np.abs(lz.x - centro_a) < ancho_a)).astype(float), 0.8), 0, 1)
    orilla = np.clip(lz.desenfocar(((lz.y > HZ_A - 3) * (np.abs(lz.x - centro_a) < ancho_a + 6 + t_ * 10)).astype(float), 1.5), 0, 1)
    lz.pintar(orilla, rampa(["#1a1020", "#2a1a2a", "#3e2834"], t_))
    lz.pintar(orilla * (lz.ruido(1.2, 2, semilla=191) > 0.7), "#5a3a40", 0.7)
    lz.pintar(agua, rampa(["#3a2a48", "#7a4a6a", "#c07070", "#f0a070", "#f9c890"], np.clip(1 - t_ * 0.9, 0, 1)))
    # (el agua no se mueve: es un espejo; refleja el cielo y a Kimya)
    # la cornisa, a la izquierda: un saliente de roca con hierba encima, donde están Mauti y Maisha
    YC = 196
    cornisa = lz.poligono([(0, YC + 2), (90, YC - 3), (230, YC - 1), (268, YC + 4), (276, YC + 14), (250, 230), (210, 256), (0, 256)])
    lz.sombrear(cornisa, ["#120a14", "#1e1420", "#2e2030", "#46303e", "#6a4650", "#9a6a60"], 6, (0.6, -0.8, 0.5),
                textura=np.floor(lz.ruido(10, 2, semilla=187) * 5) / 5, fuerza_tex=0.4)
    filo_c = np.clip(cornisa - np.roll(cornisa, int(2 * lz.s), axis=0), 0, 1)
    lz.sumar_luz(filo_c, "#f9a060", 0.7)
    hierba = np.zeros((lz.H, lz.W))
    for k in range(110):
        x = rng.random() * 262
        yb = YC - 2 + (x / 262) * 2
        hierba = np.maximum(hierba, lz.trazo([(x, yb + 2), (x + (rng.random() - 0.5) * 3, yb - 2 - rng.random() * 4)], 0.5))
    lz.pintar(hierba, "#3a4a2a", 0.9)
    lz.sumar_luz(hierba * (lz.ruido(1, 1, semilla=188) > 0.5), "#e09a5a", 0.3)
    # las ondas: las de Maisha (doradas) y las de Mauti (lilas, más altas) van hacia la pared de enfrente y vuelven
    _ondas(lz, 214, 170, (14, 22, 30), -35, 25, "#f9c46a", 0.6)
    _ondas(lz, 168, 160, (40, 50, 60), -48, -18, "#c4b0f0", 0.6)
    _ondas(lz, 470, 150, (12, 20, 28), 155, 210, "#f9c46a", 0.45)       # (vuelven de la peña)
    _ondas(lz, 470, 118, (12, 20, 28), 150, 205, "#c4b0f0", 0.45)
    # Mauti y Maisha gritando hacia la peña; Kimya flota sobre el arroyo, en silencio, mirando el agua
    lz.pintar(lz.desenfocar(lz.elipse(190, YC + 1, 40, 3.5), 2), "#0a060c", 0.5)
    _mauti_luz(lz, 168, YC, e=1.35, mira=1)
    ci.maisha_luz(lz, 210, YC, e=1.35)
    kimya = _kimya_pie(lz, 330, 172, e=1.1)
    # su reflejo en el agua quieta (lo único que devuelve la cañada de ella): la figura, dada la vuelta, más abajo
    a0, a1 = int(132 * lz.s), int(178 * lz.s)
    destino = int(206 * lz.s)
    refl = np.zeros_like(kimya)
    alto_r = min(a1 - a0, lz.H - destino)
    refl[destino:destino + alto_r, :] = kimya[a0:a1, :][::-1, :][:alto_r, :]
    refl = np.roll(refl, int(6 * lz.s), axis=1)              # (el arroyo se tuerce un poco hacia la derecha)
    lz.sumar_luz(lz.desenfocar(refl, 1.5) * agua * (np.sin(lz.y * 2.0) > -0.6), "#d8ece8", 0.45)
    # motas de luz que suben de la garganta
    motas = np.zeros((lz.H, lz.W))
    for k in range(30):
        motas = np.maximum(motas, lz.circulo(250 + rng.random() * 160, 60 + rng.random() * 120, 0.5 + rng.random() * 0.4))
    lz.sumar_luz(motas, "#ffe0b0", 0.8)
    lz.pintar(np.ones((lz.H, lz.W)), "#3e8a86", 0.06)
    ci.marco_recuerdo(lz, color="#f9e2c0", semilla=189)
    return lz


def kimya_lago():
    """«Mira el agua. ¿A quién ves en tu reflejo?» — en el lago quieto, bajo Maisha, está Mauti."""
    lz = Lienzo(W, H, semilla=200)
    rng = np.random.default_rng(201)
    HZ = 98
    # el cielo de la hora azul: azul hondo arriba, lila y melocotón pálido en el horizonte, las primeras estrellas
    cielo_cols = ["#0e1428", "#1c2a4a", "#3a3e6a", "#7a6a90", "#c8a0a8", "#f0c8a8"]
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(cielo_cols, desde=0, hasta=HZ))
    ci.estrellas(lz, 70, HZ - 30, semilla=202, color="#e8f0f4")
    luna = lz.circulo(120, 30, 8)
    lz.sumar_luz(lz.desenfocar(luna, 14), "#c8d8e8", 0.4)
    lz.pintar(luna, "#f0f4ec")
    # la orilla lejana: sauces y, al este, las paredes de la Cañada, a contraluz
    arboles = ci.mascara_bajo(lz, ci.linea_horizonte(lz, HZ - 8, 7, 34, 203))
    lz.pintar(arboles * (lz.y < HZ + 1), "#141a28")
    sauces = ci.mascara_bajo(lz, ci.linea_horizonte(lz, HZ - 4, 4, 14, 208))
    lz.pintar(sauces * (lz.y < HZ + 1), "#10141f")
    pena = lz.poligono([(470, HZ + 2), (490, HZ - 26), (520, HZ - 30), (560, HZ - 22), (600, HZ - 34), (600, HZ + 2)])
    lz.pintar(pena, "#1a1a2c")
    # el lago: un espejo. Refleja el cielo del revés (más oscuro) y la orilla lejana
    agua = (lz.y >= HZ).astype(float)
    filas = lz.img.shape[0]
    eje = int(HZ * lz.s)
    # cada fila del agua toma la del cielo que tiene encima en espejo (más abajo de lo que refleja, el cielo de arriba)
    origen = np.clip(2 * eje - 1 - np.arange(filas), 0, filas - 1)
    reflejo = lz.img[origen]
    lz.pintar(agua, reflejo * 0.82)
    lz.pintar(agua * np.clip((lz.y - HZ) / 160, 0, 1), "#0a1424", 0.25)
    vetas = (estirar_h(lz, lz.ruido(1.5, 2, semilla=204), 40) > 0.72) * agua
    lz.pintar(vetas, "#c8e0e8", 0.12)
    # Kimya, alzándose del agua, a la derecha (con su reflejo)
    kx, ky = 400, 176
    k_lz = Lienzo(W, H, semilla=205)
    _kimya_pie(k_lz, kx, ky, e=1.9)
    _sumar_con_reflejo(lz, k_lz, ky + 4, agua, 0.55)
    lz.sumar_luz(lz.desenfocar(lz.elipse(kx, ky + 4, 26, 4), 4) * agua, "#9fd0d0", 0.5)
    # la orilla de la isla, a la izquierda: hierba, el círculo de piedras y el borde donde está Maisha
    YO = 196
    isla = lz.poligono([(0, 150), (60, 158), (140, 172), (200, YO - 2), (250, YO), (262, YO + 6), (240, YO + 12),
                        (150, 230), (90, 256), (0, 256)])
    lz.sombrear(isla, ["#0e1a14", "#16261c", "#203422", "#2c4428", "#3a5430"], 6, (0.5, -0.8, 0.5),
                textura=lz.ruido(1.5, 2, semilla=206), fuerza_tex=0.35)
    filo = np.clip(isla - np.roll(isla, int(2 * lz.s), axis=0), 0, 1)
    lz.sumar_luz(filo, "#9fb8c8", 0.35)
    for (x, y, r) in ((40, 178, 6), (78, 190, 5), (120, 206, 5.5), (26, 214, 6)):
        piedra = lz.elipse(x, y, r * 1.3, r * 0.8)
        lz.sombrear(piedra, ["#1a1c24", "#2e3240", "#4a5060", "#6a7080"], r, (0.5, -0.8, 0.5))
    hierba = np.zeros((lz.H, lz.W))
    for k in range(140):
        x = rng.random() * 250
        yb = 150 + x * 0.18 + rng.random() * 40
        hierba = np.maximum(hierba, lz.trazo([(x, yb), (x + (rng.random() - 0.5) * 3, yb - 3 - rng.random() * 4)], 0.5))
    lz.pintar(hierba * isla, "#3e5a34", 0.9)
    # Maisha en el borde, mirando el agua; y en el agua, bajo ella, del revés... Mauti
    mx = 222
    m_lz = Lienzo(W, H, semilla=207)
    _mauti_luz(m_lz, mx, YO, e=1.6, mira=1)
    _pegar_con_reflejo(lz, m_lz, YO + 2, agua, 0.75, solo_reflejo=True)
    ci.maisha_luz(lz, mx, YO, e=1.6)
    # la luz de las dos, sobre el agua quieta
    lz.sumar_luz(lz.desenfocar(lz.elipse(mx, YO + 22, 14, 18), 8) * agua, "#b8a8e0", 0.35)
    motas = np.zeros((lz.H, lz.W))
    for k in range(26):
        motas = np.maximum(motas, lz.circulo(300 + rng.random() * 200, 80 + rng.random() * 100, 0.5 + rng.random() * 0.4))
    lz.sumar_luz(motas, "#e8f4f0", 0.8)
    # viñeta suave
    lz.pintar(np.clip((np.hypot((lz.x - 300) / 330, (lz.y - 140) / 170) - 0.75) * 2.0, 0, 1), "#05070c", 0.6)
    return lz


def _sumar_con_reflejo(lz, otro, eje_y, agua, fuerza):
    """Como _pegar_con_reflejo, pero para lo que está hecho de luz (se suma: lo negro no tapa nada)."""
    lz.img = 1 - (1 - lz.img) * (1 - np.clip(otro.img, 0, 1))
    eje = int(eje_y * lz.s)
    img_r = np.zeros_like(otro.img)
    alto = min(eje, lz.H - eje)
    img_r[eje:eje + alto] = otro.img[eje - alto:eje][::-1]
    img_r = img_r * (agua * fuerza)[..., None]
    lz.img = 1 - (1 - lz.img) * (1 - np.clip(img_r, 0, 1))


def estirar_h(lz, campo, largo):
    import cv2
    k = np.ones((1, int(largo * lz.s)), np.float32) / int(largo * lz.s)
    return cv2.filter2D(campo.astype(np.float32), -1, k)


def _pegar_con_reflejo(lz, otro, eje_y, agua, fuerza, solo_reflejo=False):
    """Pega lo pintado en «otro» (un lienzo aparte) y, debajo de eje_y, su reflejo del revés sobre el agua."""
    eje = int(eje_y * lz.s)
    if not solo_reflejo:
        lz.pintar(otro.alfa, otro.img)
    img_r = np.zeros_like(otro.img)
    alfa_r = np.zeros_like(otro.alfa)
    alto = min(eje, lz.H - eje)
    img_r[eje:eje + alto] = otro.img[eje - alto:eje][::-1]
    alfa_r[eje:eje + alto] = otro.alfa[eje - alto:eje][::-1]
    # el reflejo tiembla un poco y es algo más oscuro y azulado
    lz.pintar(lz.desenfocar(alfa_r, 0.6) * agua * fuerza, img_r * 0.85 + np.array([0.02, 0.04, 0.08]))


PIEZAS = {"17_kimya_lago": kimya_lago, "16_eco_canada": eco_canada, "12_eco_puente": eco_puente, "13_eco_pasarelas": eco_pasarelas, "14_eco_cobrizo": eco_cobrizo, "15_eco_surcos": eco_surcos}
