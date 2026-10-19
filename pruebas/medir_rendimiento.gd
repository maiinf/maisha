extends Node
## (no es una prueba) MIDE EL RENDIMIENTO de los mapas: carga cada escena, espera a que se asiente y mide
## unos segundos sin vsync. Se lanza SIN --headless (hace falta la tarjeta gráfica):
##   godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento
##   godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento hd2d          (con el espejo HD-2D)
##   godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento noche prados_del_eco bosque_cobrizo
##   godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento pelea          (Maisha en una zona cerrada, con
##                                                                                  enemigos y golpeando)
## Saca una tabla: lo que tarda en cargar (instanciar el mapa y sus 3 primeros fotogramas), ms por fotograma (media y el 1 % peor), ms de los scripts (_process y _physics_process de todos
## los nodos, medidos entre un nodo que va el primero y otro que va el último), ms de _draw (de ahí a que empieza a
## pintar: los _draw de lo que pidió queue_redraw y las llamadas diferidas), llamadas de dibujo, objetos y nodos.
## (En macOS, si la ventana está tapada, no se pinta y va frenada a ~145 FPS; por eso se pone siempre delante.
## Con --headless pasa lo mismo: allí solo valen «carga ms», «scripts ms» y «física ms».)

const ESCENAS := ["prados_del_eco", "cuna_de_musgo", "bosque_cobrizo", "la_travesia", "cienaga_quieta",
	"maandiko", "sendero_olvidado", "lago_espejo"]
const ASENTAR := 2.0                    # segundos antes de medir
const MEDIR := 4.0                      # segundos midiendo
const ENEMIGOS_PELEA := 8               # en el modo «pelea», los enemigos que se juntan en la zona
const MODOS := ["hd2d", "noche", "pelea"]

## Un cronómetro: «primero» apunta la hora antes de los demás nodos y «ultimo» suma lo que ha pasado
class Cronometro extends Node:
	var otro: Cronometro
	var empieza := 0
	var total := 0
	var fisica := false
	var termina := 0                    # (el último) cuándo acabó el _process de todos
	var dibujos := 0                    # (el último) de ahí a que empieza a pintar: los _draw y lo diferido
	func _process(_d: float) -> void:
		if not fisica:
			_tic()
	func _physics_process(_d: float) -> void:
		if fisica:
			_tic()
	func _tic() -> void:
		if otro:
			termina = Time.get_ticks_usec()
			total += termina - otro.empieza
		else:
			empieza = Time.get_ticks_usec()


func _cronometro(fisica: bool) -> Array:
	var a := Cronometro.new()
	var b := Cronometro.new()
	b.otro = a
	for c: Cronometro in [a, b]:
		c.fisica = fisica
		c.process_mode = Node.PROCESS_MODE_ALWAYS
		get_tree().root.add_child(c)
	a.process_priority = -1000000
	b.process_priority = 1000000
	a.process_physics_priority = -1000000
	b.process_physics_priority = 1000000
	if not fisica:
		RenderingServer.frame_pre_draw.connect(func() -> void:
			if b.termina > 0:
				b.dibujos += Time.get_ticks_usec() - b.termina
				b.termina = 0)
	return [a, b]


func _ready() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	# (en macOS, una ventana tapada deja de pintarse y va frenada: siempre delante mientras mide)
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_ALWAYS_ON_TOP, true)
	DisplayServer.window_move_to_foreground()
	var args := OS.get_cmdline_user_args().slice(1)
	var hd2d := "hd2d" in args
	var noche := "noche" in args
	var pelea := "pelea" in args
	var escenas: Array = []
	for a in args:
		if a not in MODOS:
			escenas.append(a)
	if escenas.is_empty():
		escenas = ESCENAS
	Estado.marcar("cetro_recibido")
	Estado.extra["hd2d"] = hd2d
	if noche:
		Estado.marcar(Reloj.MARCA_INICIO)      # (sin esto el reloj se queda de día)
	print("\nRENDIMIENTO (%s%s%s) · %s" % ["HD-2D" if hd2d else "2D", ", de noche" if noche else "",
		", en pelea" if pelea else "", RenderingServer.get_video_adapter_name()])
	print("| Escena | carga ms | ms/fotograma | 1 % peor | FPS | scripts ms | _draw ms | física ms | dibujo | objetos | nodos |")
	print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
	var crono := _cronometro(false)
	var crono_f := _cronometro(true)
	for id in escenas:
		var carga := Time.get_ticks_usec()
		var escena: Node = load("res://escenas/mundo/%s.tscn" % id).instantiate()
		get_tree().root.add_child(escena)
		for i in 3:
			await get_tree().process_frame
		carga = Time.get_ticks_usec() - carga
		var zona: Node2D = null
		if pelea:
			zona = await _empezar_pelea(escena)
			if zona == null:
				print("| %s | (no tiene zonas sin jefe) |" % id)
				escena.queue_free()
				await get_tree().process_frame
				continue
		var t0 := Time.get_ticks_msec()
		while Time.get_ticks_msec() - t0 < ASENTAR * 1000.0:
			if noche:
				Reloj.poner_hora(0.82)
			if zona:
				_seguir_pelea(escena, zona)
			await get_tree().process_frame
		var tiempos: Array[float] = []
		var dibujo := 0
		var objetos := 0
		crono[1].total = 0
		crono[1].dibujos = 0
		crono_f[1].total = 0
		var antes := Time.get_ticks_usec()
		var inicio := antes
		while Time.get_ticks_usec() - inicio < MEDIR * 1e6:
			if zona:
				_seguir_pelea(escena, zona)
			await get_tree().process_frame
			var ahora := Time.get_ticks_usec()
			tiempos.append((ahora - antes) / 1000.0)
			antes = ahora
			dibujo += int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME))
			objetos += int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME))
		var n := tiempos.size()
		var media: float = tiempos.reduce(func(a: float, b: float) -> float: return a + b, 0.0) / n
		tiempos.sort()
		var peor: Array = tiempos.slice(int(n * 0.99))
		var p1: float = peor.reduce(func(a: float, b: float) -> float: return a + b, 0.0) / maxi(peor.size(), 1)
		var nombre: String = id
		if pelea:
			Input.action_release("golpe")
			nombre = "%s (zona %s, %d enemigos)" % [id, ["dormida", "aviso", "cerrada", "purgando", "purgada"][int(zona.get("estado"))],
				get_tree().get_nodes_in_group("enemigos").size()]
		print("| %s | %d | %.2f | %.2f | %d | %.2f | %.2f | %.2f | %d | %d | %d |" % [nombre, carga / 1000, media, p1, roundi(1000.0 / media),
			crono[1].total / 1000.0 / n, crono[1].dibujos / 1000.0 / n, crono_f[1].total / 1000.0 / n, dibujo / n, objetos / n, int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT))])
		escena.queue_free()
		var espejo := get_tree().root.get_node_or_null("EspejoHD2D")
		if espejo:
			espejo.queue_free()
		await get_tree().process_frame
		await get_tree().process_frame
	get_tree().quit(0)


## Modo «pelea»: Maisha cruza el umbral de la primera zona sin jefe, que se cierra; se juntan ENEMIGOS_PELEA enemigos
func _empezar_pelea(escena: Node) -> Node2D:
	var zona: Node2D = null
	for z in get_tree().get_nodes_in_group("zonas"):
		if escena.is_ancestor_of(z) and String(z.get("jefe")) == "" and not z.get("ya_purgada"):
			zona = z
			break
	if zona == null:
		return null
	var maisha: Node2D = escena.get_node("Entidades/Maisha")
	maisha.global_position = zona.global_position + Vector2(-zona.radios_umbral.x - zona.ancho_borde * 0.5, 0)
	for i in 10:
		await get_tree().process_frame
	maisha.global_position = zona.global_position + Vector2(-zona.radios_umbral.x * 0.6, 0)
	for i in 10:
		await get_tree().process_frame
	for i in ENEMIGOS_PELEA:
		zona.call("_invocar_petrino", false)
	return zona


## Que Maisha no caiga y que vaya golpeando (golpes, chispas, enemigos que reciben daño)
func _seguir_pelea(escena: Node, zona: Node2D) -> void:
	var maisha: Node2D = escena.get_node("Entidades/Maisha")
	maisha.set("_invulnerable", 999.0)
	maisha.set("vida", 99)
	zona.set("_invocar", 999.0)
	if Engine.get_process_frames() % 20 == 0:
		Input.action_press("golpe")
	elif Engine.get_process_frames() % 20 == 2:
		Input.action_release("golpe")
