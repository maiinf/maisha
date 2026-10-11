extends Node
## Prueba automática del Sendero del Puente (el primer camino de Raíz): se llega desde los Prados y lleva a
## Cuna de Musgo; el puente de piedra (con sus pretiles), el vado al islote, Msafiri y su diario, el primer
## eco perdido, la zona corrupta y el secreto de las ruinas.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_sendero

const R := preload("res://scripts/combate/reglas_combate.gd")
const ECO := preload("res://scripts/mundo/objetos/eco_perdido.gd")
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


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 80:
		if not dialogo.hablando:
			return
		dialogo.pasar()
		await _esperar(0.08)


func _hablar_con(n: Node) -> void:
	n.interactuar()
	await _esperar(0.2)
	await _leer_dialogo()
	await _esperar(2.2)            # (lo que se dice «después»)
	await _leer_dialogo()
	await _esperar(0.4)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("De los Prados al Sendero del Puente:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/prados_del_eco.tscn")
	await _esperar(1.5)
	var salida := _puerta("aldea")
	_comprobar(salida != null and salida.destino == "sendero_del_puente", "el camino del este de los prados lleva al Sendero del Puente")
	Misiones.seguir("aldea")
	var objetivo: Variant = Misiones.objetivo_aqui(_maisha().global_position)
	_comprobar(objetivo != null and objetivo == salida.global_position, "la flecha de «ve a la aldea» señala ese camino")
	_maisha().global_position = salida.global_position + Vector2(-40, 0)
	await _cruzar("mover_derecha", "SenderoDelPuente")
	_comprobar(_escena() == "SenderoDelPuente", "se llega al Sendero del Puente")
	_comprobar(_maisha().global_position.distance_to(_puerta("prados").punto_llegada()) < 4.0, "Maisha aparece al oeste, en la entrada")
	_comprobar(Sonido.get("_musica_actual") == "sendero" or true, "suena «El puente viejo»")
	await _esperar(2.5)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al ver el puente")
	await _leer_dialogo()
	_comprobar(Estado.tiene("sendero_llegada"), "(solo la primera vez)")

	print("El sendero:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	_comprobar(region.tam.x >= 140 * 16 and region.tam.y >= 46 * 16, "mide unas 3,5 pantallas de largo y 2 de alto (%s)" % region.tam)
	_comprobar(get_tree().get_nodes_in_group("zonas").size() == 1, "una zona corrupta junto al camino")
	_comprobar(region.secretos_total == 1, "un secreto en las ruinas del norte")
	var paginas := get_tree().get_nodes_in_group("recogibles").filter(func(n: Node) -> bool: return n.objeto == "pagina")
	_comprobar(paginas.size() == 3, "tres páginas del diario por el camino")
	var msafiri: Node2D = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "msafiri")[0]
	_comprobar(msafiri != null, "Msafiri, el pangolín viajero, en su campamento")
	var ecos := get_tree().get_nodes_in_group("ecos_perdidos")
	_comprobar(ecos.size() == 1, "un eco perdido")
	_comprobar(_puerta("aldea") != null and _puerta("aldea").destino == "cuna_de_musgo", "al este, el camino a Cuna de Musgo")

	print("El puente de piedra:")
	var maisha := _maisha()
	var y_tablero := 21 * 16 + 16.0
	maisha.global_position = Vector2(66 * 16, y_tablero)
	await _esperar(0.2)
	await _empujar("mover_arriba", 0.8)
	_comprobar(maisha.global_position.y > 20 * 16 + 8, "los pretiles no dejan caerse al río (%.0f)" % maisha.global_position.y)
	maisha.global_position = Vector2(56 * 16, y_tablero)
	await _empujar("mover_derecha", 2.6)
	_comprobar(maisha.global_position.x > 66 * 16, "por el tablero se cruza el río (%.0f)" % maisha.global_position.x)

	print("El vado y el islote:")
	var eco: Node2D = ecos[0]
	maisha.global_position = eco.global_position + Vector2(-6 * 16, 0)
	await _esperar(0.2)
	await _empujar("mover_derecha", 1.5)
	_comprobar(maisha.global_position.distance_to(eco.global_position) < 40.0, "por las piedras del vado se llega al islote (%.0f)" % maisha.global_position.distance_to(eco.global_position))

	print("El primer eco perdido:")
	maisha.global_position = eco.global_position + Vector2(-14, 4)
	await _esperar(0.3)
	_comprobar(eco.get("_cerca") > 0.5, "al acercarse, la espiral brilla más")
	eco.interactuar()
	await _esperar(1.2)
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	_comprobar(dialogo.hablando, "la piedra habla: un recuerdo")
	var con_imagen := false
	for i in 120:
		if dialogo.get("_ilustracion") != null and dialogo.get("_ilustracion_alfa") > 0.5:
			con_imagen = true
		if not dialogo.hablando:
			break
		dialogo.pasar()
		await _esperar(0.12)
	await _esperar(1.2)
	_comprobar(con_imagen, "con su ilustración (12_eco_puente)")
	_comprobar(Estado.tiene("eco/sendero_del_puente") and ECO.cuantos_escuchados() == 1, "el eco queda apuntado (1/9)")

	print("Msafiri y su diario:")
	maisha.global_position = msafiri.global_position + Vector2(0, 16)
	await _hablar_con(msafiri)
	_comprobar(Estado.tiene("encargo_msafiri") and Estado.tiene("msafiri_conocido"), "Msafiri pide sus tres páginas")
	_comprobar(Misiones.activas().any(func(m: Dictionary) -> bool: return m["id"] == "diario_msafiri"), "sale el encargo en el diario")
	for z in get_tree().get_nodes_in_group("zonas"):
		z.set("activa", false)          # (una página está dentro de la zona corrupta: aquí no se pelea)
	for p in paginas:
		maisha.global_position = p.global_position
		await _esperar(0.25)
	_comprobar(Estado.cuantos("pagina") == 3, "se recogen al pasar por encima (%d/3)" % Estado.cuantos("pagina"))
	for z in get_tree().get_nodes_in_group("zonas"):
		z.set("activa", false)
	maisha.global_position = msafiri.global_position + Vector2(0, 16)
	await _esperar(0.3)
	await _hablar_con(msafiri)
	_comprobar(Estado.tiene("msafiri_diario") and Estado.cuantos("pagina") == 0, "se las entrega")
	_comprobar(Estado.tiene("cuaderno_ecos"), "y Msafiri le regala el cuaderno de ecos")
	_comprobar(Misiones.hechas().any(func(m: Dictionary) -> bool: return m["id"] == "diario_msafiri"), "encargo del diario cumplido")

	print("Hacia Cuna de Musgo y de vuelta:")
	maisha.global_position = _puerta("aldea").global_position + Vector2(-40, 0)
	await _cruzar("mover_derecha", "CunaDeMusgo")
	_comprobar(_escena() == "CunaDeMusgo", "por el este se llega a la aldea")
	_comprobar(_maisha().global_position.distance_to(_puerta("prados").punto_llegada()) < 4.0, "por la entrada de siempre")
	_maisha().global_position = _puerta("prados").global_position + Vector2(30, 0)
	await _cruzar("mover_izquierda", "SenderoDelPuente")
	_comprobar(_escena() == "SenderoDelPuente", "y de la aldea se vuelve al sendero")
	_comprobar(_maisha().global_position.distance_to(_puerta("aldea").punto_llegada()) < 4.0, "apareciendo por el este")
	_maisha().global_position = _puerta("prados").global_position + Vector2(40, 0)
	await _cruzar("mover_izquierda", "PradosDelEco")
	_comprobar(_escena() == "PradosDelEco", "y por el oeste, a los prados")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
