# -*- coding: utf-8 -*-
"""
modelar_petrino_giza.py - Modelador AAA de Petrino de Giza (Bestia Pétrea del Prólogo).
Según documentacion/referencias_visuales_3d/enemigos/ref_petrino_giza.md.

Dimensiones: 1.85 m longitud, 1.15 m altura a la cruz, 0.85 m anchura de pecho.
Materiales: basalto volcánico oscuro, placas de pizarra en el lomo, colmillos de sílex,
grietas y ojos de cuarzo violeta de Giza (emisivo).

Uso:
    blender -b --factory-startup -P herramientas/blender/modelar_petrino_giza.py
"""

import math
import os
import sys
import bpy
import bmesh
from mathutils import Matrix, Vector

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CARPETA_SALIDA = os.path.join(RAIZ, "modelos", "enemigos")
SALIDA_GLB = os.path.join(CARPETA_SALIDA, "petrino_giza.glb")
os.makedirs(CARPETA_SALIDA, exist_ok=True)


def _lineal(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(hexa):
    h = hexa.lstrip("#")
    return [_lineal(int(h[i : i + 2], 16) / 255.0) for i in (0, 2, 4)]


def crear_material(nombre, hexa, rugosidad=0.85, metal=0.0, emision=0.0, color_emision=None):
    m = bpy.data.materials.get(nombre)
    if m is None:
        m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    c = rgb(hexa) + [1.0]
    bsdf.inputs["Base Color"].default_value = c
    bsdf.inputs["Roughness"].default_value = rugosidad
    bsdf.inputs["Metallic"].default_value = metal
    if emision > 0.0:
        c_em = rgb(color_emision) + [1.0] if color_emision else c
        bsdf.inputs["Emission Color"].default_value = c_em
        bsdf.inputs["Emission Strength"].default_value = emision
    return m


def limpiar_escena():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Coleccion_Petrino")
    bpy.context.scene.collection.children.link(col)


def crear_cilindro(bm, radius, depth, segments=16, matrix=Matrix()):
    return bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=depth,
        matrix=matrix,
    )


def modelar_petrino():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Petrino"]

    mat_basalto = crear_material("roca_basalto_cuerpo", "#252528", rugosidad=0.92, metal=0.0)
    mat_pizarra = crear_material("pizarra_coraza_lomo", "#3c3b42", rugosidad=0.85, metal=0.05)
    mat_silex = crear_material("colmillos_silex", "#6a6258", rugosidad=0.45, metal=0.1)
    mat_giza = crear_material(
        "vetas_giza_violacea",
        "#7a288e",
        rugosidad=0.40,
        metal=0.1,
        emision=2.2,
        color_emision="#9b30b0",
    )

    # 1. Cuerpo principal (torso de basalto masivo)
    bm_cuerpo = bmesh.new()

    # Masa del tórax y abdomen (longitud 1.35 m, ancho 0.78 m, alto 0.70 m)
    bmesh.ops.create_uvsphere(
        bm_cuerpo,
        u_segments=24,
        v_segments=16,
        radius=0.55,
        matrix=Matrix.Translation(Vector((0.0, 0.05, 0.82)))
        @ Matrix.Scale(0.78, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(1.45, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.85, 4, Vector((0, 0, 1))),
    )

    # Cabeza en forma de cuña de pedernal (apuntando hacia -Y)
    bmesh.ops.create_cone(
        bm_cuerpo,
        cap_ends=True,
        segments=16,
        radius1=0.34,
        radius2=0.12,
        depth=0.68,
        matrix=Matrix.Translation(Vector((0.0, -0.85, 0.75)))
        @ Matrix.Rotation(math.radians(-80), 4, "X"),
    )

    # Cuatro patas de roca pesada con pezuñas de sílex
    posiciones_patas = [
        (-0.35, -0.42, 0.42),  # Delantera Izquierda
        (0.35, -0.42, 0.42),   # Delantera Derecha
        (-0.32, 0.48, 0.42),   # Trasera Izquierda
        (0.32, 0.48, 0.42),    # Trasera Derecha
    ]
    for px, py, pz in posiciones_patas:
        # Pata
        crear_cilindro(
            bm_cuerpo,
            segments=12,
            radius=0.13,
            depth=0.75,
            matrix=Matrix.Translation(Vector((px, py, pz))),
        )
        # Pezuña maciza en la base
        bmesh.ops.create_cube(
            bm_cuerpo,
            size=1.0,
            matrix=Matrix.Translation(Vector((px, py - 0.03, 0.08)))
            @ Matrix.Scale(0.24, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(0.28, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(0.14, 4, Vector((0, 0, 1))),
        )

    mesh_cuerpo = bpy.data.meshes.new("Petrino_Cuerpo")
    bm_cuerpo.to_mesh(mesh_cuerpo)
    bm_cuerpo.free()

    obj_cuerpo = bpy.data.objects.new("Petrino_Cuerpo", mesh_cuerpo)
    col.objects.link(obj_cuerpo)
    obj_cuerpo.data.materials.append(mat_basalto)

    # 2. Coraza dorsal de placas de pizarra superpuestas
    bm_coraza = bmesh.new()
    for i, py in enumerate([-0.35, -0.10, 0.15, 0.40, 0.62]):
        escala_x = 0.82 - (i * 0.05)
        bmesh.ops.create_cone(
            bm_coraza,
            cap_ends=True,
            segments=10,
            radius1=0.42 * escala_x,
            radius2=0.08,
            depth=0.38,
            matrix=Matrix.Translation(Vector((0.0, py, 1.15 - (i * 0.04))))
            @ Matrix.Rotation(math.radians(-25), 4, "X")
            @ Matrix.Scale(1.0, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(0.55, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(1.0, 4, Vector((0, 0, 1))),
        )

    mesh_coraza = bpy.data.meshes.new("Petrino_Coraza")
    bm_coraza.to_mesh(mesh_coraza)
    bm_coraza.free()

    obj_coraza = bpy.data.objects.new("Petrino_Coraza", mesh_coraza)
    col.objects.link(obj_coraza)
    obj_coraza.data.materials.append(mat_pizarra)

    # 3. Colmillos de pedernal / sílex
    bm_colmillos = bmesh.new()
    for sx in (-0.20, 0.20):
        bmesh.ops.create_cone(
            bm_colmillos,
            cap_ends=True,
            segments=10,
            radius1=0.07,
            radius2=0.015,
            depth=0.45,
            matrix=Matrix.Translation(Vector((sx, -1.05, 0.65)))
            @ Matrix.Rotation(math.radians(35), 4, "X")
            @ Matrix.Rotation(math.radians(-15 if sx < 0 else 15), 4, "Y"),
        )

    mesh_colmillos = bpy.data.meshes.new("Petrino_Colmillos")
    bm_colmillos.to_mesh(mesh_colmillos)
    bm_colmillos.free()

    obj_colmillos = bpy.data.objects.new("Petrino_Colmillos", mesh_colmillos)
    col.objects.link(obj_colmillos)
    obj_colmillos.data.materials.append(mat_silex)

    # 4. Ojos de resplandor violeta de Giza y grietas emisivas
    bm_giza = bmesh.new()
    for sx in (-0.16, 0.16):
        bmesh.ops.create_cube(
            bm_giza,
            size=1.0,
            matrix=Matrix.Translation(Vector((sx, -0.88, 0.82)))
            @ Matrix.Rotation(math.radians(-20), 4, "X")
            @ Matrix.Scale(0.06, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(0.12, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(0.04, 4, Vector((0, 0, 1))),
        )

    mesh_giza = bpy.data.meshes.new("Petrino_Ojos_Giza")
    bm_giza.to_mesh(mesh_giza)
    bm_giza.free()

    obj_giza = bpy.data.objects.new("Petrino_Ojos_Giza", mesh_giza)
    col.objects.link(obj_giza)
    obj_giza.data.materials.append(mat_giza)

    # Exportar GLB completo
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=SALIDA_GLB,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )
    print(f"[OK] Petrino de Giza exportado con éxito en: {SALIDA_GLB}")


def main():
    print("=== MODELANDO PETRINO DE GIZA EN BLENDER ===")
    modelar_petrino()
    print("=== FINALIZADO CON ÉXITO ===")


if __name__ == "__main__":
    main()
