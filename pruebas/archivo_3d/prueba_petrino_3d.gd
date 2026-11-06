extends Node
## Petrino de Giza en 3D: el modelo (huesos de la ficha, fragmentos, animaciones) y que la IA ponga la
## animación de cada fase (reposo, embestida, aturdido y la muerte por fractura).

var fallos := 0


func _ready() -> void:
	print("\n--- PRUEBA PETRINO 3D ---")
	var petrino: CharacterBody3D = load("res://escenas/enemigos/petrino_3d.tscn").instantiate()
	add_child(petrino)
	await get_tree().process_frame
	var esq := petrino.find_children("*", "Skeleton3D", true, false)
	comprobar(not esq.is_empty(), "tiene esqueleto")
	if not esq.is_empty():
		for hueso in ["Pelvis", "Spine_01", "Chest", "Neck", "Head", "Jaw_Tusk", "LegFront_L", "FootFront_R",
				"LegBack_R", "FootBack_L"]:
			comprobar(esq[0].find_bone(hueso) >= 0, "hueso %s" % hueso)
	comprobar(petrino.find_children("Shards_Break_*", "", true, false).size() == 6, "6 puntos de fragmentos")
	var anim: AnimationPlayer = petrino._anim
	comprobar(anim != null, "la IA encuentra el AnimationPlayer")
	if anim == null:
		terminar()
		return
	for nombre in ["reposo", "caminar", "embestida", "aturdido", "muerte_fractura"]:
		comprobar(anim.has_animation(nombre), "animación %s" % nombre)
	comprobar(anim.current_animation == "reposo", "quieto: reposo")
	petrino._cambiar_fase(petrino.FasePetrino.EMBESTIDA)
	comprobar(anim.current_animation == "embestida", "al embestir: embestida")
	petrino._cambiar_fase(petrino.FasePetrino.ATURDIDO)
	comprobar(anim.current_animation == "aturdido", "tras chocar: aturdido")
	petrino.recibir_ataque(petrino.vida)
	comprobar(petrino.fase == petrino.FasePetrino.MUERTE and anim.current_animation == "muerte_fractura",
		"al vencerlo: se rompe (muerte_fractura)")
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
