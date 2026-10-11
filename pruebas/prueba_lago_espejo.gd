extends Node
## Prueba automática del Lago Espejo: el agua turbia mientras vive Kambare, la quietud que vuelve el lago espejo,
## los puentes del reflejo (que se encienden, se cruzan y se apagan si el agua tiembla) y la vuelta a la Cañada.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_lago_espejo

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


func _quieta(segundos: float) -> void:
	# Maisha no toca nada durante un rato
	for i in int(segundos / 0.05):
		await _esperar(0.05)
		var d := get_tree().get_first_node_in_group("dialogo")
		if d.hablando:
			await _leer_dialogo()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco",
			"visto/cuna_de_musgo", "camino_bosque", "camino_cienaga", "eco/canada_eco", "canada_llegada"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("Llegar al lago:")
	Estado.llegada = "lago"
	get_tree().change_scene_to_file("res://escenas/mundo/canada_eco.tscn")
	await _esperar(1.5)
	_maisha().global_position = _puerta("lago").global_position + Vector2(40, 0)
	await _cruzar("mover_izquierda", "LagoEspejo")
	_comprobar(_escena() == "LagoEspejo", "desde la Cañada se llega al Lago Espejo")
	_comprobar(_maisha().global_position.distance_to(_puerta("canada").punto_llegada()) < 4.0, "Maisha aparece al este")
	await _esperar(2.5)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al llegar")
	await _leer_dialogo()
	_comprobar(Estado.tiene("visto/lago_espejo"), "el lago queda apuntado en el mapa")

	print("El agua turbia:")
	var espejo: Node2D = get_tree().get_first_node_in_group("espejo_lago")
	var puentes := get_tree().get_nodes_in_group("puentes_reflejo")
	_comprobar(espejo != null and espejo.turbio(), "mientras vive Kambare, el agua está turbia")
	_comprobar(puentes.size() == 2, "hay dos puentes del reflejo (a la isla y al islote)")
	var largo: Node2D = puentes[0] if puentes[0].casillas.size() > puentes[1].casillas.size() else puentes[1]
	_comprobar(not largo.cruzable(), "y ninguno es real todavía")
	for z in get_tree().get_nodes_in_group("zonas"):
		z.set("activa", false)          # (aquí no se pelea)
	var maisha := _maisha()
	var pie := Vector2(46 * 16, 48 * 16 + 4)        # al pie del puente largo, en la orilla sur
	maisha.global_position = pie
	await _quieta(R.QUIETUD_SEGUNDOS + 1.0)
	_comprobar(espejo.get("_aviso_turbio"), "Maisha intenta calmarla y piensa que algo grande remueve el fondo")
	_comprobar(not espejo.espejo, "turbia, no se calma por mucho que Maisha espere")
	await _empujar("mover_arriba", 1.2)
	_comprobar(maisha.global_position.y > 47 * 16, "y el puente no se puede pisar (%.0f)" % maisha.global_position.y)

	print("Sin Kambare, la quietud:")
	Estado.marcar("kambare_vencido")
	await _esperar(3.3)
	_comprobar(not espejo.turbio(), "al vencer a Kambare, el agua se aclara")
	maisha.global_position = pie
	await _esperar(0.5)
	await _quieta(R.QUIETUD_SEGUNDOS + 0.6)
	_comprobar(espejo.espejo, "quieta junto al agua, el lago se vuelve espejo")
	_comprobar(Estado.tiene("lago_espejo_visto"), "la primera vez, Maisha ve el puente en el reflejo")
	await _quieta(1.5)
	_comprobar(largo.cruzable(), "el puente se enciende tabla a tabla y se hace real")
	await _empujar("mover_arriba", 4.5)
	_comprobar(maisha.global_position.y < 31 * 16, "y se cruza andando hasta la isla (%.0f)" % maisha.global_position.y)
	_comprobar(espejo.espejo, "andar no rompe el espejo")

	print("El agua tiembla:")
	maisha.global_position = Vector2(46 * 16, 40 * 16)
	await _esperar(0.2)
	maisha.golpear()
	await _esperar(0.4)
	_comprobar(espejo.espejo, "encima del puente, ni un golpe lo apaga (no se cae al agua)")
	maisha.global_position = pie
	await _esperar(0.3)
	maisha.golpear()
	await _esperar(0.3)
	_comprobar(not espejo.espejo, "en la orilla, un golpe hace temblar el agua")
	await _esperar(2.8)
	_comprobar(not largo.cruzable(), "y el puente se apaga poco a poco")

	print("De vuelta a la cañada:")
	maisha.global_position = _puerta("canada").global_position + Vector2(-40, 0)
	await _cruzar("mover_derecha", "CanadaEco")
	_comprobar(_escena() == "CanadaEco", "por el este se vuelve a la Cañada del Eco")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
