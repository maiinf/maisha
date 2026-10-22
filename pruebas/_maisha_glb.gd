extends SceneTree
# Temporal: revisa maisha.glb dentro de Godot. Se borra después.

func _init() -> void:
	var escena: PackedScene = load("res://modelos/personajes/maisha.glb")
	if escena == null:
		print("FALLO: no carga")
		quit(1)
		return
	var raiz := escena.instantiate()
	var esq := raiz.find_child("*", true, false)
	var skel: Skeleton3D = null
	for n in raiz.find_children("*", "Skeleton3D", true, false):
		skel = n
	print("ESQUELETO: ", skel.get_bone_count(), " huesos")
	var nombres := []
	for i in skel.get_bone_count():
		nombres.append(skel.get_bone_name(i))
	print("HUESOS: ", ", ".join(nombres))
	for n in raiz.find_children("*", "BoneAttachment3D", true, false):
		print("ANCLAJE: ", n.name, " -> hueso ", n.bone_name, " hijos: ", n.get_children().map(func(c): return c.name))
	for n in raiz.find_children("*", "MeshInstance3D", true, false):
		var m := n as MeshInstance3D
		print("MALLA: ", m.name, " superficies ", m.mesh.get_surface_count(), " piel=", m.skin != null)
		for i in m.mesh.get_surface_count():
			var mat := m.mesh.surface_get_material(i) as BaseMaterial3D
			if mat and mat.resource_name == "piel_humanizada":
				print("  PIEL: albedo_tex=", mat.albedo_texture != null, " emision=", mat.emission_enabled,
					" emision_tex=", mat.emission_texture != null, " energia=", mat.emission_energy_multiplier,
					" color_emision=", mat.emission)
	for n in raiz.find_children("*", "AnimationPlayer", true, false):
		var ap := n as AnimationPlayer
		for a in ap.get_animation_list():
			print("ANIM: ", a, " ", snappedf(ap.get_animation(a).length, 0.01), " s")
	var aabb := AABB()
	for n in raiz.find_children("*", "MeshInstance3D", true, false):
		aabb = aabb.merge((n as MeshInstance3D).get_aabb())
	print("ALTO (reposo): ", snappedf(aabb.size.y, 0.01), " m")
	raiz.free()
	print("RESULTADO: todo correcto")
	quit()
