extends Node
## Prueba automática de La Travesía (el viaje río arriba en el transbordador): se sube en el Embarcadero Junco, la barca
## sube sola con Maisha en la cubierta (sin poder salirse), atraca en el muelle de piedra de la Gruta, Maisha baja y
## puede volver al Embarcadero desde la barca.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_la_travesia

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
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "embarcadero_llegada",
			"eco/orilla_juncos", "casa_bata_abierta", "bata_conocido", "mamba_vencido", "zona/embarcadero_junco/1",
			"boquete_tapado", "transbordador_listo"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("Subir al transbordador en el Embarcadero:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/embarcadero_junco.tscn")
	await _esperar(1.5)
	await _leer_dialogo()
	var embarque: Node2D = null
	for n in get_tree().get_nodes_in_group("interactuables"):
		if n.get_script() and String(n.get_script().resource_path).ends_with("arreglo_transbordador.gd") == false and n.get_parent().name == "ArregloTransbordador":
			embarque = n
	_comprobar(embarque != null, "con el transbordador a flote, en la punta del muelle se puede subir")
	_maisha().global_position = embarque.global_position + Vector2(0, 10)
	await _esperar(0.3)
	embarque.interactuar()
	await _esperar(0.3)
	await _leer_dialogo()
	for i in 200:
		if _escena() == "LaTravesia" and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(0.5)
	_comprobar(_escena() == "LaTravesia", "Bata zarpa: se llega a La Travesía")

	print("El viaje:")
	var viaje: Node2D = get_tree().current_scene.get_node("Entidades/Viaje")
	var cubierta: Rect2 = viaje.PISABLE
	_comprobar(viaje != null and Rect2(viaje.position + cubierta.position, cubierta.size).grow(2).has_point(_maisha().global_position), "Maisha va en la cubierta")
	await _esperar(3.0)
	_comprobar(viaje.fase == viaje.Fase.NAVEGA and viaje.recorrido > 0.0, "la barca sube sola por el río")
	await _empujar("mover_izquierda", 2.0)
	var local: Vector2 = _maisha().global_position - viaje.position
	_comprobar(cubierta.grow(1).has_point(local), "por mucho que ande, Maisha no se sale de la cubierta")
	_comprobar(Sonido.musica_actual == "orilla", "suena la barcarola de la Orilla")

	print("La llegada al muelle de la Gruta:")
	viaje.recorrido = viaje._largo - 40.0
	for i in 60:
		await _esperar(0.25)
		await _leer_dialogo()
		if Estado.tiene("travesia_hecha"):
			break
	await _esperar(0.5)
	_comprobar(Estado.tiene("travesia_hecha") and viaje.fase == viaje.Fase.ATRACADA, "atraca en el muelle de piedra")
	var p0 := _maisha().global_position
	await _empujar("mover_izquierda", 0.6)
	_comprobar(_maisha().global_position.distance_to(p0) > 20.0, "Maisha baja y anda por el muelle")
	var norte := _puerta("gruta")
	_comprobar(norte != null and norte.cerrada_hasta != "", "el camino de la Gruta de las Raíces, de momento cerrado")

	print("Volver al Embarcadero:")
	var vuelta: Node2D = null
	for n in viaje.get_children():
		if n.is_in_group("interactuables"):
			vuelta = n
	_maisha().global_position = vuelta.global_position + Vector2(-8, 0)
	await _esperar(0.3)
	vuelta.interactuar()
	await _esperar(0.3)
	await _leer_dialogo()
	for i in 200:
		if _escena() == "EmbarcaderoJunco" and not Estado.cambiando:
			break
		await get_tree().process_frame
	_comprobar(_escena() == "EmbarcaderoJunco", "desde la barca se vuelve al Embarcadero")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
