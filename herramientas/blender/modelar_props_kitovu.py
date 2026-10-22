# -*- coding: utf-8 -*-
"""
modelar_props_kitovu.py - Modelador AAA de los Props y Narrativa Ambiental de El Kitovu.
Genera los modelos 3D según documentacion/referencias_visuales_3d/construcciones/ref_props_huerto_kitovu.md:
1. Carretilla de madera volcada (carro_madera.glb)
2. Pala de labranza oxidada (pala_oxidada.glb)
3. Espantapájaros de sombras / maniquí de entrenamiento (espantapajaros.glb)
4. Pozo megalítico antiguo (pozo_antiguo.glb)

Uso:
    blender -b --factory-startup -P herramientas/blender/modelar_props_kitovu.py
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
    col = bpy.data.collections.new("Coleccion_Props")
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


def exportar_seleccion(ruta_glb):
    bpy.ops.export_scene.gltf(
        filepath=ruta_glb,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )
    print(f"[OK] Exportado: {ruta_glb}")


# ===========================================================================
# 1. CARRETILLA DE MADERA VOLCADA
# ===========================================================================
def modelar_carretilla():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Props"]
    mat_madera = crear_material("madera_roble_desgastada", "#4a443c", rugosidad=0.88, metal=0.0)
    mat_hierro = crear_material("hierro_herrumbre", "#7a3824", rugosidad=0.82, metal=0.35)
    mat_tierra = crear_material("tierra_agrietada_surco", "#3c352a", rugosidad=0.95, metal=0.0)

    bm = bmesh.new()

    # Dos varales longitudinales de madera
    for sx in (-0.28, 0.28):
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.Translation(Vector((sx, 0.0, 0.25)))
            @ Matrix.Scale(0.08, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(1.45, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(0.08, 4, Vector((0, 0, 1))),
        )

    # Rueda delantera de madera con aro de hierro
    crear_cilindro(
        bm,
        segments=24,
        radius=0.22,
        depth=0.07,
        matrix=Matrix.Translation(Vector((0.0, 0.58, 0.22)))
        @ Matrix.Rotation(math.radians(90), 4, "Y"),
    )
    # Eje de hierro de la rueda
    crear_cilindro(
        bm,
        segments=12,
        radius=0.025,
        depth=0.45,
        matrix=Matrix.Translation(Vector((0.0, 0.58, 0.22)))
        @ Matrix.Rotation(math.radians(90), 4, "Y"),
    )

    # Cajón de madera (fondo y paredes)
    # Fondo
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.Translation(Vector((0.0, -0.05, 0.32)))
        @ Matrix.Scale(0.68, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.85, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.05, 4, Vector((0, 0, 1))),
    )
    # Pared frontal
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.Translation(Vector((0.0, 0.38, 0.46)))
        @ Matrix.Rotation(math.radians(-15), 4, "X")
        @ Matrix.Scale(0.68, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.04, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.32, 4, Vector((0, 0, 1))),
    )
    # Pared lateral derecha
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.Translation(Vector((0.34, -0.05, 0.46)))
        @ Matrix.Rotation(math.radians(12), 4, "Y")
        @ Matrix.Scale(0.04, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.85, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.32, 4, Vector((0, 0, 1))),
    )
    # Pared lateral izquierda (parcialmente rota y astillada)
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.Translation(Vector((-0.34, 0.05, 0.44)))
        @ Matrix.Rotation(math.radians(-10), 4, "Y")
        @ Matrix.Scale(0.04, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.60, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.28, 4, Vector((0, 0, 1))),
    )
    # Pared trasera
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.Translation(Vector((0.0, -0.48, 0.46)))
        @ Matrix.Rotation(math.radians(10), 4, "X")
        @ Matrix.Scale(0.68, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.04, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.32, 4, Vector((0, 0, 1))),
    )
    # Dos patas de apoyo traseras
    for sx in (-0.24, 0.24):
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.Translation(Vector((sx, -0.38, 0.14)))
            @ Matrix.Scale(0.06, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(0.06, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(0.26, 4, Vector((0, 0, 1))),
        )

    # Simular montículo de tierra/abono petrificado dentro del cajón
    bmesh.ops.create_icosphere(
        bm,
        subdivisions=2,
        radius=0.24,
        matrix=Matrix.Translation(Vector((0.05, -0.05, 0.38)))
        @ Matrix.Scale(1.0, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(1.4, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.4, 4, Vector((0, 0, 1))),
    )

    mesh = bpy.data.meshes.new("Carretilla_Volcada")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Carretilla_Volcada", mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat_madera)

    # Inclinarla 28 grados hacia un lado para que repose volcada en el suelo
    obj.rotation_euler = (math.radians(12), math.radians(-28), math.radians(15))
    bpy.context.view_layer.update()
    z_min = min((obj.matrix_world @ Vector(v)).z for v in obj.bound_box)
    obj.location.z -= z_min

    bpy.ops.object.select_all(action="SELECT")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    ruta = os.path.join(CARPETA_SALIDA, "carro_madera.glb")
    exportar_seleccion(ruta)


# ===========================================================================
# 2. PALA DE LABRANZA OXIDADA
# ===========================================================================
def modelar_pala():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Props"]
    mat_madera = crear_material("madera_fresno_mango", "#5a5042", rugosidad=0.85, metal=0.0)
    mat_hierro = crear_material("hierro_herrumbre", "#7a3824", rugosidad=0.80, metal=0.40)
    mat_tierra = crear_material("tierra_agrietada_surco", "#3c352a", rugosidad=0.95, metal=0.0)

    bm = bmesh.new()

    # Pequeño montículo de surco de tierra donde está clavada la pala
    bmesh.ops.create_icosphere(
        bm,
        subdivisions=2,
        radius=0.35,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 0.02)))
        @ Matrix.Scale(1.3, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.8, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.2, 4, Vector((0, 0, 1))),
    )

    # Hoja de pala triangular de hierro forjado
    bm_hoja = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=4,
        radius1=0.14,
        radius2=0.02,
        depth=0.28,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 0.16)))
        @ Matrix.Rotation(math.radians(45), 4, "Z")
        @ Matrix.Scale(1.0, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.12, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(1.0, 4, Vector((0, 0, 1))),
    )

    # Mango cilíndrico de fresno
    crear_cilindro(
        bm,
        segments=12,
        radius=0.022,
        depth=1.15,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 0.78))),
    )

    # Agarre superior en forma de "T"
    crear_cilindro(
        bm,
        segments=10,
        radius=0.020,
        depth=0.18,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 1.35)))
        @ Matrix.Rotation(math.radians(90), 4, "Y"),
    )

    mesh = bpy.data.meshes.new("Pala_Oxidada")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Pala_Oxidada", mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat_hierro)

    # Inclinar 22 grados clavada en el surco
    obj.rotation_euler = (math.radians(22), math.radians(6), 0.0)
    bpy.context.view_layer.update()
    z_min = min((obj.matrix_world @ Vector(v)).z for v in obj.bound_box)
    obj.location.z -= z_min

    bpy.ops.object.select_all(action="SELECT")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    ruta = os.path.join(CARPETA_SALIDA, "pala_oxidada.glb")
    exportar_seleccion(ruta)


# ===========================================================================
# 3. ESPANTAPÁJAROS DE ENTRENAMIENTO
# ===========================================================================
def modelar_espantapajaros():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Props"]
    mat_madera = crear_material("madera_abedul_estaca", "#4a4237", rugosidad=0.90, metal=0.0)
    mat_saco = crear_material("saco_cañamo_parches", "#7c7462", rugosidad=0.92, metal=0.0)
    mat_paja = crear_material("paja_seca_dorada", "#b89e58", rugosidad=0.88, metal=0.0)
    mat_cuero = crear_material("cuero_remendado", "#443525", rugosidad=0.80, metal=0.0)

    bm = bmesh.new()

    # Poste vertical de madera clavado en el suelo (altura 2.10 m)
    crear_cilindro(
        bm,
        segments=12,
        radius=0.055,
        depth=2.15,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 1.075))),
    )

    # Travesaño horizontal para los brazos (envergadura 1.60 m en z = 1.48)
    crear_cilindro(
        bm,
        segments=10,
        radius=0.040,
        depth=1.60,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 1.48)))
        @ Matrix.Rotation(math.radians(90), 4, "Y")
        @ Matrix.Rotation(math.radians(4), 4, "Z"),
    )

    # Torso de saco de cáñamo relleno de paja
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=16,
        radius1=0.28,
        radius2=0.22,
        depth=0.72,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 1.25))),
    )

    # Cinturón de soga de esparto
    crear_cilindro(
        bm,
        segments=16,
        radius=0.26,
        depth=0.06,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 0.98))),
    )

    # Mechones de paja que sobresalen por las mangas y el bajo
    for sx in (-0.72, 0.72):
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            segments=8,
            radius1=0.07,
            radius2=0.01,
            depth=0.25,
            matrix=Matrix.Translation(Vector((sx, 0.0, 1.46)))
            @ Matrix.Rotation(math.radians(90 if sx > 0 else -90), 4, "Y"),
        )

    # Cabeza de calabaza / saco de arpillera
    bmesh.ops.create_uvsphere(
        bm,
        u_segments=16,
        v_segments=12,
        radius=0.19,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 1.76)))
        @ Matrix.Scale(0.9, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.9, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(1.15, 4, Vector((0, 0, 1))),
    )

    # Sombrero cónico de paja trenzada de campesino inclinado
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=16,
        radius1=0.38,
        radius2=0.03,
        depth=0.28,
        matrix=Matrix.Translation(Vector((0.02, -0.02, 1.96)))
        @ Matrix.Rotation(math.radians(-14), 4, "X")
        @ Matrix.Rotation(math.radians(8), 4, "Y"),
    )

    mesh = bpy.data.meshes.new("Espantapajaros_Entrenamiento")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Espantapajaros_Entrenamiento", mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat_saco)

    bpy.ops.object.select_all(action="SELECT")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    ruta = os.path.join(CARPETA_SALIDA, "espantapajaros.glb")
    exportar_seleccion(ruta)


# ===========================================================================
# 4. POZO MEGALÍTICO ANTIGUO
# ===========================================================================
def modelar_pozo():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Props"]
    mat_caliza = crear_material("caliza_pozo_musgo", "#585954", rugosidad=0.88, metal=0.0)
    mat_madera = crear_material("madera_roble_viga", "#42382e", rugosidad=0.88, metal=0.0)
    mat_hierro = crear_material("hierro_herrumbre", "#7a3824", rugosidad=0.80, metal=0.35)
    mat_agua = crear_material("agua_pozo_oscura", "#1b2a2e", rugosidad=0.10, metal=0.1)

    bm = bmesh.new()

    # Brocal cilíndrico de piedra caliza megalítica
    # Radio ext: 0.85m, int: 0.58m, altura: 0.90m
    crear_cilindro(
        bm,
        segments=24,
        radius=0.88,
        depth=0.90,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 0.45))),
    )
    # Superficie interior del agua oscura en el fondo
    crear_cilindro(
        bm,
        segments=16,
        radius=0.58,
        depth=0.05,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 0.15))),
    )

    # Dos pilares de roble oscuro a los lados del brocal (x = -0.78 y +0.78)
    for sx in (-0.78, 0.78):
        bmesh.ops.create_cube(
            bm,
            size=1.0,
            matrix=Matrix.Translation(Vector((sx, 0.0, 1.45)))
            @ Matrix.Scale(0.14, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(0.14, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(1.80, 4, Vector((0, 0, 1))),
        )

    # Viga travesaño superior que une los dos pilares
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 2.25)))
        @ Matrix.Scale(1.75, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.15, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.15, 4, Vector((0, 0, 1))),
    )

    # Tejadillo a dos aguas de tablas de cedro sobre la viga (z = 2.40 m)
    # Ala izquierda
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.Translation(Vector((0.0, -0.32, 2.45)))
        @ Matrix.Rotation(math.radians(35), 4, "X")
        @ Matrix.Scale(1.90, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.68, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.04, 4, Vector((0, 0, 1))),
    )
    # Ala derecha
    bmesh.ops.create_cube(
        bm,
        size=1.0,
        matrix=Matrix.Translation(Vector((0.0, 0.32, 2.45)))
        @ Matrix.Rotation(math.radians(-35), 4, "X")
        @ Matrix.Scale(1.90, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.68, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.04, 4, Vector((0, 0, 1))),
    )

    # Cilindro de cabrestante/torno de madera con cuerda
    crear_cilindro(
        bm,
        segments=16,
        radius=0.10,
        depth=1.20,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 1.82)))
        @ Matrix.Rotation(math.radians(90), 4, "Y"),
    )
    # Manivela de hierro forjado
    crear_cilindro(
        bm,
        segments=8,
        radius=0.02,
        depth=0.25,
        matrix=Matrix.Translation(Vector((0.72, 0.0, 1.82)))
        @ Matrix.Rotation(math.radians(90), 4, "Y"),
    )

    # Cubo de madera posado sobre el brocal del pozo
    crear_cilindro(
        bm,
        segments=12,
        radius=0.16,
        depth=0.32,
        matrix=Matrix.Translation(Vector((0.45, -0.42, 1.06))),
    )

    mesh = bpy.data.meshes.new("Pozo_Megalitico_Antiguo")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Pozo_Megalitico_Antiguo", mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat_caliza)

    bpy.ops.object.select_all(action="SELECT")
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    ruta = os.path.join(CARPETA_SALIDA, "pozo_antiguo.glb")
    exportar_seleccion(ruta)


def main():
    print("=== MODELANDO PROPS DE EL KITOVU EN BLENDER ===")
    modelar_carretilla()
    modelar_pala()
    modelar_espantapajaros()
    modelar_pozo()
    print("=== PROPS GENERADOS CON ÉXITO ===")


if __name__ == "__main__":
    main()
