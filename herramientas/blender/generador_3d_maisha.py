#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generador_3d_maisha.py
Generador procedural de modelos 3D para Maisha (Godot 4.7) utilizando Blender 4.x (bpy).
Exporta modelos estilizados (.glb y .blend) para personajes, enemigos, arquitectura y kits de terreno.
"""

import bpy
import math
import os

# Rutas de salida relativas a la raíz del repositorio
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIR_PROYECTO = BASE_DIR
DIR_PERSONAJES = os.path.join(BASE_DIR, "modelos", "personajes")
DIR_ENEMIGOS = os.path.join(BASE_DIR, "modelos", "enemigos")
DIR_ENTORNO = os.path.join(BASE_DIR, "modelos", "entorno")
DIR_OBJETOS = os.path.join(BASE_DIR, "modelos", "objetos")
DIR_KITOVU = os.path.join(BASE_DIR, "arte", "mundos", "kitovu")
DIR_ALDEA = os.path.join(BASE_DIR, "arte", "mundos", "raiz", "aldea")
DIR_SIGILIA = os.path.join(BASE_DIR, "arte", "mundos", "sigilia", "maandiko")

for d in [DIR_PERSONAJES, DIR_ENEMIGOS, DIR_ENTORNO, DIR_OBJETOS, DIR_ALDEA, DIR_SIGILIA]:
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# UTILIDADES DE ESCENA Y MATERIALES
# ---------------------------------------------------------------------------

def limpiar_escena():
    """Elimina todos los objetos y mallas de la escena actual."""
    # Deseleccionar y eliminar todos los objetos de la escena
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)

def obtener_material(nombre, color_hex, roughness=0.6, metallic=0.0, emission_hex=None, emission_strength=0.0):
    """Crea o reutiliza un material Principled BSDF compatible con Blender 4.x y Godot 4."""
    if nombre in bpy.data.materials:
        return bpy.data.materials[nombre]

    mat = bpy.data.materials.new(name=nombre)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    def hex_to_rgb(h):
        h = h.lstrip('#')
        srgb = [int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
        return (*linear, 1.0)

    if bsdf:
        bsdf.inputs["Base Color"].default_value = hex_to_rgb(color_hex)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission_hex and emission_strength > 0:
            bsdf.inputs["Emission Color"].default_value = hex_to_rgb(emission_hex)
            bsdf.inputs["Emission Strength"].default_value = emission_strength

    return mat

def obtener_material_textura(nombre, ruta_imagen, rugosidad=0.85, metalicidad=0.0, usar_alpha=False):
    """Crea un material PBR con textura de imagen pixel art (interpolación Closest)."""
    if nombre in bpy.data.materials:
        return bpy.data.materials[nombre]
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
        tex_node.interpolation = 'Closest'
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

def get_mat(clave):
    """Devuelve el material correspondiente según la paleta oficial de Maisha."""
    paleta_defs = {
        # Maisha
        "maisha_cuerpo": ("Mat_Maisha_Cuerpo", "#FFE08A", 0.5, 0.0, None, 0.0),
        "maisha_sombra": ("Mat_Maisha_Sombra", "#E8B860", 0.6, 0.0, None, 0.0),
        "brote_verde": ("Mat_Brote_Verde", "#6FCF4F", 0.4, 0.0, "#86EFAC", 0.3),
        "corazon_asili": ("Mat_Corazon_Asili", "#DF9022", 0.2, 0.0, "#FFF8E8", 2.2),
        "ojos_negros": ("Mat_Ojos_Negros", "#140E18", 0.1, 0.0, None, 0.0),
        "rubor": ("Mat_Rubor", "#DE6771", 0.7, 0.0, None, 0.0),
        "cetro_madera": ("Mat_Cetro_Madera", "#7A4A2A", 0.7, 0.0, None, 0.0),
        "cetro_gema": ("Mat_Cetro_Gema", "#FFAA00", 0.1, 0.0, "#FFDD00", 3.0),
        
        # Aldeanos
        "pino_seta_rojo": ("Mat_Pino_Seta", "#5C2626", 0.85, 0.0, None, 0.0),
        "pino_seta_puntos": ("Mat_Pino_Puntos", "#FEF3C7", 0.5, 0.0, None, 0.0),
        "cuero_mochila": ("Mat_Cuero_Mochila", "#78350F", 0.6, 0.0, None, 0.0),
        "castor_pelo": ("Mat_Castor_Pelo", "#5A3825", 0.8, 0.0, None, 0.0),
        "castor_peto": ("Mat_Castor_Peto", "#2D4A3E", 0.7, 0.0, None, 0.0),
        "corteza_delantal": ("Mat_Corteza_Delantal", "#3F2618", 0.8, 0.0, None, 0.0),
        "metal_forja": ("Mat_Metal_Forja", "#475569", 0.3, 0.7, None, 0.0),
        
        # Corrupción y Enemigos
        "petrino_roca": ("Mat_Petrino_Roca", "#525649", 0.85, 0.0, None, 0.0),
        "petrino_amatista": ("Mat_Petrino_Amatista", "#7C3AED", 0.2, 0.0, "#C084FC", 2.8),
        "corrupcion_giza": ("Mat_Corrupcion_Giza", "#1E1B4B", 0.9, 0.0, None, 0.0),
        "hongo_negro": ("Mat_Hongo_Negro", "#171717", 0.5, 0.0, "#A855F7", 0.8),
        
        # Arquitectura y Naturaleza
        "arbol_corteza": ("Mat_Arbol_Corteza", "#452B1F", 0.9, 0.0, None, 0.0),
        "musgo_hojas": ("Mat_Musgo_Hojas", "#365314", 0.6, 0.0, None, 0.0),
        "madera_tablas": ("Mat_Madera_Tablas", "#854D0E", 0.7, 0.0, None, 0.0),
        "farol_luz": ("Mat_Farol_Luz", "#FDE047", 0.2, 0.0, "#FEF08A", 4.0),
        "agua_limpia": ("Mat_Agua_Limpia", "#38BDF8", 0.15, 0.0, "#0284C7", 0.2),
        "piedra_plaza": ("Mat_Piedra_Plaza", "#64748B", 0.8, 0.0, None, 0.0),
        "oro_reliquia": ("Mat_Oro_Reliquia", "#F59E0B", 0.25, 0.8, "#FDE68A", 1.0),
        "tinta_sigilia": ("Mat_Tinta_Sigilia", "#312E81", 0.3, 0.0, "#4F46E5", 1.2),
        "marmol_sigilia": ("Mat_Marmol_Sigilia", "#E2E8F0", 0.5, 0.0, None, 0.0),
        "teja_cobriza": ("Mat_Teja_Cobriza", "#C2410C", 0.6, 0.0, None, 0.0),
        "tela_toldo": ("Mat_Tela_Toldo", "#DC2626", 0.7, 0.0, None, 0.0),
        "paja_dorada": ("Mat_Paja_Dorada", "#D97706", 0.8, 0.0, None, 0.0),
        "paja_techo": ("Mat_Paja_Techo", "#B45309", 0.85, 0.0, None, 0.0),
        "pizarra_nieve": ("Mat_Pizarra_Nieve", "#475569", 0.7, 0.0, None, 0.0),
        "madera_roja": ("Mat_Madera_Roja", "#991B1B", 0.75, 0.0, None, 0.0),
        "bambu_cana": ("Mat_Bambu_Cana", "#65A30D", 0.65, 0.0, None, 0.0),
        "madera_tronco": ("Mat_Madera_Tronco", "#5C381E", 0.75, 0.0, None, 0.0),
        "madera_viga": ("Mat_Madera_Viga", "#78350F", 0.7, 0.0, None, 0.0),
        "piedra_oscura": ("Mat_Piedra_Oscura", "#334155", 0.85, 0.0, None, 0.0)
    }
    nombre, col, rough, met, emis_col, emis_str = paleta_defs[clave]
    return obtener_material(nombre, col, rough, met, emis_col, emis_str)

def asignar_material(obj, mat):
    """Asigna un material como slot 0 del objeto."""
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

def suavizar(obj):
    """Activa sombreado suave para todos los polígonos."""
    for poly in obj.data.polygons:
        poly.use_smooth = True

def crear_prisma_tejado(nombre, x_min, x_max, y_front, y_back, z_base, z_top, mat=None, u_rep=3.0, v_rep=2.0):
    """Crea un tejado a dos aguas sólido en 360° con cumbrera en X y mapa UV automático."""
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

def crear_prisma_tejado_lr(nombre, x_left, x_right, y_min, y_max, z_base, z_top, mat=None):
    """Crea un tejado a dos aguas con cumbrera longitudinal en Y (vertientes hacia izquierda y derecha)."""
    mesh = bpy.data.meshes.new(nombre)
    obj = bpy.data.objects.new(nombre, mesh)
    bpy.context.collection.objects.link(obj)
    
    x_ridge = (x_left + x_right) * 0.5
    verts = [
        (x_left, y_min, z_base),  # 0: Left Front
        (x_left, y_max, z_base),  # 1: Left Back
        (x_right, y_min, z_base), # 2: Right Front
        (x_right, y_max, z_base), # 3: Right Back
        (x_ridge, y_min, z_top),  # 4: Ridge Front
        (x_ridge, y_max, z_top),  # 5: Ridge Back
    ]
    faces = [
        (0, 1, 5, 4), # Vertiente izquierda
        (4, 5, 3, 2), # Vertiente derecha
        (0, 4, 2),    # Hastial frontal
        (1, 3, 5),    # Hastial trasero
        (0, 2, 3, 1), # Techo inferior
    ]
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=True)
    if mat:
        asignar_material(obj, mat)
    return obj

def crear_pared_uv(nombre, x0, x1, y, z0, z1, mat, u_range=(0.0, 1.0), v_range=(0.0, 1.0), invertir=False):
    """Crea una pared vertical plana con mapeado UV configurable."""
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

def aplicar_uv_caja(obj, escala_u=1.0, escala_v=1.0):
    """Mapea UVs triplanares ortogonales en un objeto cúbico/prismático para texturas pixel art."""
    mesh = obj.data
    if not mesh.uv_layers:
        uv_layer = mesh.uv_layers.new(name="UVMap")
    else:
        uv_layer = mesh.uv_layers.active
    for poly in mesh.polygons:
        n = poly.normal
        for loop_idx in poly.loop_indices:
            v_idx = mesh.loops[loop_idx].vertex_index
            v = mesh.vertices[v_idx].co
            if abs(n.z) > 0.5:
                u, v_coord = v.x * escala_u, v.y * escala_v
            elif abs(n.x) > 0.5:
                u, v_coord = v.y * escala_u, v.z * escala_v
            else:
                u, v_coord = v.x * escala_u, v.z * escala_v
            uv_layer.data[loop_idx].uv = (u, v_coord)

def aplicar_uv_cilindro(obj, escala_u=1.0, escala_v=1.0):
    """Mapea UVs envolventes cilíndricas en 360° en un objeto cilíndrico o cónico alineado en Z."""
    mesh = obj.data
    if not mesh.uv_layers:
        uv_layer = mesh.uv_layers.new(name="UVMap")
    else:
        uv_layer = mesh.uv_layers.active
    for poly in mesh.polygons:
        n = poly.normal
        es_tapa = abs(n.z) > 0.85
        for loop_idx in poly.loop_indices:
            v_idx = mesh.loops[loop_idx].vertex_index
            v = mesh.vertices[v_idx].co
            if es_tapa:
                u = (v.x * escala_u) + 0.5
                v_coord = (v.y * escala_v) + 0.5
            else:
                ang = math.atan2(v.y, v.x) / (2.0 * math.pi) + 0.5
                u = ang * escala_u
                v_coord = v.z * escala_v
            uv_layer.data[loop_idx].uv = (u, v_coord)

DIR_BLEND = os.path.join(BASE_DIR, "herramientas", "blender", "fuentes")
os.makedirs(DIR_BLEND, exist_ok=True)

def exportar_modelo(nombre_base, carpeta):
    """Exporta la escena actual a .glb en carpeta y guarda copia .blend en herramientas/blender/fuentes."""
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

# ---------------------------------------------------------------------------
# GENERADORES DE MODELOS: PERSONAJES
# ---------------------------------------------------------------------------

def generar_maisha():
    """Genera a Maisha: espíritu de la vida, cabeza estilizada, brote, corazón y cetro."""
    limpiar_escena()
    
    # 1. Cabeza (chibi estilizado, z=0.95)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=16, radius=0.38, location=(0, 0, 0.95))
    cabeza = bpy.context.active_object
    cabeza.name = "Maisha_Cabeza"
    cabeza.scale = (1.05, 0.95, 0.95)
    asignar_material(cabeza, get_mat("maisha_cuerpo"))
    suavizar(cabeza)
    
    # 2. Ojos ovalados negros con brillo y rubor
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.065, location=(sign * 0.14, -0.32, 0.95))
        ojo = bpy.context.active_object
        ojo.name = f"Maisha_Ojo_{'D' if sign>0 else 'I'}"
        ojo.scale = (0.7, 0.4, 1.2)
        asignar_material(ojo, get_mat("ojos_negros"))
        
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.045, location=(sign * 0.20, -0.28, 0.85))
        rubor = bpy.context.active_object
        rubor.name = f"Maisha_Rubor_{'D' if sign>0 else 'I'}"
        rubor.scale = (1.0, 0.2, 0.5)
        asignar_material(rubor, get_mat("rubor"))

    # 3. Brote en la cabeza (tallo y 2 hojas)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=0.18, location=(0, 0, 1.34))
    tallo = bpy.context.active_object
    tallo.name = "Maisha_Tallo"
    tallo.rotation_euler = (math.radians(10), 0, math.radians(-5))
    asignar_material(tallo, get_mat("brote_verde"))
    
    for sign, rot in [(-1, -35), (1, 35)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=0.08, location=(sign * 0.08, 0, 1.42))
        hoja = bpy.context.active_object
        hoja.name = f"Maisha_Hoja_{'D' if sign>0 else 'I'}"
        hoja.scale = (1.2, 0.3, 0.6)
        hoja.rotation_euler = (0, math.radians(rot), 0)
        asignar_material(hoja, get_mat("brote_verde"))

    # 4. Torso cónico suave
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.26, radius2=0.18, depth=0.45, location=(0, 0, 0.55))
    cuerpo = bpy.context.active_object
    cuerpo.name = "Maisha_Cuerpo"
    asignar_material(cuerpo, get_mat("maisha_cuerpo"))
    suavizar(cuerpo)

    # 5. Corazón de Asili (en el pecho, luz dorada)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.07, location=(0, -0.21, 0.62))
    corazon = bpy.context.active_object
    corazon.name = "Maisha_Corazon_Asili"
    corazon.scale = (1.0, 0.5, 1.2)
    asignar_material(corazon, get_mat("corazon_asili"))

    # 6. Extremidades (brazos y piernas)
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.065, depth=0.32, location=(sign * 0.28, -0.05, 0.55))
        brazo = bpy.context.active_object
        brazo.name = f"Maisha_Brazo_{'D' if sign>0 else 'I'}"
        brazo.rotation_euler = (math.radians(-15), 0, sign * math.radians(-20))
        asignar_material(brazo, get_mat("maisha_cuerpo"))
        
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.075, depth=0.30, location=(sign * 0.12, 0, 0.16))
        pierna = bpy.context.active_object
        pierna.name = f"Maisha_Pierna_{'D' if sign>0 else 'I'}"
        asignar_material(pierna, get_mat("maisha_sombra"))

    # 7. Cetro de Raíz (en mano derecha)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.022, depth=0.95, location=(0.38, -0.15, 0.55))
    vara = bpy.context.active_object
    vara.name = "Cetro_Vara"
    vara.rotation_euler = (math.radians(10), math.radians(-10), 0)
    asignar_material(vara, get_mat("cetro_madera"))
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.09, location=(0.44, -0.22, 1.05))
    gema = bpy.context.active_object
    gema.name = "Cetro_Gema"
    asignar_material(gema, get_mat("cetro_gema"))

    exportar_modelo("maisha", DIR_PERSONAJES)

def generar_pino():
    """Genera a Pino: explorador con sombrero de seta roja y mochila de viaje."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.35, location=(0, 0, 0.85))
    cabeza = bpy.context.active_object
    cabeza.name = "Pino_Cabeza"
    asignar_material(cabeza, get_mat("maisha_cuerpo"))
    
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=0.62, radius2=0.08, depth=0.32, location=(0, 0, 1.15))
    sombrero = bpy.context.active_object
    sombrero.name = "Pino_Sombrero"
    asignar_material(sombrero, get_mat("pino_seta_rojo"))
    
    for ang in [0, 72, 144, 216, 288]:
        rad = math.radians(ang)
        x = math.cos(rad) * 0.38
        y = math.sin(rad) * 0.38
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.065, location=(x, y, 1.12))
        pto = bpy.context.active_object
        pto.scale = (1, 1, 0.3)
        asignar_material(pto, get_mat("pino_seta_puntos"))

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.28, depth=0.48, location=(0, 0, 0.45))
    cuerpo = bpy.context.active_object
    cuerpo.name = "Pino_Cuerpo"
    asignar_material(cuerpo, get_mat("castor_peto"))
    
    bpy.ops.mesh.primitive_cube_add(size=0.36, location=(0, 0.25, 0.55))
    mochila = bpy.context.active_object
    mochila.name = "Pino_Mochila"
    mochila.scale = (0.9, 0.7, 1.2)
    asignar_material(mochila, get_mat("cuero_mochila"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.09, depth=0.42, location=(0, 0.28, 0.82))
    saco = bpy.context.active_object
    saco.rotation_euler = (0, math.radians(90), 0)
    asignar_material(saco, get_mat("madera_tablas"))

    exportar_modelo("pino", DIR_PERSONAJES)

def generar_mzee_shamba():
    """Genera a Mzee Shamba: castor anciano agricultor con peto y bastón."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.44, location=(0, 0, 0.65))
    cuerpo = bpy.context.active_object
    cuerpo.name = "Shamba_Cuerpo"
    cuerpo.scale = (1.0, 1.1, 1.2)
    asignar_material(cuerpo, get_mat("castor_peto"))
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.35, location=(0, -0.15, 1.15))
    cabeza = bpy.context.active_object
    cabeza.name = "Shamba_Cabeza"
    asignar_material(cabeza, get_mat("castor_pelo"))
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.18, location=(0, -0.42, 1.08))
    hocico = bpy.context.active_object
    hocico.scale = (1.2, 0.8, 0.7)
    asignar_material(hocico, get_mat("maisha_sombra"))
    
    bpy.ops.mesh.primitive_cube_add(size=0.45, location=(0, 0.45, 0.25))
    cola = bpy.context.active_object
    cola.name = "Shamba_Cola"
    cola.scale = (0.7, 1.4, 0.15)
    cola.rotation_euler = (math.radians(-25), 0, 0)
    asignar_material(cola, get_mat("arbol_corteza"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=1.1, location=(0.42, -0.22, 0.55))
    baston = bpy.context.active_object
    baston.name = "Shamba_Baston"
    asignar_material(baston, get_mat("madera_tablas"))

    exportar_modelo("mzee_shamba", DIR_PERSONAJES)

def generar_corteza():
    """Genera a Corteza: herrero robusto con delantal de cuero y martillo."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_cube_add(size=0.55, location=(0, 0, 0.65))
    cuerpo = bpy.context.active_object
    cuerpo.name = "Corteza_Cuerpo"
    cuerpo.scale = (1.1, 0.8, 1.2)
    asignar_material(cuerpo, get_mat("corteza_delantal"))
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.32, location=(0, 0, 1.20))
    cabeza = bpy.context.active_object
    cabeza.name = "Corteza_Cabeza"
    asignar_material(cabeza, get_mat("maisha_sombra"))
    
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.10, minor_radius=0.03, location=(sign * 0.14, -0.26, 1.25))
        gafa = bpy.context.active_object
        gafa.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(gafa, get_mat("metal_forja"))

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.85, location=(0.48, -0.15, 0.55))
    mango = bpy.context.active_object
    asignar_material(mango, get_mat("madera_tablas"))
    
    bpy.ops.mesh.primitive_cube_add(size=0.22, location=(0.48, -0.15, 0.95))
    cabeza_martillo = bpy.context.active_object
    cabeza_martillo.scale = (0.9, 1.6, 0.9)
    asignar_material(cabeza_martillo, get_mat("metal_forja"))

    exportar_modelo("corteza", DIR_PERSONAJES)

# ---------------------------------------------------------------------------
# GENERADORES DE MODELOS: ENEMIGOS Y CORRUPCIÓN
# ---------------------------------------------------------------------------

def generar_petrino_giza():
    """Genera al Petrino de Giza: roca esférica con grietas amatistas luminosas."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.45, location=(0, 0, 0.48))
    roca = bpy.context.active_object
    roca.name = "Petrino_Cuerpo"
    asignar_material(roca, get_mat("petrino_roca"))
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.26, location=(0, 0, 0.48))
    nucleo = bpy.context.active_object
    nucleo.name = "Petrino_Amatista_Nucleo"
    asignar_material(nucleo, get_mat("petrino_amatista"))
    
    for ang, z_offset in [(45, 0.15), (160, -0.10), (280, 0.20)]:
        rad = math.radians(ang)
        x = math.cos(rad) * 0.60
        y = math.sin(rad) * 0.60
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.12, location=(x, y, 0.48 + z_offset))
        frag = bpy.context.active_object
        frag.scale = (1.2, 0.7, 0.9)
        asignar_material(frag, get_mat("petrino_roca"))

    exportar_modelo("petrino_giza", DIR_ENEMIGOS)

def generar_mzizi_raiz():
    """Genera a Mzizi: tocón de raíz colosal petrificada con ojos violetas."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.75, depth=1.1, location=(0, 0, 0.55))
    tocon = bpy.context.active_object
    tocon.name = "Mzizi_Tocon"
    tocon.scale = (1.1, 0.9, 1.0)
    asignar_material(tocon, get_mat("arbol_corteza"))
    
    for i in range(4):
        ang = i * (math.pi / 2) + 0.3
        x = math.cos(ang) * 0.85
        y = math.sin(ang) * 0.85
        bpy.ops.mesh.primitive_torus_add(major_radius=0.45, minor_radius=0.14, location=(x, y, 0.25))
        raiz = bpy.context.active_object
        raiz.rotation_euler = (math.radians(45), 0, ang)
        asignar_material(raiz, get_mat("arbol_corteza"))

    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.12, location=(sign * 0.32, -0.65, 0.75))
        ojo = bpy.context.active_object
        ojo.name = f"Mzizi_Ojo_{'D' if sign>0 else 'I'}"
        asignar_material(ojo, get_mat("petrino_amatista"))

    exportar_modelo("mzizi_raiz", DIR_ENEMIGOS)

def generar_babosa_oxido():
    """Genera la Babosa de Óxido: cuerpo alargado con concha de hierro oxidado."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.28, location=(0, 0, 0.20))
    cuerpo = bpy.context.active_object
    cuerpo.scale = (0.7, 1.6, 0.6)
    asignar_material(cuerpo, get_mat("maisha_sombra"))
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.32, location=(0, 0.10, 0.35))
    concha = bpy.context.active_object
    concha.scale = (0.9, 1.1, 0.8)
    asignar_material(concha, get_mat("petrino_roca"))
    
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.22, location=(sign * 0.10, -0.38, 0.38))
        antena = bpy.context.active_object
        antena.rotation_euler = (math.radians(-30), sign * math.radians(20), 0)
        asignar_material(antena, get_mat("corazon_asili"))

    exportar_modelo("babosa_oxido", DIR_ENEMIGOS)

def generar_corazon_giza():
    """Genera el Corazón de Giza (Núcleo de combate corrupto)."""
    limpiar_escena()
    
    for i in range(5):
        ang = i * (2 * math.pi / 5)
        x = math.cos(ang) * 0.42
        y = math.sin(ang) * 0.42
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.15, depth=0.85, location=(x, y, 0.42))
        espina = bpy.context.active_object
        espina.rotation_euler = (math.radians(15) * math.sin(ang), math.radians(15) * math.cos(ang), ang)
        asignar_material(espina, get_mat("corrupcion_giza"))

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.38, location=(0, 0, 0.75))
    cristal = bpy.context.active_object
    cristal.scale = (0.8, 0.8, 1.5)
    asignar_material(cristal, get_mat("petrino_amatista"))

    exportar_modelo("corazon_giza", DIR_ENEMIGOS)

# ---------------------------------------------------------------------------
# GENERADORES DE ENTORNO: ARQUITECTURA DE CUNA DE MUSGO
# ---------------------------------------------------------------------------

def generar_gran_arbol():
    """Genera el Gran Árbol hueco ancestral de Cuna de Musgo."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=2.2, depth=4.8, location=(0, 0, 2.4))
    tronco = bpy.context.active_object
    tronco.name = "GranArbol_Tronco"
    asignar_material(tronco, get_mat("arbol_corteza"))
    suavizar(tronco)
    
    for offset, rad in [((0, 0, 5.5), 3.2), ((-1.2, 0.8, 4.8), 2.4), ((1.2, -0.6, 5.0), 2.6)]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=rad, location=offset)
        copa = bpy.context.active_object
        copa.scale = (1.2, 1.1, 0.8)
        asignar_material(copa, get_mat("musgo_hojas"))
        suavizar(copa)

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.75, depth=1.6, location=(0, -2.1, 1.1))
    portal = bpy.context.active_object
    portal.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(portal, get_mat("corazon_asili"))

    exportar_modelo("gran_arbol", DIR_ENTORNO)

def generar_casa_pino():
    """Genera la Casa Seta de Pino (Cuna de Musgo) completa en 360°:
    Zócalo circular de piedra mampostera, pie cilíndrico de madera con textura pixel art y zunchos de hierro,
    gran tejado de sombrero de seta carmesí con motas blancas cremosas y láminas inferiores,
    puesto de vigía de Pino con barandilla, mástil con banderín y catalejo de latón,
    chimenea de tronco curvado, puerta de arco estilo hobbit con farol, y ventanas iluminadas en 360°."""
    limpiar_escena()
    
    tex_pared = os.path.join(DIR_ALDEA, "seta_pared_tile.png")
    tex_techo = os.path.join(DIR_ALDEA, "seta_tejado_tile.png")
    tex_zocalo = os.path.join(DIR_ALDEA, "ruina_mamposteria_tile.png")
    mat_pared = obtener_material_textura("Mat_Seta_Pared", tex_pared, rugosidad=0.82)
    mat_techo = obtener_material_textura("Mat_Seta_Techo", tex_techo, rugosidad=0.72)
    mat_zocalo = obtener_material_textura("Mat_Seta_Zocalo", tex_zocalo, rugosidad=0.88)
    
    # 1. Zócalo base circular de piedra
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=1.52, depth=0.45, location=(0, 0, 0.22))
    base = bpy.context.active_object
    asignar_material(base, mat_zocalo)
    aplicar_uv_cilindro(base, 3.0, 1.0)
    
    # 2. Pared cilíndrica de madera de la seta
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=1.38, depth=1.85, location=(0, 0, 1.15))
    pared = bpy.context.active_object
    asignar_material(pared, mat_pared)
    aplicar_uv_cilindro(pared, 3.5, 1.5)
    
    # Zunchos / cinchas de madera oscura en 360°
    for z in [0.48, 1.18, 1.88]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=1.42, depth=0.08, location=(0, 0, z))
        cincha = bpy.context.active_object
        asignar_material(cincha, get_mat("madera_viga"))
        
    # 3. Tejado de seta carmesí con motas
    # Láminas inferiores de la seta (gills)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=2.25, depth=0.15, location=(0, 0, 1.95))
    laminas = bpy.context.active_object
    asignar_material(laminas, get_mat("pino_seta_puntos"))
    
    # Sombrero cónico abombado
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=2.25, radius2=0.45, depth=1.5, location=(0, 0, 2.65))
    techo = bpy.context.active_object
    asignar_material(techo, mat_techo)
    aplicar_uv_cilindro(techo, 3.2, 1.8)
    
    # Cúpula de remate superior
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.62, location=(0, 0, 3.32))
    copete = bpy.context.active_object
    copete.scale = (1.0, 1.0, 0.65)
    asignar_material(copete, mat_techo)
    aplicar_uv_cilindro(copete, 2.0, 1.0)
    
    # 4. Puesto de vigía de Pino en la cima del sombrero
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.35, 0.25, 3.65))
    plataforma = bpy.context.active_object
    plataforma.scale = (1.1, 0.9, 0.08)
    asignar_material(plataforma, get_mat("madera_tablas"))
    
    # Barandilla de ramas de vigía
    for rx, ry in [(-0.18, 0.25), (0.88, 0.25), (0.35, -0.18), (0.35, 0.68)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.35, location=(rx, ry, 3.82))
        barrote = bpy.context.active_object
        asignar_material(barrote, get_mat("arbol_corteza"))
        
    # Mástil con banderín verde de hoja
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=1.1, location=(-0.15, -0.15, 4.2))
    mastil = bpy.context.active_object
    asignar_material(mastil, get_mat("madera_viga"))
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.02, -0.15, 4.6))
    banderin = bpy.context.active_object
    banderin.scale = (0.28, 0.02, 0.18)
    asignar_material(banderin, get_mat("brote_verde"))
    
    # Catalejo de latón dorado sobre trípode
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=0.42, location=(0.55, 0.15, 3.92))
    catalejo = bpy.context.active_object
    catalejo.rotation_euler = (math.radians(-15), math.radians(35), 0)
    asignar_material(catalejo, get_mat("oro_reliquia"))
    
    # 5. Chimenea de tronco curvado
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.18, depth=1.4, location=(0.85, 0.85, 2.9))
    chim = bpy.context.active_object
    chim.rotation_euler = (math.radians(12), math.radians(-10), 0)
    asignar_material(chim, get_mat("arbol_corteza"))
    
    # 6. Puerta frontal redonda de hobbit con herrajes
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.55, depth=0.18, location=(0, -1.35, 0.72))
    puerta_marco = bpy.context.active_object
    puerta_marco.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(puerta_marco, get_mat("madera_viga"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.46, depth=0.22, location=(0, -1.36, 0.72))
    puerta = bpy.context.active_object
    puerta.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(puerta, get_mat("arbol_corteza"))
    
    # Pomo de latón
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.065, location=(0.26, -1.48, 0.72))
    pomo = bpy.context.active_object
    asignar_material(pomo, get_mat("oro_reliquia"))
    
    # Porche con tejadillo y farol luminoso
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.52, 1.42))
    techillo = bpy.context.active_object
    techillo.scale = (1.18, 0.52, 0.09)
    techillo.rotation_euler = (math.radians(-15), 0, 0)
    asignar_material(techillo, get_mat("madera_tablas"))
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.14, location=(0.68, -1.50, 1.22))
    farol = bpy.context.active_object
    asignar_material(farol, get_mat("farol_luz"))
    
    # 7. Ventanas redondas iluminadas en laterales y trasera (visibles 360°)
    for wx, wy, wz, rx, ry in [
        (-1.35, 0.0, 1.15, 0, 90),
        (1.35, 0.0, 1.15, 0, -90),
        (0.0, 1.35, 1.15, -90, 0),
    ]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.34, depth=0.16, location=(wx, wy, wz))
        marco = bpy.context.active_object
        marco.rotation_euler = (math.radians(rx), math.radians(ry), 0)
        asignar_material(marco, get_mat("madera_viga"))
        
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.26, depth=0.20, location=(wx, wy, wz))
        cristal = bpy.context.active_object
        cristal.rotation_euler = (math.radians(rx), math.radians(ry), 0)
        asignar_material(cristal, get_mat("farol_luz"))
        
        # Cruz de celosía
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(wx, wy, wz))
        celosia = bpy.context.active_object
        celosia.scale = (0.50 if rx != 0 else 0.04, 0.50 if rx == 0 else 0.04, 0.50)
        asignar_material(celosia, get_mat("madera_viga"))

    exportar_modelo("casa_pino", DIR_ENTORNO)

def generar_forja_corteza():
    """Genera el taller de herrería de Corteza (Cuna de Musgo) completo en 360°:
    Plataforma de losas de piedra, gran horno de forja de mampostería con boca arqueada y brasas ardientes,
    chimenea de piedra con chimeneón escalonado, tejadillo de tablillas sobre entramado,
    tocón de roble con yunque de acero de doble cuerno, cubeta de enfriamiento con agua reflectante,
    mesa de herramientas lateral, y leñera de troncos trasera."""
    limpiar_escena()
    
    tex_piedra = os.path.join(DIR_ALDEA, "forja_mamposteria_tile.png")
    tex_techo = os.path.join(DIR_ALDEA, "forja_tejado_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_piedra = obtener_material_textura("Mat_Forja_Piedra", tex_piedra, rugosidad=0.88)
    mat_techo = obtener_material_textura("Mat_Forja_Techo", tex_techo, rugosidad=0.80)
    mat_madera = obtener_material_textura("Mat_Forja_Madera", tex_troncos, rugosidad=0.82)
    
    # 1. Plataforma base de losas de piedra
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.4, 0.15))
    suelo = bpy.context.active_object
    suelo.scale = (3.5, 3.3, 0.3)
    asignar_material(suelo, mat_piedra)
    aplicar_uv_caja(suelo, 2.0, 2.0)
    
    # 2. Horno de forja de piedra
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.3, 0.2, 1.1))
    horno = bpy.context.active_object
    horno.scale = (2.2, 1.6, 1.6)
    asignar_material(horno, mat_piedra)
    aplicar_uv_caja(horno, 1.8, 1.5)
    
    # Zócalo inferior del horno
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.3, 0.2, 0.38))
    zoc_h = bpy.context.active_object
    zoc_h.scale = (2.35, 1.75, 0.25)
    asignar_material(zoc_h, mat_piedra)
    aplicar_uv_caja(zoc_h, 1.5, 0.5)
    
    # Hogar interior con brasas ardientes
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.3, -0.55, 0.85))
    foco_fuego = bpy.context.active_object
    foco_fuego.scale = (1.0, 0.5, 0.5)
    asignar_material(foco_fuego, get_mat("corazon_asili"))
    
    # Campana y chimenea de mampostería
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.48, depth=1.8, location=(0.8, 0.3, 2.5))
    chim = bpy.context.active_object
    asignar_material(chim, mat_piedra)
    aplicar_uv_cilindro(chim, 1.8, 1.5)
    
    # Remate de chimenea
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.56, depth=0.22, location=(0.8, 0.3, 3.42))
    remate = bpy.context.active_object
    asignar_material(remate, mat_piedra)
    aplicar_uv_cilindro(remate, 1.5, 0.5)
    
    # Tejadillo de tablillas solapadas sobre el horno en 360°
    crear_prisma_tejado("Forja_Techo", -0.9, 1.5, -0.7, 1.1, 2.1, 2.8, mat_techo, u_rep=2.0, v_rep=1.5)
    
    # 3. Yunque sobre tocón
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.42, depth=0.55, location=(-0.3, -1.3, 0.35))
    tocon = bpy.context.active_object
    asignar_material(tocon, mat_madera)
    aplicar_uv_cilindro(tocon, 1.5, 1.0)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.3, -1.3, 0.75))
    yunque_cuerpo = bpy.context.active_object
    yunque_cuerpo.scale = (0.75, 0.38, 0.30)
    asignar_material(yunque_cuerpo, get_mat("metal_forja"))
    
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.18, radius2=0.03, depth=0.38, location=(-0.78, -1.3, 0.78))
    cuerno = bpy.context.active_object
    cuerno.rotation_euler = (0, math.radians(-90), 0)
    asignar_material(cuerno, get_mat("metal_forja"))
    
    # 4. Cubeta de enfriamiento de madera con agua reflectante
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.35, -0.7, 0.45))
    cubeta = bpy.context.active_object
    cubeta.scale = (0.65, 1.15, 0.6)
    asignar_material(cubeta, mat_madera)
    aplicar_uv_caja(cubeta, 1.0, 1.0)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.35, -0.7, 0.68))
    agua_c = bpy.context.active_object
    agua_c.scale = (0.52, 1.0, 0.08)
    asignar_material(agua_c, get_mat("agua_limpia"))
    
    # 5. Mesa de trabajo lateral con herramientas
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.15, 0.2, 0.65))
    mesa = bpy.context.active_object
    mesa.scale = (0.7, 1.45, 0.7)
    asignar_material(mesa, mat_madera)
    aplicar_uv_caja(mesa, 1.2, 1.0)
    
    # Tenazas y martillo sobre la mesa
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=0.45, location=(-1.15, 0.2, 1.03))
    mango = bpy.context.active_object
    mango.rotation_euler = (0, math.radians(90), 0)
    asignar_material(mango, mat_madera)
    
    bpy.ops.mesh.primitive_cube_add(size=0.08, location=(-0.95, 0.2, 1.03))
    cabeza_m = bpy.context.active_object
    cabeza_m.scale = (1.5, 0.8, 0.8)
    asignar_material(cabeza_m, get_mat("metal_forja"))
    
    # 6. Leñera trasera (sólida y volumétrica en 360°)
    for lz in [0.35, 0.65]:
        for ly in [0.95, 1.25]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.12, depth=1.9, location=(0.3, ly, lz))
            leno = bpy.context.active_object
            leno.rotation_euler = (0, math.radians(90), 0)
            asignar_material(leno, mat_madera)
            aplicar_uv_cilindro(leno, 1.0, 2.0)

    exportar_modelo("forja_corteza", DIR_ENTORNO)

def generar_molino_shamba():
    """Genera la cabaña con rueda de molino de agua de Mzee Shamba completa en 360°."""
    limpiar_escena()
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    mat_troncos = obtener_material_textura("Mat_Molino_Troncos", tex_troncos, rugosidad=0.85)
    mat_techo = obtener_material_textura("Mat_Molino_Techo", tex_paja, rugosidad=0.92)
    mat_madera = obtener_material("Mat_Molino_Madera", "#8B5A2B", roughness=0.8)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.1))
    casa = bpy.context.active_object
    casa.scale = (2.6, 2.0, 2.2)
    asignar_material(casa, mat_troncos)
    aplicar_uv_caja(casa, 1.2, 1.0)

    crear_prisma_tejado("Molino_Techo", -1.5, 1.5, -1.2, 1.2, 2.2, 3.4, mat_techo)

    # Rueda hidráulica
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.1, depth=0.32, location=(1.55, 0, 0.9))
    rueda = bpy.context.active_object
    rueda.rotation_euler = (0, math.radians(90), 0)
    asignar_material(rueda, mat_madera)
    aplicar_uv_cilindro(rueda, 1.0, 1.0)

    exportar_modelo("molino_shamba", DIR_ENTORNO)

def generar_puente_madera():
    """Genera el puente de madera rústico con barandilla y tablones UV-mapeados."""
    limpiar_escena()
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_troncos = obtener_material_textura("Mat_Puente_Troncos", tex_troncos, rugosidad=0.85)
    mat_madera = obtener_material("Mat_Puente_Madera", "#5C3317", roughness=0.8)

    for i in range(7):
        y_pos = (i - 3) * 0.45
        z_curve = math.cos((i - 3) * 0.3) * 0.12
        bpy.ops.mesh.primitive_cube_add(size=0.4, location=(0, y_pos, z_curve + 0.1))
        tablon = bpy.context.active_object
        tablon.scale = (3.2, 0.9, 0.18)
        asignar_material(tablon, mat_troncos)
        aplicar_uv_caja(tablon, 0.8, 0.8)

    for sign in [-1, 1]:
        for i in [-3, 0, 3]:
            y_pos = i * 0.45
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=0.75, location=(sign * 0.65, y_pos, 0.45))
            poste = bpy.context.active_object
            asignar_material(poste, mat_madera)
            
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=3.2, location=(sign * 0.65, 0, 0.8))
        pasamanos = bpy.context.active_object
        pasamanos.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(pasamanos, mat_madera)

    exportar_modelo("puente_madera", DIR_ENTORNO)

def generar_farol_madera():
    """Genera un farol de poste tallado en 3D con linterna física de celosía, caperuza y núcleo brillante:
    Poste octogonal estriado, basa de refuerzo, brazo curvo con tornapunta, linterna hexagonal con caperuza cónica,
    y núcleo luminoso incandescente en 360°."""
    limpiar_escena()
    
    # 1. Basa de apoyo en el suelo
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.18, depth=0.3, location=(0, 0, 0.15))
    basa = bpy.context.active_object
    asignar_material(basa, get_mat("piedra_plaza"))
    
    # 2. Poste vertical de madera tallada
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=2.4, location=(0, 0, 1.2))
    poste = bpy.context.active_object
    asignar_material(poste, get_mat("arbol_corteza"))
    
    # Collarines de forja en el poste
    for z in [0.4, 1.3, 2.1]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.095, depth=0.06, location=(0, 0, z))
        collar = bpy.context.active_object
        asignar_material(collar, get_mat("metal_forja"))
    
    # 3. Brazo horizontal con tornapunta de refuerzo
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.045, depth=0.85, location=(0.35, 0, 2.25))
    brazo = bpy.context.active_object
    brazo.rotation_euler = (0, math.radians(90), 0)
    asignar_material(brazo, get_mat("arbol_corteza"))
    
    # Tornapunta diagonal
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=0.45, location=(0.18, 0, 2.05))
    tornapunta = bpy.context.active_object
    tornapunta.rotation_euler = (0, math.radians(45), 0)
    asignar_material(tornapunta, get_mat("madera_viga"))
    
    # 4. Argolla y cadena de suspensión
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.02, depth=0.15, location=(0.65, 0, 2.18))
    cadena = bpy.context.active_object
    asignar_material(cadena, get_mat("metal_forja"))
    
    # 5. Caperuza superior de la linterna (cono)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.22, radius2=0.02, depth=0.18, location=(0.65, 0, 2.08))
    caperuza = bpy.context.active_object
    asignar_material(caperuza, get_mat("metal_forja"))
    
    # 6. Jaula de vidrio / linterna con celosía
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.16, depth=0.28, location=(0.65, 0, 1.88))
    jaula = bpy.context.active_object
    asignar_material(jaula, get_mat("farol_luz"))
    
    # Base inferior de la linterna
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.16, radius2=0.04, depth=0.12, location=(0.65, 0, 1.70))
    base_linterna = bpy.context.active_object
    base_linterna.rotation_euler = (math.radians(180), 0, 0)
    asignar_material(base_linterna, get_mat("metal_forja"))

    exportar_modelo("farol_madera", DIR_ENTORNO)

def generar_cocina_juncia():
    """Genera la Cocina Comunitaria de Juncia (Cuna de Musgo) completa en 360°:
    Cabaña de troncos macizos con textura pixel art, tejado cónico de tablillas y musgo en 360°,
    gran hogar exterior de mampostería con trípode de hierro y caldero hirviente,
    chimenea de piedra con tiro abierto, mesa de preparación con cuencos, y ventana trasera de despensa."""
    limpiar_escena()
    
    tex_piedra = os.path.join(DIR_ALDEA, "forja_mamposteria_tile.png")
    tex_techo = os.path.join(DIR_ALDEA, "forja_tejado_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_piedra = obtener_material_textura("Mat_Cocina_Piedra", tex_piedra, rugosidad=0.88)
    mat_techo = obtener_material_textura("Mat_Cocina_Techo", tex_techo, rugosidad=0.80)
    mat_madera = obtener_material_textura("Mat_Cocina_Madera", tex_troncos, rugosidad=0.82)
    
    # 1. Base y muros de troncos en 360°
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.1))
    cuerpo = bpy.context.active_object
    cuerpo.scale = (2.6, 2.2, 1.8)
    asignar_material(cuerpo, mat_madera)
    aplicar_uv_caja(cuerpo, 2.0, 1.5)
    
    # Vigas de arriostramiento perimetral
    for z in [0.25, 1.1, 1.95]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z))
        viga = bpy.context.active_object
        viga.scale = (2.7, 2.3, 0.12)
        asignar_material(viga, mat_madera)
        aplicar_uv_caja(viga, 1.5, 0.5)
        
    # 2. Tejado cónico de barda y musgo sólido en 360°
    bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=2.25, radius2=0.25, depth=1.5, location=(0, 0, 2.75))
    techo = bpy.context.active_object
    asignar_material(techo, mat_techo)
    aplicar_uv_cilindro(techo, 3.0, 1.5)
    
    # 3. Chimenea de mampostería de piedra
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.34, depth=2.1, location=(0.95, 0.6, 2.85))
    chim = bpy.context.active_object
    asignar_material(chim, mat_piedra)
    aplicar_uv_cilindro(chim, 1.5, 1.5)
    
    # Remate de chimenea
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.42, depth=0.18, location=(0.95, 0.6, 3.92))
    rem_chim = bpy.context.active_object
    asignar_material(rem_chim, mat_piedra)
    
    # 4. Hogar exterior de piedra con caldero y fuego
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.70, depth=0.38, location=(-0.7, -1.35, 0.2))
    hogar = bpy.context.active_object
    asignar_material(hogar, mat_piedra)
    aplicar_uv_cilindro(hogar, 1.5, 1.0)
    
    # Fuego / brasas ardientes
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.30, location=(-0.7, -1.35, 0.32))
    fuego = bpy.context.active_object
    asignar_material(fuego, get_mat("corazon_asili"))
    
    # Trípode de hierro de forja
    for a in [0, 120, 240]:
        ang = math.radians(a)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.35, location=(-0.7 + math.cos(ang) * 0.45, -1.35 + math.sin(ang) * 0.45, 0.65))
        pata = bpy.context.active_object
        pata.rotation_euler = (math.sin(ang) * math.radians(20), -math.cos(ang) * math.radians(20), 0)
        asignar_material(pata, get_mat("metal_forja"))
    
    # Gran caldero de hierro colgado
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=8, radius=0.44, location=(-0.7, -1.35, 0.72))
    caldero = bpy.context.active_object
    caldero.scale = (1.0, 1.0, 0.85)
    asignar_material(caldero, get_mat("metal_forja"))
    
    # Guiso caliente interior
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.38, depth=0.08, location=(-0.7, -1.35, 0.88))
    guiso = bpy.context.active_object
    asignar_material(guiso, get_mat("oro_reliquia"))
    
    # 5. Mesa de preparación lateral con cuenco
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.7, -1.3, 0.55))
    mesa = bpy.context.active_object
    mesa.scale = (1.05, 0.7, 0.7)
    asignar_material(mesa, mat_madera)
    aplicar_uv_caja(mesa, 1.0, 1.0)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.18, depth=0.12, location=(0.7, -1.3, 0.95))
    cuenco = bpy.context.active_object
    asignar_material(cuenco, get_mat("teja_cobriza"))
    
    # 6. Ventana trasera de despensa (visibilidad sólida 360°)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.12, 1.25))
    marco_v = bpy.context.active_object
    marco_v.scale = (0.7, 0.1, 0.7)
    asignar_material(marco_v, get_mat("madera_viga"))
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.13, 1.25))
    vidrio = bpy.context.active_object
    vidrio.scale = (0.55, 0.1, 0.55)
    asignar_material(vidrio, get_mat("farol_luz"))

    exportar_modelo("cocina_juncia", DIR_ENTORNO)

def generar_puesto_tawi():
    """Genera el puesto de mercado de Tawi (Cuna de Musgo) completo en 360°:
    Mostrador de madera de pino con textura pixel art y estante inferior,
    cuatro postes esquineros de madera estriada, armazón superior con toldo a rayas verdes y crema,
    cajas de mercancías con reliquias doradas y frutas en el frontal, y cajas de embalaje en la trasera."""
    limpiar_escena()
    
    tex_toldo = os.path.join(DIR_ALDEA, "toldo_rayas_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_toldo = obtener_material_textura("Mat_Puesto_Toldo", tex_toldo, rugosidad=0.75)
    mat_madera = obtener_material_textura("Mat_Puesto_Madera", tex_troncos, rugosidad=0.82)
    
    # 1. Mostrador con repisa
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.55))
    mostrador = bpy.context.active_object
    mostrador.scale = (2.2, 0.9, 0.75)
    asignar_material(mostrador, mat_madera)
    aplicar_uv_caja(mostrador, 1.8, 1.0)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.95))
    tabla = bpy.context.active_object
    tabla.scale = (2.35, 1.05, 0.1)
    asignar_material(tabla, mat_madera)
    aplicar_uv_caja(tabla, 2.0, 1.0)
    
    # 2. Cuatro postes esquineros
    for sx in [-1.02, 1.02]:
        for sy in [-0.42, 0.42]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.055, depth=2.2, location=(sx, sy, 1.1))
            poste = bpy.context.active_object
            asignar_material(poste, mat_madera)
            aplicar_uv_cilindro(poste, 1.0, 2.0)
            
    # 3. Toldo de tela arqueado a dos aguas sólido en 360°
    crear_prisma_tejado("Puesto_Toldo", -1.32, 1.32, -0.68, 0.68, 1.95, 2.48, mat_toldo, u_rep=2.0, v_rep=1.5)
    
    # Faldón perimetral decorativo del toldo
    for sy in [-0.55, 0.55]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sy, 2.05))
        faldon = bpy.context.active_object
        faldon.scale = (2.55, 0.05, 0.22)
        asignar_material(faldon, mat_toldo)
        aplicar_uv_caja(faldon, 2.0, 0.5)
        
    # 4. Mercancías en la mesa: cajas y canastos con reliquias
    bpy.ops.mesh.primitive_cube_add(size=0.38, location=(-0.65, -0.05, 1.15))
    caja1 = bpy.context.active_object
    asignar_material(caja1, mat_madera)
    aplicar_uv_caja(caja1, 1.0, 1.0)
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.14, location=(-0.65, -0.05, 1.38))
    reliquia = bpy.context.active_object
    asignar_material(reliquia, get_mat("oro_reliquia"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.22, depth=0.18, location=(0.6, -0.05, 1.08))
    cesta = bpy.context.active_object
    asignar_material(cesta, get_mat("paja_dorada"))
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.16, location=(0.6, -0.05, 1.22))
    bayas = bpy.context.active_object
    asignar_material(bayas, get_mat("rubor"))
    
    # 5. Trasera del puesto: cajas de provisiones apiladas (volumen 360°)
    bpy.ops.mesh.primitive_cube_add(size=0.45, location=(-0.4, 0.72, 0.25))
    caja_tras1 = bpy.context.active_object
    asignar_material(caja_tras1, mat_madera)
    aplicar_uv_caja(caja_tras1, 1.0, 1.0)
    
    bpy.ops.mesh.primitive_cube_add(size=0.35, location=(0.4, 0.68, 0.2))
    caja_tras2 = bpy.context.active_object
    asignar_material(caja_tras2, mat_madera)
    aplicar_uv_caja(caja_tras2, 1.0, 1.0)

    exportar_modelo("puesto_tawi", DIR_ENTORNO)

def generar_gran_archivo_sigilia():
    """Genera el Gran Archivo de Maandiko (Sigilia) monumental en 360°:
    Podio escalonado de mármol clásico con textura pixel art, pórtico hexástilo con 4 columnas frontales acanaladas,
    frontón triangular con tímpano esculpido, puertas monumentales de bronce rúnico,
    cuerpo cerrado con pilastras y hornacinas en laterales y fachada trasera,
    tambor octogonal y gran cúpula dorada coronada por lucernario."""
    limpiar_escena()
    
    tex_marmol = os.path.join(DIR_SIGILIA, "marmol_sigilia_tile.png")
    tex_bronce = os.path.join(DIR_SIGILIA, "bronce_sigilia_tile.png")
    mat_marmol = obtener_material_textura("Mat_Archivo_Marmol", tex_marmol, rugosidad=0.65)
    mat_bronce = obtener_material_textura("Mat_Archivo_Bronce", tex_bronce, rugosidad=0.45, metalicidad=0.85)
    
    # 1. Podio de mármol escalonado en 360°
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.1, 0.2))
    escalon1 = bpy.context.active_object
    escalon1.scale = (5.6, 4.4, 0.4)
    asignar_material(escalon1, mat_marmol)
    aplicar_uv_caja(escalon1, 2.5, 2.0)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.2, 0.5))
    escalon2 = bpy.context.active_object
    escalon2.scale = (5.2, 4.0, 0.3)
    asignar_material(escalon2, mat_marmol)
    aplicar_uv_caja(escalon2, 2.5, 2.0)
    
    # 2. Cuerpo del edificio cerrado en 360°
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.4, 2.0))
    edificio = bpy.context.active_object
    edificio.scale = (4.6, 3.4, 2.7)
    asignar_material(edificio, mat_marmol)
    aplicar_uv_caja(edificio, 2.0, 1.5)
    
    # Cornisa perimetral superior moldurada en 360°
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.4, 3.45))
    cornisa = bpy.context.active_object
    cornisa.scale = (4.9, 3.7, 0.22)
    asignar_material(cornisa, mat_marmol)
    aplicar_uv_caja(cornisa, 2.0, 0.5)
    
    # 3. Cuatro columnas frontales acanaladas
    for i in range(4):
        x_col = (i - 1.5) * 1.25
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.20, depth=2.7, location=(x_col, -1.35, 1.95))
        col = bpy.context.active_object
        asignar_material(col, mat_marmol)
        aplicar_uv_cilindro(col, 1.0, 2.5)
        
        # Basa y capitel dorados
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.26, depth=0.15, location=(x_col, -1.35, 0.7))
        basa = bpy.context.active_object
        asignar_material(basa, get_mat("oro_reliquia"))
        
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_col, -1.35, 3.25))
        capitel = bpy.context.active_object
        capitel.scale = (0.5, 0.5, 0.15)
        asignar_material(capitel, get_mat("oro_reliquia"))
        
    # Frontón triangular monumental en 360°
    crear_prisma_tejado("Archivo_Fronton", -2.6, 2.6, -1.75, -0.95, 3.45, 4.45, mat_marmol, u_rep=2.0, v_rep=1.5)
    
    # 4. Puertas monumentales de bronce rúnico
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.32, 1.6))
    puerta = bpy.context.active_object
    puerta.scale = (1.2, 0.1, 1.8)
    asignar_material(puerta, mat_bronce)
    aplicar_uv_caja(puerta, 1.0, 1.5)
    
    # 5. Cúpula dorada con tambor octogonal
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.65, depth=0.8, location=(0, 0.4, 3.8))
    tambor = bpy.context.active_object
    asignar_material(tambor, mat_marmol)
    aplicar_uv_cilindro(tambor, 2.0, 1.0)
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=1.55, location=(0, 0.4, 4.3))
    cupula = bpy.context.active_object
    cupula.scale = (1.0, 1.0, 0.75)
    asignar_material(cupula, get_mat("oro_reliquia"))
    
    # Aguja / lucernario
    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.22, radius2=0.04, depth=0.8, location=(0, 0.4, 5.7))
    aguja = bpy.context.active_object
    asignar_material(aguja, get_mat("oro_reliquia"))
    
    # 6. Fachada trasera: hornacinas y ventanales rúnicos (volumen 360°)
    for hx in [-1.3, 0.0, 1.3]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hx, 2.12, 2.1))
        hornacina = bpy.context.active_object
        hornacina.scale = (0.7, 0.1, 1.5)
        asignar_material(hornacina, get_mat("tinta_sigilia"))
        
        # Cartela rúnica dorada interior
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(hx, 2.14, 2.1))
        cartela = bpy.context.active_object
        cartela.scale = (0.35, 0.06, 0.8)
        asignar_material(cartela, get_mat("oro_reliquia"))

    exportar_modelo("gran_archivo", DIR_ENTORNO)

def generar_taller_taa():
    """Genera el taller de Taa (escriba de Maandiko) completo en 360°:
    Plataforma de sillería de piedra con textura pixel art, puerta adintelada y ventana de mostrador,
    planta alta en voladizo con entramado de madera oscura y paneles claros,
    tejado a dos aguas de teja cobriza con buhardilla,
    gran frasco de tinta de Sigilia colgando del cartel de forja frontal,
    y fachada trasera con chimenea de piedra y ventanales iluminados."""
    limpiar_escena()
    
    tex_piedra = os.path.join(DIR_ALDEA, "forja_mamposteria_tile.png")
    tex_teja = os.path.join(DIR_SIGILIA, "teja_cobriza_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_piedra = obtener_material_textura("Mat_Taller_Piedra", tex_piedra, rugosidad=0.88)
    mat_teja = obtener_material_textura("Mat_Taller_Teja", tex_teja, rugosidad=0.80)
    mat_madera = obtener_material_textura("Mat_Taller_Madera", tex_troncos, rugosidad=0.82)
    
    # 1. Planta baja de piedra en 360°
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.1))
    planta_baja = bpy.context.active_object
    planta_baja.scale = (2.8, 2.4, 2.0)
    asignar_material(planta_baja, mat_piedra)
    aplicar_uv_caja(planta_baja, 1.8, 1.5)
    
    # 2. Planta alta en voladizo con entramado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.15, 2.75))
    planta_alta = bpy.context.active_object
    planta_alta.scale = (3.0, 2.7, 1.5)
    asignar_material(planta_alta, get_mat("marmol_sigilia"))
    aplicar_uv_caja(planta_alta, 1.5, 1.0)
    
    # Vigas esquineras verticales del entramado
    for px in [-1.48, 1.48]:
        for py in [-1.48, 1.18]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, py, 2.75))
            viga_v = bpy.context.active_object
            viga_v.scale = (0.12, 0.12, 1.5)
            asignar_material(viga_v, mat_madera)
            
    # 3. Tejado a dos aguas de teja cobriza sólido en 360°
    crear_prisma_tejado("Taller_Techo", -1.82, 1.82, -1.62, 1.28, 3.4, 4.6, mat_teja, u_rep=2.0, v_rep=1.5)
    
    # Buhardilla frontal
    crear_prisma_tejado("Taller_Buhardilla", -0.52, 0.52, -1.78, -1.12, 3.8, 4.4, mat_teja, u_rep=1.0, v_rep=1.0)
    
    # 4. Cartel de forja con frasco de tinta
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.9, location=(1.35, -1.4, 2.3))
    brazo_c = bpy.context.active_object
    brazo_c.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(brazo_c, get_mat("metal_forja"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.28, depth=0.55, location=(1.35, -1.75, 1.95))
    frasco = bpy.context.active_object
    asignar_material(frasco, get_mat("tinta_sigilia"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.12, depth=0.22, location=(1.35, -1.75, 2.3))
    cuello = bpy.context.active_object
    asignar_material(cuello, get_mat("oro_reliquia"))
    
    # 5. Fachada trasera: chimenea de piedra y ventana iluminada (360°)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.32, depth=4.2, location=(-0.9, 1.25, 2.2))
    chim = bpy.context.active_object
    asignar_material(chim, mat_piedra)
    aplicar_uv_cilindro(chim, 1.5, 3.0)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.5, 1.22, 2.8))
    ventana_tras = bpy.context.active_object
    ventana_tras.scale = (0.7, 0.1, 0.7)
    asignar_material(ventana_tras, get_mat("farol_luz"))

    exportar_modelo("taller_taa", DIR_ENTORNO)

def generar_casa_escriba():
    """Genera la Casa del Escriba de Sigilia (Maandiko) completa en 360°:
    Muros enlucidos de mármol blanco con sillares de esquina de granito en las 4 aristas,
    tejado a dos aguas de teja cobriza con aleros moldurados,
    balcón voladizo de madera tallada con balaustrada en la fachada principal,
    portón de entrada adintelado, y chimenea con ventanas iluminadas en la trasera."""
    limpiar_escena()
    
    tex_marmol = os.path.join(DIR_SIGILIA, "marmol_sigilia_tile.png")
    tex_teja = os.path.join(DIR_SIGILIA, "teja_cobriza_tile.png")
    tex_piedra = os.path.join(DIR_ALDEA, "forja_mamposteria_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_marmol = obtener_material_textura("Mat_Escriba_Marmol", tex_marmol, rugosidad=0.70)
    mat_teja = obtener_material_textura("Mat_Escriba_Teja", tex_teja, rugosidad=0.80)
    mat_piedra = obtener_material_textura("Mat_Escriba_Piedra", tex_piedra, rugosidad=0.88)
    mat_madera = obtener_material_textura("Mat_Escriba_Madera", tex_troncos, rugosidad=0.82)
    
    # 1. Cuerpo principal de dos plantas en 360°
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.5))
    cuerpo = bpy.context.active_object
    cuerpo.scale = (2.6, 2.2, 2.8)
    asignar_material(cuerpo, mat_marmol)
    aplicar_uv_caja(cuerpo, 1.8, 1.8)
    
    # Sillares de esquina en las 4 aristas (360°)
    for ex in [-1.31, 1.31]:
        for ey in [-1.11, 1.11]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, ey, 1.5))
            esquina = bpy.context.active_object
            esquina.scale = (0.16, 0.16, 2.82)
            asignar_material(esquina, mat_piedra)
            aplicar_uv_caja(esquina, 0.5, 2.0)
            
    # 2. Tejado a dos aguas de teja cobriza sólido en 360°
    crear_prisma_tejado("Escriba_Techo", -1.58, 1.58, -1.38, 1.38, 2.9, 4.15, mat_teja, u_rep=2.0, v_rep=1.5)
    
    # 3. Balcón frontal de madera tallada
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.25, 1.9))
    balcon_base = bpy.context.active_object
    balcon_base.scale = (1.75, 0.48, 0.1)
    asignar_material(balcon_base, mat_madera)
    aplicar_uv_caja(balcon_base, 1.5, 0.5)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.46, 2.15))
    baranda = bpy.context.active_object
    baranda.scale = (1.75, 0.06, 0.45)
    asignar_material(baranda, mat_madera)
    
    for bx in [-0.85, 0.85]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, -1.25, 2.15))
        lateral = bpy.context.active_object
        lateral.scale = (0.06, 0.48, 0.45)
        asignar_material(lateral, mat_madera)
        
    # Ventanal del balcón iluminado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.11, 2.25))
    vent_balcon = bpy.context.active_object
    vent_balcon.scale = (0.9, 0.1, 0.8)
    asignar_material(vent_balcon, get_mat("farol_luz"))
    
    # Puerta baja
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.11, 0.75))
    puerta = bpy.context.active_object
    puerta.scale = (0.7, 0.1, 1.1)
    asignar_material(puerta, mat_madera)
    
    # 4. Fachada trasera: chimenea de piedra y ventana iluminada (360°)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.28, depth=3.8, location=(0.75, 1.12, 2.0))
    chim = bpy.context.active_object
    asignar_material(chim, mat_piedra)
    aplicar_uv_cilindro(chim, 1.2, 2.5)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.5, 1.11, 1.8))
    vent_tras = bpy.context.active_object
    vent_tras.scale = (0.65, 0.1, 0.65)
    asignar_material(vent_tras, get_mat("farol_luz"))

    exportar_modelo("casa_escriba", DIR_ENTORNO)

def generar_casa_granja_shamba():
    """Genera la Casona de troncos de Mzee Shamba completa en 360° (El Kitovu):
    Dimensiones a escala exacta del pixel art y colisión 2D (8.8m ancho, 2.4m fondo, 5.2m alto).
    Zócalo de mampostería de piedra perimetral, paredes de troncos macizos cerradas por los 4 costados,
    fachada frontal y trasera UV-mapeadas a texturas pixel-art oficiales con filtro nearest,
    gran tejado a dos aguas de paja dorada con aleros voladizos en 360°, buhardilla superior encendida,
    porche frontal con 4 postes, techillo y farol cálido, chimenea lateral de mampostería y molino de agua hidráulico."""
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
    mat_madera_viga = obtener_material("Mat_Madera_Viga", "#78350F", roughness=0.8)
    mat_farol = obtener_material("Mat_Farol", "#FDE047", roughness=0.2, emission_hex="#FEF08A", emission_strength=4.0)
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
    crear_pared_uv("Granja_Pared_Frontal", cx - w * 0.5, cx + w * 0.5, -0.02, 0.0, 3.0, mat_frontal, 
                   u_range=(0.163, 0.924), v_range=(0.057, 0.464), invertir=False)
    
    # 4. Fachada Trasera de la pared (desde el suelo z=0 hasta el inicio del alero z=3.0)
    crear_pared_uv("Granja_Pared_Trasera", cx - w * 0.5, cx + w * 0.5, depth + 0.02, 0.0, 3.0, mat_trasera,
                   u_range=(0.163, 0.924), v_range=(0.057, 0.464), invertir=True)

    # 5. Gran Tejado a dos aguas sólido en 360° con cumbrera central
    crear_prisma_tejado("Granja_Techo", cx - w * 0.5 - 0.35, cx + w * 0.5 + 0.35, -0.35, depth + 0.35, 2.95, 5.2, mat_tejado, u_rep=3.5, v_rep=2.2)

    # Buhardilla superior 3D con techillo y ventana redonda
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, depth * 0.28, 4.1))
    buhardilla = bpy.context.active_object
    buhardilla.name = "Granja_Buhardilla"
    buhardilla.scale = (1.5, 0.9, 1.1)
    asignar_material(buhardilla, mat_troncos)
    
    crear_prisma_tejado("Granja_Buhardilla_Techo", cx - 0.85, cx + 0.85, -0.25, depth * 0.45, 4.5, 5.15, mat_tejado, u_rep=1.0, v_rep=1.0)
    
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

    exportar_modelo("casa_granja", DIR_ENTORNO)

def generar_pozo_antiguo():
    """Genera el Pozo Antiguo de El Kitovu:
    Brocal de mampostería circular de piedra texturizada, espejo de agua interior reflectante,
    dos postes laterales de madera, eje con manivela/cuerda, cubo y tejadillo a dos aguas de paja dorada."""
    limpiar_escena()
    
    tex_piedra = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    tex_tejado = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    mat_piedra = obtener_material_textura("Mat_Pozo_Piedra", tex_piedra, rugosidad=0.88)
    mat_tejado = obtener_material_textura("Mat_Pozo_Tejado", tex_tejado, rugosidad=0.92)
    
    # 1. Brocal de piedra
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.8, depth=0.75, location=(0, 0, 0.38))
    brocal = bpy.context.active_object
    asignar_material(brocal, mat_piedra)
    
    # 2. Agua reflectante interior
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.64, depth=0.1, location=(0, 0, 0.25))
    agua = bpy.context.active_object
    asignar_material(agua, get_mat("agua_limpia"))
    
    # 3. Postes de soporte lateral de madera
    for px in [-0.7, 0.7]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.065, depth=1.6, location=(px, 0, 1.1))
        poste = bpy.context.active_object
        asignar_material(poste, get_mat("arbol_corteza"))
        
    # 4. Eje giratorio con cuerda
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07, depth=1.35, location=(0, 0, 1.45))
    eje = bpy.context.active_object
    eje.rotation_euler = (0, math.radians(90), 0)
    asignar_material(eje, get_mat("madera_tablas"))
    
    # Cuerda enrollada
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.11, depth=0.35, location=(0, 0, 1.45))
    cuerda = bpy.context.active_object
    cuerda.rotation_euler = (0, math.radians(90), 0)
    asignar_material(cuerda, get_mat("paja_dorada"))
    
    # Cubo de madera colgando
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.15, depth=0.25, location=(0.15, 0, 0.95))
    cubo = bpy.context.active_object
    asignar_material(cubo, get_mat("madera_tronco"))
    
    # 5. Tejadillo a dos aguas sólido en 360°
    crear_prisma_tejado("Pozo_Techo", -0.85, 0.85, -0.65, 0.65, 1.7, 2.25, mat_tejado, u_rep=1.5, v_rep=1.2)
    
    exportar_modelo("pozo_antiguo", DIR_ENTORNO)

def generar_espantapajaros():
    """Genera el Espantapájaros de la huerta de Mzee Shamba (El Kitovu):
    Poste vertical, travesaño de brazos de roble, cabeza de paja dorada con sombrero cónico de paja texturizado,
    poncho de tela campesina y harapos en 360°."""
    limpiar_escena()
    
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    mat_troncos = obtener_material_textura("Mat_Espantapajaros_Madera", tex_troncos, rugosidad=0.85)
    mat_paja = obtener_material_textura("Mat_Espantapajaros_Paja", tex_paja, rugosidad=0.90)
    
    # 1. Poste vertical
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=2.0, location=(0, 0, 1.0))
    poste = bpy.context.active_object
    asignar_material(poste, mat_troncos)
    aplicar_uv_cilindro(poste, 1.0, 2.0)
    
    # 2. Travesaño de brazos
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.045, depth=1.45, location=(0, 0, 1.4))
    brazos = bpy.context.active_object
    brazos.rotation_euler = (0, math.radians(90), 0)
    asignar_material(brazos, mat_troncos)
    aplicar_uv_cilindro(brazos, 1.0, 1.5)
    
    # Paja saliendo por los extremos de las mangas
    for bx in [-0.75, 0.75]:
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.07, radius2=0.01, depth=0.18, location=(bx, 0, 1.4))
        paja_manga = bpy.context.active_object
        paja_manga.rotation_euler = (0, math.radians(-90 if bx < 0 else 90), 0)
        asignar_material(paja_manga, mat_paja)
    
    # 3. Poncho rústico de tela
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.25))
    poncho = bpy.context.active_object
    poncho.scale = (0.58, 0.34, 0.68)
    asignar_material(poncho, get_mat("castor_peto"))
    aplicar_uv_caja(poncho, 1.2, 1.2)
    
    # Pañuelo rojo al cuello
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.16, depth=0.08, location=(0, 0, 1.58))
    panuelo = bpy.context.active_object
    asignar_material(panuelo, get_mat("rubor"))
    
    # 4. Cabeza de paja texturizada
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.20, location=(0, 0, 1.72))
    cabeza = bpy.context.active_object
    asignar_material(cabeza, mat_paja)
    aplicar_uv_cilindro(cabeza, 1.5, 1.5)
    
    # 5. Sombrero cónico de paja trenzada con cinta
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.48, radius2=0.04, depth=0.32, location=(0, 0, 1.92))
    sombrero = bpy.context.active_object
    sombrero.rotation_euler = (math.radians(7), math.radians(-5), 0)
    asignar_material(sombrero, mat_paja)
    aplicar_uv_cilindro(sombrero, 2.0, 1.0)
    
    # Cinta del sombrero
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.28, depth=0.06, location=(0, 0, 1.84))
    cinta = bpy.context.active_object
    cinta.rotation_euler = (math.radians(7), math.radians(-5), 0)
    asignar_material(cinta, get_mat("arbol_corteza"))
    
    exportar_modelo("espantapajaros", DIR_ENTORNO)

def generar_carro_madera():
    """Genera el carro de madera rústico de labranza (El Kitovu):
    Camas de tablas con textura de madera pixel art, laterales de barrotes, varales de tiro, eje con ruedas de radios y carga de heno texturizado."""
    limpiar_escena()
    
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    mat_troncos = obtener_material_textura("Mat_Carro_Madera", tex_troncos, rugosidad=0.85)
    mat_heno = obtener_material_textura("Mat_Carro_Heno", tex_paja, rugosidad=0.90)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.55))
    plataforma = bpy.context.active_object
    plataforma.scale = (1.7, 1.05, 0.12)
    asignar_material(plataforma, mat_troncos)
    aplicar_uv_caja(plataforma, 1.5, 1.0)
    
    for side_y in [-0.52, 0.52]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, side_y, 0.8))
        barandilla = bpy.context.active_object
        barandilla.scale = (1.7, 0.06, 0.42)
        asignar_material(barandilla, mat_troncos)
        aplicar_uv_caja(barandilla, 1.5, 0.5)
        
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.82, 0, 0.8))
    trasera = bpy.context.active_object
    trasera.scale = (0.06, 1.05, 0.42)
    asignar_material(trasera, mat_troncos)
    aplicar_uv_caja(trasera, 0.5, 1.0)
    
    for vy in [-0.35, 0.35]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=1.4, location=(-1.3, vy, 0.4))
        varal = bpy.context.active_object
        varal.rotation_euler = (0, math.radians(75), 0)
        asignar_material(varal, get_mat("arbol_corteza"))
        
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.045, depth=1.35, location=(0, 0, 0.42))
    eje = bpy.context.active_object
    eje.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(eje, get_mat("metal_forja"))
    
    for wy in [-0.68, 0.68]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.45, depth=0.08, location=(0, wy, 0.42))
        rueda = bpy.context.active_object
        rueda.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(rueda, get_mat("madera_viga"))
        
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.1, 0, 0.78))
    heno = bpy.context.active_object
    heno.scale = (1.2, 0.8, 0.45)
    asignar_material(heno, mat_heno)
    aplicar_uv_caja(heno, 1.2, 0.8)
    
    exportar_modelo("carro_madera", DIR_ENTORNO)

def generar_valla_madera():
    """Genera un tramo de valla de estacas de madera en 3D sólida:
    Dos postes verticales con puntas facetadas y dos travesaños horizontales con textura pixel art y clavijas de forja, visible con volumen en 360°."""
    limpiar_escena()
    
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_troncos = obtener_material_textura("Mat_Valla_Madera", tex_troncos, rugosidad=0.85)
    
    for px in [-0.48, 0.48]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07, depth=0.95, location=(px, 0, 0.47))
        poste = bpy.context.active_object
        asignar_material(poste, mat_troncos)
        aplicar_uv_cilindro(poste, 1.0, 1.2)
        
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.07, radius2=0.01, depth=0.14, location=(px, 0, 0.98))
        punta = bpy.context.active_object
        asignar_material(punta, mat_troncos)
        aplicar_uv_cilindro(punta, 1.0, 0.5)
        
    for pz in [0.32, 0.68]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, pz))
        travesano = bpy.context.active_object
        travesano.scale = (1.14, 0.055, 0.09)
        asignar_material(travesano, mat_troncos)
        aplicar_uv_caja(travesano, 1.5, 0.5)
        
        # Clavijas de forja que unen travesaño con los postes
        for px in [-0.48, 0.48]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.018, depth=0.12, location=(px, 0, pz))
            clavija = bpy.context.active_object
            clavija.rotation_euler = (math.radians(90), 0, 0)
            asignar_material(clavija, get_mat("metal_forja"))
        
    exportar_modelo("valla_madera", DIR_ENTORNO)

def generar_casa_pino_ruina():
    """Genera la versión en ruinas de la Casa Seta de Pino (Cuna de Musgo):
    Muros circulares quebrados a diferentes alturas con textura de mampostería, vigas caídas y fracturadas,
    la cubierta de seta roja partida y colapsada sobre un costado, y escombros tridimensionales en 360°."""
    limpiar_escena()
    
    tex_ruina = os.path.join(DIR_ALDEA, "ruina_mamposteria_tile.png")
    tex_pared = os.path.join(DIR_ALDEA, "seta_pared_tile.png")
    tex_techo = os.path.join(DIR_ALDEA, "seta_tejado_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_ruina = obtener_material_textura("Mat_Ruina_Piedra", tex_ruina, rugosidad=0.90)
    mat_pared = obtener_material_textura("Mat_Ruina_Pared", tex_pared, rugosidad=0.85)
    mat_techo = obtener_material_textura("Mat_Ruina_Techo", tex_techo, rugosidad=0.75)
    mat_madera = obtener_material_textura("Mat_Ruina_Madera", tex_troncos, rugosidad=0.85)
    
    # 1. Zócalo base circular roto
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.45, depth=0.65, location=(0, 0, 0.32))
    muro_base = bpy.context.active_object
    asignar_material(muro_base, mat_ruina)
    aplicar_uv_cilindro(muro_base, 2.5, 1.0)
    
    # 2. Pared cilíndrica quebrada en un cuadrante
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.65, depth=1.1, location=(-0.85, -0.35, 0.85))
    pared_rota = bpy.context.active_object
    asignar_material(pared_rota, mat_pared)
    aplicar_uv_cilindro(pared_rota, 1.5, 1.0)
    
    # 3. Cubierta de seta carmesí colapsada y partida
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=1.4, radius2=0.2, depth=0.7, location=(0.3, 0.1, 0.45))
    techo_caido = bpy.context.active_object
    techo_caido.rotation_euler = (math.radians(16), math.radians(-24), math.radians(10))
    asignar_material(techo_caido, mat_techo)
    aplicar_uv_cilindro(techo_caido, 2.0, 1.0)
    
    # 4. Vigas astilladas
    for vx, vy, vz, rx, ry in [(-0.4, 0.6, 0.9, 35, 15), (0.7, -0.5, 0.7, -25, 40), (0.0, -0.9, 0.5, 10, -50)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.065, depth=1.35, location=(vx, vy, vz))
        viga = bpy.context.active_object
        viga.rotation_euler = (math.radians(rx), math.radians(ry), 0)
        asignar_material(viga, mat_madera)
        aplicar_uv_cilindro(viga, 1.0, 1.5)
        
    # 5. Escombros tridimensionales de mampostería en 360°
    for ex, ey, s in [(-1.3, 0.8, 0.38), (1.2, -0.9, 0.42), (-0.9, -1.1, 0.32), (1.4, 0.7, 0.40), (0.1, 1.25, 0.30)]:
        bpy.ops.mesh.primitive_cube_add(size=s, location=(ex, ey, s * 0.5))
        escombro = bpy.context.active_object
        asignar_material(escombro, mat_ruina)
        aplicar_uv_caja(escombro, 1.0, 1.0)
        
    exportar_modelo("casa_pino_ruina", DIR_ENTORNO)

def generar_forja_ruina():
    """Genera la versión en ruinas de la Herrería de Corteza (Cuna de Musgo):
    Horno de piedra agrietado y medio derrumbado, chimenea toscamente fracturada,
    tocón y yunque caídos en el fango, y piedras de escombros en 360°."""
    limpiar_escena()
    
    tex_ruina = os.path.join(DIR_ALDEA, "ruina_mamposteria_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_ruina = obtener_material_textura("Mat_Forja_Ruina_Piedra", tex_ruina, rugosidad=0.90)
    mat_madera = obtener_material_textura("Mat_Forja_Ruina_Madera", tex_troncos, rugosidad=0.85)
    
    # Horno agrietado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.52))
    horno = bpy.context.active_object
    horno.scale = (2.0, 1.55, 1.05)
    asignar_material(horno, mat_ruina)
    aplicar_uv_caja(horno, 1.8, 1.2)
    
    # Chimenea fracturada inclinada
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.34, depth=0.85, location=(0.6, 0.3, 1.35))
    chimenea = bpy.context.active_object
    chimenea.rotation_euler = (math.radians(18), math.radians(12), 0)
    asignar_material(chimenea, mat_ruina)
    aplicar_uv_cilindro(chimenea, 1.2, 1.0)
    
    # Tocón volcado
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.34, depth=0.55, location=(-0.3, -1.2, 0.25))
    tocon = bpy.context.active_object
    tocon.rotation_euler = (math.radians(70), 0, math.radians(20))
    asignar_material(tocon, mat_madera)
    aplicar_uv_cilindro(tocon, 1.0, 1.0)
    
    # Yunque caído en el fango
    bpy.ops.mesh.primitive_cube_add(size=0.38, location=(0.3, -1.3, 0.2))
    yunque = bpy.context.active_object
    yunque.scale = (1.35, 0.75, 0.65)
    yunque.rotation_euler = (math.radians(35), math.radians(-15), 0)
    asignar_material(yunque, get_mat("metal_forja"))
    
    # Escombros de piedra en 360°
    for ex, ey, s in [(-1.1, 0.6, 0.38), (1.0, -0.6, 0.32), (-0.8, -0.7, 0.30), (0.45, 0.95, 0.42), (-0.2, 1.1, 0.28)]:
        bpy.ops.mesh.primitive_cube_add(size=s, location=(ex, ey, s * 0.5))
        escombro = bpy.context.active_object
        asignar_material(escombro, mat_ruina)
        aplicar_uv_caja(escombro, 1.0, 1.0)
        
    exportar_modelo("forja_ruina", DIR_ENTORNO)

def generar_cocina_ruina():
    """Genera la cocina comunitaria de Juncia en ruinas (Cuna de Musgo):
    Muros de madera rotos y desmoronados, chimenea fracturada en ángulo,
    cono de cubierta desplomado y gran caldero volcado en 360°."""
    limpiar_escena()
    
    tex_ruina = os.path.join(DIR_ALDEA, "ruina_mamposteria_tile.png")
    tex_techo = os.path.join(DIR_ALDEA, "forja_tejado_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_ruina = obtener_material_textura("Mat_Cocina_Ruina_Piedra", tex_ruina, rugosidad=0.90)
    mat_techo = obtener_material_textura("Mat_Cocina_Ruina_Techo", tex_techo, rugosidad=0.82)
    mat_madera = obtener_material_textura("Mat_Cocina_Ruina_Madera", tex_troncos, rugosidad=0.85)
    
    # Muros quebrados
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.38))
    cuerpo = bpy.context.active_object
    cuerpo.scale = (2.3, 1.9, 0.75)
    asignar_material(cuerpo, mat_madera)
    aplicar_uv_caja(cuerpo, 1.8, 1.0)
    
    # Chimenea fracturada
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.30, depth=0.95, location=(0.7, 0.3, 0.9))
    chim = bpy.context.active_object
    chim.rotation_euler = (math.radians(22), math.radians(-16), 0)
    asignar_material(chim, mat_ruina)
    aplicar_uv_cilindro(chim, 1.2, 1.0)
    
    # Cono de tejado desplomado
    bpy.ops.mesh.primitive_cone_add(vertices=14, radius1=1.45, radius2=0.1, depth=0.85, location=(-0.35, 0.2, 0.58))
    techo = bpy.context.active_object
    techo.rotation_euler = (math.radians(20), math.radians(28), 0)
    asignar_material(techo, mat_techo)
    aplicar_uv_cilindro(techo, 2.0, 1.0)
    
    # Caldero volcado derramando cenizas
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.46, location=(-0.5, -1.0, 0.32))
    caldero = bpy.context.active_object
    caldero.rotation_euler = (math.radians(65), 0, math.radians(-30))
    asignar_material(caldero, get_mat("metal_forja"))
    
    # Escombros en 360°
    for ex, ey, s in [(-0.95, 0.85, 0.38), (1.15, -0.65, 0.32), (0.2, -1.25, 0.28), (1.25, 0.95, 0.40)]:
        bpy.ops.mesh.primitive_cube_add(size=s, location=(ex, ey, s * 0.5))
        escombro = bpy.context.active_object
        asignar_material(escombro, mat_ruina)
        aplicar_uv_caja(escombro, 1.0, 1.0)
        
    exportar_modelo("cocina_ruina", DIR_ENTORNO)

def generar_puesto_ruina():
    """Genera el puesto de mercado de Tawi en ruinas (Cuna de Musgo):
    Mesa partida y vencida, postes de soporte caídos, armazón de toldo colapsado
    y cajas rotas con escombros en 360°."""
    limpiar_escena()
    
    tex_ruina = os.path.join(DIR_ALDEA, "ruina_mamposteria_tile.png")
    tex_toldo = os.path.join(DIR_ALDEA, "toldo_rayas_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_ruina = obtener_material_textura("Mat_Puesto_Ruina_Piedra", tex_ruina, rugosidad=0.90)
    mat_toldo = obtener_material_textura("Mat_Puesto_Ruina_Toldo", tex_toldo, rugosidad=0.80)
    mat_madera = obtener_material_textura("Mat_Puesto_Ruina_Madera", tex_troncos, rugosidad=0.85)
    
    # Mesa vencida en diagonal
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.36))
    mesa = bpy.context.active_object
    mesa.scale = (2.1, 0.95, 0.52)
    mesa.rotation_euler = (math.radians(9), math.radians(-14), math.radians(6))
    asignar_material(mesa, mat_madera)
    aplicar_uv_caja(mesa, 1.5, 1.0)
    
    # Postes quebrados
    for px, py, rx, ry in [(-0.9, -0.4, 65, 20), (0.9, 0.4, -45, -35)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.045, depth=1.65, location=(px, py, 0.4))
        poste = bpy.context.active_object
        poste.rotation_euler = (math.radians(rx), math.radians(ry), 0)
        asignar_material(poste, mat_madera)
        aplicar_uv_cilindro(poste, 1.0, 1.5)
        
    # Toldo colapsado arrugado
    bpy.ops.mesh.primitive_cylinder_add(vertices=4, radius=0.85, depth=1.65, location=(0.1, 0.1, 0.52))
    toldo = bpy.context.active_object
    toldo.rotation_euler = (math.radians(22), math.radians(75), math.radians(-12))
    toldo.scale = (0.75, 0.28, 0.92)
    asignar_material(toldo, mat_toldo)
    
    # Cajas quebradas y escombros en 360°
    for cx, cy in [(-0.65, -0.72), (0.75, -0.62)]:
        bpy.ops.mesh.primitive_cube_add(size=0.38, location=(cx, cy, 0.19))
        caja = bpy.context.active_object
        caja.rotation_euler = (0, 0, math.radians(25))
        asignar_material(caja, mat_madera)
        aplicar_uv_caja(caja, 1.0, 1.0)
        
    for ex, ey in [(-1.1, 0.5), (1.1, 0.5), (0.0, -1.0)]:
        bpy.ops.mesh.primitive_cube_add(size=0.28, location=(ex, ey, 0.14))
        escombro = bpy.context.active_object
        asignar_material(escombro, mat_ruina)
        aplicar_uv_caja(escombro, 1.0, 1.0)
        
    exportar_modelo("puesto_ruina", DIR_ENTORNO)

def generar_kitovu_ruina():
    """Genera las ruinas de piedra de El Kitovu en 360° (ruina_casa.png):
    Muros macizos de sillería de piedra quebrados en L con textura de mampostería pixel art,
    vigas de roble caídas y montones de escombros de mampostería tridimensional en 360°."""
    limpiar_escena()
    
    tex_mamposteria = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_piedra = obtener_material_textura("Mat_Kitovu_Ruina_Piedra", tex_mamposteria, rugosidad=0.88)
    mat_madera = obtener_material_textura("Mat_Kitovu_Ruina_Madera", tex_troncos, rugosidad=0.85)
    
    # 1. Zócalo base de piedra
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.2, 0.26))
    base = bpy.context.active_object
    base.scale = (3.3, 2.3, 0.52)
    asignar_material(base, mat_piedra)
    aplicar_uv_caja(base, 2.0, 1.5)
    
    # 2. Muro trasero (norte) roto a diferente altura
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.2, 1.02, 0.98))
    muro_n = bpy.context.active_object
    muro_n.scale = (2.7, 0.58, 1.15)
    asignar_material(muro_n, mat_piedra)
    aplicar_uv_caja(muro_n, 2.0, 1.0)
    
    # 3. Muro lateral (oeste) roto en rampa
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.12, 0.1, 0.88))
    muro_o = bpy.context.active_object
    muro_o.scale = (0.58, 1.65, 0.95)
    asignar_material(muro_o, mat_piedra)
    aplicar_uv_caja(muro_o, 1.0, 1.5)
    
    # Remate superior de esquina más alta
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.12, 1.02, 1.58))
    esquina = bpy.context.active_object
    esquina.scale = (0.62, 0.62, 0.72)
    asignar_material(esquina, mat_piedra)
    aplicar_uv_caja(esquina, 1.0, 1.0)
    
    # 4. Vigas de madera caídas
    for vx, vy, vz, rx, ry in [(-0.3, 0.2, 0.62, 30, -20), (0.6, -0.4, 0.38, -15, 60)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.085, depth=1.85, location=(vx, vy, vz))
        viga = bpy.context.active_object
        viga.rotation_euler = (math.radians(rx), math.radians(ry), 0)
        asignar_material(viga, mat_madera)
        aplicar_uv_cilindro(viga, 1.0, 2.0)
        
    # 5. Bloques de escombros de mampostería en 360°
    for ex, ey, s in [(-1.55, -0.6, 0.42), (1.35, -0.7, 0.46), (1.15, 1.25, 0.40), (-0.85, -1.05, 0.34), (0.32, -0.85, 0.36), (1.55, 0.42, 0.32)]:
        bpy.ops.mesh.primitive_cube_add(size=s, location=(ex, ey, s * 0.5))
        escombro = bpy.context.active_object
        asignar_material(escombro, mat_piedra)
        aplicar_uv_caja(escombro, 1.0, 1.0)

    exportar_modelo("kitovu_ruina", DIR_ENTORNO)

def generar_fuente_plaza():
    """Genera la Fuente Central de Maandiko (Sigilia) completa en 360°:
    Pila octogonal monumental de mármol blanco con textura pixel art y molduras escalonadas,
    lámina de agua cristalina reflectante en su interior,
    fuste central esculpido con acantos, taza superior de mármol rebosante,
    y surtidor de agua en forma de flor de loto dorada."""
    limpiar_escena()
    
    tex_marmol = os.path.join(DIR_SIGILIA, "marmol_sigilia_tile.png")
    mat_marmol = obtener_material_textura("Mat_Fuente_Marmol", tex_marmol, rugosidad=0.55)
    
    # 1. Pila octogonal exterior
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.92, depth=0.72, location=(0, 0, 0.36))
    pila = bpy.context.active_object
    asignar_material(pila, mat_marmol)
    aplicar_uv_cilindro(pila, 4.0, 1.0)
    
    # Moldura de borde superior
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=2.06, depth=0.16, location=(0, 0, 0.70))
    borde = bpy.context.active_object
    asignar_material(borde, mat_marmol)
    aplicar_uv_cilindro(borde, 4.0, 0.5)
    
    # 2. Agua reflectante interior
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.68, depth=0.1, location=(0, 0, 0.54))
    agua_base = bpy.context.active_object
    asignar_material(agua_base, get_mat("agua_limpia"))
    
    # 3. Fuste central esculpido
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.38, depth=1.45, location=(0, 0, 1.05))
    columna = bpy.context.active_object
    asignar_material(columna, mat_marmol)
    aplicar_uv_cilindro(columna, 1.5, 1.5)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.54, depth=0.22, location=(0, 0, 0.78))
    anillo = bpy.context.active_object
    asignar_material(anillo, get_mat("oro_reliquia"))
    
    # 4. Taza superior de mármol rebosante
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.98, depth=0.36, location=(0, 0, 1.75))
    taza = bpy.context.active_object
    asignar_material(taza, mat_marmol)
    aplicar_uv_cilindro(taza, 2.5, 0.8)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.85, depth=0.08, location=(0, 0, 1.88))
    agua_taza = bpy.context.active_object
    asignar_material(agua_taza, get_mat("agua_limpia"))
    
    # 5. Surtidor / flor de loto dorada central
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.26, radius2=0.05, depth=0.48, location=(0, 0, 2.12))
    surtidor = bpy.context.active_object
    asignar_material(surtidor, get_mat("oro_reliquia"))

    exportar_modelo("fuente_plaza", DIR_ENTORNO)

# ---------------------------------------------------------------------------
# GENERADORES DE TERRENO MODULAR
# ---------------------------------------------------------------------------

def generar_bloque_hierba():
    """Bloque cúbico de terreno (1x1x0.5m) con borde de musgo suave."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.25))
    bloque = bpy.context.active_object
    bloque.scale = (1.0, 1.0, 0.5)
    asignar_material(bloque, get_mat("musgo_hojas"))

    exportar_modelo("bloque_hierba", DIR_ENTORNO)

def generar_bloque_risco():
    """Bloque rocoso de desnivel (1x1x1m) de piedra de Raíz."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
    bloque = bpy.context.active_object
    asignar_material(bloque, get_mat("petrino_roca"))

    exportar_modelo("bloque_risco", DIR_ENTORNO)

def generar_canal_agua():
    """Bloque con acequia cóncava y superficie de agua reflectante."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.2))
    bloque = bpy.context.active_object
    bloque.scale = (1.0, 1.0, 0.4)
    asignar_material(bloque, get_mat("piedra_plaza"))
    
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, 0, 0.35))
    agua = bpy.context.active_object
    agua.scale = (1.0, 0.7, 1.0)
    asignar_material(agua, get_mat("agua_limpia"))

    exportar_modelo("bloque_canal_agua", DIR_ENTORNO)

def generar_bloque_camino():
    """Losa de camino empedrado para plaza de la aldea."""
    limpiar_escena()
    
    for i in [-0.25, 0.25]:
        for j in [-0.25, 0.25]:
            bpy.ops.mesh.primitive_cube_add(size=0.45, location=(i, j, 0.05))
            losa = bpy.context.active_object
            losa.scale = (0.95, 0.95, 0.15)
            asignar_material(losa, get_mat("piedra_plaza"))

    exportar_modelo("bloque_camino", DIR_ENTORNO)

# ---------------------------------------------------------------------------
# GENERADORES DE PROPS Y OBJETOS
# ---------------------------------------------------------------------------

def generar_semilla_explosiva():
    """Genera la semilla explosiva de vida que Maisha planta en el suelo."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.22, location=(0, 0, 0.22))
    semilla = bpy.context.active_object
    semilla.scale = (0.85, 0.85, 1.25)
    asignar_material(semilla, get_mat("brote_verde"))
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.08, location=(0, 0, 0.46))
    mecha = bpy.context.active_object
    asignar_material(mecha, get_mat("corazon_asili"))

    exportar_modelo("semilla_explosiva", DIR_OBJETOS)

def generar_cetro_raiz():
    """Genera el Cetro de Raíz de Asili como prop independiente."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=1.1, location=(0, 0, 0.55))
    vara = bpy.context.active_object
    asignar_material(vara, get_mat("cetro_madera"))
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.11, location=(0, 0, 1.15))
    gema = bpy.context.active_object
    asignar_material(gema, get_mat("cetro_gema"))

    exportar_modelo("cetro_raiz", DIR_OBJETOS)

def generar_casa_juncos():
    """Genera la Cabaña de Juncos sobre pilotes (Embarcadero Junco) completa en 360°:
    Pilotes de madera, plataforma de tablones, paredes de juncos y cañas, tejado a dos aguas de paja dorada."""
    limpiar_escena()
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    mat_troncos = obtener_material_textura("Mat_Juncos_Troncos", tex_troncos, rugosidad=0.85)
    mat_paja = obtener_material_textura("Mat_Juncos_Paja", tex_paja, rugosidad=0.92)
    mat_cana = get_mat("paja_dorada")
    mat_madera = get_mat("madera_viga")
    mat_luz = get_mat("farol_luz")

    w, depth = 3.6, 2.6
    for px in [-1.6, 0.0, 1.6]:
        for py in [-1.1, 1.1]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=1.6, location=(px, py, 0.4))
            poste = bpy.context.active_object
            asignar_material(poste, mat_madera)
            
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.15))
    suelo = bpy.context.active_object
    suelo.scale = (w + 0.4, depth + 0.6, 0.2)
    asignar_material(suelo, mat_troncos)
    aplicar_uv_caja(suelo, 1.5, 1.2)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.15, 2.2))
    paredes = bpy.context.active_object
    paredes.scale = (w, depth, 1.9)
    asignar_material(paredes, mat_cana)
    aplicar_uv_caja(paredes, 1.0, 1.0)
    
    for z in [1.3, 2.2, 3.1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.15, z))
        viga = bpy.context.active_object
        viga.scale = (w + 0.1, depth + 0.1, 0.1)
        asignar_material(viga, mat_madera)
        
    crear_prisma_tejado("Juncos_Techo", -w * 0.5 - 0.4, w * 0.5 + 0.4, -depth * 0.5 - 0.2, depth * 0.5 + 0.5, 3.0, 4.4, mat_paja, u_rep=2.5, v_rep=1.8)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.05, 1.35))
    puerta = bpy.context.active_object
    puerta.scale = (1.0, 0.1, 1.7)
    asignar_material(puerta, mat_madera)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.9, -1.35, 1.6))
    baranda = bpy.context.active_object
    baranda.scale = (1.4, 0.06, 0.45)
    asignar_material(baranda, mat_madera)
        
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.14, location=(-1.2, -1.1, 2.3))
    farol = bpy.context.active_object
    asignar_material(farol, mat_luz)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, depth * 0.5 + 0.18, 2.2))
    vent_tras = bpy.context.active_object
    vent_tras.scale = (0.8, 0.1, 0.8)
    asignar_material(vent_tras, mat_luz)
    
    exportar_modelo("casa_juncos", DIR_ENTORNO)

def generar_casa_bata():
    """Genera la Cabaña del barquero Bata (Embarcadero Junco) completa en 360°:
    Pilotes sobre el agua, paredes de tablas de madera vieja curtida, tejado de teja cobriza."""
    limpiar_escena()
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    tex_teja = os.path.join(DIR_SIGILIA, "teja_cobriza_tile.png")
    mat_troncos = obtener_material_textura("Mat_Bata_Troncos", tex_troncos, rugosidad=0.85)
    mat_teja = obtener_material_textura("Mat_Bata_Teja", tex_teja, rugosidad=0.80)
    mat_madera = get_mat("madera_viga")
    mat_luz = get_mat("farol_luz")

    w, depth = 3.2, 2.4
    for px in [-1.4, 1.4]:
        for py in [-1.0, 1.0]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.09, depth=1.5, location=(px, py, 0.4))
            p = bpy.context.active_object
            asignar_material(p, mat_madera)
            
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.15))
    suelo = bpy.context.active_object
    suelo.scale = (w + 0.4, depth + 0.5, 0.18)
    asignar_material(suelo, mat_troncos)
    aplicar_uv_caja(suelo, 1.4, 1.0)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.1, 2.15))
    pared = bpy.context.active_object
    pared.scale = (w, depth, 1.8)
    asignar_material(pared, mat_troncos)
    aplicar_uv_caja(pared, 1.2, 1.0)
    
    crear_prisma_tejado("Bata_Techo", -w * 0.5 - 0.35, w * 0.5 + 0.35, -depth * 0.5 - 0.25, depth * 0.5 + 0.45, 2.95, 4.2, mat_teja, u_rep=2.0, v_rep=1.5)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.5, -depth * 0.5 + 0.05, 1.85))
    puerta = bpy.context.active_object
    puerta.scale = (0.9, 0.1, 1.6)
    asignar_material(puerta, mat_madera)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.28, depth=0.7, location=(1.1, -0.9, 1.55))
    barril = bpy.context.active_object
    asignar_material(barril, mat_madera)
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.14, location=(-0.5, -1.2, 2.4))
    farol = bpy.context.active_object
    asignar_material(farol, mat_luz)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.3, depth * 0.5 + 0.14, 2.2))
    v_tras = bpy.context.active_object
    v_tras.scale = (0.8, 0.1, 0.7)
    asignar_material(v_tras, mat_luz)
    
    exportar_modelo("casa_bata", DIR_ENTORNO)

def generar_casa_nungu():
    """Genera el Refugio de Montaña de Nungu (Paso Piedra / Paso Escarcha) completo en 360°:
    Mampostería maciza de granito, tejado alpino de pizarra con vertientes empinadas y chimenea."""
    limpiar_escena()
    tex_piedra = os.path.join(DIR_ALDEA, "forja_mamposteria_tile.png")
    mat_piedra = obtener_material_textura("Mat_Nungu_Piedra", tex_piedra, rugosidad=0.90)
    mat_techo = get_mat("pizarra_nieve")
    mat_oscura = get_mat("piedra_oscura")
    mat_madera = get_mat("madera_viga")
    mat_luz = get_mat("farol_luz")

    w, depth = 4.2, 2.8
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.4))
    muro = bpy.context.active_object
    muro.scale = (w, depth, 2.6)
    asignar_material(muro, mat_piedra)
    aplicar_uv_caja(muro, 1.8, 1.4)
    
    for ex in [-w * 0.5 - 0.05, w * 0.5 + 0.05]:
        for ey in [-depth * 0.5 - 0.05, depth * 0.5 + 0.05]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, ey, 1.4))
            esq = bpy.context.active_object
            esq.scale = (0.35, 0.35, 2.65)
            asignar_material(esq, mat_oscura)
            
    crear_prisma_tejado("Nungu_Techo", -w * 0.5 - 0.45, w * 0.5 + 0.45, -depth * 0.5 - 0.4, depth * 0.5 + 0.4, 2.6, 4.6, mat_techo, u_rep=2.5, v_rep=2.0)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -depth * 0.5 - 0.05, 1.1))
    puerta = bpy.context.active_object
    puerta.scale = (1.2, 0.15, 1.9)
    asignar_material(puerta, mat_madera)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(w * 0.5 - 0.3, 0.2, 2.8))
    chim = bpy.context.active_object
    chim.scale = (0.9, 0.9, 4.8)
    asignar_material(chim, mat_piedra)
    aplicar_uv_caja(chim, 0.5, 2.0)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(w * 0.5 - 0.3, 0.2, 5.25))
    cap = bpy.context.active_object
    cap.scale = (1.1, 1.1, 0.2)
    asignar_material(cap, mat_oscura)
    
    for vy in [-depth * 0.5 - 0.05, depth * 0.5 + 0.05]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.2, vy, 1.6))
        vent = bpy.context.active_object
        vent.scale = (0.9, 0.12, 0.9)
        asignar_material(vent, mat_luz)
        
    exportar_modelo("casa_nungu", DIR_ENTORNO)

def generar_granero():
    """Genera el Granero de Campo Segado completo en 360°:
    Tablas rojas agrícolas, portón doble, tejado a dos aguas y vano de pajar con polea."""
    limpiar_escena()
    tex_piedra = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    tex_teja = os.path.join(DIR_SIGILIA, "teja_cobriza_tile.png")
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    mat_piedra = obtener_material_textura("Mat_Granero_Piedra", tex_piedra, rugosidad=0.90)
    mat_teja = obtener_material_textura("Mat_Granero_Teja", tex_teja, rugosidad=0.82)
    mat_paja = obtener_material_textura("Mat_Granero_Paja", tex_paja, rugosidad=0.92)
    mat_roja = get_mat("madera_roja")
    mat_viga = get_mat("marmol_sigilia")
    mat_madera = get_mat("madera_viga")
    mat_luz = get_mat("farol_luz")

    w, depth = 6.8, 3.6
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.3))
    zocalo = bpy.context.active_object
    zocalo.scale = (w, depth, 0.6)
    asignar_material(zocalo, mat_piedra)
    aplicar_uv_caja(zocalo, 3.0, 0.5)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.1))
    cuerpo = bpy.context.active_object
    cuerpo.scale = (w - 0.15, depth - 0.15, 3.0)
    asignar_material(cuerpo, mat_roja)
    aplicar_uv_caja(cuerpo, 2.5, 1.5)
    
    for z in [0.65, 2.1, 3.55]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, z))
        viga = bpy.context.active_object
        viga.scale = (w + 0.1, depth + 0.1, 0.12)
        asignar_material(viga, mat_viga)
        
    crear_prisma_tejado("Granero_Techo", -w * 0.5 - 0.4, w * 0.5 + 0.4, -depth * 0.5 - 0.35, depth * 0.5 + 0.35, 3.5, 5.8, mat_teja, u_rep=3.5, v_rep=2.2)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -depth * 0.5 - 0.05, 1.4))
    porton = bpy.context.active_object
    porton.scale = (2.4, 0.12, 2.2)
    asignar_material(porton, mat_madera)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -depth * 0.5 - 0.05, 4.0))
    vano = bpy.context.active_object
    vano.scale = (1.2, 0.12, 1.2)
    asignar_material(vano, mat_madera)
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=1.1, location=(0, -depth * 0.5 - 0.55, 4.7))
    brazo_p = bpy.context.active_object
    brazo_p.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(brazo_p, mat_madera)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -depth * 0.5 - 0.55, 4.1))
    heno = bpy.context.active_object
    heno.scale = (0.65, 0.5, 0.5)
    asignar_material(heno, mat_paja)
    aplicar_uv_caja(heno, 0.5, 0.5)
    
    for vx in [-1.8, 1.8]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(vx, depth * 0.5 + 0.05, 2.2))
        vent_t = bpy.context.active_object
        vent_t.scale = (1.1, 0.1, 0.9)
        asignar_material(vent_t, mat_luz)
        
    exportar_modelo("granero", DIR_ENTORNO)

def generar_palafito():
    """Genera el Palafito de Las Pasarelas completo en 360°:
    Altos pilotes sobre aguas profundas, choza de bambú, plataforma de tablas y tejado de paja."""
    limpiar_escena()
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    mat_troncos = obtener_material_textura("Mat_Palafito_Troncos", tex_troncos, rugosidad=0.85)
    mat_paja = obtener_material_textura("Mat_Palafito_Paja", tex_paja, rugosidad=0.92)
    mat_madera = get_mat("madera_viga")
    mat_bambu = get_mat("bambu_cana")
    mat_luz = get_mat("farol_luz")

    w, depth = 3.4, 2.8
    for px in [-1.4, 0.0, 1.4]:
        for py in [-1.1, 1.1]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.09, depth=2.4, location=(px, py, 0.8))
            p = bpy.context.active_object
            asignar_material(p, mat_madera)
            
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.95))
    suelo = bpy.context.active_object
    suelo.scale = (w + 0.5, depth + 0.5, 0.18)
    asignar_material(suelo, mat_troncos)
    aplicar_uv_caja(suelo, 1.5, 1.2)
    
    for bx in [-w * 0.5 - 0.15, w * 0.5 + 0.15]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, 0, 2.35))
        bar = bpy.context.active_object
        bar.scale = (0.06, depth + 0.4, 0.55)
        asignar_material(bar, mat_madera)
        
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.15, 2.9))
    choza = bpy.context.active_object
    choza.scale = (w - 0.4, depth - 0.4, 1.7)
    asignar_material(choza, mat_bambu)
    aplicar_uv_caja(choza, 1.2, 1.0)
    
    crear_prisma_tejado("Palafito_Techo", -w * 0.5 - 0.35, w * 0.5 + 0.35, -depth * 0.5 - 0.2, depth * 0.5 + 0.5, 3.6, 4.9, mat_paja, u_rep=2.4, v_rep=1.8)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -depth * 0.5 + 0.25, 2.55))
    puerta = bpy.context.active_object
    puerta.scale = (0.9, 0.1, 1.4)
    asignar_material(puerta, mat_madera)
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.15, location=(-1.1, -1.0, 2.8))
    farol = bpy.context.active_object
    asignar_material(farol, mat_luz)
    
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, depth * 0.5 + 0.05, 2.85))
    vent_t = bpy.context.active_object
    vent_t.scale = (0.75, 0.1, 0.75)
    asignar_material(vent_t, mat_luz)
    
    exportar_modelo("palafito", DIR_ENTORNO)

def generar_horreo():
    """Genera el Hórreo tradicional elevado de Sungura (Senda de los Surcos) completo en 360°:
    4 pilares de piedra con muelas/tornarratos antiroedores, plataforma de madera,
    cuerpo de tablones con ranuras de ventilación, tejado a dos aguas de paja dorada,
    escalera rústica y ventana cálida encendida."""
    limpiar_escena()
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    tex_piedra = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    tex_tejado = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    mat_troncos = obtener_material_textura("Mat_Horreo_Troncos", tex_troncos, rugosidad=0.85)
    mat_piedra = obtener_material_textura("Mat_Horreo_Piedra", tex_piedra, rugosidad=0.90)
    mat_tejado = obtener_material_textura("Mat_Horreo_Tejado", tex_tejado, rugosidad=0.92)
    mat_madera = get_mat("madera_viga")
    mat_luz = get_mat("farol_luz")

    w, depth = 3.6, 2.4
    # 1. 4 Pilares de piedra con tornarratos (muelas circulares)
    for px in [-1.4, 1.4]:
        for py in [-0.9, 0.9]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.14, depth=1.0, location=(px, py, 0.5))
            pil = bpy.context.active_object
            asignar_material(pil, mat_piedra)
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.30, depth=0.10, location=(px, py, 1.05))
            disco = bpy.context.active_object
            asignar_material(disco, mat_piedra)

    # 2. Plataforma de suelo de vigas y tablones
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.18))
    suelo = bpy.context.active_object
    suelo.scale = (w + 0.3, depth + 0.3, 0.16)
    asignar_material(suelo, mat_troncos)
    aplicar_uv_caja(suelo, 1.5, 1.0)

    # 3. Cuerpo de tablones del hórreo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.15))
    cuerpo = bpy.context.active_object
    cuerpo.scale = (w, depth, 1.8)
    asignar_material(cuerpo, mat_troncos)
    aplicar_uv_caja(cuerpo, 1.5, 1.2)

    # 4. Esquineros de refuerzo de madera
    for ex in [-w * 0.5 + 0.05, w * 0.5 - 0.05]:
        for ey in [-depth * 0.5 + 0.05, depth * 0.5 - 0.05]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, ey, 2.15))
            esq = bpy.context.active_object
            esq.scale = (0.15, 0.15, 1.85)
            asignar_material(esq, mat_madera)

    # 5. Tejado a dos aguas de paja dorada
    crear_prisma_tejado("Horreo_Techo", -w * 0.5 - 0.35, w * 0.5 + 0.35, -depth * 0.5 - 0.3, depth * 0.5 + 0.3, 3.0, 4.4, mat_tejado, u_rep=2.5, v_rep=1.8)

    # 6. Ventana frontal cálida encendida (coincidente con ["v", 58, 58])
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -depth * 0.5 - 0.04, 2.15))
    vent_f = bpy.context.active_object
    vent_f.scale = (0.7, 0.1, 0.7)
    asignar_material(vent_f, mat_luz)

    # 7. Escalera de acceso exterior
    for step in range(3):
        sy = -depth * 0.5 - 0.25 - step * 0.28
        sz = 0.85 - step * 0.26
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, sy, sz))
        peld = bpy.context.active_object
        peld.scale = (0.8, 0.26, 0.14)
        asignar_material(peld, mat_madera)

    # 8. Ventana trasera
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, depth * 0.5 + 0.04, 2.15))
    vent_tras = bpy.context.active_object
    vent_tras.scale = (0.6, 0.1, 0.6)
    asignar_material(vent_tras, mat_luz)

    exportar_modelo("horreo", DIR_ENTORNO)

def generar_campamento():
    """Genera el Campamento de explorador de Msafiri (Sendero del Puente) completo en 360°:
    Tienda canadiense de lona verde oliva con mástiles, fogata de piedras con brasas incandescentes,
    tocón de descanso, cajas de provisiones y petate enrollado."""
    limpiar_escena()
    mat_lona = obtener_material("Mat_Camp_Lona", "#4A5D3E", roughness=0.90)
    mat_madera = get_mat("madera_viga")
    mat_piedra = get_mat("piedra_plaza")
    mat_brasas = obtener_material("Mat_Camp_Brasas", "#DF9022", roughness=0.3, emission_hex="#FF6B00", emission_strength=3.5)
    mat_ceniza = get_mat("piedra_oscura")
    mat_farol = get_mat("farol_luz")

    # 1. Tienda canadiense (A-frame tent)
    for y_mast in [-1.1, 1.1]:
        for ang, sign in [(math.radians(28), -1), (-math.radians(28), 1)]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=2.4, location=(sign * 0.65, y_mast, 1.05))
            m = bpy.context.active_object
            m.rotation_euler = (0, ang, 0)
            asignar_material(m, mat_madera)

    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=2.5, location=(0, 0, 2.1))
    cumb = bpy.context.active_object
    cumb.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(cumb, mat_madera)

    crear_prisma_tejado("Tienda_Lona", -1.2, 1.2, -1.05, 1.05, 0.1, 2.05, mat_lona, u_rep=2.0, v_rep=1.5)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.0, 0.65))
    interior = bpy.context.active_object
    interior.scale = (1.4, 0.08, 1.1)
    asignar_material(interior, mat_ceniza)

    # 2. Fogata de piedras con brasas (coincidente con ["f", 52, 28])
    pos_fuego = (1.8, -0.4)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.45, depth=0.12, location=(pos_fuego[0], pos_fuego[1], 0.06))
    foso = bpy.context.active_object
    asignar_material(foso, mat_ceniza)

    for i in range(8):
        ang = i * (math.pi * 2.0 / 8.0)
        px = pos_fuego[0] + math.cos(ang) * 0.42
        py = pos_fuego[1] + math.sin(ang) * 0.42
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.11, location=(px, py, 0.10))
        piedra = bpy.context.active_object
        asignar_material(piedra, mat_piedra)

    for rot in [35, -45, 80]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=0.55, location=(pos_fuego[0], pos_fuego[1], 0.14))
        leno = bpy.context.active_object
        leno.rotation_euler = (math.radians(18), math.radians(rot), math.radians(25))
        asignar_material(leno, mat_madera)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.20, location=(pos_fuego[0], pos_fuego[1], 0.16))
    brasas = bpy.context.active_object
    asignar_material(brasas, mat_brasas)

    # 3. Tocón de asiento
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.26, depth=0.42, location=(pos_fuego[0] + 0.65, pos_fuego[1] - 0.35, 0.21))
    tocon = bpy.context.active_object
    asignar_material(tocon, mat_madera)

    # 4. Cajas de provisiones
    bpy.ops.mesh.primitive_cube_add(size=0.5, location=(-1.5, -0.3, 0.25))
    caja1 = bpy.context.active_object
    asignar_material(caja1, mat_madera)
    bpy.ops.mesh.primitive_cube_add(size=0.42, location=(-1.5, 0.3, 0.21))
    caja2 = bpy.context.active_object
    asignar_material(caja2, mat_madera)

    exportar_modelo("campamento", DIR_ENTORNO)

def generar_puesto_tinta():
    """Genera el Puesto de Venta de Tinta de Wino (Maandiko) completo en 360°:
    Mostrador de mármol de Sigilia con molduras, 4 postes de bronce, toldo a rayas índigo y blancas,
    estantería escalonada con frascos de tinta luminosa, pergaminos y farolillos dobles."""
    limpiar_escena()
    tex_marmol = os.path.join(DIR_SIGILIA, "marmol_sigilia_tile.png")
    tex_bronce = os.path.join(DIR_SIGILIA, "bronce_sigilia_tile.png")
    mat_marmol = obtener_material_textura("Mat_PuestoTinta_Marmol", tex_marmol, rugosidad=0.60)
    mat_bronce = obtener_material_textura("Mat_PuestoTinta_Bronce", tex_bronce, rugosidad=0.45, metalicidad=0.85)
    mat_toldo = obtener_material("Mat_PuestoTinta_Toldo", "#312E81", roughness=0.75)
    mat_tinta_azul = obtener_material("Mat_Tinta_Azul", "#2563EB", roughness=0.2, emission_hex="#3B82F6", emission_strength=2.8)
    mat_tinta_violeta = obtener_material("Mat_Tinta_Violeta", "#7C3AED", roughness=0.2, emission_hex="#8B5CF6", emission_strength=2.8)
    mat_pergamino = get_mat("marmol_sigilia")
    mat_luz = get_mat("farol_luz")

    w, depth = 3.6, 1.8

    # 1. Mostrador de mármol con repisa
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
    mostrador = bpy.context.active_object
    mostrador.scale = (w, depth * 0.7, 1.0)
    asignar_material(mostrador, mat_marmol)
    aplicar_uv_caja(mostrador, 1.5, 0.8)

    # 2. 4 Columnas / postes de bronce
    for px in [-w * 0.5 + 0.12, w * 0.5 - 0.12]:
        for py in [-depth * 0.5 + 0.12, depth * 0.5 - 0.12]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=2.4, location=(px, py, 1.2))
            col = bpy.context.active_object
            asignar_material(col, mat_bronce)

    # 3. Toldo de tela a dos aguas de Sigilia
    crear_prisma_tejado("Toldo_Tinta", -w * 0.5 - 0.25, w * 0.5 + 0.25, -depth * 0.5 - 0.2, depth * 0.5 + 0.2, 2.3, 3.1, mat_toldo, u_rep=2.5, v_rep=1.5)

    # 4. Estantes con frascos de tinta luminosa
    for sz, col_mat in [(1.08, mat_tinta_azul), (1.35, mat_tinta_violeta)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.15, sz - 0.05))
        estante = bpy.context.active_object
        estante.scale = (2.6, 0.35, 0.06)
        asignar_material(estante, mat_bronce)

        for fx in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.10, location=(fx, 0.15, sz + 0.08))
            frasco = bpy.context.active_object
            asignar_material(frasco, col_mat)
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=0.08, location=(fx, 0.15, sz + 0.20))
            cuello = bpy.context.active_object
            asignar_material(cuello, mat_bronce)

    # 5. Rollos de pergamino sobre el mostrador
    for rx in [-0.8, -0.5]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.04, depth=0.35, location=(rx, -0.22, 1.06))
        perg = bpy.context.active_object
        perg.rotation_euler = (math.radians(90), 0, math.radians(20))
        asignar_material(perg, mat_pergamino)

    # 6. Faroles laterales dobles (coincidentes con ["f", 28, 22] y ["f", 84, 22])
    for fx, sign in [(-w * 0.5 + 0.12, -1), (w * 0.5 - 0.12, 1)]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.13, location=(fx, -depth * 0.5 + 0.12, 1.85))
        farol = bpy.context.active_object
        asignar_material(farol, mat_luz)

    exportar_modelo("puesto_tinta", DIR_ENTORNO)

def generar_almacen():
    """Genera el Almacén portuario de Embarcadero Junco completo en 360°:
    Zócalo de mampostería, paredes de madera marítima, pórtico de carga con columnas y tornapuntas,
    gran portón doble con bisagras de hierro, tejado a dos aguas con pizarra,
    ático de carga con pescante/polea y cuerda, cajas de mercancías, barriles y farol cálido."""
    limpiar_escena()
    tex_mamposteria = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    tex_tejado = os.path.join(DIR_ALDEA, "forja_tejado_tile.png")
    
    mat_mamposteria = obtener_material_textura("Mat_Almacen_Piedra", tex_mamposteria, rugosidad=0.88)
    mat_troncos = obtener_material_textura("Mat_Almacen_Madera", tex_troncos, rugosidad=0.82)
    mat_tejado = obtener_material_textura("Mat_Almacen_Tejado", tex_tejado, rugosidad=0.75)
    mat_viga = get_mat("madera_viga")
    mat_hierro = get_mat("metal_forja")
    mat_luz = get_mat("farol_luz")
    mat_caja = get_mat("cuero_mochila")

    w, depth = 5.6, 3.6

    # 1. Zócalo de mampostería perimetral
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.22))
    zocalo = bpy.context.active_object
    zocalo.scale = (w + 0.2, depth + 0.2, 0.44)
    asignar_material(zocalo, mat_mamposteria)
    aplicar_uv_caja(zocalo, 2.0, 0.5)

    # 2. Cuerpo principal de tablones
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.65))
    cuerpo = bpy.context.active_object
    cuerpo.scale = (w, depth, 2.5)
    asignar_material(cuerpo, mat_troncos)
    aplicar_uv_caja(cuerpo, 2.2, 1.5)

    # 3. Vigas esquineras y molduras
    for ex in [-w * 0.5 + 0.08, w * 0.5 - 0.08]:
        for ey in [-depth * 0.5 + 0.08, depth * 0.5 - 0.08]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ex, ey, 1.7))
            esq = bpy.context.active_object
            esq.scale = (0.22, 0.22, 2.6)
            asignar_material(esq, mat_viga)

    # 4. Tejado a dos aguas
    crear_prisma_tejado("Almacen_Techo", -w * 0.5 - 0.4, w * 0.5 + 0.4, -depth * 0.5 - 0.35, depth * 0.5 + 0.35, 2.85, 4.65, mat_tejado, u_rep=3.0, v_rep=2.0)

    # 5. Voladizo / toldo frontal sobre el muelle de carga
    canopy_w = 3.8
    canopy_d = 1.4
    crear_prisma_tejado("Almacen_Canopy", -canopy_w * 0.5, canopy_w * 0.5, -depth * 0.5 - canopy_d, -depth * 0.5 + 0.1, 1.8, 2.5, mat_tejado, u_rep=2.0, v_rep=1.0)

    # Postes de soporte del voladizo con tornapuntas
    for px in [-canopy_w * 0.5 + 0.15, canopy_w * 0.5 - 0.15]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.09, depth=2.0, location=(px, -depth * 0.5 - canopy_d + 0.1, 1.0))
        poste = bpy.context.active_object
        asignar_material(poste, mat_viga)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, -depth * 0.5 - canopy_d * 0.5, 1.95))
        torna = bpy.context.active_object
        torna.scale = (0.1, 0.8, 0.1)
        torna.rotation_euler = (math.radians(-35), 0, 0)
        asignar_material(torna, mat_viga)

    # 6. Gran portón doble de madera con herrajes
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -depth * 0.5 - 0.05, 1.15))
    porton = bpy.context.active_object
    porton.scale = (2.2, 0.12, 1.8)
    asignar_material(porton, mat_viga)

    for hz in [0.65, 1.65]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -depth * 0.5 - 0.12, hz))
        bis = bpy.context.active_object
        bis.scale = (2.25, 0.04, 0.08)
        asignar_material(bis, mat_hierro)

    # 7. Vano superior de carga en el ático con viga pescante y polea
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -depth * 0.5 - 0.04, 3.4))
    atico_puerta = bpy.context.active_object
    atico_puerta.scale = (1.1, 0.08, 1.2)
    asignar_material(atico_puerta, mat_viga)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -depth * 0.5 - 0.7, 4.1))
    pescante = bpy.context.active_object
    pescante.scale = (0.16, 1.5, 0.16)
    asignar_material(pescante, mat_viga)

    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.18, depth=0.08, location=(0, -depth * 0.5 - 1.25, 3.95))
    polea = bpy.context.active_object
    polea.rotation_euler = (0, math.radians(90), 0)
    asignar_material(polea, mat_hierro)

    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.025, depth=1.5, location=(0, -depth * 0.5 - 1.25, 3.1))
    cuerda = bpy.context.active_object
    asignar_material(cuerda, mat_caja)

    # 8. Cajas y barriles de provisiones en el muelle
    pos_props = [
        (-1.9, -depth * 0.5 - 0.5, 0.25, 0.55),
        (-1.9, -depth * 0.5 - 1.05, 0.22, 0.48),
        (1.9, -depth * 0.5 - 0.6, 0.28, 0.60),
    ]
    for px, py, pz, sz in pos_props:
        bpy.ops.mesh.primitive_cube_add(size=sz, location=(px, py, pz))
        caja = bpy.context.active_object
        asignar_material(caja, mat_troncos)

    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.24, depth=0.6, location=(1.9, -depth * 0.5 - 1.2, 0.3))
    barril = bpy.context.active_object
    asignar_material(barril, mat_viga)

    # 9. Farol frontal encendido (coincidente con ["v", 52, 42])
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.14, location=(-canopy_w * 0.5 + 0.15, -depth * 0.5 - canopy_d + 0.1, 1.85))
    farol = bpy.context.active_object
    asignar_material(farol, mat_luz)

    # 10. Ventana trasera con luz cálida
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, depth * 0.5 + 0.05, 2.0))
    vent_t = bpy.context.active_object
    vent_t.scale = (0.9, 0.1, 0.8)
    asignar_material(vent_t, mat_luz)

    exportar_modelo("almacen", DIR_ENTORNO)

def generar_aprisco():
    """Genera el Aprisco comunal de cabras de Mbuzi (Cañada del Eco) completo en 360°:
    Muros macizos de mampostería alpina de pizarra, cobertizo rústico abierto con postes de tronco,
    tejado a un agua con teja de forja y musgo, corral vallado frontal con cancilla,
    comedero / pesebre con heno dorado, y linternas cálidas nocturnas."""
    limpiar_escena()
    tex_mamposteria = os.path.join(DIR_ALDEA, "forja_mamposteria_tile.png")
    tex_tejado = os.path.join(DIR_ALDEA, "forja_tejado_tile.png")
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")

    mat_mamposteria = obtener_material_textura("Mat_Aprisco_Piedra", tex_mamposteria, rugosidad=0.90)
    mat_tejado = obtener_material_textura("Mat_Aprisco_Techo", tex_tejado, rugosidad=0.80)
    mat_paja = obtener_material_textura("Mat_Aprisco_Heno", tex_paja, rugosidad=0.95)
    mat_viga = get_mat("madera_viga")
    mat_luz = get_mat("farol_luz")

    w, depth = 6.0, 3.8

    # 1. Muros perimetrales de piedra (fondo y laterales)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, depth * 0.5 - 0.2, 1.5))
    muro_t = bpy.context.active_object
    muro_t.scale = (w, 0.45, 3.0)
    asignar_material(muro_t, mat_mamposteria)
    aplicar_uv_caja(muro_t, 2.5, 1.5)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-w * 0.5 + 0.22, 0, 1.35))
    muro_izq = bpy.context.active_object
    muro_izq.scale = (0.45, depth, 2.7)
    asignar_material(muro_izq, mat_mamposteria)
    aplicar_uv_caja(muro_izq, 1.6, 1.4)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(w * 0.5 - 0.22, 0, 0.9))
    muro_der = bpy.context.active_object
    muro_der.scale = (0.45, depth, 1.8)
    asignar_material(muro_der, mat_mamposteria)
    aplicar_uv_caja(muro_der, 1.6, 1.0)

    # 2. Pilares de madera delanteros y viga maestra
    for px in [-w * 0.5 + 0.25, 0.0, w * 0.5 - 0.25]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.12, depth=2.8, location=(px, -depth * 0.5 + 0.25, 1.4))
        col = bpy.context.active_object
        asignar_material(col, mat_viga)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -depth * 0.5 + 0.25, 2.75))
    dintel = bpy.context.active_object
    dintel.scale = (w + 0.2, 0.24, 0.24)
    asignar_material(dintel, mat_viga)

    # 3. Tejado inclinado a dos aguas rústico
    crear_prisma_tejado("Aprisco_Techo", -w * 0.5 - 0.35, w * 0.5 + 0.35, -depth * 0.5 - 0.4, depth * 0.5 + 0.3, 2.6, 3.8, mat_tejado, u_rep=2.8, v_rep=1.8)

    # 4. Suelo de heno y paja en el interior
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.1))
    lecho = bpy.context.active_object
    lecho.scale = (w - 0.6, depth - 0.6, 0.18)
    asignar_material(lecho, mat_paja)
    aplicar_uv_caja(lecho, 2.0, 1.5)

    # 5. Pesebre / comedero de madera para las cabras
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, depth * 0.5 - 0.8, 0.45))
    pesebre = bpy.context.active_object
    pesebre.scale = (3.2, 0.55, 0.6)
    asignar_material(pesebre, mat_viga)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, depth * 0.5 - 0.8, 0.65))
    heno_pesebre = bpy.context.active_object
    heno_pesebre.scale = (3.0, 0.45, 0.25)
    asignar_material(heno_pesebre, mat_paja)

    # 6. Corral de estacas frontal
    corral_d = 2.4
    for cx in [-w * 0.5 + 0.2, -1.2, 1.2, w * 0.5 - 0.2]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.07, depth=1.1, location=(cx, -depth * 0.5 - corral_d, 0.55))
        p_corral = bpy.context.active_object
        asignar_material(p_corral, mat_viga)

    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * (w * 0.5 - 0.2), -depth * 0.5 - corral_d * 0.5, 0.6))
        trav_lat = bpy.context.active_object
        trav_lat.scale = (0.08, corral_d, 0.10)
        asignar_material(trav_lat, mat_viga)

    for bx in [-w * 0.5 * 0.65, w * 0.5 * 0.65]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bx, -depth * 0.5 - corral_d, 0.6))
        trav_f = bpy.context.active_object
        trav_f.scale = (1.6, 0.08, 0.10)
        asignar_material(trav_f, mat_viga)

    # 7. Luces cálidas correspondientes a ["v", 30, 92], ["f", 75, 85], ["f", 42, 82]
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-w * 0.5 - 0.05, 0.2, 1.6))
    vent_izq = bpy.context.active_object
    vent_izq.scale = (0.1, 0.65, 0.65)
    asignar_material(vent_izq, mat_luz)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.14, location=(-0.8, -0.2, 2.3))
    farol_int = bpy.context.active_object
    asignar_material(farol_int, mat_luz)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.14, location=(1.2, -depth * 0.5 - corral_d, 1.05))
    farol_ext = bpy.context.active_object
    asignar_material(farol_ext, mat_luz)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, depth * 0.5 + 0.05, 1.8))
    vent_post = bpy.context.active_object
    vent_post.scale = (0.7, 0.1, 0.6)
    asignar_material(vent_post, mat_luz)

    exportar_modelo("aprisco", DIR_ENTORNO)

def generar_madriguera():
    """Genera la Madriguera de Fuko el topo minero (Camino Cobrizo) completa en 360°:
    Colina de tierra y césped orgánico semiesférico, arco de mampostería de piedra labrada,
    puerta redonda tradicional con herrajes concéntricos y pomo de latón, chimenea de roca volcánica
    con tubo para humo, ventana redonda con vidriera luminosa, cubetas de mineral de cobre y faroles."""
    limpiar_escena()
    tex_mamposteria = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    mat_mamposteria = obtener_material_textura("Mat_Madriguera_Piedra", tex_mamposteria, rugosidad=0.88)
    mat_hierba = obtener_material("Mat_Madriguera_Cesped", "#3F6828", roughness=0.95)
    mat_madera = get_mat("madera_viga")
    mat_cobre = obtener_material("Mat_Madriguera_Cobre", "#DF9022", roughness=0.35, metallic=0.75, emission_hex="#FF9933", emission_strength=1.8)
    mat_luz = get_mat("farol_luz")
    mat_chimenea = get_mat("piedra_oscura")

    radius_mound = 2.8

    # 1. Túmulo de tierra y hierba orgánica (cúpula semiesférica rebajada)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=radius_mound, location=(0, 0.4, 0.0))
    colina = bpy.context.active_object
    colina.scale = (1.0, 0.85, 0.72)
    asignar_material(colina, mat_hierba)

    # 2. Fachada de mampostería frontal encastrada en la colina
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -radius_mound * 0.85 * 0.72, 1.1))
    fachada = bpy.context.active_object
    fachada.scale = (3.4, 0.6, 2.2)
    asignar_material(fachada, mat_mamposteria)
    aplicar_uv_caja(fachada, 1.8, 1.2)

    # 3. Arco de piedra labrada sobre la entrada
    bpy.ops.mesh.primitive_torus_add(major_radius=0.95, minor_radius=0.18, major_segments=16, minor_segments=8, location=(0, -radius_mound * 0.85 * 0.72 - 0.28, 1.15))
    arco = bpy.context.active_object
    arco.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(arco, mat_mamposteria)

    # 4. Puerta circular de madera con tirador de latón
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.85, depth=0.14, location=(0, -radius_mound * 0.85 * 0.72 - 0.22, 1.15))
    puerta = bpy.context.active_object
    puerta.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(puerta, mat_madera)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.08, location=(0, -radius_mound * 0.85 * 0.72 - 0.32, 1.15))
    pomo = bpy.context.active_object
    asignar_material(pomo, mat_cobre)

    # 5. Ventana redonda con luz cálida (coincidente con ["v", 29, 66])
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.38, depth=0.12, location=(-1.2, -radius_mound * 0.85 * 0.72 - 0.24, 1.15))
    vent_circ = bpy.context.active_object
    vent_circ.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(vent_circ, mat_luz)

    # 6. Chimenea de piedra con orificio superior
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.25, depth=1.4, location=(0.9, 0.6, 2.4))
    chimenea = bpy.context.active_object
    asignar_material(chimenea, mat_chimenea)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.32, depth=0.18, location=(0.9, 0.6, 3.1))
    caperuza = bpy.context.active_object
    asignar_material(caperuza, mat_chimenea)

    # 7. Cestas / cubetas con mineral de cobre brillante
    for mx, my in [(1.3, -radius_mound * 0.85 * 0.72 - 0.4), (1.65, -radius_mound * 0.85 * 0.72 - 0.15)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.24, depth=0.32, location=(mx, my, 0.16))
        cubo = bpy.context.active_object
        asignar_material(cubo, mat_madera)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.16, location=(mx, my, 0.32))
        mena = bpy.context.active_object
        asignar_material(mena, mat_cobre)

    # 8. Faroles en báculo exterior correspondientes a ["f", 59, 68] y ["f", 85, 68]
    for fx, fz in [(-1.5, 1.3), (1.5, 1.3)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=1.6, location=(fx, -radius_mound * 0.85 * 0.72 - 0.35, 0.8))
        gancho = bpy.context.active_object
        asignar_material(gancho, mat_chimenea)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.13, location=(fx, -radius_mound * 0.85 * 0.72 - 0.35, fz))
        farol = bpy.context.active_object
        asignar_material(farol, mat_luz)

    # 9. Ventanita trasera en la colina para 360°
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, radius_mound * 0.8, 1.2))
    vent_t = bpy.context.active_object
    vent_t.scale = (0.5, 0.1, 0.5)
    asignar_material(vent_t, mat_luz)

    exportar_modelo("madriguera", DIR_ENTORNO)

def generar_torre():
    """Genera la Torre Vigía Ancestral de El Kitovu completa en 360°:
    Zócalo escalonado de mampostería, fuste octogonal con troneras y aspilleras iluminadas,
    moldura intermedia de cantería, coronamiento almenado con parapeto y matacanes,
    puerta de entrada de madera con dintel de piedra, y farol en la cima."""
    limpiar_escena()
    tex_mamposteria = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    mat_piedra = obtener_material_textura("Mat_Torre_Piedra", tex_mamposteria, rugosidad=0.88)
    mat_madera = get_mat("madera_viga")
    mat_luz = get_mat("farol_luz")
    mat_cornisa = get_mat("piedra_plaza")

    # 1. Zócalo base octogonal
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.65, depth=0.45, location=(0, 0, 0.22))
    zocalo = bpy.context.active_object
    asignar_material(zocalo, mat_piedra)
    aplicar_uv_cilindro(zocalo, 2.0, 0.5)

    # 2. Fuste principal de la torre
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.40, depth=4.6, location=(0, 0, 2.7))
    fuste = bpy.context.active_object
    asignar_material(fuste, mat_piedra)
    aplicar_uv_cilindro(fuste, 2.5, 3.0)

    # 3. Moldura de imposta intermedia
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.52, depth=0.22, location=(0, 0, 2.8))
    imposta = bpy.context.active_object
    asignar_material(imposta, mat_cornisa)

    # 4. Puerta de arco de madera al sur
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.35, 1.1))
    puerta = bpy.context.active_object
    puerta.scale = (0.9, 0.2, 1.7)
    asignar_material(puerta, mat_madera)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.38, 2.05))
    dintel = bpy.context.active_object
    dintel.scale = (1.2, 0.24, 0.22)
    asignar_material(dintel, mat_cornisa)

    # 5. Aspilleras / troneras con luz interior en las 4 caras cardinales
    for rot, (ox, oy) in [(0, (0, -1.38)), (90, (1.38, 0)), (180, (0, 1.38)), (270, (-1.38, 0))]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox, oy, 3.7))
        tronera = bpy.context.active_object
        tronera.scale = (0.28, 0.15, 0.75) if (rot % 180 == 0) else (0.15, 0.28, 0.75)
        asignar_material(tronera, mat_luz)

    # 6. Coronamiento con voladizo y almenas
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.70, depth=0.35, location=(0, 0, 5.15))
    cornisa_sup = bpy.context.active_object
    asignar_material(cornisa_sup, mat_cornisa)

    for i in range(8):
        ang = i * (math.pi * 2.0 / 8.0)
        px = math.cos(ang) * 1.55
        py = math.sin(ang) * 1.55
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, py, 5.7))
        merlon = bpy.context.active_object
        merlon.scale = (0.45, 0.45, 0.75)
        merlon.rotation_euler = (0, 0, ang)
        asignar_material(merlon, mat_piedra)

    # 7. Plataforma superior de madera y mástil con farol
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.45, depth=0.15, location=(0, 0, 5.0))
    tarima = bpy.context.active_object
    asignar_material(tarima, mat_madera)

    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=1.8, location=(0, 0, 5.9))
    mastil = bpy.context.active_object
    asignar_material(mastil, mat_madera)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.20, location=(0, 0, 6.7))
    faro = bpy.context.active_object
    asignar_material(faro, mat_luz)

    exportar_modelo("torre", DIR_ENTORNO)

def generar_monumento():
    """Genera el Monumento Ancestral de las Raíces (El Kitovu) completo en 360°:
    Pedestal escalonado de mampostería, monolito megalítico vertical con runas grabadas,
    raíces petrificadas curvadas que abrazan la roca y corazón de Asili con brillo ámbar dorado."""
    limpiar_escena()
    tex_mamposteria = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_piedra = obtener_material_textura("Mat_Monumento_Piedra", tex_mamposteria, rugosidad=0.85)
    mat_raiz = obtener_material_textura("Mat_Monumento_Raiz", tex_troncos, rugosidad=0.90)
    mat_asili = obtener_material("Mat_Monumento_Asili", "#DF9022", roughness=0.2, emission_hex="#FFB300", emission_strength=3.5)
    mat_pedestal = get_mat("piedra_plaza")

    # 1. Base escalonada doble
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.18))
    grada1 = bpy.context.active_object
    grada1.scale = (2.6, 2.2, 0.36)
    asignar_material(grada1, mat_pedestal)
    aplicar_uv_caja(grada1, 1.5, 0.4)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.48))
    grada2 = bpy.context.active_object
    grada2.scale = (2.0, 1.7, 0.28)
    asignar_material(grada2, mat_pedestal)
    aplicar_uv_caja(grada2, 1.2, 0.3)

    # 2. Monolito megalítico central de piedra
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.1))
    monolito = bpy.context.active_object
    monolito.scale = (1.3, 0.85, 3.2)
    asignar_material(monolito, mat_piedra)
    aplicar_uv_caja(monolito, 1.2, 2.4)

    bpy.ops.mesh.primitive_cylinder_add(vertices=4, radius=0.68, depth=0.6, location=(0, 0, 3.85))
    cumbre = bpy.context.active_object
    cumbre.rotation_euler = (0, 0, math.radians(45))
    asignar_material(cumbre, mat_piedra)

    # 3. Raíces petrificadas curvadas alrededor del monolito
    for i, ang in enumerate([0.5, 2.2, 3.8, 5.2]):
        rx = math.cos(ang) * 0.72
        ry = math.sin(ang) * 0.52
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.14 - i * 0.015, depth=2.4, location=(rx, ry, 1.5))
        rz = bpy.context.active_object
        rz.rotation_euler = (math.sin(ang) * 0.25, math.cos(ang) * 0.25, math.radians(15 * (i % 2 * 2 - 1)))
        asignar_material(rz, mat_raiz)

    # 4. Corazón de Asili: Vena rúnica central incandescente
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.28, location=(0, -0.45, 2.3))
    corazon_f = bpy.context.active_object
    corazon_f.scale = (0.7, 0.3, 1.4)
    asignar_material(corazon_f, mat_asili)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.24, location=(0, 0.45, 2.3))
    corazon_t = bpy.context.active_object
    corazon_t.scale = (0.7, 0.3, 1.2)
    asignar_material(corazon_t, mat_asili)

    # 5. 4 Estelas satélite en las esquinas
    for sx, sy in [(-1.05, -0.85), (1.05, -0.85), (-1.05, 0.85), (1.05, 0.85)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, sy, 0.8))
        estela = bpy.context.active_object
        estela.scale = (0.28, 0.28, 0.7)
        asignar_material(estela, mat_piedra)

    exportar_modelo("monumento", DIR_ENTORNO)

def generar_altar():
    """Genera el Altar Sagrado de Lago Espejo completo en 360°:
    Grada circular de cantería sobre el agua, pila bautismal / estanque reflectante hexagonal
    con aguas puras de brillo turquesa, 4 columnas con capiteles y farol votivo central."""
    limpiar_escena()
    tex_mamposteria = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    mat_piedra = obtener_material_textura("Mat_Altar_Piedra", tex_mamposteria, rugosidad=0.85)
    mat_marmol = get_mat("piedra_plaza")
    mat_agua_sagrada = obtener_material("Mat_Altar_Agua", "#40D8C8", roughness=0.1, emission_hex="#50F8E0", emission_strength=2.8)
    mat_luz = get_mat("farol_luz")

    # 1. Grada circular escalonada
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.85, depth=0.25, location=(0, 0, 0.125))
    grada_inf = bpy.context.active_object
    asignar_material(grada_inf, mat_marmol)

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.45, depth=0.25, location=(0, 0, 0.35))
    grada_sup = bpy.context.active_object
    asignar_material(grada_sup, mat_piedra)

    # 2. Pila ritual hexagonal
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.95, depth=0.65, location=(0, 0, 0.75))
    pila = bpy.context.active_object
    asignar_material(pila, mat_marmol)

    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.82, depth=0.10, location=(0, 0, 1.05))
    agua_altar = bpy.context.active_object
    asignar_material(agua_altar, mat_agua_sagrada)

    # 3. 4 Columnas con capiteles en los vértices diagonales
    for px, py in [(-1.25, -1.05), (1.25, -1.05), (-1.25, 1.05), (1.25, 1.05)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.12, depth=1.6, location=(px, py, 1.15))
        col = bpy.context.active_object
        asignar_material(col, mat_marmol)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, py, 1.95))
        capitel = bpy.context.active_object
        capitel.scale = (0.34, 0.34, 0.16)
        asignar_material(capitel, mat_piedra)

    # 4. Mesa / losa de ofrendas frontal
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.25, 0.55))
    mesa = bpy.context.active_object
    mesa.scale = (0.85, 0.45, 0.35)
    asignar_material(mesa, mat_marmol)

    # 5. Llama sagrada votiva sobre el centro del altar
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.18, location=(0, 0, 1.45))
    llama = bpy.context.active_object
    asignar_material(llama, mat_luz)

    exportar_modelo("altar", DIR_ENTORNO)

def generar_grua():
    """Genera la Grúa de carga de Embarcadero Junco completa en 360°:
    Bancada de madera maciza con durmientes, mástil vertical de tronco reforzado con zunchos de hierro,
    pluma diagonal con tornapuntas, polea superior de fundición, cable colgante con gancho de hierro,
    cajón de contrapeso con piedras de balasto, cabrestante con manivela y farol cálido de atraque."""
    limpiar_escena()
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_troncos = obtener_material_textura("Mat_Grua_Madera", tex_troncos, rugosidad=0.85)
    mat_viga = get_mat("madera_viga")
    mat_hierro = get_mat("metal_forja")
    mat_piedra = get_mat("piedra_oscura")
    mat_luz = get_mat("farol_luz")
    mat_cuerda = get_mat("cuero_mochila")

    # 1. Bancada / plataforma base de durmientes
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.16))
    base = bpy.context.active_object
    base.scale = (3.2, 2.4, 0.32)
    asignar_material(base, mat_troncos)
    aplicar_uv_caja(base, 1.8, 1.2)

    # Tirantes / travesaños de anclaje
    for by in [-0.85, 0.85]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, by, 0.36))
        trav = bpy.context.active_object
        trav.scale = (3.4, 0.22, 0.12)
        asignar_material(trav, mat_viga)

    # 2. Mástil vertical giratorio central
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.22, depth=4.4, location=(0, 0, 2.36))
    mastil = bpy.context.active_object
    asignar_material(mastil, mat_troncos)
    aplicar_uv_cilindro(mastil, 1.5, 3.0)

    # Zunchos / abrazaderas de hierro del mástil
    for hz in [0.45, 2.2, 4.3]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.25, depth=0.10, location=(0, 0, hz))
        zuncho = bpy.context.active_object
        asignar_material(zuncho, mat_hierro)

    # 3. Tornapuntas de base (soporte en A del mástil)
    for ang in [math.radians(30), math.radians(150), math.radians(-45), math.radians(-135)]:
        tx = math.cos(ang) * 0.75
        ty = math.sin(ang) * 0.75
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.08, depth=1.8, location=(tx, ty, 0.95))
        strut = bpy.context.active_object
        strut.rotation_euler = (math.sin(ang) * 0.55, -math.cos(ang) * 0.55, 0)
        asignar_material(strut, mat_viga)

    # 4. Pluma de carga diagonal inclinada hacia el frente (muelle/agua: -Y)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.14, depth=4.2, location=(0, -1.45, 3.4))
    pluma = bpy.context.active_object
    pluma.rotation_euler = (math.radians(-48), 0, 0)
    asignar_material(pluma, mat_viga)

    # Puntal de soporte de la pluma
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.09, depth=2.4, location=(0, -1.0, 2.4))
    puntal = bpy.context.active_object
    puntal.rotation_euler = (math.radians(-25), 0, 0)
    asignar_material(puntal, mat_viga)

    # 5. Polea superior en la punta de la pluma
    punta_x, punta_y, punta_z = 0.0, -2.9, 4.8
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.26, depth=0.12, location=(punta_x, punta_y, punta_z))
    polea = bpy.context.active_object
    polea.rotation_euler = (0, math.radians(90), 0)
    asignar_material(polea, mat_hierro)

    # Horquilla de sujeción de la polea
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(punta_x, punta_y, punta_z + 0.12))
    horquilla = bpy.context.active_object
    horquilla.scale = (0.34, 0.16, 0.28)
    asignar_material(horquilla, mat_hierro)

    # 6. Cable y Gancho de elevación
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.022, depth=3.2, location=(punta_x, punta_y, punta_z - 1.6))
    cable = bpy.context.active_object
    asignar_material(cable, mat_cuerda)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.04, major_segments=12, minor_segments=6, location=(punta_x, punta_y, punta_z - 3.2))
    gancho = bpy.context.active_object
    asignar_material(gancho, mat_hierro)

    # 7. Cajón de contrapeso posterior (+Y)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 1.25, 0.75))
    cajon = bpy.context.active_object
    cajon.scale = (1.4, 0.95, 0.85)
    asignar_material(cajon, mat_troncos)
    aplicar_uv_caja(cajon, 1.2, 0.8)

    for px, py, pz in [(-0.35, 1.15, 1.25), (0.35, 1.15, 1.22), (0.0, 1.35, 1.28)]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.22, location=(px, py, pz))
        balasto = bpy.context.active_object
        asignar_material(balasto, mat_piedra)

    # 8. Cabrestante / torno manual en el mástil
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.22, depth=0.65, location=(0, -0.38, 1.15))
    tambor = bpy.context.active_object
    tambor.rotation_euler = (0, math.radians(90), 0)
    asignar_material(tambor, mat_viga)

    for mx, rot_m in [(-0.38, 0), (0.38, math.radians(180))]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(mx, -0.38, 1.15))
        brazo_m = bpy.context.active_object
        brazo_m.scale = (0.04, 0.06, 0.42)
        brazo_m.rotation_euler = (rot_m, 0, 0)
        asignar_material(brazo_m, mat_hierro)

        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.18, location=(mx + (-0.08 if mx < 0 else 0.08), -0.38, 1.15 + (0.18 if rot_m == 0 else -0.18)))
        mango = bpy.context.active_object
        mango.rotation_euler = (0, math.radians(90), 0)
        asignar_material(mango, mat_viga)

    # 9. Farol cálido de faena nocturna
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.14, location=(0.35, -0.5, 2.6))
    farol = bpy.context.active_object
    asignar_material(farol, mat_luz)

    exportar_modelo("grua", DIR_ENTORNO)

def generar_barca():
    """Genera la Barca de remos tradicional (Lago Espejo y Embarcadero) completa en 360°:
    Casco de madera de tingladillo con roda curvada y espejo de popa, regalas macizas con chumaceras,
    bancos de remero transversales, cuadernas interiores de refuerzo, par de remos descansando en la borda
    y cabo de amarre trenzado en la proa."""
    limpiar_escena()
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_madera = obtener_material_textura("Mat_Barca_Madera", tex_troncos, rugosidad=0.82)
    mat_viga = get_mat("madera_viga")
    mat_bronce = get_mat("metal_forja")
    mat_cuerda = get_mat("cuero_mochila")

    length, width, height = 3.4, 1.4, 0.65

    # 1. Quilla y Roda de proa curvada (-Y proa, +Y popa)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.08))
    quilla = bpy.context.active_object
    quilla.scale = (0.14, length, 0.16)
    asignar_material(quilla, mat_viga)

    # Roda de proa inclinada
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -length * 0.5 - 0.12, 0.38))
    roda = bpy.context.active_object
    roda.scale = (0.14, 0.18, 0.65)
    roda.rotation_euler = (math.radians(-24), 0, 0)
    asignar_material(roda, mat_viga)

    # 2. Casco: fondo y costados con caída
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.05, 0.14))
    fondo = bpy.context.active_object
    fondo.scale = (width * 0.72, length * 0.82, 0.08)
    asignar_material(fondo, mat_madera)
    aplicar_uv_caja(fondo, 1.5, 2.5)

    # Costados (bandas de babor y estribor)
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * width * 0.46, 0.05, 0.38))
        costado = bpy.context.active_object
        costado.scale = (0.08, length * 0.85, height * 0.75)
        costado.rotation_euler = (0, sign * math.radians(14), 0)
        asignar_material(costado, mat_madera)
        aplicar_uv_caja(costado, 1.0, 2.5)

        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=length * 0.90, location=(sign * width * 0.52, 0.05, 0.65))
        regala = bpy.context.active_object
        regala.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(regala, mat_viga)

        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=0.12, location=(sign * width * 0.54, 0.0, 0.72))
        chumacera = bpy.context.active_object
        asignar_material(chumacera, mat_bronce)

    # 3. Espejo de popa plano (+Y)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, length * 0.5 - 0.05, 0.38))
    popa = bpy.context.active_object
    popa.scale = (width * 0.80, 0.10, height * 0.75)
    asignar_material(popa, mat_viga)

    # 4. Cuadernas interiores
    for cy in [-0.8, 0.0, 0.8]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, cy, 0.18))
        cuaderna = bpy.context.active_object
        cuaderna.scale = (width * 0.75, 0.08, 0.10)
        asignar_material(cuaderna, mat_viga)

    # 5. Bancos transversales de remero
    bancos_pos = [
        (-0.75, 0.45, 0.45),
        (0.0, 0.65, 0.42),
        (0.9, 0.60, 0.45),
    ]
    for by, bw, bz in bancos_pos:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, by, bz))
        banco = bpy.context.active_object
        banco.scale = (width * bw, 0.28, 0.06)
        asignar_material(banco, mat_viga)

    # 6. Par de remos descansando en ángulo sobre la borda
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=2.2, location=(sign * 0.35, -0.15, 0.62))
        remo = bpy.context.active_object
        remo.rotation_euler = (math.radians(16), sign * math.radians(-22), sign * math.radians(15))
        asignar_material(remo, mat_viga)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 0.85, 0.80, 0.75))
        pala = bpy.context.active_object
        pala.scale = (0.16, 0.55, 0.03)
        pala.rotation_euler = (math.radians(16), sign * math.radians(-22), sign * math.radians(15))
        asignar_material(pala, mat_viga)

    # 7. Rollo de cabo de amarre en la proa
    bpy.ops.mesh.primitive_torus_add(major_radius=0.18, minor_radius=0.045, major_segments=12, minor_segments=6, location=(0, -length * 0.5 + 0.35, 0.42))
    cabo = bpy.context.active_object
    asignar_material(cabo, mat_cuerda)

    exportar_modelo("barca", DIR_ENTORNO)

def generar_estela():
    """Genera la Estela Rúnica de refugio de Paso de la Escarcha (Sigilia) completa en 360°:
    Pedestal macizo de roca de esquisto labrada, losa monolítica vertical con coronamiento achaflanado,
    runas de Sigilia profundamente cinceladas con incandescencia cian mística, cornisa con nieve acumulada,
    y estela satélite menor con glifos de orientación frente a la ventisca."""
    limpiar_escena()
    tex_marmol = os.path.join(DIR_SIGILIA, "marmol_sigilia_tile.png")
    mat_piedra = obtener_material_textura("Mat_Estela_Piedra", tex_marmol, rugosidad=0.80)
    mat_runa = obtener_material("Mat_Estela_Runa", "#38BDF8", roughness=0.15, emission_hex="#67E8F9", emission_strength=3.5)
    mat_nieve = obtener_material("Mat_Estela_Nieve", "#F1F5F9", roughness=0.75)
    mat_base = get_mat("piedra_oscura")

    # 1. Pedestal de mampostería base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.16))
    base = bpy.context.active_object
    base.scale = (1.8, 1.2, 0.32)
    asignar_material(base, mat_base)
    aplicar_uv_caja(base, 1.2, 0.5)

    # 2. Monolito principal vertical
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.45))
    monolito = bpy.context.active_object
    monolito.scale = (1.25, 0.55, 2.3)
    asignar_material(monolito, mat_piedra)
    aplicar_uv_caja(monolito, 1.2, 2.0)

    # 3. Coronamiento triangular achaflanado
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.65, depth=0.55, location=(0, 0, 2.85))
    cumbre = bpy.context.active_object
    cumbre.rotation_euler = (math.radians(90), 0, math.radians(90))
    asignar_material(cumbre, mat_piedra)

    # 4. Capa de nieve acumulada en la parte superior y salientes
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 3.12))
    nieve_sup = bpy.context.active_object
    nieve_sup.scale = (1.3, 0.58, 0.12)
    asignar_material(nieve_sup, mat_nieve)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.22, 0.34))
    nieve_base = bpy.context.active_object
    nieve_base.scale = (1.7, 0.40, 0.08)
    asignar_material(nieve_base, mat_nieve)

    # 5. Runas de Sigilia luminosas talladas (frontal y trasera)
    for rz in [1.1, 1.6, 2.1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.29, rz))
        runa_f = bpy.context.active_object
        runa_f.scale = (0.65, 0.06, 0.18)
        asignar_material(runa_f, mat_runa)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.22, depth=0.06, location=(0, -0.29, 2.5))
    glifo_circ_f = bpy.context.active_object
    glifo_circ_f.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(glifo_circ_f, mat_runa)

    for rz in [1.3, 1.9]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.29, rz))
        runa_t = bpy.context.active_object
        runa_t.scale = (0.55, 0.06, 0.18)
        asignar_material(runa_t, mat_runa)

    # 6. Estela satélite menor al costado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.05, 0.1, 0.55))
    menor = bpy.context.active_object
    menor.scale = (0.35, 0.35, 0.8)
    menor.rotation_euler = (0, 0, math.radians(12))
    asignar_material(menor, mat_piedra)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.05, 0.1, 0.98))
    nieve_menor = bpy.context.active_object
    nieve_menor.scale = (0.38, 0.38, 0.08)
    asignar_material(nieve_menor, mat_nieve)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.08, location=(1.05, -0.09, 0.6))
    runa_sat = bpy.context.active_object
    asignar_material(runa_sat, mat_runa)

    exportar_modelo("estela", DIR_ENTORNO)

def generar_menhir():
    """Genera el Menhir Ancestral de Lago Espejo completo en 360°:
    Monolito megalítico de piedra tallada que surge de las aguas, aristas achaflanadas orgánicas,
    petroglifos en espiral con luminiscencia turquesa de lago, y base húmeda sumergida."""
    limpiar_escena()
    tex_mamposteria = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    mat_piedra = obtener_material_textura("Mat_Menhir_Piedra", tex_mamposteria, rugosidad=0.85)
    mat_glifo = obtener_material("Mat_Menhir_Agua", "#40D8C8", roughness=0.15, emission_hex="#50F8E0", emission_strength=2.8)
    mat_base = get_mat("piedra_oscura")

    # 1. Base sumergida
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.75, depth=0.35, location=(0, 0, 0.175))
    base = bpy.context.active_object
    asignar_material(base, mat_base)

    # 2. Fuste principal del menhir
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.60, depth=2.8, location=(0, 0, 1.55))
    fuste = bpy.context.active_object
    fuste.scale = (0.9, 0.7, 1.0)
    asignar_material(fuste, mat_piedra)
    aplicar_uv_cilindro(fuste, 1.5, 2.0)

    # 3. Cumbre piramidal rebajada
    bpy.ops.mesh.primitive_cylinder_add(vertices=4, radius=0.45, depth=0.55, location=(0, 0, 3.15))
    punta = bpy.context.active_object
    punta.rotation_euler = (0, 0, math.radians(45))
    asignar_material(punta, mat_piedra)

    # 4. Grabados de espirales de agua / turquesa brillante
    for pz, rot_z in [(1.2, 0), (1.9, math.radians(120)), (2.5, math.radians(240))]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.18, minor_radius=0.035, major_segments=12, minor_segments=6, location=(0, -0.40, pz))
        espiral = bpy.context.active_object
        espiral.rotation_euler = (math.radians(90), 0, rot_z)
        asignar_material(espiral, mat_glifo)

    exportar_modelo("menhir", DIR_ENTORNO)

def generar_portal_raiz():
    """Genera el Portal Ancestral de Raíces (El Kitovu) completo en 360°:
    Dos columnas monumentales de piedra labrada con zócalos escalonados, raíces vivientes del Primer Árbol
    que trepan enroscadas por ambos fustes hasta unirse en arco superior, y la Semilla del Arco gigante
    en el vértice superior con palpitación rúnica dorada de Asili."""
    limpiar_escena()
    tex_mamposteria = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_piedra = obtener_material_textura("Mat_Portal_Piedra", tex_mamposteria, rugosidad=0.85)
    mat_raiz = obtener_material_textura("Mat_Portal_Raiz", tex_troncos, rugosidad=0.88)
    mat_semilla = obtener_material("Mat_Portal_Semilla", "#DF9022", roughness=0.15, emission_hex="#FFB300", emission_strength=3.8)
    mat_runa = obtener_material("Mat_Portal_Runa", "#DF9022", roughness=0.2, emission_hex="#FFA000", emission_strength=2.6)
    mat_base = get_mat("piedra_oscura")

    span_x = 2.4

    # 1. Zócalos escalonados de cada columna
    for sign in [-1, 1]:
        px = sign * span_x
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0, 0.22))
        base1 = bpy.context.active_object
        base1.scale = (1.5, 1.5, 0.44)
        asignar_material(base1, mat_base)
        aplicar_uv_caja(base1, 1.2, 0.4)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0, 0.55))
        base2 = bpy.context.active_object
        base2.scale = (1.2, 1.2, 0.25)
        asignar_material(base2, mat_piedra)

        # Fuste de piedra octogonal de la columna
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.48, depth=4.6, location=(px, 0, 2.9))
        fuste = bpy.context.active_object
        asignar_material(fuste, mat_piedra)
        aplicar_uv_cilindro(fuste, 1.5, 3.0)

        # Capitel superior
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0, 5.3))
        capitel = bpy.context.active_object
        capitel.scale = (1.25, 1.25, 0.35)
        asignar_material(capitel, mat_piedra)

        # Runas doradas en la cara frontal
        for rz in [2.0, 3.2, 4.4]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, -0.49, rz))
            runa = bpy.context.active_object
            runa.scale = (0.42, 0.05, 0.22)
            asignar_material(runa, mat_runa)

    # 2. Raíces trepadoras que se enroscan en las columnas
    for sign in [-1, 1]:
        px = sign * span_x
        for i, ang in enumerate([0.3, 1.8, 3.4, 4.9]):
            rx = px + math.cos(ang) * 0.52
            ry = math.sin(ang) * 0.52
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.12 - i * 0.015, depth=3.2, location=(rx, ry, 2.2))
            raiz = bpy.context.active_object
            raiz.rotation_euler = (math.sin(ang) * 0.22, -sign * math.cos(ang) * 0.22, math.radians(15 * (i % 2 * 2 - 1)))
            asignar_material(raiz, mat_raiz)

    # 3. Arco superior de raíces entrelazadas
    bpy.ops.mesh.primitive_torus_add(major_radius=span_x, minor_radius=0.28, major_segments=16, minor_segments=8, location=(0, 0, 5.3))
    arco_r = bpy.context.active_object
    arco_r.rotation_euler = (math.radians(90), 0, 0)
    arco_r.scale = (1.0, 1.0, 0.85)
    asignar_material(arco_r, mat_raiz)

    # 4. Semilla del Arco en el centro superior
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.48, location=(0, 0, 5.85))
    semilla = bpy.context.active_object
    semilla.scale = (0.85, 0.85, 1.25)
    asignar_material(semilla, mat_semilla)

    for ang in [0, math.radians(60), math.radians(120), math.radians(180), math.radians(240), math.radians(300)]:
        zx = math.cos(ang) * 0.42
        zy = math.sin(ang) * 0.42
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=0.75, location=(zx, zy, 5.85))
        zarcillo = bpy.context.active_object
        zarcillo.rotation_euler = (math.sin(ang) * 0.45, -math.cos(ang) * 0.45, ang)
        asignar_material(zarcillo, mat_raiz)

    exportar_modelo("portal_raiz", DIR_ENTORNO)

def generar_arco_ruinas():
    """Genera el Arco de las Ruinas de Sendero Olvidado completo en 360°:
    Dos pilares fracturados de piedra clara con basa moldurada, raíces ancestrales del Primer Árbol
    que abrazan el fuste, arquitrabe superior derruido con sección quebrada, las nueve espirales de los ecos
    talladas en relieve luminoso, y sillares desprendidos caídos en la base."""
    limpiar_escena()
    tex_marmol = os.path.join(DIR_SIGILIA, "marmol_sigilia_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_piedra = obtener_material_textura("Mat_ArcoRuina_Piedra", tex_marmol, rugosidad=0.82)
    mat_raiz = obtener_material_textura("Mat_ArcoRuina_Raiz", tex_troncos, rugosidad=0.88)
    mat_espiral = obtener_material("Mat_ArcoRuina_Espiral", "#DF9022", roughness=0.2, emission_hex="#FFA500", emission_strength=2.8)
    mat_base = get_mat("piedra_oscura")

    sep_x = 2.12

    alturas = [4.8, 4.2]
    for idx, sign in enumerate([-1, 1]):
        px = sign * sep_x
        h = alturas[idx]

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0, 0.25))
        basa = bpy.context.active_object
        basa.scale = (1.4, 1.4, 0.50)
        asignar_material(basa, mat_base)
        aplicar_uv_caja(basa, 1.2, 0.5)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0, 0.5 + h * 0.5))
        fuste = bpy.context.active_object
        fuste.scale = (1.05, 1.05, h)
        asignar_material(fuste, mat_piedra)
        aplicar_uv_caja(fuste, 1.2, 3.0)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 0, 0.5 + h))
        capitel = bpy.context.active_object
        capitel.scale = (1.35, 1.35, 0.35)
        asignar_material(capitel, mat_piedra)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.65, 0, 5.0))
    dintel_izq = bpy.context.active_object
    dintel_izq.scale = (3.4, 1.1, 0.55)
    asignar_material(dintel_izq, mat_piedra)
    aplicar_uv_caja(dintel_izq, 2.0, 0.5)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.6, 0.4, 0.35))
    sillar_caido = bpy.context.active_object
    sillar_caido.scale = (0.9, 0.7, 0.6)
    sillar_caido.rotation_euler = (math.radians(15), math.radians(-12), math.radians(28))
    asignar_material(sillar_caido, mat_piedra)

    for sign in [-1, 1]:
        px = sign * sep_x
        for i, ang in enumerate([0.4, 2.0, 3.6, 5.0]):
            rx = px + math.cos(ang) * 0.58
            ry = math.sin(ang) * 0.58
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.11, depth=3.0, location=(rx, ry, 2.0))
            raiz = bpy.context.active_object
            raiz.rotation_euler = (math.sin(ang) * 0.25, -sign * math.cos(ang) * 0.25, math.radians(12))
            asignar_material(raiz, mat_raiz)

    espirales_pos = [
        (-sep_x, -0.54, 1.2), (-sep_x, -0.54, 2.2), (-sep_x, -0.54, 3.4), (-sep_x, -0.54, 4.4),
        (sep_x, -0.54, 1.4), (sep_x, -0.54, 2.5), (sep_x, -0.54, 3.7),
        (-sep_x, 0.54, 2.0), (sep_x, 0.54, 2.8)
    ]
    for ex, ey, ez in espirales_pos:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.15, minor_radius=0.035, major_segments=12, minor_segments=6, location=(ex, ey, ez))
        esp = bpy.context.active_object
        esp.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(esp, mat_espiral)

    exportar_modelo("arco_ruinas", DIR_ENTORNO)

def generar_altar_corteza():
    """Genera el Santuario de Corteza de Gruta de las Raíces completo en 360°:
    Tocón colosal del Primer Árbol con contrafuertes y corteza profunda, estrado ritual superior
    con anillos de crecimiento, el Escudo de Corteza reposando en el centro con incandescencia ambarina,
    y racimos de setas y líquenes luminosos de caverna."""
    limpiar_escena()
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_corteza = obtener_material_textura("Mat_AltarCorteza_Tronco", tex_troncos, rugosidad=0.90)
    mat_escudo = get_mat("cuero_mochila")
    mat_ambar = obtener_material("Mat_AltarCorteza_Ambar", "#DF9022", roughness=0.15, emission_hex="#FFB300", emission_strength=3.5)
    mat_seta = obtener_material("Mat_AltarCorteza_Seta", "#50F8E0", roughness=0.3, emission_hex="#40D8C8", emission_strength=2.5)

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.45, depth=1.8, location=(0, 0, 0.9))
    tocon = bpy.context.active_object
    asignar_material(tocon, mat_corteza)
    aplicar_uv_cilindro(tocon, 2.5, 1.5)

    for i in range(6):
        ang = i * (math.pi * 2.0 / 6.0)
        rx = math.cos(ang) * 1.55
        ry = math.sin(ang) * 1.55
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(rx, ry, 0.45))
        contra = bpy.context.active_object
        contra.scale = (0.45, 0.75, 0.9)
        contra.rotation_euler = (0, 0, ang)
        asignar_material(contra, mat_corteza)

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.25, depth=0.15, location=(0, 0, 1.82))
    estrado = bpy.context.active_object
    asignar_material(estrado, mat_corteza)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.15, 2.25))
    escudo = bpy.context.active_object
    escudo.scale = (0.75, 0.12, 1.15)
    escudo.rotation_euler = (math.radians(-18), 0, 0)
    asignar_material(escudo, mat_escudo)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.18, location=(0, -0.23, 2.25))
    gema = bpy.context.active_object
    gema.scale = (0.7, 0.4, 1.2)
    asignar_material(gema, mat_ambar)

    for ang, dist, sz in [(0.8, 1.5, 0.16), (2.2, 1.6, 0.14), (3.9, 1.45, 0.18), (5.1, 1.55, 0.15)]:
        sx = math.cos(ang) * dist
        sy = math.sin(ang) * dist
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.25, location=(sx, sy, 0.15))
        pie = bpy.context.active_object
        asignar_material(pie, mat_corteza)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=sz, location=(sx, sy, 0.30))
        sombrero = bpy.context.active_object
        sombrero.scale = (1.0, 1.0, 0.55)
        asignar_material(sombrero, mat_seta)

    exportar_modelo("altar_corteza", DIR_ENTORNO)

def generar_balsa():
    """Genera la Balsa de juncos de Kasia (Orilla de Juncos) completa en 360°:
    Plataforma de manojos de juncos y mimbre atados con soga trenzada, pontones laterales de flotación,
    pértiga de empuje de madera apoyada en la borda y nasa / cesta de pesca artesanal en la popa."""
    limpiar_escena()
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_juncos = obtener_material_textura("Mat_Balsa_Juncos", tex_paja, rugosidad=0.88)
    mat_viga = obtener_material_textura("Mat_Balsa_Madera", tex_troncos, rugosidad=0.85)
    mat_cuerda = get_mat("cuero_mochila")

    length, width, height = 4.0, 1.8, 0.35

    for i in range(7):
        cx = -width * 0.5 + 0.15 + i * (width - 0.3) / 6.0
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.12, depth=length, location=(cx, 0, 0.14))
        tronco = bpy.context.active_object
        tronco.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(tronco, mat_juncos)

    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.20, depth=length * 1.05, location=(sign * (width * 0.5 + 0.05), 0, 0.20))
        ponton = bpy.context.active_object
        ponton.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(ponton, mat_juncos)

    for ty in [-length * 0.35, 0.0, length * 0.35]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, ty, 0.28))
        trav = bpy.context.active_object
        trav.scale = (width + 0.35, 0.12, 0.08)
        asignar_material(trav, mat_viga)

        for sign in [-1, 1]:
            bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.035, major_segments=10, minor_segments=6, location=(sign * width * 0.45, ty, 0.28))
            atado = bpy.context.active_object
            asignar_material(atado, mat_cuerda)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.035, depth=3.2, location=(0.35, 0.1, 0.34))
    pertiga = bpy.context.active_object
    pertiga.rotation_euler = (math.radians(85), math.radians(6), 0)
    asignar_material(pertiga, mat_viga)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.28, depth=0.45, location=(-0.45, length * 0.4, 0.42))
    cesta = bpy.context.active_object
    asignar_material(cesta, mat_juncos)

    exportar_modelo("balsa", DIR_ENTORNO)

def generar_brasero():
    """Genera el Brasero Ancestral de fuego y calor (Sendero Olvidado) completo en 360°:
    Cuenco semiesférico de piedra labrada con espirales de los ecos, trípode de patas de hierro forjado
    con garras curvas, lecho de ascuas y brasas de Asili incandescentes, y cenizas/nieve en la base."""
    limpiar_escena()
    tex_marmol = os.path.join(DIR_SIGILIA, "marmol_sigilia_tile.png")
    mat_piedra = obtener_material_textura("Mat_Brasero_Piedra", tex_marmol, rugosidad=0.82)
    mat_hierro = get_mat("metal_forja")
    mat_brasas = obtener_material("Mat_Brasero_Fuego", "#DF9022", roughness=0.15, emission_hex="#FF6B00", emission_strength=4.0)
    mat_nieve = obtener_material("Mat_Brasero_Nieve", "#F1F5F9", roughness=0.75)

    # 1. Cuenco de piedra superior
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.75, depth=0.45, location=(0, 0, 0.95))
    cuenco = bpy.context.active_object
    asignar_material(cuenco, mat_piedra)
    aplicar_uv_cilindro(cuenco, 1.5, 1.0)

    # Moldura exterior del borde
    bpy.ops.mesh.primitive_torus_add(major_radius=0.78, minor_radius=0.06, major_segments=16, minor_segments=8, location=(0, 0, 1.15))
    borde = bpy.context.active_object
    asignar_material(borde, mat_hierro)

    # 2. Lecho de carbones y brasas incandescentes
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.65, depth=0.15, location=(0, 0, 1.12))
    carbon = bpy.context.active_object
    asignar_material(carbon, mat_brasas)

    for ang, dist in [(0.4, 0.35), (1.6, 0.45), (3.1, 0.38), (4.5, 0.42)]:
        px = math.cos(ang) * dist
        py = math.sin(ang) * dist
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.12, location=(px, py, 1.22))
        chispa = bpy.context.active_object
        asignar_material(chispa, mat_brasas)

    # 3. Trípode de 3 patas de hierro forjado
    for i in range(3):
        ang = i * (math.pi * 2.0 / 3.0)
        px = math.cos(ang) * 0.45
        py = math.sin(ang) * 0.45
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=1.05, location=(px, py, 0.48))
        pata = bpy.context.active_object
        pata.rotation_euler = (math.sin(ang) * 0.32, -math.cos(ang) * 0.32, 0)
        asignar_material(pata, mat_hierro)

        fx = math.cos(ang) * 0.72
        fy = math.sin(ang) * 0.72
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(fx, fy, 0.04))
        pie = bpy.context.active_object
        pie.scale = (0.16, 0.16, 0.08)
        asignar_material(pie, mat_hierro)

    # 4. Escarcha y nieve en la base
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.92, depth=0.06, location=(0, 0, 0.03))
    nieve = bpy.context.active_object
    asignar_material(nieve, mat_nieve)

    exportar_modelo("brasero", DIR_ENTORNO)

def generar_maquina_campo():
    """Genera la Máquina agrícola de vapor y trilla (Campo Segado) completa en 360°:
    Caldera cilíndrica de hierro remachado con chimenea vertical y caperuza de latón, tolva de grano
    con heno dorado, engranajes y poleas de transmisión de bronce, y grandes ruedas motrices de radios."""
    limpiar_escena()
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    mat_paja = obtener_material_textura("Mat_Maquina_Paja", tex_paja, rugosidad=0.88)
    mat_hierro = get_mat("metal_forja")
    mat_cobre = obtener_material("Mat_Maquina_Cobre", "#DF9022", roughness=0.35, metallic=0.75)
    mat_madera = get_mat("madera_viga")

    # 1. Chasis / bancada de vigas
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.45))
    chasis = bpy.context.active_object
    chasis.scale = (3.2, 1.8, 0.22)
    asignar_material(chasis, mat_madera)

    # 2. Caldera cilíndrica horizontal
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.65, depth=2.4, location=(-0.35, 0, 1.15))
    caldera = bpy.context.active_object
    caldera.rotation_euler = (0, math.radians(90), 0)
    asignar_material(caldera, mat_hierro)

    for zx in [-1.2, -0.35, 0.5]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.68, depth=0.08, location=(zx, 0, 1.15))
        zuncho = bpy.context.active_object
        zuncho.rotation_euler = (0, math.radians(90), 0)
        asignar_material(zuncho, mat_cobre)

    # 3. Chimenea de escape vertical
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.14, depth=1.4, location=(0.6, 0, 2.3))
    chimenea = bpy.context.active_object
    asignar_material(chimenea, mat_hierro)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.22, depth=0.15, location=(0.6, 0, 3.0))
    caperuza = bpy.context.active_object
    asignar_material(caperuza, mat_cobre)

    # 4. Tolva de alimentación de grano
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.1, 0, 1.35))
    tolva = bpy.context.active_object
    tolva.scale = (0.9, 1.4, 0.8)
    asignar_material(tolva, mat_madera)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.1, 0, 1.75))
    heno_tolva = bpy.context.active_object
    heno_tolva.scale = (0.75, 1.25, 0.2)
    asignar_material(heno_tolva, mat_paja)

    # 5. Ruedas motrices
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.65, depth=0.14, location=(-0.85, sign * 1.05, 0.65))
        rt = bpy.context.active_object
        rt.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(rt, mat_hierro)

        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.45, depth=0.12, location=(0.85, sign * 1.02, 0.45))
        rd = bpy.context.active_object
        rd.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(rd, mat_hierro)

    # 6. Volante de inercia
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.45, depth=0.08, location=(0.1, -0.72, 1.15))
    volante = bpy.context.active_object
    volante.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(volante, mat_cobre)

    exportar_modelo("maquina_campo", DIR_ENTORNO)

def generar_raiz_gigante():
    """Genera la Raíz Gigante Ancestral (El Kitovu) completa en 360°:
    Monumento natural de tronco fósil y raíces colosales curvadas que forman un arco sobre el terreno,
    nódulos de ámbar petrificado con brillo dorado de Asili y corteza arrugada con líquenes."""
    limpiar_escena()
    tex_troncos = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_raiz = obtener_material_textura("Mat_RaizGig_Madera", tex_troncos, rugosidad=0.88)
    mat_asili = obtener_material("Mat_RaizGig_Asili", "#DF9022", roughness=0.15, emission_hex="#FFB300", emission_strength=3.5)
    mat_musgo = obtener_material("Mat_RaizGig_Musgo", "#4A5D3E", roughness=0.92)

    puntos_arco = [
        (-2.8, -0.2, 0.5, 0.55),
        (-1.5, 0.1, 1.35, 0.62),
        (0.0, -0.1, 1.85, 0.68),
        (1.5, 0.15, 1.45, 0.60),
        (2.8, -0.2, 0.6, 0.52),
    ]
    for px, py, pz, r in puntos_arco:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=r, location=(px, py, pz))
        nodo = bpy.context.active_object
        asignar_material(nodo, mat_raiz)

    for i in range(len(puntos_arco) - 1):
        p1 = puntos_arco[i]
        p2 = puntos_arco[i + 1]
        mx = (p1[0] + p2[0]) * 0.5
        my = (p1[1] + p2[1]) * 0.5
        mz = (p1[2] + p2[2]) * 0.5
        dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        ang_y = math.atan2(dx, dz)
        ang_x = math.atan2(-dy, math.sqrt(dx * dx + dz * dz))

        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=(p1[3] + p2[3]) * 0.45, depth=dist, location=(mx, my, mz))
        seg = bpy.context.active_object
        seg.rotation_euler = (ang_x, ang_y, 0)
        asignar_material(seg, mat_raiz)

    for rx, ry in [(-2.2, 0.5), (0.2, -0.6), (2.1, 0.6)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.22, depth=1.6, location=(rx, ry, 0.6))
        sub_r = bpy.context.active_object
        sub_r.rotation_euler = (math.radians(20), math.radians(-15), 0)
        asignar_material(sub_r, mat_raiz)

    for ax, ay, az in [(-0.8, -0.4, 1.5), (0.8, -0.4, 1.6), (0.0, 0.45, 1.7)]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.24, location=(ax, ay, az))
        nodulo = bpy.context.active_object
        nodulo.scale = (1.2, 0.6, 0.8)
        asignar_material(nodulo, mat_asili)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.25))
    musgo = bpy.context.active_object
    musgo.scale = (2.4, 0.65, 0.12)
    asignar_material(musgo, mat_musgo)

    exportar_modelo("raiz_gigante", DIR_ENTORNO)

def generar_columna():
    """Genera la Columna Ancestral de Piedra de las Ruinas (25 ubicaciones):
    Plinto cuadrado escalonado, fuste cilíndrico estriado, collarino y capitel clásico
    con aristas desgastadas, textura de mármol/mampostería y líquenes de musgo."""
    limpiar_escena()
    tex_marmol = os.path.join(DIR_SIGILIA, "marmol_sigilia_tile.png")
    mat_piedra = obtener_material_textura("Mat_Columna_Piedra", tex_marmol, rugosidad=0.82)
    mat_musgo = obtener_material("Mat_Columna_Musgo", "#4A5D3E", roughness=0.90)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.08))
    plinto = bpy.context.active_object
    plinto.scale = (0.76, 0.76, 0.16)
    aplicar_uv_caja(plinto, 1.5, 0.5)
    asignar_material(plinto, mat_piedra)

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.34, depth=0.12, location=(0, 0, 0.22))
    toro = bpy.context.active_object
    aplicar_uv_caja(toro, 2.0, 0.5)
    asignar_material(toro, mat_piedra)

    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.26, depth=1.55, location=(0, 0, 1.05))
    fuste = bpy.context.active_object
    aplicar_uv_caja(fuste, 2.5, 3.0)
    asignar_material(fuste, mat_piedra)

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.32, depth=0.08, location=(0, 0, 1.86))
    astragalo = bpy.context.active_object
    aplicar_uv_caja(astragalo, 2.0, 0.4)
    asignar_material(astragalo, mat_piedra)

    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.36, depth=0.10, location=(0, 0, 1.95))
    equino = bpy.context.active_object
    aplicar_uv_caja(equino, 2.0, 0.5)
    asignar_material(equino, mat_piedra)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 2.08))
    abaco = bpy.context.active_object
    abaco.scale = (0.74, 0.74, 0.16)
    aplicar_uv_caja(abaco, 1.5, 0.5)
    asignar_material(abaco, mat_piedra)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.22, -0.22, 2.18))
    musgo_top = bpy.context.active_object
    musgo_top.scale = (0.32, 0.32, 0.05)
    asignar_material(musgo_top, mat_musgo)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.25, 0.25, 0.17))
    musgo_bot = bpy.context.active_object
    musgo_bot.scale = (0.28, 0.28, 0.04)
    asignar_material(musgo_bot, mat_musgo)

    exportar_modelo("columna", DIR_ENTORNO)

def generar_muro():
    """Genera el Muro de Cantería de las Ruinas (13 ubicaciones):
    Tramo macizo de mampostería sillar con zócalo, albardilla biselada superior
    y musgo en las juntas, 360° sólido sin aberturas."""
    limpiar_escena()
    tex_mamp = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    mat_mamp = obtener_material_textura("Mat_Muro_Piedra", tex_mamp, rugosidad=0.85)
    mat_musgo = obtener_material("Mat_Muro_Musgo", "#4A5D3E", roughness=0.90)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.36))
    cuerpo = bpy.context.active_object
    cuerpo.scale = (1.44, 0.44, 0.72)
    aplicar_uv_caja(cuerpo, 2.5, 1.8)
    asignar_material(cuerpo, mat_mamp)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.78))
    albardilla = bpy.context.active_object
    albardilla.scale = (1.52, 0.52, 0.12)
    aplicar_uv_caja(albardilla, 2.8, 0.8)
    asignar_material(albardilla, mat_mamp)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.06))
    zocalo = bpy.context.active_object
    zocalo.scale = (1.48, 0.48, 0.12)
    aplicar_uv_caja(zocalo, 2.6, 0.6)
    asignar_material(zocalo, mat_mamp)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.3, -0.23, 0.45))
    musgo1 = bpy.context.active_object
    musgo1.scale = (0.35, 0.04, 0.4)
    asignar_material(musgo1, mat_musgo)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.35, 0.05, 0.85))
    musgo2 = bpy.context.active_object
    musgo2.scale = (0.45, 0.38, 0.04)
    asignar_material(musgo2, mat_musgo)

    exportar_modelo("muro", DIR_ENTORNO)

def generar_paca():
    """Genera la Paca de Paja Tradicional (26 ubicaciones):
    Rollo cilíndrico de paja dorada con textura de paja trenzada, remates circulares
    en los extremos y dos anillas de cuerda de cáñamo oscuro."""
    limpiar_escena()
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")
    mat_paja = obtener_material_textura("Mat_Paca_Paja", tex_paja, rugosidad=0.88)
    mat_cuerda = obtener_material("Mat_Paca_Cuerda", "#5A3A22", roughness=0.75)

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.45, depth=0.85, location=(0, 0, 0.45))
    cilindro = bpy.context.active_object
    cilindro.rotation_euler = (math.radians(90), 0, 0)
    aplicar_uv_caja(cilindro, 2.2, 1.8)
    asignar_material(cilindro, mat_paja)

    for y_sign in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.43, depth=0.04, location=(0, y_sign * 0.44, 0.45))
        tapa = bpy.context.active_object
        tapa.rotation_euler = (math.radians(90), 0, 0)
        aplicar_uv_caja(tapa, 1.2, 1.2)
        asignar_material(tapa, mat_paja)

    for y_pos in [-0.22, 0.22]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.46, depth=0.03, location=(0, y_pos, 0.45))
        cuerda = bpy.context.active_object
        cuerda.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(cuerda, mat_cuerda)

    exportar_modelo("paca", DIR_ENTORNO)

def generar_molino_campo():
    """Genera el Molino de Viento de Campo Segado en 360°:
    Torre troncocónica de mampostería sillar, zócalo octogonal, portal rústico con dintel de madera,
    galería/balcón superior con barandilla perimetral, tejado cónico de paja dorada con buhardilla,
    eje de rotación frontal y 4 aspas gigantes con estructura de celosía de madera y velamen de lona."""
    limpiar_escena()
    tex_mamp = os.path.join(DIR_KITOVU, "mamposteria_tile.png")
    tex_madera = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    tex_paja = os.path.join(DIR_KITOVU, "tejado_paja_tile.png")

    mat_piedra = obtener_material_textura("Mat_MolCampo_Piedra", tex_mamp, rugosidad=0.82)
    mat_madera = obtener_material_textura("Mat_MolCampo_Madera", tex_madera, rugosidad=0.85)
    mat_paja = obtener_material_textura("Mat_MolCampo_Paja", tex_paja, rugosidad=0.88)
    mat_hierro = obtener_material("Mat_MolCampo_Hierro", "#2D3748", roughness=0.45, metallic=0.7)
    mat_lona = obtener_material("Mat_MolCampo_Lona", "#ECE0CA", roughness=0.78)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=2.2, depth=0.45, location=(0, 0, 0.225))
    zocalo = bpy.context.active_object
    aplicar_uv_caja(zocalo, 3.0, 0.8)
    asignar_material(zocalo, mat_piedra)

    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=1.95, radius2=1.45, depth=3.8, location=(0, 0, 2.35))
    torre = bpy.context.active_object
    aplicar_uv_caja(torre, 4.0, 3.5)
    asignar_material(torre, mat_piedra)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.95, 0.95))
    puerta = bpy.context.active_object
    puerta.scale = (0.75, 0.15, 1.45)
    aplicar_uv_caja(puerta, 1.0, 1.5)
    asignar_material(puerta, mat_madera)

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=1.75, depth=0.15, location=(0, 0, 4.28))
    plataforma = bpy.context.active_object
    aplicar_uv_caja(plataforma, 3.5, 0.5)
    asignar_material(plataforma, mat_madera)

    for ang_deg in range(0, 360, 30):
        rad = math.radians(ang_deg)
        bx = math.sin(rad) * 1.68
        by = math.cos(rad) * 1.68
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.035, depth=0.75, location=(bx, by, 4.7))
        poste = bpy.context.active_object
        asignar_material(poste, mat_madera)

    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=1.65, radius2=0.08, depth=2.2, location=(0, 0, 5.45))
    tejado = bpy.context.active_object
    aplicar_uv_caja(tejado, 3.5, 2.5)
    asignar_material(tejado, mat_paja)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.25, 5.2))
    buhardilla = bpy.context.active_object
    buhardilla.scale = (0.45, 0.45, 0.45)
    aplicar_uv_caja(buhardilla, 1.0, 1.0)
    asignar_material(buhardilla, mat_madera)

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.22, depth=0.65, location=(0, -1.55, 5.45))
    eje = bpy.context.active_object
    eje.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(eje, mat_hierro)

    longitud_aspa = 2.85
    for ang in [0, 90, 180, 270]:
        rad = math.radians(ang)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        cx = sin_a * (longitud_aspa * 0.5)
        cz = 5.45 + cos_a * (longitud_aspa * 0.5)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, -1.88, cz))
        brazo = bpy.context.active_object
        brazo.scale = (0.08, 0.08, longitud_aspa)
        brazo.rotation_euler = (0, -rad, 0)
        asignar_material(brazo, mat_madera)

        lx = sin_a * (longitud_aspa * 0.65)
        lz = 5.45 + cos_a * (longitud_aspa * 0.65)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lx, -1.90, lz))
        tela = bpy.context.active_object
        tela.scale = (0.42, 0.02, longitud_aspa * 0.60)
        tela.rotation_euler = (0, -rad, 0)
        asignar_material(tela, mat_lona)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=3.6, location=(0, 1.25, 3.6))
    timon = bpy.context.active_object
    timon.rotation_euler = (math.radians(35), 0, 0)
    asignar_material(timon, mat_madera)

    exportar_modelo("molino_campo", DIR_ENTORNO)

def generar_atril():
    """Genera el Atril Monumental de la Gran Biblioteca de Sigilia (Estanterías Colgantes):
    Pedestal escalonado de mármol, fuste torneado con collarines de bronce, pupitre inclinado,
    tomo ancestral abierto con sigilos de tinta luminosa índigo y candil de lectura."""
    limpiar_escena()
    tex_marmol = os.path.join(DIR_SIGILIA, "marmol_sigilia_tile.png")
    tex_bronce = os.path.join(DIR_SIGILIA, "bronce_sigilia_tile.png")
    tex_madera = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")

    mat_marmol = obtener_material_textura("Mat_Atril_Marmol", tex_marmol, rugosidad=0.75)
    mat_bronce = obtener_material_textura("Mat_Atril_Bronce", tex_bronce, rugosidad=0.35, metalicidad=0.85)
    mat_nogal = obtener_material_textura("Mat_Atril_Nogal", tex_madera, rugosidad=0.65)
    mat_paginas = obtener_material("Mat_Atril_Paginas", "#FAF5EA", roughness=0.85)
    mat_runas = obtener_material("Mat_Atril_Runas", "#312E81", roughness=0.3, emission_hex="#4F46E5", emission_strength=2.8)
    mat_farol = obtener_material("Mat_Atril_Farol", "#FEF08A", roughness=0.2, emission_hex="#FDE047", emission_strength=3.5)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.08))
    base1 = bpy.context.active_object
    base1.scale = (1.25, 0.95, 0.16)
    aplicar_uv_caja(base1, 1.5, 1.0)
    asignar_material(base1, mat_marmol)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.20))
    base2 = bpy.context.active_object
    base2.scale = (1.05, 0.78, 0.12)
    aplicar_uv_caja(base2, 1.2, 0.8)
    asignar_material(base2, mat_marmol)

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.22, depth=0.82, location=(0, 0, 0.65))
    fuste = bpy.context.active_object
    aplicar_uv_caja(fuste, 1.5, 2.0)
    asignar_material(fuste, mat_nogal)

    for z_col in [0.26, 1.04]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.26, depth=0.06, location=(0, 0, z_col))
        col = bpy.context.active_object
        asignar_material(col, mat_bronce)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.05, 1.22))
    mesa = bpy.context.active_object
    mesa.scale = (1.18, 0.74, 0.08)
    mesa.rotation_euler = (math.radians(-22), 0, 0)
    aplicar_uv_caja(mesa, 1.8, 1.2)
    asignar_material(mesa, mat_nogal)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.38, 1.06))
    tope = bpy.context.active_object
    tope.scale = (1.18, 0.06, 0.06)
    tope.rotation_euler = (math.radians(-22), 0, 0)
    asignar_material(tope, mat_bronce)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.24, -0.05, 1.28))
    pag_izq = bpy.context.active_object
    pag_izq.scale = (0.42, 0.52, 0.035)
    pag_izq.rotation_euler = (math.radians(-22), math.radians(6), 0)
    asignar_material(pag_izq, mat_paginas)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.24, -0.05, 1.28))
    pag_der = bpy.context.active_object
    pag_der.scale = (0.42, 0.52, 0.035)
    pag_der.rotation_euler = (math.radians(-22), math.radians(-6), 0)
    asignar_material(pag_der, mat_paginas)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.06, location=(0, -0.05, 1.30))
    runa = bpy.context.active_object
    asignar_material(runa, mat_runas)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.025, depth=0.45, location=(0.52, 0.15, 1.45))
    brazo = bpy.context.active_object
    brazo.rotation_euler = (math.radians(-15), math.radians(20), 0)
    asignar_material(brazo, mat_bronce)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.06, depth=0.12, location=(0.46, -0.05, 1.62))
    linterna = bpy.context.active_object
    asignar_material(linterna, mat_farol)

    exportar_modelo("atril_biblioteca", DIR_ENTORNO)

def generar_tocon_bosque():
    """Genera el Tocón Sagrado del Bosque Cobrizo:
    Base con raíces contrafuerte ramificadas, corteza rojiza rugosa, superficie con anillos
    de crecimiento anuales, hongos yesqueros de repisa y musgo verde."""
    limpiar_escena()
    tex_madera = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_corteza = obtener_material_textura("Mat_Tocon_Corteza", tex_madera, rugosidad=0.88)
    mat_anillos = obtener_material("Mat_Tocon_Anillos", "#905C45", roughness=0.72)
    mat_hongo1 = obtener_material("Mat_Tocon_Hongo1", "#D97706", roughness=0.65)
    mat_hongo2 = obtener_material("Mat_Tocon_Hongo2", "#B45309", roughness=0.70)
    mat_musgo = obtener_material("Mat_Tocon_Musgo", "#4A5D3E", roughness=0.90)

    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.68, radius2=0.52, depth=0.72, location=(0, 0, 0.36))
    cuerpo = bpy.context.active_object
    aplicar_uv_caja(cuerpo, 2.5, 1.8)
    asignar_material(cuerpo, mat_corteza)

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.50, depth=0.04, location=(0, 0, 0.72))
    anillos = bpy.context.active_object
    asignar_material(anillos, mat_anillos)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.15, depth=0.06, location=(0.04, -0.02, 0.73))
    hueco = bpy.context.active_object
    asignar_material(hueco, mat_corteza)

    for ang, lx, ly in [(35, 0.55, 0.42), (120, -0.62, 0.35), (215, -0.45, -0.58), (305, 0.52, -0.48)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.16, depth=0.55, location=(lx, ly, 0.20))
        raiz = bpy.context.active_object
        raiz.rotation_euler = (math.radians(25), math.radians(ang), 0)
        asignar_material(raiz, mat_corteza)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.18, depth=0.03, location=(0.48, 0.12, 0.46))
    hongo1 = bpy.context.active_object
    hongo1.scale = (1.0, 0.6, 1.0)
    hongo1.rotation_euler = (math.radians(10), math.radians(-15), 0)
    asignar_material(hongo1, mat_hongo1)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.14, depth=0.025, location=(0.44, 0.24, 0.35))
    hongo2 = bpy.context.active_object
    hongo2.scale = (1.0, 0.55, 1.0)
    hongo2.rotation_euler = (math.radians(8), math.radians(-20), 0)
    asignar_material(hongo2, mat_hongo2)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.25, 0.38, 0.15))
    musgo = bpy.context.active_object
    musgo.scale = (0.35, 0.28, 0.08)
    asignar_material(musgo, mat_musgo)

    exportar_modelo("tocon_bosque", DIR_ENTORNO)

def generar_poste_amarre():
    """Genera el Poste de Amarre Portuario de Embarcadero Junco:
    Conjunto de 3 postes de madera náutica tratada a diferentes alturas,
    caperuza de hierro protectora, triple vuelta de cabo grueso y argolla de bronce."""
    limpiar_escena()
    tex_madera = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_poste = obtener_material_textura("Mat_Poste_Madera", tex_madera, rugosidad=0.85)
    mat_cuerda = obtener_material("Mat_Poste_Cuerda", "#705425", roughness=0.88)
    mat_bronce = obtener_material("Mat_Poste_Bronce", "#C28522", roughness=0.35, metallic=0.8)
    mat_hierro = obtener_material("Mat_Poste_Hierro", "#374151", roughness=0.55, metallic=0.6)

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.20, depth=1.45, location=(0, 0, 0.725))
    poste_c = bpy.context.active_object
    aplicar_uv_caja(poste_c, 1.8, 3.0)
    asignar_material(poste_c, mat_poste)

    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.21, radius2=0.12, depth=0.08, location=(0, 0, 1.49))
    tapa_c = bpy.context.active_object
    asignar_material(tapa_c, mat_hierro)

    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.16, depth=1.18, location=(-0.24, -0.06, 0.59))
    poste_izq = bpy.context.active_object
    poste_izq.rotation_euler = (0, math.radians(-4), 0)
    aplicar_uv_caja(poste_izq, 1.5, 2.5)
    asignar_material(poste_izq, mat_poste)

    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.17, depth=1.02, location=(0.22, 0.08, 0.51))
    poste_der = bpy.context.active_object
    poste_der.rotation_euler = (math.radians(3), math.radians(5), 0)
    aplicar_uv_caja(poste_der, 1.5, 2.2)
    asignar_material(poste_der, mat_poste)

    for z_cuerda in [0.45, 0.65, 0.85]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.38, depth=0.06, location=(0, 0, z_cuerda))
        cuerda = bpy.context.active_object
        cuerda.scale = (1.05, 0.85, 1.0)
        asignar_material(cuerda, mat_cuerda)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.035, location=(0, -0.22, 1.15))
    argolla = bpy.context.active_object
    argolla.rotation_euler = (math.radians(35), 0, 0)
    asignar_material(argolla, mat_bronce)

    exportar_modelo("poste_amarre", DIR_ENTORNO)


def generar_arbol_seco():
    """Genera el Árbol Seco / Petrificado (Kitovu, Campo Segado, Senda de los Surcos, Paso de Piedra):
    Árbol milenario gnarled con raíces tabulares expuestas, tronco retorcido con fisura abierta,
    4 ramas principales desnudas en abanico y ramaje estéril en puntas resecas."""
    limpiar_escena()
    tex_tronco = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_corteza = obtener_material_textura("Mat_ArbolSeco_Corteza", tex_tronco, rugosidad=0.92)
    mat_madera_seca = obtener_material("Mat_ArbolSeco_Seca", "#4A3525", roughness=0.94)
    mat_ramitas = obtener_material("Mat_ArbolSeco_Puntas", "#735741", roughness=0.88)
    mat_falla = obtener_material("Mat_ArbolSeco_Falla", "#261A12", roughness=0.96)

    # 1. Raíces tabulares en trípode clavadas en el sustrato
    angulos_raices = [0.0, 2.1, 4.2]
    longitudes_raices = [0.75, 0.68, 0.72]
    for ang, l_raiz in zip(angulos_raices, longitudes_raices):
        rx = math.cos(ang) * (l_raiz * 0.45)
        ry = math.sin(ang) * (l_raiz * 0.45)
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.14, depth=l_raiz, location=(rx, ry, 0.12))
        raiz = bpy.context.active_object
        raiz.rotation_euler = (math.sin(ang) * 0.65, -math.cos(ang) * 0.65, ang)
        raiz.scale = (0.7, 1.2, 0.5)
        aplicar_uv_caja(raiz, 1.2, 1.5)
        asignar_material(raiz, mat_corteza)

    # 2. Base del tronco con ensanchamiento y fisura
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.25, depth=0.95, location=(0, 0, 0.48))
    tronco_base = bpy.context.active_object
    tronco_base.rotation_euler = (math.radians(2), math.radians(-3), 0)
    aplicar_uv_caja(tronco_base, 1.6, 2.5)
    asignar_material(tronco_base, mat_corteza)

    # Fisura oscura central
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.04, -0.12, 0.55))
    fisura = bpy.context.active_object
    fisura.scale = (0.08, 0.15, 0.55)
    fisura.rotation_euler = (0, math.radians(5), math.radians(12))
    asignar_material(fisura, mat_falla)

    # 3. Bifurcación del tronco (dos brazos principales retorcidos)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.17, depth=1.10, location=(0.14, 0.02, 1.35))
    brazo_a = bpy.context.active_object
    brazo_a.rotation_euler = (math.radians(-5), math.radians(18), math.radians(10))
    aplicar_uv_caja(brazo_a, 1.4, 2.2)
    asignar_material(brazo_a, mat_corteza)

    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.14, depth=0.95, location=(-0.16, -0.04, 1.25))
    brazo_b = bpy.context.active_object
    brazo_b.rotation_euler = (math.radians(6), math.radians(-22), math.radians(-15))
    aplicar_uv_caja(brazo_b, 1.3, 2.0)
    asignar_material(brazo_b, mat_madera_seca)

    # 4. Ramas desnudas superiores retorcidas (4 ramas principales)
    ramas = [
        ((0.36, 0.08, 2.05), (math.radians(-12), math.radians(34), math.radians(15)), 0.09, 0.85, mat_madera_seca),
        ((0.18, -0.16, 2.15), (math.radians(-30), math.radians(12), math.radians(-25)), 0.075, 0.78, mat_ramitas),
        ((-0.34, 0.06, 1.95), (math.radians(15), math.radians(-38), math.radians(-10)), 0.08, 0.82, mat_madera_seca),
        ((-0.18, -0.18, 1.85), (math.radians(-28), math.radians(-16), math.radians(35)), 0.07, 0.65, mat_ramitas),
    ]
    for loc, rot, rad, largo, mat in ramas:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=rad, depth=largo, location=loc)
        rama = bpy.context.active_object
        rama.rotation_euler = rot
        aplicar_uv_caja(rama, 1.0, 1.8)
        asignar_material(rama, mat)

    # 5. Ramillas terminales resecas (puntas angulosas)
    puntas = [
        ((0.55, 0.18, 2.50), (math.radians(20), math.radians(45), 0), 0.04, 0.45),
        ((0.38, 0.22, 2.40), (math.radians(-25), math.radians(25), 0), 0.035, 0.38),
        ((-0.52, 0.12, 2.42), (math.radians(22), math.radians(-42), 0), 0.04, 0.42),
        ((-0.40, -0.10, 2.30), (math.radians(-35), math.radians(-30), 0), 0.035, 0.35),
        ((0.05, -0.28, 2.15), (math.radians(-45), math.radians(5), 0), 0.035, 0.36),
    ]
    for loc, rot, rad, largo in puntas:
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=rad, depth=largo, location=loc)
        punta = bpy.context.active_object
        punta.rotation_euler = rot
        asignar_material(punta, mat_ramitas)

    exportar_modelo("arbol_seco", DIR_ENTORNO)


def generar_piedra_eco():
    """Genera la Piedra del Eco / Piedra del Recuerdo (9 Ecos Perdidos, 9 Piedras de las Ruinas):
    Monolito ancestral esculpido en granito meteorizado con plinto escalonado, facetas achaflanadas,
    hendidura en espiral rúnica en ambas caras y núcleo de cristal Asili con emisión bioluminiscente."""
    limpiar_escena()
    tex_ruina = os.path.join(DIR_ALDEA, "ruina_mamposteria_tile.png")
    mat_piedra = obtener_material_textura("Mat_Eco_Piedra", tex_ruina, rugosidad=0.85)
    mat_plinto = obtener_material("Mat_Eco_Plinto", "#373A3E", roughness=0.82)
    mat_runa_asili = obtener_material("Mat_Eco_Runa", "#6DB0B0", roughness=0.2, emission_hex="#6DB0B0", emission_strength=4.5)
    mat_nucleo_luz = obtener_material("Mat_Eco_Luz", "#D8F0EC", roughness=0.1, emission_hex="#D8F0EC", emission_strength=6.0)

    # 1. Plinto basal escalonado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.08))
    plinto_inf = bpy.context.active_object
    plinto_inf.scale = (0.94, 0.72, 0.16)
    aplicar_uv_caja(plinto_inf, 1.8, 1.5)
    asignar_material(plinto_inf, mat_plinto)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.22))
    plinto_sup = bpy.context.active_object
    plinto_sup.scale = (0.76, 0.54, 0.12)
    aplicar_uv_caja(plinto_sup, 1.5, 1.2)
    asignar_material(plinto_sup, mat_plinto)

    # 2. Fuste del monolito (obelisco ahusado de 8 facetas)
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.34, depth=1.85, location=(0, 0, 1.18))
    fuste = bpy.context.active_object
    fuste.scale = (1.1, 0.75, 1.0)
    aplicar_uv_caja(fuste, 1.5, 3.2)
    asignar_material(fuste, mat_piedra)

    # Remate superior piramidal achaflanado
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.32, radius2=0.06, depth=0.30, location=(0, 0, 2.22))
    capitel = bpy.context.active_object
    capitel.scale = (1.05, 0.72, 1.0)
    asignar_material(capitel, mat_piedra)

    # 3. Espiral rúnica Asili tallada en la cara frontal y posterior
    for cara_y, rot_y_sign in [(-0.19, 1.0), (0.19, -1.0)]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.18, minor_radius=0.024, location=(0, cara_y, 1.35))
        anillo_ext = bpy.context.active_object
        anillo_ext.rotation_euler = (math.radians(90), 0, 0)
        anillo_ext.scale = (1.0, 1.15, 0.6)
        asignar_material(anillo_ext, mat_runa_asili)

        bpy.ops.mesh.primitive_torus_add(major_radius=0.09, minor_radius=0.020, location=(0.02 * rot_y_sign, cara_y, 1.37))
        anillo_int = bpy.context.active_object
        anillo_int.rotation_euler = (math.radians(90), 0, 0)
        anillo_int.scale = (0.9, 1.1, 0.6)
        asignar_material(anillo_int, mat_runa_asili)

        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.048, location=(0.01 * rot_y_sign, cara_y + (0.01 * rot_y_sign), 1.36))
        nucleo = bpy.context.active_object
        asignar_material(nucleo, mat_nucleo_luz)

    # 4. Cuñas de refuerzo geológico al pie
    for bx, by, brad in [(-0.35, -0.22, 0.12), (0.33, 0.20, 0.14), (-0.32, 0.24, 0.10)]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=brad, location=(bx, by, 0.18))
        bloquecito = bpy.context.active_object
        bloquecito.scale = (1.0, 0.9, 0.6)
        asignar_material(bloquecito, mat_plinto)

    exportar_modelo("piedra_eco", DIR_ENTORNO)


def generar_bloque_piedra():
    """Genera el Bloque Megalítico de Piedra Tallada (Cañada del Eco y Paso de Piedra):
    Estructura de grandes sillares ciclópeos escalonados con aristas desgastadas,
    estratificación geológica tallada y líquenes alpinos en grietas."""
    limpiar_escena()
    tex_mamposteria = os.path.join(DIR_ALDEA, "ruina_mamposteria_tile.png")
    mat_bloque = obtener_material_textura("Mat_Bloque_Piedra", tex_mamposteria, rugosidad=0.88)
    mat_piedra_corte = obtener_material("Mat_Bloque_Corte", "#5A524A", roughness=0.85)
    mat_musgo = obtener_material("Mat_Bloque_Musgo", "#4E583E", roughness=0.95)
    mat_sombra = obtener_material("Mat_Bloque_Sombra", "#332C26", roughness=0.92)

    # 1. Bloque basal mayor (asiento de cimentación ciclópeo)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.28))
    base = bpy.context.active_object
    base.scale = (1.65, 1.05, 0.56)
    aplicar_uv_caja(base, 2.2, 1.5)
    asignar_material(base, mat_bloque)

    # 2. Bloque intermedio escalonado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.08, 0.06, 0.78))
    bloque_mid = bpy.context.active_object
    bloque_mid.scale = (1.30, 0.88, 0.52)
    bloque_mid.rotation_euler = (0, 0, math.radians(2))
    aplicar_uv_caja(bloque_mid, 1.8, 1.4)
    asignar_material(bloque_mid, mat_bloque)

    # 3. Losa de coronación superior achaflanada
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.05, -0.04, 1.22))
    losa_sup = bpy.context.active_object
    losa_sup.scale = (0.95, 0.68, 0.38)
    losa_sup.rotation_euler = (math.radians(-2), math.radians(1), math.radians(-3))
    aplicar_uv_caja(losa_sup, 1.4, 1.2)
    asignar_material(losa_sup, mat_piedra_corte)

    # Capa de musgo/líquenes en la repisa superior
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.05, -0.04, 1.42))
    musgo_top = bpy.context.active_object
    musgo_top.scale = (0.88, 0.60, 0.04)
    asignar_material(musgo_top, mat_musgo)

    # 4. Piedras de contrafuerte y fracturas en la base
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.72, -0.15, 0.22))
    boulder_izq = bpy.context.active_object
    boulder_izq.scale = (0.42, 0.38, 0.44)
    boulder_izq.rotation_euler = (math.radians(10), math.radians(-8), math.radians(25))
    asignar_material(boulder_izq, mat_bloque)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.68, 0.22, 0.18))
    boulder_der = bpy.context.active_object
    boulder_der.scale = (0.36, 0.32, 0.36)
    boulder_der.rotation_euler = (math.radians(-12), math.radians(15), math.radians(-20))
    asignar_material(boulder_der, mat_bloque)

    # Hendidura horizontal de cantería
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -0.48, 0.54))
    grieta = bpy.context.active_object
    grieta.scale = (1.50, 0.08, 0.06)
    asignar_material(grieta, mat_sombra)

    exportar_modelo("bloque_piedra", DIR_ENTORNO)


def generar_transbordador():
    """Genera el Gran Transbordador Fluvial de Bata (Embarcadero Junco y La Travesía):
    Gran barcaza fluvial con casco de madera curvado, costillaje y cuadernas interiores,
    cubierta de tablones estancos, bordas reforzadas con norays de amarre, timón de popa con caña,
    y estolón de proa con farol de navegación de bronce y ámbar cálido."""
    limpiar_escena()
    tex_madera = os.path.join(DIR_KITOVU, "pared_troncos_tile.png")
    mat_casco = obtener_material_textura("Mat_Barge_Casco", tex_madera, rugosidad=0.85)
    mat_cubierta = obtener_material("Mat_Barge_Cubierta", "#8B6245", roughness=0.82)
    mat_tablones = obtener_material("Mat_Barge_Tablones", "#5E3D2B", roughness=0.86)
    mat_bronce = obtener_material("Mat_Barge_Bronce", "#C28522", roughness=0.35, metallic=0.7)
    mat_farol_luz = obtener_material("Mat_Barge_Luz", "#FFAA44", roughness=0.1, emission_hex="#FFAA44", emission_strength=4.0)
    mat_hierro = obtener_material("Mat_Barge_Hierro", "#374151", roughness=0.6, metallic=0.6)
    mat_juncos = obtener_material("Mat_Barge_Juncos", "#B3A469", roughness=0.92)

    # 1. Fondo plano del casco de la barcaza
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.06))
    fondo = bpy.context.active_object
    fondo.scale = (7.60, 2.80, 0.14)
    aplicar_uv_caja(fondo, 8.0, 3.0)
    asignar_material(fondo, mat_casco)

    # 2. Rampa / roda de proa (inclinada hacia adelante)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-4.15, 0, 0.28))
    proa = bpy.context.active_object
    proa.scale = (1.20, 2.80, 0.14)
    proa.rotation_euler = (0, math.radians(-24), 0)
    aplicar_uv_caja(proa, 2.0, 3.0)
    asignar_material(proa, mat_casco)

    # 3. Espejo de popa (inclinado hacia atrás)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(4.15, 0, 0.28))
    popa = bpy.context.active_object
    popa.scale = (1.20, 2.80, 0.14)
    popa.rotation_euler = (0, math.radians(24), 0)
    aplicar_uv_caja(popa, 2.0, 3.0)
    asignar_material(popa, mat_casco)

    # 4. Bordas laterales (babor y estribor)
    for y_borda, sign_y in [(1.42, 1), (-1.42, -1)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y_borda, 0.42))
        borda = bpy.context.active_object
        borda.scale = (7.80, 0.18, 0.88)
        aplicar_uv_caja(borda, 8.0, 1.5)
        asignar_material(borda, mat_casco)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, y_borda, 0.88))
        regala = bpy.context.active_object
        regala.scale = (8.20, 0.26, 0.10)
        asignar_material(regala, mat_tablones)

    # 5. Cubierta plana de tablones transitables
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.30))
    deck = bpy.context.active_object
    deck.scale = (7.30, 2.60, 0.10)
    aplicar_uv_caja(deck, 6.0, 3.0)
    asignar_material(deck, mat_cubierta)

    for x_t in range(-6, 7):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_t * 0.55, 0, 0.355))
        liston = bpy.context.active_object
        liston.scale = (0.04, 2.56, 0.02)
        asignar_material(liston, mat_tablones)

    # 6. Cuadernas / costillas de refuerzo en las bordas interiores
    for x_c in [-2.5, -1.25, 0.0, 1.25, 2.5]:
        for y_c in [1.32, -1.32]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x_c, y_c, 0.55))
            cuaderna = bpy.context.active_object
            cuaderna.scale = (0.16, 0.12, 0.58)
            asignar_material(cuaderna, mat_tablones)

    # 7. Norays / bitas de amarre de madera en proa y popa
    for bx, by in [(-3.6, 1.22), (-3.6, -1.22), (3.6, 1.22), (3.6, -1.22)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.10, depth=0.45, location=(bx, by, 0.95))
        bita = bpy.context.active_object
        asignar_material(bita, mat_tablones)
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.03, depth=0.32, location=(bx, by, 1.08))
        perno = bpy.context.active_object
        perno.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(perno, mat_hierro)

    # 8. Mástil de proa con farol de navegación de bronce y ámbar
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07, depth=1.55, location=(-4.30, -0.90, 0.95))
    mastil = bpy.context.active_object
    asignar_material(mastil, mat_tablones)

    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=0.55, location=(-4.15, -0.90, 1.62))
    percha = bpy.context.active_object
    percha.rotation_euler = (0, math.radians(90), 0)
    asignar_material(percha, mat_tablones)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.12, depth=0.28, location=(-3.90, -0.90, 1.48))
    farol_jaula = bpy.context.active_object
    asignar_material(farol_jaula, mat_bronce)

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.075, location=(-3.90, -0.90, 1.48))
    farol_nucleo = bpy.context.active_object
    asignar_material(farol_nucleo, mat_farol_luz)

    # 9. Timón y caña en popa
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=1.10, location=(4.65, 0, 0.45))
    eje_timon = bpy.context.active_object
    asignar_material(eje_timon, mat_hierro)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(4.95, 0, 0.20))
    pala_timon = bpy.context.active_object
    pala_timon.scale = (0.55, 0.08, 0.85)
    asignar_material(pala_timon, mat_tablones)

    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.045, depth=1.15, location=(4.15, 0, 0.95))
    cana = bpy.context.active_object
    cana.rotation_euler = (0, math.radians(75), 0)
    asignar_material(cana, mat_tablones)

    # 10. Reparación de juncos tejidos en el boquete
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-1.80, -1.45, 0.40))
    parche_juncos = bpy.context.active_object
    parche_juncos.scale = (1.40, 0.16, 0.55)
    asignar_material(parche_juncos, mat_juncos)

    exportar_modelo("transbordador", DIR_ENTORNO)

# ---------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("GENERADOR 3D MAISHA - BLENDER HEADLESS PIPELINE")
    print(f"Blender Version: {bpy.app.version_string}")
    print("=" * 60)
    
    print("\n[1/4] Generando Personajes...")
    generar_maisha()
    generar_pino()
    generar_mzee_shamba()
    generar_corteza()
    
    print("\n[2/4] Generando Enemigos y Corrupción...")
    generar_petrino_giza()
    generar_mzizi_raiz()
    generar_babosa_oxido()
    generar_corazon_giza()
    
    print("\n[3/5] Generando Arquitectura de El Kitovu, Cuna de Musgo, Sigilia y Biomas...")
    generar_gran_arbol()
    generar_casa_granja_shamba()
    generar_casa_pino()
    generar_casa_pino_ruina()
    generar_forja_corteza()
    generar_forja_ruina()
    generar_cocina_juncia()
    generar_cocina_ruina()
    generar_puesto_tawi()
    generar_puesto_ruina()
    generar_kitovu_ruina()
    generar_molino_shamba()
    generar_puente_madera()
    generar_farol_madera()
    generar_gran_archivo_sigilia()
    generar_taller_taa()
    generar_casa_escriba()
    generar_fuente_plaza()
    generar_casa_juncos()
    generar_casa_bata()
    generar_casa_nungu()
    generar_granero()
    generar_palafito()
    generar_horreo()
    generar_campamento()
    generar_puesto_tinta()
    generar_almacen()
    generar_aprisco()
    generar_madriguera()
    generar_torre()
    generar_monumento()
    generar_altar()
    generar_grua()
    generar_barca()
    generar_estela()
    generar_menhir()
    generar_portal_raiz()
    generar_arco_ruinas()
    generar_altar_corteza()
    generar_balsa()
    generar_brasero()
    generar_maquina_campo()
    generar_raiz_gigante()
    generar_columna()
    generar_muro()
    generar_paca()
    generar_molino_campo()
    generar_atril()
    generar_tocon_bosque()
    generar_poste_amarre()
    generar_arbol_seco()
    generar_piedra_eco()
    generar_bloque_piedra()
    generar_transbordador()
    
    print("\n[4/5] Generando Módulos de Terreno y Props...")
    generar_pozo_antiguo()
    generar_espantapajaros()
    generar_carro_madera()
    generar_valla_madera()
    generar_bloque_hierba()
    generar_bloque_risco()
    generar_canal_agua()
    generar_bloque_camino()
    generar_semilla_explosiva()
    generar_cetro_raiz()
    
    print("\n" + "=" * 60)
    print("TODOS LOS MODELOS GENERADOS Y EXPORTADOS CON ÉXITO")
    print("=" * 60)

if __name__ == "__main__":
    main()
