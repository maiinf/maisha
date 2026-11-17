extends Node
## Prueba automática de El Núcleo de la Estrella (el final de Asterhaul): la Losa de Mji-Jiwe solo se abre con las
## tres cadenas rotas y los doce yunques, se baja por el pozo, suena su música, Mauti en el Atrio, la Cámara Sísmica
## (muro, vagoneta, derrumbe y el pilar del primer sello), la compuerta que abre, la Cámara Magnética (barcaza,
## bloque-imán y la placa del segundo sello), la Cámara de la Resonancia (el vacío, el puente de dos monolitos y el
## sello que solo despierta con la nota de verdad), la Puerta Triple, el Corazón del Meteorito (el cetro rebota, el
## latido, el aro sísmico con la Carga, el magnético con el Pulso, el de ámbar con un monolito, el núcleo con el
## cetro), el final (Mauti, la semilla mayor, el Cetro del Nexo despierto, la pantalla de fin) y la vuelta.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_nucleo_estrella

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


func _pulsar(m: CharacterBody2D) -> bool:
	m.aliento = m.aliento_maximo()
	m.set("_espera_pulso", 0.0)
	return m.pulso()


func _resonar(m: CharacterBody2D) -> bool:
	m.aliento = m.aliento_maximo()
	m.set("_espera_resonancia", 0.0)
	return m.resonancia()


func _callar_todos() -> void:
	for mono in get_tree().get_nodes_in_group("monolitos"):
		mono.callar()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "carga_sismica", "pulso_magnetico", "resonancia_ambar",
			"puerta_crater_abierta", "mji_jiwe_llegada", "mhunzi_conocida", "arte_tierra", "mapa_asterhaul",
			"kifaru_vencido", "cadena_oeste_rota", "nyundo_vencido", "cadena_este_rota", "kipanga_vencido", "cadena_norte_rota"]:
		Estado.marcar(marca)
	for a in ["mwamba", "jabali", "kokoto", "tofali", "cheche", "makaa", "bati", "mlio", "sauti", "kito", "moto"]:
		Estado.marcar(a + "_pulso")
	Estado.jugando = true

	print("La Losa de Mji-Jiwe:")
	await _ir("mji_jiwe", "desfiladero", "MjiJiwe")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var pozo: Node2D = null
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == "nucleo":
			pozo = p
	_comprobar(pozo != null and pozo.destino == "nucleo_estrella" and not Estado.tiene("nucleo_abierto"), "con las tres cadenas rotas pero once yunques, la Losa sigue cerrada")
	_comprobar(Misiones.estado(Misiones.buscar("nucleo_estrella")) == "activa", "la misión «Lo que cayó del cielo» está activa")
	Estado.marcar("pigo_pulso")
	await _esperar(0.3)
	_comprobar(Estado.tiene("yunques_completos") and Estado.tiene("nucleo_abierto"), "con el duodécimo yunque, la Losa se abre")
	_comprobar(get_tree().current_scene.get("_pozo") != null, "y se ve el pozo")
	m.global_position = pozo.global_position + Vector2(0, 30)
	Input.action_press("mover_arriba")
	for i in 240:
		if _escena() == "NucleoEstrella":
			break
		await get_tree().process_frame
	Input.action_release("mover_arriba")
	await _esperar(1.0)
	_comprobar(_escena() == "NucleoEstrella", "bajando por el pozo se llega a El Núcleo de la Estrella (%s)" % _escena())
	_comprobar(Sonido.musica_actual == "nucleo_estrella", "suena «Lo que cayó del cielo» (%s)" % Sonido.musica_actual)
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var escena := get_tree().current_scene
	_comprobar(m.global_position.y > 65.0 * 16.0, "Maisha aparece en la escalera del pozo (%s)" % m.global_position)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("nucleo_llegada"), "piensa al llegar")
	var mauti: Node2D = null
	for n in get_tree().get_nodes_in_group("interactuables"):
		if n.get("id") == "mauti":
			mauti = n
	m.global_position = mauti.global_position + Vector2(0, 14)
	mauti.interactuar()
	await _leer_dialogo()
	_comprobar(Estado.tiene("mauti_nucleo_hablado"), "Mauti espera en el Atrio")

	print("La Cámara Sísmica:")
	var compuerta_1 := _cerca("compuertas", 28, 40)
	_comprobar(not compuerta_1.abierta, "la compuerta a la Cámara Magnética está cerrada")
	var muro := _cerca("sismicos", 6, 44)
	await _cargar(m, muro, Vector2(0, 26))
	_comprobar(Estado.tiene("nucleo/muro"), "una Carga tira el muro agrietado")
	m.set("_invulnerable", 900.0)
	var vagoneta := _cerca("vagonetas", 6, 38)
	await _cargar(m, vagoneta, Vector2(-24, 0))
	for i in 60:
		if not vagoneta.rodando:
			break
		await _esperar(0.1)
	_comprobar(Estado.tiene("nucleo/derrumbe"), "la vagoneta, lanzada por la vía, aparta el derrumbe")
	var pilar := _cerca("pilares_diapason", 22, 37)
	await _cargar(m, pilar, Vector2(0, 20))
	await _esperar(0.3)
	_comprobar(Estado.tiene("nucleo/sello_sismico") and compuerta_1.abierta, "el pilar despierta el primer sello y la compuerta se abre")

	print("La Cámara Magnética:")
	var barcaza := escena.get_node("Barcaza") as Node2D
	m.global_position = barcaza.global_position + Vector2(24, 26)
	_comprobar(_pulsar(m) and barcaza.moviendose, "subida a la barcaza, el Pulso la lleva por encima de la escoria")
	for i in 100:
		if not barcaza.moviendose:
			break
		await _esperar(0.1)
	await _esperar(0.2)
	_comprobar(barcaza.en_b and m.global_position.x > 46.0 * 16.0, "hasta la otra orilla (%s)" % m.global_position)
	var compuerta_2 := _cerca("compuertas", 57, 40)
	_comprobar(not compuerta_2.abierta, "la compuerta a la Cámara de la Resonancia está cerrada")
	var bloque := _cerca("bloques_iman", 51, 41)
	m.global_position = _sitio(51, 34)
	_pulsar(m)
	await _esperar(1.6)
	_comprobar(bloque.casilla() == Vector2i(51, 36), "el Pulso trae el bloque-imán a su placa (%s)" % bloque.casilla())
	await _esperar(0.2)
	_comprobar(Estado.tiene("nucleo/sello_magnetico") and compuerta_2.abierta, "el segundo sello se enciende y la compuerta se abre")
	var puerta := get_tree().get_first_node_in_group("puertas_triples")
	_comprobar(puerta.encendidos() == 2 and not puerta.esta_abierta(), "la Puerta Triple tiene dos ojos encendidos y sigue cerrada")

	print("La Cámara de la Resonancia:")
	var vacio := escena.get_node("Vacio")
	for popo in get_tree().get_nodes_in_group("popos"):
		popo.set("_cd", 99.0)                         # (que no se meta un picado en la cuenta de hojas)
	m.set("_invulnerable", 0.0)
	m.global_position = _sitio(63, 39)
	await _esperar(0.3)
	var vida: int = m.vida
	m.global_position = _sitio(65, 39)
	await _esperar(2.5)
	_comprobar(m.vida == vida - 1 and m.global_position.x < 64.0 * 16.0, "sin puente, el vacío hace caer (%d → %d)" % [vida, m.vida])
	m.set("_invulnerable", 900.0)
	var sello := get_tree().get_first_node_in_group("monolito_sello")
	sello.recibir_carga(Vector2.RIGHT)
	_comprobar(sello.cantando() and not Estado.tiene("nucleo/sello_resonante"), "un campanazo al monolito del sello no basta")
	sello.callar()
	m.global_position = _sitio(62, 44)
	_resonar(m)
	await _esperar(1.6)
	var puente := get_tree().get_first_node_in_group("puentes_cristal")
	_comprobar(puente.losas() == 16, "la nota del monolito de la cornisa se contagia al de la peña: el puente está entero (%d)" % puente.losas())
	_comprobar(not Estado.tiene("nucleo/sello_resonante"), "el eco no llega al sello")
	for x in range(64, 73):
		m.global_position = _sitio(x, 39)
		await _esperar(0.12)
	_comprobar(not vacio.cayendo and m.global_position.x > 71.0 * 16.0, "Maisha cruza el puente de cristal")
	m.global_position = _sitio(75, 42)
	_resonar(m)
	await _esperar(0.3)
	_comprobar(Estado.tiene("nucleo/sello_resonante"), "con la nota de verdad, el tercer sello despierta")
	await _esperar(0.4)
	_comprobar(Estado.tiene("nucleo/puerta_triple") and puerta.esta_abierta(), "con los tres ojos encendidos, la Puerta Triple se abre")
	_callar_todos()

	print("El Santuario: el Corazón del Meteorito:")
	var corazon := get_tree().get_first_node_in_group("corazones") as Node2D
	_comprobar(corazon != null and corazon.fase == corazon.Fase.DORMIDO and corazon.aro() == 0, "el Corazón flota, quieto, dentro de sus tres aros")
	m.global_position = Vector2(680, 340)
	await _esperar(0.6)
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(corazon.fase != corazon.Fase.DORMIDO and Sonido.musica_actual == "jefe_corazon", "al entrar, despierta (suena «El pulso de la estrella»)")
	_comprobar(not corazon.recibir_golpe(1, Vector2.UP) and corazon.vida == 12, "el cetro rebota en los aros")
	m.set("_invulnerable", 0.0)
	m.global_position = corazon.global_position + Vector2(60, 0)
	corazon.call("_cambiar", corazon.Fase.LATE)
	vida = m.vida
	await _esperar(1.3)
	_comprobar(m.vida == vida - 1, "el latido: la onda alcanza a quien esté en su borde (%d → %d)" % [vida, m.vida])
	m.set("_invulnerable", 900.0)
	_comprobar(corazon.fase == corazon.Fase.POSADO, "tras latir, se posa: el aro sísmico toca el suelo")
	await _cargar(m, corazon, Vector2(-26, 0))
	_comprobar(corazon.vida == 11, "una Carga lo agrieta (vida %d)" % corazon.vida)
	corazon.set("_inmune", 0.0)
	corazon.call("_cambiar", corazon.Fase.POSADO)
	await _cargar(m, corazon, Vector2(-26, 0))
	_comprobar(corazon.aro() == 1, "a la segunda, el aro sísmico se parte (aro %d)" % corazon.aro())
	for k in 2:
		m.global_position = corazon.global_position + Vector2(70, 40)
		corazon.set("_cd", 99.0)
		corazon.set("_frag", m.global_position)
		corazon.set("_devuelto", false)
		corazon.call("_cambiar", corazon.Fase.FRAGMENTO)
		await _esperar(0.6)
		_comprobar(_pulsar(m) and corazon.get("_devuelto"), "un Pulso con el fragmento de hierro ya cayendo se lo devuelve (%d)" % (k + 1))
		await _esperar(0.9)
	_comprobar(corazon.aro() == 2, "y el aro magnético se parte (aro %d)" % corazon.aro())
	var mono := _cerca("monolitos", 32, 20)
	for k in 2:
		corazon.set("_inmune", 0.0)
		corazon.call("_cambiar", corazon.Fase.FLOTA)
		corazon.set("_cd", 99.0)
		corazon.global_position = mono.global_position + Vector2(50, -10)
		m.global_position = mono.global_position + Vector2(0, 24)
		_callar_todos()
		_resonar(m)
		await _esperar(0.7)
	_comprobar(corazon.aro() == 3 and corazon.expuesto(), "la onda de un monolito que canta raja el aro de ámbar: el núcleo queda al aire")
	corazon.set("_cd", 99.0)
	await _esperar(0.6)
	_comprobar(corazon.altura < 16.0, "el núcleo baja hasta casi el suelo (%.0f)" % corazon.altura)
	for i in 6:
		await _esperar(0.15)
		corazon.recibir_golpe(1, Vector2.UP)
	_comprobar(corazon.fase == corazon.Fase.CALMADO and Estado.tiene("corazon_calmado"), "seis golpes de cetro y el Corazón se calma")
	await _esperar(2.4)
	await _leer_dialogo()
	await _esperar(0.3)
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(Estado.tiene("asterhaul_libre") and Estado.tiene("nexo_despierto"), "Mauti llega, se ve la semilla mayor y el Cetro del Nexo despierta del todo")
	_comprobar(Artes.aspecto()["cetro"] == "nexo_6" and m.get_node("Ropa").puestas().get("arma", "") == "nexo_6", "en la mano, el Cetro del Nexo despierto (%s)" % m.get_node("Ropa").puestas().get("arma", ""))
	await _leer_dialogo()
	await _esperar(0.5)
	var fin := get_tree().get_first_node_in_group("fin_mundo")
	_comprobar(fin != null and fin.abierto and fin.titulo == "Asterhaul late", "sale la pantalla del final: «Asterhaul late»")
	_comprobar(Misiones.estado(Misiones.buscar("nucleo_estrella")) == "hecha", "misión «Lo que cayó del cielo» cumplida")
	await _esperar(3.5)
	fin.cerrar()
	await _esperar(1.2)
	_comprobar(not get_tree().paused, "al cerrarla, se sigue jugando")

	print("Volver:")
	await _ir("nucleo_estrella", "pozo", "NucleoEstrella")
	var c2 := get_tree().get_first_node_in_group("corazones")
	_comprobar(c2 == null and get_tree().get_nodes_in_group("jefes").size() == 1, "al volver, el Corazón sigue en calma (no se pelea otra vez)")
	_comprobar(get_tree().get_first_node_in_group("puertas_triples").esta_abierta(), "y la Puerta Triple, abierta")
	await _ir("mji_jiwe", "nucleo", "MjiJiwe")
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.distance_to(_sitio(37, 33)) < 48.0, "de vuelta a Mji-Jiwe se sale por el pozo (%s)" % m.global_position)

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
