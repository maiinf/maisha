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
  18_eco_orilla   EL SEXTO ECO (Orilla de Juncos). La despedida: una noche de luna sobre el río ancho, que sube hacia
                  el norte entre colinas oscuras. Mauti se aleja río arriba en una barca pequeña, con su luz lila, y
                  mira hacia atrás. En la playa, entre los juncos, Maisha sostiene una linterna encendida para que Mauti
                  sepa por dónde volver. Las dos luces, la dorada y la lila, se alargan sobre el agua.
  19_eco_travesia EL SÉPTIMO ECO (La Travesía). Noche de niebla en el río, cerca de la Gruta: al fondo, la peña con
                  la boca oscura de la Gruta de las Raíces y raíces enormes que bajan por la roca. Delante, la isla:
                  la barca de Mauti, sin remos, varada entre los juncos; Mauti, de rodillas junto a una piedra plana,
                  deja debajo su hoja de cobre, que brilla. Luciérnagas y la luna tapada por la niebla.
  20_eco_cueva    EL OCTAVO ECO (la cueva de las setas, bajo el Paso de Piedra). Una cueva oscura llena de setas que
                  brillan (verde-agua y violeta). En el centro, un corro de setas pequeñas se come un montón de hojas
                  caídas, y de la tierra que dejan brotan hojitas nuevas. Maisha (dorada), de rodillas, mira las setas
                  con cara de asco; KIMYA, el Silencio, flota a su lado, plateada, tranquila. Polvo de esporas en el aire.
  21_eco_lago     EL NOVENO ECO (Lago Espejo, la voz del Silencio). Noche quieta sobre el lago: arriba, solo estrellas y
                  colinas negras. Pero en el agua, del revés, se ve lo que arriba no está: el PRIMER ÁRBOL dorado en su
                  colina, KIMYA flotando sobre su reflejo y nueve espirales de luz en arco (ocho verdes, una plateada).
                  Maisha, en la orilla de la isla, mira el agua.
  22_ruinas_mauti LAS RUINAS DEL PRIMER ÁRBOL (no es un recuerdo: pasa ahora). Anochecer nevado en la cima: columnas
                  rotas de piedra clara; en el centro, el Primer Árbol enorme, gris y medio de piedra, con vetas violetas
                  y unas pocas hojas secas. A sus pies, MAUTI, hecha piedra, con su hoja de cobre en lo alto. Alrededor,
                  nueve piedras apagadas en corro. Maisha, pequeña, de espaldas en primer término, mira hacia arriba.
  23_arbol_libre  EL FINAL DE RAÍZ. La misma cima: la copa del Primer Árbol vuelve a ser de oro y brilla como un sol; las
                  hojas doradas caen despacio. Las nueve piedras están encendidas (la del Silencio, plateada). Mauti, libre
                  (plateada y lila), junto a Maisha, que sostiene entre las manos una semilla grande que brilla.
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


def eco_orilla():
    """«Deja la linterna encendida en la orilla. Así sabré por dónde volver.»"""
    lz = Lienzo(W, H, semilla=220)
    rng = np.random.default_rng(221)
    HZ = 104
    # cielo de noche: azul hondo, un poco de verde-agua en el horizonte, estrellas y la luna creciente
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#060a16", "#0c1426", "#142238", "#1e3446", "#2e4a52"], desde=0, hasta=HZ))
    ci.estrellas(lz, 160, HZ - 14, semilla=222, color="#e8f0f4")
    lx, ly = 470, 34
    luna = np.clip(lz.circulo(lx, ly, 11) - lz.circulo(lx + 5, ly - 3, 10), 0, 1)
    lz.sumar_luz(lz.desenfocar(lz.circulo(lx, ly, 11), 18), "#c8d8e8", 0.3)
    lz.pintar(luna, "#f0f4e4")
    ci.cumulos(lz, [(160, 50, 70, 8), (380, 64, 60, 7)], colores=("#0e1626", "#1a2638", "#2a3a4e", "#3e5262"), semilla=223, alfa=0.6)
    # las colinas del norte, por donde se va el río (cuanto más lejos, más azuladas)
    for k, (base, amp, col) in enumerate(((HZ - 6, 14, "#1a2a3a"), (HZ + 2, 10, "#121c28"))):
        linea = ci.linea_horizonte(lz, base, amp, 60 - k * 10, 224 + k)
        lz.pintar(ci.mascara_bajo(lz, linea), col)
    # el río: estrecho en el horizonte (río arriba) y ancho al llegar delante, con las orillas en curva
    t = np.clip((lz.y - HZ) / (256 - HZ), 0, 1)
    xl = 296 - 70 * np.sin(np.pi * 0.8 * t) + 4 * np.sin(t * 9.0)
    xr = 310 + 330 * t ** 1.7 + 7 * np.sin(t * 5.0 + 1.0)
    rio = lz.desenfocar(((lz.x > xl) & (lz.x < xr) & (lz.y > HZ + 1)).astype(float), 0.8)
    # las orillas: prados oscuros que se pierden en la niebla del horizonte
    tierra = np.clip((lz.y > HZ).astype(float) - rio, 0, 1)
    lz.pintar(tierra, rampa(["#0a120e", "#101c16", "#16261c", "#1c3022"], np.clip(t * 1.2 + (lz.ruido(4, 2, semilla=225) - 0.5) * 0.25, 0, 1)))
    lz.pintar(tierra * np.clip(1 - t * 3.5, 0, 1), "#2a4450", 0.55)
    # bosquecillos y sauces en las riberas, a lo lejos
    copas = np.zeros((lz.H, lz.W))
    for k in range(26):
        lado = -1 if k % 2 else 1
        tt = 0.04 + rng.random() * 0.35
        yy = HZ + tt * (256 - HZ)
        borde = (296 - 70 * np.sin(np.pi * 0.8 * tt)) if lado < 0 else (310 + 330 * tt ** 1.7)
        xx = borde + lado * (6 + rng.random() * 60)
        e = 0.4 + tt * 2.2
        copas = np.maximum(copas, lz.elipse(xx, yy - 5 * e, (5 + rng.random() * 4) * e, (5 + rng.random() * 3) * e))
    lz.pintar(copas, rampa(["#0a1410", "#0e1c16"], np.clip(lz.ruido(2, 2, semilla=232), 0, 1)))
    lz.pintar(copas * np.clip(1 - t * 3.0, 0, 1), "#2a4450", 0.45)
    # el agua: refleja el cielo, más clara a lo lejos, con ondas largas
    agua_col = rampa(["#0a1820", "#10242e", "#18343e", "#24485a", "#3a6670"], np.clip(1 - t, 0, 1))
    lz.pintar(rio, agua_col)
    ondas = (estirar_h(lz, lz.ruido(1.2, 2, semilla=226), 26) > 0.66) * rio
    lz.pintar(ondas, "#4c8d8d", 0.3)
    lz.pintar(np.clip(rio - lz.desenfocar(tierra, 1.5) * 0, 0, 1) * np.clip(1 - np.abs(lz.x - xl) / 1.5, 0, 1), "#6db0b0", 0.35)
    # la luna sobre el agua: una columna de destellos que tiembla
    columna = np.clip(1 - np.abs(lz.x - 420 - np.sin(lz.y * 0.7) * 3) / 10, 0, 1) * (lz.y > 150) * rio
    lz.sumar_luz(columna * (estirar_h(lz, lz.ruido(1.0, 2, semilla=227), 8) > 0.55), "#d8f0ec", 0.5)
    # la playa de arena delante, a la izquierda, donde está Maisha
    playa = np.clip(lz.desenfocar(((lz.y > 204 + 0.04 * (lz.x - 120) ** 1.3 * (lz.x > 120) - 6 * np.sin(lz.x * 0.03)) & (lz.x < xl + 4)).astype(float), 1.0), 0, 1)
    lz.sombrear(playa, ["#100e0c", "#1a1612", "#28201a", "#382c20", "#4a3a28"], 6, (0.6, -0.6, 0.5),
                textura=lz.ruido(1.2, 2, semilla=228), fuerza_tex=0.35)
    filo = np.clip(playa - np.roll(playa, int(-3 * lz.s), axis=1), 0, 1) * (lz.y > 200)
    lz.pintar(filo, "#5a7a78", 0.35)
    # la barca de Mauti, río arriba, alejándose (con la estela que deja hacia nosotros)
    bx, by = 336, 142
    estela = np.zeros((lz.H, lz.W))
    for lado in (-1, 1):
        estela = np.maximum(estela, lz.trazo([(bx + 10 * lado, by + 3), (bx + 22 * lado + 4, by + 14), (bx + 30 * lado + 8, by + 24)], 0.5, 0.15))
    lz.pintar(estela * rio, "#9fd0d0", 0.4)
    barca = lz.poligono([(bx - 15, by - 3), (bx + 15, by - 3), (bx + 11, by + 2), (bx - 11, by + 2)])
    lz.sombrear(barca, ["#140c08", "#24160c", "#3a2414", "#5a3a20"], 2, (0.6, -0.6, 0.5))
    lz.pintar(lz.trazo([(bx - 15, by - 3), (bx + 15, by - 3)], 0.4), "#8a6040", 0.8)
    pertiga = lz.trazo([(bx + 9, by + 8), (bx + 14, by - 26)], 0.5)
    lz.pintar(pertiga, "#3a2a1e")
    m_lz = Lienzo(W, H, semilla=229)
    _mauti_luz(m_lz, bx + 2, by - 3, e=0.95, mira=-1)
    _sumar_con_reflejo(lz, m_lz, by + 2, rio, 0.45)
    lz.sumar_luz(lz.desenfocar(lz.elipse(bx, by + 10, 18, 22), 6) * rio, "#b8a8e0", 0.3)
    # Maisha en la playa, con la linterna en alto
    mx, my = 200, 228
    # la luz de la linterna, primero (para que Maisha quede delante)
    fx, fy = mx + 24, my - 34
    lz.sumar_luz(lz.desenfocar(lz.elipse(fx, my + 4, 60, 14), 12) * playa, "#f9a83a", 0.4)
    lz.sumar_luz(lz.desenfocar(lz.circulo(fx, fy, 6), 44), "#f9a83a", 0.35)
    # su reflejo, alargado sobre el agua de la orilla
    reflejo_l = np.clip(1 - np.abs(lz.x - (fx + 18) - np.sin(lz.y * 0.9) * 2) / 6, 0, 1) * (lz.y > my - 4) * rio
    lz.sumar_luz(reflejo_l * (estirar_h(lz, lz.ruido(1.0, 2, semilla=230), 6) > 0.45), "#f9c46a", 0.6)
    ci.maisha_luz(lz, mx, my, e=1.5)
    palo = lz.trazo([(mx + 7, my - 7), (mx + 14, my - 26), (mx + 20, my - 42), (fx, fy - 9)], 0.9)
    lz.pintar(palo, "#4a3018")
    lz.pintar(lz.trazo([(fx, fy - 9), (fx, fy - 6)], 0.35), "#1a120c")
    farol = lz.elipse(fx, fy, 4.4, 5.6)
    lz.sumar_luz(lz.desenfocar(farol, 12), "#f9c46a", 0.7)
    lz.pintar(farol, rampa(["#e6a852", "#fde27e", "#fffbe8"], np.clip(1 - np.hypot(lz.x - fx, lz.y - fy) / 5, 0, 1)))
    lz.pintar(lz.trazo([(fx - 4.4, fy - 5.4), (fx + 4.4, fy - 5.4)], 0.8) + lz.trazo([(fx - 4.4, fy + 5.4), (fx + 4.4, fy + 5.4)], 0.8)
              + lz.trazo([(fx, fy - 5.4), (fx, fy + 5.4)], 0.3), "#3a2414")
    # los juncos, a contraluz, delante y a los lados
    juncos = np.zeros((lz.H, lz.W))
    for k in range(70):
        lado = rng.random()
        x = rng.random() * 130 if lado < 0.6 else 560 + rng.random() * 40
        yb = 258 if lado < 0.6 else 240 + rng.random() * 18
        alto = 26 + rng.random() * 46
        juncos = np.maximum(juncos, lz.trazo([(x, yb), (x + (rng.random() - 0.5) * 8, yb - alto)], 0.7, 0.3))
        if rng.random() < 0.35:
            juncos = np.maximum(juncos, lz.elipse(x + (rng.random() - 0.5) * 4, yb - alto + 2, 1.1, 3.2))
    lz.pintar(juncos, "#070c0a")
    lz.sumar_luz(juncos * np.clip(1 - np.hypot(lz.x - fx, lz.y - fy) / 120, 0, 1), "#f9a83a", 0.25)
    # luciérnagas
    motas = np.zeros((lz.H, lz.W))
    for k in range(22):
        motas = np.maximum(motas, lz.circulo(rng.random() * 600, 150 + rng.random() * 100, 0.5 + rng.random() * 0.3))
    lz.sumar_luz(motas, "#e8f0a0", 0.8)
    lz.pintar(np.ones((lz.H, lz.W)), "#6db0b0", 0.05)
    ci.marco_recuerdo(lz, color="#d8f0ec", semilla=231)
    return lz


def eco_travesia():
    """«Te dejo algo aquí, en la isla. Debajo de la piedra plana.»"""
    lz = Lienzo(W, H, semilla=240)
    rng = np.random.default_rng(241)
    HZ = 120
    # cielo de noche con niebla y la luna tapada
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#070a12", "#0e1420", "#18202e", "#26303c", "#36424a"], desde=0, hasta=HZ))
    ci.estrellas(lz, 60, 70, semilla=242, color="#e8f0f4")
    luna = lz.circulo(140, 34, 12)
    lz.sumar_luz(lz.desenfocar(luna, 30), "#a8b8c8", 0.25)
    lz.pintar(luna, "#c8d0d0", 0.5)
    # la peña del fondo, irregular, con la boca de la Gruta
    pts = [(200, HZ + 6)]
    for k in range(15):
        t = k / 14
        x = 210 + t * 250
        y = 26 + 40 * (abs(t - 0.45) * 2) ** 1.6 + math.sin(t * 17) * 5 + rng.random() * 4
        pts.append((x, y))
    pts.append((470, HZ + 6))
    pena = lz.poligono(pts)
    grietas = (np.abs(np.sin(lz.x * 0.25 + lz.ruido(6, 2, semilla=243) * 9)) < 0.07) * pena
    lz.sombrear(pena, ["#08090c", "#0e1014", "#161a1e", "#1e2428", "#283036"], 30, (0.4, -0.7, 0.5), textura=lz.ruido(2.5, 3, semilla=243), fuerza_tex=0.55)
    lz.pintar(grietas, "#050608", 0.8)
    boca = lz.poligono([(304, HZ + 4), (308, 84), (322, 68), (338, 66), (352, 78), (358, HZ + 4)])
    lz.pintar(lz.desenfocar(boca, 1), "#020203")
    lz.sumar_luz(lz.desenfocar(lz.elipse(331, 104, 16, 12), 9), "#6a4a9a", 0.3)
    # raíces enormes que bajan por la roca, se retuercen y abrazan la boca de la cueva
    raices = np.zeros((lz.H, lz.W))
    for k in range(7):
        lado = -1 if k % 2 == 0 else 1
        x0 = 330 + lado * (8 + k * 9)
        a = (x0 + rng.random() * 10, 20 + rng.random() * 8)
        b = (330 + lado * (26 + k * 6) + math.sin(k) * 12, 60 + k * 4)
        c = (330 + lado * (20 + k * 11), HZ + 3)
        pts_r = lz.curva(a, b, c, n=40)
        raices = np.maximum(raices, lz.trazo(pts_r, 3.2 - k * 0.25, 1.0))
        for (px, py) in pts_r[8::9]:
            raices = np.maximum(raices, lz.trazo(lz.curva((px, py), (px + lado * 8, py + 6), (px + lado * 12, py + 16 + rng.random() * 8), n=12), 1.0, 0.3))
    lz.sombrear(raices, ["#120c08", "#22180e", "#342414", "#4a3420", "#64482c"], 2.4, (0.4, -0.7, 0.5), textura=np.clip(lz.ruido(0.6, 2, semilla=244), 0, 1), fuerza_tex=0.5)
    lz.pintar(raices * (lz.ruido(1.2, 2, semilla=250) > 0.7), "#2a3a22", 0.6)                 # musgo
    # las orillas: laderas con bosque a contraluz
    for (base, amp, sem, col) in ((HZ - 30, 20, 251, "#0b100d"), (HZ - 12, 14, 252, "#080c0a")):
        linea = ci.linea_horizonte(lz, base, amp, 40, sem)
        orilla = ci.mascara_bajo(lz, linea) * ((lz.x < 230) | (lz.x > 440)).astype(float) * (lz.y <= HZ + 2)
        lz.pintar(orilla, col)
    # el río, con la niebla encima
    rio = (lz.y > HZ).astype(float)
    lz.pintar(rio, lz.gradiente(["#1e2e36", "#16242c", "#0e181e", "#0a1014"], desde=HZ, hasta=256))
    lz.sumar_luz(np.clip(1 - np.abs(lz.x - 140) / 8, 0, 1) * (lz.y > HZ + 4) * (estirar_h(lz, lz.ruido(1.0, 2, semilla=245), 8) > 0.6), "#a8b8c8", 0.25)
    lz.pintar(np.clip(1 - (lz.y - HZ) / 16, 0, 1) * (lz.y >= HZ), "#141c22", 0.7)            # (el borde del agua, sin raya)
    lz.pintar(np.clip(1 - (HZ - lz.y) / 10, 0, 1) * (lz.y < HZ) * ((lz.x < 230) | (lz.x > 440)), "#141c22", 0.5)
    niebla = np.clip(1 - np.abs(lz.y - HZ) / 22, 0, 1) * (lz.ruido(30, 2, semilla=246) * 0.5 + 0.5)
    lz.pintar(lz.desenfocar(niebla, 4), "#7a8a98", 0.45)
    # la isla delante, con juncos, y la piedra plana
    isla = lz.poligono([(120, 256), (150, 214), (210, 196), (300, 192), (380, 200), (430, 222), (460, 256)])
    lz.sombrear(isla, ["#0c120e", "#141e16", "#1c2a1e", "#263826"], 8, (0.5, -0.7, 0.5), textura=lz.ruido(1.5, 2, semilla=247), fuerza_tex=0.4)
    piedra = lz.elipse(290, 222, 22, 7)
    lz.sombrear(piedra, ["#1a1c20", "#2a2e34", "#3e444c", "#565e66"], 6, (0.5, -0.7, 0.5))
    # la barca de Mauti, sin remos, varada a la izquierda
    barca = lz.poligono([(150, 222), (158, 232), (210, 232), (218, 220), (210, 224), (158, 224)])
    lz.sombrear(barca, ["#140c08", "#24160c", "#3a2414", "#5a3a20"], 3, (0.5, -0.7, 0.5))
    lz.pintar(lz.trazo([(150, 222), (158, 224), (210, 224), (218, 220)], 0.8), "#7a5a3a")
    # Mauti, de rodillas junto a la piedra, dejando la hoja (que brilla, de cobre)
    m_lz = Lienzo(W, H, semilla=248)
    _mauti_luz(m_lz, 262, 222, e=1.3, mira=1)
    lz.img = 1 - (1 - lz.img) * (1 - np.clip(m_lz.img, 0, 1))
    hoja = lz.elipse(282, 219, 4, 2, -25)
    lz.sumar_luz(lz.desenfocar(hoja, 8), "#f4b470", 0.6)
    lz.pintar(hoja, "#e0904e")
    lz.pintar(lz.trazo([(279, 220.5), (285, 217.5)], 0.4), "#7a3418")
    lz.sumar_luz(lz.desenfocar(lz.elipse(262, 222, 30, 8), 10) * isla, "#b8a8e0", 0.25)
    # juncos a contraluz y luciérnagas
    juncos = np.zeros((lz.H, lz.W))
    for k in range(60):
        x = 120 + rng.random() * 340
        yb = 200 + rng.random() * 40 if 140 < x < 440 else 250
        if 240 < x < 320 and yb < 230:
            continue
        alto = 12 + rng.random() * 24
        juncos = np.maximum(juncos, lz.trazo([(x, yb), (x + (rng.random() - 0.5) * 6, yb - alto)], 0.6, 0.3))
    lz.pintar(juncos * (lz.y > 170), "#060a08")
    motas = np.zeros((lz.H, lz.W))
    for k in range(30):
        motas = np.maximum(motas, lz.circulo(rng.random() * 600, 120 + rng.random() * 120, 0.5 + rng.random() * 0.3))
    lz.sumar_luz(motas, "#e8f0a0", 0.8)
    lz.pintar(np.ones((lz.H, lz.W)), "#6db0b0", 0.05)
    ci.marco_recuerdo(lz, color="#d8f0ec", semilla=249)
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


def eco_cueva():
    """«¿Son tuyas?» — «Son mías. Se comen lo que cae y se lo devuelven a la tierra.» — «Son un poco feas.»
    — «Lo necesario casi nunca es bonito.» — «Una seta que mandara en vez de servir... eso sí sería feo.»"""
    lz = Lienzo(W, H, semilla=200)
    rng = np.random.default_rng(201)
    # la cueva: roca oscura, más clara en el centro, con estalactitas arriba
    fondo = np.clip(1 - np.hypot((lz.x - 300) / 330, (lz.y - 150) / 200), 0, 1)
    lz.pintar(np.ones((lz.H, lz.W)), rampa(["#050408", "#0c0a12", "#16121e", "#221c2c", "#30283c"],
                                           np.clip(fondo * 0.8 + (lz.ruido(30, 3, semilla=202) - 0.5) * 0.25, 0, 1)))
    for k in range(12):
        x = rng.random() * W
        largo = 14 + rng.random() * 36
        est = lz.poligono([(x - 6 - rng.random() * 6, 0), (x + 6 + rng.random() * 6, 0), (x + rng.random() * 2, largo)])
        lz.sombrear(est, ["#08060c", "#141018", "#221c28", "#342a3a"], 4, LUZ)
    suelo = lz.poligono([(0, 176), (120, 166), (300, 170), (480, 164), (600, 172), (600, 256), (0, 256)])
    lz.pintar(suelo, rampa(["#0e0a12", "#1a141e", "#261e2a", "#342a38"], np.clip((lz.y - 166) / 90 + (lz.ruido(8, 2, semilla=203) - 0.5) * 0.3, 0, 1)))
    # las setas que brillan, por todas partes (más grandes delante)
    def seta(x, y, r, col):
        lz.sumar_luz(lz.desenfocar(lz.circulo(x, y - r * 1.4, r * 2.2), r * 1.6), col[2], 0.35)
        lz.sombrear(lz.trazo([(x, y), (x + r * 0.15, y - r * 1.4)], r * 0.32, r * 0.24), ["#5a5262", "#8a8094", "#c8c0d0", "#eee8f4"], r * 0.2, LUZ)
        som = lz.elipse(x + r * 0.15, y - r * 1.5, r, r * 0.55)
        lz.sombrear(som, col, r * 0.4, LUZ)
        lz.sumar_luz(som, col[3], 0.25)
    VERDE = ["#0e3a3a", "#1e7a6e", "#5ae0c0", "#c8fff0"]
    VIOLETA = ["#2a1040", "#6a2a9a", "#b070e0", "#f0d8ff"]
    for k in range(70):
        x = rng.random() * W
        y = 150 + rng.random() * 100
        if 210 < x < 400 and y > 180:
            continue
        seta(x, y, 2 + (y - 150) / 100 * 7 * rng.uniform(0.6, 1.2), VERDE if k % 3 else VIOLETA)
    # en el centro: el montón de hojas caídas y el corro de setas pequeñas que se las come; de la tierra brotan hojitas
    YM = 222
    for k in range(40):
        hx, hy = 300 + rng.normal(0, 30), YM + rng.normal(0, 6)
        lz.sombrear(lz.elipse(hx, hy, 4.5, 2.2, rng.uniform(0, 180)),
                    [["#3a1e0a", "#7a4a1a", "#c47a2a", "#e0a050"], ["#3a2a0a", "#6a5a1a", "#a08a30", "#c8b050"]][k % 2], 1.2, LUZ)
    for k in range(12):
        a = k / 12 * 2 * np.pi
        seta(300 + np.cos(a) * 54, YM + 6 + np.sin(a) * 12, 5.0, VERDE if k % 2 else VIOLETA)
    for (bx, by) in ((292, YM - 4), (308, YM - 2), (300, YM - 8)):
        lz.pintar(lz.trazo([(bx, by + 4), (bx, by - 4)], 0.8), "#3e9a35")
        lz.pintar(lz.elipse(bx - 2.5, by - 4, 2.6, 1.2, 25), "#8fe06a")
        lz.pintar(lz.elipse(bx + 2.5, by - 5, 2.6, 1.2, -25), "#6fcf4f")
    lz.sumar_luz(lz.desenfocar(lz.circulo(300, YM - 6, 10), 8), "#8fe06a", 0.4)
    # Maisha, de rodillas a la izquierda (mirando las setas), y Kimya, flotando a la derecha
    lz.sumar_luz(lz.desenfocar(lz.elipse(300, 200, 150, 60), 30), "#5ae0c0", 0.18)
    lz.pintar(lz.desenfocar(lz.elipse(226, YM + 8, 22, 3), 2), "#050308", 0.5)
    ci.maisha_luz(lz, 226, YM + 6, e=1.9)
    _kimya_pie(lz, 380, 196, e=1.8)
    # esporas flotando
    motas = np.zeros((lz.H, lz.W))
    for k in range(80):
        motas = np.maximum(motas, lz.circulo(rng.random() * W, 60 + rng.random() * 150, 0.4 + rng.random() * 0.4))
    lz.sumar_luz(motas, "#e6d0ff", 0.7)
    lz.pintar(np.ones((lz.H, lz.W)), "#3e8a86", 0.06)
    ci.marco_recuerdo(lz, color="#4a4058", semilla=204)
    return lz


def _solo_reflejo_luz(lz, otro, eje_y, agua, fuerza):
    """Solo el reflejo (del revés, bajo eje_y) de algo hecho de luz: se suma al agua; arriba no se pinta nada."""
    eje = int(eje_y * lz.s)
    img_r = np.zeros_like(otro.img)
    alto = min(eje, lz.H - eje)
    img_r[eje:eje + alto] = otro.img[eje - alto:eje][::-1]
    img_r = img_r * (agua * fuerza)[..., None]
    lz.img = 1 - (1 - lz.img) * (1 - np.clip(img_r, 0, 1))


def eco_lago():
    """El noveno eco, la voz que no suena: lo que importa solo está en el reflejo del lago quieto."""
    lz = Lienzo(W, H, semilla=300)
    rng = np.random.default_rng(301)
    HZ = 96
    # la noche: azul hondo, sin luna (la luz de esta noche está en el agua)
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#04060e", "#0a1020", "#121a32", "#1c2644", "#26304e"], desde=0, hasta=HZ))
    ci.estrellas(lz, 90, HZ - 20, semilla=302, color="#dce6f4")
    # la orilla lejana: colinas negras y, al norte, una colina vacía (donde el agua dice que está el Primer Árbol)
    colinas = ci.mascara_bajo(lz, ci.linea_horizonte(lz, HZ - 10, 9, 60, 303))
    lz.pintar(colinas * (lz.y < HZ + 1), "#070a14")
    colina = lz.poligono([(330, HZ + 1), (380, HZ - 22), (430, HZ - 30), (480, HZ - 20), (530, HZ + 1)])
    lz.pintar(colina, "#080b16")
    # el lago, liso como un espejo: refleja el cielo del revés
    agua = (lz.y >= HZ).astype(float)
    filas = lz.img.shape[0]
    eje = int(HZ * lz.s)
    origen = np.clip(2 * eje - 1 - np.arange(filas), 0, filas - 1)
    lz.pintar(agua, lz.img[origen] * 0.85)
    # el agua de cerca refleja lo más alto del cielo, lo más oscuro (y así no se repite la fila de arriba)
    lz.pintar(agua * np.clip((lz.y - 150) / 40, 0, 1), "#04060e")
    vetas = (estirar_h(lz, lz.ruido(1.5, 2, semilla=304), 50) > 0.76) * agua
    lz.pintar(vetas, "#a8c8e0", 0.08)
    # SOLO EN EL REFLEJO: el Primer Árbol en su colina (su halo, recortado en suave)...
    a_lz = Lienzo(W, H, semilla=305)
    _primer_arbol(a_lz, 430, HZ - 8, 56)
    # (el halo del árbol llena todo el cielo: fuera la luz débil, y lo que queda se apaga en suave hacia los lados)
    cerca = np.clip(1.15 - np.hypot((a_lz.x - 430) / 120, (a_lz.y - (HZ - 36)) / 48), 0, 1) ** 1.5
    a_lz.img = np.clip((a_lz.img - 0.16) / 0.84, 0, 1) * cerca[..., None]
    _solo_reflejo_luz(lz, a_lz, HZ, agua, 0.8)
    # ...nueve espirales de luz en arco sobre él (ocho verdes y la del Silencio, plateada, en el centro)...
    e_lz = Lienzo(W, H, semilla=306)
    for k in range(9):
        a = math.pi * (0.12 + 0.76 * k / 8)
        cx, cy = 430 - math.cos(a) * 130, HZ - 22 - math.sin(a) * 52
        plateada = k == 4
        r0 = 6.5 if plateada else 4.5
        pts = [(cx + math.cos(t) * r0 * t / 12, cy + math.sin(t) * r0 * t / 12 * 0.9) for t in np.linspace(0.5, 12, 40)]
        espiral = lz.trazo(pts, 0.9)
        e_lz.sumar_luz(lz.desenfocar(lz.circulo(cx, cy, r0 + 2), 4), "#e8f0ff" if plateada else "#9ff0c0", 0.35)
        e_lz.sumar_luz(espiral, "#ffffff" if plateada else "#c8ffd8", 0.95)
    _solo_reflejo_luz(lz, e_lz, HZ, agua, 0.85)
    # ...y Kimya, de pie sobre el agua (arriba no hay nadie)
    kx, ky = 310, 170
    k_lz = Lienzo(W, H, semilla=307)
    _kimya_pie(k_lz, kx, ky, e=2.0)
    _solo_reflejo_luz(lz, k_lz, ky + 3, agua, 0.75)
    lz.sumar_luz(lz.desenfocar(lz.elipse(kx, ky + 3, 22, 3), 4) * agua, "#c0d0e8", 0.45)
    # la orilla de la isla, abajo a la izquierda, con dos menhires del círculo
    YO = 210
    isla = lz.poligono([(0, 176), (80, 186), (160, 198), (214, YO - 2), (236, YO + 4), (210, YO + 14), (120, 236), (60, 256), (0, 256)])
    lz.sombrear(isla, ["#070c0c", "#0e1814", "#16221c", "#203024", "#2a3c2c"], 6, (0.5, -0.8, 0.5),
                textura=lz.ruido(1.5, 2, semilla=308), fuerza_tex=0.35)
    filo = np.clip(isla - np.roll(isla, int(2 * lz.s), axis=0), 0, 1)
    lz.sumar_luz(filo, "#8aa8c8", 0.3)
    for (x, y, alto) in ((36, 190, 26), (92, 200, 20)):
        menhir = lz.poligono([(x - 6, y), (x - 5, y - alto), (x, y - alto - 3), (x + 5, y - alto + 1), (x + 6, y)])
        lz.sombrear(menhir, ["#0c0e16", "#1a1e2a", "#2c3242", "#40485a"], 4, (0.5, -0.8, 0.5))
    hierba = np.zeros((lz.H, lz.W))
    for k in range(120):
        x = rng.random() * 220
        yb = 178 + x * 0.14 + rng.random() * 40
        hierba = np.maximum(hierba, lz.trazo([(x, yb), (x + (rng.random() - 0.5) * 3, yb - 3 - rng.random() * 4)], 0.5))
    lz.pintar(hierba * isla, "#2a4030", 0.9)
    # Maisha, sentada al borde, mirando el agua (su luz se refleja)
    m_lz = Lienzo(W, H, semilla=309)
    ci.maisha_luz(m_lz, 200, YO, e=1.5)
    _pegar_con_reflejo(lz, m_lz, YO + 2, agua, 0.55)
    lz.sumar_luz(lz.desenfocar(lz.elipse(200, YO + 18, 10, 14), 7) * agua, "#ffe0a0", 0.3)
    # unas pocas motas plateadas sobre el agua
    motas = np.zeros((lz.H, lz.W))
    for k in range(30):
        motas = np.maximum(motas, lz.circulo(230 + rng.random() * 330, HZ + 8 + rng.random() * 120, 0.4 + rng.random() * 0.4))
    lz.sumar_luz(motas * agua, "#e8f0ff", 0.7)
    lz.pintar(np.ones((lz.H, lz.W)), "#3e8a86", 0.05)
    ci.marco_recuerdo(lz, color="#40506a", semilla=310)
    return lz


def _cima_ruinas(lz, rng, nevada=True):
    """El fondo de las dos ilustraciones de las Ruinas: el cielo, la cima nevada, las columnas rotas y el corro de piedras."""
    HZ = 150
    suelo = lz.poligono([(0, 168), (120, 158), (300, 154), (480, 158), (600, 166), (600, 256), (0, 256)])
    lz.sombrear(suelo, ["#3a4458", "#5a6680", "#8a96ae", "#b8c2d4", "#dde4ee"], 30, (0.4, -0.9, 0.6),
                textura=lz.ruido(28, 2, semilla=411), fuerza_tex=0.0)
    ondas = (estirar_h(lz, lz.ruido(0.7, 2, semilla=412), 22) > 0.62) * suelo
    lz.pintar(ondas, "#e6ecf4", 0.25)
    for (x, alto, roto) in ((70, 70, 12), (130, 54, 30), (470, 64, 18), (536, 76, 8), (30, 40, 40)):
        col = lz.poligono([(x - 9, 168), (x - 8, 168 - alto), (x - 3, 168 - alto - roto * 0.2), (x + 6, 168 - alto + 4), (x + 9, 168)])
        lz.sombrear(col, ["#4a4840", "#77736a", "#a8a499", "#d4d0c6", "#ece9e1"], 5, (-0.6, -0.7, 0.5),
                    textura=((lz.y % 12) < 1.2) * 1.0 + lz.ruido(1, 2, semilla=x) * 0.3, fuerza_tex=0.3)
        tapa = col * (1 - np.roll(col, int(2 * lz.s), axis=0))
        lz.pintar(tapa, "#eef2f8")
    return HZ


def _corro(lz, encendidas):
    for k in range(9):
        a = np.pi * (0.08 + k * 0.105)
        x = 300 - np.cos(a) * 210
        y = 176 + np.sin(a) * 34
        piedra = lz.poligono([(x - 5, y), (x - 4, y - 18), (x, y - 21), (x + 4, y - 17), (x + 5, y)])
        lz.sombrear(piedra, ["#2a2c34", "#4a4e5a", "#6e7482", "#9aa0ac"], 3, (-0.6, -0.7, 0.5))
        if encendidas:
            col = "#c8d4f0" if k == 4 else "#8ff0d0"
            pts = [(x + np.cos(t) * t * 0.35, y - 11 + np.sin(t) * t * 0.33) for t in np.linspace(0.3, 9, 22)]
            lz.sumar_luz(lz.trazo(pts, 0.5), col, 0.9)
            lz.sumar_luz(lz.desenfocar(lz.circulo(x, y - 11, 6), 4), col, 0.35)


def _arbol_gris(lz, x, y, alto, rng):
    tronco = lz.poligono([(x - 26, y), (x - 17, y - alto * 0.35), (x - 13, y - alto * 0.6), (x + 13, y - alto * 0.6), (x + 18, y - alto * 0.35), (x + 27, y)])
    ramas = np.zeros((lz.H, lz.W))
    def rama(a, ang, largo, g, n):
        nonlocal ramas
        b = (a[0] + np.cos(ang) * largo, a[1] + np.sin(ang) * largo)
        m = (a[0] + np.cos(ang) * largo * 0.5 + rng.normal(0, 3), a[1] + np.sin(ang) * largo * 0.5)
        ramas = np.maximum(ramas, lz.trazo(lz.curva(a, m, b, n=20), g, g * 0.6))
        if n < 3:
            for d in (-0.5, 0.45):
                rama(b, ang + d + rng.normal(0, 0.15), largo * 0.68, g * 0.6, n + 1)
    for ang in (-2.5, -1.9, -1.25, -0.65):
        rama((x, y - alto * 0.58), ang, alto * 0.32, 5.0, 0)
    madera = np.clip(tronco + ramas, 0, 1)
    lz.sombrear(madera, ["#1e1e22", "#36363c", "#55555c", "#77777e", "#9a9aa0"], 7, (-0.6, -0.7, 0.5),
                textura=lz.ruido(1.5, 3, semilla=421), fuerza_tex=0.35)
    for pts in ([(x - 18, y), (x - 12, y - alto * 0.3), (x - 14, y - alto * 0.55)], [(x + 20, y), (x + 13, y - alto * 0.35), (x + 15, y - alto * 0.58)]):
        v = lz.trazo(lz.curva(*pts, n=30), 1.0) * madera
        lz.pintar(v, "#8a4ad0")
        lz.sumar_luz(lz.desenfocar(v, 2), "#b080ff", 0.4)
    nieve = madera * (1 - np.roll(madera, int(2 * lz.s), axis=0))
    lz.pintar(nieve, "#dfe6f0")
    for k in range(30):
        hx, hy = x + rng.normal(0, 70), y - alto * 0.8 - abs(rng.normal(0, 26))
        lz.pintar(lz.elipse(hx, hy, 2.2, 1.1, rng.uniform(0, 180)), "#6e6044")


def _mauti_piedra(lz, x, y, e=1.0):
    figura = np.maximum.reduce([lz.elipse(x, y - 15 * e, 9 * e, 8.5 * e), lz.elipse(x, y - 4.5 * e, 5 * e, 5 * e),
                                lz.trazo([(x - 2.2 * e, y - 1 * e), (x - 2.4 * e, y + 2 * e)], 2.2 * e),
                                lz.trazo([(x + 2.2 * e, y - 1 * e), (x + 2.4 * e, y + 2 * e)], 2.2 * e)])
    lz.sombrear(figura, ["#2a2c30", "#4a4e54", "#6e7378", "#989da2"], 4 * e, (-0.6, -0.7, 0.5))
    lz.pintar(lz.trazo([(x - 3 * e, y - 12 * e), (x + 1 * e, y - 6 * e), (x - 1 * e, y)], 0.5 * e) * figura, "#8a4ad0")
    hoja = lz.elipse(x + 1.5 * e, y - 29 * e, 3.6 * e, 1.7 * e, -35)
    lz.pintar(np.maximum(lz.trazo([(x, y - 23 * e), (x - 1 * e, y - 27.5 * e)], 0.9 * e), hoja), "#7a7064")
    lz.pintar(figura * (1 - np.roll(figura, int(1.5 * lz.s), axis=0)), "#dfe6f0")


def ruinas_mauti():
    lz = Lienzo(W, H, semilla=400)
    rng = np.random.default_rng(401)
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#0c1020", "#1c2238", "#3a3c58", "#6a5a78", "#a07a88"], desde=0, hasta=170))
    ci.estrellas(lz, 50, 90, semilla=402, color="#dce6f4")
    _cima_ruinas(lz, rng)
    _arbol_gris(lz, 300, 166, 150, rng)
    _corro(lz, False)
    # Mauti, de piedra, sentada al pie del tronco (un poco a la izquierda, para que se vea entera)
    lz.sumar_luz(lz.desenfocar(lz.circulo(262, 160, 16), 10), "#b8a8e0", 0.18)
    _mauti_piedra(lz, 262, 178, e=1.5)
    # Maisha, de espaldas en primer término, mirando arriba
    ci.maisha_luz(lz, 330, 246, e=2.2)
    motas = np.zeros((lz.H, lz.W))
    for k in range(160):
        motas = np.maximum(motas, lz.circulo(rng.random() * W, rng.random() * H, 0.4 + rng.random() * 0.6))
    lz.sumar_luz(motas, "#eef2f8", 0.7)
    lz.pintar(np.clip((np.hypot((lz.x - 300) / 330, (lz.y - 140) / 170) - 0.75) * 2.0, 0, 1), "#05070c", 0.55)
    return lz


def arbol_libre():
    lz = Lienzo(W, H, semilla=500)
    rng = np.random.default_rng(501)
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#2a2a50", "#5a4a70", "#b07a70", "#f0b878", "#ffe0a0"], desde=0, hasta=170))
    _cima_ruinas(lz, rng)
    _primer_arbol(lz, 300, 166, 150)
    _corro(lz, True)
    # Mauti, libre, y Maisha con la semilla
    _mauti_luz(lz, 268, 222, e=1.7, mira=1)
    ci.maisha_luz(lz, 330, 224, e=1.7)
    semilla = lz.elipse(318, 206, 3.2, 4.0, 20)
    lz.sumar_luz(lz.desenfocar(semilla, 6), "#ffe39a", 0.8)
    lz.pintar(semilla, "#f0cc60")
    hojas = np.zeros((lz.H, lz.W))
    for k in range(90):
        hojas = np.maximum(hojas, lz.elipse(rng.random() * W, rng.random() * 200, 1.6, 0.8, rng.uniform(0, 180)))
    lz.sumar_luz(hojas, "#ffe39a", 0.9)
    ci.marco_recuerdo(lz, color="#f0d8a0", semilla=502) if False else None
    lz.pintar(np.clip((np.hypot((lz.x - 300) / 330, (lz.y - 140) / 170) - 0.8) * 2.0, 0, 1), "#140a06", 0.45)
    return lz


PIEZAS = {"22_ruinas_mauti": ruinas_mauti, "23_arbol_libre": arbol_libre, "21_eco_lago": eco_lago, "20_eco_cueva": eco_cueva, "19_eco_travesia": eco_travesia, "18_eco_orilla": eco_orilla, "17_kimya_lago": kimya_lago, "16_eco_canada": eco_canada, "12_eco_puente": eco_puente, "13_eco_pasarelas": eco_pasarelas, "14_eco_cobrizo": eco_cobrizo, "15_eco_surcos": eco_surcos}
