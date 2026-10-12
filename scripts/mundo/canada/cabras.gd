extends Node2D
## LAS CABRAS DE MBUZI (doce, y una negra: Tumbo). Mientras Mbuzi no tiene sus cencerros, están asustadas arriba,
## en el borde de las mesetas de la peña, pastando y mirando abajo. Cuando se los devuelves (marca
## «mbuzi_cencerros»), oyen el grave y bajan, una a una, al corral del aprisco; Tumbo, la última.
## En el corral pastan, dan unos pasos y levantan la cabeza. No estorban al andar.
## Dibujo: arte/mundos/raiz/canada/cabras.png (herramientas/pintar_canada.py): 0-3 blanca, 4-7 Tumbo.

const TEXTURA := preload("res://arte/mundos/raiz/canada/cabras.png")

## dónde están arriba, en el borde de las mesetas (casillas de peña junto al fondo), y el corral (en píxeles)
@export var arriba: Array[Vector2] = []
@export var corral := Rect2()

var _cabras: Array[Dictionary] = []
var _tiempo := 0.0


func _ready() -> void:
	y_sort_enabled = true                                         # (se ordenan entre ellas)
	z_index = 1          # por encima del aprisco: su dibujo incluye el corral (y en el corral no se puede entrar)
	var abajo := Estado.tiene("mbuzi_cencerros")
	for i in arriba.size():
		var s := Sprite2D.new()
		s.texture = TEXTURA
		s.hframes = 8
		s.centered = false
		s.offset = Vector2(-9, -15)
		s.use_parent_material = true
		add_child(s)
		var negra := i == arriba.size() - 1                 # Tumbo, la última
		var c := {"s": s, "negra": negra, "pos": _en_corral(i) if abajo else arriba[i], "meta": Vector2.ZERO,
			"pose": 0, "espera": randf_range(0.5, 3.0), "mira": 1.0 if i % 2 == 0 else -1.0, "bajando": false}
		c["meta"] = c["pos"]
		_cabras.append(c)
	Estado.marca_puesta.connect(_al_poner_marca)


func _en_corral(i: int) -> Vector2:
	var a := _azar(i * 7, 3)
	var b := _azar(3, i * 11)
	return corral.position + Vector2(a * corral.size.x, b * corral.size.y)


func _al_poner_marca(m: String) -> void:
	if m != "mbuzi_cencerros":
		return
	# bajan una a una (Tumbo, la última, y con muchas ganas de no hacerlo)
	for i in _cabras.size():
		var c: Dictionary = _cabras[i]
		var retraso := 1.5 + i * 0.6 + (2.5 if c["negra"] else 0.0)
		get_tree().create_timer(retraso).timeout.connect(func() -> void:
			c["bajando"] = true
			c["meta"] = _en_corral(i))


func _process(delta: float) -> void:
	_tiempo += delta
	for c in _cabras:
		var s: Sprite2D = c["s"]
		var pos: Vector2 = c["pos"]
		var meta: Vector2 = c["meta"]
		if pos.distance_to(meta) > 1.0:
			var velocidad := 55.0 if c["bajando"] else 12.0
			pos = pos.move_toward(meta, velocidad * delta)
			c["mira"] = signf(meta.x - pos.x) if absf(meta.x - pos.x) > 0.5 else c["mira"]
			c["pose"] = 1 + int(_tiempo * 8.0) % 2
		else:
			c["bajando"] = false
			c["espera"] -= delta
			if c["espera"] <= 0.0:
				c["espera"] = randf_range(1.5, 4.5)
				var r := randf()
				if r < 0.45:
					c["pose"] = 0                                 # pasta
				elif r < 0.7:
					c["pose"] = 3                                 # levanta la cabeza
				elif corral.has_point(pos):
					c["meta"] = (pos + Vector2(randf_range(-14, 14), randf_range(-6, 6))).clamp(corral.position, corral.end)
		c["pos"] = pos
		s.position = pos.round()
		s.flip_h = c["mira"] < 0.0
		s.frame = int(c["pose"]) + (4 if c["negra"] else 0)


static func _azar(x: int, y: int) -> float:
	var h := int(x) * 374761393 + int(y) * 668265263
	h = (h ^ (h >> 13)) * 1274126177
	h = h ^ (h >> 16)
	return float(h & 0xFFFF) / 65535.0
