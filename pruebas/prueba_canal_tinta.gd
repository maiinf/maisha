extends Node
## Prueba automática de El Canal de Tinta (Sigilia), parte 1: se llega desde Maandiko por el este, suena su música,
## Maisha piensa al llegar, la tinta del cauce no se pisa, el muelle norte lleva hasta la Gran Dársena, el tapón de
## Tinta Quieta del Remanso Norte está puesto y se vuelve a Maandiko.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_canal_tinta

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
	_comprobar(m.global_position.x < 4 * 16 and m.global_position.y > 15 * 16 and m.global_position.y < 20 * 16,
			"aparece en el muelle norte, junto a la entrada")

	print("La tinta y los muelles:")
	m.global_position = Vector2(30 * 16 + 8, 19 * 16)
	await _andar(m, "mover_abajo", 1.2)
	_comprobar(m.global_position.y < 21 * 16, "la tinta del cauce no se pisa")
	m.global_position = Vector2(60 * 16 + 8, 17 * 16)
	await _andar(m, "mover_derecha", 2.5)
	_comprobar(m.global_position.x > 70 * 16, "el muelle norte sigue hacia la Gran Dársena (x=%d)" % int(m.global_position.x / 16))
	var charcos := 0
	for n in get_tree().get_nodes_in_group("charcos_tinta"):
		charcos += 1
	_comprobar(charcos == 1, "un tapón de Tinta Quieta cierra el Remanso Norte (%d)" % charcos)

	print("El Sigilo de Hielo y las placas:")
	_comprobar(not m.cambiar_sigilo() and m.sigilo_elegido() == "fuego", "con un solo sigilo, R no cambia nada")
	Estado.marcar("sigilo_hielo")
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
	m.global_position = Vector2(30 * 16 + 8, 17 * 16)
	await _esperar(0.8)
	m.aliento = m.aliento_maximo()
	m.sigilo()
	await _esperar(0.5)
	_comprobar(get_tree().get_nodes_in_group("placas_hielo").is_empty(), "en el muelle, el hielo no hace placas")
	m.cambiar_sigilo()
	_comprobar(m.sigilo_elegido() == "fuego", "R vuelve al Sigilo de Fuego")

	print("De vuelta:")
	await _ir("maandiko", "canal", "Maandiko")
	_comprobar(_escena() == "Maandiko", "se vuelve a Maandiko por la salida del este")

	print()
	print("RESULTADO: todo correcto" if _fallos == 0 else "RESULTADO: %d fallos" % _fallos)
	get_tree().quit(1 if _fallos else 0)
