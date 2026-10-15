extends Node
## Prueba automática de La Travesía (el viaje río arriba en el transbordador): se sube en el Embarcadero Junco, la barca
## sube sola con Maisha en la cubierta (sin poder salirse), atraca en el muelle de piedra de la Gruta, Maisha baja y
## puede volver al Embarcadero desde la barca.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_la_travesia

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
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "embarcadero_llegada",
			"eco/orilla_juncos", "casa_bata_abierta", "bata_conocido", "mamba_vencido", "zona/embarcadero_junco/1",
			"boquete_tapado", "transbordador_listo"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("Subir al transbordador en el Embarcadero:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/embarcadero_junco.tscn")
	await _esperar(1.5)
	await _leer_dialogo()
	var embarque: Node2D = null
	for n in get_tree().get_nodes_in_group("interactuables"):
		if n.get_script() and String(n.get_script().resource_path).ends_with("arreglo_transbordador.gd") == false and n.get_parent().name == "ArregloTransbordador":
			embarque = n
	_comprobar(embarque != null, "con el transbordador a flote, en la punta del muelle se puede subir")
	_maisha().global_position = embarque.global_position + Vector2(0, 10)
	await _esperar(0.3)
	embarque.interactuar()
	await _esperar(0.3)
	await _leer_dialogo()
	for i in 200:
		if _escena() == "LaTravesia" and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(0.5)
	_comprobar(_escena() == "LaTravesia", "Bata zarpa: se llega a La Travesía")

	print("El viaje:")
	var viaje: Node2D = get_tree().current_scene.get_node("Entidades/Viaje")
	var cubierta: Rect2 = viaje.PISABLE
	_comprobar(viaje != null and Rect2(viaje.position + cubierta.position, cubierta.size).grow(2).has_point(_maisha().global_position), "Maisha va en la cubierta")
	await _esperar(3.0)
	_comprobar(viaje.fase == viaje.Fase.NAVEGA and viaje.recorrido > 0.0, "la barca sube sola por el río")
	await _empujar("mover_izquierda", 2.0)
	var local: Vector2 = _maisha().global_position - viaje.position
	_comprobar(cubierta.grow(1).has_point(local), "por mucho que ande, Maisha no se sale de la cubierta")
	_comprobar(Sonido.musica_actual == "travesia", "suena su música: «Río arriba» (%s)" % Sonido.musica_actual)

	print("Lo que sale del agua:")
	viaje.recorrido = viaje._largo * 0.125
	await _esperar(1.5)
	var cangrejos := get_tree().get_nodes_in_group("enemigos").filter(func(e: Node) -> bool: return String(e.get_script().resource_path).ends_with("cangrejo.gd"))
	_comprobar(cangrejos.size() >= 2 and viaje._a_bordo.size() >= 2, "los cangrejos trepan por la borda a la cubierta (%d)" % cangrejos.size())
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.call("morir")
	await _esperar(0.5)

	print("La isla del séptimo eco:")
	viaje._oleada = 2
	viaje.recorrido = viaje._parada - 10.0
	for i in 40:
		await _esperar(0.2)
		await _leer_dialogo()
		if viaje.fase == viaje.Fase.PARADA:
			break
	_comprobar(viaje.fase == viaje.Fase.PARADA, "junto a la isla, la barca se para")
	await _esperar(1.5)
	await _leer_dialogo()
	# baja andando por la pasarela hasta la isla
	_maisha().global_position = viaje.position + Vector2(40, -5)
	await _esperar(0.2)
	await _empujar("mover_derecha", 1.6)
	_comprobar(_maisha().global_position.x > viaje.position.x + 100.0, "Bata tiende una pasarela y Maisha baja andando a la isla (%.0f)" % (_maisha().global_position.x - viaje.position.x))
	var eco: Node2D = get_tree().get_first_node_in_group("ecos_perdidos")
	_maisha().global_position = eco.global_position + Vector2(-14, 6)
	await _esperar(0.3)
	_comprobar(_maisha().global_position.distance_to(eco.global_position + Vector2(-14, 6)) < 3.0, "Maisha baja a la isla")
	var en_tierra := _maisha().global_position
	_maisha().global_position = Vector2(viaje.position.x, en_tierra.y + 120.0)
	await _esperar(0.2)
	_comprobar(_maisha().global_position.distance_to(en_tierra) < 3.0, "pero no puede meterse en el agua")
	eco.interactuar()
	await _esperar(1.2)
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	var con_imagen := false
	for i in 120:
		if dialogo.get("_ilustracion") != null and dialogo.get("_ilustracion_alfa") > 0.5:
			con_imagen = true
		if not dialogo.hablando:
			break
		dialogo.pasar()
		await _esperar(0.12)
	await _esperar(1.2)
	_comprobar(con_imagen and Estado.tiene("eco/la_travesia"), "el séptimo eco, con su ilustración (19_eco_travesia)")
	var hoja: Node2D = null
	for n in get_tree().get_nodes_in_group("interactuables"):
		for h in n.get_children():
			var t: Texture2D = (h as Sprite2D).texture if h is Sprite2D else null
			if t is CanvasTexture:
				t = (t as CanvasTexture).diffuse_texture   # (con relieve: scripts/mundo/relieve.gd)
			if t and t.resource_path.ends_with("hoja_mauti.png"):
				hoja = n
	_comprobar(hoja != null, "debajo de la piedra plana aparece la hoja de Mauti")
	_maisha().global_position = hoja.global_position + Vector2(-10, 4)
	await _esperar(0.3)
	hoja.interactuar()
	for i in 40:
		await _esperar(0.2)
		await _leer_dialogo()
		if Estado.tiene("hoja_mauti"):
			break
	_comprobar(Estado.tiene("hoja_mauti"), "Maisha recoge la hoja de Mauti")
	_maisha().global_position = viaje.position + Vector2(0, -10)
	for i in 30:
		await _esperar(0.2)
		await _leer_dialogo()
		if viaje.fase == viaje.Fase.NAVEGA:
			break
	_comprobar(viaje.fase == viaje.Fase.NAVEGA, "de vuelta a bordo, Bata sigue río arriba")

	print("Las anguilas de óxido:")
	viaje.recorrido = viaje._largo * 0.625
	await _esperar(1.5)
	var anguila: Node2D = null
	for e in get_tree().get_nodes_in_group("enemigos"):
		if String(e.get_script().resource_path).ends_with("anguila.gd"):
			anguila = e
	_comprobar(anguila != null, "salen anguilas que saltan por encima de la cubierta")
	for i in 60:
		if anguila.fase == anguila.Fase.SALTA:
			break
		await _esperar(0.05)
	_comprobar(anguila.recibir_golpe(1, Vector2.RIGHT) and anguila.fase == anguila.Fase.ATURDIDA, "un golpe en el aire la tumba en la cubierta")
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.call("morir")
	viaje._oleada = 4

	print("La llegada al muelle de la Gruta:")
	viaje.recorrido = viaje._largo - 40.0
	for i in 60:
		await _esperar(0.25)
		await _leer_dialogo()
		if Estado.tiene("travesia_hecha"):
			break
	await _esperar(0.5)
	_comprobar(Estado.tiene("travesia_hecha") and viaje.fase == viaje.Fase.ATRACADA, "atraca en el muelle de piedra")
	var p0 := _maisha().global_position
	await _empujar("mover_izquierda", 0.6)
	_comprobar(_maisha().global_position.distance_to(p0) > 20.0, "Maisha baja y anda por el muelle")
	var norte := _puerta("gruta")
	_comprobar(norte != null and norte.cerrada_hasta != "", "el camino de la Gruta de las Raíces, de momento cerrado")

	print("Volver al Embarcadero:")
	var vuelta: Node2D = null
	for n in viaje.get_children():
		if n.is_in_group("interactuables"):
			vuelta = n
	_maisha().global_position = vuelta.global_position + Vector2(-8, 0)
	await _esperar(0.3)
	vuelta.interactuar()
	await _esperar(0.3)
	await _leer_dialogo()
	for i in 200:
		if _escena() == "EmbarcaderoJunco" and not Estado.cambiando:
			break
		await get_tree().process_frame
	_comprobar(_escena() == "EmbarcaderoJunco", "desde la barca se vuelve al Embarcadero")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
