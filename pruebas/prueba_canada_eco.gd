extends Node
## Prueba automática de la Cañada del Eco (el quinto camino de Raíz): del Bosque Cobrizo hacia el Lago Espejo;
## la garganta de peña, Mbuzi y sus cencerros, la escala de cuerda que descuelga hasta la cornisa del quinto eco
## y el paso al lago, aún cerrado.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_canada_eco

const R := preload("res://scripts/combate/reglas_combate.gd")
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
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco",
			"visto/cuna_de_musgo", "bibi_conocida", "bibi_aldea_viva", "camino_bosque", "camino_cienaga",
			"visto/bosque_cobrizo", "bosque_llegada", "cobrizo_llegada"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("Del bosque a la Cañada del Eco:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/bosque_cobrizo.tscn")
	await _esperar(1.5)
	await _leer_dialogo()
	var oeste := _puerta("canada")
	_comprobar(oeste != null and oeste.destino == "canada_eco", "el bosque tiene una salida al oeste, a la Cañada del Eco")
	_maisha().global_position = oeste.global_position + Vector2(30, 0)
	await _cruzar("mover_izquierda", "CanadaEco")
	_comprobar(_escena() == "CanadaEco", "se llega a la Cañada del Eco")
	_comprobar(_maisha().global_position.distance_to(_puerta("bosque").punto_llegada()) < 4.0, "Maisha aparece al este, viniendo del bosque")
	await _esperar(2.5)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al llegar")
	await _leer_dialogo()

	print("La cañada:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	_comprobar(region.tam.x >= 140 * 16, "va de este a oeste: unas 3,5 pantallas de largo")
	var zonas := get_tree().get_nodes_in_group("zonas")
	_comprobar(zonas.size() == 1, "una zona corrupta en el ensanche del sur")
	_comprobar(region.secretos_total == 1, "un secreto al noroeste")
	var cencerros := get_tree().get_nodes_in_group("recogibles").filter(func(n: Node) -> bool: return n.objeto == "cencerro")
	_comprobar(cencerros.size() == 3, "tres cencerros de Mbuzi")
	var mbuzi: Node2D = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "mbuzi")[0]
	_comprobar(mbuzi != null, "Mbuzi, la cabra montés, junto a su aprisco")
	var escala: Node2D = get_tree().get_first_node_in_group("escalas")
	_comprobar(escala != null and not escala.descolgada(), "la escala de cuerda está enrollada arriba")
	for z in zonas:
		z.set("activa", false)          # (aquí no se pelea)

	print("La peña y la escala:")
	var maisha := _maisha()
	var pie := Vector2(104 * 16 + 16, 16 * 16)
	maisha.global_position = pie
	await _esperar(0.2)
	await _empujar("mover_arriba", 1.6)
	_comprobar(maisha.global_position.y > 12 * 16, "sin la escala no se sube a la cornisa (%.0f)" % maisha.global_position.y)
	maisha.global_position = Vector2(80 * 16, 22 * 16)
	await _esperar(0.2)
	await _empujar("mover_arriba", 1.6)
	_comprobar(maisha.global_position.y > 16 * 16, "las paredes de la garganta no dejan pasar (%.0f)" % maisha.global_position.y)

	print("Mbuzi y sus cencerros:")
	maisha.global_position = mbuzi.global_position + Vector2(0, 16)
	await _esperar(0.2)
	await _hablar_con(mbuzi)
	_comprobar(Estado.tiene("encargo_mbuzi") and Estado.tiene("mbuzi_conocida"), "Mbuzi pide sus tres cencerros")
	_comprobar(Misiones.activas().any(func(m: Dictionary) -> bool: return m["id"] == "cencerros_mbuzi"), "sale el encargo en el diario")
	for n in cencerros:
		maisha.global_position = n.global_position
		await _esperar(0.25)
	_comprobar(Estado.cuantos("cencerro") == 3, "se recogen al pasar (%d/3)" % Estado.cuantos("cencerro"))
	var sopas: int = Estado.cuantos("sopa")
	maisha.global_position = mbuzi.global_position + Vector2(0, 16)
	await _esperar(0.3)
	await _hablar_con(mbuzi)
	_comprobar(Estado.tiene("mbuzi_cencerros") and Estado.cuantos("cencerro") == 0, "se los entrega")
	_comprobar(Estado.cuantos("sopa") == sopas + 2, "y Mbuzi le da dos sopas")
	await _esperar(2.0)
	_comprobar(escala.descolgada(), "Mbuzi descuelga la escala (tramo a tramo)")
	maisha.global_position = pie
	await _esperar(0.2)
	await _empujar("mover_arriba", 2.5)
	_comprobar(maisha.global_position.y < 9 * 16, "por la escala se sube a la cornisa (%.0f)" % maisha.global_position.y)
	var eco: Node2D = get_tree().get_first_node_in_group("ecos_perdidos")
	_comprobar(eco != null and eco.global_position.y < 7 * 16, "arriba está la piedra del quinto eco")

	print("El paso al lago, cerrado:")
	var lago := _puerta("lago")
	_comprobar(lago != null and lago.destino == "lago_espejo" and lago.cerrada_hasta != "", "al oeste, el paso al Lago Espejo (cerrado)")
	maisha.global_position = lago.global_position + Vector2(30, 0)
	await _esperar(0.3)
	await _empujar("mover_izquierda", 1.2)
	await _esperar(0.3)
	_comprobar(_escena() == "CanadaEco" and not Estado.cambiando, "no deja pasar")
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "y Maisha piensa por qué")
	await _leer_dialogo()

	print("De vuelta al bosque:")
	maisha.global_position = _puerta("bosque").global_position + Vector2(-40, 0)
	await _cruzar("mover_derecha", "BosqueCobrizo")
	_comprobar(_escena() == "BosqueCobrizo", "por el este se vuelve al Bosque Cobrizo")
	_comprobar(_maisha().global_position.distance_to(_puerta("canada").punto_llegada()) < 4.0, "apareciendo por el oeste del bosque")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
