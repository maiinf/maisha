extends Node
## Prueba automática de La Calzada de los Obeliscos (el Valle del Ocaso): se llega desde Jioni por el sureste, Maisha
## piensa al llegar, el abismo hace caer, cada tramo de sombra pide su hora del sol (al girarlo se abre uno y se cierra
## otro), el Balcón del Mediodía y su farol, los Centinelas de Reloj (en penumbra el cetro y la Carga rebotan; al sol
## se quedan de piedra y la Carga los rompe), el farol del Viaducto, Saa-Mchanga (en la sombra de un obelisco su rayo
## no hace nada; fuera, sí; inclinado, la Carga o el Reloj lo vuelcan), la Pesa del Sur, las tres pesas en Jioni, la
## misión, y que todo queda como estaba al volver.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_calzada_obeliscos

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


func _pisar(m: Node2D, x: int, y: int) -> void:
	m.global_position = _sitio(x, y)
	await _esperar(0.3)


func _fase(saa: Node2D, f: int, maximo := 12.0) -> void:
	for i in int(maximo * 10):
		if saa.fase == f:
			return
		await _esperar(0.1)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "asterhaul_libre", "nexo_despierto", "mirador_ocaso",
			"arco_atardecer_abierto", "jioni", "kibatari_conocido", "kibatari_caminos", "mwanga_reloj", "carga_sismica",
			"arte_tierra", "peso_oeste", "peso_este"]:
		Estado.marcar(marca)
	Estado.extra["sol"] = 1
	Estado.jugando = true
	_comprobar(Misiones.estado(Misiones.buscar("calzada_obeliscos")) == "activa", "con los caminos de Kibatari aparece la misión")

	print("Llegar a la Calzada:")
	await _ir("calzada_obeliscos", "jioni", "CalzadaObeliscos")
	_comprobar(_escena() == "CalzadaObeliscos", "se llega a La Calzada de los Obeliscos (%s)" % _escena())
	var escena := get_tree().current_scene
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.y < 5.0 * 16.0, "Maisha aparece al norte, junto a la puerta de Jioni (%s)" % m.global_position)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("calzada_llegada"), "piensa al llegar")
	var sol: Node2D = escena.sol
	var vacio: Node = escena.get_node("Vacio")

	print("Las sombras de la Calzada:")
	_comprobar(not sol.firme(_sitio(22, 8)), "con el sol al sur, no hay sombra hacia el Pilar I")
	m.set("_invulnerable", 0.0)
	await _pisar(m, 16, 8)
	var vida: int = m.vida
	m.global_position = _sitio(22, 8)
	await _esperar(0.3)
	_comprobar(vacio.cayendo, "pisar el abismo: se cae")
	await _esperar(2.6)
	_comprobar(m.vida == vida - 1 and m.global_position.x < 19.0 * 16.0 and m.puede_actuar, "pierde una hoja y vuelve a la isla (%s)" % m.global_position)
	m.set("_invulnerable", 900.0)
	var reloj1 := _cerca("relojes_sol", 8, 8)
	reloj1.recibir_golpe(1, Vector2.UP)
	reloj1.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.hora == 0 and sol.firme(_sitio(22, 8)) and sol.firme(_sitio(26, 9)), "sol al oeste: la sombra del obelisco cruza al Pilar I")
	await _pisar(m, 22, 8)
	await _pisar(m, 30, 8)
	_comprobar(not vacio.cayendo, "se cruza al Pilar I por la sombra")
	var reloj2 := _cerca("relojes_sol", 30, 11)
	reloj2.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.hora == 1 and sol.firme(_sitio(32, 18)) and not sol.firme(_sitio(22, 8)), "sol al sur: se abre el tramo del Viaducto y se cierra el de atrás")
	reloj2.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.hora == 2 and sol.firme(_sitio(43, 7)), "sol al este: la sombra del Balcón llega al Pilar")
	await _pisar(m, 43, 7)
	await _pisar(m, 52, 7)
	m.global_position = _sitio(59, 5)
	await _esperar(0.6)
	_comprobar(not vacio.cayendo and Estado.tiene("farol/calzada_1"), "el Balcón del Mediodía y su Farol de la Hora")
	await _pisar(m, 43, 7)
	await _pisar(m, 33, 8)
	reloj2.recibir_golpe(1, Vector2.UP)
	reloj2.recibir_golpe(1, Vector2.UP)
	await _pisar(m, 32, 17)
	await _pisar(m, 32, 26)
	_comprobar(not vacio.cayendo and sol.hora == 1, "con el sol al sur, se baja al Viaducto")
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("calzada_centinelas"), "Maisha ve a los Centinelas")

	print("Los Centinelas de Reloj:")
	var cs := get_tree().get_nodes_in_group("centinelas")
	_comprobar(cs.size() == 2 and not cs[0].estatua() and not cs[1].estatua(), "con el sol al sur, los dos andan en penumbra")
	var oeste: Node2D = cs[0] if cs[0].global_position.x < cs[1].global_position.x else cs[1]
	var este: Node2D = cs[1] if oeste == cs[0] else cs[0]
	var rebota: bool = not este.recibir_golpe(1, Vector2.UP)
	await _cargar(m, este, Vector2(-24, 0))
	_comprobar(rebota and este.fase != este.Fase.ROTO, "en penumbra, el cetro y la Carga rebotan")
	oeste.global_position = _sitio(28, 29)
	este.global_position = _sitio(40, 29)
	var reloj3 := _cerca("relojes_sol", 26, 24)
	reloj3.recibir_golpe(1, Vector2.UP)
	await _esperar(0.2)
	_comprobar(este.estatua() and not oeste.estatua(), "sol al este: el del este se queda de piedra")
	este.global_position = _sitio(40, 29)
	_comprobar(await _cargar(m, este, Vector2(-24, 0)) and este.fase == este.Fase.ROTO, "de piedra, la Carga lo vuelca y se rompe")
	oeste.global_position = _sitio(28, 29)
	reloj3.recibir_golpe(1, Vector2.UP)
	await _esperar(0.2)
	oeste.global_position = _sitio(28, 29)
	_comprobar(oeste.estatua() and await _cargar(m, oeste, Vector2(24, 0)), "sol al oeste: el otro, igual")
	_comprobar(int(Estado.extra.get("bestiario", {}).get("centinela", 0)) == 2, "los dos, en el Bestiario")
	m.global_position = _sitio(42, 24)
	await _esperar(0.6)
	_comprobar(Estado.tiene("farol/calzada_2"), "el Farol de la Hora del Viaducto")

	print("Saa-Mchanga, el Autómata Reloj de Arena:")
	reloj3.recibir_golpe(1, Vector2.UP)
	_comprobar(sol.hora == 1 and sol.firme(_sitio(34, 34)), "sol al sur: la sombra de la Rotonda sube al Viaducto")
	var saa: Node2D = escena.saa
	_comprobar(saa != null and saa.fase == saa.Fase.DORMIDO, "Saa-Mchanga espera en la Rotonda")
	await _pisar(m, 34, 33)
	m.global_position = _sitio(34, 40)
	await _esperar(1.0)
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(saa.fase == saa.Fase.CARGA, "al entrar en la Rotonda, despierta y se carga")
	_comprobar(not saa.recibir_golpe(1, Vector2.UP), "cargado, el cetro rebota")
	m.global_position = _sitio(27, 46)
	m.set("_invulnerable", 0.0)
	vida = m.vida
	await _fase(saa, saa.Fase.BARRE)
	_comprobar(sol.en_sombra(m.global_position), "Maisha, a la sombra de un obelisco")
	await _fase(saa, saa.Fase.INCLINADO)
	_comprobar(m.vida == vida, "el rayo da la vuelta entera y a la sombra no hace nada")
	_comprobar(await _cargar(m, saa, Vector2(0, 26)) and saa.fase == saa.Fase.VOLCADO, "inclinado, la Carga lo vuelca")
	m.set("_invulnerable", 900.0)
	var golpes := 0
	while saa.fase == saa.Fase.VOLCADO:
		saa.recibir_golpe(1, Vector2.UP)
		golpes += 1
		await _esperar(0.25)
	_comprobar(golpes == 3 and saa.vida == 6 and saa.fase == saa.Fase.CARGA, "volcado, tres golpes y se levanta")
	m.global_position = _sitio(34, 50)
	m.set("_invulnerable", 0.0)
	vida = m.vida
	await _fase(saa, saa.Fase.INCLINADO)
	_comprobar(m.vida < vida, "fuera de la sombra, el rayo quema")
	m.set("_invulnerable", 900.0)
	_cerca("relojes_sol", 34, 52).recibir_golpe(1, Vector2.UP)
	_comprobar(saa.fase == saa.Fase.VOLCADO, "inclinado, girar el Reloj también lo vuelca")
	for vuelta in 6:
		while saa.fase == saa.Fase.VOLCADO and saa.vida > 0:
			saa.recibir_golpe(1, Vector2.UP)
			await _esperar(0.25)
		if Estado.tiene("saa_vencido"):
			break
		await _fase(saa, saa.Fase.INCLINADO)
		_cerca("relojes_sol", 34, 52).recibir_golpe(1, Vector2.UP)
	_comprobar(Estado.tiene("saa_vencido") and Estado.tiene("peso_sur"), "Saa-Mchanga, vencido: la Pesa del Sur")
	await _esperar(3.6)
	await _leer_dialogo()
	_comprobar(Estado.cuantos("peso_sur") == 1, "y la Pesa, en la mochila")
	_comprobar(int(Estado.extra.get("bestiario", {}).get("saa_mchanga", 0)) == 1, "en el Bestiario")
	_comprobar(Misiones.estado(Misiones.buscar("calzada_obeliscos")) == "hecha", "la misión, hecha")
	var suelto := get_tree().get_nodes_in_group("recogibles").any(func(r: Node) -> bool: return r.get("marca") == "farol/calzada_3")
	_comprobar(suelto or Estado.tiene("farol/calzada_3"), "y suelta un Farol de la Hora")

	print("Las tres pesas y al volver:")
	await _ir("jioni", "calzada", "Jioni")
	_comprobar(Estado.tiene("tres_pesos"), "con las tres pesas, en Jioni se abre la Puerta del Horizonte")
	await _ir("calzada_obeliscos", "jioni", "CalzadaObeliscos")
	escena = get_tree().current_scene
	_comprobar(escena.saa == null, "Saa-Mchanga no vuelve")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
