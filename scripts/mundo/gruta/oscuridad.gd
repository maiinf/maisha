extends Node2D
## LA OSCURIDAD DE LA GRUTA. Todo se ve en penumbra (un CanvasModulate oscuro) salvo lo que tiene luz:
##   - Maisha, que brilla un poco a su alrededor (su luz respira despacio);
##   - las SEMILLAS DORMIDAS de los nichos («ŝ» en el mapa), que laten verdes;
##   - las HUELLAS LILAS de Mauti, que van de la entrada al fondo (guían).
## Lo crea scripts/mundo/gruta_raices.gd.

const SEMILLA := preload("res://arte/mundos/raiz/gruta/semilla_dormida.png")
const HUELLA := preload("res://arte/mundos/raiz/gruta/huella.png")
const PENUMBRA := Color(0.13, 0.11, 0.17)
## el rastro de Mauti (en casillas): de la entrada, por el pasillo y la galería, hasta el fondo
const RASTRO := [Vector2(32, 81), Vector2(32, 72), Vector2(31, 62), Vector2(32, 52), Vector2(33, 46), Vector2(42, 44),
	Vector2(50, 40), Vector2(52, 31), Vector2(46, 23), Vector2(38, 17), Vector2(32, 12)]

var _luz_maisha: PointLight2D
var _semillas: Array[Sprite2D] = []
var _tiempo := 0.0


static func textura_luz(tam := 256) -> GradientTexture2D:
	return preload("res://scripts/mundo/relieve.gd").textura_luz(tam)


func _ready() -> void:
	var penumbra := CanvasModulate.new()
	penumbra.color = PENUMBRA
	add_child(penumbra)
	var tex := textura_luz()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	_luz_maisha = PointLight2D.new()
	_luz_maisha.texture = tex
	_luz_maisha.texture_scale = 1.45
	_luz_maisha.energy = 1.25
	_luz_maisha.color = Color(1.0, 0.92, 0.75)
	_luz_maisha.position = Vector2(0, -10)
	maisha.add_child(_luz_maisha)
	var region := get_tree().get_first_node_in_group("region")
	var filas: PackedStringArray = region.get("_filas")
	var entidades := get_parent().get_node("Entidades")
	for y in filas.size():
		for x in filas[y].length():
			if filas[y][x] == "ŝ":
				var s := Sprite2D.new()
				s.texture = SEMILLA
				s.hframes = 3
				s.offset = Vector2(0, -12)
				s.position = Vector2(x, y) * 16.0 + Vector2(8, 14)
				s.set_meta("fase", float(x * 7 + y * 3) * 0.37)
				var luz := PointLight2D.new()
				luz.texture = tex
				luz.texture_scale = 0.38
				luz.color = Color(0.45, 1.0, 0.4)
				luz.energy = 0.9
				luz.position = Vector2(0, -12)
				s.add_child(luz)
				entidades.add_child(s)
				_semillas.append(s)
	# las huellas de Mauti, a pares, con una lucecita cada pocas
	var n := 0
	for i in RASTRO.size() - 1:
		var a: Vector2 = RASTRO[i] * 16.0 + Vector2(8, 8)
		var b: Vector2 = RASTRO[i + 1] * 16.0 + Vector2(8, 8)
		var pasos := int(a.distance_to(b) / 22.0)
		for k in pasos:
			var h := Sprite2D.new()
			h.texture = HUELLA
			h.hframes = 2
			h.frame = n % 2
			h.position = a.lerp(b, float(k) / pasos) + Vector2(sin(n * 1.7) * 3.0, 0)
			h.rotation = (b - a).angle() + PI / 2.0
			h.z_index = -6
			add_child(h)
			if n % 3 == 0:
				var luz := PointLight2D.new()
				luz.texture = tex
				luz.texture_scale = 0.14
				luz.color = Color(0.75, 0.6, 1.0)
				luz.energy = 0.7
				h.add_child(luz)
			n += 1


func _process(delta: float) -> void:
	_tiempo += delta
	_luz_maisha.energy = 1.2 + sin(_tiempo * 1.3) * 0.08
	for s in _semillas:
		var f: float = 0.5 + 0.5 * sin(_tiempo * 1.1 + float(s.get_meta("fase")))
		s.frame = 2 if f > 0.66 else (1 if f > 0.33 else 0)
		(s.get_child(0) as PointLight2D).energy = 0.45 + f * 0.7
