extends Node2D
## DECORADO DEL SUELO: hierba alta que se mece, flores, helechos, setas, piedrecitas, ramas,
## tréboles, tocones y arbustos repartidos por la hierba. No estorban al andar.
## Se colocan siempre igual en cada mapa (salen de la posición de cada casilla) y solo se dibuja
## lo que se ve en pantalla. Las piezas están en arte/mundos/raiz/objetos/decorado.png
## (las dibuja herramientas/dibujar_decorado.py).

const TEXTURA := preload("res://arte/mundos/raiz/objetos/decorado.png")
const TAM := 16
## pieza: [primer fotograma, fotogramas, peso en la hierba, peso en las casillas con flores]
const PIEZAS := [
	[0, 2, 34, 10],   # hierba alta (se mece)
	[2, 1, 6, 20],    # flores amarillas
	[3, 1, 5, 18],    # flores rojas
	[4, 1, 5, 18],    # flores blancas
	[5, 1, 8, 2],     # helecho
	[6, 1, 4, 2],     # arbusto con bayas
	[7, 1, 2, 0],     # tocón
	[8, 1, 4, 3],     # setas
	[9, 1, 10, 2],    # piedrecitas
	[10, 1, 12, 8],   # trébol
	[11, 1, 4, 0],    # rama caída
]

var densidad := 0.22
var _piezas: Array[Dictionary] = []
var _barandillas: Array[Rect2] = []          # los bordes de los puentes (tablas de madera)
var _tiempo := 0.0
var _redibujar := 0.0


## filas: el mapa en texto; prohibidas: casillas donde no poner nada (zonas, caminos...)
func preparar(filas: PackedStringArray, prohibidas: Dictionary) -> void:
	z_index = -9
	for y in filas.size():
		var fila := filas[y]
		for x in fila.length():
			var c := fila[x]
			if c == "=":
				# barandilla arriba y abajo del puente (si por ahí corre el agua)
				if y > 0 and filas[y - 1][x] == "~":
					_barandillas.append(Rect2(Vector2(x, y) * TAM, Vector2(TAM, 3)))
				if y + 1 < filas.size() and filas[y + 1][x] == "~":
					_barandillas.append(Rect2(Vector2(x, y + 1) * TAM - Vector2(0, 3), Vector2(TAM, 3)))
				continue
			if c != "." and c != ",":
				continue
			if prohibidas.has(Vector2i(x, y)):
				continue
			# que no toque caminos, agua ni objetos de las casillas de al lado
			var libre := true
			for v in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
				var yy: int = y + v.y
				var xx: int = x + v.x
				if yy >= 0 and yy < filas.size() and xx >= 0 and xx < filas[yy].length():
					if not filas[yy][xx] in [".", ","]:
						libre = false
			var azar := _azar_de(x, y)
			if not libre or azar > densidad * (1.6 if c == "," else 1.0):
				continue
			var flores := c == ","
			var total := 0
			for p in PIEZAS:
				total += p[3] if flores else p[2]
			var tirada := int(_azar_de(y * 7 + 3, x * 13 + 1) * total)
			for p in PIEZAS:
				tirada -= p[3] if flores else p[2]
				if tirada < 0:
					var pos := Vector2(x, y) * TAM + Vector2(_azar_de(x + 11, y) * 6.0 - 3.0, _azar_de(x, y + 17) * 6.0 - 3.0)
					_piezas.append({"pos": pos.round(), "f": p[0], "n": p[1], "fase": _azar_de(x * 3, y * 5) * TAU,
						"espejo": _azar_de(x + 5, y + 9) < 0.5})
					break


static func _azar_de(x: int, y: int) -> float:
	var h := int(x) * 374761393 + int(y) * 668265263
	h = (h ^ (h >> 13)) * 1274126177
	h = h ^ (h >> 16)
	return float(h & 0xFFFF) / 65535.0


func _process(delta: float) -> void:
	_tiempo += delta
	_redibujar -= delta
	if _redibujar <= 0.0:
		_redibujar = 0.2                 # la hierba se mece despacio: no hace falta redibujar siempre
		queue_redraw()


func _draw() -> void:
	var inversa := get_viewport().get_canvas_transform().affine_inverse()
	var vista := Rect2(inversa.origin, get_viewport().get_visible_rect().size).grow(24)
	for b in _barandillas:
		if not vista.intersects(b):
			continue
		draw_rect(b, Color("6d4534"))
		draw_rect(Rect2(b.position, Vector2(b.size.x, 1)), Color("a8735a"))
		draw_rect(Rect2(b.position + Vector2(0, b.size.y - 1), Vector2(b.size.x, 1)), Color("251812"))
		for px in [b.position.x + 2, b.position.x + 10]:
			draw_rect(Rect2(Vector2(px, b.position.y - 2), Vector2(3, b.size.y + 3)), Color("492e23"))
			draw_rect(Rect2(Vector2(px, b.position.y - 2), Vector2(3, 1)), Color("905c45"))
	for p in _piezas:
		var pos: Vector2 = p["pos"]
		if not vista.has_point(pos):
			continue
		var f: int = p["f"]
		if p["n"] > 1:
			# el viento pasa en olas: la hierba se mece a destiempo según dónde esté
			f += 1 if sin(_tiempo * 2.2 - pos.x * 0.03 + p["fase"] * 0.3) > 0.2 else 0
		var origen := Rect2(f * TAM, 0, TAM, TAM)
		var destino := Rect2(pos, Vector2(TAM, TAM))
		if p["espejo"]:
			destino = Rect2(pos + Vector2(TAM, 0), Vector2(-TAM, TAM))
		draw_texture_rect_region(TEXTURA, destino, origen)
