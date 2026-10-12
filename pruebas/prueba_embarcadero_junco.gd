extends Node
## Prueba automática del Embarcadero Junco: se sube desde la Orilla de Juncos tras el sexto eco; el pueblo de barqueros
## (casas de juncos, grúa, almacén), el transbordador varado, las zonas y los secretos, Bata de piedra junto a la
## dársena (despierta al purgarla y se va a su transbordador) y el paso de La Travesía, aún cerrado.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_embarcadero_junco

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


func _fijos_con(dibujo: String) -> Array:
	var r: Array = []
	for n in get_tree().get_nodes_in_group("entidades_fijas") + get_tree().current_scene.get_node("Entidades").get_children():
		for h in n.get_children():
			if h is Sprite2D and h.texture and h.texture.resource_path.ends_with(dibujo):
				r.append(h)
	return r


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco",
			"visto/cuna_de_musgo", "camino_cienaga", "visto/cienaga_quieta", "cienaga_llegada", "orilla_llegada",
			"eco/orilla_juncos"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("De la Orilla al Embarcadero Junco:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/orilla_juncos.tscn")
	await _esperar(1.5)
	await _leer_dialogo()
	_maisha().global_position = _puerta("embarcadero").global_position + Vector2(0, 30)
	await _cruzar("mover_arriba", "EmbarcaderoJunco")
	_comprobar(_escena() == "EmbarcaderoJunco", "con el sexto eco escuchado, se sube al Embarcadero Junco")
	_comprobar(_maisha().global_position.distance_to(_puerta("orilla").punto_llegada()) < 4.0, "Maisha aparece al sur, viniendo de la Orilla")
	await _esperar(2.5)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al llegar")
	await _leer_dialogo()
	_comprobar(Sonido.musica_actual == "orilla", "suena la música del río")

	print("El pueblo de barqueros:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	_comprobar(region.tam == Vector2(96, 72) * 16, "un lugar de 96×72 casillas")
	_comprobar(get_tree().get_nodes_in_group("zonas").size() == 3, "tres zonas corruptas")
	_comprobar(region.secretos_total == 3, "tres secretos")
	_comprobar(_fijos_con("casa_juncos.png").size() >= 6, "casas de juncos sobre pilotes (%d)" % _fijos_con("casa_juncos.png").size())
	_comprobar(_fijos_con("grua.png").size() == 1 and _fijos_con("almacen.png").size() == 1, "la grúa rota y el almacén")
	var barca: Array = _fijos_con("transbordador.png")
	_comprobar(barca.size() == 1 and barca[0].frame == 0, "el transbordador, varado")

	print("La Travesía, cerrada:")
	var norte := _puerta("travesia")
	_comprobar(norte != null and norte.destino == "la_travesia" and norte.cerrada_hasta == "transbordador_listo", "al norte, La Travesía (cerrada hasta que el transbordador navegue)")
	_maisha().global_position = norte.global_position + Vector2(0, 30)
	await _esperar(0.3)
	await _empujar("mover_arriba", 1.2)
	await _esperar(0.3)
	_comprobar(_escena() == "EmbarcaderoJunco" and get_tree().get_first_node_in_group("dialogo").hablando, "no deja pasar, y Maisha piensa por qué")
	await _leer_dialogo()

	print("Bata, el pato barquero:")
	var estatua: Node2D = null
	for e in get_tree().get_nodes_in_group("estatuas"):
		if e.id == "bata":
			estatua = e
	_comprobar(estatua != null, "Bata está de piedra junto a la dársena")
	var darsena: Node2D = null
	for z in get_tree().get_nodes_in_group("zonas"):
		if z.get_meta("clave") == "1":
			darsena = z
	darsena._al_romper_nucleo()
	var bata: Node2D = null
	for i in 60:
		await _esperar(0.3)
		await _leer_dialogo()
		for n in get_tree().get_nodes_in_group("aldeanos"):
			if n.get("id") == "bata":
				bata = n
		if bata:
			break
	_comprobar(Estado.tiene("rescatado_bata"), "al purgar la dársena, Bata vuelve a la vida")
	var sitio := Vector2(region.get("_sitio_viajero"))
	_comprobar(bata != null and bata.global_position.distance_to(sitio) < 4.0, "y se va a su transbordador, en vez de a la aldea")
	await _leer_dialogo()
	_maisha().global_position = bata.global_position + Vector2(-18, 0)
	await _esperar(0.3)
	await _hablar_con(bata)
	_comprobar(Estado.tiene("bata_conocido"), "Bata cuenta lo del transbordador y la Gruta de las Raíces")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
