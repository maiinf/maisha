extends Node
## Prueba automática de La Aguja Caída (Asterhaul): se llega por la verja del norte de Mji-Jiwe (abierta con las dos
## primeras cadenas rotas), suena su música, el abismo no se pisa, Pigo en gris, pisar el vacío hace caer (1 hoja y
## de vuelta al suelo firme), el campanazo de la Carga (dura poco y no se contagia), las losas de cristal solo donde
## llega la onda, los Popo (el chillido aturde; con un monolito cantando, el eco le vuelve), la Esquirla de Pigo, la
## Resonancia de Ámbar, la nota que pasa de monolito en monolito (3 → 2 → 1) y tiende el puente alto, el peñasco
## flotante que acude al que canta, los islotes, Kipanga (en el aire no se le da, la onda le rompe el vuelo, las
## plumas-cuchilla enmudecen al monolito, el picado, la furia, vencido: la Cadena del Norte) y la vuelta.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_aguja_caida

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


## El nodo de `grupo` más cercano a una casilla
func _cerca(grupo: String, x: int, y: int) -> Node2D:
	var mejor: Node2D = null
	for n in get_tree().get_nodes_in_group(grupo):
		if mejor == null or (n as Node2D).global_position.distance_to(_sitio(x, y)) < mejor.global_position.distance_to(_sitio(x, y)):
			mejor = n
	return mejor


## Maisha se pone junto a `algo`, lo mira y embiste
func _cargar(m: CharacterBody2D, algo: Node2D, desde: Vector2) -> bool:
	m.global_position = algo.global_position + desde
	m.mirar(-desde.normalized())
	m.aliento = m.aliento_maximo()
	m.set("_espera_carga", 0.0)
	var si: bool = m.carga()
	await _esperar(0.6)
	return si


func _hablar(m: CharacterBody2D, quien: Node2D) -> void:
	m.global_position = quien.global_position + Vector2(0, 14)
	quien.interactuar()
	await _leer_dialogo()


func _resonar(m: CharacterBody2D) -> bool:
	m.aliento = m.aliento_maximo()
	m.set("_espera_resonancia", 0.0)
	return m.resonancia()


## El puente de cristal que pasa por esa casilla (los dos están anclados en el origen: se buscan por sus casillas)
func _puente(x: int, y: int) -> Node2D:
	for p in get_tree().get_nodes_in_group("puentes_cristal"):
		if p.casillas.has_point(Vector2i(x, y)):
			return p
	return null


func _callar_todos() -> void:
	for mono in get_tree().get_nodes_in_group("monolitos"):
		mono.callar()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "carga_sismica", "pulso_magnetico", "mwamba_pulso", "mwamba_hablado",
			"puerta_crater_abierta", "mji_jiwe_llegada", "mhunzi_conocida", "arte_tierra", "mapa_asterhaul",
			"kifaru_vencido", "cadena_oeste_rota", "nyundo_vencido", "cadena_este_rota"]:
		Estado.marcar(marca)
	Estado.jugando = true

	print("Llegar a la Aguja:")
	await _ir("mji_jiwe", "desfiladero", "MjiJiwe")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var paso: Node2D = null
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == "aguja":
			paso = p
	_comprobar(Estado.tiene("aguja_abierta") and paso != null and paso.destino == "aguja_caida", "rotas las dos primeras cadenas, la verja del norte de Mji-Jiwe está abierta")
	m.global_position = paso.global_position + Vector2(0, 30)
	Input.action_press("mover_arriba")
	for i in 240:
		if _escena() == "AgujaCaida":
			break
		await get_tree().process_frame
	Input.action_release("mover_arriba")
	await _esperar(1.0)
	_comprobar(_escena() == "AgujaCaida", "andando por ella se llega a La Aguja Caída (%s)" % _escena())
	_comprobar(Sonido.musica_actual == "aguja_caida", "suena «Donde canta el cristal» (%s)" % Sonido.musica_actual)
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var escena := get_tree().current_scene
	_comprobar(m.global_position.y > 74.0 * 16.0, "Maisha aparece en la entrada del sur (%s)" % m.global_position)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("aguja_llegada"), "piensa al llegar")
	m.global_position = _sitio(25, 68)
	Input.action_press("mover_izquierda")
	await _esperar(1.2)
	Input.action_release("mover_izquierda")
	_comprobar(m.global_position.x > 21.0 * 16.0, "el abismo no se pisa (%.0f)" % m.global_position.x)

	print("Pigo y el vacío:")
	var pigo := _cerca("escribas", 36, 68)
	_comprobar(pigo.id == "pigo_gris", "Pigo está en gris")
	await _hablar(m, pigo)
	_comprobar(Estado.tiene("pigo_vista") and not m.resonancia(), "no habla; y sin aprenderla, no hay Resonancia")
	var monolitos := get_tree().get_nodes_in_group("monolitos")
	_comprobar(monolitos.size() == 13 and monolitos.all(func(x: Node) -> bool: return not x.cantando()), "hay trece monolitos, todos callados")
	var bajo := _puente(36, 60)
	_comprobar(bajo.losas() == 0, "el primer puente de cristal no está: solo su dibujo a puntos")
	m.set("_invulnerable", 0.0)
	m.global_position = _sitio(36, 62)
	await _esperar(0.3)
	var vida: int = m.vida
	m.global_position = _sitio(36, 60)
	await _esperar(0.3)
	_comprobar(escena.get_node("Vacio").cayendo and not m.puede_actuar, "si pisa el vacío, cae")
	await _esperar(2.4)
	_comprobar(m.vida == vida - 1 and m.global_position.y > 61.0 * 16.0 and m.puede_actuar, "pierde una hoja y vuelve al último suelo firme (%d → %d, %s)" % [vida, m.vida, m.global_position])
	m.set("_invulnerable", 900.0)

	print("El campanazo de la Carga:")
	var oeste := _cerca("monolitos", 31, 63)
	_comprobar(await _cargar(m, oeste, Vector2(0, 20)) and oeste.fuerza == 1, "una Carga le da un campanazo a un monolito (fuerza %d)" % oeste.fuerza)
	await _esperar(0.5)
	_comprobar(bajo.firme(Vector2(34, 60) * 16.0 + Vector2(8, 8)), "y bajo su onda aparecen losas de cristal")
	_comprobar(not bajo.firme(Vector2(37, 58) * 16.0 + Vector2(8, 8)) and bajo.losas() < 16, "pero no donde la onda no llega (%d losas de 16)" % bajo.losas())
	m.global_position = _sitio(34, 60)
	await _esperar(0.6)
	_comprobar(not escena.get_node("Vacio").cayendo, "las losas sostienen a Maisha")
	m.global_position = _sitio(36, 56)
	await _esperar(4.6)
	_comprobar(not oeste.cantando() and bajo.losas() == 0, "el campanazo dura poco: el monolito calla y el puente se deshace")

	print("La Cresta de los Diapasones:")
	m.global_position = _cerca("recogibles", 36, 47).global_position
	await _esperar(0.5)
	_comprobar(Estado.cuantos("esquirla_pigo") == 1, "la Esquirla de Pigo está en la Cresta")
	var popo := _cerca("popos", 22, 53)
	_comprobar(get_tree().get_nodes_in_group("popos").size() == 3 and not popo.recibir_golpe(1, Vector2.RIGHT), "hay tres Popo; en el aire no les llega el cetro")
	m.global_position = _sitio(25, 54)
	popo.set("_cd", 0.0)
	for i in 40:
		if m.mareo > 0.0:
			break
		await _esperar(0.1)
	_comprobar(m.mareo > 0.0 and popo.fase == popo.Fase.PICADO, "su chillido aturde a Maisha, y se le tira en picado (%.1f, %d)" % [m.mareo, popo.fase])
	await _esperar(1.6)
	m.set("mareo", 0.0)
	var cresta_o := _cerca("monolitos", 18, 49)
	await _cargar(m, cresta_o, Vector2(0, 20))
	m.global_position = _sitio(25, 54)
	popo.global_position = _sitio(21, 52)
	popo.call("_cambiar", popo.Fase.VUELA)
	popo.set("_cd", 0.0)
	for i in 30:
		if popo.fase == popo.Fase.CAIDO:
			break
		await _esperar(0.1)
	_comprobar(popo.fase == popo.Fase.CAIDO, "si chilla bajo la onda de un monolito que canta, el eco le vuelve y cae (%d)" % popo.fase)
	_comprobar(popo.recibir_golpe(1, Vector2.RIGHT) and popo.vida == 1, "en el suelo, el cetro sí entra")
	popo.recibir_golpe(1, Vector2.RIGHT)
	await _esperar(0.6)
	_comprobar(get_tree().get_nodes_in_group("popos").size() == 2 and int(Estado.extra.get("bestiario", {}).get("popo", 0)) == 1, "dos golpes y cuenta en el Bestiario")
	_callar_todos()

	print("Pigo enseña la Resonancia de Ámbar:")
	await _hablar(m, pigo)
	await _esperar(1.2)
	await _leer_dialogo()
	_comprobar(pigo.id == "pigo" and Estado.tiene("pigo_pulso") and Estado.tiene("resonancia_ambar"), "Pigo recupera el pulso y enseña la Resonancia de Ámbar")
	m.global_position = _sitio(36, 64)
	m.aliento = m.aliento_maximo()
	m.set("_espera_resonancia", 0.0)
	_comprobar(m.resonancia() and is_equal_approx(m.aliento, m.aliento_maximo() - 18.0), "con P, Maisha da la nota (18 de Aliento)")
	_comprobar(oeste.fuerza == 3 and _cerca("monolitos", 40, 63).fuerza == 3, "los monolitos que alcanza cantan con toda su fuerza")
	await _esperar(1.0)
	_comprobar(bajo.losas() == 16, "con los dos cantando, el primer puente está entero (%d)" % bajo.losas())
	_callar_todos()

	print("La nota se contagia: el puente alto:")
	var alto := _puente(36, 38)
	var norte := _cerca("monolitos", 38, 45)
	var suelto_1 := _cerca("monolitos", 40, 40)
	var suelto_2 := _cerca("monolitos", 40, 35)
	await _cargar(m, norte, Vector2(0, 20))
	await _esperar(1.0)
	_comprobar(norte.fuerza == 1 and not suelto_1.cantando() and alto.losas() < 40, "un campanazo no se contagia: el puente alto se queda a medias (%d de 40)" % alto.losas())
	_callar_todos()
	await _esperar(1.4)
	m.global_position = _sitio(38, 49)
	_resonar(m)
	_comprobar(norte.fuerza == 3 and not suelto_1.cantando(), "la Resonancia despierta al monolito de la Cresta; los de las peñas sueltas quedan lejos")
	await _esperar(1.3)
	_comprobar(suelto_1.fuerza == 2 and suelto_2.fuerza == 1, "pero su onda los despierta por simpatía: 3 → 2 → 1 (%d, %d)" % [suelto_1.fuerza, suelto_2.fuerza])
	_comprobar(alto.losas() < 40, "la nota tarda en llegar: el final del puente aún no está (%d de 40)" % alto.losas())
	await _esperar(1.0)
	_comprobar(alto.losas() == 40, "con los tres cantando, el puente alto está entero (%d)" % alto.losas())
	await _esperar(3.0)
	_comprobar(alto.losas() == 40 and suelto_2.cantando(), "y la nota contagiada dura tanto como la primera: da tiempo a cruzar")
	_callar_todos()

	print("Los peñascos flotantes:")
	var penasco := _cerca("penascos", 11, 49)
	_comprobar(get_tree().get_nodes_in_group("penascos").size() == 2 and not escena.sostenida(_sitio(14, 49)), "hay dos peñascos, sueltos en medio del vacío: desde la orilla no se llega")
	m.global_position = _sitio(19, 51)
	_resonar(m)
	await _esperar(1.8)
	_comprobar(penasco.en_muelle("a"), "el peñasco acude al monolito que canta, hasta la orilla de la Cresta")
	m.global_position = penasco.centro()
	await _esperar(0.4)
	_comprobar(not escena.get_node("Vacio").cayendo, "y sostiene a Maisha")
	_callar_todos()
	await _esperar(5.6)
	_comprobar(penasco.global_position.distance_to(penasco.reposo()) < 1.0 and penasco.firme(m.global_position), "cuando el monolito calla, vuelve al medio con Maisha encima (%s)" % m.global_position)
	_resonar(m)
	var isla := _cerca("monolitos", 6, 51)
	_comprobar(isla.fuerza == 3, "desde el medio, la Resonancia alcanza al monolito del islote")
	await _esperar(1.8)
	_comprobar(penasco.en_muelle("b") and penasco.firme(m.global_position), "y el peñasco la lleva hasta él")
	m.global_position = _cerca("recogibles", 4, 50).global_position
	await _esperar(0.5)
	_comprobar(Estado.tiene("esquirla/islote") and Estado.cuantos("esquirla_estrella") == 1, "en el islote del oeste, una Esquirla de Estrella")
	m.global_position = _sitio(66, 51)
	await _esperar(0.4)
	_comprobar(Estado.tiene("secreto/aguja_caida/islote_este"), "en el islote del este, un secreto")
	_callar_todos()

	print("El Nido de la Cima: Kipanga Astral:")
	var kipanga := get_tree().get_first_node_in_group("kipangas") as Node2D
	_comprobar(kipanga != null and kipanga.fase == kipanga.Fase.DORMIDO, "Kipanga anida en la cima, quieto")
	m.global_position = Vector2(576, 470)
	await _esperar(0.6)
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(kipanga.fase == kipanga.Fase.PLANEA and Sonido.musica_actual == "jefe_kipanga", "al entrar, levanta el vuelo (suena «Alas de obsidiana»)")
	await _esperar(1.0)
	_comprobar(kipanga.altura > 20.0 and not kipanga.recibir_golpe(1, Vector2.UP) and kipanga.vida == 12, "en el aire no hay forma de darle (altura %.0f)" % kipanga.altura)
	var nido := _cerca("monolitos", 26, 27)
	kipanga.set("_inmune", 0.0)
	kipanga.set("_cd", 99.0)
	kipanga.global_position = nido.global_position + Vector2(40, -30)
	kipanga.set("_angulo", ((kipanga.global_position - Vector2(576, 360)) / Vector2(240, 176)).angle())
	m.global_position = nido.global_position + Vector2(0, 22)
	_resonar(m)
	for i in 30:
		if kipanga.fase == kipanga.Fase.ATURDIDO:
			break
		await _esperar(0.1)
	_comprobar(kipanga.fase == kipanga.Fase.ATURDIDO, "la onda de un monolito que canta le rompe el vuelo (%d)" % kipanga.fase)
	await _esperar(0.4)
	_comprobar(kipanga.recibir_golpe(1, Vector2.UP) and kipanga.vida == 11, "aturdido en el suelo, el cetro sí entra")
	for i in 3:
		await _esperar(0.15)
		kipanga.recibir_golpe(1, Vector2.UP)
	await _esperar(0.3)
	_comprobar(kipanga.vida == 8 and kipanga.fase == kipanga.Fase.PLANEA, "a los cuatro golpes remonta (vida %d)" % kipanga.vida)
	_callar_todos()
	m.global_position = Vector2(576, 470)
	for i in 60:
		if get_tree().get_nodes_in_group("plumas_cuchilla").size() >= 2:
			break
		await _esperar(0.1)
	_comprobar(get_tree().get_nodes_in_group("plumas_cuchilla").size() == 2 and nido.mudo(), "y lo primero que hace es clavarle dos plumas-cuchilla al monolito que lo tiró: lo enmudecen")
	_comprobar(not nido.resonar(3) and not nido.cantando(), "enmudecido, no canta")
	for p in get_tree().get_nodes_in_group("plumas_cuchilla"):
		p.recibir_golpe(1, Vector2.UP)
	await _esperar(0.2)
	_comprobar(not nido.mudo() and nido.resonar(3), "rotas las plumas de un golpe, vuelve a cantar")
	_callar_todos()
	kipanga.set("_inmune", 99.0)
	kipanga.set("_ataques", 2)
	kipanga.set("_cd", 0.0)
	var posado := false
	for i in 50:
		if kipanga.fase == kipanga.Fase.POSADO:
			posado = true
			break
		await _esperar(0.1)
	_comprobar(posado and kipanga.altura < 1.0 and not kipanga.recibir_golpe(1, Vector2.UP), "cae en picado y se queda un momento posado: el cetro rebota en las lajas")
	for k in 2:
		kipanga.call("_cambiar", kipanga.Fase.PLANEA)
		kipanga.set("_cd", 99.0)
		kipanga.caer(nido)
		for i in 4:
			await _esperar(0.15)
			kipanga.recibir_golpe(1, Vector2.UP)
		if k == 0:
			_comprobar(kipanga.furia() and kipanga.vida == 4, "con la mitad de la vida, entra en furia (vida %d)" % kipanga.vida)
	await _esperar(0.4)
	_comprobar(Estado.tiene("kipanga_vencido") and Estado.tiene("cadena_norte_rota"), "vencido: se rompe la tercera Cadena del Cráter")
	_comprobar(Misiones.estado(Misiones.buscar("aguja_caida")) == "hecha", "misión cumplida")
	var esquirla: Node2D = null
	for r in get_tree().get_nodes_in_group("recogibles"):
		if r.marca == "esquirla/kipanga":
			esquirla = r
	_comprobar(esquirla != null and get_tree().get_nodes_in_group("plumas_cuchilla").is_empty(), "suelta una Esquirla de Estrella y sus plumas se deshacen")
	await _esperar(3.4)
	await _leer_dialogo()
	_comprobar(Sonido.musica_actual == "aguja_caida", "vuelve la música de la Aguja (%s)" % Sonido.musica_actual)

	print("Volver:")
	await _ir("aguja_caida", "sur", "AgujaCaida")
	_comprobar(get_tree().get_first_node_in_group("kipangas") == null and _cerca("escribas", 36, 68).id == "pigo", "al volver, Kipanga ya no está y Pigo sigue con su color")
	await _ir("mji_jiwe", "aguja", "MjiJiwe")
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.y < 110.0, "de vuelta a Mji-Jiwe se sale por la verja del norte (%s)" % m.global_position)

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
