"""EL SUELO DE UN MAPA, pintado con detalle (con el pintor de las cinemáticas).

    python3 herramientas/pintar_suelo.py kitovu

Lee el mapa de datos/mapas/<mapa>.txt (cada letra es una casilla de 16×16) y pinta el suelo entero en
arte/mundos/raiz/suelos/<mapa>_suelo.png:
  hierba   con manchas claras y oscuras, briznas con la punta iluminada, matas y tréboles
  flores   (las casillas «,») de varios colores, con su sombrita
  camino   tierra apisonada con piedrecitas, rodadas y la hierba que se come los bordes
  agua     clara en la orilla y honda en el centro, con ondas, brillos y la orilla mojada
  losas    piedras irregulares con volumen y juntas con musgo
  puente   tablas con vetas y clavos
construir_mapa.py lo usa para los mapas de MAPAS_PINTADOS (los demás siguen con el dibujo sencillo).
"""
import os
import sys
import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pintor import Lienzo, rampa, hex2, desplazar, RAIZ  # noqa: E402

CASILLA = 16
SUELOS = ".,#~=%/-|'\"0"
HIERBA_R = ["#1d2e18", "#2b4220", "#3f582f", "#526d38", "#6a8246", "#829856", "#9aa95f", "#b4bd78"]
TIERRA_R = ["#2b1e17", "#3f2c21", "#533b2d", "#684937", "#7c5843", "#91674f", "#a57559", "#bb8c6e"]
AGUA_R = ["#122626", "#1c3535", "#28484a", "#346161", "#407676", "#4c8d8d", "#5d9f9f", "#6db0b0", "#9fd0d0"]
PIEDRA_R = ["#2e302a", "#41443a", "#525649", "#666b5b", "#7a806d", "#8d9381", "#a0a596", "#bfc3b4"]
# el Bosque Cobrizo: suelo de musgo oscuro cubierto de hojarasca cobriza y rojiza
HIERBA_BOSQUE = ["#141f10", "#1d2e18", "#26381c", "#2f4422", "#3f582f", "#4d6436", "#5d793e", "#6a8246"]
HOJAS_BOSQUE = ["#3d3214", "#705425", "#a37036", "#c68756", "#472b14", "#794123", "#ab5031", "#cc6351", "#e0a874"]
# la Ciénaga Quieta: hierba húmeda verde oliva, agua quieta y turbia, barro en las orillas
HIERBA_CAMPO = ["#26200f", "#342c15", "#463b1c", "#5a4c24", "#6e5d2e", "#836f38", "#9a8445", "#b39c58"]
SURCO = ["#1d140f", "#2b1e17", "#3f2c21", "#533b2d", "#684937", "#7c5843"]
HIERBA_CIENAGA = ["#142019", "#1c2c22", "#26392a", "#324833", "#41583c", "#526845", "#657a52", "#7d8c62"]
AGUA_CIENAGA = ["#0e1c1a", "#142826", "#1c3532", "#24433f", "#2e524c", "#3a615a", "#4c7066", "#5d8074", "#8aa697"]
MADERA_R = ["#251812", "#3a261d", "#492e23", "#5b392b", "#6d4534", "#7f513d", "#905c45", "#a8735a"]


def leer(nombre):
    with open(os.path.join(RAIZ, "datos", "mapas", nombre + ".txt"), encoding="utf-8") as f:
        filas = [l.rstrip("\n") for l in f if not l.startswith(";")]
    ancho = max(len(f) for f in filas)
    return [f.ljust(ancho, ".") for f in filas]


def tipos_de(filas, derrumbe=False, escala=False):
    """El tipo de suelo de cada casilla (bajo los objetos, el que más se repite alrededor).
    «"» es una pasarela rota (agua), en el Camino Cobrizo (derrumbe=True) un derrumbe sobre el camino y en la
    Cañada del Eco (escala=True) la escala de cuerda, que cuelga por la peña."""
    def tipo(c):
        return {"~": "agua", "=": "puente", "#": "camino", "%": "losas", ",": "flores", "/": "surco",
                "-": "puente_piedra", "|": "pretil", "'": "vado", "\\": "agua",
                '"': "risco" if escala else ("camino" if derrumbe else "agua"),
                "0": "risco"}.get(c, "hierba")
    alto, ancho = len(filas), len(filas[0])
    tipos = [[tipo(c) for c in f] for f in filas]
    for y in range(alto):
        for x in range(ancho):
            if filas[y][x] in SUELOS:
                continue
            vecinos = [tipos[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                       if 0 <= x + dx < ancho and 0 <= y + dy < alto and filas[y + dy][x + dx] in SUELOS]
            vecinos = ["hierba" if v == "flores" else v for v in vecinos]
            if vecinos:
                tipos[y][x] = max(set(vecinos), key=vecinos.count)
    return tipos


def mascara(lz, tipos, cuales, radio, ruido_borde=0.18, semilla=0):
    """Máscara (0..1, al tamaño interno del lienzo) de unas casillas, con el borde redondeado e irregular."""
    alto, ancho = len(tipos), len(tipos[0])
    m = np.array([[1.0 if tipos[y][x] in cuales else 0.0 for x in range(ancho)] for y in range(alto)], np.float32)
    m = cv2.resize(m, (lz.W, lz.H), interpolation=cv2.INTER_NEAREST)
    m = cv2.GaussianBlur(m, (0, 0), radio * lz.s)
    n = lz.ruido(6, 3, semilla=semilla)
    return np.clip((m - 0.5 + (n - 0.5) * ruido_borde) * 6 + 0.5, 0, 1)


def estirar(campo, largo, vertical=True):
    k = np.ones((largo, 1), np.float32) / largo if vertical else np.ones((1, largo), np.float32) / largo
    c = cv2.filter2D(campo.astype(np.float32), -1, k)
    return (c - c.min()) / (np.ptp(c) + 1e-6)


def _hojarasca(lz, tipos, alto, ancho, por_fila=None, por_columna=None):
    """Hojas caídas por todo el suelo del bosque (muchas en la hierba, pocas en el camino, ninguna en el agua):
    cada hoja es una elipse pequeña con su color, su luz arriba y su sombra abajo a la derecha.
    por_fila(y): cuántas hojas hay en cada fila de casillas (0..1; en el Camino Cobrizo, más cuanto más al norte).
    por_columna(x): lo mismo por columnas (en la Cañada del Eco, más cuanto más al este, junto al bosque)."""
    rng = np.random.default_rng(33)
    densidad = np.zeros((alto, ancho))
    for y in range(alto):
        for x in range(ancho):
            densidad[y, x] = {"hierba": 1.0, "flores": 1.0, "camino": 0.25, "losas": 0.2, "risco": 0.03}.get(tipos[y][x], 0.0)
            if por_fila:
                densidad[y, x] *= por_fila(y)
            if por_columna:
                densidad[y, x] *= por_columna(x)
    mancha = lz.ruido(22, 3, semilla=34)
    hojas = np.zeros((lz.H, lz.W), np.float32)
    colores = np.zeros((lz.H, lz.W, 3), np.float32)
    sombras = np.zeros((lz.H, lz.W), np.float32)
    total = int(lz.w * lz.h / 11)
    xs = rng.random(total) * lz.w
    ys = rng.random(total) * lz.h
    pal = [hex2(cc) for cc in HOJAS_BOSQUE]
    for x, y in zip(xs, ys):
        tx, ty = int(x // CASILLA), int(y // CASILLA)
        if ty >= alto or tx >= ancho:
            continue
        prob = densidad[ty, tx] * np.clip((mancha[int(y * lz.s), int(x * lz.s)] - 0.32) * 2.4, 0.04, 1.0)
        if rng.random() > prob:
            continue
        ang = rng.random() * 180
        largo = (1.6 + rng.random() * 1.5) * lz.s
        corto = largo * (0.42 + rng.random() * 0.15)
        centro = (int(x * lz.s), int(y * lz.s))
        cv2.ellipse(sombras, (centro[0] + lz.s, centro[1] + lz.s), (int(largo), int(corto)), ang, 0, 360, 1.0, -1)
        cv2.ellipse(hojas, centro, (int(largo), int(corto)), ang, 0, 360, 1.0, -1)
        col = pal[rng.integers(len(pal))] * (0.85 + rng.random() * 0.3)
        cv2.ellipse(colores, centro, (int(largo), int(corto)), ang, 0, 360, tuple(float(k) for k in np.clip(col, 0, 1)), -1)
    lz.pintar(np.clip(sombras - hojas, 0, 1), "#141f10", 0.55)
    lz.pintar(hojas, colores)
    # el nervio claro de algunas hojas (luz arriba a la izquierda)
    luz = np.clip(hojas - desplazar(lz, hojas, -0.5, -0.5), 0, 1)
    lz.pintar(luz * (lz.ruido(0.8, 1, semilla=35) > 0.5), "#e0a874", 0.35)


def _puente_piedra(lz, tipos, alto, ancho, fina, media):
    """El PUENTE DE PIEDRA de los antiguos, en vista 3/4: tablero de sillares con el centro gastado, el pretil
    del norte (albardilla y su cara interior), el pretil del sur (albardilla y su cara exterior) y, debajo, la
    fachada con arcos sobre el agua (dovelas, musgo que cuelga y espuma al pie). Y el VADO: piedras planas."""
    pp = mascara(lz, tipos, ("puente_piedra",), 0.4, 0.0, semilla=40)
    pr = mascara(lz, tipos, ("pretil",), 0.4, 0.0, semilla=41)
    S = lz.s
    if pp.max() > 0:
        fila = np.floor(lz.y / 5.0)
        desfase = (fila % 2) * 4.0
        bx = (lz.x + desfase) % 8.0
        by = lz.y % 5.0
        junta = ((bx < 0.8) | (by < 0.8)).astype(np.float32)
        tono = (np.sin(np.floor((lz.x + desfase) / 8.0) * 12.99 + fila * 78.23) * 43758.5) % 1
        bisel = (by < 1.8) * 0.12 - (bx > 6.8) * 0.08
        vp = 0.5 + tono * 0.2 + (fina - 0.5) * 0.14 + bisel
        lz.pintar(pp, rampa(PIEDRA_R, np.clip(vp, 0, 1)))
        lz.pintar(pp * junta, rampa(["#2e302a", "#41443a", "#2b4220"], media), 0.85)
        musgo = np.clip((lz.ruido(4, 3, semilla=43) - 0.72) * 5, 0, 1) * pp * junta
        lz.pintar(musgo, "#526d38", 0.9)
        grietas = (np.clip(1 - np.abs(lz.ruido(14, 3, semilla=42) - 0.5) * 40, 0, 1) > 0.6) * pp
        lz.pintar(grietas, "#2e302a", 0.7)
    if pr.max() > 0:
        rows_n, rows_s = [], []
        for ty in range(alto):
            for tx in range(ancho):
                if tipos[ty][tx] == "pretil":
                    norte = ty + 1 < alto and tipos[ty + 1][tx] == "puente_piedra"
                    (rows_n if norte else rows_s).append((tx, ty))
        # cada pretil: albardilla (tapa clara redondeada) y su cara de piedra; los bloques de la tapa son largos
        tono_t = (np.sin(np.floor(lz.x / 10.0) * 7.31) * 9137.1) % 1
        tono_c = (np.sin(np.floor((lz.x + (np.floor(lz.y / 4.0) % 2) * 3) / 6.0) * 3.7 + np.floor(lz.y / 4.0) * 1.3) * 5813.7) % 1
        for lista, tapa_arriba in ((rows_n, (0, 7)), (rows_s, (0, 7))):
            m = np.zeros((lz.H, lz.W), np.float32)
            tapa = np.zeros_like(m)
            for (tx, ty) in lista:
                y0, x0 = int(ty * 16 * S), int(tx * 16 * S)
                m[y0:y0 + 16 * S, x0:x0 + 16 * S] = 1
                tapa[y0:y0 + 7 * S, x0:x0 + 16 * S] = 1
            if not lista:
                continue
            cara = m * (1 - tapa)
            lz.pintar(cara, rampa(PIEDRA_R[0:5], np.clip(0.3 + tono_c * 0.35 + (fina - 0.5) * 0.2 - ((lz.y % 16) - 7) / 9 * 0.2, 0, 1)))
            lz.pintar(cara * (((lz.y % 4.0) < 0.8) | (((lz.x + (np.floor(lz.y / 4.0) % 2) * 3) % 6.0) < 0.8)), "#292c25", 0.8)
            yy = lz.y % 16.0
            redondo = np.clip(1 - np.abs(yy - 3.5) / 3.5, 0, 1)
            lz.pintar(tapa, rampa(PIEDRA_R[3:], np.clip(0.25 + redondo * 0.5 + tono_t * 0.2 + (fina - 0.5) * 0.15, 0, 1)))
            lz.pintar(tapa * ((lz.x % 10.0) < 0.8), "#41443a", 0.9)
            lz.pintar(tapa * (yy > 6.2), "#2e302a", 0.9)                       # borde de la albardilla
            lz.pintar(m * np.clip((lz.ruido(3, 2, semilla=44) - 0.74) * 6, 0, 1), rampa(["#3f582f", "#526d38", "#6a8246"], fina), 0.85)
        # la sombra del pretil norte sobre el tablero
        for (tx, ty) in rows_n:
            y0, x0 = int((ty + 1) * 16 * S), int(tx * 16 * S)
            sombra = np.zeros((lz.H, lz.W), np.float32)
            sombra[y0:y0 + 3 * S, x0:x0 + 16 * S] = 1
            lz.pintar(sombra * pp, "#2e302a", 0.45)
        # la FACHADA con arcos, bajo el pretil sur, sobre el agua (dos casillas de alto)
        if rows_s:
            fach = np.zeros((lz.H, lz.W), np.float32)
            rows_s = [(tx, ty) for (tx, ty) in rows_s if ty + 1 < alto and tipos[ty + 1][tx] == "agua"] or rows_s
            for (tx, ty) in rows_s:
                y0, x0 = int((ty + 1) * 16 * S), int(tx * 16 * S)
                fach[y0:y0 + 22 * S, x0:x0 + 16 * S] = 1
            xs = [tx for (tx, ty) in rows_s]
            y_base = (rows_s[0][1] + 1) * 16
            x_ini, x_fin = min(xs) * 16, (max(xs) + 1) * 16
            hueco = np.zeros_like(fach)
            dovelas = np.zeros_like(fach)
            n_arcos = max(1, round((x_fin - x_ini) / 70))
            paso = (x_fin - x_ini) / n_arcos
            for k in range(n_arcos):
                cx = x_ini + paso * (k + 0.5)
                r = paso * 0.36
                arco = lz.elipse(cx, y_base + 22, r, 17).astype(np.float32)
                hueco = np.maximum(hueco, arco)
                dovelas = np.maximum(dovelas, lz.elipse(cx, y_base + 22, r + 3, 20).astype(np.float32) - arco)
            hueco *= fach
            dovelas *= fach
            muro = fach * (1 - hueco)
            lz.pintar(muro, rampa(PIEDRA_R[0:6], np.clip(0.28 + tono_c * 0.3 + (fina - 0.5) * 0.2 - ((lz.y - y_base) / 22.0) * 0.25, 0, 1)))
            lz.pintar(muro * (((lz.y % 4.0) < 0.8) | (((lz.x + (np.floor(lz.y / 4.0) % 2) * 3) % 6.0) < 0.8)), "#292c25", 0.75)
            ang = np.arctan2(lz.y - (y_base + 22), lz.x - x_ini)
            lz.pintar(dovelas, rampa(PIEDRA_R[2:6], np.clip(0.5 + (fina - 0.5) * 0.3, 0, 1)))
            lz.pintar(dovelas * ((np.floor(ang * 18) % 2) == 0), "#41443a", 0.5)
            # bajo el arco: oscuro, y el agua que sigue al otro lado con un reflejo
            lz.pintar(hueco, rampa(["#0a1414", "#122626", "#1c3535"], np.clip((lz.y - y_base) / 22.0, 0, 1)))
            lz.pintar(hueco * (lz.y > y_base + 17) * (fina > 0.6), "#346161", 0.6)
            # musgo y hiedra que cuelgan de la fachada
            colgante = estirar(np.clip((lz.ruido(1.4, 2, semilla=48) - 0.7) * 6, 0, 1), 10) > 0.55
            lz.pintar(colgante * muro * (lz.y < y_base + 12), rampa(["#2b4220", "#3f582f", "#526d38"], fina), 0.9)
            # espuma y sombra al pie, en el agua
            pie = np.zeros_like(fach)
            pie[int((y_base + 20) * S):int((y_base + 23) * S), int(x_ini * S):int(x_fin * S)] = 1
            lz.pintar(pie * (1 - hueco) * (fina > 0.4), "#9fd0d0", 0.6)
            sombra = np.zeros_like(fach)
            sombra[int((y_base + 22) * S):int((y_base + 30) * S), int(x_ini * S):int(x_fin * S)] = 1
            lz.pintar(sombra * (1 - fach), "#122626", 0.45)
    va = mascara(lz, tipos, ("vado",), 0.4, 0.0, semilla=45)
    if va.max() > 0:
        rng = np.random.default_rng(46)
        piedras = np.zeros((lz.H, lz.W), np.float32)
        for ty in range(alto):
            for tx in range(ancho):
                if tipos[ty][tx] != "vado":
                    continue
                cx = tx * 16 + 8 + (rng.random() - 0.5) * 2
                cy = ty * 16 + 9 + (rng.random() - 0.5) * 2
                piedras = np.maximum(piedras, lz.elipse(cx, cy, 6.2 + rng.random(), 4.6 + rng.random() * 0.8, rng.random() * 30).astype(np.float32))
        lz.pintar(np.clip(desplazar(lz, piedras, 0.5, 2.0) - piedras, 0, 1), "#122626", 0.75)
        espuma = np.clip(lz.desenfocar(piedras, 1.4) - piedras, 0, 1)
        lz.pintar(espuma * (fina > 0.35), "#9fd0d0", 0.7)
        alto_p = lz.desenfocar(piedras, 1.4)
        gy_, gx_ = np.gradient(alto_p)
        ilum = np.clip(0.5 + (gx_ * 0.6 + gy_ * 0.7) * -40, 0, 1)
        lz.pintar(piedras, rampa(PIEDRA_R[1:], np.clip(0.45 + (ilum - 0.5) * 0.9 + (fina - 0.5) * 0.2, 0, 1)))
        lz.pintar(piedras * np.clip((lz.ruido(2, 2, semilla=47) - 0.62) * 5, 0, 1), "#526d38", 0.75)
        lz.pintar(np.clip(piedras - desplazar(lz, piedras, 0, 1.0), 0, 1) * 0 + np.clip(desplazar(lz, piedras, 0, -1.0) * 0, 0, 1), "#000000", 0)


PENA = ["#1a1c20", "#292c32", "#3a3e45", "#4d5259", "#62686e", "#7a8086", "#949a9e", "#b1b5b6", "#cfd2cf"]


def _riscos(lz, tipos, fina, media, cara=1.0):
    """Las PEÑAS («0», en el Camino Cobrizo): roca natural de piedra parda en vista 3/4. Arriba, una masa de roca
    abombada, con bultos y grietas que siguen la piedra, musgo en lo que da a la sombra y hojas; al sur, la pared
    (de altura irregular) con estratos, grietas verticales y vetas de cobre (naranja) y malaquita (verde-agua);
    al pie, piedras sueltas, hierba y la sombra sobre el suelo.
    cara: cuántas veces más alta es la pared (en la Cañada del Eco, el doble: es una garganta)."""
    ri = mascara(lz, tipos, ("risco",), 4.0, 0.5, semilla=50)
    if ri.max() <= 0:
        return
    S = lz.s
    import cv2 as _cv
    # la altura de la roca: más alta hacia dentro, con bultos grandes y medianos
    dentro = _cv.distanceTransform((ri > 0.5).astype(np.uint8), _cv.DIST_L2, 5) / S
    bultos = lz.ruido(22, 2, semilla=51)
    alto = np.clip(dentro / 16.0, 0, 1) ** 0.7 * 16 + (bultos - 0.5) * 10
    alto = lz.desenfocar(alto * ri, 4.0)
    # la pared del sur: de 14 a 26 px según el sitio (el borde de arriba no es una línea recta)
    alto_pared = (14 + estirar(lz.ruido(14, 2, semilla=59), int(60 * S)) * 10) * cara
    pared = np.zeros_like(ri)
    for k in range(1, int(27 * cara)):
        abajo = np.clip(desplazar(lz, ri, 0, -k), 0, 1)
        pared = np.maximum(pared, ri * (1 - abajo) * (alto_pared >= k))
    pared = np.clip((pared - 0.5) * 4 + 0.5, 0, 1) * ri
    encima = np.clip(ri - pared, 0, 1)
    # la sombra al pie de la pared y a la derecha
    lz.pintar(np.clip(lz.desenfocar(desplazar(lz, ri, 4, 7), 3.0) - ri, 0, 1), "#0b0907", 0.7)
    # encima: luz según la inclinación (de arriba a la izquierda)
    gy, gx = np.gradient(alto)
    luz_e = np.clip(0.55 + (gx * 0.7 + gy * 0.8) * 2.2, 0, 1)
    ve = 0.47 + (luz_e - 0.5) * 0.62 + (fina - 0.5) * 0.08 + (lz.ruido(3, 2, semilla=60) - 0.5) * 0.08
    lz.pintar(encima, rampa(PENA, np.clip(ve, 0, 1)))
    # grietas que siguen la piedra (líneas torcidas), con el labio de arriba iluminado
    gr = lz.ruido(7, 4, semilla=61)
    grieta = np.clip(1 - np.abs(gr - 0.5) * 30, 0, 1) * encima * (lz.ruido(10, 2, semilla=62) > 0.6)
    lz.pintar(grieta, PENA[1], 0.9)
    lz.pintar(np.clip(desplazar(lz, grieta, 0, -1.0) - grieta, 0, 1) * encima, PENA[7], 0.5)
    # musgo en lo que da a la sombra y en los huecos, y alguna mata de hierba
    musgo = np.clip((lz.ruido(8, 2, semilla=52) - 0.55) * 4, 0, 1) * encima * np.clip(1.1 - luz_e * 1.4, 0, 1)
    lz.pintar(musgo, rampa(HIERBA_BOSQUE[2:], np.clip(media * 0.8 + fina * 0.2, 0, 1)), 0.85)
    # la pared: estratos casi horizontales, grietas verticales, más oscura abajo
    capas = np.sin((lz.y + (lz.ruido(20, 2, semilla=64) - 0.5) * 10) * 0.9) * 0.5 + 0.5
    estrias = estirar(lz.ruido(1.6, 2, semilla=53), int(10 * S))
    hondo = np.clip(1 - lz.desenfocar(pared, 4.0), 0, 1)
    vp = 0.36 + (capas - 0.5) * 0.18 + (estrias - 0.5) * 0.35 + (lz.ruido(4, 2, semilla=56) - 0.5) * 0.15 + hondo * 0.1
    sombra_baja = np.clip(desplazar(lz, 1 - ri, 0, -6), 0, 1) * pared        # los últimos px antes del suelo, más oscuros
    vp = vp - sombra_baja * 0.18
    lz.pintar(pared, rampa(PENA[:8], np.clip(vp, 0, 1)))
    lz.pintar(pared * (np.abs(estrias - 0.5) < 0.03), "#120e0b", 0.8)
    lz.pintar(pared * (capas > 0.93), PENA[6], 0.35)
    # el canto de arriba de la pared, iluminado e irregular
    filo = np.clip(pared - desplazar(lz, pared, 0, 1.5), 0, 1)
    lz.pintar(filo, PENA[8], 0.9)
    # vetas de cobre y de malaquita en la pared
    veta = np.clip(1 - np.abs(lz.ruido(12, 3, semilla=54) - 0.5) * 16, 0, 1)
    lz.pintar(veta * pared * (media > 0.5), "#b8622e", 0.85)
    lz.pintar(veta * pared * (media <= 0.5) * (fina > 0.35), "#3e8f7a", 0.75)
    lz.pintar(np.clip((fina - 0.88) * 8, 0, 1) * pared * (media > 0.55), "#f4b470", 0.9)
    # la hierba y el musgo que cuelgan por el canto
    cuelga = filo * (estirar(fina, 5) > 0.5)
    for k in (1.5, 3.0):
        lz.pintar(np.clip(desplazar(lz, cuelga, 0, k), 0, 1) * pared * (fina > 0.3 + k * 0.1), HIERBA_BOSQUE[5 - int(k)], 0.85)
    # el contorno oscuro de la roca (la separa de la hierba)
    borde = np.clip(_cv.dilate((ri > 0.5).astype(np.uint8), np.ones((S + 1, S + 1), np.uint8)).astype(float) - (ri > 0.5), 0, 1)
    lz.pintar(borde, "#14100c", 0.75)
    # piedras sueltas y hierba al pie
    pie = np.clip(desplazar(lz, ri, 0, 4) - ri, 0, 1)
    sueltas = np.clip((lz.ruido(1.4, 2, semilla=57) - 0.7) * 8, 0, 1) * (lz.desenfocar(pie, 1.5) > 0.15)
    lz.pintar(np.clip(desplazar(lz, sueltas, 0.6, 0.8) - sueltas, 0, 1), "#0b0907", 0.6)
    lz.pintar(sueltas, rampa(PENA[3:8], fina), 0.95)
    return pared


NIEVE_N = ["#4a5672", "#61708e", "#7a89a6", "#95a3bd", "#adbbd1", "#c4cfe0", "#d9e1ed", "#eef2f8"]
PISADA_N = ["#4a5468", "#5e6a80", "#76829a", "#8e9ab0", "#a8b2c4", "#c0c9d8"]
# la nieve de Sigilia: lila (los morados de Sigilia), con el sendero pisado más gris
NIEVE_LILA = ["#4e4870", "#655e8a", "#7e76a2", "#9890ba", "#b0a9cd", "#c8c2de", "#dddaec", "#f0eef8"]
PISADA_LILA = ["#4c4664", "#605a7a", "#787292", "#908aa8", "#a8a2bc", "#c0bbd0"]
# los mapas de Sigilia guardan su suelo en arte/mundos/sigilia/suelos
SIGILIA = {"paso_escarcha", "maandiko", "estanterias_colgantes", "canal_tinta", "observatorio_aurora", "seccion_prohibida"}
# la tinta del Canal: casi negra en lo hondo, morada en la orilla
AGUA_TINTA = ["#0b0812", "#120d1c", "#1a1328", "#231a36", "#2e2246", "#3a2c58", "#4a3a6c", "#5c4c82", "#9a8cc4"]
BIBLIOTECAS = {"estanterias_colgantes"}
OBSERVATORIOS = {"observatorio_aurora"}


def _nevar(lz, tipos, fina, media, pared, conservar=(), lila=False, sin_agua=False):
    """El SENDERO OLVIDADO: todo nevado. Donde había hierba, nieve con ondas del viento y sombras azuladas; el camino,
    nieve pisada (más gris, con huellas); encima de las peñas, nieve; en sus paredes, escarcha."""
    import cv2 as _cv
    NIEVE_S = NIEVE_LILA if lila else NIEVE_N
    PISADA = PISADA_LILA if lila else PISADA_N
    S = lz.s
    ri = mascara(lz, tipos, ("risco",), 4.0, 0.5, semilla=50)
    pared = pared if pared is not None else np.zeros_like(ri)
    suelo = np.clip(1 - ri, 0, 1)
    if sin_agua:
        # (la tinta del Canal no se hiela, y en la pasarela se ven las tablas: la nieve se queda en los muelles)
        suelo = suelo * np.clip(1 - mascara(lz, tipos, ("agua", "puente"), 3, 0.2, semilla=910), 0, 1)
    if conservar:
        # (lo que se conserva, p. ej. las losas de las Ruinas, solo lleva un poco de nieve en las juntas)
        guardar = mascara(lz, tipos, conservar, 5, 0.2, semilla=909)
        suelo = suelo * np.clip(1 - guardar * 0.92, 0, 1)
        # las losas de las Ruinas: piedra vieja y clara (no el gris verdoso de las de los caminos)
        lz.pintar(guardar * (1 - ri), "#7e7296" if lila else "#a8a596", 0.62 if lila else 0.35)
    grande = lz.ruido(40, 3, semilla=901)
    ondas = estirar(lz.ruido(2.5, 2, semilla=902), int(14 * S), vertical=False)
    # (más oscura y azulada que el blanco puro: si no, deslumbra y no se ve nada encima)
    v = (0.4 if lila else 0.56) + (grande - 0.5) * 0.2 + (ondas - 0.5) * 0.42 + (fina - 0.5) * 0.08
    lz.pintar(suelo, rampa(NIEVE_S, np.clip(v, 0, 1)))
    # las crestas de las ondas, con luz, y su sombra azulada debajo
    cresta = np.clip((ondas - 0.62) * 6, 0, 1) * suelo
    lz.pintar(np.clip(desplazar(lz, cresta, 0, 1.2) - cresta, 0, 1), NIEVE_S[2], 0.5)
    lz.pintar(cresta, NIEVE_S[7], 0.5)
    # destellos del hielo
    lz.pintar((fina > 0.93) * suelo, "#ffffff", 0.8)
    # el camino: nieve pisada, con huellas pequeñas
    cam = mascara(lz, tipos, ("camino",), 6, 0.25, semilla=903)
    if cam.max() > 0:
        vp = 0.5 + (lz.ruido(8, 3, semilla=904) - 0.5) * 0.3 + (fina - 0.5) * 0.15
        lz.pintar(cam * suelo, rampa(PISADA, np.clip(vp, 0, 1)), 0.9)
        huellas = np.clip((lz.ruido(0.9, 1, semilla=905) - 0.78) * 8, 0, 1) * cam * suelo
        lz.pintar(huellas, PISADA[0], 0.6)
        lz.pintar(np.clip(desplazar(lz, huellas, 0, -0.8) - huellas, 0, 1) * cam, NIEVE_S[6], 0.5)
    # sombra azulada al pie de las peñas
    lz.pintar(np.clip(lz.desenfocar(desplazar(lz, ri, 3, 8), 4.0) - ri, 0, 1) * suelo, "#2a3450", 0.45)
    # encima de las peñas, nieve (deja asomar la roca en los bordes y en algunas manchas)
    encima = np.clip(ri - pared, 0, 1)
    dentro = _cv.distanceTransform((encima > 0.5).astype(np.uint8), _cv.DIST_L2, 5) / S
    # (una capa compacta: solo asoma la roca en el borde y en alguna mancha grande, no a motas)
    manchas = lz.desenfocar((lz.ruido(18 if not conservar else 34, 2, semilla=906) > (0.22 if not conservar else 0.08)).astype(float), 3.0) > 0.5
    capa = encima * (dentro > 1.6) * (manchas if not lila else 1.0)
    vn = (0.5 if lila else 0.62) + (lz.ruido(10, 2, semilla=907) - 0.5) * (0.1 if lila else 0.3) + (fina - 0.5) * 0.1
    lz.pintar(capa, rampa(NIEVE_S, np.clip(vn, 0, 1)))
    lz.pintar(np.clip(capa - desplazar(lz, capa, 0, 1.0), 0, 1), NIEVE_S[7], 0.7)
    # escarcha en la pared y carámbanos que cuelgan del canto
    lz.pintar((lz.ruido(0.6, 1, semilla=908) > 0.86) * pared, NIEVE_S[5], 0.4)
    filo = np.clip(pared - desplazar(lz, pared, 0, 1.5), 0, 1)
    caramb = filo * (estirar(fina, 4) > 0.62)
    for k in (1.0, 2.0, 3.0):
        lz.pintar(np.clip(desplazar(lz, caramb, 0, k), 0, 1) * pared * (fina > 0.25 * k), NIEVE_S[6 - int(k)], 0.85)


def _agua_espejo(lz, agua, prof, fina):
    """El agua del LAGO ESPEJO, quieta como un cristal: clara y lisa, con el cielo reflejado (vetas largas de luz),
    la orilla del norte reflejada en oscuro justo debajo (los árboles se ven del revés en el agua) y casi sin ondas.
    (Lo turbio, mientras vive Kambare, lo pone el juego encima.)"""
    hondo = np.clip(prof / 40, 0, 1)
    cielo = estirar(lz.ruido(30, 3, semilla=81), int(90 * lz.s), False)
    v = 0.62 - hondo * 0.22 + (cielo - 0.5) * 0.25
    lz.pintar(agua, rampa(["#1c3a3a", "#285050", "#346161", "#4c8d8d", "#6db0b0", "#9fd0d0", "#c8e6e2"], np.clip(v, 0, 1)), 0.9)
    # el reflejo de la orilla del norte: una franja oscura y verdosa bajo el borde de arriba, deshilachada
    for k in range(1, 22, 2):
        bajo_orilla = np.clip(agua - desplazar(lz, agua, 0, k), 0, 1)
        lz.pintar(bajo_orilla * (1 - k / 24) * (estirar(fina, 9) > 0.35), "#1d3a26", 0.35)
    # vetas largas de luz (el cielo en el cristal) y algún destello
    vetas_ = (estirar(lz.ruido(2, 2, semilla=82), int(60 * lz.s), False) > 0.66) * agua * np.clip(hondo * 2, 0, 1)
    lz.pintar(vetas_, "#d8f0ec", 0.25)
    lz.pintar((fina > 0.93) * agua * np.clip(hondo * 3, 0, 1), "#ffffff", 0.5)


def _playas(lz, agua, fina, media):
    """Las orillas del río de la Orilla de Juncos: una franja de arena clara y barro húmedo a lo largo del agua
    (más ancha en los recodos), con huellas de pájaro, conchitas y ramitas que ha dejado la corriente; y el banco de
    arena del río, de arena del todo (lo que no es agua y está rodeado de agua)."""
    import cv2 as _cv
    S = lz.s
    seco = (agua < 0.5).astype(np.uint8)
    # lo que está rodeado de agua por los dos lados (el banco de arena): tierra que no toca el borde del mapa
    n, etiquetas = _cv.connectedComponents(seco)
    banco = np.zeros_like(agua)
    for k in range(1, n):
        trozo = etiquetas == k
        ys, xs = np.nonzero(trozo)
        if xs.min() > 2 and xs.max() < lz.W - 3 and ys.min() > 2 and ys.max() < lz.H - 3:
            banco = np.maximum(banco, trozo.astype(float))
    ancho = (20 + (lz.ruido(30, 2, semilla=91) - 0.5) * 22) * S
    cerca = _cv.distanceTransform(seco, _cv.DIST_L2, 5)
    playa = np.clip((ancho - cerca) / (4 * S), 0, 1) * (1 - agua)
    playa = np.maximum(playa, lz.desenfocar(banco, 1.0))
    v = 0.5 + (media - 0.5) * 0.3 + (fina - 0.5) * 0.25
    lz.pintar(playa, rampa(["#6e5a3a", "#8a7350", "#a68e64", "#c2aa7c", "#d8c294"], np.clip(v, 0, 1)), 0.95)
    # barro húmedo justo junto al agua
    humedo = np.clip((6 * S - cerca) / (3 * S), 0, 1) * (1 - agua)
    lz.pintar(humedo, rampa(["#3f3420", "#52442a", "#66563a"], np.clip(media, 0, 1)), 0.8)
    # huellas de pájaro, conchitas y ramitas
    marcas = (lz.ruido(0.6, 1, semilla=92) > 0.9) * playa
    lz.pintar(marcas * (fina > 0.5), "#5a4a30", 0.7)
    conchas = (lz.ruido(0.5, 1, semilla=93) > 0.93) * playa
    lz.pintar(conchas, "#efe6cf", 0.85)
    ramitas = (estirar(lz.ruido(0.8, 1, semilla=94), int(4 * S), False) > 0.86) * playa
    lz.pintar(ramitas, "#4a3624", 0.6)


def _mesetas(lz, tipos, fina, media, pared):
    """Encima de las peñas grandes (la Cañada del Eco): una MESETA de hierba, más alta que el fondo. La roca solo se
    ve en el filo (unos pocos píxeles con musgo) y en la cara del acantilado del sur; dentro, hierba oscura con
    matas, piedras sueltas y algún claro de roca desnuda."""
    import cv2 as _cv
    ri = mascara(lz, tipos, ("risco",), 4.0, 0.5, semilla=50)
    if ri.max() <= 0:
        return
    S = lz.s
    dentro = _cv.distanceTransform((ri > 0.5).astype(np.uint8), _cv.DIST_L2, 5) / S
    # un poco dentro del borde y por encima de la cara de la pared: hierba; el borde, irregular
    filo = 10 + (lz.ruido(10, 2, semilla=71) - 0.5) * 8
    sobre_cara = lz.desenfocar(_cv.dilate((pared > 0.3).astype(np.uint8), np.ones((int(8 * S), int(8 * S)), np.uint8)).astype(float), 2.0)
    me = np.clip((dentro - filo) / 4.0, 0, 1) * np.clip(1 - sobre_cara * 1.5, 0, 1)
    calvas = np.clip((lz.ruido(16, 2, semilla=72) - 0.8) * 6, 0, 1)
    me = me * (1 - calvas * 0.9)
    v = 0.42 + (lz.ruido(40, 3, semilla=73) - 0.5) * 0.2 + (media - 0.5) * 0.2 + (estirar(fina, 5) - 0.5) * 0.3
    lz.pintar(me, rampa(HIERBA_BOSQUE, np.clip(v, 0, 1)))
    # el filo de la meseta: una línea de roca clara y, por dentro, la sombra de la hierba que cuelga
    labio = np.clip(me - lz.desenfocar(me, 1.5), 0, 1) * 2.5
    lz.pintar(np.clip(labio, 0, 1), PENA[6], 0.6)
    lz.pintar(np.clip(me - desplazar(lz, me, 0, -2.0), 0, 1), HIERBA_BOSQUE[1], 0.5)
    # matas y piedrecitas en la meseta
    matas = np.clip((lz.ruido(3.0, 3, semilla=74) - 0.64) * 6, 0, 1) * me
    lz.pintar(np.clip(desplazar(lz, matas, 1.2, 1.4) - matas, 0, 1), "#0e160b", 0.5)
    lz.pintar(matas, rampa(HIERBA_BOSQUE[4:], fina), 0.85)
    piedras = np.clip((lz.ruido(1.2, 2, semilla=75) - 0.84) * 10, 0, 1) * me
    lz.pintar(np.clip(desplazar(lz, piedras, 0.6, 0.8) - piedras, 0, 1), "#0b0907", 0.6)
    lz.pintar(piedras, rampa(PENA[4:8], fina), 0.9)


def pintar_gruta(nombre, salida=None, setas=False):
    """El suelo de una cueva (la Gruta de las Raíces): tierra oscura con guijarros, raíces finas que corren por el
    suelo y algún charco; las paredes («0») son roca maciza, con la cara iluminada donde se juntan con el suelo y raíces
    que bajan por ella. Se verá a oscuras en el juego (scripts/mundo/gruta/oscuridad.gd)."""
    filas = leer(nombre)
    alto, ancho = len(filas), len(filas[0])
    lz = Lienzo(ancho * CASILLA, alto * CASILLA, s=2, semilla=17)
    roca_t = [["roca" if c == "0" else "suelo" for c in f] for f in filas]
    roca = mascara(lz, roca_t, ("roca",), 4.0, 0.9, semilla=171)
    fina = lz.ruido(0.8, 2, semilla=172)
    media = lz.ruido(7, 3, semilla=173)
    # el suelo: tierra oscura, con manchas y guijarros
    v = 0.45 + (media - 0.5) * 0.35 + (fina - 0.5) * 0.25
    lz.pintar(np.ones((lz.H, lz.W)), rampa(["#0e0b0a", "#17120f", "#211a15", "#2c231c", "#3a2e24", "#4a3c2e"], np.clip(v, 0, 1)))
    guij = (lz.ruido(0.9, 1, semilla=174) > 0.86).astype(np.float32)
    lz.pintar(np.clip(desplazar(lz, guij, 0.6, 0.8) - guij, 0, 1), "#0a0706", 0.6)
    lz.pintar(guij, rampa(["#3e342c", "#5a4e44", "#7a6c5e"], fina), 0.85)
    # raíces finas que corren por el suelo (vienen del Primer Árbol, arriba)
    raices = np.zeros((lz.H, lz.W), np.float32)
    rng = np.random.default_rng(175)
    for k in range(70):
        x, y = rng.random() * lz.w, rng.random() * lz.h
        pts = []
        ang = -np.pi / 2 + (rng.random() - 0.5) * 1.6
        for j in range(18):
            pts.append((x, y))
            x += np.cos(ang) * 6
            y += np.sin(ang) * 6
            ang += (rng.random() - 0.5) * 0.7
        raices = np.maximum(raices, lz.trazo(pts, 0.9 + rng.random() * 0.8, 0.3).astype(np.float32))
    lz.pintar(np.clip(desplazar(lz, raices, 0.5, 0.8) - raices, 0, 1), "#070504", 0.6)
    if setas:
        # en la cueva de las setas no son raíces: es MICELIO, hilos blancos y violetas que lo cubren todo
        lz.pintar(raices, rampa(["#3a2a48", "#6a5a80", "#a898c0", "#e0d8f0"], fina), 0.8)
        lz.sumar_luz(lz.desenfocar(raices, 1.5), "#a855d6", 0.12)
    else:
        lz.pintar(raices, rampa(["#3e2a1a", "#563a24", "#74502e", "#94683c"], fina), 0.95)
    # charcos donde gotea
    charcos = (lz.ruido(18, 2, semilla=176) > 0.95).astype(np.float32) * (1 - roca)
    lz.pintar(charcos, "#18262a", 0.85)
    lz.pintar(charcos * (fina > 0.7), "#4c8d8d", 0.4)
    # la roca: maciza, con grietas, y la cara iluminada donde se junta con el suelo (las paredes miran al sur)
    vr = 0.35 + (media - 0.5) * 0.4 + (fina - 0.5) * 0.3
    lz.pintar(roca, rampa(["#0b0a0b", "#151315", "#211e21", "#2e2a2c", "#3d383a", "#504a4a"], np.clip(vr, 0, 1)))
    grietas = (np.abs(np.sin(lz.x * 0.21 + lz.ruido(5, 2, semilla=177) * 9)) < 0.05) * roca
    lz.pintar(grietas, "#050405", 0.8)
    cara = np.clip(roca - desplazar(lz, roca, 0, -7), 0, 1)             # la franja de roca justo encima del suelo
    tono = np.clip((lz.y % 7) / 7 + (fina - 0.5) * 0.3, 0, 1)
    lz.pintar(cara, rampa(["#2a2624", "#3e3834", "#57504a", "#6e665e"], tono), 0.95)
    lz.pintar(np.clip(desplazar(lz, roca, 0, -1.5) - roca, 0, 1), "#080606", 0.7)   # la sombra al pie de la pared
    musgo = (lz.ruido(2, 2, semilla=178) > 0.7) * cara
    lz.pintar(musgo, "#4a2f5a" if setas else "#2f4a2a", 0.6)
    destino = salida or os.path.join(RAIZ, "arte", "mundos", "raiz", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.012)
    print("Suelo pintado:", destino, (lz.w, lz.h))


def pintar_biblioteca(nombre, salida=None):
    """El suelo de una BIBLIOTECA de Sigilia (Las Estanterías Colgantes): parqué de tablones de madera oscura con
    alfombras moradas en los pasillos («#»); las paredes («0») son ESTANTERÍAS vistas en 3/4: arriba el canto de la
    madera, al sur la cara llena de libros de colores en baldas; y los HUECOS («ɵ»), la caída a los pisos de abajo:
    oscuridad azulada con las baldas del piso de abajo muy al fondo y un canto de madera rota en el borde."""
    filas = leer(nombre)
    alto, ancho = len(filas), len(filas[0])
    lz = Lienzo(ancho * CASILLA, alto * CASILLA, s=2, semilla=19)
    tipos = [["pared" if c == "0" else ("hueco" if c == "ɵ" else ("pasillo" if c in "#_<>^" else "suelo")) for c in f] for f in filas]
    pared = mascara(lz, tipos, ("pared",), 2.0, 0.1, semilla=191)
    hueco = mascara(lz, tipos, ("hueco",), 2.0, 0.2, semilla=192)
    pasillo = mascara(lz, tipos, ("pasillo",), 4.0, 0.3, semilla=193)
    fina = lz.ruido(0.8, 2, semilla=194)
    media = lz.ruido(7, 3, semilla=195)
    # el parqué: tablones largos (en espiga suave), cada uno con su tono, y sus juntas
    tabla = np.floor(lz.y / 5)
    corte = np.floor((lz.x + (tabla % 3) * 13) / 40)
    tono = (np.sin(tabla * 12.9 + corte * 78.2) * 43758.5) % 1
    veta = estirar(lz.ruido(0.6, 2, semilla=196), 9, False)
    v = 0.42 + (tono - 0.5) * 0.22 + (veta - 0.5) * 0.25 + (media - 0.5) * 0.1
    lz.pintar(np.ones((lz.H, lz.W)), rampa(["#1a1014", "#2a1a1e", "#3c2628", "#523632", "#6a4a3e", "#84604a"], np.clip(v, 0, 1)))
    junta = ((lz.y % 5) < 0.5) | (((lz.x + (tabla % 3) * 13) % 40) < 0.6)
    lz.pintar(junta * 1.0, "#120a0c", 0.7)
    # las alfombras de los pasillos: moradas, con su cenefa dorada
    lz.pintar(pasillo, rampa(["#2a1838", "#3e2452", "#563470", "#6e4888"], np.clip(0.5 + (fina - 0.5) * 0.4, 0, 1)), 0.95)
    borde_alf = np.clip(pasillo - lz.desenfocar((pasillo > 0.5).astype(float), 1.2) * 0 - np.clip(desplazar(lz, pasillo, 0, 2) * desplazar(lz, pasillo, 0, -2) * desplazar(lz, pasillo, 2, 0) * desplazar(lz, pasillo, -2, 0), 0, 1), 0, 1)
    lz.pintar(borde_alf, "#c89a40", 0.8)
    # los HUECOS: oscuridad que baja, con las baldas del piso de abajo al fondo
    fondo = rampa(["#05040a", "#0a0814", "#120e20", "#1c162e"], np.clip(0.5 + (media - 0.5) * 0.5, 0, 1))
    lz.pintar(hueco, fondo)
    baldas = ((lz.y % 6) < 1.2) * (np.sin(lz.x * 0.4 + lz.y) > -0.2) * hueco
    lz.pintar(baldas, "#2a1e30", 0.6)
    lz.pintar(((lz.ruido(0.5, 1, semilla=197) > 0.9) * hueco), "#5a3a6a", 0.5)        # lomos de libros allá abajo
    # el borde del hueco: el canto de las tablas rotas, iluminado, y la sombra que cae
    canto = np.clip(desplazar(lz, hueco, 0, 2) - hueco, 0, 1)
    lz.pintar(np.clip(hueco - desplazar(lz, hueco, 0, -3), 0, 1), "#6a4a3e", 0.9)       # (la cara del suelo que se ve al borde de arriba)
    lz.pintar(canto, "#2a1a1e", 0.6)
    # las ESTANTERÍAS: la cara del sur llena de libros, y el canto de arriba de madera
    vr = 0.45 + (media - 0.5) * 0.2
    lz.pintar(pared, rampa(["#140a0c", "#24141a", "#362028", "#4a2e34"], np.clip(vr, 0, 1)))
    cara = np.clip(pared - desplazar(lz, pared, 0, -22), 0, 1)                         # 22 px de estantería por delante (3 baldas)
    fila = np.floor(lz.y / 7)
    balda = ((lz.y % 7) < 1.6) * cara
    # cada libro: 3 o 4 px de ancho (según la balda, desplazados), con su color apagado, su altura y un hueco oscuro
    u = lz.x + fila * 5.3
    n_libro = np.floor(u / 3.5)
    azar_l = (np.sin(n_libro * 12.9898 + fila * 78.233) * 43758.5453) % 1
    libros_col = rampa(["#4a1a20", "#6a2a2a", "#2a3e5a", "#2e4a34", "#7a5a24", "#4a3060", "#8a7a5a", "#2a3a40"], azar_l)
    alto_libro = 1.6 + np.floor(((azar_l * 7.13) % 1) * 3)
    libro = cara * (1 - balda) * ((lz.y % 7) > alto_libro)
    lz.pintar(cara * (1 - balda), "#0a0608")                                               # el fondo de la balda
    lz.pintar(libro, libros_col)
    lz.pintar(libro * ((u % 3.5) < 0.5), "#0a0608", 0.75)                                 # el hueco entre libros
    lz.pintar(libro * ((u % 3.5) > 3.0), "#ffffff", 0.12)                                  # el lomo, con luz
    lz.pintar(libro * (np.abs((lz.y % 7) - 4.6) < 0.3) * (azar_l > 0.4), "#d8c088", 0.45)   # el letrero dorado
    lz.pintar(balda, "#4a2e22")
    lz.pintar(cara * ((lz.y % 7) < 0.5), "#7a5a40", 0.8)                                   # el canto de la balda
    encima = np.clip(pared - cara, 0, 1)
    lz.pintar(encima * (((lz.x + lz.y) % 9) < 0.6), "#0a0608", 0.5)
    lz.pintar(np.clip(encima - desplazar(lz, encima, 0, 1.5), 0, 1), "#7a5a48", 0.7)    # el canto de arriba, con luz
    lz.pintar(np.clip(desplazar(lz, pared, 0, -2) - pared, 0, 1), "#08050a", 0.6)       # la sombra al pie
    destino = salida or os.path.join(RAIZ, "arte", "mundos", "sigilia", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.012)
    print("Suelo pintado:", destino, (lz.w, lz.h))


def pintar_observatorio(nombre, salida=None):
    """El suelo de EL OBSERVATORIO DE LA AURORA (Sigilia): terrazas de piedra astronómica colgadas en la noche.
    El vacío («0» y los puentes «=», que los enciende el juego) es el CIELO: azul muy hondo, estrellas y, arriba, las
    cintas verdes y moradas de la aurora. Las TERRAZAS: losas grandes lila-gris con juntas, un cerco de cobre junto al
    borde, círculos y líneas de constelación grabados en oro y un poco de nieve en los rincones; por el sur se les ve
    la CARA (sillares en sombra, con carámbanos). La TINTA («~»): negra, con brillos morados."""
    filas = leer(nombre)
    alto, ancho = len(filas), len(filas[0])
    lz = Lienzo(ancho * CASILLA, alto * CASILLA, s=2, semilla=23)
    tipos = [["cielo" if c in "0=" else ("tinta" if c == "~" else "suelo") for c in f] for f in filas]
    firme = [["cielo" if c in "0=" else "suelo" for c in f] for f in filas]        # (la terraza, con su estanque dentro)
    suelo = mascara(lz, firme, ("suelo",), 1.2, 0.0, semilla=231)
    tinta = mascara(lz, tipos, ("tinta",), 2.0, 0.12, semilla=232)
    fina = lz.ruido(0.8, 2, semilla=233)
    media = lz.ruido(9, 3, semilla=234)
    grande = lz.ruido(60, 3, semilla=235)
    # EL CIELO: de azul casi negro (abajo) a morado hondo (arriba), con nubes de polvo de estrellas
    v = np.clip(1 - lz.y / lz.h, 0, 1)
    lz.pintar(np.ones((lz.H, lz.W)), rampa(["#05040c", "#080714", "#0c0a1e", "#120e2a", "#1a1238"], np.clip(v * 0.8 + (grande - 0.5) * 0.5, 0, 1)))
    polvo = np.clip((ruido_torcido_local(lz, 40, 236) - 0.52) * 3.0, 0, 1)
    lz.pintar(lz.desenfocar(polvo, 10), "#3a2c66", 0.4)
    # las estrellas: muchas pequeñas, algunas gordas con su cruz
    chica = (lz.ruido(0.45, 1, semilla=237) > 0.972) * (lz.ruido(3, 2, semilla=238) > 0.4)
    lz.pintar(chica * 1.0, "#b8b4e0", 0.8)
    rng = np.random.default_rng(239)
    S = lz.s
    for col in ("#ffffff", "#ffe9b0", "#bfe3f3", "#e0c8ff"):                      # (con cv2: muchas formas pequeñas de una vez)
        gordas = np.zeros((lz.H, lz.W), np.float32)
        for _ in range(int(ancho * alto * 0.0125)):
            x, y = int(rng.uniform(2, lz.w - 2) * S), int(rng.uniform(2, lz.h - 2) * S)
            cv2.rectangle(gordas, (x, y), (x + S - 1, y + S - 1), 1.0, -1)
            if rng.random() < 0.3:
                cv2.rectangle(gordas, (x - 2 * S, y), (x + 3 * S - 1, y + S - 1), 0.6, -1)
                cv2.rectangle(gordas, (x, y - 2 * S), (x + S - 1, y + 3 * S - 1), 0.6, -1)
                cv2.rectangle(gordas, (x, y), (x + S - 1, y + S - 1), 1.0, -1)
        lz.pintar(gordas, col)
    # la AURORA: cintas que ondean, verdes y moradas (fuertes arriba, un velo más abajo)
    for k, (col, y0, amp, fuerza) in enumerate((("#3fd6a8", 40, 16, 0.95), ("#9a6cf0", 62, 20, 0.8), ("#5ff0c8", 84, 12, 0.7),
                                                ("#7a5ae0", 330, 30, 0.3), ("#3fd6a8", 600, 36, 0.24), ("#9a6cf0", 960, 30, 0.2), ("#3fd6a8", 1230, 24, 0.18))):
        onda = y0 + np.sin(lz.x * 0.011 + k * 1.7) * amp + np.sin(lz.x * 0.031 + k) * amp * 0.35
        d = lz.y - onda
        cinta = np.clip(1 - np.abs(d) / 4.0, 0, 1) + np.clip(1 - d / 46.0, 0, 1) ** 2 * (d > 0) * 0.7      # el filo y la cortina que cuelga
        hebras = 0.72 + 0.28 * np.sin(lz.x * 0.35 + np.sin(lz.y * 0.05) * 3)
        lz.sumar_luz(np.clip(cinta * hebras, 0, 1), col, fuerza)
    # LA CARA de las terrazas (22 px por el sur): sillares en sombra, con su hilada de cobre y carámbanos
    cara = np.clip(desplazar(lz, suelo, 0, 22) - suelo, 0, 1)
    hil = np.floor(lz.y / 6)
    sillar = ((lz.y % 6) < 0.8) | (((lz.x + (hil % 2) * 7) % 14) < 0.8)
    vc = 0.42 + (media - 0.5) * 0.3 + (fina - 0.5) * 0.2
    lz.pintar(cara, rampa(["#0e0c1c", "#1a1730", "#2a2548", "#3c3562", "#4e4678"], np.clip(vc, 0, 1)))
    lz.pintar(cara * sillar, "#08071a", 0.6)
    lz.pintar(np.clip(desplazar(lz, suelo, 0, 3) - suelo, 0, 1), "#b87a3c", 0.9)       # la hilada de cobre, bajo el borde
    lz.pintar(np.clip(desplazar(lz, suelo, 0, 1.2) - suelo, 0, 1), "#f0c070", 0.8)
    caram = cara * (lz.ruido(1.4, 1, semilla=240) > 0.6) * (((lz.y - 3) % 22) < 9 + 6 * np.sin(lz.x * 0.7))
    lz.pintar(np.clip(desplazar(lz, suelo, 0, 12) - suelo, 0, 1) * caram, "#bfe3f3", 0.7)
    lz.pintar(np.clip(desplazar(lz, suelo, 0, 26) - desplazar(lz, suelo, 0, 22), 0, 1) * (1 - suelo), "#030208", 0.55)   # la sombra de debajo
    # LAS LOSAS: grandes, a matajunta, cada una con su tono
    fl = np.floor(lz.y / 16)
    cl = np.floor((lz.x + (fl % 2) * 12) / 24)
    tono = (np.sin(fl * 12.9898 + cl * 78.233) * 43758.5453) % 1
    vl = 0.5 + (tono - 0.5) * 0.24 + (media - 0.5) * 0.22 + (fina - 0.5) * 0.16
    lz.pintar(suelo, rampa(["#3a3558", "#4c4670", "#605a88", "#77709e", "#8e88b2", "#a6a0c4"], np.clip(vl, 0, 1)))
    junta = ((lz.y % 16) < 0.9) | (((lz.x + (fl % 2) * 12) % 24) < 0.9)
    lz.pintar(suelo * junta, "#262240", 0.75)
    lz.pintar(suelo * desplazar(lz, junta * 1.0, 0, 1), "#b8b2d4", 0.25)                # la luz en el canto de cada losa
    lz.pintar(suelo * (lz.ruido(1.1, 2, semilla=241) > 0.78), "#2e2a4a", 0.35)          # picaduras
    # el CERCO DE COBRE, a 5 px del borde, y el canto de arriba con luz
    dist = lz.distancia(suelo)
    lz.pintar(suelo * (np.abs(dist - 5.0) < 0.9), "#b87a3c", 0.9)
    lz.pintar(suelo * (np.abs(dist - 4.4) < 0.35), "#f0c070", 0.8)
    lz.pintar(suelo * (dist < 1.4), "#c8c2de", 0.7)
    # los GRABADOS de oro: en el centro de cada terraza grande, círculos de astrolabio con sus marcas y rayos
    def astrolabio(cx, cy, r):
        dx, dy = lz.x - cx, lz.y - cy
        d = np.sqrt(dx * dx + dy * dy)
        a = np.arctan2(dy, dx)
        g = (np.abs(d - r) < 0.7) | (np.abs(d - r * 0.62) < 0.5) | (np.abs(d - r * 0.3) < 0.5)
        g = g | ((d > r * 0.62) & (d < r) & (np.abs(((a / (np.pi / 12)) % 1) - 0.5) > 0.46))        # las 24 marcas de las horas
        g = g | ((d < r * 0.62) & (d > r * 0.3) & (np.abs(((a / (np.pi / 4)) % 1) - 0.5) > 0.47))   # los 8 rayos
        lz.pintar(suelo * g, "#8a5a24", 0.9)
        lz.pintar(suelo * desplazar(lz, g * 1.0, -0.6, -0.6) * g, "#f0c868", 0.75)
    for (cx, cy, r) in ((36, 46.5, 62), (36, 67, 46), (36.5, 19.5, 120), (11.5, 46.5, 18), (61.5, 46.5, 44)):
        astrolabio(cx * 16, cy * 16, r)
    # constelaciones grabadas: estrellitas de oro unidas por líneas finas
    lineas = np.zeros((lz.H, lz.W), np.float32)
    puntos = np.zeros((lz.H, lz.W), np.float32)
    for _ in range(26):
        pts = [(rng.uniform(40, lz.w - 40), rng.uniform(40, lz.h - 40))]
        for _k in range(int(rng.integers(2, 5))):
            pts.append((pts[-1][0] + rng.uniform(-22, 22), pts[-1][1] + rng.uniform(-16, 16)))
        ent = [(int(x * S), int(y * S)) for (x, y) in pts]
        for i in range(len(ent) - 1):
            cv2.line(lineas, ent[i], ent[i + 1], 1.0, 1)
        for (x, y) in ent:
            cv2.rectangle(puntos, (x - S, y - S), (x + S - 1, y + S - 1), 1.0, -1)
    lz.pintar(lineas * suelo * (dist > 8), "#c89a40", 0.55)
    lz.pintar(puntos * suelo * (dist > 8), "#f0d27a", 0.9)
    # nieve en los rincones y junto a los bordes del norte
    nieve = suelo * np.clip((lz.ruido(14, 3, semilla=242) - 0.56) * 5, 0, 1) * np.clip(1.15 - dist / 18.0, 0, 1)
    lz.pintar(nieve, rampa(NIEVE_LILA[3:], np.clip(0.5 + (fina - 0.5) * 0.6, 0, 1)), 0.9)
    # LA TINTA del estanque: negra, con ondas moradas, el borde de piedra en sombra y un filo de luz
    vt = 0.3 + (lz.ruido(12, 3, semilla=243) - 0.5) * 0.6 + np.sin(lz.y * 0.5 + lz.ruido(6, 2, semilla=244) * 8) * 0.06
    lz.pintar(tinta, rampa(AGUA_TINTA, np.clip(vt, 0, 1)))
    lz.pintar(np.clip(tinta - desplazar(lz, tinta, 0, 4), 0, 1), "#05040c", 0.75)       # la sombra del borde del norte
    lz.pintar(np.clip(tinta - desplazar(lz, tinta, 0, -1.5), 0, 1), "#9a8cc4", 0.6)     # el filo de luz del sur
    lz.pintar(tinta * (lz.ruido(0.5, 1, semilla=245) > 0.95), "#c8b8f0", 0.6)           # estrellas reflejadas
    destino = salida or os.path.join(RAIZ, "arte", "mundos", "sigilia", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.012)
    print("Suelo pintado:", destino, (lz.w, lz.h))


def pintar_seccion(nombre, salida=None):
    """El suelo de LA SECCIÓN PROHIBIDA (Sigilia): salas de MÁRMOL MORADO bajo el Gran Archivo: damero de losas
    claras y oscuras con vetas, un filete de oro junto a las paredes y un gran sello de oro en el centro de cada sala.
    Las paredes («0») son ESTANTERÍAS DE LIBROS ENCADENADOS vistas en 3/4: arriba el canto de madera negra; al sur, la
    cara con libros oscuros cruzados por cadenas. La SIMA («=») es un pozo negro con baldas al fondo; la TINTA («~»),
    negra con brillos morados."""
    filas = leer(nombre)
    alto, ancho = len(filas), len(filas[0])
    lz = Lienzo(ancho * CASILLA, alto * CASILLA, s=2, semilla=29)
    tipos = [["pared" if c == "0" else ("sima" if c == "=" else ("tinta" if c == "~" else "suelo")) for c in f] for f in filas]
    pared = mascara(lz, tipos, ("pared",), 1.2, 0.0, semilla=291)
    sima = mascara(lz, tipos, ("sima",), 1.5, 0.08, semilla=292)
    tinta = mascara(lz, tipos, ("tinta",), 2.0, 0.1, semilla=293)
    fina = lz.ruido(0.8, 2, semilla=294)
    media = lz.ruido(9, 3, semilla=295)
    S = lz.s
    # EL MÁRMOL: damero de losas de 16 px, vetas claras que cruzan varias losas
    cx_, cy_ = np.floor(lz.x / 16), np.floor(lz.y / 16)
    clara = ((cx_ + cy_) % 2) == 0
    veta = np.abs(ruido_torcido_local(lz, 26, 296) - 0.5) < 0.018
    veta2 = np.abs(ruido_torcido_local(lz, 11, 297) - 0.5) < 0.012
    v = np.where(clara, 0.52, 0.36) + (media - 0.5) * 0.22 + (fina - 0.5) * 0.12
    lz.pintar(np.ones((lz.H, lz.W)), rampa(["#1c1230", "#2a1c46", "#3c2a60", "#523c7c", "#6c5698", "#8a76b4", "#a896cc"], np.clip(v, 0, 1)))
    lz.pintar(veta * 1.0, "#c8b8e8", 0.5)
    lz.pintar(veta2 * 1.0, "#140c24", 0.35)
    junta = ((lz.x % 16) < 0.6) | ((lz.y % 16) < 0.6)
    lz.pintar(junta * 1.0, "#120a20", 0.7)
    lz.pintar(desplazar(lz, junta * 1.0, 0.6, 0.6) * (1 - junta), "#b8a8dc", 0.18)       # el brillo del canto pulido
    # el filete de oro junto a las paredes y los sellos de oro de las salas
    suelo = np.clip(1 - pared - sima - tinta, 0, 1)
    dist = lz.distancia(1 - pared)
    lz.pintar(suelo * (np.abs(dist - 6.0) < 0.8), "#8a5a24", 0.9)
    lz.pintar(suelo * (np.abs(dist - 5.5) < 0.3), "#f0c868", 0.85)

    def sello(cx, cy, r, puntas):
        dx, dy = lz.x - cx, lz.y - cy
        d = np.sqrt(dx * dx + dy * dy)
        a = np.arctan2(dy, dx)
        estrella = d < r * (0.55 + 0.3 * np.abs(np.cos(a * puntas / 2.0)) ** 6)
        g = (np.abs(d - r) < 0.8) | (np.abs(d - r * 0.92) < 0.4) | ((np.abs(d - r * 0.55) < 0.5))
        borde = estrella & ~(d < r * (0.55 + 0.3 * np.abs(np.cos(a * puntas / 2.0)) ** 6) - 1.2)
        g = g | borde
        lz.pintar(suelo * g, "#8a5a24", 0.9)
        lz.pintar(suelo * desplazar(lz, g * 1.0, -0.6, -0.6) * g, "#f0c868", 0.8)
    for (cx, cy, r, n) in ((32, 44, 56, 6), (32, 63.5, 40, 12), (31.5 + 0.5, 18.5, 110, 12), (8.5, 44, 40, 4), (56.5, 44.5, 20, 4)):
        sello(cx * 16, cy * 16, r, n)
    # LA TINTA
    vt = 0.3 + (lz.ruido(12, 3, semilla=298) - 0.5) * 0.6 + np.sin(lz.y * 0.5 + lz.ruido(6, 2, semilla=299) * 8) * 0.06
    lz.pintar(tinta, rampa(AGUA_TINTA, np.clip(vt, 0, 1)))
    lz.pintar(np.clip(tinta - desplazar(lz, tinta, 0, 5), 0, 1), "#05040c", 0.8)
    lz.pintar(np.clip(tinta - desplazar(lz, tinta, 0, -1.5), 0, 1), "#9a8cc4", 0.6)
    # LA SIMA: un pozo negro, con baldas de libros muy al fondo y el canto del mármol roto arriba
    lz.pintar(sima, rampa(["#030208", "#07050f", "#0c0918", "#120e22"], np.clip(0.4 + (media - 0.5) * 0.6, 0, 1)))
    lz.pintar(sima * ((lz.y % 7) < 1.0) * (np.sin(lz.x * 0.3 + lz.y) > 0.1), "#1c1430", 0.7)
    lz.pintar(np.clip(sima - desplazar(lz, sima, 0, -4), 0, 1), "#6c5698", 0.9)
    # LAS ESTANTERÍAS ENCADENADAS: el canto de arriba y, al sur, la cara con libros oscuros y cadenas
    lz.pintar(pared, rampa(["#08060e", "#100c1a", "#1a1428", "#261e38"], np.clip(0.45 + (media - 0.5) * 0.3, 0, 1)))
    lz.pintar(pared * (((lz.x + lz.y * 0.5) % 11) < 0.6), "#05040a", 0.5)
    cara = np.clip(pared - desplazar(lz, pared, 0, -24), 0, 1)
    fila = np.floor(lz.y / 8)
    balda = ((lz.y % 8) < 1.6) * cara
    u = lz.x + fila * 5.3
    n_libro = np.floor(u / 3.5)
    azar_l = (np.sin(n_libro * 12.9898 + fila * 78.233) * 43758.5453) % 1
    libros_col = rampa(["#2a1030", "#3c1a44", "#1c2040", "#20303a", "#4a2a50", "#3a2a1c", "#2a1a3a", "#50305a"], azar_l)
    alto_libro = 1.6 + np.floor(((azar_l * 7.13) % 1) * 3)
    libro = cara * (1 - balda) * ((lz.y % 8) > alto_libro)
    lz.pintar(cara * (1 - balda), "#05030a")
    lz.pintar(libro, libros_col)
    lz.pintar(libro * ((u % 3.5) < 0.5), "#05030a", 0.8)
    lz.pintar(libro * (np.abs((lz.y % 8) - 5.2) < 0.3) * (azar_l > 0.55), "#c89a40", 0.5)
    lz.pintar(balda, "#1e1626")
    lz.pintar(cara * ((lz.y % 8) < 0.5), "#4a3a5c", 0.8)
    # las cadenas: eslabones en aspa por delante de los libros, con un candado de oro en cada cruce
    aspa = (np.abs(((lz.x + lz.y) % 40) - 20) < 1.0) | (np.abs(((lz.x - lz.y) % 40) - 20) < 1.0)
    eslabon = (((lz.x + lz.y * 0.0) % 3) < 1.6)
    lz.pintar(cara * aspa, "#2e2c38")
    lz.pintar(cara * aspa * eslabon, "#8a8898", 0.9)
    cruce = (np.abs(((lz.x + lz.y) % 40) - 20) < 2.2) & (np.abs(((lz.x - lz.y) % 40) - 20) < 2.2)
    lz.pintar(cara * cruce, "#c89a40")
    lz.pintar(cara * desplazar(lz, cruce * 1.0, -0.6, -0.6) * cruce, "#f8e098", 0.8)
    encima = np.clip(pared - cara, 0, 1)
    lz.pintar(np.clip(encima - desplazar(lz, encima, 0, 1.5), 0, 1), "#4a3a5c", 0.8)
    lz.pintar(np.clip(desplazar(lz, pared, 0, -3) - pared, 0, 1), "#05030a", 0.6)       # la sombra al pie
    destino = salida or os.path.join(RAIZ, "arte", "mundos", "sigilia", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.012)
    print("Suelo pintado:", destino, (lz.w, lz.h))


def pintar_desfiladero(nombre, salida=None):
    """El suelo de EL DESFILADERO DEL METEORITO (Asterhaul): un cañón de ROCA OCRE con estratos, polvo claro por
    donde se pisa, vetas y esquirlas de ÁMBAR que brillan, y grietas. Las paredes («0») son el cañón visto en 3/4:
    arriba la meseta morada (es de noche) y, al sur, la cara de roca en franjas con vetas de ámbar. Las VÍAS («=»)
    son dos raíles de hierro sobre traviesas de madera."""
    filas = leer(nombre)
    alto, ancho = len(filas), len(filas[0])
    lz = Lienzo(ancho * CASILLA, alto * CASILLA, s=2, semilla=41)
    tipos = [["pared" if c == "0" else "suelo" for c in f] for f in filas]
    pared = mascara(lz, tipos, ("pared",), 2.2, 0.16, semilla=411)
    fina = lz.ruido(0.8, 2, semilla=412)
    media = lz.ruido(10, 3, semilla=413)
    grande = lz.ruido(46, 3, semilla=414)
    S = lz.s
    # LA ROCA DEL SUELO: ocre, con estratos anchos que ondulan y polvo claro lejos de las paredes
    dist = lz.distancia(1 - pared)
    estrato = np.sin((lz.y + ruido_torcido_local(lz, 30, 415) * 60) * 0.16) * 0.5 + 0.5
    v = 0.42 + (grande - 0.5) * 0.35 + (media - 0.5) * 0.25 + (fina - 0.5) * 0.14 + (estrato - 0.5) * 0.1
    v += np.clip(dist / 40.0, 0, 1) * 0.12
    lz.pintar(np.ones((lz.H, lz.W)), rampa(["#2a1810", "#3e2416", "#573420", "#74482c", "#8e5e3a", "#a8764a", "#c0905e", "#d4a874"], np.clip(v, 0, 1)))
    mina = nombre == "galerias_ambar"
    if mina:
        # LAS GALERÍAS DE ÁMBAR: la BÓVEDA DE LAS GEODAS (sur) es de piedra azulada y fría; la CÁMARA DEL ANCLA
        # (oeste, ovalada) tiene un gran aro de bronce en el suelo y una argolla en el centro
        boveda = ((lz.y > 37.5 * 16) & (lz.x > 33 * 16) & (lz.x < 76 * 16)) * 1.0
        lz.pintar(boveda, rampa(["#12141e", "#1c2030", "#2a3044", "#3a4258", "#4c566e"], np.clip(0.4 + (grande - 0.5) * 0.4 + (media - 0.5) * 0.3 + (fina - 0.5) * 0.14, 0, 1)), 0.85)
        ra = np.sqrt(((lz.x - 14.5 * 16) / (13.0 * 16)) ** 2 + ((lz.y - 27.5 * 16) / (11.0 * 16)) ** 2)
        aro = ((np.abs(ra - 0.8) < 0.012) | (np.abs(ra - 0.2) < 0.02)) * 1.0
        lz.pintar(aro, "#6a4612")
        lz.pintar(desplazar(lz, aro, -0.6, -0.6) * aro, "#e0b860", 0.8)
        lz.pintar((ra < 0.18) * 1.0, "#2a1810", 0.45)
    # LA CANTERA HUNDIDA (sureste): bancales tallados que bajan hacia el centro, con las marcas del cincel
    cantera = ((lz.x > 46 * 16) & (lz.x < 78 * 16) & (lz.y > 36 * 16) & (lz.y < 55 * 16)) * (0.0 if mina else 1.0)
    borde = np.minimum(np.minimum(lz.x - 46 * 16, 78 * 16 - lz.x), np.minimum(lz.y - 36 * 16, 55 * 16 - lz.y))
    for k, d0 in enumerate((30.0, 62.0, 98.0)):
        dentro = cantera * (borde > d0)
        lz.pintar(dentro, "#1c0e08", 0.12)                                             # cada bancal, un poco más hondo
        lz.pintar(cantera * (np.abs(borde - d0 - 1.5) < 1.6), "#1c0e08", 0.55)          # la sombra del escalón
        lz.pintar(cantera * (np.abs(borde - d0 + 1.0) < 0.6), "#e8c090", 0.6)           # el canto, con luz
    lz.pintar(cantera * (((lz.x + lz.y * 0.35) % 9) < 0.5) * (media > 0.52), "#2a1810", 0.3)   # las marcas del cincel
    # guijarros y grietas
    guijarro = (lz.ruido(1.6, 1, semilla=416) > 0.78) * (media > 0.45)
    lz.pintar(guijarro * 1.0, "#5a3a26", 0.55)
    lz.pintar(desplazar(lz, guijarro * 1.0, -0.6, -0.6) * guijarro, "#e0b888", 0.35)
    grieta = np.abs(ruido_torcido_local(lz, 22, 417) - 0.5) < 0.012
    lz.pintar(grieta * (grande < 0.55), "#24140c", 0.6)
    # EL ÁMBAR: vetas finas que brillan y esquirlas sueltas
    veta = (np.abs(ruido_torcido_local(lz, 34, 418) - 0.5) < 0.01) * (lz.ruido(40, 2, semilla=419) > 0.5)
    lz.pintar(veta * 1.0, "#c8741c", 0.9)
    lz.pintar(desplazar(lz, veta * 1.0, -0.5, -0.5) * veta, "#ffd070", 0.8)
    rng = np.random.default_rng(420)
    esq = np.zeros((lz.H, lz.W), np.float32)
    luz_e = np.zeros((lz.H, lz.W), np.float32)
    for _ in range(260):
        x, y = int(rng.integers(8, lz.w - 8)), int(rng.integers(8, lz.h - 8))
        if filas[y // CASILLA][x // CASILLA] == "0":
            continue
        a, b = int(rng.integers(2, 4)), int(rng.integers(3, 6))
        pts = np.array([[x * S, (y - b) * S], [(x + a) * S, y * S], [x * S, (y + 1) * S], [(x - a) * S, y * S]], np.int32)
        cv2.fillConvexPoly(esq, pts, 1.0)
        cv2.fillConvexPoly(luz_e, np.array([[x * S, (y - b) * S], [x * S, (y + 1) * S], [(x - a) * S, y * S]], np.int32), 1.0)
    lz.pintar(desplazar(lz, esq, 1.2, 1.5) * (1 - esq), "#1c0e08", 0.5)
    lz.pintar(esq, "#d8841c")
    lz.pintar(luz_e, "#ffd878", 0.9)
    lz.sumar_luz(lz.desenfocar(esq, 5), "#ffb040", 0.35)
    # LAS VÍAS: traviesas de madera y dos raíles (cada casilla de vía se une con sus vecinas)
    trav = np.zeros((lz.H, lz.W), np.float32)
    rail = np.zeros((lz.H, lz.W), np.float32)
    es_via = lambda x, y: 0 <= y < alto and 0 <= x < ancho and filas[y][x] == "="
    for y in range(alto):
        for x in range(ancho):
            if not es_via(x, y):
                continue
            cx, cy = x * CASILLA + 8, y * CASILLA + 8
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if not es_via(x + dx, y + dy):
                    continue
                ex, ey = cx + dx * 8, cy + dy * 8
                px_, py_ = -dy, dx                                   # la perpendicular
                for k in (-3, 3):
                    cv2.line(rail, (int((cx + px_ * k) * S), int((cy + py_ * k) * S)), (int((ex + px_ * k) * S), int((ey + py_ * k) * S)), 1.0, S)
                for t in (2, 6):
                    mx, my = cx + dx * t, cy + dy * t
                    cv2.line(trav, (int((mx - px_ * 5) * S), int((my - py_ * 5) * S)), (int((mx + px_ * 5) * S), int((my + py_ * 5) * S)), 1.0, 2 * S)
    lz.pintar(desplazar(lz, trav, 0.8, 1.0) * (1 - trav), "#1c0e08", 0.5)
    lz.pintar(trav, rampa(["#3a2414", "#523420", "#6a462c"], np.clip(fina, 0, 1)))
    lz.pintar(desplazar(lz, rail, 0.6, 1.0) * (1 - rail), "#140a06", 0.6)
    lz.pintar(rail, "#565a6a")
    lz.pintar(desplazar(lz, rail, -0.5, -0.5) * rail, "#b8bccc", 0.8)
    # LAS PAREDES DEL CAÑÓN: la meseta de arriba (morada, de noche; en la mina, roca negra) y, al sur, la cara de roca en franjas
    lz.pintar(pared, rampa(["#0a0706", "#120c0a", "#1a120e", "#241812", "#2e2018"] if mina else ["#140c18", "#1e1222", "#2a1a2c", "#382236", "#462a3c"], np.clip(0.4 + (grande - 0.5) * 0.5 + (media - 0.5) * 0.3 + (fina - 0.5) * 0.12, 0, 1)))
    lz.pintar(pared * (np.abs(ruido_torcido_local(lz, 18, 421) - 0.5) < 0.014), "#0c0610", 0.6)
    cara = np.clip(pared - desplazar(lz, pared, 0, -26), 0, 1)
    franja = np.sin((lz.y + ruido_torcido_local(lz, 40, 422) * 30) * 0.9) * 0.5 + 0.5
    vc = 0.35 + (franja - 0.5) * 0.4 + (media - 0.5) * 0.25 + (fina - 0.5) * 0.12
    lz.pintar(cara, rampa(["#1e100c", "#341c12", "#4c2a1a", "#663a22", "#80502e", "#9a683e"], np.clip(vc, 0, 1)))
    lz.pintar(cara * (np.abs(((lz.x + lz.ruido(8, 2, semilla=423) * 30) % 23) - 11) < 0.5), "#1a0c08", 0.5)       # grietas verticales
    veta_c = cara * (np.abs(franja - 0.5) < 0.06) * (lz.ruido(26, 2, semilla=424) > 0.55)
    lz.pintar(veta_c, "#d8841c", 0.9)
    lz.sumar_luz(lz.desenfocar(veta_c, 3), "#ffb040", 0.3)
    encima = np.clip(pared - cara, 0, 1)
    lz.pintar(np.clip(encima - desplazar(lz, encima, 0, 1.6), 0, 1), "#6a4458", 0.8)          # el canto de la meseta
    lz.pintar(np.clip(desplazar(lz, pared, 0, -5) - pared, 0, 1), "#1c0e08", 0.55)            # la sombra al pie
    destino = salida or os.path.join(RAIZ, "arte", "mundos", "asterhaul", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.014)
    print("Suelo pintado:", destino, (lz.w, lz.h))


def pintar_nucleo(nombre, salida=None):
    """El suelo de EL NÚCLEO DE LA ESTRELLA (Asterhaul): BASALTO negro labrado en losas hexagonales con filetes de
    ámbar que laten hacia el centro; cada cámara con su tinte (la Sísmica, ocre; la Magnética, hierro; la de la
    Resonancia, piedra de estrella azulada). La escoria («≈») y los muelles de la Cámara Magnética, al rojo; las
    vías («=») de la Sísmica, raíles; el vacío («=» y «0») de la de la Resonancia, abismo estrellado. El SANTUARIO
    tiene una estrella de doce puntas de ámbar y tres arcos de hierro grabados (los aros del Corazón)."""
    filas = leer(nombre)
    alto, ancho = len(filas), len(filas[0])
    lz = Lienzo(ancho * CASILLA, alto * CASILLA, s=2, semilla=59)
    S = lz.s
    resonancia = lambda x, y: x >= 59 and 34 <= y <= 48
    tipos = []
    for y, f in enumerate(filas):
        fila = []
        for x, c in enumerate(f):
            if c == "≈" or (c == "=" and 32 <= y <= 46 and 36 <= x <= 48):
                fila.append("lava")
            elif resonancia(x, y) and c in "0=":
                fila.append("vacio")
            elif c == "0":
                fila.append("pared")
            else:
                fila.append("suelo")
        tipos.append(fila)
    pared = mascara(lz, tipos, ("pared",), 1.6, 0.1, semilla=591)
    lava = mascara(lz, tipos, ("lava",), 1.2, 0.05, semilla=592)
    vacio = mascara(lz, tipos, ("vacio",), 1.2, 0.05, semilla=593)
    suelo = np.clip(1 - pared - lava - vacio, 0, 1)
    fina = lz.ruido(0.8, 2, semilla=594)
    media = lz.ruido(10, 3, semilla=595)
    grande = lz.ruido(46, 3, semilla=596)
    # EL BASALTO: losas hexagonales (una rejilla de hexágonos de 14 px)
    hx = lz.x / 12.0
    hy = lz.y / 10.4 + (np.floor(hx) % 2) * 0.5
    junta = (np.abs((hx % 1) - 0.5) > 0.44) | (np.abs((hy % 1) - 0.5) > 0.45)
    celda = (np.sin(np.floor(hx) * 12.9898 + np.floor(hy) * 78.233) * 43758.5453) % 1
    v = 0.42 + (celda - 0.5) * 0.18 + (grande - 0.5) * 0.22 + (media - 0.5) * 0.16 + (fina - 0.5) * 0.1
    lz.pintar(np.ones((lz.H, lz.W)), rampa(["#0e0c12", "#1a1720", "#282430", "#383242", "#4a4256", "#5e566c"], np.clip(v, 0, 1)))
    # el tinte de cada cámara
    zona = lambda x0, y0, x1, y1: ((lz.x >= x0 * 16) & (lz.x < (x1 + 1) * 16) & (lz.y >= y0 * 16) & (lz.y < (y1 + 1) * 16)) * 1.0
    lz.pintar(zona(3, 34, 25, 56), "#8e5e3a", 0.28)
    lz.pintar(zona(30, 32, 54, 46), "#62697c", 0.26)
    lz.pintar(zona(59, 34, 81, 48), "#546280", 0.32)
    lz.pintar(suelo * junta, "#08060c", 0.75)
    lz.pintar(suelo * desplazar(lz, junta * 1.0, 0.7, 0.7) * (1 - junta), "#9a90b0", 0.12)
    # los filetes de ámbar: hilos que bajan por las juntas hacia el Santuario y laten
    hilo = suelo * junta * (np.abs(ruido_torcido_local(lz, 40, 597) - 0.5) < 0.05)
    lz.pintar(hilo, "#c8741c", 0.9)
    lz.sumar_luz(lz.desenfocar(hilo, 2), "#ffb040", 0.35)
    # EL SANTUARIO: la estrella de doce puntas y los tres arcos de hierro grabados
    cx, cy = 42.5 * 16, 14.5 * 16
    d = np.hypot((lz.x - cx) / 1.0, (lz.y - cy) / 0.72)
    a = np.arctan2((lz.y - cy) / 0.72, lz.x - cx)
    estrella = suelo * (d < 30 + 70 * np.abs(np.cos(a * 6)) ** 6) * (d > 26)
    lz.pintar(estrella, rampa(["#5a2406", "#9a4a0c", "#d8841c"], np.clip(0.5 + (media - 0.5) * 0.8, 0, 1)), 0.75)
    lz.pintar(np.clip(estrella - desplazar(lz, estrella, 1.0, 1.0), 0, 1), "#ffd878", 0.7)
    for r in (40.0, 54.0, 68.0):
        aro = suelo * (np.abs(d - r) < 1.2)
        lz.pintar(aro, "#3a3e4c")
        lz.pintar(desplazar(lz, aro, -0.6, -0.6) * aro, "#9aa2b6", 0.7)
    lz.pintar(suelo * (d < 24), "#05030a", 0.6)
    lz.sumar_luz(lz.desenfocar(suelo * (d < 24), 10), "#ff9a30", 0.35)
    # LAS VÍAS de la Cámara Sísmica: traviesas y raíles
    trav = np.zeros((lz.H, lz.W), np.float32)
    rail = np.zeros((lz.H, lz.W), np.float32)
    for y in range(alto):
        for x in range(ancho):
            if filas[y][x] == "=" and x < 30:
                x0, y0 = x * CASILLA, y * CASILLA
                for k in (-3, 3):
                    cv2.line(rail, (x0 * S, (y0 + 8 + k) * S), ((x0 + 16) * S, (y0 + 8 + k) * S), 1.0, S)
                for t in (2, 10):
                    cv2.line(trav, ((x0 + t) * S, (y0 + 3) * S), ((x0 + t) * S, (y0 + 13) * S), 1.0, 2 * S)
    lz.pintar(trav, "#523420")
    lz.pintar(rail, "#565a6a")
    lz.pintar(desplazar(lz, rail, -0.5, -0.5) * rail, "#b8bccc", 0.8)
    # LA ESCORIA
    corre = ruido_torcido_local(lz, 60, 598)
    vetas_l = np.sin((lz.y + corre * 90) * 0.10 + lz.ruido(60, 2, semilla=599) * 3) * 0.5 + 0.5
    vl = 0.46 + (vetas_l - 0.5) * 0.34 + (grande - 0.5) * 0.2 + (fina - 0.5) * 0.06
    lz.pintar(lava, rampa(["#7a1c04", "#b83a08", "#e86a10", "#f89a20", "#ffc848", "#fff0a0"], np.clip(vl, 0, 1)))
    costra_r = lz.ruido(22, 3, semilla=600)
    lz.pintar(lava * (costra_r > 0.66), "#2e120a")
    lz.pintar(lava * (costra_r > 0.64) * (costra_r <= 0.66), "#ffe070", 0.9)
    lz.sumar_luz(lz.desenfocar(lava, 12) * suelo, "#ff7a18", 0.5)
    # EL ABISMO de la Cámara de la Resonancia: añil con estrellas, y el fantasma del puente a puntos
    lz.pintar(vacio, rampa(["#05040c", "#0a0a1c", "#11142e", "#1a2044"], np.clip(0.4 + (grande - 0.5) * 0.5, 0, 1)))
    rng = np.random.default_rng(601)
    est = np.zeros((lz.H, lz.W), np.float32)
    for _ in range(220):
        x, y = int(rng.integers(59 * 16, 82 * 16)), int(rng.integers(34 * 16, 49 * 16))
        if tipos[y // CASILLA][x // CASILLA] == "vacio":
            cv2.rectangle(est, (x * S, y * S), (x * S + S - 1, y * S + S - 1), float(rng.uniform(0.4, 1.0)), -1)
    lz.pintar(est, "#dff4ff", 0.9)
    fant = np.zeros((lz.H, lz.W), np.float32)
    for y in range(alto):
        for x in range(ancho):
            if filas[y][x] == "=" and resonancia(x, y):
                for k in range(0, 16, 4):
                    for (ax, ay) in ((x * 16 + k, y * 16), (x * 16 + k, y * 16 + 15), (x * 16, y * 16 + k), (x * 16 + 15, y * 16 + k)):
                        cv2.rectangle(fant, (ax * S, ay * S), (ax * S + 2 * S - 1, ay * S + S - 1), 1.0, -1)
    lz.pintar(fant, "#6ad0f0", 0.3)
    canto = np.clip(desplazar(lz, suelo, 0, 18) - suelo, 0, 1) * vacio
    lz.pintar(canto, "#28344e")
    # LA ROCA: negra, con la cara al sur en franjas y vetas de ámbar
    lz.pintar(pared, rampa(["#06050a", "#0e0c14", "#18141e", "#221c2a"], np.clip(0.4 + (grande - 0.5) * 0.5 + (media - 0.5) * 0.3, 0, 1)))
    cara = np.clip(pared - desplazar(lz, pared, 0, -22), 0, 1)
    franja = np.sin((lz.y + ruido_torcido_local(lz, 40, 602) * 30) * 0.9) * 0.5 + 0.5
    lz.pintar(cara, rampa(["#140e12", "#241a20", "#36262e", "#4a343c"], np.clip(0.35 + (franja - 0.5) * 0.4 + (media - 0.5) * 0.25, 0, 1)))
    veta_c = cara * (np.abs(franja - 0.5) < 0.05) * (lz.ruido(26, 2, semilla=603) > 0.55)
    lz.pintar(veta_c, "#d8841c", 0.9)
    lz.sumar_luz(lz.desenfocar(veta_c, 3), "#ffb040", 0.3)
    encima = np.clip(pared - cara, 0, 1)
    lz.pintar(np.clip(encima - desplazar(lz, encima, 0, 1.6), 0, 1), "#4a3a4c", 0.8)
    lz.pintar(np.clip(desplazar(lz, pared, 0, -4) - pared, 0, 1), "#05030a", 0.5)
    destino = salida or os.path.join(RAIZ, "arte", "mundos", "asterhaul", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.014)
    print("Suelo pintado:", destino, (lz.w, lz.h))


def pintar_aguja(nombre, salida=None):
    """El suelo de LA AGUJA CAÍDA (Asterhaul): terrazas de PIEDRA DE ESTRELLA (pizarra azulada en lajas, con vetas
    de cristal turquesa) colgadas sobre el VIENTO ASTRAL: un abismo añil con estrellas y rachas de luz que corren
    en diagonal. Cada terraza enseña por el sur su canto de roca, que se afila hacia abajo. El NIDO DE LA CIMA
    (redondo) tiene un cerco de lascas de obsidiana y, en el centro, la argolla de la tercera cadena. Las casillas
    «=» (puentes de cristal y pasillos de peñasco) son abismo con el fantasma del cristal dibujado a puntos."""
    filas = leer(nombre)
    alto, ancho = len(filas), len(filas[0])
    lz = Lienzo(ancho * CASILLA, alto * CASILLA, s=2, semilla=53)
    tipos = [["vacio" if c in "0=" else "suelo" for c in f] for f in filas]
    vacio = mascara(lz, tipos, ("vacio",), 1.4, 0.06, semilla=531)
    suelo = np.clip(1 - vacio, 0, 1)
    fina = lz.ruido(0.8, 2, semilla=532)
    media = lz.ruido(10, 3, semilla=533)
    grande = lz.ruido(46, 3, semilla=534)
    S = lz.s
    # EL VIENTO ASTRAL: añil hondo, más claro hacia el centro, con rachas diagonales y estrellas
    racha = np.sin((lz.x * 0.55 + lz.y) * 0.035 + ruido_torcido_local(lz, 70, 535) * 9) * 0.5 + 0.5
    vv = 0.3 + (grande - 0.5) * 0.4 + (racha - 0.5) * 0.3 + (media - 0.5) * 0.12
    lz.pintar(np.ones((lz.H, lz.W)), rampa(["#05040c", "#0a0a1c", "#11142e", "#1a2044", "#24305c", "#304474"], np.clip(vv, 0, 1)))
    hilo = (np.abs(((lz.x * 0.55 + lz.y + ruido_torcido_local(lz, 50, 536) * 60) % 46) - 23) < 0.5) * (lz.ruido(30, 2, semilla=537) > 0.52)
    lz.pintar(hilo * 1.0, "#7fd6e6", 0.3)
    rng = np.random.default_rng(538)
    estrellas = np.zeros((lz.H, lz.W), np.float32)
    for _ in range(520):
        x, y = int(rng.integers(2, lz.w - 2)), int(rng.integers(2, lz.h - 2))
        if filas[y // CASILLA][x // CASILLA] in "0=":
            cv2.rectangle(estrellas, (x * S, y * S), (x * S + S - 1, y * S + S - 1), float(rng.uniform(0.4, 1.0)), -1)
    lz.pintar(estrellas, "#dff4ff", 0.9)
    # el fantasma de los puentes y los pasillos: losas de cristal dibujadas a puntos
    fantasma = np.zeros((lz.H, lz.W), np.float32)
    for y in range(alto):
        for x in range(ancho):
            if filas[y][x] == "=":
                x0, y0 = x * CASILLA, y * CASILLA
                for k in range(0, 16, 4):
                    for (ax, ay) in ((x0 + k, y0), (x0 + k, y0 + 15), (x0, y0 + k), (x0 + 15, y0 + k)):
                        cv2.rectangle(fantasma, (ax * S, ay * S), (ax * S + 2 * S - 1, ay * S + S - 1), 1.0, -1)
    lz.pintar(fantasma, "#6ad0f0", 0.28)
    # el canto de roca de cada terraza, por el sur: se afila hacia abajo, con cristales que cuelgan
    canto = np.clip(desplazar(lz, suelo, 0, 22) - suelo, 0, 1)
    afila = np.clip(1.0 - lz.distancia(suelo) / 22.0, 0, 1)
    diente = (np.sin(lz.x * 0.35 + lz.ruido(6, 2, semilla=539) * 5) * 0.5 + 0.5)
    canto = canto * (afila > diente * 0.55)
    lz.pintar(canto, rampa(["#0c1020", "#182036", "#28344e", "#3a4a68", "#506084"], np.clip(0.3 + afila * 0.5 + (media - 0.5) * 0.3, 0, 1)))
    lz.pintar(canto * (np.abs(ruido_torcido_local(lz, 14, 540) - 0.5) < 0.02), "#6ad0f0", 0.7)
    # LA PIEDRA DE ESTRELLA: lajas de pizarra azulada, irregulares
    u = lz.x + ruido_torcido_local(lz, 22, 541) * 22
    w = lz.y + ruido_torcido_local(lz, 22, 542) * 22
    junta = ((u % 26) < 0.9) | ((w % 15) < 0.9)
    celda = (np.sin(np.floor(u / 26) * 12.9898 + np.floor(w / 15) * 78.233) * 43758.5453) % 1
    vs = 0.46 + (celda - 0.5) * 0.24 + (grande - 0.5) * 0.2 + (media - 0.5) * 0.18 + (fina - 0.5) * 0.12
    lz.pintar(suelo, rampa(["#2c3246", "#3e4862", "#546280", "#6e7e9e", "#8a9ab8", "#a8b6ce", "#c6d2e2"], np.clip(vs, 0, 1)))
    lz.pintar(suelo * junta, "#1a2034", 0.6)
    lz.pintar(suelo * desplazar(lz, junta * 1.0, 0.7, 0.7) * (1 - junta), "#e4eef8", 0.2)
    veta = suelo * (np.abs(ruido_torcido_local(lz, 30, 543) - 0.5) < 0.009) * (lz.ruido(36, 2, semilla=544) > 0.5)
    lz.pintar(veta, "#2e9ac0", 0.9)
    lz.pintar(desplazar(lz, veta, -0.5, -0.5) * veta, "#c0f4ff", 0.8)
    lz.sumar_luz(lz.desenfocar(veta, 2), "#6ad0f0", 0.25)
    # el borde de las terrazas: un filo claro (la piedra pulida por el viento)
    dist = lz.distancia(suelo)
    lz.pintar(suelo * (dist < 2.2), "#0e1220", 0.55)
    lz.pintar(suelo * (np.abs(dist - 3.0) < 0.6), "#c0f4ff", 0.35)
    # EL NIDO DE LA CIMA: un cerco de lascas de obsidiana y la argolla de la cadena en el centro
    cx, cy = 35.5 * 16 + 8, 22.0 * 16 + 8
    rn = np.sqrt(((lz.x - cx) / (15.0 * 16)) ** 2 + ((lz.y - cy) / (11.0 * 16)) ** 2)
    an = np.arctan2((lz.y - cy) / 11.0, (lz.x - cx) / 15.0)
    lasca = suelo * (rn > 0.78) * (rn < 0.78 + 0.14 * (np.abs(np.sin(an * 23 + lz.ruido(5, 2, semilla=545) * 4)) ** 3))
    lz.pintar(lasca, rampa(["#06060c", "#0e0e1a", "#1a1a2c", "#2c2c44"], np.clip(0.4 + (fina - 0.5) * 0.9, 0, 1)))
    lz.pintar(np.clip(lasca - desplazar(lz, lasca, 0.8, 0.8), 0, 1), "#8a9ad8", 0.6)
    aro = suelo * ((np.abs(rn - 0.16) < 0.022) | (np.abs(rn - 0.5) < 0.008))
    lz.pintar(aro, "#3a4658")
    lz.pintar(desplazar(lz, aro, -0.6, -0.6) * aro, "#c4cad8", 0.8)
    lz.pintar(suelo * (rn < 0.135), "#080a14", 0.55)
    destino = salida or os.path.join(RAIZ, "arte", "mundos", "asterhaul", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.014)
    print("Suelo pintado:", destino, (lz.w, lz.h))


def pintar_mirador(nombre, salida=None):
    """El suelo de EL MIRADOR DEL OCASO (el Valle del Ocaso): mesetas de ARENISCA ROSADA, con ondas de arena que el
    viento peina y losas gastadas, colgadas sobre el ABISMO DEL ATARDECER: un cielo que se ve hacia abajo, malva
    arriba y coral y ámbar al fondo, con bancos de nubes quietas. Cada meseta enseña por el sur su canto de roca en
    franjas. La PLAZA lleva grabada la esfera de un gran reloj de sol; la ENTRADA y el ARCO, un camino de losas.
    Las sombras largas de los obeliscos las dibuja el juego."""
    filas = leer(nombre)
    alto, ancho = len(filas), len(filas[0])
    lz = Lienzo(ancho * CASILLA, alto * CASILLA, s=2, semilla=61)
    tipos = [["vacio" if c in "0=" else "suelo" for c in f] for f in filas]       # (en Jioni, «0» es abismo con pretil)
    vacio = mascara(lz, tipos, ("vacio",), 2.4, 0.24, semilla=611)
    suelo = np.clip(1 - vacio, 0, 1)
    fina = lz.ruido(0.8, 2, semilla=612)
    media = lz.ruido(10, 3, semilla=613)
    grande = lz.ruido(46, 3, semilla=614)
    # EL ABISMO DEL ATARDECER: de malva (arriba) a coral y ámbar (abajo), con nubes quietas en bandas
    alto_px = alto * CASILLA
    fondo = np.clip(lz.y / alto_px, 0, 1)
    nube = np.clip((lz.ruido(60, 3, semilla=615) - 0.45) * 3.0, 0, 1) * (np.sin(lz.y * 0.05 + grande * 4) * 0.5 + 0.5)
    vv = 0.15 + fondo * 0.55 + (grande - 0.5) * 0.25 + nube * 0.25
    lz.pintar(np.ones((lz.H, lz.W)), rampa(["#1a0e26", "#2e1640", "#4a2256", "#6e3062", "#9a4462", "#c45e5a", "#e8885a", "#f8b46a"], np.clip(vv, 0, 1)))
    lz.pintar(nube * (fina > 0.4), "#ffd8a8", 0.18)
    hilo = (np.abs(((lz.y + ruido_torcido_local(lz, 80, 616) * 40) % 38) - 19) < 0.5) * (lz.ruido(30, 2, semilla=617) > 0.55)
    lz.pintar(hilo * 1.0, "#ffc890", 0.25)
    # el canto de roca de cada meseta, por el sur: franjas de arenisca que se oscurecen hacia abajo
    canto = np.clip(desplazar(lz, suelo, 0, 34) - suelo, 0, 1)
    baja = np.clip(lz.distancia(suelo) / 34.0, 0, 1)
    franja = np.sin((lz.y + ruido_torcido_local(lz, 16, 618) * 10) * 0.55) * 0.5 + 0.5
    canto = canto * (baja < 0.95 - (np.sin(lz.x * 0.3 + media * 6) * 0.5 + 0.5) * 0.35)
    lz.pintar(canto, rampa(["#2a1020", "#4a1c2c", "#6e2c38", "#944044", "#b45a50"], np.clip(0.75 - baja * 0.6 + (franja - 0.5) * 0.25, 0, 1)))
    # LA ARENISCA: rosa y albaricoque, con ondas de arena y lajas gastadas
    onda = np.sin((lz.x * 0.6 + lz.y + ruido_torcido_local(lz, 24, 619) * 26) * 0.32) * 0.5 + 0.5
    vs = 0.52 + (grande - 0.5) * 0.22 + (media - 0.5) * 0.12 + (fina - 0.5) * 0.07 + (onda - 0.5) * 0.1
    lz.pintar(suelo, rampa(["#5a2a2a", "#7a3e36", "#9a5642", "#b87050", "#d08c62", "#e2a878", "#f0c494"], np.clip(vs, 0, 1)))
    lz.pintar(suelo * (onda > 0.88) * (media > 0.45), "#f8d8a8", 0.35)
    u = lz.x + ruido_torcido_local(lz, 22, 620) * 22
    w = lz.y + ruido_torcido_local(lz, 22, 621) * 22
    junta = ((u % 30) < 0.8) | ((w % 18) < 0.8)
    laja = suelo * (lz.ruido(40, 3, semilla=622) > 0.56)
    lz.pintar(laja * junta, "#6a3430", 0.55)
    # el camino de losas: de la entrada a la plaza y del arco a la bajada
    S = lz.s
    camino = np.zeros((lz.H, lz.W), np.float32)
    jioni = nombre == "jioni"
    calles = ((30, 0, 33, 14), (0, 20, 26, 22), (38, 26, 63, 28), (29, 30, 34, 43), (52, 29, 56, 43), (42, 26, 56, 30)) if jioni \
        else ((36, 1, 38, 10), (30, 38, 56, 41))
    for (x0, y0, x1, y1) in calles:
        cv2.rectangle(camino, (x0 * 16 * S, y0 * 16 * S), ((x1 + 1) * 16 * S - 1, (y1 + 1) * 16 * S - 1), 1.0, -1)
    camino = lz.desenfocar(camino, 3) > 0.5
    cw = (lz.y % 9) < 0.8
    cu = ((lz.x + np.floor(lz.y / 9) * 7) % 14) < 0.8            # (las losas, a matajunta)
    lz.pintar(camino * 1.0, rampa(["#7a4a3a", "#a06a50", "#c08a66", "#d8a880"], np.clip(0.5 + (fina - 0.5) * 0.6 + (media - 0.5) * 0.3, 0, 1)))
    lz.pintar(camino * (cu | cw), "#5a2e2a", 0.35)
    if jioni:
        # LA PLAZA DE LOS DOCE FAROLES: un gran disco de losas en corro
        cx, cy = 32.0 * 16, 22.0 * 16
        rp = np.hypot(lz.x - cx, (lz.y - cy) * 1.45)
        plaza = (rp < 150) * 1.0
        anillo = np.floor(rp / 22)
        sector = np.floor((np.arctan2(lz.y - cy, lz.x - cx) + np.pi) / (2 * np.pi) * (12 + anillo * 4))
        celda = (np.sin(anillo * 12.9898 + sector * 78.233) * 43758.5453) % 1
        lz.pintar(plaza, rampa(["#8a5444", "#b07a5e", "#cc9a74", "#e2b892"], np.clip(0.45 + (celda - 0.5) * 0.4 + (fina - 0.5) * 0.3, 0, 1)))
        junta_p = plaza * ((np.abs((rp % 22) - 11) > 10.2) | (np.abs(((np.arctan2(lz.y - cy, lz.x - cx) + np.pi) / (2 * np.pi) * (12 + anillo * 4)) % 1 - 0.5) > 0.47))
        lz.pintar(junta_p, "#5a2e2a", 0.45)
        lz.pintar(plaza * (np.abs(rp - 150) < 2.0), "#5a2e2a", 0.8)
    # LA ESFERA DEL RELOJ DE SOL, grabada en la plaza (alrededor del reloj)
    cx, cy = (32.0 * 16, 22.0 * 16) if jioni else (42.5 * 16, 23.0 * 16)
    r = np.hypot(lz.x - cx, (lz.y - cy) * 1.25)
    an = np.arctan2(lz.y - cy, lz.x - cx)
    e0, e1 = (40, 52) if jioni else (58, 70)
    esfera = suelo * ((np.abs(r - e1) < 1.2) | (np.abs(r - e0) < 0.8) | ((r > e0) & (r < e1) & (np.abs(((an * 12 / np.pi) % 2) - 1) < 0.06)))
    lz.pintar(esfera, "#6a3430", 0.75)
    lz.pintar(desplazar(lz, esfera, 0.7, 0.7) * (1 - esfera) * suelo, "#f8d0a0", 0.35)
    # el borde de las mesetas: un filo oscuro y un brillo cálido (les da el sol de lado)
    dist = lz.distancia(suelo)
    lz.pintar(suelo * (dist < 2.0), "#3a1420", 0.55)
    lz.pintar(suelo * (np.abs(dist - 3.0) < 0.6), "#ffd8a0", 0.3)
    if nombre == "jioni":
        # el pretil: un murete de arenisca al borde de la meseta
        pretil = suelo * (dist < 7.0)
        lz.pintar(pretil, rampa(["#5a2a2a", "#8a4a3e", "#b46a52", "#d48c66"], np.clip(0.4 + (7.0 - dist) / 14.0 + (fina - 0.5) * 0.3, 0, 1)))
        lz.pintar(suelo * (np.abs(dist - 7.0) < 0.8), "#3a1420", 0.7)
        lz.pintar(pretil * ((lz.x % 18) < 0.8), "#5a2a2a", 0.6)
    destino = salida or os.path.join(RAIZ, "arte", "mundos", "ocaso", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.014)
    print("Suelo pintado:", destino, (lz.w, lz.h))


def pintar_fundicion(nombre, salida=None):
    """El suelo de LA FUNDICIÓN DE ESCORIA (Asterhaul): un lago de ESCORIA FUNDIDA («≈») que corre despacio de
    oeste a este, naranja y amarilla, con costras negras que flotan; y, sobre ella, islas de LOSAS DE PIEDRA
    tiznadas con planchas de hierro remachadas y el canto de hierro al rojo. La Gran Fragua del Este (redonda)
    tiene un gran aro de bronce. Lo de fuera («0») es roca negra, con su cara en franjas."""
    filas = leer(nombre)
    alto, ancho = len(filas), len(filas[0])
    lz = Lienzo(ancho * CASILLA, alto * CASILLA, s=2, semilla=47)
    tipos = [["pared" if c == "0" else ("lava" if c in "≈=" else "suelo") for c in f] for f in filas]      # (los muelles «=» se ven escoria: encima va la barcaza)
    pared = mascara(lz, tipos, ("pared",), 2.0, 0.14, semilla=471)
    lava = mascara(lz, tipos, ("lava",), 1.2, 0.05, semilla=472) * (1 - pared)
    suelo = np.clip(1 - pared - lava, 0, 1)
    fina = lz.ruido(0.8, 2, semilla=473)
    media = lz.ruido(10, 3, semilla=474)
    grande = lz.ruido(46, 3, semilla=475)
    # LAS LOSAS: piedra gris parda tiznada, en sillares grandes, con planchas de hierro remachadas aquí y allá
    hilada = np.floor(lz.y / 24)
    junta = ((lz.y % 24) < 1.0) | (((lz.x + hilada * 20) % 40) < 1.0)
    celda = (np.sin(hilada * 12.9898 + np.floor((lz.x + hilada * 20) / 40) * 78.233) * 43758.5453) % 1
    v = 0.45 + (celda - 0.5) * 0.2 + (grande - 0.5) * 0.25 + (media - 0.5) * 0.2 + (fina - 0.5) * 0.12
    lz.pintar(np.ones((lz.H, lz.W)), rampa(["#1c1614", "#2e2420", "#44362e", "#5c4a3e", "#766050", "#907864", "#a89078"], np.clip(v, 0, 1)))
    lz.pintar(junta * 1.0, "#140e0c", 0.65)
    plancha = (celda > 0.78) * (1 - junta)
    lz.pintar(plancha, rampa(["#22262e", "#343a46", "#4a5262", "#62697c"], np.clip(0.5 + (media - 0.5) * 0.5 + (fina - 0.5) * 0.2, 0, 1)), 0.9)
    remache = plancha * ((np.abs((lz.x + hilada * 20) % 40 - 5) < 1.2) | (np.abs((lz.x + hilada * 20) % 40 - 35) < 1.2)) * ((np.abs(lz.y % 24 - 5) < 1.2) | (np.abs(lz.y % 24 - 19) < 1.2))
    lz.pintar(remache, "#9aa2b6", 0.9)
    lz.pintar((lz.ruido(5, 3, semilla=476) > 0.62) * 1.0, "#0e0a08", 0.3)                      # el tizne
    # el aro de bronce de la Gran Fragua
    ra = np.sqrt(((lz.x - 68.5 * 16) / (11.5 * 16)) ** 2 + ((lz.y - 29.5 * 16) / (11.5 * 16)) ** 2)
    aro = ((np.abs(ra - 0.78) < 0.012) | (np.abs(ra - 0.3) < 0.016)) * 1.0
    lz.pintar(aro, "#6a4612")
    lz.pintar(desplazar(lz, aro, -0.6, -0.6) * aro, "#e0b860", 0.8)
    # LA ESCORIA: corre de oeste a este (vetas largas), con costras negras de borde encendido
    corre = ruido_torcido_local(lz, 60, 477)
    vetas_l = np.sin((lz.y + corre * 90) * 0.10 + lz.ruido(60, 2, semilla=478) * 3) * 0.5 + 0.5
    vl = 0.46 + (vetas_l - 0.5) * 0.34 + (grande - 0.5) * 0.2 + (fina - 0.5) * 0.06
    lz.pintar(lava, rampa(["#7a1c04", "#b83a08", "#e86a10", "#f89a20", "#ffc848", "#fff0a0"], np.clip(vl, 0, 1)))
    costra_r = lz.ruido(22, 3, semilla=479) + (lz.ruido(4, 2, semilla=480) - 0.5) * 0.12
    costra = lava * (costra_r > 0.66)
    borde_c = lava * (costra_r > 0.64) * (costra_r <= 0.66)
    lz.pintar(borde_c, "#ffe070", 0.9)
    lz.pintar(costra, rampa(["#1c0a06", "#2e120a", "#44200e"], np.clip(0.5 + (fina - 0.5) * 0.8, 0, 1)))
    lz.pintar(costra * (np.abs(ruido_torcido_local(lz, 9, 481) - 0.5) < 0.02), "#f87a18", 0.8)   # grietas al rojo en la costra
    # el canto de las islas: hierro al rojo junto a la escoria, y el resplandor que sube a las losas
    dist_l = lz.distancia(1 - lava)
    canto = suelo * (dist_l < 3.2)
    lz.pintar(canto, "#2a1408", 0.85)
    lz.pintar(suelo * (np.abs(dist_l - 3.0) < 0.6), "#f8a040", 0.7)
    lz.sumar_luz(lz.desenfocar(lava, 14) * suelo, "#ff7a18", 0.55)
    lz.sumar_luz(lz.desenfocar(lava, 5) * lava, "#ffb040", 0.15)
    lz.pintar(np.clip(desplazar(lz, suelo, 0, 4) - suelo, 0, 1) * lava, "#3a0e02", 0.75)        # el lado sur de cada isla, en sombra
    # LA ROCA DE FUERA: negra, con su cara en franjas y el reflejo naranja de la escoria
    lz.pintar(pared, rampa(["#0a0706", "#120c0a", "#1a120e", "#241812", "#2e2018"], np.clip(0.4 + (grande - 0.5) * 0.5 + (media - 0.5) * 0.3 + (fina - 0.5) * 0.12, 0, 1)))
    cara = np.clip(pared - desplazar(lz, pared, 0, -26), 0, 1)
    franja = np.sin((lz.y + ruido_torcido_local(lz, 40, 482) * 30) * 0.9) * 0.5 + 0.5
    lz.pintar(cara, rampa(["#1e100c", "#341c12", "#4c2a1a", "#663a22", "#80502e"], np.clip(0.35 + (franja - 0.5) * 0.4 + (media - 0.5) * 0.25, 0, 1)))
    lz.sumar_luz(cara * lz.desenfocar(lava, 10), "#ff7a18", 0.6)
    encima = np.clip(pared - cara, 0, 1)
    lz.pintar(np.clip(encima - desplazar(lz, encima, 0, 1.6), 0, 1), "#5a3420", 0.8)
    destino = salida or os.path.join(RAIZ, "arte", "mundos", "asterhaul", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.014)
    print("Suelo pintado:", destino, (lz.w, lz.h))


def pintar_mji_jiwe(nombre, salida=None):
    """El suelo de MJI-JIWE, LA CIUDAD DEL CRÁTER (Asterhaul): un anfiteatro ovalado. TERRAZA ALTA de losas ocres
    irregulares; TERRAZA MEDIA de adoquín tallado en anillos; TERRAZA BAJA de basalto pulido con filetes de ámbar;
    en el centro, la LOSA DEL NÚCLEO: un disco de basalto y bronce con una estrella de doce puntas grabada y las
    TRES CADENAS que lo sellan. Calzadas claras hacia las salidas. Los muros de contención («0» entre terrazas) son
    sillares; lo de fuera, la pared del cráter (morada, de noche) con su cara de roca en franjas."""
    filas = leer(nombre)
    alto, ancho = len(filas), len(filas[0])
    lz = Lienzo(ancho * CASILLA, alto * CASILLA, s=2, semilla=43)
    tipos = [["pared" if c == "0" else "suelo" for c in f] for f in filas]
    pared = mascara(lz, tipos, ("pared",), 1.4, 0.05, semilla=431)
    fina = lz.ruido(0.8, 2, semilla=432)
    media = lz.ruido(10, 3, semilla=433)
    grande = lz.ruido(46, 3, semilla=434)
    CX, CY, RX, RY = 37.5 * 16 + 8, 28.5 * 16 + 8, 36.0 * 16, 27.0 * 16
    dx, dy = (lz.x - CX) / RX, (lz.y - CY) / RY
    r = np.sqrt(dx * dx + dy * dy)
    a = np.arctan2(dy, dx)
    alta = (r >= 0.72) * 1.0
    medi = ((r >= 0.45) & (r < 0.72)) * 1.0
    baja = ((r >= 0.19) & (r < 0.45)) * 1.0
    losa = (r < 0.19) * 1.0
    # TERRAZA ALTA: losas ocres irregulares (celdas torcidas por el ruido)
    u = lz.x + ruido_torcido_local(lz, 24, 435) * 26
    w = lz.y + ruido_torcido_local(lz, 24, 436) * 26
    junta_a = ((u % 22) < 1.0) | ((w % 17) < 1.0)
    celda = (np.sin(np.floor(u / 22) * 12.9898 + np.floor(w / 17) * 78.233) * 43758.5453) % 1
    va = 0.46 + (celda - 0.5) * 0.22 + (media - 0.5) * 0.2 + (fina - 0.5) * 0.12
    lz.pintar(np.ones((lz.H, lz.W)), rampa(["#2a1810", "#3e2416", "#573420", "#74482c", "#8e5e3a", "#a8764a", "#c0905e"], np.clip(va, 0, 1)))
    lz.pintar(junta_a * 1.0, "#24140c", 0.6)
    # TERRAZA MEDIA: adoquín tallado en anillos (juntas concéntricas y radiales alternas)
    anillo = np.floor(r * 46)
    junta_m = ((r * 46) % 1 < 0.09) | (((a * 28 + anillo * 0.5) % 1) < 0.07)
    celda_m = (np.sin(anillo * 12.9898 + np.floor(a * 28 + anillo * 0.5) * 78.233) * 43758.5453) % 1
    vm = 0.5 + (celda_m - 0.5) * 0.18 + (media - 0.5) * 0.16 + (fina - 0.5) * 0.1
    lz.pintar(medi, rampa(["#3a2618", "#55381f", "#72502e", "#8f6a40", "#aa8656", "#c4a270", "#dcbe8c"], np.clip(vm, 0, 1)))
    lz.pintar(medi * junta_m, "#2a1810", 0.6)
    # TERRAZA BAJA: basalto pulido, con filetes de ámbar concéntricos y doce rayos (uno por yunque)
    vb = 0.42 + (grande - 0.5) * 0.3 + (media - 0.5) * 0.2 + (fina - 0.5) * 0.1
    lz.pintar(baja, rampa(["#14121c", "#201e2c", "#2e2c3e", "#403e54", "#56546c", "#6e6c86"], np.clip(vb, 0, 1)))
    lz.pintar(baja * (np.abs(ruido_torcido_local(lz, 26, 437) - 0.5) < 0.012), "#8a88a0", 0.4)
    filete = (np.abs(r - 0.225) < 0.004) | (np.abs(r - 0.40) < 0.004) | ((np.abs(((a / (np.pi / 6)) + 0.5) % 1 - 0.5) < 0.012) & (r > 0.33))
    lz.pintar(baja * filete, "#c8741c", 0.95)
    lz.pintar(baja * desplazar(lz, filete * 1.0, -0.5, -0.5) * filete, "#ffd070", 0.8)
    # LA LOSA DEL NÚCLEO: disco de basalto y bronce, estrella de doce puntas grabada, y un resquicio de luz en el borde
    vl = 0.4 + (media - 0.5) * 0.3 + (fina - 0.5) * 0.14
    lz.pintar(losa, rampa(["#0c0a12", "#16141e", "#22202c", "#302e3c", "#42404e"], np.clip(vl, 0, 1)))
    estrella = (r < 0.05 + 0.115 * np.abs(np.cos(a * 6)) ** 4) * losa
    lz.pintar(estrella, rampa(["#3a2408", "#6a4612", "#9a6c20", "#c4963a"], np.clip(0.5 + (media - 0.5) * 0.6, 0, 1)), 0.9)
    lz.pintar(np.clip(estrella - desplazar(lz, estrella, 1.0, 1.0), 0, 1), "#f0cc78", 0.7)
    aro = (np.abs(r - 0.182) < 0.008) * 1.0
    lz.pintar(aro, "#6a4612")
    lz.pintar(desplazar(lz, aro, -0.6, -0.6) * aro, "#e0b860", 0.8)
    resquicio = (np.abs(r - 0.192) < 0.003) * 1.0
    lz.pintar(resquicio, "#ffb040", 0.9)
    lz.sumar_luz(lz.desenfocar(resquicio, 4), "#ff9a30", 0.5)
    # LAS TRES CADENAS: del centro a tres argollas en el borde de la losa
    cad = np.zeros((lz.H, lz.W), np.float32)
    S = lz.s
    for ang in (np.pi / 2, np.pi / 2 + 2 * np.pi / 3, np.pi / 2 + 4 * np.pi / 3):
        x1, y1 = CX + np.cos(ang) * RX * 0.215, CY + np.sin(ang) * RY * 0.215
        n = 26
        for i in range(n + 1):
            t = 0.12 + 0.88 * i / n
            px_, py_ = CX + (x1 - CX) * t, CY + (y1 - CY) * t
            eje = (5, 3) if i % 2 else (3, 5)
            cv2.ellipse(cad, (int(px_ * S), int(py_ * S)), (eje[0] * S // 2 + S, eje[1] * S // 2 + S), float(np.degrees(ang)), 0, 360, 1.0, S)
        cv2.circle(cad, (int(x1 * S), int(y1 * S)), 5 * S, 1.0, 2 * S)
    lz.pintar(desplazar(lz, cad, 1.0, 1.4) * (1 - cad), "#05040a", 0.7)
    lz.pintar(cad, "#565a6a")
    lz.pintar(desplazar(lz, cad, -0.5, -0.5) * cad, "#c4cad8", 0.8)
    # LAS CALZADAS: franjas claras hacia el oeste, el este, el norte y la entrada del suroeste
    def franja(ang, medio):
        d = np.abs(np.arctan2(np.sin(a - ang), np.cos(a - ang)))
        return (d < medio / np.maximum(r, 0.2)) * (r > 0.46)
    calz = np.clip(franja(np.pi, 0.035) + franja(0.0, 0.035) + franja(-np.pi / 2, 0.045) + franja(np.radians(140), 0.04), 0, 1) * 1.0
    calz = np.clip(calz + ((lz.y > 44 * 16) & (lz.y < 47 * 16) & (lz.x < 13 * 16)), 0, 1)
    lz.pintar(calz, "#e8cc98", 0.28)
    lz.pintar(np.clip(calz - desplazar(lz, calz, 0, 1.2), 0, 1) + np.clip(calz - desplazar(lz, calz, 0, -1.2), 0, 1), "#3a2414", 0.4)
    # esquirlas de ámbar sueltas (pocas: es una ciudad barrida)
    veta = (np.abs(ruido_torcido_local(lz, 34, 438) - 0.5) < 0.008) * (lz.ruido(40, 2, semilla=439) > 0.6) * (alta + medi)
    lz.pintar(veta, "#c8741c", 0.8)
    # LOS MUROS: fuera, la pared del cráter; entre terrazas, sillares de contención (más bajos y claros)
    fuera = pared * (r > 0.9)
    muro_t = pared * (r <= 0.9)
    lz.pintar(fuera, rampa(["#140c18", "#1e1222", "#2a1a2c", "#382236", "#462a3c"], np.clip(0.4 + (grande - 0.5) * 0.5 + (media - 0.5) * 0.3 + (fina - 0.5) * 0.12, 0, 1)))
    cara = np.clip(fuera - desplazar(lz, fuera, 0, -26), 0, 1)
    franja_c = np.sin((lz.y + ruido_torcido_local(lz, 40, 440) * 30) * 0.9) * 0.5 + 0.5
    lz.pintar(cara, rampa(["#1e100c", "#341c12", "#4c2a1a", "#663a22", "#80502e", "#9a683e"], np.clip(0.35 + (franja_c - 0.5) * 0.4 + (media - 0.5) * 0.25, 0, 1)))
    veta_c = cara * (np.abs(franja_c - 0.5) < 0.06) * (lz.ruido(26, 2, semilla=441) > 0.55)
    lz.pintar(veta_c, "#d8841c", 0.9)
    lz.pintar(np.clip(fuera - cara - desplazar(lz, fuera - cara, 0, 1.6), 0, 1), "#6a4458", 0.8)
    lz.pintar(muro_t, rampa(["#4a3220", "#64462c", "#80603c", "#9c7c52", "#b8986a"], np.clip(0.5 + (media - 0.5) * 0.3 + (fina - 0.5) * 0.15, 0, 1)))
    cara_t = np.clip(muro_t - desplazar(lz, muro_t, 0, -12), 0, 1)
    sillar = ((lz.y % 6) < 0.8) | (((lz.x + np.floor(lz.y / 6) * 5) % 11) < 0.8)
    lz.pintar(cara_t, rampa(["#2e1c12", "#44291a", "#5c3a24", "#765032"], np.clip(0.5 + (media - 0.5) * 0.4, 0, 1)))
    lz.pintar(cara_t * sillar, "#1c0e08", 0.6)
    lz.pintar(np.clip(muro_t - cara_t - desplazar(lz, muro_t - cara_t, 0, 1.4), 0, 1), "#e0c08c", 0.7)      # el canto del muro
    lz.pintar(np.clip(desplazar(lz, pared, 0, -4) - pared, 0, 1), "#1c0e08", 0.5)                            # la sombra al pie
    destino = salida or os.path.join(RAIZ, "arte", "mundos", "asterhaul", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.014)
    print("Suelo pintado:", destino, (lz.w, lz.h))


def ruido_torcido_local(lz, escala, semilla):
    from pintor import ruido_torcido
    return ruido_torcido(lz, escala, 4, semilla)


def pintar(nombre, salida=None):
    if nombre in ("gruta_raices", "cueva_setas"):
        return pintar_gruta(nombre, salida, setas=nombre == "cueva_setas")
    if nombre in OBSERVATORIOS:
        return pintar_observatorio(nombre, salida)
    if nombre == "seccion_prohibida":
        return pintar_seccion(nombre, salida)
    if nombre in ("desfiladero_meteorito", "galerias_ambar"):
        return pintar_desfiladero(nombre, salida)
    if nombre == "mji_jiwe":
        return pintar_mji_jiwe(nombre, salida)
    if nombre == "fundicion_escoria":
        return pintar_fundicion(nombre, salida)
    if nombre == "aguja_caida":
        return pintar_aguja(nombre, salida)
    if nombre in ("mirador_ocaso", "jioni"):
        return pintar_mirador(nombre, salida)
    if nombre == "nucleo_estrella":
        return pintar_nucleo(nombre, salida)
    if nombre in BIBLIOTECAS:
        return pintar_biblioteca(nombre, salida)
    filas = leer(nombre)
    cobrizo = nombre == "camino_cobrizo"
    senda = nombre == "senda_surcos"
    canada = nombre == "canada_eco"
    espejo = nombre == "lago_espejo"
    orilla_j = nombre in ("orilla_juncos", "embarcadero_junco")
    tipos = tipos_de(filas, derrumbe=cobrizo or senda, escala=canada)
    alto, ancho = len(filas), len(filas[0])
    lz = Lienzo(ancho * CASILLA, alto * CASILLA, s=2, semilla=7)
    luz = (-0.6, -0.7)

    bosque = nombre.startswith("bosque")
    cienaga = nombre.startswith("cienaga")
    paso = nombre == "paso_piedra"
    campo = nombre.startswith("campo") or paso
    hierba_r = HIERBA_BOSQUE if bosque else (HIERBA_CIENAGA if cienaga else (HIERBA_CAMPO if campo else HIERBA_R))
    agua_r = AGUA_CIENAGA if cienaga else (AGUA_TINTA if nombre == "canal_tinta" else AGUA_R)
    # ---- hierba: base con manchas grandes, matas medianas y briznas finas
    grande = lz.ruido(60, 3, semilla=1)
    media = lz.ruido(9, 3, semilla=2)
    fina = lz.ruido(0.7, 2, semilla=3)
    briznas = estirar(fina, 5)
    punta = np.clip(briznas - desplazar(lz, briznas, 0, 1.0), 0, 1)          # la punta de cada brizna, iluminada
    v = 0.5 + (grande - 0.5) * 0.18 + (media - 0.5) * 0.16 + (briznas - 0.5) * 0.26 + punta * 0.55
    lz.pintar(np.ones((lz.H, lz.W)), rampa(hierba_r, np.clip(v, 0, 1)))
    if cobrizo or senda:
        # los caminos que suben de sur a norte cambian de hierba: hacia el bosque (más oscura) o hacia el campo (seca)
        desde, largo, rampa_n = (66, 40, HIERBA_BOSQUE) if cobrizo else (60, 45, HIERBA_CAMPO)
        hacia = np.clip((desde * CASILLA - lz.y) / (largo * CASILLA) + (grande - 0.5) * 0.5, 0, 1)
        lz.pintar(hacia, rampa(rampa_n, np.clip(v, 0, 1)))
    if paso:
        # el Paso de Piedra: la hierba seca del campo se va volviendo gravilla gris hacia la cantera (este)
        hacia = np.clip((lz.x - 60 * CASILLA) / (60 * CASILLA) + (grande - 0.5) * 0.6, 0, 0.85)
        grava = np.clip(0.45 + (media - 0.5) * 0.5 + (fina - 0.5) * 0.5, 0, 1)
        lz.pintar(hacia, rampa(["#3a3630", "#57524a", "#76705f", "#958e7c", "#b3ab98"], grava))
    if canada:
        # la Cañada va de este a oeste: junto al Bosque Cobrizo (este) la hierba es la del bosque
        hacia = np.clip((lz.x - 96 * CASILLA) / (34 * CASILLA) + (grande - 0.5) * 0.5, 0, 1)
        lz.pintar(hacia, rampa(HIERBA_BOSQUE, np.clip(v, 0, 1)))
    # matas de hierba más alta (bultos con sombra abajo a la derecha)
    matas = np.clip((lz.ruido(3.2, 3, semilla=4) - 0.62) * 6, 0, 1)
    sombra_m = np.clip(desplazar(lz, matas, 1.2, 1.4) - matas, 0, 1)
    lz.pintar(sombra_m, ("#2b4220" if not bosque else "#141f10") if not campo else hierba_r[1], 0.4)
    lz.pintar(matas * (briznas > 0.45), rampa(hierba_r[4:], briznas), 0.8)
    # tréboles y hojitas sueltas
    treb = np.clip((lz.ruido(1.4, 2, semilla=5) - 0.78) * 8, 0, 1) * (grande > 0.5)
    lz.pintar(treb, "#829856" if not campo else hierba_r[5], 0.7)

    # ---- flores en las casillas «,» (y alguna suelta por la hierba)
    fl = mascara(lz, tipos, ("flores",), 4, 0.4, semilla=6)
    rng = np.random.default_rng(8)
    puntos = np.zeros((lz.H, lz.W))
    colores = np.zeros((lz.H, lz.W, 3))
    paleta_f = [hex2("#e6a852"), hex2("#de6771"), hex2("#fff3c4"), hex2("#c98ad6"), hex2("#f1c27a")]
    ys, xs = np.nonzero(fl > 0.5)
    if len(xs):
        elegidos = rng.choice(len(xs), size=min(len(xs) // 90, 4000), replace=False)
        for i in elegidos:
            x, y = xs[i], ys[i]
            r = int(lz.s * (0.8 + rng.random() * 0.7))
            c = paleta_f[rng.integers(len(paleta_f))]
            cv2.circle(puntos, (int(x), int(y)), r, 1.0, -1)
            cv2.circle(colores, (int(x), int(y)), r, tuple(float(k) for k in c), -1)
            cv2.circle(puntos, (int(x + lz.s), int(y + lz.s)), r, 0.0, -1)
    sombra_f = np.clip(desplazar(lz, puntos, 0.8, 1.0) - puntos, 0, 1)
    lz.pintar(sombra_f, "#1d2e18", 0.6)
    lz.pintar(puntos, colores)
    corazon = np.clip(puntos - cv2.dilate(1 - puntos.astype(np.float32), np.ones((3, 3), np.uint8)), 0, 1) * 0
    lz.pintar(puntos * (fina > 0.75), "#fde27e", 0.6)

    # ---- camino de tierra
    cam = mascara(lz, tipos, ("camino", "losas", "puente_piedra"), 7, 0.25, semilla=9)
    if cam.max() > 0:
        tierra = 0.55 + (lz.ruido(14, 3, semilla=10) - 0.5) * 0.22 + (lz.ruido(1.2, 2, semilla=11) - 0.5) * 0.3
        lz.pintar(cam, rampa(TIERRA_R, np.clip(tierra, 0, 1)))
        # piedrecitas con luz arriba y sombra abajo
        piedras = np.clip((lz.ruido(1.0, 2, semilla=12) - 0.8) * 10, 0, 1) * cam
        lz.pintar(np.clip(desplazar(lz, piedras, 0.6, 0.8) - piedras, 0, 1), "#2b1e17", 0.7)
        lz.pintar(piedras, rampa(["#7a806d", "#a0a596", "#bfc3b4"], fina), 0.9)
        # rodadas y pisadas: surcos suaves
        surco = np.clip(1 - np.abs(lz.ruido(30, 2, semilla=13) - 0.5) * 9, 0, 1) * cam * 0.35
        lz.pintar(surco, "#3f2c21", 0.6)
        # la hierba se come el borde del camino, con briznas por encima
        borde = np.clip(1 - np.abs(cam - 0.5) * 2.2, 0, 1)
        invade = (briznas > 0.55) * borde * (1 - cam * 0.3)
        lz.pintar(invade, rampa((HIERBA_R if not campo else hierba_r)[2:], briznas), 0.85)
        lz.pintar(np.clip(desplazar(lz, cam, 0, -1.2) - cam, 0, 1), "#3f582f" if not campo else hierba_r[2], 0.5)

    # ---- surcos de tierra labrada: lomos horizontales con luz arriba y sombra abajo, y rastrojo de trigo segado
    su = mascara(lz, tipos, ("surco",), 2.5, 0.2, semilla=21)
    if su.max() > 0:
        fase_s = (lz.y + (lz.ruido(20, 2, semilla=22) - 0.5) * 2.0) % 8.0
        lomo = np.clip(np.sin(fase_s / 8.0 * 2 * np.pi) * 0.5 + 0.5, 0, 1)
        vs = 0.25 + lomo * 0.45 + (lz.ruido(1.0, 2, semilla=23) - 0.5) * 0.25 + (lz.ruido(12, 3, semilla=24) - 0.5) * 0.15
        lz.pintar(su, rampa(SURCO, np.clip(vs, 0, 1)))
        # rastrojo: tallitos cortados en lo alto de cada lomo
        rastrojo = (lomo > 0.8) * (lz.ruido(0.5, 1, semilla=25) > 0.72) * su
        lz.pintar(estirar(rastrojo.astype(np.float32), 3) > 0.5, "#a37036", 0.8)
        lz.pintar(rastrojo, "#d29a43", 0.6)
        # terrones con su sombra
        terron = np.clip((lz.ruido(1.2, 2, semilla=26) - 0.82) * 10, 0, 1) * su
        lz.pintar(np.clip(desplazar(lz, terron, 0.6, 0.8) - terron, 0, 1), "#1d140f", 0.6)
        lz.pintar(terron, "#7c5843", 0.8)

    # ---- losas de piedra
    los = mascara(lz, tipos, ("losas",), 5, 0.2, semilla=14)
    if los.max() > 0:
        from scipy.spatial import cKDTree
        semillas = []
        for gy in np.arange(0, lz.h + 10, 8):
            for gx in np.arange(0, lz.w + 10, 9):
                semillas.append((gx + rng.random() * 7, gy + rng.random() * 6))
        semillas = np.array(semillas)
        arbol = cKDTree(semillas)
        d, idx = arbol.query(np.stack([lz.x.ravel(), lz.y.ravel()], 1), k=2)
        borde_v = (d[:, 1] - d[:, 0]).reshape(lz.H, lz.W)
        tono = (np.sin(idx[:, 0] * 12.9898) * 43758.5453 % 1).reshape(lz.H, lz.W)
        cara = np.clip(borde_v / 3.0, 0, 1)
        # cada losa abombada: más clara arriba a la izquierda
        alto_l = np.sqrt(cara)
        gy_, gx_ = np.gradient(cv2.GaussianBlur(alto_l.astype(np.float32), (0, 0), 1.5))
        ilum = np.clip(0.5 + (-gx_ * luz[0] - gy_ * luz[1]) * 18, 0, 1)
        v_l = 0.35 + tono * 0.25 + (ilum - 0.5) * 0.5 + (fina - 0.5) * 0.15
        lz.pintar(los, rampa(PIEDRA_R, np.clip(v_l, 0, 1)))
        juntas = np.clip(1 - borde_v / 0.9, 0, 1) * los
        lz.pintar(juntas, rampa(["#1d2e18", "#2b4220", "#2e302a"], media), 0.95)

    # ---- agua: honda en el centro, clara y con orilla mojada en el borde
    agua = mascara(lz, tipos, ("agua", "vado"), 6, 0.2, semilla=15)
    if agua.max() > 0:
        prof = cv2.distanceTransform((agua > 0.5).astype(np.uint8), cv2.DIST_L2, 5) / lz.s
        hondo = np.clip(prof / 30, 0, 1)
        ancho_orilla = 9 if cienaga else 5
        orilla_moj = np.clip(cv2.dilate((agua > 0.5).astype(np.uint8), np.ones((int(ancho_orilla * lz.s), int(ancho_orilla * lz.s)), np.uint8)).astype(float) - agua, 0, 1)
        if cienaga:
            # barro húmedo con charquitos y huellas
            barro = lz.desenfocar(orilla_moj, 2.0) * np.clip(0.6 + (media - 0.5) * 1.2, 0, 1)
            lz.pintar(barro, rampa(["#1f1a12", "#2e2619", "#3f3420", "#52442a"], np.clip(media * 0.8 + fina * 0.2, 0, 1)), 0.85)
        lz.pintar(lz.desenfocar(orilla_moj, 0.8), "#3f2c21" if not cienaga else "#2a2418", 0.75)
        lz.pintar(np.clip(orilla_moj - desplazar(lz, orilla_moj, 0, 1.5), 0, 1) * 0, "#000000", 0)
        ondas = np.sin(lz.y * 1.3 + (lz.ruido(10, 3, semilla=16) - 0.5) * 14) * 0.5 + 0.5
        reflejo_cielo = np.clip(1 - hondo * 1.5, 0, 1)
        va = 0.8 - hondo * 0.35 + (ondas - 0.5) * 0.06 + (media - 0.5) * 0.08
        lz.pintar(agua, rampa(agua_r, np.clip(va, 0, 1)))
        # brillos de luz en las crestas de las ondas
        brillo = (ondas > 0.93) * (fina > 0.55) * agua * np.clip(hondo * 3, 0, 1)
        lz.pintar(brillo, "#9fd0d0" if not cienaga else "#8aa697", 0.85 if not cienaga else 0.5)
        lz.pintar((ondas > 0.97) * (fina > 0.8) * agua, "#e8f0dc", 0.8)
        # la línea clara de la orilla (espuma) y la sombra de la orilla sobre el agua (arriba)
        linea = np.clip(1 - np.abs(prof - 1.0) / 0.8, 0, 1) * agua
        lz.pintar(linea, "#9fd0d0", 0.55)
        sombra_o = np.clip(1 - prof / 4, 0, 1) * agua * np.clip(desplazar(lz, 1 - agua, 0, 3) , 0, 1)
        lz.pintar(sombra_o, "#122626", 0.35)
        # piedrecitas y juncos en la orilla
        juncos = (orilla_moj > 0.5) * (lz.ruido(1.5, 2, semilla=17) > 0.8)
        lz.pintar(juncos * estirar(fina, 7) > 0.6, "#526d38", 0.9)
        if espejo:
            _agua_espejo(lz, agua, prof, fina)
        if orilla_j:
            _playas(lz, agua, fina, media)

    # ---- puentes y pasarelas de tablas: las tablas van de través (en las pasarelas que bajan, en horizontal),
    #      con vigas en los bordes, pilotes que asoman y la sombra sobre el agua
    pu = mascara(lz, tipos, ("puente",), 0.5, 0.0, semilla=18)
    if pu.max() > 0:
        vertical = np.zeros((lz.H, lz.W), np.float32)
        for ty in range(alto):
            for tx in range(ancho):
                if tipos[ty][tx] != "puente":
                    continue
                arriba_abajo = sum(1 for dy in (-1, 1) if 0 <= ty + dy < alto and tipos[ty + dy][tx] == "puente")
                lados = sum(1 for dx in (-1, 1) if 0 <= tx + dx < ancho and tipos[ty][tx + dx] == "puente")
                # una pasarela de 2 de ancho que baja: sus vecinas de arriba/abajo son puente y solo una de los lados
                if arriba_abajo == 2 and lados <= 1:
                    vertical[int(ty * 16 * lz.s):int((ty + 1) * 16 * lz.s), int(tx * 16 * lz.s):int((tx + 1) * 16 * lz.s)] = 1
        coord = np.where(vertical > 0.5, lz.y, lz.x)
        tabla = (coord // 4) % 2
        veta = np.where(vertical > 0.5, estirar(lz.ruido(0.8, 2, semilla=19), 9, False), estirar(lz.ruido(0.8, 2, semilla=19), 9))
        tono = (np.sin((coord // 4) * 12.9) * 4375.5) % 1
        vp = 0.48 + (tabla - 0.5) * 0.12 + (veta - 0.5) * 0.35 + (tono - 0.5) * 0.18
        # sombra sobre el agua (abajo y a la derecha)
        lz.pintar(np.clip(desplazar(lz, pu, 1.0, 3.0) - pu, 0, 1), "#122626", 0.55)
        lz.pintar(pu, rampa(MADERA_R, np.clip(vp, 0, 1)))
        lz.pintar(pu * ((coord % 4) < 0.6), "#251812", 0.9)
        # clavos
        lz.pintar(pu * ((coord % 4) > 1.6) * ((coord % 4) < 2.2) * (((np.where(vertical > 0.5, lz.x, lz.y)) % 16) > 2.5) *
                  (((np.where(vertical > 0.5, lz.x, lz.y)) % 16) < 3.3), "#7a806d", 0.6)
        # vigas en los bordes (oscuras) y su canto claro
        borde = np.clip(pu - cv2.erode((pu > 0.5).astype(np.uint8), np.ones((int(2 * lz.s), int(2 * lz.s)), np.uint8)), 0, 1)
        lz.pintar(borde, "#3a261d", 0.9)
        # pilotes: postes redondos que asoman en las esquinas, cada dos casillas
        rng_p = np.random.default_rng(20)
        postes = np.zeros((lz.H, lz.W), np.float32)
        for ty in range(alto):
            for tx in range(ancho):
                if tipos[ty][tx] != "puente" or (tx + ty) % 2:
                    continue
                for (dx, dy) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx, ny = tx + dx, ty + dy
                    if 0 <= nx < ancho and 0 <= ny < alto and tipos[ny][nx] == "agua":
                        px_ = tx * 16 + 8 + dx * 8.5
                        py_ = ty * 16 + 8 + dy * 8.5
                        postes = np.maximum(postes, lz.circulo(px_, py_, 1.9 + rng_p.random() * 0.4).astype(np.float32))
        lz.pintar(np.clip(desplazar(lz, postes, 0.6, 1.2) - postes, 0, 1), "#122626", 0.6)
        lz.pintar(postes, rampa(MADERA_R[1:6], np.clip(0.5 + (fina - 0.5) * 0.4 - (lz.y % 4) * 0.05, 0, 1)))
        lz.pintar(postes * (lz.ruido(0.5, 1, semilla=21) > 0.6), "#a8735a", 0.6)

    _puente_piedra(lz, tipos, alto, ancho, fina, media)
    olvidado = nombre in ("sendero_olvidado", "paso_escarcha", "maandiko", "canal_tinta")
    ruinas = nombre in ("ruinas_primer_arbol", "maandiko", "canal_tinta")
    pared = _riscos(lz, tipos, fina, media, cara=2.0 if (canada or paso or olvidado or ruinas) else 1.0)
    if olvidado or ruinas:
        _nevar(lz, tipos, fina, media, pared, conservar=("losas",) if ruinas else (), lila=nombre in SIGILIA, sin_agua=nombre == "canal_tinta")
    if canada or paso:
        _mesetas(lz, tipos, fina, media, pared)

    if bosque:
        _hojarasca(lz, tipos, alto, ancho)
    if cobrizo:
        _hojarasca(lz, tipos, alto, ancho, lambda y: float(np.clip((70 - y) / 45, 0.05, 1.0)))
    if canada:
        _hojarasca(lz, tipos, alto, ancho, por_columna=lambda x: float(np.clip((x - 92) / 40, 0.0, 1.0)))

    # sombra muy suave de las nubes (da volumen al terreno)
    nubes = np.clip((lz.ruido(90, 3, semilla=20) - 0.6) * 3, 0, 1)
    lz.pintar(nubes, "#1d2e18" if nombre not in ("sendero_olvidado", "ruinas_primer_arbol", "paso_escarcha", "maandiko", "canal_tinta") else "#1a2236", 0.12)

    destino = salida or os.path.join(RAIZ, "arte", "mundos", "sigilia" if nombre in SIGILIA else "raiz", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.016)
    print("Suelo pintado:", destino, (lz.w, lz.h))


if __name__ == "__main__":
    pintar(sys.argv[1] if len(sys.argv) > 1 else "kitovu")
