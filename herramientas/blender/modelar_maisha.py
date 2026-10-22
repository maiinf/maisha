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
        caras = []
        pares = range(n) if cerrado else range(n - 1)
        for i in pares:
            a, b = anillos[i], anillos[(i + 1) % n]
            for j in range(lados):
                j2 = (j + 1) % lados
                f = self.bm.faces.new((a[j], a[j2], b[j2], b[j]))
                caras.append(f)
                us = (j / lados, (j + 1) / lados, (j + 1) / lados, j / lados)
                vs = (i / (n - 1), i / (n - 1), (i + 1) / (n - 1), (i + 1) / (n - 1)) if not cerrado else \
                     (i / n, i / n, (i + 1) / n, (i + 1) / n)
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
CABEZA_C = Vector((0.0, 0.004, 1.586))       # centro de la cabeza
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
    (1.31, 0.160, 0.098, -0.004),
    (1.36, 0.166, 0.092, 0.000),
    (1.395, 0.150, 0.085, 0.004),
    (1.418, 0.105, 0.070, 0.006),
    (1.435, 0.060, 0.056, 0.000),
    (1.47, 0.052, 0.052, -0.006),
    (1.51, 0.048, 0.050, -0.006),
    (1.54, 0.042, 0.046, -0.004),
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
    inicio = hombro - (codo - hombro).normalized() * 0.03
    tramo = [(inicio, 0.050), (hombro, 0.050)]
    for k in range(1, 6):
        t = k / 6
        tramo.append((hombro.lerp(codo, t), 0.048 - 0.012 * t + 0.004 * math.sin(math.pi * t)))
    tramo.append((codo, 0.034))
    for k in range(1, 6):
        t = k / 6
        tramo.append((codo.lerp(muneca, t), 0.037 - 0.010 * t + 0.003 * math.sin(math.pi * t * 0.8)))
    tramo.append((muneca, 0.025))
    for c, r in tramo:
        centros.append(c)
        radios.append((r, r * 0.86))
    m.tubo(centros, radios, "piel_humanizada", Vector((0, -1, 0)), lados=16, tapas=(False, True), uv=UV_BRAZO[lado])


def mano(m, lado, cerrada=0.25):
    """Palma, cuatro dedos y pulgar. cerrada: 0 abierta, 1 puño (la derecha agarra el cetro)."""
    hombro, codo, muneca, d = puntos_brazo(lado)
    s = -1 if lado == "L" else 1
    ancho = Vector((0, -1, 0))                             # la palma se extiende de delante a atrás
    palma_n = d.cross(ancho).normalized() * (-s)           # la palma mira hacia el cuerpo
    if palma_n.x * s > 0:
        palma_n = -palma_n
    base = muneca + d * 0.008
    nudillos = muneca + d * 0.085
    m.tubo([base, muneca + d * 0.045, nudillos], [(0.026, 0.012), (0.032, 0.013), (0.031, 0.011)],
           "piel_humanizada", ancho, lados=12, uv=UV_LISO)
    for k, (off, largo) in enumerate(((-0.020, 0.068), (-0.007, 0.078), (0.007, 0.074), (0.020, 0.060))):
        p0 = nudillos + ancho * off
        pts = [p0]
        dir_ = d.copy()
        for f in range(3):
            ang = (0.25 + 0.85 * cerrada) * (0.6 + 0.4 * f)
            dir_ = (dir_ * math.cos(ang * 0.6) + palma_n * math.sin(ang * 0.6)).normalized()
            pts.append(pts[-1] + dir_ * largo / 3)
        r = 0.0085 - 0.0007 * abs(k - 1.5)
        m.tubo(pts, [(r, r), (r * 0.95, r * 0.95), (r * 0.88, r * 0.88), (r * 0.78, r * 0.78)],
               "piel_humanizada", palma_n, lados=8, uv=UV_LISO)
    p0 = muneca + d * 0.03 + ancho * (-0.024) + palma_n * 0.006
    dir_ = (d * 0.6 + ancho * (-0.6) + palma_n * (0.3 + 0.5 * cerrada)).normalized()
    pts = [p0, p0 + dir_ * 0.03]
    dir2 = (dir_ + palma_n * (0.4 + 0.6 * cerrada) + d * 0.3).normalized()
    pts.append(pts[-1] + dir2 * 0.03)
    m.tubo(pts, [(0.011, 0.010), (0.0095, 0.009), (0.0082, 0.0078)], "piel_humanizada", palma_n, lados=8,
           uv=UV_LISO)


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
    verts, caras = m.esfera((0, 0, 0), (1, 1, 1), "piel_humanizada", seg=(40, 30), uv=UV_LISO)
    labios = m.indice("labios")
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
        d += 0.018 * gauss(p.x, 0.10) * gauss(p.z + 0.08, 0.16) * max(0.0, -p.y) ** 4      # nariz
        d += 0.006 * gauss(p.x, 0.07) * gauss(p.z - 0.12, 0.14) * max(0.0, -p.y) ** 4      # puente
        d += 0.009 * gauss(p.x, 0.22) * gauss(p.z + 0.80, 0.14) * max(0.0, -p.y) ** 2      # barbilla
        d += 0.003 * gauss(p.x, 0.16) * gauss(p.z + 0.40, 0.035) * max(0.0, -p.y) ** 4     # labio sup.
        d += 0.004 * gauss(p.x, 0.15) * gauss(p.z + 0.50, 0.035) * max(0.0, -p.y) ** 4     # labio inf.
        d -= 0.002 * gauss(p.x, 0.18) * gauss(p.z + 0.45, 0.012) * max(0.0, -p.y) ** 4     # boca
        d += 0.004 * gauss(p.z - 0.30, 0.10) * max(0.0, -p.y) ** 3                          # cejas
        for sx in (-1, 1):
            d -= 0.009 * gauss(p.x - sx * 0.36, 0.13) * gauss(p.z - 0.10, 0.11) * max(0.0, -p.y) ** 2  # cuencas
            d += 0.004 * gauss(p.x - sx * 0.62, 0.17) * gauss(p.z + 0.12, 0.14) * max(0.0, -p.y)       # pómulos
        n = q.normalized()
        v.co = CABEZA_C + q + n * d
    # labios con su color
    for f in caras:
        c = f.calc_center_median() - CABEZA_C
        cz = c.z / CABEZA_R.z
        if c.y < -0.07 and abs(c.x) < 0.024 and -0.56 < cz < -0.36:
            f.material_index = labios
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
        mech = 1.0 + 0.045 * max(0.0, math.sin(az * 7 + p.z * 3)) * (0.5 + 0.5 * (1 - abs(p.z)))
        k = 1.085 * mech
        v.co = CABEZA_C + Vector((p.x * CABEZA_R.x * k, p.y * CABEZA_R.y * k, p.z * CABEZA_R.z * 1.06 * mech))
    bmesh.ops.delete(m.bm, geom=quitar, context="VERTS")
    # mechones que caen
    def mechon(dir_ini, caida, largo, grosor, lados_=8, curva=0.0):
        a = CABEZA_C + Vector((dir_ini.x * CABEZA_R.x, dir_ini.y * CABEZA_R.y, dir_ini.z * CABEZA_R.z)) * 1.04
        pts = [a]
        d = caida.normalized()
        for k in range(1, 6):
            t = k / 5
            p = a + caida * (largo * t) + Vector((0, 0, -largo * 0.25 * t * t)) + \
                Vector((dir_ini.x, dir_ini.y, 0)).normalized() * curva * math.sin(math.pi * t)
            pts.append(p)
        rad = [(grosor * (1 - 0.82 * k / 5) + 0.002, grosor * 0.55 * (1 - 0.8 * k / 5) + 0.0015) for k in range(6)]
        lat = Vector((dir_ini.x, dir_ini.y, 0)).normalized().cross(Z)
        m.tubo(pts, rad, "cabello_viajero", lat, lados=lados_)
    # flequillo ladeado y mechones laterales que enmarcan la cara
    mechon(Vector((-0.30, -0.80, 0.55)), Vector((0.35, -0.10, -0.55)), 0.11, 0.020)
    mechon(Vector((-0.05, -0.85, 0.55)), Vector((0.45, -0.12, -0.40)), 0.10, 0.018)
    mechon(Vector((0.25, -0.80, 0.55)), Vector((0.30, -0.10, -0.55)), 0.08, 0.016)
    for sx in (-1, 1):
        mechon(Vector((sx * 0.75, -0.45, 0.25)), Vector((sx * 0.06, -0.05, -1.0)), 0.13, 0.020, curva=0.004)
        mechon(Vector((sx * 0.85, -0.10, 0.20)), Vector((sx * 0.05, 0.08, -1.0)), 0.14, 0.022, curva=0.005)
    # detrás: mechones que bajan a la nuca y el recogido
    for k, ax in enumerate((-0.6, -0.3, 0.0, 0.3, 0.6)):
        mechon(Vector((ax, 0.75, 0.40)), Vector((-ax * 0.15, 0.25, -1.0)), 0.16, 0.024, curva=0.004)
    nuca = CABEZA_C + Vector((0, CABEZA_R.y * 0.95, -0.085))
    m.esfera(nuca, (0.034, 0.026, 0.030), "cabello_viajero", seg=(16, 12))
    m.tubo([nuca + Vector((0, -0.010, 0.028)), nuca + Vector((0, 0.004, 0.034)), nuca + Vector((0, 0.020, 0.028))],
           [(0.022, 0.006)] * 3, "cuero_cinturon", Z, lados=10, tapas=(False, False))
    mechon(Vector((0.0, 0.95, -0.80)), Vector((0.0, 0.25, -1.0)), 0.07, 0.020)


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
            holgura = 0.013
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
    # tirante sobre el hombro izquierdo hasta la espalda
    hombro = Vector((-HOMBRO + 0.06, 0.0, 1.405))
    m.tubo([Vector((-0.11, -0.085, 1.33)), hombro + Vector((0, -0.04, 0.012)), hombro + Vector((0, 0.04, 0.010)),
            Vector((-0.10, 0.085, 1.31))], [(0.032, 0.006)] * 4, "tunica_lino_arena", X, lados=8)


def capa(m):
    """Capa corta de viaje sobre el hombro izquierdo: cuelga por la espalda y el costado, con pliegues."""
    lados, filas = 30, 20
    a0, a1 = math.radians(55), math.radians(245)     # de la espalda-derecha al frente-izquierda (0 = +X)
    anillos = []
    for i in range(filas):
        s = i / (filas - 1)
        fila = []
        for j in range(lados):
            t = j / (lados - 1)
            fase = a0 + (a1 - a0) * t
            cx, cy = math.cos(fase), math.sin(fase)
            # arriba: sobre el hombro izquierdo, más baja hacia la espalda-derecha
            izq = suavizar(0.15, 0.62, t)
            arriba = 1.37 + 0.06 * izq - 0.02 * gauss(t - 0.95, 0.08)
            abajo = 0.97 - 0.06 * gauss(t - 0.30, 0.25) + 0.05 * suavizar(0.8, 1.0, t)
            z = arriba + (abajo - arriba) * s
            rx, ry, dy = radio_torso(min(z, 1.36))
            hueco = 0.035 + 0.06 * s + (0.03 if z > 1.30 and izq > 0.5 else 0.0)
            ondas = 1.0 + 0.05 * math.sin(fase * 10) * s
            r_x = (rx + hueco) * ondas
            r_y = (ry + hueco) * ondas
            if z > 1.36:      # sobre el hombro: se acerca al cuello
                k = suavizar(1.36, 1.43, z)
                r_x = r_x * (1 - k) + 0.085 * k
                r_y = r_y * (1 - k) + 0.075 * k
            fila.append(m.bm.verts.new(Vector((r_x * cx, dy + r_y * cy, z))))
        anillos.append(fila)
    caras = []
    for i in range(filas - 1):
        for j in range(lados - 1):
            caras.append(m.bm.faces.new((anillos[i][j], anillos[i][j + 1], anillos[i + 1][j + 1], anillos[i + 1][j])))
    m.poner_mat(caras, "capa_viaje_musgo")
    m.uv_fijo(caras, UV_LISO)
    # cuello vuelto de la capa
    pts = []
    for k in range(13):
        a = math.radians(-20 + 240 * k / 12)
        pts.append(Vector((0.078 * math.cos(a + math.pi / 2) * 1.05, 0.004 + 0.070 * math.sin(a + math.pi / 2),
                           1.425 - 0.02 * math.sin(math.radians(240 * k / 12)))))
    m.tubo(pts, [(0.018, 0.012)] * 13, "capa_viaje_musgo", Z, lados=10)


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

def cetro(m, agarre):
    """Construido vertical, con el agarre (la mano) en el punto dado."""
    abajo, arriba = agarre.z - 0.78, agarre.z + 0.97
    pts, rad = [], []
    n = 26
    for k in range(n):
        t = k / (n - 1)
        z = abajo + (arriba - 0.10 - abajo) * t
        dx = 0.006 * math.sin(t * 17) + 0.004 * math.sin(t * 41)
        dy = 0.006 * math.cos(t * 13)
        pts.append(Vector((agarre.x + dx, agarre.y + dy, z)))
        nudo = 0.004 * max(0.0, math.sin(t * 29)) ** 6
        rad.append((0.0175 - 0.004 * t + nudo, 0.0165 - 0.004 * t + nudo))
    m.tubo(pts, rad, "cetro_madera", X, lados=10)
    # espiral de la punta
    centro = Vector((agarre.x, agarre.y, arriba - 0.03))
    pts, rad = [], []
    vueltas = 1.25
    for k in range(30):
        t = k / 29
        a = 2 * math.pi * vueltas * t
        r = 0.040 * (1 - 0.35 * t)
        pts.append(centro + Vector((r * math.cos(a), r * math.sin(a), -0.075 + 0.13 * t)))
        rad.append((0.011 * (1 - 0.55 * t) + 0.002, 0.010 * (1 - 0.55 * t) + 0.002))
    m.tubo(pts, rad, "cetro_madera", Z, lados=8)
    m.esfera(centro + Vector((0, 0, 0.0)), (0.024, 0.024, 0.030), "semilla_esmeralda", seg=(16, 12))


# ---------------------------------------------------------------------------
# Tatuajes de la Memoria: textura de piel y máscara
# ---------------------------------------------------------------------------

TAM = 1024


class Lienzo:
    """Dibuja trazos en metros sobre una zona del atlas (cada zona sabe cuántos metros mide la superficie)."""
    def __init__(self):
        self.mascara = np.zeros((TAM, TAM), np.float32)

    def trazo(self, zona, puntos, grueso):
        (u0, v0, u1, v1), (wm, hm) = zona
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
        # zona del brazo: alrededor ~0,22 m, a lo largo 0,56 m (del hombro a la muñeca)
        zona = (UV_BRAZO[lado], (0.22, 0.56))
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
        mano(cuerpo, lado, cerrada=0.25 if lado == "L" else 0.85)
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

    hombro, codo, muneca, d = puntos_brazo("R")
    agarre = muneca + d * 0.055 + Vector((0, 0, 0)) + d.cross(Vector((0, -1, 0))).normalized() * 0.0
    m_cetro = Malla("Cetro")
    cetro(m_cetro, agarre)
    ob_cetro = a_objeto(m_cetro, mats)

    return {"cuerpo": ob_cuerpo, "pelo": ob_pelo, "tunica": ob_tunica, "ropa": ob_ropa, "capa": ob_capa,
            "cetro": ob_cetro, "agarre": agarre}


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
    for nombre, (pos, obj, lente) in planos.items():
        cam.data.lens = lente
        cam.location = pos
        cam.rotation_euler = (Vector(obj) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        esc.render.filepath = os.path.join(carpeta, f"maisha_{nombre}.png")
        bpy.ops.render.render(write_still=True)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    partes = montar()
    if "--vistas" in args:
        vistas(args[args.index("--vistas") + 1])


if __name__ == "__main__":
    main()
