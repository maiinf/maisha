# -*- coding: utf-8 -*-
"""
Maisha en 3D sobre malla base profesional (contrato del Kitovu): el Guardián de la Memoria.

Referencias: documentacion/referencias_visuales_3d/CONTRATO_KITOVU.md y personajes/ref_maisha_mistico.md
  - malla base oficial GEO-body_male_stylized de Blender Studio (CC0), llevada a 1,70 m y suavizada hacia lo
    andrógino (sin rasgos de género marcados);
  - sin cuernos ni astas, pelo orgánico suave y oscuro;
  - Tatuajes de la Memoria en brazos, hombros, cuello, pecho y espalda: oscuros al empezar y dorados al
    recuperar los Ecos (textura de emisión: el juego sube o baja su brillo);
  - túnica de lino arena asimétrica, capa de viaje color musgo sobre el hombro izquierdo, cinturón con bolsas
    de semillas, pantalón y botas; Corazón de Asili en el esternón; Cetro de Raíz con semilla esmeralda.

    blender -b --factory-startup -P herramientas/blender/modelar_maisha.py [-- --vistas <carpeta>]

Sale modelos/personajes/maisha.glb (esqueleto de 27 huesos, Cetro anclado a hand_R, 6 animaciones: reposo,
caminar_atento, correr, golpe_cetro, idle_mirar_tatuajes, eco_despertar) y la máscara de los tatuajes
modelos/personajes/maisha_tatuajes_mascara.png. Lo usa scripts/personajes/maisha_3d.gd.
"""

import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aparejo as ap  # noqa: E402
from aparejo import X, Y, Z  # noqa: E402
from modelar_mzee_shamba import Cuerpo, Piezas, _catmull, gauss, suave  # noqa: E402

CARPETA = os.path.join(ap.RAIZ, "modelos", "personajes")
SALIDA = os.path.join(CARPETA, "maisha.glb")
MASCARA = os.path.join(CARPETA, "maisha_tatuajes_mascara.png")
ESCALA = 1.70 / 1.794

PALETA = {
    "piel_humanizada": ("#e8ded0", 0.60, 0.0, 0.0),
    "cabello_viajero": ("#4e443b", 0.70, 0.0, 0.0),      # contrato: pelo suave y oscuro
    "tunica_lino_arena": ("#eae3d2", 0.85, 0.0, 0.0),
    "capa_viaje_musgo": ("#46543b", 0.85, 0.0, 0.0),
    "cuero_cinturon": ("#4a3828", 0.70, 0.1, 0.0),
    "tela_pantalon": ("#7d735f", 0.90, 0.0, 0.0),
    "cuero_botas": ("#5a4534", 0.75, 0.05, 0.0),
    "corazon_asili_oro": ("#f5c238", 0.20, 0.1, 1.6),
    "engaste_corazon": ("#b8a58a", 0.55, 0.0, 0.0),
    "cetro_madera": ("#4e3b2b", 0.80, 0.0, 0.0),
    "semilla_esmeralda": ("#2ecc8a", 0.15, 0.0, 1.8),
    "iris_ambar": ("#6b4a24", 0.20, 0.0, 0.3),
}
TINTA = "#3d3835"      # tatuajes dormidos
ORO = "#ffd766"        # tatuajes despiertos


# ---------------------------------------------------------------------------
# Cuerpo: malla base a 1,70 m, algo más andrógina
# ---------------------------------------------------------------------------

def dar_forma(cuerpo, forma):
    hombro_medio = forma.torso_medio(1.30) or 0.20
    for v in cuerpo.data.vertices:
        p = forma.base[v.index]
        zona = forma.zona[v.index]
        kx = 1.0 - 0.07 * suave(1.12, 1.38, p.z) + 0.05 * gauss(p.z - 0.93, 0.08) - 0.03 * gauss(p.z - 1.06, 0.06)
        ky = 1.0
        if 1.44 < p.z < 1.56:      # cuello más fino
            kx *= 0.92
            ky = 0.94
        if zona in ("brazo", "mano"):
            x = p.x - math.copysign(hombro_medio * 0.07, p.x) * (1 - suave(1.15, 1.26, p.z))
            x = x if p.z < 1.15 else p.x * kx
        else:
            x = p.x * kx
        if zona == "cabeza":       # mandíbula un poco más suave
            x = p.x * (1.0 - 0.06 * suave(1.66, 1.56, p.z))
        v.co = Vector((x, p.y * ky, p.z)) * ESCALA
    cuerpo.data.update()
    ap.normales_fuera(cuerpo)


def punto(p, zona=None):
    """Transforma un punto de la malla base (sin las correcciones finas: basta para huesos y prendas)."""
    return Vector(p) * ESCALA


# ---------------------------------------------------------------------------
# Tatuajes de la Memoria: se dibujan sobre el cuerpo en 3D y se pasan a su textura
# ---------------------------------------------------------------------------

class Lienzo:
    """Imagen en metros: dibuja trazos y círculos (para luego leerlos desde la superficie)."""

    def __init__(self, ancho_m, alto_m, px_m=1800):
        self.w, self.h = ancho_m, alto_m
        self.k = px_m
        self.img = np.zeros((int(alto_m * px_m) + 1, int(ancho_m * px_m) + 1), np.float32)

    def trazo(self, pts, grueso):
        aa = 0.8 / self.k
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            x0 = max(int((min(ax, bx) - grueso) * self.k) - 2, 0)
            x1 = min(int((max(ax, bx) + grueso) * self.k) + 3, self.img.shape[1])
            y0 = max(int((min(ay, by) - grueso) * self.k) - 2, 0)
            y1 = min(int((max(ay, by) + grueso) * self.k) + 3, self.img.shape[0])
            if x1 <= x0 or y1 <= y0:
                continue
            gx, gy = np.meshgrid((np.arange(x0, x1) + 0.5) / self.k, (np.arange(y0, y1) + 0.5) / self.k)
            dx, dy = bx - ax, by - ay
            l2 = dx * dx + dy * dy or 1e-12
            t = np.clip(((gx - ax) * dx + (gy - ay) * dy) / l2, 0, 1)
            d = np.hypot(gx - (ax + t * dx), gy - (ay + t * dy))
            self.img[y0:y1, x0:x1] = np.maximum(self.img[y0:y1, x0:x1], np.clip((grueso / 2 + aa - d) / (2 * aa), 0, 1))

    def circulo(self, c, r, grueso, a0=0.0, a1=2 * math.pi, pasos=48):
        self.trazo([(c[0] + r * math.cos(a0 + (a1 - a0) * k / pasos), c[1] + r * math.sin(a0 + (a1 - a0) * k / pasos))
                    for k in range(pasos + 1)], grueso)

    def punto(self, c, r):
        self.circulo(c, r * 0.5, r, pasos=12)

    def leer(self, x, y):
        i = np.clip((y * self.k).astype(int), 0, self.img.shape[0] - 1)
        j = np.clip((x * self.k).astype(int), 0, self.img.shape[1] - 1)
        dentro = (x >= 0) & (x <= self.w) & (y >= 0) & (y <= self.h)
        return np.where(dentro, self.img[i, j], 0.0)


G = 0.0026    # grosor de las líneas (2,6 mm)


def lienzo_brazo(largo, derecho):
    """Brazo desenrollado: x = alrededor (0,22 m, empezando por delante), y = del hombro a la muñeca."""
    W = 0.22
    lz = Lienzo(W, largo)
    for k, r in enumerate((0.030, 0.045, 0.060)):                      # arcos del hombro
        lz.circulo((W * 0.5, 0.0), r, G * (1.2 if k == 0 else 1.0), math.radians(10), math.radians(170))
    for v in (largo * 0.42, largo * 0.44, largo * 0.965, largo * 0.985):  # brazaletes: sobre el codo y la muñeca
        lz.trazo([(0.004, v), (W - 0.004, v)], G * 0.9)
    for k in range(5):                                                  # runas en triángulo
        x = 0.03 + k * 0.04
        y = largo * 0.27
        lz.trazo([(x, y), (x + 0.012, y + 0.025), (x + 0.024, y), (x, y)], G * 0.9)
        lz.trazo([(x + 0.012, y + 0.035), (x + 0.012, y + 0.055)], G * 0.9)
    eje = W * (0.25 if derecho else 0.75)                                # constelación del antebrazo
    y0 = largo * 0.52
    lz.trazo([(eje, y0), (eje, largo * 0.95)], G)
    for k in range(6):
        y = y0 + 0.02 + k * (largo * 0.40) / 6
        lz.circulo((eje, y), 0.0055, G * 0.9)
        lz.punto((eje, y), 0.0028)
        off = 0.035 * (1 if k % 2 else -1)
        lz.trazo([(eje + math.copysign(0.0055, off), y), (eje + off, y + 0.018)], G * 0.8)
        lz.punto((eje + off, y + 0.018), 0.0032)
    cx = W * (0.62 if derecho else 0.38)                                 # espiral y círculo de agua
    pts = []
    for k in range(80):
        a = k / 79 * 2.6 * 2 * math.pi
        r = 0.002 + 0.0040 * a / (2 * math.pi)
        pts.append((cx + r * math.cos(a), largo * 0.62 + r * math.sin(a)))
    lz.trazo(pts, G * 0.85)
    for r in (0.014, 0.008):
        lz.circulo((cx, largo * 0.80), r, G)
    lz.punto((cx, largo * 0.80), 0.003)
    for k in range(6):                                                   # cheurones
        y = largo * 0.53 + k * 0.038
        x = W * (0.88 if derecho else 0.12)
        lz.trazo([(x - 0.008, y), (x, y + 0.010), (x + 0.008, y)], G * 0.85)
    return lz


def lienzo_pecho(alto_corazon):
    """Pecho visto de frente (x de -0,25 a 0,25 m, z absoluta): venas del corazón y líneas de las clavículas."""
    lz = Lienzo(0.50, 0.60)
    def P(x, z):
        return (x + 0.25, z - (alto_corazon - 0.30))
    for s in (-1, 1):
        lz.trazo([P(s * 0.025, alto_corazon + 0.01), P(s * 0.06, alto_corazon + 0.05), P(s * 0.11, alto_corazon + 0.08),
                  P(s * 0.17, alto_corazon + 0.09)], G * 0.9)
        lz.trazo([P(s * 0.03, alto_corazon - 0.02), P(s * 0.07, alto_corazon - 0.06), P(s * 0.09, alto_corazon - 0.11)],
                 G * 0.8)
        for k in range(3):
            z = alto_corazon + 0.11 - 0.017 * k
            lz.trazo([P(s * 0.05, z), P(s * 0.11, z - 0.008), P(s * 0.17, z - 0.010)], G)
    return lz


def lienzo_espalda(alto):
    lz = Lienzo(0.50, 0.60)
    c = (0.25, 0.30)
    for r in (0.040, 0.055):
        lz.circulo(c, r, G)
    for k in range(9):
        a = 2 * math.pi * k / 9
        lz.punto((c[0] + 0.068 * math.cos(a), c[1] + 0.068 * math.sin(a)), 0.004)
    return lz


BALDOSAS = 5          # la UV de la malla base va en 5 baldosas (UDIM 1001-1005): cabeza, torso, brazo, mano, pies
TAM_BALDOSA = 1024


def juntar_baldosas(cuerpo):
    """Pone las 5 baldosas una al lado de otra dentro de 0..1 (u/5): una sola textura de 5120 x 1024."""
    for d in cuerpo.data.uv_layers.active.data:
        d.uv = (d.uv[0] / BALDOSAS, d.uv[1])


def hornear_tatuajes(cuerpo, forma, brazos, z_cuello, z_corazon):
    """Recorre los triángulos del cuerpo en su UV: para cada píxel calcula el punto 3D y pregunta al dibujo de
    su zona (brazo desenrollado, pecho, espalda, banda del cuello). Devuelve la máscara (alto x ancho)."""
    me = cuerpo.data
    me.calc_loop_triangles()
    uv = me.uv_layers.active.data
    ancho, alto = TAM_BALDOSA * BALDOSAS, TAM_BALDOSA
    mascara = np.zeros((alto, ancho), np.float32)
    lienzos = {lado: (lienzo_brazo(datos["largo"], lado == "R"), datos) for lado, datos in brazos.items()}
    pecho, espalda = lienzo_pecho(z_corazon), lienzo_espalda(z_corazon)

    def patron(P, zona_tri, lado):
        if zona_tri in ("brazo", "hombro") and lado in lienzos:
            lz, d = lienzos[lado]
            S, E, W = (np.array(d[k][:]) for k in ("hombro", "codo", "muneca"))
            # a lo largo: proyección sobre hombro→codo y codo→muñeca
            ab, bc = E - S, W - E
            lab, lbc = np.linalg.norm(ab), np.linalg.norm(bc)
            t1 = np.clip(((P - S) @ ab) / (lab * lab), 0, 1)
            t2 = np.clip(((P - E) @ bc) / (lbc * lbc), 0, 1)
            en_ante = t1 >= 0.999
            largo = np.where(en_ante, lab + t2 * lbc, t1 * lab)
            eje = np.where(en_ante[:, None], bc / lbc, ab / lab)
            centro = np.where(en_ante[:, None], E + bc * t2[:, None], S + ab * t1[:, None])
            r = P - centro
            r -= eje * np.sum(r * eje, axis=1)[:, None]
            delante = np.array([0.0, -1.0, 0.0])
            ref = delante - eje * (eje @ delante)[:, None]
            ref /= np.linalg.norm(ref, axis=1)[:, None]
            otro = np.cross(eje, ref)
            ang = np.arctan2(np.sum(r * otro, axis=1), np.sum(r * ref, axis=1))
            alrededor = (ang / (2 * math.pi) % 1.0) * lz.w
            return lz.leer(alrededor, largo + d["inicio"])
        # torso: cuello, pecho, espalda
        val = np.zeros(len(P), np.float32)
        z = P[:, 2]
        banda = (np.abs(z - z_cuello) < 0.0016) | (np.abs(z - (z_cuello + 0.013)) < 0.0016)
        ang = np.arctan2(P[:, 0], -P[:, 1])
        puntos = (np.abs(((ang / (2 * math.pi)) * 34) % 1.0 - 0.5) < 0.09) & (np.abs(z - (z_cuello + 0.0065)) < 0.0028)
        val = np.where(banda | puntos, 1.0, val)
        val = np.maximum(val, np.where(P[:, 1] < 0, pecho.leer(P[:, 0] + 0.25, z - (z_corazon - 0.30)), 0.0))
        val = np.maximum(val, np.where(P[:, 1] > 0.02, espalda.leer(P[:, 0] + 0.25, z - (z_corazon - 0.30) + 0.03),
                                       0.0))
        return val

    for tri in me.loop_triangles:
        zonas = [forma.zona[i] for i in tri.vertices]
        if "cabeza" in zonas or "pierna" in zonas or "pie" in zonas or "mano" in zonas:
            continue
        P3 = np.array([me.vertices[i].co[:] for i in tri.vertices])
        if "brazo" not in zonas and np.all(P3[:, 2] < z_corazon - 0.24):   # bajo el pecho solo hay brazos
            continue
        U = np.array([uv[l].uv[:] for l in tri.loops]) * np.array([ancho - 1, alto - 1])
        x0, y0 = np.floor(U.min(axis=0)).astype(int)
        x1, y1 = np.ceil(U.max(axis=0)).astype(int) + 1
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, ancho), min(y1, alto)
        if x1 <= x0 or y1 <= y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        q = np.stack([gx.ravel(), gy.ravel()], axis=1)
        a, b, c = U
        m = np.array([[b[0] - a[0], c[0] - a[0]], [b[1] - a[1], c[1] - a[1]]])
        if abs(np.linalg.det(m)) < 1e-9:
            continue
        l12 = np.linalg.solve(m, (q - a).T).T
        l0 = 1 - l12.sum(axis=1)
        dentro = (l0 >= -0.02) & (l12[:, 0] >= -0.02) & (l12[:, 1] >= -0.02)
        if not dentro.any():
            continue
        bar = np.stack([l0, l12[:, 0], l12[:, 1]], axis=1)[dentro]
        P = bar @ P3
        zona_tri = "brazo" if "brazo" in zonas else "torso"
        x_medio = P3[:, 0].mean()
        lado = "R" if x_medio > 0 else "L"
        if zona_tri == "torso" and abs(x_medio) > 0.13 and P3[:, 2].mean() > z_corazon:
            zona_tri = "hombro"
        val = patron(P, zona_tri, lado)
        qq = q[dentro].astype(int)
        mascara[qq[:, 1], qq[:, 0]] = np.maximum(mascara[qq[:, 1], qq[:, 0]], val)
    return mascara


def imagenes_piel(mascara):
    piel = np.array(ap.rgb(PALETA["piel_humanizada"][0]), np.float32)
    tinta = np.array(ap.rgb(TINTA), np.float32)
    oro = np.array(ap.rgb(ORO), np.float32)
    k = (mascara * 0.88)[..., None]
    base = piel * (1 - k) + tinta * k
    emis = oro * mascara[..., None]
    alto, ancho = mascara.shape

    def imagen(nombre, rgb_):
        img = bpy.data.images.new(nombre, ancho, alto, alpha=False)
        img.pixels.foreach_set(np.concatenate([rgb_, np.ones((alto, ancho, 1), np.float32)], axis=2).ravel())
        img.pack()
        return img
    os.makedirs(CARPETA, exist_ok=True)
    guardar = bpy.data.images.new("mascara", ancho, alto, alpha=False)
    guardar.pixels.foreach_set(np.stack([mascara, mascara, mascara, np.ones_like(mascara)], axis=2).ravel())
    guardar.filepath_raw = MASCARA
    guardar.file_format = "PNG"
    guardar.save()
    return imagen("maisha_piel", np.clip(base, 0, 1)), imagen("maisha_tatuajes", np.clip(emis, 0, 1))


def material_piel(img_base, img_emision):
    m = ap.material("piel_humanizada", PALETA["piel_humanizada"][0], 0.60)
    n, enl = m.node_tree.nodes, m.node_tree.links
    bsdf = n.get("Principled BSDF")
    t1, t2 = n.new("ShaderNodeTexImage"), n.new("ShaderNodeTexImage")
    t1.image, t2.image = img_base, img_emision
    enl.new(t1.outputs["Color"], bsdf.inputs["Base Color"])
    enl.new(t2.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 1.5
    return m


# ---------------------------------------------------------------------------
# Ropa y accesorios
# ---------------------------------------------------------------------------

def medir_torso(cuerpo, forma):
    """Semiejes del torso (ya a 1,70 m) cada 2 cm de altura: para la falda, la capa y el cinturón."""
    tabla = []
    for k in range(70, 150, 2):
        zb = k / 100
        pts = [cuerpo.data.vertices[i].co for i, p in forma.base.items()
               if forma.zona[i] == "torso" and abs(p.z - zb) < 0.012]
        if len(pts) < 6:
            continue
        xs = [abs(q.x) for q in pts]
        ys = [q.y for q in pts]
        tabla.append((zb * ESCALA, max(xs), (max(ys) - min(ys)) / 2, (max(ys) + min(ys)) / 2))
    return tabla


def radio(tabla, z):
    if z <= tabla[0][0]:
        return tabla[0][1:]
    for a, b in zip(tabla, tabla[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(a[i] + (b[i] - a[i]) * t for i in (1, 2, 3))
    return tabla[-1][1:]


def falda(pz, tabla, z_cintura, z_bajo):
    """Falda de la túnica: cae de la cintura en diagonal, con vuelo, pliegues y el borde deshilachado."""
    lados, filas = 56, 22
    anillos = []
    for i in range(filas):
        s = i / (filas - 1)
        fila = []
        for j in range(lados):
            f = 2 * math.pi * j / lados
            cx, cy = math.cos(f), math.sin(f)
            dientes = 0.010 * abs(((f * 44 / (2 * math.pi)) % 1.0) - 0.5) * 2
            abajo = z_bajo + 0.07 * math.cos(f + 0.6) - dientes
            z = z_cintura + (abajo - z_cintura) * s
            rx, ry, cy0 = radio(tabla, max(z, tabla[0][0]))
            vuelo = max(0.0, z_cintura - z) * 0.32
            rx, ry = max(rx, 0.15) + 0.016 + vuelo, max(ry, 0.11) + 0.016 + vuelo * 0.85
            pl = 1.0 + 0.030 * math.sin(f * 9 + 0.7) * s + 0.012 * math.sin(f * 23) * s
            fila.append(pz.bm.verts.new(Vector((rx * cx * pl, cy0 + ry * cy * pl, z))))
        anillos.append(fila)
    caras = []
    for i in range(filas - 1):
        for j in range(lados):
            j2 = (j + 1) % lados
            caras.append(pz.bm.faces.new((anillos[i][j], anillos[i][j2], anillos[i + 1][j2], anillos[i + 1][j])))
    k = pz._i("tunica_lino_arena")
    for c in caras:
        c.material_index = k


def capa(pz, tabla, z_hombro):
    """Capa corta sobre el hombro izquierdo: cae por la espalda y el costado, sin tapar el pecho."""
    rx_h, ry_h, cy_h = radio(tabla, z_hombro - 0.02)
    arriba = [Vector(p) for p in ((0.06, cy_h + ry_h * 0.85, z_hombro + 0.03), (-0.01, cy_h + ry_h * 0.95, z_hombro + 0.04),
                                  (-0.09, cy_h + ry_h * 0.85, z_hombro + 0.055), (-rx_h * 0.85, cy_h + ry_h * 0.45, z_hombro + 0.085),
                                  (-rx_h * 1.18, cy_h + 0.02, z_hombro + 0.055), (-rx_h * 1.32, cy_h + 0.05, z_hombro - 0.01))]
    abajo = [Vector(p) for p in ((0.15, cy_h + 0.17, z_hombro - 0.42), (0.0, cy_h + 0.21, z_hombro - 0.51),
                                 (-0.16, cy_h + 0.20, z_hombro - 0.53), (-0.28, cy_h + 0.13, z_hombro - 0.49),
                                 (-0.33, cy_h + 0.09, z_hombro - 0.41), (-0.33, cy_h + 0.08, z_hombro - 0.31))]
    columnas, filas = 34, 22
    rejilla = []
    for i in range(filas):
        s = i / (filas - 1)
        fila = []
        for j in range(columnas):
            u = j / (columnas - 1)
            p = _catmull(arriba, u).lerp(_catmull(abajo, u), s)
            fuera = Vector((p.x, p.y - cy_h, 0.0))
            fuera = fuera.normalized() if fuera.length > 1e-6 else Y
            pl = (0.022 * math.sin(u * math.pi * 5.0 + 0.4) + 0.010 * math.sin(u * math.pi * 11.0)) * s ** 0.8
            p += fuera * (pl + 0.012 * math.sin(math.pi * min(s * 1.4, 1.0)))
            fila.append(pz.bm.verts.new(p))
        rejilla.append(fila)
    caras = []
    for i in range(filas - 1):
        for j in range(columnas - 1):
            caras.append(pz.bm.faces.new((rejilla[i][j], rejilla[i][j + 1], rejilla[i + 1][j + 1], rejilla[i + 1][j])))
    k = pz._i("capa_viaje_musgo")
    for c in caras:
        c.material_index = k
    pz.tubo([_catmull(arriba, k / 15) + Vector((0, 0, 0.004)) for k in range(16)], [(0.013, 0.010)] * 16,
            "capa_viaje_musgo", lados=10, lateral=Z)
    return arriba


def cetro(pz, agarre, eje, largo=1.75, desde_abajo=0.78):
    eje = eje.normalized()
    a1 = eje.cross(X if abs(eje.x) < 0.9 else Y).normalized()
    a2 = eje.cross(a1)
    abajo = agarre - eje * desde_abajo
    pts, rad = [], []
    for k in range(30):
        t = k / 29
        p = abajo + eje * ((largo - 0.10) * t) + a1 * (0.0035 * math.sin(t * 13) + 0.0015 * math.sin(t * 37)) \
            + a2 * (0.003 * math.cos(t * 11))
        pts.append(p)
        nudo = 0.0035 * max(0.0, math.sin(t * 29 + 1.0)) ** 8
        rad.append((0.0175 - 0.0035 * t + nudo, 0.0165 - 0.0035 * t + nudo))
    pz.tubo(pts, rad, "cetro_madera", lados=10, lateral=a1)
    pz.tubo([abajo - eje * 0.004, abajo + eje * 0.03], [(0.019, 0.019), (0.018, 0.018)], "cuero_cinturon", lados=10,
            lateral=a1)
    centro = abajo + eje * (largo - 0.035)
    pts, rad = [], []
    for k in range(32):
        t = k / 31
        a = 2 * math.pi * 1.3 * t
        r = 0.040 * (1 - 0.35 * t)
        pts.append(centro + a1 * (r * math.cos(a)) + a2 * (r * math.sin(a)) + eje * (-0.080 + 0.135 * t))
        rad.append((0.011 * (1 - 0.55 * t) + 0.002, 0.010 * (1 - 0.55 * t) + 0.002))
    pz.tubo(pts, rad, "cetro_madera", lados=8, lateral=eje)
    pz.esfera(centro, (0.024, 0.024, 0.030), "semilla_esmeralda", Z.rotation_difference(eje).to_matrix(), seg=(16, 12))


# ---------------------------------------------------------------------------
# Montaje
# ---------------------------------------------------------------------------

def construir():
    ap.escena_vacia()
    mats = {n: ap.material(n, *v) for n, v in PALETA.items() if n != "piel_humanizada"}   # la piel va aparte
    mats["ojo_blanco"] = ap.material("ojo_blanco", "#f1ece4", 0.30)
    mats["pupila"] = ap.material("pupila", "#140d08", 0.15)
    cuerpo, ojos = ap.cargar_malla_base("GEO-body_male_stylized")
    forma = Cuerpo(cuerpo)
    dar_forma(cuerpo, forma)
    for ojo in ojos:
        for v in ojo.data.vertices:
            v.co = v.co * ESCALA
        me_o = ojo.data
        me_o.materials.clear()
        for n in ("ojo_blanco", "iris_ambar", "pupila"):
            me_o.materials.append(mats[n])
        centro_o = sum((v.co for v in me_o.vertices), Vector()) / len(me_o.vertices)
        for pol in me_o.polygons:      # el iris mira al frente (-Y); la pupila, en su centro
            d = (pol.center - centro_o).normalized()
            frente = d.dot(Vector((0, -1, 0)))
            pol.material_index = 2 if frente > 0.975 else (1 if frente > 0.86 else 0)
    ojos_ob = ap.unir(ojos, "Maisha_Ojos")
    cuerpo.name = "Maisha_Cuerpo"
    base, zona = forma.base, forma.zona

    # articulaciones del brazo (a 1,70 m) para los tatuajes y el esqueleto
    brazos = {}
    for lado, s in (("L", -1), ("R", 1)):
        hombro = Vector((s * 0.19, 0.0, 1.32)) * ESCALA
        codo = forma.centro("brazo", 1.02, s) * ESCALA
        muneca = forma.centro("mano", 0.79, s) * ESCALA
        brazos[lado] = {"hombro": hombro, "codo": codo, "muneca": muneca, "inicio": 0.0,
                        "largo": (codo - hombro).length + (muneca - codo).length}
    tabla = medir_torso(cuerpo, forma)
    juntar_baldosas(cuerpo)
    z_corazon = 1.24 * ESCALA
    z_cuello = 1.475 * ESCALA
    mascara = hornear_tatuajes(cuerpo, forma, brazos, z_cuello, z_corazon)
    mat_piel = material_piel(*imagenes_piel(mascara))
    cuerpo.data.materials.clear()
    cuerpo.data.materials.append(mat_piel)
    ap.activar(cuerpo)
    bpy.ops.object.shade_smooth()

    # ropa que sigue al cuerpo: cuerpo de la túnica (deja al aire el hombro derecho y el esternón), pantalón y botas
    def tunica_dentro(i, p):
        b = base[i]
        if zona[i] != "torso" or not (0.88 < b.z < 1.44):
            return False
        hombro_der = b.x > 0.05 and b.z > 1.26 - 0.10 * suave(0.05, 0.20, b.x)
        escote = abs(b.x) < 0.045 + 0.04 * suave(1.18, 1.40, b.z) and b.y < -0.02 and b.z > 1.17
        return not (hombro_der or escote)
    tunica = ap.concha(cuerpo, "Maisha_Tunica", tunica_dentro, 0.009, 0.005, mats["tunica_lino_arena"])
    pantalon = ap.concha(cuerpo, "Maisha_Pantalon",
                         lambda i, p: zona[i] in ("pierna", "torso") and 0.30 < base[i].z < 0.92,
                         0.008, 0.004, mats["tela_pantalon"])
    botas = ap.concha(cuerpo, "Maisha_Botas", lambda i, p: zona[i] in ("pierna", "pie") and base[i].z < 0.42,
                      0.012, 0.005, mats["cuero_botas"])

    pz = Piezas("Maisha_Ropa", mats)
    z_cintura = 0.95 * ESCALA
    falda(pz, tabla, z_cintura, 0.60 * ESCALA)
    # cinturón con hebilla, bolsas de semillas y saquito
    rx, ry, cy = radio(tabla, z_cintura)
    anillo = [Vector(((rx + 0.03) * math.cos(a), cy + (ry + 0.03) * math.sin(a), z_cintura - 0.02 * math.cos(a - 0.4)))
              for a in (2 * math.pi * k / 32 for k in range(32))]
    pz.tubo(anillo, [(0.020, 0.0065)] * 32, "cuero_cinturon", lados=8, cerrado=True, lateral=Z)
    pz.caja((0.02, cy - ry - 0.034, z_cintura - 0.02), (0.04, 0.012, 0.034), "cuero_botas")
    for (x, dy, rot) in ((-(rx + 0.02), -0.04, -35), (rx + 0.02, 0.06, 140)):
        giro = Matrix.Rotation(math.radians(rot), 3, "Z")
        c = Vector((x, cy + dy, z_cintura - 0.08))
        pz.esfera(c, (0.042, 0.026, 0.050), "cuero_cinturon", giro, seg=(14, 10))
        pz.caja(c + Vector((0, 0, 0.032)), (0.075, 0.050, 0.012), "cuero_botas", giro)
        pz.esfera(c + Vector((0, 0, 0.018)), (0.008, 0.008, 0.008), "corazon_asili_oro", seg=(8, 6))
    # Corazón de Asili en el esternón
    rxc, ryc, cyc = radio(tabla, z_corazon)
    frente = Vector((0, cyc - ryc + 0.004, z_corazon))
    pz.tubo([frente + Vector((0, 0.006, 0)), frente + Vector((0, -0.006, 0))], [(0.030, 0.038), (0.026, 0.034)],
            "engaste_corazon", lados=20, lateral=X)
    pz.esfera(frente + Vector((0, -0.006, 0)), (0.019, 0.010, 0.026), "corazon_asili_oro", seg=(20, 12))
    ropa = pz.objeto()

    pc = Piezas("Maisha_Capa", mats)
    capa(pc, tabla, 1.40 * ESCALA)
    capa_ob = pc.objeto(grosor=0.008)

    pelo_ob = pelo(mats, cuerpo, forma)

    # cetro: por el puño derecho, con el eje lo más vertical posible
    d = (brazos["R"]["muneca"] - brazos["R"]["codo"]).normalized()
    eje = (Z - d * Z.dot(d)).normalized()
    agarre = brazos["R"]["muneca"] + d * 0.06
    pcet = Piezas("Cetro", mats)
    cetro(pcet, agarre, eje)
    cetro_ob = pcet.objeto()

    return {"cuerpo": cuerpo, "ojos": ojos_ob, "tunica": tunica, "pantalon": pantalon, "botas": botas, "ropa": ropa,
            "capa": capa_ob, "pelo": pelo_ob, "cetro": cetro_ob, "forma": forma, "brazos": brazos, "eje_cetro": eje,
            "agarre": agarre}


def pelo(mats, cuerpo, forma):
    """Pelo suave y oscuro: casquete que copia el cráneo y mechones como cintas que caen hacia la nuca y
    enmarcan la cara (sin astas)."""
    cab = [cuerpo.data.vertices[i].co.copy() for i, z in forma.zona.items() if z == "cabeza"]
    zs = [q.z for q in cab]
    tope = max(zs)
    centro = Vector((0, sum(q.y for q in cab) / len(cab), tope - 0.115))
    R = Vector((max(abs(q.x) for q in cab if q.z > centro.z) * 1.0,
                (max(q.y for q in cab) - min(q.y for q in cab if q.z > centro.z)) / 2, tope - centro.z))
    pz = Piezas("Maisha_Pelo", mats)
    # casquete: copia del cráneo por encima del nacimiento del pelo, separada 1 cm
    casquete = ap.concha(cuerpo, "Maisha_Casquete", lambda i, p: _es_pelo(p, centro, R), 0.010, 0.006,
                         mats["cabello_viajero"])

    def sobre(az, el, k):
        a, e = math.radians(az), math.radians(el)
        dd = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
        return centro + Vector((dd.x * R.x * k, dd.y * R.y * k, dd.z * R.z * k))

    def normal(p):
        q = p - centro
        return Vector((q.x / R.x ** 2, q.y / R.y ** 2, q.z / R.z ** 2)).normalized()

    def mechon(az0, el0, az1, el1, ancho, grueso=0.009, caida=0.0, capa_=1.10, curva=0.0):
        pts = []
        for k in range(9):
            t = k / 8
            e = t * t * (3 - 2 * t)
            pts.append(sobre(az0 + (az1 - az0) * e, el0 + (el1 - el0) * t, capa_ + 0.015 * math.sin(math.pi * t)))
        if caida > 0:
            fin = pts[-1]
            fuera = normal(fin)
            fuera.z = 0
            for k in range(1, 5):
                t = k / 4
                pts.append(fin + Vector((0, 0, -caida * t)) + fuera.normalized() * (curva * t * t))
        n = len(pts)
        rad = [(grueso * (0.6 + 0.4 * (1 - 0.85 * suave(0.55, 1.0, k / (n - 1)))),
                ancho * (1 - 0.85 * suave(0.55, 1.0, k / (n - 1))) + 0.002) for k in range(n)]
        # cinta con la cara ancha pegada al cráneo en cada punto
        pz.tubo(pts, rad, "cabello_viajero", lados=8, lateral=normal)

    for k, (az1, el1, ancho) in enumerate(((38, 22, 0.030), (55, 14, 0.026), (68, 6, 0.022), (22, 30, 0.026))):
        mechon(-22 + k * 4, 72 - k * 3, az1, el1, ancho, capa_=1.10 + 0.008 * k)
    for k, (az0, az1) in enumerate(((-30, -62), (-40, -80), (-55, -95))):
        mechon(az0, 74 - 4 * k, az1, -20 - 6 * k, 0.030, caida=0.035 + 0.01 * k, curva=0.006)
    for k, (az0, az1) in enumerate(((60, 78), (78, 98), (95, 112))):
        mechon(az0, 58 - 6 * k, az1, -24 - 4 * k, 0.030, caida=0.04, curva=0.006, capa_=1.095)
    for k in range(9):
        az0 = 115 + k * 16
        mechon(az0, 70, 180 + (az0 - 180) * 0.35, -40, 0.034, grueso=0.010, capa_=1.09 + 0.004 * (k % 2))
    nuca = sobre(180, -42, 1.12)
    pz.esfera(nuca, (0.032, 0.026, 0.028), "cabello_viajero", seg=(16, 12))
    pz.tubo([nuca + Vector((-0.024, -0.006, 0.006)), nuca + Vector((0, -0.004, 0.012)),
             nuca + Vector((0.024, -0.006, 0.006))], [(0.009, 0.006)] * 3, "cuero_cinturon", lados=8, lateral=Y)
    pz.tubo([nuca + Vector((0, 0.010, -0.010)), nuca + Vector((0, 0.022, -0.045)), nuca + Vector((0, 0.020, -0.080)),
             nuca + Vector((0, 0.012, -0.105))], [(0.016, 0.020), (0.014, 0.018), (0.010, 0.013), (0.003, 0.004)],
            "cabello_viajero", lados=10, lateral=X)
    mechones = pz.objeto()
    return ap.unir([mechones, casquete], "Maisha_Pelo")


def _es_pelo(p, centro, R):
    q = p - centro
    n = Vector((q.x / R.x, q.y / R.y, q.z / R.z))
    az = math.atan2(n.x, -n.y)
    if abs(az) < math.radians(70):
        limite = 0.42 - 0.30 * (abs(az) / math.radians(70)) ** 2      # frente: nacimiento del pelo
    elif abs(az) < math.radians(115):
        limite = 0.05 - 0.45 * (abs(az) - math.radians(70)) / math.radians(45)   # sienes, detrás de las orejas
    else:
        limite = -0.55                                                   # nuca
    return n.z > limite


# ---------------------------------------------------------------------------
# Esqueleto (los 27 huesos que espera maisha_3d.gd) y pesos
# ---------------------------------------------------------------------------

def huesos(p):
    forma, brazos = p["forma"], p["brazos"]
    E = ESCALA
    cab_z = 1.665 * E
    lista = [
        ("root", (0, 0, 0), (0, 0, 0.12), None),
        ("hips", (0, 0, 0.88 * E), (0, 0, 0.98 * E), "root"),
        ("spine_01", (0, 0, 0.98 * E), (0, 0, 1.08 * E), "hips"),
        ("spine_02", (0, 0, 1.08 * E), (0, 0, 1.20 * E), "spine_01"),
        ("chest", (0, 0, 1.20 * E), (0, 0, 1.42 * E), "spine_02"),
        ("neck", (0, 0, 1.42 * E), (0, -0.005, 1.53 * E), "chest"),
        ("head", (0, -0.005, 1.53 * E), (0, -0.01, 1.79 * E), "neck"),
        ("jaw", (0, 0.0, 1.585 * E), (0, -0.075, 1.545 * E), "head"),
        ("eyes_look", (0, -0.05, 1.63 * E), (0, -0.11, 1.63 * E), "head"),
        ("hair_back_01", (0, 0.085, cab_z), (0, 0.11, cab_z - 0.07), "head"),
        ("hair_back_02", (0, 0.11, cab_z - 0.07), (0, 0.12, cab_z - 0.14), "hair_back_01"),
        ("cloak_L_01", (-0.09, 0.08, 1.45 * E), (-0.14, 0.15, 1.17 * E), "chest"),
        ("cloak_L_02", (-0.14, 0.15, 1.17 * E), (-0.16, 0.19, 0.90 * E), "cloak_L_01"),
    ]
    for lado, s in (("L", -1), ("R", 1)):
        b = brazos[lado]
        d = (b["muneca"] - b["codo"]).normalized()
        rodilla = forma.centro("pierna", 0.36, s) * E
        tobillo = forma.centro("pierna", 0.10, s) * E
        punta = forma.centro("pie", 0.03, s)
        punta = Vector((punta.x, punta.y - 0.08, 0.03)) * E
        lista += [
            (f"shoulder_{lado}", (s * 0.03, 0.0, 1.38 * E), tuple(b["hombro"]), "chest"),
            (f"arm_{lado}", tuple(b["hombro"]), tuple(b["codo"]), f"shoulder_{lado}"),
            (f"forearm_{lado}", tuple(b["codo"]), tuple(b["muneca"]), f"arm_{lado}"),
            (f"hand_{lado}", tuple(b["muneca"]), tuple(b["muneca"] + d * 0.10), f"forearm_{lado}"),
            (f"thigh_{lado}", (s * 0.09, -0.01, 0.68 * E), tuple(rodilla), "hips"),
            (f"calf_{lado}", tuple(rodilla), tuple(tobillo), f"thigh_{lado}"),
            (f"foot_{lado}", tuple(tobillo), tuple(punta), f"calf_{lado}"),
        ]
    return lista


def aparejar(p):
    forma = p["forma"]
    arm = ap.crear_esqueleto("Maisha", huesos(p))
    zona = forma.zona
    brazo = {"L": {"shoulder_L", "arm_L", "forearm_L", "hand_L"}, "R": {"shoulder_R", "arm_R", "forearm_R", "hand_R"}}
    piernas = {f"{h}_{l}" for h in ("thigh", "calf", "foot") for l in "LR"}
    columna = {"hips", "spine_01", "spine_02", "chest", "neck"}

    def regla(n, i, co):
        z = zona.get(i, "torso")
        if z == "cabeza":
            if n == "jaw":
                return 1.0 if (co.z < 1.575 * ESCALA and co.y < -0.04) else 0.0
            return 1.0 if n in ("head", "neck") else 0.0
        if z in ("brazo", "mano"):
            return 1.0 if (n in brazo["L" if forma.base[i].x < 0 else "R"] or n == "chest") else 0.0
        if z in ("pierna", "pie"):
            return 1.0 if (n in piernas or n == "hips") else 0.0
        return 1.0 if (n in columna or n in ("shoulder_L", "shoulder_R", "thigh_L", "thigh_R")) else 0.0

    huesos_cuerpo = [b.name for b in arm.data.bones if not b.name.startswith(("cloak", "hair"))]
    ap.pesar(p["cuerpo"], arm, huesos_cuerpo, regla)
    for k in ("tunica", "pantalon", "botas"):
        ap.copiar_pesos(p["cuerpo"], p[k], arm)
    ap.pesar(p["ojos"], arm, ["head"])
    # falda, cinturón y corazón: la cadera y la columna mandan; los muslos, a medias y solo bajo la cadera
    # (si la falda copiara el peso del muslo que tiene al lado, sacaría picos al andar)
    ap.pesar(p["ropa"], arm, ["hips", "spine_01", "spine_02", "chest", "thigh_L", "thigh_R"],
             lambda n, i, co: (0.45 if co.z < 0.80 * ESCALA else 0.0) if n.startswith("thigh") else 1.0)
    ap.pesar(p["capa"], arm, ["chest", "neck", "shoulder_L", "cloak_L_01", "cloak_L_02"])
    ap.pesar(p["pelo"], arm, ["head", "hair_back_01", "hair_back_02"],
             lambda n, i, co: (1.0 if (co.z < 1.60 * ESCALA and co.y > 0.04) else 0.0) if n.startswith("hair") else 1.0)
    ap.anclar(p["cetro"], arm, "hand_R")
    return arm


# ---------------------------------------------------------------------------
# Animaciones (las 6 que usa maisha_3d.gd). La pose A de la malla base deja los brazos a ~68° bajo la
# horizontal: brazo(lado, abajo, adelante) los coloca a un ángulo final en vez de girar a ciegas.
# ---------------------------------------------------------------------------

def angulo_pose_a(arm, lado):
    b = arm.data.bones[f"arm_{lado}"]
    d = (b.tail_local - b.head_local).normalized()
    return math.degrees(math.asin(-d.z))


class Poses:
    def __init__(self, arm):
        self.a = {l: angulo_pose_a(arm, l) for l in "LR"}

    def brazo(self, lado, abajo, adelante=0.0, extra=()):
        """abajo: grados bajo la horizontal (90 = colgando); adelante: grados hacia delante."""
        g = abajo - self.a[lado]
        return [("Y", g if lado == "R" else -g), ("X", -adelante)] + list(extra)

    def reposo(self, respira=0.0, balanceo=0.0):
        return {
            "spine_01": [("X", 1.5 + 0.4 * respira)],
            "chest": [("X", -1.0 - 1.2 * respira)],
            "neck": [("X", 2.0)],
            "head": [("X", 2.0 + 0.6 * respira), ("Z", 1.5 * balanceo)],
            "arm_L": self.brazo("L", 84, 4 - 1.5 * balanceo),
            "forearm_L": [("X", -12.0)],
            "hand_L": [("Z", 6.0)],
            "arm_R": self.brazo("R", 82, 14),
            "forearm_R": [("X", -38.0)],
            "thigh_L": [("Y", 1.5)], "thigh_R": [("Y", -1.5)],
            "cloak_L_01": [("X", 2.0 + 1.5 * balanceo)],
            "cloak_L_02": [("X", 1.5 + 2.5 * balanceo)],
            "hair_back_01": [("X", 1.0 * balanceo)],
        }


CETRO_ARRIBA = (0.0, -0.10, 1.0)


def _paso(fase, amp):
    muslo = amp * math.sin(fase)
    rodilla = 6 + amp * 1.55 * max(0.0, math.cos(fase)) ** 1.5 + 4 * max(0.0, -math.sin(fase))
    punta = 14 * max(0.0, math.sin(fase)) - 24 * max(0.0, -math.sin(fase)) * max(0.0, math.cos(fase))
    return muslo, rodilla, muslo - rodilla - punta


def animar(arm, p):
    an = ap.Animador(arm, "hand_R", p["eje_cetro"])
    ps = Poses(arm)

    an.nueva("reposo")
    for f in range(0, 61, 6):
        t = 2 * math.pi * f / 60
        an.fotograma(f, ps.reposo(math.sin(t), math.sin(t + 0.8)),
                     mover={"hips": (0, 0, -0.004 * (1 - math.cos(t)) / 2)}, baston=CETRO_ARRIBA)
    an.cerrar("reposo")

    for nombre, n, amp, incl, braz, bote, codo in (("caminar_atento", 32, 24, 4, 1.0, 0.018, 14),
                                                 ("correr", 20, 38, 14, 1.5, 0.035, 60)):
        an.nueva(nombre)
        for f in range(0, n + 1, 2):
            fa = 2 * math.pi * f / n
            mL, rL, pL = _paso(fa, amp)
            mR, rR, pR = _paso(fa + math.pi, amp)
            g = math.sin(fa)
            pose = {
                "hips": [("Z", 5 * g), ("Y", 2.0 * g)],
                "spine_01": [("X", incl * 0.4)],
                "spine_02": [("Z", -4 * g), ("X", incl * 0.3)],
                "chest": [("Z", -3 * g), ("X", incl * 0.3)],
                "neck": [("X", -incl * 0.4)],
                "head": [("X", -incl * 0.3 + 2), ("Z", 2 * g)],
                "thigh_L": [("X", -mL)], "calf_L": [("X", rL)], "foot_L": [("X", pL)],
                "thigh_R": [("X", -mR)], "calf_R": [("X", rR)], "foot_R": [("X", pR)],
                "arm_L": ps.brazo("L", 82, -braz * mL * 0.9),
                "forearm_L": [("X", -codo - 8 * max(0.0, -math.sin(fa)))],
                "arm_R": ps.brazo("R", 82, 14 - braz * mR * 0.35),
                "forearm_R": [("X", -38.0 - codo * 0.4)],
                "cloak_L_01": [("X", 4 + incl * 0.6 + 2 * math.sin(2 * fa))],
                "cloak_L_02": [("X", 6 + incl + 4 * math.sin(2 * fa + 0.6))],
                "hair_back_01": [("X", 3 + 2 * math.sin(2 * fa + 0.4))],
                "hair_back_02": [("X", 2 + 3 * math.sin(2 * fa + 0.9))],
            }
            an.fotograma(f, pose, mover={"hips": (0.006 * g, 0, -bote * (1 - abs(math.cos(fa))))},
                         baston=(0.0, -0.10 - incl / 60, 1.0))
        an.cerrar(nombre)

    an.nueva("golpe_cetro")
    claves = [
        (0, 0, 0, ps.brazo("R", 82, 14), -38, ps.brazo("L", 84, 4), -12, 0.0, CETRO_ARRIBA),
        (9, 32, -4, ps.brazo("R", 25, -40), -45, ps.brazo("L", 35, 55), -55, 0.3, (0.35, 0.55, 0.76)),
        (13, 38, -6, ps.brazo("R", 18, -48), -50, ps.brazo("L", 30, 60), -60, 0.4, (0.25, 0.70, 0.67)),
        (17, -28, 10, ps.brazo("R", 70, 72), -10, ps.brazo("L", 75, -25), -25, 1.0, (-0.42, -0.89, 0.18)),
        (21, -42, 12, ps.brazo("R", 82, 55, [("Z", -15)]), -12, ps.brazo("L", 80, -30), -20, 1.0, (-0.85, 0.25, 0.05)),
        (28, -25, 6, ps.brazo("R", 80, 35), -25, ps.brazo("L", 84, -10), -15, 0.6, (-0.3, -0.2, 0.9)),
        (36, 0, 0, ps.brazo("R", 82, 14), -38, ps.brazo("L", 84, 4), -12, 0.0, CETRO_ARRIBA),
    ]
    for f, giro, incl, br, codo, bl, codo_l, z, cet in claves:
        pose = {
            "hips": [("Z", giro * 0.30)],
            "spine_01": [("X", incl * 0.4), ("Z", giro * 0.20)],
            "spine_02": [("Z", giro * 0.25), ("X", incl * 0.3)],
            "chest": [("Z", giro * 0.25), ("X", incl * 0.3)],
            "head": [("Z", -giro * 0.45), ("X", 3 - incl * 0.4)],
            "arm_R": br, "forearm_R": [("X", codo)], "arm_L": bl, "forearm_L": [("X", codo_l)],
            "thigh_L": [("X", -18 * z), ("Y", 3)], "calf_L": [("X", 22 * z)], "foot_L": [("X", 4 * z)],
            "thigh_R": [("X", 14 * z), ("Y", -3)], "calf_R": [("X", 16 * z)], "foot_R": [("X", -6 * z)],
            "cloak_L_01": [("X", 4 + 4 * z), ("Z", -giro * 0.3)],
            "cloak_L_02": [("X", 6 + 8 * z), ("Z", -giro * 0.45)],
            "hair_back_01": [("Z", -giro * 0.2)],
        }
        an.fotograma(f, pose, mover={"hips": (0, 0, -0.035 * z)}, baston=cet)
    an.cerrar("golpe_cetro")

    an.nueva("idle_mirar_tatuajes")
    hombro_l = p["brazos"]["L"]["hombro"]
    for f, k, traza in ((0, 0.0, 0), (18, 0.8, 0), (26, 1.0, 0), (40, 1.0, 1), (55, 1.0, -1), (70, 1.0, 0),
                        (78, 0.8, 0), (90, 0.0, 0)):
        pose = ps.reposo()
        pose.update({
            "forearm_L": [("Z", 35 * k)],
            "hand_L": [("Z", 6 - 30 * k)],
            "neck": [("X", 2 + 10 * k), ("Z", -8 * k)],
            "head": [("X", 2 + 16 * k + 2 * traza), ("Z", -10 * k + 3 * traza)],
            "chest": [("X", -1 + 3 * k), ("Z", -4 * k)],
        })
        delante = hombro_l + Vector((0.10, -0.30, -0.20))     # el antebrazo alzado ante el pecho
        colgando = p["brazos"]["L"]["muneca"] + Vector((0.08, -0.06, 0.0))
        objetivo = colgando.lerp(delante + Vector((0.0, 0.0, 0.01 * traza)), k)
        an.fotograma(f, pose, ik={"forearm_L": objetivo} if k > 0 else None, baston=CETRO_ARRIBA)
    an.cerrar("idle_mirar_tatuajes")

    an.nueva("eco_despertar")
    for f, k in ((0, 0.0), (14, 0.7), (22, 1.0), (44, 1.0), (60, 0.0)):
        pose = ps.reposo()
        pose.update({
            "spine_02": [("X", -5 * k)],
            "chest": [("X", -1 - 11 * k)],
            "neck": [("X", 2 - 8 * k)],
            "head": [("X", 2 - 14 * k)],
            "arm_L": ps.brazo("L", 84 - 14 * k, 4 + 10 * k),
            "forearm_L": [("X", -12 - 10 * k)],
            "hand_L": [("Z", 6 + 20 * k)],
            "cloak_L_01": [("X", 2 + 6 * k)],
            "cloak_L_02": [("X", 1.5 + 10 * k)],
            "hair_back_01": [("X", 4 * k)],
        })
        an.fotograma(f, pose, mover={"hips": (0, 0, 0.006 * k)}, baston=CETRO_ARRIBA)
    an.cerrar("eco_despertar")
    animar_acrobacias(an, ps)


def _agachar(muslo, rodilla):
    """Cuánto baja la cadera con el muslo adelantado `muslo` grados y la rodilla doblada `rodilla` grados
    (pies en el suelo). Las medidas son las de la pierna de la malla base."""
    lt, lc = 0.29, 0.26
    return lt * math.cos(math.radians(muslo)) + lc * math.cos(math.radians(rodilla - muslo)) - (lt + lc)


def _piernas(mL, rL, mR=None, rR=None, punta=0.0):
    mR = mL if mR is None else mR
    rR = rL if rR is None else rR
    return {"thigh_L": [("X", -mL)], "calf_L": [("X", rL)], "foot_L": [("X", mL - rL + punta)],
            "thigh_R": [("X", -mR)], "calf_R": [("X", rR)], "foot_R": [("X", mR - rR + punta)]}


def _tramos(claves, f):
    """Interpola linealmente una tabla [(fotograma, valores...)] en el fotograma f."""
    for (f0, *a), (f1, *b) in zip(claves, claves[1:]):
        if f0 <= f <= f1:
            t = (f - f0) / (f1 - f0)
            return [x + (y - x) * t for x, y in zip(a, b)]
    return list(claves[-1][1:])


def animar_acrobacias(an, ps):
    """esquivar_rodando, saltar, aterrizar y trepar. En el sitio: el juego mueve el cuerpo."""
    # Voltereta hacia delante: se agacha, se hace un ovillo, da la vuelta entera y se levanta.
    # Columnas: vuelta (grados), ovillo (0-1), agachada (0-1)
    claves = [(0, 0, 0.0, 0.2), (3, 10, 0.4, 0.8), (6, 70, 1.0, 0.6), (9, 150, 1.0, 0.4), (12, 220, 1.0, 0.4),
              (15, 290, 1.0, 0.5), (18, 345, 0.8, 0.8), (21, 360, 0.3, 0.8), (24, 360, 0.0, 0.25)]
    an.nueva("esquivar_rodando")
    for f in range(0, 25):
        vuelta, k, c = _tramos(claves, f)
        m, r = 50 * c + 75 * k, 90 * c + 60 * k
        pose = _piernas(min(m, 125), min(r, 145))
        pose.update({
            "hips": [("X", vuelta)],
            "spine_01": [("X", 12 * k + 6 * c)], "spine_02": [("X", 20 * k + 6 * c)], "chest": [("X", 15 * k)],
            "neck": [("X", 18 * k)], "head": [("X", 12 * k)],
            "arm_L": ps.brazo("L", 75, 15 * c + 55 * k), "forearm_L": [("X", -15 - 70 * k)],
            "arm_R": ps.brazo("R", 75, 20 * c + 55 * k), "forearm_R": [("X", -38 - 45 * k)],
            "cloak_L_01": [("X", 4 + 12 * k)], "cloak_L_02": [("X", 6 + 18 * k)],
            "hair_back_01": [("X", 6 * k)],
        })
        de_pie = 0.88 * ESCALA
        # el ovillo rueda pegado al suelo: cadera más baja con el cuerpo tumbado (90° y 270°)
        ovillo = 0.21 + 0.24 * math.cos(math.radians(vuelta)) ** 2
        alto = (de_pie + _agachar(50 * c, 90 * c)) * (1 - k) + ovillo * k
        an.fotograma(f, pose, mover={"hips": (0, 0, alto - de_pie)})
    an.cerrar("esquivar_rodando")

    # Salto: se agacha, se impulsa con los brazos y se queda en el aire (la última pose se mantiene)
    an.nueva("saltar")
    for f, c, impulso, aire in ((0, 0.0, 0.0, 0.0), (5, 1.0, 0.0, 0.0), (8, 0.0, 1.0, 0.0), (13, 0.0, 0.3, 1.0),
                                (20, 0.0, 0.0, 1.0)):
        m, r = 55 * c, 95 * c
        pose = _piernas(m + 45 * aire, r + 70 * aire, m + 15 * aire, r + 35 * aire, punta=25 * impulso)
        pose.update({
            "spine_01": [("X", 14 * c - 4 * impulso)], "chest": [("X", 6 * c - 6 * impulso + 4 * aire)],
            "head": [("X", 4 - 8 * impulso)],
            "arm_L": ps.brazo("L", 82 - 35 * aire, -35 * c + 80 * impulso + 15 * aire),
            "forearm_L": [("X", -15 - 25 * aire)],
            "arm_R": ps.brazo("R", 82 - 30 * aire, 14 - 30 * c + 60 * impulso + 15 * aire),
            "forearm_R": [("X", -38 - 10 * aire)],
            "cloak_L_01": [("X", 4 - 14 * impulso + 10 * aire)], "cloak_L_02": [("X", 6 - 20 * impulso + 16 * aire)],
            "hair_back_01": [("X", -8 * impulso + 6 * aire)], "hair_back_02": [("X", -6 * impulso + 8 * aire)],
        })
        an.fotograma(f, pose, mover={"hips": (0, 0, _agachar(m, r))}, baston=CETRO_ARRIBA)
    an.cerrar("saltar")

    # Aterrizaje: cae con las rodillas, amortigua y se levanta
    an.nueva("aterrizar")
    for f, c, aire in ((0, 0.0, 1.0), (3, 1.0, 0.0), (6, 0.8, 0.0), (14, 0.0, 0.0)):
        m, r = 60 * c, 105 * c
        pose = ps.reposo() if c == 0 and aire == 0 else {}
        pose.update(_piernas(m + 45 * aire, r + 70 * aire, m + 15 * aire, r + 35 * aire))
        pose.update({
            "spine_01": [("X", 16 * c + 1.5)], "chest": [("X", 6 * c - 1)], "head": [("X", 2 - 6 * c)],
            "arm_L": ps.brazo("L", 82 - 35 * aire - 25 * c, 4 + 15 * aire + 25 * c),
            "forearm_L": [("X", -12 - 25 * aire - 20 * c)],
            "arm_R": ps.brazo("R", 82 - 30 * aire - 15 * c, 14 + 15 * aire + 10 * c),
            "forearm_R": [("X", -38 - 10 * aire)],
            "cloak_L_01": [("X", 4 + 10 * aire + 8 * c)], "cloak_L_02": [("X", 6 + 16 * aire + 14 * c)],
        })
        an.fotograma(f, pose, mover={"hips": (0, 0, _agachar(m, r))}, baston=CETRO_ARRIBA)
    an.cerrar("aterrizar")

    # Trepar (en bucle): de cara a la pared (-Y); mano izquierda arriba con el pie derecho arriba y al revés
    an.nueva("trepar")
    for f in range(0, 41, 2):
        fase = 2 * math.pi * f / 40
        arriba_l = 0.5 + 0.5 * math.sin(fase)
        arriba_r = 1 - arriba_l
        mL, mR = 20 + 55 * arriba_r, 20 + 55 * arriba_l
        pose = _piernas(mL, 30 + 75 * arriba_r, mR, 30 + 75 * arriba_l, punta=-10)
        pose.update({
            "spine_01": [("X", 8)], "spine_02": [("X", 4)], "chest": [("X", -2), ("Z", 4 * math.sin(fase))],
            "neck": [("X", -10)], "head": [("X", -14), ("Z", 5 * math.sin(fase))],
            "hips": [("Z", -3 * math.sin(fase))],
            "cloak_L_01": [("X", 6)], "cloak_L_02": [("X", 8 + 3 * math.sin(2 * fase))],
        })
        manos = {"forearm_L": Vector((-0.20, -0.30, 1.42 + 0.30 * arriba_l)),
                 "forearm_R": Vector((0.20, -0.30, 1.42 + 0.30 * arriba_r))}
        an.fotograma(f, pose, mover={"hips": (0, 0, -0.03 + 0.03 * abs(math.sin(fase)))}, ik=manos)
    an.cerrar("trepar")


# ---------------------------------------------------------------------------

def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = construir()
    arm = aparejar(p)
    animar(arm, p)
    objetos = [p[k] for k in ("cuerpo", "ojos", "tunica", "pantalon", "botas", "ropa", "capa", "pelo", "cetro")]
    ap.exportar(SALIDA, arm, objetos)
    ap.informe("MAISHA", arm, objetos, SALIDA)
    if "--vistas" in args:
        carpeta = args[args.index("--vistas") + 1]
        os.makedirs(carpeta, exist_ok=True)
        foto = ap.preparar_vistas()
        for nombre, pos, obj, lente in (("1_frente", (0, -4.6, 1.0), (0, 0, 0.88), 50),
                                        ("2_perfil", (4.6, 0, 1.0), (0, 0, 0.88), 50),
                                        ("3_espalda", (0, 4.6, 1.0), (0, 0, 0.88), 50),
                                        ("4_tres_cuartos", (-3.0, -3.6, 1.6), (0, 0, 0.88), 50),
                                        ("5_cara", (-0.25, -0.80, 1.60), (0, 0, 1.55), 70),
                                        ("6_brazo", (1.0, -0.9, 1.3), (0.35, 0, 1.0), 60)):
            foto(os.path.join(carpeta, f"maisha_{nombre}.png"), pos, obj, lente)
        for accion, f, nombre, pos, obj in (
                ("reposo", 0, "a_reposo_tres_cuartos", (-3.0, -3.6, 1.6), (0, 0, 0.88)),
                ("caminar_atento", 8, "b_caminar_perfil", (4.6, 0, 1.0), (0, 0, 0.88)),
                ("golpe_cetro", 13, "c_golpe_carga", (-2.2, -4.0, 1.4), (0, 0, 0.95)),
                ("golpe_cetro", 17, "d_golpe_impacto", (-2.2, -4.0, 1.4), (0, 0, 0.95)),
                ("idle_mirar_tatuajes", 40, "e_mirar_tatuajes", (-1.4, -2.2, 1.5), (0, 0, 1.25)),
                ("eco_despertar", 30, "f_eco", (-2.4, -3.6, 1.4), (0, 0, 1.0)),
                ("esquivar_rodando", 3, "g_rodar_entrada", (4.6, 0, 1.0), (0, 0, 0.6)),
                ("esquivar_rodando", 9, "h_rodar_ovillo", (4.6, 0, 1.0), (0, 0, 0.5)),
                ("esquivar_rodando", 15, "i_rodar_vuelta", (4.6, 0, 1.0), (0, 0, 0.5)),
                ("saltar", 5, "j_salto_carga", (-3.0, -3.6, 1.4), (0, 0, 0.8)),
                ("saltar", 8, "k_salto_impulso", (-3.0, -3.6, 1.4), (0, 0, 0.9)),
                ("saltar", 20, "l_salto_aire", (-3.0, -3.6, 1.4), (0, 0, 0.9)),
                ("aterrizar", 3, "m_aterrizar", (-3.0, -3.6, 1.4), (0, 0, 0.7)),
                ("trepar", 0, "n_trepar_a", (3.4, 3.0, 1.6), (0, 0, 1.0)),
                ("trepar", 20, "o_trepar_b", (3.4, 3.0, 1.6), (0, 0, 1.0))):
            arm.animation_data.action = bpy.data.actions[accion]
            bpy.context.scene.frame_set(f)
            foto(os.path.join(carpeta, f"maisha_{nombre}.png"), pos, obj, 50)
        arm.animation_data.action = None


if __name__ == "__main__":
    main()
