extends Node
## Prueba automática de la Cañada del Eco (el quinto camino de Raíz): del Bosque Cobrizo hacia el Lago Espejo;
## la garganta de peña, el murciélago de eco (enemigo nuevo), Mbuzi y sus cencerros, la escala de cuerda que descuelga hasta la cornisa del quinto eco
## (con su recuerdo: Maisha, Mauti y Kimya en la cañada) y el paso al lago, aún cerrado.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_canada_eco

const R := preload("res://scripts/combate/reglas_combate.gd")
const MURCIELAGO := preload("res://scripts/enemigos/murcielago.gd")
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
			"visto/cuna_de_musgo", "bibi_conocida", "bibi_aldea_viva", "camino_bosque", "camino_cienaga",
			"visto/bosque_cobrizo", "bosque_llegada", "cobrizo_llegada"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("Del bosque a la Cañada del Eco:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/bosque_cobrizo.tscn")
	await _esperar(1.5)
	await _leer_dialogo()
	var oeste := _puerta("canada")
	_comprobar(oeste != null and oeste.destino == "canada_eco", "el bosque tiene una salida al oeste, a la Cañada del Eco")
	_maisha().global_position = oeste.global_position + Vector2(30, 0)
	await _cruzar("mover_izquierda", "CanadaEco")
	_comprobar(_escena() == "CanadaEco", "se llega a la Cañada del Eco")
	_comprobar(_maisha().global_position.distance_to(_puerta("bosque").punto_llegada()) < 4.0, "Maisha aparece al este, viniendo del bosque")
	await _esperar(2.5)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al llegar")
	await _leer_dialogo()
	_comprobar(Sonido.musica_actual == "canada", "suena su música: «Lo que la peña devuelve» (%s)" % Sonido.musica_actual)

	print("La cañada:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	_comprobar(region.tam.x >= 140 * 16, "va de este a oeste: unas 3,5 pantallas de largo")
	var zonas := get_tree().get_nodes_in_group("zonas")
	_comprobar(zonas.size() == 1 and zonas[0].tipos_enemigo.has("murcielago"), "una zona corrupta en el ensanche del sur, con murciélagos de eco")
	_comprobar(region.secretos_total == 1, "un secreto al noroeste")
	var cencerros := get_tree().get_nodes_in_group("recogibles").filter(func(n: Node) -> bool: return n.objeto == "cencerro")
	_comprobar(cencerros.size() == 3, "tres cencerros de Mbuzi")
	var mbuzi: Node2D = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "mbuzi")[0]
	_comprobar(mbuzi != null, "Mbuzi, la cabra montés, junto a su aprisco")
	var escala: Node2D = get_tree().get_first_node_in_group("escalas")
	_comprobar(escala != null and not escala.descolgada(), "la escala de cuerda está enrollada arriba")
	for z in zonas:
		z.set("activa", false)          # (aquí no se pelea)

	print("La peña y la escala:")
	var maisha := _maisha()
	var pie := Vector2(104 * 16 + 16, 16 * 16)
	maisha.global_position = pie
	await _esperar(0.2)
	await _empujar("mover_arriba", 1.6)
	_comprobar(maisha.global_position.y > 12 * 16, "sin la escala no se sube a la cornisa (%.0f)" % maisha.global_position.y)
	maisha.global_position = Vector2(80 * 16, 22 * 16)
	await _esperar(0.2)
	await _empujar("mover_arriba", 1.6)
	_comprobar(maisha.global_position.y > 16 * 16, "las paredes de la garganta no dejan pasar (%.0f)" % maisha.global_position.y)

	print("El murciélago de eco:")
	var zona: Node2D = zonas[0]
	var murcielago: CharacterBody2D = MURCIELAGO.new()
	murcielago.zona = zona
	murcielago.position = zona.global_position
	region.get_node(region.entidades).add_child(murcielago)
	maisha.global_position = zona.global_position + Vector2(-60, 10)
	maisha.vida = maisha.vida_maxima()
	await _esperar(0.2)
	_comprobar(murcielago.fase == murcielago.Fase.COLGADO, "aparece colgado")
	await _esperar(R.MURCIELAGO_DESPIERTA + 0.6)
	_comprobar(murcielago.en_el_aire() and not murcielago.recibir_golpe(1, Vector2.LEFT) and murcielago.vida == R.MURCIELAGO_VIDA, "despierta y vuela: en el aire el cetro no le da")
	var aviso := false
	var onda: Node2D = null
	for i in 120:
		await _esperar(0.05)
		if murcielago.fase == murcielago.Fase.AVISA:
			aviso = true
		if aviso and not get_tree().get_nodes_in_group("ondas").is_empty():
			onda = get_tree().get_nodes_in_group("ondas")[0]
			break
	_comprobar(aviso and onda != null, "avisa (anillo y línea en el suelo) y grita: sale una onda")
	var vuelve := false
	for i in 80:
		await _esperar(0.05)
		if not is_instance_valid(onda):
			break
		if onda.volviendo:
			vuelve = true
	_comprobar(vuelve, "la onda llega lejos y vuelve, como un eco")
	_comprobar(maisha.vida < maisha.vida_maxima(), "y si pilla a Maisha, le hace daño")
	_comprobar(murcielago.fase == murcielago.Fase.ATURDIDO, "al tragarse su eco cae aturdido al suelo")
	await _esperar(0.3)
	_comprobar(murcielago.recibir_golpe(1, Vector2.LEFT) and murcielago.vida == R.MURCIELAGO_VIDA - 2, "aturdido, el cetro le quita 2")
	await _esperar(R.MURCIELAGO_ATURDIDO + 0.8)
	_comprobar(murcielago.en_el_aire(), "luego vuelve a volar")
	# el Latido deshace la onda
	onda = null
	for i in 120:
		await _esperar(0.05)
		if not get_tree().get_nodes_in_group("ondas").is_empty():
			onda = get_tree().get_nodes_in_group("ondas")[0]
			break
	if onda:
		maisha.global_position = onda.global_position + Vector2(10, 0)
		maisha.aliento = maisha.aliento_maximo()
		maisha.set("_espera_latido", 0.0)
		maisha.latido()
		await _esperar(0.1)
	_comprobar(onda != null and not onda.is_in_group("ondas"), "el Latido deshace la onda")
	await _esperar(0.3)
	_comprobar(murcielago.fase != murcielago.Fase.ATURDIDO, "y sin su eco, no se marea")
	murcielago.recibir_danio(1, murcielago.global_position, "explosion")
	_comprobar(murcielago.get("_muriendo"), "la explosión de una semilla le da aunque vuele")
	var oidos := ["murcielago_chillido", "murcielago_aleteo", "murcielago_grito", "onda_rebota", "murcielago_mareo"].filter(
			func(n: String) -> bool: return int(Sonido.conteo.get(n, 0)) > 0)
	_comprobar(oidos.size() == 5, "con sus sonidos: chillido, aleteo, grito, la onda que rebota y el mareo (%s)" % [oidos])
	maisha.vida = maisha.vida_maxima()
	await _esperar(0.5)

	print("Mbuzi y sus cencerros:")
	maisha.global_position = mbuzi.global_position + Vector2(0, 16)
	await _esperar(0.2)
	await _hablar_con(mbuzi)
	_comprobar(Estado.tiene("encargo_mbuzi") and Estado.tiene("mbuzi_conocida"), "Mbuzi pide sus tres cencerros")
	_comprobar(Misiones.activas().any(func(m: Dictionary) -> bool: return m["id"] == "cencerros_mbuzi"), "sale el encargo en el diario")
	for n in cencerros:
		maisha.global_position = n.global_position
		await _esperar(0.25)
	_comprobar(Estado.cuantos("cencerro") == 3 and int(Sonido.conteo.get("cencerro", 0)) == 3, "se recogen al pasar, con su clonc (%d/3)" % Estado.cuantos("cencerro"))
	var sopas: int = Estado.cuantos("sopa")
	maisha.global_position = mbuzi.global_position + Vector2(0, 16)
	await _esperar(0.3)
	await _hablar_con(mbuzi)
	_comprobar(Estado.tiene("mbuzi_cencerros") and Estado.cuantos("cencerro") == 0, "se los entrega")
	_comprobar(Estado.cuantos("sopa") == sopas + 2, "y Mbuzi le da dos sopas")
	await _esperar(2.0)
	_comprobar(escala.descolgada(), "Mbuzi descuelga la escala (tramo a tramo; desde el aprisco no se oye: está lejos)")
	maisha.global_position = pie
	await _esperar(0.2)
	await _empujar("mover_arriba", 2.5)
	_comprobar(maisha.global_position.y < 9 * 16, "por la escala se sube a la cornisa (%.0f)" % maisha.global_position.y)
	var eco: Node2D = get_tree().get_first_node_in_group("ecos_perdidos")
	_comprobar(eco != null and eco.global_position.y < 7 * 16, "arriba está la piedra del quinto eco")

	print("El quinto eco perdido:")
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
	_comprobar(con_imagen, "el recuerdo tiene su ilustración (16_eco_canada)")
	_comprobar(Estado.tiene("eco/canada_eco") and ECO.cuantos_escuchados() == 1, "quinto eco apuntado (en esta prueba, el primero que se oye)")

	print("El paso al lago, cerrado:")
	var lago := _puerta("lago")
	_comprobar(lago != null and lago.destino == "lago_espejo" and lago.cerrada_hasta != "", "al oeste, el paso al Lago Espejo (cerrado)")
	maisha.global_position = lago.global_position + Vector2(30, 0)
	await _esperar(0.3)
	await _empujar("mover_izquierda", 1.2)
	await _esperar(0.3)
	_comprobar(_escena() == "CanadaEco" and not Estado.cambiando, "no deja pasar")
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "y Maisha piensa por qué")
	await _leer_dialogo()

	print("De vuelta al bosque:")
	maisha.global_position = _puerta("bosque").global_position + Vector2(-40, 0)
	await _cruzar("mover_derecha", "BosqueCobrizo")
	_comprobar(_escena() == "BosqueCobrizo", "por el este se vuelve al Bosque Cobrizo")
	_comprobar(_maisha().global_position.distance_to(_puerta("canada").punto_llegada()) < 4.0, "apareciendo por el oeste del bosque")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
