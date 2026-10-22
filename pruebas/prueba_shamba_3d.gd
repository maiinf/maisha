extends Node
## Mzee Shamba en 3D: esqueleto de la ficha, bastón y cuenco anclados a sus huesos y las 4 animaciones.

var fallos := 0


func _ready() -> void:
	print("\n--- PRUEBA MZEE SHAMBA 3D ---")
	var escena: PackedScene = load("res://modelos/personajes/mzee_shamba.glb")
	comprobar(escena != null, "carga mzee_shamba.glb")
	if escena == null:
		terminar()
		return
	var shamba := escena.instantiate()
	add_child(shamba)
	var esqueletos := shamba.find_children("*", "Skeleton3D", true, false)
	comprobar(not esqueletos.is_empty(), "tiene esqueleto")
	if not esqueletos.is_empty():
		var esq: Skeleton3D = esqueletos[0]
		for hueso in ["hips", "head", "jaw", "beard_root", "hat_bone", "whiskers_L", "whiskers_R", "tail_01",
				"tail_flat", "hand_R", "hand_L", "foot_L", "cuenco"]:
			comprobar(esq.find_bone(hueso) >= 0, "hueso %s" % hueso)
	var anclajes := {}
	for a in shamba.find_children("*", "BoneAttachment3D", true, false):
		for hijo in a.get_children():
			anclajes[String(hijo.name)] = a.bone_name
	comprobar(anclajes.get("Baston") == "hand_R", "el bastón va en la mano derecha")
	comprobar(anclajes.get("Cuenco") == "cuenco", "el cuenco va en su hueso")
	var reproductores := shamba.find_children("*", "AnimationPlayer", true, false)
	comprobar(not reproductores.is_empty(), "tiene AnimationPlayer")
	if not reproductores.is_empty():
		var ap: AnimationPlayer = reproductores[0]
		for nombre in ["idle_labranza", "hablar_afable", "cavar_tierra", "ofrecer_cuenco"]:
			comprobar(ap.has_animation(nombre), "animación %s" % nombre)
	var alto := 0.0
	for m in shamba.find_children("*", "MeshInstance3D", true, false):
		var caja: AABB = (m as MeshInstance3D).get_aabb()
		alto = maxf(alto, caja.end.y)
	comprobar(alto > 1.35 and alto < 1.60, "mide unos 1,45 m (con el sombrero %.2f m)" % alto)
	terminar()


func terminar() -> void:
	print("\nRESULTADO: " + ("todo correcto" if fallos == 0 else "%d fallos" % fallos))
	get_tree().quit(1 if fallos else 0)


func comprobar(ok: bool, que: String) -> void:
	if ok:
		print("  bien: " + que)
	else:
		fallos += 1
		print("  FALLO: " + que)
