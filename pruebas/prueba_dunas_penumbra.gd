extends Node
## Prueba automática de Las Dunas de Penumbra (el Valle del Ocaso): se llega desde Jioni por el oeste, Maisha piensa
## al llegar, la arena movediza hunde, las Velas de Sombra solo dan sombra con el sol en la tela (y un golpe las
## gira), los Relojes, el Oasis secreto y su farol, los espejos semienterrados (la Carga los saca) y el puente de
## cristal, Kivuli (enterrado no se le toca; en su sombra tampoco; al girar el sol se vuelca y entonces sí), la Pesa
## del Oeste, la misión, y que todo queda como estaba al volver.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_dunas_penumbra

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


func _cargar(m: CharacterBody2D, algo: Node2D, desde: Vector2) -> bool:
	m.global_position = algo.global_position + desde
	m.mirar(-desde.normalized())
	m.aliento = m.aliento_maximo()
	m.set("_espera_carga", 0.0)
	var si: bool = m.carga()
	await _esperar(0.6)
	return si


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "asterhaul_libre", "nexo_despierto", "mirador_ocaso",
			"arco_atardecer_abierto", "jioni", "kibatari_conocido", "kibatari_caminos", "mwanga_reloj", "carga_sismica", "arte_tierra"]:
		Estado.marcar(marca)
	Estado.extra["sol"] = 0
	Estado.jugando = true
	_comprobar(Misiones.estado(Misiones.buscar("dunas_penumbra")) == "activa", "con los caminos de Kibatari aparece la misión")

	print("Llegar a las Dunas:")
	await _ir("dunas_penumbra", "jioni", "DunasPenumbra")
	_comprobar(_escena() == "DunasPenumbra", "se llega a Las Dunas de Penumbra (%s)" % _escena())
	var escena := get_tree().current_scene
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.x > 66.0 * 16.0, "Maisha aparece al este, junto a la puerta de Jioni (%s)" % m.global_position)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("dunas_llegada"), "piensa al llegar")
	var sol: Node2D = escena.sol
	var vacio: Node = escena.get_node("Vacio")
	_comprobar(vacio.hundir, "aquí la arena hunde (no se cae)")

	print("La arena movediza y la primera Vela:")
	_comprobar(not sol.firme(_sitio(52, 27)), "con el sol al oeste, la vela de cara no echa sombra hacia la Meseta")
	m.set("_invulnerable", 0.0)
	m.global_position = _sitio(64, 27)
	await _esperar(0.3)
	var vida: int = m.vida
	m.global_position = _sitio(56, 27)
	await _esperar(0.3)
	_comprobar(vacio.cayendo, "pisar la arena movediza: se hunde")
	await _esperar(2.6)
	_comprobar(m.vida == vida - 1 and m.global_position.x > 60.0 * 16.0 and m.puede_actuar, "pierde una hoja y vuelve a la roca (%s)" % m.global_position)
	m.set("_invulnerable", 900.0)
	var reloj := _cerca("relojes_sol", 66, 24)
	reloj.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.hora == 1 and not sol.firme(_sitio(52, 27)), "sol al sur: la vela le da de lado y tampoco echa sombra")
	reloj.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.hora == 2 and sol.firme(_sitio(52, 27)) and sol.firme(_sitio(47, 28)), "sol al este: la sombra de la vela cruza hasta la Meseta")
	var vela1 := _cerca("velas_sombra", 60, 27)
	vela1.recibir_golpe(1, Vector2.LEFT)
	_comprobar(vela1.de_canto and not sol.firme(_sitio(52, 27)), "un golpe la pone de canto: la sombra se va")
	vela1.recibir_golpe(1, Vector2.LEFT)
	_comprobar(not vela1.de_canto and sol.firme(_sitio(52, 27)), "otro golpe, de cara otra vez")
	m.global_position = _sitio(52, 27)
	await _esperar(0.4)
	m.global_position = _sitio(44, 27)
	await _esperar(0.4)
	_comprobar(not vacio.cayendo, "se cruza a la Meseta por la sombra")

	print("Los Kivuli excavadores:")
	var bicho := _cerca("kivulis", 43, 31)
	_comprobar(get_tree().get_nodes_in_group("kivulis").size() == 2, "hay dos Kivuli en la Meseta")
	_comprobar(bicho.al_sol(), "con el sol al este, al de la mitad este le da de lleno")

	print("El Oasis secreto:")
	var reloj2 := _cerca("relojes_sol", 42, 22)
	reloj2.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.hora == 0, "el Reloj de la Meseta: sol al oeste")
	reloj2.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.hora == 1 and not sol.firme(_sitio(38, 14)), "sol al sur: la vela del norte está de cara y no da sombra hacia el Oasis")
	_comprobar(sol.firme(_sitio(39, 39)), "pero la del Cañón, de canto, sí sube hasta la Meseta")
	var vela2 := _cerca("velas_sombra", 38, 18)
	vela2.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.firme(_sitio(38, 14)), "de canto: su sombra sube al Oasis")
	m.global_position = _sitio(38, 14)
	await _esperar(0.3)
	m.global_position = _sitio(38, 5)
	await _esperar(0.6)
	_comprobar(not vacio.cayendo and Estado.tiene("farol/dunas_1"), "el Farol de la Hora del Oasis")

	print("Los espejos del Cañón y el puente de cristal:")
	m.global_position = _sitio(39, 40)
	await _esperar(0.3)
	m.global_position = _sitio(39, 49)
	await _esperar(0.6)
	_comprobar(not vacio.cayendo and Estado.tiene("farol/dunas_2"), "se baja al Cañón por la sombra y está su farol")
	var a := _cerca("espejos", 32, 47)
	var b := _cerca("espejos", 46, 47)
	_comprobar(a.enterrado() and b.enterrado() and not a.recibir_golpe(1, Vector2.UP), "los dos espejos, enterrados: el cetro no los mueve")
	_comprobar(await _cargar(m, a, Vector2(24, 0)) and not a.enterrado(), "una Carga saca el primero de la arena")
	await _cargar(m, b, Vector2(-24, 0))
	_comprobar(not b.enterrado(), "y otra, el segundo")
	b.recibir_golpe(1, Vector2.UP)
	a.recibir_golpe(1, Vector2.UP)
	a.recibir_golpe(1, Vector2.UP)
	_comprobar(a.encendido and b.encendido, "el primero mira al sol y el segundo al primero: los dos encendidos")
	_comprobar(escena.puente.hecho() and escena.puente.firme(_sitio(27, 27)), "el rayo funde la arena en un puente de cristal")

	print("Kivuli, el Alacrán de Reloj de Arena:")
	var kivuli: Node2D = escena.kivuli
	_comprobar(kivuli != null and kivuli.fase == kivuli.Fase.DORMIDO, "Kivuli duerme bajo el Cráter")
	m.global_position = _sitio(27, 27)
	await _esperar(0.3)
	m.global_position = _sitio(13, 26)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(kivuli.fase != kivuli.Fase.DORMIDO and Estado.tiene("kivuli_visto"), "al entrar en el Cráter, despierta")
	_comprobar(not kivuli.recibir_golpe(1, Vector2.UP), "enterrado no hay forma de darle")
	for i in 80:
		if kivuli.fase == kivuli.Fase.ACECHA or kivuli.fase == kivuli.Fase.AVISA:
			break
		await _esperar(0.1)
	_comprobar(kivuli.fase in [kivuli.Fase.ACECHA, kivuli.Fase.AVISA] and sol.en_sombra(kivuli.global_position), "emerge en una sombra")
	_comprobar(not kivuli.recibir_golpe(1, Vector2.UP) and kivuli.vida == 9, "en su sombra, el cetro rebota")
	var golpes := 0
	for vuelta in 4:
		for i in 80:
			if kivuli.fase == kivuli.Fase.ACECHA or kivuli.fase == kivuli.Fase.AVISA:
				break
			await _esperar(0.1)
		_cerca("relojes_sol", 13, 20).recibir_golpe(1, Vector2.UP)
		await _esperar(0.2)
		if kivuli.fase == kivuli.Fase.VOLCADO:
			if vuelta == 0:
				_comprobar(true, "al girar el sol, su sombra se va: se vuelca panza arriba")
			while kivuli.fase == kivuli.Fase.VOLCADO and kivuli.vida > 0:
				kivuli.recibir_golpe(1, Vector2.UP)
				golpes += 1
				await _esperar(0.25)
		if Estado.tiene("kivuli_vencido"):
			break
	_comprobar(golpes > 0 and golpes <= 3 * 4, "volcado, el cetro le entra")
	_comprobar(kivuli.vida == 9 - golpes or Estado.tiene("kivuli_vencido"), "y a los tres golpes se vuelve a enterrar (vida %d)" % kivuli.vida)
	for vuelta in 8:
		if Estado.tiene("kivuli_vencido"):
			break
		for i in 80:
			if kivuli.fase == kivuli.Fase.ACECHA or kivuli.fase == kivuli.Fase.AVISA:
				break
			await _esperar(0.1)
		_cerca("relojes_sol", 13, 20).recibir_golpe(1, Vector2.UP)
		await _esperar(0.2)
		while kivuli.fase == kivuli.Fase.VOLCADO and kivuli.vida > 0:
			kivuli.recibir_golpe(1, Vector2.UP)
			await _esperar(0.25)
	_comprobar(Estado.tiene("kivuli_vencido") and Estado.tiene("peso_oeste"), "Kivuli, vencido: la Pesa del Oeste")
	await _esperar(3.6)
	await _leer_dialogo()
	_comprobar(Estado.cuantos("peso_oeste") == 1, "y la Pesa, en la mochila")
	_comprobar(int(Estado.extra.get("bestiario", {}).get("kivuli", 0)) == 1, "en el Bestiario")
	_comprobar(Misiones.estado(Misiones.buscar("dunas_penumbra")) == "hecha", "la misión, hecha")
	var suelto := get_tree().get_nodes_in_group("recogibles").any(func(r: Node) -> bool: return r.get("marca") == "farol/dunas_3")
	_comprobar(suelto or Estado.tiene("farol/dunas_3"), "y suelta un Farol de la Hora")

	print("Al volver, todo sigue igual:")
	await _ir("jioni", "dunas", "Jioni")
	await _ir("dunas_penumbra", "jioni", "DunasPenumbra")
	escena = get_tree().current_scene
	_comprobar(escena.puente.hecho() and escena.kivuli == null, "el puente sigue y Kivuli no vuelve")
	_comprobar(not _cerca("espejos", 32, 47).enterrado() and _cerca("velas_sombra", 38, 18).de_canto, "los espejos fuera y la vela del norte, de canto")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
