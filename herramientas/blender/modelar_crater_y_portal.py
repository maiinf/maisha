# -*- coding: utf-8 -*-
"""
modelar_crater_y_portal.py - Modelador AAA del Cráter del Despertar, Árbol Seco, Portal de Raíz y Nudo de Corrupción.
Según documentacion/referencias_visuales_3d/construcciones/ref_crater_despertar.md
y documentacion/referencias_visuales_3d/construcciones/ref_portal_raiz.md:

1. crater_kitovu.glb (Cráter del impacto de Asili con glifos en espiral emisivos)
2. arbol_seco.glb (Roble milenario petrificado por la ceniza de Giza)
3. portal_raiz.glb (Arco monumental de raíces colosales vivas entrelazadas)
4. nudo_corrupcion.glb (Nudo de zarcillos espinosos y cristales de cuarzo violeta)

Uso:
    blender -b --factory-startup -P herramientas/blender/modelar_crater_y_portal.py
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
    col = bpy.data.collections.new("Coleccion_Entorno")
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
# 1. CRÁTER DEL DESPERTAR
# ===========================================================================
def modelar_crater():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Entorno"]
    mat_roca = crear_material("roca_calcinada_crater", "#22201e", rugosidad=0.90, metal=0.0)
    mat_glifos = crear_material(
        "glifos_ambar_crater",
        "#d89b38",
        rugosidad=0.35,
        metal=0.1,
        emision=1.8,
        color_emision="#e8aa42",
    )

    bm_roca = bmesh.new()

    # Cuenco elíptico exterior (3.40 x 3.00 m)
    # Creamos un anillo exterior levantado (labio del cráter)
    bmesh.ops.create_circle(
        bm_roca,
        cap_ends=False,
        segments=32,
        radius=1.70,
        matrix=Matrix.Scale(1.0, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.88, 4, Vector((0, 1, 0))),
    )
    # Reborde rocoso fracturado: lajas de pizarra levantadas alrededor del cráter
    for i in range(16):
        angulo = i * (2 * math.pi / 16)
        rx = math.cos(angulo) * 1.65
        ry = math.sin(angulo) * 1.45
        bmesh.ops.create_cube(
            bm_roca,
            size=1.0,
            matrix=Matrix.Translation(Vector((rx, ry, 0.12)))
            @ Matrix.Rotation(angulo, 4, "Z")
            @ Matrix.Rotation(math.radians(25), 4, "Y")
            @ Matrix.Scale(0.35, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(0.25, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(0.18, 4, Vector((0, 0, 1))),
        )

    # Fondo cóncavo del cráter
    bmesh.ops.create_cone(
        bm_roca,
        cap_ends=True,
        segments=24,
        radius1=1.60,
        radius2=0.40,
        depth=0.45,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 0.20)))
        @ Matrix.Rotation(math.radians(180), 4, "X")
        @ Matrix.Scale(1.0, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.88, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(1.0, 4, Vector((0, 0, 1))),
    )

    mesh_roca = bpy.data.meshes.new("Crater_Roca")
    bm_roca.to_mesh(mesh_roca)
    bm_roca.free()

    obj_roca = bpy.data.objects.new("Crater_Roca", mesh_roca)
    col.objects.link(obj_roca)
    obj_roca.data.materials.append(mat_roca)

    # Glifos rúnicos en espiral en el fondo del cráter (material emisivo ámbar)
    bm_runas = bmesh.new()
    pasos_espiral = 48
    radio_max = 0.95
    for p in range(pasos_espiral):
        t = p / pasos_espiral
        ang = t * (math.pi * 5.0)  # 2.5 vueltas
        r = t * radio_max
        gx = math.cos(ang) * r
        gy = math.sin(ang) * r * 0.88
        gz = 0.04 + (r * 0.08)  # adaptado a la pendiente cóncava

        bmesh.ops.create_cube(
            bm_runas,
            size=1.0,
            matrix=Matrix.Translation(Vector((gx, gy, gz)))
            @ Matrix.Rotation(ang, 4, "Z")
            @ Matrix.Scale(0.06, 4, Vector((1, 0, 0)))
            @ Matrix.Scale(0.04, 4, Vector((0, 1, 0)))
            @ Matrix.Scale(0.02, 4, Vector((0, 0, 1))),
        )

    mesh_runas = bpy.data.meshes.new("Glifos_Espiral_Ambar")
    bm_runas.to_mesh(mesh_runas)
    bm_runas.free()

    obj_runas = bpy.data.objects.new("Glifos_Espiral_Ambar", mesh_runas)
    col.objects.link(obj_runas)
    obj_runas.data.materials.append(mat_glifos)

    bpy.ops.object.select_all(action="SELECT")
    ruta = os.path.join(CARPETA_SALIDA, "crater_kitovu.glb")
    exportar_seleccion(ruta)


# ===========================================================================
# 2. ÁRBOL SECO ANCESTRAL
# ===========================================================================
def modelar_arbol_seco():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Entorno"]
    mat_petrificado = crear_material("madera_petrificada_seco", "#2e2c2a", rugosidad=0.95, metal=0.0)
    mat_ceniza = crear_material("ceniza_incrustada", "#8c8a85", rugosidad=0.98, metal=0.0)

    bm = bmesh.new()

    # Tronco principal nudoso retorcido en espiral (altura 4.60 m)
    # Base ancha (0.70 m radio 0.35) a cuello (0.45 m radio 0.225)
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=16,
        radius1=0.38,
        radius2=0.22,
        depth=2.80,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 1.40)))
        @ Matrix.Rotation(math.radians(6), 4, "Y"),
    )

    # 3 Grandes ramas maestras desnudas que se alzan como garras
    # Rama 1 (hacia +X y +Z)
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=12,
        radius1=0.18,
        radius2=0.06,
        depth=1.90,
        matrix=Matrix.Translation(Vector((0.45, 0.10, 3.40)))
        @ Matrix.Rotation(math.radians(28), 4, "Y")
        @ Matrix.Rotation(math.radians(15), 4, "X"),
    )
    # Rama 2 (hacia -X y +Z)
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=12,
        radius1=0.16,
        radius2=0.05,
        depth=1.85,
        matrix=Matrix.Translation(Vector((-0.42, -0.15, 3.35)))
        @ Matrix.Rotation(math.radians(-32), 4, "Y")
        @ Matrix.Rotation(math.radians(-10), 4, "X"),
    )
    # Rama 3 (hacia +Y y +Z, más vertical)
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=12,
        radius1=0.15,
        radius2=0.04,
        depth=1.75,
        matrix=Matrix.Translation(Vector((0.05, 0.40, 3.55)))
        @ Matrix.Rotation(math.radians(-26), 4, "X"),
    )

    # Raíces superficiales gruesas que abrazan el borde rocoso del cráter
    for ang in (math.radians(35), math.radians(160), math.radians(-85)):
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            segments=10,
            radius1=0.22,
            radius2=0.08,
            depth=1.20,
            matrix=Matrix.Translation(Vector((math.cos(ang) * 0.45, math.sin(ang) * 0.45, 0.25)))
            @ Matrix.Rotation(ang, 4, "Z")
            @ Matrix.Rotation(math.radians(70), 4, "Y"),
        )

    mesh = bpy.data.meshes.new("Arbol_Seco_Ancestral")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Arbol_Seco_Ancestral", mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat_petrificado)

    bpy.ops.object.select_all(action="SELECT")
    ruta = os.path.join(CARPETA_SALIDA, "arbol_seco.glb")
    exportar_seleccion(ruta)


# ===========================================================================
# 3. PORTAL DE RAÍZ MONUMENTAL
# ===========================================================================
def modelar_portal_raiz():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Entorno"]
    mat_raiz = crear_material("madera_raiz_portal", "#453324", rugosidad=0.85, metal=0.0)
    mat_savia = crear_material(
        "savia_dorada_raiz",
        "#dfa838",
        rugosidad=0.35,
        metal=0.1,
        emision=1.6,
        color_emision="#f5be42",
    )

    bm = bmesh.new()

    # Pilar izquierdo: Raíz viva retorcida que asciende hacia la derecha
    # Altura 4.80 m, vano interior 2.80 m
    # Segmento bajo izquierdo (x = -1.50)
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=16,
        radius1=0.45,
        radius2=0.35,
        depth=2.60,
        matrix=Matrix.Translation(Vector((-1.55, 0.0, 1.30)))
        @ Matrix.Rotation(math.radians(-10), 4, "Y"),
    )
    # Segmento arqueado superior izquierdo
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=16,
        radius1=0.35,
        radius2=0.25,
        depth=2.40,
        matrix=Matrix.Translation(Vector((-0.80, 0.0, 3.65)))
        @ Matrix.Rotation(math.radians(-42), 4, "Y"),
    )

    # Pilar derecho: Raíz viva que asciende hacia la izquierda
    # Segmento bajo derecho (x = +1.50)
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=16,
        radius1=0.45,
        radius2=0.35,
        depth=2.60,
        matrix=Matrix.Translation(Vector((1.55, 0.0, 1.30)))
        @ Matrix.Rotation(math.radians(10), 4, "Y"),
    )
    # Segmento arqueado superior derecho
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        segments=16,
        radius1=0.35,
        radius2=0.25,
        depth=2.40,
        matrix=Matrix.Translation(Vector((0.80, 0.0, 3.65)))
        @ Matrix.Rotation(math.radians(42), 4, "Y"),
    )

    # Clave del arco: Nudo superior entrelazado en z = 4.70 m
    bmesh.ops.create_icosphere(
        bm,
        subdivisions=2,
        radius=0.45,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 4.65)))
        @ Matrix.Scale(1.3, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.8, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(0.8, 4, Vector((0, 0, 1))),
    )

    # Zarcillos entrelazados secundarios que abrazan el arco
    for sx in (-1.1, 1.1):
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            segments=10,
            radius1=0.14,
            radius2=0.05,
            depth=2.80,
            matrix=Matrix.Translation(Vector((sx, 0.15, 2.40)))
            @ Matrix.Rotation(math.radians(-18 if sx < 0 else 18), 4, "Y")
            @ Matrix.Rotation(math.radians(12), 4, "X"),
        )

    mesh = bpy.data.meshes.new("Portal_Raiz_Monumental")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Portal_Raiz_Monumental", mesh)
    col.objects.link(obj)
    obj.data.materials.append(mat_raiz)

    bpy.ops.object.select_all(action="SELECT")
    ruta = os.path.join(CARPETA_SALIDA, "portal_raiz.glb")
    exportar_seleccion(ruta)


# ===========================================================================
# 4. NUDO DE CORRUPCIÓN DE GIZA
# ===========================================================================
def modelar_nudo_corrupcion():
    limpiar_escena()
    col = bpy.data.collections["Coleccion_Entorno"]
    mat_madera_corrupta = crear_material("madera_corrupta_nudo", "#1c181d", rugosidad=0.95, metal=0.0)
    mat_cristal_giza = crear_material(
        "cristal_giza_violeta",
        "#4a1856",
        rugosidad=0.20,
        metal=0.1,
        emision=2.5,
        color_emision="#7b2292",
    )

    bm_nudo = bmesh.new()

    # Bulbo central petrificado podrido (diámetro 1.60 m)
    bmesh.ops.create_icosphere(
        bm_nudo,
        subdivisions=2,
        radius=0.75,
        matrix=Matrix.Translation(Vector((0.0, 0.0, 0.72)))
        @ Matrix.Scale(1.15, 4, Vector((1, 0, 0)))
        @ Matrix.Scale(0.90, 4, Vector((0, 1, 0)))
        @ Matrix.Scale(1.05, 4, Vector((0, 0, 1))),
    )

    # Zarcillos espinosos que sellan el paso (envergadura 3.20 m)
    for i, ang in enumerate((0, 30, 65, 115, 150, 180, 210, 250, 300, 335)):
        rad = math.radians(ang)
        longitud = 1.35 if i % 2 == 0 else 1.70
        bmesh.ops.create_cone(
            bm_nudo,
            cap_ends=True,
            segments=8,
            radius1=0.12,
            radius2=0.02,
            depth=longitud,
            matrix=Matrix.Translation(Vector((math.cos(rad) * 1.10, math.sin(rad) * 0.40, 0.65)))
            @ Matrix.Rotation(rad, 4, "Z")
            @ Matrix.Rotation(math.radians(55), 4, "Y"),
        )

    mesh_nudo = bpy.data.meshes.new("Nudo_Madera_Corrupta")
    bm_nudo.to_mesh(mesh_nudo)
    bm_nudo.free()

    obj_nudo = bpy.data.objects.new("Nudo_Madera_Corrupta", mesh_nudo)
    col.objects.link(obj_nudo)
    obj_nudo.data.materials.append(mat_madera_corrupta)

    # Agujas y cristales afilados de cuarzo violeta de Giza (emisivos)
    bm_cristal = bmesh.new()
    for cx, cy, cz, rx, ry in [
        (0.0, 0.15, 1.25, 15, -20),
        (-0.35, -0.10, 1.10, -25, 30),
        (0.40, 0.05, 1.05, 10, -35),
        (-0.15, 0.25, 0.85, 30, 15),
        (0.20, -0.20, 0.90, -15, -15),
    ]:
        bmesh.ops.create_cone(
            bm_cristal,
            cap_ends=True,
            segments=6,
            radius1=0.08,
            radius2=0.01,
            depth=0.55,
            matrix=Matrix.Translation(Vector((cx, cy, cz)))
            @ Matrix.Rotation(math.radians(rx), 4, "X")
            @ Matrix.Rotation(math.radians(ry), 4, "Y"),
        )

    mesh_cristal = bpy.data.meshes.new("Cristales_Giza_Violeta")
    bm_cristal.to_mesh(mesh_cristal)
    bm_cristal.free()

    obj_cristal = bpy.data.objects.new("Cristales_Giza_Violeta", mesh_cristal)
    col.objects.link(obj_cristal)
    obj_cristal.data.materials.append(mat_cristal_giza)

    bpy.ops.object.select_all(action="SELECT")
    ruta = os.path.join(CARPETA_SALIDA, "nudo_corrupcion.glb")
    exportar_seleccion(ruta)


def main():
    print("=== MODELANDO CRÁTER, ÁRBOL Y PORTAL DE EL KITOVU ===")
    modelar_crater()
    modelar_arbol_seco()
    modelar_portal_raiz()
    modelar_nudo_corrupcion()
    print("=== MODELOS DE ENTORNO GENERADOS CON ÉXITO ===")


if __name__ == "__main__":
    main()
