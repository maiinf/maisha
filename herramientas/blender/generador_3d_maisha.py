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
DIR_PERSONAJES = os.path.join(BASE_DIR, "modelos", "personajes")
DIR_ENEMIGOS = os.path.join(BASE_DIR, "modelos", "enemigos")
DIR_ENTORNO = os.path.join(BASE_DIR, "modelos", "entorno")
DIR_OBJETOS = os.path.join(BASE_DIR, "modelos", "objetos")

for d in [DIR_PERSONAJES, DIR_ENEMIGOS, DIR_ENTORNO, DIR_OBJETOS]:
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
        "pino_seta_rojo": ("Mat_Pino_Seta", "#B91C1C", 0.4, 0.0, None, 0.0),
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
        "tela_toldo": ("Mat_Tela_Toldo", "#DC2626", 0.7, 0.0, None, 0.0)
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

def exportar_modelo(nombre_base, carpeta):
    """Exporta la escena actual a .glb y guarda copia .blend."""
    ruta_glb = os.path.join(carpeta, f"{nombre_base}.glb")
    ruta_blend = os.path.join(carpeta, f"{nombre_base}.blend")
    
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
    """Genera la Casa Seta de Pino con tejado carmesí y puerta circular."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=1.35, depth=1.6, location=(0, 0, 0.8))
    pared = bpy.context.active_object
    asignar_material(pared, get_mat("madera_tablas"))
    
    bpy.ops.mesh.primitive_cone_add(vertices=18, radius1=1.95, radius2=0.2, depth=1.2, location=(0, 0, 2.1))
    techo = bpy.context.active_object
    asignar_material(techo, get_mat("pino_seta_rojo"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.45, depth=0.15, location=(0, -1.35, 0.6))
    puerta = bpy.context.active_object
    puerta.rotation_euler = (math.radians(90), 0, 0)
    asignar_material(puerta, get_mat("arbol_corteza"))
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.14, location=(0.65, -1.45, 1.1))
    farol = bpy.context.active_object
    asignar_material(farol, get_mat("farol_luz"))

    exportar_modelo("casa_pino", DIR_ENTORNO)

def generar_forja_corteza():
    """Genera el taller de forja de Corteza: horno de piedra y yunque."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_cube_add(size=1.8, location=(0, 0, 0.9))
    horno = bpy.context.active_object
    horno.scale = (1.2, 1.0, 1.0)
    asignar_material(horno, get_mat("piedra_plaza"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.35, depth=1.4, location=(0.6, 0.3, 2.2))
    chimenea = bpy.context.active_object
    asignar_material(chimenea, get_mat("piedra_plaza"))
    
    bpy.ops.mesh.primitive_cube_add(size=0.6, location=(0, -0.85, 0.6))
    fuego = bpy.context.active_object
    asignar_material(fuego, get_mat("corazon_asili"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.35, depth=0.5, location=(0, -1.6, 0.25))
    tocon = bpy.context.active_object
    asignar_material(tocon, get_mat("arbol_corteza"))
    
    bpy.ops.mesh.primitive_cube_add(size=0.35, location=(0, -1.6, 0.65))
    yunque = bpy.context.active_object
    yunque.scale = (1.4, 0.7, 0.6)
    asignar_material(yunque, get_mat("metal_forja"))

    exportar_modelo("forja_corteza", DIR_ENTORNO)

def generar_molino_shamba():
    """Genera la cabaña con rueda de molino de agua de Mzee Shamba."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_cube_add(size=2.2, location=(0, 0, 1.1))
    casa = bpy.context.active_object
    casa.scale = (1.2, 0.9, 1.0)
    asignar_material(casa, get_mat("madera_tablas"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=1.6, depth=2.8, location=(0, 0, 2.7))
    techo = bpy.context.active_object
    techo.rotation_euler = (0, math.radians(90), 0)
    techo.scale = (1.1, 0.9, 1.0)
    asignar_material(techo, get_mat("arbol_corteza"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.1, depth=0.32, location=(1.55, 0, 0.9))
    rueda = bpy.context.active_object
    rueda.rotation_euler = (0, math.radians(90), 0)
    asignar_material(rueda, get_mat("madera_tablas"))

    exportar_modelo("molino_shamba", DIR_ENTORNO)

def generar_puente_madera():
    """Genera el puente de madera rústico con barandilla."""
    limpiar_escena()
    
    for i in range(7):
        y_pos = (i - 3) * 0.45
        z_curve = math.cos((i - 3) * 0.3) * 0.12
        bpy.ops.mesh.primitive_cube_add(size=0.4, location=(0, y_pos, z_curve + 0.1))
        tablon = bpy.context.active_object
        tablon.scale = (3.2, 0.9, 0.18)
        asignar_material(tablon, get_mat("madera_tablas"))

    for sign in [-1, 1]:
        for i in [-3, 0, 3]:
            y_pos = i * 0.45
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.06, depth=0.75, location=(sign * 0.65, y_pos, 0.45))
            poste = bpy.context.active_object
            asignar_material(poste, get_mat("arbol_corteza"))
            
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05, depth=3.2, location=(sign * 0.65, 0, 0.8))
        pasamanos = bpy.context.active_object
        pasamanos.rotation_euler = (math.radians(90), 0, 0)
        asignar_material(pasamanos, get_mat("madera_tablas"))

    exportar_modelo("puente_madera", DIR_ENTORNO)

def generar_farol_madera():
    """Genera un farol de poste tallado con emisión de luz cálida."""
    limpiar_escena()
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=2.4, location=(0, 0, 1.2))
    poste = bpy.context.active_object
    asignar_material(poste, get_mat("arbol_corteza"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=0.75, location=(0.3, 0, 2.25))
    brazo = bpy.context.active_object
    brazo.rotation_euler = (0, math.radians(90), 0)
    asignar_material(brazo, get_mat("arbol_corteza"))
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.18, location=(0.6, 0, 2.05))
    farol = bpy.context.active_object
    asignar_material(farol, get_mat("farol_luz"))

    exportar_modelo("farol_madera", DIR_ENTORNO)

def generar_cocina_juncia():
    """Genera la cocina comunitaria de Juncia: cabaña con gran caldero exterior y chimenea."""
    limpiar_escena()
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.0))
    cuerpo = bpy.context.active_object
    cuerpo.scale = (1.2, 1.0, 1.0)
    asignar_material(cuerpo, get_mat("madera_tablas"))
    
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=1.8, radius2=0.2, depth=1.4, location=(0, 0, 2.7))
    techo = bpy.context.active_object
    asignar_material(techo, get_mat("musgo_hojas"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.25, depth=1.6, location=(0.8, 0.4, 2.8))
    chim = bpy.context.active_object
    asignar_material(chim, get_mat("piedra_plaza"))
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.45, location=(-0.6, -1.3, 0.4))
    caldero = bpy.context.active_object
    asignar_material(caldero, get_mat("metal_forja"))
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.22, location=(-0.6, -1.3, 0.15))
    fuego = bpy.context.active_object
    asignar_material(fuego, get_mat("corazon_asili"))

    exportar_modelo("cocina_juncia", DIR_ENTORNO)

def generar_puesto_tawi():
    """Genera el puesto de mercado de Tawi: mostrador con toldo de rayas y cestas."""
    limpiar_escena()
    bpy.ops.mesh.primitive_cube_add(size=1.2, location=(0, 0, 0.5))
    mesa = bpy.context.active_object
    mesa.scale = (1.8, 0.8, 0.8)
    asignar_material(mesa, get_mat("madera_tablas"))
    
    for sx in [-1.0, 1.0]:
        for sy in [-0.45, 0.45]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.04, depth=2.0, location=(sx * 0.95, sy, 1.0))
            poste = bpy.context.active_object
            asignar_material(poste, get_mat("arbol_corteza"))
            
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=1.3, depth=2.4, location=(0, 0, 2.1))
    toldo = bpy.context.active_object
    toldo.rotation_euler = (0, math.radians(90), 0)
    toldo.scale = (0.9, 0.35, 1.0)
    asignar_material(toldo, get_mat("tela_toldo"))
    
    bpy.ops.mesh.primitive_cube_add(size=0.35, location=(-0.5, 0.0, 1.05))
    caja1 = bpy.context.active_object
    asignar_material(caja1, get_mat("oro_reliquia"))

    exportar_modelo("puesto_tawi", DIR_ENTORNO)

def generar_gran_archivo_sigilia():
    """Genera el Gran Archivo de Maandiko (Sigilia): edificio monumental de piedra con columnas y cúpula."""
    limpiar_escena()
    bpy.ops.mesh.primitive_cube_add(size=3.6, location=(0, 0, 0.3))
    base = bpy.context.active_object
    base.scale = (1.4, 1.1, 0.18)
    asignar_material(base, get_mat("marmol_sigilia"))
    
    bpy.ops.mesh.primitive_cube_add(size=3.0, location=(0, 0.2, 1.7))
    cuerpo = bpy.context.active_object
    cuerpo.scale = (1.3, 0.9, 0.9)
    asignar_material(cuerpo, get_mat("marmol_sigilia"))
    
    for i in range(4):
        x_col = (i - 1.5) * 1.1
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.18, depth=2.4, location=(x_col, -1.2, 1.4))
        columna = bpy.context.active_object
        asignar_material(columna, get_mat("marmol_sigilia"))
        
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=1.6, depth=4.2, location=(0, -0.1, 3.4))
    techo = bpy.context.active_object
    techo.rotation_euler = (0, math.radians(90), 0)
    techo.scale = (1.0, 0.45, 1.0)
    asignar_material(techo, get_mat("teja_cobriza"))
    
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.9, location=(0, 0.4, 4.0))
    cupula = bpy.context.active_object
    asignar_material(cupula, get_mat("oro_reliquia"))

    exportar_modelo("gran_archivo", DIR_ENTORNO)

def generar_taller_taa():
    """Genera el taller de Taa (escriba de Maandiko): arquitectura urbana con frascos de tinta y vitrales."""
    limpiar_escena()
    bpy.ops.mesh.primitive_cube_add(size=2.4, location=(0, 0, 1.2))
    planta_baja = bpy.context.active_object
    planta_baja.scale = (1.1, 0.9, 1.0)
    asignar_material(planta_baja, get_mat("piedra_plaza"))
    
    bpy.ops.mesh.primitive_cube_add(size=2.2, location=(0, -0.15, 2.6))
    planta_alta = bpy.context.active_object
    planta_alta.scale = (1.2, 1.05, 0.8)
    asignar_material(planta_alta, get_mat("madera_tablas"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=1.5, depth=3.0, location=(0, -0.15, 3.7))
    techo = bpy.context.active_object
    techo.rotation_euler = (0, math.radians(90), 0)
    techo.scale = (1.1, 0.5, 1.0)
    asignar_material(techo, get_mat("teja_cobriza"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.32, depth=0.6, location=(1.1, -1.2, 0.35))
    frasco = bpy.context.active_object
    asignar_material(frasco, get_mat("tinta_sigilia"))

    exportar_modelo("taller_taa", DIR_ENTORNO)

def generar_casa_escriba():
    """Genera una casa tradicional de Sigilia (Maandiko): muros blancos, vigas y tejas cobrizas."""
    limpiar_escena()
    bpy.ops.mesh.primitive_cube_add(size=2.2, location=(0, 0, 1.1))
    casa = bpy.context.active_object
    casa.scale = (1.1, 1.0, 1.0)
    asignar_material(casa, get_mat("marmol_sigilia"))
    
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=1.4, depth=2.7, location=(0, 0, 2.6))
    techo = bpy.context.active_object
    techo.rotation_euler = (0, math.radians(90), 0)
    techo.scale = (1.05, 0.55, 1.0)
    asignar_material(techo, get_mat("teja_cobriza"))
    
    bpy.ops.mesh.primitive_cube_add(size=0.6, location=(0, -1.15, 1.6))
    balcon = bpy.context.active_object
    balcon.scale = (1.6, 0.4, 0.5)
    asignar_material(balcon, get_mat("madera_tablas"))

    exportar_modelo("casa_escriba", DIR_ENTORNO)

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
    
    print("\n[3/5] Generando Arquitectura de Cuna de Musgo y Sigilia...")
    generar_gran_arbol()
    generar_casa_pino()
    generar_forja_corteza()
    generar_molino_shamba()
    generar_puente_madera()
    generar_farol_madera()
    generar_cocina_juncia()
    generar_puesto_tawi()
    generar_gran_archivo_sigilia()
    generar_taller_taa()
    generar_casa_escriba()
    
    print("\n[4/5] Generando Módulos de Terreno y Props...")
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
