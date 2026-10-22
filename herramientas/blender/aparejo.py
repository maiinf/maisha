# -*- coding: utf-8 -*-
"""
Aparejo común para los personajes 3D de Maisha (Blender 5.2): materiales, malla base de Blender Studio,
esqueleto, pesos por cercanía, animación por poses y exportación a .glb.

Lo usan modelar_mzee_shamba.py, modelar_maisha.py y los enemigos. Se importa así:
    sys.path.insert(0, os.path.dirname(__file__)); import aparejo

Convención de las rotaciones de las poses (comprobada en Blender): ejes del mundo en la pose de reposo.
  Pierna o brazo caídos: X- = hacia delante, X+ = hacia atrás.  Pie: X+ = bajar la punta.
  Columna y cabeza: X+ = inclinar hacia delante.  Z+ = girar hacia la derecha del personaje (frente = -Y).
  Brazo derecho: Y+ = bajar (hacia el costado), Y- = subir.  Brazo izquierdo: al revés.
"""

import math
import os

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MALLAS_BASE = os.path.join(os.path.dirname(__file__), "recursos", "human_base_meshes",
                           "human-base-meshes-bundle-v1.4.1", "human_base_meshes_bundle.blend")
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
EJES = {"X": X, "Y": Y, "Z": Z}
FPS = 30


# ---------------------------------------------------------------------------
# Escena y materiales
# ---------------------------------------------------------------------------

def escena_vacia():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = FPS


def _lineal(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgb(hexa):
    h = hexa.lstrip("#")
    return [_lineal(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]


def material(nombre, hexa, rugosidad=0.8, metal=0.0, emision=0.0, alfa=1.0):
    m = bpy.data.materials.new(nombre)
    if m.node_tree is None:
        m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    color = rgb(hexa) + [1.0]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = rugosidad
    bsdf.inputs["Metallic"].default_value = metal
    if emision > 0:
        bsdf.inputs["Emission Color"].default_value = color
        bsdf.inputs["Emission Strength"].default_value = emision
    if alfa < 1.0:
        bsdf.inputs["Alpha"].default_value = alfa
        if hasattr(m, "surface_render_method"):
            m.surface_render_method = "BLENDED"
    m.diffuse_color = color
    return m


def activar(ob):
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)


# ---------------------------------------------------------------------------
# Malla base profesional (Blender Studio, CC0)
# ---------------------------------------------------------------------------

def cargar_malla_base(nombre="GEO-body_male_stylized", con_ojos=True):
    """Trae la malla base del paquete de Blender Studio, con sus transformaciones aplicadas (coordenadas del
    mundo en los vértices). Devuelve (cuerpo, [ojo_L, ojo_R])."""
    queridos = [nombre] + ([f"{nombre}.eye.L", f"{nombre}.eye.R"] if con_ojos else [])
    with bpy.data.libraries.load(MALLAS_BASE) as (origen, destino):
        destino.objects = [n for n in origen.objects if n in queridos]
    obs = {}
    for ob in destino.objects:
        bpy.context.collection.objects.link(ob)
        obs[ob.name] = ob
    bpy.context.view_layer.update()
    for ob in obs.values():
        ob.data = ob.data.copy()
        M = ob.matrix_world.copy()
        ob.parent = None
        ob.data.transform(M)
        ob.matrix_world = Matrix.Identity(4)
        ob.modifiers.clear()
    cuerpo = obs[nombre]
    ojos = [obs[f"{nombre}.eye.L"], obs[f"{nombre}.eye.R"]] if con_ojos else []
    # en el catálogo cada malla está desplazada para no pisarse: se centra en X y se apoya en el suelo
    xs = [v.co.x for v in cuerpo.data.vertices]
    zs = [v.co.z for v in cuerpo.data.vertices]
    centrar = Matrix.Translation(Vector((-(min(xs) + max(xs)) / 2, 0.0, -min(zs))))
    for ob in obs.values():
        ob.data.transform(centrar)
        ob.data.update()
    return cuerpo, ojos


def normales_fuera(ob):
    """La malla base trae caras con la normal hacia dentro: en Godot (que no pinta la cara de atrás) se verían
    agujeros, y las prendas se separarían del cuerpo hacia dentro. Se dejan todas hacia fuera."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()


def deformar(ob, funcion):
    """Pasa cada vértice por funcion(Vector) -> Vector."""
    for v in ob.data.vertices:
        v.co = funcion(v.co.copy())
    ob.data.update()


def concha(ob, nombre, dentro, separacion, grosor, mat, quitar=None):
    """Prenda que copia la forma del cuerpo: las caras cuyos vértices cumplen dentro(i, p) (índice y posición),
    separadas del cuerpo «separacion» metros y con «grosor». quitar(i, p) abre huecos (escotes, aberturas)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.normal_update()
    fuera = [f for f in bm.faces
             if not all(dentro(v.index, v.co) for v in f.verts)
             or (quitar and any(quitar(v.index, v.co) for v in f.verts))]
    # separar ANTES de borrar: al borrar, los índices se renumeran y cada vértice cogería la normal de otro
    desplaza = [(v, v.normal.copy()) for v in bm.verts]
    for v, n in desplaza:
        v.co += n * separacion
    bmesh.ops.delete(bm, geom=fuera, context="FACES")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    me.materials.clear()
    me.materials.append(mat)
    for p in me.polygons:
        p.material_index = 0
    nuevo = bpy.data.objects.new(nombre, me)
    bpy.context.collection.objects.link(nuevo)
    activar(nuevo)
    if grosor:
        mod = nuevo.modifiers.new("Grosor", "SOLIDIFY")
        mod.thickness = grosor
        mod.offset = 1.0
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.object.shade_smooth()
    return nuevo


def unir(objetos, nombre):
    activar(objetos[0])
    for ob in objetos[1:]:
        ob.select_set(True)
    bpy.ops.object.join()
    objetos[0].name = nombre
    objetos[0].data.name = nombre
    return objetos[0]


# ---------------------------------------------------------------------------
# Esqueleto y pesos
# ---------------------------------------------------------------------------

def crear_esqueleto(nombre, lista_huesos):
    """lista_huesos: (nombre, cabeza, cola, padre)."""
    datos = bpy.data.armatures.new(f"{nombre}_Esqueleto")
    arm = bpy.data.objects.new(nombre, datos)
    bpy.context.collection.objects.link(arm)
    activar(arm)
    bpy.ops.object.mode_set(mode="EDIT")
    for n, cab, cola, padre in lista_huesos:
        eb = datos.edit_bones.new(n)
        eb.head, eb.tail = Vector(cab), Vector(cola)
        eje = (eb.tail - eb.head).normalized()
        eb.align_roll(Vector((0, -1, 0)) if abs(eje.y) < 0.8 else Z)
        if padre:
            eb.parent = datos.edit_bones[padre]
            eb.use_connect = (eb.head - datos.edit_bones[padre].tail).length < 1e-4
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    return arm


def _dist_segmento(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / (ab.length_squared or 1e-12)))
    return (p - (a + ab * t)).length


def pesar(ob, arm, permitidos, regla=None, vecinos=2):
    """Pesos por cercanía a los huesos permitidos (se mezclan los más cercanos: suave en las articulaciones).
    regla(hueso, índice, punto) -> factor (0 quita el hueso para ese vértice)."""
    segs = {b.name: (b.head_local.copy(), b.tail_local.copy()) for b in arm.data.bones if b.name in permitidos}
    grupos = {n: ob.vertex_groups.new(name=n) for n in segs}
    for v in ob.data.vertices:
        cand = []
        for n, (a, b) in segs.items():
            f = regla(n, v.index, v.co) if regla else 1.0
            if f <= 0:
                continue
            d = _dist_segmento(v.co, a, b)
            cand.append((f / (d ** 4 + 1e-7), n))
        cand.sort(reverse=True)
        cand = cand[:vecinos]
        total = sum(w for w, _ in cand) or 1.0
        for w, n in cand:
            grupos[n].add([v.index], w / total, "REPLACE")
    mod = ob.modifiers.new("Esqueleto", "ARMATURE")
    mod.object = arm
    ob.parent = arm


def copiar_pesos(origen, destino, arm, filtro=None):
    """La ropa copia los pesos del vértice del cuerpo que tiene más cerca (así una manga sigue al brazo que
    cubre y no se rasga). filtro(punto) decide a qué vértices del destino se aplica (por defecto, a todos)."""
    from mathutils import kdtree
    arbol = kdtree.KDTree(len(origen.data.vertices))
    for v in origen.data.vertices:
        arbol.insert(v.co, v.index)
    arbol.balance()
    nombres = {g.index: g.name for g in origen.vertex_groups}
    for v in destino.data.vertices:
        if filtro and not filtro(v.co):
            continue
        for g in list(v.groups):
            destino.vertex_groups[g.group].remove([v.index])
        _, i, _ = arbol.find(v.co)
        for g in origen.data.vertices[i].groups:
            nombre = nombres[g.group]
            grupo = destino.vertex_groups.get(nombre) or destino.vertex_groups.new(name=nombre)
            grupo.add([v.index], g.weight, "REPLACE")
    if not any(m.type == "ARMATURE" for m in destino.modifiers):
        mod = destino.modifiers.new("Esqueleto", "ARMATURE")
        mod.object = arm
    destino.parent = arm


def anclar(ob, arm, hueso):
    """El objeto sigue al hueso (en Godot: BoneAttachment3D)."""
    activar(ob)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    arm.data.bones.active = arm.data.bones[hueso]
    bpy.ops.object.parent_set(type="BONE", keep_transform=True)


# ---------------------------------------------------------------------------
# Animación por poses
# ---------------------------------------------------------------------------

def curvas(act):
    if hasattr(act, "fcurves") and len(getattr(act, "fcurves", [])):
        return list(act.fcurves)
    lista = []
    for capa in getattr(act, "layers", []):
        for tira in capa.strips:
            for bolsa in tira.channelbags:
                lista.extend(bolsa.fcurves)
    return lista


class Animador:
    """Poses con rotaciones sobre ejes del mundo (ver la convención arriba). Puede mantener un objeto anclado
    (bastón, cetro) apuntando a una dirección fija girando la mano que lo sujeta."""

    def __init__(self, arm, mano_baston=None, eje_baston=None):
        self.arm = arm
        self.rest = {b.name: b.matrix_local.to_3x3() for b in arm.data.bones}
        self.mano = mano_baston
        if mano_baston:
            R = arm.data.bones[mano_baston].matrix_local.to_3x3()
            self.baston_local = (R.inverted() @ eje_baston).normalized()
        arm.animation_data_create()

    def q(self, nombre, rotaciones):
        qw = Quaternion()
        for eje, grados in rotaciones:
            qw = Quaternion(EJES[eje], math.radians(grados)) @ qw
        R = self.rest[nombre]
        return (R.inverted() @ qw.to_matrix() @ R).to_quaternion()

    def nueva(self, nombre):
        act = bpy.data.actions.new(nombre)
        act.use_fake_user = True
        self.arm.animation_data.action = act
        return act

    def _ik(self, objetivos):
        """Coloca muñecas en puntos del mundo: {hueso_antebrazo: punto}. Blender resuelve hombro y codo con
        cinemática inversa y el resultado se guarda como rotaciones normales (en Godot no hace falta IK)."""
        temporales = []
        for antebrazo, punto in objetivos.items():
            vacio = bpy.data.objects.new(f"ik_{antebrazo}", None)
            bpy.context.collection.objects.link(vacio)
            vacio.location = Vector(punto)
            c = self.arm.pose.bones[antebrazo].constraints.new("IK")
            c.target = vacio
            c.chain_count = 2
            temporales.append((antebrazo, c, vacio))
        bpy.context.view_layer.update()
        resultado = []
        for antebrazo, _, _ in temporales:
            pb = self.arm.pose.bones[antebrazo]
            resultado.append((pb.parent.name, pb.parent.matrix.copy()))
            resultado.append((antebrazo, pb.matrix.copy()))
        for antebrazo, c, vacio in temporales:
            self.arm.pose.bones[antebrazo].constraints.remove(c)
            bpy.data.objects.remove(vacio)
        bpy.context.view_layer.update()
        for nombre, M in resultado:
            self.arm.pose.bones[nombre].matrix = M
            bpy.context.view_layer.update()

    def fotograma(self, f, pose, mover=None, baston=None, escalas=None, ik=None):
        """pose: {hueso: [(eje, grados)...]}; mover: {hueso: (x, y, z) en el mundo};
        baston: dirección del mundo del objeto anclado; escalas: {hueso: factor};
        ik: {antebrazo: punto del mundo donde debe quedar la muñeca}."""
        mover = mover or {}
        escalas = escalas or {}
        for pb in self.arm.pose.bones:
            pb.rotation_quaternion = self.q(pb.name, pose.get(pb.name, []))
            pb.location = self.rest[pb.name].inverted() @ Vector(mover.get(pb.name, (0, 0, 0)))
            s = escalas.get(pb.name, 1.0)
            pb.scale = Vector((s, s, s))
        if ik:
            self._ik(ik)
        if baston is not None and self.mano:
            bpy.context.view_layer.update()
            pb = self.arm.pose.bones[self.mano]
            M = pb.matrix.copy()
            actual = (M.to_3x3() @ self.baston_local).normalized()
            delta = actual.rotation_difference(Vector(baston).normalized())
            pb.matrix = Matrix.Translation(M.translation) @ (delta.to_matrix() @ M.to_3x3()).to_4x4()
            bpy.context.view_layer.update()
        for pb in self.arm.pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=f)
            pb.keyframe_insert("location", frame=f)
            pb.keyframe_insert("scale", frame=f)

    def cerrar(self, nombre):
        act = self.arm.animation_data.action
        pista = self.arm.animation_data.nla_tracks.new()
        pista.name = nombre
        pista.strips.new(nombre, int(act.frame_range[0]), act)
        pista.mute = True
        self.arm.animation_data.action = None


# ---------------------------------------------------------------------------
# Exportación, informe y vistas
# ---------------------------------------------------------------------------

def exportar(salida, arm, objetos):
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    for ob in objetos:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.gltf(filepath=salida, export_format="GLB", use_selection=True, export_yup=True,
                              export_apply=False, export_skins=True, export_animations=True,
                              export_animation_mode="ACTIONS", export_def_bones=False)


def exportar_estatico(salida, objetos):
    """Para atrezo sin esqueleto: solo mallas (y nodos vacíos si los hay)."""
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objetos:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objetos[0]
    bpy.ops.export_scene.gltf(filepath=salida, export_format="GLB", use_selection=True, export_yup=True,
                              export_apply=True, export_animations=False)


def informe(titulo, arm, objetos, salida):
    print(f"\n=== {titulo} ===")
    total = 0
    for ob in objetos:
        tris = sum(len(p.vertices) - 2 for p in ob.data.polygons)
        total += tris
        print(f"  {ob.name:18s} {tris:6d} triángulos  [{', '.join(m.name for m in ob.data.materials if m)}]")
    alto = max((ob.matrix_world @ Vector(c)).z for ob in objetos for c in ob.bound_box)
    print(f"  Triángulos en total: {total}   Alto: {alto:.2f} m")
    print(f"  Huesos: {len(arm.data.bones)}")
    acts = [a for a in bpy.data.actions if a.use_fake_user]
    print("  Animaciones: " + ", ".join(f"{a.name} ({int(a.frame_range[1] - a.frame_range[0])} f)" for a in acts))
    print(f"  Exportado a {salida}")


def preparar_vistas(fondo=(0.36, 0.38, 0.40), resolucion=(800, 1000)):
    esc = bpy.context.scene
    esc.render.engine = "BLENDER_EEVEE"
    esc.render.resolution_x, esc.render.resolution_y = resolucion
    mundo = bpy.data.worlds.new("Fondo")
    mundo.use_nodes = True
    mundo.node_tree.nodes["Background"].inputs["Color"].default_value = (*fondo, 1)
    mundo.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    esc.world = mundo
    for nombre, energia, rot in (("Clave", 3.2, (52, 0, -35)), ("Relleno", 1.0, (65, 0, 140))):
        luz = bpy.data.objects.new(nombre, bpy.data.lights.new(nombre, "SUN"))
        luz.data.energy = energia
        luz.data.angle = math.radians(6)
        luz.rotation_euler = tuple(math.radians(a) for a in rot)
        esc.collection.objects.link(luz)
    suelo = bpy.data.meshes.new("Suelo")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=3)
    bm.to_mesh(suelo)
    bm.free()
    esc.collection.objects.link(bpy.data.objects.new("Suelo", suelo))
    cam = bpy.data.objects.new("Camara", bpy.data.cameras.new("Camara"))
    esc.collection.objects.link(cam)
    esc.camera = cam

    def foto(ruta, pos, obj, lente=50):
        cam.data.lens = lente
        cam.location = pos
        cam.rotation_euler = (Vector(obj) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        esc.render.filepath = ruta
        bpy.ops.render.render(write_still=True)
    return foto
