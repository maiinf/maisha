# -*- coding: utf-8 -*-
"""
modelar_detalles_huerto.py - Modelador AAA de los detalles de huerto y atrezzo de El Kitovu.
1. valla_madera.glb (Valla rústica de cedro con musgo y clavos forjados)
2. zanahoria_huerto.glb (Bancal de tierra asfixiada con hortalizas marchitas)
3. farol_madera.glb (Poste de madera con farol de forja y luz ámbar)

Uso:
    blender -b --factory-startup -P herramientas/blender/modelar_detalles_huerto.py
"""

import math
import os
import sys
import bpy
import bmesh
from mathutils import Matrix, Vector

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CARPETA_SALIDA = os.path.join(RAIZ, "modelos", "entorno")
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
    col = bpy.data.collections.new("Coleccion_Huerto")
    bpy.context.scene.collection.children.link(col)


def exportar_seleccion(ruta_glb):
    bpy.ops.export_scene.gltf(
        filepath=ruta_glb,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )
    print(f"[OK] Exportado: {ruta_glb}")


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


# ===========================================================================
# 1. VALLA RÚSTICA DE MADERA DE CEDRO
# ===========================================================================
def modelar_valla():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Huerto"]
    mat_madera = crear_material("madera_cedro_valla", "#544638", rugosidad=0.88, metal=0.0)

    bm = bmesh.new()

    # Dos postes verticales cilíndricos en los extremos (x = -1.15 y +1.15, altura 1.05m)
    for sx in (-1.15, 1.15):
        crear_cilindro(
            bm,
            segments=12,
            radius=0.07,
            depth=1.05,
            matrix=Matrix.Translation(Vector((sx, 0.0, 0.525))),
        )
        # Remate cónico en la parte superior del poste
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            segments=10,
            radius1=0.07,
            radius2=0.01,
            depth=0.10,
            matrix=Matrix.Translation(Vector((sx, 0.0, 1.10))),
        )

    # Dos travesaños horizontales (longitud 2.30 m)
    for sz in (0.35, 0.75):
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.Translation(Vector((0.0, 0.02, sz)))
            @ Matrix.Scale(2.30, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(0.06, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(0.08, 4, Vector((0, 0, 1))),
        )

    # 5 estacas verticales irregulares
    for i, sx in enumerate([-0.80, -0.40, 0.0, 0.40, 0.80]):
        inclinacion = (i - 2) * 2.5
        altura = 0.90 + (0.05 if i % 2 == 0 else -0.04)
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.Translation(Vector((sx, -0.02, altura / 2.0)))
            @ Matrix.Rotation(math.radians(inclinacion), 4, "Y")
            @ Matrix.Scale(0.09, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(0.03, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(altura, 4, Vector((0, 0, 1))),
        )

    mesh = bpy.data.meshes.new("Valla_Madera_Cedro")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Valla_Madera_Cedro", mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat_madera)

    bpy.ops.object.select_all(action="SELECT")
    ruta = os.path.join(CARPETA_SALIDA, "valla_madera.glb")
    exportar_seleccion(ruta)


# ===========================================================================
# 2. BANCAL DEL HUERTO ASFIXIADO
# ===========================================================================
def modelar_huerto():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Huerto"]
    mat_tierra = crear_material("tierra_huerto_asfixiado", "#3a3227", rugosidad=0.96, metal=0.0)
    mat_vegetal = crear_material("zanahoria_marchita", "#886b3a", rugosidad=0.85, metal=0.0)

    bm = bmesh.new()

    # Montículo alargado de tierra labrada (1.80 m x 1.20 m)
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 0.08)))
        @ Matrix.Scale(1.85, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(1.20, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.16, 4, Vector((0, 0, 1))),
    )

    # 4 Brotes de zanahorias asomando en los surcos
    for sx, sy in [(-0.55, -0.25), (-0.15, 0.25), (0.25, -0.20), (0.60, 0.20)]:
        # Punta de la zanahoria que asoma
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            segments=8,
            radius1=0.045,
            radius2=0.015,
            depth=0.12,
            matrix=Matrix.Translation(Vector((sx, sy, 0.18))),
        )
        # Hojas marchitas
        for ang in (0, 120, 240):
            rad = math.radians(ang)
            bmesh.ops.create_cone(
                bm,
                cap_ends=True,
                segments=4,
                radius1=0.02,
                radius2=0.005,
                depth=0.15,
                matrix=Matrix.Translation(Vector((sx + math.cos(rad) * 0.03, sy + math.sin(rad) * 0.03, 0.26)))
                @ Matrix.Rotation(rad, 4, "Z")
                @ Matrix.Rotation(math.radians(35), 4, "Y"),
            )

    mesh = bpy.data.meshes.new("Huerto_Asfixiado")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Huerto_Asfixiado", mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat_tierra)

    bpy.ops.object.select_all(action="SELECT")
    ruta = os.path.join(CARPETA_SALIDA, "zanahoria_huerto.glb")
    exportar_seleccion(ruta)


# ===========================================================================
# 3. FAROL RÚSTICO DE MADERA Y FORJA
# ===========================================================================
def modelar_farol():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Huerto"]
    mat_madera = crear_material("madera_poste_farol", "#463a2f", rugosidad=0.88, metal=0.0)
    mat_hierro = crear_material("hierro_forja_farol", "#282627", rugosidad=0.65, metal=0.60)
    mat_luz = crear_material(
        "luz_farol_calida",
        "#ffcc44",
        rugosidad=0.15,
        metal=0.0,
        emision=2.8,
        color_emision="#ffa822",
    )

    bm = bmesh.new()

    # Poste principal de madera (altura 2.20 m)
    crear_cilindro(
        bm,
        segments=12,
        radius=0.08,
        depth=2.20,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 1.10))),
    )

    # Brazo en escuadra de hierro forjado
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.Translation(Vector((0.25, 0.0, 2.15)))
        @ Matrix.Scale(0.48, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.04, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.04, 4, Vector((0, 0, 1))),
    )

    # Farol colgante en x = 0.45 m
    # Tejadillo cónico del farol
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=4,
        radius1=0.16,
        radius2=0.02,
        depth=0.12,
        matrix=Matrix.Translation(Vector((0.45, 0.0, 2.10)))
        @ Matrix.Rotation(math.radians(45), 4, "Z"),
    )
    # Cuerpo de vidrio ámbar iluminado
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=4,
        radius1=0.14,
        radius2=0.09,
        depth=0.22,
        matrix=Matrix.Translation(Vector((0.45, 0.0, 1.95)))
        @ Matrix.Rotation(math.radians(45), 4, "Z"),
    )

    mesh = bpy.data.meshes.new("Farol_Madera_Forja")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Farol_Madera_Forja", mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat_madera)

    bpy.ops.object.select_all(action="SELECT")
    ruta = os.path.join(CARPETA_SALIDA, "farol_madera.glb")
    exportar_seleccion(ruta)


def main():
    print("=== MODELANDO DETALLES DE HUERTO Y FAROL DE EL KITOVU ===")
    modelar_valla()
    modelar_huerto()
    modelar_farol()
    print("=== DETALLES GENERADOS CON ÉXITO ===")


if __name__ == "__main__":
    main()
