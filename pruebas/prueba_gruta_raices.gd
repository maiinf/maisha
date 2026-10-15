extends Node
## Prueba automática de la Gruta de las Raíces (parte 1): desde el muelle de piedra de La Travesía, la boca de la cueva
## está tapada por raíces hasta tener la hoja de Mauti; dentro, la oscuridad, las semillas dormidas que laten y las
## huellas lilas de Mauti.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_gruta_raices

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
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "travesia_hecha",
			"eco/la_travesia"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("La boca de la Gruta:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/la_travesia.tscn")
	await _esperar(2.0)
	await _leer_dialogo()
	var boca := _puerta("gruta")
	_comprobar(boca != null and boca.destino == "gruta_raices" and boca.cerrada_hasta == "hoja_mauti", "en el muelle de piedra, el camino de la Gruta (se abre con la hoja de Mauti)")
	_maisha().global_position = boca.global_position + Vector2(0, 30)
	await _esperar(0.3)
	await _empujar("mover_arriba", 1.2)
	await _esperar(0.3)
	_comprobar(_escena() == "LaTravesia" and get_tree().get_first_node_in_group("dialogo").hablando, "sin la hoja, las raíces no dejan pasar")
	await _leer_dialogo()
	Estado.marcar("hoja_mauti")
	_maisha().global_position = boca.global_position + Vector2(0, 30)
	await _cruzar("mover_arriba", "GrutaRaices")
	_comprobar(_escena() == "GrutaRaices", "con la hoja de Mauti, las raíces se apartan: se entra en la Gruta")
	await _esperar(2.0)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al entrar")
	await _leer_dialogo()

	print("A oscuras:")
	var oscuridad: Node = get_tree().current_scene.get_node("Oscuridad")
	var penumbra := false
	for h in oscuridad.get_children():
		if h is CanvasModulate:
			penumbra = (h as CanvasModulate).color.v < 0.3
	_comprobar(penumbra, "la cueva está en penumbra")
	var luz := false
	for h in _maisha().get_children():
		if h is PointLight2D:
			luz = true
	_comprobar(luz, "Maisha alumbra un poco a su alrededor")
	var semillas: Array = oscuridad.get("_semillas")
	_comprobar(semillas.size() >= 6, "semillas dormidas que laten verdes en los nichos (%d)" % semillas.size())
	var huellas := 0
	for h in oscuridad.get_children():
		if h is Sprite2D:
			huellas += 1
	_comprobar(huellas >= 20, "las huellas lilas de Mauti marcan el camino hacia dentro (%d)" % huellas)
	_comprobar(Sonido.musica_actual == "gruta", "suena su música: «Las raíces que duermen» (%s)" % Sonido.musica_actual)
	var norte := _puerta("olvidado")
	_comprobar(norte != null and norte.cerrada_hasta != "", "al fondo, el Sendero Olvidado (cerrado)")

	print("El pasillo de las raíces dormidas:")
	var raices := get_tree().get_nodes_in_group("raices_dormidas")
	_comprobar(raices.size() == 3, "tres raíces enormes duermen atravesadas en el pasillo")
	_comprobar(get_tree().get_nodes_in_group("tapon_raices").size() == 2, "y dos marañas de raíces tapan el atajo al fondo y el túnel al Paso de Piedra")
	var raiz: Node2D = raices[0]
	for r in raices:
		if (r as Node2D).global_position.y > raiz.global_position.y:
			raiz = r
	var vida0: int = _maisha().vida
	_maisha().global_position = raiz.global_position + Vector2(0, 40)
	await _esperar(0.4)
	await _empujar("mover_arriba", 1.4)
	await _esperar(0.3)
	_comprobar(_maisha().global_position.y < raiz.global_position.y - 10.0, "andando, Maisha pasa por encima de la raíz")
	_comprobar(raiz.fase == raiz.Fase.DUERME and _maisha().vida == vida0, "y la raíz sigue dormida")
	_maisha().global_position = raiz.global_position + Vector2(0, 50)
	await _esperar(0.4)
	Input.action_press("correr")
	await _empujar("mover_arriba", 0.35)
	_comprobar(raiz.fase != raiz.Fase.DUERME, "corriendo cerca, la raíz abre su ojo violeta")
	_maisha().global_position = raiz.global_position + Vector2(0, 20)
	Input.action_press("mover_abajo")
	await _esperar(0.25)
	Input.action_press("mover_arriba")
	Input.action_release("mover_abajo")
	await _esperar(0.25)
	Input.action_release("mover_arriba")
	_maisha().global_position = raiz.global_position + Vector2(0, 20)
	for i in 30:
		if raiz.fase == raiz.Fase.AZOTA:
			break
		Input.action_press("mover_izquierda")
		await _esperar(0.05)
		Input.action_release("mover_izquierda")
		Input.action_press("mover_derecha")
		await _esperar(0.05)
		Input.action_release("mover_derecha")
	Input.action_release("correr")
	await _esperar(0.3)
	_comprobar(_maisha().vida < vida0, "si sigue el ruido, azota: daño y empujón")
	await _esperar(2.5)
	_comprobar(raiz.fase == raiz.Fase.DUERME, "y luego se vuelve a dormir")

	print("El santuario de corteza y el escudo:")
	var altar: Node2D = null
	for n in get_tree().get_nodes_in_group("interactuables"):
		if String(n.get_script().resource_path if n.get_script() else "").ends_with("altar_corteza.gd"):
			altar = n
	_comprobar(altar != null, "en el santuario, el tocón del Primer Árbol con un escudo encima")
	_maisha().global_position = altar.global_position + Vector2(0, 22)
	_maisha().vida = _maisha().vida_maxima()
	await _esperar(0.3)
	altar.interactuar()
	for i in 30:
		await _esperar(0.2)
		await _leer_dialogo()
		if Estado.tiene("escudo_corteza"):
			break
	_comprobar(Estado.tiene("escudo_corteza"), "al tocarlo, la corteza se enrosca en el cetro: el Escudo de corteza")
	await _esperar(1.5)
	Input.action_press("golpe")
	await _esperar(0.5)
	_comprobar(_maisha().escudo, "manteniendo J, Maisha levanta el escudo")
	_maisha().mirar(Vector2.UP)
	await _esperar(0.1)
	var vida1: int = _maisha().vida
	_maisha().set("_invulnerable", 0.0)
	_comprobar(not _maisha().recibir_danio(1, _maisha().global_position + Vector2(0, -40), "espina") and _maisha().vida == vida1, "el escudo para lo que viene de frente")
	_maisha().set("_invulnerable", 0.0)
	Input.action_release("golpe")
	await _esperar(0.2)
	_comprobar(not _maisha().escudo, "al soltar J, lo baja")
	_comprobar(_maisha().recibir_danio(1, _maisha().global_position + Vector2(0, -40), "espina") and _maisha().vida == vida1 - 1, "sin escudo, la espina hace daño")

	print("La galería de las espinas:")
	var espinos := get_tree().get_nodes_in_group("espinos")
	_comprobar(espinos.size() == 4, "cuatro espinos de Giza en la galería")
	var espino: Node2D = espinos[0]
	_maisha().global_position = espino.global_position + Vector2(0, 70)
	_maisha().vida = _maisha().vida_maxima()
	_maisha().set("_invulnerable", 0.0)
	var escupe := false
	for i in 40:
		await _esperar(0.1)
		if not get_tree().get_nodes_in_group("espinas").is_empty():
			escupe = true
			break
	_comprobar(escupe, "con Maisha cerca, el espino se hincha y escupe espinas")
	_comprobar(not espino.recibir_golpe(1, Vector2.UP), "el cetro rebota en el espino")
	espino.recibir_danio(1, espino.global_position, "explosion")
	await _esperar(0.2)
	_comprobar(not is_instance_valid(espino), "una semilla lo deshace")

	print("El Guardián y su pesadilla:")
	var fondo: Node2D = null
	for z in get_tree().get_nodes_in_group("zonas"):
		if z.get_meta("clave") == "1":
			fondo = z
	_comprobar(fondo != null and fondo.jefe == "guardian", "en el fondo duerme el Guardián de la Gruta")
	_maisha().vida = _maisha().vida_maxima()
	_maisha().global_position = fondo.global_position + Vector2(0, 50)
	await _esperar(1.2)
	var g: Node2D = get_tree().get_first_node_in_group("jefes")
	_comprobar(g != null and g.fase != g.Fase.DORMIDO, "al entrar, la pesadilla lo despierta como a una marioneta")
	_comprobar(Sonido.musica_actual == "jefe_guardian", "con su música («La pesadilla del Guardián»)")
	_comprobar(not g.recibir_golpe(1, Vector2.UP), "con la máscara puesta, el cetro rebota")
	# la ola de raíces: de frente y con el escudo, no hace daño
	g.call("_cambiar", g.Fase.ESPERA)
	g.set("_espera", 99.0)                 # (quieto, para probar la ola a solas)
	_maisha().mirar(Vector2.UP)
	Input.action_press("golpe")
	await _esperar(0.45)
	_maisha().set("_invulnerable", 0.0)
	var vida_ola: int = _maisha().vida
	g.set("_ola_desde", _maisha().global_position + Vector2(0, -60))
	g.set("_ola_hacia", Vector2.DOWN)
	g.set("_ola_pillo", false)
	g.set("_ola", 30.0)
	await _esperar(0.5)
	Input.action_release("golpe")
	_comprobar(_maisha().vida == vida_ola, "la ola de raíces se para con el escudo, de frente")
	g.call("_chocar")
	_comprobar(g.fase == g.Fase.ATURDIDO, "si choca contra la pared, queda aturdido con la máscara torcida")
	var vida_g: int = g.vida
	_comprobar(g.recibir_golpe(1, Vector2.UP) and g.vida == vida_g - 1, "aturdido, el cetro le agrieta la máscara")
	g.vida = 1
	g.recibir_golpe(1, Vector2.UP)
	_comprobar(g.fase == g.Fase.VENCIDO, "la máscara estalla")
	for i in 60:
		await _esperar(0.25)
		await _leer_dialogo()
		if Estado.tiene("gruta_guardian") and fondo.estado == fondo.Estado.PURGADA:
			break
	_comprobar(Estado.tiene("gruta_guardian") and fondo.estado == fondo.Estado.PURGADA, "el Guardián despierta y el fondo queda purgado")
	for i in 20:
		await _esperar(0.25)
		await _leer_dialogo()
	_comprobar(get_tree().get_nodes_in_group("tapon_raices").is_empty(), "la maraña del atajo se aparta")
	_comprobar(g.is_in_group("interactuables"), "y se queda en la sala, despierto, para hablar")

	print("Las nueve voces abren el Sendero Olvidado:")
	var olvidado: Node2D = _puerta("olvidado")
	_maisha().global_position = olvidado.global_position
	await _esperar(0.6)
	await _leer_dialogo()
	await _esperar(0.4)
	_comprobar(_escena() == "GrutaRaices" and _maisha().get("puede_actuar"), "sin las nueve voces, las raíces no dejan pasar (%s %s)" % [_escena(), _maisha().get("puede_actuar")])
	Estado.marcar("nueve_ecos")
	_maisha().global_position = g.global_position + Vector2(0, 30)
	await _esperar(0.3)
	await _hablar_con(g)
	_comprobar(Estado.tiene("sendero_abierto"), "con las nueve, el Guardián abre el sendero")
	_maisha().global_position = olvidado.global_position + Vector2(0, 30)
	await _esperar(0.4)
	await _cruzar("mover_arriba", "SenderoOlvidado")
	_comprobar(_escena() == "SenderoOlvidado", "y por el fondo se sube al Sendero Olvidado")
	var a_gruta: Area2D = _puerta("gruta")
	_maisha().global_position = a_gruta.global_position + Vector2(0, -30)
	await _esperar(0.4)
	await _cruzar("mover_abajo", "GrutaRaices")
	_comprobar(_escena() == "GrutaRaices", "y se baja otra vez a la Gruta")

	print("De vuelta a La Travesía:")
	_maisha().global_position = _puerta("travesia").global_position + Vector2(0, -30)
	await _cruzar("mover_abajo", "LaTravesia")
	_comprobar(_escena() == "LaTravesia", "por el sur se vuelve al muelle de piedra")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
