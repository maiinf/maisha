extends Node
## Prueba automática del Paso de Piedra (parte 1): del Campo Segado al Paso, la casa abandonada de Nungu por fuera y por
## dentro (las pistas, el armario cerrado con la cerradura de Corteza), la misión «La casa del Paso de Piedra», la
## maraña que tapa el paso a la Gruta (se aparta al despertar el Guardián) y su túnel por el lado de la Gruta.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_paso_piedra

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


func _usar(n: Node) -> void:
	n.interactuar()
	await _esperar(0.2)
	await _leer_dialogo()
	await _esperar(0.3)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco",
			"visto/cuna_de_musgo", "bibi_conocida", "bibi_aldea_viva", "camino_campo", "visto/campo_segado", "campo_llegada",
			"rescatado_corteza", "encargo_corteza", "construido_taller"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("Del Campo Segado al Paso de Piedra:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/campo_segado.tscn")
	await _esperar(1.5)
	await _leer_dialogo()
	var este := _puerta("paso")
	_comprobar(este != null and este.destino == "paso_piedra", "el Campo Segado tiene una salida al este, al Paso de Piedra")
	_maisha().global_position = este.global_position + Vector2(-30, 0)
	await _cruzar("mover_derecha", "PasoPiedra")
	_comprobar(_escena() == "PasoPiedra", "se llega al Paso de Piedra")
	_comprobar(_maisha().global_position.distance_to(_puerta("campo").punto_llegada()) < 4.0, "Maisha aparece al oeste, viniendo del campo")
	await _esperar(2.5)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al llegar (la casa con la cúpula)")
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(Estado.tiene("paso_llegada") and Misiones.estado(Misiones.buscar("casa_nungu")) == "activa", "sale la misión «La casa del Paso de Piedra»")
	_comprobar(Sonido.musica_actual == "paso", "suena su música: «La casa del observatorio» (%s)" % Sonido.musica_actual)
	var region: Node2D = get_tree().get_first_node_in_group("region")
	_comprobar(region.tam.x >= 140 * 16, "va de oeste a este: unas 4 pantallas de largo")
	var zonas := get_tree().get_nodes_in_group("zonas")
	_comprobar(zonas.size() == 1 and zonas[0].tipos_enemigo.has("bundi") and zonas[0].tipos_enemigo.has("buibui"), "una zona corrupta con búhos-mago y arañas-bruja")
	_comprobar(region.secretos_total == 1, "un secreto en la cantera")
	for z in zonas:
		z.set("activa", false)

	print("La maraña de la Gruta:")
	var gruta := _puerta("gruta")
	_comprobar(gruta != null and gruta.destino == "gruta_raices" and gruta.cerrada_hasta == "gruta_guardian", "al este, el paso a la Gruta, cerrado hasta despertar al Guardián")
	_maisha().global_position = gruta.global_position + Vector2(-60, 0)
	await _esperar(0.2)
	_maisha().global_position = gruta.global_position + Vector2(-12, 0)
	await _esperar(0.5)
	_comprobar(_escena() == "PasoPiedra", "la maraña no deja pasar")
	await _leer_dialogo()

	print("La casa de Nungu:")
	var casa := _puerta("casa")
	_comprobar(casa != null and casa.destino == "casa_nungu", "la casa abandonada tiene puerta")
	_maisha().global_position = casa.global_position + Vector2(0, 30)
	await _cruzar("mover_arriba", "CasaNungu")
	_comprobar(_escena() == "CasaNungu", "se entra en la casa")
	await _esperar(1.2)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al entrar")
	await _leer_dialogo()
	var armario: Node2D = get_tree().get_first_node_in_group("armario")
	_comprobar(armario != null and armario._sprite.frame == 0, "al fondo, el armario, cerrado")
	_maisha().global_position = armario.global_position + Vector2(0, 24)
	await _usar(armario)
	_comprobar(Estado.tiene("nungu_cerradura") and not Estado.tiene("armario_abierto"), "sin llave no se abre (y lleva la marca de Corteza)")
	var mesa: Node2D = null
	for n in get_tree().get_nodes_in_group("interactuables"):
		if n.get("charla") == "nungu_mesa":
			mesa = n
	_comprobar(mesa != null, "en la mesa hay papeles")
	_maisha().global_position = mesa.global_position + Vector2(0, 14)
	await _usar(mesa)
	_comprobar(Estado.tiene("nungu_nota"), "una carta de Nungu: le dejó la llave de repuesto a Corteza")
	_comprobar(Misiones.paso_actual(Misiones.buscar("casa_nungu")).get("texto", "") == "Pregunta a Corteza por la llave del armario", "la misión dice que se pregunte a Corteza")

	print("La llave, en el taller de Corteza:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/interiores/taller_corteza.tscn")
	await _esperar(1.2)
	var corteza: Node2D = null
	for n in get_tree().get_nodes_in_group("aldeanos"):
		if n.id == "corteza":
			corteza = n
	_comprobar(corteza != null, "Corteza está en su taller")
	_maisha().global_position = corteza.global_position + Vector2(-16, 6)
	corteza.interactuar()
	await _esperar(0.2)
	await _leer_dialogo()
	await _esperar(2.4)
	await _leer_dialogo()
	_comprobar(Estado.tiene("corteza_busca_llave") and not Estado.tiene("llave_nungu"), "Corteza se acuerda de Nungu... pero no de dónde guardó la llave")
	var sitios := {}
	for n in get_tree().get_nodes_in_group("interactuables"):
		if str(n.get("charla")).begins_with("taller_"):
			sitios[str(n.get("charla"))] = n
	for c in ["taller_herramientas", "taller_banco"]:
		_maisha().global_position = sitios[c].global_position + Vector2(0, 12)
		await _usar(sitios[c])
	_comprobar(not Estado.tiene("llave_nungu"), "ni con las herramientas ni en el banco (allí solo hay polvo de carbón)")
	_maisha().global_position = sitios["taller_barril"].global_position + Vector2(0, -12)
	await _usar(sitios["taller_barril"])
	_comprobar(Estado.tiene("llave_nungu"), "¡en el barril del carbón! La llave, negra de hollín")
	var mochila := get_tree().get_first_node_in_group("mochila")
	mochila.abrir(1)
	await _esperar(0.3)
	_comprobar(mochila._lista().any(func(f: Dictionary) -> bool: return f["nombre"] == "Llave del armario"), "la llave sale en la mochila, con los objetos clave")
	mochila.cerrar()
	await _esperar(1.0)
	_maisha().global_position = corteza.global_position + Vector2(-16, 6)
	await _esperar(0.3)
	corteza.interactuar()
	await _esperar(0.3)
	await _leer_dialogo()
	await _esperar(0.4)
	_comprobar(Estado.tiene("corteza_llave_hablado"), "y Corteza avisa: Nungu hablaba de cosas que crecen bajo tierra")
	get_tree().change_scene_to_file("res://escenas/interiores/casa_nungu.tscn")
	await _esperar(1.2)
	armario = get_tree().get_first_node_in_group("armario")
	_maisha().global_position = armario.global_position + Vector2(0, 24)
	await _usar(armario)
	_comprobar(Estado.tiene("armario_abierto") and armario._sprite.frame == 1, "con la llave, el armario se abre: dentro, una escalera")
	_comprobar(Misiones.estado(Misiones.buscar("casa_nungu")) == "hecha", "y la misión se cumple")

	print("La cueva de las setas:")
	_maisha().global_position = Vector2(160, 104)
	await _esperar(0.3)
	await _cruzar("mover_arriba", "CuevaSetas")
	_comprobar(_escena() == "CuevaSetas", "por la escalera del armario se baja a la cueva de las setas")
	await _esperar(1.6)
	await _leer_dialogo()
	_comprobar(Estado.tiene("cueva_llegada") and Misiones.estado(Misiones.buscar("bajo_la_casa")) == "activa", "sale la misión «Bajo la casa»")
	_comprobar(get_tree().get_nodes_in_group("esporas").size() == 3, "hay nubes de esporas")
	var nube: Node2D = get_tree().get_nodes_in_group("esporas")[0]
	for i in 120:
		if nube.activa():
			break
		await _esperar(0.05)
	_maisha().global_position = nube.global_position + Vector2(0, 6)
	await _esperar(0.2)
	await _leer_dialogo()
	_comprobar(float(_maisha().mareo) > 0.0, "respirarlas marea: los controles van al revés")
	nube.disipar()
	await _esperar(0.7)
	_comprobar(not nube.activa(), "el Latido las deshace un rato")
	_maisha().mareo = 0.0
	for p in get_tree().get_nodes_in_group("paginas"):
		_maisha().global_position = p.global_position + Vector2(0, 10)
		await _usar(p)
	_comprobar(Estado.tiene("nungu_pagina/1") and Estado.tiene("nungu_pagina/2") and Estado.tiene("nungu_pagina/3"), "las tres páginas del diario de Nungu")
	_comprobar(Misiones.paso_actual(Misiones.buscar("bajo_la_casa")).get("texto", "") == "Busca a Nungu al fondo de la cueva", "la misión pide buscar a Nungu al fondo")
	var eco: Node2D = get_tree().get_first_node_in_group("ecos_perdidos")
	_comprobar(eco != null, "en la cámara del este, el octavo eco")
	_maisha().global_position = eco.global_position + Vector2(0, 16)
	eco.interactuar()
	await _esperar(1.2)
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 30:
		if Estado.tiene("eco/cueva_setas") and not dialogo.hablando:
			break
		await _leer_dialogo()
		await _esperar(0.4)
	_comprobar(Estado.tiene("eco/cueva_setas"), "se oye el recuerdo de Kimya y las setas (8.º eco)")
	var cortina: Node2D = get_tree().get_first_node_in_group("cortina")
	_comprobar(cortina != null, "al sur, una cortina de micelio")
	_maisha().global_position = cortina.global_position + Vector2(0, -30)
	await _esperar(0.2)
	Input.action_press("mover_abajo")
	await _esperar(1.0)
	Input.action_release("mover_abajo")
	_comprobar(_maisha().global_position.y < cortina.global_position.y, "la cortina no deja pasar")
	_maisha().global_position = _puerta("escalera").global_position + Vector2(0, 30)
	await _cruzar("mover_arriba", "CasaNungu")
	_comprobar(_escena() == "CasaNungu", "por la escalera se vuelve a la casa")
	_maisha().global_position = Vector2(160, 176)
	await _cruzar("mover_abajo", "PasoPiedra")
	_comprobar(_escena() == "PasoPiedra" and _maisha().global_position.distance_to(_puerta("casa").punto_llegada()) < 4.0, "al salir, Maisha aparece delante de la casa")

	print("El paso a la Gruta, abierto:")
	Estado.marcar("gruta_guardian")
	_maisha().global_position = _puerta("gruta").global_position + Vector2(-30, 0)
	await _cruzar("mover_derecha", "GrutaRaices")
	_comprobar(_escena() == "GrutaRaices", "con el Guardián despierto, la maraña se aparta y se llega a la Gruta")
	_comprobar(get_tree().get_nodes_in_group("tapon_raices").is_empty(), "y por dentro, el túnel del oeste está libre")
	_maisha().global_position = _puerta("paso").global_position + Vector2(30, 0)
	await _cruzar("mover_izquierda", "PasoPiedra")
	_comprobar(_escena() == "PasoPiedra", "y por el túnel se vuelve al Paso de Piedra")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
