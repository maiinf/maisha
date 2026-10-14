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

	print("El árbol de habilidades del diario (rama Cetro, Cristales en los nodos grandes):")
	_comprobar(Artes.cristales_gastados() == 4, "los nodos grandes Raíz III y Aliento III gastaron 2 + 2 Cristales (%d)" % Artes.cristales_gastados())
	var cristales := Tienda.cristales()
	for m in ["zona/prados_del_eco/4", "zona/prados_del_eco/5", "zona/prados_del_eco/6", "secreto/prados_del_eco/1,1", "secreto/prados_del_eco/2,2", "secreto/prados_del_eco/5,5"]:
		Estado.marcar(m)
	_comprobar(Artes.subir("cetro") and Artes.golpe_alcance() == R.GOLPE_ALCANCE + 4.0, "Cetro I: el golpe llega más lejos")
	_comprobar(Artes.subir("cetro") and Artes.golpe_angulo() == R.GOLPE_ANGULO + 20.0, "Cetro II: barre más ancho")
	_comprobar(Artes.cristales_siguiente("cetro") == 2 and Artes.es_grande("cetro", 3), "Cetro III es un nodo grande: pide 2 Cristales")
	if Tienda.cristales() >= 2 and Artes.esencia() >= 3:
		_comprobar(Artes.subir("cetro") and Artes.golpe_danio() == R.GOLPE_DANIO + 1 and Tienda.cristales() == cristales - 2, "Cetro III: pega más fuerte y se gastan los Cristales")
	else:
		_comprobar(not Artes.puede_subir("cetro"), "sin Cristales o Esencia, Cetro III no se puede despertar")
	Estado.extra["cristales_gastados"] = 999
	_comprobar(Tienda.cristales() == 0 and Artes.nivel("cetro") >= 2, "sin Cristales…")
	var antes := Artes.nivel("cetro")
	if Artes.cristales_siguiente("cetro") > 0:
		_comprobar(not Artes.subir("cetro") and Artes.nivel("cetro") == antes, "…un nodo grande no se despierta")
	Estado.extra["cristales_gastados"] = 0

	print("Lo que se le ve a Maisha (las Artes visuales):")
	var asp := Artes.aspecto({"raiz": 5, "cetro": 3, "aliento": 2})
	_comprobar(asp["prendas"] == ["brazaletes_hoja", "corona_hojas", "capa_musgo", "bufanda_viento"], "Raíz 5 y Aliento 2: brazaletes con hoja, corona, capa y bufanda larga (%s)" % [asp["prendas"]])
	_comprobar(asp["cetro"] == "cetro_3" and "brote" in asp["rasgos"], "Cetro 3: el cetro de roble; Raíz 3+: el brote")
	asp = Artes.aspecto({"raiz": 0, "cetro": 0, "aliento": 6})
	_comprobar(asp["cetro"] == "cetro_raiz" and asp["rasgos"] == ["aura", "motas", "brillo", "brisa"], "Aliento 6: aura, motas, destellos y cuerpo de brisa (%s)" % [asp["rasgos"]])
	var ropa := maisha.get_node("Ropa")
	var puestas: Dictionary = ropa.puestas()
	_comprobar(puestas.get("arma", "") == "cetro_%d" % Artes.nivel("cetro"), "en la mano, el cetro de su nivel (%s)" % puestas.get("arma", ""))
	_comprobar(puestas.get("torso", "") == "bufanda_viento", "y la bufanda de viento del Aliento 3 (%s)" % puestas.get("torso", ""))
	var niveles: Dictionary = Estado.extra.get("artes", {}).duplicate()
	niveles["raiz"] = 4
	Estado.extra["artes"] = niveles
	Artes.arte_subida.emit("raiz", 4)
	_comprobar(ropa.puestas().get("cabeza", "") == "corona_hojas", "Raíz 4: la corona de hojas")
	var compradas: Dictionary = Estado.extra.get("comprado", {}).duplicate()
	compradas["sombrero_paja"] = 1
	Estado.extra["comprado"] = compradas
	Tienda.poner_prenda("sombrero_paja", true)
	_comprobar(ropa.puestas().get("cabeza", "") == "sombrero_paja", "lo que se pone desde la mochila manda en su zona")
	Tienda.poner_prenda("sombrero_paja", false)
	_comprobar(ropa.puestas().get("cabeza", "") == "corona_hojas", "y al quitárselo vuelve la corona de la Raíz")
	var golpe: Node2D = load("res://scripts/combate/golpe_efecto.gd").new()
	golpe.cetro = "cetro_6"
	maisha.add_child(golpe)
	_comprobar(golpe.get("_textura") != null, "el golpe gira el cetro que se lleva (también el del Primer Árbol)")
	var diario := get_tree().get_first_node_in_group("mochila")
	diario.abrir(diario.P_HABILIDADES)
	await _esperar(0.6)
	diario.set("_rama", 0)
	diario.set("_nodo", 6)
	await _esperar(0.2)
	var muneco_ropa: Node = diario.get("_muneco_ropa")
	_comprobar(diario.get("_muneco").visible and muneco_ropa.puestas().get("espalda", "") == "capa_musgo", "en Habilidades, sobre Raíz VI, Maisha en grande se ve con la capa de musgo")
	_comprobar("flores" in Artes.aspecto(diario.get("_muneco_rasgos").get("niveles"))["rasgos"], "y con las flores")
	diario.set("_ver_antes", true)
	await _esperar(0.2)
	_comprobar(not muneco_ropa.puestas().has("espalda"), "con F se ve otra vez cómo es ahora (sin capa)")
	diario.cerrar()
	await _esperar(0.5)
	_comprobar(not diario.get("_muneco").visible, "al cerrar el diario, Maisha en grande desaparece")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
