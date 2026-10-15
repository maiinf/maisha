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


func _cruzar(accion: String, nombre: String) -> void:
	Input.action_press(accion)
	for i in 400:
		if Estado.cambiando:
			break
		await get_tree().process_frame
	Input.action_release(accion)
	for i in 300:
		if _escena() == nombre and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(0.3)


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

	# (los Quietos, lejos mientras se prueba lo demás: si no, atacan a Maisha cuando se queda quieta)
	var salida_quietos := {}
	for n in get_tree().get_nodes_in_group("quietos"):
		salida_quietos[n] = (n as Node2D).global_position
		(n as Node2D).global_position += Vector2(0, 4000)

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
	_comprobar(maisha.vida == vida - 1, "y pierde una hoja de Vida (%d → %d)" % [vida, maisha.vida])
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

	print("Los Quietos:")
	var quietos := get_tree().get_nodes_in_group("quietos")
	_comprobar(quietos.size() == 7, "siete Quietos por el sendero (%d)" % quietos.size())
	var q: CharacterBody2D = null
	for n in quietos:
		if (salida_quietos[n] as Vector2).distance_to(Vector2(17 * 16 + 8, 56 * 16 + 14)) < 4.0:
			q = n
	q.global_position = salida_quietos[q]                   # (los demás siguen lejos)
	maisha.global_position = q.global_position + Vector2(70, 0)
	maisha.call("mirar", Vector2.LEFT)
	await _esperar(0.3)
	var donde := q.global_position
	await _esperar(1.0)
	_comprobar(q.mirado and q.global_position.distance_to(donde) < 1.0, "mirándolo, no se mueve")
	maisha.call("mirar", Vector2.RIGHT)
	await _esperar(0.35)
	_comprobar(not q.mirado and q.global_position.distance_to(maisha.global_position) < 60.0, "de espaldas, se acerca muy deprisa (%.0f)" % q.global_position.distance_to(maisha.global_position))
	maisha.call("mirar", Vector2.LEFT)
	await _esperar(0.2)
	var vida_q: int = q.vida
	q.global_position = maisha.global_position + Vector2(-16, 0)
	await _esperar(0.1)
	for i in 3:
		if is_instance_valid(q):
			q.global_position = maisha.global_position + Vector2(-16, 0)    # (como si Maisha diera un paso)
		maisha.call("golpear")
		await _esperar(0.6)
	_comprobar(not is_instance_valid(q) or q.vida <= 0, "tres golpes de frente lo rompen (tenía %d)" % vida_q)
	await _esperar(0.5)
	_comprobar(Bestiario.cuantos("quieto") >= 1, "y queda en el Bestiario")

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
	await _esperar(0.3)
	await _cruzar("mover_arriba", "RuinasPrimerArbol")
	_comprobar(_escena() == "RuinasPrimerArbol", "por el arco del norte se llega a las Ruinas del Primer Árbol")
	var de_vuelta: Area2D = _puerta("sendero")
	_maisha().global_position = de_vuelta.global_position + Vector2(0, -30)
	await _esperar(0.3)
	await _cruzar("mover_abajo", "SenderoOlvidado")
	_comprobar(_escena() == "SenderoOlvidado", "y se vuelve a bajar")
	maisha = _maisha()
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
