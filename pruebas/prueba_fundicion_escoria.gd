extends Node
## Prueba automática de La Fundición de Escoria (Asterhaul): se llega por la verja del este de Mji-Jiwe (abierta al
## romperse la Cadena del Oeste), suena su música, la escoria no se pisa, Moto en gris, la barcaza del cabrestante,
## el Kovu que escupe, la Esquirla de Moto, el Pulso Magnético (la barcaza lleva a Maisha y viene cuando se la
## llama), los bloques-imán y sus placas, las compuertas, el Kovu sacado a la piedra, Nyundo (el cetro rebota, la
## tenaza repelida, el bloque devuelto, el peto abierto, la furia, vencido: la Cadena del Este) y la vuelta.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_fundicion_escoria

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


func _pulsar(m: CharacterBody2D) -> bool:
	m.aliento = m.aliento_maximo()
	m.set("_espera_pulso", 0.0)
	return m.pulso()


## Espera a que una barcaza llegue
func _cruzar(b: Node2D) -> void:
	for i in 100:
		if not b.moviendose:
			break
		await _esperar(0.1)
	await _esperar(0.1)


func _centro(b: Node2D) -> Vector2:
	return b.global_position + Vector2(24, 26)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "carga_sismica", "mwamba_pulso", "mwamba_hablado", "puerta_crater_abierta",
			"mji_jiwe_llegada", "mhunzi_conocida", "arte_tierra", "mapa_asterhaul", "kifaru_vencido", "cadena_oeste_rota"]:
		Estado.marcar(marca)
	Estado.jugando = true

	print("Llegar a la Fundición:")
	await _ir("mji_jiwe", "desfiladero", "MjiJiwe")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var paso: Node2D = null
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == "fundicion":
			paso = p
	_comprobar(paso != null and paso.destino == "fundicion_escoria", "rota la Cadena del Oeste, la verja del este de Mji-Jiwe está abierta")
	m.global_position = paso.global_position + Vector2(-30, 6)
	Input.action_press("mover_derecha")
	for i in 240:
		if _escena() == "FundicionEscoria":
			break
		await get_tree().process_frame
	Input.action_release("mover_derecha")
	await _esperar(1.0)
	_comprobar(_escena() == "FundicionEscoria", "andando por ella se llega a La Fundición de Escoria (%s)" % _escena())
	_comprobar(Sonido.musica_actual == "fundicion_escoria", "suena «El hierro que no duerme» (%s)" % Sonido.musica_actual)
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.x < 60.0, "Maisha aparece en la entrada del oeste (%s)" % m.global_position)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("fundicion_llegada"), "piensa al llegar")
	m.global_position = _sitio(10, 37)
	Input.action_press("mover_abajo")
	await _esperar(1.0)
	Input.action_release("mover_abajo")
	_comprobar(m.global_position.y < 39.0 * 16.0 + 6.0, "la escoria no se pisa (%.0f)" % m.global_position.y)

	print("Moto y la barcaza del cabrestante:")
	var moto := _cerca("escribas", 15, 24)
	_comprobar(moto.id == "moto_gris", "Moto está en gris")
	await _hablar(m, moto)
	_comprobar(Estado.tiene("moto_visto") and not m.pulso(), "no habla; y sin aprenderlo, no hay Pulso")
	var norte := get_tree().current_scene.get_node("Barcaza_norte") as Node2D
	_comprobar(get_tree().get_nodes_in_group("barcazas").size() == 4 and not norte.en_b, "hay cuatro barcazas; la del norte, en la orilla de Moto")
	m.global_position = _centro(norte)
	Input.action_press("mover_arriba")
	await _esperar(1.0)
	Input.action_release("mover_arriba")
	_comprobar(m.global_position.y > 19.0 * 16.0 - 2.0, "el hueco vacío del otro lado no se pisa (%.0f)" % m.global_position.y)
	_comprobar(_cerca("cabrestantes", 22, 22).recibir_golpe(1, Vector2.UP), "un golpe al cabrestante suelta la cadena")
	m.global_position = _centro(norte)
	await _esperar(1.6)
	_comprobar(norte.moviendose and not m.puede_actuar, "al momento, la barcaza sale con Maisha encima")
	await _cruzar(norte)
	_comprobar(norte.en_b and m.puede_actuar and m.global_position.y < 19.0 * 16.0, "y la deja en el Crisol Norte (%s)" % m.global_position)

	print("El Crisol Norte:")
	var kovu := _cerca("kovus", 37, 10)
	_comprobar(get_tree().get_nodes_in_group("kovus").size() == 3 and not kovu.recibir_golpe(1, Vector2.RIGHT), "hay tres Kovu; en la escoria no hay forma de darles")
	m.global_position = _sitio(33, 11)
	kovu.global_position = _sitio(37, 11)
	for i in 40:
		if kovu.fase == kovu.Fase.ASOMA:
			break
		await _esperar(0.1)
	_comprobar(kovu.fase == kovu.Fase.ASOMA, "si Maisha se acerca a la orilla, asoma (%d)" % kovu.fase)
	var vida: int = m.vida
	await _esperar(2.2)
	_comprobar(m.vida == vida - 1, "y le escupe una bola de escoria (%d → %d)" % [vida, m.vida])
	m.set("_invulnerable", 900.0)
	m.global_position = _cerca("recogibles", 30, 9).global_position
	await _esperar(0.5)
	_comprobar(Estado.cuantos("esquirla_moto") == 1, "la Esquirla de Moto está en el Crisol")
	_cerca("cabrestantes", 22, 15).recibir_golpe(1, Vector2.UP)
	m.global_position = _centro(norte)
	await _esperar(1.6)
	await _cruzar(norte)
	_comprobar(not norte.en_b and m.global_position.y > 19.0 * 16.0, "con el otro cabrestante se vuelve")

	print("Moto enseña el Pulso Magnético:")
	await _hablar(m, moto)
	await _esperar(1.2)
	await _leer_dialogo()
	_comprobar(moto.id == "moto" and Estado.tiene("moto_pulso") and Estado.tiene("pulso_magnetico"), "Moto recupera el pulso y enseña el Pulso Magnético")
	m.aliento = m.aliento_maximo()
	m.set("_espera_pulso", 0.0)
	_comprobar(m.pulso() and is_equal_approx(m.aliento, m.aliento_maximo() - 15.0), "con O, Maisha pulsa (15 de Aliento)")
	var oeste := get_tree().current_scene.get_node("Barcaza_oeste") as Node2D
	m.global_position = _centro(oeste)
	_comprobar(_pulsar(m) and oeste.moviendose, "subida a una barcaza, el Pulso la despega")
	await _cruzar(oeste)
	_comprobar(oeste.en_b and m.global_position.x > 31.0 * 16.0, "y la lleva a la Plataforma de los Imanes (%s)" % m.global_position)
	m.global_position = _sitio(22, 29)
	_comprobar(_pulsar(m) and oeste.moviendose, "desde la orilla del hueco vacío, el Pulso la llama")
	await _cruzar(oeste)
	_comprobar(not oeste.en_b, "y viene")
	m.global_position = _centro(oeste)
	_pulsar(m)
	await _cruzar(oeste)

	print("La Plataforma de los Imanes:")
	var compuerta := _cerca("compuertas", 48, 30)
	_comprobar(not compuerta.abierta, "la compuerta del este está cerrada")
	var bloque := _cerca("bloques_iman", 38, 30)
	m.global_position = _sitio(36, 24)
	_comprobar(_pulsar(m) and bloque.deslizando, "el Pulso trae un bloque-imán hacia Maisha")
	await _esperar(1.6)
	_comprobar(bloque.casilla() == Vector2i(38, 25) and not Estado.tiene("fundicion/compuerta_este"), "y encaja en su placa; con una sola, la compuerta sigue cerrada (%s)" % bloque.casilla())
	bloque = _cerca("bloques_iman", 44, 26)
	m.global_position = _sitio(45, 33)
	_pulsar(m)
	await _esperar(1.8)
	_comprobar(bloque.casilla() == Vector2i(44, 32), "el otro bloque, a la otra placa (%s)" % bloque.casilla())
	_comprobar(Estado.tiene("fundicion/compuerta_este") and compuerta.abierta, "con las dos, la compuerta del este se abre")

	print("Kovu, con el Pulso:")
	kovu = _cerca("kovus", 35, 40)
	m.global_position = _sitio(36, 36)
	kovu.global_position = _sitio(36, 39)
	kovu.call("_cambiar", kovu.Fase.NADA)
	_comprobar(_pulsar(m) and kovu.fase == kovu.Fase.SALTA, "el Pulso tira de su cresta")
	await _esperar(0.7)
	_comprobar(kovu.fase == kovu.Fase.FUERA and kovu.global_position.y <= 37.0 * 16.0, "y lo saca a la piedra, donde se enfría (%s)" % kovu.global_position)
	_comprobar(kovu.recibir_golpe(1, Vector2.RIGHT) and kovu.vida == 2, "fuera, el cetro sí entra")
	kovu.recibir_golpe(1, Vector2.RIGHT)
	kovu.recibir_golpe(1, Vector2.RIGHT)
	await _esperar(0.5)
	_comprobar(get_tree().get_nodes_in_group("kovus").size() == 2 and int(Estado.extra.get("bestiario", {}).get("kovu", 0)) == 1, "tres golpes y cuenta en el Bestiario")

	print("La Nave de las Grúas:")
	var sur := get_tree().current_scene.get_node("Barcaza_sur") as Node2D
	m.global_position = _centro(sur)
	_pulsar(m)
	await _cruzar(sur)
	_comprobar(sur.en_b and m.global_position.y > 41.0 * 16.0, "la barcaza del sur lleva a la Nave")
	bloque = _cerca("bloques_iman", 36, 49)
	m.global_position = _sitio(43, 49)
	_pulsar(m)
	await _esperar(1.6)
	_comprobar(bloque.casilla() == Vector2i(42, 49), "el bloque viene hasta quedarse al lado de Maisha (%s)" % bloque.casilla())
	m.global_position = _sitio(49, 49)
	_pulsar(m)
	await _esperar(1.4)
	_comprobar(bloque.casilla() == Vector2i(46, 49) and Estado.tiene("fundicion/compuerta_nave"), "al segundo tirón encaja en la placa y abre la compuerta de la Nave (%s)" % bloque.casilla())
	m.global_position = _cerca("recogibles", 57, 49).global_position
	await _esperar(0.5)
	_comprobar(Estado.tiene("esquirla/nave") and Estado.cuantos("esquirla_estrella") == 1, "detrás, una Esquirla de Estrella")
	m.global_position = _centro(sur)
	_pulsar(m)
	await _cruzar(sur)

	print("La Gran Fragua: Nyundo:")
	var este := get_tree().current_scene.get_node("Barcaza_este") as Node2D
	m.global_position = _centro(este)
	_pulsar(m)
	await _cruzar(este)
	_comprobar(este.en_b and m.global_position.x > 54.0 * 16.0, "la barcaza del este lleva a la Gran Fragua")
	var nyundo := get_tree().get_first_node_in_group("nyundos") as Node2D
	_comprobar(nyundo != null and nyundo.fase == nyundo.Fase.DORMIDO, "Nyundo espera en el centro, apagado")
	m.global_position = nyundo.global_position + Vector2(-100, 10)
	await _esperar(0.6)
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(nyundo.fase != nyundo.Fase.DORMIDO and Sonido.musica_actual == "jefe_nyundo", "al entrar, despierta (suena «Las cuatro tenazas del crisol»)")
	_comprobar(not nyundo.recibir_golpe(1, Vector2.RIGHT) and nyundo.vida == 12, "el cetro rebota en el peto")
	nyundo.set("_cd", 0.0)
	var repelida := false
	for i in 400:
		if nyundo.fase == nyundo.Fase.TENAZA and nyundo.punta().distance_to(m.global_position + Vector2(0, -8)) < 55.0:
			repelida = _pulsar(m) and nyundo.get("_repelida")
			break
		await get_tree().process_frame
	_comprobar(repelida, "un Pulso con la tenaza ya encima la repele")
	await _esperar(0.6)
	_comprobar(nyundo.abolladuras == 1, "y le da a él en el peto: una abolladura (%d)" % nyundo.abolladuras)
	nyundo.set("_ataques", 2)
	nyundo.set("_cd", 0.0)
	var devuelto := false
	for i in 400:
		if nyundo.fase == nyundo.Fase.BLOQUE and nyundo.get("_t") > 0.55:
			devuelto = _pulsar(m) and nyundo.get("_devuelto")
			break
		await get_tree().process_frame
	_comprobar(devuelto, "un Pulso con el bloque ya cayendo se lo devuelve")
	await _esperar(0.8)
	_comprobar(nyundo.fase == nyundo.Fase.ABIERTO, "a la segunda abolladura se le abre el peto (%d)" % nyundo.fase)
	for i in 4:
		nyundo.recibir_golpe(1, Vector2.RIGHT)
		await _esperar(0.15)
	await _esperar(0.2)
	_comprobar(nyundo.vida == 8 and nyundo.fase == nyundo.Fase.GUARDIA and nyundo.abolladuras == 0, "cuatro golpes al núcleo y se cierra (vida %d)" % nyundo.vida)
	for k in 2:
		nyundo.abrir()
		for i in 4:
			nyundo.recibir_golpe(1, Vector2.RIGHT)
			await _esperar(0.15)
		if k == 0:
			_comprobar(nyundo.furia() and nyundo.vida == 4, "con la mitad de la vida, entra en furia (vida %d)" % nyundo.vida)
	await _esperar(0.4)
	_comprobar(Estado.tiene("nyundo_vencido") and Estado.tiene("cadena_este_rota"), "vencido: se rompe la Cadena del Este")
	_comprobar(Misiones.estado(Misiones.buscar("fundicion_escoria")) == "hecha", "misión cumplida")
	var esquirla: Node2D = null
	for r in get_tree().get_nodes_in_group("recogibles"):
		if r.marca == "esquirla/nyundo":
			esquirla = r
	_comprobar(esquirla != null, "suelta una Esquirla de Estrella")
	await _esperar(3.4)
	await _leer_dialogo()
	_comprobar(Sonido.musica_actual == "fundicion_escoria", "vuelve la música de la Fundición (%s)" % Sonido.musica_actual)

	print("Volver:")
	await _ir("fundicion_escoria", "oeste", "FundicionEscoria")
	_comprobar(get_tree().get_first_node_in_group("nyundos") == null, "al volver, Nyundo ya no está")
	_comprobar(_cerca("compuertas", 48, 30).abierta and _cerca("bloques_iman", 38, 25).casilla() == Vector2i(38, 25), "las compuertas siguen abiertas y los bloques, en sus placas")
	await _ir("mji_jiwe", "fundicion", "MjiJiwe")
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.x > 1050.0, "de vuelta a Mji-Jiwe se sale por la verja del este (%s)" % m.global_position)

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
