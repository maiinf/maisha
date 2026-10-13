extends Node
## Prueba automática de la Gruta de las Raíces (parte 1): desde el muelle de piedra de La Travesía, la boca de la cueva
## está tapada por raíces hasta tener la hoja de Mauti; dentro, la oscuridad, las semillas dormidas que laten y las
## huellas lilas de Mauti.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_gruta_raices

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


func _escena() -> String:
	var e := get_tree().current_scene
	return e.name if e else ""


func _puerta(id: String) -> Area2D:
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == id:
			return p
	return null


func _empujar(accion: String, segundos: float) -> void:
	Input.action_press(accion)
	await _esperar(segundos)
	Input.action_release(accion)


func _cruzar(accion: String, nombre: String) -> void:
	Input.action_press(accion)
	for i in 400:
		if Estado.cambiando:
			break
		await get_tree().process_frame
	Input.action_release(accion)
	for i in 300:
		if _escena() == nombre and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(0.3)


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 80:
		if not dialogo.hablando:
			return
		dialogo.pasar()
		await _esperar(0.08)


func _hablar_con(n: Node) -> void:
	n.interactuar()
	await _esperar(0.2)
	await _leer_dialogo()
	await _esperar(2.2)            # (lo que se dice «después»)
	await _leer_dialogo()
	await _esperar(0.4)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "travesia_hecha",
			"eco/la_travesia"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("La boca de la Gruta:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/la_travesia.tscn")
	await _esperar(2.0)
	await _leer_dialogo()
	var boca := _puerta("gruta")
	_comprobar(boca != null and boca.destino == "gruta_raices" and boca.cerrada_hasta == "hoja_mauti", "en el muelle de piedra, el camino de la Gruta (se abre con la hoja de Mauti)")
	_maisha().global_position = boca.global_position + Vector2(0, 30)
	await _esperar(0.3)
	await _empujar("mover_arriba", 1.2)
	await _esperar(0.3)
	_comprobar(_escena() == "LaTravesia" and get_tree().get_first_node_in_group("dialogo").hablando, "sin la hoja, las raíces no dejan pasar")
	await _leer_dialogo()
	Estado.marcar("hoja_mauti")
	_maisha().global_position = boca.global_position + Vector2(0, 30)
	await _cruzar("mover_arriba", "GrutaRaices")
	_comprobar(_escena() == "GrutaRaices", "con la hoja de Mauti, las raíces se apartan: se entra en la Gruta")
	await _esperar(2.0)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al entrar")
	await _leer_dialogo()

	print("A oscuras:")
	var oscuridad: Node = get_tree().current_scene.get_node("Oscuridad")
	var penumbra := false
	for h in oscuridad.get_children():
		if h is CanvasModulate:
			penumbra = (h as CanvasModulate).color.v < 0.3
	_comprobar(penumbra, "la cueva está en penumbra")
	var luz := false
	for h in _maisha().get_children():
		if h is PointLight2D:
			luz = true
	_comprobar(luz, "Maisha alumbra un poco a su alrededor")
	var semillas: Array = oscuridad.get("_semillas")
	_comprobar(semillas.size() >= 6, "semillas dormidas que laten verdes en los nichos (%d)" % semillas.size())
	var huellas := 0
	for h in oscuridad.get_children():
		if h is Sprite2D:
			huellas += 1
	_comprobar(huellas >= 20, "las huellas lilas de Mauti marcan el camino hacia dentro (%d)" % huellas)
	_comprobar(Sonido.musica_actual != "", "suena música (de momento, la del Lago)")
	var norte := _puerta("olvidado")
	_comprobar(norte != null and norte.cerrada_hasta != "", "al fondo, el Sendero Olvidado (cerrado)")

	print("De vuelta a La Travesía:")
	_maisha().global_position = _puerta("travesia").global_position + Vector2(0, -30)
	await _cruzar("mover_abajo", "LaTravesia")
	_comprobar(_escena() == "LaTravesia", "por el sur se vuelve al muelle de piedra")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
