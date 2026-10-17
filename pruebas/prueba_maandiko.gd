extends Node
## Prueba automática de Maandiko, la Ciudad-Archivo (Sigilia): se llega desde el Paso de la Escarcha, están la plaza
## con su fuente, el Gran Archivo, las casas y los vecinos (Kalamu, Wino, Mauti, Taa y los escribas en blanco), Kalamu
## da el trozo del norte del mapa, los charcos de Tinta Quieta tapan las salidas y se derriten con el sigilo, la
## música y la misión.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_maandiko

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _escena() -> String:
	var e := get_tree().current_scene
	return e.name if e else ""


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 160:
		if not dialogo.hablando:
			await _esperar(0.3)
			if not dialogo.hablando:
				return
		dialogo.pasar()
		await _esperar(0.08)


func _vecino(id: String) -> Node:
	for a in get_tree().get_nodes_in_group("aldeanos"):
		if a.id == id:
			return a
	return null


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["cetro_recibido", "visto/cuna_de_musgo", "primer_arbol_libre", "mauti_libre", "paso_escarcha",
			"escarcha_llegada", "escarcha_racha", "taa_nombre", "sigilo_fuego", "puerta_sellada_abierta"]:
		Estado.marcar(m)
	Estado.jugando = true
	_comprobar(Misiones.estado(Misiones.buscar("maandiko")) == "activa", "con la Puerta Sellada abierta aparece la misión «La Ciudad-Archivo»")

	print("La llegada:")
	Estado.ir_a("maandiko", "paso")
	for i in 300:
		if _escena() == "Maandiko" and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(1.0)
	_comprobar(_escena() == "Maandiko" and Estado.tiene("maandiko"), "se llega a Maandiko por el sur")
	_comprobar(Sonido.musica_actual == "maandiko", "suena «Las calles del Índice»")
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("maandiko_llegada"), "Maisha ve la ciudad en blanco al llegar")

	print("La ciudad:")
	var region := get_tree().current_scene.get_node("Region")
	var filas: PackedStringArray = region._filas
	var cuenta := {}
	for f in filas:
		for c in f:
			cuenta[c] = cuenta.get(c, 0) + 1
	_comprobar(cuenta.get("ḃ", 0) == 1 and cuenta.get("ḟ", 0) == 1, "el Gran Archivo y la fuente de la plaza")
	_comprobar(cuenta.get("ḣ", 0) >= 5 and cuenta.get("ḱ", 0) == 1, "las casas de los escribas y la de Kalamu")
	_comprobar(cuenta.get("ṗ", 0) >= 4 and cuenta.get("ṫ", 0) == 1, "los puestos del mercado y el taller de Taa")
	for id in ["kalamu", "mauti", "wino", "taa"]:
		_comprobar(_vecino(id) != null, "%s está en la ciudad" % id)
	var blancos := get_tree().get_nodes_in_group("aldeanos").filter(func(a: Node) -> bool: return a.id == "escriba_blanco")
	_comprobar(blancos.size() >= 5, "escribas en blanco por las calles (%d)" % blancos.size())

	print("Kalamu y el mapa:")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var kalamu := _vecino("kalamu")
	m.global_position = (kalamu as Node2D).global_position + Vector2(-18, 6)
	kalamu.interactuar()
	await _leer_dialogo()
	await _esperar(0.5)
	_comprobar(Estado.tiene("mapa_norte") and Estado.tiene("kalamu_conocida"), "Kalamu da el trozo del norte del mapa")
	_comprobar(Misiones.estado(Misiones.buscar("maandiko")) == "hecha", "y la misión se cumple")

	print("La Tinta Quieta de las salidas:")
	var charcos := get_tree().get_nodes_in_group("charcos_tinta")
	_comprobar(charcos.size() == 3, "tres charcos tapan las salidas (%d)" % charcos.size())
	var charco: Node2D = charcos[0]
	for i in 3:
		m.global_position = charco.global_position + Vector2(24, 0)
		m.mirar(Vector2.LEFT)
		m.aliento = m.aliento_maximo()
		await _esperar(0.8)
		m.sigilo()
		await _esperar(0.5)
	await _esperar(0.7)
	_comprobar(not is_instance_valid(charco) or not charco.is_in_group("charcos_tinta"), "con tres sigilos de fuego, el charco se derrite")
	var marca := "charco/maandiko/4,25/3"
	_comprobar(Estado.tiene(marca), "y no vuelve")

	print()
	print("RESULTADO: todo correcto" if _fallos == 0 else "RESULTADO: %d fallos" % _fallos)
	get_tree().quit(1 if _fallos else 0)
