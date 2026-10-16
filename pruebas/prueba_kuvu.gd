extends Node
## Prueba automática de la pelea contra KUVU, la seta que manda (cueva de las setas, Paso de Piedra parte 4): la cortina
## de micelio que se corta con el cetro, Nungu controlado (bola de púas, el escudo lo marea, el cetro le corta el hilo),
## Nungu libre que le abre el sombrero a Kuvu, los latigazos (el escudo los para), el hilo lento de la fase 3 que vuelve
## a atrapar a Nungu, la victoria, lo que cuenta Nungu y Nungu de vuelta en su casa.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_kuvu

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


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 80:
		if not dialogo.hablando:
			return
		dialogo.pasar()
		await _esperar(0.08)


func _mirar(accion: String) -> void:
	Input.action_press(accion)
	await _esperar(0.06)
	Input.action_release(accion)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "cetro_recibido", "mapa_partido", "portal_raiz", "escudo_corteza", "armario_abierto",
			"cueva_llegada", "cueva_esporas", "nungu_pagina/1", "nungu_pagina/2", "nungu_pagina/3", "visto/cueva_setas"]:
		Estado.marcar(m)
	Estado.jugando = true
	get_tree().change_scene_to_file("res://escenas/mundo/cueva_setas.tscn")
	await _esperar(1.5)
	var maisha := _maisha()
	for n in get_tree().get_nodes_in_group("esporas"):
		n.queue_free()

	print("La cortina de micelio:")
	var cortina: Node2D = get_tree().get_first_node_in_group("cortina")
	_comprobar(cortina != null, "la cortina tapa el paso a la sala de Kuvu")
	for k in 3:
		cortina.recibir_golpe(1, Vector2.DOWN)
	await _esperar(0.3)
	await _leer_dialogo()
	await _esperar(0.6)
	_comprobar(Estado.tiene("cortina_abierta") and get_tree().get_first_node_in_group("cortina") == null, "tres golpes de cetro y se rompe")

	print("Nungu, controlado:")
	var zona: Node2D = get_tree().get_nodes_in_group("zonas")[0]
	_comprobar(zona.jefe == "kuvu", "en la sala del fondo, la zona de Kuvu")
	maisha.global_position = zona.global_position + Vector2(0, 40)
	for i in 60:
		if zona.estado == zona.Estado.CERRADA:
			break
		await _esperar(0.05)
	_comprobar(zona.estado == zona.Estado.CERRADA, "al entrar, las espinas suben")
	await _esperar(2.4)
	var kuvu: Node2D = get_tree().get_first_node_in_group("jefes")
	var nungu: Node2D = get_tree().get_first_node_in_group("nungu")
	_comprobar(kuvu != null and nungu != null and nungu.controlado(), "Kuvu despierta y Nungu está colgado de su hilo")
	_comprobar(Sonido.musica_actual == "jefe_kuvu", "suena «La seta que manda» (%s)" % Sonido.musica_actual)
	_comprobar(not kuvu.recibir_golpe(1, Vector2.UP) and kuvu.vida == R.KUVU_VIDA, "con el sombrero cerrado, el cetro no le hace nada")
	_comprobar(not nungu.recibir_golpe(1, Vector2.UP) and nungu.controlado(), "a Nungu sin marear el cetro le rebota en las púas")
	# Nungu, a la derecha de Maisha, rueda hacia ella; Maisha mira a la derecha con el escudo
	maisha.global_position = zona.global_position + Vector2(-40, 30)
	maisha.vida = maisha.vida_maxima()
	await _mirar("mover_derecha")
	maisha.global_position = zona.global_position + Vector2(-40, 30)
	nungu.global_position = maisha.global_position + Vector2(60, 0)
	Input.action_press("golpe")
	await _esperar(0.4)
	nungu._hacia = Vector2.LEFT
	nungu._pillo = false
	nungu._cambiar(nungu.Fase.RUEDA)
	for i in 40:
		if nungu.fase == nungu.Fase.MAREADO:
			break
		maisha.global_position = zona.global_position + Vector2(-40, 30)
		await _esperar(0.03)
	Input.action_release("golpe")
	_comprobar(nungu.fase == nungu.Fase.MAREADO and maisha.vida == maisha.vida_maxima(), "el escudo para la bola de púas: Nungu rebota y se marea")
	nungu.recibir_golpe(1, Vector2.RIGHT)
	_comprobar(not nungu.controlado(), "un golpe de cetro le corta el hilo: Nungu, libre")

	print("Dos contra uno:")
	for i in 200:
		if kuvu.fase == kuvu.Fase.ABIERTO:
			break
		await _esperar(0.05)
	_comprobar(kuvu.fase == kuvu.Fase.ABIERTO, "Nungu rueda contra el pie de Kuvu y Kuvu levanta el sombrero")
	_comprobar(kuvu.recibir_golpe(1, Vector2.UP) and kuvu.vida == R.KUVU_VIDA - 1, "con las láminas al aire, el cetro le quita 1")
	kuvu.recibir_danio(2, kuvu.global_position, "explosion")
	_comprobar(kuvu.vida == R.KUVU_VIDA - 3, "y una semilla, 2")
	# un latigazo con el escudo: no hace daño (Kuvu y Nungu, quietos mientras tanto, y sin esporas: así nada más
	# puede tocar a Maisha ni apartarla de la raya del latigazo)
	kuvu.set_process(false)
	nungu.set_process(false)
	nungu.set_physics_process(false)
	for n in get_tree().get_nodes_in_group("esporas"):
		n.queue_free()
	maisha.global_position = kuvu.global_position + Vector2(0, 60)
	maisha.mirar(Vector2.UP)                 # (mirando a Kuvu: directamente, no con un toque de tecla que puede perderse)
	Input.action_press("golpe")
	for i in 40:
		if maisha.escudo:
			break
		await _esperar(0.05)
	maisha.mirar(Vector2.UP)
	maisha.global_position = kuvu.global_position + Vector2(0, 60)
	var vida_antes: int = maisha.vida
	kuvu._latigo_hacia = (maisha.global_position + Vector2(0, -8) - (kuvu.global_position + Vector2(0, -30))).normalized()
	kuvu._latigazo(maisha)
	Input.action_release("golpe")
	_comprobar(maisha.vida == vida_antes, "el escudo, de frente, para el latigazo de hilo")
	await _esperar(0.3)
	maisha.set("_invulnerable", 0.0)
	maisha.global_position = kuvu.global_position + Vector2(0, 60)
	vida_antes = maisha.vida
	kuvu._latigo_hacia = (maisha.global_position + Vector2(0, -8) - (kuvu.global_position + Vector2(0, -30))).normalized()
	kuvu._latigazo(maisha)
	_comprobar(maisha.vida == vida_antes - 1 and float(maisha.mareo) > 0.0, "sin escudo, el latigazo duele y marea")
	kuvu.set_process(true)
	nungu.set_process(true)
	nungu.set_physics_process(true)

	print("La fase 3: el hilo lento que va a por Nungu:")
	kuvu.vida = R.KUVU_VIDA / 3
	kuvu._cambiar(kuvu.Fase.PELEA)
	nungu.global_position = kuvu.global_position + Vector2(50, 60)
	nungu.set_process(false)
	maisha.global_position = kuvu.global_position + Vector2(-80, 60)
	kuvu._hilo = 0.0
	for i in 200:
		if nungu.controlado():
			break
		await _esperar(0.05)
	_comprobar(nungu.controlado(), "si nadie se pone en medio, el hilo vuelve a atrapar a Nungu")
	nungu.set_process(true)
	nungu._cambiar(nungu.Fase.MAREADO)
	nungu.recibir_golpe(1, Vector2.RIGHT)
	_comprobar(not nungu.controlado(), "(y se le vuelve a liberar igual)")

	print("La victoria:")
	maisha.vida = maisha.vida_maxima()
	kuvu._cambiar(kuvu.Fase.ABIERTO)
	kuvu._herir(kuvu.vida)
	for i in 120:
		if zona.estado == zona.Estado.PURGADA:
			break
		await _esperar(0.05)
	_comprobar(Estado.tiene("kuvu_vencido") and zona.estado == zona.Estado.PURGADA, "Kuvu se marchita y la sala queda limpia")
	_comprobar(Bestiario.rango("kuvu") >= 1, "Kuvu entra en el Bestiario")
	await _esperar(3.0)
	await _leer_dialogo()
	await _esperar(0.6)
	_comprobar(Estado.tiene("nungu_libre") and Estado.tiene("investigacion_nungu"), "Nungu da las gracias y regala su investigación")
	_comprobar(Misiones.estado(Misiones.buscar("bajo_la_casa")) == "hecha", "la misión «Bajo la casa», cumplida")

	print("Nungu, de vuelta en casa:")
	get_tree().change_scene_to_file("res://escenas/interiores/casa_nungu.tscn")
	await _esperar(1.2)
	await _leer_dialogo()
	var en_casa := get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.has_method("interactuar") and str(n.get_script().resource_path).ends_with("nungu_casa.gd"))
	_comprobar(not en_casa.is_empty(), "Nungu está en su casa, junto a la mesa")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
