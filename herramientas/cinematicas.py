"""Las ilustraciones de la historia de Maisha, pintadas con mucho detalle (herramientas/pintor.py).

    python3 herramientas/cinematicas.py            → las pinta todas en arte/historia/
    python3 herramientas/cinematicas.py 4_giza     → solo una
"""
import os
import sys
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import desplazar, iluminar, Lienzo, rampa, gris, hex2, mezcla, bolas, humo, relieve_bolas, iluminar_relieve, ruido_torcido, humo_volumen, R, RAIZ  # noqa: E402

SALIDA = os.path.join(RAIZ, "arte", "historia")
W, H = 600, 256

# rampas de material (de sombra a luz), con las sombras hacia el frío y las luces hacia el cálido
HIERBA = ["#152218", "#1d2e18", "#2f4a22", "#3f5a2f", "#5d7a3c", "#7c9a4c", "#a8b866", "#cfd08a"]
FOLLAJE = ["#0f1c14", "#152814", "#24401f", "#355029", "#5d793e", "#8aa152", "#b4c070", "#dcd994"]
COBRE = ["#2a1c14", "#3d3214", "#704f25", "#a37036", "#c68756", "#e2a978", "#f3cf9e"]
TIERRA = ["#1a1210", "#2b1e17", "#53392d", "#7c5843", "#a57559", "#c79a78", "#e0c09c"]
MADERA = ["#140c0a", "#251812", "#492e23", "#6d4534", "#905c45", "#b07a5c", "#d2a07c"]
PIEDRA = ["#18191a", "#292c25", "#525649", "#7a806d", "#a0a596", "#c4c7b8", "#e2e2d4"]
PELO = ["#1b100b", "#2e1a10", "#4f2d1a", "#73432a", "#96603b", "#b7814f", "#d6a76c", "#ecd09a"]
TEJADO = ["#2a0d10", "#5a1820", "#8f2532", "#b03a44", "#d5525e", "#e98378", "#f4b39a"]
HUMO_GIZA = ["#05030a", "#0d0716", "#170c26", "#221035", "#2f1547", "#3e1b5c", "#55257a", "#7a3aa3", "#a466cf"]
LUZ_GIZA = ["#7a2fa0", "#a24fd0", "#c27ce6", "#dcaaf2", "#f1d8fb", "#ffffff"]


# ---------------------------------------------------------------- piezas que se repiten
def linea_horizonte(lz, base, amplitud, escala, semilla, octavas=4):
    """Una silueta de montañas o colinas: devuelve la altura (y) para cada x."""
    rng = np.random.default_rng(semilla)
    x = np.arange(lz.W) / lz.s
    y = 0.45 * np.sin(x * (0.37 / escala) * 2 * np.pi + rng.random() * 6.28)
    amp, suma = 1.0, 0.45
    for o in range(octavas):
        f = (2.17 ** o) / escala * (0.92 + 0.16 * rng.random())
        y += amp * np.sin(x * f * 2 * np.pi + rng.random() * 6.28) * (0.6 + 0.4 * rng.random())
        suma += amp
        amp *= 0.52
    return base - amplitud * y / suma


def mascara_bajo(lz, linea):
    """Todo lo que queda por debajo de una línea de horizonte."""
    return np.clip((lz.y - linea[None, :]) * lz.s * 0.5 + 0.5, 0, 1)


def copa_racimos(lz, grupos, rampa_copa, luz=(-0.7, -0.6, 0.5), semilla=0, filo=None):
    """Una copa hecha de RACIMOS de hojas con volumen: cada grupo (x, y, radio) se pinta por separado, de atrás adelante,
    con su luz y su sombra, el borde hecho de hojitas y una sombra suave debajo (así se ven los volúmenes y no ruido).
    filo = (color, fuerza): la luz que roza el borde de cada racimo por el lado de la luz. Devuelve la máscara de la copa."""
    copa = np.zeros((lz.H, lz.W))
    for n, (gx, gy, r) in enumerate(sorted(grupos, key=lambda g: g[1])):
        forma = lz.elipse(gx, gy, r * 1.12, r * 0.84)
        hojitas = lz.desenfocar((lz.ruido(min(1.4, max(0.6, r * 0.07)), 2, semilla=semilla + n * 7) > 0.42).astype(float), 0.6) > 0.5
        borde = np.clip(lz.elipse(gx, gy, r * 1.3, r * 1.0) - forma, 0, 1) * hojitas
        racimo = np.clip(forma + borde, 0, 1)
        lz.sombrear(racimo, rampa_copa, r * 0.7, luz, textura=lz.ruido(max(1.0, r * 0.1), 2, semilla=semilla + n * 13), fuerza_tex=0.12)
        if filo:
            lado = np.clip(racimo - np.roll(np.roll(racimo, int(-luz[1] * 1.5 * lz.s), axis=0), int(-luz[0] * 1.5 * lz.s), axis=1), 0, 1)
            lz.pintar(lado, filo[0], filo[1])
        abajo = np.clip(racimo - np.roll(racimo, int(-1.4 * lz.s), axis=0), 0, 1) * (lz.y > gy)
        lz.pintar(abajo, rampa_copa[0], 0.2)
        copa = np.maximum(copa, racimo)
    return copa


def arbol(lz, x, y, alto, ancho, luz=(-0.7, -0.6, 0.5), rampa_copa=FOLLAJE, semilla=0, sombra=True, tronco_col=MADERA):
    """Un árbol de copa redonda hecha de racimos de hojas con volumen, con tronco y sombra en el suelo."""
    rng = np.random.default_rng(semilla)
    if sombra:
        lz.pintar(lz.desenfocar(lz.elipse(x + ancho * 0.25, y + 1, ancho * 0.6, ancho * 0.14), 1.0), "#0c140c", 0.45)
    tronco = lz.poligono([(x - ancho * 0.07, y), (x - ancho * 0.045, y - alto * 0.55), (x + ancho * 0.045, y - alto * 0.55), (x + ancho * 0.08, y)])
    lz.sombrear(tronco, tronco_col, ancho * 0.08, luz, textura=lz.ruido(2, 2), fuerza_tex=0.2)
    cy = y - alto * 0.62
    grupos = [(x, cy, ancho * 0.3)]
    for _ in range(9):
        a_ = rng.random() * 2 * np.pi
        d_ = np.sqrt(rng.random())
        grupos.append((x + np.cos(a_) * ancho * 0.32 * d_, cy + np.sin(a_) * alto * 0.2 * d_ - alto * 0.04, ancho * (0.16 + rng.random() * 0.1)))
    return copa_racimos(lz, grupos, rampa_copa, luz, semilla=semilla, filo=(rampa_copa[-1], 0.22))


def arbol_antiguo(lz, x, y, alto, ancho, luz=(-0.7, -0.6, 0.5), rampa_copa=FOLLAJE, semilla=0, sombra=True, tronco_col=MADERA):
    """Un árbol de copa redonda hecha de varios grupos de hojas, con tronco y sombra en el suelo."""
    rng = np.random.default_rng(semilla)
    if sombra:
        lz.pintar(lz.desenfocar(lz.elipse(x + ancho * 0.25, y + 1, ancho * 0.6, ancho * 0.14), 1.0), "#0c140c", 0.45)
    tronco = lz.poligono([(x - ancho * 0.07, y), (x - ancho * 0.045, y - alto * 0.55), (x + ancho * 0.045, y - alto * 0.55), (x + ancho * 0.08, y)])
    lz.sombrear(tronco, tronco_col, ancho * 0.08, luz, textura=lz.ruido(2, 2), fuerza_tex=0.3)
    copa = np.zeros((lz.H, lz.W))
    cy = y - alto * 0.62
    grupos = [(0, 0, 0.5)] + [((rng.random() - 0.5) * 0.8, (rng.random() - 0.6) * 0.6, 0.28 + rng.random() * 0.14) for _ in range(6)]
    for gx, gy, gr in grupos:
        copa = np.maximum(copa, lz.circulo(x + gx * ancho, cy + gy * alto * 0.6, gr * ancho))
    hojas = lz.ruido(max(1.5, ancho * 0.08), 3)
    borde = (hojas > 0.42).astype(float)
    copa_d = np.clip(copa * (0.75 + borde * 0.5), 0, 1)
    copa_d = (copa_d > 0.6).astype(float)
    lz.sombrear(copa_d, rampa_copa, ancho * 0.35, luz, textura=hojas, fuerza_tex=0.45)
    return copa_d


def castor_silueta(lz, x, y, escala, mira=1, cola=True):
    """Silueta de castor sentado (de lado), para escenas a contraluz."""
    s = escala
    m = lz.elipse(x, y - 9 * s, 7 * s, 9 * s, -8 * mira)
    m = np.maximum(m, lz.circulo(x + 3 * s * mira, y - 19 * s, 5.2 * s))
    m = np.maximum(m, lz.elipse(x + 7.5 * s * mira, y - 18 * s, 3.2 * s, 2.4 * s))
    m = np.maximum(m, lz.circulo(x + 1 * s * mira, y - 23.5 * s, 1.5 * s))
    if cola:
        m = np.maximum(m, lz.elipse(x - 8 * s * mira, y - 1 * s, 6 * s, 2 * s, -10 * mira))
    return np.clip(m, 0, 1)


def estrellas(lz, n, zona_y, semilla=3, color="#e8f0dc"):
    rng = np.random.default_rng(semilla)
    m = np.zeros((lz.H, lz.W))
    for _ in range(n):
        x, y = rng.random() * lz.w, rng.random() * zona_y
        r = 0.35 + rng.random() ** 4 * 0.9
        m = np.maximum(m, lz.circulo(x, y, r) * (0.4 + rng.random() * 0.6))
    lz.sumar_luz(m, color, 1.0)
    lz.brillo(m, color, 1.5, 0.6)


# ---------------------------------------------------------------- los castores
CREMA = ["#3b2416", "#6d4a30", "#a3794f", "#c99d6b", "#e3c391", "#f3e0b8"]
COLA = ["#120b0a", "#1f1512", "#33241d", "#4a362b", "#64503f", "#7f6a55"]


def pelo(lz, semilla=0, largo=9):
    """Textura de pelo: ruido fino estirado hacia abajo."""
    n = lz.ruido(1.2, 2, semilla=semilla).astype(np.float32)
    k = np.zeros((largo * lz.s // 2 * 2 + 1, 1), np.float32)
    k[:, 0] = 1.0 / k.shape[0]
    n = cv2.filter2D(n, -1, k)
    return (n - n.min()) / (n.max() - n.min() + 1e-6)


def castor(lz, x, y, e=1.0, mira=1, luz=(-0.7, -0.6, 0.5), recorte=None, recorte_dir=(1, 0),
           sombrero=False, gafas=False, delantal=False, chal=False, barba=False, cria=False, sentado=True,
           brazo_alto=False, rampa_pelo=PELO, sem=0, mirada=(1, 0), crema=None):
    """Un castor pintado con detalle, de tres cuartos, mirando a la derecha (mira=1) o a la izquierda (-1).
    (x, y) es el suelo bajo sus pies. e = tamaño (1 → unos 46 px de alto). Devuelve la máscara del cuerpo."""
    m = mira
    def X(dx):
        return x + dx * e * m
    def Y(dy):
        return y - dy * e
    cab = 1.18 if cria else 1.0      # las crías tienen la cabeza más grande
    crema = CREMA if crema is None else crema
    tex = pelo(lz, sem)
    kw = dict(luz=(luz[0] * m if False else luz[0], luz[1], luz[2]), textura=tex, fuerza_tex=0.32)
    if recorte:
        kw.update(recorte=recorte, recorte_dir=recorte_dir)
    total = np.zeros((lz.H, lz.W))

    # sombra en el suelo
    lz.pintar(lz.desenfocar(lz.elipse(X(-2), y, 19 * e, 3.6 * e), 1.2), "#0a0608", 0.5)
    # la cola: una pala plana con escamas, detrás
    cola = lz.elipse(X(-17), Y(2.5), 12 * e, 4 * e, -12 * m)
    escamas = np.clip(1 - np.minimum(np.abs(np.sin((lz.x + lz.y) / (1.6 * e))), np.abs(np.sin((lz.x - lz.y) / (1.6 * e)))) * 4, 0, 1)
    lz.sombrear(cola, COLA, 3 * e, kw["luz"], textura=1 - escamas * 0.8, fuerza_tex=0.5)
    total = np.maximum(total, cola)
    # el cuerpo: forma de pera
    cuerpo = np.maximum(lz.elipse(X(0), Y(13), 13.5 * e, 14 * e), lz.elipse(X(2), Y(25), 10 * e, 10 * e))
    lz.sombrear(cuerpo, rampa_pelo, 10 * e, **kw)
    # la barriga, más clara
    barriga = lz.elipse(X(4.5), Y(15), 7.5 * e, 10.5 * e) * cuerpo
    lz.sombrear(barriga, crema[1:], 6 * e, kw["luz"], textura=tex, fuerza_tex=0.25)
    total = np.maximum(total, cuerpo)
    if delantal:
        d = lz.poligono([(X(-3), Y(28)), (X(10), Y(28)), (X(13), Y(4)), (X(-6), Y(4))]) * cuerpo
        lz.sombrear(d, ["#152814", "#24401f", "#355029", "#5d793e", "#8aa152"], 5 * e, kw["luz"], textura=lz.ruido(1.0, 2), fuerza_tex=0.15)
        bolsillo = lz.poligono([(X(0), Y(16)), (X(8), Y(16)), (X(8.5), Y(10)), (X(-0.5), Y(10))]) * d
        lz.pintar(bolsillo, "#24401f", 0.9)
        lz.pintar(lz.trazo([(X(0), Y(16)), (X(8), Y(16))], 0.7 * e), "#5d793e")
    if chal:
        c_ = lz.poligono([(X(-10), Y(31)), (X(12), Y(31)), (X(14), Y(22)), (X(5), Y(13)), (X(-8), Y(20))])
        punto = (np.sin(lz.x * 2.2 / e) * np.sin(lz.y * 2.2 / e) > 0.2).astype(float)
        lz.sombrear(c_, ["#2a0d10", "#5a1820", "#8f2532", "#b03a44", "#d5525e", "#e98378"], 5 * e, kw["luz"], textura=punto, fuerza_tex=0.22)
        franja = lz.trazo([(X(-8), Y(20.5)), (X(5), Y(14)), (X(13.5), Y(22.5))], 1.6 * e) * c_
        lz.pintar(franja, "#e2a978", 0.85)
        total = np.maximum(total, c_)
    # los pies
    for dx in (-4, 7):
        pie = lz.elipse(X(dx), Y(1.5), 5 * e, 2.6 * e)
        lz.sombrear(pie, COLA[1:], 2 * e, kw["luz"])
        for k in (-1.5, 0, 1.5):
            lz.pintar(lz.trazo([(X(dx + 3 + k * 0.4), Y(0.6 + k)), (X(dx + 4.6), Y(1 + k * 0.6))], 0.5 * e), "#120b0a", 0.7)
    # el brazo de delante
    if brazo_alto:
        brazo = lz.trazo([(X(6), Y(27)), (X(13), Y(23)), (X(16), Y(31))], 4.6 * e, 3.6 * e)
        mano = lz.circulo(X(16.2), Y(31.5), 2.8 * e)
    else:
        brazo = lz.trazo([(X(6), Y(27)), (X(11), Y(21)), (X(10), Y(15))], 4.8 * e, 3.6 * e)
        mano = lz.circulo(X(9.5), Y(14.5), 2.8 * e)
    lz.sombrear(brazo, rampa_pelo, 2.4 * e, **kw)
    lz.sombrear(mano, COLA[1:], 2 * e, kw["luz"])
    total = np.maximum(total, np.maximum(brazo, mano))

    # la cabeza
    hx, hy = X(4 * cab), Y(36 + (cab - 1) * 4)
    r = 10.5 * e * cab
    cabeza = np.maximum(lz.circulo(hx, hy, r), lz.elipse(hx + 2 * e * m * cab, hy + 4 * e * cab, r * 0.92, r * 0.72))
    oreja = lz.circulo(hx - 6.5 * e * m * cab, hy - 8 * e * cab, 3.2 * e * cab)
    lz.sombrear(oreja, rampa_pelo, 2 * e, **kw)
    lz.pintar(lz.circulo(hx - 6.2 * e * m * cab, hy - 7.6 * e * cab, 1.6 * e * cab) * oreja, "#2e1a10", 0.8)
    lz.sombrear(cabeza, rampa_pelo, 8 * e * cab, **kw)
    total = np.maximum(total, np.maximum(cabeza, oreja))
    # el hocico, abultado y claro
    hoc_x, hoc_y = hx + 7 * e * m * cab, hy + 4 * e * cab
    hocico = np.maximum(lz.elipse(hoc_x, hoc_y, 6.2 * e * cab, 4.6 * e * cab), lz.elipse(hoc_x - 3 * e * m * cab, hoc_y + 1.5 * e * cab, 5 * e * cab, 4 * e * cab))
    lz.sombrear(hocico, crema, 4 * e * cab, kw["luz"], textura=tex, fuerza_tex=0.15)
    # la nariz: negra, redondeada, con brillo
    nariz = lz.elipse(hoc_x + 3.6 * e * m * cab, hoc_y - 2.6 * e * cab, 2.6 * e * cab, 1.8 * e * cab)
    lz.sombrear(nariz, ["#050304", "#140c0c", "#2e2222", "#5a4a48"], 1.5 * e, kw["luz"])
    lz.pintar(lz.circulo(hoc_x + 3 * e * m * cab, hoc_y - 3.3 * e * cab, 0.6 * e * cab), "#c5c6c7", 0.9)
    # la boca y los dientes grandes de castor
    lz.pintar(lz.trazo([(hoc_x + 3.6 * e * m * cab, hoc_y - 1 * e * cab), (hoc_x + 3.2 * e * m * cab, hoc_y + 1 * e * cab)], 0.6 * e), "#3b2416", 0.9)
    dientes = lz.poligono([(hoc_x + 1.6 * e * m * cab, hoc_y + 1.2 * e * cab), (hoc_x + 4.6 * e * m * cab, hoc_y + 1.2 * e * cab),
                           (hoc_x + 4.4 * e * m * cab, hoc_y + 5 * e * cab), (hoc_x + 1.8 * e * m * cab, hoc_y + 5 * e * cab)])
    lz.sombrear(dientes, ["#8a7a58", "#d8cba6", "#f6efd8", "#fffdf4"], 1.2 * e, kw["luz"])
    lz.pintar(lz.trazo([(hoc_x + 3.1 * e * m * cab, hoc_y + 1.4 * e * cab), (hoc_x + 3.1 * e * m * cab, hoc_y + 4.8 * e * cab)], 0.4 * e) * dientes, "#8a7a58", 0.8)
    # bigotes
    for k in (-1, 0, 1):
        lz.pintar(lz.trazo(lz.curva((hoc_x + 1 * e * m * cab, hoc_y - 0.5 * e * cab + k), (hoc_x + 7 * e * m * cab, hoc_y - 1 * e * cab + k * 2),
                                    (hoc_x + 11 * e * m * cab, hoc_y + k * 3.4), n=12), 0.35 * e), "#f3e0b8", 0.55)
    if barba:
        b_ = lz.poligono([(hoc_x - 2 * e * m, hoc_y + 4 * e), (hoc_x + 3 * e * m, hoc_y + 4.5 * e), (hoc_x + 1 * e * m, hoc_y + 10 * e), (hoc_x - 1.5 * e * m, hoc_y + 8 * e)])
        lz.sombrear(b_, ["#8a8a8a", "#c5c6c7", "#eeeeea", "#ffffff"], 2 * e, kw["luz"], textura=tex, fuerza_tex=0.4)
    # el ojo: grande, oscuro y brillante (mirando hacia 'mirada')
    ox, oy = hx + 3.5 * e * m * cab, hy - 2 * e * cab
    lz.pintar(lz.elipse(ox, oy, 2.4 * e * cab, 2.8 * e * cab), "#2e1a10", 0.6)
    ojo = lz.elipse(ox + mirada[0] * 0.3 * e * m, oy + mirada[1] * 0.3 * e, 1.9 * e * cab, 2.3 * e * cab)
    lz.sombrear(ojo, ["#050304", "#120b0a", "#2b1e17"], 1.2 * e, kw["luz"])
    lz.pintar(lz.circulo(ox - 0.6 * e * m * cab + mirada[0] * 0.3 * e * m, oy - 0.9 * e * cab, 0.75 * e * cab), "#ffffff")
    lz.pintar(lz.circulo(ox + 0.7 * e * m * cab, oy + 0.9 * e * cab, 0.35 * e * cab), "#c5c6c7", 0.7)
    # cejas de pelo
    lz.pintar(lz.trazo([(ox - 2.4 * e * m, oy - 3.4 * e * cab), (ox + 1.8 * e * m, oy - 3.8 * e * cab)], 1.0 * e), "#4f2d1a", 0.6)
    if gafas:
        # dos cristales: el del ojo cercano y, más estrecho, el del ojo de detrás (junto al hocico)
        for dx_, ancho in ((0.0, 1.0), (5.2, 0.55)):
            cx_ = ox + dx_ * e * m * cab
            aro = np.clip(lz.elipse(cx_, oy, 3.4 * e * ancho, 3.4 * e) - lz.elipse(cx_, oy, 2.7 * e * ancho, 2.7 * e), 0, 1)
            lz.pintar(lz.elipse(cx_, oy, 2.8 * e * ancho, 2.8 * e), "#9fd0d0", 0.2)
            lz.sombrear(aro, ["#3d3f43", "#85878a", "#c5c6c7", "#ffffff"], 0.6 * e, kw["luz"])
            lz.pintar(lz.trazo([(cx_ - 1.4 * e * ancho, oy - 1.6 * e), (cx_ - 0.3 * e * ancho, oy - 2.4 * e)], 0.5 * e), "#ffffff", 0.7)
        lz.pintar(lz.trazo([(ox + 3.3 * e * m * cab, oy - 0.6 * e), (ox + 3.6 * e * m * cab, oy - 0.6 * e)], 0.6 * e), "#85878a")
        lz.pintar(lz.trazo([(ox - 3.4 * e * m, oy - 0.4 * e), (ox - 7.5 * e * m, oy - 1.4 * e)], 0.5 * e), "#85878a")
    if sombrero:
        sx, sy = hx - 0.5 * e * m, hy - 8.2 * e * cab
        ala = lz.elipse(sx, sy + 1.2 * e, 15 * e, 3.2 * e, -4 * m)
        copa = np.maximum(lz.elipse(sx, sy - 3 * e, 9 * e, 4.8 * e), lz.poligono([(sx - 8.6 * e, sy - 3 * e), (sx + 8.6 * e, sy - 3 * e), (sx + 8 * e, sy + 1 * e), (sx - 8 * e, sy + 1 * e)]))
        paja = (np.abs(np.sin(lz.x * 1.6 / e + lz.y * 0.4)) > 0.55).astype(float) * 0.6 + lz.ruido(0.8, 2) * 0.4
        straw = ["#3d2a10", "#704f25", "#a37036", "#d29a43", "#efc06a", "#f8dc96"]
        lz.sombrear(ala, straw, 2 * e, kw["luz"], textura=paja, fuerza_tex=0.35)
        lz.sombrear(copa, straw, 4 * e, kw["luz"], textura=paja, fuerza_tex=0.35)
        cinta = copa * np.clip(1 - np.abs(lz.y - (sy - 0.5 * e)) / (1.5 * e), 0, 1)
        lz.pintar((cinta > 0.4).astype(float), rampa(["#5a1820", "#b03a44", "#e98378"], lz.volumen(copa, 4 * e, kw["luz"])[0]))
        hoja = lz.elipse(sx + 4 * e * m, sy - 2 * e, 2.6 * e, 1.1 * e, -30 * m)
        lz.sombrear(hoja, ["#1f4a1a", "#3e9a35", "#6fcf4f", "#b8ef8e"], 1 * e, kw["luz"])
        total = np.maximum(total, np.maximum(ala, copa))
    return total


def ojo_giza(lz, ox, oy, largo, alto, ang, fuerza=1.0):
    """Un ojo de Giza: alargado, en punta, con la pupila como una rendija y un halo violeta."""
    ca, sa = np.cos(np.radians(ang)), np.sin(np.radians(ang))
    pts = []
    for k in range(40):
        t = k / 39 * 2 * np.pi
        ex = np.cos(t) * largo
        ey = np.sin(t) * alto * (abs(np.cos(t)) ** 0.15 if True else 1) * (1 - 0.35 * np.cos(t))
        pts.append((ox + ex * ca - ey * sa, oy + ex * sa + ey * ca))
    mo = lz.poligono(pts)
    lz.sumar_luz(lz.desenfocar(mo, largo * 0.9), "#a24fd0", 0.9 * fuerza)
    lz.sumar_luz(lz.desenfocar(mo, largo * 0.3), "#c27ce6", 0.8 * fuerza)
    dist = np.clip(np.hypot((lz.x - ox) / largo, (lz.y - oy) / (alto * 1.4)), 0, 1)
    lz.pintar(mo, rampa(["#ffffff", "#f1d8fb", "#dcaaf2", "#c27ce6", "#a24fd0"], dist))
    lz.pintar(lz.elipse(ox + ca * largo * 0.05, oy + sa * largo * 0.05, alto * 0.95, alto * 0.95), rampa(["#f1d8fb", "#c27ce6", "#7a2fa0"], dist * 1.5), 0.8 * mo.max())
    lz.pintar(lz.elipse(ox + ca * largo * 0.05, oy + sa * largo * 0.05, alto * 0.22, alto * 0.9, ang * 0.2) * mo, "#0d0716")
    lz.pintar(lz.circulo(ox - largo * 0.25, oy - alto * 0.35, alto * 0.18) * mo, "#ffffff")


# ---------------------------------------------------------------- 4. Llega Giza
def giza():
    """«Llegó Giza: una sombra sin forma que se bebe la vida de todo lo que toca.»
    A la izquierda, el valle aún verde bajo la tarde; a la derecha, una montaña de humo violeta con ojos
    que se traga el cielo y estira brazos de sombra. Lo que toca se queda gris. En primer plano, una
    familia de castores lo mira desde una loma."""
    lz = Lienzo(W, H, semilla=4)
    sol = (92, 58)

    # cielo de tarde, con nubes iluminadas
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#24395a", "#4a7a93", "#97c1bf", "#f1c27a", "#f8e1a6"], desde=-10, hasta=160))
    nubes = lz.ruido(60, 5, semilla=11)
    banda = np.exp(-((lz.y - 70) / 34) ** 2)
    nube = np.clip((nubes - 0.52) * 4.0, 0, 1) * banda
    luz_nube = np.clip(1 - np.hypot(lz.x - sol[0], lz.y - sol[1]) / 260, 0, 1)
    lz.pintar(nube, rampa(["#9c4b4a", "#e49a5c", "#f8e1a6", "#fff4d6"], luz_nube * 0.8 + nubes * 0.4), 0.85)
    disco = lz.circulo(*sol, 11)
    lz.sumar_luz(lz.desenfocar(disco, 30), "#f8e1a6", 0.8)
    lz.pintar(disco, rampa(["#fde27e", "#fff8d2"], np.clip(1 - np.hypot(lz.x - sol[0], lz.y - sol[1]) / 11, 0, 1)))

    # montañas lejanas (dos capas, azuladas por la distancia)
    for base, amp, col, sem in [(150, 26, "#6b9eab", 5), (158, 18, "#4a7a93", 6)]:
        m = mascara_bajo(lz, linea_horizonte(lz, base, amp, 260, sem))
        tex = lz.ruido(10, 3)
        lz.pintar(m, rampa([mezcla(col, "#16233a", 0.3), col, mezcla(col, "#f1c27a", 0.3)], tex * 0.6 + np.clip((lz.x - 0) / 600, 0, 1) * 0.0 + 0.2))

    # colinas del valle, con caminos y luz de tarde
    colinas = []
    for base, amp, sem, r in [(170, 12, 21, HIERBA[3:]), (186, 14, 22, HIERBA[2:7]), (204, 10, 23, HIERBA[1:6])]:
        linea = linea_horizonte(lz, base, amp, 220, sem)
        m = mascara_bajo(lz, linea)
        prof = np.clip((lz.y - linea[None, :]) / 30, 0, 1)
        tex = lz.ruido(6, 4)
        lz.pintar(m, rampa(r, np.clip(1 - prof * 0.7 + (tex - 0.5) * 0.4, 0, 1)))
        colinas.append(linea)

    # el río que baja serpenteando hacia nosotros
    t = np.linspace(0, 1, 60)
    rx = 240 + 40 * np.sin(t * 5.0) - 120 * t
    ry = 166 + 90 * t ** 1.4
    rio = lz.trazo(np.stack([rx, ry], 1), 1.5, 16)
    lz.pintar(rio, rampa(["#335777", "#6b9eab", "#c4ddd0"], lz.ruido(3, 2) * 0.6 + 0.3))
    lz.sumar_luz(rio * np.clip(1 - np.abs(lz.x - sol[0]) / 200, 0, 1), "#f8e1a6", 0.35)

    # casitas con tejado rojo junto al río
    for i, (cx, cy, e) in enumerate([(150, 186, 1.0), (178, 182, 0.8), (205, 190, 1.1), (300, 175, 0.7), (128, 196, 1.2)]):
        pared = lz.poligono([(cx - 7 * e, cy), (cx - 7 * e, cy - 7 * e), (cx + 7 * e, cy - 7 * e), (cx + 7 * e, cy)])
        lz.sombrear(pared, ["#53392d", "#a57559", "#e0c09c"], 3 * e, (-0.8, -0.3, 0.5))
        techo = lz.poligono([(cx - 9 * e, cy - 6.5 * e), (cx, cy - 14 * e), (cx + 9 * e, cy - 6.5 * e)])
        lz.sombrear(techo, TEJADO, 3 * e, (-0.8, -0.5, 0.4))
        lz.pintar(lz.poligono([(cx - 2 * e, cy), (cx - 2 * e, cy - 4 * e), (cx + 1.5 * e, cy - 4 * e), (cx + 1.5 * e, cy)]), "#2b1e17")
        ventana = lz.poligono([(cx + 3.5 * e, cy - 4.5 * e), (cx + 3.5 * e, cy - 2 * e), (cx + 5.5 * e, cy - 2 * e), (cx + 5.5 * e, cy - 4.5 * e)])
        lz.pintar(ventana, "#f9b947")

    # árboles por el valle (más pequeños y azulados cuanto más lejos)
    rng = np.random.default_rng(8)
    for i in range(26):
        x = rng.random() * 600
        y = 164 + rng.random() * 50
        e = 0.4 + (y - 164) / 50 * 0.9
        arbol(lz, x, y, 22 * e, 14 * e, semilla=i, sombra=e > 0.7)

    # --- Giza: una ola de humo que se levanta a la derecha y se inclina sobre el valle
    rng = np.random.default_rng(77)
    # Giza: humo con volumen. Primero su forma (cabeza, hombros y brazos que se estiran)…
    forma = np.maximum.reduce([
        np.exp(-(((lz.x - 512) / 92) ** 2 + ((lz.y - 100) / 84) ** 2)),
        np.exp(-(((lz.x - 555) / 115) ** 2)) * np.clip((lz.y - 60) / 60, 0, 1),
    ])
    brazos = np.zeros((lz.H, lz.W))
    for (p0, p1, p2, p3, g) in [((440, 120), (380, 96), (320, 164), (236, 150), 30),
                                ((450, 176), (380, 210), (320, 214), (262, 198), 26),
                                ((480, 214), (430, 248), (380, 232), (322, 244), 28)]:
        brazos = np.maximum(brazos, lz.trazo(lz.curva(p0, p1, p2, p3, 80), g, 3))
    brazos_f = lz.desenfocar(brazos, 4)
    # …y luego el humo que la rellena, con remolinos
    r1 = ruido_torcido(lz, 30, 6, semilla=31, torcer=30)
    r2 = ruido_torcido(lz, 9, 4, semilla=32, torcer=10)
    densidad = np.clip(forma * 1.7, 0, 1.3) * (0.5 + r1 * 0.6) + (r2 - 0.5) * 0.25 * np.clip(forma * 2, 0, 1)
    densidad = np.maximum(densidad, np.clip((forma - 0.55) * 4, 0, 1))
    densidad = np.maximum(densidad, brazos_f * (0.48 + r1 * 0.5 + (r2 - 0.5) * 0.35))
    forma = np.maximum(forma, brazos_f)
    alfa, luz_h = humo_volumen(lz, densidad, luz=(-1.0, -0.55), paso=2.0, umbral=(0.34, 0.56))
    mascara = alfa
    # lo que Giza ya se ha bebido: gris bajo la sombra, con un frente irregular
    consumido = np.clip(lz.desenfocar(mascara, 16) * 1.8 + np.clip((lz.x - 400) / 80, 0, 1), 0, 1)
    consumido *= np.clip(0.75 + lz.ruido(9, 3, semilla=40) * 0.5, 0, 1)
    lz.img = gris(lz.img, consumido * 0.95)
    frente = np.clip(1 - np.abs(consumido - 0.5) * 6, 0, 1) * (lz.y > 165)
    lz.sumar_luz(frente * lz.ruido(2, 2), "#7a2fa0", 0.55)
    # resplandor violeta detrás
    lz.sumar_luz(lz.desenfocar(mascara, 14), "#4d1a6b", 0.8)
    # el humo: casi negro por dentro; la tarde enciende los bordes que miran al sol y lo de dentro brilla violeta
    hondo = np.clip(lz.distancia(mascara, 0.5) / 40, 0, 1)
    grandes = lz.desenfocar(ruido_torcido(lz, 40, 4, semilla=35, torcer=40), 3)
    _, luz_i = humo_volumen(lz, grandes * 0.8 + r1 * 0.2, luz=(-1.0, -0.55), paso=5.0, umbral=(0, 1))
    luz_i = np.clip((luz_i - 0.5) * 2.2 + 0.5, 0, 1)
    v = np.maximum(luz_h * (1 - hondo * 0.6), luz_i * 0.7 * np.clip(hondo * 2, 0, 1))
    col = rampa(["#05030a", "#0d0716", "#170c26", "#2f1547", "#55257a"], np.clip(v * 0.9, 0, 1))
    sol_k = np.clip((luz_h - 0.62) * 3, 0, 1) * np.clip(1 - hondo * 2.5, 0, 1) * np.clip(1 - (lz.y - 10) / 240, 0.15, 1)
    col = col * (1 - sol_k[..., None]) + rampa(["#6a3446", "#c96d4f", "#f1c27a"], sol_k) * sol_k[..., None]
    dentro = np.clip((0.4 - luz_h) * 2.5, 0, 1) * np.clip(1 - np.abs(r2 - 0.5) * 5, 0, 1) * np.clip(hondo * 3, 0, 1)
    col = col * (1 - dentro[..., None] * 0.6) + hex2("#7a2fa0") * dentro[..., None] * 0.6
    lz.pintar(mascara, col)
    cuerpo = mascara
    # contorno: luz de tarde por la izquierda y violeta por abajo
    dist_c = lz.distancia(cuerpo, 0.4)
    gy, gx = np.gradient(lz.desenfocar(dist_c, 1.5))
    nn = np.hypot(gx, gy) + 1e-6
    izq = np.clip(gx / nn, 0, 1) * np.clip(1 - dist_c / 2.5, 0, 1) * (cuerpo > 0.3)
    abajo = np.clip(-gy / nn, 0, 1) * np.clip(1 - dist_c / 3.0, 0, 1) * (cuerpo > 0.3)
    lz.pintar(izq * np.clip(1 - (lz.y - 30) / 220, 0.15, 1), "#e49a5c", 0.9)
    lz.pintar(abajo, "#a24fd0", 0.7)

    # los ojos: dos grandes, alargados y en punta, y tres pequeños medio escondidos
    # una mirada de enfado: cejas de humo que bajan hacia el centro
    for (bx0, by0, bx1, by1) in [(428, 72, 492, 92), (586, 66, 522, 86)]:
        ceja = lz.trazo(lz.curva((bx0, by0), ((bx0 + bx1) / 2, by0 - 2), (bx1, by1), n=20), 9, 6)
        lz.pintar(lz.desenfocar(ceja, 0.6), "#0d0716")
        lz.pintar(np.clip(ceja - lz.desenfocar(ceja, 1.5) * 0.9, 0, 1) * (lz.y < (by0 + by1) / 2), "#7a3aa3", 0.6)
    ojo_giza(lz, 462, 98, 26, 8, 16)
    ojo_giza(lz, 548, 92, 26, 8, -16)
    for (ox, oy, l, a, g) in [(592, 168, 7, 2.4, 14), (402, 40, 7, 2.2, -18), (520, 36, 6, 2.0, 8)]:
        ojo_giza(lz, ox, oy, l, a, g, 0.6)

    # resplandor violeta sobre todo lo cercano
    lz.sumar_luz(lz.desenfocar(cuerpo, 34) * (1 - cuerpo), "#4d1a6b", 0.6)

    # pájaros que huyen hacia el sol
    rng = np.random.default_rng(9)
    for i in range(14):
        bx, by = 120 + rng.random() * 200, 30 + rng.random() * 80
        e = 0.6 + rng.random() * 0.8
        ala = lz.trazo([(bx - 3 * e, by - 1.5 * e), (bx, by), (bx + 3 * e, by - 2 * e)], 0.9, 0.6)
        lz.pintar(ala, "#2b2c30", 0.9)

    # ceniza violeta en el aire
    motas = np.zeros((lz.H, lz.W))
    for i in range(140):
        mx, my = 260 + rng.random() * 340, rng.random() * 256
        motas = np.maximum(motas, lz.circulo(mx, my, 0.4 + rng.random() * 0.6) * rng.random())
    lz.sumar_luz(motas, "#c27ce6", 1.0)

    # primer plano: una loma oscura con hierba alta y una familia de castores que mira
    loma_l = 236 - 26 * np.exp(-((np.arange(lz.W) / lz.s - 70) / 120) ** 2) + 3 * np.sin(np.arange(lz.W) / lz.s / 9)
    loma = mascara_bajo(lz, loma_l) * np.clip((260 - lz.x) / 30, 0, 1)
    lz.pintar(loma, rampa(["#0b100b", "#152218", "#1d2e18"], lz.ruido(4, 3) * 0.7))
    hierba = np.zeros((lz.H, lz.W))
    for i in range(260):
        hx = rng.random() * 250
        hy = loma_l[int(min(lz.W - 1, hx * lz.s))] + 2 + rng.random() * 3
        largo = 5 + rng.random() * 9
        inc = (rng.random() - 0.3) * 5
        hierba = np.maximum(hierba, lz.trazo([(hx, hy), (hx + inc * 0.4, hy - largo * 0.6), (hx + inc, hy - largo)], 1.2, 0.3))
    lz.pintar(hierba, "#152218")
    # castores a contraluz, con el filo violeta de Giza
    # la familia Shamba a contraluz: el sol detrás y el violeta de Giza en la cara
    OSCURO = ["#0d0a0a", "#160f0d", "#21150f", "#2e1d14", "#3d2819"]
    for (cx_, e_, sem_, cria_, somb_) in [(92, 1.05, 41, False, False), (122, 1.2, 42, False, True), (146, 0.8, 43, True, False)]:
        castor(lz, cx_, loma_l[int(cx_ * lz.s)] + 4, e_, 1, luz=(0.7, -0.3, 0.35), recorte=("#c27ce6", 0.9), recorte_dir=(1, -0.1),
               rampa_pelo=OSCURO, sem=sem_, cria=cria_, sombrero=somb_, mirada=(1, -1),
               crema=["#160f0d", "#2e1d14", "#4a3322", "#5e4430", "#6d5038", "#7c5d42"])

    # viñeta suave para centrar la mirada
    vin = np.clip(np.hypot((lz.x - 300) / 360, (lz.y - 128) / 190) - 0.6, 0, 1)
    lz.pintar(vin, "#07060d", 0.6)
    return lz


# ---------------------------------------------------------------- piezas de interior
def pared_troncos(lz, y0, y1, alto=22, luz_x=90, semilla=0):
    """Pared de troncos horizontales, con corteza y juntas de barro y musgo."""
    rng = np.random.default_rng(semilla)
    corteza = lz.ruido(3, 3, semilla=semilla).astype(np.float32)
    k = np.ones((1, 15), np.float32) / 15
    corteza = cv2.filter2D(corteza, -1, k)
    corteza = (corteza - corteza.min()) / (np.ptp(corteza) + 1e-6)
    y = y0
    while y < y1:
        h = alto * (0.85 + rng.random() * 0.3)
        tronco = np.clip((lz.y - y) * lz.s, 0, 1) * np.clip((y + h - lz.y) * lz.s, 0, 1)
        t_ = np.clip((lz.y - y) / h, 0, 1)
        redondo = np.sin(t_ * np.pi) ** 0.6 * (1 - t_ * 0.35)
        v = redondo * 0.75 + (corteza - 0.5) * 0.35
        lz.pintar(tronco, rampa(MADERA, np.clip(v, 0, 1)))
        # vetas y nudos
        for _ in range(3):
            nx_, ny_ = rng.random() * lz.w, y + h * (0.3 + rng.random() * 0.4)
            nudo = np.clip(lz.elipse(nx_, ny_, 4 + rng.random() * 3, 1.6) - lz.elipse(nx_, ny_, 2.4, 0.8), 0, 1)
            lz.pintar(nudo * tronco, "#251812", 0.7)
        junta = np.clip(1 - np.abs(lz.y - (y + h)) * lz.s / 2.2, 0, 1)
        lz.pintar(junta, "#140c0a", 0.95)
        musgo = junta * (lz.ruido(2, 2) > 0.62)
        lz.pintar(lz.desenfocar(musgo, 0.5), "#355029", 0.7)
        y += h + 1.2


def piedras(lz, region, tam=9.0, semilla=2, rampa_p=PIEDRA, luz=(-0.5, -0.7, 0.5), mortero="#1b1714"):
    """Muro de piedras redondeadas dentro de 'region' (máscara)."""
    rng = np.random.default_rng(semilla)
    ys, xs = np.nonzero(region > 0.5)
    if len(xs) == 0:
        return
    x0, x1, y0, y1 = xs.min() / lz.s, xs.max() / lz.s, ys.min() / lz.s, ys.max() / lz.s
    lz.pintar(region, mortero)
    tex_p = lz.ruido(1.5, 2, semilla=semilla + 11)
    grupos = [np.zeros((lz.H, lz.W)) for _ in range(4)]
    fila = 0
    y = y0
    while y < y1 + tam:
        x = x0 - (tam * 0.5 if fila % 2 else 0)
        col = 0
        while x < x1 + tam:
            w_ = tam * (0.8 + rng.random() * 0.6)
            h_ = tam * (0.6 + rng.random() * 0.25)
            p = lz.elipse(x + w_ / 2, y + h_ / 2, w_ / 2 - 0.6, h_ / 2 - 0.6, (rng.random() - 0.5) * 20) * region
            if p.max() > 0.3:
                g_idx = (fila % 2) * 2 + (col % 2)
                grupos[g_idx] = np.maximum(grupos[g_idx], p)
            x += w_
            col += 1
        y += tam * 0.72
        fila += 1
    for g in grupos:
        if g.max() > 0.3:
            lz.sombrear(g, rampa_p, tam * 0.25, luz, textura=tex_p, fuerza_tex=0.3)


def lengua(lz, x, base, ancho, alto, curva, fase=0.0):
    """Una lengua de fuego: gota que se afina hacia arriba y se tuerce."""
    izq, der = [], []
    for k in range(30):
        tt = k / 29
        w_ = ancho * (1 - tt) ** 0.85 * min(1.0, (tt + 0.12) * 3.2)
        xx = x + curva * tt ** 1.6 + np.sin(tt * 5 + fase) * ancho * 0.25 * tt
        izq.append((xx - w_, base - alto * tt))
        der.append((xx + w_, base - alto * tt))
    return lz.poligono(izq + der[::-1])


def llamas(lz, cx, base, ancho, alto, semilla=0, n=7):
    """Un fuego: lenguas rojas por fuera, amarillas dentro y casi blancas en el corazón."""
    rng = np.random.default_rng(semilla)
    fuego = np.zeros((lz.H, lz.W))
    capas = [(1.0, 1.0, ["#6e200c", "#a8380f", "#d45a17"]), (0.62, 0.72, ["#d45a17", "#ef8a26", "#f9b947"]),
             (0.32, 0.42, ["#f9b947", "#fde27e", "#fff8d2"])]
    lenguas = []
    for i in range(n):
        dx = (rng.random() - 0.5) * ancho * 0.9
        h = alto * (0.45 + rng.random() * 0.55) * (1 - abs(dx) / ancho * 0.9)
        w_ = ancho * (0.12 + rng.random() * 0.08)
        lenguas.append((cx + dx, h, w_, (rng.random() - 0.5) * w_ * 3, rng.random() * 6))
    lenguas.sort(key=lambda l: -l[1])
    for (escala_w, escala_h, cols) in capas:
        for (lx, h, w_, cur, fase) in lenguas:
            m = lengua(lz, lx, base, w_ * escala_w, h * escala_h, cur * escala_h, fase)
            v = np.clip((base - lz.y) / max(h * escala_h, 1), 0, 1)
            lz.pintar(m, rampa(cols, np.clip(1 - v * 0.8, 0, 1)))
            fuego = np.maximum(fuego, m)
    # chispas que suben
    ch = np.zeros((lz.H, lz.W))
    for i in range(16):
        ch = np.maximum(ch, lz.circulo(cx + (rng.random() - 0.5) * ancho, base - alto * (0.8 + rng.random() * 0.8), 0.4 + rng.random() * 0.5))
    lz.sumar_luz(ch, "#fde27e", 1.0)
    return fuego


def brillo_cetro(lz, x, y, r=4.0, fuerza=1.0):
    lz.sumar_luz(lz.desenfocar(lz.circulo(x, y, r), r * 6), "#f9b947", 0.7 * fuerza)
    lz.sumar_luz(lz.desenfocar(lz.circulo(x, y, r), r * 2), "#fde27e", 0.8 * fuerza)


def cetro(lz, x, y_pie, y_cabeza, e=1.0, luz=(-0.6, -0.6, 0.5), brilla=1.0):
    """El Cetro de Raíz: rama de madera con una enredadera y, arriba, el corazón de ámbar con un brote."""
    palo = lz.trazo(lz.curva((x, y_pie), (x - 2 * e, (y_pie + y_cabeza) / 2), (x + 1 * e, y_cabeza + 6 * e), n=30), 3.2 * e, 2.4 * e)
    lz.sombrear(palo, MADERA, 1.6 * e, luz, textura=lz.ruido(1, 2), fuerza_tex=0.3)
    # la enredadera que sube en espiral
    pts = [(x + np.sin(k * 0.55) * 2.2 * e - k * 0.03 * e, y_pie - (y_pie - y_cabeza - 6 * e) * k / 60) for k in range(61)]
    lz.pintar(lz.trazo(pts, 0.9 * e), "#355029")
    for k in range(4, 60, 9):
        hx_, hy_ = pts[k]
        lz.sombrear(lz.elipse(hx_ + 1.5 * e, hy_, 1.8 * e, 0.9 * e, -30), ["#1f4a1a", "#3e9a35", "#6fcf4f"], 0.8 * e, luz)
    # garras de raíz que abrazan el corazón
    for ang in (-50, 0, 50):
        a_ = np.radians(ang - 90)
        lz.pintar(lz.trazo(lz.curva((x + 1 * e, y_cabeza + 5 * e), (x + np.cos(a_) * 5 * e, y_cabeza + 2 * e), (x + np.cos(a_) * 3.5 * e, y_cabeza - 3 * e), n=10), 1.4 * e, 0.6 * e), "#492e23")
    corazon = lz.circulo(x + 1 * e, y_cabeza, 3.8 * e)
    lz.sombrear(corazon, ["#704f25", "#c96d17", "#ef8a26", "#f9b947", "#fde27e", "#fff8d2"], 2.4 * e, luz)
    brillo_cetro(lz, x + 1 * e, y_cabeza, 3.0 * e, brilla)
    # el brote de arriba
    lz.pintar(lz.trazo(lz.curva((x + 1 * e, y_cabeza - 3 * e), (x + 1.5 * e, y_cabeza - 6 * e), (x + 3 * e, y_cabeza - 8 * e), n=8), 0.8 * e), "#3e9a35")
    lz.sombrear(lz.elipse(x + 4.4 * e, y_cabeza - 8.6 * e, 2.2 * e, 1.1 * e, -25), ["#1f4a1a", "#3e9a35", "#6fcf4f", "#b8ef8e"], 0.8 * e, luz)


def maisha_luz(lz, x, y, e=1.0, alfa=1.0):
    """Maisha hecha de luz (para visiones y leyendas): cabeza grande, cuerpo pequeño y el brote."""
    figura = np.maximum.reduce([lz.elipse(x, y - 15 * e, 9 * e, 8.5 * e), lz.elipse(x, y - 4.5 * e, 5 * e, 5 * e),
                                lz.trazo([(x - 2.2 * e, y - 1 * e), (x - 2.4 * e, y + 2 * e)], 2.2 * e),
                                lz.trazo([(x + 2.2 * e, y - 1 * e), (x + 2.4 * e, y + 2 * e)], 2.2 * e)])
    lz.sumar_luz(lz.desenfocar(figura, 6 * e), "#f9b947", 0.8 * alfa)
    lz.pintar(figura, rampa(["#e8b860", "#ffe08a", "#fff3c4"], lz.volumen(figura, 6 * e, (-0.5, -0.7, 0.6))[0]), alfa)
    brote = lz.trazo(lz.curva((x, y - 23 * e), (x + 0.5 * e, y - 27 * e), (x + 1 * e, y - 29 * e), n=8), 1.0 * e)
    hojas_ = np.maximum(lz.elipse(x - 2.6 * e, y - 29.5 * e, 3 * e, 1.4 * e, 25), lz.elipse(x + 3.6 * e, y - 30.5 * e, 3 * e, 1.4 * e, -25))
    lz.pintar(np.maximum(brote, hojas_), "#6fcf4f", alfa)
    corazon = lz.circulo(x + 0.5 * e, y - 5 * e, 1.4 * e)
    lz.sumar_luz(lz.desenfocar(corazon, 2 * e), "#e98378", 0.9 * alfa)
    lz.pintar(lz.elipse(x + 3.5 * e, y - 15 * e, 1.0 * e, 1.6 * e), "#3b2416", 0.85 * alfa)
    return figura


# ---------------------------------------------------------------- 3. La leyenda
def leyenda():
    """«Mi abuela guardaba el Cetro de Raíz. Por las noches nos contaba la leyenda…»
    Noche en la casa de los Shamba: la abuela, con su chal y sus gafas, sostiene el cetro junto al fuego.
    Dos crías (una es el pequeño Shamba, con su primer sombrero) la escuchan en la alfombra. Del corazón
    del cetro sube una luz dorada donde se ve la leyenda: un espíritu pequeño con un brote de luz."""
    lz = Lienzo(W, H, semilla=3)
    fuego_xy = (92, 170)

    pared_troncos(lz, -6, 190, semilla=5)
    # la ventana: noche azul con luna y estrellas
    vx0, vy0, vx1, vy1 = 474, 34, 556, 112
    cristal = lz.poligono([(vx0, vy0), (vx1, vy0), (vx1, vy1), (vx0, vy1)])
    lz.pintar(cristal, lz.gradiente(["#0d0c19", "#1e2038", "#3b4063"], desde=vy0, hasta=vy1))
    rng = np.random.default_rng(4)
    est = np.zeros((lz.H, lz.W))
    for _ in range(26):
        est = np.maximum(est, lz.circulo(vx0 + rng.random() * (vx1 - vx0), vy0 + rng.random() * (vy1 - vy0) * 0.7, 0.4 + rng.random() * 0.5))
    lz.sumar_luz(est * cristal, "#e8f0dc", 1.0)
    luna = lz.circulo(538, 54, 8)
    lz.sumar_luz(lz.desenfocar(luna, 8) * cristal, "#7680a0", 0.8)
    lz.pintar(luna * cristal, rampa(["#97c1bf", "#e8f0dc"], lz.volumen(luna, 5, (-0.6, -0.4, 0.6))[0]))
    lz.pintar(lz.circulo(542, 52, 7) * luna, "#1e2038", 0.0)
    # copos de árboles secos fuera (silueta)
    rama = lz.trazo(lz.curva((vx0, 100), (500, 86), (520, 70), n=20), 2.4, 0.6)
    lz.pintar(rama * cristal, "#0d0c19")
    marco = np.clip(lz.poligono([(vx0 - 6, vy0 - 6), (vx1 + 6, vy0 - 6), (vx1 + 6, vy1 + 8), (vx0 - 6, vy1 + 8)]) - cristal, 0, 1)
    marco = np.maximum(marco, lz.trazo([((vx0 + vx1) / 2, vy0), ((vx0 + vx1) / 2, vy1)], 3) * cristal)
    marco = np.maximum(marco, lz.trazo([(vx0, (vy0 + vy1) / 2), (vx1, (vy0 + vy1) / 2)], 3) * cristal)
    lz.sombrear(marco, MADERA, 2.5, (-0.7, -0.5, 0.5))

    # el suelo de tablas, en perspectiva
    suelo = np.clip((lz.y - 188) * lz.s, 0, 1)
    vpx, vpy = 330, 60
    ang = np.arctan2(lz.y - vpy, lz.x - vpx)
    tablas = (np.sin(ang * 46) * 0.5 + 0.5)
    veta = lz.ruido(2, 3)
    lz.pintar(suelo, rampa(MADERA[1:6], np.clip(0.25 + tablas * 0.25 + (veta - 0.5) * 0.4 + (lz.y - 188) / 120, 0, 1)))
    lz.pintar(suelo * np.clip(1 - np.abs(np.sin(ang * 46)) * 9, 0, 1), "#140c0a", 0.8)
    lz.pintar(np.clip(1 - np.abs(lz.y - 189) * lz.s / 2, 0, 1), "#140c0a")
    # la luz de luna que entra por la ventana y cae en el suelo
    rayo = lz.poligono([(vx0, vy1), (vx1, vy1), (vx1 - 10, 250), (vx0 - 70, 250)])
    lz.sumar_luz(lz.desenfocar(rayo, 6) * np.clip((lz.y - vy1) / 40, 0, 1), "#3b4063", 0.35)

    # la alfombra trenzada
    alfombra = lz.elipse(372, 226, 156, 24)
    dist_a = np.hypot((lz.x - 372) / 156, (lz.y - 226) / 24)
    bandas = (np.floor(dist_a * 9) % 3)
    trenza = (np.sin(lz.x * 1.4 + dist_a * 40) > 0).astype(float)
    col_a = rampa(["#5a1820", "#8f2532", "#b03a44"], np.clip(0.4 + trenza * 0.3, 0, 1))
    col_b = rampa(["#704f25", "#c68756", "#e2a978"], np.clip(0.4 + trenza * 0.3, 0, 1))
    col_c = rampa(["#24401f", "#355029", "#5d793e"], np.clip(0.4 + trenza * 0.3, 0, 1))
    col = np.where((bandas == 0)[..., None], col_a, np.where((bandas == 1)[..., None], col_b, col_c))
    lz.pintar(alfombra, col)

    # la chimenea de piedra con su repisa
    chim = lz.poligono([(14, 196), (14, 100), (170, 100), (170, 196)])
    piedras(lz, chim, tam=10, semilla=7)
    boca = lz.poligono([(44, 196), (44, 142)] + [(92 + np.cos(a) * 48, 142 - np.sin(a) * 26) for a in np.linspace(np.pi, 0, 20)] + [(140, 142), (140, 196)])
    lz.pintar(boca, lz.gradiente(["#1a0a06", "#2e1208", "#140c0a"], desde=116, hasta=196))
    repisa = lz.poligono([(6, 92), (178, 92), (176, 102), (8, 102)])
    lz.sombrear(repisa, MADERA, 3, (-0.6, -0.8, 0.5), textura=lz.ruido(2, 2), fuerza_tex=0.3)
    # cosas en la repisa: dos tarros, una vela y un ramito seco
    for (tx, th, tc) in [(30, 16, COBRE), (48, 11, ["#152814", "#24401f", "#5d793e", "#a8b866"])]:
        tarro = lz.elipse(tx, 92 - th / 2, 6, th / 2)
        lz.sombrear(tarro, tc, 4, (-0.6, -0.5, 0.6))
        lz.pintar(lz.poligono([(tx - 4, 92 - th - 1), (tx + 4, 92 - th - 1), (tx + 3.5, 92 - th + 2), (tx - 3.5, 92 - th + 2)]), "#7c5843")
    vela = lz.poligono([(150, 92), (150, 78), (156, 78), (156, 92)])
    lz.sombrear(vela, ["#a3794f", "#e3c391", "#f3e0b8"], 2, (-0.8, -0.3, 0.5))
    llama_v = lz.elipse(153, 74, 1.6, 3.4)
    lz.pintar(llama_v, "#fde27e")
    lz.sumar_luz(lz.desenfocar(llama_v, 8), "#ef8a26", 0.6)
    # el fuego con sus troncos
    for (a0, a1) in [((58, 192), (124, 184)), ((62, 184), (122, 192))]:
        tr = lz.trazo([a0, a1], 7)
        lz.sombrear(tr, MADERA[:5], 3, (0, -1, 0.5))
    fuego = llamas(lz, fuego_xy[0], 190, 44, 46, semilla=3, n=9)
    brasas = (lz.ruido(1.2, 2) > 0.7) * lz.elipse(92, 192, 40, 5)
    lz.sumar_luz(brasas, "#ef8a26", 0.9)


    # la mecedora (respaldo detrás de la abuela)
    for k in range(5):
        bx = 236 + k * 6
        barra = lz.trazo(lz.curva((bx, 210), (bx - 4, 168), (bx - 2 + k, 120 + abs(k - 2) * 2), n=16), 2.6)
        lz.sombrear(barra, MADERA, 1.3, (-0.8, -0.4, 0.5))
    travesano = lz.trazo(lz.curva((228, 122), (248, 114), (268, 124), n=16), 4)
    lz.sombrear(travesano, MADERA, 2, (-0.8, -0.4, 0.5))
    # la abuela con su chal y sus gafas, con el cetro en alto
    castor(lz, 266, 214, 2.05, 1, chal=True, gafas=True, brazo_alto=True, sem=11,
           luz=(-0.9, -0.3, 0.45), recorte=("#535a80", 0.6), recorte_dir=(1, -0.2))
    # el balancín y el brazo de la mecedora delante
    balancin = lz.trazo(lz.curva((206, 212), (262, 226), (318, 210), n=30), 3.4)
    lz.sombrear(balancin, MADERA, 1.7, (-0.8, -0.5, 0.5))
    brazo_m = lz.trazo([(222, 176), (294, 178)], 3.2)
    lz.sombrear(brazo_m, MADERA, 1.6, (-0.8, -0.4, 0.5))
    cetro(lz, 300, 222, 116, e=1.7, luz=(-0.9, -0.3, 0.45))
    # la mano que agarra el cetro (delante del palo)
    mano = lz.elipse(299, 149, 4.4, 4.6)
    lz.sombrear(mano, COLA[1:], 2.4, (-0.9, -0.3, 0.45))
    for k in (-1.6, 0, 1.6):
        lz.pintar(lz.trazo([(297, 149 + k), (302, 149 + k)], 0.6), "#120b0a", 0.6)

    # la leyenda: una luz dorada que sube del cetro y, dentro, un espíritu con un brote
    cx_v, cy_v = 388, 74
    camino = lz.curva((302, 110), (320, 70), (cx_v - 30, cy_v + 10), n=40)
    rng = np.random.default_rng(21)
    chispas = np.zeros((lz.H, lz.W))
    for (px_, py_) in camino[::2]:
        chispas = np.maximum(chispas, lz.circulo(px_ + (rng.random() - 0.5) * 8, py_ + (rng.random() - 0.5) * 8, 0.5 + rng.random() * 0.9))
    lz.sumar_luz(lz.desenfocar(chispas, 2), "#f9b947", 0.7)
    lz.sumar_luz(chispas, "#fff8d2", 0.9)
    burbuja = lz.circulo(cx_v, cy_v, 44)
    humo_dorado = lz.ruido(8, 4, semilla=22)
    d_b = np.hypot(lz.x - cx_v, lz.y - cy_v) / 44
    # un disco de luz con el borde deshilachado
    borde_b = np.clip(1 - np.abs(d_b - 0.95 + (humo_dorado - 0.5) * 0.25) * 9, 0, 1)
    dentro_b = np.clip((1 - d_b) * 4 + (humo_dorado - 0.5) * 0.6, 0, 1)
    lz.pintar(dentro_b, rampa(["#3a2238", "#6a3446", "#9c4b4a", "#c96d4f"], np.clip(1 - d_b + humo_dorado * 0.3, 0, 1)), 0.75)
    # dentro: el mundo gris, con el árbol viejo que empieza a reverdecer donde llega la luz
    for (hx_, hy_, hr_, col_) in [(cx_v - 20, cy_v + 40, 40, "#525458"), (cx_v + 26, cy_v + 44, 36, "#3d3f43")]:
        lz.pintar(lz.circulo(hx_, hy_, hr_) * dentro_b, col_, 0.9)
    ax, ay = cx_v - 25, cy_v + 12
    arb = lz.trazo(lz.curva((ax, ay), (ax - 1.5, ay - 9), (ax - 1, ay - 18), n=16), 2.8, 1.4)
    for (p1, p2, g_) in [((ax - 4, ay + 1), (ax - 9, ay + 3), 1.4), ((ax + 3, ay + 1), (ax + 8, ay + 2), 1.4),
                         ((ax - 1, ay - 13), (ax - 10, ay - 22), 1.4), ((ax - 1, ay - 15), (ax + 8, ay - 23), 1.3),
                         ((ax - 4, ay - 17), (ax - 3, ay - 26), 1.1)]:
        arb = np.maximum(arb, lz.trazo(lz.curva((ax - 1, p1[1]), p1, p2, n=12), g_, g_ * 0.45))
    lz.sombrear(arb * dentro_b, ["#1b1c1f", "#2b2c30", "#525458", "#85878a"], 1.5, (0.8, -0.4, 0.5))
    brotes_v = (lz.elipse(ax + 6, ay - 22, 4.5, 3.0) + lz.elipse(ax - 2, ay - 25, 4.0, 2.6)) * dentro_b
    lz.sombrear( np.clip(brotes_v, 0, 1), ["#24401f", "#3e9a35", "#6fcf4f", "#b8ef8e"], 2.0, (0.7, -0.5, 0.5))
    lz.sumar_luz(borde_b, "#f9b947", 0.8)
    lz.sumar_luz(lz.desenfocar(borde_b, 3), "#ef8a26", 0.6)
    rayos_l = lz.rayos(lz.circulo(cx_v, cy_v - 4, 9), (cx_v, cy_v - 4), largo=0.965, pasos=34)
    lz.sumar_luz(rayos_l * 2.4 * dentro_b, "#fde27e", 0.7)
    # el color vuelve donde toca su luz: hierba verde a sus pies
    pie_verde = lz.elipse(cx_v, cy_v + 22, 22, 5) * dentro_b
    lz.pintar(lz.desenfocar(pie_verde, 1.5), "#5d793e", 0.85)
    maisha_luz(lz, cx_v, cy_v + 20, 1.2, alfa=0.97)

    # las dos crías en la alfombra, mirando a la abuela (una es el pequeño Shamba)
    castor(lz, 412, 236, 1.32, -1, cria=True, sem=12, luz=(-0.9, -0.4, 0.45), recorte=("#535a80", 0.7), recorte_dir=(1, -0.3), mirada=(1, -1))
    castor(lz, 458, 244, 1.18, -1, cria=True, sombrero=True, sem=13, luz=(-0.9, -0.4, 0.45), recorte=("#535a80", 0.7), recorte_dir=(1, -0.3), mirada=(1, -1))

    # la luz del fuego sobre toda la habitación (cálida, cae con la distancia); lo que brilla, brilla igual
    d_f = np.hypot(lz.x - fuego_xy[0], (lz.y - fuego_xy[1]) * 1.3)
    luz_f = np.clip(1 - d_f / 420, 0, 1) ** 1.5
    propia = np.clip(lz.desenfocar(fuego, 1) + lz.desenfocar(burbuja, 2) * 0.8, 0, 1)[..., None]
    luz_total = 0.34 + 1.0 * luz_f[..., None] * hex2("#f1c27a") + lz.desenfocar(lz.circulo(302, 116, 6), 30)[..., None] * hex2("#f9b947") * 1.5
    base_img = lz.img.copy()
    lz.img = base_img * (1 - propia) * np.clip(luz_total, 0, 1.6) + base_img * propia
    lz.img = np.clip(lz.img, 0, 1)
    lz.sumar_luz(lz.desenfocar(fuego, 22), "#d45a17", 0.55)
    lz.sumar_luz(lz.desenfocar(fuego, 6), "#f9b947", 0.5)
    brillo_cetro(lz, 302, 116, 5, 0.8)

    # viñeta
    vin = np.clip(np.hypot((lz.x - 300) / 360, (lz.y - 140) / 200) - 0.55, 0, 1)
    lz.pintar(vin, "#07060d", 0.75)
    return lz


# ---------------------------------------------------------------- paisaje: piezas
def cumulos(lz, nubes, luz=(-1, -0.4), colores=("#97c1bf", "#c4ddd0", "#e8f0dc", "#fff4d6"), semilla=60, alfa=1.0, suave=0.0):
    """Nubes de algodón con volumen. nubes = [(x, y, ancho, alto), ...]"""
    forma = np.zeros((lz.H, lz.W))
    for (x, y, w_, h_) in nubes:
        base_plana = np.clip((y + h_ * 0.4 - lz.y) / 4, 0, 1)
        forma = np.maximum(forma, np.exp(-(((lz.x - x) / w_) ** 2 + ((lz.y - y) / h_) ** 2)) * base_plana)
    r1 = ruido_torcido(lz, 14, 5, semilla=semilla, torcer=10)
    dens = np.clip(forma * 1.6, 0, 1.2) * (0.45 + r1 * 0.7)
    if suave:
        dens = lz.desenfocar(dens, suave)
    alfa_n, luz_n = humo_volumen(lz, dens, luz=luz, paso=2.0 + suave, umbral=(0.42, 0.62))
    if suave:
        luz_n = lz.desenfocar(luz_n, suave * 0.6)
    lz.pintar(alfa_n, rampa(list(colores), luz_n), alfa)
    return alfa_n


def campos(lz, y0, y1, semilla=0, colores=None):
    """Parcelas de cultivo en perspectiva: pequeñas y apagadas lejos, grandes y vivas cerca, con setos."""
    rng = np.random.default_rng(semilla)
    colores = colores or [HIERBA[4:7], ["#a37036", "#c68756", "#e2a978"], ["#5d7a3c", "#8aa152", "#b4c070"],
                          ["#9c7a2a", "#c9a046", "#e8c56a"], HIERBA[3:6], HIERBA[3:6]]
    m = np.zeros((lz.H, lz.W))
    setos = np.zeros((lz.H, lz.W))
    y = y0
    while y < y1:
        prof = (y - y0) / (y1 - y0)
        h_ = 2.5 + prof ** 1.5 * 14
        x = -rng.random() * 40
        while x < lz.w:
            w_ = (16 + rng.random() * 30) * (0.5 + prof * 1.4)
            if rng.random() < 0.25:
                x += w_
                continue
            dx = (x + w_ / 2 - 300) * 0.05 * (0.3 + prof)
            parcela = lz.poligono([(x + 0.5, y + 0.4), (x + w_ - 0.5, y + 0.4), (x + w_ - 0.5 + dx, y + h_ - 0.4), (x + 0.5 + dx, y + h_ - 0.4)])
            cols = colores[rng.integers(len(colores))]
            surcos = (np.sin((lz.x - x + (lz.y - y) * 0.6) * (1.8 - prof)) > 0).astype(float) * (rng.random() < 0.6)
            col = rampa(cols, np.clip(0.35 + surcos * 0.25 + lz.ruido(2, 2) * 0.2, 0, 1))
            lz.pintar(parcela, col)
            m = np.maximum(m, parcela)
            setos = np.maximum(setos, lz.trazo([(x + dx, y + h_), (x + w_ + dx, y + h_)], 0.8 + prof * 1.6))
            x += w_
        y += h_
    lz.pintar(setos * (lz.ruido(1, 2) > 0.35), "#24401f", 0.85)
    return m


def raiz_luz(lz, puntos, grosor, color=("#c99d2a", "#f9b947", "#fde27e", "#fff8d2"), brillo=1.0, semilla=0):
    """Una raíz que brilla como un río de luz: serpentea, se mete en la tierra y vuelve a salir."""
    rng = np.random.default_rng(semilla)
    pts = np.array(puntos, float)
    # que serpentee
    n = len(pts)
    d = np.gradient(pts, axis=0)
    perp = np.stack([-d[:, 1], d[:, 0]], 1)
    perp /= np.linalg.norm(perp, axis=1, keepdims=True) + 1e-6
    onda = np.sin(np.linspace(0, 1, n) * (6 + rng.random() * 4) + rng.random() * 6) * grosor * 1.4
    pts = pts + perp * onda[:, None]
    m = lz.trazo(pts, grosor, grosor * 0.4)
    nucleo = lz.trazo(pts, grosor * 0.35, grosor * 0.14)
    # a trozos se hunde en la tierra
    asoma = np.clip((lz.ruido(9, 2, semilla=semilla + 7) - 0.32) * 5, 0, 1)
    lz.sumar_luz(lz.desenfocar(m, grosor * 2.5) * (0.4 + asoma * 0.6), "#ef8a26", 0.5 * brillo)
    lz.pintar(m * asoma, rampa(list(color[:3]), lz.ruido(1.5, 2) * 0.6 + 0.2))
    lz.pintar(nucleo * asoma, color[3], 0.9)
    lz.sumar_luz(m * (1 - asoma), "#f9b947", 0.35 * brillo)
    return m


def arco_raiz(lz, x, y, ancho, alto, brillo="#6b9eab", fuerza=0.8, cerrado=False, rampa_m=MADERA):
    """Un arco de raíces trenzadas (las puertas entre tierras)."""
    pts_e = [(x + np.cos(a) * ancho / 2, y - np.sin(a) * alto) for a in np.linspace(0, np.pi, 40)]
    interior = lz.poligono([(x - ancho / 2 + ancho * 0.12, y)] + [(x + np.cos(a) * ancho * 0.38, y - np.sin(a) * alto * 0.8) for a in np.linspace(np.pi, 0, 30)] + [(x + ancho * 0.38, y)])
    if not cerrado:
        lz.sumar_luz(lz.desenfocar(interior, ancho * 0.2), brillo, fuerza)
        lz.pintar(interior, brillo, 0.6 * fuerza)
    else:
        lz.pintar(interior, "#0d0716", 0.95)
    arco = np.zeros((lz.H, lz.W))
    for k in range(3):
        desf = (k - 1) * ancho * 0.05
        pts = [(x + np.cos(a) * (ancho / 2 - ancho * 0.06 + desf) + np.sin(a * 9 + k * 2) * ancho * 0.02, y - np.sin(a) * (alto - alto * 0.06 + desf)) for a in np.linspace(-0.05, np.pi + 0.05, 50)]
        arco = np.maximum(arco, lz.trazo(pts, ancho * 0.09, ancho * 0.07))
    lz.sombrear(arco, rampa_m, ancho * 0.05, (-0.6, -0.6, 0.5), textura=lz.ruido(1, 2), fuerza_tex=0.3)
    return arco


def arbol_grande(lz, x, y, alto, ancho, luz=(0.7, -0.6, 0.5), semilla=0, rampa_copa=FOLLAJE, rampa_tronco=MADERA,
                 seco=False):
    """Un árbol viejo y enorme: tronco ancho con raíces, ramas gruesas y una copa de muchos grupos de hojas."""
    rng = np.random.default_rng(semilla)
    lz.pintar(lz.desenfocar(lz.elipse(x + ancho * 0.1, y + 1, ancho * 0.55, ancho * 0.08), 1.5), "#0c140c", 0.5)
    # raíces que salen del pie
    tronco = np.zeros((lz.H, lz.W))
    for k in range(6):
        lado = -1 if k % 2 else 1
        largo = ancho * (0.15 + rng.random() * 0.2)
        tronco = np.maximum(tronco, lz.trazo(lz.curva((x + lado * ancho * 0.03, y - alto * 0.06), (x + lado * largo * 0.6, y - 1),
                                                      (x + lado * largo, y + 1 + rng.random() * 2), n=16), ancho * 0.06, ancho * 0.015))
    # el tronco, que se ensancha abajo
    pts = []
    for k in range(20):
        tt = k / 19
        w_ = ancho * (0.11 - 0.05 * tt + 0.06 * (1 - tt) ** 4)
        pts.append((x - w_ + np.sin(tt * 3) * ancho * 0.02, y - alto * 0.55 * tt))
    pts += [(x + ancho * (0.11 - 0.05 * (k / 19) + 0.06 * (1 - k / 19) ** 4) + np.sin(k / 19 * 3) * ancho * 0.02, y - alto * 0.55 * k / 19) for k in range(19, -1, -1)]
    tronco = np.maximum(tronco, lz.poligono(pts))
    # ramas gruesas hacia la copa
    ramas = []
    for k in range(7):
        a_ = np.radians(-90 + (k - 3) * 24 + (rng.random() - 0.5) * 10)
        largo = alto * (0.3 + rng.random() * 0.12)
        p0 = (x, y - alto * 0.5)
        p2 = (x + np.cos(a_) * largo * 1.3, y - alto * 0.5 + np.sin(a_) * largo * 0.9)
        p1 = ((p0[0] + p2[0]) / 2 + (rng.random() - 0.5) * 10, (p0[1] + p2[1]) / 2)
        ramas.append(p2)
        tronco = np.maximum(tronco, lz.trazo(lz.curva(p0, p1, p2, n=20), ancho * 0.06, ancho * 0.015))
        if seco:
            # ramitas que salen de cada rama, retorcidas
            for j in range(3):
                tt = 0.45 + j * 0.2
                b0 = (p0[0] + (p2[0] - p0[0]) * tt, p0[1] + (p2[1] - p0[1]) * tt)
                a2 = a_ + (rng.random() - 0.5) * 1.6
                l2 = largo * (0.25 + rng.random() * 0.25)
                b2 = (b0[0] + np.cos(a2) * l2, b0[1] + np.sin(a2) * l2)
                tronco = np.maximum(tronco, lz.trazo(lz.curva(b0, ((b0[0] + b2[0]) / 2 + (rng.random() - 0.5) * 6, (b0[1] + b2[1]) / 2), b2, n=10), ancho * 0.022, ancho * 0.006))
    corteza = lz.ruido(1.2, 2).astype(np.float32)
    corteza = cv2.filter2D(corteza, -1, np.ones((9, 1), np.float32) / 9)
    corteza = (corteza - corteza.min()) / (np.ptp(corteza) + 1e-6)
    lz.sombrear(tronco, rampa_tronco, ancho * 0.06, luz, textura=corteza, fuerza_tex=0.5)
    if seco:
        return tronco
    # la copa: muchos grupos de hojas (los de atrás más oscuros)
    grupos = []
    for k in range(84):
        a_ = rng.random() * 2 * np.pi
        d_ = np.sqrt(rng.random())
        gx = x + np.cos(a_) * ancho * 0.52 * d_
        gy = y - alto * 0.72 + np.sin(a_) * alto * 0.27 * d_
        grupos.append((gx, gy, ancho * (0.06 + rng.random() * 0.055)))
    for (rx_, ry_) in ramas:
        grupos.append((rx_, ry_, ancho * 0.09))
    grupos.sort(key=lambda g: g[1])
    copa_racimos(lz, grupos, rampa_copa, luz, semilla=semilla, filo=(rampa_copa[-1], 0.22))
    return tronco


def flores(lz, n, zona, colores, semilla=5, tam=1.2):
    rng = np.random.default_rng(semilla)
    x0, y0, x1, y1 = zona
    for _ in range(n):
        x, y = x0 + rng.random() * (x1 - x0), y0 + rng.random() * (y1 - y0)
        e = tam * (0.6 + (y - y0) / max(1, y1 - y0) * 0.8)
        tallo = lz.trazo([(x, y), (x + (rng.random() - 0.5) * 2, y - 4 * e)], 0.5 * e)
        lz.pintar(tallo, "#2f4a22")
        c = colores[rng.integers(len(colores))]
        flor = lz.circulo(x, y - 4 * e, 1.3 * e)
        lz.sombrear(flor, c, 0.9 * e, (-0.6, -0.6, 0.5))
        lz.pintar(lz.circulo(x, y - 4 * e, 0.45 * e), "#fde27e")


# ---------------------------------------------------------------- 1. El Kitovu antes
def kitovu_antes():
    """«Hace mucho tiempo, el Kitovu era el corazón verde del mundo. Por aquí pasaban las raíces de todas
    las tierras, y brillaban como ríos de luz.»
    El valle visto desde una loma, una mañana dorada: campos, el río, la aldea y, en el centro, el árbol
    viejo donde se cruzan las raíces de luz. En el horizonte, los arcos hacia las otras tierras."""
    lz = Lienzo(W, H, semilla=1)
    sol = (470, 40)
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#335777", "#4a7a93", "#6b9eab", "#97c1bf", "#e8f0dc", "#f8e1a6"], desde=-10, hasta=150))
    disco = lz.circulo(*sol, 12)
    lz.sumar_luz(lz.desenfocar(disco, 40), "#f8e1a6", 0.9)
    lz.sumar_luz(lz.rayos(lz.desenfocar(disco, 3), sol, largo=0.96, pasos=40) * 3, "#fff4d6", 0.5)
    lz.pintar(disco, "#fff8d2")
    cumulos(lz, [(110, 46, 60, 16), (170, 36, 40, 14), (330, 58, 70, 14), (560, 72, 60, 12), (40, 80, 50, 10)],
            luz=(sol[0] - 300, sol[1] - 60), colores=("#6b9eab", "#97c1bf", "#c4ddd0", "#e8f0dc", "#fff4d6"))
    # montañas lejanas, muy azuladas, con los arcos de las otras tierras en lo alto
    for base, amp, col, sem in [(132, 30, "#6b9eab", 5), (142, 20, "#4a7a93", 6)]:
        linea = linea_horizonte(lz, base, amp, 240, sem)
        m = mascara_bajo(lz, linea)
        lz.pintar(m, rampa([mezcla(col, "#16233a", 0.25), col, mezcla(col, "#e8f0dc", 0.35)], lz.ruido(10, 3) * 0.6 + 0.2))
        if sem == 5:
            for (ax, color) in [(70, "#6fcf4f"), (205, "#97c1bf"), (420, "#e98378"), (545, "#dcaaf2")]:
                ay = linea[int(ax * lz.s)] + 3
                arco_raiz(lz, ax, ay, 16, 15, brillo=color, fuerza=0.9, rampa_m=["#335777", "#4a7a93", "#6b9eab", "#97c1bf"])
    lz.niebla(np.clip((lz.y - 120) / 30, 0, 1) * np.clip((160 - lz.y) / 10, 0, 1), "#c4ddd0", 0.35)
    # colinas y campos del valle
    linea_v = linea_horizonte(lz, 152, 8, 300, 21)
    valle = mascara_bajo(lz, linea_v)
    lz.pintar(valle, rampa(HIERBA[3:7], np.clip(0.6 + (lz.ruido(6, 3) - 0.5) * 0.5, 0, 1)))
    cm = campos(lz, 154, 212, semilla=3)
    sombras_n = np.clip((lz.ruido(40, 3, semilla=61) - 0.55) * 4, 0, 1) * valle
    lz.pintar(sombras_n, "#1d2e18", 0.35)
    lz.niebla(valle * np.clip(1 - (lz.y - 150) / 40, 0, 1), "#c4ddd0", 0.3)
    # el río, que brilla con el sol
    t_ = np.linspace(0, 1, 70)
    rio_pts = np.stack([410 + 70 * np.sin(t_ * 4.2) - 260 * t_, 152 + 110 * t_ ** 1.3], 1)
    rio = lz.trazo(rio_pts, 1.2, 20)
    lz.pintar(rio, rampa(["#335777", "#6b9eab", "#c4ddd0"], lz.ruido(2, 2) * 0.5 + np.clip((lz.y - 150) / 100, 0, 1) * 0.4))
    lz.sumar_luz(rio * (lz.ruido(1.2, 2) > 0.8) * np.clip((lz.y - 150) / 60, 0, 1), "#fff8d2", 0.7)
    orilla = np.clip(lz.desenfocar(rio, 1.2) - rio, 0, 1)
    lz.pintar(orilla, "#3f5a2f", 0.6)
    # las raíces de luz: vienen de todas partes y se cruzan en el centro
    centro = (300, 182)
    for (p0, p1, g) in [((-10, 250), (120, 200), 5), ((610, 238), (470, 210), 5), ((40, 162), (170, 172), 3),
                        ((590, 160), (450, 172), 3), ((300, 262), (290, 220), 6), ((150, 260), (220, 210), 4), ((470, 262), (380, 214), 4)]:
        raiz_luz(lz, lz.curva(p0, p1, centro, n=60), g * 1.5, semilla=int(p0[0] + p0[1]), brillo=1.3)
    # la aldea: casitas de tejado rojo entre los campos
    for (cx, cy, e) in [(230, 178, 0.8), (250, 184, 0.9), (212, 188, 1.0), (372, 176, 0.7), (392, 186, 0.9), (356, 190, 1.0)]:
        pared = lz.poligono([(cx - 7 * e, cy), (cx - 7 * e, cy - 7 * e), (cx + 7 * e, cy - 7 * e), (cx + 7 * e, cy)])
        lz.sombrear(pared, ["#53392d", "#a57559", "#e0c09c"], 3 * e, (0.8, -0.4, 0.5))
        lz.sombrear(lz.poligono([(cx - 9 * e, cy - 6.5 * e), (cx, cy - 14 * e), (cx + 9 * e, cy - 6.5 * e)]), TEJADO, 3 * e, (0.8, -0.5, 0.4))
        lz.pintar(lz.poligono([(cx - 2 * e, cy), (cx - 2 * e, cy - 4 * e), (cx + 1.5 * e, cy - 4 * e), (cx + 1.5 * e, cy)]), "#2b1e17")
    # árboles por el valle
    rng = np.random.default_rng(8)
    for i in range(30):
        x = rng.random() * 600
        y = 156 + rng.random() * 60
        if abs(x - centro[0]) < 40 and abs(y - centro[1]) < 20:
            continue
        e = 0.35 + (y - 156) / 60 * 0.8
        arbol(lz, x, y, 22 * e, 14 * e, luz=(0.7, -0.6, 0.5), semilla=i, sombra=e > 0.6)
    # el árbol viejo del centro, con la luz de las raíces en sus pies
    lz.sumar_luz(lz.desenfocar(lz.elipse(centro[0], centro[1], 34, 8), 8), "#f9b947", 0.9)
    arbol_grande(lz, centro[0], centro[1] + 2, 96, 120, luz=(0.7, -0.6, 0.5), semilla=99)
    # primer plano: la loma con hierba alta y flores, y una rama que enmarca arriba
    loma_l = 236 - 14 * np.exp(-((np.arange(lz.W) / lz.s - 520) / 160) ** 2) + 2 * np.sin(np.arange(lz.W) / lz.s / 11)
    loma = mascara_bajo(lz, loma_l)
    lz.pintar(loma, rampa(HIERBA[1:5], lz.ruido(3, 3) * 0.6 + np.clip((lz.x - 300) / 400, 0, 1) * 0.3))
    hierba = np.zeros((lz.H, lz.W))
    for i in range(320):
        hx = rng.random() * 600
        hy = loma_l[int(min(lz.W - 1, hx * lz.s))] + 2 + rng.random() * 18
        largo = 5 + rng.random() * 10
        inc = (rng.random() - 0.5) * 6
        hierba = np.maximum(hierba, lz.trazo([(hx, hy), (hx + inc * 0.4, hy - largo * 0.6), (hx + inc, hy - largo)], 1.3, 0.3))
    lz.sombrear(hierba, HIERBA[1:7], 0.8, (0.7, -0.6, 0.5))
    flores(lz, 40, (10, 236, 590, 256), [["#8f2532", "#d5525e", "#e98378"], ["#b2721a", "#df9022", "#f1c27a"], ["#6a3446", "#c96d4f", "#f4b39a"]], semilla=6, tam=1.5)
    # hojas que cuelgan de una rama en la esquina de arriba
    rama = lz.trazo(lz.curva((-5, 8), (60, 18), (120, 6), n=30), 6, 2)
    lz.sombrear(rama, MADERA, 2, (0.7, -0.6, 0.5))
    hojas_m = np.zeros((lz.H, lz.W))
    for k in range(70):
        hx, hy = rng.random() * 130, 4 + rng.random() * 26 - rng.random() * 10
        hojas_m = np.maximum(hojas_m, lz.elipse(hx, hy, 4 + rng.random() * 3, 2, rng.random() * 180))
    lz.sombrear(hojas_m, FOLLAJE, 2, (0.7, -0.6, 0.5), textura=lz.ruido(1, 2), fuerza_tex=0.3)
    # luz cálida del sol por encima de todo
    lz.sumar_luz(np.clip(1 - np.hypot(lz.x - sol[0], lz.y - sol[1]) / 500, 0, 1) ** 2, "#f8e1a6", 0.25)
    vin = np.clip(np.hypot((lz.x - 300) / 360, (lz.y - 128) / 190) - 0.62, 0, 1)
    lz.pintar(vin, "#16233a", 0.5)
    return lz


# ---------------------------------------------------------------- la granja: piezas
PAJA = ["#3d2a10", "#704f25", "#a37036", "#d29a43", "#efc06a", "#f8dc96"]


def casa_troncos(lz, x, y, ancho, alto, luz=(-0.7, -0.6, 0.5), ventanas_luz=0.0, rueda=True, semilla=0):
    """La casa grande de los Shamba: troncos, tejado de paja, chimenea, porche y rueda de molino."""
    rng = np.random.default_rng(semilla)
    x0, x1 = x - ancho / 2, x + ancho / 2
    yt = y - alto * 0.55
    pared = lz.poligono([(x0, y), (x0, yt), (x1, yt), (x1, y)])
    # troncos horizontales
    n = 8
    for k in range(n):
        ya = yt + (y - yt) * k / n
        yb = yt + (y - yt) * (k + 1) / n
        tr = pared * np.clip((lz.y - ya) * lz.s, 0, 1) * np.clip((yb - lz.y) * lz.s, 0, 1)
        tt = np.clip((lz.y - ya) / (yb - ya), 0, 1)
        lz.pintar(tr, rampa(MADERA, np.clip(np.sin(tt * np.pi) * 0.7 + 0.15 + (lz.ruido(2, 2) - 0.5) * 0.25, 0, 1)))
        for lado in (x0, x1):
            lz.sombrear(lz.circulo(lado, (ya + yb) / 2, (yb - ya) * 0.55), ["#53392d", "#a57559", "#e0c09c"], (yb - ya) * 0.4, luz)
    # chimenea de piedra
    chx = x1 - ancho * 0.18
    chim = lz.poligono([(chx - 6, yt), (chx - 6, y - alto * 1.05), (chx + 6, y - alto * 1.05), (chx + 6, yt)])
    piedras(lz, chim, tam=4, semilla=semilla + 3)
    # el tejado de paja, grueso y redondeado
    tejado = lz.poligono([(x0 - ancho * 0.1, yt + 4), (x - ancho * 0.05, y - alto), (x + ancho * 0.05, y - alto), (x1 + ancho * 0.1, yt + 4),
                          (x1 + ancho * 0.08, yt + 9), (x0 - ancho * 0.08, yt + 9)])
    paja = (np.sin(lz.x * 2.4 + np.sin(lz.y * 0.8) * 2) * 0.5 + 0.5) * 0.6 + lz.ruido(0.8, 2) * 0.4
    lz.sombrear(tejado, PAJA, alto * 0.15, luz, textura=paja, fuerza_tex=0.4)
    borde_t = lz.trazo([(x0 - ancho * 0.09, yt + 8.5), (x1 + ancho * 0.09, yt + 8.5)], 2.2)
    lz.pintar(borde_t, "#704f25", 0.8)
    # buhardilla con ventana redonda
    bv = lz.circulo(x, y - alto * 0.72, alto * 0.08)
    lz.pintar(bv, "#251812")
    lz.pintar(lz.circulo(x, y - alto * 0.72, alto * 0.06), "#f9b947" if ventanas_luz else "#335777", 1.0)
    # porche: dos postes y un tejadillo
    for px_ in (x - ancho * 0.18, x + ancho * 0.18):
        lz.sombrear(lz.trazo([(px_, y), (px_, yt + 12)], 2.6), MADERA, 1.2, luz)
    # puerta y ventanas
    puerta = lz.poligono([(x - 6, y), (x - 6, y - 17), (x + 6, y - 17), (x + 6, y)])
    lz.sombrear(puerta, MADERA[:5], 3, luz)
    lz.pintar(lz.circulo(x + 3.5, y - 8, 0.9), "#f9b947")
    for vx_ in (x - ancho * 0.32, x + ancho * 0.32):
        v_ = lz.poligono([(vx_ - 7, y - 20), (vx_ + 7, y - 20), (vx_ + 7, y - 9), (vx_ - 7, y - 9)])
        lz.pintar(v_, "#251812")
        cristal = lz.poligono([(vx_ - 5.5, y - 18.5), (vx_ + 5.5, y - 18.5), (vx_ + 5.5, y - 10.5), (vx_ - 5.5, y - 10.5)])
        if ventanas_luz:
            lz.pintar(cristal, rampa(["#ef8a26", "#f9b947", "#fde27e"], lz.ruido(2, 2)))
            lz.sumar_luz(lz.desenfocar(cristal, 8), "#ef8a26", 0.6 * ventanas_luz)
        else:
            lz.pintar(cristal, lz.gradiente(["#97c1bf", "#4a7a93"], desde=y - 18, hasta=y - 10))
        lz.pintar(lz.trazo([(vx_, y - 18.5), (vx_, y - 10.5)], 1), "#251812")
        lz.pintar(lz.trazo([(vx_ - 5.5, y - 14.5), (vx_ + 5.5, y - 14.5)], 1), "#251812")
        # jardinera con flores
        lz.pintar(lz.poligono([(vx_ - 8, y - 9), (vx_ + 8, y - 9), (vx_ + 7, y - 6), (vx_ - 7, y - 6)]), "#6d4534")
        flores(lz, 6, (vx_ - 7, y - 9, vx_ + 7, y - 8.5), [["#8f2532", "#d5525e", "#e98378"], ["#b2721a", "#df9022", "#f1c27a"]], semilla=int(vx_), tam=0.7)
    if rueda:
        # la rueda del molino, a un lado, con su acequia de piedra y agua con espuma
        rx_, ry_ = x0 - 10, y - 12
        r_ = alto * 0.3
        acequia = lz.trazo(lz.curva((rx_ - 42, y + 6), (rx_ - 6, y + 3), (rx_ + 22, y + 1), n=28), 7.5, 5.0)
        borde_a = np.clip(lz.desenfocar(acequia, 1.6) - acequia, 0, 1)
        lz.sombrear(borde_a, PIEDRA[:5], 1.5, luz)
        lz.pintar(acequia, rampa(["#1d3a44", "#335777", "#6b9eab", "#c4ddd0"], np.clip(0.35 + lz.ruido(2, 2, semilla=semilla + 9) * 0.55, 0, 1)))
        aro = np.clip(lz.circulo(rx_, ry_, r_) - lz.circulo(rx_, ry_, r_ - 2.5), 0, 1)
        for k in range(10):
            a_ = k * np.pi / 5
            aro = np.maximum(aro, lz.trazo([(rx_, ry_), (rx_ + np.cos(a_) * r_, ry_ + np.sin(a_) * r_)], 1.4))
            aro = np.maximum(aro, lz.trazo([(rx_ + np.cos(a_) * (r_ - 1), ry_ + np.sin(a_) * (r_ - 1)), (rx_ + np.cos(a_) * (r_ + 3), ry_ + np.sin(a_) * (r_ + 3))], 2.4))
        lz.sombrear(aro, MADERA, 1.2, luz)
        lz.sombrear(lz.circulo(rx_, ry_, 3), MADERA, 2, luz)
        espuma = lz.elipse(rx_, y + 2, 12, 2.6) * (lz.ruido(1.2, 2, semilla=semilla + 11) > 0.38)
        lz.pintar(lz.desenfocar(espuma, 0.6), "#e8f0dc", 0.85)
    return pared


def zanahorias(lz, x0, x1, y, e=1.0, semilla=0, n=None):
    """Una fila de zanahorias: la cabeza naranja asomando y un penacho de hojas."""
    rng = np.random.default_rng(semilla)
    n = n or int((x1 - x0) / (7 * e))
    cabs_m = np.zeros((lz.H, lz.W))
    hojas_m = np.zeros((lz.H, lz.W))
    for k in range(n):
        x = x0 + (x1 - x0) * (k + 0.5) / n + (rng.random() - 0.5) * 2 * e
        cabs_m = np.maximum(cabs_m, lz.elipse(x, y - 0.5 * e, 2.4 * e, 1.6 * e))
        for j in range(5):
            a_ = np.radians(-90 + (j - 2) * 22 + (rng.random() - 0.5) * 10)
            l_ = (6 + rng.random() * 4) * e
            pts = lz.curva((x, y - 1 * e), (x + np.cos(a_) * l_ * 0.5, y - 1 * e + np.sin(a_) * l_ * 0.6), (x + np.cos(a_) * l_, y - 1 * e + np.sin(a_) * l_ * 0.9 + 1 * e), n=10)
            hojas_m = np.maximum(hojas_m, lz.trazo(pts, 1.6 * e, 0.6 * e))
    lz.sombrear(cabs_m, ["#6e200c", "#a8380f", "#d45a17", "#ef8a26", "#f9b947"], 1.4 * e, (-0.6, -0.7, 0.5))
    lz.sombrear(hojas_m, HIERBA[2:], 0.9 * e, (-0.6, -0.7, 0.5), textura=lz.ruido(0.7, 2), fuerza_tex=0.4)


def coles(lz, x0, x1, y, e=1.0, semilla=0):
    rng = np.random.default_rng(semilla)
    n = int((x1 - x0) / (12 * e))
    hojas_ = []
    for k in range(n):
        x = x0 + (x1 - x0) * (k + 0.5) / n
        for j in range(9):
            a_ = j / 9 * 2 * np.pi
            hojas_.append((x + np.cos(a_) * 3.5 * e, y - 3 * e + np.sin(a_) * 2 * e, 3.4 * e))
        hojas_.append((x, y - 3.6 * e, 3.2 * e))
    if hojas_:
        bolas(lz, hojas_, ["#24401f", "#355029", "#5d793e", "#8aa152", "#b4c070", "#dcd994"], luz=(-0.6, -0.7, 0.5),
              ruido_borde=0.2, fuerza_tex=0.2, plano=1.3)


def azada(lz, x_mano, y_mano, e=1.0, luz=(-0.6, -0.7, 0.5)):
    """Una azada: mango largo de madera y la hoja de hierro clavada en la tierra."""
    p_alto = (x_mano - 6 * e, y_mano - 14 * e)
    p_bajo = (x_mano + 9 * e, y_mano + 22 * e)
    mango = lz.trazo([p_alto, p_bajo], 1.6 * e)
    lz.sombrear(mango, MADERA, 0.8 * e, luz)
    hoja = lz.poligono([(p_bajo[0] - 1 * e, p_bajo[1] - 2 * e), (p_bajo[0] + 7 * e, p_bajo[1] - 1 * e), (p_bajo[0] + 8 * e, p_bajo[1] + 2 * e), (p_bajo[0] - 0.5 * e, p_bajo[1] + 1.5 * e)])
    lz.sombrear(hoja, ["#1b1c1f", "#3d3f43", "#6a6c6f", "#a3a4a6", "#c5c6c7"], 1.2 * e, luz)


def cesta(lz, x, y, e=1.0, luz=(-0.6, -0.7, 0.5), contenido="zanahorias", semilla=0):
    """Una cesta de mimbre llena (de zanahorias)."""
    rng = np.random.default_rng(semilla)
    # lo de dentro asoma por arriba
    if contenido == "zanahorias":
        for k in range(7):
            cx_ = x + (k - 3) * 2.2 * e + (rng.random() - 0.5) * e
            z = lz.trazo([(cx_, y - 5 * e), (cx_ + (rng.random() - 0.5) * 4 * e, y - 11 * e)], 2.6 * e, 0.8 * e)
            lz.sombrear(z, ["#6e200c", "#a8380f", "#d45a17", "#ef8a26", "#f9b947"], 1.0 * e, luz)
            lz.pintar(lz.trazo([(cx_, y - 5 * e), (cx_ + (rng.random() - 0.5) * 3 * e, y - 2 * e)], 1.0 * e), "#5d793e")
    cuerpo = lz.poligono([(x - 9 * e, y - 6 * e), (x + 9 * e, y - 6 * e), (x + 7 * e, y + 4 * e), (x - 7 * e, y + 4 * e)])
    mimbre = (np.sin(lz.x * 3 / e) * np.sin(lz.y * 3 / e) > 0).astype(float)
    lz.sombrear(cuerpo, ["#3d2a10", "#704f25", "#a37036", "#d29a43", "#efc06a"], 3 * e, luz, textura=mimbre, fuerza_tex=0.35)
    lz.sombrear(lz.trazo([(x - 9 * e, y - 6 * e), (x + 9 * e, y - 6 * e)], 1.8 * e), ["#3d2a10", "#a37036", "#efc06a"], 0.8 * e, luz)


def regadera(lz, x, y, e=1.0, luz=(-0.6, -0.7, 0.5), mira=1):
    """Una regadera de chapa que echa agua por delante."""
    cuerpo = lz.elipse(x, y, 5 * e, 4 * e)
    lz.sombrear(cuerpo, ["#1e2038", "#335777", "#4a7a93", "#6b9eab", "#c4ddd0"], 2.5 * e, luz)
    pico = lz.trazo([(x + 4 * e * mira, y), (x + 11 * e * mira, y - 5 * e)], 1.4 * e, 1.0 * e)
    lz.sombrear(pico, ["#1e2038", "#335777", "#6b9eab", "#c4ddd0"], 0.6 * e, luz)
    asa = np.clip(lz.elipse(x - 1 * e * mira, y - 4 * e, 4 * e, 3 * e) - lz.elipse(x - 1 * e * mira, y - 4 * e, 2.8 * e, 1.8 * e), 0, 1) * (lz.y < y - 3 * e)
    lz.pintar(asa, "#335777")
    # el chorrito de gotas
    rng = np.random.default_rng(3)
    gotas = np.zeros((lz.H, lz.W))
    for k in range(18):
        tt = rng.random()
        gx = x + (11 + tt * 8) * e * mira + (rng.random() - 0.5) * 3 * e
        gy = y - 5 * e + tt * tt * 26 * e
        gotas = np.maximum(gotas, lz.elipse(gx, gy, 0.5 * e, 0.9 * e))
    lz.pintar(gotas, "#c4ddd0", 0.9)
    lz.sumar_luz(gotas, "#ffffff", 0.4)


def mariposa(lz, x, y, e=1.0, color=("#b2721a", "#df9022", "#f1c27a")):
    for lado in (-1, 1):
        ala = lz.elipse(x + lado * 1.8 * e, y - 0.8 * e, 2 * e, 1.5 * e, lado * 25)
        lz.sombrear(ala, list(color), 1 * e, (-0.6, -0.7, 0.5))
    lz.pintar(lz.trazo([(x, y - 2 * e), (x, y + 1 * e)], 0.6 * e), "#251812")


# ---------------------------------------------------------------- 2. La familia Shamba
def familia_shamba():
    """«Los castores Shamba cuidábamos sus huertos y sus raíces, de generación en generación.»
    Una tarde de cosecha en la granja, cuando todo tenía color: la casa grande con su rueda de molino,
    el huerto en hileras y la familia trabajando: uno cava con la azada, otra lleva una cesta de
    zanahorias, la abuela vigila con sus gafas y una cría riega las coles."""
    lz = Lienzo(W, H, semilla=2)
    sol = (520, 52)
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#4a7a93", "#6b9eab", "#c4ddd0", "#f8e1a6", "#f1c27a"], desde=-10, hasta=130))
    disco = lz.circulo(*sol, 13)
    lz.sumar_luz(lz.desenfocar(disco, 40), "#f8e1a6", 0.9)
    lz.pintar(disco, "#fff8d2")
    cumulos(lz, [(150, 40, 70, 16), (330, 30, 50, 13), (60, 70, 40, 11)], luz=(1, -0.3),
            colores=("#97c1bf", "#e8f0dc", "#f8e1a6", "#fff4d6", "#ffffff"))
    # colinas del fondo con árboles
    for base, amp, cols, sem in [(112, 14, HIERBA[3:7], 31), (124, 10, HIERBA[2:6], 32)]:
        linea = linea_horizonte(lz, base, amp, 200, sem)
        m = mascara_bajo(lz, linea)
        lz.pintar(m, rampa(cols, np.clip(0.55 + (lz.ruido(5, 3) - 0.5) * 0.5, 0, 1)))
    lz.niebla(np.clip(1 - (lz.y - 95) / 40, 0, 1) * (lz.y > 95), "#f8e1a6", 0.35)
    rng = np.random.default_rng(5)
    for i in range(16):
        x = rng.random() * 600
        y = 112 + rng.random() * 18
        arbol(lz, x, y, 26, 18, luz=(0.8, -0.5, 0.5), semilla=i + 40)
    # el suelo de la granja
    suelo = np.clip((lz.y - 128) * lz.s, 0, 1)
    lz.pintar(suelo, rampa(HIERBA[3:7], np.clip(0.5 + (lz.ruido(4, 3) - 0.5) * 0.5, 0, 1)))
    # la casa al fondo a la derecha, con la acequia y la rueda
    # un camino de tierra desde la puerta hasta el huerto
    camino = lz.trazo(lz.curva((486, 148), (440, 170), (330, 200), (250, 262), n=50), 10, 34)
    lz.pintar(camino, rampa(TIERRA[2:6], np.clip(0.5 + (lz.ruido(2, 3) - 0.5) * 0.6, 0, 1)))
    lz.pintar(np.clip(lz.desenfocar(camino, 1.5) - camino, 0, 1), "#3f5a2f", 0.6)
    casa_troncos(lz, 486, 146, 136, 92, luz=(0.8, -0.5, 0.5), semilla=4)
    # el huerto: tierra en hileras con perspectiva
    huerto = lz.poligono([(10, 256), (60, 150), (340, 150), (420, 256)])
    lz.pintar(huerto, rampa(TIERRA[1:6], np.clip(0.45 + (lz.ruido(2, 3) - 0.5) * 0.4, 0, 1)))
    filas_y = [156, 163, 171, 181, 193, 208, 226, 248]
    for k, fy in enumerate(filas_y):
        prof = k / (len(filas_y) - 1)
        e = 0.45 + prof * 0.9
        izq = 60 - (fy - 150) * 0.47
        der = 340 + (fy - 150) * 0.78
        caballon = lz.trazo([(izq, fy), (der, fy)], 2.2 * e)
        lz.sombrear(caballon, TIERRA[1:], 1.2 * e, (0.8, -0.6, 0.5))
        if k % 2 == 0:
            zanahorias(lz, izq + 6, der - 6, fy, e, semilla=k)
        elif k in (3, 7):
            coles(lz, izq + 8, der - 8, fy + 1, e, semilla=k)
        else:
            zanahorias(lz, izq + 6, der - 6, fy, e * 0.8, semilla=k + 20)
    # la familia (de atrás hacia delante)
    luz_c = (0.8, -0.5, 0.5)
    # la abuela, junto a la casa, mira con sus gafas y su chal
    castor(lz, 462, 150, 0.85, -1, chal=True, gafas=True, sem=21, luz=luz_c, recorte=("#fde27e", 0.6), recorte_dir=(1, -0.4))
    # el padre, cavando con la azada y su sombrero de paja
    castor(lz, 120, 200, 1.55, 1, sombrero=True, delantal=True, sem=22, luz=luz_c, recorte=("#fde27e", 0.6), recorte_dir=(1, -0.4))
    azada(lz, 135, 178, 1.55, luz_c)
    # la madre, con la cesta llena de zanahorias
    castor(lz, 250, 214, 1.6, -1, delantal=True, sem=23, luz=luz_c, recorte=("#fde27e", 0.6), recorte_dir=(1, -0.4))
    cesta(lz, 236, 192, 1.4, luz_c)
    # la cría, regando las coles
    castor(lz, 330, 236, 1.05, 1, cria=True, sem=24, luz=luz_c, recorte=("#fde27e", 0.6), recorte_dir=(1, -0.4))
    regadera(lz, 342, 218, 1.1, luz_c)
    # primer plano: hojas de zanahoria grandes en la esquina y una valla a la derecha
    zanahorias(lz, -10, 70, 262, 2.6, semilla=77, n=4)
    for k in range(5):
        px_ = 470 + k * 34
        poste = lz.trazo([(px_, 260), (px_ + 1, 206)], 4.6, 3.6)
        lz.sombrear(poste, MADERA, 2, luz_c, textura=lz.ruido(1, 2), fuerza_tex=0.3)
    for yy in (218, 238):
        tabla = lz.trazo([(460, yy + 3), (610, yy - 3)], 4)
        lz.sombrear(tabla, MADERA, 2, luz_c, textura=lz.ruido(1, 2), fuerza_tex=0.3)
    # mariposas
    for (mx_, my_, c_) in [(180, 140, ("#b2721a", "#df9022", "#f1c27a")), (300, 128, ("#8f2532", "#d5525e", "#e98378")), (420, 190, ("#e3c391", "#f3e0b8", "#ffffff"))]:
        mariposa(lz, mx_, my_, 1.4, c_)
    # luz dorada de tarde
    lz.sumar_luz(np.clip(1 - np.hypot(lz.x - sol[0], lz.y - sol[1]) / 520, 0, 1) ** 2, "#f8e1a6", 0.3)
    vin = np.clip(np.hypot((lz.x - 300) / 360, (lz.y - 128) / 190) - 0.62, 0, 1)
    lz.pintar(vin, "#3a2238", 0.45)
    return lz


# ---------------------------------------------------------------- 5. La piedra
def volver_piedra(lz, mascara, semilla=0, grietas_violeta=0.6):
    """Convierte lo pintado bajo la máscara en piedra: sin color, con grietas, musgo y un brillo violeta."""
    m = np.clip(mascara, 0, 1)
    lum = (lz.img * [0.3, 0.55, 0.15]).sum(-1)
    piedra = rampa(PIEDRA[:6], np.clip(0.28 + lum * 0.75 + (lz.ruido(1.5, 3, semilla=semilla) - 0.5) * 0.12, 0, 1))
    lz.pintar(m, piedra)
    grieta = np.clip(1 - np.abs(lz.ruido(12, 3, semilla=semilla + 1) - 0.5) * 40, 0, 1) * (m > 0.5)
    lz.pintar(grieta, "#18191a", 0.9)
    if grietas_violeta:
        lz.sumar_luz(lz.desenfocar(grieta, 1.2) * (lz.ruido(8, 2, semilla=semilla + 3) > 0.55), "#7a2fa0", grietas_violeta)
    musgo = (lz.ruido(2.5, 3, semilla=semilla + 4) > 0.74) * m * np.clip((lz.y - 120) / 120, 0, 1)
    lz.pintar(lz.desenfocar(musgo, 0.5), rampa(["#24401f", "#3f5a2f", "#5d7a3c"], lz.ruido(1, 2)), 0.6)


def piedra():
    """«Las raíces se secaron. Los vecinos se convirtieron en piedra. Los arcos a las otras tierras se cerraron.»
    La plaza de la aldea, gris y quieta bajo un cielo encapotado: los vecinos son estatuas agrietadas (una
    madre que abraza a su cría, uno que alarga la mano), las raíces secas rompen el suelo y, al fondo,
    el Arco de Raíz está cerrado por espinas de Giza."""
    lz = Lienzo(W, H, semilla=5)
    # cielo de tormenta, gris violáceo
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#151527", "#2a2d4c", "#3d3f43", "#525458", "#6a6c6f"], desde=-10, hasta=150))
    cumulos(lz, [(100, 30, 120, 22), (330, 20, 140, 20), (540, 40, 110, 22), (220, 70, 90, 14)], luz=(-0.3, -1),
            colores=("#151527", "#1e2038", "#2b2c30", "#3d3f43", "#525458", "#6a6c6f"), semilla=71)
    # el arco cerrado al fondo, en lo alto de una loma, con espinas y una luz violeta enferma
    loma = mascara_bajo(lz, linea_horizonte(lz, 136, 10, 260, 72))
    lz.pintar(loma, rampa(["#2b2c30", "#3d3f43", "#525458"], lz.ruido(6, 3) * 0.7 + 0.15))
    arco_raiz(lz, 300, 132, 96, 92, cerrado=True, rampa_m=["#18191a", "#2b2c30", "#3d3f43", "#525458", "#6a6c6f"])
    rng = np.random.default_rng(73)
    espinas = np.zeros((lz.H, lz.W))
    for k in range(16):
        a_ = np.pi * (0.05 + 0.9 * rng.random())
        x0_, y0_ = 300 + np.cos(a_) * 34, 132 - np.sin(a_) * 70
        espinas = np.maximum(espinas, lz.trazo(lz.curva((x0_, y0_), (300 + (rng.random() - 0.5) * 30, 100 + rng.random() * 30), (300 + np.cos(a_ + 3) * 30, 132 - rng.random() * 50), n=20), 3, 0.5))
    lz.sumar_luz(lz.desenfocar(espinas, 4), "#4d1a6b", 0.8)
    lz.pintar(espinas, "#0d0716")
    ojo_giza(lz, 300, 92, 9, 2.6, 0, 0.7)
    # árboles secos a los lados
    arbol_grande(lz, 70, 150, 120, 90, luz=(-0.4, -0.8, 0.5), semilla=5, seco=True, rampa_tronco=["#18191a", "#2b2c30", "#3d3f43", "#525458", "#6a6c6f"])
    arbol_grande(lz, 540, 142, 100, 70, luz=(-0.4, -0.8, 0.5), semilla=6, seco=True, rampa_tronco=["#18191a", "#2b2c30", "#3d3f43", "#525458", "#6a6c6f"])
    # casas caídas
    for (cx, cy, e) in [(150, 150, 1.4), (450, 146, 1.2)]:
        pared = lz.poligono([(cx - 12 * e, cy), (cx - 12 * e, cy - 9 * e), (cx - 2 * e, cy - 12 * e), (cx + 4 * e, cy - 7 * e), (cx + 12 * e, cy - 6 * e), (cx + 12 * e, cy)])
        lz.sombrear(pared, ["#2b2c30", "#3d3f43", "#525458", "#6a6c6f"], 4 * e, (-0.4, -0.8, 0.5), textura=lz.ruido(1, 2), fuerza_tex=0.3)
        viga = lz.trazo([(cx - 14 * e, cy - 8 * e), (cx + 6 * e, cy - 16 * e)], 1.6 * e)
        lz.sombrear(viga, ["#18191a", "#2b2c30", "#3d3f43"], 0.8 * e, (-0.4, -0.8, 0.5))
        lz.pintar(lz.poligono([(cx - 3 * e, cy), (cx - 3 * e, cy - 6 * e), (cx + 2 * e, cy - 6 * e), (cx + 2 * e, cy)]), "#151527")
    # la plaza: losas irregulares, rotas
    suelo = np.clip((lz.y - 150) * lz.s, 0, 1)
    lz.pintar(suelo, rampa(["#2b2c30", "#3d3f43", "#525458", "#6a6c6f"], np.clip(0.4 + (lz.ruido(3, 3) - 0.5) * 0.4 + (lz.y - 150) / 300, 0, 1)))
    semillas_v = []
    yv = 150.0
    while yv < 270:
        paso = 4 + (yv - 150) * 0.16
        for xv in np.arange(-20, 620, paso * 1.6):
            semillas_v.append((xv + rng.random() * paso, yv + rng.random() * paso * 0.6))
        yv += paso * 0.7
    from scipy.spatial import cKDTree
    arbol_v = cKDTree(np.array(semillas_v))
    pts = np.stack([lz.x.ravel(), lz.y.ravel()], 1)
    d2, _ = arbol_v.query(pts, k=2)
    borde_v = (d2[:, 1] - d2[:, 0]).reshape(lz.H, lz.W)
    juntas = np.clip(1 - borde_v / (0.5 + (lz.y - 150) / 90), 0, 1) * suelo
    lz.pintar(juntas, "#18191a", 0.9)
    lz.pintar(np.clip(1 - np.abs(borde_v - 1.2 - (lz.y - 150) / 60) * 2, 0, 1) * suelo * 0.5, "#85878a", 0.3)
    # raíces secas y agrietadas que rompen el suelo
    for (p0, p1, p2, g) in [((-10, 196), (120, 176), (250, 184), 10), ((610, 206), (480, 182), (360, 188), 9), ((250, 266), (270, 220), (300, 196), 8)]:
        r_ = lz.trazo(lz.curva(p0, p1, p2, n=40), g, g * 0.3)
        lz.sombrear(r_, ["#18191a", "#2b2c30", "#3d3f43", "#525458", "#6a6c6f"], g * 0.5, (-0.4, -0.8, 0.5), textura=lz.ruido(0.8, 2), fuerza_tex=0.4)
        lz.pintar(r_ * (np.abs(np.sin(lz.x * 0.9)) < 0.12), "#0d0c19", 0.8)
    # los vecinos de piedra
    estatuas = np.zeros((lz.H, lz.W))
    antes = lz.img.copy()
    luz_e = (-0.5, -0.8, 0.5)
    estatuas = np.maximum(estatuas, castor(lz, 486, 184, 1.0, -1, sombrero=True, sem=54, luz=luz_e))
    estatuas = np.maximum(estatuas, castor(lz, 156, 240, 2.2, 1, delantal=True, brazo_alto=True, sem=51, luz=luz_e, mirada=(1, -1)))
    estatuas = np.maximum(estatuas, castor(lz, 418, 242, 2.1, -1, chal=True, sem=52, luz=luz_e))
    estatuas = np.maximum(estatuas, castor(lz, 384, 250, 1.25, -1, cria=True, sem=53, luz=luz_e, mirada=(-1, -1)))
    volver_piedra(lz, lz.desenfocar(estatuas, 0.3), semilla=5)
    # neblina violeta baja y polvo
    lz.niebla(np.clip((lz.y - 170) / 90, 0, 1) * lz.ruido(30, 3, semilla=75), "#3e1b5c", 0.35)
    motas = np.zeros((lz.H, lz.W))
    for i in range(80):
        motas = np.maximum(motas, lz.circulo(rng.random() * 600, rng.random() * 256, 0.4 + rng.random() * 0.5) * rng.random())
    lz.sumar_luz(motas, "#a3a4a6", 0.5)
    vin = np.clip(np.hypot((lz.x - 300) / 340, (lz.y - 128) / 180) - 0.5, 0, 1)
    lz.pintar(vin, "#07060d", 0.7)
    return lz


# ---------------------------------------------------------------- 6. Hoy
def farol(lz, x, y, e=1.0, luz=(-0.6, -0.6, 0.5), fuerza=1.0):
    """Un farol de mano: asa, techito de chapa, cristal con una llama y su halo de luz."""
    lz.sumar_luz(lz.desenfocar(lz.circulo(x, y, 4 * e), 26 * e), "#ef8a26", 0.7 * fuerza)
    lz.sumar_luz(lz.desenfocar(lz.circulo(x, y, 3 * e), 8 * e), "#f9b947", 0.8 * fuerza)
    asa = np.clip(lz.elipse(x, y - 7 * e, 3 * e, 3.4 * e) - lz.elipse(x, y - 7 * e, 2.2 * e, 2.6 * e), 0, 1) * (lz.y < y - 7 * e)
    lz.pintar(asa, "#2b2c30")
    cristal = lz.poligono([(x - 3.4 * e, y - 5 * e), (x + 3.4 * e, y - 5 * e), (x + 3 * e, y + 4 * e), (x - 3 * e, y + 4 * e)])
    lz.pintar(cristal, rampa(["#ef8a26", "#f9b947", "#fde27e"], np.clip(1 - np.hypot(lz.x - x, lz.y - y) / (5 * e), 0, 1)))
    lz.pintar(lz.elipse(x, y, 1.2 * e, 2.4 * e), "#fff8d2")
    techo = lz.poligono([(x - 4.4 * e, y - 5 * e), (x, y - 8 * e), (x + 4.4 * e, y - 5 * e)])
    lz.sombrear(techo, ["#1b1c1f", "#3d3f43", "#6a6c6f"], 1 * e, luz)
    base = lz.poligono([(x - 4 * e, y + 4 * e), (x + 4 * e, y + 4 * e), (x + 3.4 * e, y + 6 * e), (x - 3.4 * e, y + 6 * e)])
    lz.sombrear(base, ["#1b1c1f", "#3d3f43", "#6a6c6f"], 1 * e, luz)
    for dx_ in (-3.2, 0, 3.2):
        lz.pintar(lz.trazo([(x + dx_ * e, y - 5 * e), (x + dx_ * 0.9 * e, y + 4 * e)], 0.6 * e), "#2b2c30", 0.9)


def hoy():
    """«Yo me quedé. Alguien tenía que cuidar lo poco que seguía vivo. Y esperé. Esperé mucho tiempo... hasta hoy.»
    Anochece sobre un valle gris. Solo la granja conserva el color, con las ventanas encendidas. Mzee Shamba,
    ya viejo, con su sombrero, sus gafas y un farol, mira hacia el arco cerrado del horizonte."""
    lz = Lienzo(W, H, semilla=6)
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#07060d", "#151527", "#2a2d4c", "#535a80", "#9c4b4a", "#c96d4f"], desde=-20, hasta=150))
    estrellas(lz, 90, 90, semilla=61)
    luna = lz.circulo(90, 40, 10)
    lz.sumar_luz(lz.desenfocar(luna, 20), "#535a80", 0.7)
    lz.pintar(luna, rampa(["#97c1bf", "#e8f0dc"], lz.volumen(luna, 6, (-0.6, -0.5, 0.6))[0]))
    lz.pintar(lz.circulo(95, 37, 9) * luna, "#151527", 0.85)   # luna menguante
    # montañas grises y el arco cerrado a lo lejos
    for base, amp, cols, sem in [(130, 24, ["#1e2038", "#2a2d4c", "#3b4063"], 81), (142, 14, ["#151527", "#1e2038", "#2a2d4c"], 82)]:
        linea = linea_horizonte(lz, base, amp, 220, sem)
        lz.pintar(mascara_bajo(lz, linea), rampa(cols, lz.ruido(8, 3) * 0.7 + 0.15))
        if sem == 81:
            ay = linea[int(520 * lz.s)] + 2
            arco_raiz(lz, 520, ay, 22, 22, cerrado=True, rampa_m=["#0d0c19", "#151527", "#1e2038", "#2a2d4c"])
            lz.sumar_luz(lz.desenfocar(lz.circulo(520, ay - 10, 6), 6), "#4d1a6b", 0.8)
    lz.niebla(np.clip(1 - np.abs(lz.y - 140) / 20, 0, 1), "#3b4063", 0.4)
    # el valle gris, con árboles muertos
    valle = mascara_bajo(lz, linea_horizonte(lz, 150, 6, 260, 83))
    lz.pintar(valle, rampa(["#1b1c1f", "#2b2c30", "#3d3f43", "#525458"], np.clip(0.3 + (lz.ruido(5, 3) - 0.5) * 0.2 + (lz.y - 150) / 300, 0, 1)))
    rng = np.random.default_rng(62)
    for i in range(10):
        x = rng.random() * 600
        if 250 < x < 470:
            continue
        y = 152 + rng.random() * 30
        e = 0.3 + (y - 152) / 30 * 0.3
        arbol_grande(lz, x, y, 70 * e, 50 * e, luz=(-0.4, -0.8, 0.5), semilla=i + 70, seco=True,
                     rampa_tronco=["#0d0c19", "#151527", "#1e2038", "#2b2c30", "#3d3f43"])
    # la isla de color: la granja con su hierba, el huerto y las ventanas encendidas
    isla = lz.desenfocar(lz.elipse(372, 186, 120, 30), 6)
    lz.pintar(isla, rampa(HIERBA[1:5], np.clip(0.4 + (lz.ruido(3, 3) - 0.5) * 0.5, 0, 1)), 0.95)
    casa_troncos(lz, 372, 176, 104, 70, luz=(0.6, -0.5, 0.5), ventanas_luz=1.0, rueda=True, semilla=9)
    for fy in (190, 196, 202):
        zanahorias(lz, 420, 470, fy, 0.6, semilla=fy)
    # humo de la chimenea
    humo_c = np.zeros((lz.H, lz.W))
    for k in range(14):
        tt = k / 13
        humo_c = np.maximum(humo_c, lz.circulo(372 + 33 + np.sin(tt * 5) * 6 + tt * 20, 106 - tt * 70, 2 + tt * 7))
    lz.pintar(lz.desenfocar(humo_c, 2) * np.clip((lz.y - 30) / 80, 0, 1), "#535a80", 0.45)
    # primer plano: un poste de la valla y Shamba con su farol
    loma_l = 246 - 10 * np.exp(-((np.arange(lz.W) / lz.s - 150) / 120) ** 2)
    loma = mascara_bajo(lz, loma_l)
    lz.pintar(loma, rampa(["#0d0c19", "#151527", "#1e2038"], lz.ruido(3, 3)))
    for k in range(3):
        px_ = 30 + k * 40
        poste = lz.trazo([(px_, 252), (px_ + 1, 208 + k * 3)], 4.6, 3.6)
        lz.sombrear(poste, MADERA[:5], 2, (0.8, -0.3, 0.5))
    lz.sombrear(lz.trazo([(10, 222), (120, 228)], 3.6), MADERA[:5], 1.8, (0.8, -0.3, 0.5))
    luz_s = (0.8, -0.2, 0.5)
    castor(lz, 176, 240, 2.3, 1, sombrero=True, gafas=True, delantal=True, barba=True, sem=61,
           luz=luz_s, recorte=("#535a80", 0.6), recorte_dir=(-1, -0.4), mirada=(1, 0))
    # es de noche: todo en penumbra azul, salvo la luz del farol y de las ventanas
    cielo = (lz.y < 150).astype(float) * (1 - lz.desenfocar(mascara_bajo(lz, linea_horizonte(lz, 130, 24, 220, 81)), 1))
    iluminar(lz, "#525a80", [(198, 222, 120, "#ef8a26", 1.3), (372, 170, 130, "#c96d17", 0.55)], propia=cielo)
    farol(lz, 198, 222, 1.6, luz_s)
    # las ventanas siguen encendidas (luz propia), y su luz cae sobre la hierba
    for (vx_, vy_) in [(372 - 104 * 0.32, 161.5), (372 + 104 * 0.32, 161.5)]:
        v_ = lz.poligono([(vx_ - 5.5, vy_ - 4), (vx_ + 5.5, vy_ - 4), (vx_ + 5.5, vy_ + 4), (vx_ - 5.5, vy_ + 4)])
        lz.pintar(v_, rampa(["#ef8a26", "#f9b947", "#fde27e"], lz.ruido(2, 2)))
        lz.pintar(lz.trazo([(vx_, vy_ - 4), (vx_, vy_ + 4)], 1) + lz.trazo([(vx_ - 5.5, vy_), (vx_ + 5.5, vy_)], 1), "#251812")
        lz.sumar_luz(lz.desenfocar(v_, 10), "#ef8a26", 0.7)
        lz.sumar_luz(lz.desenfocar(lz.elipse(vx_, vy_ + 22, 16, 5), 4), "#c96d17", 0.35)
    ventanita = lz.circulo(372, 176 - 70 * 0.72, 70 * 0.06)
    lz.pintar(ventanita, "#f9b947")
    lz.sumar_luz(lz.desenfocar(ventanita, 6), "#ef8a26", 0.6)
    vin = np.clip(np.hypot((lz.x - 300) / 340, (lz.y - 128) / 180) - 0.55, 0, 1)
    lz.pintar(vin, "#07060d", 0.7)
    return lz


# ---------------------------------------------------------------- los recuerdos de Maisha
def marco_recuerdo(lz, color="#efe6cf", semilla=90):
    """Los recuerdos se ven como a través de una niebla clara que se come los bordes."""
    d = np.maximum(np.abs(lz.x - 300) / 300, np.abs(lz.y - 128) / 128) * 0.55 + np.hypot((lz.x - 300) / 300, (lz.y - 128) / 128) * 0.45
    # un velo suave y estrecho (sin manchas): los bordes de la propia escena, desenfocados y aclarados hacia el color
    ondas = lz.desenfocar(lz.ruido(20, 2, semilla=semilla), 12)
    borde = lz.desenfocar(np.clip((d - 0.76 + (ondas - 0.5) * 0.08) * 2.4, 0, 1), 14) ** 1.6
    velo = np.clip(cv2.GaussianBlur(lz.img.astype(np.float32), (0, 0), 6 * lz.s) * 0.7 + 0.22, 0, 1)
    lz.pintar(borde, velo, 0.75)
    lz.pintar(borde, color, 0.35)
    # motas de luz flotando
    rng = np.random.default_rng(semilla)
    motas = np.zeros((lz.H, lz.W))
    for _ in range(40):
        motas = np.maximum(motas, lz.circulo(rng.random() * 600, rng.random() * 256, 0.5 + rng.random()) * rng.random())
    lz.sumar_luz(lz.desenfocar(motas, 0.8), "#fff4d6", 0.6)


def recuerdo_aldea():
    """«Faroles encendidos. Gente que ríe alrededor de un fuego... Yo estaba aquí. Lo sé. Pero... ¿cuándo?»
    La aldea antigua del Kitovu, una noche de fiesta: guirnaldas de farolillos colgadas del árbol viejo,
    ventanas encendidas y los vecinos alrededor de una hoguera."""
    lz = Lienzo(W, H, semilla=7)
    fuego_xy = (300, 214)
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#07060d", "#151527", "#1e2038", "#2a2d4c", "#3b4063"], desde=-10, hasta=170))
    estrellas(lz, 120, 140, semilla=71)
    # el árbol viejo detrás, enorme, oscuro
    arbol_grande(lz, 300, 196, 190, 300, luz=(0.0, 0.8, 0.4), semilla=72,
                 rampa_copa=["#0d0c19", "#151527", "#1e2038", "#2a2d4c", "#3b4063", "#535a80"],
                 rampa_tronco=["#07060d", "#0d0c19", "#151527", "#1e2038", "#2a2d4c"])
    # casas alrededor con las ventanas encendidas
    for (cx, cy, e) in [(70, 200, 1.6), (150, 190, 1.2), (470, 192, 1.3), (548, 202, 1.7)]:
        pared = lz.poligono([(cx - 9 * e, cy), (cx - 9 * e, cy - 9 * e), (cx + 9 * e, cy - 9 * e), (cx + 9 * e, cy)])
        lz.sombrear(pared, ["#0d0c19", "#151527", "#2a2d4c", "#3b4063"], 3 * e, (0.6, 0.3, 0.5))
        lz.sombrear(lz.poligono([(cx - 12 * e, cy - 8.5 * e), (cx, cy - 18 * e), (cx + 12 * e, cy - 8.5 * e)]),
                    ["#0d0c19", "#151527", "#2a2d4c"], 3 * e, (0.6, 0.3, 0.5))
        for dx_ in (-4.5, 4.5):
            v_ = lz.poligono([(cx + (dx_ - 2) * e, cy - 6.5 * e), (cx + (dx_ + 2) * e, cy - 6.5 * e), (cx + (dx_ + 2) * e, cy - 3 * e), (cx + (dx_ - 2) * e, cy - 3 * e)])
            lz.pintar(v_, rampa(["#ef8a26", "#f9b947", "#fde27e"], lz.ruido(1, 2)))
            lz.sumar_luz(lz.desenfocar(v_, 6 * e), "#ef8a26", 0.6)
    # el suelo de la plaza
    suelo = np.clip((lz.y - 196) * lz.s, 0, 1)
    lz.pintar(suelo, rampa(["#0d0c19", "#151527", "#1e2038"], lz.ruido(3, 3)))
    # guirnaldas de farolillos: del árbol a las casas
    rng = np.random.default_rng(73)
    for (p0, p1, p2) in [((300, 90), (200, 140), (80, 160)), ((300, 90), (400, 140), (530, 160)), ((300, 120), (230, 170), (150, 166)),
                         ((300, 120), (370, 172), (470, 168)), ((60, 120), (130, 150), (190, 130))]:
        c = lz.curva(p0, p1, p2, n=60)
        lz.pintar(lz.trazo(c, 0.6), "#2a2d4c", 0.9)
        for k in range(3, 60, 6):
            fx_, fy_ = c[k]
            col = [("#ef8a26", "#f9b947"), ("#b03a44", "#e98378"), ("#df9022", "#fde27e"), ("#3e9a35", "#b8ef8e")][rng.integers(4)]
            f_ = lz.elipse(fx_, fy_ + 3, 2.2, 2.8)
            lz.sumar_luz(lz.desenfocar(f_, 6), col[0], 0.6)
            lz.pintar(f_, rampa(list(col), np.clip(1 - np.hypot(lz.x - fx_, lz.y - fy_ - 3) / 3, 0, 1)))
    # la hoguera
    for (a0, a1) in [((282, 220), (318, 212)), ((284, 212), (316, 220))]:
        lz.sombrear(lz.trazo([a0, a1], 5), MADERA[:4], 2, (0, -1, 0.5))
    fuego = llamas(lz, fuego_xy[0], 216, 22, 40, semilla=7, n=9)
    lz.sumar_luz(lz.desenfocar(fuego, 30), "#d45a17", 0.6)
    # el charco de luz de la hoguera en el suelo de la plaza
    charco = np.clip(1 - np.hypot((lz.x - fuego_xy[0]) / 170, (lz.y - 228) / 34), 0, 1) * (lz.y > 198)
    lz.sumar_luz(charco ** 1.3, "#d4782a", 0.55)
    # los vecinos alrededor del fuego (unos bailan, otros miran): la hoguera les ilumina la cara y el pecho
    FUEGO_PELO = ["#140a06", "#2e170c", "#5a2e16", "#8a4a22", "#c0703a", "#e8a058", "#ffd08a"]
    FUEGO_CREMA = ["#3a2014", "#7a4a2a", "#b87a48", "#e0a868", "#f4c88a", "#ffe4b0"]
    for (vx, vy, e, m_, kw_) in [(232, 228, 1.4, 1, dict(brazo_alto=True)), (262, 236, 1.0, 1, dict(cria=True)),
                                 (372, 230, 1.5, -1, dict(sombrero=True, brazo_alto=True)), (338, 240, 1.1, -1, dict(cria=True, brazo_alto=True)),
                                 (186, 238, 1.6, 1, dict(chal=True)), (420, 242, 1.7, -1, dict(delantal=True))]:
        hacia_fuego = 1 if vx < fuego_xy[0] else -1
        castor(lz, vx, vy, e, m_, luz=(hacia_fuego * 0.85, -0.25, 0.45), recorte=("#ffd890", 0.7), recorte_dir=(hacia_fuego, -0.2),
               rampa_pelo=FUEGO_PELO, crema=FUEGO_CREMA, sem=int(vx), mirada=(1, -1), **kw_)
    # chispas que suben al cielo
    ch = np.zeros((lz.H, lz.W))
    for i in range(40):
        ch = np.maximum(ch, lz.circulo(300 + (rng.random() - 0.5) * 80, 200 - rng.random() * 160, 0.4 + rng.random() * 0.6) * rng.random())
    lz.sumar_luz(ch, "#fde27e", 1.0)
    marco_recuerdo(lz)
    return lz


def recuerdo_ojos():
    """«Oscuridad. Unos ojos violetas que no parpadean. Y una voz, muy lejos: «...despierta».»
    Todo negro, con humo violeta que se mueve muy despacio. Arriba, los ojos de Giza, enormes.
    Abajo, pequeño, un brote de luz que empieza a brillar."""
    lz = Lienzo(W, H, semilla=8)
    lz.pintar(np.ones((lz.H, lz.W)), "#05030a")
    r1 = ruido_torcido(lz, 40, 5, semilla=81, torcer=40)
    dens = (r1 * 0.9 + 0.1) * np.clip(1 - (lz.y - 20) / 230, 0.2, 1)
    alfa_h, luz_h = humo_volumen(lz, dens, luz=(0, 1), paso=3.0, umbral=(0.4, 0.75))
    lz.pintar(alfa_h, rampa(["#05030a", "#0d0716", "#170c26", "#2f1547"], luz_h * 0.9), 0.9)
    # grietas violetas que se abren en la oscuridad
    grietas = np.clip(1 - np.abs(lz.ruido(30, 3, semilla=82) - 0.5) * 50, 0, 1) * np.clip((lz.y - 120) / 120, 0, 1)
    lz.sumar_luz(lz.desenfocar(grietas, 2), "#4d1a6b", 0.8)
    lz.sumar_luz(grietas, "#a24fd0", 0.5)
    # los ojos
    for (ox, oy, ang) in [(220, 82, 10), (380, 82, -10)]:
        ojo_giza(lz, ox, oy, 44, 12, ang, 1.2)
    # el brote de luz abajo, en el centro
    bx, by = 300, 214
    lz.sumar_luz(lz.desenfocar(lz.circulo(bx, by, 6), 30), "#f9b947", 0.7)
    lz.sumar_luz(lz.desenfocar(lz.circulo(bx, by, 4), 8), "#fde27e", 0.8)
    semilla_m = lz.elipse(bx, by + 4, 5, 3.4)
    lz.sombrear(semilla_m, ["#7a4a2a", "#e8b860", "#ffe08a", "#fff3c4"], 2.5, (-0.4, -0.8, 0.5))
    tallo = lz.trazo(lz.curva((bx, by + 1), (bx + 0.6, by - 4), (bx + 1, by - 7), n=10), 1.0)
    hojas_ = np.maximum(lz.elipse(bx - 2.8, by - 7.6, 3.2, 1.4, 25), lz.elipse(bx + 4.2, by - 8.6, 3.2, 1.4, -25))
    lz.sombrear(np.maximum(tallo, hojas_), ["#1f4a1a", "#3e9a35", "#6fcf4f", "#b8ef8e"], 1.0, (-0.4, -0.8, 0.5))
    rayos_b = lz.rayos(lz.circulo(bx, by - 2, 3), (bx, by - 2), largo=0.95, pasos=30)
    lz.sumar_luz(rayos_b * 3, "#fde27e", 0.5)
    marco_recuerdo(lz, color="#d9cfe0", semilla=91)
    return lz


def recuerdo_estrella():
    """«Una luz que cae del cielo, como una estrella... y cae aquí, en el corazón del mundo.»
    Una noche muy clara sobre el Kitovu dormido, con la Vía Láctea. Una luz verde y dorada cruza el cielo
    con una estela larga y cae junto al árbol viejo del centro del valle."""
    lz = Lienzo(W, H, semilla=9)
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#07060d", "#0d0c19", "#151527", "#1e2038", "#2a2d4c", "#335777"], desde=-10, hasta=200))
    # la Vía Láctea: una banda de polvo de estrellas cruzada
    banda = np.exp(-(((lz.y - 40) - (lz.x - 300) * -0.35) / 34) ** 2)
    polvo = lz.ruido(10, 5, semilla=92)
    lz.sumar_luz(banda * polvo * 0.9, "#535a80", 0.8)
    lz.sumar_luz(banda * np.clip((polvo - 0.55) * 3, 0, 1), "#dcaaf2", 0.25)
    estrellas(lz, 220, 190, semilla=93)
    rng = np.random.default_rng(94)
    finas = np.zeros((lz.H, lz.W))
    for _ in range(400):
        finas = np.maximum(finas, lz.circulo(rng.random() * 600, rng.random() * 200, 0.3) * rng.random() * banda.max())
    lz.sumar_luz(finas * (0.3 + banda), "#e8f0dc", 0.8)
    # el valle dormido y el árbol viejo
    for base, amp, cols, sem in [(176, 20, ["#0d0c19", "#151527", "#1e2038"], 95), (196, 12, ["#07060d", "#0d0c19", "#151527"], 96)]:
        lz.pintar(mascara_bajo(lz, linea_horizonte(lz, base, amp, 260, sem)), rampa(cols, lz.ruido(6, 3) * 0.7 + 0.15))
    arbol_grande(lz, 330, 208, 80, 100, luz=(-0.8, -0.3, 0.5), semilla=97,
                 rampa_copa=["#05040a", "#0d0c19", "#151527", "#1e2038", "#2a2d4c"], rampa_tronco=["#07060d", "#0d0c19", "#151527", "#1e2038"])
    # la luz que cae, con su estela
    cabeza = (282, 196)
    estela = lz.curva((-20, -10), (150, 30), (230, 110), cabeza, n=90)
    trazo_e = lz.trazo(estela, 0.5, 7)
    lz.sumar_luz(lz.desenfocar(trazo_e, 10), "#3e9a35", 0.7)
    lz.sumar_luz(lz.desenfocar(trazo_e, 6), "#3e9a35", 0.8)
    lz.sumar_luz(lz.desenfocar(trazo_e, 2), "#6fcf4f", 0.8)
    lz.sumar_luz(lz.trazo(estela, 0.2, 2.2), "#fff8d2", 1.0)
    # chispas que se desprenden
    ch = np.zeros((lz.H, lz.W))
    for k in range(10, 80, 3):
        px_, py_ = estela[k]
        ch = np.maximum(ch, lz.circulo(px_ + (rng.random() - 0.5) * 14, py_ + rng.random() * 10, 0.5 + rng.random() * 0.8))
    lz.sumar_luz(ch, "#b8ef8e", 0.9)
    # el resplandor donde cae: ilumina el árbol y el valle
    lz.sumar_luz(lz.desenfocar(lz.circulo(*cabeza, 6), 60), "#3e9a35", 0.5)
    lz.sumar_luz(lz.desenfocar(lz.circulo(*cabeza, 5), 18), "#fde27e", 0.8)
    lz.sumar_luz(lz.rayos(lz.circulo(*cabeza, 4), cabeza, largo=0.96, pasos=40) * 3, "#fff8d2", 0.6)
    lz.pintar(lz.circulo(*cabeza, 3.2), "#fff8d2")
    marco_recuerdo(lz, color="#e3e8d6", semilla=98)
    return lz


# ---------------------------------------------------------------- Maisha
DORADO = ["#7a4a2a", "#a8693a", "#e8b860", "#f5cc78", "#ffe08a", "#fff3c4"]


def maisha(lz, x, y, e=1.0, vista="lado", mira=1, luz=(-0.6, -0.7, 0.5), con_cetro=True, cetro_alto=False,
           recorte=None, recorte_dir=(1, 0), brillo=0.5):
    """Maisha, el espíritu del bosque: cabeza grande, cuerpo pequeño, el brote arriba y el corazón que late.
    vista = "lado" (de tres cuartos), "frente" o "espalda". (x, y) es el suelo bajo sus pies; e=1 → 30 px."""
    m = mira
    def X(dx):
        return x + dx * e * m
    def Y(dy):
        return y - dy * e
    kw = dict()
    if recorte:
        kw.update(recorte=recorte, recorte_dir=recorte_dir)
    lz.pintar(lz.desenfocar(lz.elipse(x, y, 7 * e, 1.8 * e), 0.8), "#0a0608", 0.45)
    # el halo de luz que la rodea
    if brillo:
        lz.sumar_luz(lz.desenfocar(lz.elipse(x, Y(14), 12 * e, 14 * e), 6 * e), "#f9b947", 0.35 * brillo)
    # piernas
    for dx in (-2.2, 2.2):
        pierna = lz.trazo([(X(dx), Y(6)), (X(dx * 1.05), Y(0.8))], 2.8 * e, 2.6 * e)
        lz.sombrear(pierna, DORADO, 1.4 * e, luz, **kw)
    # brazo de detrás
    if vista != "espalda":
        brazo2 = lz.trazo([(X(-3.5), Y(10.5)), (X(-5.5), Y(7))], 2.4 * e, 2.2 * e)
        lz.sombrear(brazo2, DORADO[:5], 1.2 * e, luz, **kw)
    # cuerpo
    cuerpo = lz.elipse(X(0), Y(8.5), 5.2 * e, 5.6 * e)
    lz.sombrear(cuerpo, DORADO, 4 * e, luz, **kw)
    # el corazón luminoso del pecho
    if vista != "espalda":
        cx_ = X(1.2 if vista == "lado" else 0)
        corazon = lz.circulo(cx_, Y(9.5), 1.3 * e)
        lz.sumar_luz(lz.desenfocar(corazon, 2.5 * e), "#e98378", 0.7)
        lz.pintar(corazon, rampa(["#d5525e", "#e98378", "#ffd8d0"], np.clip(1 - np.hypot(lz.x - cx_, lz.y - Y(9.8)) / (1.3 * e), 0, 1)))
    # cabeza (grande)
    hx, hy = X(0.6 if vista == "lado" else 0), Y(20)
    cabeza = lz.elipse(hx, hy, 8.4 * e, 7.8 * e)
    lz.sombrear(cabeza, DORADO, 6 * e, luz, **kw)
    if vista != "espalda":
        dx_ojos = [(2.6, 1.0)] if vista == "lado" else [(-2.8, 1.0), (2.8, 1.0)]
        for (ox_, s_) in dx_ojos:
            ox, oy = hx + ox_ * e * m, hy + 0.2 * e
            ojo = lz.elipse(ox, oy, 1.25 * e * s_, 1.9 * e)
            lz.sombrear(ojo, ["#120b08", "#2a160c", "#3b2416"], 1 * e, luz)
            lz.pintar(lz.circulo(ox - 0.4 * e * m, oy - 0.8 * e, 0.5 * e), "#ffffff")
            lz.pintar(lz.circulo(ox + 0.35 * e * m, oy + 0.7 * e, 0.25 * e), "#e8f0dc", 0.7)
            lz.pintar(lz.desenfocar(lz.elipse(ox + 0.6 * e * m, oy + 2.6 * e, 1.6 * e, 0.8 * e), 0.4 * e), "#e98378", 0.55)
    # brazo de delante (con el cetro)
    if cetro_alto:
        brazo = lz.trazo([(X(3.5), Y(11)), (X(6.5), Y(15))], 2.4 * e, 2.2 * e)
        mano = (X(6.8), Y(15.5))
    else:
        brazo = lz.trazo([(X(3.5), Y(11)), (X(5.8), Y(7.2))], 2.4 * e, 2.2 * e)
        mano = (X(6), Y(7))
    if con_cetro and vista != "espalda":
        cetro(lz, mano[0] + 0.5 * e * m, y + (1 if not cetro_alto else -6) * e, mano[1] - (13 if not cetro_alto else 16) * e, e=0.62 * e, luz=luz, brilla=0.8)
    lz.sombrear(brazo, DORADO, 1.2 * e, luz, **kw)
    lz.sombrear(lz.circulo(*mano, 1.4 * e), DORADO, 1 * e, luz)
    if con_cetro and vista == "espalda":
        cetro(lz, X(6), Y(-0.5), Y(19), e=0.62 * e, luz=luz, brilla=0.8)
    # el brote de la cabeza
    tallo = lz.trazo(lz.curva((hx, hy - 7.2 * e), (hx + 0.4 * e * m, hy - 10 * e), (hx + 0.8 * e * m, hy - 11.5 * e), n=10), 0.9 * e, 0.7 * e)
    lz.pintar(tallo, "#3e9a35")
    for (lx_, ang) in [(-2.6, 28), (3.4, -24)]:
        hoja = lz.elipse(hx + (lx_ + 0.5) * e * m, hy - 12 * e, 2.8 * e, 1.25 * e, ang * m)
        lz.sombrear(hoja, ["#1f4a1a", "#3e9a35", "#6fcf4f", "#b8ef8e"], 1 * e, luz)
    return cabeza


# ---------------------------------------------------------------- Mzizi y el Arco
PIEDRA_MZ = ["#18191a", "#2b2c30", "#3d3f43", "#525458", "#6a6c6f", "#85878a", "#a3a4a6"]
MADERA_VIVA = ["#2a160c", "#4a2a16", "#73432a", "#96603b", "#b7814f", "#d6a76c", "#ecd09a"]


def punta_raiz(lz, base, punta, ancho, curva=0.0):
    """La silueta de una punta de raíz (como Mzizi): ancha abajo, ovalada y acabada en punta."""
    bx, by = base
    px_, py_ = punta
    pts_i, pts_d = [], []
    for k in range(48):
        tt = k / 47
        w_ = ancho * (1 - tt) ** 0.75 * min(1.0, (tt + 0.25) * 1.9) ** 0.7
        cx = bx + (px_ - bx) * tt + np.sin(tt * np.pi) * curva
        cy = by + (py_ - by) * tt
        pts_i.append((cx - w_, cy))
        pts_d.append((cx + w_, cy))
    return lz.poligono(pts_i + pts_d[::-1])


def hebra(lz, puntos, g0, g1, colores, luz=(-0.7, -0.6, 0.5), semilla=0, fuerza_tex=0.4):
    """Una raíz gruesa y redonda que sigue un camino, con corteza en surcos a lo largo."""
    m = lz.trazo(puntos, g0, g1)
    # surcos de corteza: ruido estirado en la dirección media del camino
    pts = np.array(puntos, float)
    d = pts[-1] - pts[0]
    ang = np.degrees(np.arctan2(d[1], d[0]))
    n = lz.ruido(0.9, 3, semilla=semilla).astype(np.float32)
    largo = 15
    k = np.zeros((largo, largo), np.float32)
    cv2.line(k, (0, largo // 2), (largo - 1, largo // 2), 1.0, 1)
    M = cv2.getRotationMatrix2D((largo / 2 - 0.5, largo / 2 - 0.5), -ang, 1.0)
    k = cv2.warpAffine(k, M, (largo, largo))
    k /= k.sum() + 1e-6
    n = cv2.filter2D(n, -1, k)
    n = (n - n.min()) / (np.ptp(n) + 1e-6)
    lz.sombrear(m, colores, max(g0, g1) * 0.5, luz, textura=n, fuerza_tex=fuerza_tex)
    return m


def arco_vivo(lz, cx, base, ancho, alto, colores, luz=(-0.6, -0.6, 0.5), hebras=5, semilla=0, vida=None):
    """El Arco de Raíz grande: varias raíces que suben trenzándose y se juntan arriba.
    vida = (color, fuerza): una luz que corre por el centro de cada raíz."""
    rng = np.random.default_rng(semilla)
    total = np.zeros((lz.H, lz.W))
    caminos = []
    for k in range(hebras):
        fase = k / hebras * 2 * np.pi
        grosor = ancho * (0.05 + 0.025 * rng.random())
        pts = []
        for a in np.linspace(-0.08, np.pi + 0.08, 80):
            tr = np.sin(a * 3 + fase) * ancho * 0.035
            r_x = ancho / 2 - ancho * 0.07 + tr
            r_y = alto - alto * 0.07 + tr
            pts.append((cx + np.cos(a) * r_x, base - np.sin(a) * r_y))
        caminos.append((pts, grosor))
    # de atrás hacia delante, alternando, para que parezcan trenzadas
    for k, (pts, g) in enumerate(caminos):
        m = hebra(lz, pts, g * 1.3, g, colores, luz, semilla=semilla + k)
        lz.pintar(np.clip(lz.desenfocar(m, 1.0) - m, 0, 1), "#0d0a0a", 0.5)
        total = np.maximum(total, m)
        if vida:
            nucleo = lz.trazo(pts, g * 0.22, g * 0.15) * (np.sin(lz.x * 0.08 + k) * 0.5 + 0.5 > 0.25)
            lz.sumar_luz(lz.desenfocar(nucleo, g * 0.4), vida[0], 0.6 * vida[1])
            lz.sumar_luz(nucleo, "#fff8d2", 0.5 * vida[1])
    # raicillas que cuelgan por dentro y pies que se agarran al suelo
    for k in range(10):
        a = 0.3 + rng.random() * (np.pi - 0.6)
        x0 = cx + np.cos(a) * (ancho / 2 - ancho * 0.12)
        y0 = base - np.sin(a) * (alto - alto * 0.12)
        largo = alto * (0.06 + rng.random() * 0.12)
        total = np.maximum(total, hebra(lz, lz.curva((x0, y0), (x0 + (rng.random() - 0.5) * 8, y0 + largo * 0.6), (x0 + (rng.random() - 0.5) * 12, y0 + largo), n=12),
                                         ancho * 0.012, ancho * 0.003, colores, luz, semilla=semilla + 30 + k, fuerza_tex=0.2))
    for lado in (-1, 1):
        for k in range(3):
            x0 = cx + lado * (ancho / 2 - ancho * 0.07)
            total = np.maximum(total, hebra(lz, lz.curva((x0, base - 6), (x0 + lado * (10 + k * 8), base - 2), (x0 + lado * (20 + k * 14), base + 3 + k), n=14),
                                             ancho * 0.03, ancho * 0.008, colores, luz, semilla=semilla + 50 + k))
    return total


def tramo_raiz(lz, x, y, rx, ry, ang, colores, luz, semilla=0, fuerza_tex=0.5):
    """Un tramo del cuerpo de una raíz gigante: un bulto ovalado con surcos y un nudo oscuro alrededor."""
    m = lz.elipse(x, y, rx, ry, ang)
    a = np.radians(ang)
    # surcos a lo largo del cuerpo (perpendiculares al eje corto del óvalo)
    u = (lz.x - x) * np.cos(a) + (lz.y - y) * np.sin(a)
    v = -(lz.x - x) * np.sin(a) + (lz.y - y) * np.cos(a)
    surcos = np.clip(np.abs(np.sin(v / ry * 6 + np.sin(u * 0.3 + semilla) * 0.6)) * 1.2, 0, 1)
    tex = surcos * 0.6 + lz.ruido(0.8, 2, semilla=semilla) * 0.4
    lz.sombrear(m, colores, min(rx, ry) * 0.8, luz, textura=tex, fuerza_tex=fuerza_tex)
    anillo = np.clip(1 - np.abs(np.abs(u) / rx - 0.92) * 14, 0, 1) * m
    lz.pintar(anillo, colores[0], 0.7)
    return m


def mzizi_madera():
    """«La piedra se cae a trozos: debajo, Mzizi vuelve a ser madera viva.»
    Plano desde abajo. Mzizi, la raíz del Arco, se alza en una gran S. Abajo aún es piedra que revienta
    en pedazos; arriba ya es madera viva. Su cabeza, una punta de raíz enorme con una corona de placas de
    corteza abiertas como pétalos, mira a Maisha: sus ojos de grieta ya no son violetas, brillan ámbar.
    El humo de Giza se escapa hacia arriba y el sol rompe las nubes detrás. Maisha, pequeña, alza el cetro."""
    lz = Lienzo(W, H, semilla=10)
    sol = (420, 40)
    # cielo de tormenta que se abre: gris violáceo arriba, oro detrás de Mzizi
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#1e2038", "#3b4063", "#6a6c6f", "#c96d4f", "#f1c27a"], desde=-20, hasta=200))
    lz.sumar_luz(np.clip(1 - np.hypot(lz.x - sol[0], (lz.y - sol[1]) * 1.4) / 300, 0, 1) ** 2, "#f9b947", 0.8)
    # nubes de tormenta en bandas suaves, con el borde de abajo encendido por el sol
    for (cy_, alto_, fuerza, sem) in [(26, 24, 0.85, 131), (78, 14, 0.6, 132), (120, 10, 0.45, 133)]:
        banda = np.exp(-((lz.y - cy_) / alto_) ** 2)
        n_ = lz.desenfocar(ruido_torcido(lz, 30, 4, semilla=sem, torcer=30), 2)
        forma_n = np.clip((n_ * banda - 0.32) * 3, 0, 1) * np.clip(1 - np.hypot(lz.x - sol[0], lz.y - sol[1]) / 90, 0.25, 1)
        borde_luz = np.clip(desplazar(lz, forma_n, 0, -3) - forma_n * 0.6, 0, 1)
        col_n = rampa(["#2a2d4c", "#3b4063", "#535a80", "#6a5a78"], n_ * 0.8)
        lz.pintar(forma_n, col_n, fuerza)
        lz.pintar(np.clip(forma_n - desplazar(lz, forma_n, 0, 2.5), 0, 1), rampa(["#c96d4f", "#f1c27a"], n_), 0.8 * fuerza)
    # rayos de sol entre las nubes
    lz.sumar_luz(lz.rayos(lz.desenfocar(lz.circulo(*sol, 24), 4), sol, largo=0.985, pasos=60) * 2.2, "#fde27e", 0.5)
    # el Arco de piedra al fondo, a la izquierda, y montañas
    lz.pintar(mascara_bajo(lz, linea_horizonte(lz, 200, 20, 260, 132)), rampa(["#2b2c30", "#3d3f43", "#525458"], lz.ruido(8, 3) * 0.6 + 0.2))
    arco_vivo(lz, 150, 206, 90, 92, PIEDRA_MZ[:6], semilla=33)
    # el suelo de la arena: piedra gris; alrededor de Mzizi vuelve la hierba en una ola
    suelo = mascara_bajo(lz, linea_horizonte(lz, 222, 3, 300, 133))
    lz.pintar(suelo, rampa(["#1b1c1f", "#2b2c30", "#3d3f43", "#525458"], np.clip(0.4 + (lz.ruido(3, 3) - 0.5) * 0.4 + (lz.y - 222) / 200, 0, 1)))
    verde = np.clip(1 - np.hypot((lz.x - 470) / 260, (lz.y - 246) / 34) + (lz.ruido(6, 3) - 0.5) * 0.35, 0, 1)
    lz.pintar(suelo * np.clip(verde * 3, 0, 1), rampa(HIERBA[2:7], np.clip(0.4 + (lz.ruido(2, 3) - 0.5) * 0.6, 0, 1)))
    lz.sumar_luz(np.clip(1 - np.abs(verde * 3 - 0.5) * 3, 0, 1) * suelo, "#fde27e", 0.5)
    flores(lz, 26, (300, 230, 600, 256), [["#8f2532", "#d5525e", "#e98378"], ["#b2721a", "#df9022", "#f1c27a"], ["#c4ddd0", "#e8f0dc", "#ffffff"]], semilla=134, tam=1.4)
    luz_m = (0.6, -0.2, 0.55)        # contraluz: la luz fuerte viene de detrás (arriba a la derecha)
    rng = np.random.default_rng(135)
    # escombros de piedra al pie de Mzizi
    for k in range(18):
        fx_, fy_ = 470 + rng.random() * 130, 236 + rng.random() * 18
        tam = 3 + rng.random() * 6
        pts = [(fx_ + np.cos(b_) * tam * (0.6 + rng.random() * 0.6), fy_ + np.sin(b_) * tam * 0.6 * (0.6 + rng.random() * 0.6)) for b_ in np.linspace(0, 2 * np.pi, 7)[:-1]]
        lz.sombrear(lz.poligono(pts), PIEDRA_MZ, tam * 0.4, luz_m)
    # el cuerpo principal: una gran S desde el suelo hasta el cuello
    camino = lz.curva((560, 272), (610, 180), (430, 200), (420, 132), n=17)
    cuerpo = np.zeros((lz.H, lz.W))
    for k, (cx_, cy_) in enumerate(camino):
        tt = k / (len(camino) - 1)
        r = 31 - tt * 11
        siguiente = camino[min(k + 1, len(camino) - 1)]
        ang = np.degrees(np.arctan2(siguiente[1] - cy_, siguiente[0] - cx_)) + 90
        es_piedra = tt < 0.42
        m = tramo_raiz(lz, cx_, cy_, r, r * 0.8, ang, PIEDRA_MZ[:6] if es_piedra else MADERA_VIVA, luz_m, semilla=k + 20)
        cuerpo = np.maximum(cuerpo, m)
    # trozos de coraza que aún se agarran a la madera, con luz dorada por las grietas
    coraza = cuerpo * (lz.ruido(9, 3, semilla=136) > 0.58) * np.clip((lz.y - 120) / 50, 0, 1) * (lz.x > 440)
    lz.sombrear(coraza, PIEDRA_MZ, 5, luz_m, textura=lz.ruido(1, 2), fuerza_tex=0.3)
    borde_c = np.clip(lz.desenfocar(coraza, 1.5) - coraza, 0, 1) * cuerpo
    lz.sumar_luz(lz.desenfocar(borde_c, 2), "#f9b947", 0.9)
    lz.sumar_luz(borde_c, "#fff8d2", 0.6)
    grieta_v = np.clip(1 - np.abs(lz.ruido(6, 2, semilla=137) - 0.5) * 30, 0, 1) * cuerpo * (lz.y > 150)
    lz.sumar_luz(grieta_v, "#a24fd0", 0.6)
    # la corona: cuatro placas de corteza abiertas como pétalos detrás de la cabeza
    hx, hy = 394, 82
    for (ang, largo, ancho_p) in [(-150, 54, 16), (-105, 60, 17), (-60, 58, 17), (-18, 50, 15)]:
        a_ = np.radians(ang)
        cx_, cy_ = hx + np.cos(a_) * largo * 0.55, hy + 14 + np.sin(a_) * largo * 0.55
        # un pétalo en punta (como una hoja dura de corteza)
        ca, sa = np.cos(a_), np.sin(a_)
        pts_p = []
        for k2 in range(20):
            tt = k2 / 19
            w_ = ancho_p * np.sin(np.pi * tt) ** 0.7 * (1 - tt * 0.3)
            pts_p.append((hx + ca * largo * tt - sa * w_, hy + 14 + sa * largo * tt + ca * w_))
        for k2 in range(19, -1, -1):
            tt = k2 / 19
            w_ = ancho_p * np.sin(np.pi * tt) ** 0.7 * (1 - tt * 0.3)
            pts_p.append((hx + ca * largo * tt + sa * w_, hy + 14 + sa * largo * tt - ca * w_))
        petalo = lz.poligono(pts_p)
        nervio = np.clip(1 - np.abs((lz.x - cx_) * np.sin(a_) - (lz.y - cy_) * np.cos(a_)) / 1.2, 0, 1) * petalo
        lz.sombrear(petalo, MADERA_VIVA[:6], ancho_p * 0.6, luz_m, textura=vetas_c(lz, 0.7, 9, False, int(ang)), fuerza_tex=0.4)
        lz.pintar(nervio, "#2a160c", 0.6)
        borde_p = np.clip(petalo - lz.desenfocar(petalo, 1.2), 0, 1) * 2
        lz.pintar(np.clip(borde_p, 0, 1), "#fde27e", 0.5)
    # la cabeza: una punta de raíz enorme, inclinada hacia Maisha
    cabeza = punta_raiz(lz, (406, 134), (356, 22), 40, curva=-10)
    lz.sombrear(cabeza, MADERA_VIVA, 26, luz_m, textura=vetas_c(lz, 1.0, 15, False, 138), fuerza_tex=0.5)
    for k in range(6):
        ny_ = 126 - k * 17
        lz.pintar(cabeza * np.clip(1 - np.abs(lz.y - ny_ - (lz.x - 380) * 0.35 - np.sin((lz.x - 380) / 10) * 2) / 1.2, 0, 1), "#2a160c", 0.55)
    # la cara: ojos de grieta, ahora ámbar, y la costura de la boca con luz
    for (ox, oy, ang) in [(372, 88, 22), (402, 84, -18)]:
        ojo = lz.elipse(ox, oy, 8.5, 2.4, ang)
        lz.pintar(lz.elipse(ox, oy - 2.5, 10, 3.4, ang) * cabeza, "#2a160c", 0.75)
        lz.sumar_luz(lz.desenfocar(ojo, 6), "#ef8a26", 0.8)
        lz.pintar(ojo, rampa(["#ef8a26", "#f9b947", "#fde27e", "#fff8d2"], np.clip(1 - np.hypot((lz.x - ox) / 8.5, (lz.y - oy) / 2.4), 0, 1)))
    boca = lz.trazo(lz.curva((376, 110), (388, 114), (402, 108), n=16), 1.8, 1.0)
    lz.sumar_luz(lz.desenfocar(boca, 3), "#f9b947", 0.8)
    lz.pintar(boca, "#fde27e")
    # contorno dorado de contraluz en todo Mzizi
    todo = np.clip(cuerpo + cabeza, 0, 1)
    lz.sumar_luz(lz.desenfocar(todo, 6) * (1 - todo), "#f9b947", 0.7)
    dist_t = lz.distancia(todo)
    gy, gx = np.gradient(lz.desenfocar(dist_t, 1.0))
    filo = np.clip(1 - dist_t / 2.2, 0, 1) * np.clip((-gx * 0.6 + gy * 0.8) / (np.hypot(gx, gy) + 1e-6), 0, 1) * (todo > 0.5)
    lz.pintar(filo, "#fde27e", 0.75)
    # el brote nuevo en la punta
    tip = (356, 22)
    lz.sumar_luz(lz.desenfocar(lz.circulo(*tip, 6), 18), "#b8ef8e", 0.6)
    lz.pintar(lz.trazo(lz.curva(tip, (tip[0] - 2, tip[1] - 6), (tip[0] - 1, tip[1] - 10), n=10), 2, 1.2), "#3e9a35")
    for (hx_, hy_, a_) in [(tip[0] - 8, tip[1] - 10, 25), (tip[0] + 6, tip[1] - 12, -30)]:
        lz.sombrear(lz.elipse(hx_, hy_, 7, 2.8, a_), ["#1f4a1a", "#3e9a35", "#6fcf4f", "#b8ef8e"], 2, (-0.6, -0.7, 0.5))
    # el humo de Giza que se escapa y se deshace
    humo_g = np.zeros((lz.H, lz.W))
    for k in range(5):
        c = lz.curva((470 + k * 14, 170 - k * 12), (520 + k * 10, 110), (480 + k * 30, 30 - k * 6), n=30)
        humo_g = np.maximum(humo_g, lz.trazo(c, 12, 3))
    dens_g = lz.desenfocar(humo_g, 4) * (0.4 + ruido_torcido(lz, 8, 4, semilla=139, torcer=12) * 0.8)
    alfa_g, luz_g = humo_volumen(lz, dens_g, luz=(-1, 0.4), paso=2.0, umbral=(0.35, 0.72))
    lz.pintar(alfa_g, rampa(["#0d0716", "#2f1547", "#55257a", "#a466cf"], luz_g), 0.7)
    lz.sumar_luz(lz.desenfocar(alfa_g, 4), "#7a2fa0", 0.3)
    # trozos de piedra que salen volando, con estela
    for k in range(34):
        a_ = rng.random() * 2 * np.pi
        d_ = 60 + rng.random() * 140
        ox_, oy_ = 500, 190
        fx_, fy_ = ox_ + np.cos(a_) * d_ * 1.3, oy_ + np.sin(a_) * d_ * 0.6 - 30
        if fy_ > 250 or (fx_ < 200):
            continue
        tam = 2 + rng.random() * 6
        pts = [(fx_ + np.cos(b) * tam * (0.6 + rng.random() * 0.6), fy_ + np.sin(b) * tam * (0.6 + rng.random() * 0.6)) for b in np.linspace(0, 2 * np.pi, 6)[:-1] + rng.random()]
        estela = lz.trazo([(fx_, fy_), (fx_ - np.cos(a_) * tam * 3, fy_ - np.sin(a_) * tam * 1.6)], tam * 0.8, 0.3)
        lz.pintar(lz.desenfocar(estela, 1), "#a3a4a6", 0.25)
        lz.sombrear(lz.poligono(pts), PIEDRA_MZ, tam * 0.4, luz_m)
        lz.sumar_luz(lz.desenfocar(lz.circulo(fx_, fy_, tam * 0.4), 1.5), "#a24fd0", 0.3)
    # polvo dorado en el aire
    motas = np.zeros((lz.H, lz.W))
    for _ in range(70):
        motas = np.maximum(motas, lz.circulo(250 + rng.random() * 350, rng.random() * 240, 0.4 + rng.random() * 0.6) * rng.random())
    lz.sumar_luz(motas, "#fde27e", 0.9)
    # Maisha, abajo a la izquierda, con el cetro en alto
    maisha(lz, 96, 248, 2.5, "lado", 1, luz=(0.7, -0.5, 0.5), cetro_alto=True, recorte=("#fde27e", 0.8), recorte_dir=(1, -0.3))
    vin = np.clip(np.hypot((lz.x - 330) / 380, (lz.y - 128) / 200) - 0.58, 0, 1)
    lz.pintar(vin, "#07060d", 0.6)
    return lz


def vetas_c(lz, escala=1.0, largo=21, horizontal=True, semilla=0):
    n = lz.ruido(escala, 3, semilla=semilla).astype(np.float32)
    k = np.ones((1, largo), np.float32) / largo if horizontal else np.ones((largo, 1), np.float32) / largo
    n = cv2.filter2D(n, -1, k)
    return (n - n.min()) / (np.ptp(n) + 1e-6)


def arco_despierta():
    """«La vida corre por la raíz hasta el Arco. El Arco de Raíz despierta.»
    El Arco, enorme, se llena de luz: por sus raíces trenzadas sube un río de vida dorada y, dentro,
    se abre la primera tierra: los Prados del Eco, verdes, con su río y el cielo azul. El viento trae
    hojas y pétalos. Maisha, de espaldas, lo mira."""
    lz = Lienzo(W, H, semilla=11)
    # el Kitovu aún gris, al atardecer
    lz.pintar(np.ones((lz.H, lz.W)), lz.gradiente(["#1e2038", "#2a2d4c", "#525458", "#6a6c6f", "#85878a"], desde=-10, hasta=200))
    cumulos(lz, [(90, 40, 90, 16), (520, 36, 90, 16)], luz=(0, -1), colores=("#2b2c30", "#3d3f43", "#525458", "#6a6c6f", "#85878a"))
    suelo = mascara_bajo(lz, linea_horizonte(lz, 206, 5, 300, 111))
    lz.pintar(suelo, rampa(["#2b2c30", "#3d3f43", "#525458"], np.clip(0.4 + (lz.ruido(4, 3) - 0.5) * 0.4, 0, 1)))
    cx, base, aw, ah = 300, 214, 300, 206
    # dentro del Arco: los Prados del Eco, de día, llenos de color
    dentro = lz.poligono([(cx - aw * 0.38, base)] + [(cx + np.cos(a) * aw * 0.38, base - np.sin(a) * ah * 0.86) for a in np.linspace(np.pi, 0, 40)] + [(cx + aw * 0.38, base)])
    pr = Lienzo(W, H, semilla=12)
    pr.pintar(np.ones((pr.H, pr.W)), pr.gradiente(["#4a7a93", "#6b9eab", "#97c1bf", "#e8f0dc"], desde=20, hasta=150))
    cumulos(pr, [(250, 70, 50, 12), (360, 56, 40, 10)], luz=(-1, -0.4))
    for base_, amp, cols, sem in [(150, 14, HIERBA[3:7], 112), (166, 10, HIERBA[2:7], 113), (184, 8, HIERBA[2:6], 114)]:
        pr.pintar(mascara_bajo(pr, linea_horizonte(pr, base_, amp, 160, sem)), rampa(cols, np.clip(0.5 + (pr.ruido(4, 3) - 0.5) * 0.5, 0, 1)))
    t_ = np.linspace(0, 1, 50)
    rio = pr.trazo(np.stack([300 + 30 * np.sin(t_ * 5) - 10 * t_, 150 + 70 * t_], 1), 1, 16)
    pr.pintar(rio, rampa(["#335777", "#6b9eab", "#c4ddd0"], pr.ruido(2, 2) * 0.5 + 0.3))
    for k in range(10):
        arbol(pr, 180 + k * 26 + (k % 3) * 5, 150 + (k % 4) * 4, 18, 12, luz=(-0.7, -0.6, 0.5), semilla=k + 120)
    flores(pr, 50, (190, 196, 410, 214), [["#8f2532", "#d5525e", "#e98378"], ["#b2721a", "#df9022", "#f1c27a"], ["#c4ddd0", "#e8f0dc", "#ffffff"]], semilla=121, tam=1.3)
    lz.pintar(dentro, pr.img)
    # luz que sale por el Arco y cae sobre el suelo gris (que empieza a tener color)
    lz.sumar_luz(lz.desenfocar(dentro, 18), "#fde27e", 0.45)
    haz = lz.poligono([(cx - aw * 0.38, base), (cx + aw * 0.38, base), (cx + aw * 0.6, 260), (cx - aw * 0.6, 260)])
    lz.sumar_luz(lz.desenfocar(haz, 8) * suelo, "#f8e1a6", 0.4)
    verde = np.clip(1 - np.hypot((lz.x - cx) / 240, (lz.y - 236) / 30) * 1.1 + (lz.ruido(5, 3) - 0.5) * 0.4, 0, 1) * suelo
    lz.pintar(np.clip(verde * 3, 0, 1), rampa(HIERBA[3:7], np.clip(0.5 + (lz.ruido(2, 3) - 0.5) * 0.6, 0, 1)), 0.9)
    # el Arco: raíces trenzadas, vivas, con la vida dorada subiendo por ellas
    arco = arco_vivo(lz, cx, base + 4, aw, ah, MADERA_VIVA, luz=(0.2, -0.6, 0.6), hebras=6, semilla=15, vida=("#f9b947", 1.0))
    # raíces que llegan por el suelo hasta el arco, brillando
    for (p0, p1) in [((-10, 250), (120, 222)), ((610, 248), (480, 224))]:
        raiz_luz(lz, lz.curva(p0, p1, (cx + (p0[0] - cx) * 0.38, base + 2), n=50), 5, semilla=abs(int(p0[0])) + 5, brillo=1.2)
    # hojas y pétalos que trae el viento desde dentro
    rng = np.random.default_rng(116)
    for k in range(40):
        hx_, hy_ = cx + (rng.random() - 0.5) * 360, 40 + rng.random() * 190
        if abs(hx_ - cx) < 40 and hy_ > 150:
            continue
        col = [["#1f4a1a", "#3e9a35", "#6fcf4f"], ["#8f2532", "#d5525e", "#f4b39a"], ["#b2721a", "#df9022", "#fde27e"]][k % 3]
        lz.sombrear(lz.elipse(hx_, hy_, 2.2, 1.0, rng.random() * 180), col, 0.8, (-0.6, -0.7, 0.5))
    # Maisha, de espaldas, mirando el Arco abierto
    maisha(lz, cx, 250, 2.4, "espalda", 1, luz=(0.0, -0.4, 0.6), recorte=("#fde27e", 0.9), recorte_dir=(0, -1), brillo=0.8)
    vin = np.clip(np.hypot((lz.x - 300) / 360, (lz.y - 128) / 190) - 0.6, 0, 1)
    lz.pintar(vin, "#07060d", 0.55)
    return lz


PIEZAS = {"1_kitovu_antes": kitovu_antes, "2_familia_shamba": familia_shamba, "3_leyenda": leyenda, "4_giza": giza, "5_piedra": piedra, "6_hoy": hoy, "recuerdo_1": recuerdo_aldea, "recuerdo_2": recuerdo_ojos, "recuerdo_3": recuerdo_estrella, "7_mzizi_madera": mzizi_madera, "8_arco_despierta": arco_despierta}


def main():
    # las del Bosque Cobrizo, la Ciénaga Quieta y el Campo Segado están en su propio archivo
    import cinematicas_bosque
    import cinematicas_cienaga
    import cinematicas_campo
    import cinematicas_sendero
    PIEZAS.update(cinematicas_sendero.PIEZAS)
    PIEZAS.update(cinematicas_bosque.PIEZAS)
    PIEZAS.update(cinematicas_cienaga.PIEZAS)
    PIEZAS.update(cinematicas_campo.PIEZAS)
    nombres = sys.argv[1:] or list(PIEZAS)
    for n in nombres:
        lz = PIEZAS[n]()
        lz.guardar(os.path.join(SALIDA, n + ".png"))
        print("pintada", n)


if __name__ == "__main__":
    main()
