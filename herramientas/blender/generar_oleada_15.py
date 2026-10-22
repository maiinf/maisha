#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_oleada_15.py
Generador de la Oleada 15 de modelos 3D sólidos para Maisha (Sigilia: Maandiko y Las Estanterías).
Exporta:
  - modelos/entorno/charco_tinta.glb    (Charco de Tinta Quieta que bloquea las calles)
  - modelos/entorno/ficha_indice.glb    (Ficha rúnica del Índice sobre pedestal de mármol)
  - modelos/enemigos/pagina_suelta.glb  (Página suelta voladora de la ventisca de Sigilia)
  - modelos/enemigos/tintero_rabioso.glb (Tintero rabioso de cristal con patas de latón)
"""

import bpy
import math
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIR_ENTORNO = os.path.join(BASE_DIR, "modelos", "entorno")
DIR_ENEMIGOS = os.path.join(BASE_DIR, "modelos", "enemigos")
DIR_SIGILIA = os.path.join(BASE_DIR, "arte", "mundos", "sigilia", "maandiko")
DIR_KITOVU = os.path.join(BASE_DIR, "arte", "mundos", "kitovu")
DIR_ALDEA = os.path.join(BASE_DIR, "arte", "mundos", "raiz", "aldea")
DIR_BLEND = os.path.join(BASE_DIR, "herramientas", "blender", "fuentes")

for d in [DIR_ENTORNO, DIR_ENEMIGOS, DIR_BLEND]:
    os.makedirs(d, exist_ok=True)


def limpiar_escena():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)


def obtener_material(nombre, color_hex, roughness=0.6, metallic=0.0, emission_hex=None, emission_strength=0.0):
    if nombre in bpy.data.materials:
        return bpy.data.materials[nombre]

    mat = bpy.data.materials.new(name=nombre)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")

    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)) + (1.0,)

    if bsdf:
        bsdf.inputs['Base Color'].default_value = hex_to_rgb(color_hex)
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if emission_hex and emission_strength > 0:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = hex_to_rgb(emission_hex)
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = hex_to_rgb(emission_hex)
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emission_strength

    return mat


def obtener_material_textura(nombre, ruta_textura, rugosidad=0.7, metalicidad=0.0, factor_mezcla=0.0, color_tinte="#FFFFFF"):
    if nombre in bpy.data.materials:
        return bpy.data.materials[nombre]

    mat = bpy.data.materials.new(name=nombre)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        return mat

    bsdf.inputs['Roughness'].default_value = rugosidad
    bsdf.inputs['Metallic'].default_value = metalicidad

    if os.path.exists(ruta_textura):
        img = bpy.data.images.load(ruta_textura)
        node_tex = nodes.new(type='ShaderNodeTexImage')
        node_tex.image = img
        node_tex.interpolation = 'Closest'  # Pixel art filter NEAREST

        if factor_mezcla > 0.0:
            node_mix = nodes.new(type='ShaderNodeMix')
            node_mix.data_type = 'RGBA'
            node_mix.inputs[0].default_value = factor_mezcla
            h = color_tinte.lstrip('#')
            c_rgb = tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)) + (1.0,)
            node_mix.inputs[7].default_value = c_rgb
            links.new(node_tex.outputs['Color'], node_mix.inputs[6])
            links.new(node_mix.outputs[2], bsdf.inputs['Base Color'])
        else:
            links.new(node_tex.outputs['Color'], bsdf.inputs['Base Color'])

    return mat


def asignar_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def suavizar(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True


def aplicar_uv_caja(obj, escala_u=1.0, escala_v=1.0):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=1.0, correct_aspect=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    if obj.data.uv_layers:
        uvs = obj.data.uv_layers.active.data
        for loop in uvs:
            loop.uv[0] *= escala_u
            loop.uv[1] *= escala_v
    obj.select_set(False)


def exportar_modelo(nombre_base, carpeta):
    ruta_glb = os.path.join(carpeta, f"{nombre_base}.glb")
    ruta_blend = os.path.join(DIR_BLEND, f"{nombre_base}.blend")

    bpy.ops.export_scene.gltf(
        filepath=ruta_glb,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_yup=True
    )
    bpy.ops.wm.save_as_mainfile(filepath=ruta_blend)
    print(f" -> Generado: {ruta_glb} ({os.path.getsize(ruta_glb)} bytes)")


# ===========================================================================
# 1. CHARCO DE TINTA QUIETA (Sigilia / Maandiko)
# ===========================================================================

def generar_charco_tinta():
    """Charco elíptico de Tinta Quieta que bloquea las calles de Maandiko.
    Bordillo de mármol esculpido con escarcha, lecho cóncavo de piedra oscura,
    tinta densa violeta reflectante y burbujas de corrupción de Giza."""
    limpiar_escena()

    tex_marmol = os.path.join(DIR_SIGILIA, "marmol_sigilia_tile.png")
    mat_marmol = obtener_material_textura("Mat_Charco_Marmol", tex_marmol, rugosidad=0.65)
    mat_fondo_piedra = obtener_material("Mat_Charco_FondoPiedra", "#1E1828", roughness=0.88)
    mat_tinta_quieta = obtener_material("Mat_Charco_Tinta", "#180F2A", roughness=0.18, metallic=0.15, emission_hex="#4F46E5", emission_strength=1.4)
    mat_escarcha = obtener_material("Mat_Charco_Escarcha", "#C7D2FE", roughness=0.40, emission_hex="#E0E7FF", emission_strength=0.8)
    mat_burbuja = obtener_material("Mat_Charco_Burbuja", "#4338CA", roughness=0.15, emission_hex="#6366F1", emission_strength=2.2)

    # 1. Bordillo perimetral elíptico en gajos de mármol
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.85, depth=0.18, location=(0, 0, 0.09))
    borde_ext = bpy.context.active_object
    borde_ext.name = "Charco_Borde_Base"
    borde_ext.scale = (1.55, 0.72, 1.0)
    asignar_material(borde_ext, mat_marmol)
    aplicar_uv_caja(borde_ext, 3.0, 1.5)

    # 2. Lecho cóncavo de piedra oscura
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.65, depth=0.12, location=(0, 0, 0.08))
    lecho = bpy.context.active_object
    lecho.name = "Charco_Lecho_Piedra"
    lecho.scale = (1.50, 0.68, 1.0)
    asignar_material(lecho, mat_fondo_piedra)

    # 3. Superficie líquida de Tinta Quieta
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.58, depth=0.08, location=(0, 0, 0.11))
    tinta = bpy.context.active_object
    tinta.name = "Charco_Tinta_Liquida"
    tinta.scale = (1.48, 0.65, 1.0)
    asignar_material(tinta, mat_tinta_quieta)

    # 4. Parches de escarcha helada en el borde
    puntos_escarcha = [
        (-1.8, 0.35, 0.16, 0.45, 0.22),
        (1.9, -0.28, 0.16, 0.50, 0.25),
        (-0.7, -0.65, 0.16, 0.60, 0.20),
        (0.8, 0.68, 0.16, 0.55, 0.22),
        (-2.2, -0.10, 0.16, 0.40, 0.20),
        (2.1, 0.15, 0.16, 0.42, 0.20),
    ]
    for idx, (ex, ey, ez, sx, sy) in enumerate(puntos_escarcha):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, ey, ez))
        hielo = bpy.context.active_object
        hielo.name = f"Charco_Hielo_{idx}"
        hielo.scale = (sx, sy, 0.04)
        asignar_material(hielo, mat_escarcha)
        suavizar(hielo)

    # 5. Burbujas de corrupción de Giza emergiendo de la tinta
    burbujas_pos = [
        (-0.8, 0.15, 0.14, 0.16),
        (-0.2, -0.20, 0.14, 0.20),
        (0.45, 0.18, 0.14, 0.18),
        (1.1, -0.10, 0.14, 0.14),
        (0.1, 0.22, 0.14, 0.12),
        (-1.2, -0.12, 0.14, 0.15),
    ]
    for idx, (bx, by, bz, br) in enumerate(burbujas_pos):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=br, location=(bx, by, bz))
        burbuja = bpy.context.active_object
        burbuja.name = f"Charco_Burbuja_{idx}"
        burbuja.scale = (1.0, 1.0, 0.65)
        asignar_material(burbuja, mat_burbuja)
        suavizar(burbuja)

    exportar_modelo("charco_tinta", DIR_ENTORNO)


# ===========================================================================
# 2. FICHA DEL ÍNDICE DE SIGILIA
# ===========================================================================

def generar_ficha_indice():
    """Ficha rúnica del Índice de Sigilia sobre pedestal de mármol.
    Losa de mármol blanco y bronce con runas caligráficas incisas,
    núcleo de tinta luminiscente y pedestal hexagonal tallado."""
    limpiar_escena()

    tex_marmol = os.path.join(DIR_SIGILIA, "marmol_sigilia_tile.png")
    tex_bronce = os.path.join(DIR_SIGILIA, "bronce_sigilia_tile.png")
    mat_marmol = obtener_material_textura("Mat_Ficha_Marmol", tex_marmol, rugosidad=0.55)
    mat_bronce = obtener_material_textura("Mat_Ficha_Bronce", tex_bronce, rugosidad=0.35, metalicidad=0.88)
    mat_runas = obtener_material("Mat_Ficha_Runas", "#312E81", roughness=0.25, emission_hex="#4F46E5", emission_strength=3.2)
    mat_nieve = obtener_material("Mat_Ficha_Nieve", "#F8FAFC", roughness=0.75)

    # 1. Pedestal hexagonal inferior
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.65, depth=0.18, location=(0, 0, 0.09))
    base1 = bpy.context.active_object
    base1.name = "Ficha_Pedestal_Base"
    asignar_material(base1, mat_marmol)
    aplicar_uv_caja(base1, 1.5, 0.5)

    # 2. Moldura de bronce del pedestal
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.55, depth=0.12, location=(0, 0, 0.24))
    moldura = bpy.context.active_object
    moldura.name = "Ficha_Pedestal_Bronce"
    asignar_material(moldura, mat_bronce)

    # 3. Soporte ranurado de piedra
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.38))
    soporte = bpy.context.active_object
    soporte.name = "Ficha_Soporte_Ranura"
    soporte.scale = (0.52, 0.26, 0.16)
    asignar_material(soporte, mat_marmol)

    # 4. Tableta rúnica principal (Losa vertical biselada)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.95))
    losa = bpy.context.active_object
    losa.name = "Ficha_Losa_Principal"
    losa.scale = (0.58, 0.14, 0.95)
    asignar_material(losa, mat_marmol)
    aplicar_uv_caja(losa, 1.2, 1.8)

    # 5. Marco/Ribete de bronce que guarnece la tableta
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.44))
    remate_sup = bpy.context.active_object
    remate_sup.name = "Ficha_Remate_Superior"
    remate_sup.scale = (0.64, 0.18, 0.08)
    asignar_material(remate_sup, mat_bronce)

    # 6. Ranuras y glifos rúnicos incisos en la cara frontal y trasera
    for y_offset, rot_y in [(0.076, 0), (-0.076, 180)]:
        # Sello circular superior
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.12, depth=0.03, location=(0, y_offset, 1.22))
        sello = bpy.context.active_object
        sello.name = f"Ficha_Glifo_Sello_{int(y_offset*100)}"
        sello.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(sello, mat_runas)

        # Líneas horizontales de inscripciones de escriba
        for l_idx, z_lin in enumerate([1.00, 0.88, 0.76, 0.64]):
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y_offset, z_lin))
            linea = bpy.context.active_object
            linea.name = f"Ficha_Linea_{int(y_offset*100)}_{l_idx}"
            linea.scale = (0.38, 0.02, 0.04)
            asignar_material(linea, mat_runas)

    # 7. Copete de nieve depositada sobre el remate superior
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.50))
    nieve_tapa = bpy.context.active_object
    nieve_tapa.name = "Ficha_Nieve_Remate"
    nieve_tapa.scale = (0.62, 0.16, 0.06)
    asignar_material(nieve_tapa, mat_nieve)
    suavizar(nieve_tapa)

    exportar_modelo("ficha_indice", DIR_ENTORNO)


# ===========================================================================
# 3. PÁGINA SUELTA DE SIGILIA (Enemigo y prop de ventisca)
# ===========================================================================

def generar_pagina_suelta():
    """Página suelta voladora de la ventisca de Sigilia (enemigo y objeto coleccionable).
    Hoja de pergamino envejecido con doblez aerodinámico en S,
    filigranas caligráficas rúnicas y halo de escarcha fría."""
    limpiar_escena()

    mat_pergamino = obtener_material("Mat_Pagina_Papel", "#F5ECD7", roughness=0.82)
    mat_tinta_escrita = obtener_material("Mat_Pagina_Tinta", "#2E1065", roughness=0.35, emission_hex="#4F46E5", emission_strength=1.8)
    mat_hielo_borde = obtener_material("Mat_Pagina_Hielo", "#93C5FD", roughness=0.30, emission_hex="#BFDBFE", emission_strength=1.2)

    # 1. Malla curvada de pergamino en 3D (3 segmentos articulados simulando flutter en el aire)
    # Segmento central
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.40))
    cuerpo_pag = bpy.context.active_object
    cuerpo_pag.name = "Pagina_Cuerpo_Centro"
    cuerpo_pag.scale = (0.32, 0.016, 0.42)
    cuerpo_pag.rotation_euler = (math.radians(12), math.radians(-14), math.radians(8))
    asignar_material(cuerpo_pag, mat_pergamino)

    # Ala izquierda ondulada hacia arriba
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.24, 0.06, 0.44))
    ala_izq = bpy.context.active_object
    ala_izq.name = "Pagina_Ala_Izquierda"
    ala_izq.scale = (0.18, 0.014, 0.38)
    ala_izq.rotation_euler = (math.radians(18), math.radians(-28), math.radians(24))
    asignar_material(ala_izq, mat_pergamino)

    # Ala derecha ondulada hacia abajo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.24, -0.05, 0.36))
    ala_der = bpy.context.active_object
    ala_der.name = "Pagina_Ala_Derecha"
    ala_der.scale = (0.18, 0.014, 0.38)
    ala_der.rotation_euler = (math.radians(6), math.radians(4), math.radians(-12))
    asignar_material(ala_der, mat_pergamino)

    # 2. Trazos caligráficos rúnicos grabados en la página
    lineas_caligrafia = [
        (0.0, 0.010, 0.46, 0.22, 0.02),
        (0.0, 0.010, 0.40, 0.26, 0.02),
        (0.0, 0.010, 0.34, 0.20, 0.02),
        (-0.20, 0.070, 0.44, 0.12, 0.018),
        (0.20, -0.040, 0.36, 0.14, 0.018),
    ]
    for idx, (lx, ly, lz, lw, lh) in enumerate(lineas_caligrafia):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lx, ly, lz))
        trazo = bpy.context.active_object
        trazo.name = f"Pagina_Trazo_{idx}"
        trazo.scale = (lw, 0.006, lh)
        trazo.rotation_euler = cuerpo_pag.rotation_euler
        asignar_material(trazo, mat_tinta_escrita)

    # 3. Cristal de escarcha adherido al vértice
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.08, location=(0.28, -0.06, 0.50))
    cristal = bpy.context.active_object
    cristal.name = "Pagina_Cristal_Escarcha"
    cristal.rotation_euler = (math.radians(35), math.radians(20), math.radians(45))
    asignar_material(cristal, mat_hielo_borde)

    # Exportar tanto a entorno como a enemigos
    exportar_modelo("pagina_suelta", DIR_ENEMIGOS)
    exportar_modelo("pagina_suelta", DIR_ENTORNO)


# ===========================================================================
# 4. TINTERO RABIOSO (Enemigo cazador de Las Estanterías)
# ===========================================================================

def generar_tintero_rabioso():
    """Tintero rabioso (enemigo de Las Estanterías Colgantes).
    Frasco de cristal oscuro facetado lleno de tinta corrupta,
    cuello con anillo de latón y tapón de corcho, etiqueta con ojos enfadados
    y 4 patitas mecánicas de latón articuladas."""
    limpiar_escena()

    mat_cristal = obtener_material("Mat_Tintero_Cristal", "#1E182A", roughness=0.15, metallic=0.10)
    mat_tinta_int = obtener_material("Mat_Tintero_TintaInterior", "#2E1065", roughness=0.20, emission_hex="#4C1D95", emission_strength=2.2)
    mat_laton = obtener_material("Mat_Tintero_Laton", "#D97706", roughness=0.35, metallic=0.88)
    mat_corcho = obtener_material("Mat_Tintero_Corcho", "#92400E", roughness=0.85)
    mat_etiqueta = obtener_material("Mat_Tintero_Etiqueta", "#FDE68A", roughness=0.75)
    mat_ojos_enfadados = obtener_material("Mat_Tintero_Ojos", "#0F172A", roughness=0.20, emission_hex="#EF4444", emission_strength=1.5)

    # 1. Cuerpo principal del frasco: prisma octogonal de cristal
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.34, depth=0.48, location=(0, 0, 0.36))
    frasco = bpy.context.active_object
    frasco.name = "Tintero_Frasco_Cristal"
    asignar_material(frasco, mat_cristal)
    suavizar(frasco)

    # 2. Núcleo interior de tinta viscosa
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.30, depth=0.40, location=(0, 0, 0.33))
    tinta_core = bpy.context.active_object
    tinta_core.name = "Tintero_Tinta_Liquido"
    asignar_material(tinta_core, mat_tinta_int)
    suavizar(tinta_core)

    # 3. Cuello del tintero
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.18, depth=0.14, location=(0, 0, 0.65))
    cuello = bpy.context.active_object
    cuello.name = "Tintero_Cuello_Frasco"
    asignar_material(cuello, mat_cristal)

    # 4. Anillo de latón que refuerza el cuello
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.20, depth=0.05, location=(0, 0, 0.68))
    anillo = bpy.context.active_object
    anillo.name = "Tintero_Anillo_Laton"
    asignar_material(anillo, mat_laton)

    # 5. Tapón de corcho encajado en el cuello
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.16, depth=0.16, location=(0, 0, 0.77))
    tapon = bpy.context.active_object
    tapon.name = "Tintero_Tapon_Corcho"
    # Leve inclinación para darle personalidad cómica/rabiosa
    tapon.rotation_euler = (math.radians(6), math.radians(-4), 0)
    asignar_material(tapon, mat_corcho)

    # 6. Etiqueta frontal de papel apergaminado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.345, 0.36))
    etiqueta = bpy.context.active_object
    etiqueta.name = "Tintero_Etiqueta_Papel"
    etiqueta.scale = (0.28, 0.015, 0.22)
    asignar_material(etiqueta, mat_etiqueta)

    # 7. Dos ojos enfadados oblicuos en la etiqueta
    for idx, (ox, oz, rot_z) in enumerate([(-0.07, 0.38, 22), (0.07, 0.38, -22)]):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox, -0.355, oz))
        ojo = bpy.context.active_object
        ojo.name = f"Tintero_Ojo_{idx}"
        ojo.scale = (0.05, 0.01, 0.02)
        ojo.rotation_euler = (0, 0, math.radians(rot_z))
        asignar_material(ojo, mat_ojos_enfadados)

    # 8. 4 Patitas de latón articuladas a los costados
    patas_coords = [
        (-0.32, -0.18, 0.16, 35, 40),
        (-0.32, 0.18, 0.16, -35, 40),
        (0.32, -0.18, 0.16, 35, -40),
        (0.32, 0.18, 0.16, -35, -40),
    ]
    for idx, (px, py, pz, rx, ry) in enumerate(patas_coords):
        # Muslo superior
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.032, depth=0.22, location=(px * 0.9, py * 0.9, pz))
        muslo = bpy.context.active_object
        muslo.name = f"Tintero_Pata_Muslo_{idx}"
        muslo.rotation_euler = (math.radians(rx), math.radians(ry), 0)
        asignar_material(muslo, mat_laton)

        # Garra/pie inferior tocando el suelo
        ext_x = px * 1.35
        ext_y = py * 1.35
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.18, location=(ext_x, ext_y, 0.08))
        pie = bpy.context.active_object
        pie.name = f"Tintero_Pata_Pie_{idx}"
        pie.rotation_euler = (math.radians(-rx * 0.5), math.radians(-ry * 0.5), 0)
        asignar_material(pie, mat_laton)

    exportar_modelo("tintero_rabioso", DIR_ENEMIGOS)


# ===========================================================================
# MAIN DE OLEADA 15
# ===========================================================================

def main():
    print("=" * 60)
    print("GENERADOR 3D MAISHA - OLEADA 15 (SIGILIA & ESTANTERÍAS)")
    print(f"Blender Version: {bpy.app.version_string}")
    print("=" * 60)

    print("\n[1/4] Modelando Charco de Tinta Quieta...")
    generar_charco_tinta()

    print("\n[2/4] Modelando Ficha del Índice de Sigilia...")
    generar_ficha_indice()

    print("\n[3/4] Modelando Página Suelta de Ventisca...")
    generar_pagina_suelta()

    print("\n[4/4] Modelando Tintero Rabioso...")
    generar_tintero_rabioso()

    print("\n" + "=" * 60)
    print("OLEADA 15 COMPLETADA Y EXPORTADA CON ÉXITO")
    print("=" * 60)


if __name__ == "__main__":
    main()
