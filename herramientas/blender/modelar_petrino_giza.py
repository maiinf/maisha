# -*- coding: utf-8 -*-
"""
Petrino de Giza en 3D: la bestia pétrea cenicienta (enemigo de choque del prólogo).

Ficha: documentacion/referencias_visuales_3d/enemigos/ref_petrino_giza.md; coraza inspirada en el blindaje
de lajas de personajes/bata_castor_mitico_concept_art.jpg (contrato del Kitovu).
  - jabalí de piedra (hoja canónica enemigos/petrino_giza_turnaround_sheet.jpg): 1,85 m de largo y
    1,15 m a la cruz, con la joroba alta en los hombros;
  - cuerpo de placas de basalto pardo grisáceo y, debajo, un núcleo violeta que brilla por las juntas
    (la red de grietas de corrupción de Giza);
  - cabeza de jabalí con hocico y disco, ojos violetas bajo la ceja, orejas cortas y colmillos curvos de
    cuarzo ferruginoso;
  - cresta de lajas de pizarra en abanico (más altas en la cruz), cola corta con espinas, pezuñas partidas.

Es una criatura de roca: cada bloque va rígido a su hueso (no se dobla como la carne), y así puede
romperse en pedazos al morir. Los bloques se esculpen por código: roca con relieve de ruido y facetas.

    blender -b --factory-startup -P herramientas/blender/modelar_petrino_giza.py [-- --vistas <carpeta>]

Sale modelos/enemigos/petrino_giza.glb: huesos de la ficha (Pelvis, Spine_01, Spine_02, Chest, Neck, Head,
Jaw_Tusk, Shoulder/LegFront/FootFront L/R, LegBack/FootBack L/R), seis nodos vacíos Shards_Break_* para los
fragmentos al morir, y las animaciones reposo, caminar, embestida, aturdido y muerte_fractura.
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

SALIDA = os.path.join(ap.RAIZ, "modelos", "enemigos", "petrino_giza.glb")
azar = random.Random(77)

PALETA = {
    "roca_basalto_cuerpo": ("#4d4842", 0.92, 0.0, 0.0),
    "pizarra_coraza_lomo": ("#3b3a40", 0.85, 0.05, 0.0),
    "colmillos_silex": ("#b49a7c", 0.45, 0.1, 0.0),
    "vetas_giza_violacea": ("#8a2fc0", 0.60, 0.0, 2.2),
    "musgo_seco_grietas": ("#353826", 0.95, 0.0, 0.0),
    "cuenca_oscura": ("#0d0b10", 0.95, 0.0, 0.0),
}

HUESOS = [
    ("root", (0, 0, 0), (0, 0, 0.10), None),
    ("Pelvis", (0, 0.45, 0.75), (0, 0.20, 0.77), "root"),
    ("Spine_01", (0, 0.20, 0.77), (0, -0.05, 0.80), "Pelvis"),
    ("Spine_02", (0, -0.05, 0.80), (0, -0.25, 0.84), "Spine_01"),
    ("Chest", (0, -0.25, 0.84), (0, -0.50, 0.88), "Spine_02"),
    ("Neck", (0, -0.50, 0.88), (0, -0.68, 0.88), "Chest"),
    ("Head", (0, -0.68, 0.88), (0, -1.00, 0.80), "Neck"),
    ("Jaw_Tusk", (0, -0.70, 0.73), (0, -0.98, 0.64), "Head"),
]
for _l, _s in (("L", -1), ("R", 1)):
    HUESOS += [
        (f"Shoulder_{_l}", (_s * 0.10, -0.32, 0.86), (_s * 0.33, -0.34, 0.74), "Chest"),
        (f"LegFront_{_l}", (_s * 0.33, -0.34, 0.74), (_s * 0.35, -0.38, 0.16), f"Shoulder_{_l}"),
        (f"FootFront_{_l}", (_s * 0.35, -0.38, 0.16), (_s * 0.36, -0.56, 0.05), f"LegFront_{_l}"),
        (f"LegBack_{_l}", (_s * 0.26, 0.48, 0.70), (_s * 0.31, 0.50, 0.16), "Pelvis"),
        (f"FootBack_{_l}", (_s * 0.31, 0.50, 0.16), (_s * 0.32, 0.33, 0.05), f"LegBack_{_l}"),
    ]
NOMBRES = [h[0] for h in HUESOS]


class Roca:
    """Malla con un hueso por vértice (capa «hueso»): cada bloque es rígido."""

    def __init__(self, nombre, mats):
        self.nombre, self.mats = nombre, mats
        self.bm = bmesh.new()
        self.capa = self.bm.verts.layers.int.new("hueso")
        self.lista = []

    def _marcar(self, verts, mat, hueso):
        if mat not in self.lista:
            self.lista.append(mat)
        k = self.lista.index(mat)
        for v in verts:
            v[self.capa] = NOMBRES.index(hueso)
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = k

    def bloque(self, c, r, mat, hueso, giro=None, sub=3, aspereza=0.22, escala_ruido=2.6, semilla=0.0, recorte=None,
               tallas=7):
        """Roca: icosfera con bultos de ruido y «tallada»: varios planos al azar le cortan caras planas, como
        piedra partida (si no, parece un globo). recorte(p) -> p opcional, para dar forma (cuña...)."""
        M = Matrix.Translation(Vector(c)) @ (giro.to_4x4() if giro else Matrix.Identity(4))
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=sub, radius=1.0)
        rnd = random.Random(int(semilla * 1000) + 7)
        planos = []
        for _ in range(tallas):
            n = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.6, 1))).normalized()
            planos.append((n, rnd.uniform(0.70, 0.88)))
        for v in res["verts"]:
            d = v.co.normalized()
            s = d * escala_ruido + Vector((semilla, semilla * 1.7, semilla * 0.3))
            k = 1.0 + noise.fractal(s, 0.6, 2.2, 4) * aspereza
            k -= abs(noise.noise(d * 7.0 + Vector((semilla, 0, 0)))) * aspereza * 0.4
            for n, dist in planos:      # talla: nada sobresale del plano
                proy = (d * k).dot(n)
                if proy > dist:
                    k -= (proy - dist) / max(d.dot(n), 0.2)
            k = max(k, 0.45)
            q = Vector((d.x * r[0] * k, d.y * r[1] * k, d.z * r[2] * k))
            if recorte:
                q = recorte(q)
            v.co = M @ q
        self._marcar(res["verts"], mat, hueso)
        return res["verts"]

    def losa(self, c, tam, mat, hueso, giro, cresta=0.0):
        """Laja de pizarra: caja fina con bordes irregulares y una cresta afilada por arriba."""
        res = bmesh.ops.create_grid(self.bm, x_segments=6, y_segments=5, size=0.5)
        for v in res["verts"]:
            x, y = v.co.x * 2, v.co.y * 2        # -1..1
            borde = 1.0 + 0.10 * noise.noise(Vector((x * 2.3, y * 2.3, c[1] * 5)))
            v.co = Vector((x * tam[0] / 2 * borde, y * tam[1] / 2 * borde,
                           cresta * max(0.0, 1 - abs(x) * 1.4) * (0.5 + 0.5 * y)))
        caras = bmesh.ops.extrude_face_region(self.bm, geom=[f for f in {f for v in res["verts"] for f in v.link_faces}])
        nuevos = [e for e in caras["geom"] if isinstance(e, bmesh.types.BMVert)]
        for v in nuevos:
            v.co.z -= tam[2]
        todos = list(res["verts"]) + nuevos
        M = Matrix.Translation(Vector(c)) @ giro.to_4x4()
        for v in todos:
            v.co = M @ v.co
        self._marcar(todos, mat, hueso)

    def cono(self, a, b, r, mat, hueso, lados=6):
        a, b = Vector(a), Vector(b)
        eje = b - a
        giro = Z.rotation_difference(eje.normalized()).to_matrix().to_4x4()
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, segments=lados, radius1=r, radius2=0.002,
                                    depth=eje.length, matrix=Matrix.Translation((a + b) / 2) @ giro)
        self._marcar(res["verts"], mat, hueso)

    def veta(self, pts, mat, hueso, ancho=0.012):
        """Grieta de corrupción: cinta quebrada que brilla (asoma un poco sobre la roca)."""
        verts = []
        for i in range(len(pts) - 1):
            a, b = Vector(pts[i]), Vector(pts[i + 1])
            d = (b - a).normalized()
            lado = d.cross(Y if abs(d.y) < 0.9 else X).normalized() * ancho
            fila = [self.bm.verts.new(a - lado), self.bm.verts.new(a + lado), self.bm.verts.new(b + lado),
                    self.bm.verts.new(b - lado)]
            self.bm.faces.new(fila)
            verts += fila
        self._marcar(verts, mat, hueso)

    def objeto(self):
        me = bpy.data.meshes.new(self.nombre)
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        self.bm.to_mesh(me)
        self.bm.free()
        for n in self.lista:
            me.materials.append(self.mats[n])
        ob = bpy.data.objects.new(self.nombre, me)
        bpy.context.collection.objects.link(ob)
        ap.activar(ob)
        bpy.ops.object.shade_flat()      # roca facetada
        return ob


def placas(r, c, radios, hueso, n, semilla, mat="roca_basalto_cuerpo", grosor=0.55, debajo=True):
    """Cuerpo de placas: n trozos de basalto repartidos por un elipsoide y, debajo, un núcleo violeta que
    brilla por las juntas (las grietas de Giza de la hoja canónica)."""
    c, radios = Vector(c), Vector(radios)
    n = max(6, int(n * 0.6))     # placas grandes, como músculos de piedra
    if debajo:
        r.bloque(c, radios * 0.88, "vetas_giza_violacea", hueso, sub=2, aspereza=0.04, tallas=0, semilla=semilla)
    area = 4 * math.pi * ((radios.x * radios.y) ** 1.6 + (radios.x * radios.z) ** 1.6 + (radios.y * radios.z) ** 1.6
                          / 3) ** (1 / 1.6)
    lado = math.sqrt(area / n) * 0.50
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        rr = math.sqrt(max(0.0, 1 - z * z))
        fi = i * 2.399963 + semilla
        d = Vector((rr * math.cos(fi), rr * math.sin(fi), z))
        p = c + Vector((d.x * radios.x, d.y * radios.y, d.z * radios.z)) * 0.93
        normal = Vector((d.x / radios.x, d.y / radios.y, d.z / radios.z)).normalized()
        giro = Z.rotation_difference(normal).to_matrix() @ Matrix.Rotation(azar.uniform(0, 3), 3, "Z")
        k = azar.uniform(0.85, 1.15)
        r.bloque(p, (lado * k, lado * k * azar.uniform(0.8, 1.1), lado * grosor), mat, hueso, giro=giro, sub=2,
                 aspereza=0.18, semilla=semilla + i * 0.37, tallas=6)


def lasca(r, base, alto, ancho, inclinacion, hueso, mat="pizarra_coraza_lomo", semilla=0.0, lado=0.0):
    """Laja de la cresta: sale del lomo hacia arriba, afilada en punta e inclinada hacia atrás."""
    def punta(q):
        t = min(1.0, max(0.0, (q.z / alto) + 0.5))
        return Vector((q.x * (1 - 0.6 * t), q.y * (1 - 0.55 * t) - 0.35 * t * t * abs(q.y), q.z))
    giro = Matrix.Rotation(math.radians(lado), 3, "Y") @ Matrix.Rotation(math.radians(-inclinacion), 3, "X")
    r.bloque(Vector(base) + giro @ Vector((0, 0, alto * 0.45)), (0.05, ancho / 2, alto / 2), mat, hueso, giro=giro,
             sub=2, aspereza=0.08, recorte=punta, semilla=semilla, tallas=4)


def colmillo(r, pts, r0, mat, hueso):
    """Colmillo curvo: tubo que se afila hasta la punta."""
    pts = [Vector(p) for p in pts]
    anillos = []
    for i, c in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        e1 = (X - t * X.dot(t)).normalized() if abs(t.x) < 0.9 else (Y - t * Y.dot(t)).normalized()
        e2 = t.cross(e1)
        rad = r0 * (1 - i / (len(pts) - 1)) + 0.002
        anillos.append([r.bm.verts.new(c + (e1 * math.cos(a) + e2 * math.sin(a)) * rad)
                        for a in (2 * math.pi * j / 8 for j in range(8))])
    for i in range(len(anillos) - 1):
        for j in range(8):
            r.bm.faces.new((anillos[i][j], anillos[i][(j + 1) % 8], anillos[i + 1][(j + 1) % 8], anillos[i + 1][j]))
    r.bm.faces.new(list(reversed(anillos[0])))
    r.bm.faces.new(anillos[-1])
    r._marcar([v for a in anillos for v in a], mat, hueso)


def construir():
    ap.escena_vacia()
    mats = {n: ap.material(n, *v) for n, v in PALETA.items()}
    r = Roca("Petrino_Cuerpo", mats)
    B, P, V, S = "roca_basalto_cuerpo", "pizarra_coraza_lomo", "vetas_giza_violacea", "colmillos_silex"

    # tronco de jabalí: la joroba alta en la cruz y el lomo que baja hacia la grupa
    placas(r, (0, 0.44, 0.70), (0.29, 0.28, 0.27), "Pelvis", 26, 1.0)
    placas(r, (0, 0.14, 0.72), (0.33, 0.28, 0.29), "Spine_01", 28, 2.0)
    placas(r, (0, -0.14, 0.79), (0.37, 0.27, 0.33), "Spine_02", 30, 3.0)
    placas(r, (0, -0.38, 0.84), (0.39, 0.26, 0.37), "Chest", 32, 4.0)
    placas(r, (0, -0.60, 0.79), (0.29, 0.18, 0.28), "Neck", 18, 5.0)

    # cabeza: cráneo macizo, ceja de piedra, hocico de cerdo con su disco y orejas cortas
    def cuña(q):
        k = 1.0 - 0.30 * max(0.0, -q.y) / 0.25
        return Vector((q.x * k, q.y, q.z * k))
    for k, (c, rad) in enumerate((((0, -0.80, 0.86), (0.20, 0.20, 0.12)), ((-0.12, -0.84, 0.72), (0.10, 0.17, 0.12)),
                                  ((0.12, -0.84, 0.72), (0.10, 0.17, 0.12)), ((0, -0.72, 0.70), (0.17, 0.12, 0.14)))):
        r.bloque(c, rad, B, "Head", sub=3, aspereza=0.12, semilla=30 + k, recorte=cuña, tallas=8)
    for pts in (((0.0, -0.95, 0.93), (0.03, -0.90, 0.97), (-0.02, -0.82, 0.99), (0.02, -0.74, 0.98)),
                ((0.10, -0.92, 0.80), (0.15, -0.86, 0.76), (0.17, -0.78, 0.79)),
                ((-0.10, -0.92, 0.80), (-0.15, -0.86, 0.76), (-0.17, -0.78, 0.79)),
                ((0.05, -1.05, 0.76), (0.0, -0.99, 0.80), (-0.05, -0.95, 0.85))):
        r.veta([(x * 1.08, y, z) for x, y, z in pts], V, "Head", ancho=0.010)
    r.bloque((0, -0.93, 0.89), (0.19, 0.07, 0.05), B, "Head", sub=2, aspereza=0.15, semilla=36)        # ceja
    r.bloque((0, -1.00, 0.70), (0.12, 0.14, 0.11), B, "Head", sub=3, aspereza=0.10, semilla=37, tallas=6)  # hocico
    r.bloque((0, -1.12, 0.67), (0.105, 0.035, 0.085), B, "Head", sub=2, aspereza=0.03, tallas=0)          # disco
    for s in (-1, 1):
        lado = "L" if s < 0 else "R"
        r.bloque((s * 0.04, -1.15, 0.665), (0.022, 0.012, 0.03), "cuenca_oscura", "Head", sub=2, aspereza=0.0,
                 tallas=0)
        r.bloque((s * 0.105, -0.95, 0.835), (0.045, 0.03, 0.03), "cuenca_oscura", "Head", sub=2, aspereza=0.05,
                 tallas=0)
        r.bloque((s * 0.105, -0.972, 0.835), (0.026, 0.012, 0.016), V, "Head", sub=2, aspereza=0.0, tallas=0)
        r.cono((s * 0.13, -0.70, 0.94), (s * 0.20, -0.62, 1.08), 0.055, B, "Head", lados=4)            # oreja
        # colmillos curvos de cuarzo ferruginoso: salen de la mandíbula hacia fuera, delante y arriba
        colmillo(r, [(s * 0.09, -1.00, 0.60), (s * 0.15, -1.06, 0.62), (s * 0.20, -1.09, 0.70),
                     (s * 0.21, -1.07, 0.80), (s * 0.18, -1.02, 0.87)], 0.036, S, "Jaw_Tusk")
        # patas gruesas de placas y pezuñas partidas en dos dedos
        placas(r, (s * 0.31, -0.34, 0.70), (0.15, 0.17, 0.19), f"Shoulder_{lado}", 12, 8 + s)
        placas(r, (s * 0.33, -0.37, 0.40), (0.11, 0.12, 0.24), f"LegFront_{lado}", 12, 10 + s)
        placas(r, (s * 0.27, 0.45, 0.62), (0.15, 0.19, 0.19), f"LegBack_{lado}", 12, 14 + s)
        placas(r, (s * 0.29, 0.50, 0.36), (0.10, 0.11, 0.21), f"LegBack_{lado}", 10, 16 + s)
        for pie, py in ((f"FootFront_{lado}", -0.42), (f"FootBack_{lado}", 0.44)):
            r.bloque((s * (0.33 if "Front" in pie else 0.30), py, 0.13), (0.10, 0.11, 0.08), B, pie, sub=2,
                     aspereza=0.12, semilla=18 + s, tallas=5)
            for dedo in (-1, 1):
                x = s * (0.33 if "Front" in pie else 0.30) + dedo * 0.045
                r.bloque((x, py - 0.06, 0.045), (0.042, 0.075, 0.045), P, pie, sub=2, aspereza=0.1,
                         semilla=40 + dedo, tallas=4)
    r.bloque((0, -0.93, 0.60), (0.12, 0.16, 0.06), B, "Jaw_Tusk", sub=2, aspereza=0.12, semilla=7, tallas=5)

    # cresta: lajas de pizarra en abanico, más altas en la cruz, en dos filas al tresbolillo
    for k in range(8):
        t = k / 7
        y = -0.55 + 1.05 * t
        hueso = "Chest" if y < -0.27 else "Spine_02" if y < -0.02 else "Spine_01" if y < 0.28 else "Pelvis"
        alto = 0.50 * (1 - t) ** 0.8 + 0.12
        z = 1.12 - 0.20 * t
        for fila in (-1, 1):
            lasca(r, (fila * 0.05, y + fila * 0.04, z - 0.04), alto * (1.0 if fila < 0 else 0.85), 0.42 - 0.12 * t,
                  48 + 10 * t, hueso, semilla=50 + k * 2 + fila, lado=fila * 8)
    # cola corta de placas con espinas
    for k in range(5):
        t = k / 4
        c = (0, 0.70 + 0.22 * t, 0.78 - 0.20 * t)
        r.bloque(c, (0.06 - 0.03 * t, 0.07, 0.06 - 0.03 * t), B, "Pelvis", sub=2, aspereza=0.15, semilla=60 + k)
        if k < 4:
            r.cono((0, c[1], c[2] + 0.04), (0, c[1] + 0.06, c[2] + 0.12 - 0.04 * t), 0.025, P, "Pelvis", lados=4)
    return r.objeto(), mats


def aparejar(cuerpo):
    arm = ap.crear_esqueleto("Petrino", HUESOS)
    capa = cuerpo.data.attributes["hueso"]
    grupos = {n: cuerpo.vertex_groups.new(name=n) for n in NOMBRES}
    for v in cuerpo.data.vertices:
        grupos[NOMBRES[capa.data[v.index].value]].add([v.index], 1.0, "REPLACE")
    mod = cuerpo.modifiers.new("Esqueleto", "ARMATURE")
    mod.object = arm
    cuerpo.parent = arm
    # puntos donde el juego hace salir los fragmentos al romperse
    vacios = []
    for k, p in enumerate(((0, -0.40, 0.95), (0, 0.10, 0.95), (0, 0.48, 0.90), (-0.35, -0.35, 0.40),
                           (0.35, -0.35, 0.40), (0, -0.85, 0.80))):
        e = bpy.data.objects.new(f"Shards_Break_{k + 1}", None)
        e.empty_display_size = 0.08
        e.location = p
        bpy.context.collection.objects.link(e)
        e.parent = arm
        vacios.append(e)
    return arm, vacios


# ---------------------------------------------------------------------------
# Animaciones. Patas colgando: X- = hacia delante. Cabeza y columna: X+ = bajar el morro.
# ---------------------------------------------------------------------------

def animar(arm):
    an = ap.Animador(arm)

    an.nueva("reposo")
    for f in range(0, 61, 6):
        t = 2 * math.pi * f / 60
        an.fotograma(f, {
            "Chest": [("X", 1.5 * math.sin(t))],
            "Neck": [("X", 2 * math.sin(t + 0.5)), ("Z", 3 * math.sin(t * 0.5))],
            "Head": [("X", 3 + 2 * math.sin(t + 1.0)), ("Z", 4 * math.sin(t * 0.5 + 0.3))],
            "Jaw_Tusk": [("X", 2 + 2 * math.sin(t * 2))],
        }, mover={"Pelvis": (0, 0, -0.006 * (1 - math.cos(t)) / 2)})
    an.cerrar("reposo")

    def paso(nombre, n, amp, cabeza, bote):
        an.nueva(nombre)
        for f in range(0, n + 1, 2):
            t = 2 * math.pi * f / n
            # paso diagonal: delantera izquierda con trasera derecha
            pata = {"FL": math.sin(t), "BR": math.sin(t), "FR": math.sin(t + math.pi), "BL": math.sin(t + math.pi)}
            pose = {
                "Spine_01": [("Z", 3 * math.sin(t))], "Chest": [("Z", -3 * math.sin(t))],
                "Neck": [("X", cabeza * 0.4)], "Head": [("X", cabeza * 0.6 + 3 * math.sin(2 * t)), ("Z", 2 * math.sin(t))],
                "Jaw_Tusk": [("X", 3)],
            }
            for clave, (pierna, pie) in {"FL": ("LegFront_L", "FootFront_L"), "FR": ("LegFront_R", "FootFront_R"),
                                         "BL": ("LegBack_L", "FootBack_L"), "BR": ("LegBack_R", "FootBack_R")}.items():
                a = amp * pata[clave]
                sube = max(0.0, math.cos(t if clave in ("FL", "BR") else t + math.pi)) * amp * 0.9
                pose[pierna] = [("X", -a)]
                pose[pie] = [("X", a * 0.7 - sube * 0.5)]
            an.fotograma(f, pose, mover={"Pelvis": (0, 0, -bote * abs(math.sin(t)))})
        an.cerrar(nombre)

    paso("caminar", 36, 18, 4, 0.012)
    paso("embestida", 16, 34, 26, 0.045)        # cabeza gacha, zancadas largas

    an.nueva("aturdido")
    for f in range(0, 41, 2):
        t = f / 40
        golpe = math.exp(-3 * t)
        an.fotograma(f, {
            "Head": [("X", 18 * golpe), ("Z", 22 * math.sin(f * 1.3) * golpe)],
            "Neck": [("Z", -10 * math.sin(f * 1.3 + 0.5) * golpe)],
            "Chest": [("Y", 6 * math.sin(f * 0.9) * golpe)],
            "LegFront_L": [("Y", -8 * golpe)], "LegFront_R": [("Y", 8 * golpe)],
            "Jaw_Tusk": [("X", 10 * golpe)],
        }, mover={"Pelvis": (0, 0.03 * golpe, -0.03 * golpe)})
    an.cerrar("aturdido")

    an.nueva("muerte_fractura")
    # se tambalea, se le doblan las patas y los bloques se separan y caen
    salto = {n: Vector((azar.uniform(-1, 1), azar.uniform(-1, 1), 0)).normalized() * azar.uniform(0.10, 0.35)
             for n in NOMBRES if n != "root"}
    giros = {n: (azar.choice("XYZ"), azar.uniform(-70, 70)) for n in NOMBRES}
    for f, k in ((0, 0.0), (10, 0.15), (18, 0.45), (26, 0.8), (34, 1.0), (40, 1.0)):
        pose, mover = {}, {}
        for n in NOMBRES:
            if n == "root":
                continue
            eje, g = giros[n]
            pose[n] = [(eje, g * max(0.0, k - 0.3) / 0.7)]
            if n.startswith(("Leg", "Foot")):
                pose[n].append(("X", 25 * min(1.0, k * 2)))
            caida = -0.55 * max(0.0, k - 0.2) ** 2 if n in ("Pelvis",) else 0.0
            mover[n] = tuple(salto[n] * max(0.0, k - 0.35) / 0.65) if n != "Pelvis" else (0, 0, caida)
        pose["Head"] = pose.get("Head", []) + [("X", 30 * min(1.0, k * 3))]
        an.fotograma(f, pose, mover=mover)
    an.cerrar("muerte_fractura")


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    cuerpo, mats = construir()
    arm, vacios = aparejar(cuerpo)
    animar(arm)
    ap.exportar(SALIDA, arm, [cuerpo] + vacios)
    ap.informe("PETRINO DE GIZA", arm, [cuerpo], SALIDA)
    if "--vistas" in args:
        carpeta = args[args.index("--vistas") + 1]
        os.makedirs(carpeta, exist_ok=True)
        foto = ap.preparar_vistas()
        for nombre, pos, obj, lente in (("1_frente", (0, -4.2, 0.9), (0, 0, 0.55), 50),
                                        ("2_perfil", (4.2, 0, 0.9), (0, 0, 0.55), 50),
                                        ("3_espalda", (0, 4.2, 0.9), (0, 0, 0.55), 50),
                                        ("4_tres_cuartos", (-2.6, -3.0, 1.5), (0, 0, 0.55), 50),
                                        ("5_cabeza", (-0.6, -1.9, 1.05), (0, -0.85, 0.78), 60)):
            foto(os.path.join(carpeta, f"petrino_{nombre}.png"), pos, obj, lente)
        for accion, f, nombre, pos in (("caminar", 9, "a_caminar", (4.2, 0, 0.9)),
                                       ("embestida", 4, "b_embestida", (3.2, -2.4, 1.0)),
                                       ("aturdido", 6, "c_aturdido", (-2.6, -3.0, 1.5)),
                                       ("muerte_fractura", 40, "d_muerte", (-2.6, -3.0, 1.5))):
            arm.animation_data.action = bpy.data.actions[accion]
            bpy.context.scene.frame_set(f)
            foto(os.path.join(carpeta, f"petrino_{nombre}.png"), pos, (0, 0, 0.5), 50)
        arm.animation_data.action = None


if __name__ == "__main__":
    main()
