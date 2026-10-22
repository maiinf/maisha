# -*- coding: utf-8 -*-
"""
reconstruir_maisha_base.py - Generación AAA de Maisha sobre Base Mesh de Blender Studio (CC0).
Elimina los cilindros matemáticos procedimentales y utiliza la topología profesional estilizada
de 12.502 quads ('GEO-body_male_stylized').

Uso:
    blender -b --factory-startup -P herramientas/blender/reconstruir_maisha_base.py
    blender -b --factory-startup -P herramientas/blender/reconstruir_maisha_base.py -- --vistas documentacion/referencias_visuales_3d/personajes/vistas_maisha_base
"""

import math
import os
import sys
import bpy
import bmesh
from mathutils import Matrix, Vector

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BUNDLE_BLEND = os.path.join(
    RAIZ,
    "herramientas",
    "blender",
    "recursos",
    "human_base_meshes",
    "human-base-meshes-bundle-v1.4.1",
    "human_base_meshes_bundle.blend",
)
CARPETA_SALIDA = os.path.join(RAIZ, "modelos", "personajes")
SALIDA_GLB = os.path.join(CARPETA_SALIDA, "maisha.glb")

ALTURA_OBJETIVO = 1.70  # Metros oficiales de Maisha


def _lineal(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(hexa):
    h = hexa.lstrip("#")
    return [_lineal(int(h[i : i + 2], 16) / 255.0) for i in (0, 2, 4)]


def crear_material(nombre, hexa, rugosidad=0.5, metal=0.0, emision=0.0, color_emision=None):
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
        col_em = rgb(color_emision) + [1.0] if color_emision else c
        bsdf.inputs["Emission Color"].default_value = col_em
        bsdf.inputs["Emission Strength"].default_value = emision
    return m


def limpiar_escena():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Coleccion_Maisha")
    bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[col.name]


def importar_base_mesh():
    if not os.path.isfile(BUNDLE_BLEND):
        raise FileNotFoundError(f"No se encontró el paquete de base meshes en: {BUNDLE_BLEND}")

    nombres_objetos = [
        "GEO-body_male_stylized",
        "GEO-body_male_stylized.eye.L",
        "GEO-body_male_stylized.eye.R",
    ]

    with bpy.data.libraries.load(BUNDLE_BLEND) as (data_from, data_to):
        data_to.objects = [n for n in nombres_objetos if n in data_from.objects]

    col = bpy.data.collections["Coleccion_Maisha"]
    objetos_importados = []
    cuerpo = None

    for obj in data_to.objects:
        col.objects.link(obj)
        objetos_importados.append(obj)
        if obj.name == "GEO-body_male_stylized":
            cuerpo = obj

    if not cuerpo:
        raise RuntimeError("No se pudo cargar el cuerpo base estilizado")

    # Limpiar modificadores no deseados o rotos
    for obj in objetos_importados:
        for mod in list(obj.modifiers):
            if not mod.name.startswith("Subdivision") and not mod.name.startswith("Armature"):
                obj.modifiers.remove(mod)

    # Calcular bounding box y escalar a 1.70m
    bpy.context.view_layer.update()
    cuerpo_z_min = min((cuerpo.matrix_world @ Vector(v)).z for v in cuerpo.bound_box)
    cuerpo_z_max = max((cuerpo.matrix_world @ Vector(v)).z for v in cuerpo.bound_box)
    altura_actual = cuerpo_z_max - cuerpo_z_min
    factor_escala = ALTURA_OBJETIVO / altura_actual

    for obj in objetos_importados:
        obj.scale *= factor_escala
        # Alinear pies a z = 0
        obj.location.z -= cuerpo_z_min * factor_escala

    bpy.ops.object.select_all(action="DESELECT")
    for obj in objetos_importados:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = cuerpo
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=True)

    # Asignar materiales PBR
    mat_piel = crear_material("piel_humanizada", "#e8ded0", rugosidad=0.60, metal=0.0)
    mat_ojo = crear_material("ojo_esclerotica", "#f4efe8", rugosidad=0.20, metal=0.0)
    cuerpo.data.materials.clear()
    cuerpo.data.materials.append(mat_piel)

    for obj in objetos_importados:
        if "eye" in obj.name:
            obj.data.materials.clear()
            obj.data.materials.append(mat_ojo)

    return cuerpo, objetos_importados


def modelar_cabello(cuerpo):
    """Crea una cabellera suave de mechones orgánicos que enmarcan el rostro sin astas."""
    bm = bmesh.new()
    col_obj = bpy.data.collections["Coleccion_Maisha"]

    # Crear una masa suave de cabello envolvente sobre la cabeza
    # Cabeza en el modelo 1.70m está entre z = 1.45 y 1.70
    z_centro_cabeza = 1.56
    y_centro_cabeza = -0.015

    bmesh.ops.create_uvsphere(
        bm,
        u_segments=24,
        v_segments=16,
        radius=0.118,
    )
    # Deformar hacia atrás y lados para caída de cabello
    for v in bm.verts:
        v.co.x *= 1.05
        v.co.y = (v.co.y * 1.15) - 0.02
        v.co.z = (v.co.z * 1.02) + z_centro_cabeza
        v.co.y += y_centro_cabeza

        # Recortar la parte frontal/rostro
        if v.co.y < y_centro_cabeza and v.co.z < z_centro_cabeza + 0.05:
            v.co.y += 0.04
            v.co.z += 0.03

    # Mechones que caen por los hombros y nuca
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=12,
        radius1=0.065,
        radius2=0.015,
        depth=0.28,
        matrix=Matrix.Translation(Vector((0.0, -0.08, z_centro_cabeza - 0.14)))
        @ Matrix.Rotation(math.radians(-15), 4, "X"),
    )

    mesh = bpy.data.meshes.new("Cabello_Viajero")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Cabello_Viajero", mesh)
    col_obj.objects.link(obj)

    mat_pelo = crear_material("cabello_viajero", "#3b3127", rugosidad=0.75, metal=0.0)
    obj.data.materials.append(mat_pelo)

    mod_sub = obj.modifiers.new("Subdivision", "SUBSURF")
    mod_sub.levels = 1
    return obj


def modelar_tunica_y_capa():
    """Modela la túnica de lino asimétrica y la capa de viajero."""
    bm_tunica = bmesh.new()
    col_obj = bpy.data.collections["Coleccion_Maisha"]

    # Túnica: Torso cilíndrico contorneado de z = 0.85 a 1.42
    bmesh.ops.create_cone(
        bm_tunica,
        cap_ends=True,
        cap_tris=False,
        segments=20,
        radius1=0.24,  # Bajo (caderas)
        radius2=0.21,  # Alto (pecho)
        depth=0.58,
        matrix=Matrix.Translation(Vector((0.0, -0.01, 1.14))),
    )
    # Aplanar suavemente en Y para adaptarse al torso
    for v in bm_tunica.verts:
        v.co.y *= 0.72

    mesh_tunica = bpy.data.meshes.new("Tunica_Lino")
    bm_tunica.to_mesh(mesh_tunica)
    bm_tunica.free()

    obj_tunica = bpy.data.objects.new("Tunica_Lino", mesh_tunica)
    col_obj.objects.link(obj_tunica)
    mat_tunica = crear_material("tunica_lino_arena", "#d5caa8", rugosidad=0.85, metal=0.0)
    obj_tunica.data.materials.append(mat_tunica)

    # Capa de viajero sobre el hombro izquierdo
    bm_capa = bmesh.new()
    bmesh.ops.create_cone(
        bm_capa,
        cap_ends=True,
        cap_tris=False,
        segments=16,
        radius1=0.22,
        radius2=0.10,
        depth=0.62,
        matrix=Matrix.Translation(Vector((-0.18, -0.04, 1.18)))
        @ Matrix.Rotation(math.radians(12), 4, "Y")
        @ Matrix.Rotation(math.radians(-10), 4, "X"),
    )
    for v in bm_capa.verts:
        v.co.y *= 0.65

    mesh_capa = bpy.data.meshes.new("Capa_Viajero")
    bm_capa.to_mesh(mesh_capa)
    bm_capa.free()

    obj_capa = bpy.data.objects.new("Capa_Viajero", mesh_capa)
    col_obj.objects.link(obj_capa)
    mat_capa = crear_material("capa_viaje_musgo", "#46543b", rugosidad=0.85, metal=0.0)
    obj_capa.data.materials.append(mat_capa)

    return obj_tunica, obj_capa


def modelar_corazon_y_cetro():
    """Modela el Corazón de Asili en el esternón y el Cetro de Raíz."""
    col_obj = bpy.data.collections["Coleccion_Maisha"]

    # Corazón de Asili (gema dorada incrustada en z = 1.28)
    bm_cor = bmesh.new()
    bmesh.ops.create_icosphere(
        bm_cor,
        subdivisions=2,
        radius=0.038,
        matrix=Matrix.Translation(Vector((0.0, 0.12, 1.28))),
    )
    for v in bm_cor.verts:
        v.co.y *= 0.5  # Achatado contra el pecho
        v.co.z *= 1.25

    mesh_cor = bpy.data.meshes.new("Corazon_Asili")
    bm_cor.to_mesh(mesh_cor)
    bm_cor.free()

    obj_cor = bpy.data.objects.new("Corazon_Asili", mesh_cor)
    col_obj.objects.link(obj_cor)
    mat_cor = crear_material(
        "corazon_asili_oro",
        "#f5c238",
        rugosidad=0.15,
        metal=0.1,
        emision=2.2,
        color_emision="#ffcc33",
    )
    obj_cor.data.materials.append(mat_cor)

    # Cetro de Raíz en la mano derecha (x ≈ 0.42, y ≈ 0.05, z de 0 a 1.75)
    bm_cetro = bmesh.new()
    bmesh.ops.create_cone(
        bm_cetro,
        cap_ends=True,
        cap_tris=False,
        segments=12,
        radius1=0.022,
        radius2=0.016,
        depth=1.75,
        matrix=Matrix.Translation(Vector((0.42, 0.04, 0.875))),
    )
    # Semilla esmeralda en la punta del báculo (z = 1.76)
    bmesh.ops.create_icosphere(
        bm_cetro,
        subdivisions=2,
        radius=0.045,
        matrix=Matrix.Translation(Vector((0.42, 0.04, 1.76))),
    )
    mesh_cetro = bpy.data.meshes.new("Cetro_Raiz")
    bm_cetro.to_mesh(mesh_cetro)
    bm_cetro.free()

    obj_cetro = bpy.data.objects.new("Cetro_Raiz", mesh_cetro)
    col_obj.objects.link(obj_cetro)
    mat_vara = crear_material("cetro_madera", "#4e3b2b", rugosidad=0.80, metal=0.0)
    obj_cetro.data.materials.append(mat_vara)

    return obj_cor, obj_cetro


def exportar_glb():
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=SALIDA_GLB,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )
    print(f"[OK] Modelo Maisha exportado con éxito en: {SALIDA_GLB}")


def renderizar_vistas(carpeta_vistas):
    script_turnaround = os.path.join(RAIZ, "herramientas", "blender", "render_turnaround.py")
    if not os.path.isfile(script_turnaround):
        print(f"[AVISO] No se encontró {script_turnaround}")
        return

    import subprocess

    cmd = [
        bpy.app.binary_path,
        "-b",
        "--factory-startup",
        "-P",
        script_turnaround,
        "--",
        "--modelo",
        SALIDA_GLB,
        "--prefijo",
        "maisha_base",
        "--salida",
        carpeta_vistas,
    ]
    print("[INFO] Renderizando 4 vistas de turnaround con render_turnaround.py...")
    subprocess.run(cmd, check=True)


def main():
    print("=== RECONSTRUYENDO MAISHA SOBRE BASE MESH PROFESIONAL ===")
    limpiar_escena()
    cuerpo, objs = importar_base_mesh()
    print(f"Cuerpo base importado: {cuerpo.name} con {len(cuerpo.data.vertices)} vértices")

    cabello = modelar_cabello(cuerpo)
    tunica, capa = modelar_tunica_y_capa()
    corazon, cetro = modelar_corazon_y_cetro()

    exportar_glb()

    # Si se pasó el flag --vistas, renderizar las 4 vistas
    if "--vistas" in sys.argv:
        idx = sys.argv.index("--vistas")
        carpeta = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else os.path.join(RAIZ, "documentacion", "referencias_visuales_3d", "personajes", "vistas_maisha_base")
        renderizar_vistas(carpeta)

    print("=== FINALIZADO CON ÉXITO ===")


if __name__ == "__main__":
    main()
