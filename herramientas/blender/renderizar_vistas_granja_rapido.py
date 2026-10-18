import bpy
import os
import math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIR_OUT = "/Users/iinfafer/.gemini/antigravity/brain/6baa257f-5b81-4a6e-8f7a-1cebbcab1026"
ruta_blend = os.path.join(BASE_DIR, "herramientas", "blender", "fuentes", "casa_granja.blend")

bpy.ops.wm.open_mainfile(filepath=ruta_blend)

# Usar EEVEE o Workbench para render ultra-rápido en 1 segundo
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
if hasattr(bpy.context.scene, "eevee"):
    bpy.context.scene.eevee.taa_render_samples = 16

# Limpiar cámaras y luces
for c in list(bpy.data.cameras):
    bpy.data.cameras.remove(c)
for l in list(bpy.data.lights):
    bpy.data.lights.remove(l)

# 1. Luz de sol frontal-alta
sun_front = bpy.data.lights.new('SunFront', type='SUN')
sun_front.energy = 2.5
sun_front.color = (1.0, 0.95, 0.88)
o_sf = bpy.data.objects.new('SunFront', sun_front)
bpy.context.scene.collection.objects.link(o_sf)
o_sf.rotation_euler = (math.radians(-50), math.radians(30), 0)

# 2. Luz de relleno trasera (para que la parte trasera se vea clara y nítida en 360°)
sun_back = bpy.data.lights.new('SunBack', type='SUN')
sun_back.energy = 1.8
sun_back.color = (0.85, 0.90, 1.0)
o_sb = bpy.data.objects.new('SunBack', sun_back)
bpy.context.scene.collection.objects.link(o_sb)
o_sb.rotation_euler = (math.radians(50), math.radians(-30), 0)

# Target en el centro de la casa (cx=0, cy=1.2, cz=2.5)
target = bpy.data.objects.new("Target", None)
bpy.context.scene.collection.objects.link(target)
target.location = (0.0, 1.2, 2.5)

# Cámara
cam = bpy.data.cameras.new('InspectorCam')
cam.lens = 55.0
cam_obj = bpy.data.objects.new('InspectorCam', cam)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Constraint Track To
track = cam_obj.constraints.new(type='TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'

bpy.context.scene.render.film_transparent = True
bpy.context.scene.render.resolution_x = 768
bpy.context.scene.render.resolution_y = 512

vistas = [
    ("render_granja_frontal_hd2d.png", (0.0, -14.0, 12.0)),
    ("render_granja_trasera_360.png", (0.0, 16.0, 12.0)),
    ("render_granja_molino_izq.png", (-16.0, 1.2, 7.0)),
    ("render_granja_chimenea_der.png", (16.0, 1.2, 7.0)),
]

for nom, pos in vistas:
    cam_obj.location = pos
    bpy.context.scene.render.filepath = os.path.join(DIR_OUT, nom)
    bpy.ops.render.render(write_still=True)
    print(f"Renderizado y guardado: {nom}")
