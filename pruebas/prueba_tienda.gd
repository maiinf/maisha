extends Node
## Prueba automática de la tienda de Tawi y los Cristales del Nexo (y de la pantalla del final de Raíz):
## los cristales se ganan con misiones y marcas, la tienda se abre hablando con Tawi, se compra (prendas que se
## ponen solas, el mapa de los secretos, ingredientes, la semilla del olvido que devuelve la Esencia y sube de
## precio), lo que no se puede pagar, la ropa desde la mochila y que todo se guarda.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_tienda

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 60:
		if not dialogo.hablando:
			return
		dialogo.pasar()
		await _esperar(0.08)


func _pulsar(accion: String) -> void:
	var e := InputEventAction.new()
	e.action = accion
	e.pressed = true
	Input.parse_input_event(e)
	await get_tree().process_frame
	await get_tree().process_frame
	e = InputEventAction.new()
	e.action = accion
	e.pressed = false
	Input.parse_input_event(e)
	await get_tree().process_frame


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco",
			"rescatado_pino", "rescatado_corteza", "bibi_conocida", "bibi_meditar", "bibi_aldea_viva", "visto/cuna_de_musgo",
			"camino_bosque", "camino_cienaga", "visto/bosque_cobrizo", "rescatado_tawi", "encargo_tawi", "construido_puesto",
			"mapa_raiz", "construido_cocina", "rescatado_juncia"]:
		Estado.marcar(m)
	Estado.jugando = true

	await _esperar(0.3)
	print("Los Cristales del Nexo:")
	var antes := Tienda.cristales()
	var ganados: Array = []
	Tienda.cristales_ganados.connect(func(n: int, _m: String) -> void: ganados.append(n))
	Estado.marcar("zona/bosque_cobrizo/4")         # Pembe: 3 por el guardián y la misión del bosque (historia, 3)
	await _esperar(0.5)
	_comprobar(Tienda.cristales() == antes + 6, "liberar a Pembe da cristales: el guardián y la misión (%d → %d)" % [antes, Tienda.cristales()])
	_comprobar(ganados.size() >= 2, "y salen avisos «+N Cristales»")
	Estado.marcar("secreto/prados_del_eco/3,4")
	_comprobar(Tienda.cristales() == antes + 7, "un secreto, 1 más")
	for m in ["zona/cienaga_quieta/4", "zona/campo_segado/3"]:
		Estado.marcar(m)
	var total := Tienda.cristales()
	_comprobar(total >= 20, "hay cristales para gastar (%d)" % total)

	print("La tienda de Tawi:")
	Estado.llegada = "prados"
	get_tree().change_scene_to_file("res://escenas/mundo/cuna_de_musgo.tscn")
	await _esperar(1.5)
	var tawi: Node = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "tawi")[0]
	var maisha := get_tree().get_first_node_in_group("maisha")
	maisha.global_position = tawi.global_position + Vector2(0, 16)
	tawi.interactuar()
	await _esperar(0.2)
	await _leer_dialogo()
	await _esperar(0.4)
	var tienda := get_tree().get_first_node_in_group("tienda")
	_comprobar(tienda != null and tienda.abierto and get_tree().paused, "al hablar con Tawi se abre su tienda y el juego se para")
	var lista: Array = tienda._lista()
	var ids := lista.map(func(a: Dictionary) -> String: return String(a["id"]))
	_comprobar("corona_hojas" in ids and "mapa_secretos" in ids and "semilla_olvido" in ids and "ingredientes" in ids,
		"vende prendas, el mapa de los secretos, ingredientes y la semilla del olvido (%d cosas)" % ids.size())
	_comprobar(not "sombrero_paja" in ids, "el sombrero de paja no sale hasta haber visto el Campo Segado")
	# el mapa de los secretos
	tienda.seleccion = ids.find("mapa_secretos")
	await _pulsar("accion")
	_comprobar(Estado.tiene("mapa_secretos") and Tienda.cristales() == total - 5, "Acción compra: el mapa de los secretos por 5")
	await _pulsar("accion")
	_comprobar(Tienda.cristales() == total - 5, "lo que ya se tiene no se vende dos veces")
	# una prenda: se pone sola
	tienda.seleccion = ids.find("corona_hojas")
	_comprobar(tienda.comprar_elegido() == "ok" and maisha.get_node("Ropa").lleva("corona_hojas"), "la corona de hojas: comprada y puesta")
	# ingredientes (se pueden comprar varias veces)
	var bayas := Estado.cuantos("bayas")
	tienda.seleccion = ids.find("ingredientes")
	tienda.comprar_elegido()
	tienda.comprar_elegido()
	_comprobar(Estado.cuantos("bayas") == bayas + 4 and Estado.cuantos("junco") == 2, "los ingredientes de Juncia se pueden comprar más de una vez")
	# la semilla del olvido: devuelve la Esencia y sube de precio
	Estado.extra["artes"] = {"raiz": 2, "aliento": 1}
	var esencia := Artes.esencia()
	var art: Dictionary = Tienda.buscar("semilla_olvido")
	var precio := Tienda.precio(art)
	tienda.seleccion = ids.find("semilla_olvido")
	_comprobar(tienda.comprar_elegido() == "ok" and Artes.nivel("raiz") == 0 and Artes.esencia() == esencia + 4,
		"la semilla del olvido devuelve toda la Esencia gastada (+%d)" % (Artes.esencia() - esencia))
	_comprobar(Tienda.precio(art) == precio + 2, "y la siguiente cuesta 2 más")
	_comprobar(tienda.comprar_elegido() == "nada_que_olvidar", "sin niveles, no hay nada que olvidar")
	# sin cristales
	Estado.extra["cristales_gastados"] = Tienda.cristales_ganados_total()
	tienda.seleccion = ids.find("capa_musgo")
	_comprobar(tienda.comprar_elegido() == "caro" and not Tienda.tiene("capa_musgo"), "sin cristales, Tawi no vende (y lo dice)")
	await _pulsar("mochila")
	await _esperar(0.5)
	_comprobar(not is_instance_valid(tienda) or not tienda.abierto, "Tab cierra la tienda")
	_comprobar(not get_tree().paused, "y el juego sigue")

	print("La ropa, desde la mochila:")
	var mochila := get_tree().get_first_node_in_group("mochila")
	mochila.abrir(1)
	await _esperar(0.2)
	var filas: Array = mochila._lista()
	_comprobar(filas.any(func(f: Dictionary) -> bool: return f["nombre"] == "Cristales del Nexo"), "la mochila enseña los cristales")
	var i_corona := -1
	for i in filas.size():
		if filas[i].get("prenda", "") == "corona_hojas":
			i_corona = i
	_comprobar(i_corona >= 0, "y la corona comprada")
	mochila.seleccion = i_corona
	mochila._usar_elegido()
	_comprobar(not Tienda.lleva("corona_hojas") and not maisha.get_node("Ropa").lleva("corona_hojas"), "Acción se la quita")
	mochila._usar_elegido()
	_comprobar(Tienda.lleva("corona_hojas") and maisha.get_node("Ropa").lleva("corona_hojas"), "y otra vez se la pone")
	mochila.cerrar()
	await _esperar(0.3)
	Estado.guardar()
	Estado.cargar()
	_comprobar(Tienda.tiene("corona_hojas") and Tienda.lleva("corona_hojas") and Estado.tiene("mapa_secretos"), "lo comprado se guarda con la partida")
	Estado.llegada = "prados"
	get_tree().change_scene_to_file("res://escenas/mundo/cuna_de_musgo.tscn")
	await _esperar(1.2)
	_comprobar(get_tree().get_first_node_in_group("maisha").get_node("Ropa").lleva("corona_hojas"), "y al cambiar de escena, Maisha sigue con su corona")

	print("El final de Raíz:")
	var fin: CanvasLayer = load("res://scripts/interfaz/fin_mundo.gd").new()
	get_tree().current_scene.add_child(fin)
	fin.abrir()
	await _esperar(7.0)
	_comprobar(get_tree().paused and fin.lineas_vistas() == 7, "salen las 7 líneas de lo conseguido en Raíz")
	await _pulsar("accion")
	await _esperar(1.2)
	_comprobar(not is_instance_valid(fin) and not get_tree().paused, "Acción cierra el final y se sigue jugando")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
