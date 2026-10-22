extends Node
## Maisha en 3D: el modelo (esqueleto, cetro en la mano y animaciones) y el controlador (qué animación suena
## en cada momento, el golpe y los Tatuajes de la Memoria que se encienden con los Ecos).

var fallos := 0


func _ready() -> void:
	print("\n--- PRUEBA MAISHA 3D ---")
	var maisha: CharacterBody3D = load("res://escenas/personajes/maisha_3d.tscn").instantiate()
	var suelo := StaticBody3D.new()
	var forma := CollisionShape3D.new()
	forma.shape = BoxShape3D.new()
	(forma.shape as BoxShape3D).size = Vector3(20, 1, 20)
	forma.position.y = -0.5
	suelo.add_child(forma)
	add_child(suelo)
	add_child(maisha)
	await get_tree().process_frame

	# el modelo
	var esqueleto := maisha.find_children("*", "Skeleton3D", true, false)
	comprobar(not esqueleto.is_empty() and esqueleto[0].get_bone_count() == 27, "esqueleto de 27 huesos")
	var anclajes := maisha.find_children("*", "BoneAttachment3D", true, false)
	comprobar(not anclajes.is_empty() and anclajes[0].bone_name == "hand_R"
		and anclajes[0].find_child("Cetro", true, false) != null, "el cetro va anclado a la mano derecha")
	var anim: AnimationPlayer = maisha._anim
	comprobar(anim != null, "el controlador encuentra el AnimationPlayer")
	if anim == null:   # sin animaciones no hay más que comprobar (y no hay que quedarse colgada)
		print("\nRESULTADO: %d fallos" % fallos)
		get_tree().quit(1)
		return
	for nombre in ["reposo", "caminar_atento", "correr", "golpe_cetro", "idle_mirar_tatuajes", "eco_despertar"]:
		comprobar(anim.has_animation(nombre), "animación %s" % nombre)
	comprobar(anim.get_animation("caminar_atento").loop_mode == Animation.LOOP_LINEAR, "caminar se repite en bucle")

	# quieta: reposo
	await esperar(3)
	comprobar(anim.current_animation == "reposo", "quieta: reposo (va: %s)" % anim.current_animation)

	# caminando y corriendo (se simula la velocidad)
	maisha.velocity = Vector3(0, 0, 1.3)
	maisha._process(0.016)
	comprobar(anim.current_animation == "caminar_atento", "a 1,3 m/s camina")
	maisha.velocity = Vector3(0, 0, 6.0)
	maisha._process(0.016)
	comprobar(anim.current_animation == "correr", "a 6 m/s corre")
	maisha.velocity = Vector3.ZERO

	# golpe con el cetro
	maisha._intentar_ataque()
	comprobar(maisha.atacando and anim.current_animation == "golpe_cetro", "J / clic: golpe con el cetro")
	await esperar(int(Engine.physics_ticks_per_second * 0.7))
	comprobar(not maisha.atacando, "el golpe termina y devuelve el control")

	# tatuajes: dormidos al empezar; un Eco los enciende un noveno
	var piel: BaseMaterial3D = maisha._piel
	comprobar(piel != null, "el controlador tiene su propio material de piel")
	comprobar(is_zero_approx(piel.emission_energy_multiplier), "al despertar, los tatuajes están dormidos (brillo 0)")
	maisha.recuperar_eco()
	comprobar(anim.current_animation == "eco_despertar", "al recuperar un Eco: animación del despertar")
	await get_tree().create_timer(1.8).timeout
	comprobar(is_equal_approx(maisha.memoria, 1.0 / 9.0), "un Eco = un noveno de la memoria (va %.3f)" % maisha.memoria)
	comprobar(piel.emission_energy_multiplier > 0.1, "los tatuajes ya brillan un poco")
	maisha.despertar_memoria(1.0)
	comprobar(is_equal_approx(piel.emission_energy_multiplier, 1.5), "con los 9 Ecos brillan del todo (1,5)")

	print("\nRESULTADO: " + ("todo correcto" if fallos == 0 else "%d fallos" % fallos))
	get_tree().quit(1 if fallos else 0)


func esperar(fotogramas: int) -> void:
	for i in fotogramas:
		await get_tree().physics_frame


func comprobar(ok: bool, que: String) -> void:
	if ok:
		print("  bien: " + que)
	else:
		fallos += 1
		print("  FALLO: " + que)
