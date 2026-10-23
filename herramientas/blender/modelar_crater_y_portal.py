# -*- coding: utf-8 -*-
"""
El Cráter del Despertar, el Árbol Seco, el Portal de Raíz y el Nudo de Corrupción (El Kitovu).
Fichas: construcciones/ref_crater_despertar.md y construcciones/ref_portal_raiz.md (contrato del Kitovu).

  crater_kitovu.glb    cuenco elíptico de 3,40 x 3,00 m y 0,45 m de hondo: tierra calcinada vidriada con
                       grietas radiales, reborde de lajas de pizarra levantadas por el choque, vetas de ámbar
                       que laten y los glifos en espiral de los tatuajes de Maisha en el fondo (emisión: el
                       juego puede hacerlos latir a la vez que los tatuajes)
  arbol_seco.glb       roble milenario petrificado de 4,60 m: tronco retorcido en espiral con fisuras, tres
                       ramas maestras como garras, raíces que abrazan el borde del cráter, ceniza en lo alto
  portal_raiz.glb      arco ojival de 4,80 m (2,80 m de paso, 1,40 m de umbral): dos raíces vivas de 0,75 m
                       que se retuercen y se entrelazan arriba, musgo, vetas de savia dorada y brotes
  nudo_corrupcion.glb  bulbo podrido de 1,60 m con zarcillos negros espinosos que cierran el paso (3,20 m) y
                       agujas de cuarzo violeta; suelo de ceniza alrededor (nodo aparte, SueloMarchito).
                       Esqueleto (bulbo, cristales, zarcillos) y animaciones latido y purificar

    blender -b --factory-startup -P herramientas/blender/modelar_crater_y_portal.py [-- --vistas <carpeta>]
"""

import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aparejo as ap  # noqa: E402
from aparejo import X, Y, Z  # noqa: E402
from modelar_mzee_shamba import Piezas  # noqa: E402
from modelar_props_kitovu import roca  # noqa: E402

CARPETA = os.path.join(ap.RAIZ, "modelos", "entorno")
azar = random.Random(4)

PALETA = {
    "roca_calcinada_crater": ("#22201e", 0.90, 0.0, 0.0),
    "tierra_vidriada": ("#2c2925", 0.35, 0.0, 0.0),
    "pizarra_reborde": ("#3a3a3e", 0.85, 0.05, 0.0),
    "glifos_ambar_crater": ("#e8aa42", 0.40, 0.1, 1.4),
    "madera_petrificada_seco": ("#2e2c2a", 0.95, 0.0, 0.0),
    "ceniza_incrustada": ("#8c8a85", 0.98, 0.0, 0.0),
    "madera_raiz_portal": ("#453324", 0.85, 0.0, 0.0),
    "musgo_fresco_portal": ("#2d4822", 0.90, 0.0, 0.0),
    "savia_dorada_raiz": ("#f5be42", 0.40, 0.1, 1.5),
    "hoja_brote": ("#5d9a3a", 0.60, 0.0, 0.0),
    "roca_desfiladero": ("#45433f", 0.88, 0.0, 0.0),
    "madera_corrupta_nudo": ("#1c181d", 0.95, 0.0, 0.0),
    "cristal_giza_violeta": ("#7b2292", 0.25, 0.1, 2.2),
    "ceniza_cuarteada": ("#5d5b57", 0.98, 0.0, 0.0),
}


def nuevo():
    ap.escena_vacia()
    return {n: ap.material(n, *v) for n, v in PALETA.items()}


def cinta(pz, pts, ancho, mat, normal=Z, alto=0.004):
    """Cinta plana pegada a una superficie (glifos, vetas): un poco por encima para que se vea."""
    verts = []
    for i in range(len(pts) - 1):
        a, b = Vector(pts[i]), Vector(pts[i + 1])
        d = (b - a).normalized()
        lado = d.cross(normal).normalized() * ancho / 2
        fila = [pz.bm.verts.new(a - lado + normal * alto), pz.bm.verts.new(a + lado + normal * alto),
                pz.bm.verts.new(b + lado + normal * alto), pz.bm.verts.new(b - lado + normal * alto)]
        pz.bm.faces.new(fila)
        verts += fila
    i = pz._i(mat)
    for f in {f for v in verts for f in v.link_faces}:
        f.material_index = i


def losa(pz, c, tam, mat, giro):
    res = bmesh.ops.create_grid(pz.bm, x_segments=5, y_segments=4, size=0.5)
    for v in res["verts"]:
        x, y = v.co.x * 2, v.co.y * 2
        borde = 1.0 + 0.15 * noise.noise(Vector((x * 2.1, y * 2.1, c[0] * 3 + c[1])))
        v.co = Vector((x * tam[0] / 2 * borde, y * tam[1] / 2 * borde, 0.0))
    geom = bmesh.ops.extrude_face_region(pz.bm, geom=list({f for v in res["verts"] for f in v.link_faces}))
    nuevos = [e for e in geom["geom"] if isinstance(e, bmesh.types.BMVert)]
    for v in nuevos:
        v.co.z -= tam[2]
    M = Matrix.Translation(Vector(c)) @ giro.to_4x4()
    todos = list(res["verts"]) + nuevos
    for v in todos:
        v.co = M @ v.co
    i = pz._i(mat)
    for f in {f for v in todos for f in v.link_faces}:
        f.material_index = i


# ---------------------------------------------------------------------------
# Cráter y árbol seco
# ---------------------------------------------------------------------------

RX, RY, HONDO = 1.70, 1.50, 0.45


def altura_crater(x, y):
    r = math.sqrt((x / RX) ** 2 + (y / RY) ** 2)       # 1 = labio
    if r < 1.0:
        z = -HONDO * (1 - r * r) ** 1.3 + 0.10 * r ** 6
    else:
        z = 0.10 * math.exp(-((r - 1.0) / 0.18) ** 2)
    ang = math.atan2(y, x)
    grieta = 0.0
    for k in range(9):                              # grietas radiales del choque
        a = k * 2 * math.pi / 9 + 0.3 * math.sin(k * 7)
        d = abs(math.atan2(math.sin(ang - a), math.cos(ang - a)))
        grieta -= 0.035 * max(0.0, 1 - d / 0.035) * (0.25 < r < 1.15)
    return z + grieta + 0.012 * noise.noise(Vector((x * 4, y * 4, 0.5)))


def crater(mats):
    pz = Piezas("Crater", mats)
    anillos, lados = 26, 64
    filas = []
    centro = pz.bm.verts.new(Vector((0, 0, altura_crater(0, 0))))
    for i in range(1, anillos + 1):
        r = 1.35 * i / anillos
        fila = []
        for j in range(lados):
            a = 2 * math.pi * j / lados
            x, y = RX * r * math.cos(a), RY * r * math.sin(a)
            fila.append(pz.bm.verts.new(Vector((x, y, altura_crater(x, y)))))
        filas.append(fila)
    caras = []
    for j in range(lados):
        caras.append(pz.bm.faces.new((centro, filas[0][j], filas[0][(j + 1) % lados])))
    for i in range(anillos - 1):
        for j in range(lados):
            caras.append(pz.bm.faces.new((filas[i][j], filas[i + 1][j], filas[i + 1][(j + 1) % lados],
                                          filas[i][(j + 1) % lados])))
    i_v, i_c = pz._i("tierra_vidriada"), pz._i("roca_calcinada_crater")
    for f in caras:
        c = f.calc_center_median()
        r = math.sqrt((c.x / RX) ** 2 + (c.y / RY) ** 2)
        f.material_index = i_v if r < 0.75 else i_c
    # reborde de lajas de pizarra levantadas hacia fuera por el choque
    for k in range(22):
        a = 2 * math.pi * k / 22 + azar.uniform(-0.08, 0.08)
        x, y = RX * 1.02 * math.cos(a), RY * 1.02 * math.sin(a)
        giro = Matrix.Rotation(a, 3, "Z") @ Matrix.Rotation(math.radians(azar.uniform(25, 60)), 3, "Y")
        losa(pz, (x, y, altura_crater(x, y) + 0.06), (0.36 + azar.uniform(0, 0.2), 0.30 + azar.uniform(0, 0.15),
                                                       0.05), "pizarra_reborde", giro)
    # glifos de ámbar en espiral (los de los tatuajes de Maisha) en el fondo
    def en_fondo(x, y):
        return Vector((x, y, altura_crater(x, y)))
    pts = []
    for k in range(140):
        a = k / 139 * 3.2 * 2 * math.pi
        r = 0.04 + 0.075 * a / (2 * math.pi)
        pts.append(en_fondo(r * math.cos(a), r * math.sin(a)))
    cinta(pz, pts, 0.018, "glifos_ambar_crater")
    for r in (0.36, 0.42):
        cinta(pz, [en_fondo(r * 1.1 * math.cos(a), r * math.sin(a)) for a in
                   (2 * math.pi * k / 72 for k in range(73))], 0.014, "glifos_ambar_crater")
    for k in range(9):              # nodos de la constelación alrededor
        a = 2 * math.pi * k / 9
        c = en_fondo(0.55 * math.cos(a), 0.50 * math.sin(a))
        cinta(pz, [c + Vector((0.025 * math.cos(b), 0.025 * math.sin(b), 0)) for b in
                   (2 * math.pi * j / 12 for j in range(13))], 0.012, "glifos_ambar_crater")
        cinta(pz, [en_fondo(0.44 * 1.1 * math.cos(a), 0.44 * math.sin(a)), c], 0.010, "glifos_ambar_crater")
    # vetas de ámbar en las grietas
    for k in range(9):
        a = k * 2 * math.pi / 9 + 0.3 * math.sin(k * 7)
        pts = [en_fondo(RX * t * math.cos(a), RY * t * math.sin(a)) + Vector((0, 0, -0.02))
               for t in (0.30, 0.45, 0.62, 0.80, 0.95)]
        cinta(pz, pts, 0.012, "glifos_ambar_crater", alto=0.0)
    ob = pz.objeto()
    ob.name = "Crater"
    return ob


def tubo_organico(pz, pts, radios, mat, lobulos=6, giro_lobulo=0.0, fisura=0.10, lados=14):
    """Tronco o raíz: anillos con lóbulos (fisuras de la corteza) que se retuercen a lo largo."""
    n = len(pts)
    anillos = []
    for i, c in enumerate(pts):
        c = Vector(c)
        t = (Vector(pts[min(i + 1, n - 1)]) - Vector(pts[max(i - 1, 0)])).normalized()
        ref = X if abs(t.x) < 0.9 else Y
        e1 = (ref - t * ref.dot(t)).normalized()
        e2 = t.cross(e1)
        fila = []
        for j in range(lados):
            a = 2 * math.pi * j / lados
            k = 1 + fisura * math.sin(lobulos * a + giro_lobulo * i) \
                + 0.04 * noise.noise(Vector((c.x * 3 + a, c.y * 3, c.z * 3)))
            fila.append(pz.bm.verts.new(c + (e1 * math.cos(a) + e2 * math.sin(a)) * radios[i] * k))
        anillos.append(fila)
    caras = []
    for i in range(n - 1):
        for j in range(lados):
            caras.append(pz.bm.faces.new((anillos[i][j], anillos[i][(j + 1) % lados], anillos[i + 1][(j + 1) % lados],
                                          anillos[i + 1][j])))
    caras.append(pz.bm.faces.new(list(reversed(anillos[0]))))
    caras.append(pz.bm.faces.new(anillos[-1]))
    i_m = pz._i(mat)
    for f in caras:
        f.material_index = i_m
    return caras


def rama(pz, base, direccion, largo, radio, nivel, mat, rnd):
    """Rama que se curva hacia el cielo como una garra y se divide."""
    pts, rad = [Vector(base)], [radio]
    d = Vector(direccion).normalized()
    pasos = 8
    for k in range(1, pasos + 1):
        d = (d + Vector((rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), 0.18))).normalized()
        pts.append(pts[-1] + d * largo / pasos)
        rad.append(radio * (1 - 0.75 * k / pasos) + 0.006)
    tubo_organico(pz, pts, rad, mat, lobulos=4, fisura=0.06, lados=8 if nivel > 1 else 10)
    if nivel < 3:
        for h in range(2 if nivel > 0 else 3):
            i = rnd.randint(4, 7)
            lateral = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0.6)).normalized()
            rama(pz, pts[i], (d + lateral).normalized(), largo * 0.55, rad[i] * 0.75, nivel + 1, mat, rnd)


def arbol(mats):
    pz = Piezas("ArbolSeco", mats)
    rnd = random.Random(9)
    pts, rad = [], []
    for k in range(13):
        t = k / 12
        z = -0.15 + 2.55 * t
        pts.append(Vector((0.10 * math.sin(t * 2.6), 0.08 * math.cos(t * 2.2) - 0.08, z)))
        rad.append(0.35 - 0.125 * t + 0.10 * max(0.0, 0.25 - t) / 0.25)
    tubo_organico(pz, pts, rad, "madera_petrificada_seco", lobulos=7, giro_lobulo=-0.35, fisura=0.12, lados=18)
    copa = pts[-1]
    for k, ang in enumerate((0.3, 2.4, 4.4)):            # tres ramas maestras como garras
        d = Vector((math.cos(ang), math.sin(ang), 0.40)).normalized()
        rama(pz, copa - Vector((0, 0, 0.45)) + d * 0.05, d, 1.80, 0.19, 0, "madera_petrificada_seco", rnd)
    for k, ang in enumerate((-0.9, 0.9)):                # raíces que abrazan el borde del cráter (hacia -Y)
        d = Vector((math.sin(ang), -math.cos(ang), 0))
        pts_r = [Vector((0, 0, 0.35)) + d * 0.1, Vector((0, 0, 0.12)) + d * 0.45, d * 0.95 + Vector((0, 0, 0.02)),
                 d * 1.45 + Vector((0, 0, -0.08))]
        tubo_organico(pz, pts_r, [0.20, 0.15, 0.10, 0.05], "madera_petrificada_seco", lobulos=5, fisura=0.10,
                      lados=12)
    ob = pz.objeto()
    # ceniza en lo alto de las ramas y en las caras que miran al cielo
    i_c = list(ob.data.materials).index(mats["ceniza_incrustada"]) if mats["ceniza_incrustada"].name in \
        [m.name for m in ob.data.materials] else None
    if i_c is None:
        ob.data.materials.append(mats["ceniza_incrustada"])
        i_c = len(ob.data.materials) - 1
    for pol in ob.data.polygons:
        if pol.normal.z > 0.75 and pol.center.z > 2.7 and azar.random() < 0.8:
            pol.material_index = i_c
    ob.name = "ArbolSeco"
    return ob


# ---------------------------------------------------------------------------
# Portal de raíz y nudo de corrupción
# ---------------------------------------------------------------------------

def raiz_arco(s, t_max=1.0):
    """Recorrido de la raíz del lado s: sube por el lado y se curva hasta cruzar al otro lado arriba."""
    pts = []
    for k in range(25):
        t = k / 24 * t_max
        c, sn = math.cos(t * math.pi * 0.62), math.sin(t * math.pi * 0.52)
        x = s * (1.75 * math.copysign(abs(c) ** 0.9, c) - 0.25 * t)
        z = 4.55 * math.copysign(abs(sn) ** 1.1, sn)
        y = 0.20 * math.sin(t * 7 + s) * (0.5 + t)
        pts.append(Vector((x, y, z - 0.10)))
    return pts


def portal(mats):
    pz = Piezas("PortalRaiz", mats)
    for s in (-1, 1):
        pts = raiz_arco(s, 1.08)
        rad = [0.42 - 0.18 * (k / 24) for k in range(25)]
        tubo_organico(pz, pts, rad, "madera_raiz_portal", lobulos=5, giro_lobulo=0.45 * s, fisura=0.11, lados=18)
        # raíces secundarias que se enroscan a la principal y pies de raíz en el suelo
        for h in range(2):
            fase = h * math.pi
            sec = []
            for k in range(0, 22):
                t = k / 21
                c = pts[k]
                sec.append(c + Vector((math.cos(t * 14 + fase) * 0.36, math.sin(t * 14 + fase) * 0.36, 0)))
            tubo_organico(pz, sec, [0.11 - 0.07 * k / 21 for k in range(22)], "madera_raiz_portal", lobulos=3,
                          fisura=0.08, lados=8)
        for k, ang in enumerate((-0.7, 0.0, 0.8)):
            d = Vector((s * math.cos(ang), math.sin(ang), 0))
            base = Vector((s * 1.75, 0, 0.25))
            tubo_organico(pz, [base, base + d * 0.5 + Vector((0, 0, -0.15)), base + d * 1.0 + Vector((0, 0, -0.28))],
                          [0.22, 0.13, 0.05], "madera_raiz_portal", lobulos=4, fisura=0.10, lados=10)
        # vetas de savia dorada en los surcos y brotes con hojas en las uniones
        for k in range(3, 20, 2):
            c = pts[k]
            ap_ = (pts[k + 1] - pts[k - 1]).normalized()
            lado = ap_.cross(Y).normalized()
            cinta(pz, [c + lado * rad[k] * 1.02 + ap_ * 0.0, c + lado * rad[k] * 1.03 + ap_ * 0.15,
                       c + lado * rad[k] * 1.02 + ap_ * 0.30], 0.02, "savia_dorada_raiz", normal=lado, alto=0.004)
        for k in (8, 14, 19):
            c = pts[k] + Vector((0, -0.38, 0.05))
            for h in range(4):
                a = h * math.pi / 2 + 0.4
                pz.esfera(c + Vector((0.06 * math.cos(a), -0.02, 0.06 * math.sin(a))), (0.045, 0.012, 0.022),
                          "hoja_brote", Matrix.Rotation(a, 3, "Y"), seg=(8, 6))
        # musgo en la base húmeda
        for k in range(6):
            roca(pz, (s * 1.75 + azar.uniform(-0.3, 0.3), azar.uniform(-0.45, 0.45), azar.uniform(0.15, 0.9)),
                 (0.22, 0.14, 0.10), "musgo_fresco_portal", semilla=k + s * 10, aspereza=0.4)
        # rocas del desfiladero de donde nacen
        for k in range(3):
            roca(pz, (s * (2.3 + 0.3 * k), azar.uniform(-0.6, 0.6), 0.3 + 0.4 * k), (0.55, 0.65, 0.5 + 0.2 * k),
                 "roca_desfiladero", semilla=20 + k + s * 5, aspereza=0.25)
    ob = pz.objeto()
    ob.name = "PortalRaiz"
    return ob


def nudo(mats):
    """Devuelve las piezas por hueso (bulbo, cristales, zarcillos) y el suelo de ceniza."""
    piezas = {}
    pb = Piezas("Nudo_Bulbo", mats)
    res = bmesh.ops.create_icosphere(pb.bm, subdivisions=4, radius=1.0)
    for v in res["verts"]:
        d = v.co.normalized()
        k = 1 + 0.18 * noise.fractal(d * 2.2, 0.6, 2.0, 4) + 0.08 * abs(noise.noise(d * 6))
        v.co = Vector((0, 0, 0.62)) + Vector((d.x * 0.80 * k, d.y * 0.72 * k, d.z * 0.70 * k))
        v.co.z = max(v.co.z, -0.05)
    i_m = pb._i("madera_corrupta_nudo")
    for f in {f for v in res["verts"] for f in v.link_faces}:
        f.material_index = i_m
    for k in range(10):          # grietas violeta sobre el bulbo
        a = 2 * math.pi * k / 10
        pts = [Vector((0.80 * math.cos(a) * (1 - t * 0.3), 0.72 * math.sin(a) * (1 - t * 0.3), 0.30 + t * 0.85))
               for t in (0.0, 0.25, 0.5, 0.75)]
        cinta(pb, pts, 0.03, "cristal_giza_violeta", normal=Vector((math.cos(a), math.sin(a), 0.3)).normalized(),
              alto=0.03)
    piezas["bulbo"] = pb.objeto()
    pc = Piezas("Nudo_Cristales", mats)
    rnd = random.Random(3)
    for k in range(14):          # agujas de cuarzo violeta que brotan del corazón
        a = rnd.uniform(0, 2 * math.pi)
        incl = rnd.uniform(0.0, 0.6)
        d = Vector((math.sin(incl) * math.cos(a), math.sin(incl) * math.sin(a), math.cos(incl)))
        base = Vector((0, 0, 1.05)) + d * 0.15
        largo = rnd.uniform(0.35, 0.80)
        res = bmesh.ops.create_cone(pc.bm, cap_ends=True, segments=6, radius1=rnd.uniform(0.04, 0.08), radius2=0.0,
                                    depth=largo, matrix=Matrix.Translation(base + d * largo / 2)
                                    @ Z.rotation_difference(d).to_matrix().to_4x4())
        i_c = pc._i("cristal_giza_violeta")
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = i_c
    piezas["cristales"] = pc.objeto(suave_=False)
    for lado, s in (("L", -1), ("R", 1)):
        pzz = Piezas(f"Nudo_Zarcillos_{lado}", mats)
        for h in range(5):        # zarcillos negros que salen del suelo y cierran el paso
            a0 = rnd.uniform(-0.6, 0.6)
            pts = []
            for k in range(14):
                t = k / 13
                x = s * (0.45 + 1.15 * t)
                pts.append(Vector((x, a0 * 0.6 + 0.25 * math.sin(t * 6 + h), 0.15 + 1.1 * math.sin(t * math.pi) *
                                   (0.6 + 0.4 * rnd.random()) * (0.4 + 0.15 * h))))
            tubo_organico(pzz, pts, [0.09 - 0.07 * k / 13 for k in range(14)], "madera_corrupta_nudo", lobulos=3,
                          fisura=0.15, lados=8)
            for k in range(2, 13, 2):   # espinas
                c = pts[k]
                d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.3, 1))).normalized()
                r0 = 0.09 - 0.07 * k / 13
                res = bmesh.ops.create_cone(pzz.bm, cap_ends=True, segments=4, radius1=0.022, radius2=0.0, depth=0.14,
                                            matrix=Matrix.Translation(c + d * (r0 + 0.06))
                                            @ Z.rotation_difference(d).to_matrix().to_4x4())
                i_m = pzz._i("madera_corrupta_nudo")
                for f in {f for v in res["verts"] for f in v.link_faces}:
                    f.material_index = i_m
        piezas[f"zarcillos_{lado}"] = pzz.objeto()
    ps = Piezas("SueloMarchito", mats)       # ceniza cuarteada alrededor (Gemini puede quitarla)
    res = bmesh.ops.create_circle(ps.bm, cap_ends=True, segments=48, radius=3.0)
    bmesh.ops.triangulate(ps.bm, faces=ps.bm.faces[:])
    for v in res["verts"]:
        v.co.z = 0.008
    i_s = ps._i("ceniza_cuarteada")
    for f in ps.bm.faces:
        f.material_index = i_s
    piezas["suelo"] = ps.objeto()
    return piezas


def aparejar_nudo(piezas):
    arm = ap.crear_esqueleto("NudoCorrupcion", [
        ("root", (0, 0, 0), (0, 0, 0.1), None),
        ("bulbo", (0, 0, 0.0), (0, 0, 1.0), "root"),
        ("cristales", (0, 0, 1.0), (0, 0, 1.6), "bulbo"),
        ("zarcillos_L", (-0.4, 0, 0.1), (-1.6, 0, 0.1), "root"),
        ("zarcillos_R", (0.4, 0, 0.1), (1.6, 0, 0.1), "root"),
    ])
    for clave, hueso in (("bulbo", "bulbo"), ("cristales", "cristales"), ("zarcillos_L", "zarcillos_L"),
                         ("zarcillos_R", "zarcillos_R")):
        ob = piezas[clave]
        g = ob.vertex_groups.new(name=hueso)
        g.add([v.index for v in ob.data.vertices], 1.0, "REPLACE")
        mod = ob.modifiers.new("Esqueleto", "ARMATURE")
        mod.object = arm
        ob.parent = arm
    an = ap.Animador(arm)
    an.nueva("latido")
    for f in range(0, 41, 4):
        t = 2 * math.pi * f / 40
        late = 1.0 + 0.035 * max(0.0, math.sin(t)) ** 3
        an.fotograma(f, {"zarcillos_L": [("Y", 1.5 * math.sin(t))], "zarcillos_R": [("Y", -1.5 * math.sin(t))]},
                     escalas={"bulbo": late, "cristales": 1.0 + 0.06 * max(0.0, math.sin(t - 0.4)) ** 3})
    an.cerrar("latido")
    an.nueva("purificar")     # las agujas se quiebran, los zarcillos se recogen y el bulbo se deshace
    for f, k in ((0, 0.0), (6, 0.15), (14, 0.5), (24, 0.85), (36, 1.0)):
        an.fotograma(f, {"zarcillos_L": [("Y", -40 * k)], "zarcillos_R": [("Y", 40 * k)]},
                     mover={"zarcillos_L": (0, 0, -0.6 * k), "zarcillos_R": (0, 0, -0.6 * k),
                            "bulbo": (0, 0, -0.5 * k * k)},
                     escalas={"cristales": max(0.001, 1 - k * 1.6), "bulbo": max(0.001, 1 - 0.95 * k),
                              "zarcillos_L": max(0.001, 1 - k), "zarcillos_R": max(0.001, 1 - k)})
    an.cerrar("purificar")
    return arm


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    vistas = args[args.index("--vistas") + 1] if "--vistas" in args else None

    def fotos(nombre, objetivo, dist, alto):
        if not vistas:
            return
        os.makedirs(vistas, exist_ok=True)
        foto = ap.preparar_vistas(resolucion=(900, 800))
        for vista, pos in (("frente", (0, -dist, alto)), ("tres_cuartos", (-dist * 0.7, -dist * 0.75, alto * 1.2))):
            foto(os.path.join(vistas, f"{nombre}_{vista}.png"), pos, objetivo, 50)

    mats = nuevo()
    ob = crater(mats)
    ap.exportar_estatico(os.path.join(CARPETA, "crater_kitovu.glb"), [ob])
    ob.location.z = 0.5        # solo para la foto: el cuenco queda bajo el suelo de las vistas
    fotos("crater_kitovu", (0, 0, 0.3), 5.0, 3.8)
    mats = nuevo()
    ob = arbol(mats)
    ap.exportar_estatico(os.path.join(CARPETA, "arbol_seco.glb"), [ob])
    print("ALTO ARBOL", round(max(v.co.z for v in ob.data.vertices), 2), "ANCHO", round(max(v.co.x for v in ob.data.vertices) - min(v.co.x for v in ob.data.vertices), 2))
    fotos("arbol_seco", (0, 0, 2.4), 12.0, 3.6)
    mats = nuevo()
    ob = portal(mats)
    ap.exportar_estatico(os.path.join(CARPETA, "portal_raiz.glb"), [ob])
    fotos("portal_raiz", (0, 0, 2.2), 10.0, 3.0)
    mats = nuevo()
    piezas = nudo(mats)
    arm = aparejar_nudo(piezas)
    ap.exportar(os.path.join(CARPETA, "nudo_corrupcion.glb"), arm,
                [piezas[k] for k in ("bulbo", "cristales", "zarcillos_L", "zarcillos_R", "suelo")])
    fotos("nudo_corrupcion", (0, 0, 0.7), 7.0, 2.6)
    print("\n=== CRÁTER, ÁRBOL SECO, PORTAL DE RAÍZ Y NUDO exportados ===")


if __name__ == "__main__":
    main()
