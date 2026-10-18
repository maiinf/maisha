import bpy
import os
import math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIR_KITOVU = os.path.join(BASE_DIR, "arte", "mundos", "kitovu")
DIR_MODELOS = os.path.join(BASE_DIR, "modelos", "entorno")
DIR_BLEND = os.path.join(BASE_DIR, "herramientas", "blender", "fuentes")
DIR_OUT = "/Users/iinfafer/.gemini/antigravity/brain/6baa257f-5b81-4a6e-8f7a-1cebbcab1026"

def limpiar_escena():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def obtener_material_textura(nombre, ruta_imagen, rugosidad=0.85, metalicidad=0.0, usar_alpha=False):
    mat = bpy.data.materials.new(name=nombre)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    
    if os.path.exists(ruta_imagen):
        img = bpy.data.images.load(ruta_imagen, check_existing=True)
        img.colorspace_settings.name = 'sRGB'
        tex_node = nodes.new("ShaderNodeTexImage")
        tex_node.image = img
        tex_node.interpolation = 'Closest' # Pixel art nearest neighbor!
        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        if usar_alpha and 'Alpha' in tex_node.outputs:
            links.new(tex_node.outputs['Alpha'], bsdf.inputs['Alpha'])
            if hasattr(mat, 'blend_method'):
                mat.blend_method = 'CLIP'
    
    if 'Roughness' in bsdf.inputs:
        bsdf.inputs['Roughness'].default_value = rugosidad
    if 'Metallic' in bsdf.inputs:
        bsdf.inputs['Metallic'].default_value = metalicidad
    return mat

def obtener_material_color(nombre, hex_color, rugosidad=0.8, emis_hex=None, emis_str=0.0):
    mat = bpy.data.materials.new(name=nombre)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    
    h = hex_color.lstrip('#')
    srgb = tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    bsdf.inputs['Base Color'].default_value = (*linear, 1.0)
    bsdf.inputs['Roughness'].default_value = rugosidad
    if emis_hex and emis_str > 0:
        eh = emis_hex.lstrip('#')
        esrgb = tuple(int(eh[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        elinear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in esrgb]
        bsdf.inputs['Emission Color'].default_value = (*elinear, 1.0)
        bsdf.inputs['Emission Strength'].default_value = emis_str
    return mat

def asignar_material(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def crear_prisma_tejado_uv(nombre, x_min, x_max, y_front, y_back, z_base, z_top, mat=None, u_rep=3.0, v_rep=2.0):
    mesh = bpy.data.meshes.new(nombre)
    obj = bpy.data.objects.new(nombre, mesh)
    bpy.context.collection.objects.link(obj)
    
    y_ridge = (y_front + y_back) * 0.5
    verts = [
        (x_min, y_front, z_base), # 0: Front Left
        (x_max, y_front, z_base), # 1: Front Right
        (x_min, y_back, z_base),  # 2: Back Left
        (x_max, y_back, z_base),  # 3: Back Right
        (x_min, y_ridge, z_top),  # 4: Ridge Left
        (x_max, y_ridge, z_top),  # 5: Ridge Right
    ]
    faces = [
        (0, 1, 5, 4), # Vertiente frontal
        (5, 3, 2, 4), # Vertiente trasera
        (0, 4, 2),    # Hastial izquierdo
        (1, 3, 5),    # Hastial derecho
        (0, 2, 3, 1), # Techo inferior
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    
    uv_layer = mesh.uv_layers.new(name="UVMap")
    uv_coords = [
        # Cara 0: Frontal (0, 1, 5, 4)
        [(0.0, 0.0), (u_rep, 0.0), (u_rep, v_rep), (0.0, v_rep)],
        # Cara 1: Trasera (5, 3, 2, 4)
        [(u_rep, v_rep), (u_rep, 0.0), (0.0, 0.0), (0.0, v_rep)],
        # Cara 2: Hastial izq (0, 4, 2)
        [(0.0, 0.0), (u_rep * 0.5, v_rep), (u_rep, 0.0)],
        # Cara 3: Hastial der (1, 3, 5)
        [(0.0, 0.0), (u_rep, 0.0), (u_rep * 0.5, v_rep)],
        # Cara 4: Inferior (0, 2, 3, 1)
        [(0.0, 0.0), (0.0, 1.0), (u_rep, 1.0), (u_rep, 0.0)],
    ]
    
    loop_idx = 0
    for face_idx, poly in enumerate(mesh.polygons):
        f_uvs = uv_coords[face_idx]
        for v_idx in range(len(poly.vertices)):
            uv_layer.data[loop_idx].uv = f_uvs[v_idx]
            loop_idx += 1
            
    if mat:
        asignar_material(obj, mat)
    return obj

def crear_pared_uv(nombre, x0, x1, y, z0, z1, mat, u_range=(0.0, 1.0), v_range=(0.0, 1.0), invertir=False):
    mesh = bpy.data.meshes.new(nombre)
    obj = bpy.data.objects.new(nombre, mesh)
    bpy.context.collection.objects.link(obj)
    
    verts = [
        (x0, y, z0),
        (x1, y, z0),
        (x1, y, z1),
        (x0, y, z1),
    ]
    faces = [(3, 2, 1, 0)] if invertir else [(0, 1, 2, 3)]
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    
    uv_layer = mesh.uv_layers.new(name="UVMap")
    u0, u1 = u_range
    v0, v1 = v_range
    uv_coords = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    if invertir:
        uv_coords = [(u0, v1), (u1, v1), (u1, v0), (u0, v0)]
    for i, loop in enumerate(mesh.loops):
        uv_layer.data[i].uv = uv_coords[i % 4]
        
    if mat:
        asignar_material(obj, mat)
    return obj

def construir_casa_granja_completa():
    limpiar_escena()
    
    tex_frontal = os.path.join(DIR_KITOVU, "casa_granja.png")
    tex_trasera = os.path.join(DIR_KITOVU, "trasera_casa_granja.png")
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    tex_piedra = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    tex_molino = os.path.join(DIR_KITOVU, "molino.png")
    
    mat_frontal = obtener_material_textura("Mat_Granja_Frontal", tex_frontal, rugosidad=0.88, usar_alpha=True)
    mat_trasera = obtener_material_textura("Mat_Granja_Trasera", tex_trasera, rugosidad=0.88, usar_alpha=True)
    mat_tejado = obtener_material_textura("Mat_Granja_Tejado", tex_paja, rugosidad=0.92)
    mat_troncos = obtener_material_textura("Mat_Granja_Troncos", tex_troncos, rugosidad=0.85)
    mat_piedra = obtener_material_textura("Mat_Granja_Piedra", tex_piedra, rugosidad=0.90)
    mat_madera_viga = obtener_material_color("Mat_Madera_Viga", "#78350F", rugosidad=0.8)
    mat_farol = obtener_material_color("Mat_Farol", "#FDE047", rugosidad=0.2, emis_hex="#FEF08A", emis_str=4.0)
    mat_molino = obtener_material_textura("Mat_Molino", tex_molino, rugosidad=0.8, usar_alpha=True)
    
    w = 8.8
    depth = 2.4
    cx = 0.0
    
    # 1. Zócalo de mampostería de piedra perimetral (base sólida en 360°)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, depth * 0.5, 0.35))
    zocalo = bpy.context.active_object
    zocalo.name = "Granja_Zocalo"
    zocalo.scale = (w, depth, 0.7)
    asignar_material(zocalo, mat_piedra)
    
    # 2. Paredes laterales de troncos (cerradas en 360°)
    for px, sign in [(cx - w * 0.5 + 0.05, -1), (cx + w * 0.5 - 0.05, 1)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, depth * 0.5, 1.85))
        pared_lat = bpy.context.active_object
        pared_lat.name = f"Granja_Pared_Lat_{'D' if sign>0 else 'I'}"
        pared_lat.scale = (0.1, depth - 0.1, 2.3)
        asignar_material(pared_lat, mat_troncos)

    # 3. Fachada Frontal de la pared (desde el suelo z=0 hasta el inicio del alero z=3.0)
    # UV mapeada a la zona inferior de casa_granja.png (u de 0.163 a 0.924, v de 0.057 a 0.464)
    crear_pared_uv("Granja_Pared_Frontal", cx - w * 0.5, cx + w * 0.5, -0.02, 0.0, 3.0, mat_frontal, 
                   u_range=(0.163, 0.924), v_range=(0.057, 0.464), invertir=False)
    
    # 4. Fachada Trasera de la pared (desde el suelo z=0 hasta el inicio del alero z=3.0)
    # UV mapeada a la zona inferior de trasera_casa_granja.png
    crear_pared_uv("Granja_Pared_Trasera", cx - w * 0.5, cx + w * 0.5, depth + 0.02, 0.0, 3.0, mat_trasera,
                   u_range=(0.163, 0.924), v_range=(0.057, 0.464), invertir=True)

    # 5. Gran Tejado a dos aguas sólido en 360° con cumbrera central
    # Aleros voladizos en las 4 direcciones (sobrevuela 0.35m en cada lado)
    crear_prisma_tejado_uv("Granja_Techo", cx - w * 0.5 - 0.35, cx + w * 0.5 + 0.35, -0.35, depth + 0.35, 2.95, 5.2, mat_tejado, u_rep=3.5, v_rep=2.2)

    # Buhardilla superior 3D con techillo y ventana redonda
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, depth * 0.28, 4.1))
    buhardilla = bpy.context.active_object
    buhardilla.name = "Granja_Buhardilla"
    buhardilla.scale = (1.5, 0.9, 1.1)
    asignar_material(buhardilla, mat_troncos)
    
    crear_prisma_tejado_uv("Granja_Buhardilla_Techo", cx - 0.85, cx + 0.85, -0.25, depth * 0.45, 4.5, 5.15, mat_tejado, u_rep=1.0, v_rep=1.0)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.35, depth=0.1, location=(cx, -0.22, 4.15))
    cristal_buh = bpy.context.active_object
    cristal_buh.name = "Granja_Buhardilla_Ventana"
    cristal_buh.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(cristal_buh, mat_farol)

    # 6. Porche Frontal 3D que se extiende hacia el jugador (Y = -0.4 a -0.75)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, -0.4, 0.18))
    porche_suelo = bpy.context.active_object
    porche_suelo.name = "Granja_Porche_Suelo"
    porche_suelo.scale = (5.8, 0.75, 0.36)
    asignar_material(porche_suelo, mat_piedra)
    
    for px in [cx - 2.5, cx - 0.85, cx + 0.85, cx + 2.5]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.075, depth=2.1, location=(px, -0.72, 1.20))
        poste = bpy.context.active_object
        poste.name = "Granja_Poste"
        asignar_material(poste, mat_madera_viga)
        
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, -0.40, 2.30))
    alero_porche = bpy.context.active_object
    alero_porche.name = "Granja_Porche_Techo"
    alero_porche.scale = (6.0, 0.90, 0.12)
    alero_porche.rotation_euler = (math.radians(10), 0, 0)
    asignar_material(alero_porche, mat_tejado)
    
    # Farol colgante encendido en el porche
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.16, location=(cx + 1.1, -0.68, 2.12))
    farol = bpy.context.active_object
    farol.name = "Granja_Farol"
    asignar_material(farol, mat_farol)

    # 7. Gran chimenea lateral de mampostería de piedra (a la derecha)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx + w * 0.5 - 0.75, depth * 0.5, 3.1))
    chimenea = bpy.context.active_object
    chimenea.name = "Granja_Chimenea"
    chimenea.scale = (1.1, 1.1, 6.2)
    asignar_material(chimenea, mat_piedra)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx + w * 0.5 - 0.75, depth * 0.5, 6.3))
    chimenea_cap = bpy.context.active_object
    chimenea_cap.name = "Granja_Chimenea_Cap"
    chimenea_cap.scale = (1.3, 1.3, 0.25)
    asignar_material(chimenea_cap, mat_piedra)

    # 8. Rueda de molino de agua lateral (a la izquierda)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.22, depth=0.8, location=(cx - w * 0.5 - 0.42, depth * 0.5, 1.6))
    eje_rueda = bpy.context.active_object
    eje_rueda.name = "Granja_Molino_Eje"
    eje_rueda.rotation_euler = (0, math.radians(90), 0)
    asignar_material(eje_rueda, mat_madera_viga)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.45, depth=0.32, location=(cx - w * 0.5 - 0.52, depth * 0.5, 1.6))
    aro_rueda = bpy.context.active_object
    aro_rueda.name = "Granja_Molino_Aro"
    aro_rueda.rotation_euler = (0, math.radians(90), 0)
    asignar_material(aro_rueda, mat_molino)
    
    for i in range(8):
        ang = i * (math.pi / 4)
        lx = cx - w * 0.5 - 0.52
        ly = depth * 0.5 + math.cos(ang) * 1.15
        lz = 1.6 + math.sin(ang) * 1.15
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lx, ly, lz))
        pala = bpy.context.active_object
        pala.name = f"Granja_Pala_{i}"
        pala.scale = (0.32, 0.28, 0.05)
        pala.rotation_euler = (ang, 0, 0)
        asignar_material(pala, mat_madera_viga)

    # Exportar GLB y BLEND
    os.makedirs(DIR_MODELOS, exist_ok=True)
    os.makedirs(DIR_BLEND, exist_ok=True)
    ruta_glb = os.path.join(DIR_MODELOS, "casa_granja.glb")
    ruta_blend = os.path.join(DIR_BLEND, "casa_granja.blend")
    
    bpy.ops.wm.save_as_mainfile(filepath=ruta_blend)
    bpy.ops.export_scene.gltf(
        filepath=ruta_glb,
        export_format='GLB',
        use_selection=False,
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT',
        export_image_format='AUTO'
    )
    print(f"Exportado exitosamente: {ruta_glb} y {ruta_blend}")

if __name__ == "__main__":
    construir_casa_granja_completa()
