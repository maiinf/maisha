extends Node2D
## LA LUZ DEL JARDÍN DE LOS FAROLES (el Valle del Ocaso). Lo pone la escena. Sigue los RAYOS casilla a casilla desde
## cada fuente (`fuentes`: [casilla, dirección]; salen DORADOS) hasta que chocan con un seto («0») o con algo que
## los para. Lo que hay por el camino (grupo «opticas»: `ocupa(casilla)` y `desviar(dirección, color)` → los rayos
## que salen: [[dirección, color], ...]) decide: un espejo de ángulo lo dobla, un prisma lo parte en dorado y
## VIOLETA, la celosía y la verja lo paran o lo dejan pasar.
## Guarda por dónde pasa cada color (`casillas`: casilla → bits de color) y avisa (`cambiada`) para que se enteren
## las pasarelas y los espejos. Hay que llamar a `cambiar()` cuando algo gira o se tapa.

signal cambiada

const DORADO := 1
const VIOLETA := 2
const COLOR := {DORADO: Color(1.0, 0.82, 0.42), VIOLETA: Color(0.78, 0.5, 1.0)}
const PASOS := 160

var fuentes: Array = []                   # [[Vector2i casilla, Vector2i dirección], ...]
var casillas := {}                        # Vector2i → bits (DORADO | VIOLETA)
var segmentos: Array = []                 # [[desde px, hasta px, color], ...] (para dibujar)
var _filas: PackedStringArray
var _sucio := true
var _t := 0.0


func _ready() -> void:
	add_to_group("luz_jardin")
	z_index = 2
	_filas = get_parent().get_node("Region")._filas


func cambiar() -> void:
	_sucio = true


func tiene(c: Vector2i, color: int) -> bool:
	return int(casillas.get(c, 0)) & color != 0


func _seto(c: Vector2i) -> bool:
	return c.y < 0 or c.y >= _filas.size() or c.x < 0 or c.x >= _filas[c.y].length() or _filas[c.y][c.x] == "0"


func _process(delta: float) -> void:
	_t += delta
	if _sucio:
		_sucio = false
		_trazar()
		cambiada.emit()
	queue_redraw()


func _trazar() -> void:
	casillas.clear()
	segmentos.clear()
	var opticas := get_tree().get_nodes_in_group("opticas")
	for o in opticas:
		o.set("encendido", false)
	var pendientes: Array = []
	for f in fuentes:
		pendientes.append([f[0], f[1], DORADO])
	var vistos := {}
	while not pendientes.is_empty() and segmentos.size() < 40:
		var r: Array = pendientes.pop_front()
		var c: Vector2i = r[0]
		var d: Vector2i = r[1]
		var color: int = r[2]
		var clave := [c, d, color]
		if vistos.has(clave):
			continue
		vistos[clave] = true
		var desde := Vector2(c) * 16.0 + Vector2(8, 8)
		var hasta := desde
		for _i in PASOS:
			c += d
			if _seto(c):
				hasta = Vector2(c) * 16.0 + Vector2(8, 8) - Vector2(d) * 8.0
				break
			casillas[c] = int(casillas.get(c, 0)) | color
			hasta = Vector2(c) * 16.0 + Vector2(8, 8)
			var choca: Node = null
			for o in opticas:
				if o.ocupa(c):
					choca = o
					break
			if choca:
				choca.set("encendido", true)
				for s in choca.desviar(d, color):
					pendientes.append([c, s[0], s[1]])
				break
		segmentos.append([desde, hasta, color])


func _draw() -> void:
	var latido := 0.75 + sin(_t * 4.0) * 0.12
	for s in segmentos:
		var col: Color = COLOR[s[2]]
		var a: Vector2 = s[0] + Vector2(0, -8)          # (el rayo va a la altura de los espejos)
		var b: Vector2 = s[1] + Vector2(0, -8)
		draw_line(s[0], s[1], Color(col, 0.12), 10.0)          # (la luz en el suelo)
		draw_line(a, b, Color(col, 0.22 * latido), 9.0)
		draw_line(a, b, Color(col, 0.55 * latido), 4.0)
		draw_line(a, b, col.lerp(Color.WHITE, 0.6), 2.0)
