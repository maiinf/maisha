# -*- coding: utf-8 -*-
"""
Casa Granja de Mzee Shamba: versión sólida 360° para el Maisha 3D.

Sigue la ficha de Gemini: documentacion/referencias_visuales_3d/construcciones/ref_casa_granja.md
(5,0 m de frente, 4,2 m de fondo, 4,8 m hasta la cumbrera; zócalo de piedra de río, troncos con las
esquinas cruzadas, tejado de tablillas a dos aguas, chimenea de caliza abierta y rueda de molino aparte).

Se lanza con Blender 5.2 sin ventana:
    blender -b --factory-startup -P herramientas/blender/modelar_casa_granja.py
    blender -b --factory-startup -P herramientas/blender/modelar_casa_granja.py -- --vistas <carpeta>
    blender -b --factory-startup -P herramientas/blender/modelar_casa_granja.py -- --ruina [--vistas <carpeta>]

Con --ruina sale modelos/entorno/casa_granja_ruina.glb (ficha ref_casa_granja_ruina.md): la misma casa con las
mismas medidas, pero apagada por la ceniza de Giza: tablones caídos del faldón izquierdo con las vigas negras al
aire, ceniza en las canales, chimenea fría tapada de telarañas, rueda atascada por un zarcillo petrificado (dos
paletas partidas), canaleta agrietada que solo gotea agua turbia, troncos con manchas de podredumbre, musgo seco,
ventanas y farol apagados (el farol con el cristal roto) y un escalón partido. Sin Marcador_Humo.

Sale modelos/entorno/casa_granja.glb con estos nodos:
    CasaGranja      la casa entera (estática)
    RuedaMolino     la rueda, con el pivote en el eje: gira con rotate_x en Godot
    AguaGranja      el agua de la canaleta, la cascada, la poza y el desagüe (para cambiarle el sombreador)
    Marcador_Humo   punto vacío en la boca de la chimenea, para las partículas de humo
Con --vistas, además, guarda cuatro vistas renderizadas en esa carpeta.

Medidas: 1 unidad = 1 metro. El frente mira a -Y en Blender (a +Z en Godot). Suelo en z = 0.
"""

import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SALIDA = os.path.join(RAIZ, "modelos", "entorno", "casa_granja.glb")
RUINA = False            # lo pone main() con --ruina

azar = random.Random(1907)
Z = Vector((0.0, 0.0, 1.0))

# ---------------------------------------------------------------------------
# Paleta (la de la ficha y unos pocos materiales de apoyo)
# ---------------------------------------------------------------------------

PALETA = {
    # nombre:          (color,     rugosidad, metal, emisión, alfa)
    "madera_troncos":  ("#855430", 0.75, 0.0, 0.0, 1.0),
    "madera_tejado":   ("#ab5e35", 0.80, 0.0, 0.0, 1.0),
    "piedra_zocalo":   ("#5e636b", 0.85, 0.0, 0.0, 1.0),
    "chimenea_caliza": ("#828894", 0.90, 0.0, 0.0, 1.0),
    "luz_ventana":     ("#ffcc33", 0.20, 0.0, 1.8, 1.0),
    "rueda_molino":    ("#4a301c", 0.70, 0.0, 0.0, 1.0),
    "agua_acequia":    ("#52a3c7", 0.05, 0.0, 0.0, 0.8),
    # de apoyo
    "madera_oscura":   ("#4f3220", 0.75, 0.0, 0.0, 1.0),  # marcos, vigas y banco
    "madera_puerta":   ("#6e4327", 0.75, 0.0, 0.0, 1.0),
    "madera_corte":    ("#c9955c", 0.80, 0.0, 0.0, 1.0),  # testas de los troncos y el letrero
    "mortero":         ("#8a7560", 0.95, 0.0, 0.0, 1.0),  # mortero de arcilla del zócalo
    "musgo":           ("#6b8a3a", 0.95, 0.0, 0.0, 1.0),
    "hierro":          ("#38383c", 0.45, 0.6, 0.0, 1.0),
    "hollin":          ("#2b2623", 0.95, 0.0, 0.0, 1.0),
    "barro":           ("#b8794a", 0.85, 0.0, 0.0, 1.0),
    "estera":          ("#9c7a4a", 0.95, 0.0, 0.0, 1.0),
    "grava":           ("#4a4a44", 0.95, 0.0, 0.0, 1.0),
    # solo para la ruina
    "madera_podrida":  ("#3a2e25", 0.95, 0.0, 0.0, 1.0),
    "ceniza":          ("#8c8a85", 0.98, 0.0, 0.0, 1.0),
    "telarana":        ("#c8c6c0", 0.90, 0.0, 0.0, 0.45),
    "zarcillo_petrificado": ("#2e2c2a", 0.95, 0.0, 0.0, 1.0),
}

# En la ruina, los mismos sitios con los materiales apagados de la ficha (nombre nuevo para que Godot los distinga)
PALETA_RUINA = {
    "madera_troncos":  ("madera_troncos_ceniza", "#5a483a", 0.90, 0.0, 0.0, 1.0),
    "madera_tejado":   ("madera_tejado_roto", "#6b4b38", 0.88, 0.0, 0.0, 1.0),
    "piedra_zocalo":   ("piedra_zocalo_seco", "#45484d", 0.92, 0.0, 0.0, 1.0),
    "luz_ventana":     ("ventana_apagada", "#282a2e", 0.60, 0.1, 0.0, 1.0),
    "rueda_molino":    ("rueda_atascada", "#35281e", 0.85, 0.0, 0.0, 1.0),
    "chimenea_caliza": ("chimenea_caliza_hollin", "#6c6f75", 0.92, 0.0, 0.0, 1.0),
    "madera_puerta":   ("madera_puerta_ceniza", "#4e3a2c", 0.88, 0.0, 0.0, 1.0),
    "madera_corte":    ("madera_corte_ceniza", "#8f7a62", 0.90, 0.0, 0.0, 1.0),
    "madera_oscura":   ("madera_oscura_ceniza", "#3d2e24", 0.88, 0.0, 0.0, 1.0),
    "musgo":           ("musgo_seco", "#6e6a48", 0.97, 0.0, 0.0, 1.0),
    "agua_acequia":    ("agua_turbia", "#4d4936", 0.15, 0.0, 0.0, 0.85),
}


def _lineal(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _rgba(hexa):
    h = hexa.lstrip("#")
    return tuple(_lineal(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4)) + (1.0,)


def crear_materiales():
    mats = {}
    for nombre, valores in PALETA.items():
        nombre_mat = nombre
        if RUINA and nombre in PALETA_RUINA:
            nombre_mat, *valores = PALETA_RUINA[nombre]
        hexa, rugosidad, metal, emision, alfa = valores
        m = bpy.data.materials.new(nombre_mat)
        if m.node_tree is None:
            m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        color = _rgba(hexa)
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = rugosidad
        bsdf.inputs["Metallic"].default_value = metal
        if emision > 0:
            bsdf.inputs["Emission Color"].default_value = color
            bsdf.inputs["Emission Strength"].default_value = emision
        if alfa < 1.0:
            bsdf.inputs["Alpha"].default_value = alfa
            if hasattr(m, "surface_render_method"):
                m.surface_render_method = "BLENDED"
        m.diffuse_color = color
        mats[nombre] = m
    return mats


# ---------------------------------------------------------------------------
# Constructor de mallas: muchas piezas en un solo bmesh, cada cara con su material
# ---------------------------------------------------------------------------

def base(t, arriba, n):
    """Matriz de giro cuyas columnas son t, arriba y n."""
    return Matrix((Vector(t), Vector(arriba), Vector(n))).transposed()


class Malla:
    def __init__(self, nombre):
        self.nombre = nombre
        self.bm = bmesh.new()
        self.bm.loops.layers.uv.new("UVMap")
        self.mats = []

    def _indice(self, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        return self.mats.index(mat)

    def _marcar(self, verts, mat):
        i = self._indice(mat)
        caras = {f for v in verts for f in v.link_faces}
        for f in caras:
            f.material_index = i
        return caras

    def caja(self, centro, tam, mat, giro=None):
        M = Matrix.Translation(Vector(centro))
        if giro is not None:
            M = M @ giro.to_4x4()
        M = M @ Matrix.Diagonal((tam[0], tam[1], tam[2], 1.0))
        r = bmesh.ops.create_cube(self.bm, size=1.0, matrix=M, calc_uvs=True)
        return self._marcar(r["verts"], mat)

    def cilindro(self, a, b, radio, mat, lados=12, radio2=None, mat_tapas=None):
        a, b = Vector(a), Vector(b)
        eje = b - a
        giro = Z.rotation_difference(eje.normalized()).to_matrix().to_4x4()
        M = Matrix.Translation((a + b) / 2) @ giro
        r = bmesh.ops.create_cone(self.bm, cap_ends=True, cap_tris=False, segments=lados,
                                  radius1=radio, radius2=radio2 if radio2 else radio,
                                  depth=eje.length, matrix=M, calc_uvs=True)
        caras = self._marcar(r["verts"], mat)
        if mat_tapas:
            i = self._indice(mat_tapas)
            d = eje.normalized()
            for f in caras:
                f.normal_update()
                if abs(f.normal.dot(d)) > 0.95:
                    f.material_index = i
        return caras

    @staticmethod
    def cortar_arriba(caras, altura):
        """Lleva los cuatro vértices de arriba de una caja a altura(x, y): tablas con el canto en pendiente."""
        verts = {v for f in caras for v in f.verts}
        medio = sum(v.co.z for v in verts) / len(verts)
        for v in verts:
            if v.co.z > medio:
                v.co.z = altura(v.co.x, v.co.y)

    def piedra(self, centro, tam, mat, giro=None, sub=1):
        M = Matrix.Translation(Vector(centro))
        if giro is not None:
            M = M @ giro.to_4x4()
        M = M @ Matrix.Diagonal((tam[0] / 2, tam[1] / 2, tam[2] / 2, 1.0))
        r = bmesh.ops.create_icosphere(self.bm, subdivisions=sub, radius=1.0, matrix=M, calc_uvs=True)
        return self._marcar(r["verts"], mat)


def a_objeto(malla, mats, bisel=0.012, segmentos=1, angulo_suave=35.0):
    me = bpy.data.meshes.new(malla.nombre)
    bmesh.ops.recalc_face_normals(malla.bm, faces=malla.bm.faces[:])
    malla.bm.to_mesh(me)
    malla.bm.free()
    for nombre in malla.mats:
        me.materials.append(mats[nombre])
    ob = bpy.data.objects.new(malla.nombre, me)
    bpy.context.collection.objects.link(ob)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    if bisel:
        mod = ob.modifiers.new("Bisel", "BEVEL")
        mod.width = bisel
        mod.segments = segmentos
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(50)
        mod.use_clamp_overlap = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angulo_suave))
    return ob


# ---------------------------------------------------------------------------
# Medidas generales
# ---------------------------------------------------------------------------

ZOCALO = 0.40            # altura del zócalo de piedra (suelo de la casa)
R_TRONCO = 0.13          # radio de los troncos de los muros
PASO_TRONCO = 0.24       # separación entre filas (se solapan: muro macizo)
SALIENTE = 0.20          # lo que sobresalen los troncos por las esquinas cruzadas
FILAS = 9

ANG = math.radians(39)   # pendiente del tejado principal
Z_CUMBRE = 4.58          # cara inferior del tejado en la cumbrera
ALERO = 0.45             # vuelo del tejado sobre los muros
GROSOR_TEJADO = 0.10

# Muros: n = hacia fuera, D = distancia del eje del muro al centro, mitad = media longitud, fase de filas
PAREDES = {
    "frente": {"n": Vector((0, -1, 0)), "D": 1.9, "mitad": 2.3, "fase": 0.0},
    "fondo":  {"n": Vector((0, 1, 0)),  "D": 1.9, "mitad": 2.3, "fase": 0.0},
    "izq":    {"n": Vector((-1, 0, 0)), "D": 2.3, "mitad": 1.9, "fase": 0.5},
    "der":    {"n": Vector((1, 0, 0)),  "D": 2.3, "mitad": 1.9, "fase": 0.5},
}


def tangente(n):
    return Z.cross(n)


def P(pared, a, z, d=0.0):
    """Punto en el muro: a a lo largo del muro, z altura, d hacia fuera desde el eje del muro."""
    n = pared["n"]
    return n * (pared["D"] + d) + tangente(n) * a + Z * z


def giro_pared(pared):
    n = pared["n"]
    return base(tangente(n), Z, n)


def filas(pared):
    return [ZOCALO + R_TRONCO + (i + pared["fase"]) * PASO_TRONCO for i in range(FILAS)]


def techo_bajo(x):
    """Altura de la cara inferior del tejado principal a una distancia x del eje."""
    return Z_CUMBRE - abs(x) * math.tan(ANG)


# Huecos de cada muro: (a0, a1, z0, z1, tipo). Las alturas se ajustan a las filas de troncos.
HUECOS = {
    "frente": [(-0.50, 0.30, 0.40, 2.15, "puerta"),
               (0.80, 1.60, 1.05, 1.85, "ventana"),
               (-1.85, -1.10, 1.05, 1.85, "ventana")],
    "fondo":  [(1.45, 2.00, 1.25, 1.80, "ventana")],
    "izq":    [(-1.30, -0.60, 1.10, 1.65, "ventana")],
    "der":    [(-0.70, 0.10, 1.10, 1.65, "ventana")],
}


def hueco_ajustado(pared, hueco):
    a0, a1, z0, z1, tipo = hueco
    cortadas = [zc for zc in filas(pared) if z0 <= zc <= z1]
    return a0, a1, min(cortadas) - PASO_TRONCO / 2, max(cortadas) + PASO_TRONCO / 2, tipo, cortadas


# ---------------------------------------------------------------------------
# Piezas de la casa
# ---------------------------------------------------------------------------

def zocalo(m):
    m.caja((0, 0, ZOCALO / 2), (4.9, 4.1, ZOCALO), "mortero")
    lados = [
        (Vector((0, -1, 0)), 2.05, 2.45),
        (Vector((0, 1, 0)), 2.05, 2.45),
        (Vector((-1, 0, 0)), 2.45, 2.05),
        (Vector((1, 0, 0)), 2.45, 2.05),
    ]
    for n, D, mitad in lados:
        t = tangente(n)
        for curso, zc in enumerate((0.11, 0.29)):
            a = -mitad + (0.0 if curso == 0 else 0.15)
            while a < mitad:
                largo = azar.uniform(0.24, 0.36)
                alto = azar.uniform(0.15, 0.20)
                ac = min(a + largo / 2, mitad - 0.08)
                giro = base(t, Z, n) @ Matrix.Rotation(azar.uniform(-0.15, 0.15), 3, "Z")
                centro = n * (D + azar.uniform(0.0, 0.03)) + t * ac + Z * (zc + azar.uniform(-0.01, 0.01))
                m.piedra(centro, (largo, alto, 0.2), "piedra_zocalo", giro)
                if azar.random() < 0.18:
                    m.piedra(centro + Z * (alto * 0.42) + n * 0.02, (largo * 0.5, 0.05, 0.12), "musgo", giro)
                a += largo * 0.92


def muros_de_troncos(m):
    for nombre, pared in PAREDES.items():
        n, t = pared["n"], tangente(pared["n"])
        extremo = pared["mitad"] + SALIENTE
        huecos = [hueco_ajustado(pared, h) for h in HUECOS.get(nombre, [])]
        for zc in filas(pared):
            tramos = [(-extremo, extremo)]
            for a0, a1, _, _, _, cortadas in huecos:
                if zc not in cortadas:
                    continue
                nuevos = []
                for s, e in tramos:
                    if a1 <= s or a0 >= e:
                        nuevos.append((s, e))
                        continue
                    if a0 > s:
                        nuevos.append((s, a0))
                    if a1 < e:
                        nuevos.append((a1, e))
                tramos = nuevos
            for s, e in tramos:
                if e - s < 0.1:
                    continue
                r = R_TRONCO * azar.uniform(0.93, 1.05)
                zz = zc + azar.uniform(-0.006, 0.006)
                pa = n * pared["D"] + t * s + Z * zz
                pb = n * pared["D"] + t * e + Z * zz
                m.cilindro(pa, pb, r, "madera_troncos", lados=12, radio2=r * azar.uniform(0.94, 1.0),
                           mat_tapas="madera_corte")
    # Núcleo interior: cierra cualquier rendija entre troncos y hace de pared por dentro de los huecos
    m.caja((0, 0, (ZOCALO + 2.72) / 2), (4.4, 3.6, 2.72 - ZOCALO), "madera_troncos")


def ventana(m, pared, a0, a1, z0, z1, alfeizar=True, marco=0.08):
    R = giro_pared(pared)
    w, h = a1 - a0, z1 - z0
    ac, zc = (a0 + a1) / 2, (z0 + z1) / 2
    m.caja(P(pared, ac, zc, -0.03), (w, h, 0.03), "luz_ventana", R)
    m.caja(P(pared, ac, zc, 0.0), (0.045, h, 0.04), "madera_oscura", R)
    m.caja(P(pared, ac, zc, 0.0), (w, 0.045, 0.04), "madera_oscura", R)
    fondo, dc = 0.24, 0.06
    m.caja(P(pared, a0 - marco / 2, zc, dc), (marco, h + 2 * marco, fondo), "madera_oscura", R)
    m.caja(P(pared, a1 + marco / 2, zc, dc), (marco, h + 2 * marco, fondo), "madera_oscura", R)
    m.caja(P(pared, ac, z1 + marco / 2, dc), (w + 2 * marco, marco, fondo), "madera_oscura", R)
    if alfeizar:
        m.caja(P(pared, ac, z0 - 0.04, dc + 0.04), (w + 2 * marco + 0.1, 0.08, fondo + 0.08), "madera_oscura", R)
    else:
        m.caja(P(pared, ac, z0 - marco / 2, dc), (w + 2 * marco, marco, fondo), "madera_oscura", R)


def puerta(m, pared, a0, a1, z0, z1, marco=0.09):
    R = giro_pared(pared)
    w, h = a1 - a0, z1 - z0
    ac, zc = (a0 + a1) / 2, (z0 + z1) / 2
    # Hoja de cuatro tablones
    ancho = w / 4
    for k in range(4):
        m.caja(P(pared, a0 + ancho * (k + 0.5), zc, -0.01), (ancho - 0.008, h, 0.06), "madera_puerta", R)
    # Travesaños y la tornapunta en diagonal
    for zt in (z0 + 0.25, z1 - 0.22):
        m.caja(P(pared, ac, zt, 0.035), (w - 0.06, 0.1, 0.03), "madera_puerta", R)
    pa, pb = (a0 + 0.1, z0 + 0.3), (a1 - 0.1, z1 - 0.32)
    largo = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
    ang = math.atan2(pb[1] - pa[1], pb[0] - pa[0])
    m.caja(P(pared, (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2, 0.035), (largo, 0.09, 0.03), "madera_puerta",
           R @ Matrix.Rotation(ang, 3, "Z"))
    # Ventanuco en rombo
    rombo = R @ Matrix.Rotation(math.pi / 4, 3, "Z")
    m.caja(P(pared, ac, z1 - 0.42, 0.0), (0.2, 0.2, 0.065), "madera_oscura", rombo)
    m.caja(P(pared, ac, z1 - 0.42, 0.012), (0.14, 0.14, 0.07), "luz_ventana", rombo)
    # Bisagras y tirador de hierro
    for zb in (z0 + 0.35, z1 - 0.35):
        m.caja(P(pared, a0 + 0.17, zb, 0.045), (0.3, 0.045, 0.012), "hierro", R)
    m.caja(P(pared, a1 - 0.13, zc - 0.1, 0.04), (0.05, 0.14, 0.015), "hierro", R)
    m.piedra(P(pared, a1 - 0.13, zc - 0.1, 0.07), (0.07, 0.07, 0.07), "hierro", R)
    # Marco y umbral
    fondo, dc = 0.26, 0.07
    m.caja(P(pared, a0 - marco / 2, zc, dc), (marco, h + marco, fondo), "madera_oscura", R)
    m.caja(P(pared, a1 + marco / 2, zc, dc), (marco, h + marco, fondo), "madera_oscura", R)
    m.caja(P(pared, ac, z1 + marco / 2, dc), (w + 2 * marco + 0.08, marco, fondo + 0.02), "madera_oscura", R)
    m.caja(P(pared, ac, z0 + 0.015, dc), (w + 2 * marco, 0.03, fondo), "madera_oscura", R)


def huecos_de_muros(m):
    for nombre, lista in HUECOS.items():
        pared = PAREDES[nombre]
        for h in lista:
            a0, a1, z0, z1, tipo, _ = hueco_ajustado(pared, h)
            if tipo == "puerta":
                puerta(m, pared, a0, a1, z0, z1)
            else:
                ventana(m, pared, a0, a1, z0, z1)


def letrero(cuerpo, centro, tam, material):
    cu = bpy.data.curves.new("Letrero", "FONT")
    cu.body = cuerpo
    cu.size = tam
    cu.extrude = 0.006
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.space_line = 1.05
    ob = bpy.data.objects.new("Letrero", cu)
    bpy.context.collection.objects.link(ob)
    ob.location = centro
    ob.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.convert(target="MESH")
    ob.data.materials.append(material)
    return ob


def hastiales(m):
    """Tablas verticales de los dos hastiales, el entramado, el letrero y la ventana del desván."""
    ventana_desvan = (-0.32, 0.32, 3.27, 3.80)
    for nombre in ("frente", "fondo"):
        pared = dict(PAREDES[nombre])
        R = giro_pared(pared)
        ancho = 0.23
        a = -2.3
        while a < 2.3 - 1e-6:
            a0, a1 = a, min(a + ancho, 2.3)
            cruza = a0 < -1e-6 and a1 > 1e-6
            arriba = Z_CUMBRE if cruza else techo_bajo(min(abs(a0), abs(a1)))
            tramos = [(2.55, arriba)]
            if nombre == "frente" and a1 > ventana_desvan[0] and a0 < ventana_desvan[1]:
                tramos = [(2.55, ventana_desvan[2]), (ventana_desvan[3], arriba)]
            for i, (z0, z1) in enumerate(tramos):
                caras = m.caja(P(pared, (a0 + a1) / 2, (z0 + z1) / 2, 0.06), (a1 - a0, z1 - z0, 0.06),
                               "madera_troncos", R)
                if i == len(tramos) - 1:
                    # El canto sigue la pendiente y se mete 3 cm en el tablero: sin esquinas que asomen
                    m.cortar_arriba(caras, (lambda x, y: Z_CUMBRE + 0.03) if cruza
                                    else (lambda x, y: techo_bajo(x) + 0.03))
            a += ancho
        # Entramado: tirante, dos pies derechos y sus jabalcones
        m.caja(P(pared, 0, 2.63, 0.12), (4.7, 0.14, 0.07), "madera_oscura", R)
        for lado in (-1, 1):
            xa = 1.05 * lado
            alto = techo_bajo(1.05) - 2.70
            m.caja(P(pared, xa, 2.70 + alto / 2, 0.12), (0.12, alto, 0.07), "madera_oscura", R)
            pa, pb = (1.75 * lado, 2.70), (1.11 * lado, 3.28)
            largo = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
            ang = math.atan2(pb[1] - pa[1], pb[0] - pa[0])
            m.caja(P(pared, (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2, 0.12), (largo, 0.1, 0.065), "madera_oscura",
                   R @ Matrix.Rotation(ang, 3, "Z"))
        if nombre == "frente":
            m.caja(P(pared, 0, 2.97, 0.13), (1.62, 0.40, 0.05), "madera_corte", R)
            for lado in (-1, 1):  # clavos del letrero
                for zc in (2.85, 3.09):
                    m.piedra(P(pared, 0.74 * lado, zc, 0.16), (0.03, 0.03, 0.02), "hierro", R)
            desvan = dict(pared)
            desvan["D"] = 1.96
            ventana(m, desvan, *ventana_desvan, alfeizar=True, marco=0.07)


def faldon(m, R0, u, eje, largo, ancho, grosor, paso=0.23, teja=(0.34, 0.27, 0.035), canecillos=(), hueco=None):
    """Un faldón: tablero macizo con tablillas escalonadas encima.
    R0 = punto alto (cara inferior) en el centro del faldón, u = dirección cuesta abajo, eje = a lo largo.
    hueco = (t0, t1, e0, e1): tramo sin tablas (cuesta abajo de t0 a t1, a lo largo del eje de e0 a e1),
    con los cabios negros al aire y astillas colgando."""
    u, eje = Vector(u).normalized(), Vector(eje).normalized()
    n = u.cross(eje)
    if n.z < 0:
        n = -n
    R = base(u, eje, n)
    if R.determinant() < 0:
        R = base(u, -eje, n)
    R0 = Vector(R0)
    if hueco:   # a lo largo del eje se mide con R.col[1], que puede ir al revés que eje
        signo = R.col[1].dot(eje)
        t0, t1 = hueco[0], hueco[1]
        h0, h1 = sorted((hueco[2] * signo, hueco[3] * signo))
        trozos = [(0.0, t0, -ancho / 2, ancho / 2), (t1, largo, -ancho / 2, ancho / 2),
                  (t0, t1, -ancho / 2, h0), (t0, t1, h1, ancho / 2)]
        for a0, a1, b0, b1 in trozos:
            m.caja(R0 + u * ((a0 + a1) / 2) + R.col[1] * ((b0 + b1) / 2) + n * (grosor / 2),
                   (a1 - a0, b1 - b0, grosor), "madera_tejado", R)
        e = h0 + 0.12
        while e < h1:      # cabios ennegrecidos que asoman
            m.caja(R0 + u * ((t0 + t1) / 2) + R.col[1] * e + n * (-0.05), (t1 - t0 + 0.3, 0.08, 0.1), "hollin", R)
            e += 0.4
        m.caja(R0 + u * ((t0 + t1) / 2) + R.col[1] * ((h0 + h1) / 2) + n * (-0.16),
               (0.1, h1 - h0 + 0.3, 0.1), "hollin", R)
        for k in range(3):  # tablas partidas que cuelgan del borde del hueco
            e = h0 + (h1 - h0) * (k + 0.5) / 3
            giro = R @ Matrix.Rotation(math.radians(-35 - 10 * k), 3, "Y")
            m.caja(R0 + u * (t0 + 0.12) + R.col[1] * e + n * (grosor - 0.08), (0.24, teja[1] * 0.8, teja[2]),
                   "madera_tejado", giro)
    else:
        m.caja(R0 + u * (largo / 2) + n * (grosor / 2), (largo, ancho, grosor), "madera_tejado", R)
    # Tablillas de abajo arriba, a matacán
    fila = 0
    tc = largo - teja[0] / 2 + 0.04
    while tc > 0.05:
        pos = -ancho / 2 - (teja[1] / 2 if fila % 2 else 0.0)
        while pos < ancho / 2:
            w = teja[1] * azar.uniform(0.85, 1.12)
            s, e = max(pos, -ancho / 2), min(pos + w, ancho / 2)
            if hueco and t0 - 0.1 < tc < t1 + 0.1 and h0 - 0.05 < (s + e) / 2 < h1 + 0.05:
                pos += w
                continue
            if e - s > 0.05:
                beta = math.radians(azar.uniform(5, 9))
                e1 = u * math.cos(beta) + n * math.sin(beta)
                e3 = -u * math.sin(beta) + n * math.cos(beta)
                giro = base(e1, R.col[1], e3) @ Matrix.Rotation(math.radians(azar.uniform(-0.8, 0.8)), 3, "Z")
                if giro.determinant() < 0:
                    giro = base(e1, -R.col[1], e3)
                centro = (R0 + u * tc + R.col[1] * ((s + e) / 2)
                          + n * (grosor + teja[2] / 2 + 0.006 + teja[0] / 2 * math.sin(beta) * 0.6))
                # Casi sin rendija: la junta la marca el bisel. Con rendija se veía el tablero por huecos.
                m.caja(centro, (teja[0], e - s - 0.002, teja[2] * azar.uniform(0.9, 1.15)), "madera_tejado", giro)
            pos += w
        tc -= paso
        fila += 1
    # Tablas de remate (alerones) en los extremos, cruzadas por arriba
    for off in canecillos:
        largo_t = largo + 0.32
        centro = R0 + u * (largo_t / 2 - 0.32) + n * (grosor / 2) + R.col[1] * off
        m.caja(centro, (largo_t, 0.07, 0.26), "madera_oscura", R)
    return n


def tejado(m):
    largo = (2.3 + ALERO) / math.cos(ANG)
    fondo = 2 * (1.9 + ALERO)
    for s in (-1, 1):
        u = (s * math.cos(ANG), 0, -math.sin(ANG))
        # En la ruina, el faldón izquierdo ha perdido tres hileras de tablas detrás de la buhardilla
        hueco = (0.95, 1.85, 0.35, 1.45) if RUINA and s < 0 else None
        n = faldon(m, (0, 0, Z_CUMBRE), u, (0, 1, 0), largo, fondo, GROSOR_TEJADO,
                   canecillos=(-fondo / 2 - 0.035, fondo / 2 + 0.035), hueco=hueco)
        # Tabla del alero a lo largo del borde bajo
        borde = Vector((0, 0, Z_CUMBRE)) + Vector(u) * largo
        m.caja(borde + Vector((s * 0.02, 0, -0.03)), (0.06, fondo + 0.1, 0.16), "madera_oscura")
        if RUINA:   # ceniza acumulada en la canal (junto al alero) y a manchas sobre las tablas
            giro = base(Vector(u), Vector((0, 1, 0)), n)
            if giro.determinant() < 0:
                giro = base(Vector(u), Vector((0, -1, 0)), n)
            yy = -fondo / 2 + 0.15
            while yy < fondo / 2 - 0.15:     # la canal: montoncitos sueltos, no una tira
                largo_c = azar.uniform(0.25, 0.6)
                m.piedra(Vector((0, 0, Z_CUMBRE)) + Vector(u) * (largo - azar.uniform(0.18, 0.3))
                         + Vector((0, yy + largo_c / 2, 0)) + n * (GROSOR_TEJADO + 0.06),
                         (azar.uniform(0.16, 0.3), largo_c, 0.028), "ceniza", giro, sub=2)
                yy += largo_c * azar.uniform(0.8, 1.6)
            for k in range(9):
                tt = azar.uniform(0.4, largo - 0.5)
                yy = azar.uniform(-fondo / 2 + 0.3, fondo / 2 - 0.3)
                if hueco and 0.8 < tt < 2.0 and 0.2 < yy < 1.6:
                    continue
                m.piedra(Vector((0, 0, Z_CUMBRE)) + Vector(u) * tt + Vector((0, yy, 0)) + n * (GROSOR_TEJADO + 0.07),
                         (azar.uniform(0.15, 0.35), azar.uniform(0.2, 0.5), 0.018), "ceniza",
                         giro @ Matrix.Rotation(azar.uniform(0, 3), 3, "Z"), sub=2)
    # Cumbrera
    z_top = Z_CUMBRE + GROSOR_TEJADO / math.cos(ANG)
    m.caja((0, 0, z_top + 0.03), (0.30, fondo + 0.14, 0.12), "madera_oscura")


def buhardilla(m):
    """Buhardilla en el faldón izquierdo, con su ventana mirando a -X."""
    y0, y1, yc = -1.1, -0.1, -0.6
    alero, ang = 3.95, math.radians(37)
    pico = alero + 0.5 * math.tan(ang)
    m.caja((-1.12, yc, 3.48), (1.12, 0.98, 0.95), "madera_troncos")  # núcleo
    frente = {"n": Vector((-1, 0, 0)), "D": 1.73, "mitad": 0.5, "fase": 0.0}
    R = giro_pared(frente)
    vent = (0.35, 0.85, 3.30, 3.74)  # a = -y
    a = -y1
    while a < -y0 - 1e-6:
        a0, a1 = a, min(a + 0.2, -y0)
        cruza = a0 < 0.6 - 1e-6 and a1 > 0.6 + 1e-6
        dist = 0.0 if cruza else min(abs(a0 - 0.6), abs(a1 - 0.6))
        arriba = alero + (0.5 - dist) * math.tan(ang)
        tramos = [(3.0, arriba)]
        if a1 > vent[0] and a0 < vent[1]:
            tramos = [(3.0, vent[2]), (vent[3], arriba)]
        for i, (z0, z1) in enumerate(tramos):
            caras = m.caja(P(frente, (a0 + a1) / 2, (z0 + z1) / 2, 0.0), (a1 - a0, z1 - z0, 0.05),
                           "madera_troncos", R)
            if i == len(tramos) - 1:
                m.cortar_arriba(caras, (lambda x, y: pico + 0.02) if cruza
                                else (lambda x, y: alero + (0.5 - abs(y - yc)) * math.tan(ang) + 0.02))
        a += 0.2
    ventana(m, frente, *vent, alfeizar=True, marco=0.06)
    # Troncos de los costados
    for y in (y0, y1):
        zc = 3.12
        while zc < alero - 0.02:
            m.cilindro((-1.80, y, zc), (-0.62, y, zc), 0.075, "madera_troncos", lados=10, mat_tapas="madera_corte")
            zc += 0.15
    # Tejadillo a dos aguas con la cumbrera a lo largo de X
    largo = 0.66 / math.cos(ang)
    for s in (-1, 1):
        u = (0, s * math.cos(ang), -math.sin(ang))
        faldon(m, (-1.29, yc, pico), u, (1, 0, 0), largo, 1.38, 0.08, paso=0.19, teja=(0.28, 0.22, 0.03),
               canecillos=(-0.72,) if s > 0 else (0.72,))
    m.caja((-1.29, yc, pico + 0.08 / math.cos(ang) + 0.03), (1.4, 0.2, 0.09), "madera_oscura")


def chimenea(m):
    cx, cy, lado, grueso = 1.05, 1.15, 0.70, 0.15
    z, alto = 3.2, 0.2
    curso = 0
    while z < 5.2 - 1e-6:
        zc = z + alto / 2
        largo_fb = lado if curso % 2 == 0 else lado - 2 * grueso
        largo_lt = lado - 2 * grueso if curso % 2 == 0 else lado
        for sy in (-1, 1):  # caras delantera y trasera
            for k in (-1, 1):
                m.caja((cx + k * largo_fb / 4, cy + sy * (lado - grueso) / 2 + azar.uniform(-0.006, 0.006), zc),
                       (largo_fb / 2 - 0.012, grueso, alto - 0.014), "chimenea_caliza",
                       Matrix.Rotation(azar.uniform(-0.03, 0.03), 3, "Z"))
        for sx in (-1, 1):  # costados
            for k in (-1, 1):
                m.caja((cx + sx * (lado - grueso) / 2 + azar.uniform(-0.006, 0.006), cy + k * largo_lt / 4, zc),
                       (grueso, largo_lt / 2 - 0.012, alto - 0.014), "chimenea_caliza",
                       Matrix.Rotation(azar.uniform(-0.03, 0.03), 3, "Z"))
        z += alto
        curso += 1
    # Forro de hollín por dentro y fondo oscuro (la boca queda abierta)
    interior = lado - 2 * grueso
    for sy in (-1, 1):
        m.caja((cx, cy + sy * (interior / 2 - 0.01), 4.6), (interior, 0.02, 1.4), "hollin")
    for sx in (-1, 1):
        m.caja((cx + sx * (interior / 2 - 0.01), cy, 4.6), (0.02, interior, 1.4), "hollin")
    m.caja((cx, cy, 4.9), (interior, interior, 0.02), "hollin")
    # Remate: corona algo más ancha
    for sy in (-1, 1):
        m.caja((cx, cy + sy * 0.3, 5.24), (0.82, 0.22, 0.08), "chimenea_caliza")
    for sx in (-1, 1):
        m.caja((cx + sx * 0.3, cy, 5.24), (0.22, 0.38, 0.08), "chimenea_caliza")
    if RUINA:   # boca tapada de telarañas sobre hollín cuarteado
        m.caja((cx, cy, 5.18), (interior + 0.02, interior + 0.02, 0.004), "telarana",
               Matrix.Rotation(math.radians(4), 3, "X"))
        for k in range(5):
            m.caja((cx + azar.uniform(-0.12, 0.12), cy + azar.uniform(-0.12, 0.12), 5.05),
                   (azar.uniform(0.1, 0.18), azar.uniform(0.08, 0.16), 0.03), "hollin",
                   Matrix.Rotation(azar.uniform(-0.3, 0.3), 3, "X") @ Matrix.Rotation(azar.uniform(0, 3), 3, "Z"))
        for k in range(4):  # hilos que bajan por la corona
            a = k * math.pi / 2 + 0.4
            m.caja((cx + 0.33 * math.cos(a), cy + 0.33 * math.sin(a), 5.1), (0.006, 0.006, 0.3), "telarana")
    return Vector((cx, cy, 5.32))


def porche(m):
    y0, y1 = -2.06, -3.0
    x0, x1 = -1.45, 1.65
    # Tablones del suelo
    y = y0
    while y > y1 + 0.05:
        ancho = 0.17
        m.caja(((x0 + x1) / 2 + azar.uniform(-0.02, 0.02), y - ancho / 2, ZOCALO - 0.005),
               (x1 - x0 + azar.uniform(-0.03, 0.03), ancho - 0.012, 0.05), "madera_troncos")
        y -= ancho
    # Faldón del porche y pilares de piedra
    m.caja(((x0 + x1) / 2, y1 + 0.04, 0.24), (x1 - x0, 0.08, 0.28), "madera_oscura")
    for x in (x0 + 0.04, x1 - 0.04):
        m.caja((x, (y0 + y1) / 2, 0.24), (0.08, abs(y1 - y0), 0.28), "madera_oscura")
    for x in (x0 + 0.1, x1 - 0.1):
        m.piedra((x, y1 + 0.12, 0.06), (0.32, 0.3, 0.16), "piedra_zocalo")
    # Escalones frente a la puerta
    for k, (zt, ya, yb) in enumerate(((0.27, -3.0, -3.32), (0.135, -3.32, -3.64))):
        m.caja((-0.1, (ya + yb) / 2, zt / 2), (1.3, abs(yb - ya), zt), "madera_oscura")
        if RUINA and k == 0:    # la tabla del escalón de arriba, partida y hundida por un lado
            m.caja((-0.45, (ya + yb) / 2 - 0.01, zt + 0.02), (0.62, abs(yb - ya) + 0.03, 0.04), "madera_troncos")
            m.caja((0.27, (ya + yb) / 2 - 0.01, zt - 0.01), (0.6, abs(yb - ya) + 0.03, 0.04), "madera_troncos",
                   Matrix.Rotation(math.radians(-9), 3, "Y"))
            continue
        m.caja((-0.1, (ya + yb) / 2 - 0.01, zt + 0.02), (1.36, abs(yb - ya) + 0.03, 0.04), "madera_troncos")
    # Estera
    m.caja((-0.1, -2.32, ZOCALO + 0.028), (0.62, 0.36, 0.016), "estera")
    # Banco junto a la pared
    bx0, bx1 = 0.78, 1.56
    m.caja(((bx0 + bx1) / 2, -2.33, ZOCALO + 0.44), (bx1 - bx0, 0.36, 0.05), "madera_oscura")
    for x in (bx0 + 0.05, bx1 - 0.05):
        for yy in (-2.18, -2.48):
            m.caja((x, yy, ZOCALO + 0.21), (0.06, 0.06, 0.42), "madera_oscura")
        m.caja((x, -2.2, ZOCALO + 0.7), (0.06, 0.06, 0.5), "madera_oscura")
    for zr in (ZOCALO + 0.72, ZOCALO + 0.88):
        m.caja(((bx0 + bx1) / 2, -2.17, zr), (bx1 - bx0, 0.04, 0.1), "madera_oscura")
    # Cántaro de barro
    m.piedra((-0.98, -2.36, ZOCALO + 0.2), (0.34, 0.34, 0.38), "barro", sub=2)
    m.cilindro((-0.98, -2.36, ZOCALO + 0.36), (-0.98, -2.36, ZOCALO + 0.47), 0.075, "barro", lados=14)
    m.cilindro((-0.98, -2.36, ZOCALO + 0.46), (-0.98, -2.36, ZOCALO + 0.5), 0.1, "barro", lados=14)
    # Farol de hierro entre la puerta y la ventana
    fx = 0.56
    m.caja((fx, -2.16, 2.18), (0.03, 0.28, 0.03), "hierro")
    m.caja((fx, -2.3, 2.12), (0.02, 0.02, 0.06), "hierro")
    m.caja((fx, -2.3, 2.07), (0.17, 0.17, 0.035), "hierro")
    if RUINA:   # cristal roto: quedan dos esquirlas en el marco y el resto en el suelo del porche
        m.caja((fx - 0.04, -2.3 - 0.055, 1.89), (0.05, 0.006, 0.09), "luz_ventana",
               Matrix.Rotation(math.radians(12), 3, "Y"))
        m.caja((fx + 0.055, -2.3, 2.0), (0.006, 0.07, 0.06), "luz_ventana")
        for k in range(4):
            m.caja((fx + azar.uniform(-0.25, 0.25), -2.4 + azar.uniform(-0.15, 0.15), ZOCALO + 0.024),
                   (azar.uniform(0.02, 0.05), azar.uniform(0.02, 0.04), 0.004), "luz_ventana",
                   Matrix.Rotation(azar.uniform(0, 3), 3, "Z"))
    else:
        m.caja((fx, -2.3, 1.94), (0.12, 0.12, 0.2), "luz_ventana")
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.caja((fx + sx * 0.065, -2.3 + sy * 0.065, 1.94), (0.018, 0.018, 0.22), "hierro")
    m.caja((fx, -2.3, 1.83), (0.15, 0.15, 0.025), "hierro")


def leñera(m):
    # Tarima, pies derechos y viga
    m.caja((0.35, 2.52, 0.04), (2.7, 0.84, 0.08), "madera_oscura")
    for x in (-1.0, 0.35, 1.7):
        m.caja((x, 3.0, 0.9), (0.1, 0.1, 1.8), "madera_oscura")
    m.caja((0.35, 3.0, 1.82), (2.9, 0.12, 0.1), "madera_oscura")
    ang = math.radians(25)
    faldon(m, (0.35, 2.02, 2.25), (0, math.cos(ang), -math.sin(ang)), (1, 0, 0), 1.32, 3.0, 0.07,
           paso=0.21, teja=(0.3, 0.25, 0.03))
    # Leña apilada, con las testas hacia atrás
    for capa in range(6):
        zc = 0.08 + 0.075 + capa * 0.13
        x = -0.85 + (0.075 if capa % 2 else 0.0) + capa * 0.04
        while x < 1.55 - capa * 0.04:
            r = 0.075 * azar.uniform(0.85, 1.1)
            y0 = 2.14 + azar.uniform(0, 0.05)
            y1 = 2.88 - azar.uniform(0, 0.05)
            m.cilindro((x, y0, zc), (x, y1, zc), r, "madera_troncos", lados=9, mat_tapas="madera_corte")
            x += 0.155
    # Tajo con un hacha clavada
    m.cilindro((2.15, 2.65, 0.0), (2.15, 2.65, 0.45), 0.22, "madera_troncos", lados=14, mat_tapas="madera_corte")
    m.cilindro((2.12, 2.6, 0.43), (2.4, 2.88, 0.92), 0.022, "madera_corte", lados=8)
    m.caja((2.1, 2.58, 0.47), (0.16, 0.04, 0.1), "hierro", Matrix.Rotation(math.radians(45), 3, "Z"))


def canaleta_y_poza(m):
    """Canaleta sobre caballetes, cojinetes de la rueda, poza de piedra y desagüe (la estructura; el agua aparte)."""
    xc = -2.92
    z_fondo = 1.88
    if RUINA:   # la canaleta se ha partido en y = 1,5: el tramo de delante cede un poco
        for (y0, y1, giro) in ((1.52, 2.76, 0.0), (-0.64, 1.48, math.radians(-2.5))):
            G = Matrix.Rotation(giro, 3, "X")
            yc = (y0 + y1) / 2
            m.caja((xc, yc, z_fondo - (1.5 - yc) * math.sin(giro)), (0.4, y1 - y0, 0.04), "rueda_molino", G)
            for sx in (-1, 1):
                m.caja((xc + sx * 0.18, yc, z_fondo + 0.1 - (1.5 - yc) * math.sin(giro)), (0.04, y1 - y0, 0.2),
                       "rueda_molino", G)
    else:
        m.caja((xc, 1.06, z_fondo), (0.4, 3.4, 0.04), "rueda_molino")
        for sx in (-1, 1):
            m.caja((xc + sx * 0.18, 1.06, z_fondo + 0.1), (0.04, 3.4, 0.2), "rueda_molino")
    for yy in (2.4, 0.95):
        for sx in (-1, 1):
            m.caja((xc + sx * 0.26, yy, z_fondo / 2), (0.1, 0.1, z_fondo), "rueda_molino")
            m.piedra((xc + sx * 0.26, yy, 0.03), (0.22, 0.22, 0.12), "piedra_zocalo")
        m.caja((xc, yy, z_fondo - 0.06), (0.66, 0.1, 0.08), "rueda_molino")
        largo = math.hypot(0.52, 1.0)
        m.caja((xc, yy, 0.95), (largo, 0.06, 0.06), "rueda_molino",
               Matrix.Rotation(math.atan2(1.0, 0.52), 3, "Y"))
    # Cojinete en el muro y poste de fuera con su cojinete
    m.caja((-2.48, -0.55, 0.98), (0.1, 0.3, 0.3), "madera_oscura")
    m.cilindro((-2.55, -0.55, 0.98), (-2.53, -0.55, 0.98), 0.09, "hierro", lados=14)
    m.caja((-3.29, -0.55, 0.62), (0.12, 0.18, 0.86), "madera_oscura")
    m.caja((-3.29, -0.55, 1.0), (0.14, 0.22, 0.12), "madera_oscura")
    # Poza: fondo de grava y piedras alrededor
    m.caja((-2.9, -0.55, -0.02), (0.9, 2.05, 0.04), "grava")
    for x in [-3.38 + i * 0.22 for i in range(5)]:
        for y in (-1.6, 0.5):
            m.piedra((x, y + azar.uniform(-0.03, 0.03), 0.12), (0.26, 0.22, 0.24), "piedra_zocalo",
                     Matrix.Rotation(azar.uniform(0, 3), 3, "Z"))
    y = -1.5
    while y < 0.45:
        m.piedra((-3.42, y, 0.12), (0.22, 0.26, 0.24), "piedra_zocalo", Matrix.Rotation(azar.uniform(0, 3), 3, "Z"))
        y += 0.22
    # Desagüe hacia delante
    m.caja((-2.95, -2.1, -0.02), (0.42, 1.0, 0.04), "grava")
    y = -1.72
    while y > -2.62:
        for x in (-3.24, -2.66):
            m.piedra((x, y, 0.08), (0.2, 0.22, 0.17), "piedra_zocalo", Matrix.Rotation(azar.uniform(0, 3), 3, "Z"))
        y -= 0.2


def agua(m):
    xc = -2.92
    if RUINA:   # apenas un hilo turbio: lámina fina en la canaleta, goteo por la grieta y la poza baja
        m.caja((xc, 2.1, 1.91), (0.3, 1.2, 0.015), "agua_acequia")
        m.caja((xc, 1.5, 0.95), (0.025, 0.025, 1.9), "agua_acequia")
        m.caja((xc, 1.5, 0.01), (0.35, 0.3, 0.01), "agua_acequia")
        m.caja((-2.9, -0.55, 0.04), (0.86, 2.0, 0.07), "agua_acequia")
        return
    m.caja((xc, 1.06, 1.94), (0.32, 3.4, 0.08), "agua_acequia")
    # Cascada sobre los cangilones de delante de la rueda
    m.caja((xc, -0.7, 1.86), (0.3, 0.26, 0.03), "agua_acequia", Matrix.Rotation(math.radians(55), 3, "X"))
    m.caja((xc, -0.8, 1.63), (0.28, 0.03, 0.34), "agua_acequia")
    # Poza y desagüe
    m.caja((-2.9, -0.55, 0.11), (0.86, 2.0, 0.22), "agua_acequia")
    m.caja((-2.95, -2.1, 0.05), (0.38, 1.0, 0.1), "agua_acequia")


def rueda(m):
    """Rueda de 1,6 m de diámetro, construida alrededor de su eje (X) en el origen."""
    radio, segmentos = 0.8, 20
    for x in (-0.17, 0.17):
        for i in range(segmentos):
            th = 2 * math.pi * i / segmentos
            R = Matrix.Rotation(th, 3, "X")
            cuerda = 2 * (radio - 0.045) * math.sin(math.pi / segmentos) * 1.04
            m.caja(R @ Vector((x, 0, radio - 0.045)), (0.06, cuerda, 0.09), "rueda_molino", R)
        for i in range(8):
            th = 2 * math.pi * (i + 0.5) / 8
            R = Matrix.Rotation(th, 3, "X")
            m.caja(R @ Vector((x, 0, 0.42)), (0.06, 0.06, 0.6), "rueda_molino", R)
    for i in range(16):
        th = 2 * math.pi * i / 16
        R = Matrix.Rotation(th, 3, "X") @ Matrix.Rotation(0.35, 3, "X")
        if RUINA and i in (5, 6):   # partidas por el zarcillo: queda medio cangilón astillado
            m.caja(Matrix.Rotation(th, 3, "X") @ Vector((0.08, 0, 0.66)), (0.17, 0.04, 0.12), "rueda_molino",
                   R @ Matrix.Rotation(math.radians(18), 3, "Y"))
            continue
        m.caja(Matrix.Rotation(th, 3, "X") @ Vector((0, 0, 0.69)), (0.34, 0.04, 0.2), "rueda_molino", R)
    m.cilindro((-0.23, 0, 0), (0.23, 0, 0), 0.15, "rueda_molino", lados=16)
    for x in (-0.2, 0.2):
        m.cilindro((x - 0.015, 0, 0), (x + 0.015, 0, 0), 0.16, "hierro", lados=16)
    m.cilindro((-0.36, 0, 0), (0.5, 0, 0), 0.055, "hierro", lados=12)


# ---------------------------------------------------------------------------
# Montaje, exportación y vistas
# ---------------------------------------------------------------------------

def ruina_extra(m):
    """Zarcillo petrificado que sale del suelo, se mete entre los radios y atasca la rueda; tablones caídos."""
    pts = [Vector(p) for p in ((-3.55, -0.05, -0.05), (-3.35, -0.35, 0.35), (-3.05, -0.62, 0.62),
                               (-2.9, -0.70, 0.95), (-2.78, -0.62, 1.35), (-2.62, -0.45, 1.62),
                               (-2.5, -0.25, 1.78))]
    for i in range(len(pts) - 1):
        r0, r1 = 0.11 * (1 - i / 7) + 0.02, 0.11 * (1 - (i + 1) / 7) + 0.02
        m.cilindro(pts[i], pts[i + 1], r0, "zarcillo_petrificado", lados=9, radio2=r1)
        m.piedra(pts[i + 1], (r1 * 2.1, r1 * 2.1, r1 * 2.1), "zarcillo_petrificado")
        d = (pts[i + 1] - pts[i]).normalized()
        lado = d.cross(Z).normalized()
        for s in (-1, 1):   # espinas
            base_ = pts[i] + d * 0.12 + lado * s * r0
            m.cilindro(base_, base_ + (lado * s + d * 0.4).normalized() * 0.12, r0 * 0.35, "zarcillo_petrificado",
                       lados=5, radio2=0.004)
    # tres tablones del tejado caídos delante del porche, a la izquierda de los escalones
    for k, (x, y, giro, incl) in enumerate(((-1.55, -3.35, 20, 0), (-1.75, -3.55, -12, 0), (-1.3, -3.0, 70, 14))):
        G = Matrix.Rotation(math.radians(giro), 3, "Z") @ Matrix.Rotation(math.radians(incl), 3, "Y")
        m.caja((x, y, 0.03 + 0.1 * (incl > 0) + 0.04 * k), (0.62 - 0.12 * k, 0.26, 0.035), "madera_tejado", G)


def manchas_de_podredumbre(malla):
    """Manchas de humedad podrida en los troncos, más abajo que arriba (en la ruina)."""
    if "madera_troncos" not in malla.mats:
        return
    i_t = malla.mats.index("madera_troncos")
    i_p = malla._indice("madera_podrida")
    for f in malla.bm.faces:
        if f.material_index != i_t:
            continue
        c = f.calc_center_median()
        mancha = noise.noise(c * 1.3) + 0.4 * noise.noise(c * 4.0) - c.z * 0.12
        if mancha > 0.12:
            f.material_index = i_p


def limpiar_escena():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def montar():
    mats = crear_materiales()

    casa = Malla("CasaGranja")
    zocalo(casa)
    muros_de_troncos(casa)
    huecos_de_muros(casa)
    hastiales(casa)
    tejado(casa)
    buhardilla(casa)
    boca = chimenea(casa)
    porche(casa)
    leñera(casa)
    canaleta_y_poza(casa)
    if RUINA:
        ruina_extra(casa)
        manchas_de_podredumbre(casa)
    ob_casa = a_objeto(casa, mats)

    texto = letrero("CASA GRANJA DE\nMZEE SHAMBA", (0, -2.061, 2.97), 0.13, mats["madera_oscura"])
    bpy.ops.object.select_all(action="DESELECT")
    texto.select_set(True)
    ob_casa.select_set(True)
    bpy.context.view_layer.objects.active = ob_casa
    bpy.ops.object.join()

    m_rueda = Malla("RuedaMolino")
    rueda(m_rueda)
    ob_rueda = a_objeto(m_rueda, mats, bisel=0.01)
    ob_rueda.location = (-2.92, -0.55, 0.98)

    m_agua = Malla("AguaGranja")
    agua(m_agua)
    ob_agua = a_objeto(m_agua, mats, bisel=0.0, angulo_suave=30.0)

    humo = bpy.data.objects.new("Marcador_Humo", None)
    humo.empty_display_type = "SPHERE"
    humo.empty_display_size = 0.15
    humo.location = boca
    bpy.context.collection.objects.link(humo)

    if RUINA:   # chimenea fría: sin punto de humo
        bpy.data.objects.remove(humo)
        return [ob_casa, ob_rueda, ob_agua]
    return [ob_casa, ob_rueda, ob_agua, humo]


def exportar(objetos):
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objetos:
        ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=SALIDA, export_format="GLB", use_selection=True,
                              export_apply=True, export_yup=True)


def informe(objetos):
    print("\n=== CASA GRANJA ===")
    minimo = Vector((1e9, 1e9, 1e9))
    maximo = -minimo
    total = 0
    for ob in objetos:
        if ob.type != "MESH":
            print(f"  {ob.name:14s} vacío en {tuple(round(c, 2) for c in ob.location)}")
            continue
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        total += tris
        for v in ob.bound_box:
            w = ob.matrix_world @ Vector(v)
            minimo = Vector(map(min, minimo, w))
            maximo = Vector(map(max, maximo, w))
        print(f"  {ob.name:14s} {tris:7d} triángulos, materiales: {', '.join(m.name for m in ob.data.materials)}")
    casa = objetos[0]
    caja = [casa.matrix_world @ Vector(v) for v in casa.bound_box]
    print(f"  Triángulos en total: {total}")
    print(f"  Caja de todo: {tuple(round(c, 2) for c in minimo)} -> {tuple(round(c, 2) for c in maximo)}")
    print(f"  Cumbrera (sin chimenea): {Z_CUMBRE + GROSOR_TEJADO / math.cos(ANG) + 0.09:.2f} m")
    print(f"  Exportado a {SALIDA}")


def vistas(carpeta):
    os.makedirs(carpeta, exist_ok=True)
    escena = bpy.context.scene
    for motor in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES"):
        try:
            escena.render.engine = motor
            break
        except TypeError:
            continue
    if escena.render.engine == "CYCLES":
        escena.cycles.samples = 48
    escena.render.resolution_x, escena.render.resolution_y = 1000, 750
    mundo = bpy.data.worlds.new("Cielo")
    mundo.use_nodes = True
    fondo = mundo.node_tree.nodes["Background"]
    fondo.inputs["Color"].default_value = (0.55, 0.72, 0.9, 1.0)
    fondo.inputs["Strength"].default_value = 0.9
    escena.world = mundo
    sol = bpy.data.objects.new("Sol", bpy.data.lights.new("Sol", "SUN"))
    sol.data.energy = 3.5
    sol.data.angle = math.radians(8)
    sol.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
    escena.collection.objects.link(sol)
    suelo = bpy.data.meshes.new("Suelo")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=12)
    bm.to_mesh(suelo)
    bm.free()
    m_suelo = bpy.data.materials.new("Hierba")
    m_suelo.diffuse_color = _rgba("#6f9a45")
    if m_suelo.node_tree is None:
        m_suelo.use_nodes = True
    m_suelo.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = _rgba("#6f9a45")
    suelo.materials.append(m_suelo)
    ob_suelo = bpy.data.objects.new("Suelo", suelo)
    ob_suelo.location.z = -0.001
    escena.collection.objects.link(ob_suelo)
    cam = bpy.data.objects.new("Camara", bpy.data.cameras.new("Camara"))
    cam.data.lens = 40
    escena.collection.objects.link(cam)
    escena.camera = cam
    objetivo = Vector((-0.3, -0.3, 1.9))
    planos = {
        "1_frente_izquierda": (-8.5, -9.5, 6.2),
        "2_fondo_derecha": (8.5, 9.5, 6.0),
        "3_lateral_rueda": (-11.0, -1.5, 3.2),
        "4_frente_derecha": (9.0, -9.0, 5.2),
        "5_tejado_cerca": (-4.5, -5.0, 6.6),
        "6_lenera_cerca": (3.2, 6.6, 2.4),
    }
    cerca = {"5_tejado_cerca": Vector((-1.2, -0.6, 3.6)), "6_lenera_cerca": Vector((0.4, 2.4, 1.0))}
    for nombre, pos in planos.items():
        objetivo = cerca.get(nombre, Vector((-0.3, -0.3, 1.9)))
        cam.location = pos
        cam.rotation_euler = (objetivo - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        escena.render.filepath = os.path.join(carpeta, f"casa_granja{'_ruina' if RUINA else ''}_{nombre}.png")
        bpy.ops.render.render(write_still=True)
        print(f"  Vista: {escena.render.filepath}")


def main():
    global RUINA, SALIDA
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--ruina" in args:
        RUINA = True
        SALIDA = SALIDA.replace("casa_granja.glb", "casa_granja_ruina.glb")
    limpiar_escena()
    objetos = montar()
    exportar(objetos)
    informe(objetos)
    if "--vistas" in args:
        vistas(args[args.index("--vistas") + 1])


if __name__ == "__main__":
    main()
