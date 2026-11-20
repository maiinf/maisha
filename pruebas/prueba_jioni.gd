extends Node
## Prueba automática de Jioni, la Ciudad de los Faroles (el Valle del Ocaso): se llega por la escalera del Arco del
## Atardecer, Maisha piensa al llegar, Kibatari, los doce postes vacíos, los seis vecinos desvelados, colgar un Farol
## de la Hora (y que sin farol no se puede), que con cada farol descansa un vecino (y abre su casa o su puesto), la
## misión, las salidas (cerradas: aún no existen) y la Puerta del Horizonte sellada, y que todo queda al volver.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_jioni

const POSTE := preload("res://scripts/mundo/ocaso/poste_farol.gd")

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
	for i in 200:
		if not dialogo.hablando:
			await _esperar(0.4)
			if not dialogo.hablando:
				return
		dialogo.pasar()
		await _esperar(0.08)


func _ir(escena: String, puerta: String, nombre: String) -> void:
	Estado.ir_a(escena, puerta)
	for i in 300:
		if _escena() == nombre and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(1.0)


func _vecino(id: String) -> Node2D:
	for v in get_tree().get_nodes_in_group("aldeanos"):
		if v.id == id and not v.is_queued_for_deletion():
			return v
	return null


func _hablar(m: CharacterBody2D, quien: Node2D) -> void:
	m.global_position = quien.global_position + Vector2(0, 14)
	quien.interactuar()
	await _leer_dialogo()


func _puerta(id: String) -> Node2D:
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == id:
			return p
	return null


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "asterhaul_libre", "nexo_despierto", "mirador_ocaso", "arco_atardecer_abierto"]:
		Estado.marcar(marca)
	Estado.dar("farol_hora", 2)
	Estado.jugando = true

	print("Llegar a Jioni:")
	_comprobar(Misiones.estado(Misiones.buscar("jioni")) == "activa", "con el Arco abierto aparece la misión")
	await _ir("jioni", "mirador", "Jioni")
	_comprobar(_escena() == "Jioni", "se llega a Jioni por la escalera (%s)" % _escena())
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.y < 5.0 * 16.0, "Maisha aparece arriba, en la escalera (%s)" % m.global_position)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("jioni_llegada"), "piensa al llegar")
	var postes := get_tree().get_nodes_in_group("postes_farol")
	_comprobar(postes.size() == 12 and postes.all(func(p: Node) -> bool: return not p.encendido()), "doce postes en la plaza, todos vacíos")
	_comprobar(get_tree().get_nodes_in_group("vecinos_jioni").size() == 6 and _vecino("kikombe_desvelado") != null and _vecino("ndoto_desvelado") != null, "seis vecinos, todos desvelados")

	print("Kibatari:")
	var kibatari := _vecino("kibatari")
	_comprobar(kibatari != null, "Kibatari está en la plaza")
	await _hablar(m, kibatari)
	_comprobar(Estado.tiene("kibatari_conocido"), "Kibatari se presenta")

	print("Colgar los Faroles de la Hora:")
	var p0: Node2D = postes[0]
	var p5: Node2D = postes[5]
	m.global_position = p0.global_position + Vector2(0, 14)
	p0.interactuar()
	await _esperar(0.8)
	_comprobar(p0.encendido() and Estado.cuantos("farol_hora") == 1 and POSTE.colgados() == 1, "se cuelga un farol en un poste")
	_comprobar(Estado.tiene("jioni/descansa_kikombe"), "y Kikombe, por fin, descansa")
	_comprobar(_vecino("kikombe") != null and _vecino("kikombe_desvelado") == null, "ya sin ojeras")
	p5.interactuar()
	await _esperar(0.8)
	_comprobar(POSTE.colgados() == 2 and Estado.cuantos("farol_hora") == 0 and Estado.tiene("jioni/descansa_kesho"), "el segundo farol: descansa Kesho")
	p0.interactuar()
	await _leer_dialogo()
	_comprobar(POSTE.colgados() == 2, "un poste que ya luce no se toca")
	var p3: Node2D = postes[3]
	p3.interactuar()
	await _leer_dialogo()
	_comprobar(not p3.encendido(), "sin farol no se puede colgar nada")
	_comprobar(not Estado.tiene("jioni/descansa_mto"), "y los demás siguen desvelados")

	print("Kibatari cuenta los tres caminos:")
	await _hablar(m, _vecino("kibatari"))
	_comprobar(Estado.tiene("kibatari_caminos"), "Kibatari habla de las Dunas, el Jardín y la Calzada")
	_comprobar(Misiones.estado(Misiones.buscar("jioni")) == "hecha", "la misión, hecha (%s)" % Misiones.estado(Misiones.buscar("jioni")))

	print("Las salidas:")
	for id in ["dunas", "jardin", "calzada", "horizonte"]:
		_comprobar(_puerta(id) != null, "está la salida «%s»" % id)
	_comprobar(_puerta("horizonte").cerrada_hasta == "tres_pesos", "la Puerta del Horizonte, sellada hasta tener las tres pesas")

	print("Al volver, todo sigue igual:")
	await _ir("mirador_ocaso", "jioni", "MiradorOcaso")
	_comprobar(_escena() == "MiradorOcaso", "se vuelve al Mirador por el Arco")
	await _ir("jioni", "mirador", "Jioni")
	_comprobar(get_tree().get_nodes_in_group("postes_farol").filter(func(p: Node) -> bool: return p.encendido()).size() == 2, "los dos faroles siguen colgados")
	_comprobar(_vecino("kikombe") != null and _vecino("kesho") != null and _vecino("mto_desvelado") != null, "Kikombe y Kesho descansan; los demás, no")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
