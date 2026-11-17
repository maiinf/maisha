extends Node
## Prueba automática del HD-2D (scripts/mundo/hd2d/espejo_hd2d.gd): se enciende y se apaga con H, cada dibujo
## del mundo tiene su gemelo 3D, la interfaz sigue a la vista, el juego por debajo no cambia (Maisha anda, su gemelo
## la sigue), las peñas se levantan y se recuerda al cambiar de escena.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_hd2d

const PIEL := preload("res://scripts/interfaz/piel.gd")

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

	print("Arranca en HD-2D y se alterna con H:")
	await _ir("prados_del_eco", "")
	var escena := get_tree().current_scene
	var espejo := _espejo()
	_comprobar(espejo != null and escena.visible, "al empezar, el juego arranca directamente en HD-2D")
	var tecla := InputEventKey.new()
	tecla.physical_keycode = KEY_H
	tecla.pressed = true
	escena._unhandled_key_input(tecla)
	await _esperar(0.3)
	_comprobar(_espejo() == null and not Estado.extra.get("hd2d", false), "con H se apaga al 2D clásico")
	escena._unhandled_key_input(tecla)
	await _esperar(0.5)
	espejo = _espejo()
	_comprobar(espejo != null, "con H vuelve a encenderse el HD-2D")
	_comprobar(escena.visible and espejo != null and espejo.get("_capa_suelo") != null, "el dibujo 2D del mundo pasa a las capas 3D (la escena sigue viva)")
	var gemelos: Dictionary = espejo.get("_gemelos") if espejo else {}
	_comprobar(gemelos.size() > 40, "cada dibujo del mundo tiene su gemelo 3D (%d)" % gemelos.size())
	_comprobar(espejo != null and espejo.camara.current, "y una cámara 3D lo mira")
	var hud: CanvasLayer = get_tree().get_first_node_in_group("hud")
	_comprobar(hud != null and hud.visible, "la interfaz sigue a la vista")

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

	print("Edificios con volumen 3D:")
	await _ir("cuna_de_musgo", "")
	espejo = _espejo()
	var edificios_3d := 0
	if espejo:
		for par in espejo.get("_gemelos").values():
			if par[1] is MeshInstance3D:
				edificios_3d += 1
	_comprobar(edificios_3d > 0, "los edificios de Cuna de Musgo se construyen como mallas 3D con volumen (%d)" % edificios_3d)

	await _ir("mji_jiwe", "")
	espejo = _espejo()
	var mji_edifs := 0
	if espejo:
		for par in espejo.get("_gemelos").values():
			if par[1] is MeshInstance3D:
				mji_edifs += 1
	_comprobar(mji_edifs >= 12, "los edificios y verjas de Mji-Jiwe se construyen en 3D con volumen (%d)" % mji_edifs)
	_comprobar(espejo != null and absf(float(espejo.get("_alto_pena")) - 0.75) < 0.01, "los muros de terraza de Mji-Jiwe usan su altura baja (0,75)")

	print("Rutas de Asterhaul y plataformas horizontales:")
	await _ir("galerias_ambar", "")
	espejo = _espejo()
	var gal_edifs := 0
	var ventanas_malla := 0
	if espejo:
		for par in espejo.get("_gemelos").values():
			if par[1] is MeshInstance3D and String(par[4]) != "__plataforma__":
				gal_edifs += 1
		for vpar in espejo.get("_ventanas"):
			if vpar[1] is MeshInstance3D and (vpar[1] as MeshInstance3D).mesh is ArrayMesh:
				ventanas_malla += 1
	_comprobar(espejo != null and absf(float(espejo.get("_alto_pena")) - 1.625) < 0.01, "Galerías de Ámbar usa muros de acantilado altos (1,625)")
	_comprobar(gal_edifs >= 2, "taller y barricadas de Galerías se construyen en 3D (%d)" % gal_edifs)
	_comprobar(ventanas_malla > 0 and espejo != null and not espejo.get("_moduladores").is_empty(), "las ventanitas usan malla doblada y sigue el CanvasModulate de penumbra")

	await _ir("fundicion_escoria", "")
	espejo = _espejo()
	var barcazas_3d := 0
	if espejo:
		for par in espejo.get("_gemelos").values():
			if String(par[4]) == "__plataforma__" and par[1] is MeshInstance3D and (par[1] as MeshInstance3D).mesh is PlaneMesh:
				barcazas_3d += 1
	_comprobar(espejo != null and bool(espejo.get("_es_escoria")) and absf(float(espejo.get("_alto_pena")) - 1.625) < 0.01, "Fundición de Escoria activa el modo escoria y muros 1,625")
	_comprobar(barcazas_3d >= 4, "las 4 barcazas de hierro flotan como plataformas 3D horizontales (%d)" % barcazas_3d)

	await _ir("aguja_caida", "")
	espejo = _espejo()
	var penas_aguja := false
	var penascos_3d := 0
	var maisha_node := get_tree().get_first_node_in_group("maisha") as Node2D
	var sprite_m := maisha_node.get_node_or_null("Sprite") as Node2D if maisha_node else null
	if espejo:
		for h in espejo.get_children():
			if h is MeshInstance3D and (h as MeshInstance3D).layers == 2:
				penas_aguja = true
		for par in espejo.get("_gemelos").values():
			if String(par[4]) == "__plataforma__" and par[1] is MeshInstance3D and (par[1] as MeshInstance3D).mesh is PlaneMesh:
				penascos_3d += 1
	_comprobar(espejo != null and not penas_aguja, "La Aguja Caída respeta el abismo en los bordes «0» (sin muros falsos)")
	_comprobar(penascos_3d >= 2, "los peñascos flotantes de La Aguja usan plataforma horizontal 3D (%d)" % penascos_3d)
	if espejo and maisha_node and sprite_m:
		maisha_node.set_physics_process(false)
		maisha_node.modulate.a = 0.4
		await _esperar(0.1)
		var g_maisha := espejo.get("_gemelos").get(sprite_m.get_instance_id())[1] as Sprite3D
		_comprobar(g_maisha != null and g_maisha.alpha_cut == SpriteBase3D.ALPHA_CUT_DISABLED and g_maisha.modulate.a < 0.5, "al desvanecer al padre al caer al vacío, el gemelo 3D también transparenta")
		maisha_node.modulate.a = 1.0
		maisha_node.set_physics_process(true)
	_comprobar(PIEL.TACTICO_INFO.has("magnetico") and PIEL.TACTICO_INFO.has("resonancia"), "el HUD táctico y bestiario registran magnetico y resonancia")

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
