# -*- coding: utf-8 -*-
"""
Petrino de Giza en 3D: la bestia pétrea cenicienta (enemigo de choque del prólogo).

Ficha: documentacion/referencias_visuales_3d/enemigos/ref_petrino_giza.md; coraza inspirada en el blindaje
de lajas de personajes/bata_castor_mitico_concept_art.jpg (contrato del Kitovu).
  - cuadrúpedo bajo y denso: 1,85 m de largo, 1,15 m a la cruz, 0,85 m de pecho;
  - cuerpo de basalto poroso, cabeza en cuña de pedernal sin ojos (cuencas con resplandor violeta),
    mandíbula con dos colmillos de sílex;
  - coraza dorsal de 5 lajas de pizarra superpuestas y cortantes;
  - patas cortas y anchas con garras de sílex; grietas de corrupción violeta en pecho y flancos.

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
    "roca_basalto_cuerpo": ("#252528", 0.92, 0.0, 0.0),
    "pizarra_coraza_lomo": ("#3c3b42", 0.85, 0.05, 0.0),
    "colmillos_silex": ("#6a6258", 0.45, 0.1, 0.0),
    "vetas_giza_violacea": ("#9b30b0", 0.60, 0.0, 1.8),
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


def construir():
    ap.escena_vacia()
    mats = {n: ap.material(n, *v) for n, v in PALETA.items()}
    r = Roca("Petrino_Cuerpo", mats)
    B, P, V, S, M = "roca_basalto_cuerpo", "pizarra_coraza_lomo", "vetas_giza_violacea", "colmillos_silex", \
        "musgo_seco_grietas"

    # tronco: grupa, vientre, lomo y pecho macizo, con bloques sueltos que rompen la silueta
    r.bloque((0, 0.47, 0.74), (0.31, 0.30, 0.29), B, "Pelvis", semilla=1)
    r.bloque((0, 0.13, 0.72), (0.35, 0.34, 0.30), B, "Spine_01", semilla=2)
    r.bloque((0, -0.17, 0.78), (0.39, 0.30, 0.33), B, "Spine_02", semilla=3)
    r.bloque((0, -0.40, 0.79), (0.42, 0.27, 0.37), B, "Chest", semilla=4)
    r.bloque((0, -0.36, 0.53), (0.30, 0.22, 0.17), B, "Chest", semilla=4.5)          # quilla del pecho
    for s in (-1, 1):
        r.bloque((s * 0.26, -0.05, 0.88), (0.14, 0.18, 0.12), B, "Spine_02", semilla=20 + s)
        r.bloque((s * 0.27, 0.36, 0.84), (0.13, 0.15, 0.12), B, "Pelvis", semilla=22 + s)
    r.bloque((0, -0.62, 0.85), (0.24, 0.19, 0.22), B, "Neck", semilla=5)

    def cuña(q):      # la cabeza se estrecha y se aplana hacia delante, como una punta de pedernal
        k = 1.0 - 0.50 * max(0.0, -q.y) / 0.25
        return Vector((q.x * k, q.y * 1.05, q.z * (0.55 + 0.45 * k) - 0.02 * max(0.0, -q.y) / 0.25))
    r.bloque((0, -0.85, 0.82), (0.21, 0.25, 0.15), B, "Head", sub=3, aspereza=0.10, semilla=6, recorte=cuña,
             tallas=9)
    r.bloque((0, -0.80, 0.93), (0.20, 0.13, 0.05), B, "Head", sub=2, aspereza=0.15, semilla=6.5)      # ceja de roca
    r.bloque((0, -0.85, 0.67), (0.17, 0.21, 0.06), B, "Jaw_Tusk", sub=2, aspereza=0.12, semilla=7, recorte=cuña)
    for s in (-1, 1):
        lado = "L" if s < 0 else "R"
        # cuencas hondas bajo la ceja, con la luz violeta de Giza dentro
        r.bloque((s * 0.095, -0.93, 0.875), (0.045, 0.030, 0.030), "cuenca_oscura", "Head", sub=2, aspereza=0.05,
                 tallas=0)
        r.bloque((s * 0.095, -0.955, 0.873), (0.022, 0.012, 0.014), V, "Head", sub=2, aspereza=0.0, tallas=0)
        # colmillos de sílex desde la mandíbula hacia arriba y delante
        r.cono((s * 0.11, -0.94, 0.68), (s * 0.15, -1.07, 0.85), 0.028, S, "Jaw_Tusk")
        # patas: hombro, pata que baja hasta la pezuña (solapadas) y pezuña ancha con garras
        r.bloque((s * 0.33, -0.33, 0.74), (0.18, 0.20, 0.21), B, f"Shoulder_{lado}", semilla=8 + s)
        r.bloque((s * 0.345, -0.36, 0.42), (0.125, 0.135, 0.30), B, f"LegFront_{lado}", semilla=10 + s)
        r.bloque((s * 0.355, -0.42, 0.10), (0.15, 0.20, 0.10), B, f"FootFront_{lado}", semilla=12 + s)
        r.bloque((s * 0.28, 0.47, 0.64), (0.17, 0.21, 0.21), B, f"LegBack_{lado}", semilla=14 + s)
        r.bloque((s * 0.30, 0.49, 0.38), (0.125, 0.135, 0.25), B, f"LegBack_{lado}", semilla=16 + s)
        r.bloque((s * 0.315, 0.44, 0.10), (0.15, 0.19, 0.10), B, f"FootBack_{lado}", semilla=18 + s)
        for k in (-1, 0, 1):
            for pata, (py, hueso) in (("d", (-0.56, f"FootFront_{lado}")), ("t", (0.28, f"FootBack_{lado}"))):
                base = Vector((s * 0.355 + k * 0.06, py + (0.0 if pata == "d" else 0.0), 0.05))
                r.cono(base, base + Vector((k * 0.01, -0.07, -0.035)), 0.022, S, hueso, lados=5)
        # grietas de Giza en los flancos
        y0 = -0.30
        pts = [(s * 0.40, y0 - 0.05, 0.92), (s * 0.43, y0, 0.84), (s * 0.41, y0 + 0.06, 0.78),
               (s * 0.43, y0 + 0.12, 0.70), (s * 0.40, y0 + 0.20, 0.64)]
        r.veta(pts, V, "Chest")
        r.veta([(s * 0.34, 0.05, 0.86), (s * 0.37, 0.12, 0.78), (s * 0.35, 0.20, 0.72)], V, "Spine_01")
        # líquenes muertos en las juntas
        r.bloque((s * 0.30, -0.20, 0.92), (0.06, 0.05, 0.02), M, "Spine_02", sub=2, aspereza=0.3)
        r.bloque((s * 0.24, 0.32, 0.86), (0.05, 0.06, 0.02), M, "Pelvis", sub=2, aspereza=0.3)
    # grieta del pecho
    r.veta([(0.0, -0.66, 0.93), (0.05, -0.665, 0.85), (-0.03, -0.665, 0.77), (0.04, -0.66, 0.69)], V, "Chest")

    # coraza: 5 lajas de pizarra superpuestas, de la cruz a la grupa, con cresta cortante
    lajas = [(-0.42, 1.06, "Chest", 0.62), (-0.22, 1.08, "Spine_02", 0.66), (0.00, 1.05, "Spine_01", 0.64),
             (0.22, 1.02, "Spine_01", 0.60), (0.42, 0.98, "Pelvis", 0.54)]
    for k, (y, z, hueso, ancho) in enumerate(lajas):
        giro = Matrix.Rotation(math.radians(-14), 3, "X") @ Matrix.Rotation(math.radians(azar.uniform(-4, 4)), 3, "Z")
        r.losa((0, y, z), (ancho, 0.30, 0.045), P, hueso, giro, cresta=0.10)
        for s in (-1, 1):   # lajas laterales que bajan por los costados
            g2 = Matrix.Rotation(math.radians(s * 48), 3, "Y") @ giro
            r.losa((s * ancho * 0.42, y + 0.02, z - 0.16), (0.24, 0.26, 0.035), P, hueso, g2, cresta=0.04)
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
