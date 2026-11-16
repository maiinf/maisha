extends Node
## Prueba automática de Las Galerías de Ámbar (Asterhaul): se llega por la verja del oeste de Mji-Jiwe, suena su
## música, Kito en gris, la reja cerrada (que corta la vía), el cambio de agujas (la vagoneta va por donde manda),
## la barricada de la Veta, la Esquirla de Kito, la reja abierta, el Mchimbaji estampado en el ramal muerto, la
## Bóveda a oscuras y sus geodas, la barricada de la Cámara, el Kifaru (el cetro rebota, el pilar, la vagoneta,
## la furia, vencido: la Cadena del Oeste y su Esquirla) y la vuelta.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_galerias_ambar

const VIA := preload("res://scripts/mundo/asterhaul/via.gd")

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


## Espera a que una vagoneta se pare
func _rodar(v: Node2D) -> void:
	for i in 100:
		if not v.rodando:
			break
		await _esperar(0.1)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "carga_sismica", "mwamba_pulso", "mwamba_hablado", "puerta_crater_abierta",
			"mji_jiwe_llegada", "mhunzi_conocida", "arte_tierra", "mapa_asterhaul"]:
		Estado.marcar(marca)
	Estado.jugando = true

	print("Llegar a las Galerías:")
	await _ir("mji_jiwe", "desfiladero", "MjiJiwe")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var paso: Node2D = null
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == "galerias":
			paso = p
	_comprobar(paso != null and paso.destino == "galerias_ambar", "con el Arte de la Tierra, la verja del oeste de Mji-Jiwe está abierta")
	m.global_position = paso.global_position + Vector2(30, 6)
	Input.action_press("mover_izquierda")
	for i in 240:
		if _escena() == "GaleriasAmbar":
			break
		await get_tree().process_frame
	Input.action_release("mover_izquierda")
	await _esperar(1.0)
	_comprobar(_escena() == "GaleriasAmbar", "andando por ella se llega a Las Galerías de Ámbar (%s)" % _escena())
	_comprobar(Sonido.musica_actual == "galerias_ambar", "suena «Las vetas que cantan» (%s)" % Sonido.musica_actual)
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.x > 84.0 * 16.0, "Maisha aparece en la entrada del este (%s)" % m.global_position)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("galerias_llegada"), "piensa al llegar")
	m.set("_invulnerable", 600.0)

	print("Kito y la reja:")
	var kito := _cerca("escribas", 70, 25)
	_comprobar(kito.id == "kito_gris", "Kito está en gris")
	await _hablar(m, kito)
	_comprobar(Estado.tiene("kito_vista") and not Estado.tiene("kito_pulso"), "no habla: Maisha la mira")
	_comprobar(VIA.tope(get_tree(), Vector2i(49, 27)) != null, "la reja del Cruce Mayor está cerrada y corta la vía")
	m.global_position = _sitio(51, 27)
	Input.action_press("mover_izquierda")
	await _esperar(0.9)
	Input.action_release("mover_izquierda")
	_comprobar(m.global_position.x > 49.0 * 16.0, "y no deja pasar (%.0f)" % m.global_position.x)

	print("El cambio de agujas:")
	var aguja := _cerca("agujas", 64, 27)
	var vagoneta := _cerca("vagonetas", 76, 27)
	_comprobar(aguja.direccion() == Vector2i.LEFT, "el primer desvío apunta al oeste")
	await _cargar(m, vagoneta, Vector2(24, 0))
	await _rodar(vagoneta)
	_comprobar(vagoneta.casilla() == Vector2i(50, 27), "la vagoneta sigue recto y se para ante la reja (%s)" % vagoneta.casilla())
	_comprobar(aguja.recibir_golpe(1, Vector2.UP) and aguja.direccion() == Vector2i.UP, "un golpe de cetro gira la palanca al norte")
	await _cargar(m, vagoneta, Vector2(-24, 0))
	await _rodar(vagoneta)
	_comprobar(vagoneta.casilla() == Vector2i(64, 18), "ahora la vagoneta toma el ramal del norte (%s)" % vagoneta.casilla())
	_comprobar(Estado.tiene("galerias/barricada_veta"), "y rompe la barricada de la Veta Norte")

	print("La Veta Norte:")
	var bicho := _cerca("mchimbajis", 58, 9)
	_comprobar(get_tree().get_nodes_in_group("mchimbajis").size() == 3 and not bicho.recibir_golpe(1, Vector2.RIGHT), "hay tres Mchimbaji; rodando, el cetro rebota")
	m.global_position = _cerca("recogibles", 54, 7).global_position
	await _esperar(0.5)
	_comprobar(Estado.cuantos("esquirla_kito") == 1, "la Esquirla de Kito está en la Veta")
	await _hablar(m, kito)
	await _esperar(1.2)
	await _leer_dialogo()
	_comprobar(kito.id == "kito" and Estado.tiene("kito_pulso") and Estado.tiene("kito_hablado"), "Kito recupera el pulso y habla")
	await _esperar(0.3)
	_comprobar(VIA.tope(get_tree(), Vector2i(49, 27)) == null, "y abre la reja del Cruce Mayor")

	print("El Cruce Mayor: el Mchimbaji y el ramal muerto:")
	var triple := _cerca("agujas", 40, 27)
	bicho = _cerca("mchimbajis", 36, 27)
	triple.recibir_golpe(1, Vector2.UP)
	_comprobar(triple.direccion() == Vector2i.UP, "el desvío triple, al norte")
	for i in 150:
		if bicho.fase == bicho.Fase.PANZA:
			break
		await _esperar(0.1)
	_comprobar(bicho.fase == bicho.Fase.PANZA and bicho.casilla() == Vector2i(33, 22), "el Mchimbaji entra en el ramal muerto y se estampa contra el parachoques (%s)" % bicho.casilla())
	_comprobar(bicho.recibir_golpe(1, Vector2.RIGHT) and bicho.vida == 1, "panza arriba, el cetro sí entra")
	bicho.recibir_golpe(1, Vector2.RIGHT)
	await _esperar(0.6)
	_comprobar(get_tree().get_nodes_in_group("mchimbajis").size() == 2 and int(Estado.extra.get("bestiario", {}).get("mchimbaji", 0)) == 1, "dos golpes y cuenta en el Bestiario")

	print("La Bóveda de las Geodas:")
	triple.recibir_golpe(1, Vector2.UP)
	_comprobar(triple.direccion() == Vector2i.DOWN, "el desvío triple, al sur")
	vagoneta = _cerca("vagonetas", 45, 27)
	await _cargar(m, vagoneta, Vector2(24, 0))
	await _rodar(vagoneta)
	_comprobar(vagoneta.casilla() == Vector2i(40, 35) and Estado.tiene("galerias/barricada_boveda"), "la vagoneta baja y rompe la barricada de la Bóveda (%s)" % vagoneta.casilla())
	var escena := get_tree().current_scene
	_comprobar(escena.get("_oscuro") < 0.1, "arriba hay luz")
	m.global_position = _sitio(50, 47)
	await _esperar(1.2)
	_comprobar(escena.get("_oscuro") > 0.9, "en la Bóveda no se ve nada (%.2f)" % escena.get("_oscuro"))
	var geodas := get_tree().get_nodes_in_group("geodas")
	_comprobar(geodas.size() == 5 and not geodas[0].encendida, "hay cinco geodas dormidas")
	_comprobar(geodas[0].recibir_golpe(1, Vector2.UP) and geodas[0].encendida and Estado.tiene("galerias/geoda_1"), "un golpe de cetro y la geoda alumbra")
	for i in range(1, 5):
		geodas[i].recibir_golpe(1, Vector2.UP)
	_comprobar(Estado.tiene("secreto/galerias_ambar/geodas"), "con las cinco encendidas, un secreto")
	bicho = _cerca("mchimbajis", 56, 44)
	vagoneta.global_position = _sitio(40, 44)
	var antes := get_tree().get_nodes_in_group("mchimbajis").size()
	bicho.global_position = _sitio(46, 44)
	bicho.set("_meta", _sitio(46, 44))
	await _cargar(m, vagoneta, Vector2(-24, 0))
	await _rodar(vagoneta)
	_comprobar(get_tree().get_nodes_in_group("mchimbajis").size() == antes - 1, "una vagoneta lanzada aplasta al Mchimbaji")
	m.global_position = _cerca("recogibles", 71, 51).global_position
	await _esperar(0.5)
	_comprobar(Estado.tiene("esquirla/boveda") and Estado.cuantos("esquirla_estrella") == 1, "al fondo, una Esquirla de Estrella")

	print("La Cámara del Ancla:")
	triple.recibir_golpe(1, Vector2.UP)
	_comprobar(triple.direccion() == Vector2i.LEFT, "el desvío triple, al oeste")
	vagoneta.global_position = _sitio(40, 35)
	await _cargar(m, vagoneta, Vector2(0, 24))
	await _rodar(vagoneta)
	_comprobar(vagoneta.casilla() == Vector2i(30, 27) and Estado.tiene("galerias/barricada_camara"), "la vagoneta sube, gira al oeste y rompe la barricada de la Cámara (%s)" % vagoneta.casilla())
	var kifaru := get_tree().get_first_node_in_group("kifarus") as Node2D
	_comprobar(kifaru != null and kifaru.fase == kifaru.Fase.DORMIDO, "el Kifaru duerme en su cámara")
	m.global_position = _sitio(23, 24)
	await _esperar(0.6)
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(kifaru.fase != kifaru.Fase.DORMIDO and Sonido.musica_actual == "jefe_kifaru", "al entrar, despierta (suena «El cuerno de basalto»)")
	_comprobar(not kifaru.recibir_golpe(1, Vector2.LEFT) and kifaru.vida == 12, "el cetro rebota en el basalto")
	var pilar := _cerca("pilares_basalto", 20, 22)
	m.global_position = _sitio(14, 34)
	kifaru.global_position = pilar.global_position + Vector2(-70, 6)
	kifaru.set("_rumbo", Vector2.RIGHT)
	kifaru.call("_cambiar", kifaru.Fase.EMBISTE)
	await _esperar(0.7)
	_comprobar(pilar.roto and kifaru.fase == kifaru.Fase.ABIERTO, "si embiste contra un pilar, el pilar se parte y se le abre la coraza (%d)" % kifaru.fase)
	_comprobar(kifaru.recibir_golpe(1, Vector2.LEFT) and kifaru.vida == 11, "abierto, el cetro sí entra")
	for i in 3:
		kifaru.recibir_golpe(1, Vector2.LEFT)
	await _esperar(0.3)
	_comprobar(kifaru.fase == kifaru.Fase.PASEA and kifaru.vida == 8, "a los cuatro golpes se cierra (%d, vida %d)" % [kifaru.fase, kifaru.vida])
	vagoneta = _cerca("vagonetas", 23, 27)
	kifaru.global_position = _sitio(13, 27)
	kifaru.set("_cd", 9.0)
	await _cargar(m, vagoneta, Vector2(24, 0))
	await _rodar(vagoneta)
	_comprobar(kifaru.fase == kifaru.Fase.ABIERTO, "una vagoneta lanzada también le abre la coraza (%d)" % kifaru.fase)
	for i in 4:
		kifaru.recibir_golpe(1, Vector2.LEFT)
	_comprobar(kifaru.furia() and kifaru.vida == 4, "con la mitad de la vida, entra en furia (vida %d)" % kifaru.vida)
	kifaru.abrir()
	for i in 4:
		kifaru.recibir_golpe(1, Vector2.LEFT)
	await _esperar(0.5)
	_comprobar(Estado.tiene("kifaru_vencido") and Estado.tiene("cadena_oeste_rota"), "vencido: se rompe la Cadena del Oeste")
	_comprobar(Misiones.estado(Misiones.buscar("galerias_ambar")) == "hecha", "misión cumplida")
	var esquirla: Node2D = null
	for r in get_tree().get_nodes_in_group("recogibles"):
		if r.marca == "esquirla/kifaru":
			esquirla = r
	_comprobar(esquirla != null, "suelta una Esquirla de Estrella")
	m.global_position = esquirla.global_position
	await _esperar(0.5)
	_comprobar(Estado.cuantos("esquirla_estrella") == 2, "y se recoge (%d)" % Estado.cuantos("esquirla_estrella"))
	await _esperar(3.2)
	await _leer_dialogo()
	_comprobar(Sonido.musica_actual == "galerias_ambar", "vuelve la música de la mina (%s)" % Sonido.musica_actual)

	print("Volver:")
	await _ir("galerias_ambar", "este", "GaleriasAmbar")
	_comprobar(get_tree().get_first_node_in_group("kifarus") == null, "al volver, el Kifaru ya no está")
	_comprobar(_cerca("agujas", 40, 27).direccion() == Vector2i.LEFT and _cerca("agujas", 64, 27).direccion() == Vector2i.UP, "las agujas siguen como se dejaron")
	_comprobar(get_tree().get_nodes_in_group("geodas").all(func(g: Node) -> bool: return g.encendida), "y las geodas, encendidas")
	await _ir("mji_jiwe", "galerias", "MjiJiwe")
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.x < 120.0, "de vuelta a Mji-Jiwe se sale por la verja del oeste (%s)" % m.global_position)

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
