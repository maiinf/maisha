extends Node
## Prueba automática del Árbol de la Vida: Esencia, Artes, meditar y rasgos.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_artes

const R := preload("res://scripts/combate/reglas_combate.gd")
var _fallos := 0
var _ganada: Array = []


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 40:
		if not dialogo.hablando:
			return
		dialogo.pasar()
		await _esperar(0.1)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Artes.esencia_ganada.connect(func(n: int, _m: String) -> void: _ganada.append(n))
	Estado.olvidar_todo()

	print("La Esencia:")
	_comprobar(Artes.esencia() == 0, "al empezar no hay Esencia")
	for m in ["zona/kitovu/1", "zona/kitovu/4", "zona/kitovu/6"]:
		Estado.marcar(m)
	_comprobar(Artes.esencia() == 3 and _ganada == [1, 1, 1], "cada mancha del Kitovu da 1 (%d)" % Artes.esencia())
	Estado.marcar("zona/kitovu/7")
	_comprobar(Artes.esencia() == 6, "Mzizi da 3 (%d)" % Artes.esencia())
	Estado.marcar("zona/prados_del_eco/2")
	Estado.marcar("secreto/prados_del_eco/3,4")
	Estado.marcar("construido_casa_seta")
	_comprobar(Artes.esencia() == 9, "zona de los prados 1, secreto 1, casa 1 (%d)" % Artes.esencia())
	Estado.marcar("zona/prados_del_eco/3")
	_comprobar(Artes.esencia() == 10, "otra zona, 1 más (%d)" % Artes.esencia())
	Estado.marcar("kuku_devuelta")
	_comprobar(Artes.esencia() == 10, "otras marcas no dan Esencia")

	print("Subir Artes:")
	_comprobar(not Artes.puede_subir("runa"), "la Runa duerme hasta Sigilia")
	_comprobar(Artes.subir("raiz") and Artes.nivel("raiz") == 1 and Artes.esencia() == 9, "subir la Raíz al 1 cuesta 1")
	_comprobar(Artes.subir("raiz") and Artes.esencia() == 7, "al 2 cuesta 2")
	_comprobar(Artes.subir("raiz") and Artes.esencia() == 4, "al 3 cuesta 3")
	_comprobar(Artes.semilla_coste() == R.SEMILLA_COSTE - 3.0 and Artes.semilla_alcance() == R.SEMILLA_ALCANCE + 1, "la semilla cuesta menos y su cruz llega más lejos")
	_comprobar(Artes.tiene_rasgo("brote"), "Raíz 3: a Maisha le sale el brote")
	_comprobar(Artes.esencia() == 4, "quedan 4 de Esencia")
	_comprobar(Artes.subir("aliento") and Artes.subir("aliento") and Artes.esencia() == 1, "dos niveles de Aliento (1 + 2)")
	_comprobar(not Artes.subir("raiz"), "al 4 hace falta más Esencia (cuesta 4, hay %d)" % Artes.esencia())
	_comprobar(Artes.aliento_maximo() == R.ALIENTO_MAXIMO + 10.0 and is_equal_approx(Artes.ritmo_aliento(), 1.15), "más Aliento y respira más rápido")
	Estado.guardar()
	Estado.cargar()
	_comprobar(Artes.nivel("raiz") == 3 and Artes.nivel("aliento") == 2 and Artes.esencia() == 1, "los niveles se guardan con la partida")

	print("Meditar en el Claro de Calma:")
	for m in ["cetro_recibido", "visto/prados_del_eco", "visto/cuna_de_musgo", "bibi_conocida", "zona/prados_del_eco/4", "zona/prados_del_eco/5", "secreto/prados_del_eco/8,9"]:
		Estado.marcar(m)
	Estado.jugando = true
	get_tree().change_scene_to_file("res://escenas/interiores/claro_de_calma.tscn")
	await _esperar(1.5)
	var maisha := get_tree().get_first_node_in_group("maisha")
	var brote := get_tree().get_first_node_in_group("brote_vida")
	_comprobar(maisha.get_node_or_null("Rasgos") != null, "Maisha lleva sus rasgos")
	brote.interactuar()
	await _esperar(0.3)
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(get_tree().get_first_node_in_group("arbol_vida") == null and not Estado.tiene("meditado"), "sin que Bibi enseñe, el brote solo se mira")
	Estado.marcar("bibi_meditar")
	maisha.vida = 3
	brote.interactuar()
	await _esperar(0.3)
	await _leer_dialogo()
	await _esperar(0.5)
	var arbol := get_tree().get_first_node_in_group("arbol_vida")
	_comprobar(arbol != null and arbol.abierto and get_tree().paused, "al meditar se abre el Árbol de la Vida y el juego se para")
	_comprobar(maisha.vida == maisha.vida_maxima() and Estado.tiene("meditado"), "meditar cura a Maisha (%d)" % maisha.vida)
	var esencia := Artes.esencia()
	arbol._elegir(2)       # Aliento
	Input.action_press("accion")
	await _esperar(0.2)
	Input.action_release("accion")
	await _esperar(0.1)
	_comprobar(Artes.nivel("aliento") == 2, "pulsar Acción un momento no gasta Esencia (hay que mantener)")
	Input.action_press("accion")
	await _esperar(1.0)
	Input.action_release("accion")
	await _esperar(0.1)
	_comprobar(Artes.nivel("aliento") == 3 and Artes.esencia() == esencia - 3, "mantener Acción despierta el nivel 3 del Aliento")
	_comprobar(maisha.vida_maxima() == R.VIDA_MAXIMA + 1 and maisha.vida == maisha.vida_maxima(), "una hoja más de Vida (%d)" % maisha.vida_maxima())
	_comprobar(Artes.tiene_rasgo("aura"), "y el aura")
	var tab := InputEventAction.new()
	tab.action = "mochila"
	tab.pressed = true
	Input.parse_input_event(tab)
	await get_tree().process_frame
	await get_tree().process_frame
	tab = InputEventAction.new()
	tab.action = "mochila"
	tab.pressed = false
	Input.parse_input_event(tab)
	await _esperar(0.6)
	_comprobar(not arbol.abierto and not get_tree().paused and maisha.puede_actuar, "Tab deja de meditar y se puede seguir jugando (%s %s %s)" % [arbol.abierto, get_tree().paused, maisha.puede_actuar])
	_comprobar(Misiones.estado(Misiones.buscar("arbol_vida")) == "hecha", "misión «El Árbol de la Vida» cumplida")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
