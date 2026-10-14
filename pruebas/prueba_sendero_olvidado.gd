extends Node
## Prueba automática del Sendero Olvidado: los braseros (encender con una semilla, el calor), la escarcha de la
## quietud (congelarse quita una hoja), las estatuas, las puertas y la misión.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_sendero_olvidado

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _maisha() -> CharacterBody2D:
	return get_tree().get_first_node_in_group("maisha") as CharacterBody2D


func _escena() -> String:
	var e := get_tree().current_scene
	return e.name if e else ""


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 80:
		if not dialogo.hablando:
			return
		dialogo.pasar()
		await _esperar(0.08)


func _puerta(id: String) -> Area2D:
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == id:
			return p
	return null


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["cetro_recibido", "visto/cuna_de_musgo", "gruta_guardian", "nueve_ecos", "sendero_abierto"]:
		Estado.marcar(m)
	Estado.jugando = true
	_comprobar(Misiones.estado(Misiones.buscar("sendero_olvidado")) != "", "con el sendero abierto aparece la misión «El Sendero Olvidado»")
	get_tree().change_scene_to_file("res://escenas/mundo/sendero_olvidado.tscn")
	await _esperar(1.5)

	print("El sendero:")
	_comprobar(_escena() == "SenderoOlvidado" and Estado.tiene("sendero_olvidado"), "se llega al Sendero Olvidado (y la misión de los ecos se cumple)")
	_comprobar(Sonido.musica_actual == "olvidado", "con su música («La montaña que no se mueve»)")
	await _esperar(1.0)
	await _leer_dialogo()
	await _esperar(0.4)
	_comprobar(Estado.tiene("olvidado_llegada"), "Maisha nota el frío al llegar")
	var braseros := get_tree().get_nodes_in_group("braseros")
	var encendidos := braseros.filter(func(b: Node) -> bool: return b.encendido)
	_comprobar(braseros.size() == 6 and encendidos.size() == 1, "seis braseros, y solo el de la entrada encendido (%d, %d)" % [braseros.size(), encendidos.size()])
	_comprobar(get_tree().get_nodes_in_group("estatuas_olvidado").size() == 3, "tres estatuas de quienes se quedaron quietos")

	print("La escarcha de la quietud:")
	var maisha := _maisha()
	var escarcha: Node2D = get_tree().current_scene.get("escarcha")
	maisha.global_position = Vector2(20 * 16, 60 * 16)
	await _esperar(0.3)
	var vida: int = maisha.vida
	await _esperar(2.5)
	_comprobar(escarcha.frio > 0.1, "quieta lejos del fuego, el frío sube (%.2f)" % escarcha.frio)
	await _esperar(5.0)
	_comprobar(escarcha.esta_congelada() or maisha.vida < vida, "si no se mueve, se congela")
	await _esperar(1.6)
	_comprobar(maisha.vida == vida - 1 and maisha.get("puede_actuar") == false or maisha.vida == vida - 1, "y pierde una hoja de Vida (%d → %d)" % [vida, maisha.vida])
	await _esperar(0.5)
	await _leer_dialogo()
	_comprobar(Estado.tiene("olvidado_congelada"), "la primera vez, Maisha entiende lo que pasa")
	var antes: float = escarcha.frio
	Input.action_press("mover_derecha")
	await _esperar(0.8)
	Input.action_release("mover_derecha")
	_comprobar(escarcha.frio < antes, "andando, el frío baja (%.2f → %.2f)" % [antes, escarcha.frio])

	print("Los braseros:")
	var rellano: Node2D = null
	for b in braseros:
		if (b as Node2D).global_position.distance_to(Vector2(30 * 16 + 8, 52 * 16 + 14)) < 4.0:
			rellano = b
	_comprobar(rellano != null and not rellano.encendido, "el brasero del rellano está apagado")
	maisha.global_position = rellano.global_position + Vector2(0, 16)
	await _esperar(0.3)
	maisha.call("lanzar_semilla")
	await _esperar(0.05)
	for s in get_tree().get_nodes_in_group("semillas"):
		s.call("estallar")
	await _esperar(0.3)
	_comprobar(rellano.encendido and Estado.tiene(rellano.marca), "una semilla lo enciende (y se queda encendido)")
	escarcha.frio = 0.8
	await _esperar(1.0)
	_comprobar(escarcha.frio < 0.3 and escarcha.ultimo_brasero == rellano, "junto al fuego, el frío se va deprisa (%.2f)" % escarcha.frio)

	print("Las estatuas:")
	var estatua: Node = get_tree().get_nodes_in_group("estatuas_olvidado")[0]
	maisha.global_position = (estatua as Node2D).global_position + Vector2(0, 18)
	await _esperar(0.2)
	estatua.interactuar()
	await _esperar(0.3)
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	_comprobar(dialogo.hablando, "mirar una estatua cuenta qué quería guardar")
	await _leer_dialogo()

	print("Las puertas:")
	var ruinas: Area2D = _puerta("ruinas")
	maisha.global_position = ruinas.global_position + Vector2(0, 30)
	await _esperar(0.4)
	maisha.global_position = ruinas.global_position
	await _esperar(0.8)
	await _leer_dialogo()
	await _esperar(0.4)
	_comprobar(_escena() == "SenderoOlvidado" and maisha.get("puede_actuar"), "las Ruinas aún no se abren, y Maisha no se queda atascada")
	var gruta: Area2D = _puerta("gruta")
	maisha.global_position = gruta.global_position + Vector2(0, -30)
	await _esperar(0.3)
	Input.action_press("mover_abajo")
	for i in 400:
		if Estado.cambiando:
			break
		await get_tree().process_frame
	Input.action_release("mover_abajo")
	for i in 300:
		if _escena() == "GrutaRaices" and not Estado.cambiando:
			break
		await get_tree().process_frame
	_comprobar(_escena() == "GrutaRaices", "por el sur se baja a la Gruta")

	Estado.jugando = false
	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
