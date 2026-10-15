"""Pintor de cinemáticas de Maisha.

Las ilustraciones de la historia (como las de los legendarios en Pokémon Platino) se pintan con
mucho más detalle que el juego:

- A tamaño de pantalla (600×256, sin ampliar), pintadas al doble y reducidas (bordes limpios).
- Volumen de verdad: cada forma sabe dónde está su borde y se ilumina como si fuera redonda
  (luz principal, luz de rebote y luz de contorno), con texturas de ruido (pelo, corteza, piedra, humo).
- Luz y aire: brillos, rayos de luz, niebla de distancia.
- Al final todo se pasa a la paleta de cinemáticas (la de Raíz más tonos intermedios, cielos,
  noche y fuego) con un tramado suave, para que siga siendo pixel art.
"""
import os
import numpy as np
import cv2
from scipy.spatial import cKDTree

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------- colores
def hex2(c):
    if isinstance(c, str):
        c = c.lstrip("#")
        return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], float) / 255.0
    return np.array(c, float) / (255.0 if max(c) > 1.0 else 1.0)


def leer_paleta_raiz():
    nombres = {}
    with open(os.path.join(RAIZ, "arte", "paletas", "raiz.gpl"), encoding="utf-8") as f:
        for linea in f:
            p = linea.split()
            if len(p) >= 4 and all(x.isdigit() for x in p[:3]):
                nombres[" ".join(p[3:])] = np.array([int(x) for x in p[:3]], float) / 255.0
    return nombres


R = leer_paleta_raiz()


def _a_lab(rgb):
    """sRGB (0-1) → OKLab, para medir distancias de color como las ve el ojo."""
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    l = 0.4122214708 * c[..., 0] + 0.5363325363 * c[..., 1] + 0.0514459929 * c[..., 2]
    m = 0.2119034982 * c[..., 0] + 0.6806995451 * c[..., 1] + 0.1073969566 * c[..., 2]
    s = 0.0883024619 * c[..., 0] + 0.2817188376 * c[..., 1] + 0.6299787005 * c[..., 2]
    l, m, s = np.cbrt(l), np.cbrt(m), np.cbrt(s)
    return np.stack([0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
                     1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
                     0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s], -1)


def _de_lab(lab):
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    c = np.clip(np.stack([r, g, bb], -1), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def mezcla(a, b, t):
    """Mezcla dos colores en OKLab (las mezclas no se ensucian)."""
    a, b = hex2(a) if isinstance(a, str) else np.asarray(a), hex2(b) if isinstance(b, str) else np.asarray(b)
    return _de_lab(_a_lab(a) * (1 - t) + _a_lab(b) * t)


# Rampas extra que la paleta de Raíz no tiene (cielos, noche, fuego, luz) — solo para cinemáticas
EXTRA = {
    "Cielo": ["#16233a", "#24395a", "#335777", "#4a7a93", "#6b9eab", "#97c1bf", "#c4ddd0", "#e8f0dc"],
    "Atardecer": ["#3a2238", "#6a3446", "#9c4b4a", "#c96d4f", "#e49a5c", "#f1c27a", "#f8e1a6", "#fff4d6"],
    "Noche": ["#07060d", "#0d0c19", "#151527", "#1e2038", "#2a2d4c", "#3b4063", "#535a80", "#7680a0"],
    "Fuego": ["#3c1208", "#6e200c", "#a8380f", "#d45a17", "#ef8a26", "#f9b947", "#fde27e", "#fff8d2"],
    "Giza luz": ["#2a0f3d", "#4d1a6b", "#7a2fa0", "#a24fd0", "#c27ce6", "#dcaaf2", "#f1d8fb"],
    "Gris": ["#1b1c1f", "#2b2c30", "#3d3f43", "#525458", "#6a6c6f", "#85878a", "#a3a4a6", "#c5c6c7"],
    # para los recuerdos y las escenas de noche, agua y nieve (sin ellas, los degradados saltaban a gris en manchas)
    "Agua honda": ["#03080c", "#081218", "#0e1c24", "#142834", "#1d3a44", "#2a5058", "#3e6c70", "#5a8a88"],
    "Verde agua": ["#2e5e5c", "#3e8a86", "#62a8a2", "#8cc4bc", "#b4dcd4", "#d8f0ec"],
    "Bruma": ["#353943", "#4a4e5a", "#5e6472", "#767c8a", "#9096a2", "#aab0b8", "#c8ccd2", "#e2e4e8"],
    "Malva": ["#1c1420", "#2a1e2e", "#3e2a3e", "#5a3a50", "#7a4e62"],
    "Nieve": ["#5e6a80", "#7c8aa0", "#a0aec0", "#c4d0dc", "#e2eaf0", "#f6f8fa"],
    # la nieve lila de Sigilia
    "Nieve lila": ["#4e4870", "#655e8a", "#7e76a2", "#9890ba", "#b0a9cd", "#c8c2de", "#dddaec", "#f0eef8"],
}


def paleta_cine():
    """La paleta de cinemáticas: todos los colores de Raíz, sus tonos intermedios y las rampas extra."""
    cols = list(R.values())
    familias = {}
    for nombre, c in R.items():
        base = nombre.rsplit(" ", 1)[0]
        familias.setdefault(base, []).append(c)
    for base, rampa in familias.items():
        if len(rampa) < 2:
            continue
        for a, b in zip(rampa, rampa[1:]):
            cols.append(mezcla(a, b, 0.5))
        # un tono más oscuro (hacia el frío) y uno más claro (hacia el cálido)
        cols.append(mezcla(rampa[0], "#0c0a1a", 0.45))
        cols.append(mezcla(rampa[-1], "#fff6dc", 0.4))
    for rampa in EXTRA.values():
        cols += [hex2(c) for c in rampa]
    p = np.unique(np.round(np.array(cols) * 255).astype(int), axis=0)
    return p / 255.0


PALETA = paleta_cine()
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], float) / 16.0 - 0.47


def cuantizar(img, tramado=0.022, paleta=None):
    """Pasa la imagen a la paleta, con un tramado ordenado suave (pixel art de verdad)."""
    pal = PALETA if paleta is None else paleta
    h, w, _ = img.shape
    b = np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]
    lab = _a_lab(np.clip(img + b[..., None] * tramado, 0, 1))
    arbol = cKDTree(_a_lab(pal))
    _, idx = arbol.query(lab.reshape(-1, 3))
    return pal[idx].reshape(h, w, 3)


# ---------------------------------------------------------------- lienzo
class Lienzo:
    """Pinta en coordenadas de la imagen final (600×256), pero por dentro al doble."""

    def __init__(self, w=600, h=256, s=2, semilla=1):
        self.w, self.h, self.s = w, h, s
        self.W, self.H = w * s, h * s
        self.img = np.zeros((self.H, self.W, 3))
        self.alfa = np.zeros((self.H, self.W))      # lo que está pintado (para sprites con fondo transparente)
        ys, xs = np.mgrid[0:self.H, 0:self.W]
        self.x = (xs + 0.5) / s
        self.y = (ys + 0.5) / s
        self.azar = np.random.default_rng(semilla)

    # ---- máscaras (0..1, con bordes suaves)
    def _vacia(self):
        return np.zeros((self.H, self.W), np.uint8)

    def poligono(self, puntos):
        m = self._vacia()
        p = np.round(np.array(puntos, float) * self.s * 8).astype(np.int32)
        cv2.fillPoly(m, [p], 255, cv2.LINE_AA, 3)
        return m / 255.0

    def elipse(self, cx, cy, rx, ry, angulo=0.0):
        m = self._vacia()
        cv2.ellipse(m, (int(cx * self.s * 8), int(cy * self.s * 8)), (max(1, int(rx * self.s * 8)), max(1, int(ry * self.s * 8))),
                    angulo, 0, 360, 255, -1, cv2.LINE_AA, 3)
        return m / 255.0

    def circulo(self, cx, cy, r):
        return self.elipse(cx, cy, r, r)

    def trazo(self, puntos, grosor_ini, grosor_fin=None, puntas=True):
        """Una línea gruesa que se afina (ramas, raíces, tentáculos, pelos)."""
        grosor_fin = grosor_ini if grosor_fin is None else grosor_fin
        pts = np.array(puntos, float)
        m = self._vacia()
        n = len(pts)
        for i in range(n - 1):
            t = i / max(1, n - 2)
            g = grosor_ini * (1 - t) + grosor_fin * t
            a = tuple(np.round(pts[i] * self.s * 8).astype(int))
            b = tuple(np.round(pts[i + 1] * self.s * 8).astype(int))
            cv2.line(m, a, b, 255, max(1, int(round(g * self.s))), cv2.LINE_AA, 3)
        return m / 255.0

    def curva(self, p0, p1, p2, p3=None, n=40):
        """Puntos de una curva de Bézier (cuadrática o cúbica)."""
        t = np.linspace(0, 1, n)[:, None]
        p0, p1, p2 = np.array(p0, float), np.array(p1, float), np.array(p2, float)
        if p3 is None:
            return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2
        p3 = np.array(p3, float)
        return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3

    # ---- campos
    def ruido(self, escala=40.0, octavas=4, semilla=None, persistencia=0.5):
        """Ruido fractal suave (0..1). escala = tamaño de las manchas grandes, en píxeles finales."""
        rng = np.random.default_rng(abs(int(semilla))) if semilla is not None else self.azar
        total = np.zeros((self.H, self.W))
        amp, suma = 1.0, 0.0
        for o in range(octavas):
            paso = max(1.0, escala * self.s / (2 ** o))
            gw, gh = int(self.W / paso) + 3, int(self.H / paso) + 3
            g = rng.random((gh, gw)).astype(np.float32)
            capa = cv2.resize(g, (int(gw * paso), int(gh * paso)), interpolation=cv2.INTER_CUBIC)[:self.H, :self.W]
            total += amp * capa
            suma += amp
            amp *= persistencia
        total /= suma
        return np.clip((total - total.mean()) / (total.std() * 3.2 + 1e-6) + 0.5, 0, 1)

    def distancia(self, mascara, umbral=0.5):
        """Distancia (en píxeles finales) desde cada punto de dentro hasta el borde de la forma."""
        m = (mascara > umbral).astype(np.uint8)
        return cv2.distanceTransform(m, cv2.DIST_L2, 5) / self.s

    def desenfocar(self, campo, radio):
        k = max(1, int(radio * self.s)) | 1
        return cv2.GaussianBlur(campo.astype(np.float32), (0, 0), radio * self.s)

    # ---- pintar
    def pintar(self, mascara, color, alfa=1.0):
        """Pinta un color (o un campo de colores H×W×3) donde dice la máscara."""
        c = color if (isinstance(color, np.ndarray) and color.ndim == 3) else hex2(color) if isinstance(color, str) else np.asarray(color, float)
        a = np.clip(mascara * alfa, 0, 1)[..., None]
        self.img = self.img * (1 - a) + c * a
        self.alfa = self.alfa * (1 - a[..., 0]) + a[..., 0]

    def sumar_luz(self, campo, color, fuerza=1.0):
        """Luz que se suma (brillos, fuego, magia)."""
        c = hex2(color) if isinstance(color, str) else np.asarray(color, float)
        self.img = 1 - (1 - self.img) * (1 - np.clip(campo * fuerza, 0, 1)[..., None] * c)

    def brillo(self, mascara, color, radio, fuerza=1.0):
        self.sumar_luz(self.desenfocar(mascara, radio), color, fuerza)

    def gradiente(self, colores, eje="y", desde=0.0, hasta=None, campo=None):
        """Un campo de color que pasa por varios colores (de arriba abajo, por defecto)."""
        if campo is None:
            hasta = (self.h if eje == "y" else self.w) if hasta is None else hasta
            v = (self.y if eje == "y" else self.x)
            campo = np.clip((v - desde) / (hasta - desde), 0, 1)
        return rampa(colores, campo)

    def volumen(self, mascara, radio, luz=(-0.6, -0.7, 0.55), suavizar=1.0):
        """Ilumina una forma como si fuera redonda. Devuelve 0..1 (0 = sombra, 1 = luz de lleno)
        y el contorno (cerca del borde) para la luz de recorte."""
        d = self.distancia(mascara)
        t = np.clip(d / radio, 0, 1)
        altura = np.sqrt(1 - (1 - t) ** 2)
        if suavizar:
            altura = self.desenfocar(altura, suavizar)
        gy, gx = np.gradient(altura * radio * self.s)
        n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
        n /= np.linalg.norm(n, axis=-1, keepdims=True)
        L = np.array(luz, float)
        L /= np.linalg.norm(L)
        dif = np.clip((n * L).sum(-1), 0, 1)
        borde = 1 - t
        return dif, borde

    def sombrear(self, mascara, rampa_colores, radio, luz=(-0.6, -0.7, 0.55), textura=None, fuerza_tex=0.18,
                 rebote=None, recorte=None, recorte_dir=(1, 0), ambiente=0.18):
        """Pinta una forma con volumen: rampa de oscuro a claro según la luz, textura, luz de rebote
        (desde abajo) y luz de recorte (un filo de color por un lado)."""
        dif, borde = self.volumen(mascara, radio, luz)
        v = ambiente + (1 - ambiente) * dif
        if textura is not None:
            v = v + (textura - 0.5) * fuerza_tex
        col = rampa(rampa_colores, np.clip(v, 0, 1))
        if rebote is not None:
            c, f = rebote
            abajo = np.clip(borde * 1.3, 0, 1) * np.clip(1 - dif * 1.5, 0, 1)
            col = col * (1 - (abajo * f)[..., None]) + hex2(c) * (abajo * f)[..., None]
        if recorte is not None:
            c, f = recorte
            dx, dy = recorte_dir
            dist = self.distancia(mascara)
            gy, gx = np.gradient(self.desenfocar(dist, 1.0))
            nn = np.sqrt(gx ** 2 + gy ** 2) + 1e-6
            lado = np.clip((-(gx * dx + gy * dy) / nn), 0, 1)
            filo = np.clip(1 - dist / 2.2, 0, 1) * lado
            col = col * (1 - (filo * f)[..., None]) + hex2(c) * (filo * f)[..., None]
        self.pintar(mascara, col)
        return dif

    def niebla(self, mascara_profundidad, color, fuerza):
        self.pintar(np.clip(mascara_profundidad, 0, 1), color, fuerza)

    def rayos(self, fuente, origen, largo=0.94, pasos=48):
        """Rayos de luz que salen de 'fuente' (máscara de brillo) desde el punto 'origen'."""
        ox, oy = origen[0] * self.s, origen[1] * self.s
        acum = np.zeros_like(fuente, dtype=np.float32)
        f = fuente.astype(np.float32)
        for i in range(pasos):
            k = largo ** i
            M = np.float32([[k, 0, ox * (1 - k)], [0, k, oy * (1 - k)]])
            acum += cv2.warpAffine(f, M, (self.W, self.H), flags=cv2.INTER_LINEAR) * (1 - i / pasos)
        return acum / pasos

    def final(self, tramado=0.022):
        peq = cv2.resize(self.img.astype(np.float32), (self.w, self.h), interpolation=cv2.INTER_AREA)
        return cuantizar(peq.astype(float), tramado)

    def sprite(self, tramado=0.018, umbral=0.5, contorno=0.0):
        """La imagen final con fondo transparente (bordes limpios: cada píxel está o no está).
        contorno > 0: oscurece los píxeles del borde (contorno selectivo: un tono más oscuro del mismo color)."""
        a = cv2.resize(self.alfa.astype(np.float32), (self.w, self.h), interpolation=cv2.INTER_AREA)
        col = cv2.resize((self.img * self.alfa[..., None]).astype(np.float32), (self.w, self.h), interpolation=cv2.INTER_AREA)
        col = col / np.maximum(a[..., None], 1e-4)
        if contorno:
            dentro = (a > umbral).astype(np.uint8)
            borde = dentro - cv2.erode(dentro, np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], np.uint8))
            oscuro = _de_lab(_a_lab(np.clip(col, 0, 1)) * np.array([1 - contorno, 1, 1]) + np.array([0, 0.004, 0.008]))
            col = np.where(borde[..., None] > 0, oscuro, col)
        rgb = cuantizar(np.clip(col, 0, 1).astype(float), tramado)
        out = np.zeros((self.h, self.w, 4), np.uint8)
        out[..., :3] = (np.clip(rgb, 0, 1) * 255).round().astype(np.uint8)
        out[..., 3] = np.where(a > umbral, 255, 0)
        return out

    def guardar_sprite(self, ruta, tramado=0.018, umbral=0.5, contorno=0.0):
        from PIL import Image
        Image.fromarray(self.sprite(tramado, umbral, contorno), "RGBA").save(ruta)

    def guardar(self, ruta, tramado=0.022):
        out = (np.clip(self.final(tramado), 0, 1) * 255).round().astype(np.uint8)
        guardar_png_ligero(ruta, out)
        return out


def guardar_png_ligero(ruta, rgb):
    """Guarda un PNG con paleta si tiene 256 colores o menos (sin perder nada: ocupa 4 o 5 veces menos)."""
    from PIL import Image
    im = Image.fromarray(rgb, "RGB")
    colores = im.getcolors(256)
    if colores is None:
        im.save(ruta, optimize=True)
        return
    paleta = [c for _, c in colores]
    indice = {c: i for i, c in enumerate(paleta)}
    plano = rgb.reshape(-1, 3)
    claves = plano[:, 0].astype(np.int32) * 65536 + plano[:, 1].astype(np.int32) * 256 + plano[:, 2]
    tabla = {c[0] * 65536 + c[1] * 256 + c[2]: i for c, i in indice.items()}
    idx = np.vectorize(tabla.__getitem__)(claves).astype(np.uint8).reshape(rgb.shape[:2])
    p = Image.fromarray(idx, "P")
    plana = [v for c in paleta for v in c]
    p.putpalette(plana + [0] * (768 - len(plana)))
    p.save(ruta, optimize=True)


def rampa(colores, v):
    """Lleva un campo 0..1 a una rampa de colores (interpolando)."""
    cs = np.array([hex2(c) if isinstance(c, str) else np.asarray(c, float) for c in colores])
    v = np.clip(v, 0, 1) * (len(cs) - 1)
    i = np.clip(np.floor(v).astype(int), 0, len(cs) - 2)
    t = (v - i)[..., None]
    return cs[i] * (1 - t) + cs[i + 1] * t


def gris(img, fuerza, tinte=(0.48, 0.5, 0.56)):
    """Le quita el color a la imagen (lo que hace Giza), con un tinte frío."""
    lum = (img * [0.3, 0.55, 0.15]).sum(-1, keepdims=True)
    g = lum * 0.85 + np.array(tinte) * lum * 0.3
    f = np.clip(fuerza, 0, 1)[..., None]
    return img * (1 - f) + g * f


# ---------------------------------------------------------------- humo y nubes con volumen
def bolas(lz, lista, colores, luz=(-0.7, -0.6, 0.5), filo=None, filo_dir=(-1, -0.6), bajo=None, ruido_borde=0.35,
          textura=None, fuerza_tex=0.25, ambiente=0.12, mascara_total=None, plano=1.2, suave=0.7):
    """Pinta bolas de humo (o de nube, o de hojas) una detrás de otra, cada una con su volumen.
    lista = [(x, y, radio), ...] en el orden en que se pintan (las de atrás primero).
    filo = (color, fuerza): luz de contorno por el lado filo_dir.  bajo = (color, fuerza): luz que
    se cuela por debajo de cada bola (el brillo de dentro de Giza)."""
    s = lz.s
    L = np.array(luz, float)
    L /= np.linalg.norm(L)
    fd = np.array(filo_dir, float)
    fd /= np.linalg.norm(fd)
    tex_global = textura if textura is not None else lz.ruido(3, 3)
    borde_ruido = lz.ruido(2.2, 2)
    total = np.zeros((lz.H, lz.W)) if mascara_total is None else mascara_total
    for (x, y, r) in lista:
        m = int(r * 1.5 + 4)
        x0, x1 = int(max(0, (x - m) * s)), int(min(lz.W, (x + m) * s))
        y0, y1 = int(max(0, (y - m) * s)), int(min(lz.H, (y + m) * s))
        if x1 <= x0 or y1 <= y0:
            continue
        xs, ys = lz.x[y0:y1, x0:x1], lz.y[y0:y1, x0:x1]
        d = np.hypot(xs - x, ys - y) / r
        d = d + (borde_ruido[y0:y1, x0:x1] - 0.5) * ruido_borde
        mask = np.clip((1 - d) * r * s * suave + 0.5, 0, 1)
        if mask.max() <= 0:
            continue
        # normal de una esfera (aplastada por el ruido del borde)
        t = np.clip(1 - d, 0, 1)
        nz = np.sqrt(np.clip(1 - (1 - t) ** 2, 0, 1))
        nx = (xs - x) / r
        ny = (ys - y) / r
        n = np.stack([nx, ny, nz * plano], -1)
        n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-6
        dif = np.clip((n * L).sum(-1), 0, 1)
        v = ambiente + (1 - ambiente) * dif + (tex_global[y0:y1, x0:x1] - 0.5) * fuerza_tex
        col = rampa(colores, np.clip(v, 0, 1))
        if bajo is not None:
            c, f = bajo
            k = np.clip((ny * 0.8 + nx * 0.3) * (1 - nz) * 2.2, 0, 1) * f
            col = col * (1 - k[..., None]) + hex2(c) * k[..., None]
        if filo is not None:
            c, f = filo
            k = np.clip((nx * fd[0] + ny * fd[1]), 0, 1) * np.clip(1 - nz * 1.6, 0, 1) * f
            col = col * (1 - k[..., None]) + hex2(c) * k[..., None]
        a = mask[..., None]
        lz.img[y0:y1, x0:x1] = lz.img[y0:y1, x0:x1] * (1 - a) + col * a
        lz.alfa[y0:y1, x0:x1] = lz.alfa[y0:y1, x0:x1] * (1 - a[..., 0]) + a[..., 0]
        total[y0:y1, x0:x1] = np.maximum(total[y0:y1, x0:x1], mask)
    return total


def humo(lz, forma, colores, luz=(-0.7, -0.6, 0.45), escala=26.0, semilla=5, umbral=0.5, relieve=1.0,
         torcer=10.0, detalle=0.35):
    """Humo (o nubes) con relieve: la forma (0..1) se rompe con ruido torcido y se ilumina como
    si fuera un terreno de bultos. Devuelve la máscara y la luz (0..1)."""
    rng_s = semilla
    # ruido torcido (como remolinos): se desplaza el ruido con otro ruido
    wx = (lz.ruido(escala * 1.5, 3, semilla=rng_s + 1) - 0.5) * torcer * lz.s
    wy = (lz.ruido(escala * 1.5, 3, semilla=rng_s + 2) - 0.5) * torcer * lz.s
    base = lz.ruido(escala, 5, semilla=rng_s).astype(np.float32)
    mapx = (np.arange(lz.W)[None, :] + wx).astype(np.float32)
    mapy = (np.arange(lz.H)[:, None] + wy).astype(np.float32)
    n = cv2.remap(base, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # bultos: el ruido "hinchado" (abs) da formas redondas de nube
    bultos = 1 - np.abs(n - 0.5) * 2
    dens = forma * 1.0 + (n - 0.5) * 0.7 + (bultos - 0.5) * detalle
    mascara = np.clip((dens - umbral) * 14, 0, 1)
    mascara = lz.desenfocar(mascara, 0.6)
    alto = lz.desenfocar(np.clip(dens - umbral, 0, 1), 2.5) * 4 + n * 1.2 + bultos * 0.8
    alto = lz.desenfocar(alto, 1.2) * relieve
    gy, gx = np.gradient(alto * 40)
    nrm = np.stack([-gx, -gy, np.ones_like(gx)], -1)
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    L = np.array(luz, float)
    L /= np.linalg.norm(L)
    dif = np.clip((nrm * L).sum(-1), 0, 1)
    return mascara, dif, n


def relieve_bolas(lz, lista, alto=None):
    """Campo de altura hecho con medias esferas (como un cúmulo de nubes). lista = [(x, y, r), ...]"""
    alto = np.zeros((lz.H, lz.W)) if alto is None else alto
    s = lz.s
    for (x, y, r) in lista:
        x0, x1 = int(max(0, (x - r - 2) * s)), int(min(lz.W, (x + r + 2) * s))
        y0, y1 = int(max(0, (y - r - 2) * s)), int(min(lz.H, (y + r + 2) * s))
        if x1 <= x0 or y1 <= y0:
            continue
        d2 = ((lz.x[y0:y1, x0:x1] - x) ** 2 + (lz.y[y0:y1, x0:x1] - y) ** 2) / (r * r)
        h = r * np.sqrt(np.clip(1 - d2, 0, 1)) + (d2 < 1) * 0.001
        alto[y0:y1, x0:x1] = np.maximum(alto[y0:y1, x0:x1], h)
    return alto


def iluminar_relieve(lz, alto, luz=(-0.7, -0.6, 0.45), suavizar=0.8):
    a = lz.desenfocar(alto, suavizar) if suavizar else alto
    gy, gx = np.gradient(a * lz.s)
    n = np.stack([-gx / lz.s * lz.s, -gy, np.ones_like(gx)], -1)
    n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    L = np.array(luz, float)
    L /= np.linalg.norm(L)
    return np.clip((n * L).sum(-1), 0, 1), n


def ruido_torcido(lz, escala, octavas=5, semilla=0, torcer=12.0, escala_torcer=None):
    """Ruido fractal desplazado por otro ruido: remolinos de humo."""
    et = escala * 1.3 if escala_torcer is None else escala_torcer
    wx = (lz.ruido(et, 3, semilla=semilla + 101) - 0.5) * torcer * lz.s
    wy = (lz.ruido(et, 3, semilla=semilla + 102) - 0.5) * torcer * lz.s
    base = lz.ruido(escala, octavas, semilla=semilla).astype(np.float32)
    mapx = (np.arange(lz.W)[None, :] + wx).astype(np.float32)
    mapy = (np.arange(lz.H)[:, None] + wy).astype(np.float32)
    return cv2.remap(base, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def desplazar(lz, campo, dx, dy):
    M = np.float32([[1, 0, dx * lz.s], [0, 1, dy * lz.s]])
    return cv2.warpAffine(campo.astype(np.float32), M, (lz.W, lz.H), borderMode=cv2.BORDER_REPLICATE)


def humo_volumen(lz, densidad, luz=(-1.0, -0.6), paso=2.5, umbral=(0.35, 0.62)):
    """Humo con volumen de verdad: donde la densidad crece en contra de la luz, el humo se ilumina
    (como el sol rozando el borde de una nube). Devuelve alfa (0..1) y luz (0..1)."""
    lx, ly = luz
    nrm = np.hypot(lx, ly)
    lx, ly = lx / nrm, ly / nrm
    luz_v = np.zeros_like(densidad)
    for k, peso in [(1, 0.5), (2, 0.3), (4, 0.2)]:
        atras = desplazar(lz, densidad, lx * paso * k, ly * paso * k)  # la densidad hacia la luz
        luz_v += peso * np.clip((densidad - atras) * 3.0 / k ** 0.5 + 0.5, 0, 1)
    a, b = umbral
    alfa = np.clip((densidad - a) / (b - a), 0, 1)
    alfa = alfa * alfa * (3 - 2 * alfa)
    return alfa, np.clip(luz_v, 0, 1)


def iluminar(lz, ambiente, luces, propia=None):
    """Luz de escena: multiplica todo por la luz ambiente más las luces puntuales (color y caída suave).
    luces = [(x, y, radio, color, fuerza), ...]. Lo que tiene luz propia (máscara 'propia') no se oscurece."""
    total = np.ones((lz.H, lz.W, 3)) * hex2(ambiente)
    for (x, y, radio, color, fuerza) in luces:
        d = np.hypot(lz.x - x, lz.y - y) / radio
        total += (np.clip(1 - d, 0, 1) ** 2)[..., None] * hex2(color) * fuerza
    nuevo = np.clip(lz.img * total, 0, 1)
    if propia is not None:
        p = np.clip(propia, 0, 1)[..., None]
        nuevo = nuevo * (1 - p) + lz.img * p
    lz.img = nuevo
