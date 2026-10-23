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
    "madera_petrificada_seco": ("#7d7a74", 0.95, 0.0, 0.0),   # concepto canónico: gris ceniza claro
    "ceniza_incrustada": ("#b9b6b0", 0.98, 0.0, 0.0),
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
    # concepto canónico: anillos de runas y espirales pequeñas alrededor de la grande
    for anillo_r, n in ((0.78, 26), (1.10, 34)):
        for k in range(n):
            a = 2 * math.pi * k / n
            base_p = en_fondo(anillo_r * 1.1 * math.cos(a), anillo_r * math.sin(a))
            tang = Vector((-math.sin(a), math.cos(a), 0))
            radial = Vector((math.cos(a), math.sin(a), 0))
            forma_runa = k % 4
            trazos = [((0, -0.04), (0, 0.04))]
            trazos += [((0, 0.04), (0.03, 0.01))] if forma_runa in (0, 2) else [((0, 0.0), (0.03, 0.03))]
            if forma_runa >= 2:
                trazos.append(((0, -0.01), (-0.03, -0.04)))
            for (u0, v0), (u1, v1) in trazos:
                p0 = base_p + tang * u0 + radial * v0
                p1 = base_p + tang * u1 + radial * v1
                p0.z = altura_crater(p0.x, p0.y)
                p1.z = altura_crater(p1.x, p1.y)
                cinta(pz, [p0, p1], 0.012, "glifos_ambar_crater")
    for k in range(4):
        a = 2 * math.pi * k / 4 + 0.6
        cx, cy = 0.95 * 1.1 * math.cos(a) * 0.62, 0.95 * math.sin(a) * 0.62
        cinta(pz, [en_fondo(cx + (0.012 + 0.02 * b / (2 * math.pi)) * math.cos(b),
                            cy + (0.012 + 0.02 * b / (2 * math.pi)) * math.sin(b)) for b in
                   (j / 40 * 2.2 * 2 * math.pi for j in range(41))], 0.010, "glifos_ambar_crater")
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
    tubo_organico(pz, [Vector((p.x * 0.5, p.y * 0.5 - 0.04, p.z)) for p in pts], [r_ * 0.55 for r_ in rad],
                  "madera_petrificada_seco", lobulos=5, fisura=0.10, lados=14)      # alma del tronco
    for h in range(3):        # tres hebras que se retuercen en espiral (sentido horario)
        hebra = []
        for k in range(13):
            tt = k / 12
            a = h * 2 * math.pi / 3 - tt * 2 * math.pi * 0.9
            rr = rad[k] * 0.55
            hebra.append(pts[k] + Vector((rr * math.cos(a), rr * math.sin(a), 0)))
        tubo_organico(pz, hebra, [r_ * 0.55 for r_ in rad], "madera_petrificada_seco", lobulos=4, fisura=0.10,
                      lados=12)
    copa = pts[-1]
    for k, ang in enumerate((0.3, 2.4, 4.4)):            # tres ramas maestras como garras
        d = Vector((math.cos(ang), math.sin(ang), 0.40)).normalized()
        rama(pz, copa - Vector((0, 0, 0.45)) + d * 0.05, d, 1.80, 0.19, 0, "madera_petrificada_seco", rnd)
    for k, ang in enumerate((-1.3, -0.75, -0.25, 0.25, 0.75, 1.3, 2.6, 3.6)):   # raíces, casi todas hacia el cráter
        d = Vector((math.sin(ang), -math.cos(ang), 0))
        largo = 1.6 if abs(ang) < 1.4 else 0.9
        pts_r = [Vector((0, 0, 0.45)) + d * 0.12, Vector((0, 0, 0.18)) + d * 0.45,
                 d * largo * 0.55 + Vector((0, 0, 0.06)), d * largo * 0.8 + Vector((0.05 * math.cos(k), 0, 0.0)),
                 d * largo + Vector((0, 0, -0.12))]
        tubo_organico(pz, pts_r, [0.17, 0.13, 0.09, 0.06, 0.03], "madera_petrificada_seco", lobulos=5, fisura=0.10,
                      lados=10)
        for h in (-1, 1):     # raicillas que se agarran a las piedras
            b = pts_r[2]
            tubo_organico(pz, [b, b + (d + Vector((h * 0.6, 0, 0))).normalized() * 0.35 + Vector((0, 0, -0.06)),
                               b + (d + Vector((h * 0.9, 0, 0))).normalized() * 0.55 + Vector((0, 0, -0.14))],
                          [0.05, 0.03, 0.012], "madera_petrificada_seco", lobulos=3, fisura=0.08, lados=6)
    ob = pz.objeto()
    # ceniza en lo alto de las ramas y en las caras que miran al cielo
    i_c = list(ob.data.materials).index(mats["ceniza_incrustada"]) if mats["ceniza_incrustada"].name in \
        [m.name for m in ob.data.materials] else None
    if i_c is None:
        ob.data.materials.append(mats["ceniza_incrustada"])
        i_c = len(ob.data.materials) - 1
    for pol in ob.data.polygons:
        if pol.normal.z > 0.6 and pol.center.z > 1.0 and azar.random() < 0.8:
            pol.material_index = i_c
    ob.name = "ArbolSeco"
    return ob


# ---------------------------------------------------------------------------
# Portal de raíz y nudo de corrupción
# ---------------------------------------------------------------------------

def raiz_arco(s, t_max=1.0):
    """Recorrido de la raíz del lado s: arco ojival (de círculo) que sube recto desde el suelo y se junta con
    el del otro lado en la punta, a 4,6 m (con su grosor, el arco llega a 4,8 m)."""
    w, alto = 1.75, 4.6
    R = (w * w + alto * alto) / (2 * w)
    cx = w - R
    tope = math.acos(-cx / R)
    pts = []
    for k in range(25):
        u = k / 24 * t_max
        th = u * tope
        x = s * (cx + R * math.cos(th))
        z = R * math.sin(th)
        y = 0.12 * math.sin(u * 7 + s) * (0.5 + u)
        pts.append(Vector((x, y, z - 0.05)))
    return pts


def portal(mats):
    pz = Piezas("PortalRaiz", mats)
    for s in (-1, 1):
        pts = raiz_arco(s, 1.0)      # hoja canónica: las dos raíces se juntan en punta, sin cruzarse
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
        # runas de savia talladas en la cara delantera de la pata (hoja canónica)
        delante = Vector((0, -1, 0))
        for k in range(5):
            base_r = pts[3 + k] + delante * (rad[3 + k] * 0.95)
            for p0, p1 in ((Vector((0, 0, -0.05)), Vector((0, 0, 0.05))), (Vector((-0.03, 0, 0.03)), Vector((0.03, 0, -0.01))),
                           (Vector((-0.03, 0, -0.04)), Vector((0.03, 0, -0.02)))):
                cinta(pz, [base_r + p0, base_r + p1], 0.016, "savia_dorada_raiz", normal=delante, alto=0.03)
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


def pata_portal(s, z):
    """Centro de la pata del portal (lado s) a la altura z, para atarle el nudo."""
    pts = raiz_arco(s, 1.0)
    return min(pts[:16], key=lambda p: abs(p.z - z))


def zarzal(pz, pts, r0, mat, rnd, espinas=True):
    """Zarcillo negro con espinas."""
    n = len(pts)
    rad = [r0 * (1 - 0.6 * k / (n - 1)) + 0.01 for k in range(n)]
    tubo_organico(pz, pts, rad, mat, lobulos=3, fisura=0.15, lados=7)
    if espinas:
        for k in range(1, n - 1):
            d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized()
            res = bmesh.ops.create_cone(pz.bm, cap_ends=True, segments=4, radius1=0.018, radius2=0.0, depth=0.11,
                                        matrix=Matrix.Translation(Vector(pts[k]) + d * (rad[k] + 0.04))
                                        @ Z.rotation_difference(d).to_matrix().to_4x4())
            i_m = pz._i(mat)
            for f in {f for v in res["verts"] for f in v.link_faces}:
                f.material_index = i_m


def racimo(pz, centro, n, tam, rnd, hacia=None):
    """Racimo de agujas de cuarzo violeta que brotan hacia fuera."""
    hacia = Vector(hacia) if hacia else Z
    for k in range(n):
        d = (hacia + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * 0.9).normalized()
        largo = tam * rnd.uniform(0.5, 1.0)
        base = Vector(centro) + d * 0.05
        res = bmesh.ops.create_cone(pz.bm, cap_ends=True, segments=6, radius1=largo * rnd.uniform(0.12, 0.2),
                                    radius2=0.0, depth=largo, matrix=Matrix.Translation(base + d * largo / 2)
                                    @ Z.rotation_difference(d).to_matrix().to_4x4())
        i_c = pz._i("cristal_giza_violeta")
        for f in {f for v in res["verts"] for f in v.link_faces}:
            f.material_index = i_c


def nudo(mats):
    """Hoja canónica: el nudo envuelve el portal a media altura. Zarzas negras atadas a las dos patas, un
    puente de zarcillos entre ellas con cortina de espinas que cierra el paso hasta el suelo, y racimos de
    cuarzo violeta (el grande en la pata derecha). Se coloca en el mismo sitio que portal_raiz.glb."""
    rnd = random.Random(3)
    piezas = {}
    M = "madera_corrupta_nudo"
    for lado, s in (("L", -1), ("R", 1)):
        pz = Piezas(f"Nudo_Zarcillos_{lado}", mats)
        for h in range(3):        # espirales de zarza alrededor de la pata
            pts = []
            for k in range(22):
                t = k / 21
                z = 1.35 + 1.45 * t
                c = pata_portal(s, z)
                a = 2 * math.pi * (1.4 * t) + h * 2.1
                r = 0.50 + 0.06 * math.sin(t * 9 + h)
                pts.append(Vector((c.x + r * math.cos(a), c.y + r * math.sin(a), z + 0.05 * math.sin(a * 2))))
            zarzal(pz, pts, 0.06, M, rnd)
        piezas[f"zarcillos_{lado}"] = pz.objeto()
    pb = Piezas("Nudo_Bulbo", mats)       # puente y cortina
    izq, der = pata_portal(-1, 2.25), pata_portal(1, 2.25)
    for h in range(4):
        pts = []
        for k in range(18):
            t = k / 17
            x = izq.x + 0.35 + (der.x - izq.x - 0.70) * t
            pts.append(Vector((x, 0.12 * math.sin(t * 7 + h * 1.6), 2.25 - 0.45 * math.sin(math.pi * t) + 0.12 * h
                               + 0.08 * math.sin(t * 11 + h))))
        zarzal(pb, pts, 0.07, M, rnd)
    for k in range(9):           # cortina: zarcillos que cuelgan del puente hasta el suelo
        t = (k + 0.5) / 9
        x = izq.x + 0.45 + (der.x - izq.x - 0.9) * t
        arriba = 2.25 - 0.45 * math.sin(math.pi * (0.1 + 0.8 * t))
        pts = [Vector((x + 0.08 * math.sin(j * 1.7 + k), 0.10 * math.sin(j + k), arriba - arriba * j / 9))
               for j in range(10)]
        zarzal(pb, pts, 0.045, M, rnd)
    # corazón podrido en el centro del puente, con grietas violetas
    c = Vector((0, 0, 1.90))
    res = bmesh.ops.create_icosphere(pb.bm, subdivisions=3, radius=1.0)
    for v in res["verts"]:
        d = v.co.normalized()
        k = 1 + 0.2 * noise.fractal(d * 2.2, 0.6, 2.0, 4)
        v.co = c + Vector((d.x * 0.42 * k, d.y * 0.36 * k, d.z * 0.40 * k))
    i_m = pb._i(M)
    for f in {f for v in res["verts"] for f in v.link_faces}:
        f.material_index = i_m
    for k in range(8):
        a = 2 * math.pi * k / 8
        cinta(pb, [c + Vector((0.42 * math.cos(a) * (1 - u * 0.3), 0.36 * math.sin(a) * (1 - u * 0.3), -0.3 + 0.6 * u))
                   for u in (0.0, 0.33, 0.66, 1.0)], 0.03, "cristal_giza_violeta",
              normal=Vector((math.cos(a), math.sin(a), 0.2)).normalized(), alto=0.03)
    piezas["bulbo"] = pb.objeto()
    pc = Piezas("Nudo_Cristales", mats)
    racimo(pc, pata_portal(1, 2.35) + Vector((-0.30, -0.25, 0)), 24, 1.10, rnd, hacia=(-0.4, -0.6, 0.5))
    racimo(pc, pata_portal(-1, 2.05) + Vector((0.30, -0.25, 0)), 12, 0.65, rnd, hacia=(0.4, -0.6, 0.4))
    racimo(pc, c + Vector((0, -0.25, 0.25)), 7, 0.45, rnd, hacia=(0, -0.5, 0.8))
    piezas["cristales"] = pc.objeto(suave_=False)
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
    izq, der = pata_portal(-1, 2.0), pata_portal(1, 2.0)
    arm = ap.crear_esqueleto("NudoCorrupcion", [
        ("root", (0, 0, 0), (0, 0, 0.1), None),
        ("bulbo", (0, 0, 1.9), (0, 0, 2.3), "root"),
        ("cristales", (0, 0, 2.3), (0, 0, 2.6), "bulbo"),
        ("zarcillos_L", (izq.x, 0, 1.3), (izq.x, 0, 2.8), "root"),
        ("zarcillos_R", (der.x, 0, 1.3), (der.x, 0, 2.8), "root"),
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
        an.fotograma(f, {},
                     mover={"zarcillos_L": (0, 0, -0.6 * k), "zarcillos_R": (0, 0, -0.6 * k),
                            "bulbo": (0, 0, -1.2 * k * k)},
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
    fotos("nudo_corrupcion", (0, 0, 1.8), 10.0, 3.0)
    if vistas:     # el nudo puesto en el portal, como lo verá el jugador
        portal(mats)
        fotos("portal_con_nudo", (0, 0, 2.2), 10.0, 3.0)
    print("\n=== CRÁTER, ÁRBOL SECO, PORTAL DE RAÍZ Y NUDO exportados ===")


if __name__ == "__main__":
    main()
