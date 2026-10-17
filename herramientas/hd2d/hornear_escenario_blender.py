#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hornear_escenario_blender.py
Prueba piloto 5.8: Genera el modelo 3D de la Casa Seta de Pino en Blender 4.x
con geometría de baja poligonización y textura pixel art con la paleta de Raíz (filtro NEAREST).
Exporta el modelo .glb en modelos/entorno/casa_seta_piloto.glb.
"""
import bpy
import math
import os

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DIR_ENTORNO = os.path.join(RAIZ, "modelos", "entorno")
DIR_TEXTURAS = os.path.join(RAIZ, "modelos", "texturas")
os.makedirs(DIR_ENTORNO, exist_ok=True)
os.makedirs(DIR_TEXTURAS, exist_ok=True)

RUTA_TEX = os.path.join(DIR_TEXTURAS, "tex_casa_seta_raiz.png")

# 2. Modelado procedural en Blender 4.x
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
for mesh in list(bpy.data.meshes):
    bpy.data.meshes.remove(mesh)

# Material pixel art con textura y NEAREST
mat = bpy.data.materials.new(name="MatCasaSeta")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
bsdf = nodes.get("Principled BSDF")
bsdf.inputs["Roughness"].default_value = 0.95
bsdf.inputs["Specular IOR Level"].default_value = 0.05

tex_node = nodes.new("ShaderNodeTexImage")
tex_node.image = bpy.data.images.load(RUTA_TEX)
tex_node.interpolation = "Closest" # NEAREST
links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])

# Base cilíndrica de la casa
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.65, depth=1.8, location=(0, 0, 0.9))
pared = bpy.context.active_object
pared.name = "ParedCasa"
pared.data.materials.append(mat)

# Tejado cónico de seta
bpy.ops.mesh.primitive_cone_add(vertices=20, radius1=2.45, radius2=0.3, depth=1.6, location=(0, 0, 2.5))
techo = bpy.context.active_object
techo.name = "TejadoSeta"
techo.data.materials.append(mat)

# Chimenea y farol
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.28, depth=1.2, location=(0.95, 0.65, 2.8))
chimenea = bpy.context.active_object
chimenea.name = "Chimenea"
chimenea.data.materials.append(mat)

# Unir en una única malla optimizada
bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active = pared
bpy.ops.object.join()
casa_total = bpy.context.active_object
casa_total.name = "CasaSetaPiloto"

# Exportar GLB para Godot
ruta_glb = os.path.join(DIR_ENTORNO, "casa_seta_piloto.glb")
bpy.ops.export_scene.gltf(
    filepath=ruta_glb,
    export_format='GLB',
    use_selection=True,
    export_apply=True
)
print("EXPORTADO CORRECTAMENTE:", ruta_glb)
