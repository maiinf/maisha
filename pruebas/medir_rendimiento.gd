extends Node
## (no es una prueba) MIDE EL RENDIMIENTO de los mapas: carga cada escena, espera a que se asiente y mide
## unos segundos sin vsync. Se lanza SIN --headless (hace falta la tarjeta gráfica):
##   godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento
##   godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento hd2d          (con el espejo HD-2D)
##   godot --path . res://pruebas/ejecutar.tscn -- medir_rendimiento noche prados_del_eco bosque_cobrizo
## Saca una tabla: ms por fotograma (media y el 1 % peor), ms de los scripts (_process y _physics_process de todos
## los nodos, medidos entre un nodo que va el primero y otro que va el último), llamadas de dibujo, objetos y nodos.
## (En macOS, si la ventana no está delante, el sistema la frena a ~145 FPS: los ms de los scripts siguen valiendo.)

const ESCENAS := ["prados_del_eco", "cuna_de_musgo", "bosque_cobrizo", "la_travesia", "cienaga_quieta",
	"maandiko", "sendero_olvidado", "lago_espejo"]
const ASENTAR := 2.0                    # segundos antes de medir
const MEDIR := 4.0                      # segundos midiendo

## Un cronómetro: «primero» apunta la hora antes de los demás nodos y «ultimo» suma lo que ha pasado
class Cronometro extends Node:
	var otro: Cronometro
	var empieza := 0
	var total := 0
	var fisica := false
	func _process(_d: float) -> void:
		if not fisica:
			_tic()
	func _physics_process(_d: float) -> void:
		if fisica:
			_tic()
	func _tic() -> void:
		if otro:
			total += Time.get_ticks_usec() - otro.empieza
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
	return [a, b]


func _ready() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	var args := OS.get_cmdline_user_args().slice(1)
	var hd2d := "hd2d" in args
	var noche := "noche" in args
	var escenas: Array = []
	for a in args:
		if a not in ["hd2d", "noche"]:
			escenas.append(a)
	if escenas.is_empty():
		escenas = ESCENAS
	Estado.marcar("cetro_recibido")
	Estado.extra["hd2d"] = hd2d
	if noche:
		Estado.marcar(Reloj.MARCA_INICIO)      # (sin esto el reloj se queda de día)
	print("\nRENDIMIENTO (%s%s) · %s" % ["HD-2D" if hd2d else "2D", ", de noche" if noche else "",
		RenderingServer.get_video_adapter_name()])
	print("| Escena | ms/fotograma | 1 %% peor | FPS | scripts ms | física ms | dibujo | objetos | nodos |")
	print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
	var crono := _cronometro(false)
	var crono_f := _cronometro(true)
	for id in escenas:
		var escena: Node = load("res://escenas/mundo/%s.tscn" % id).instantiate()
		get_tree().root.add_child(escena)
		var t0 := Time.get_ticks_msec()
		while Time.get_ticks_msec() - t0 < ASENTAR * 1000.0:
			if noche:
				Reloj.poner_hora(0.82)
			await get_tree().process_frame
		var tiempos: Array[float] = []
		var dibujo := 0
		var objetos := 0
		crono[1].total = 0
		crono_f[1].total = 0
		var antes := Time.get_ticks_usec()
		var inicio := antes
		while Time.get_ticks_usec() - inicio < MEDIR * 1e6:
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
		print("| %s | %.2f | %.2f | %d | %.2f | %.2f | %d | %d | %d |" % [id, media, p1, roundi(1000.0 / media),
			crono[1].total / 1000.0 / n, crono_f[1].total / 1000.0 / n, dibujo / n, objetos / n, int(Performance.get_monitor(Performance.OBJECT_NODE_COUNT))])
		escena.queue_free()
		var espejo := get_tree().root.get_node_or_null("EspejoHD2D")
		if espejo:
			espejo.queue_free()
		await get_tree().process_frame
		await get_tree().process_frame
	get_tree().quit(0)
