extends Node
## Prueba automática de Las Estanterías Colgantes (Sigilia): se llega desde Maandiko (al derretir la tinta de la
## salida del oeste), los huecos no se pisan, las escaleras rodantes se tienden, se van y tiran a Maisha si se van con
## ella encima, el tintero rabioso embiste y pringa, la cerradura de tinta, la ficha de Daftari y Daftari recupera su
## nombre en Maandiko.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_estanterias

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


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["cetro_recibido", "visto/cuna_de_musgo", "sigilo_fuego", "maandiko_llegada", "kalamu_conocida", "mapa_norte",
			"charco/maandiko/4,25/3"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("La llegada:")
	await _ir("estanterias_colgantes", "ciudad", "EstanteriasColgantes")
	_comprobar(_escena() == "EstanteriasColgantes" and Estado.tiene("estanterias_colgantes"), "se llega a Las Estanterías Colgantes por el este")
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("estanterias_llegada"), "Maisha ve los pisos y los huecos al llegar")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var escaleras := get_tree().get_nodes_in_group("escaleras_rodantes")
	_comprobar(escaleras.size() == 5, "cinco escaleras rodantes cruzan los huecos (%d)" % escaleras.size())
	_comprobar(get_tree().get_nodes_in_group("tinteros").size() >= 5, "tinteros rabiosos por los pisos")
	for t in get_tree().get_nodes_in_group("tinteros"):
		t.set_physics_process(false)
	for p in get_tree().get_nodes_in_group("paginas"):
		p.set_physics_process(false)

	print("Los huecos y las escaleras:")
	# un hueco sin escalera: no se puede pasar
	m.global_position = Vector2(30 * 16 + 8, 75 * 16)
	Input.action_press("mover_arriba")
	await _esperar(1.2)
	Input.action_release("mover_arriba")
	_comprobar(m.global_position.y > 73 * 16, "el hueco no se pisa (fuera de las escaleras)")
	# la escalera de abajo a la izquierda: tendida, se cruza
	var e: Node2D = null
	for x in escaleras:
		if (x as Node2D).position == Vector2(14, 74) * 16.0:
			e = x
	_comprobar(e != null, "la escalera del primer hueco")
	e.set_process(false)
	e.fase = e.Fase.TENDIDA
	e._poner_pared()
	await _esperar(0.2)
	m.global_position = e.global_position + Vector2(16, 10)
	Input.action_press("mover_arriba")
	await _esperar(1.4)
	Input.action_release("mover_arriba")
	_comprobar(m.global_position.y < 70 * 16, "con la escalera tendida, se cruza el hueco")
	# recogida: no se pasa
	e.fase = e.Fase.RECOGIDA
	e._poner_pared()
	await _esperar(0.2)
	m.global_position = e.global_position + Vector2(16, 10)
	Input.action_press("mover_arriba")
	await _esperar(1.2)
	Input.action_release("mover_arriba")
	_comprobar(m.global_position.y > 73 * 16, "con la escalera recogida, no")
	# si se va con Maisha encima, cae
	var vida0: int = m.vida
	e.fase = e.Fase.AVISO
	e._poner_pared()
	await _esperar(0.2)
	m.global_position = e.global_position + Vector2(16, -30)
	e._t = 2.0
	e.set_process(true)
	await _esperar(0.9)
	_comprobar(m.vida == vida0 - 1 and m.global_position.y > e.global_position.y, "si la escalera se va con Maisha encima, cae al piso de abajo y pierde una hoja")
	m.revivir(m.global_position)

	print("El tintero rabioso:")
	var tintero: CharacterBody2D = get_tree().get_nodes_in_group("tinteros")[0]
	tintero.set_physics_process(true)
	m.global_position = tintero.global_position + Vector2(-90, 0)
	await _esperar(0.1)
	var vida1: int = m.vida
	var embistio := false
	for i in 60:
		await _esperar(0.05)
		if tintero.fase == tintero.Fase.EMBESTIR:
			embistio = true
		if m.vida < vida1:
			break
	_comprobar(embistio, "si ve a Maisha en línea recta, embiste")
	_comprobar(m.vida < vida1, "y le hace daño")
	_comprobar(not tintero._manchas.is_empty(), "dejando manchas de tinta detrás")
	m.revivir(m.global_position)
	tintero.morir()
	await _esperar(0.5)
	_comprobar(int(Estado.extra.get("bestiario", {}).get("tintero", 0)) >= 1, "cuenta en el Bestiario")

	print("La cerradura y la ficha:")
	var cerradura: Node2D = null
	for ch in get_tree().get_nodes_in_group("charcos_tinta"):
		if ch.position == Vector2(7, 34) * 16.0 + Vector2(8, 14):
			cerradura = ch
	_comprobar(cerradura != null, "una cerradura de Tinta Quieta tapa la alcoba")
	for i in 3:
		m.global_position = cerradura.global_position + Vector2(26, 0)
		m.mirar(Vector2.LEFT)
		m.aliento = m.aliento_maximo()
		await _esperar(0.8)
		m.sigilo()
		await _esperar(0.5)
	await _esperar(0.7)
	_comprobar(not is_instance_valid(cerradura) or not cerradura.is_in_group("charcos_tinta"), "el fuego la derrite")
	var ficha: Node2D = null
	for r in get_tree().get_nodes_in_group("recogibles"):
		if r.objeto == "ficha_daftari":
			ficha = r
	m.global_position = ficha.global_position
	await _esperar(0.4)
	_comprobar(Estado.cuantos("ficha_daftari") == 1, "dentro, la ficha del Índice de Daftari")

	print("Daftari:")
	await _ir("maandiko", "estanterias", "Maandiko")
	var daftari: Node = null
	for a in get_tree().get_nodes_in_group("escribas"):
		if a.nombre == "daftari":
			daftari = a
	_comprobar(daftari != null and daftari.id == "escriba_blanco", "en Maandiko, Daftari está en blanco")
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	m.global_position = (daftari as Node2D).global_position + Vector2(-18, 6)
	daftari.interactuar()
	await _leer_dialogo()
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("daftari_nombre") and Estado.cuantos("ficha_daftari") == 0, "al darle su ficha, recupera el nombre")
	_comprobar(daftari.id == "escriba" and Estado.tiene("daftari_hablado"), "y el color, y la voz")

	print()
	print("RESULTADO: todo correcto" if _fallos == 0 else "RESULTADO: %d fallos" % _fallos)
	get_tree().quit(1 if _fallos else 0)
