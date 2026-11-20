extends Node
## Prueba automática de El Mirador del Ocaso (el Valle del Ocaso): el arco del sur del Kitovu (frío hasta que el
## Cetro del Nexo despierta), se llega por el norte, Maisha piensa al llegar, la sombra del primer obelisco sostiene
## sobre el vacío y fuera de ella se cae, el reloj atascado hasta hablar con Mwanga, el sol que gira (y las sombras
## con él), los Kivuli (invulnerables en penumbra, deslumbrados y vencibles al sol), el Farol de la Hora, los dos
## espejos y el Arco del Atardecer, que todo queda como estaba al volver, y la puerta del Kitovu.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_mirador_ocaso

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


func _sitio(x: int, y: int) -> Vector2:
	return Vector2(x, y) * 16.0 + Vector2(8, 14)


func _cerca(grupo: String, x: int, y: int) -> Node2D:
	var mejor: Node2D = null
	for n in get_tree().get_nodes_in_group(grupo):
		if mejor == null or (n as Node2D).global_position.distance_to(_sitio(x, y)) < mejor.global_position.distance_to(_sitio(x, y)):
			mejor = n
	return mejor


func _puerta(id: String) -> Node2D:
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == id:
			return p
	return null


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "asterhaul_libre"]:
		Estado.marcar(marca)
	Estado.jugando = true

	print("El arco del sur del Kitovu:")
	await _ir("kitovu", "desfiladero", "Kitovu")
	var arco := _puerta("ocaso")
	_comprobar(arco != null and arco.destino == "mirador_ocaso" and arco.cerrada_hasta == "nexo_despierto", "en el Kitovu está el arco al Mirador, cerrado hasta que despierte el Cetro del Nexo")
	Estado.marcar("nexo_despierto")
	_comprobar(Misiones.estado(Misiones.buscar("mirador_ocaso")) == "activa", "con el cetro despierto aparece la misión (%s)" % Misiones.estado(Misiones.buscar("mirador_ocaso")))

	print("Llegar al Mirador:")
	await _ir("mirador_ocaso", "norte", "MiradorOcaso")
	_comprobar(_escena() == "MiradorOcaso", "se llega a El Mirador del Ocaso (%s)" % _escena())
	var escena := get_tree().current_scene
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.y < 4.0 * 16.0, "Maisha aparece en la puerta del norte (%s)" % m.global_position)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("mirador_llegada"), "piensa al llegar")
	var sol: Node2D = escena.sol
	_comprobar(sol.hora == sol.OESTE, "el sol empieza al oeste")
	_comprobar(get_tree().get_nodes_in_group("obeliscos").size() == 4 and get_tree().get_nodes_in_group("relojes_sol").size() == 2, "hay cuatro obeliscos y dos relojes de sol")

	print("Las sombras-puente:")
	m.set("_invulnerable", 900.0)
	m.global_position = _sitio(48, 6)
	await _esperar(0.5)
	_comprobar(not escena.get_node("Vacio").cayendo, "la sombra del primer obelisco (sol al oeste) sostiene sobre el vacío")
	m.global_position = _sitio(40, 9)
	await _esperar(0.3)
	m.set("_invulnerable", 0.0)
	var vida: int = m.vida
	m.global_position = _sitio(40, 12)
	await _esperar(0.3)
	_comprobar(escena.get_node("Vacio").cayendo, "fuera de la sombra, el vacío: cae")
	await _esperar(2.4)
	_comprobar(m.vida == vida - 1 and m.global_position.distance_to(_sitio(40, 9)) < 24.0 and m.puede_actuar, "pierde una hoja y vuelve al último suelo firme (vida %d → %d, %s)" % [vida, m.vida, m.global_position])
	m.set("_invulnerable", 900.0)

	print("El Farol de la Hora del Balcón:")
	m.global_position = _sitio(65, 6)
	await _esperar(0.6)
	_comprobar(Estado.tiene("farol/mirador_1") and Estado.cuantos("farol_hora") == 1, "se recoge el primer Farol de la Hora")

	print("Los Kivuli:")
	var kivuli := _cerca("kivulis", 61, 9)
	_comprobar(get_tree().get_nodes_in_group("kivulis").size() == 4, "hay cuatro Kivuli")
	_comprobar(not kivuli.al_sol() and not kivuli.recibir_golpe(1, Vector2.RIGHT) and kivuli.vida == 3, "con el sol al oeste, el del Balcón está en penumbra: el cetro lo atraviesa")

	print("Mwanga y el Reloj de Sol:")
	var reloj := _cerca("relojes_sol", 43, 23)
	_comprobar(not reloj.recibir_golpe(1, Vector2.UP) and sol.hora == sol.OESTE, "antes de hablar con Mwanga, el reloj está atascado")
	await _leer_dialogo()
	var mwanga := _cerca("aldeanos", 37, 21)
	_comprobar(mwanga != null and mwanga.id == "mwanga", "Mwanga está en la plaza")
	m.global_position = mwanga.global_position + Vector2(0, 14)
	mwanga.interactuar()
	await _leer_dialogo()
	_comprobar(Estado.tiene("mwanga_reloj"), "Mwanga enseña a girar los relojes")
	_comprobar(reloj.recibir_golpe(1, Vector2.UP) and sol.hora == sol.SUR, "un golpe al reloj: el sol, al sur")
	_comprobar(Estado.tiene("mirador/sol_sur"), "y lo apunta la misión")
	_comprobar(sol.firme(_sitio(39, 33)) and not sol.firme(_sitio(48, 6)), "la sombra del Arco sube a la plaza; la de la entrada ya no cruza")
	reloj.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.hora == sol.ESTE and sol.firme(_sitio(24, 27)), "otro golpe: sol al este, y la sombra del oeste cruza a las Terrazas")
	await _esperar(0.3)
	_comprobar(kivuli.al_sol(), "con el sol al este, al Kivuli del Balcón le da de lleno")
	await _esperar(0.3)
	_comprobar(kivuli.fase == kivuli.Fase.DESLUMBRADO, "y se queda deslumbrado")
	for i in 3:
		kivuli.recibir_golpe(1, Vector2.RIGHT)
	await _esperar(0.6)
	_comprobar(not is_instance_valid(kivuli) or kivuli.is_queued_for_deletion() or not kivuli.is_in_group("kivulis"), "tres golpes al sol y se deshace")
	_comprobar(int(Estado.extra.get("bestiario", {}).get("kivuli_menor", 0)) == 1, "y cuenta en el Bestiario")

	print("Las Terrazas y el secreto:")
	m.global_position = _sitio(24, 27)
	await _esperar(0.4)
	_comprobar(not escena.get_node("Vacio").cayendo, "Maisha cruza a las Terrazas por la sombra")
	var reloj2 := _cerca("relojes_sol", 12, 28)
	reloj2.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.hora == sol.OESTE and _cerca("kivulis", 8, 22).al_sol(), "el 2.º reloj: sol al oeste, los Kivuli de las Terrazas al sol")
	reloj2.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.hora == sol.SUR and sol.firme(_sitio(11, 12)), "y al sur, la sombra que sube al secreto")
	m.global_position = _sitio(11, 12)
	await _esperar(0.3)
	m.global_position = _sitio(11, 5)
	await _esperar(0.6)
	_comprobar(not escena.get_node("Vacio").cayendo and Estado.tiene("farol/mirador_2") and Estado.cuantos("farol_hora") == 2, "el segundo Farol de la Hora, en el secreto")

	print("Los espejos y el Arco del Atardecer:")
	var arco_paso := _puerta("jioni")
	m.global_position = _sitio(39, 33)
	await _esperar(0.3)
	_comprobar(not escena.get_node("Vacio").cayendo, "con el sol al sur, la sombra del Arco baja de la plaza")
	var a := _cerca("espejos", 34, 42)
	var b := _cerca("espejos", 48, 42)
	_comprobar(not a.encendido and not b.encendido and escena.espejos_encendidos() == 0, "los dos espejos, apagados")
	b.recibir_golpe(1, Vector2.UP)
	_comprobar(b.lado == 3 and not b.encendido, "el segundo mira al primero, pero el primero no tiene luz")
	a.recibir_golpe(1, Vector2.UP)
	a.recibir_golpe(1, Vector2.UP)
	_comprobar(a.lado == 2 and a.encendido, "el primero, al sur: mira al sol y se enciende")
	_comprobar(b.encendido and Estado.tiene("arco_atardecer_abierto"), "el segundo coge su luz y el Arco del Atardecer se abre")
	_comprobar(Misiones.estado(Misiones.buscar("mirador_ocaso")) == "hecha", "la misión, hecha (%s)" % Misiones.estado(Misiones.buscar("mirador_ocaso")))
	_comprobar(arco_paso != null and arco_paso.destino == "jioni", "el arco lleva a Jioni")

	print("Al volver, todo sigue igual:")
	await _ir("kitovu", "ocaso", "Kitovu")
	await _ir("mirador_ocaso", "norte", "MiradorOcaso")
	escena = get_tree().current_scene
	_comprobar(escena.sol.hora == 1, "el sol sigue al sur")
	_comprobar(_cerca("espejos", 34, 42).lado == 2 and _cerca("espejos", 48, 42).lado == 3 and escena.espejos_encendidos() == 2, "los espejos, como se dejaron")
	_comprobar(get_tree().get_nodes_in_group("recogibles").filter(func(r: Node) -> bool: return r.get("objeto") == "farol_hora").is_empty(), "los faroles ya recogidos no vuelven")

	print("La puerta del Kitovu:")
	await _ir("kitovu", "ocaso", "Kitovu")
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	arco = _puerta("ocaso")
	_comprobar(arco != null and m.global_position.distance_to(arco.global_position) < 48.0, "se vuelve por el arco del sur (%s)" % m.global_position)

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
