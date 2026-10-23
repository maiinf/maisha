# -*- coding: utf-8 -*-
"""
Mzee Shamba en 3D: el patriarca castor, bípedo, sabio y culto (1,45 m).

Referencias (documentacion/referencias_visuales_3d/CONTRATO_KITOVU.md):
  - imagen canónica personajes/mzee_shamba_castor_mitico_concept_art.jpg: cuerpo de castor en pera, pelaje
    plateado y gastado, ojos dorados, manos y pies con garras, cola de pizarra que arrastra, herramienta;
  - requisitos de Iam: gafas redondas de latón sobre el hocico, chaleco de pana ocre y camisa crema
    arremangada (en vez de las hombreras de musgo de la imagen), sombrero de paja, incisivos de ámbar,
    barba con espigas y bastón de roble con azadilla.

Se construye sobre la malla base profesional de Blender Studio (GEO-body_male_stylized, CC0) transformada en
castor, como pide el contrato (nada de cuerpos hechos con cilindros).

    blender -b --factory-startup -P herramientas/blender/modelar_mzee_shamba.py [-- --vistas <carpeta>]

Sale modelos/personajes/mzee_shamba.glb: esqueleto de la ficha (con jaw, beard_root, hat_bone, whiskers y la
cola), el bastón anclado a hand_R, el cuenco de sopa anclado a hand_L (escala 0 salvo en ofrecer_cuenco) y
4 animaciones: idle_labranza, hablar_afable, cavar_tierra, ofrecer_cuenco.
"""

import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aparejo as ap  # noqa: E402
from aparejo import X, Y, Z  # noqa: E402

SALIDA = os.path.join(ap.RAIZ, "modelos", "personajes", "mzee_shamba.glb")

PALETA = {
    "pelaje_castor_anciano": ("#6b4a33", 0.90, 0.0, 0.0),   # hoja canónica: pardo cálido
    "pelaje_hocico": ("#9a7a5e", 0.90, 0.0, 0.0),
    "barba_espigas_musgo": ("#b8ad9c", 0.85, 0.0, 0.0),
    "piel_manos_pies": ("#3a332e", 0.70, 0.0, 0.0),
    "garras": ("#1f1b18", 0.40, 0.0, 0.0),
    "nariz": ("#141110", 0.30, 0.0, 0.0),
    "ojos_dorados": ("#1c120c", 0.10, 0.0, 0.0),           # ojillos oscuros y brillantes
    "incisivos_ambar": ("#d4882e", 0.25, 0.0, 0.6),
    "espigas": ("#c9a75a", 0.80, 0.0, 0.0),
    "camisa_algodon": ("#e3d7bd", 0.90, 0.0, 0.0),
    "chaleco_pana": ("#a8642a", 0.92, 0.0, 0.0),
    "peto_saco_cuero": ("#5e5a3d", 0.90, 0.0, 0.0),        # pantalón oliva
    "remiendo": ("#3f342a", 0.90, 0.0, 0.0),
    "cuero": ("#3b2a1c", 0.65, 0.05, 0.0),
    "sombrero_paja": ("#c9b07a", 0.85, 0.0, 0.0),
    "laton_gafas": ("#b08d3e", 0.30, 0.85, 0.0),
    "cola_pizarra_laja": ("#4a5257", 0.70, 0.1, 0.0),
    "baston_roble": ("#5a4027", 0.80, 0.0, 0.0),
    "hierro_azada_runas": ("#2d2f33", 0.40, 0.7, 0.0),
    "barro_cuenco": ("#9b6a45", 0.80, 0.0, 0.0),
    "sopa_zanahoria": ("#d9772b", 0.35, 0.0, 0.3),
}

# ---------------------------------------------------------------------------
# De humano (1,79 m) a castor bípedo (1,45 m)
# ---------------------------------------------------------------------------

# alturas de la malla base -> alturas del castor (piernas cortas, barriga baja, cuello hundido)
TRAMOS_Z = [(0.00, 0.000), (0.09, 0.065), (0.36, 0.195), (0.67, 0.365), (0.90, 0.600), (1.21, 0.860),
            (1.40, 0.985), (1.50, 1.035), (1.545, 1.070)]
Y_CENTRO = -0.02
CABEZA_BASE = Vector((0.0, -0.035, 1.665))
CABEZA_ESC = Vector((1.45, 1.30, 1.30))
CABEZA = Vector((0.0, -0.035, 1.070 + (1.665 - 1.545) * 1.30))     # centro de la cabeza del castor
CABEZA_R = Vector((0.105 * 1.45, 0.14 * 1.30, 0.125 * 1.30))      # semiejes aproximados


def mapa_z(z):
    if z <= TRAMOS_Z[0][0]:
        return z * TRAMOS_Z[1][1] / TRAMOS_Z[1][0]
    for (a, a2), (b, b2) in zip(TRAMOS_Z, TRAMOS_Z[1:]):
        if a <= z <= b:
            return a2 + (b2 - a2) * (z - a) / (b - a)
    a, a2 = TRAMOS_Z[-1]
    return a2 + (z - a) * 1.30


def gauss(d, s):
    return math.exp(-(d * d) / (2 * s * s))


def suave(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def ancho_x(z):
    """Factor de anchura del cuerpo según la altura de la malla base: piernas gruesas, barriga en pera."""
    return 1.28 + 0.40 * gauss(z - 0.86, 0.18)


def fondo_y(z, y):
    if y < Y_CENTRO:   # barriga hacia delante
        return 1.22 + 0.60 * gauss(z - 0.86, 0.17)
    return 1.18 + 0.30 * gauss(z - 0.80, 0.20)     # rabadilla


class Cuerpo:
    """Sabe qué es cada vértice de la malla base (brazo, mano, pierna, pie, torso, cabeza) y lo transforma."""

    def __init__(self, ob):
        self.base = {v.index: v.co.copy() for v in ob.data.vertices}
        self.medio_torso = self._medir_torso()
        self.zona = {i: self.clasificar(p) for i, p in self.base.items()}

    def _medir_torso(self):
        """Media anchura del torso en cada rebanada de 1 cm donde los brazos van separados."""
        tabla = {}
        for k in range(60, 132):
            z0 = k / 100
            xs = sorted(p.x for p in self.base.values() if abs(p.z - z0) < 0.015)
            if not xs:
                continue
            grupo, medio = [], 0.0
            for x in xs:
                if grupo and x - grupo[-1] > 0.045:
                    if grupo[0] <= 0 <= grupo[-1]:
                        break
                    grupo = []
                grupo.append(x)
            if grupo and grupo[0] <= 0 <= grupo[-1]:
                medio = max(abs(grupo[0]), abs(grupo[-1]))
            tabla[k] = medio
        return tabla

    def torso_medio(self, z):
        return self.medio_torso.get(int(round(z * 100)), 0.0)

    def clasificar(self, p):
        if p.z > 1.50:
            return "cabeza"
        if 0.66 < p.z < 1.26:
            medio = self.torso_medio(p.z)
            if medio and abs(p.x) > medio + 0.012:
                return "mano" if p.z < 0.80 else "brazo"
        if p.z < 0.67:
            return "pie" if p.z < 0.10 else "pierna"
        return "torso"

    def cuerpo(self, p):
        x = p.x * ancho_x(p.z)
        y = Y_CENTRO + (p.y - Y_CENTRO) * fondo_y(p.z, p.y)
        if p.z < 0.12:     # pies de castor, largos y anchos
            k = 1.0 + 0.45 * (1 - suave(0.06, 0.12, p.z))
            y = Y_CENTRO + (y - Y_CENTRO) * k
        return Vector((x, y, mapa_z(p.z)))

    def brazo(self, p):
        desplazar = self.torso_medio(1.21) * (ancho_x(1.21) - 1.0) + 0.02
        s = 1 if p.x > 0 else -1
        q = Vector((p.x + s * desplazar, Y_CENTRO + (p.y - Y_CENTRO) * 1.18, mapa_z(p.z)))
        w = suave(1.15, 1.26, p.z)     # cerca de la axila se funde con el torso
        return q.lerp(self.cuerpo(p), w)

    def cabeza(self, p):
        q = CABEZA + Vector(((p.x - CABEZA_BASE.x) * CABEZA_ESC.x, (p.y - CABEZA_BASE.y) * CABEZA_ESC.y,
                             (p.z - CABEZA_BASE.z) * CABEZA_ESC.z))
        # rasgos de castor en coordenadas de la cabeza (frente = -Y)
        n = Vector(((q.x - CABEZA.x) / CABEZA_R.x, (q.y - CABEZA.y) / CABEZA_R.y, (q.z - CABEZA.z) / CABEZA_R.z))
        delante = suave(0.0, -0.75, n.y)
        # los ojos quedan en n.z ≈ -0,28: el hocico va por debajo, de los ojos a la barbilla
        q.y -= 0.105 * gauss(n.x, 0.42) * gauss(n.z + 0.64, 0.30) * delante                 # hocico
        q.x += math.copysign(0.026, n.x) * gauss(abs(n.x) - 0.60, 0.25) * gauss(n.z + 0.60, 0.28)   # carrillos
        q.z -= 0.028 * max(0.0, n.z - 0.55)                                                  # cráneo chato
        q.y += 0.012 * suave(0.2, 0.9, n.y) * gauss(n.z - 0.1, 0.5)                           # nuca redonda
        # orejas humanas de la malla base: se recogen contra la cabeza (las de castor van aparte)
        oreja = suave(0.80, 0.98, abs(n.x)) * gauss(n.z + 0.25, 0.30) * gauss(n.y, 0.45)
        q.x -= (q.x - CABEZA.x) * 0.22 * oreja
        return q

    def transformar(self, i, p):
        zona = self.zona[i]
        if zona == "cabeza" or p.z > 1.48:
            w = suave(1.48, 1.56, p.z)
            return self.cuerpo(p).lerp(self.cabeza(p), w)
        if zona in ("brazo", "mano"):
            return self.brazo(p)
        return self.cuerpo(p)

    def punto(self, p, zona=None):
        """Transforma un punto suelto (articulaciones), diciéndole qué es."""
        p = Vector(p)
        if zona in ("brazo", "mano"):
            return self.brazo(p)
        if zona == "cabeza":
            return self.cabeza(p)
        return self.cuerpo(p)

    def centro(self, zona, z, lado):
        """Centro de una rebanada de la malla base (para colocar codos, muñecas, rodillas...)."""
        pts = [p for i, p in self.base.items() if self.zona[i] == zona and abs(p.z - z) < 0.012
               and (p.x > 0) == (lado > 0)]
        if not pts:
            return None
        return sum(pts, Vector()) / len(pts)


# ---------------------------------------------------------------------------
# Piezas sueltas (con bmesh): esferas, tubos, cajas
# ---------------------------------------------------------------------------

class Piezas:
    def __init__(self, nombre, mats):
        self.nombre = nombre
        self.mats = mats
        self.bm = bmesh.new()
        self.lista = []

    def _i(self, mat):
        if mat not in self.lista:
            self.lista.append(mat)
        return self.lista.index(mat)

    def _poner(self, verts, mat):
        i = self._i(mat)
        caras = {f for v in verts for f in v.link_faces}
        for f in caras:
            f.material_index = i
        return caras

    def esfera(self, c, r, mat, giro=None, seg=(16, 10)):
        M = Matrix.Translation(Vector(c)) @ (giro.to_4x4() if giro else Matrix.Identity(4)) @ \
            Matrix.Diagonal((r[0], r[1], r[2], 1))
        res = bmesh.ops.create_uvsphere(self.bm, u_segments=seg[0], v_segments=seg[1], radius=1.0, matrix=M)
        return self._poner(res["verts"], mat), res["verts"]

    def caja(self, c, t, mat, giro=None):
        M = Matrix.Translation(Vector(c)) @ (giro.to_4x4() if giro else Matrix.Identity(4)) @ \
            Matrix.Diagonal((t[0], t[1], t[2], 1))
        res = bmesh.ops.create_cube(self.bm, size=1.0, matrix=M)
        return self._poner(res["verts"], mat)

    def tubo(self, pts, radios, mat, lados=8, cerrado=False, lateral=None):
        pts = [Vector(p) for p in pts]
        n = len(pts)
        anillos = []
        for i, c in enumerate(pts):
            t = ((pts[(i + 1) % n] if cerrado else pts[min(i + 1, n - 1)]) - pts[i - 1 if cerrado else max(i - 1, 0)])
            t.normalize()
            if callable(lateral):          # lateral(punto): una dirección distinta en cada punto
                lat = Vector(lateral(c))
            else:
                lat = Vector(lateral) if lateral is not None else (Z if abs(t.z) < 0.9 else X)
            ex = (lat - t * lat.dot(t)).normalized()
            ey = t.cross(ex)
            r = radios[i] if isinstance(radios[i], (tuple, list)) else (radios[i], radios[i])
            anillos.append([self.bm.verts.new(c + ex * (r[0] * math.cos(2 * math.pi * j / lados))
                                              + ey * (r[1] * math.sin(2 * math.pi * j / lados)))
                            for j in range(lados)])
        caras = []
        for i in range(n if cerrado else n - 1):
            a, b = anillos[i], anillos[(i + 1) % n]
            for j in range(lados):
                caras.append(self.bm.faces.new((a[j], a[(j + 1) % lados], b[(j + 1) % lados], b[j])))
        if not cerrado:
            caras.append(self.bm.faces.new(list(reversed(anillos[0]))))
            caras.append(self.bm.faces.new(anillos[-1]))
        i = self._i(mat)
        for f in caras:
            f.material_index = i
        return caras

    def torno(self, perfil, centro, mat, lados=32, giro=None, ruido=None):
        """Sólido de revolución alrededor de Z: perfil = [(radio, altura), ...]."""
        anillos = []
        G = giro if giro else Matrix.Identity(3)
        for k, (r, h) in enumerate(perfil):
            fila = []
            for j in range(lados):
                a = 2 * math.pi * j / lados
                rr = r * (1 + (ruido(k, a) if ruido else 0.0))
                fila.append(self.bm.verts.new(Vector(centro) + G @ Vector((rr * math.cos(a), rr * math.sin(a), h))))
            anillos.append(fila)
        caras = []
        for k in range(len(anillos) - 1):
            for j in range(lados):
                a, b = anillos[k], anillos[k + 1]
                caras.append(self.bm.faces.new((a[j], a[(j + 1) % lados], b[(j + 1) % lados], b[j])))
        i = self._i(mat)
        for f in caras:
            f.material_index = i
        return caras

    def objeto(self, suave_=True, grosor=0.0):
        me = bpy.data.meshes.new(self.nombre)
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        self.bm.to_mesh(me)
        self.bm.free()
        for n in self.lista:
            me.materials.append(self.mats[n])
        ob = bpy.data.objects.new(self.nombre, me)
        bpy.context.collection.objects.link(ob)
        ap.activar(ob)
        if grosor:
            mod = ob.modifiers.new("Grosor", "SOLIDIFY")
            mod.thickness = grosor
            bpy.ops.object.modifier_apply(modifier=mod.name)
        if suave_:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
        return ob


# ---------------------------------------------------------------------------
# Montaje
# ---------------------------------------------------------------------------

def construir():
    ap.escena_vacia()
    mats = {n: ap.material(n, *v) for n, v in PALETA.items()}
    mats["cristal_gafas"] = ap.material("cristal_gafas", "#dfe8e6", 0.05, 0.0, 0.0, alfa=0.25)
    cuerpo, ojos = ap.cargar_malla_base("GEO-body_male_stylized")
    forma = Cuerpo(cuerpo)
    me = cuerpo.data
    for v in me.vertices:
        v.co = forma.transformar(v.index, v.co.copy())
    me.update()
    ap.normales_fuera(cuerpo)
    cuerpo.name = "Shamba_Cuerpo"

    # materiales del cuerpo: pelaje y, en manos y pies, piel oscura
    me.materials.clear()
    for n in ("pelaje_castor_anciano", "piel_manos_pies"):
        me.materials.append(mats[n])
    for pol in me.polygons:
        zonas = [forma.zona[i] for i in pol.vertices]
        pol.material_index = 1 if (all(z == "mano" for z in zonas) or all(z == "pie" for z in zonas)) else 0
    ap.activar(cuerpo)
    bpy.ops.object.shade_smooth()

    # ojos: más pequeños y algo más a los lados, dorados
    centros_ojo = []
    for ojo in ojos:
        base_c = sum((v.co for v in ojo.data.vertices), Vector()) / len(ojo.data.vertices)
        nuevo_c = forma.cabeza(base_c)
        nuevo_c.x *= 1.12
        nuevo_c.y += 0.012
        for v in ojo.data.vertices:
            v.co = nuevo_c + (v.co - base_c) * 0.62
        ojo.data.materials.clear()
        ojo.data.materials.append(mats["ojos_dorados"])
        centros_ojo.append(nuevo_c)
    ojos_ob = ap.unir(ojos, "Shamba_Ojos")

    # ropa: camisa crema arremangada, chaleco de pana abierto, pantalón con remiendos
    base, zona = forma.base, forma.zona
    camisa = ap.concha(cuerpo, "Shamba_Camisa",
                       lambda i, p: (zona[i] == "torso" and 0.80 < base[i].z < 1.47)
                       or (zona[i] == "brazo" and base[i].z > 1.01),
                       0.008, 0.005, mats["camisa_algodon"])
    chaleco = ap.concha(cuerpo, "Shamba_Chaleco",
                        lambda i, p: zona[i] == "torso" and 0.83 < base[i].z < 1.40,
                        0.019, 0.006, mats["chaleco_pana"],
                        quitar=lambda i, p: abs(base[i].x) < 0.030 and base[i].y < Y_CENTRO)
    pantalon = ap.concha(cuerpo, "Shamba_Pantalon",
                         lambda i, p: zona[i] in ("pierna", "torso") and 0.13 < base[i].z < 0.90,
                         0.010, 0.005, mats["peto_saco_cuero"])

    acc = Piezas("Shamba_Accesorios", mats)
    # remangado de la camisa en los codos
    for lado in (-1, 1):
        codo = forma.centro("brazo", 1.01, lado)
        if codo:
            c = forma.brazo(codo)
            arriba = forma.brazo(forma.centro("brazo", 1.06, lado) or codo)
            eje = (arriba - c).normalized()
            acc.tubo([c - eje * 0.012, c + eje * 0.016], [(0.062, 0.062), (0.060, 0.060)], "camisa_algodon",
                     lados=16, lateral=X)
    # botones del chaleco y cinturón
    for k in range(4):
        zb = 0.92 + k * 0.11
        pts = [forma.cuerpo(p) for i, p in base.items() if zona[i] == "torso" and abs(p.z - zb) < 0.01
               and abs(p.x) < 0.045 and p.y < Y_CENTRO]
        if pts:
            frente = min(pts, key=lambda q: q.y)
            for s in (-1, 1):
                acc.esfera(frente + Vector((s * 0.045, -0.022, 0)), (0.011, 0.005, 0.011), "cuero", seg=(10, 6))
    pts_cint = [forma.cuerpo(p) for i, p in base.items() if zona[i] == "torso" and abs(p.z - 0.86) < 0.008]
    if pts_cint:
        rx = max(abs(q.x) for q in pts_cint) + 0.022
        ry0, ry1 = min(q.y for q in pts_cint) - 0.022, max(q.y for q in pts_cint) + 0.022
        zc = sum(q.z for q in pts_cint) / len(pts_cint)
        cy, ry = (ry0 + ry1) / 2, (ry1 - ry0) / 2
        anillo = [Vector((rx * math.cos(a), cy + ry * math.sin(a), zc)) for a in
                  (2 * math.pi * k / 32 for k in range(32))]
        acc.tubo(anillo, [(0.022, 0.006)] * 32, "cuero", lados=6, cerrado=True, lateral=Z)
        acc.caja(Vector((0, ry0 - 0.004, zc)), (0.05, 0.012, 0.042), "laton_gafas")
        for s in (-1, 1):     # bolsillos de pana con tapeta
            pts_b = [forma.cuerpo(p) for i, p in base.items() if zona[i] == "torso" and abs(p.z - 0.97) < 0.01
                     and abs(p.x - s * 0.10) < 0.02 and p.y < Y_CENTRO]
            if pts_b:
                f = min(pts_b, key=lambda q: q.y)
                acc.caja(f + Vector((0, -0.024, 0)), (0.085, 0.010, 0.075), "chaleco_pana")
                acc.caja(f + Vector((0, -0.030, 0.033)), (0.090, 0.012, 0.022), "chaleco_pana")
        zurron = Vector((rx + 0.02, cy - ry * 0.4, zc - 0.07))
        acc.esfera(zurron, (0.035, 0.055, 0.065), "cuero", seg=(14, 10))
        acc.caja(zurron + Vector((0.02, 0, 0.04)), (0.03, 0.10, 0.06), "cuero")
    # remiendos del pantalón en las rodillas
    for lado in (-1, 1):
        rod = forma.centro("pierna", 0.38, lado)
        if rod:
            pts = [forma.cuerpo(p) for i, p in base.items() if zona[i] == "pierna" and abs(p.z - 0.38) < 0.012
                   and (p.x > 0) == (lado > 0)]
            frente = min(pts, key=lambda q: q.y)
            acc.caja(frente + Vector((0, -0.014, 0.0)), (0.075, 0.008, 0.07), "remiendo",
                     Matrix.Rotation(math.radians(8 * lado), 3, "Y"))

    # hocico: nariz, incisivos de ámbar, bigotes, orejas, barba con espigas
    cabeza_pts = [q for i, q in enumerate(v.co for v in me.vertices) if zona[i] == "cabeza"]
    def frontal(nz, nx=0.0):
        cand = [q for q in cabeza_pts if abs((q.z - CABEZA.z) / CABEZA_R.z - nz) < 0.06
                and abs((q.x - CABEZA.x) / CABEZA_R.x - nx) < 0.08]
        return min(cand, key=lambda q: q.y) if cand else CABEZA + Vector((0, -CABEZA_R.y, 0))
    nariz = frontal(-0.50)
    acc.esfera(nariz + Vector((0, -0.006, 0.006)), (0.034, 0.022, 0.022), "nariz", seg=(16, 10))
    for s in (-1, 1):     # almohadillas de los bigotes, claras y abultadas
        acc.esfera(frontal(-0.66, s * 0.22) + Vector((s * 0.004, -0.012, 0)), (0.042, 0.030, 0.034),
                   "pelaje_hocico", seg=(14, 10))
    boca = frontal(-0.84)
    for s in (-1, 1):
        acc.caja(boca + Vector((s * 0.0065, 0.004, -0.012)), (0.011, 0.006, 0.024), "incisivos_ambar")
    for s in (-1, 1):
        lado_hocico = frontal(-0.62, s * 0.42)
        for k in range(4):
            ang = math.radians(-12 + 9 * k)
            d = Vector((s * math.cos(ang), -0.25, math.sin(ang))).normalized()
            pts = [lado_hocico + d * (0.13 * t) + Vector((0, 0, -0.02 * t * t)) for t in (0, 0.35, 0.7, 1.0)]
            acc.tubo(pts, [0.0018, 0.0015, 0.0011, 0.0005], "barba_espigas_musgo", lados=4)
        oreja = CABEZA + Vector((s * CABEZA_R.x * 0.78, CABEZA_R.y * 0.10, CABEZA_R.z * 0.60))
        acc.esfera(oreja, (0.034, 0.016, 0.030), "pelaje_castor_anciano",
                   Matrix.Rotation(math.radians(-25 * s), 3, "Y"), seg=(12, 8))
    barbilla = frontal(-0.98)
    # barba canosa: mechones blandos superpuestos bajo la barbilla y en los carrillos
    acc.esfera(barbilla + Vector((0, 0.025, -0.030)), (0.062, 0.040, 0.050), "barba_espigas_musgo", seg=(16, 10))
    for k in range(7):
        a = (k - 3) * 0.32
        c = barbilla + Vector((math.sin(a) * 0.060, 0.030 + 0.012 * abs(k - 3), -0.045 - 0.012 * (k % 2)))
        acc.esfera(c, (0.024, 0.020, 0.040), "barba_espigas_musgo",
                   Matrix.Rotation(a * 0.4, 3, "Y") @ Matrix.Rotation(math.radians(-15), 3, "X"), seg=(10, 8))
    trenza = barbilla + Vector((0, 0.02, -0.07))
    for k in range(9):     # trenza: eslabones alternos que bajan hasta el pecho
        s = 1 if k % 2 else -1
        cc = trenza + Vector((s * 0.010, -0.004 * k, -0.026 * k))
        acc.esfera(cc, (0.022 - 0.0012 * k, 0.018 - 0.001 * k, 0.020), "barba_espigas_musgo",
                   Matrix.Rotation(math.radians(25 * s), 3, "Y"), seg=(10, 8))
    acc.tubo([trenza + Vector((0, -0.01, -0.235)), trenza + Vector((0, -0.012, -0.25))], [0.012, 0.012], "cuero",
             lados=8)
    for s in (-1, 1):      # espigas largas a los lados de la trenza
        raiz_e = barbilla + Vector((s * 0.05, 0.0, -0.04))
        tallo = [raiz_e + Vector((s * 0.012 * u, -0.01 * u, -0.17 * u)) for u in (0, 0.5, 1.0)]
        acc.tubo(tallo, [0.002] * 3, "espigas", lados=4)
        for g in range(7):
            p = tallo[-1] + Vector((s * 0.002 * (g % 2), -0.004, 0.012 * g))
            acc.esfera(p + Vector((s * 0.006 * (1 if g % 2 else -1), 0, 0)), (0.0055, 0.0045, 0.010), "espigas",
                       seg=(8, 6))
    for k, s in enumerate((-1, 1, -1)):   # espigas de trigo enredadas en la barba
        tallo = barbilla + Vector((s * (0.025 + 0.012 * k), -0.03, -0.035 - 0.01 * k))
        for g in range(5):
            acc.esfera(tallo + Vector((s * 0.004 * g, -0.003 * g, -0.012 * g)), (0.0045, 0.004, 0.008), "espigas",
                       seg=(8, 6))

    # gafas redondas de latón apoyadas en el hocico
    for c in centros_ojo:
        centro = c + Vector((math.copysign(-0.004, c.x), -0.068, -0.030))
        aro = [centro + Vector((0.024 * math.cos(a), 0, 0.024 * math.sin(a))) for a in
               (2 * math.pi * k / 24 for k in range(24))]
        acc.tubo(aro, [0.0028] * 24, "laton_gafas", lados=6, cerrado=True, lateral=Y)
        acc.esfera(centro + Vector((0, 0.001, 0)), (0.0225, 0.002, 0.0225), "cristal_gafas", seg=(16, 6))
        patilla_ini = centro + Vector((math.copysign(0.024, c.x), 0, 0))
        oreja = CABEZA + Vector((math.copysign(CABEZA_R.x * 0.95, c.x), CABEZA_R.y * 0.15, CABEZA_R.z * 0.15))
        acc.tubo([patilla_ini, patilla_ini.lerp(oreja, 0.5) + Vector((math.copysign(0.012, c.x), 0, 0.004)), oreja],
                 [0.0018] * 3, "laton_gafas", lados=5)
    a = centros_ojo[0] + Vector((math.copysign(-0.004, centros_ojo[0].x), -0.068, -0.030))
    b = centros_ojo[1] + Vector((math.copysign(-0.004, centros_ojo[1].x), -0.068, -0.030))
    if a.x > b.x:
        a, b = b, a
    medio = (a + b) / 2 + Vector((0, -0.010, 0.010))
    acc.tubo([a + Vector((0.024, 0, 0)), medio, b - Vector((0.024, 0, 0))], [0.0024] * 3, "laton_gafas", lados=5)

    # sombrero de paja con el ala deshilachada
    copa = CABEZA + Vector((0, 0.010, CABEZA_R.z * 0.62))
    perfil = [(0.30, -0.035), (0.29, -0.028), (0.24, -0.005), (0.17, 0.045), (0.10, 0.115), (0.04, 0.185),
              (0.012, 0.215), (0.0, 0.222)]
    acc.torno(perfil, copa, "sombrero_paja", lados=48, giro=Matrix.Rotation(math.radians(-6), 3, "X"),
              ruido=lambda k, a: (0.06 * math.sin(a * 29) + 0.04 * math.sin(a * 53)) if k == 0
              else 0.012 * math.sin(a * 60 + k))
    for s in (-1, 1):     # barboquejo de cordel
        acc.tubo([copa + Vector((s * 0.15, 0.0, 0.0)), copa + Vector((s * 0.12, -0.04, -0.20)),
                  barbilla + Vector((s * 0.03, 0.02, 0.02))], [0.0025] * 3, "cuero", lados=4)

    accesorios = acc.objeto()

    # cola plana de pizarra: sale de la rabadilla y descansa en el suelo (tercer apoyo)
    cola = Piezas("Shamba_Cola", mats)
    rabadilla = [forma.cuerpo(p) for i, p in base.items() if zona[i] == "torso" and abs(p.z - 0.72) < 0.01]
    if rabadilla:   # centrada en X: el vértice más trasero cae en una nalga
        atras = max(q.y for q in rabadilla if abs(q.x) < 0.05) if any(abs(q.x) < 0.05 for q in rabadilla) \
            else max(q.y for q in rabadilla)
        raiz = Vector((0.0, atras - 0.02, sum(q.z for q in rabadilla) / len(rabadilla)))
    else:
        raiz = Vector((0, 0.15, 0.42))
    curva = [raiz, raiz + Vector((0, 0.12, -0.16)), raiz + Vector((0, 0.27, -0.30)),
             Vector((0, raiz.y + 0.43, 0.035)), Vector((0, raiz.y + 0.62, 0.025)), Vector((0, raiz.y + 0.70, 0.03))]
    filas, cols = 26, 14
    rejilla = []
    for i in range(filas):
        u = i / (filas - 1)
        c = _catmull(curva, u)
        ancho = 0.035 + 0.115 * math.sin(math.pi * min(1.0, 0.12 + u * 0.95)) ** 0.7
        grueso = 0.034 - 0.016 * u
        fila = []
        for j in range(cols):
            v = -1 + 2 * j / (cols - 1)
            surco = 0.0
            for d in ((u * 9 + v * 2.2), (u * 9 - v * 2.2)):
                if abs(d - round(d)) < 0.07:
                    surco = 0.0035
            arriba = fila.append(cola.bm.verts.new(c + Vector((v * ancho, 0, grueso * (1 - 0.4 * v * v) - surco))))
            fila.append(cola.bm.verts.new(c + Vector((v * ancho, 0, -grueso * 0.6 * (1 - 0.4 * v * v)))))
        rejilla.append(fila)
    caras = []
    for i in range(filas - 1):
        for j in range(cols - 1):
            for capa_ in (0, 1):
                a1, b1 = rejilla[i][2 * j + capa_], rejilla[i][2 * (j + 1) + capa_]
                a2, b2 = rejilla[i + 1][2 * j + capa_], rejilla[i + 1][2 * (j + 1) + capa_]
                caras.append(cola.bm.faces.new((a1, b1, b2, a2) if capa_ == 0 else (a1, a2, b2, b1)))
        for j, capa_par in ((0, None), (cols - 1, None)):
            caras.append(cola.bm.faces.new((rejilla[i][2 * j], rejilla[i + 1][2 * j], rejilla[i + 1][2 * j + 1],
                                            rejilla[i][2 * j + 1])))
    for j in range(cols - 1):
        caras.append(cola.bm.faces.new((rejilla[-1][2 * j], rejilla[-1][2 * j + 2], rejilla[-1][2 * j + 3],
                                        rejilla[-1][2 * j + 1])))
    k = cola._i("cola_pizarra_laja")
    for f in caras:
        f.material_index = k
    cola_ob = cola.objeto()

    # bastón de roble con azadilla de hierro rúnico en la base
    baston = Piezas("Baston", mats)
    eje = Z
    largo = 1.45          # hoja canónica: más alto que él, nudoso, con la azada arriba
    pts = [Vector((0, 0, largo * t)) + Vector((0.010 * math.sin(t * 9), 0.008 * math.cos(t * 6), 0))
           for t in [k / 24 for k in range(25)]]
    baston.tubo(pts, [0.019 - 0.004 * k / 24 + 0.005 * max(0.0, math.sin(k * 1.3)) ** 8 for k in range(25)],
                "baston_roble", lados=10)
    tope = pts[-1]
    baston.tubo([tope - Vector((0, 0, 0.09)), tope + Vector((0, 0, 0.005))], [0.021, 0.019], "hierro_azada_runas",
                lados=10)
    hoja = bmesh.ops.create_grid(baston.bm, x_segments=3, y_segments=3, size=0.5)
    for v in hoja["verts"]:
        u, w = v.co.x + 0.5, v.co.y + 0.5          # u: del mango a la punta; w: de arriba abajo
        v.co = tope + Vector((0.02 + 0.15 * u, 0, -0.025 - 0.07 * w * (1 - 0.35 * u) + 0.02 * u))   # hacia fuera
    geom = bmesh.ops.extrude_face_region(baston.bm, geom=list({f for v in hoja["verts"] for f in v.link_faces}))
    for e in geom["geom"]:
        if isinstance(e, bmesh.types.BMVert):
            e.co.y += 0.006
    baston._poner(list(hoja["verts"]) + [e for e in geom["geom"] if isinstance(e, bmesh.types.BMVert)],
                  "hierro_azada_runas")
    baston_ob = baston.objeto()

    # cuenco de sopa de zanahoria (aparece solo en ofrecer_cuenco)
    cuenco = Piezas("Cuenco", mats)
    cuenco.torno([(0.0, 0.0), (0.040, 0.002), (0.062, 0.022), (0.072, 0.050), (0.068, 0.052),
                  (0.058, 0.026), (0.036, 0.012), (0.0, 0.010)], Vector(), "barro_cuenco", lados=24)
    cuenco.torno([(0.064, 0.043), (0.0, 0.043)], Vector(), "sopa_zanahoria", lados=24)
    cuenco_ob = cuenco.objeto()

    return {"cuerpo": cuerpo, "ojos": ojos_ob, "camisa": camisa, "chaleco": chaleco, "pantalon": pantalon,
            "accesorios": accesorios, "cola": cola_ob, "baston": baston_ob, "cuenco": cuenco_ob,
            "forma": forma, "curva_cola": curva}


def _catmull(pts, t):
    n = len(pts) - 1
    x = min(max(t, 0.0), 1.0) * n
    i = min(int(x), n - 1)
    f = x - i
    p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * f * f * f)


# ---------------------------------------------------------------------------
# Esqueleto (nombres de la ficha) y pesos
# ---------------------------------------------------------------------------

def huesos(forma, curva_cola):
    P = forma.punto
    lista = [
        ("root", (0, 0, 0), (0, 0, 0.10), None),
        ("hips", tuple(P((0, -0.01, 0.70))), tuple(P((0, -0.01, 0.86))), "root"),
        ("spine_01", tuple(P((0, -0.01, 0.86))), tuple(P((0, -0.01, 1.00))), "hips"),
        ("spine_02", tuple(P((0, -0.01, 1.00))), tuple(P((0, -0.01, 1.14))), "spine_01"),
        ("chest", tuple(P((0, -0.01, 1.14))), tuple(P((0, -0.01, 1.40))), "spine_02"),
        ("neck", tuple(P((0, -0.01, 1.40))), tuple(P((0, -0.02, 1.52), "cabeza")), "chest"),
        ("head", tuple(P((0, -0.02, 1.52), "cabeza")), tuple(P((0, -0.03, 1.79), "cabeza")), "neck"),
        ("jaw", tuple(CABEZA + Vector((0, -0.02, -0.09))), tuple(CABEZA + Vector((0, -0.20, -0.15))), "head"),
        ("beard_root", tuple(CABEZA + Vector((0, -0.10, -0.16))), tuple(CABEZA + Vector((0, -0.12, -0.25))), "head"),
        ("hat_bone", tuple(CABEZA + Vector((0, 0.01, CABEZA_R.z * 0.62))),
         tuple(CABEZA + Vector((0, 0.01, CABEZA_R.z * 0.62 + 0.15))), "head"),
        ("whiskers_L", tuple(CABEZA + Vector((-0.07, -0.19, -0.10))), tuple(CABEZA + Vector((-0.18, -0.22, -0.10))),
         "head"),
        ("whiskers_R", tuple(CABEZA + Vector((0.07, -0.19, -0.10))), tuple(CABEZA + Vector((0.18, -0.22, -0.10))),
         "head"),
        ("tail_01", tuple(curva_cola[0]), tuple(curva_cola[2]), "hips"),
        ("tail_02", tuple(curva_cola[2]), tuple(curva_cola[3]), "tail_01"),
        ("tail_flat", tuple(curva_cola[3]), tuple(curva_cola[5]), "tail_02"),
    ]
    for lado, s in (("L", -1), ("R", 1)):
        hombro = forma.centro("torso", 1.30, s) or Vector((s * 0.15, 0, 1.30))
        hombro = Vector((s * 0.19, hombro.y, 1.32))
        codo = forma.centro("brazo", 1.02, s)
        muneca = forma.centro("mano", 0.79, s) or forma.centro("brazo", 0.82, s)
        punta = forma.centro("mano", 0.72, s) or muneca + Vector((s * 0.03, 0, -0.08))
        rodilla = forma.centro("pierna", 0.36, s)
        tobillo = forma.centro("pierna", 0.10, s)
        punta_pie = forma.centro("pie", 0.03, s)
        punta_pie = Vector((punta_pie.x, punta_pie.y - 0.08, 0.03)) if punta_pie else tobillo + Vector((0, -0.12, -0.06))
        lista += [
            (f"shoulder_{lado}", tuple(P((s * 0.04, -0.01, 1.38))), tuple(P(hombro, "brazo")), "chest"),
            (f"arm_{lado}", tuple(P(hombro, "brazo")), tuple(P(codo, "brazo")), f"shoulder_{lado}"),
            (f"forearm_{lado}", tuple(P(codo, "brazo")), tuple(P(muneca, "brazo")), f"arm_{lado}"),
            (f"hand_{lado}", tuple(P(muneca, "brazo")), tuple(P(punta, "brazo")), f"forearm_{lado}"),
            (f"thigh_{lado}", tuple(P((s * 0.09, -0.01, 0.68))), tuple(P(rodilla)), "hips"),
            (f"calf_{lado}", tuple(P(rodilla)), tuple(P(tobillo)), f"thigh_{lado}"),
            (f"foot_{lado}", tuple(P(tobillo)), tuple(P(punta_pie)), f"calf_{lado}"),
        ]
    # hueso del cuenco, en la palma izquierda
    mano_l = [h for h in lista if h[0] == "hand_L"][0]
    palma = (Vector(mano_l[1]) + Vector(mano_l[2])) / 2
    lista.append(("cuenco", tuple(palma + Vector((0.03, -0.04, 0.0))), tuple(palma + Vector((0.03, -0.04, 0.08))),
                  "hand_L"))
    return lista


def aparejar(p):
    forma = p["forma"]
    arm = ap.crear_esqueleto("MzeeShamba", huesos(forma, p["curva_cola"]))
    zona = forma.zona
    brazo_l = {"shoulder_L", "arm_L", "forearm_L", "hand_L"}
    brazo_r = {"shoulder_R", "arm_R", "forearm_R", "hand_R"}
    piernas = {f"{h}_{l}" for h in ("thigh", "calf", "foot") for l in "LR"}
    columna = {"hips", "spine_01", "spine_02", "chest", "neck"}

    def regla_cuerpo(n, i, co):
        z = zona.get(i, "torso")
        if z == "cabeza":
            if n == "jaw":
                q = (co - CABEZA)
                return 1.0 if (q.z < -0.115 and q.y < -0.07) else 0.0
            return 1.0 if n in ("head", "neck") else 0.0
        if z in ("brazo", "mano"):
            lado = brazo_l if forma.base[i].x < 0 else brazo_r
            return 1.0 if (n in lado or n == "chest") else 0.0
        if z in ("pierna", "pie"):
            return 1.0 if (n in piernas or n == "hips") else 0.0
        return 1.0 if (n in columna or n in ("shoulder_L", "shoulder_R", "thigh_L", "thigh_R")) else 0.0

    todos = [b.name for b in arm.data.bones if b.name != "cuenco"]
    ap.pesar(p["cuerpo"], arm, todos, regla_cuerpo)
    # la ropa copia los pesos del cuerpo que tiene debajo: las mangas siguen al brazo y no se rasgan
    for clave in ("camisa", "chaleco", "pantalon"):
        ap.copiar_pesos(p["cuerpo"], p[clave], arm)
    ap.pesar(p["ojos"], arm, ["head"])
    ap.pesar(p["accesorios"], arm, ["head", "jaw", "hat_bone", "beard_root", "whiskers_L", "whiskers_R", "hips"],
             lambda n, i, co: _regla_accesorio(n, co))
    # lo que no es de la cabeza (cinturón, botones, remiendos, remangados) también copia del cuerpo
    ap.copiar_pesos(p["cuerpo"], p["accesorios"], arm, filtro=lambda co: not _en_cabeza(co))
    ap.pesar(p["cola"], arm, ["hips", "tail_01", "tail_02", "tail_flat"])
    # bastón en la mano derecha, cuenco en su hueso
    hand_r = arm.data.bones["hand_R"]
    agarre = (hand_r.head_local + hand_r.tail_local) / 2
    baston = p["baston"]
    baston.location = agarre - Vector((0, 0, 0.76))
    bpy.context.view_layer.update()
    ap.anclar(baston, arm, "hand_R")
    cuenco = p["cuenco"]
    cuenco.location = arm.data.bones["cuenco"].head_local
    bpy.context.view_layer.update()
    ap.anclar(cuenco, arm, "cuenco")
    return arm


def _en_cabeza(co):
    q = co - CABEZA
    return q.z > -0.27 and abs(q.x) < 0.30 and q.y < 0.25


def _regla_accesorio(n, co):
    q = co - CABEZA
    en_cabeza = _en_cabeza(co)
    if n == "hat_bone":
        return 1.0 if q.z > CABEZA_R.z * 0.45 else 0.0
    if n in ("head",):
        return 1.0 if en_cabeza else 0.0
    if n == "jaw":
        return 1.0 if (en_cabeza and -0.17 < q.z < -0.12 and q.y < -0.10) else 0.0
    if n == "beard_root":
        return 1.0 if (en_cabeza and q.z < -0.15) else 0.0
    if n.startswith("whiskers"):
        return 1.0 if (en_cabeza and abs(q.x) > 0.06 and -0.17 < q.z < -0.04 and q.y < -0.12
                       and (q.x < 0) == n.endswith("L")) else 0.0
    return 0.0 if en_cabeza else 1.0


# ---------------------------------------------------------------------------
# Animaciones
# ---------------------------------------------------------------------------

BASTON_ARRIBA = (0.0, -0.06, 1.0)


def puntos_clave(cuerpo):
    """Dónde queda la barriga (para apoyar las manos en el pomo del bastón, delante de ella)."""
    frente = [v.co for v in cuerpo.data.vertices if abs(v.co.x) < 0.08 and abs(v.co.z - 0.60) < 0.03]
    barriga_y = min(c.y for c in frente) if frente else -0.30
    pomo = Vector((0.03, barriga_y - 0.11, 0.80))
    return pomo


def animar(arm, p):
    an = ap.Animador(arm, "hand_R", Z)
    oculto = {"cuenco": 0.0}
    pomo = puntos_clave(p["cuerpo"])
    izq_sobre = Vector((-0.075, -0.01, 0.035))          # la mano izquierda, encima de la derecha en el pomo

    def respirar(t, extra=None):
        pose = {
            "spine_01": [("X", 4 + 0.8 * math.sin(t))],
            "chest": [("X", 3 - 1.5 * math.sin(t))],
            "head": [("X", 3 + 1.0 * math.sin(t + 0.5)), ("Z", 4 * math.sin(t * 0.5))],
            "tail_01": [("Z", 3 * math.sin(t))],
            "tail_flat": [("Z", 4 * math.sin(t + 0.6))],
            "whiskers_L": [("Z", 3 * math.sin(t * 3))],
            "whiskers_R": [("Z", -3 * math.sin(t * 3 + 0.4))],
            "hand_L": [("X", -20)],
        }
        pose.update(extra or {})
        return pose

    an.nueva("idle_labranza")
    for f in range(0, 91, 6):
        t = 2 * math.pi * f / 90
        r = pomo + Vector((0, 0, 0.004 * math.sin(t)))
        an.fotograma(f, respirar(t), mover={"hips": (0, 0, -0.004 * (1 - math.cos(t)) / 2)},
                     ik={"forearm_R": r, "forearm_L": r + izq_sobre}, baston=BASTON_ARRIBA, escalas=oculto)
    an.cerrar("idle_labranza")

    an.nueva("hablar_afable")
    for f in range(0, 61, 4):
        t = 2 * math.pi * f / 60
        gesto = pomo + Vector((-0.20 - 0.04 * math.sin(t), -0.04, 0.17 + 0.06 * math.sin(t + 0.8)))
        an.fotograma(f, respirar(t, {
            "hand_L": [("Z", -10 + 25 * math.sin(t * 2)), ("X", -35)],
            "head": [("X", 2 + 5 * math.sin(t * 2)), ("Z", 5 * math.sin(t))],
            "jaw": [("X", 6 + 6 * math.sin(t * 6))],
            "chest": [("Z", 4 * math.sin(t))],
            "whiskers_L": [("Z", 5 * math.sin(t * 4))],
            "whiskers_R": [("Z", -5 * math.sin(t * 4))],
            "beard_root": [("X", 3 * math.sin(t * 6))],
        }), ik={"forearm_R": pomo, "forearm_L": gesto}, baston=BASTON_ARRIBA, escalas=oculto)
    an.cerrar("hablar_afable")

    an.nueva("cavar_tierra")
    # (fotograma, dónde va la mano derecha respecto al pomo, dirección del bastón, agacharse)
    claves = [(0, Vector(), BASTON_ARRIBA, 0.0),
              # la azada está arriba: la alza sobre el hombro y la baja de punta contra el surco
              (14, Vector((0.0, 0.02, 0.20)), (0.0, 0.35, 0.94), 0.0),      # alza la azada por detrás
              (22, Vector((0.0, -0.16, -0.10)), (0.0, -0.62, -0.78), 1.0),  # golpe en el surco
              (30, Vector((0.0, -0.06, -0.06)), (0.0, -0.45, -0.89), 0.8),  # tira de la tierra hacia sí
              (40, Vector(), BASTON_ARRIBA, 0.0), (48, Vector(), BASTON_ARRIBA, 0.0)]
    for f, d, dir_b, baja in claves:
        r = pomo + d
        dir_v = Vector(dir_b).normalized()
        izq = r - dir_v * 0.16 + Vector((-0.05, 0, 0))     # la izquierda, más abajo en el mango
        an.fotograma(f, respirar(0.0, {
            "spine_01": [("X", 4 + 16 * baja)],
            "chest": [("X", 3 + 10 * baja)],
            "head": [("X", 6 * baja)],
            "thigh_L": [("X", 10 * baja)], "calf_L": [("X", 16 * baja)],
            "thigh_R": [("X", 10 * baja)], "calf_R": [("X", 16 * baja)],
            "tail_01": [("X", -4 * baja)],
        }), mover={"hips": (0, 0, -0.03 * baja)}, ik={"forearm_R": r, "forearm_L": izq}, baston=dir_b,
            escalas=oculto)
    an.cerrar("cavar_tierra")

    an.nueva("ofrecer_cuenco")
    for f, k, visible in ((0, 0.0, 0.0), (6, 0.15, 1.0), (20, 1.0, 1.0), (44, 1.0, 1.0), (56, 0.15, 1.0),
                          (60, 0.0, 0.0)):
        ofrece = (pomo + izq_sobre).lerp(pomo + Vector((-0.12, -0.26, 0.02)), k)   # a la altura del pecho, hacia Maisha
        an.fotograma(f, respirar(0.0, {
            "hand_L": [("Y", -70 * k), ("X", -20 + 10 * k)],
            "spine_02": [("X", 5 * k)],
            "head": [("X", 6 * k)],
            "jaw": [("X", 4 * k)],
        }), ik={"forearm_R": pomo, "forearm_L": ofrece}, baston=BASTON_ARRIBA, escalas={"cuenco": visible})
    an.cerrar("ofrecer_cuenco")


# ---------------------------------------------------------------------------

def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = construir()
    arm = aparejar(p)
    animar(arm, p)
    objetos = [p[k] for k in ("cuerpo", "ojos", "camisa", "chaleco", "pantalon", "accesorios", "cola", "baston",
                              "cuenco")]
    ap.exportar(SALIDA, arm, objetos)
    ap.informe("MZEE SHAMBA", arm, objetos, SALIDA)
    if "--vistas" in args:
        carpeta = args[args.index("--vistas") + 1]
        os.makedirs(carpeta, exist_ok=True)
        foto = ap.preparar_vistas()
        for nombre, pos, obj, lente in (("1_frente", (0, -3.8, 0.9), (0, 0, 0.72), 50),
                                        ("2_perfil", (3.8, 0, 0.9), (0, 0.15, 0.72), 50),
                                        ("3_espalda", (0, 3.8, 0.9), (0, 0, 0.72), 50),
                                        ("4_tres_cuartos", (-2.4, -3.0, 1.3), (0, 0, 0.72), 50),
                                        ("5_cara", (-0.35, -0.95, 1.30), (0, -0.05, 1.20), 70)):
            foto(os.path.join(carpeta, f"shamba_{nombre}.png"), pos, obj, lente)
        for accion, f, nombre, pos, obj in (
                ("idle_labranza", 0, "a_idle_frente", (0, -3.8, 0.9), (0, 0, 0.72)),
                ("idle_labranza", 0, "b_idle_tres_cuartos", (-2.4, -3.0, 1.3), (0, 0, 0.72)),
                ("hablar_afable", 20, "c_hablar", (-2.0, -3.0, 1.2), (0, 0, 0.75)),
                ("cavar_tierra", 22, "d_cavar", (3.2, -1.5, 1.0), (0, 0, 0.6)),
                ("ofrecer_cuenco", 30, "e_ofrecer_cuenco", (-1.6, -2.6, 1.2), (0, 0, 0.8))):
            arm.animation_data.action = bpy.data.actions[accion]
            bpy.context.scene.frame_set(f)
            foto(os.path.join(carpeta, f"shamba_{nombre}.png"), pos, obj, 50)
        arm.animation_data.action = None


if __name__ == "__main__":
    main()
