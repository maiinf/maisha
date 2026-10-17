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
SIGILIA = {"paso_escarcha", "maandiko"}


def _nevar(lz, tipos, fina, media, pared, conservar=(), lila=False):
    """El SENDERO OLVIDADO: todo nevado. Donde había hierba, nieve con ondas del viento y sombras azuladas; el camino,
    nieve pisada (más gris, con huellas); encima de las peñas, nieve; en sus paredes, escarcha."""
    import cv2 as _cv
    NIEVE_S = NIEVE_LILA if lila else NIEVE_N
    PISADA = PISADA_LILA if lila else PISADA_N
    S = lz.s
    ri = mascara(lz, tipos, ("risco",), 4.0, 0.5, semilla=50)
    pared = pared if pared is not None else np.zeros_like(ri)
    suelo = np.clip(1 - ri, 0, 1)
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


def pintar(nombre, salida=None):
    if nombre in ("gruta_raices", "cueva_setas"):
        return pintar_gruta(nombre, salida, setas=nombre == "cueva_setas")
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
    agua_r = AGUA_CIENAGA if cienaga else AGUA_R
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
    olvidado = nombre in ("sendero_olvidado", "paso_escarcha", "maandiko")
    ruinas = nombre in ("ruinas_primer_arbol", "maandiko")
    pared = _riscos(lz, tipos, fina, media, cara=2.0 if (canada or paso or olvidado or ruinas) else 1.0)
    if olvidado or ruinas:
        _nevar(lz, tipos, fina, media, pared, conservar=("losas",) if ruinas else (), lila=nombre in SIGILIA)
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
    lz.pintar(nubes, "#1d2e18" if nombre not in ("sendero_olvidado", "ruinas_primer_arbol", "paso_escarcha", "maandiko") else "#1a2236", 0.12)

    destino = salida or os.path.join(RAIZ, "arte", "mundos", "sigilia" if nombre in SIGILIA else "raiz", "suelos", nombre + "_suelo.png")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    lz.guardar(destino, tramado=0.016)
    print("Suelo pintado:", destino, (lz.w, lz.h))


if __name__ == "__main__":
    pintar(sys.argv[1] if len(sys.argv) > 1 else "kitovu")
