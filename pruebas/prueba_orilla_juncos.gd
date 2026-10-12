extends Node
## Prueba automática de la Orilla de Juncos (el sexto camino de Raíz): de la Ciénaga Quieta hacia el Embarcadero
## Junco; el cangrejo de herrumbre (enemigo nuevo), Kasia y sus remos, la balsa que cruza al banco de arena del sexto
## eco y el paso al Embarcadero, aún cerrado.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_orilla_juncos

const R := preload("res://scripts/combate/reglas_combate.gd")
const CANGREJO := preload("res://scripts/enemigos/cangrejo.gd")
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
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco",
			"visto/cuna_de_musgo", "camino_cienaga", "visto/cienaga_quieta", "cienaga_llegada"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("De la ciénaga a la Orilla de Juncos:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/cienaga_quieta.tscn")
	await _esperar(1.5)
	await _leer_dialogo()
	var este := _puerta("orilla")
	_comprobar(este != null and este.destino == "orilla_juncos", "la ciénaga tiene una salida al este, a la Orilla de Juncos")
	_maisha().global_position = este.global_position + Vector2(-30, 0)
	await _cruzar("mover_derecha", "OrillaJuncos")
	_comprobar(_escena() == "OrillaJuncos", "se llega a la Orilla de Juncos")
	_comprobar(_maisha().global_position.distance_to(_puerta("cienaga").punto_llegada()) < 4.0, "Maisha aparece al sur, viniendo de la ciénaga")
	await _esperar(2.5)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al llegar")
	await _leer_dialogo()
	_comprobar(Sonido.musica_actual == "orilla", "suena su propia música («La linterna en la orilla»)")

	print("La orilla:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	_comprobar(region.tam.y >= 100 * 16, "sube de sur a norte: unas 4 pantallas de alto")
	var zonas := get_tree().get_nodes_in_group("zonas")
	_comprobar(zonas.size() == 1 and zonas[0].tipos_enemigo.has("cangrejo"), "una zona corrupta en la playa del sur, con cangrejos de herrumbre")
	_comprobar(region.secretos_total == 1, "un secreto entre los juncos del noroeste")
	var remos := get_tree().get_nodes_in_group("recogibles").filter(func(n: Node) -> bool: return n.objeto == "remo")
	_comprobar(remos.size() == 3, "tres remos de Kasia")
	var kasia: Node2D = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "kasia")[0]
	_comprobar(kasia != null, "Kasia, la nutria barquera, junto a su casa de barcas")
	var balsa: Node2D = get_tree().get_first_node_in_group("balsas")
	_comprobar(balsa != null and not balsa.arreglada(), "su balsa está medio hundida en el embarcadero")
	for z in zonas:
		z.set("activa", false)

	print("El cangrejo de herrumbre:")
	var maisha := _maisha()
	var zona: Node2D = zonas[0]
	var cangrejo: CharacterBody2D = CANGREJO.new()
	cangrejo.zona = zona
	cangrejo.position = zona.global_position
	region.get_node(region.entidades).add_child(cangrejo)
	maisha.global_position = zona.global_position + Vector2(60, 0)
	maisha.vida = maisha.vida_maxima()
	await _esperar(0.3)
	_comprobar(not cangrejo.recibir_golpe(1, Vector2.LEFT) and cangrejo.vida == R.CANGREJO_VIDA, "de frente, el cetro rebota en su caparazón")
	var pellizco := false
	for i in 80:
		await _esperar(0.05)
		if cangrejo.fase == cangrejo.Fase.EXPUESTO:
			pellizco = true
			break
	_comprobar(pellizco and maisha.vida < maisha.vida_maxima(), "se acerca de lado, avisa con las pinzas y pellizca")
	_comprobar(cangrejo.recibir_golpe(1, Vector2.LEFT) and cangrejo.vida == R.CANGREJO_VIDA - 1, "justo después queda expuesto: el cetro le quita 1")
	cangrejo.recibir_danio(1, cangrejo.global_position, "explosion")
	_comprobar(cangrejo.fase == cangrejo.Fase.VOLCADO, "la explosión de una semilla lo vuelca, panza arriba")
	var vida_antes: int = cangrejo.vida
	var dio: bool = cangrejo.recibir_golpe(1, Vector2.LEFT)
	_comprobar(dio and (cangrejo.vida <= vida_antes - 2 or cangrejo.get("_muriendo")), "volcado, el cetro le quita 2")
	await _esperar(0.6)
	_comprobar(not is_instance_valid(cangrejo), "y acaba deshecho")
	maisha.vida = maisha.vida_maxima()

	print("Kasia y sus remos:")
	maisha.global_position = balsa.punto_interaccion() + Vector2(-20, 0)
	await _esperar(0.2)
	balsa.interactuar()
	await _esperar(0.3)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "la balsa rota no se puede usar (Maisha piensa por qué)")
	await _leer_dialogo()
	maisha.global_position = kasia.global_position + Vector2(0, 16)
	await _esperar(0.2)
	await _hablar_con(kasia)
	_comprobar(Estado.tiene("encargo_kasia") and Estado.tiene("kasia_conocida"), "Kasia pide sus tres remos")
	_comprobar(Misiones.activas().any(func(m: Dictionary) -> bool: return m["id"] == "remos_kasia"), "sale el encargo en el diario")
	for n in remos:
		maisha.global_position = n.global_position
		await _esperar(0.25)
	_comprobar(Estado.cuantos("remo") == 3, "se recogen al pasar (%d/3)" % Estado.cuantos("remo"))
	var sopas: int = Estado.cuantos("sopa")
	maisha.global_position = kasia.global_position + Vector2(0, 16)
	await _esperar(0.3)
	await _hablar_con(kasia)
	_comprobar(Estado.tiene("kasia_remos") and Estado.cuantos("remo") == 0, "se los entrega")
	_comprobar(Estado.cuantos("sopa") == sopas + 2, "y Kasia le da dos sopas")
	_comprobar(balsa.arreglada(), "Kasia saca la balsa del agua")

	print("La balsa:")
	maisha.global_position = balsa.punto_interaccion() + Vector2(-20, 0)
	await _esperar(0.3)
	balsa.interactuar()
	for i in 80:
		await _esperar(0.1)
		if not balsa.cruzando:
			break
	_comprobar(balsa.en_el_este and maisha.global_position.x > 46 * 16, "Maisha se sube y la balsa cruza el río hasta el banco de arena (%.0f)" % maisha.global_position.x)
	var eco: Node2D = get_tree().get_first_node_in_group("ecos_perdidos")
	_comprobar(eco != null and eco.global_position.distance_to(maisha.global_position) < 80.0, "allí está la piedra del sexto eco")
	print("El paso al Embarcadero, cerrado antes del eco:")
	var norte := _puerta("embarcadero")
	_comprobar(norte != null and norte.destino == "embarcadero_junco" and norte.cerrada_hasta == "eco/orilla_juncos", "al norte, el paso al Embarcadero Junco (se abre con el sexto eco)")
	var en_el_banco := maisha.global_position
	maisha.global_position = norte.global_position + Vector2(0, 30)
	await _esperar(0.3)
	await _empujar("mover_arriba", 1.2)
	await _esperar(0.3)
	_comprobar(_escena() == "OrillaJuncos" and get_tree().get_first_node_in_group("dialogo").hablando, "no deja pasar, y Maisha piensa por qué")
	await _leer_dialogo()
	maisha.global_position = en_el_banco
	await _esperar(0.3)

	print("El sexto eco perdido (la despedida):")
	maisha.global_position = eco.global_position + Vector2(-14, 4)
	await _esperar(0.3)
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
	_comprobar(con_imagen, "el recuerdo tiene su ilustración (18_eco_orilla)")
	_comprobar(Estado.tiene("eco/orilla_juncos") and ECO.cuantos_escuchados() == 1, "sexto eco apuntado (en esta prueba, el primero que se oye)")
	# (de vuelta a la balsa, que está en el banco de arena)
	maisha.global_position = balsa.punto_interaccion() + Vector2(18, 0)
	await _esperar(0.3)
	balsa.interactuar()
	for i in 80:
		await _esperar(0.1)
		if not balsa.cruzando:
			break
	_comprobar(not balsa.en_el_este and maisha.global_position.x < 42 * 16, "y de vuelta, a la orilla del oeste (%.0f)" % maisha.global_position.x)

	print("El paso al Embarcadero, abierto tras el eco:")
	maisha.global_position = norte.global_position + Vector2(0, 30)
	await _cruzar("mover_arriba", "EmbarcaderoJunco")
	_comprobar(_escena() == "EmbarcaderoJunco", "tras el sexto eco se sube al Embarcadero Junco")
	await _esperar(2.5)
	await _leer_dialogo()
	maisha = _maisha()
	maisha.global_position = _puerta("orilla").global_position + Vector2(0, -36)
	await _cruzar("mover_abajo", "OrillaJuncos")
	_comprobar(_escena() == "OrillaJuncos", "y por el sur se vuelve a la Orilla")
	maisha = _maisha()

	print("De vuelta a la ciénaga:")
	maisha.global_position = _puerta("cienaga").global_position + Vector2(0, -40)
	await _cruzar("mover_abajo", "CienagaQuieta")
	_comprobar(_escena() == "CienagaQuieta", "por el sur se vuelve a la Ciénaga Quieta")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
