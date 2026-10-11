extends Node
## Prueba automática del diario de misiones, el objetivo en pantalla y las acciones rápidas de la mochila.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_misiones

var _fallos := 0
var _nuevas: Array = []
var _cumplidas: Array = []


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _marcar(marcas: Array) -> void:
	for m in marcas:
		Estado.marcar(m)
	await get_tree().process_frame
	await get_tree().process_frame


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Misiones.mision_nueva.connect(func(m: Dictionary) -> void: _nuevas.append(m["id"]))
	Misiones.mision_cumplida.connect(func(m: Dictionary) -> void: _cumplidas.append(m["id"]))
	Estado.olvidar_todo()
	await get_tree().process_frame

	print("El diario se lee de las marcas:")
	_comprobar(Misiones.activas().is_empty(), "al empezar no hay ninguna misión")
	await _marcar(["kitovu_despierta"])
	_comprobar(_nuevas == ["despertar"], "al despertar sale «Un despertar extraño» (%s)" % [_nuevas])
	_comprobar(Misiones.seguida().get("id", "") == "despertar", "y es la que se sigue en pantalla")
	_comprobar(Misiones.paso_actual(Misiones.seguida())["texto"] == "Sigue a la chispa de vida", "primer objetivo: seguir a la chispa")
	await _marcar(["recuerdo_1", "recuerdo_2", "recuerdo_3", "kuku_perdida", "kuku_cogida", "kuku_devuelta"])
	_comprobar("despertar" in _cumplidas and "granja" in _nuevas, "al devolver a Kuku se cumple y sale «La granja de Mzee Shamba»")
	await _marcar(["shamba_conocido", "cena_shamba", "amanecer_granja", "tarea_cosecha"])
	Estado.dar("zanahoria", 3)
	await get_tree().process_frame
	var granja := Misiones.buscar("granja")
	_comprobar(Misiones.paso_actual(granja)["texto"] == "Arranca zanahorias del huerto (3/5)", "el contador de zanahorias: %s" % Misiones.paso_actual(granja)["texto"])
	Estado.dar("zanahoria", 2)
	await get_tree().process_frame
	_comprobar(Misiones.paso_actual(granja)["texto"] == "Lleva las zanahorias a Mzee Shamba", "con 5, toca llevárselas")
	Estado.quitar("zanahoria", 5)
	await _marcar(["hecha_cosecha", "tarea_pesca"])
	_comprobar(Misiones.paso_actual(granja)["texto"] == "Pesca un pez en el estanque", "al entregarlas no vuelve atrás: ahora toca pescar")
	_comprobar(Misiones.pasos_visibles(granja).size() == 6, "en el diario se ven los pasos hechos y el actual (%d)" % Misiones.pasos_visibles(granja).size())
	await _marcar(["hecha_pesca", "tarea_cerca", "tablas_cogidas", "cerca_arreglada", "hecha_cerca", "cetro_recibido", "mapa_partido"])
	_comprobar(Misiones.estado(granja) == "hecha" and Misiones.seguida().get("id", "") == "manchas", "con el cetro se cumple la granja y se sigue «Las manchas de Giza»")
	await _marcar(["zona/kitovu/1", "zona/kitovu/4"])
	_comprobar(Misiones.paso_actual(Misiones.buscar("manchas"))["texto"] == "Limpia las manchas de Giza (2/3)", "cuenta las manchas limpias")

	print("Encargos y cuál se sigue:")
	await _marcar(["zona/kitovu/6", "zona/kitovu/7", "portal_raiz", "visto/prados_del_eco", "zona/prados_del_eco/2", "rescatado_pino", "encargo_pino"])
	_comprobar(Misiones.seguida().get("id", "") == "prados", "la historia sigue en pantalla aunque salga un encargo")
	Misiones.seguir("casa_pino")
	_comprobar(Misiones.seguida().get("id", "") == "casa_pino", "se puede elegir seguir el encargo de Pino")
	Estado.guardar()
	var guardada := Estado.extra.duplicate()
	Estado.cargar()
	_comprobar(Misiones.seguida().get("id", "") == "casa_pino" and guardada.has("mision_seguida"), "lo que se sigue se guarda con la partida")
	_comprobar(Misiones.siguiente_escena("casa_pino", "kitovu") == "cuna_de_musgo", "de casa de Pino al Kitovu se sale primero a la aldea")
	_comprobar(Misiones.siguiente_escena("cuna_de_musgo", "kitovu") == "sendero_del_puente", "y de la aldea, al Sendero del Puente (hacia los prados)")

	print("La flecha en el mundo:")
	Estado.jugando = true
	get_tree().change_scene_to_file("res://escenas/mundo/prados_del_eco.tscn")
	await _esperar(1.5)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var objetivo: Variant = Misiones.objetivo_aqui(maisha.global_position)
	var setas := get_tree().get_nodes_in_group("recogibles")
	_comprobar(objetivo != null and setas.any(func(n: Node2D) -> bool: return n.global_position == objetivo), "en los prados, la flecha señala una seta luminosa")
	Misiones.seguir("aldea")
	objetivo = Misiones.objetivo_aqui(maisha.global_position)
	var puerta_aldea := get_tree().get_nodes_in_group("puertas").filter(func(p: Node) -> bool: return p.destino == "sendero_del_puente")
	_comprobar(objetivo != null and objetivo == puerta_aldea[0].global_position, "para hablar con Bibi, señala el camino a la aldea")
	var capa := get_tree().get_first_node_in_group("objetivo")
	await _esperar(0.5)
	_comprobar(capa != null and capa._alfa > 0.9, "el objetivo se ve arriba a la derecha")

	print("Acciones rápidas de la mochila:")
	var mochila := get_tree().get_first_node_in_group("mochila")
	var tecla := InputEventKey.new()
	tecla.physical_keycode = KEY_4
	tecla.pressed = true
	Input.parse_input_event(tecla)
	await get_tree().process_frame
	await get_tree().process_frame
	_comprobar(mochila.abierta and mochila.pestana == 3, "la tecla 4 abre el mapa")
	await _esperar(0.1)
	_comprobar(capa._alfa < 0.95, "con la mochila abierta, el objetivo se esconde")
	mochila.cerrar()
	await get_tree().process_frame
	# la rueda: mantener Tab, inclinar a la derecha y soltar
	Input.action_press("mochila")
	await _esperar(0.45)
	_comprobar(mochila.rueda, "al mantener Tab sale la rueda rápida")
	Input.action_press("mover_derecha")
	await _esperar(0.1)
	Input.action_release("mover_derecha")
	Input.action_release("mochila")
	await get_tree().process_frame
	await get_tree().process_frame
	_comprobar(mochila.abierta and not mochila.rueda and mochila.pestana == 1, "inclinando a la derecha y soltando se abren los Objetos (%d)" % mochila.pestana)
	mochila.cerrar()
	Input.action_press("mochila")
	await _esperar(0.45)
	Input.action_release("mochila")
	await get_tree().process_frame
	await get_tree().process_frame
	_comprobar(not mochila.abierta and not get_tree().paused, "si se suelta sin elegir, la rueda se cierra")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
