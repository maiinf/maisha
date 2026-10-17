#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
renderizar_estudio_activos.py
Genera renders de estudio fotográfico en alta resolución de los activos 3D de Maisha.
"""

import bpy
import os
import math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIR_CAPTURAS = os.path.join(BASE_DIR, "documentacion", "capturas")
os.makedirs(DIR_CAPTURAS, exist_ok=True)

MODELOS_A_RENDERIZAR = [
    ("herramientas/blender/fuentes/maisha.blend", "render_maisha.png", (0, -2.6, 1.05), (1.5708, 0, 0), 1.2),
    ("herramientas/blender/fuentes/pino.blend", "render_pino.png", (0, -2.6, 0.95), (1.5708, 0, 0), 1.2),
    ("herramientas/blender/fuentes/mzee_shamba.blend", "render_shamba.png", (0, -2.8, 1.05), (1.5708, 0, 0), 1.2),
    ("herramientas/blender/fuentes/corteza.blend", "render_corteza.png", (0, -2.8, 1.10), (1.5708, 0, 0), 1.2),
    ("herramientas/blender/fuentes/casa_granja.blend", "render_shamba_casa.png", (0, -7.5, 2.0), (1.5708, 0, 0), 2.5),
    ("herramientas/blender/fuentes/pozo_antiguo.blend", "render_pozo.png", (0, -4.0, 1.2), (1.5708, 0, 0), 1.4),
    ("herramientas/blender/fuentes/casa_pino.blend", "render_casa_pino.png", (0, -5.5, 1.6), (1.5708, 0, 0), 2.2),
    ("herramientas/blender/fuentes/casa_pino_ruina.blend", "render_casa_ruina.png", (0, -5.5, 1.2), (1.5708, 0, 0), 1.8),
    ("herramientas/blender/fuentes/fuente_plaza.blend", "render_fuente_plaza.png", (0, -5.5, 1.3), (1.5708, 0, 0), 1.8),
    ("herramientas/blender/fuentes/gran_arbol.blend", "render_gran_arbol.png", (0, -10.5, 3.2), (1.5708, 0, 0), 4.5)
]

for ruta_rel, nombre_salida, cam_pos, cam_rot, target_z in MODELOS_A_RENDERIZAR:
    ruta_blend = os.path.join(BASE_DIR, ruta_rel)
    if not os.path.exists(ruta_blend):
        continue

    bpy.ops.wm.open_mainfile(filepath=ruta_blend)
    
    # Configurar cámara
    cam = bpy.data.cameras.new('StudioCam')
    cam.lens = 50.0
    cam_obj = bpy.data.objects.new('StudioCam', cam)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = cam_pos
    cam_obj.rotation_euler = cam_rot
    bpy.context.scene.camera = cam_obj

    # Luz de estudio de 3 puntos (Key, Fill, Rim)
    # 1. Key Sun
    l_key = bpy.data.lights.new('KeyLight', type='SUN')
    l_key.energy = 2.4
    l_key.color = (1.0, 0.95, 0.88)
    o_key = bpy.data.objects.new('KeyLight', l_key)
    bpy.context.scene.collection.objects.link(o_key)
    o_key.rotation_euler = (math.radians(-45), math.radians(35), 0)

    # 2. Fill Sun (tono frío suave)
    l_fill = bpy.data.lights.new('FillLight', type='SUN')
    l_fill.energy = 1.0
    l_fill.color = (0.75, 0.85, 1.0)
    o_fill = bpy.data.objects.new('FillLight', l_fill)
    bpy.context.scene.collection.objects.link(o_fill)
    o_fill.rotation_euler = (math.radians(-30), math.radians(-50), 0)

    # 3. Rim Sun (resalte de bordes desde atrás)
    l_rim = bpy.data.lights.new('RimLight', type='SUN')
    l_rim.energy = 1.8
    l_rim.color = (1.0, 0.9, 0.7)
    o_rim = bpy.data.objects.new('RimLight', l_rim)
    bpy.context.scene.collection.objects.link(o_rim)
    o_rim.rotation_euler = (math.radians(135), 0, 0)

    # Fondo suave neutro
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512
    
    if hasattr(bpy.context.scene, "cycles"):
        bpy.context.scene.cycles.samples = 8
        bpy.context.scene.cycles.adaptive_threshold = 0.1

    ruta_final = os.path.join(DIR_CAPTURAS, nombre_salida)
    bpy.context.scene.render.filepath = ruta_final
    
    print(f"Renderizando {nombre_salida}...")
    bpy.ops.render.render(write_still=True)
    print(f" -> Guardado: {ruta_final}")

print("\nTodos los renders de estudio completados.")
