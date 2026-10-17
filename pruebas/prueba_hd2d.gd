extends Node
## Prueba automática del HD-2D (scripts/mundo/hd2d/espejo_hd2d.gd): se enciende y se apaga con H, cada dibujo
## del mundo tiene su gemelo 3D, la interfaz sigue a la vista, el juego por debajo no cambia (Maisha anda, su gemelo
## la sigue), las peñas se levantan y se recuerda al cambiar de escena.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_hd2d

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _espejo() -> Node3D:
	return get_tree().root.get_node_or_null("EspejoHD2D") as Node3D


func _ir(escena: String, puerta: String) -> void:
	Estado.ir_a(escena, puerta)
	for i in 300:
		if get_tree().current_scene and get_tree().current_scene.scene_file_path.ends_with(escena + ".tscn") and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(1.0)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["cetro_recibido", "visto/cuna_de_musgo", "primer_arbol_libre", "escarcha_llegada", "escarcha_racha"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("Encender el HD-2D:")
	await _ir("prados_del_eco", "")
	var escena := get_tree().current_scene
	_comprobar(_espejo() == null and escena.visible, "al empezar, el juego se ve en 2D")
	var tecla := InputEventKey.new()
	tecla.physical_keycode = KEY_H
	tecla.pressed = true
	escena._unhandled_key_input(tecla)
	await _esperar(0.5)
	var espejo := _espejo()
	_comprobar(espejo != null, "con H se enciende el HD-2D")
	_comprobar(escena.visible and espejo != null and espejo.get("_capa_suelo") != null, "el dibujo 2D del mundo pasa a las capas 3D (la escena sigue viva)")
	var gemelos: Dictionary = espejo.get("_gemelos") if espejo else {}
	_comprobar(gemelos.size() > 40, "cada dibujo del mundo tiene su gemelo 3D (%d)" % gemelos.size())
	_comprobar(espejo != null and espejo.camara.current, "y una cámara 3D lo mira")
	var hud: CanvasLayer = get_tree().get_first_node_in_group("hud")
	_comprobar(hud != null and hud.visible, "la interfaz sigue a la vista")
	_comprobar(espejo != null and espejo.get("_capa_post") != null and espejo.get("_mat_post") != null, "el postprocesado cinematográfico HD-2D está activo")
	Estado.extra["calidad_hd2d"] = "baja"
	await get_tree().process_frame
	await get_tree().process_frame
	var capa_post: CanvasLayer = espejo.get("_capa_post") if espejo else null
	_comprobar(capa_post != null and not capa_post.visible, "el selector de calidad HD-2D cambia los niveles de postprocesado")
	Estado.extra["calidad_hd2d"] = "alta"
	await get_tree().process_frame
	await get_tree().process_frame
	_comprobar(espejo != null and espejo.get("_mascara_ao") != null, "la oclusión ambiental de contacto del suelo está horneada")
	_comprobar(espejo != null and ((espejo.get("_luces_3d") as Array).size() > 0 or (espejo.get("_luces_pt2d") as Dictionary).size() > 0), "las luces puntuales 3D (OmniLight3D) están registradas")
	_comprobar(espejo != null and is_equal_approx(espejo.camara.fov, 18.0), "la cámara usa teleobjetivo de maqueta (18°) sin deformar los bordes")
	var mm_motas: MultiMeshInstance3D = espejo.get("_malla_motas") if espejo else null
	var mm_polvo: MultiMeshInstance3D = espejo.get("_malla_polvo") if espejo else null
	_comprobar(mm_motas != null and mm_motas.multimesh != null and mm_polvo != null, "las partículas 3D (motas ambientales y polvo al correr) están activas")
	_comprobar(espejo != null and (espejo.get("DE_PIE") as Array).has("guardian.gd") and (espejo.get("DE_PIE") as Array).has("tintero.gd"), "los enemigos y jefes que dibujan en el aire están en DE_PIE")
	_comprobar(espejo != null and espejo.get("MODELOS_BLENDER") != null and (espejo.get("MODELOS_BLENDER") as Dictionary).has("casa_seta.png") and (espejo.get("MODELOS_BLENDER") as Dictionary).has("gran_arbol.png"), "los modelos 3D de Blender para arquitectura (.glb) están conectados")

	print("El juego no cambia:")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var gemelo_m: Sprite3D = null
	for par in gemelos.values():
		if par[0] == m.get_node("Sprite"):
			gemelo_m = par[1]
	_comprobar(gemelo_m != null, "Maisha tiene su gemelo 3D")
	var antes := m.global_position
	Input.action_press("mover_derecha")
	await _esperar(0.6)
	Input.action_release("mover_derecha")
	await _esperar(0.1)
	_comprobar(m.global_position.x > antes.x + 20, "Maisha anda igual que en 2D")
	_comprobar(gemelo_m != null and absf(gemelo_m.position.x - m.global_position.x / 16.0) < 0.05, "y su gemelo la sigue por el suelo 3D")
	_comprobar(gemelo_m != null and gemelo_m.texture != null and gemelo_m.billboard == BaseMaterial3D.BILLBOARD_FIXED_Y, "de pie, mirando a la cámara, con su dibujo")
	_comprobar(gemelo_m != null and gemelo_m.has_meta("capas_fondo") and (gemelo_m.get_meta("capas_fondo") as Array).size() >= 3, "las estructuras, personajes y jefes tienen fondo volumétrico 3D")

	print("Las peñas y el recuerdo:")
	await _ir("paso_escarcha", "sur")
	espejo = _espejo()
	_comprobar(espejo != null, "al cambiar de escena, sigue en HD-2D (se recuerda)")
	var hay_penas := false
	if espejo:
		for h in espejo.get_children():
			if h is MeshInstance3D and (h as MeshInstance3D).mesh and (h as MeshInstance3D).mesh.get_surface_count() > 0 and (h as MeshInstance3D).mesh is ArrayMesh:
				hay_penas = true
	_comprobar(hay_penas, "las peñas del mapa se levantan en 3D")
	get_tree().current_scene.poner_hd2d(false)
	await _esperar(0.3)
	_comprobar(_espejo() == null and not Estado.extra.get("hd2d", false), "al apagarlo, vuelve el 2D de siempre")
	var sombras_ok := true
	for s in get_tree().get_nodes_in_group("maisha"):
		for h in s.get_children():
			if h is CanvasItem and (h as CanvasItem).visibility_layer != 1:
				sombras_ok = false
	_comprobar(sombras_ok, "y cada dibujo vuelve a su canal")

	print()
	print("RESULTADO: todo correcto" if _fallos == 0 else "RESULTADO: %d fallos" % _fallos)
	get_tree().quit(1 if _fallos else 0)
