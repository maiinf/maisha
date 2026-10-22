# -*- coding: utf-8 -*-
"""
Maisha en 3D: el Guardián de la Memoria (ficha documentacion/referencias_visuales_3d/personajes/ref_maisha_mistico.md).

Ser humanizado y sin género marcado, 1,70 m, sin astas, pelo suave color ceniza, túnica asimétrica de lino,
capa corta de musgo sobre el hombro izquierdo, cinturón con bolsas, pantalón y botas altas, el Corazón de Asili
en el esternón y los Tatuajes de la Memoria en brazos, hombros y cuello (oscuros al despertar; brillan en oro con
los Ecos). Lleva el Cetro de Raíz en la mano derecha.

    blender -b --factory-startup -P herramientas/blender/modelar_maisha.py
    blender -b --factory-startup -P herramientas/blender/modelar_maisha.py -- --vistas <carpeta>

Sale modelos/personajes/maisha.glb y la máscara de los tatuajes modelos/personajes/maisha_tatuajes_mascara.png
(blanco = tatuaje), para el sombreador de piel.

Medidas en metros, suelo en z = 0, el frente mira a -Y (a +Z en Godot).
"""

import math
import os
import random
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Quaternion, Vector

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CARPETA = os.path.join(RAIZ, "modelos", "personajes")
SALIDA = os.path.join(CARPETA, "maisha.glb")
MASCARA = os.path.join(CARPETA, "maisha_tatuajes_mascara.png")

azar = random.Random(2024)
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))

# ---------------------------------------------------------------------------
# Paleta de la ficha (y unos pocos de apoyo)
# ---------------------------------------------------------------------------

PALETA = {
    # nombre:                     (color,     rugosidad, metal, emisión)
    "piel_humanizada":            ("#e8ded0", 0.60, 0.0, 0.0),
    "cabello_viajero":            ("#827768", 0.70, 0.0, 0.0),
    "tunica_lino_arena":          ("#d5caa8", 0.85, 0.0, 0.0),
    "capa_viaje_musgo":           ("#46543b", 0.85, 0.0, 0.0),
    "cuero_cinturon":             ("#4a3828", 0.70, 0.1, 0.0),
    "corazon_asili_oro":          ("#f5c238", 0.20, 0.1, 1.6),
    "cetro_madera":               ("#4e3b2b", 0.80, 0.0, 0.0),
    "semilla_esmeralda":          ("#2ecc8a", 0.15, 0.0, 1.8),
    # de apoyo
    "tela_pantalon":              ("#7d735f", 0.90, 0.0, 0.0),
    "cuero_botas":                ("#5a4534", 0.75, 0.05, 0.0),
    "ojo_blanco":                 ("#f1ece4", 0.30, 0.0, 0.0),
    "iris_ambar":                 ("#7a4a1c", 0.25, 0.0, 0.25),
    "pupila":                     ("#140d08", 0.20, 0.0, 0.0),
    "brillo_ojo":                 ("#ffffff", 0.10, 0.0, 2.0),
    "labios":                     ("#c99a8a", 0.55, 0.0, 0.0),
    "engaste_corazon":            ("#b8a58a", 0.55, 0.0, 0.0),
}
COLOR_TATUAJE_DORMIDO = "#3d3835"   # tatuajes_memoria_dormidos
COLOR_TATUAJE_ACTIVO = "#ffd766"    # tatuajes_memoria_activos (emisión 1,5)


def _lineal(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(hexa):
    h = hexa.lstrip("#")
    return [_lineal(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]


def material(nombre, hexa, rugosidad, metal, emision):
    m = bpy.data.materials.new(nombre)
    if m.node_tree is None:
        m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    color = rgb(hexa) + [1.0]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rugosidad
    bsdf.inputs["Metallic"].default_value = metal
    if emision > 0:
        bsdf.inputs["Emission Color"].default_value = color
        bsdf.inputs["Emission Strength"].default_value = emision
    m.diffuse_color = color
    return m


# ---------------------------------------------------------------------------
# Constructor de mallas
# ---------------------------------------------------------------------------

class Malla:
    def __init__(self, nombre):
        self.nombre = nombre
        self.bm = bmesh.new()
        self.uv = self.bm.loops.layers.uv.new("UVMap")
        self.mats = []

    def indice(self, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        return self.mats.index(mat)

    def poner_mat(self, caras, mat):
        i = self.indice(mat)
        for f in caras:
            f.material_index = i

    def esfera(self, centro, radios, mat, giro=None, seg=(16, 10), uv=(0.0, 0.0, 0.03, 0.03)):
        M = Matrix.Translation(Vector(centro))
        if giro is not None:
            M = M @ giro.to_4x4()
        M = M @ Matrix.Diagonal((radios[0], radios[1], radios[2], 1.0))
        r = bmesh.ops.create_uvsphere(self.bm, u_segments=seg[0], v_segments=seg[1], radius=1.0, matrix=M,
                                      calc_uvs=False)
        caras = {f for v in r["verts"] for f in v.link_faces}
        self.poner_mat(caras, mat)
        self.uv_fijo(caras, uv)
        return r["verts"], caras

    def caja(self, centro, tam, mat, giro=None, uv=(0.0, 0.0, 0.03, 0.03)):
        M = Matrix.Translation(Vector(centro))
        if giro is not None:
            M = M @ giro.to_4x4()
        M = M @ Matrix.Diagonal((tam[0], tam[1], tam[2], 1.0))
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=M, calc_uvs=False)
        caras = {f for v in r["verts"] for f in v.link_faces}
        self.poner_mat(caras, mat)
        self.uv_fijo(caras, uv)
        return caras

    def uv_fijo(self, caras, rect):
        u0, v0, u1, v1 = rect
        for f in caras:
            for k, l in enumerate(f.loops):
                l[self.uv].uv = (u0 + (u1 - u0) * (k % 2), v0 + (v1 - v0) * (k // 2 % 2))

    def tubo(self, centros, radios, mat, lateral, lados=16, tapas=(True, True), cerrado=False, forma=None,
             uv=(0.0, 0.0, 0.03, 0.03), giro_fase=0.0):
        """Tubo que pasa por los centros con anillos elípticos (rx a lo largo de «lateral», ry perpendicular).
        forma(i, fase) -> factor del radio, para pliegues y bultos. UV: u alrededor, v a lo largo."""
        n = len(centros)
        centros = [Vector(c) for c in centros]
        anillos = []
        for i, c in enumerate(centros):
            if cerrado:
                t = (centros[(i + 1) % n] - centros[i - 1]).normalized()
            else:
                t = (centros[min(i + 1, n - 1)] - centros[max(i - 1, 0)]).normalized()
            lat = Vector(lateral(i, c) if callable(lateral) else lateral)
            ex = (lat - t * lat.dot(t)).normalized()
            ey = t.cross(ex)
            rx, ry = radios[i]
            anillo = []
            for j in range(lados):
                fase = 2 * math.pi * j / lados + giro_fase
                k = forma(i, fase) if forma else 1.0
                p = c + ex * (rx * k * math.cos(fase)) + ey * (ry * k * math.sin(fase))
                anillo.append(self.bm.verts.new(p))
            anillos.append(anillo)
        u0, v0, u1, v1 = uv
        # v proporcional a la longitud recorrida, para que la textura no se estire
        largo = [0.0]
        for i in range(1, n + (1 if cerrado else 0)):
            largo.append(largo[-1] + (centros[i % n] - centros[i - 1]).length)
        total = largo[-1] or 1.0
        caras = []
        pares = range(n) if cerrado else range(n - 1)
        for i in pares:
            a, b = anillos[i], anillos[(i + 1) % n]
            for j in range(lados):
                j2 = (j + 1) % lados
                f = self.bm.faces.new((a[j], a[j2], b[j2], b[j]))
                caras.append(f)
                us = (j / lados, (j + 1) / lados, (j + 1) / lados, j / lados)
                va, vb = largo[i] / total, largo[i + 1] / total
                vs = (va, va, vb, vb)
                for l, uu, vv in zip(f.loops, us, vs):
                    l[self.uv].uv = (u0 + (u1 - u0) * uu, v0 + (v1 - v0) * vv)
        if not cerrado:
            if tapas[0]:
                caras.append(self.bm.faces.new(list(reversed(anillos[0]))))
            if tapas[-1]:
                caras.append(self.bm.faces.new(anillos[-1]))
        self.poner_mat(caras, mat)
        return anillos, caras


def a_objeto(malla, mats, suave=True, grosor=0.0):
    me = bpy.data.meshes.new(malla.nombre)
    bmesh.ops.remove_doubles(malla.bm, verts=malla.bm.verts[:], dist=1e-6)
    bmesh.ops.recalc_face_normals(malla.bm, faces=malla.bm.faces[:])
    malla.bm.to_mesh(me)
    malla.bm.free()
    for nombre in malla.mats:
        me.materials.append(mats[nombre])
    ob = bpy.data.objects.new(malla.nombre, me)
    bpy.context.collection.objects.link(ob)
    activar(ob)
    if grosor:
        mod = ob.modifiers.new("Grosor", "SOLIDIFY")
        mod.thickness = grosor
        mod.offset = 1.0
        bpy.ops.object.modifier_apply(modifier=mod.name)
    if suave:
        bpy.ops.object.shade_smooth()
    return ob


def activar(ob):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)


def suavizar(x0, x1, x):
    t = max(0.0, min(1.0, (x - x0) / (x1 - x0)))
    return t * t * (3 - 2 * t)


def gauss(d, s):
    return math.exp(-(d * d) / (2 * s * s))


# ---------------------------------------------------------------------------
# Proporciones (7 cabezas, 1,70 m)
# ---------------------------------------------------------------------------

ALTURA = 1.70
CABEZA_C = Vector((0.0, 0.004, 1.578))       # centro de la cabeza
CABEZA_R = Vector((0.074, 0.088, 0.112))     # semiejes del cráneo
HOMBRO = 0.175                               # articulación del hombro (x)
Z_HOMBRO = 1.385
CADERA = 0.088
Z_CADERA = 0.88
ANG_BRAZO = math.radians(50)                 # pose A: brazos 50° por debajo de la horizontal


def puntos_brazo(lado):
    s = -1 if lado == "L" else 1
    hombro = Vector((s * HOMBRO, 0.0, Z_HOMBRO))
    d1 = Vector((s * math.cos(ANG_BRAZO), 0.0, -math.sin(ANG_BRAZO)))
    codo = hombro + d1 * 0.28
    d2 = Vector((s * math.cos(ANG_BRAZO), -0.16, -math.sin(ANG_BRAZO))).normalized()
    muneca = codo + d2 * 0.25
    return hombro, codo, muneca, d2


def puntos_pierna(lado):
    s = -1 if lado == "L" else 1
    cadera = Vector((s * CADERA, 0.0, Z_CADERA))
    rodilla = Vector((s * 0.094, -0.012, 0.48))
    tobillo = Vector((s * 0.100, 0.006, 0.085))
    punta = Vector((s * 0.108, -0.150, 0.030))
    return cadera, rodilla, tobillo, punta


# Torso: (z, rx, ry, desplazamiento en y)
TORSO = [
    (0.835, 0.125, 0.098, 0.000),
    (0.88, 0.146, 0.108, 0.002),
    (0.95, 0.142, 0.100, 0.004),
    (1.02, 0.128, 0.090, 0.004),
    (1.08, 0.130, 0.090, 0.000),
    (1.16, 0.143, 0.096, -0.004),
    (1.24, 0.153, 0.100, -0.006),
    (1.30, 0.158, 0.098, -0.004),
    (1.345, 0.158, 0.093, 0.000),
    (1.38, 0.145, 0.086, 0.004),
    (1.405, 0.118, 0.076, 0.006),
    (1.425, 0.082, 0.064, 0.004),
    (1.442, 0.058, 0.055, 0.000),
    (1.47, 0.048, 0.049, -0.006),
    (1.51, 0.044, 0.047, -0.006),
    (1.54, 0.040, 0.044, -0.004),
]

# Atlas de la piel: dónde cae cada parte en la textura (u0, v0, u1, v1)
UV_TORSO = (0.0, 0.0, 1.0, 0.5)
UV_BRAZO = {"R": (0.0, 0.5, 0.5, 1.0), "L": (0.5, 0.5, 1.0, 1.0)}
UV_LISO = (0.0, 0.0, 0.02, 0.02)   # esquina sin tatuajes (abajo del torso, bajo la túnica)


def radio_torso(z):
    """rx, ry y desplazamiento en y del torso a la altura z (interpolado)."""
    if z <= TORSO[0][0]:
        return TORSO[0][1:]
    for a, b in zip(TORSO, TORSO[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(a[k] + (b[k] - a[k]) * t for k in (1, 2, 3))
    return TORSO[-1][1:]


# ---------------------------------------------------------------------------
# Cuerpo: torso y cuello, brazos, manos y corazón de Asili
# ---------------------------------------------------------------------------

def torso(m):
    centros = [Vector((0, dy, z)) for z, _, _, dy in TORSO]
    radios = [(rx, ry) for _, rx, ry, _ in TORSO]
    m.tubo(centros, radios, "piel_humanizada", X, lados=28, uv=UV_TORSO)


def brazo(m, lado):
    hombro, codo, muneca, d2 = puntos_brazo(lado)
    s = -1 if lado == "L" else 1
    centros, radios = [], []
    # empieza dentro del torso y es más grueso en el hombro: hace de deltoides (y conserva los tatuajes)
    d1 = (codo - hombro).normalized()
    inicio = hombro - d1 * 0.055 + Vector((0, 0, -0.012))
    tramo = [(inicio, 0.040), (hombro - d1 * 0.022, 0.056), (hombro + d1 * 0.012, 0.058)]
    for k in range(1, 6):
        t = k / 6
        tramo.append((hombro.lerp(codo, t), 0.056 - 0.020 * t + 0.003 * math.sin(math.pi * t)))
    tramo.append((codo, 0.034))
    for k in range(1, 6):
        t = k / 6
        tramo.append((codo.lerp(muneca, t), 0.037 - 0.010 * t + 0.003 * math.sin(math.pi * t * 0.8)))
    tramo.append((muneca, 0.025))
    for c, r in tramo:
        centros.append(c)
        radios.append((r, r * 0.86))
    m.tubo(centros, radios, "piel_humanizada", Vector((0, -1, 0)), lados=16, tapas=(False, True), uv=UV_BRAZO[lado])


def marco_mano(lado):
    """Ejes de la mano en la pose de reposo: d (hacia los dedos), ancho (del meñique al índice) y la normal de
    la palma. La izquierda cuelga con la palma hacia el cuerpo; la derecha tiene el ancho lo más vertical
    posible, porque agarra el cetro."""
    hombro, codo, muneca, d = puntos_brazo(lado)
    s = -1 if lado == "L" else 1
    if lado == "L":
        ancho = Vector((0, -1, 0))
        ancho = (ancho - d * ancho.dot(d)).normalized()
        palma_n = d.cross(ancho).normalized()
        if palma_n.x * s > 0:
            palma_n = -palma_n
    else:
        ancho = (Z - d * Z.dot(d)).normalized()
        palma_n = d.cross(ancho).normalized()
        if palma_n.y < 0:
            palma_n = -palma_n
    return muneca, d, ancho, palma_n


def agarre_cetro():
    """Centro y eje del puño derecho: por ahí pasa el cetro."""
    muneca, d, ancho, palma_n = marco_mano("R")
    nudillos = muneca + d * 0.095
    return nudillos + palma_n * 0.026 - d * 0.006, ancho


def mano(m, lado, cerrada=0.25):
    """Palma, cuatro dedos y pulgar. cerrada: 0 abierta, 1 puño cerrado alrededor del cetro."""
    muneca, d, ancho, palma_n = marco_mano(lado)
    giro_dedos = d.cross(palma_n).normalized()        # girar sobre este eje lleva los dedos hacia la palma
    base = muneca + d * 0.006
    nudillos = muneca + d * 0.095
    m.tubo([base, muneca + d * 0.050, nudillos], [(0.021, 0.012), (0.025, 0.0135), (0.024, 0.012)],
           "piel_humanizada", ancho, lados=12, uv=UV_LISO)
    doblez = math.radians(35 + 150 * cerrada)          # cuánto se cierran los dedos en total
    for k, (off, largo) in enumerate(((0.021, 0.080), (0.007, 0.088), (-0.007, 0.083), (-0.021, 0.068))):
        p = nudillos + ancho * off
        pts = [p]
        for f in range(3):
            dir_ = Quaternion(giro_dedos, doblez * (f + 0.5) / 3) @ d
            p = p + dir_ * largo / 3
            pts.append(p)
        r = 0.0100 - 0.0008 * abs(k - 1.5)
        m.tubo(pts, [(r, r * 0.92), (r * 0.96, r * 0.9), (r * 0.9, r * 0.85), (r * 0.78, r * 0.74)],
               "piel_humanizada", palma_n, lados=8, uv=UV_LISO)
    # pulgar, en el lado del índice
    p0 = muneca + d * 0.030 + ancho * 0.024 + palma_n * 0.008
    dir1 = (d * 0.55 + ancho * 0.55 + palma_n * (0.35 + 0.4 * cerrada)).normalized()
    p1 = p0 + dir1 * 0.032
    dir2 = (dir1 + palma_n * (0.3 + 0.9 * cerrada) - ancho * (0.6 * cerrada)).normalized()
    p2 = p1 + dir2 * 0.030
    m.tubo([p0, p1, p2], [(0.0125, 0.011), (0.0108, 0.0098), (0.0090, 0.0084)], "piel_humanizada", palma_n,
           lados=8, uv=UV_LISO)


def corazon(m):
    """Corazón de Asili: gema de oro líquido en una cavidad del esternón."""
    z = 1.30
    rx, ry, dy = radio_torso(z)
    p = Vector((0, dy - ry + 0.004, z))
    giro = Matrix.Rotation(math.radians(90), 3, "X")
    m.tubo([p + Vector((0, 0.006, 0)), p + Vector((0, -0.006, 0))], [(0.030, 0.038), (0.026, 0.034)],
           "engaste_corazon", X, lados=20, uv=UV_LISO)
    m.esfera(p + Vector((0, -0.006, 0)), (0.019, 0.010, 0.026), "corazon_asili_oro", seg=(20, 12))


# ---------------------------------------------------------------------------
# Cabeza: cráneo con rasgos, ojos, párpados, cejas, orejas
# ---------------------------------------------------------------------------

def cabeza(m):
    verts, caras = m.esfera((0, 0, 0), (1, 1, 1), "piel_humanizada", seg=(64, 48), uv=UV_LISO)
    for v in verts:
        p = v.co.copy()                               # punto de la esfera unidad
        x, y, z = p
        # mandíbula y barbilla que se estrechan
        if z < 0:
            k = (-z) ** 1.6
            x *= 1 - 0.36 * k
            y *= 1 - 0.12 * k
        # frente un poco plana y occipital redondo
        if y < 0 and z > 0.2:
            y *= 1 - 0.06 * z
        q = Vector((x * CABEZA_R.x, y * CABEZA_R.y, z * CABEZA_R.z))
        frente = -1.0 if p.y < 0 else 0.0
        # rasgos (desplazamientos en metros sobre la cara, que mira a -Y)
        d = 0.0
        cara = max(0.0, -p.y) ** 4
        # nariz: cresta suave desde el entrecejo y punta redondeada
        d += 0.0045 * gauss(p.x, 0.075) * suavizar(0.18, -0.20, p.z) * suavizar(-0.32, -0.12, p.z) * cara
        d += 0.0110 * gauss(p.x, 0.11) * gauss(p.z + 0.22, 0.09) * cara
        for sx in (-1, 1):
            d += 0.0030 * gauss(p.x - sx * 0.10, 0.06) * gauss(p.z + 0.27, 0.05) * cara      # aletas
        d += 0.008 * gauss(p.x, 0.22) * gauss(p.z + 0.78, 0.13) * max(0.0, -p.y) ** 2      # barbilla
        d += 0.0035 * gauss(p.x, 0.17) * gauss(p.z + 0.43, 0.040) * cara                    # labio sup.
        d += 0.0042 * gauss(p.x, 0.15) * gauss(p.z + 0.53, 0.040) * cara                    # labio inf.
        d -= 0.0028 * gauss(p.x, 0.19) * gauss(p.z + 0.48, 0.016) * cara                    # comisura
        d -= 0.0020 * gauss(p.x, 0.10) * gauss(p.z + 0.36, 0.030) * cara                    # surco nasolabial
        d += 0.0035 * gauss(p.z - 0.30, 0.09) * max(0.0, -p.y) ** 3                         # arco de las cejas
        for sx in (-1, 1):
            d -= 0.0085 * gauss(p.x - sx * 0.36, 0.13) * gauss(p.z - 0.10, 0.11) * max(0.0, -p.y) ** 2  # cuencas
            d += 0.0045 * gauss(p.x - sx * 0.62, 0.17) * gauss(p.z + 0.12, 0.14) * max(0.0, -p.y)       # pómulos
        n = q.normalized()
        v.co = CABEZA_C + q + n * d
    # boca: una línea fina, apenas sonriente, sobre los labios
    zn = -0.48
    kx, ky = 1 - 0.36 * abs(zn) ** 1.6, 1 - 0.12 * abs(zn) ** 1.6
    pts = []
    for k in range(9):
        x = -0.021 + 0.042 * k / 8
        xn = x / (CABEZA_R.x * kx)
        y = -math.sqrt(max(0.0, 1 - xn * xn - zn * zn)) * CABEZA_R.y * ky
        sonrisa = 0.0018 * (abs(x) / 0.021) ** 2
        pts.append(CABEZA_C + Vector((x, y - 0.0012, zn * CABEZA_R.z + sonrisa)))
    m.tubo(pts, [(0.0016, 0.0011 * (1 - 0.4 * abs(k - 4) / 4))for k in range(9)], "labios", Z, lados=6)
    # ojos
    for sx in (-1, 1):
        dirn = Vector((sx * 0.36, -0.93, 0.10)).normalized()
        sup = CABEZA_C + Vector((dirn.x * CABEZA_R.x, dirn.y * CABEZA_R.y, dirn.z * CABEZA_R.z))
        centro = sup + Vector((0, 0.010, 0))
        r = 0.0135
        m.esfera(centro, (r, r, r), "ojo_blanco", seg=(16, 12))
        mira = Vector((sx * 0.08, -1, 0.02)).normalized()
        giro = Vector((0, 0, 1)).rotation_difference(mira).to_matrix()
        # iris, pupila y brillo, cada uno un poco más fuera que el anterior para que no se tapen
        m.esfera(centro + mira * (r * 0.88), (0.0082, 0.0082, 0.0025), "iris_ambar", giro, seg=(16, 8))
        m.esfera(centro + mira * (r * 0.95), (0.0040, 0.0040, 0.0017), "pupila", giro, seg=(12, 6))
        m.esfera(centro + mira * (r * 1.05) + Vector((-sx * 0.003, 0, 0.0035)), (0.0013, 0.0013, 0.0006),
                 "brillo_ojo", giro, seg=(8, 4))
        # párpados: medio casquete por encima (mirada serena) y uno fino por debajo
        for arriba, corte, grosor in ((True, 0.18, 1.18), (False, -0.55, 1.12)):
            vs, cs = m.esfera(centro, (r * grosor, r * grosor, r * grosor), "piel_humanizada", seg=(16, 12))
            quitar = [v for v in vs if ((v.co - centro).z / (r * grosor) < corte) == arriba
                      or (v.co - centro).y > r * 0.35]
            bmesh.ops.delete(m.bm, geom=quitar, context="VERTS")
        # ceja
        pts = []
        for k in range(6):
            t = k / 5
            a = sx * (0.16 + 0.36 * t)
            dir_ = Vector((a, -0.92, 0.36 + 0.05 * math.sin(math.pi * t) - 0.06 * t)).normalized()
            pts.append(CABEZA_C + Vector((dir_.x * CABEZA_R.x, dir_.y * CABEZA_R.y, dir_.z * CABEZA_R.z)) * 1.035)
        m.tubo(pts, [(0.0028, 0.0018 * (1.0 - 0.5 * k / 5) + 0.0008) for k in range(6)], "cabello_viajero",
               Vector((0, -1, 0)), lados=6)
        # oreja
        oreja = CABEZA_C + Vector((sx * CABEZA_R.x * 0.98, 0.012, -0.012))
        m.esfera(oreja, (0.010, 0.020, 0.030), "piel_humanizada", Matrix.Rotation(math.radians(-12 * sx), 3, "Y")
                 @ Matrix.Rotation(math.radians(15), 3, "X"), seg=(12, 10))


def pelo(m):
    """Pelo suave color ceniza: casquete con mechones gruesos, flequillo a un lado y recogido bajo en la nuca."""
    vs, cs = m.esfera((0, 0, 0), (1, 1, 1), "cabello_viajero", seg=(40, 26))
    quitar = []
    for v in vs:
        p = v.co.copy()
        az = math.atan2(p.x, -p.y)                    # 0 = frente
        limite = -0.05 + 0.48 * math.cos(az) ** 2 * (1 if abs(az) < math.pi / 2 else 0)  # nacimiento del pelo
        if abs(az) > math.radians(70):
            limite = -0.62 + 0.25 * max(0.0, math.cos(az)) if abs(az) < math.radians(110) else -0.62
        if p.z < limite:
            quitar.append(v)
            continue
        mech = 1.0 + 0.020 * max(0.0, math.sin(az * 7 + p.z * 3))
        k = 1.07 * mech
        v.co = CABEZA_C + Vector((p.x * CABEZA_R.x * k, p.y * CABEZA_R.y * k, p.z * CABEZA_R.z * 1.05 * mech))
    bmesh.ops.delete(m.bm, geom=quitar, context="VERTS")

    # Mechones: cintas gruesas que siguen la superficie de la cabeza y luego caen
    def sobre(az, el, k):
        """Punto sobre el cráneo: az en grados (0 = frente, 90 = derecha, 180 = nuca), el en grados (90 = arriba)."""
        a, e = math.radians(az), math.radians(el)
        d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
        return CABEZA_C + Vector((d.x * CABEZA_R.x * k, d.y * CABEZA_R.y * k, d.z * CABEZA_R.z * 1.04 * k))

    def normal(p):
        q = p - CABEZA_C
        return Vector((q.x / CABEZA_R.x ** 2, q.y / CABEZA_R.y ** 2, q.z / CABEZA_R.z ** 2)).normalized()

    def mechon(az0, el0, az1, el1, ancho, grueso=0.009, caida=0.0, capa=1.10, curva=0.0):
        pts = []
        for k in range(9):
            t = k / 8
            ease = t * t * (3 - 2 * t)
            pts.append(sobre(az0 + (az1 - az0) * ease, el0 + (el1 - el0) * t, capa + 0.015 * math.sin(math.pi * t)))
        if caida > 0:
            fin = pts[-1]
            fuera = normal(fin)
            fuera.z = 0
            for k in range(1, 5):
                t = k / 4
                pts.append(fin + Vector((0, 0, -caida * t)) + fuera.normalized() * (curva * t * t))
        n = len(pts)
        rad = []
        for k in range(n):
            t = k / (n - 1)
            afila = 1.0 - 0.85 * suavizar(0.55, 1.0, t)
            rad.append((grueso * (0.6 + 0.4 * afila), ancho * afila + 0.002))
        m.tubo(pts, rad, "cabello_viajero", lambda i, c: normal(c), lados=8)

    # flequillo con raya a la izquierda, que barre la frente hacia la derecha
    for k, (az1, el1, ancho) in enumerate(((38, 24, 0.030), (55, 16, 0.026), (68, 8, 0.022), (22, 32, 0.026))):
        mechon(-22 + k * 4, 72 - k * 3, az1, el1, ancho, capa=1.11 + 0.008 * k)
    # lado izquierdo (desde la raya hacia la sien y la mandíbula)
    for k, (az0, az1) in enumerate(((-30, -62), (-40, -80), (-55, -95))):
        mechon(az0, 74 - 4 * k, az1, -18 - 6 * k, 0.030, caida=0.035 + 0.01 * k, curva=0.006, capa=1.10)
    # lado derecho, detrás del flequillo
    for k, (az0, az1) in enumerate(((60, 78), (78, 98), (95, 112))):
        mechon(az0, 58 - 6 * k, az1, -22 - 4 * k, 0.030, caida=0.04, curva=0.006, capa=1.095)
    # coronilla y nuca: bajan juntándose hacia el recogido
    for k in range(9):
        az0 = 115 + k * 16
        az1 = 180 + (az0 - 180) * 0.35
        mechon(az0, 70, az1, -40, 0.034, grueso=0.010, capa=1.09 + 0.004 * (k % 2))
    for az in (-8, 8, 30, -30):
        mechon(az + 180, 88, az * 0.5 + 180, 40, 0.032, capa=1.10)
    # recogido bajo en la nuca, atado con una tira de cuero, y la coleta corta
    nuca = sobre(180, -42, 1.12)
    m.esfera(nuca, (0.032, 0.026, 0.028), "cabello_viajero", seg=(16, 12))
    m.tubo([nuca + Vector((-0.024, -0.006, 0.006)), nuca + Vector((0, -0.004, 0.012)),
            nuca + Vector((0.024, -0.006, 0.006))], [(0.009, 0.006)] * 3, "cuero_cinturon", Y, lados=8)
    cola = [nuca + Vector((0, 0.010, -0.010)), nuca + Vector((0, 0.022, -0.045)), nuca + Vector((0, 0.020, -0.080)),
            nuca + Vector((0, 0.012, -0.105))]
    m.tubo(cola, [(0.016, 0.020), (0.014, 0.018), (0.010, 0.013), (0.003, 0.004)], "cabello_viajero", X, lados=10)


# ---------------------------------------------------------------------------
# Ropa: túnica, capa, cinturón y bolsas, pantalón y botas
# ---------------------------------------------------------------------------

def tunica(m):
    """Túnica asimétrica de lino: deja el hombro derecho y la clavícula al aire, escote en el esternón para el
    Corazón de Asili, falda que cae en diagonal con el borde deshilachado."""
    lados, filas = 56, 34
    anillos = []
    for i in range(filas):
        s = i / (filas - 1)
        anillo = []
        for j in range(lados):
            fase = 2 * math.pi * j / lados
            cx, cy = math.cos(fase), math.sin(fase)
            # borde de arriba: alto en el hombro izquierdo, bajo bajo la axila derecha, escote delante
            arriba = 1.395 - 0.175 * suavizar(-0.25, 0.85, cx)
            arriba -= 0.11 * gauss(math.atan2(cy, cx) + math.pi / 2, 0.32)
            # bajo en diagonal con flecos
            dientes = 0.010 * abs(((fase * 44 / (2 * math.pi)) % 1.0) - 0.5) * 2
            abajo = 0.60 + 0.07 * math.cos(fase + 0.6) - dientes
            z = arriba + (abajo - arriba) * s
            rx, ry, dy = radio_torso(z)
            holgura = 0.004 + 0.009 * suavizar(0.0, 0.25, s)      # pegada al cuerpo en el borde de arriba
            if z < 0.99:
                vuelo = (0.99 - z) * 0.30
                rx, ry = max(rx, 0.146) + vuelo, max(ry, 0.108) + vuelo * 0.85
            plieg = 1.0 + 0.030 * math.sin(fase * 9 + 0.7) * suavizar(1.02, 0.80, z) \
                + 0.012 * math.sin(fase * 23) * suavizar(1.0, 0.7, z)
            p = Vector(((rx + holgura) * cx * plieg, dy + (ry + holgura) * cy * plieg, z))
            anillo.append(m.bm.verts.new(p))
        anillos.append(anillo)
    caras = []
    for i in range(filas - 1):
        for j in range(lados):
            j2 = (j + 1) % lados
            caras.append(m.bm.faces.new((anillos[i][j], anillos[i][j2], anillos[i + 1][j2], anillos[i + 1][j])))
    m.poner_mat(caras, "tunica_lino_arena")
    m.uv_fijo(caras, UV_LISO)
    # dobladillo del borde de arriba: se lee como tela y no como un escalón
    m.tubo([v.co.copy() for v in anillos[0]], [(0.0055, 0.0045)] * lados, "tunica_lino_arena", Z, lados=6,
           cerrado=True)
    # tirante sobre el hombro izquierdo hasta la espalda
    hombro = Vector((-HOMBRO + 0.06, 0.0, 1.405))
    m.tubo([Vector((-0.11, -0.085, 1.33)), hombro + Vector((0, -0.04, 0.012)), hombro + Vector((0, 0.04, 0.010)),
            Vector((-0.10, 0.085, 1.31))], [(0.032, 0.006)] * 4, "tunica_lino_arena", X, lados=8)


def _catmull(pts, t):
    """Curva suave que pasa por los puntos (t de 0 a 1)."""
    n = len(pts) - 1
    x = min(max(t, 0.0), 1.0) * n
    i = min(int(x), n - 1)
    f = x - i
    p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * f * f * f)


# Capa: borde de arriba (del cuello por la espalda hasta encima del hombro izquierdo) y bajo
CAPA_ARRIBA = [Vector(p) for p in ((0.060, 0.072, 1.405), (-0.010, 0.082, 1.418), (-0.085, 0.074, 1.432),
                                   (-0.150, 0.045, 1.458), (-0.215, 0.030, 1.432), (-0.250, 0.060, 1.372))]
CAPA_ABAJO = [Vector(p) for p in ((0.135, 0.150, 0.960), (0.000, 0.185, 0.870), (-0.150, 0.180, 0.845),
                                  (-0.260, 0.120, 0.880), (-0.300, 0.090, 0.960), (-0.300, 0.080, 1.060))]


def capa(m):
    """Capa corta de viaje sobre el hombro izquierdo: por encima del hombro y cayendo por la espalda y el
    costado, sin tapar el pecho; pliegues verticales y el bajo curvo. Se puede quitar (pieza aparte)."""
    columnas, filas = 34, 22
    rejilla = []
    for i in range(filas):
        s = i / (filas - 1)
        fila = []
        for j in range(columnas):
            u = j / (columnas - 1)
            a = _catmull(CAPA_ARRIBA, u)
            b = _catmull(CAPA_ABAJO, u)
            p = a.lerp(b, s)
            fuera = Vector((p.x, p.y - 0.01, 0.0))
            fuera = fuera.normalized() if fuera.length > 1e-6 else Y
            pliegue = (0.022 * math.sin(u * math.pi * 5.0 + 0.4) + 0.010 * math.sin(u * math.pi * 11.0)) * s ** 0.8
            bulto = 0.012 * math.sin(math.pi * min(s * 1.4, 1.0))
            p += fuera * (pliegue + bulto)
            fila.append(m.bm.verts.new(p))
        rejilla.append(fila)
    caras = []
    for i in range(filas - 1):
        for j in range(columnas - 1):
            caras.append(m.bm.faces.new((rejilla[i][j], rejilla[i][j + 1], rejilla[i + 1][j + 1], rejilla[i + 1][j])))
    m.poner_mat(caras, "capa_viaje_musgo")
    m.uv_fijo(caras, UV_LISO)
    # dobladillo enrollado a lo largo del borde de arriba
    borde = [_catmull(CAPA_ARRIBA, k / 15) + Vector((0, 0, 0.004)) for k in range(16)]
    m.tubo(borde, [(0.013, 0.010)] * 16, "capa_viaje_musgo", Z, lados=10)


def cinturon(m):
    z0 = 1.005
    pts = []
    n = 28
    for k in range(n):
        a = 2 * math.pi * k / n
        z = z0 - 0.025 * math.cos(a - 0.4)
        rx, ry, dy = radio_torso(z)
        pts.append(Vector(((rx + 0.020) * math.cos(a), dy + (ry + 0.020) * math.sin(a), z)))
    m.tubo(pts, [(0.020, 0.0065)] * n, "cuero_cinturon", Z, lados=8, cerrado=True)
    # hebilla
    m.caja((0.02, -0.118, z0 - 0.02), (0.040, 0.012, 0.034), "cuero_botas")
    # extremo colgante del nudo
    m.tubo([Vector((0.04, -0.118, z0 - 0.03)), Vector((0.05, -0.122, z0 - 0.09)), Vector((0.045, -0.12, z0 - 0.15))],
           [(0.010, 0.003)] * 3, "cuero_cinturon", X, lados=6)
    # bolsas de semillas
    for (x, y, z, rot) in ((-0.135, -0.07, 0.93, -35), (0.12, 0.08, 0.94, 140)):
        giro = Matrix.Rotation(math.radians(rot), 3, "Z")
        m.esfera((x, y, z), (0.042, 0.026, 0.050), "cuero_cinturon", giro, seg=(14, 10))
        m.caja((x, y, z + 0.032), (0.075, 0.050, 0.012), "cuero_botas", giro)
        m.esfera((x + 0.0, y, z + 0.018), (0.008, 0.008, 0.008), "corazon_asili_oro", seg=(8, 6))
    # saquito atado
    m.esfera((-0.06, -0.12, 0.92), (0.025, 0.020, 0.030), "tunica_lino_arena", seg=(12, 8))
    m.tubo([Vector((-0.06, -0.12, 0.95)), Vector((-0.06, -0.122, 0.99))], [(0.008, 0.008)] * 2, "cuero_cinturon",
           X, lados=6)


def piernas(m):
    for lado in ("L", "R"):
        cadera, rodilla, tobillo, punta = puntos_pierna(lado)
        tramo = [(cadera + Vector((0, 0, 0.03)), 0.084), (cadera, 0.084), (cadera.lerp(rodilla, 0.3), 0.078),
                 (cadera.lerp(rodilla, 0.65), 0.066), (rodilla, 0.054), (rodilla.lerp(tobillo, 0.15), 0.054)]
        m.tubo([c for c, _ in tramo], [(r, r * 0.95) for _, r in tramo], "tela_pantalon", Vector((0, -1, 0)),
               lados=16, uv=UV_LISO)
        # bota alta: caña y pie
        cana = [(rodilla.lerp(tobillo, 0.10), 0.062), (rodilla.lerp(tobillo, 0.16), 0.058),
                (rodilla.lerp(tobillo, 0.45), 0.054), (rodilla.lerp(tobillo, 0.80), 0.046), (tobillo, 0.044)]
        m.tubo([c for c, _ in cana], [(r, r * 0.92) for _, r in cana], "cuero_botas", Vector((0, -1, 0)), lados=16)
        s = -1 if lado == "L" else 1
        x = tobillo.x
        pie = [Vector((x, 0.050, 0.070)), Vector((x, 0.005, 0.062)), Vector((x + s * 0.004, -0.075, 0.046)),
               Vector((x + s * 0.007, -0.140, 0.036)), Vector((x + s * 0.008, -0.168, 0.030))]
        rad = [(0.038, 0.050), (0.044, 0.052), (0.047, 0.040), (0.041, 0.030), (0.026, 0.020)]
        m.tubo(pie, rad, "cuero_botas", X, lados=14)
        m.caja((x + s * 0.004, -0.055, 0.008), (0.090, 0.225, 0.016), "cuero_cinturon")
        # correas de la caña
        for t in (0.35, 0.70):
            c = rodilla.lerp(tobillo, t)
            r = 0.058 - 0.012 * t
            m.tubo([c + Vector((0, 0, 0.008)), c - Vector((0, 0, 0.008))], [(r, r * 0.93)] * 2, "cuero_cinturon",
                   Vector((0, -1, 0)), lados=16)


# ---------------------------------------------------------------------------
# Cetro de Raíz: bastón de 1,75 m con espiral que abraza la semilla
# ---------------------------------------------------------------------------

LARGO_CETRO = 1.75
AGARRE_DESDE_ABAJO = 0.78      # el puño queda a 78 cm de la contera: con el brazo caído, la contera toca el suelo


def cetro(m, agarre, eje):
    """Bastón de roble a lo largo de «eje» (de la contera a la punta), con el puño en «agarre»."""
    eje = eje.normalized()
    a1 = eje.cross(X if abs(eje.x) < 0.9 else Y).normalized()
    a2 = eje.cross(a1)
    abajo = agarre - eje * AGARRE_DESDE_ABAJO
    pts, rad = [], []
    n = 30
    for k in range(n):
        t = k / (n - 1)
        p = abajo + eje * ((LARGO_CETRO - 0.10) * t)
        p += a1 * (0.0035 * math.sin(t * 13) + 0.0015 * math.sin(t * 37)) + a2 * (0.003 * math.cos(t * 11))
        pts.append(p)
        nudo = 0.0035 * max(0.0, math.sin(t * 29 + 1.0)) ** 8
        rad.append((0.0175 - 0.0035 * t + nudo, 0.0165 - 0.0035 * t + nudo))
    m.tubo(pts, rad, "cetro_madera", a1, lados=10)
    # contera algo más ancha
    m.tubo([abajo - eje * 0.004, abajo + eje * 0.03], [(0.019, 0.019), (0.018, 0.018)], "cuero_cinturon", a1, lados=10)
    # espiral de la punta que abraza la semilla
    centro = abajo + eje * (LARGO_CETRO - 0.035)
    pts, rad = [], []
    for k in range(32):
        t = k / 31
        a = 2 * math.pi * 1.3 * t
        r = 0.040 * (1 - 0.35 * t)
        pts.append(centro + a1 * (r * math.cos(a)) + a2 * (r * math.sin(a)) + eje * (-0.080 + 0.135 * t))
        rad.append((0.011 * (1 - 0.55 * t) + 0.002, 0.010 * (1 - 0.55 * t) + 0.002))
    m.tubo(pts, rad, "cetro_madera", eje, lados=8)
    giro = Z.rotation_difference(eje).to_matrix()
    m.esfera(centro, (0.024, 0.024, 0.030), "semilla_esmeralda", giro, seg=(16, 12))


# ---------------------------------------------------------------------------
# Tatuajes de la Memoria: textura de piel y máscara
# ---------------------------------------------------------------------------

TAM = 1024


class Lienzo:
    """Dibuja trazos en metros sobre una zona del atlas (cada zona sabe cuántos metros mide la superficie)."""
    def __init__(self):
        self.mascara = np.zeros((TAM, TAM), np.float32)

    def trazo(self, zona, puntos, grueso):
        (u0, v0, u1, v1), (wm, hm) = zona[:2]
        ox, oy = zona[2] if len(zona) > 2 else (0.0, 0.0)          # desplazamiento de la zona (metros)
        puntos = [(x + ox, y + oy) for x, y in puntos]
        kx, ky = (u1 - u0) * TAM / wm, (v1 - v0) * TAM / hm       # píxeles por metro
        aa = 0.8 / min(kx, ky)
        for a, b in zip(puntos, puntos[1:]):
            ax, ay = a
            bx, by = b
            x0 = int((u0 * TAM) + (min(ax, bx) - grueso) * kx) - 2
            x1 = int((u0 * TAM) + (max(ax, bx) + grueso) * kx) + 3
            y0 = int((v0 * TAM) + (min(ay, by) - grueso) * ky) - 2
            y1 = int((v0 * TAM) + (max(ay, by) + grueso) * ky) + 3
            x0, y0 = max(x0, 0), max(y0, 0)
            x1, y1 = min(x1, TAM), min(y1, TAM)
            if x1 <= x0 or y1 <= y0:
                continue
            gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
            mx = (gx - u0 * TAM) / kx
            my = (gy - v0 * TAM) / ky
            dx, dy = bx - ax, by - ay
            l2 = dx * dx + dy * dy or 1e-12
            t = np.clip(((mx - ax) * dx + (my - ay) * dy) / l2, 0, 1)
            d = np.hypot(mx - (ax + t * dx), my - (ay + t * dy))
            val = np.clip((grueso / 2 + aa - d) / (2 * aa), 0, 1)
            self.mascara[y0:y1, x0:x1] = np.maximum(self.mascara[y0:y1, x0:x1], val)

    def circulo(self, zona, c, r, grueso, a0=0.0, a1=2 * math.pi, pasos=40):
        pts = [(c[0] + r * math.cos(a0 + (a1 - a0) * k / pasos), c[1] + r * math.sin(a0 + (a1 - a0) * k / pasos))
               for k in range(pasos + 1)]
        self.trazo(zona, pts, grueso)

    def punto(self, zona, c, r):
        self.circulo(zona, c, r * 0.5, r, pasos=12)


def dibujar_tatuajes():
    lz = Lienzo()
    G = 0.0026   # grosor de las líneas (2,6 mm)
    for lado in ("R", "L"):
        # zona del brazo: alrededor ~0,22 m; a lo largo, desde dentro del torso (5 cm) hasta la muñeca
        hombro, codo, muneca, _ = puntos_brazo(lado)
        largo = 0.057 + (codo - hombro).length + (muneca - codo).length
        zona = (UV_BRAZO[lado], (0.22, largo), (0.0, 0.050))
        W, H = 0.22, 0.56
        # el hombro: arcos concéntricos
        for k, r in enumerate((0.030, 0.045, 0.060)):
            lz.circulo(zona, (W * 0.5, 0.0), r, G * (1.2 if k == 0 else 1.0), math.radians(10), math.radians(170))
        for k in range(7):
            a = math.radians(20 + 140 * k / 6)
            lz.trazo(zona, [(W * 0.5 + 0.064 * math.cos(a), 0.064 * math.sin(a)),
                            (W * 0.5 + 0.074 * math.cos(a), 0.074 * math.sin(a))], G)
        # brazalete sobre el codo y en la muñeca (dos líneas cada uno)
        for v in (0.235, 0.247, 0.540, 0.551):
            lz.trazo(zona, [(0.004, v), (W - 0.004, v)], G * 0.9)
        # runas del brazo: triángulos y marcas
        for k in range(5):
            x = 0.03 + k * 0.04
            lz.trazo(zona, [(x, 0.16), (x + 0.012, 0.185), (x + 0.024, 0.16), (x, 0.16)], G * 0.9)
            lz.trazo(zona, [(x + 0.012, 0.195), (x + 0.012, 0.215)], G * 0.9)
        # antebrazo: constelación (eje con nodos y ramas)
        eje_u = W * (0.25 if lado == "R" else 0.75)
        nodos = [(eje_u, 0.30 + k * 0.045) for k in range(6)]
        lz.trazo(zona, [(eje_u, 0.285), (eje_u, 0.53)], G)
        for k, (x, y) in enumerate(nodos):
            lz.circulo(zona, (x, y), 0.0055, G * 0.9)
            lz.punto(zona, (x, y), 0.0028)
            off = 0.035 * (1 if k % 2 else -1)
            lz.trazo(zona, [(x + 0.0055 * (1 if off > 0 else -1), y), (x + off, y + 0.018)], G * 0.8)
            lz.punto(zona, (x + off, y + 0.018), 0.0032)
        # espiral de crecimiento y círculo de agua (los glifos que irán despertando con los Ecos)
        cx = W * (0.62 if lado == "R" else 0.38)
        pts = []
        for k in range(80):
            a = k / 79 * 2.6 * 2 * math.pi
            r = 0.002 + 0.0040 * a / (2 * math.pi)
            pts.append((cx + r * math.cos(a), 0.36 + r * math.sin(a)))
        lz.trazo(zona, pts, G * 0.85)
        lz.circulo(zona, (cx, 0.46), 0.014, G)
        lz.circulo(zona, (cx, 0.46), 0.008, G * 0.8)
        lz.punto(zona, (cx, 0.46), 0.003)
        # cheurones a lo largo del otro costado
        for k in range(6):
            y = 0.30 + k * 0.038
            x = W * (0.88 if lado == "R" else 0.12)
            lz.trazo(zona, [(x - 0.008, y), (x, y + 0.010), (x + 0.008, y)], G * 0.85)
    # torso: alrededor ~0,85 m, alto 0,705 m (z 0,835 → 1,54)
    W, H = 0.85, 0.705
    zona = (UV_TORSO, (W, H))
    def v_de(z):
        return z - 0.835
    # banda del cuello con puntos
    for z in (1.452, 1.466):
        lz.trazo(zona, [(0.003, v_de(z)), (W - 0.003, v_de(z))], G * 0.9)
    for k in range(34):
        lz.punto(zona, ((k + 0.5) * W / 34, v_de(1.459)), 0.0026)
    # hombro y clavícula derechos (u ≈ 0 = +X, delante = 0,75): líneas que bajan hacia el corazón
    for s in (1, -1):
        base_u = (0.0 if s > 0 else 0.5)
        for k in range(3):
            y0 = v_de(1.40 - 0.018 * k)
            lz.trazo(zona, [((0.03 + base_u) * W, y0), ((0.10 + base_u) * W, y0 - 0.010), ((0.17 + base_u) * W,
                                                                                          y0 - 0.012)], G)
    # venas de savia: del corazón (delante, z 1,30) hacia las clavículas
    cu = 0.75 * W
    for s in (-1, 1):
        lz.trazo(zona, [(cu + s * 0.03, v_de(1.31)), (cu + s * 0.08, v_de(1.35)), (cu + s * 0.15, v_de(1.38)),
                        (cu + s * 0.22, v_de(1.39))], G * 0.9)
    # espalda: un gran círculo mnemotécnico entre los omóplatos (u ≈ 0,25)
    bu = 0.25 * W
    for r in (0.040, 0.055):
        lz.circulo(zona, (bu, v_de(1.27)), r, G)
    for k in range(9):
        a = 2 * math.pi * k / 9
        lz.punto(zona, (bu + 0.068 * math.cos(a), v_de(1.27) + 0.068 * math.sin(a)), 0.004)
    return lz.mascara


def imagenes_tatuajes(mascara):
    piel = np.array(rgb(PALETA["piel_humanizada"][0]), np.float32)
    tinta = np.array(rgb(COLOR_TATUAJE_DORMIDO), np.float32)
    oro = np.array(rgb(COLOR_TATUAJE_ACTIVO), np.float32)
    # leve variación de tono en la piel para que no sea plana
    ruido = np.random.default_rng(7).normal(0, 0.008, (TAM, TAM)).astype(np.float32)
    k = (mascara * 0.88)[..., None]
    base = piel[None, None, :] * (1 + ruido[..., None]) * (1 - k) + tinta[None, None, :] * k
    emis = oro[None, None, :] * mascara[..., None]
    def a_imagen(nombre, rgb_arr):
        img = bpy.data.images.new(nombre, TAM, TAM, alpha=False)
        rgba = np.concatenate([rgb_arr, np.ones((TAM, TAM, 1), np.float32)], axis=2)
        img.pixels.foreach_set(rgba.ravel())
        img.pack()
        return img
    return a_imagen("maisha_piel", np.clip(base, 0, 1)), a_imagen("maisha_tatuajes", np.clip(emis, 0, 1))


def guardar_mascara(mascara):
    os.makedirs(CARPETA, exist_ok=True)
    img = bpy.data.images.new("mascara_guardar", TAM, TAM, alpha=False)
    rgba = np.stack([mascara, mascara, mascara, np.ones_like(mascara)], axis=2)
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = MASCARA
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def materiales(img_piel, img_tatuajes):
    mats = {n: material(n, *v) for n, v in PALETA.items()}
    piel = mats["piel_humanizada"]
    nodos, enlaces = piel.node_tree.nodes, piel.node_tree.links
    bsdf = nodos.get("Principled BSDF")
    t_base = nodos.new("ShaderNodeTexImage")
    t_base.image = img_piel
    t_emis = nodos.new("ShaderNodeTexImage")
    t_emis.image = img_tatuajes
    enlaces.new(t_base.outputs["Color"], bsdf.inputs["Base Color"])
    enlaces.new(t_emis.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 1.5
    return mats


# ---------------------------------------------------------------------------
# Montaje
# ---------------------------------------------------------------------------

def montar():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mascara = dibujar_tatuajes()
    guardar_mascara(mascara)
    mats = materiales(*imagenes_tatuajes(mascara))

    cuerpo = Malla("Maisha_Cuerpo")
    torso(cuerpo)
    for lado in ("L", "R"):
        brazo(cuerpo, lado)
        mano(cuerpo, lado, cerrada=0.20 if lado == "L" else 1.0)
    corazon(cuerpo)
    cabeza(cuerpo)
    ob_cuerpo = a_objeto(cuerpo, mats)

    m_pelo = Malla("Maisha_Pelo")
    pelo(m_pelo)
    ob_pelo = a_objeto(m_pelo, mats)

    m_tunica = Malla("Maisha_Tunica")
    tunica(m_tunica)
    ob_tunica = a_objeto(m_tunica, mats, grosor=0.006)

    ropa = Malla("Maisha_Ropa")
    cinturon(ropa)
    piernas(ropa)
    ob_ropa = a_objeto(ropa, mats)

    m_capa = Malla("Maisha_Capa")
    capa(m_capa)
    ob_capa = a_objeto(m_capa, mats, grosor=0.008)

    agarre, eje = agarre_cetro()
    m_cetro = Malla("Cetro")
    cetro(m_cetro, agarre, eje)
    ob_cetro = a_objeto(m_cetro, mats)

    return {"cuerpo": ob_cuerpo, "pelo": ob_pelo, "tunica": ob_tunica, "ropa": ob_ropa, "capa": ob_capa,
            "cetro": ob_cetro, "agarre": agarre}


# ---------------------------------------------------------------------------
# Esqueleto (nombres de la ficha) y pesos
# ---------------------------------------------------------------------------

def huesos():
    """(nombre, cabeza, cola, padre) en la pose de reposo (pose A)."""
    lista = [
        ("root", (0, 0, 0), (0, 0, 0.12), None),
        ("hips", (0, 0, 0.90), (0, 0, 1.00), "root"),
        ("spine_01", (0, 0, 1.00), (0, 0, 1.10), "hips"),
        ("spine_02", (0, 0, 1.10), (0, 0, 1.22), "spine_01"),
        ("chest", (0, 0, 1.22), (0, 0, 1.40), "spine_02"),
        ("neck", (0, 0, 1.40), (0, -0.004, 1.48), "chest"),
        ("head", (0, -0.004, 1.48), (0, -0.004, 1.70), "neck"),
        ("jaw", (0, 0.0, 1.525), (0, -0.062, 1.488), "head"),
        ("eyes_look", (0, -0.040, 1.595), (0, -0.100, 1.595), "head"),
        ("hair_back_01", (0, 0.080, 1.585), (0, 0.105, 1.525), "head"),
        ("hair_back_02", (0, 0.105, 1.525), (0, 0.115, 1.455), "hair_back_01"),
        ("cloak_L_01", (-0.085, 0.080, 1.430), (-0.130, 0.150, 1.150), "chest"),
        ("cloak_L_02", (-0.130, 0.150, 1.150), (-0.150, 0.185, 0.870), "cloak_L_01"),
    ]
    for lado in ("L", "R"):
        s = -1 if lado == "L" else 1
        hombro, codo, muneca, d = puntos_brazo(lado)
        lista += [
            (f"shoulder_{lado}", (s * 0.020, 0.0, 1.390), tuple(hombro), "chest"),
            (f"arm_{lado}", tuple(hombro), tuple(codo), f"shoulder_{lado}"),
            (f"forearm_{lado}", tuple(codo), tuple(muneca), f"arm_{lado}"),
            (f"hand_{lado}", tuple(muneca), tuple(muneca + d * 0.10), f"forearm_{lado}"),
        ]
        cadera, rodilla, tobillo, punta = puntos_pierna(lado)
        lista += [
            (f"thigh_{lado}", tuple(cadera), tuple(rodilla), "hips"),
            (f"calf_{lado}", tuple(rodilla), tuple(tobillo), f"thigh_{lado}"),
            (f"foot_{lado}", tuple(tobillo), tuple(punta), f"calf_{lado}"),
        ]
    return lista


def crear_esqueleto():
    datos = bpy.data.armatures.new("Maisha_Esqueleto")
    arm = bpy.data.objects.new("Maisha", datos)
    bpy.context.collection.objects.link(arm)
    activar(arm)
    bpy.ops.object.mode_set(mode="EDIT")
    for nombre, cab, cola, padre in huesos():
        eb = datos.edit_bones.new(nombre)
        eb.head, eb.tail = Vector(cab), Vector(cola)
        eje = (eb.tail - eb.head).normalized()
        eb.align_roll(Vector((0, -1, 0)) if abs(eje.y) < 0.8 else Z)
        if padre:
            eb.parent = datos.edit_bones[padre]
            eb.use_connect = (eb.head - datos.edit_bones[padre].tail).length < 1e-4 and nombre != "hips"
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return arm


def _dist_segmento(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / (ab.length_squared or 1e-12)))
    return (p - (a + ab * t)).length


def pesar(ob, arm, permitidos, regla=None):
    """Pesos por cercanía a los huesos permitidos (se mezclan los dos más cercanos, suave en las articulaciones).
    regla(nombre_hueso, punto) -> factor (0 quita el hueso para ese punto)."""
    segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones if b.name in permitidos}
    grupos = {n: ob.vertex_groups.new(name=n) for n in segs}
    for v in ob.data.vertices:
        p = v.co
        cand = []
        for n, (a, b) in segs.items():
            f = regla(n, p) if regla else 1.0
            if f <= 0:
                continue
            d = _dist_segmento(p, a, b)
            cand.append((f / (d ** 4 + 1e-7), n))
        cand.sort(reverse=True)
        cand = cand[:2]
        total = sum(w for w, _ in cand) or 1.0
        for w, n in cand:
            grupos[n].add([v.index], w / total, "REPLACE")
    mod = ob.modifiers.new("Esqueleto", "ARMATURE")
    mod.object = arm
    ob.parent = arm


def rigging(partes, arm):
    cuerpo_ok = ["hips", "spine_01", "spine_02", "chest", "neck", "head", "jaw"] + \
                [f"{h}_{l}" for h in ("shoulder", "arm", "forearm", "hand") for l in "LR"]

    def regla_cuerpo(n, p):
        if n == "jaw":   # solo la barbilla y el labio de abajo
            return 1.0 if (p.z < CABEZA_C.z - 0.040 and p.z > 1.46 and p.y < CABEZA_C.y - 0.030) else 0.0
        if n == "head":
            return 1.0 if p.z > 1.44 else 0.0
        return 1.0

    pesar(partes["cuerpo"], arm, cuerpo_ok, regla_cuerpo)

    def regla_pelo(n, p):
        if n.startswith("hair_back"):
            return 1.0 if (p.z < 1.555 and p.y > 0.040) else 0.0
        return 1.0
    pesar(partes["pelo"], arm, ["head", "hair_back_01", "hair_back_02"], regla_pelo)

    def regla_tunica(n, p):
        if n.startswith("thigh"):
            return 0.55 if p.z < 0.86 else 0.0
        return 1.0
    pesar(partes["tunica"], arm, ["hips", "spine_01", "spine_02", "chest", "shoulder_L", "shoulder_R",
                                  "thigh_L", "thigh_R"], regla_tunica)

    def regla_ropa(n, p):
        if n.startswith("thigh") or n.startswith("calf") or n.startswith("foot"):
            return 1.0 if p.z < 0.93 else 0.0
        return 1.0
    pesar(partes["ropa"], arm, ["hips", "spine_01", "thigh_L", "thigh_R", "calf_L", "calf_R", "foot_L", "foot_R"],
          regla_ropa)
    pesar(partes["capa"], arm, ["chest", "neck", "shoulder_L", "cloak_L_01", "cloak_L_02"])

    # el cetro va en la mano derecha (en Godot queda como BoneAttachment3D de hand_R)
    cetro_ob = partes["cetro"]
    activar(cetro_ob)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    arm.data.bones.active = arm.data.bones["hand_R"]
    bpy.ops.object.parent_set(type="BONE", keep_transform=True)


# ---------------------------------------------------------------------------
# Animaciones (30 fps). Las rotaciones se dan sobre ejes del mundo en la pose de reposo:
#   X+ en una pierna o un brazo caído = hacia atrás (X- = hacia delante); X+ en la columna o la cabeza = inclinar
#   hacia delante; Z+ = girar hacia la derecha de Maisha; Y- baja el brazo izquierdo, Y+ el derecho.
# ---------------------------------------------------------------------------

EJES = {"X": X, "Y": Y, "Z": Z}
FPS = 30


class Animador:
    def __init__(self, arm, eje_cetro):
        self.arm = arm
        self.rest = {b.name: b.matrix_local.to_3x3() for b in arm.data.bones}
        mano = arm.data.bones["hand_R"].matrix_local.to_3x3()
        self.cetro_local = (mano.inverted() @ eje_cetro).normalized()
        arm.animation_data_create()

    def q(self, nombre, rotaciones):
        qw = Quaternion()
        for eje, grados in rotaciones:
            qw = Quaternion(EJES[eje], math.radians(grados)) @ qw
        R = self.rest[nombre]
        return (R.inverted() @ qw.to_matrix() @ R).to_quaternion()

    def nueva(self, nombre):
        act = bpy.data.actions.new(nombre)
        act.use_fake_user = True
        self.arm.animation_data.action = act
        for pb in self.arm.pose.bones:
            pb.rotation_quaternion = Quaternion()
            pb.location = Vector()
        return act

    def fotograma(self, f, pose, cadera=(0.0, 0.0, 0.0), cetro=None):
        """pose: {hueso: [(eje, grados), ...]}; cadera: desplazamiento (x, y, z) en el mundo;
        cetro: dirección del mundo a la que debe apuntar el cetro (None = dejarlo como vaya la mano)."""
        for pb in self.arm.pose.bones:
            pb.rotation_quaternion = self.q(pb.name, pose.get(pb.name, []))
            pb.location = Vector()
        hips = self.arm.pose.bones["hips"]
        hips.location = self.rest["hips"].inverted() @ Vector(cadera)
        if cetro is not None:
            bpy.context.view_layer.update()
            pb = self.arm.pose.bones["hand_R"]
            M = pb.matrix.copy()
            actual = (M.to_3x3() @ self.cetro_local).normalized()
            delta = actual.rotation_difference(Vector(cetro).normalized())
            nueva = Matrix.Translation(M.translation) @ (delta.to_matrix() @ M.to_3x3()).to_4x4()
            pb.matrix = nueva
            bpy.context.view_layer.update()
        for pb in self.arm.pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=f)
        hips.keyframe_insert("location", frame=f)

    def cerrar(self, nombre, ciclica):
        act = self.arm.animation_data.action
        for fc in _curvas(act):
            for k in fc.keyframe_points:
                k.interpolation = "BEZIER"
        pista = self.arm.animation_data.nla_tracks.new()
        pista.name = nombre
        pista.strips.new(nombre, int(act.frame_range[0]), act)
        pista.mute = True
        self.arm.animation_data.action = None


def _curvas(act):
    """Curvas de una acción (Blender 5 guarda las curvas en capas y ranuras)."""
    if hasattr(act, "fcurves") and len(getattr(act, "fcurves", [])):
        return list(act.fcurves)
    curvas = []
    for capa_ in getattr(act, "layers", []):
        for tira in capa_.strips:
            for bolsa in tira.channelbags:
                curvas.extend(bolsa.fcurves)
    return curvas


def pose_reposo(respira=0.0, balanceo=0.0):
    """Erguida, brazos caídos (el derecho con el cetro delante), mirada al frente."""
    return {
        "spine_01": [("X", 1.5 + 0.4 * respira)],
        "chest": [("X", -1.0 - 1.2 * respira)],
        "neck": [("X", 2.0)],
        "head": [("X", 2.0 + 0.6 * respira), ("Z", 1.5 * balanceo)],
        "shoulder_L": [("Y", -2.0 * respira)],
        "shoulder_R": [("Y", 2.0 * respira)],
        "arm_L": [("Y", -36.0), ("X", -4.0 + 1.5 * balanceo)],
        "forearm_L": [("X", -12.0)],
        "hand_L": [("Z", 6.0)],
        "arm_R": [("Y", 34.0), ("X", -14.0)],
        "forearm_R": [("X", -38.0)],
        "thigh_L": [("Y", 1.5)],
        "thigh_R": [("Y", -1.5)],
        "cloak_L_01": [("X", 2.0 + 1.5 * balanceo)],
        "cloak_L_02": [("X", 1.5 + 2.5 * balanceo)],
        "hair_back_01": [("X", 1.0 * balanceo)],
    }


CETRO_ARRIBA = (0.0, -0.10, 1.0)        # el cetro, casi vertical y un poco adelantado


def anim_reposo(an):
    an.nueva("reposo")
    n = 60
    for f in range(0, n + 1, 6):
        t = 2 * math.pi * f / n
        an.fotograma(f, pose_reposo(math.sin(t), math.sin(t + 0.8)), cadera=(0, 0, -0.004 * (1 - math.cos(t)) / 2),
                     cetro=CETRO_ARRIBA)
    an.cerrar("reposo", True)


def _paso(fase, amplitud):
    """Ángulos de una pierna en el ciclo de paso: muslo (+ = adelante), rodilla y pie."""
    muslo = amplitud * math.sin(fase)
    rodilla = 6 + amplitud * 1.55 * max(0.0, math.cos(fase)) ** 1.5 + 4 * max(0.0, -math.sin(fase))
    pie = muslo - rodilla * 0.85 + (8 if math.sin(fase) < -0.6 else 0)
    return muslo, rodilla, pie


def anim_andar(an, nombre, n, amplitud, inclinacion, brazos, bote, codo):
    an.nueva(nombre)
    for f in range(0, n + 1, 2):
        p = 2 * math.pi * f / n
        mL, rL, pL = _paso(p, amplitud)
        mR, rR, pR = _paso(p + math.pi, amplitud)
        giro = math.sin(p)
        pose = {
            "hips": [("Z", 5 * giro), ("Y", 2.0 * giro)],
            "spine_01": [("X", inclinacion * 0.4)],
            "spine_02": [("Z", -4 * giro), ("X", inclinacion * 0.3)],
            "chest": [("Z", -3 * giro), ("X", inclinacion * 0.3)],
            "neck": [("X", -inclinacion * 0.4)],
            "head": [("X", -inclinacion * 0.3 + 2), ("Z", 2 * giro)],
            "thigh_L": [("X", -mL)],
            "calf_L": [("X", rL)],
            "foot_L": [("X", -pL)],
            "thigh_R": [("X", -mR)],
            "calf_R": [("X", rR)],
            "foot_R": [("X", -pR)],
            "arm_L": [("Y", -38.0), ("X", brazos * mL * 0.9)],
            "forearm_L": [("X", -codo - 8 * max(0.0, -math.sin(p)))],
            "arm_R": [("Y", 34.0), ("X", -14.0 + brazos * mR * 0.35)],
            "forearm_R": [("X", -38.0 - codo * 0.4)],
            "cloak_L_01": [("X", 4 + inclinacion * 0.6 + 2 * math.sin(2 * p))],
            "cloak_L_02": [("X", 6 + inclinacion + 4 * math.sin(2 * p + 0.6))],
            "hair_back_01": [("X", 3 + 2 * math.sin(2 * p + 0.4))],
            "hair_back_02": [("X", 2 + 3 * math.sin(2 * p + 0.9))],
        }
        z = -bote * (1 - abs(math.cos(p)))
        an.fotograma(f, pose, cadera=(0.006 * giro, 0, z),
                     cetro=(0.0, -0.10 - inclinacion / 60, 1.0))
    an.cerrar(nombre, True)


def anim_golpe(an):
    """Barrido con el cetro: carga a la derecha, golpe cruzado con peso, seguimiento y vuelta a la guardia."""
    an.nueva("golpe_cetro")
    claves = [
        # (fotograma, giro del tronco, brazo der. (Y, X), codo der., brazo izq. (Y, X), codo izq., agachar)
        (0, 0, (34, -14), -38, (-36, -4), -12, 0),
        (8, 30, (5, -10), -70, (-20, -40), -75, 6),      # carga: tronco a la derecha, cetro atrás
        (12, 36, (-5, -15), -80, (-15, -50), -85, 8),
        (16, -30, (40, -60), -20, (-10, -65), -50, 10),   # golpe: cruza por delante con todo el peso
        (20, -42, (55, -45), -15, (-25, -40), -35, 12),
        (26, -30, (45, -30), -25, (-30, -20), -25, 8),    # seguimiento
        (36, 0, (34, -14), -38, (-36, -4), -12, 0),       # guardia
    ]
    for f, giro, (bY, bX), codo, (lY, lX), codo_l, agacha in claves:
        pose = {
            "hips": [("Z", giro * 0.35)],
            "spine_01": [("X", agacha * 0.3), ("Z", giro * 0.25)],
            "spine_02": [("Z", giro * 0.3), ("X", agacha * 0.3)],
            "chest": [("Z", giro * 0.3), ("X", agacha * 0.2)],
            "head": [("Z", -giro * 0.5), ("X", 4)],
            "arm_R": [("Y", bY), ("X", bX)],
            "forearm_R": [("X", codo)],
            "arm_L": [("Y", lY), ("X", lX)],
            "forearm_L": [("X", codo_l)],
            "thigh_L": [("X", -12 * agacha / 12), ("Y", 4)],
            "calf_L": [("X", 14 * agacha / 12)],
            "foot_L": [("X", -2)],
            "thigh_R": [("X", 10 * agacha / 12), ("Y", -4)],
            "calf_R": [("X", 10 * agacha / 12)],
            "cloak_L_01": [("X", 4), ("Z", -giro * 0.3)],
            "cloak_L_02": [("X", 6), ("Z", -giro * 0.4)],
        }
        an.fotograma(f, pose, cadera=(0, 0, -0.012 * agacha / 12))
    an.cerrar("golpe_cetro", False)


def anim_mirar_tatuajes(an):
    """Se detiene, alza el antebrazo izquierdo, baja la mirada y lo recorre como quien busca recordar."""
    an.nueva("idle_mirar_tatuajes")
    for f, k, traza in ((0, 0.0, 0), (18, 0.8, 0), (26, 1.0, 0), (40, 1.0, 1), (55, 1.0, -1), (70, 1.0, 0),
                        (78, 0.8, 0), (90, 0.0, 0)):
        pose = pose_reposo()
        pose.update({
            "arm_L": [("Y", -36 + 20 * k), ("X", -4 - 34 * k)],
            "forearm_L": [("X", -12 - 98 * k), ("Z", 30 * k)],
            "hand_L": [("Z", 6 - 30 * k)],
            "neck": [("X", 2 + 10 * k), ("Z", -8 * k)],
            "head": [("X", 2 + 14 * k + 2 * traza), ("Z", -10 * k + 3 * traza)],
            "arm_R": [("Y", 34 - 6 * k), ("X", -14 - 8 * k)],
            "forearm_R": [("X", -38 - 18 * k + 4 * traza)],
            "chest": [("X", -1 + 3 * k), ("Z", -4 * k)],
        })
        an.fotograma(f, pose, cetro=CETRO_ARRIBA)
    an.cerrar("idle_mirar_tatuajes", False)


def anim_eco(an):
    """Al tocar un Eco: el pecho se abre, la cabeza se alza y los brazos se separan un poco (el brillo lo pone el
    juego subiendo la emisión de los tatuajes)."""
    an.nueva("eco_despertar")
    for f, k in ((0, 0.0), (14, 0.7), (22, 1.0), (44, 1.0), (60, 0.0)):
        pose = pose_reposo()
        pose.update({
            "spine_02": [("X", -5 * k)],
            "chest": [("X", -1 - 11 * k)],
            "neck": [("X", 2 - 8 * k)],
            "head": [("X", 2 - 14 * k)],
            "arm_L": [("Y", -36 + 14 * k), ("X", -4 - 10 * k)],
            "forearm_L": [("X", -12 - 10 * k)],
            "hand_L": [("Z", 6 + 20 * k)],
            "arm_R": [("Y", 34 - 6 * k), ("X", -14 - 6 * k)],
            "cloak_L_01": [("X", 2 + 6 * k)],
            "cloak_L_02": [("X", 1.5 + 10 * k)],
            "hair_back_01": [("X", 4 * k)],
        })
        an.fotograma(f, pose, cadera=(0, 0, 0.006 * k), cetro=CETRO_ARRIBA)
    an.cerrar("eco_despertar", False)


def animar(arm, eje_cetro):
    bpy.context.scene.render.fps = FPS
    an = Animador(arm, eje_cetro)
    anim_reposo(an)
    anim_andar(an, "caminar_atento", 32, amplitud=24, inclinacion=4, brazos=1.0, bote=0.018, codo=14)
    anim_andar(an, "correr", 20, amplitud=38, inclinacion=14, brazos=1.5, bote=0.035, codo=60)
    anim_golpe(an)
    anim_mirar_tatuajes(an)
    anim_eco(an)
    return an


# ---------------------------------------------------------------------------
# Exportación
# ---------------------------------------------------------------------------

def exportar(arm, partes):
    os.makedirs(CARPETA, exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    for clave in ("cuerpo", "pelo", "tunica", "ropa", "capa", "cetro"):
        partes[clave].select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.gltf(filepath=SALIDA, export_format="GLB", use_selection=True, export_yup=True,
                              export_apply=False, export_skins=True, export_animations=True,
                              export_animation_mode="ACTIONS", export_def_bones=False)


def informe(arm, partes):
    print("\n=== MAISHA ===")
    total = 0
    for clave in ("cuerpo", "pelo", "tunica", "ropa", "capa", "cetro"):
        ob = partes[clave]
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        total += tris
        print(f"  {ob.name:15s} {tris:6d} triángulos  [{', '.join(m.name for m in ob.data.materials)}]")
    print(f"  Triángulos en total: {total}")
    print(f"  Huesos: {len(arm.data.bones)}  ({', '.join(b.name for b in arm.data.bones)})")
    acts = [a for a in bpy.data.actions if a.use_fake_user]
    print(f"  Animaciones: " + ", ".join(f"{a.name} ({int(a.frame_range[1] - a.frame_range[0])} f)" for a in acts))
    print(f"  Exportado a {SALIDA}")


# ---------------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------------

def vistas(carpeta, planos=None):
    os.makedirs(carpeta, exist_ok=True)
    esc = bpy.context.scene
    esc.render.engine = "BLENDER_EEVEE"
    esc.render.resolution_x, esc.render.resolution_y = 800, 1000
    mundo = bpy.data.worlds.new("Fondo")
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs["Color"].default_value = (0.36, 0.38, 0.40, 1)
    mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    esc.world = mundo
    for nombre, energia, rot in (("Clave", 3.2, (52, 0, -35)), ("Relleno", 1.0, (65, 0, 140))):
        luz = bpy.data.objects.new(nombre, bpy.data.lights.new(nombre, "SUN"))
        luz.data.energy = energia
        luz.data.angle = math.radians(6)
        luz.rotation_euler = tuple(math.radians(a) for a in rot)
        esc.collection.objects.link(luz)
    suelo = bpy.data.meshes.new("Suelo")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=3)
    bm.to_mesh(suelo)
    bm.free()
    ob_s = bpy.data.objects.new("Suelo", suelo)
    esc.collection.objects.link(ob_s)
    cam = bpy.data.objects.new("Camara", bpy.data.cameras.new("Camara"))
    esc.collection.objects.link(cam)
    esc.camera = cam
    planos = planos or {
        "1_frente": ((0.0, -4.6, 1.0), (0, 0, 0.88), 50),
        "2_perfil": ((4.6, 0.0, 1.0), (0, 0, 0.88), 50),
        "3_espalda": ((0.0, 4.6, 1.0), (0, 0, 0.88), 50),
        "4_tres_cuartos": ((-3.0, -3.6, 1.6), (0, 0, 0.88), 50),
        "5_cara": ((-0.22, -0.75, 1.62), (0, 0, 1.58), 70),
        "6_brazo": ((1.0, -0.9, 1.3), (0.38, 0, 1.08), 60),
    }
    def foto(nombre, pos, obj, lente):
        cam.data.lens = lente
        cam.location = pos
        cam.rotation_euler = (Vector(obj) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        esc.render.filepath = os.path.join(carpeta, f"maisha_{nombre}.png")
        bpy.ops.render.render(write_still=True)

    for nombre, (pos, obj, lente) in planos.items():
        foto(nombre, pos, obj, lente)
    return foto


def vistas_animadas(foto, arm):
    """Fotogramas sueltos de las animaciones, para revisarlas sin abrir Godot."""
    tomas = [
        ("reposo", 0, "a_reposo_frente", ((0.0, -4.6, 1.0), (0, 0, 0.88), 50)),
        ("reposo", 0, "b_reposo_tres_cuartos", ((-3.0, -3.6, 1.6), (0, 0, 0.88), 50)),
        ("caminar_atento", 8, "c_caminar_perfil", ((4.6, 0.0, 1.0), (0, 0, 0.88), 50)),
        ("correr", 5, "d_correr_perfil", ((4.6, 0.0, 1.0), (0, 0, 0.88), 50)),
        ("golpe_cetro", 8, "e_golpe_carga", ((-2.2, -4.0, 1.4), (0, 0, 0.95), 50)),
        ("golpe_cetro", 16, "f_golpe_impacto", ((-2.2, -4.0, 1.4), (0, 0, 0.95), 50)),
        ("idle_mirar_tatuajes", 40, "g_mirar_tatuajes", ((-1.4, -2.2, 1.5), (0, 0, 1.25), 55)),
        ("eco_despertar", 30, "h_eco_despertar", ((-2.4, -3.6, 1.4), (0, 0, 1.0), 50)),
    ]
    for accion, f, nombre, (pos, obj, lente) in tomas:
        arm.animation_data.action = bpy.data.actions[accion]
        bpy.context.scene.frame_set(f)
        foto(nombre, pos, obj, lente)
    arm.animation_data.action = None


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    partes = montar()
    arm = crear_esqueleto()
    rigging(partes, arm)
    _, eje = agarre_cetro()
    animar(arm, eje)
    exportar(arm, partes)
    informe(arm, partes)
    if "--vistas" in args:
        foto = vistas(args[args.index("--vistas") + 1])
        vistas_animadas(foto, arm)


if __name__ == "__main__":
    main()
