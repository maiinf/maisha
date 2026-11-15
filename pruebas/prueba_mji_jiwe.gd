extends Node
## Prueba automática de Mji-Jiwe, la Ciudad del Cráter (Asterhaul): se llega por la Puerta del Cráter del
## Desfiladero, suena su música, Maisha piensa al llegar, los muros entre terrazas, Mhunzi (el Arte de la Tierra y el
## mapa), los artesanos en gris y las Esquirlas (cualquiera vale), los Yunques de Memoria, los hornos-diapasón (los
## de la terraza media abren el Mercado de Chuma; todos, los Cristales de Mwamba), las misiones y la vuelta.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_mji_jiwe

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


func _vecino(id: String) -> Node2D:
	for n in get_tree().get_nodes_in_group("interactuables"):
		if n.get("id") == id:
			return n
	return null


func _artesano(nombre: String) -> Node2D:
	for n in get_tree().get_nodes_in_group("escribas"):
		if n.nombre == nombre:
			return n
	return null


func _yunques_despiertos() -> int:
	var n := 0
	for y in get_tree().get_nodes_in_group("yunques_memoria"):
		if (y.get_child(0) as Sprite2D).frame == 1:
			n += 1
	return n


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "desfiladero_llegada", "carga_sismica", "mwamba_pulso", "mwamba_hablado",
			"mauti_desfiladero_libre", "desfiladero/muro_puerta", "puerta_crater_abierta"]:
		Estado.marcar(marca)
	Estado.dar("esquirla_estrella")
	Estado.jugando = true

	print("Llegar a Mji-Jiwe:")
	await _ir("desfiladero_meteorito", "oeste", "DesfiladeroMeteorito")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var paso: Node2D = null
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == "crater":
			paso = p
	_comprobar(paso != null and paso.destino == "mji_jiwe", "la Puerta del Cráter lleva a la ciudad")
	m.global_position = paso.global_position + Vector2(0, 26)
	Input.action_press("mover_arriba")
	for i in 200:
		if _escena() == "MjiJiwe":
			break
		await get_tree().process_frame
	Input.action_release("mover_arriba")
	await _esperar(1.0)
	_comprobar(_escena() == "MjiJiwe", "andando por ella se llega a Mji-Jiwe (%s)" % _escena())
	_comprobar(Sonido.musica_actual == "mji_jiwe", "suena «La ciudad dentro del cráter» (%s)" % Sonido.musica_actual)
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.x < 80.0, "Maisha aparece en la entrada del suroeste (%s)" % m.global_position)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("mji_jiwe_llegada"), "piensa al llegar")
	m.global_position = _sitio(37, 19)
	Input.action_press("mover_arriba")
	await _esperar(1.0)
	Input.action_release("mover_arriba")
	_comprobar(m.global_position.y > 17.0 * 16.0, "el muro entre terrazas no se atraviesa (%.0f)" % m.global_position.y)
	m.global_position = _sitio(26, 20)
	Input.action_press("mover_abajo")
	Input.action_press("mover_derecha")
	await _esperar(1.2)
	Input.action_release("mover_abajo")
	Input.action_release("mover_derecha")
	_comprobar(m.global_position.y > _sitio(26, 22).y, "por los pasos de las diagonales sí se baja (%s)" % m.global_position)

	print("Mhunzi:")
	_comprobar(get_tree().get_nodes_in_group("yunques_memoria").size() == 12 and _yunques_despiertos() == 1, "doce Yunques de Memoria; el de Mwamba ya canta (%d)" % _yunques_despiertos())
	await _hablar(m, _vecino("mhunzi"))
	_comprobar(Estado.tiene("arte_tierra") and Estado.tiene("mapa_asterhaul"), "despierta el Arte de la Tierra y da el mapa de Asterhaul")
	_comprobar(Misiones.estado(Misiones.buscar("yunques_memoria")) == "activa", "empieza el encargo de los doce yunques")
	_comprobar(_vecino("mauti") != null and _vecino("mwamba") != null and _vecino("chuma") != null, "Mauti, Mwamba y Chuma están en la ciudad")

	print("Los artesanos en gris:")
	_comprobar(get_tree().get_nodes_in_group("escribas").size() == 8, "hay ocho artesanos en la ciudad")
	var jabali := _artesano("jabali")
	_comprobar(jabali.id == "artesano_a_gris", "Jabali está en gris")
	await _hablar(m, jabali)
	_comprobar(Estado.tiene("jabali_pulso") and Estado.cuantos("esquirla_estrella") == 0, "con una Esquirla recupera el pulso")
	await _esperar(1.2)
	await _leer_dialogo()
	_comprobar(jabali.id == "artesano_a" and Estado.tiene("jabali_hablado"), "le vuelve el color y habla")
	_comprobar(_yunques_despiertos() == 2, "y canta otro yunque (%d)" % _yunques_despiertos())
	var kokoto := _artesano("kokoto")
	await _hablar(m, kokoto)
	_comprobar(not Estado.tiene("kokoto_pulso"), "sin Esquirla, Kokoto sigue en gris")
	m.global_position = _cerca("recogibles", 58, 48).global_position
	await _esperar(0.5)
	_comprobar(Estado.cuantos("esquirla_estrella") == 1 and Estado.tiene("esquirla/mji_jiwe_sur"), "hay una Esquirla escondida al sur")
	await _hablar(m, kokoto)
	await _esperar(1.2)
	await _leer_dialogo()
	_comprobar(Estado.tiene("kokoto_pulso") and _yunques_despiertos() == 3, "cualquier Esquirla vale: Kokoto despierta (%d yunques)" % _yunques_despiertos())

	print("Los hornos-diapasón:")
	var hornos := get_tree().get_nodes_in_group("hornos_diapason")
	_comprobar(hornos.size() == 6, "hay seis hornos de calle")
	await _hablar(m, _vecino("chuma"))
	_comprobar(not Estado.tiene("mercado_escoria"), "el Mercado está cerrado")
	for i in 3:
		await _cargar(m, hornos[i], Vector2(0, 20))
	_comprobar(hornos[0].encendido and not Estado.tiene("mercado_escoria"), "con tres de la terraza media, aún no")
	await _cargar(m, hornos[3], Vector2(0, 20))
	await _esperar(0.3)
	_comprobar(Estado.tiene("mercado_escoria"), "con los cuatro, Chuma abre el Mercado de la Escoria")
	_comprobar(Misiones.estado(Misiones.buscar("mji_jiwe")) == "hecha", "misión «La Ciudad del Cráter» cumplida")
	await _hablar(m, _vecino("mwamba"))
	_comprobar(not Estado.tiene("mwamba_cristales"), "Mwamba pide los seis")
	for i in [4, 5]:
		await _cargar(m, hornos[i], Vector2(0, 20))
	_comprobar(Estado.tiene("hornos_mji_jiwe"), "los seis hornos arden")
	var cristales := Tienda.cristales()
	await _hablar(m, _vecino("mwamba"))
	_comprobar(Estado.tiene("mwamba_cristales") and Tienda.cristales() == cristales + 3, "Mwamba da 3 Cristales (%d → %d)" % [cristales, Tienda.cristales()])

	print("Volver:")
	await _ir("mji_jiwe", "desfiladero", "MjiJiwe")
	_comprobar(_artesano("jabali").id == "artesano_a" and _yunques_despiertos() == 3, "al volver, los artesanos y los yunques siguen despiertos")
	_comprobar(get_tree().get_nodes_in_group("hornos_diapason").all(func(h: Node) -> bool: return h.encendido), "y los hornos, encendidos")
	await _ir("desfiladero_meteorito", "crater", "DesfiladeroMeteorito")
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.distance_to(_sitio(73, 8)) < 48.0, "de vuelta al Desfiladero se sale por la Puerta del Cráter (%s)" % m.global_position)

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
