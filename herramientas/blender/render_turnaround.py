"""
render_turnaround.py
Generador automatizado de hojas de modelo (Turnaround Model Sheets) multi-ángulo desde Blender.
Renderiza 4 vistas ortográficas y de perspectiva (Frente, Perfil, Trasera, 3/4) de cualquier modelo .glb
adaptando dinámicamente el encuadre al tamaño del modelo y asegurando la pose de reposo (REST).

Uso:
    blender -b --factory-startup -P herramientas/blender/render_turnaround.py -- --modelo <ruta.glb> --salida <carpeta_salida>
"""

import sys
import os
import math

try:
    import bpy
    from mathutils import Vector
except ImportError:
    print("Este script debe ejecutarse dentro de Blender: blender -b -P render_turnaround.py -- ...")
    sys.exit(1)


def parse_args():
    argv = sys.argv
    if "--" not in argv:
        return None, None
    args = argv[argv.index("--") + 1:]
    modelo_path = None
    salida_dir = None
    
    for i in range(len(args)):
        if args[i] == "--modelo" and i + 1 < len(args):
            modelo_path = os.path.abspath(args[i + 1])
        elif args[i] == "--salida" and i + 1 < len(args):
            salida_dir = os.path.abspath(args[i + 1])
            
    return modelo_path, salida_dir


def limpiar_escena():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def importar_glb(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el modelo: {ruta}")
    bpy.ops.import_scene.gltf(filepath=ruta)
    
    # Asegurar pose de reposo (REST) en todas las armaduras y anular acciones activas
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            obj.data.pose_position = 'REST'
            if obj.animation_data:
                obj.animation_data.action = None
    bpy.context.view_layer.update()
    
    # Calcular bounding box global
    objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if not objs:
        raise ValueError("El archivo .glb no contiene mallas (meshes).")
        
    min_coord = Vector((float('inf'), float('inf'), float('inf')))
    max_coord = Vector((float('-inf'), float('-inf'), float('-inf')))
    
    for obj in objs:
        for v in obj.bound_box:
            world_v = obj.matrix_world @ Vector(v)
            min_coord.x = min(min_coord.x, world_v.x)
            min_coord.y = min(min_coord.y, world_v.y)
            min_coord.z = min(min_coord.z, world_v.z)
            max_coord.x = max(max_coord.x, world_v.x)
            max_coord.y = max(max_coord.y, world_v.y)
            max_coord.z = max(max_coord.z, world_v.z)
            
    centro = (min_coord + max_coord) * 0.5
    dimensiones = max_coord - min_coord
    return centro, dimensiones


def configurar_estudio(centro, dimensiones):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    
    # Luz principal cálida
    luz_key_data = bpy.data.lights.new(name="LuzKey", type='SUN')
    luz_key_data.energy = 3.5
    luz_key_data.color = (1.0, 0.96, 0.88)
    luz_key = bpy.data.objects.new(name="LuzKey", object_data=luz_key_data)
    luz_key.rotation_euler = (math.radians(45), math.radians(15), math.radians(35))
    scene.collection.objects.link(luz_key)
    
    # Luz de relleno fría
    luz_fill_data = bpy.data.lights.new(name="LuzFill", type='SUN')
    luz_fill_data.energy = 1.8
    luz_fill_data.color = (0.75, 0.85, 0.95)
    luz_fill = bpy.data.objects.new(name="LuzFill", object_data=luz_fill_data)
    luz_fill.rotation_euler = (math.radians(30), math.radians(-30), math.radians(-145))
    scene.collection.objects.link(luz_fill)


def renderizar_vistas(centro, dimensiones, salida_dir, nombre_base):
    os.makedirs(salida_dir, exist_ok=True)
    scene = bpy.context.scene
    
    alto = max(dimensiones.z, 0.1)
    ancho_max = max(dimensiones.x, dimensiones.y, 0.1)
    tamano_encuadre = max(alto, ancho_max) * 1.15
    
    # Cámara ajustada al tamaño exacto del modelo
    cam_data = bpy.data.cameras.new("CamaraTurnaround")
    cam_data.lens = 50.0
    cam_obj = bpy.data.objects.new("CamaraTurnaround", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    # Para perspectiva: calcular distancia exacta para encuadrar al 85% de la ventana
    sensor_h = cam_data.sensor_height if hasattr(cam_data, 'sensor_height') else 24.0
    fov_vertical = 2.0 * math.atan(sensor_h / (2.0 * cam_data.lens))
    distancia_persp = (tamano_encuadre * 0.5) / math.tan(fov_vertical * 0.5) * 1.12
    distancia_orto = tamano_encuadre * 1.5
    
    vistas = [
        ("01_frente", (centro.x, centro.y - distancia_orto, centro.z), (math.radians(90), 0, 0), True),
        ("02_perfil_derecho", (centro.x + distancia_orto, centro.y, centro.z), (math.radians(90), 0, math.radians(90)), True),
        ("03_trasera", (centro.x, centro.y + distancia_orto, centro.z), (math.radians(90), 0, math.radians(180)), True),
        ("04_perspectiva_3_4", (centro.x + distancia_persp * 0.70, centro.y - distancia_persp * 0.70, centro.z + tamano_encuadre * 0.35), (math.radians(65), 0, math.radians(45)), False)
    ]
    
    rutas_generadas = []
    
    for etiqueta, pos, rot, es_orto in vistas:
        cam_obj.location = pos
        # Apuntar siempre al centro del modelo (la rotación fija dejaba la vista 3/4 cortada por arriba)
        direccion = centro - Vector(pos)
        cam_obj.rotation_euler = direccion.to_track_quat('-Z', 'Y').to_euler()
        
        if es_orto:
            cam_data.type = 'ORTHO'
            cam_data.ortho_scale = tamano_encuadre
        else:
            cam_data.type = 'PERSP'
            
        nombre_archivo = f"{nombre_base}_{etiqueta}.png"
        ruta_salida = os.path.join(salida_dir, nombre_archivo)
        scene.render.filepath = ruta_salida
        bpy.ops.render.render(write_still=True)
        print(f"[Turnaround] Renderizado: {ruta_salida}")
        rutas_generadas.append(ruta_salida)
        
    return rutas_generadas


def main():
    modelo_path, salida_dir = parse_args()
    if not modelo_path:
        print("Uso: blender -b -P render_turnaround.py -- --modelo <ruta.glb> [--salida <dir>]")
        sys.exit(1)
        
    if not salida_dir:
        salida_dir = os.path.join(os.path.dirname(modelo_path), "vistas")
        
    nombre_base = os.path.splitext(os.path.basename(modelo_path))[0]
    limpiar_escena()
    centro, dimensiones = importar_glb(modelo_path)
    configurar_estudio(centro, dimensiones)
    rutas = renderizar_vistas(centro, dimensiones, salida_dir, nombre_base)
    print(f"\n[Turnaround] ¡4 Vistas generadas con éxito para {nombre_base} en {salida_dir}!")


if __name__ == "__main__":
    main()
