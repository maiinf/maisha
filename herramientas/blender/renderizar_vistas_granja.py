import bpy
import os
import math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIR_OUT = "/Users/iinfafer/.gemini/antigravity/brain/6baa257f-5b81-4a6e-8f7a-1cebbcab1026"
ruta_blend = os.path.join(BASE_DIR, "herramientas", "blender", "fuentes", "casa_granja.blend")

if os.path.exists(ruta_blend):
    bpy.ops.wm.open_mainfile(filepath=ruta_blend)
    
    # Eliminar cámaras existentes
    for c in bpy.data.cameras:
        bpy.data.cameras.remove(c)
    for l in bpy.data.lights:
        bpy.data.lights.remove(l)

    # 1. Luz de sol principal (similar a la luz del juego)
    sun_data = bpy.data.lights.new('Sun', type='SUN')
    sun_data.energy = 2.8
    sun_data.color = (1.0, 0.96, 0.90)
    sun_obj = bpy.data.objects.new('Sun', sun_data)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(-52), math.radians(28), 0)

    # 2. Luz de relleno suave
    fill_data = bpy.data.lights.new('Fill', type='SUN')
    fill_data.energy = 1.0
    fill_data.color = (0.75, 0.85, 1.0)
    fill_obj = bpy.data.objects.new('Fill', fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.rotation_euler = (math.radians(-30), math.radians(-60), 0)

    cam = bpy.data.cameras.new('GameCam')
    cam.lens = 110.0 # Telephoto like in game
    cam_obj = bpy.data.objects.new('GameCam', cam)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.resolution_x = 768
    bpy.context.scene.render.resolution_y = 512

    # Vista Frontal HD-2D (ángulo idéntico al juego: inclinada 48° mirando al norte)
    # En Blender, mirar hacia +Y con inclinación de -48°
    cam_obj.location = (0, -18.0, 16.5)
    cam_obj.rotation_euler = (math.radians(48), 0, 0)
    bpy.context.scene.render.filepath = os.path.join(DIR_OUT, "render_granja_frontal_hd2d.png")
    bpy.ops.render.render(write_still=True)
    print("Guardado render_granja_frontal_hd2d.png")

    # Vista Trasera (cuando Maisha va por detrás: mirando desde el norte hacia el sur)
    cam_obj.location = (0, 20.0, 16.5)
    cam_obj.rotation_euler = (math.radians(132), 0, math.radians(180))
    bpy.context.scene.render.filepath = os.path.join(DIR_OUT, "render_granja_trasera_360.png")
    bpy.ops.render.render(write_still=True)
    print("Guardado render_granja_trasera_360.png")

    # Vista Completa Frontal
    cam_obj.location = (0, -22.0, 3.2)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.scene.render.filepath = os.path.join(DIR_OUT, "render_granja_fachada_completa.png")
    bpy.ops.render.render(write_still=True)
    print("Guardado render_granja_fachada_completa.png")
