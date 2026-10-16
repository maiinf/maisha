extends Node
## Prueba automática del sonido: que todo exista y que cada cosa suene cuando toca.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_sonido
## (sin altavoces no se oye nada, pero el autoload «Sonido» cuenta lo que manda sonar)

const R := preload("res://scripts/combate/reglas_combate.gd")
const MUSICAS := ["despertar", "kitovu", "inicio", "prados", "aldea", "interior", "combate", "jefe", "purga", "victoria", "objeto", "tarea", "recuerdo", "noche", "amanece"]
const AMBIENTES := ["brisa", "viento", "fuego", "agua", "pajaros"]
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


func _esperar_cambio(nombre: String) -> void:
	for i in 1500:
		if _escena() == nombre and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(0.3)


func _veces(clave: String) -> int:
	return int(Sonido.conteo.get(clave, 0))


func _pulsar(accion: String) -> void:
	await get_tree().process_frame
	Input.action_press(accion)
	await get_tree().process_frame
	await get_tree().process_frame
	Input.action_release(accion)
	await get_tree().process_frame


func _ready() -> void:
	Engine.time_scale = 2.0
	Estado.olvidar_todo()
	Estado.borrar_partida()

	print("Los archivos:")
	var faltan: Array[String] = []
	for m in MUSICAS:
		if not ResourceLoader.exists("res://audio/musica/%s.ogg" % m):
			faltan.append(m)
	for a in AMBIENTES:
		if not ResourceLoader.exists("res://audio/ambiente/%s.ogg" % a):
			faltan.append(a)
	for e in Sonido.VOLUMEN:
		if not ResourceLoader.exists("res://audio/sonidos/%s.ogg" % e):
			faltan.append(e)
	_comprobar(faltan.is_empty(), "están las %d músicas, los %d ambientes y los %d efectos %s" % [MUSICAS.size(), AMBIENTES.size(), Sonido.VOLUMEN.size(), faltan])
	var kitovu: AudioStream = load("res://audio/musica/kitovu.ogg")
	_comprobar(kitovu.get_length() > 50.0, "la música del Kitovu dura más de un minuto (%.0f s)" % kitovu.get_length())
	_comprobar(AudioServer.get_bus_index("Musica") >= 0 and AudioServer.get_bus_index("Efectos") >= 0 and AudioServer.get_bus_index("Ambiente") >= 0, "hay buses de música, efectos y ambiente")

	print("Pantalla de inicio y partida nueva:")
	get_tree().change_scene_to_file("res://escenas/interfaz/inicio.tscn")
	await _esperar_cambio("Inicio")
	_comprobar(Sonido.musica_actual == "inicio", "en el inicio suena el tema de Maisha")
	var inicio := get_tree().current_scene
	inicio._al_elegir(inicio._acciones.find("nueva"))
	await _esperar(0.3)
	_comprobar(Sonido.musica_actual == "despertar" and Sonido._siguiente == "kitovu", "al empezar, la música del despertar (y después la del Kitovu)")
	await _esperar_cambio("Kitovu")
	_comprobar(Sonido.musica_actual == "despertar", "al despertar en el Kitovu sigue sonando el despertar")
	_comprobar(Sonido._ambientes.has("brisa") and Sonido._ambientes.has("viento") and not Sonido._ambientes.has("pajaros_pocos"), "con brisa y viento de fondo (sin pájaros)")

	print("Diálogos:")
	await _esperar(3.0)
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	_comprobar(dialogo.hablando, "Maisha piensa al despertar")
	var antes := _veces("dialogo_pasar")
	for i in 40:
		if not dialogo.hablando:
			break
		await _pulsar("accion")
		await _pulsar("accion")
	_comprobar(_veces("dialogo_pasar") > antes, "cada vez que se sigue leyendo suena el «bip» (%d)" % (_veces("dialogo_pasar") - antes))
	_comprobar(_veces("dialogo_cerrar") >= 1, "y otro al cerrar el diálogo")

	print("Cuando acaba el despertar:")
	Sonido._musica[Sonido._activa].finished.emit()
	await _esperar(0.2)
	_comprobar(Sonido.musica_actual == "kitovu", "empieza la música del Kitovu")
	var maisha: Node2D = get_tree().get_first_node_in_group("maisha")
	maisha.global_position = get_tree().current_scene.GRANJA
	await _esperar(0.5)
	var cerca: float = Sonido._objetivo_ambiente.get("brisa", 0.0)
	maisha.global_position = Vector2(40, 700)
	await _esperar(0.5)
	var lejos: float = Sonido._objetivo_ambiente.get("brisa", 0.0)
	_comprobar(cerca > lejos, "la brisa en la hierba se oye más cerca de la granja (%.2f > %.2f)" % [cerca, lejos])
	# el Kitovu no suena sin parar: al acabar, un rato de silencio y vuelve
	Sonido._musica[Sonido._activa].finished.emit()
	await _esperar(0.1)
	_comprobar(_veces("silencio:kitovu") == 1 and Sonido.musica_actual == "kitovu", "al acabar la música del Kitovu hay un rato de silencio (y luego vuelve)")

	print("El agua:")
	var sitio: Node2D = get_tree().get_nodes_in_group("sitios_pesca")[0]
	maisha.global_position = sitio.global_position + Vector2(8, 6)
	await _esperar(0.5)
	var junto: float = Sonido._objetivo_ambiente.get("agua", 0.0)
	maisha.global_position = get_tree().current_scene.GRANJA + Vector2(120, 0)
	await _esperar(0.5)
	var lejos_agua: float = Sonido._objetivo_ambiente.get("agua", 0.0)
	_comprobar(junto > 0.3 and lejos_agua < junto * 0.5, "junto al estanque se oye correr el agua; lejos, no (%.2f / %.2f)" % [junto, lejos_agua])

	print("Las tareas suenan distinto:")
	Estado.marcar("tarea_pesca")
	Estado.marcar("tarea_cosecha")
	maisha.global_position = sitio.global_position + Vector2(8, 6)
	sitio.empezar()
	await _esperar(0.2)
	_comprobar(_veces("pesca_lanzar") == 1, "al lanzar la caña: el sedal y el corcho que cae al agua")
	for i in 200:
		if sitio.fase == 2:
			break
		await get_tree().process_frame
	_comprobar(_veces("pesca_pica") == 1, "cuando pica: el tirón")
	sitio.marca_en_verde()
	await _pulsar("accion")
	await _esperar(0.3)
	_comprobar(_veces("pesca_saca") == 1, "al sacarlo: chapoteo y una notita")
	await _esperar(1.2)
	get_tree().get_nodes_in_group("zanahorias")[0].arrancar()
	_comprobar(_veces("zanahoria_arrancar") == 1 and _veces("recoger") == 0, "arrancar una zanahoria suena a tierra y raíces (no como coger otra cosa)")
	var dialogo2 := get_tree().get_first_node_in_group("dialogo")
	while dialogo2.hablando:
		await _pulsar("accion")

	print("Mochila y pausa:")
	var libro_antes := _veces("libro_abrir")       # (el diario del inicio ya sonó al abrirse)
	await _pulsar("mochila")
	_comprobar(_veces("libro_abrir") == libro_antes + 1, "el diario suena al abrirse (cuero y hojas)")
	await _pulsar("mochila")
	await _esperar(0.1)
	await _pulsar("menu")
	var pausa := get_tree().get_first_node_in_group("pausa")
	_comprobar(pausa.abierto and _veces("pausa") == 1, "la pausa también")
	var nivel: int = Sonido.niveles["Musica"]
	pausa._al_ajustar(pausa._acciones.find("musica"), -1)
	_comprobar(Sonido.niveles["Musica"] == nivel - 1, "en la pausa se baja la música (%d → %d)" % [nivel, Sonido.niveles["Musica"]])
	pausa._al_ajustar(pausa._acciones.find("musica"), 1)
	_comprobar(Sonido.niveles["Musica"] == nivel, "y se vuelve a subir")
	var cfg := ConfigFile.new()
	_comprobar(cfg.load("user://ajustes.cfg") == OK and int(cfg.get_value("sonido", "Musica", -1)) == nivel, "el nivel se guarda")
	await _pulsar("menu")

	print("Una mancha de Giza:")
	Estado.marcar("cetro_recibido")
	for m in ["narr/zona", "narr/cerrada", "narr/nucleo", "narr/cetro"]:
		Estado.marcar(m)
	await _esperar(0.3)
	var zona: Node2D = get_tree().get_nodes_in_group("zonas").filter(func(z: Node2D) -> bool: return z.jefe == "")[0]
	var p: Vector2 = zona.global_position
	while zona.distancia_normal(p) < 0.8:
		p.y += 2.0
	maisha.global_position = p + Vector2(0, 40)
	await _esperar(0.3)
	_comprobar(_veces("zona_aviso") >= 1, "al pisar el borde suena el aviso")
	maisha.global_position = p
	await _esperar(0.5)
	while dialogo.hablando:
		await _pulsar("accion")
	_comprobar(zona.estado == 2 and Sonido.musica_actual == "combate" and _veces("espinas_suben") >= 1, "al cerrarse: las raíces-espina y la música de pelea")
	_comprobar(_veces("petrino_aparece") >= 1, "los Petrinos suenan al brotar (%d)" % _veces("petrino_aparece"))
	maisha.golpear()
	await _esperar(0.3)
	_comprobar(_veces("cetro_golpe") >= 1, "el golpe del cetro corta el aire")
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.call("morir")
	await _esperar(0.2)
	_comprobar(_veces("petrino_muere") >= 1, "y se desmoronan con ruido de piedra")
	var nucleo: Node2D = zona.get("_nucleo")
	zona.set("_invocar", 999.0)
	for i in nucleo.vida_maxima:
		nucleo.recibir_danio(3, nucleo.global_position, "explosion")
	await _esperar(4.0)
	while dialogo.hablando:
		await _pulsar("accion")
	_comprobar(_veces("corazon_roto") == 1 and _veces("fanfarria:purga") == 1, "al romper el Corazón: estallido y la fanfarria de la purga")
	_comprobar(Sonido.musica_actual == "kitovu", "y vuelve la música del Kitovu")

	print("Mzizi:")
	var arena: Node2D = get_tree().get_first_node_in_group("arena_jefe")
	var mzizi: Node2D = null
	await _esperar(0.5)
	for j in get_tree().get_nodes_in_group("jefes"):
		mzizi = j
	Estado.marcar("narr/arena")
	Estado.marcar("narr/mzizi")
	arena.activa = true
	var q: Vector2 = arena.global_position
	while arena.distancia_normal(q) < 0.8:
		q.y += 2.0
	maisha.global_position = q
	await _esperar(0.6)
	_comprobar(Sonido.musica_actual == "jefe" and _veces("mzizi_rugido") == 1, "sale rugiendo y suena la música del jefe")
	mzizi.recibir_golpe(1, Vector2.UP)
	_comprobar(_veces("clinc") >= 1, "el cetro hace «clinc» en su piedra")

	print("Los Prados del Eco:")
	Estado.llegada = "kitovu"
	get_tree().change_scene_to_file("res://escenas/mundo/prados_del_eco.tscn")
	await _esperar_cambio("PradosDelEco")
	await _esperar(0.5)
	_comprobar(Sonido.musica_actual == "prados" and Sonido._objetivo_ambiente.has("brisa") and Sonido._objetivo_ambiente.has("agua"), "música de los prados, brisa y el río")

	print("Pasos según el terreno:")
	var maisha_prados: CharacterBody2D = get_tree().get_first_node_in_group("maisha")
	if maisha_prados:
		var pasos_antes := _veces("paso_hierba") + _veces("paso_piedra") + _veces("paso_tierra")
		maisha_prados.velocity = Vector2.RIGHT * 70.0
		maisha_prados._actualizar_animacion(Vector2.RIGHT)
		maisha_prados._sprite.frame = 0
		maisha_prados._al_cambiar_fotograma()
		var pasos_despues := _veces("paso_hierba") + _veces("paso_piedra") + _veces("paso_tierra")
		_comprobar(pasos_despues > pasos_antes, "al andar suena el paso correspondiente al terreno")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	await Sonido.callar()
	get_tree().quit(_fallos)
