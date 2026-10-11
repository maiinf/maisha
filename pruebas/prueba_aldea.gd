extends Node
## Prueba automática de Cuna de Musgo y de los cambios de escena.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_aldea

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
	for i in 300:
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


func _ready() -> void:
	Engine.time_scale = 3.0
	Estado.olvidar_todo()
	Estado.marcar("cetro_recibido")       # en los prados, Maisha ya trae el cetro del Kitovu
	get_tree().change_scene_to_file("res://escenas/mundo/prados_del_eco.tscn")
	await _esperar_cambio("PradosDelEco")

	print("Prados del Eco:")
	_comprobar(get_tree().get_nodes_in_group("estatuas").size() == 2, "hay 2 estatuas (Pino y Corteza)")
	_comprobar(_puerta("aldea") != null, "hay una salida hacia la aldea")

	print("Del puente a la aldea:")
	var salida := _puerta("aldea")
	_maisha().global_position = salida.global_position + Vector2(-40, 0)
	await _por_el_sendero("mover_derecha", "CunaDeMusgo")
	_comprobar(_escena() == "CunaDeMusgo", "al cruzar el borde se llega a Cuna de Musgo")
	var llegada := _puerta("prados")
	_comprobar(llegada != null and _maisha().global_position.distance_to(llegada.punto_llegada()) < 4.0, "Maisha aparece en la entrada de la aldea")

	print("En la aldea:")
	var aldeanos := get_tree().get_nodes_in_group("aldeanos").map(func(a: Node) -> String: return a.id)
	_comprobar(aldeanos == ["bibi"], "solo está Bibi; Pino y Corteza siguen de piedra (%s)" % [aldeanos])
	_comprobar(get_tree().get_nodes_in_group("edificios").size() == 4, "4 edificios en ruinas")
	var maisha := _maisha()
	maisha.global_position = Vector2(200, 300)     # cualquier sitio: no hay combate
	Input.action_press("explosivo")
	await get_tree().process_frame
	await get_tree().process_frame
	Input.action_release("explosivo")
	_comprobar(get_tree().get_nodes_in_group("semillas").is_empty() and maisha.aliento == R.ALIENTO_MAXIMO, "en la aldea no se lanzan semillas")

	print("Hablar con Bibi:")
	var bibi: Node2D = get_tree().get_nodes_in_group("aldeanos")[0]
	_comprobar(bibi.get_script().resource_path.ends_with("aldeano.gd") and preload("res://scripts/mundo/charla.gd").tiene_novedad("bibi"), "Bibi tiene algo que contar (!)")
	maisha.global_position = bibi.global_position + Vector2(0, 16)
	await _esperar(0.1)
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	await _pulsar_accion()
	_comprobar(dialogo.hablando, "al pulsar Acción junto a Bibi se abre el diálogo")
	_comprobar(not maisha.puede_actuar, "mientras habla, Maisha no se mueve")
	var lineas := await _leer_dialogo()
	_comprobar(Estado.tiene("bibi_conocida"), "tras la presentación queda la marca bibi_conocida (%d pulsaciones)" % lineas)
	_comprobar(maisha.puede_actuar, "al terminar, Maisha vuelve a moverse")

	print("Entrar en el Gran Árbol:")
	var puerta_arbol := _puerta("arbol")
	maisha.global_position = puerta_arbol.punto_llegada()
	await _cruzar("mover_arriba", "ClaroDeCalma")
	_comprobar(_escena() == "ClaroDeCalma", "por la puerta del tronco se entra al Claro de Calma")
	maisha = _maisha()
	_comprobar(maisha.global_position.distance_to(_puerta("salida").punto_llegada()) < 4.0, "Maisha aparece junto a la salida")
	maisha.global_position = Vector2(140, 170)
	await _empujar("mover_arriba", 2.5)
	var y := maisha.global_position.y
	_comprobar(y > 54.0 and y < 75.0, "Maisha camina hasta la pared del fondo y no la atraviesa (y = %d)" % y)
	maisha.global_position = Vector2(176, 142)
	await _esperar(0.1)
	await _pulsar_accion()
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "se puede mirar el brote del Árbol de la Vida")
	await _leer_dialogo()
	maisha.global_position = _puerta("salida").punto_llegada()
	await _cruzar("mover_abajo", "CunaDeMusgo")
	_comprobar(_escena() == "CunaDeMusgo", "al salir se vuelve a la aldea")
	_comprobar(_maisha().global_position.distance_to(_puerta("arbol").punto_llegada()) < 4.0, "y Maisha aparece delante de la puerta del árbol")

	print("Rescatar a Pino:")
	maisha = _maisha()
	maisha.global_position = _puerta("prados").global_position + Vector2(30, 0)
	await _por_el_sendero("mover_izquierda", "PradosDelEco")
	_comprobar(_escena() == "PradosDelEco", "de vuelta a los prados")
	_comprobar(_maisha().global_position.distance_to(_puerta("aldea").punto_llegada()) < 4.0, "Maisha aparece junto al puente")
	var zona_pino: Node2D = null
	for z in get_tree().get_nodes_in_group("zonas"):
		if z.get_meta("clave") == "2":
			zona_pino = z
	var estatua_pino: Node2D = get_tree().get_nodes_in_group("estatuas").filter(func(e: Node) -> bool: return e.id == "pino")[0]
	await _purgar(zona_pino)
	await _esperar(3.5)
	_comprobar(estatua_pino.despierto, "al purgar la zona, la estatua de Pino empieza a romperse")
	for i in 40:
		if get_tree().get_first_node_in_group("dialogo").hablando:
			break
		await _esperar(0.2)
	_comprobar(zona_pino.estado == zona_pino.Estado.PURGADA, "zona de Pino purgada")
	_comprobar(Estado.zona_purgada("prados_del_eco", "2"), "Estado recuerda la zona purgada")
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "la estatua se rompe y Pino da las gracias")
	await _leer_dialogo()
	_comprobar(Estado.rescatado("pino"), "Pino queda rescatado")

	print("Pino en la aldea, y los prados recuerdan lo hecho:")
	maisha = _maisha()
	maisha.global_position = _puerta("aldea").global_position + Vector2(-40, 0)
	await _por_el_sendero("mover_derecha", "CunaDeMusgo")
	aldeanos = get_tree().get_nodes_in_group("aldeanos").map(func(a: Node) -> String: return a.id)
	_comprobar("pino" in aldeanos and not "corteza" in aldeanos, "Pino está en la aldea, Corteza aún no (%s)" % [aldeanos])
	_comprobar(preload("res://scripts/mundo/charla.gd").tiene_novedad("pino"), "Pino tiene un encargo que contar (!)")
	maisha = _maisha()
	maisha.global_position = _puerta("prados").global_position + Vector2(30, 0)
	await _por_el_sendero("mover_izquierda", "PradosDelEco")
	var estados := {}
	for z in get_tree().get_nodes_in_group("zonas"):
		estados[z.get_meta("clave")] = z.estado
	_comprobar(estados["2"] == 4 and estados["1"] == 0, "la zona 2 sigue purgada y la 1 no (%s)" % [estados])
	var estatuas := get_tree().get_nodes_in_group("estatuas").map(func(e: Node) -> String: return e.id)
	_comprobar(estatuas == ["corteza"], "solo queda la estatua de Corteza (%s)" % [estatuas])

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	await Sonido.callar()
	get_tree().quit(_fallos)


## Desde la entrada de los prados hasta la aldea: se cruza el Sendero del Puente (dos cambios de escena)
func _por_el_sendero(accion: String, nombre: String) -> void:
	var sendero_puerta := "aldea" if accion == "mover_derecha" else "prados"
	await _cruzar(accion, "SenderoDelPuente")
	var p := _puerta(sendero_puerta)
	_maisha().global_position = p.global_position + (Vector2(-40, 0) if accion == "mover_derecha" else Vector2(40, 0))
	await _esperar(0.2)
	await _cruzar(accion, nombre)
