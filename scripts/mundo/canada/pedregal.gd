extends Node2D
## EL PEDREGAL de la Cañada del Eco: grava, piedrecitas, losas, matojos secos, tomillo en flor, flores de roca,
## ramitas y matas de hierba por el fondo de la garganta. Más espeso al pie de las paredes (lo que se ha caído de
## la peña) y en la garganta. No estorba al andar. Siempre igual (sale de la posición de cada casilla).
## Piezas: arte/mundos/raiz/canada/pedregal.png (herramientas/pintar_canada.py).

const TEXTURA := preload("res://arte/mundos/raiz/canada/pedregal.png")
const R := preload("res://scripts/combate/reglas_combate.gd")
## peso de cada pieza (grava, piedrecitas, losa, matojo seco, tomillo, flor de roca, ramitas, mata verde)
const PESOS := [10, 9, 4, 6, 3, 2, 3, 5]


func preparar(filas: PackedStringArray) -> void:
	z_index = -9
	var total := 0
	for p in PESOS:
		total += p
	for y in filas.size():
		for x in filas[y].length():
			if filas[y][x] != ".":
				continue
			if not _libre(filas, x, y):
				continue
			# cuanto más cerca de la peña, más piedras (lo que se ha desprendido de las paredes)
			var cerca := 9
			for d in range(1, 4):
				for v in [Vector2i(0, -d), Vector2i(0, d), Vector2i(-d, 0), Vector2i(d, 0)]:
					var yy: int = y + v.y
					var xx: int = x + v.x
					if yy >= 0 and yy < filas.size() and xx >= 0 and xx < filas[yy].length() and filas[yy][xx] == "0":
						cerca = mini(cerca, d)
			var prob := 0.1 + (0.5 if cerca == 1 else (0.3 if cerca == 2 else (0.14 if cerca == 3 else 0.0)))
			if _azar(x, y) > prob:
				continue
			var tirada := int(_azar(y * 7 + 3, x * 13 + 1) * total)
			var pieza := 0
			for i in PESOS.size():
				tirada -= PESOS[i]
				if tirada < 0:
					pieza = i
					break
			# junto a la peña, sobre todo piedras; lejos, más plantas
			if cerca <= 2 and pieza >= 3 and _azar(x + 9, y + 2) < 0.6:
				pieza = int(_azar(x + 1, y + 7) * 3.0)
			var s := Sprite2D.new()
			s.texture = TEXTURA
			s.hframes = 8
			s.frame = pieza
			s.centered = false
			s.use_parent_material = true
			s.flip_h = _azar(x + 5, y + 9) < 0.5
			s.position = Vector2(x, y) * R.CASILLA + Vector2(_azar(x + 11, y) * 6.0 - 3.0, _azar(x, y + 17) * 6.0 - 3.0).round()
			add_child(s)


func _libre(filas: PackedStringArray, x: int, y: int) -> bool:
	for v in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
		var yy: int = y + v.y
		var xx: int = x + v.x
		if yy >= 0 and yy < filas.size() and xx >= 0 and xx < filas[yy].length():
			if not filas[yy][xx] in [".", ",", "0"]:
				return false
	return true


static func _azar(x: int, y: int) -> float:
	var h := int(x) * 374761393 + int(y) * 668265263
	h = (h ^ (h >> 13)) * 1274126177
	h = h ^ (h >> 16)
	return float(h & 0xFFFF) / 65535.0
