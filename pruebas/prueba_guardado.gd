extends Node
## Prueba automática de la pantalla de inicio, el guardado de partida y el menú de pausa.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_guardado
## (usa su propio archivo de partida: no toca la partida de verdad)

const R := preload("res://scripts/combate/reglas_combate.gd")
var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


func _escena() -> String:
	var e := get_tree().current_scene
	return e.name if e else ""


func _puerta(id: String) -> Area2D:
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == id:
			return p
	return null


func _empujar(accion: String, segundos: float) -> void:
	Input.action_press(accion)
	await _esperar(segundos)
	Input.action_release(accion)


func _pulsar_accion() -> void:
	# se pulsa al empezar un fotograma (como una tecla de verdad), no a mitad
	await get_tree().process_frame
	Input.action_press("accion")
	await get_tree().process_frame
	await get_tree().process_frame
	Input.action_release("accion")
	await get_tree().process_frame


## Pasa todas las líneas del diálogo abierto
func _leer_dialogo() -> int:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	var lineas := 0
	for i in 60:
		if not dialogo.hablando:
			break
		await _pulsar_accion()
		await _pulsar_accion()
		lineas += 1
	await _esperar(0.25)
	return lineas


## Camina en una dirección hasta cruzar una puerta y llegar a la escena «nombre»
func _cruzar(accion: String, nombre: String) -> void:
	Input.action_press(accion)
	for i in 400:
		if Estado.cambiando:
			break
		await get_tree().process_frame
	Input.action_release(accion)
	await _esperar_cambio(nombre)


## Espera a que termine un cambio de escena
func _esperar_cambio(nombre: String) -> void:
	for i in 900:
		if _escena() == nombre and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(0.2)


## Purga una zona de los prados con semillas, como en prueba_prados
func _purgar(zona: Node2D) -> void:
	var maisha := _maisha()
	maisha.global_position = zona.global_position + Vector2(-zona.radios_umbral.x - 20, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	maisha.global_position = zona.global_position + Vector2(-zona.radios_umbral.x * 0.8, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.queue_free()
	zona.set("_invocar", 999.0)
	var nucleo: Node2D = zona.get("_nucleo")
	var c := R.casilla_de(nucleo.global_position)
	for v in 3:
		maisha.aliento = R.ALIENTO_MAXIMO
		maisha.vida = R.VIDA_MAXIMA
		maisha.global_position = R.centro_de(c + Vector2i(-2, 0))
		maisha.lanzar_semilla()
		maisha.global_position = R.centro_de(c + Vector2i(-3, 3))
		await _esperar(R.SEMILLA_MECHA + 0.2)


func _inicio() -> Node:
	return get_tree().current_scene


func _opcion(accion: String) -> int:
	return _inicio()._acciones.find(accion)


func _pulsar(accion: String) -> void:
	await get_tree().process_frame
	Input.action_press(accion)
	await get_tree().process_frame
	await get_tree().process_frame
	Input.action_release(accion)
	await get_tree().process_frame


func _ready() -> void:
	Engine.time_scale = 3.0
	Estado.olvidar_todo()
	get_tree().change_scene_to_file("res://escenas/interfaz/inicio.tscn")
	await _esperar_cambio("Inicio")

	print("Pantalla de inicio sin partida:")
	_comprobar(_opcion("continuar") == -1 and _opcion("nueva") == 0, "sin partida guardada no sale «Continuar» (%s)" % [_inicio()._acciones])
	_comprobar(not Estado.jugando, "en el inicio no se está jugando")

	print("Nueva partida:")
	_inicio()._al_elegir(_opcion("nueva"))
	for i in 1500:
		if _escena() == "Kitovu" and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(0.3)
	_comprobar(_escena() == "Kitovu", "tras la introducción se despierta en el Kitovu")
	_comprobar(Estado.hay_partida(), "al llegar se guarda la partida")
	await _esperar(3.0)
	while get_tree().get_first_node_in_group("dialogo").hablando:
		await _pulsar("accion")
		await _esperar(0.1)
	Estado.marcar("tarea_cosecha")
	get_tree().get_nodes_in_group("zanahorias")[0].arrancar()
	await _esperar(0.3)
	var datos := Estado.leer_partida()
	_comprobar(int(datos.get("objetos", {}).get("zanahoria", 0)) == 1, "al coger una zanahoria se guarda sola")

	print("Pausa:")
	var sitio := _maisha().global_position + Vector2(20, 30)
	_maisha().global_position = sitio
	await _esperar(0.2)
	await _pulsar("menu")
	var pausa := get_tree().get_first_node_in_group("pausa")
	_comprobar(pausa.abierto and get_tree().paused, "Esc abre la pausa y para el juego")
	Input.action_press("mover_derecha")
	await _esperar(0.4)
	Input.action_release("mover_derecha")
	_comprobar(_maisha().global_position.distance_to(sitio) < 0.5, "en pausa Maisha no se mueve")
	await _pulsar("menu")
	_comprobar(not pausa.abierto and not get_tree().paused, "Esc otra vez vuelve al juego")
	await _pulsar("menu")
	pausa._al_elegir(pausa._acciones.find("inicio"))
	await _esperar_cambio("Inicio")
	_comprobar(_escena() == "Inicio" and not get_tree().paused, "«Volver al inicio» lleva a la pantalla de inicio")
	datos = Estado.leer_partida()
	var guardada := Vector2(datos["posicion"][0], datos["posicion"][1])
	_comprobar(datos["escena"] == "kitovu" and guardada.distance_to(sitio) < 1.0, "se guardó la escena y el sitio exacto (%s)" % guardada)

	print("Continuar:")
	var i_cont := _opcion("continuar")
	_comprobar(i_cont == 0, "ahora sale «Continuar» la primera")
	_comprobar(String(_inicio()._lista.opciones[0].get("nota", "")).begins_with("Kitovu"), "con el sitio y el tiempo: «%s»" % _inicio()._lista.opciones[0].get("nota", ""))
	Estado.olvidar_todo()          # como si se acabara de abrir el juego
	_inicio()._al_elegir(i_cont)
	await _esperar_cambio("Kitovu")
	_comprobar(_maisha().global_position.distance_to(sitio) < 1.0, "Maisha aparece donde se guardó")
	_comprobar(Estado.cuantos("zanahoria") == 1, "lleva la zanahoria que había cogido")
	_comprobar(get_tree().get_nodes_in_group("zanahorias").size() == 7, "y esa zanahoria ya no está en el huerto")
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando == false and Estado.tiene("kitovu_despierta"), "al continuar no se repite el despertar")

	print("En plena pelea no se guarda el sitio:")
	Estado.marcar("cetro_recibido")
	Estado.marcar("narr/zona")            # sin el narrador, para ir al grano
	var zona: Node2D = get_tree().get_nodes_in_group("zonas")[0]
	zona.activa = true
	await _esperar(0.2)                   # deja que se guarde lo de las marcas
	var antes := Estado.posicion
	_maisha().global_position = zona.punto_del_umbral(PI, 1.15)
	await _esperar(0.2)
	Estado.guardar()
	datos = Estado.leer_partida()
	_comprobar(Vector2(datos["posicion"][0], datos["posicion"][1]).distance_to(antes) < 1.0, "junto a una zona corrupta se guarda el último sitio seguro")

	print("Nueva partida con una guardada:")
	_maisha().global_position = antes
	await _esperar(0.2)
	while get_tree().get_first_node_in_group("dialogo").hablando:
		await _pulsar("accion")
		await _esperar(0.1)
	await _pulsar("menu")
	pausa = get_tree().get_first_node_in_group("pausa")
	pausa._al_elegir(pausa._acciones.find("inicio"))
	await _esperar_cambio("Inicio")
	_inicio()._al_elegir(_opcion("nueva"))
	_comprobar(_inicio()._pregunta.visible, "pregunta antes de borrar la partida")
	_inicio()._al_responder(0)
	_comprobar(Estado.hay_partida() and _inicio()._lista.activa, "con «No» no se borra nada")
	_inicio()._al_elegir(_opcion("nueva"))
	_inicio()._al_responder(1)
	_comprobar(Estado.marcas.is_empty() and Estado.cuantos("seta_luminosa") == 0, "con «Sí» se empieza de cero")
	for i in 1500:
		if _escena() == "Kitovu" and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(0.3)
	_comprobar(get_tree().get_nodes_in_group("zanahorias").size() == 8, "las 8 zanahorias vuelven a estar en el huerto")

	print("Archivo estropeado:")
	var archivo := FileAccess.open(Estado.ruta_partida, FileAccess.WRITE)
	archivo.store_string("esto no es una partida")
	archivo.close()
	_comprobar(not Estado.hay_partida() and not Estado.cargar(), "un archivo estropeado no rompe nada: no se ofrece continuar")

	Estado.borrar_partida()
	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	await Sonido.callar()
	get_tree().quit(_fallos)
