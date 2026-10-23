# -*- coding: utf-8 -*-
"""
Atrezo del Huerto Asfixiado de El Kitovu (ficha construcciones/ref_props_huerto_kitovu.md, contrato del Kitovu).
Narrativa ambiental: la granja abandonada a toda prisa ante la Purga de Giza.

  carro_madera.glb     carretilla volcada 28°, varales de roble agrietado, lateral roto, rueda con el aro
                       de hierro partido, abono petrificado y hierbas secas dentro (1,45 x 0,75 x 0,60 m)
  pala_oxidada.glb     mango de fresno con agarre en T y hoja triangular oxidada y mellada, clavada 20 cm
                       en un surco seco a 22° (el origen es el suelo: lo enterrado queda bajo z = 0)
  espantapajaros.glb   maniquí del tutorial (2,10 m, brazos de 1,60 m): cruceta de abedul descortezado
                       atada con esparto, saco de cáñamo deshilachado con remiendos de cuero, cabeza de
                       calabaza seca con capucha de arpillera y ojos de carbón, sombrero de paja caído.
                       Lleva esqueleto (poste, torso, cabeza, brazos) y animaciones reposo y golpeado
  pozo_antiguo.glb     brocal de 4 sillares curvos de caliza (1,70 / 1,15 m, 0,90 m de alto) con las
                       marcas de la soga, musgo, pilastras de roble, tejadillo podrido, torno con manivela,
                       soga que baja al fondo oscuro y cubo de cedro con aros de hierro (2,35 m en total)

    blender -b --factory-startup -P herramientas/blender/modelar_props_kitovu.py [-- --vistas <carpeta>]
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

CARPETA = os.path.join(ap.RAIZ, "modelos", "entorno")
azar = random.Random(28)

PALETA = {
    "madera_roble_desgastada": ("#4a443c", 0.88, 0.0, 0.0),
    "madera_veta_clara": ("#6b6255", 0.88, 0.0, 0.0),
    "hierro_herrumbre": ("#7a3824", 0.82, 0.25, 0.0),
    "oxido_hoja": ("#8a3a22", 0.85, 0.2, 0.0),
    "fresno_mango": ("#7a6650", 0.80, 0.0, 0.0),
    "saco_canamo_parches": ("#7c7462", 0.90, 0.0, 0.0),
    "cuero_parche": ("#3b2a1c", 0.70, 0.0, 0.0),
    "esparto_cuerda": ("#9c8a62", 0.90, 0.0, 0.0),
    "abedul_descortezado": ("#cbbfa8", 0.80, 0.0, 0.0),
    "calabaza_seca": ("#8a6a3a", 0.75, 0.0, 0.0),
    "arpillera_gris": ("#6e6a62", 0.92, 0.0, 0.0),
    "carbon": ("#121110", 0.50, 0.0, 0.0),
    "paja_sombrero": ("#a8915e", 0.85, 0.0, 0.0),
    "caliza_pozo_musgo": ("#585954", 0.85, 0.0, 0.0),
    "musgo_humedo": ("#3d4a2a", 0.95, 0.0, 0.0),
    "fondo_oscuro": ("#050506", 0.30, 0.0, 0.0),
    "cedro_cubo": ("#5a3e28", 0.80, 0.0, 0.0),
    "tierra_agrietada_surco": ("#3c352a", 0.95, 0.0, 0.0),
    "tierra_seca_clara": ("#7d6c52", 0.97, 0.0, 0.0),
    "abono_petrificado": ("#2e2a24", 0.95, 0.0, 0.0),
    "hierba_seca": ("#8b7d55", 0.90, 0.0, 0.0),
}


def tabla(pz, a, b, ancho, grueso, mat, astillado=0.0, giro_x=0.0):
    """Tablón de a a b (centros), con el canto irregular y, si astillado, el final roto en punta."""
    a, b = Vector(a), Vector(b)
    eje = b - a
    largo = eje.length
    t = eje.normalized()
    lado = (Z.cross(t) if abs(t.z) < 0.9 else X.cross(t)).normalized()
    lado = (Matrix.Rotation(giro_x, 3, t) @ lado)
    arriba = t.cross(lado)
    res = bmesh.ops.create_grid(pz.bm, x_segments=8, y_segments=1, size=0.5)
    for v in res["verts"]:
        u, w = v.co.x + 0.5, v.co.y * 2           # u 0..1 a lo largo, w -1..1 a lo ancho
        borde = 1.0 + 0.06 * noise.noise(Vector((u * 7, w, a.x * 3 + a.y)))
        if astillado and u > 1 - astillado:
            borde *= 1.0 - 0.8 * (u - (1 - astillado)) / astillado * (0.5 + 0.5 * abs(math.sin(w * 3)))
        v.co = a + t * (u * largo) + lado * (w * ancho / 2 * borde)
    geom = bmesh.ops.extrude_face_region(pz.bm, geom=list({f for v in res["verts"] for f in v.link_faces}))
    nuevos = [e for e in geom["geom"] if isinstance(e, bmesh.types.BMVert)]
    for v in nuevos:
        v.co -= arriba * grueso
    i = pz._i(mat)
    for f in {f for v in list(res["verts"]) + nuevos for f in v.link_faces}:
        f.material_index = i


def roca(pz, c, r, mat, semilla=0.0, aspereza=0.15):
    res = bmesh.ops.create_icosphere(pz.bm, subdivisions=2, radius=1.0)
    for v in res["verts"]:
        d = v.co.normalized()
        k = 1.0 + noise.fractal(d * 2.5 + Vector((semilla, 0, 0)), 0.6, 2.0, 3) * aspereza
        v.co = Vector(c) + Vector((d.x * r[0] * k, d.y * r[1] * k, d.z * r[2] * k))
    i = pz._i(mat)
    for f in {f for v in res["verts"] for f in v.link_faces}:
        f.material_index = i


def costra(pz, radio, alto, mat, semilla=0.0, grietas=9):
    """Parche de tierra seca y cuarteada: disco irregular algo abombado con grietas oscuras."""
    res = bmesh.ops.create_circle(pz.bm, cap_ends=True, segments=40, radius=1.0)
    centro = bmesh.ops.poke(pz.bm, faces=[f for f in pz.bm.faces if all(v in res["verts"] for v in f.verts)])
    for v in res["verts"]:
        a = math.atan2(v.co.y, v.co.x)
        k = 1 + 0.18 * noise.noise(Vector((math.cos(a) * 2, math.sin(a) * 2, semilla)))
        v.co = Vector((v.co.x * radio * k, v.co.y * radio * k, 0.004))
    for v in centro["verts"]:
        v.co = Vector((0, 0, alto))
    i = pz._i(mat)
    for f in {f for v in res["verts"] for f in v.link_faces}:
        f.material_index = i
    for k in range(grietas):     # grietas: cintas oscuras quebradas
        a = 2 * math.pi * k / grietas + semilla
        pts = []
        for j in range(5):
            r = radio * (0.15 + 0.75 * j / 4)
            aa = a + 0.25 * math.sin(j * 2.1 + k)
            z = alto * (1 - (r / radio)) + 0.006
            pts.append(Vector((r * math.cos(aa), r * math.sin(aa), z)))
        pz.tubo(pts, [(0.006, 0.002)] * 5, "abono_petrificado", lados=4, lateral=Z)


def montón(pz, c, radio, alto, mat, semilla=0.0):
    """Montón de tierra: cúpula irregular."""
    res = bmesh.ops.create_icosphere(pz.bm, subdivisions=3, radius=1.0)
    for v in res["verts"]:
        d = v.co.normalized()
        k = 1 + 0.12 * noise.fractal(d * 2.0 + Vector((semilla, 0, 0)), 0.6, 2.0, 3)
        v.co = Vector(c) + Vector((d.x * radio * k, d.y * radio * k, max(d.z, -0.05) * alto * k))
    i = pz._i(mat)
    for f in {f for v in res["verts"] for f in v.link_faces}:
        f.material_index = i


def girar_todo(ob, giro, apoyar=True):
    """Gira la malla entera y, si apoyar, la deja tocando el suelo."""
    ob.data.transform(giro.to_4x4())
    if apoyar:
        zmin = min(v.co.z for v in ob.data.vertices)
        ob.data.transform(Matrix.Translation((0, 0, -zmin)))
    ob.data.update()


# ---------------------------------------------------------------------------

def carretilla(mats):
    """Carretilla de una rueda: cajón de tablas en trapecio, dos varales que acaban en mangos, dos patas
    traseras y la rueda delante entre los varales. Se construye de pie y se vuelca 28° de lado."""
    pz = Piezas("Carretilla", mats)
    R, C = "madera_roble_desgastada", "madera_veta_clara"

    def tablon(c, tam, rot=(0, 0, 0), mat=R):
        giro = (Matrix.Rotation(math.radians(rot[2]), 3, "Z") @ Matrix.Rotation(math.radians(rot[1]), 3, "Y")
                @ Matrix.Rotation(math.radians(rot[0]), 3, "X"))
        pz.caja(c, tam, mat, giro)

    # varales de roble: de los mangos (atrás, +Y) a la rueda (delante, -Y), bajando hacia delante
    for s in (-1, 1):
        tablon((s * 0.27, 0.05, 0.43), (0.055, 1.40, 0.055), (-9, 0, s * -4))
        pz.tubo([(s * 0.30, 0.70, 0.55), (s * 0.31, 0.80, 0.57)], [0.024, 0.022], C, lados=8)       # mangos
        tablon((s * 0.25, 0.42, 0.20), (0.05, 0.05, 0.40), (-8, 0, 0))                               # patas
    # cajón en trapecio: fondo de tablas, laterales abiertos hacia arriba, frente inclinado y trasera
    for k in range(4):
        tablon((-0.18 + k * 0.12, 0.02, 0.47), (0.11, 0.80, 0.022), (-6, 0, 0))
    for s in (-1, 1):
        for k in range(3):
            if s > 0 and k == 2:
                tablon((s * 0.30, 0.14, 0.62), (0.022, 0.42, 0.075), (-6, s * -22, 0))    # tabla partida
                continue
            tablon((s * (0.26 + 0.035 * k), 0.02, 0.51 + 0.075 * k), (0.022, 0.84, 0.075), (-6, s * -22, 0))
    for k in range(3):
        tablon((0, -0.40, 0.52 + 0.075 * k), (0.52 + 0.07 * k, 0.022, 0.075), (35, 0, 0))   # frente inclinado
        tablon((0, 0.43, 0.56 + 0.075 * k), (0.56 + 0.07 * k, 0.022, 0.075), (-8, 0, 0))
    # remaches de hierro oxidado en las esquinas
    for s in (-1, 1):
        for y in (-0.36, 0.40):
            for z in (0.55, 0.65):
                pz.esfera((s * 0.30, y, z), (0.011, 0.011, 0.011), "hierro_herrumbre", seg=(8, 6))
    # rueda de radios con el aro de hierro partido y el eje
    centro = Vector((0, -0.62, 0.24))
    giro_rueda = Matrix.Rotation(math.radians(90), 3, "Y")
    pz.torno([(0.05, -0.04), (0.07, -0.04), (0.07, 0.04), (0.05, 0.04)], centro, C, lados=16, giro=giro_rueda)
    llanta = [centro + Vector((0, 0.21 * math.cos(a), 0.21 * math.sin(a))) for a in
              (2 * math.pi * k / 24 for k in range(24))]
    pz.tubo(llanta, [(0.035, 0.022)] * 24, C, lados=6, cerrado=True, lateral=X)
    for k in range(8):
        a = 2 * math.pi * k / 8
        d = Vector((0, math.cos(a), math.sin(a)))
        pz.tubo([centro + d * 0.06, centro + d * 0.20], [0.012, 0.010], C, lados=6)
    aro = [centro + Vector((0, 0.232 * math.cos(a), 0.232 * math.sin(a))) for a in
           [math.radians(20 + 290 * k / 28) for k in range(29)]]
    pz.tubo(aro, [(0.010, 0.026)] * 29, "hierro_herrumbre", lados=6, lateral=X)
    pz.tubo([centro + Vector((-0.30, 0, 0)), centro + Vector((0.30, 0, 0))], [0.016, 0.016], "hierro_herrumbre",
            lados=8)
    # abono petrificado y hierbas secas dentro del cajón
    for k in range(6):
        roca(pz, (azar.uniform(-0.15, 0.15), azar.uniform(-0.2, 0.3), 0.52), (0.09, 0.11, 0.05),
             "abono_petrificado", semilla=k, aspereza=0.3)
    for k in range(14):
        b = Vector((azar.uniform(-0.18, 0.18), azar.uniform(-0.25, 0.35), 0.54))
        d = Vector((azar.uniform(-0.4, 0.4), azar.uniform(-0.4, 0.4), 1)).normalized()
        pz.tubo([b, b + d * 0.10, b + d * 0.18 + Vector((0.03, 0, -0.04))], [0.004, 0.003, 0.001], "hierba_seca",
                lados=4)
    ob = pz.objeto()
    # hoja canónica: abandonada de morros sobre la rueda, los varales en alto (28°) y algo ladeada
    girar_todo(ob, Matrix.Rotation(math.radians(6), 3, "Y") @ Matrix.Rotation(math.radians(28), 3, "X"))
    suelo = Piezas("Costra", mats)
    costra(suelo, 0.72, 0.02, "tierra_seca_clara", semilla=1.0)
    ob = ap.unir([ob, suelo.objeto()], "Carretilla")
    return ob


def pala(mats):
    pz = Piezas("Pala", mats)
    largo = 1.15
    # se modela vertical: la hoja abajo; luego se inclina 22° y se entierra 20 cm
    pz.tubo([(0, 0, 0.25), (0, 0, largo)], [0.018, 0.017], "fresno_mango", lados=10)
    pz.tubo([(-0.08, 0, largo + 0.02), (0.08, 0, largo + 0.02)], [0.016, 0.016], "fresno_mango", lados=8)  # agarre T
    pz.tubo([(0, 0, largo - 0.03), (0, 0, largo + 0.02)], [0.021, 0.021], "fresno_mango", lados=8)
    pz.tubo([(0, 0, 0.22), (0, 0, 0.30)], [0.022, 0.020], "hierro_herrumbre", lados=10)            # cubo
    hoja = bmesh.ops.create_grid(pz.bm, x_segments=6, y_segments=6, size=0.5)
    for v in hoja["verts"]:
        u, w = v.co.x * 2, v.co.y + 0.5            # u -1..1 ancho, w 0..1 de arriba (mango) a la punta
        ancho = 0.11 * (1 - 0.65 * w ** 1.4)
        mella = 0.012 * max(0.0, noise.noise(Vector((u * 9, w * 4, 0.3)))) * (w > 0.85)
        v.co = Vector((u * ancho, 0.012 * (1 - u * u), 0.22 - w * 0.28 + mella))
    geom = bmesh.ops.extrude_face_region(pz.bm, geom=list({f for v in hoja["verts"] for f in v.link_faces}))
    for e in geom["geom"]:
        if isinstance(e, bmesh.types.BMVert):
            e.co.y -= 0.006
    i = pz._i("oxido_hoja")
    for f in {f for v in hoja["verts"] for f in v.link_faces}:
        f.material_index = i
    for e in geom["geom"]:
        if isinstance(e, bmesh.types.BMFace):
            e.material_index = i
    ob = pz.objeto()
    # inclinada 22° y con la hoja 20 cm bajo el suelo, como la soltaron al huir
    ob.data.transform(Matrix.Translation((0, 0, -0.13)) @ Matrix.Rotation(math.radians(22), 4, "X"))
    ob.data.update()
    # montón de tierra seca alrededor del corte (a ras de suelo)
    tierra = Piezas("Tierra", mats)
    montón(tierra, (0, -0.05, 0.0), 0.34, 0.20, "tierra_seca_clara", semilla=3.0)
    for k in range(7):        # terrones sueltos y grietas sobre el montón
        a = 2 * math.pi * k / 7 + 0.3
        roca(tierra, (0.36 * math.cos(a), 0.36 * math.sin(a) - 0.05, 0.02), (0.06, 0.05, 0.03),
             "tierra_seca_clara", semilla=k + 3, aspereza=0.35)
        rr = [0.06 + 0.07 * j for j in range(4)]
        tierra.tubo([Vector((x * math.cos(a + 0.2 * j), x * math.sin(a + 0.2 * j) - 0.05,
                             0.20 * (1 - (x / 0.34) ** 2) + 0.004)) for j, x in enumerate(rr)],
                    [(0.005, 0.002)] * 4, "abono_petrificado", lados=4, lateral=Z)
    ob = ap.unir([ob, tierra.objeto()], "Pala")
    return ob


def espantapajaros(mats):
    """Devuelve (objeto, huesos) — los vértices se pesan después por altura."""
    pz = Piezas("Espantapajaros", mats)
    H = 2.10
    B = "abedul_descortezado"
    # poste y travesaño de abedul, con nudos
    poste = [Vector((0.01 * math.sin(k), 0.008 * math.cos(k * 1.3), H * 0.83 * k / 8)) for k in range(9)]
    pz.tubo(poste, [0.045 - 0.008 * k / 8 for k in range(9)], B, lados=10)
    brazo = [Vector((-0.80 + 1.60 * k / 8, 0.0, 1.42 + 0.02 * math.sin(k * 0.9))) for k in range(9)]
    pz.tubo(brazo, [0.030 + 0.006 * abs(k - 4) / 4 for k in range(9)], B, lados=8)
    for s in (-1, 1):     # ramitas en las puntas
        pz.tubo([(s * 0.80, 0, 1.42), (s * 0.90, 0.02, 1.47), (s * 0.96, 0.03, 1.55)], [0.012, 0.008, 0.003], B,
                lados=5)
    # atadura de esparto en el cruce
    for k in range(4):
        a = math.radians(45 + 90 * k)
        pz.tubo([(0.06 * math.cos(a), 0.06 * math.sin(a), 1.38), (-0.06 * math.cos(a), -0.06 * math.sin(a), 1.46)],
                [0.010, 0.010], "esparto_cuerda", lados=6)
    # saco de cáñamo: cuerpo con el bajo deshilachado
    perfil = [(0.17, 1.47), (0.22, 1.38), (0.25, 1.20), (0.24, 1.00), (0.27, 0.86)]
    pz.torno([(r, z) for r, z in perfil], Vector(), "saco_canamo_parches", lados=24,
             ruido=lambda k, a: (0.05 * math.sin(a * 13) + 0.03 * math.sin(a * 29)) * (k == len(perfil) - 1)
             + 0.03 * noise.noise(Vector((a * 2, k, 0))))
    for (z, a) in ((1.18, 0.5), (1.02, -1.9), (1.30, 2.6)):     # remiendos de cuero cosidos
        p = Vector((0.25 * math.sin(a), -0.25 * math.cos(a), z))
        pz.caja(p, (0.09, 0.012, 0.08), "cuero_parche", Matrix.Rotation(-a, 3, "Z"))
    # mangas de saco a lo largo del travesaño, atadas con esparto y con la paja asomando por los puños
    def paja(base, direccion, n, largo):
        for k in range(n):
            d = (Vector(direccion) + Vector((azar.uniform(-0.5, 0.5), azar.uniform(-0.5, 0.5),
                                             azar.uniform(-0.5, 0.5)))).normalized()
            pz.tubo([base, base + d * largo * azar.uniform(0.6, 1.1)], [0.004, 0.0015], "paja_sombrero", lados=3)
    for s in (-1, 1):
        manga = [Vector((s * (0.16 + 0.48 * k / 6), 0, 1.42 - 0.03 * k / 6)) for k in range(7)]
        pz.tubo(manga, [(0.085 - 0.012 * k / 6) * (1 + 0.06 * math.sin(k * 2.3)) for k in range(7)],
                "saco_canamo_parches", lados=12)
        for x in (0.30, 0.60):
            pz.tubo([Vector((s * x, 0.075 * math.cos(a), 1.42 - 0.02 * x + 0.075 * math.sin(a))) for a in
                     (2 * math.pi * j / 10 for j in range(11))], [0.008] * 11, "esparto_cuerda", lados=5)
        paja(Vector((s * 0.64, 0, 1.40)), (s, 0, -0.2), 26, 0.12)
        pz.tubo([Vector((s * 0.60, 0, 1.39)), Vector((s * 0.62, -0.02, 1.25))], [0.004, 0.003], "esparto_cuerda",
                lados=4)
    paja(Vector((0, -0.02, 1.47)), (0, -0.2, 0.4), 18, 0.08)              # paja del cuello
    paja(Vector((0, -0.02, 0.90)), (0, -0.2, -1.0), 22, 0.10)             # paja bajo el saco
    # cabeza: saco de arpillera relleno, atado al cuello, con ojos en cruz y boca cosida
    c = Vector((0, -0.01, 1.62))
    pz.esfera(c, (0.125, 0.12, 0.14), "saco_canamo_parches", seg=(20, 14))
    pz.tubo([c + Vector((0.11 * math.cos(a), 0.11 * math.sin(a), -0.12)) for a in
             (2 * math.pi * j / 12 for j in range(13))], [0.010] * 13, "esparto_cuerda", lados=5)
    frente = c + Vector((0, -0.118, 0))
    for s in (-1, 1):     # ojos: dos puntadas en cruz
        o = frente + Vector((s * 0.045, 0.004, 0.03))
        for d in ((1, 1), (1, -1)):
            pz.tubo([o + Vector((-0.018 * d[0], 0, -0.018 * d[1])), o + Vector((0.018 * d[0], 0, 0.018 * d[1]))],
                    [0.0045, 0.0045], "carbon", lados=4)
    boca = [frente + Vector((-0.06 + 0.12 * k / 8, 0.006 + 0.004 * (1 - abs(k - 4) / 4),
                             -0.04 - 0.012 * (1 - ((k - 4) / 4) ** 2))) for k in range(9)]
    pz.tubo(boca, [0.003] * 9, "carbon", lados=4)
    for k in range(1, 8):     # puntadas cruzando la boca
        p = boca[k]
        pz.tubo([p + Vector((0, 0, -0.012)), p + Vector((0, 0, 0.012))], [0.0025, 0.0025], "carbon", lados=4)
    # sombrero cónico de paja, algo ladeado
    pz.torno([(0.27, -0.01), (0.25, 0.0), (0.18, 0.04), (0.10, 0.10), (0.03, 0.17), (0.0, 0.185)],
             c + Vector((0.01, 0, 0.10)), "paja_sombrero", lados=36,
             giro=Matrix.Rotation(math.radians(8), 3, "Y") @ Matrix.Rotation(math.radians(-6), 3, "X"),
             ruido=lambda k, a: (0.06 * math.sin(a * 21) + 0.04 * math.sin(a * 37)) * (k == 0))
    ob = pz.objeto()
    ob.name = "Espantapajaros"
    huesos = [("root", (0, 0, 0), (0, 0, 0.1), None),
              ("poste", (0, 0, 0.0), (0, 0, 1.10), "root"),
              ("torso", (0, 0, 1.10), (0, 0, 1.50), "poste"),
              ("cabeza", (0, 0, 1.50), (0, 0, 1.85), "torso"),
              ("brazo_L", (-0.05, 0, 1.42), (-0.85, 0, 1.42), "torso"),
              ("brazo_R", (0.05, 0, 1.42), (0.85, 0, 1.42), "torso")]
    return ob, huesos


def pesar_espantapajaros(ob, arm):
    grupos = {n: ob.vertex_groups.new(name=n) for n in ("poste", "torso", "cabeza", "brazo_L", "brazo_R")}
    for v in ob.data.vertices:
        p = v.co
        if p.z > 1.50:
            n = "cabeza"
        elif abs(p.x) > 0.22 and p.z > 1.2:
            n = "brazo_L" if p.x < 0 else "brazo_R"
        elif p.z > 0.95:
            n = "torso"
        else:
            n = "poste"
        grupos[n].add([v.index], 1.0, "REPLACE")
    mod = ob.modifiers.new("Esqueleto", "ARMATURE")
    mod.object = arm
    ob.parent = arm


def animar_espantapajaros(arm):
    an = ap.Animador(arm)
    an.nueva("reposo")       # el viento lo mece despacio
    for f in range(0, 91, 10):
        t = 2 * math.pi * f / 90
        an.fotograma(f, {"poste": [("Y", 1.2 * math.sin(t))], "torso": [("Y", 1.5 * math.sin(t + 0.6))],
                         "cabeza": [("Y", 3 * math.sin(t + 1.2)), ("X", 2 * math.sin(t * 2))],
                         "brazo_L": [("Z", 2 * math.sin(t + 0.3))], "brazo_R": [("Z", -2 * math.sin(t + 0.9))]})
    an.cerrar("reposo")
    an.nueva("golpeado")      # el báculo lo empuja hacia atrás y rebota amortiguándose
    for f in range(0, 49, 2):
        t = f / 48
        k = math.exp(-4.0 * t) * math.cos(t * 18)
        an.fotograma(f, {"poste": [("X", 9 * k)], "torso": [("X", 14 * k), ("Z", 6 * k)],
                         "cabeza": [("X", 22 * k), ("Y", 10 * math.sin(t * 25) * math.exp(-4 * t))],
                         "brazo_L": [("X", -10 * k)], "brazo_R": [("X", -12 * k)]})
    an.cerrar("golpeado")


def sillar(pz, a0, a1, r0, r1, alto, mat, semilla):
    """Sillar curvo de caliza: sector de anillo con cantos gastados y las hendiduras de la soga arriba."""
    n_a, n_r, n_z = 10, 3, 5
    capa = {}
    verts = {}
    for i in range(n_a + 1):
        a = a0 + (a1 - a0) * i / n_a
        for j in range(n_r + 1):
            r = r0 + (r1 - r0) * j / n_r
            for k in range(n_z + 1):
                z = alto * k / n_z
                borde = 1.0
                d = noise.noise(Vector((a * 3, r * 4, z * 4 + semilla))) * 0.012
                if k == n_z and 0.15 < (i / n_a) < 0.85:   # hendiduras de la soga en lo alto
                    d -= 0.020 * max(0.0, math.sin((i / n_a) * math.pi * 4)) ** 8
                verts[(i, j, k)] = pz.bm.verts.new(Vector(((r + d) * math.cos(a), (r + d) * math.sin(a), z + d * 0.5)))
    caras = []

    def cara(c):
        try:
            caras.append(pz.bm.faces.new(c))
        except ValueError:
            pass
    for i in range(n_a):
        for k in range(n_z):
            cara([verts[(i, 0, k)], verts[(i, 0, k + 1)], verts[(i + 1, 0, k + 1)], verts[(i + 1, 0, k)]])
            cara([verts[(i, n_r, k)], verts[(i + 1, n_r, k)], verts[(i + 1, n_r, k + 1)], verts[(i, n_r, k + 1)]])
        for j in range(n_r):
            cara([verts[(i, j, n_z)], verts[(i, j + 1, n_z)], verts[(i + 1, j + 1, n_z)], verts[(i + 1, j, n_z)]])
            cara([verts[(i, j, 0)], verts[(i + 1, j, 0)], verts[(i + 1, j + 1, 0)], verts[(i, j + 1, 0)]])
    for j in range(n_r):
        for k in range(n_z):
            cara([verts[(0, j, k)], verts[(0, j + 1, k)], verts[(0, j + 1, k + 1)], verts[(0, j, k + 1)]])
            cara([verts[(n_a, j, k)], verts[(n_a, j, k + 1)], verts[(n_a, j + 1, k + 1)], verts[(n_a, j + 1, k)]])
    i_mat = pz._i(mat)
    for f in caras:
        f.material_index = i_mat


def sillar_recto(pz, c, tam, giro, semilla, musgo=0.0):
    """Sillar labrado: caja con caras algo abombadas y cantos gastados; musgo en la cara de fuera."""
    n0 = len(pz.bm.verts)        # los vértices nuevos se añaden al final
    res = bmesh.ops.create_cube(pz.bm, size=1.0)
    bmesh.ops.subdivide_edges(pz.bm, edges=list({e for v in res["verts"] for e in v.link_edges}), cuts=2,
                              use_grid_fill=True)
    pz.bm.verts.ensure_lookup_table()
    verts = [pz.bm.verts[i] for i in range(n0, len(pz.bm.verts))]
    for v in verts:
        q = v.co.copy()
        canto = sum(1 for x in q if abs(x) > 0.49)
        q *= 1 - 0.06 * max(0, canto - 1)
        q += q.normalized() * 0.03 * noise.noise(q * 3 + Vector((semilla, 0, 0)))
        v.co = Vector(c) + giro @ Vector((q.x * tam[0], q.y * tam[1], q.z * tam[2]))
    i_p, i_m = pz._i("caliza_pozo_musgo"), pz._i("musgo_humedo")
    fuera = giro @ Y
    for f in {f for v in verts for f in v.link_faces}:
        f.material_index = i_p
        if musgo and f.calc_center_median().z < 0.75 and noise.noise(f.calc_center_median() * 4) + musgo > 0.35 \
                and f.normal.dot(fuera) > -0.3:
            f.material_index = i_m
    return verts


def pozo(mats):
    pz = Piezas("Pozo", mats)
    r_in, r_out, alto = 0.575, 0.85, 0.90
    for hilada in range(3):   # hoja canónica: tres hiladas de sillares a matajunta
        n = 11
        for k in range(n):
            a = 2 * math.pi * (k + 0.5 * (hilada % 2)) / n
            rm = (r_in + r_out) / 2
            giro = Matrix.Rotation(a - math.pi / 2, 3, "Z") @ Matrix.Rotation(math.radians(azar.uniform(-2, 2)), 3,
                                                                                "Y")
            sillar_recto(pz, (rm * math.cos(a), rm * math.sin(a), 0.15 + 0.30 * hilada),
                         (2 * math.pi * rm / n - 0.02, r_out - r_in, 0.285), giro, semilla=hilada * 20 + k,
                         musgo=0.35 - 0.2 * hilada)
    for k in range(18):       # musgo en la base y en las juntas
        a = 2 * math.pi * k / 18 + azar.uniform(-0.1, 0.1)
        roca(pz, (0.87 * math.cos(a), 0.87 * math.sin(a), 0.04), (0.10, 0.10, 0.04), "musgo_humedo", semilla=k,
             aspereza=0.4)
    for k in range(4):
        a = math.radians(90 * k)
        roca(pz, (0.71 * math.cos(a), 0.71 * math.sin(a), alto - 0.15), (0.05, 0.05, 0.12), "musgo_humedo",
             semilla=k + 30, aspereza=0.3)
    # el hueco: pared interior que baja y fondo oscuro
    pz.torno([(r_in - 0.005, 0.02), (r_in - 0.005, -1.40)], Vector(), "caliza_pozo_musgo", lados=32)
    pz.torno([(0.0, -1.40), (r_in, -1.40)], Vector(), "fondo_oscuro", lados=32)
    # pilastras de roble, travesaño y tejadillo a dos aguas de tablas podridas (le faltan algunas)
    R = "madera_roble_desgastada"
    for s in (-1, 1):
        tabla(pz, (s * 0.80, 0.0, 0.0), (s * 0.80, 0.0, 2.05), 0.12, 0.10, R)
    tabla(pz, (-0.92, 0.05, 2.05), (0.92, 0.05, 2.05), 0.10, 0.10, R)
    for s in (-1, 1):
        for k in range(7):
            if (s, k) in ((1, 2), (-1, 5)):
                continue      # tablas que ya se cayeron
            x = -0.90 + k * 0.30
            tabla(pz, (x, s * 0.02, 2.36), (x + azar.uniform(-0.02, 0.02), s * 0.62, 2.02), 0.28, 0.025, R,
                  astillado=0.15 if k in (0, 6) else 0.0)
    # torno con manivela de hierro y soga
    pz.tubo([(-0.80, -0.02, 1.55), (0.80, -0.02, 1.55)], [0.06, 0.06], "madera_veta_clara", lados=14)
    pz.tubo([(0.88, -0.02, 1.55), (0.95, -0.02, 1.55), (0.95, -0.02, 1.38), (1.02, -0.02, 1.38)],
            [0.014] * 4, "hierro_herrumbre", lados=6)
    for k in range(14):       # vueltas de soga en el carrete
        x = -0.32 + k * 0.045
        pz.tubo([(x, -0.02 + 0.072 * math.cos(a), 1.55 + 0.072 * math.sin(a)) for a in
                 (2 * math.pi * j / 12 for j in range(13))], [0.012] * 13, "esparto_cuerda", lados=5)
    pz.tubo([(0.0, -0.09, 1.55), (0.0, -0.10, 0.6), (0.01, -0.10, -0.6), (0.02, -0.09, -1.30)], [0.011] * 4,
            "esparto_cuerda", lados=6)
    # cubo de cedro con dos aros de hierro, sobre el brocal
    cubo_c = Vector((0.70, -0.20, alto))
    pz.torno([(0.0, 0.0), (0.11, 0.0), (0.13, 0.22), (0.12, 0.22), (0.10, 0.02), (0.0, 0.02)], cubo_c, "cedro_cubo",
             lados=18)
    for z in (0.05, 0.18):
        pz.torno([(0.118 + 0.02 * z, z - 0.012), (0.122 + 0.02 * z, z + 0.012)], cubo_c, "hierro_herrumbre",
                 lados=18)
    pz.tubo([cubo_c + Vector((-0.13, 0, 0.21)), cubo_c + Vector((0, 0, 0.36)), cubo_c + Vector((0.13, 0, 0.21))],
            [0.007] * 3, "hierro_herrumbre", lados=5)
    ob = pz.objeto()
    ob.name = "Pozo"
    return ob


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    resultados = []

    def nuevo():
        ap.escena_vacia()
        return {n: ap.material(n, *v) for n, v in PALETA.items()}

    mats = nuevo()
    ob = carretilla(mats)
    ap.exportar_estatico(os.path.join(CARPETA, "carro_madera.glb"), [ob])
    resultados.append(("carro_madera", ob))
    vistas = args[args.index("--vistas") + 1] if "--vistas" in args else None

    def fotos(nombre, objetivo_z, dist):
        if not vistas:
            return
        os.makedirs(vistas, exist_ok=True)
        foto = ap.preparar_vistas(resolucion=(900, 800))
        for vista, pos in (("frente", (0, -dist, objetivo_z + dist * 0.35)),
                           ("tres_cuartos", (-dist * 0.7, -dist * 0.8, objetivo_z + dist * 0.45)),
                           ("perfil", (dist, 0, objetivo_z + dist * 0.3))):
            foto(os.path.join(vistas, f"{nombre}_{vista}.png"), pos, (0, 0, objetivo_z), 50)

    fotos("carro_madera", 0.35, 3.2)
    mats = nuevo()
    ob = pala(mats)
    ap.exportar_estatico(os.path.join(CARPETA, "pala_oxidada.glb"), [ob])
    fotos("pala_oxidada", 0.55, 2.6)
    mats = nuevo()
    ob, huesos = espantapajaros(mats)
    arm = ap.crear_esqueleto("Espantapajaros_Esqueleto", huesos)
    pesar_espantapajaros(ob, arm)
    animar_espantapajaros(arm)
    ap.exportar(os.path.join(CARPETA, "espantapajaros.glb"), arm, [ob])
    fotos("espantapajaros", 1.05, 4.6)
    mats = nuevo()
    ob = pozo(mats)
    ap.exportar_estatico(os.path.join(CARPETA, "pozo_antiguo.glb"), [ob])
    fotos("pozo_antiguo", 1.0, 5.0)
    print("\n=== ATREZO DEL HUERTO: carro_madera, pala_oxidada, espantapajaros, pozo_antiguo exportados ===")


if __name__ == "__main__":
    main()
