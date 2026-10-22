# -*- coding: utf-8 -*-
"""
modelar_mzee_shamba.py - Modelador AAA de Mzee Shamba (El Sabio Patriarca Castor Bípedo con Gafas).
Según documentacion/referencias_visuales_3d/personajes/ref_mzee_shamba_castor_mitico.md.

Dimensiones: 1.45 m altura bípeda.
Características: Gafas redondas de latón sobre el hocico, chaleco de pana, camisa crema,
cola plana de castor como tercer apoyo, barba canosa y bastón de botánico.

Uso:
    blender -b --factory-startup -P herramientas/blender/modelar_mzee_shamba.py
"""

import math
import os
import sys
import bpy
import bmesh
from mathutils import Matrix, Vector

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CARPETA_SALIDA = os.path.join(RAIZ, "modelos", "personajes")
SALIDA_GLB = os.path.join(CARPETA_SALIDA, "mzee_shamba.glb")
os.makedirs(CARPETA_SALIDA, exist_ok=True)


def _lineal(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(hexa):
    h = hexa.lstrip("#")
    return [_lineal(int(h[i : i + 2], 16) / 255.0) for i in (0, 2, 4)]


def crear_material(nombre, hexa, rugosidad=0.85, metal=0.0, emision=0.0):
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
        bsdf.inputs["Emission Color"].default_value = c
        bsdf.inputs["Emission Strength"].default_value = emision
    return m


def limpiar_escena():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Coleccion_Shamba")
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


def modelar_shamba():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Shamba"]

    # Materiales de la paleta oficial
    mat_pelaje = crear_material("pelaje_castor_canoso", "#4a3a2d", rugosidad=0.85, metal=0.0)
    mat_chaleco = crear_material("chaleco_pana_sabio", "#6b4f35", rugosidad=0.80, metal=0.0)
    mat_camisa = crear_material("camisa_algodon_crudo", "#e0d8c3", rugosidad=0.85, metal=0.0)
    mat_cola = crear_material("cola_cuero_castor", "#3b2e24", rugosidad=0.70, metal=0.0)
    mat_gafas = crear_material("gafas_sabio_laton", "#9c8144", rugosidad=0.30, metal=0.85)
    mat_lentes = crear_material("cristal_lentes", "#c8dce4", rugosidad=0.10, metal=0.05)
    mat_baston = crear_material("baston_azada_roble", "#423223", rugosidad=0.75, metal=0.0)
    mat_barba = crear_material("barba_canosa_trigo", "#d5c9aa", rugosidad=0.90, metal=0.0)

    # 1. Cuerpo, Piernas y Brazos Bípedos
    bm_cuerpo = bmesh.new()

    # Pelvis y vientre rechoncho de anciano castor (z = 0.40 a 0.85)
    bmesh.ops.create_uvsphere(
        bm_cuerpo,
        u_segments=20,
        v_segments=16,
        radius=0.36,
        matrix=Matrix.Translation(Vector((0.0, -0.02, 0.65)))
        @ Matrix.Scale(0.92, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(1.10, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(1.15, 4, Vector((0, 0, 1))),
    )

    # Dos piernas cortas y robustas
    for sx in (-0.18, 0.18):
        crear_cilindro(
            bm_cuerpo,
            segments=12,
            radius=0.11,
            depth=0.42,
            matrix=Matrix.Translation(Vector((sx, 0.0, 0.22))),
        )
        # Pies palmeados de castor apoyados en el suelo
        bmesh.ops.create_cube(
            bm_cuerpo,
            size=1.0,
            matrix=Matrix.Translation(Vector((sx, -0.08, 0.05)))
            @ Matrix.Scale(0.18, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(0.28, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(0.10, 4, Vector((0, 0, 1))),
        )

    # Dos brazos bípedos
    # Brazo izquierdo (relajado al costado)
    crear_cilindro(
        bm_cuerpo,
        segments=10,
        radius=0.08,
        depth=0.48,
        matrix=Matrix.Translation(Vector((-0.34, 0.0, 0.78)))
        @ Matrix.Rotation(math.radians(-12), 4, "Y"),
    )
    # Brazo derecho (adelantado sosteniendo el bastón)
    crear_cilindro(
        bm_cuerpo,
        segments=10,
        radius=0.08,
        depth=0.48,
        matrix=Matrix.Translation(Vector((0.32, -0.12, 0.82)))
        @ Matrix.Rotation(math.radians(25), 4, "X")
        @ Matrix.Rotation(math.radians(10), 4, "Y"),
    )

    mesh_cuerpo = bpy.data.meshes.new("Shamba_Cuerpo")
    bm_cuerpo.to_mesh(mesh_cuerpo)
    bm_cuerpo.free()

    obj_cuerpo = bpy.data.objects.new("Shamba_Cuerpo", mesh_cuerpo)
    col.objects.link(obj_cuerpo)
    obj_cuerpo.data.materials.append(mat_pelaje)

    # 2. Cabeza de Castor Venerable, Hocico y Orejitas
    bm_cabeza = bmesh.new()

    # Cráneo redondeado (z = 1.05 a 1.35 m)
    bmesh.ops.create_uvsphere(
        bm_cabeza,
        u_segments=20,
        v_segments=16,
        radius=0.22,
        matrix=Matrix.Translation(Vector((0.0, -0.04, 1.18)))
        @ Matrix.Scale(0.95, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(1.10, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.95, 4, Vector((0, 0, 1))),
    )

    # Hocico prominente de castor
    bmesh.ops.create_uvsphere(
        bm_cabeza,
        u_segments=16,
        v_segments=12,
        radius=0.13,
        matrix=Matrix.Translation(Vector((0.0, -0.22, 1.14)))
        @ Matrix.Scale(1.1, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(1.3, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.8, 4, Vector((0, 0, 1))),
    )

    # Pequeñas orejas redondas de castor
    for sx in (-0.17, 0.17):
        bmesh.ops.create_uvsphere(
            bm_cabeza,
            u_segments=12,
            v_segments=8,
            radius=0.045,
            matrix=Matrix.Translation(Vector((sx, 0.05, 1.34)))
            @ Matrix.Scale(0.4, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(1.0, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(1.0, 4, Vector((0, 0, 1))),
        )

    mesh_cabeza = bpy.data.meshes.new("Shamba_Cabeza")
    bm_cabeza.to_mesh(mesh_cabeza)
    bm_cabeza.free()

    obj_cabeza = bpy.data.objects.new("Shamba_Cabeza", mesh_cabeza)
    col.objects.link(obj_cabeza)
    obj_cabeza.data.materials.append(mat_pelaje)

    # 3. Barba de Anciano entretejida con espigas secas
    bm_barba = bmesh.new()
    bmesh.ops.create_cone(
        bm_barba,
        cap_ends=True,
        segments=12,
        radius1=0.16,
        radius2=0.03,
        depth=0.28,
        matrix=Matrix.Translation(Vector((0.0, -0.22, 1.02)))
        @ Matrix.Rotation(math.radians(-20), 4, "X"),
    )
    mesh_barba = bpy.data.meshes.new("Shamba_Barba")
    bm_barba.to_mesh(mesh_barba)
    bm_barba.free()

    obj_barba = bpy.data.objects.new("Shamba_Barba", mesh_barba)
    col.objects.link(obj_barba)
    obj_barba.data.materials.append(mat_barba)

    # 4. Gafas Redondas de Sabio Botánico sobre el hocico
    bm_gafas = bmesh.new()
    for sx in (-0.08, 0.08):
        # Aro metálico
        crear_cilindro(
            bm_gafas,
            segments=16,
            radius=0.045,
            depth=0.015,
            matrix=Matrix.Translation(Vector((sx, -0.28, 1.21)))
            @ Matrix.Rotation(math.radians(80), 4, "X"),
        )
    # Puente de unión de las gafas
    crear_cilindro(
        bm_gafas,
        segments=8,
        radius=0.008,
        depth=0.08,
        matrix=Matrix.Translation(Vector((0.0, -0.28, 1.21)))
        @ Matrix.Rotation(math.radians(90), 4, "Y"),
    )

    mesh_gafas = bpy.data.meshes.new("Shamba_Gafas")
    bm_gafas.to_mesh(mesh_gafas)
    bm_gafas.free()

    obj_gafas = bpy.data.objects.new("Shamba_Gafas", mesh_gafas)
    col.objects.link(obj_gafas)
    obj_gafas.data.materials.append(mat_gafas)

    # 5. Chaleco de Pana y Camisa de Algodón
    bm_ropa = bmesh.new()
    # Chaleco rústico sobre el torso
    bmesh.ops.create_cone(
        bm_ropa,
        cap_ends=True,
        segments=16,
        radius1=0.37,
        radius2=0.28,
        depth=0.52,
        matrix=Matrix.Translation(Vector((0.0, -0.02, 0.78))),
    )
    mesh_ropa = bpy.data.meshes.new("Shamba_Chaleco")
    bm_ropa.to_mesh(mesh_ropa)
    bm_ropa.free()

    obj_ropa = bpy.data.objects.new("Shamba_Chaleco", mesh_ropa)
    col.objects.link(obj_ropa)
    obj_ropa.data.materials.append(mat_chaleco)

    # 6. Emblemática Cola de Castor como tercer punto de apoyo
    bm_cola = bmesh.new()
    # Cola aplanada de castor: longitud 0.65 m, ancho 0.28 m, espesor 0.06 m
    # Nace en z = 0.45 m y baja en rampa suave hasta tocar el suelo en z = 0.03 m
    bmesh.ops.create_cube(
        bm_cola,
        size=1.0,
        matrix=Matrix.Translation(Vector((0.0, 0.42, 0.22)))
        @ Matrix.Rotation(math.radians(-35), 4, "X")
        @ Matrix.Scale(0.28, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.65, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.06, 4, Vector((0, 0, 1))),
    )
    mesh_cola = bpy.data.meshes.new("Shamba_Cola")
    bm_cola.to_mesh(mesh_cola)
    bm_cola.free()

    obj_cola = bpy.data.objects.new("Shamba_Cola", mesh_cola)
    col.objects.link(obj_cola)
    obj_cola.data.materials.append(mat_cola)

    # 7. Bastón Botánico con Azadilla en la mano derecha
    bm_baston = bmesh.new()
    # Vara de roble (longitud 1.35 m, z de 0 a 1.35 m en x = 0.42 m)
    crear_cilindro(
        bm_baston,
        segments=10,
        radius=0.022,
        depth=1.35,
        matrix=Matrix.Translation(Vector((0.38, -0.22, 0.675))),
    )
    # Pequeña hoja de azadilla de latón en la base
    bmesh.ops.create_cube(
        bm_baston,
        size=1.0,
        matrix=Matrix.Translation(Vector((0.38, -0.26, 0.06)))
        @ Matrix.Scale(0.08, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.12, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.02, 4, Vector((0, 0, 1))),
    )
    mesh_baston = bpy.data.meshes.new("Shamba_Baston")
    bm_baston.to_mesh(mesh_baston)
    bm_baston.free()

    obj_baston = bpy.data.objects.new("Shamba_Baston", mesh_baston)
    col.objects.link(obj_baston)
    obj_baston.data.materials.append(mat_baston)

    # Exportar modelo final
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=SALIDA_GLB,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )
    print(f"[OK] Mzee Shamba exportado con éxito en: {SALIDA_GLB}")


def main():
    print("=== MODELANDO MZEE SHAMBA (CASTOR SABIO BÍPEDO CON GAFAS) ===")
    modelar_shamba()
    print("=== FINALIZADO CON ÉXITO ===")


if __name__ == "__main__":
    main()
