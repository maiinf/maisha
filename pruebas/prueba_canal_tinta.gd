extends Node
## Prueba automática de El Canal de Tinta (Sigilia), parte 1: se llega desde Maandiko por el este, suena su música,
## Maisha piensa al llegar, la tinta del cauce no se pisa, el muelle norte lleva hasta la Gran Dársena, el tapón de
## Tinta Quieta del Remanso Norte está puesto, Mfereji y su ficha, el Sigilo de Hielo y sus placas, las compuertas,
## la Esclusa Hundida (la tinta baja al sur), la trampilla que se abre desde abajo, la estela, Ruba (oculta, muerde,
## atrapada en el hielo y vencida), la ficha de Karatasi en el andén, y en Maandiko Karatasi recupera su nombre.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_canal_tinta

const PLACA := preload("res://scripts/mundo/sigilia/placa_hielo.gd")
const TRAMPILLA := preload("res://scripts/mundo/sigilia/trampilla.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")

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


func _andar(m: CharacterBody2D, accion: String, s: float) -> void:
	Input.action_press(accion)
	await _esperar(s)
	Input.action_release(accion)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["cetro_recibido", "visto/cuna_de_musgo", "sigilo_fuego", "maandiko_llegada", "kalamu_conocida", "mapa_norte"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("La llegada:")
	await _ir("canal_tinta", "ciudad", "CanalTinta")
	_comprobar(_escena() == "CanalTinta" and Estado.tiene("canal_tinta"), "se llega al Canal de Tinta desde Maandiko")
	_comprobar(Sonido.musica_actual == "canal_tinta", "suena «Lo que lleva la corriente» (%s)" % Sonido.musica_actual)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("canal_llegada"), "Maisha mira la tinta que corre al llegar")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var rubas := get_tree().get_nodes_in_group("rubas")
	_comprobar(rubas.size() == 4, "cuatro Rubas nadan en la tinta (%d)" % rubas.size())
	for r in rubas:
		r.set_process(false)              # (quietas hasta su parte de la prueba)
	_comprobar(m.global_position.x < 4 * 16 and m.global_position.y > 15 * 16 and m.global_position.y < 20 * 16,
			"aparece en el muelle norte, junto a la entrada")

	print("La tinta y los muelles:")
	m.global_position = Vector2(30 * 16 + 8, 19 * 16)
	await _andar(m, "mover_abajo", 1.2)
	_comprobar(m.global_position.y < 21 * 16, "la tinta del cauce no se pisa")
	m.global_position = Vector2(60 * 16 + 8, 17 * 16)
	await _andar(m, "mover_derecha", 2.5)
	_comprobar(m.global_position.x < 69 * 16, "el muelle norte se acaba antes de la Gran Dársena (x=%d)" % int(m.global_position.x / 16))
	m.global_position = Vector2(23 * 16 + 16, 20 * 16 + 8)
	await _andar(m, "mover_abajo", 4.0)
	_comprobar(m.global_position.y > 31 * 16, "la pasarela de la esclusa cruza el cauce hasta el muelle sur")
	var charcos := 0
	for n in get_tree().get_nodes_in_group("charcos_tinta"):
		charcos += 1
	_comprobar(charcos == 1, "un tapón de Tinta Quieta cierra el Remanso Norte (%d)" % charcos)

	print("Mfereji y su ficha:")
	var mfereji: Node = null
	for a in get_tree().get_nodes_in_group("escribas"):
		if a.nombre == "mfereji":
			mfereji = a
	_comprobar(mfereji != null and mfereji.id == "mfereji_blanco", "junto a la primera compuerta, Mfereji está en blanco")
	m.global_position = (mfereji as Node2D).global_position + Vector2(-18, 6)
	mfereji.interactuar()
	await _leer_dialogo()
	_comprobar(not Estado.tiene("mfereji_nombre"), "sin su ficha, solo se le mira")
	var tapon: Node2D = get_tree().get_nodes_in_group("charcos_tinta")[0]
	for i in 3:
		m.global_position = tapon.global_position + Vector2(0, 26)
		m.mirar(Vector2.UP)
		m.aliento = m.aliento_maximo()
		await _esperar(0.8)
		m.sigilo()
		await _esperar(0.5)
	await _esperar(0.7)
	_comprobar(not is_instance_valid(tapon) or not tapon.is_in_group("charcos_tinta"), "el fuego derrite el tapón del Remanso Norte")
	var ficha: Node2D = null
	for r in get_tree().get_nodes_in_group("recogibles"):
		if r.objeto == "ficha_mfereji":
			ficha = r
	m.global_position = ficha.global_position
	await _esperar(0.4)
	_comprobar(Estado.cuantos("ficha_mfereji") == 1, "en su casa, la ficha de Mfereji")
	_comprobar(not m.cambiar_sigilo() and m.sigilo_elegido() == "fuego", "con un solo sigilo, R no cambia nada")
	m.global_position = (mfereji as Node2D).global_position + Vector2(-18, 6)
	mfereji.interactuar()
	await _leer_dialogo()
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("mfereji_nombre") and mfereji.id == "mfereji", "al darle su ficha, recupera el nombre y el color")
	_comprobar(Estado.tiene("sigilo_hielo") and Estado.cuantos("llave_compuerta") == 1, "enseña el Sigilo de Hielo y da la llave de compuerta")

	print("El Sigilo de Hielo y las placas:")
	_comprobar(m.cambiar_sigilo() and m.sigilo_elegido() == "hielo", "con el de hielo aprendido, R pasa al Sigilo de Hielo")
	m.global_position = Vector2(30 * 16 + 8, 20 * 16 + 8)
	await _andar(m, "mover_abajo", 0.3)
	m.aliento = m.aliento_maximo()
	await _esperar(0.8)
	_comprobar(m.sigilo(), "Maisha traza la runa de hielo hacia la tinta")
	await _esperar(0.5)
	var placas := get_tree().get_nodes_in_group("placas_hielo")
	_comprobar(placas.size() == 1, "la tinta se endurece en una placa de hielo (%d)" % placas.size())
	if placas.size() == 1:
		var placa: Node2D = placas[0]
		var x0 := placa.position.x
		await _esperar(1.0)
		_comprobar(placa.position.x > x0 + 8.0, "la corriente lleva la placa hacia el este")
		# se sube andando hacia ella
		m.global_position = Vector2(placa.position.x, 20 * 16 + 8)
		await _andar(m, "mover_abajo", 0.4)
		_comprobar(placa.encima(), "Maisha salta encima de la placa")
		var xm := m.global_position.x
		await _esperar(1.5)
		_comprobar(m.global_position.x > xm + 16.0 and placa.contiene(m.global_position), "la placa la lleva (y no se cae)")
		await _andar(m, "mover_abajo", 1.0)
		_comprobar(placa.encima() and m.global_position.y < 31 * 16, "andar hacia la tinta no la saca de la placa")
		# de vuelta al muelle norte
		await _andar(m, "mover_arriba", 1.5)
		_comprobar(not placa.encima() and m.global_position.y < 21 * 16, "y anda hacia el muelle para bajar")
		# la compuerta cerrada la para
		placa.position.x = 46 * 16 - 30
		await _esperar(1.5)
		_comprobar(placa.quieta and placa.position.x < 46 * 16 - 20, "la compuerta cerrada frena la placa")
		# si se deshace con Maisha encima, se hunde
		m.global_position = Vector2(placa.position.x, 20 * 16 + 8)
		await _andar(m, "mover_abajo", 0.4)
		var hojas: int = m.vida
		placa.vida = 0.2
		await _esperar(1.5)
		_comprobar(m.vida == hojas - 1 and m.global_position.y < 21 * 16, "si se deshace con ella encima, se hunde, pierde una hoja y vuelve a la orilla")
		_comprobar(not is_instance_valid(placa), "y la placa se deshace")
	print("Las compuertas:")
	var compuerta: Node = null
	for c in get_tree().get_nodes_in_group("compuertas"):
		if c.columna == 46:
			compuerta = c
	_comprobar(get_tree().get_nodes_in_group("compuertas").size() == 2 and compuerta != null and not compuerta.abierta,
			"dos compuertas con su rueda dorada, cerradas")
	compuerta.interactuar()
	await _esperar(1.6)
	_comprobar(compuerta.abierta and Estado.tiene("compuerta/46"), "con la llave, la rueda gira y la compuerta sube")
	var otra: Node2D = PLACA.helar_en(m.get_parent(), Vector2(46 * 16 - 30, 25 * 16))
	await _esperar(2.5)
	_comprobar(otra != null and otra.position.x > 46 * 16 + 8, "con la compuerta abierta, la placa sigue")
	compuerta.interactuar()
	await _esperar(1.6)
	_comprobar(not compuerta.abierta and not Estado.tiene("compuerta/46"), "otra vuelta y la compuerta baja")
	Estado.quitar("llave_compuerta")
	(get_tree().get_nodes_in_group("compuertas")[1]).interactuar()
	await _leer_dialogo()
	_comprobar(not Estado.tiene("compuerta/66"), "sin la llave, la rueda no se mueve")
	Estado.dar("llave_compuerta")

	print("La Esclusa Hundida:")
	var escena := get_tree().current_scene
	_comprobar(escena.corriente_en(Vector2(48, 40) * 16.0) == Vector2.DOWN and escena.corriente_en(Vector2(30, 25) * 16.0) == Vector2.RIGHT,
			"en la Esclusa Hundida la tinta baja hacia el sur; en el cauce, al este")
	var baja: Node2D = PLACA.helar_en(m.get_parent(), Vector2(48, 38) * 16.0)
	var y0 := baja.position.y
	await _esperar(1.5)
	_comprobar(baja.position.y > y0 + 16.0 and absf(baja.position.x - 48 * 16) < 2.0, "la placa baja hacia el andén del fondo")
	var trampilla: Node = get_tree().get_nodes_in_group("interactuables").filter(func(n): return n.get_script() == TRAMPILLA)[0]
	m.global_position = Vector2(40 * 16, 35 * 16 + 4)
	trampilla.interactuar()
	await _leer_dialogo()
	await _andar(m, "mover_abajo", 0.8)
	_comprobar(m.global_position.y < 36 * 16 and not Estado.tiene("canal/trampilla"), "desde arriba, la trampilla no se abre")
	m.global_position = Vector2(40 * 16, 38 * 16)
	trampilla.interactuar()
	await _esperar(0.3)
	await _andar(m, "mover_arriba", 1.0)
	_comprobar(Estado.tiene("canal/trampilla") and m.global_position.y < 36 * 16, "desde la escalerilla se abre y se sube al muelle sur")

	print("La estela:")
	var estela: Node = get_tree().get_nodes_in_group("interactuables").filter(func(n): return n.get_script() == LECTURA)[0]
	estela.interactuar()
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	await _esperar(0.2)
	_comprobar(dialogo.hablando, "la estela del copo se lee")
	await _leer_dialogo()

	m.global_position = Vector2(30 * 16 + 8, 17 * 16)
	await _esperar(0.8)
	var antes := get_tree().get_nodes_in_group("placas_hielo").size()
	m.aliento = m.aliento_maximo()
	m.sigilo()
	await _esperar(0.5)
	_comprobar(get_tree().get_nodes_in_group("placas_hielo").size() == antes, "en el muelle, el hielo no hace placas")
	m.cambiar_sigilo()
	_comprobar(m.sigilo_elegido() == "fuego", "R vuelve al Sigilo de Fuego")

	print("Ruba:")
	for p in get_tree().get_nodes_in_group("placas_hielo"):
		p.queue_free()
	m.cambiar_sigilo()
	var ruba: Node2D = rubas[0]
	ruba.set_process(true)
	m.global_position = Vector2(34 * 16 + 8, 20 * 16 + 8)
	m.mirar(Vector2.DOWN)
	_comprobar(ruba.fase == ruba.Fase.OCULTA and not ruba.is_in_group("golpeables"), "oculta bajo la tinta: solo se ven las ondas")
	var hojas2: int = m.vida
	for i in 40:
		await _esperar(0.1)
		if ruba.fase == ruba.Fase.LANZA:
			break
	_comprobar(ruba.fase == ruba.Fase.LANZA or ruba.fase == ruba.Fase.OCULTA, "nada hacia Maisha, asoma y se lanza")
	await _esperar(0.5)
	_comprobar(m.vida == hojas2 - 1, "muerde: Maisha pierde una hoja")
	_comprobar(ruba.fase == ruba.Fase.OCULTA and not ruba.recibir_golpe(1, Vector2.DOWN), "se vuelve a hundir, y en la tinta no hay forma de darle")
	# el hielo encima la atrapa
	var placas_antes := get_tree().get_nodes_in_group("placas_hielo").size()
	ruba.global_position = m.global_position + Vector2(0, 16)
	await _esperar(1.0)
	m.aliento = m.aliento_maximo()
	m.mirar(Vector2.DOWN)
	_comprobar(m.sigilo_elegido() == "hielo" and m.sigilo(), "Maisha le traza la runa de hielo encima")
	await _esperar(0.4)
	_comprobar(ruba.fase == ruba.Fase.ATRAPADA, "Ruba se queda atrapada en un témpano, con media cabeza fuera")
	_comprobar(get_tree().get_nodes_in_group("placas_hielo").size() == placas_antes, "(y el sigilo no hace además una placa)")
	var vencidas := int(Estado.extra.get("bestiario", {}).get("ruba", 0))
	for i in 3:
		m.mirar(Vector2.DOWN)
		m.golpear()
		await _esperar(0.5)
	await _esperar(0.5)
	_comprobar(not is_instance_valid(ruba) or ruba.is_queued_for_deletion() or ruba.vida <= 0, "tres golpes de cetro y Ruba se deshace")
	_comprobar(int(Estado.extra.get("bestiario", {}).get("ruba", 0)) == vencidas + 1, "y cuenta en el Bestiario")
	# si no se le da a tiempo, rompe el hielo
	var otra_ruba: Node2D = rubas[1]
	otra_ruba.set_process(true)
	otra_ruba.congelar()
	await _esperar(4.4)
	_comprobar(otra_ruba.fase == otra_ruba.Fase.OCULTA, "si no se le da a tiempo, rompe el hielo y se hunde")
	otra_ruba.set_process(false)

	print("La ficha de la Esclusa Hundida:")
	var ficha2: Node2D = null
	for r in get_tree().get_nodes_in_group("recogibles"):
		if r.objeto == "ficha_karatasi":
			ficha2 = r
	_comprobar(ficha2 != null and ficha2.global_position.y > 51 * 16, "en el andén del fondo, otra ficha del Índice")
	m.global_position = ficha2.global_position
	await _esperar(0.4)
	_comprobar(Estado.cuantos("ficha_karatasi") == 1, "es la de Karatasi")

	print("De vuelta:")
	await _ir("maandiko", "canal", "Maandiko")
	_comprobar(_escena() == "Maandiko", "se vuelve a Maandiko por la salida del este")
	var karatasi: Node = null
	for a in get_tree().get_nodes_in_group("escribas"):
		if a.nombre == "karatasi":
			karatasi = a
	_comprobar(karatasi != null and karatasi.id == "escriba_blanco", "en Maandiko, Karatasi está en blanco")
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	m.global_position = (karatasi as Node2D).global_position + Vector2(-18, 6)
	karatasi.interactuar()
	await _leer_dialogo()
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("karatasi_nombre") and karatasi.id == "escriba" and Estado.tiene("karatasi_hablado"), "al darle su ficha, recupera el nombre y habla")

	print()
	print("RESULTADO: todo correcto" if _fallos == 0 else "RESULTADO: %d fallos" % _fallos)
	get_tree().quit(1 if _fallos else 0)
