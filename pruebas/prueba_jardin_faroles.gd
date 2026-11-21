extends Node
## Prueba automática de El Jardín de los Faroles (el Valle del Ocaso): se llega desde Jioni por el este, Maisha piensa
## al llegar, la luz del Prisma Solar sigue los espejos de ángulo (un golpe los cambia), las polillas de papel tapan
## los espejos encendidos (un golpe o la Resonancia las rompe), la luz dorada abre la verja, el prisma saca el haz
## violeta que deshace la celosía (el Pabellón del Té y su farol) y delata la pasarela falsa del Estanque (la otra
## sostiene; su farol), Mondo (sus reflejos se esfuman con la luz de los espejos altos y él cae aturdido), la Pesa del
## Este, la misión, y que todo queda como estaba al volver.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_jardin_faroles

const RESONANCIA := preload("res://scripts/combate/resonancia_ambar.gd")

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


func _luz() -> void:
	await get_tree().process_frame
	await get_tree().process_frame


## Espera a que Mondo y sus reflejos estén quietos delante de sus espejos (y ya se les pueda delatar)
func _posados(mondo: Node2D) -> void:
	for i in 60:
		if mondo._inmune <= 0.0 and mondo.fase == mondo.Fase.CAZA and mondo._figuras.all(func(f: Dictionary) -> bool: return f["estado"] == mondo.Fig.POSADO):
			return
		await _esperar(0.1)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "asterhaul_libre", "nexo_despierto", "mirador_ocaso",
			"arco_atardecer_abierto", "jioni", "kibatari_conocido", "kibatari_caminos", "mwanga_reloj", "carga_sismica",
			"arte_tierra", "resonancia_ambar"]:
		Estado.marcar(marca)
	Estado.jugando = true
	_comprobar(Misiones.estado(Misiones.buscar("jardin_faroles")) == "activa", "con los caminos de Kibatari aparece la misión")

	print("Llegar al Jardín:")
	await _ir("jardin_faroles", "jioni", "JardinFaroles")
	_comprobar(_escena() == "JardinFaroles", "se llega a El Jardín de los Faroles (%s)" % _escena())
	var escena := get_tree().current_scene
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.x < 4.0 * 16.0, "Maisha aparece al oeste, junto a la puerta de Jioni (%s)" % m.global_position)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("jardin_llegada"), "piensa al llegar")
	m.set("_invulnerable", 900.0)
	var luz: Node2D = escena.luz

	print("La luz y las polillas de papel:")
	_comprobar(luz.tiene(Vector2i(20, 27), 1) and luz.tiene(Vector2i(26, 32), 1), "el rayo dorado entra en el Claustro y el primer espejo lo tuerce al sur")
	var e1 := _cerca("espejos", 26, 27)
	_comprobar(not is_instance_valid(e1.tapado), "mientras Maisha está lejos, las polillas no se mueven de su sitio")
	m.global_position = _sitio(20, 27)
	for i in 120:
		if is_instance_valid(e1.tapado):
			break
		await _esperar(0.1)
	await _luz()
	_comprobar(is_instance_valid(e1.tapado) and not luz.tiene(Vector2i(26, 32), 1), "una polilla se posa en el espejo encendido y lo tapa")
	_comprobar(not e1.recibir_golpe(1, Vector2.UP), "tapado, el golpe no lo gira")
	var polilla: Node2D = e1.tapado
	polilla.recibir_golpe(1, Vector2.UP)
	await _luz()
	_comprobar(not is_instance_valid(e1.tapado) and luz.tiene(Vector2i(26, 32), 1), "un golpe rompe la polilla y la luz vuelve")
	var quedan := get_tree().get_nodes_in_group("polillas")
	for p in quedan:
		var onda: Node2D = RESONANCIA.new()
		onda.global_position = (p as Node2D).global_position
		escena.add_child(onda)
	await _esperar(0.2)
	_comprobar(quedan.size() == 2 and get_tree().get_nodes_in_group("polillas").is_empty(), "la Resonancia deshace las otras dos")
	_comprobar(int(Estado.extra.get("bestiario", {}).get("polilla_papel", 0)) >= 1, "las polillas, en el Bestiario")

	print("Los espejos y la verja:")
	_comprobar(not Estado.tiene("jardin/verja") and escena.get_node("Entidades/Verja") != null, "la verja del Invernadero, cerrada")
	for c in [Vector2i(26, 27), Vector2i(26, 19), Vector2i(40, 19), Vector2i(40, 27)]:
		_cerca("espejos", c.x, c.y).recibir_golpe(1, Vector2.UP)
	await _luz()
	_comprobar(luz.tiene(Vector2i(33, 19), 1) and luz.tiene(Vector2i(40, 23), 1), "cuatro golpes: la luz da la vuelta al Claustro y pasa por el prisma")
	_comprobar(Estado.tiene("jardin/verja") and luz.tiene(Vector2i(45, 27), 1) and not luz.tiene(Vector2i(48, 27), 1), "la luz dorada abre la verja (su disco se la bebe)")
	await _esperar(1.2)
	await _leer_dialogo()

	print("El prisma, la celosía y el Pabellón del Té:")
	var prisma := _cerca("prismas", 33, 19)
	_comprobar(not luz.tiene(Vector2i(33, 15), 2) and not luz.tiene(Vector2i(33, 25), 2), "con la cara hacia atrás, el prisma no saca violeta")
	prisma.recibir_golpe(1, Vector2.UP)
	await _luz()
	_comprobar(Estado.tiene("jardin/celosia"), "cara al norte: el haz violeta deshace la celosía ilusoria")
	await _esperar(1.2)
	await _leer_dialogo()
	m.global_position = _sitio(33, 14)
	await _esperar(0.3)
	m.global_position = _sitio(38, 5)
	await _esperar(0.6)
	_comprobar(Estado.tiene("farol/jardin_1"), "detrás, el Pabellón del Té y su Farol de la Hora")

	print("El Estanque de los Reflejos:")
	var vacio: Node = escena.get_node("Vacio")
	m.set("_invulnerable", 0.0)
	m.global_position = _sitio(22, 46)
	await _esperar(0.3)
	var vida: int = m.vida
	m.global_position = _sitio(30, 46)
	await _esperar(0.3)
	_comprobar(vacio.cayendo, "la pasarela de arriba es un reflejo: se hunde")
	await _esperar(2.6)
	_comprobar(m.vida == vida - 1 and m.global_position.x < 25.0 * 16.0 and m.puede_actuar, "pierde una hoja y vuelve a la orilla (%s)" % m.global_position)
	m.set("_invulnerable", 900.0)
	prisma.recibir_golpe(1, Vector2.UP)
	prisma.recibir_golpe(1, Vector2.UP)
	await _luz()
	_comprobar(luz.tiene(Vector2i(33, 47), 2) and Estado.tiene("jardin/reflejo_delatado"), "cara al sur: el haz violeta cruza el estanque y delata la falsa")
	await _esperar(1.2)
	await _leer_dialogo()
	m.global_position = _sitio(30, 49)
	await _esperar(0.3)
	m.global_position = _sitio(42, 49)
	await _esperar(0.3)
	m.global_position = _sitio(48, 50)
	await _esperar(0.6)
	_comprobar(not vacio.cayendo and Estado.tiene("farol/jardin_2"), "la de abajo sostiene: el farol del muelle")

	print("Mondo, el Serval de Mil Reflejos:")
	var mondo: Node2D = escena.mondo
	_comprobar(mondo != null and mondo.fase == mondo.Fase.DORMIDO, "Mondo espera en el Invernadero")
	m.global_position = _sitio(52, 27)
	await _esperar(0.3)
	m.global_position = _sitio(61, 30)
	await _esperar(1.0)
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(mondo.fase == mondo.Fase.CAZA and get_tree().get_nodes_in_group("reflejos_mondo").size() == 2, "despierta y se parte en tres")
	_comprobar(not mondo.recibir_golpe(1, Vector2.UP), "sin aturdir, el cetro no le da")
	await _posados(mondo)
	var real_en: int = mondo._figuras.filter(func(f: Dictionary) -> bool: return f["real"])[0]["espejo"]
	var copia: Dictionary = mondo._figuras.filter(func(f: Dictionary) -> bool: return not f["real"] and (f["espejo"] + 2) % 4 != real_en)[0]
	mondo.espejos[(copia["espejo"] + 2) % 4].recibir_golpe(1, Vector2.UP)
	await _esperar(0.2)
	_comprobar(get_tree().get_nodes_in_group("reflejos_mondo").size() == 1 and mondo.fase == mondo.Fase.CAZA, "el rayo de un espejo alto toca un reflejo: se esfuma")
	var golpes := 0
	for vuelta in 8:
		if Estado.tiene("mondo_vencido"):
			break
		await _posados(mondo)
		real_en = mondo._figuras.filter(func(f: Dictionary) -> bool: return f["real"])[0]["espejo"]
		var alto: Node2D = mondo.espejos[(real_en + 2) % 4]
		for i in 40:
			if alto.recibir_golpe(1, Vector2.UP):
				break
			await _esperar(0.1)
		await _esperar(0.2)
		if mondo.fase == mondo.Fase.ATURDIDO:
			if vuelta == 0:
				_comprobar(get_tree().get_nodes_in_group("reflejos_mondo").is_empty(), "al de verdad lo toca el rayo: cae aturdido y los reflejos se esfuman")
			while mondo.fase == mondo.Fase.ATURDIDO and mondo.vida > 0:
				mondo.recibir_golpe(1, Vector2.UP)
				golpes += 1
				await _esperar(0.25)
			if vuelta == 0:
				_comprobar(mondo.vida == 6 and mondo.fase == mondo.Fase.CAZA, "a los tres golpes se levanta y se vuelve a partir")
	_comprobar(golpes == 9, "aturdido, el cetro le entra (%d golpes)" % golpes)
	_comprobar(Estado.tiene("mondo_vencido") and Estado.tiene("peso_este"), "Mondo, vencido: la Pesa del Este")
	await _esperar(3.6)
	await _leer_dialogo()
	_comprobar(Estado.cuantos("peso_este") == 1, "y la Pesa, en la mochila")
	_comprobar(int(Estado.extra.get("bestiario", {}).get("mondo", 0)) == 1, "en el Bestiario")
	_comprobar(Misiones.estado(Misiones.buscar("jardin_faroles")) == "hecha", "la misión, hecha")
	var suelto := get_tree().get_nodes_in_group("recogibles").any(func(r: Node) -> bool: return r.get("marca") == "farol/jardin_3")
	_comprobar(suelto or Estado.tiene("farol/jardin_3"), "y suelta un Farol de la Hora")

	print("Al volver, todo sigue igual:")
	await _ir("jioni", "jardin", "Jioni")
	await _ir("jardin_faroles", "jioni", "JardinFaroles")
	escena = get_tree().current_scene
	await _luz()
	_comprobar(escena.mondo == null and Estado.tiene("jardin/verja"), "la verja abierta y Mondo no vuelve")
	_comprobar(escena.luz.tiene(Vector2i(33, 47), 2) and _cerca("espejos", 26, 27).barra, "los espejos y el prisma, como se dejaron")
	_comprobar(escena.get_node("Entidades/Celosia").get_child_count() > 0 and Estado.tiene("jardin/celosia"), "la celosía sigue deshecha")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
