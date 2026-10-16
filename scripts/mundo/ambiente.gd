extends Node2D
## AMBIENTE de una región: lo que hace que el mundo se sienta vivo aunque el arte sea sencillo.
##   - sombras de nubes que cruzan despacio
##   - hojas que caen cerca de la cámara
##   - mariposas, solo donde el mundo ya ha recuperado el color
##   - destellos en el agua
##   - polen que brilla al sol donde hay color, y ceniza de Giza que cae donde todo es gris
##   - rayos de sol que entran en diagonal y una viñeta suave (luz_sol.gd, en la pantalla)
## Se dibuja todo desde aquí para que sea ligero.

const MARIPOSA := preload("res://arte/mundos/raiz/objetos/mariposa.png")
const VIENTO := Vector2(7, 2)            # píxeles por segundo
const HOJAS_MAX := 16
const MOTAS_MAX := 40
const LUZ_SOL := preload("res://scripts/mundo/luz_sol.gd")
## Las hojas, en 4 giros (cada fila es un píxel: «#» color, «+» luz, «-» sombra)
const FORMAS_HOJA := [
	[".+#.", "+##-", ".#-."],
	["..+#", ".##-", "#-.."],
	["+#", "##", "#-", ".-"],
	["#+..", "-##.", "..-#"],
]
const MARIPOSAS_MAX := 10
const COLORES_HOJA := [Color("5d793e"), Color("90a153"), Color("a37036"), Color("c68756"), Color("6a8246")]
const COLORES_HOJA_OTONO := [Color("a37036"), Color("c68756"), Color("ab5031"), Color("cc6351"), Color("e0a874"), Color("794123")]
const COLORES_HOJA_SECA := [Color("6a6c6f"), Color("85878a"), Color("525458")]
const SOMBRA_NUBE := Color(0.03, 0.05, 0.08, 0.10)

## Luciérnagas que flotan cerca de la cámara (en la aldea, la vida del Gran Árbol)
@export var luciernagas := 0
## Rayos de sol y viñeta en la pantalla
@export var rayos_de_sol := true
## Bosque en otoño: muchas más hojas, cobrizas y rojizas
@export var otono := false
## Niebla baja que se arrastra por el suelo (la ciénaga). Es más espesa donde Giza lo tiene todo gris
## y casi desaparece cuando la zona vuelve a tener color.
@export_range(0.0, 1.0) var niebla := 0.0
const COLOR_NIEBLA := Color(0.78, 0.84, 0.8)

var tam_mapa := Vector2(1920, 1088)      # lo ajusta la región al cargar
var agua: Array[Vector2] = []            # centros de las casillas de agua (los pone la región)

var _nubes: Array[Dictionary] = []
var _hojas: Array[Dictionary] = []
var _mariposas: Array[Dictionary] = []
var _destellos: Array[Dictionary] = []
var _bichitos: Array[Dictionary] = []
var _motas: Array[Dictionary] = []
var _bancos: Array[Dictionary] = []      # bancos de niebla (en coordenadas de pantalla, se mueven con el viento)
var _espesor := -1.0                      # lo espesa que está la niebla ahora (sigue al gris con suavidad)
var _tiempo := 0.0
var _azar := RandomNumberGenerator.new()
var _gestor: Node = null


func _ready() -> void:
	_azar.seed = 21
	if rayos_de_sol:
		add_child(LUZ_SOL.new())
	for i in 6:
		var puntos := PackedVector2Array()
		var radio := _azar.randf_range(60, 120)
		for k in 20:
			var a := TAU * k / 20
			var r := radio * (0.75 + 0.25 * sin(a * 3.0 + i) + _azar.randf_range(-0.05, 0.05))
			puntos.append(Vector2(cos(a) * r, sin(a) * r * 0.6))
		_nubes.append({"pos": Vector2(_azar.randf() * tam_mapa.x, _azar.randf() * tam_mapa.y), "forma": puntos})
	if niebla > 0.0:
		for i in 9:
			var forma := PackedVector2Array()
			var ancho := _azar.randf_range(70, 140)
			for k in 18:
				var a := TAU * k / 18
				var r := 1.0 + 0.18 * sin(a * 2.0 + i) + 0.1 * sin(a * 5.0 + i * 2.0)
				forma.append(Vector2(cos(a) * ancho * r, sin(a) * ancho * 0.28 * r))
			_bancos.append({"pos": Vector2(_azar.randf() * 640 - 80, _azar.randf() * 400 - 20), "forma": forma,
				"vel": _azar.randf_range(0.5, 1.4), "fase": _azar.randf() * TAU})


func _vista() -> Rect2:
	var inversa := get_viewport().get_canvas_transform().affine_inverse()
	return Rect2(inversa.origin, get_viewport().get_visible_rect().size)


func _process(delta: float) -> void:
	_tiempo += delta
	var vista := _vista()
	if _gestor == null or not is_instance_valid(_gestor):
		_gestor = get_tree().get_first_node_in_group("corrupcion")
	var gestor := _gestor
	# nubes: avanzan con el viento y dan la vuelta al mapa
	for n in _nubes:
		n["pos"] += VIENTO * delta
		if n["pos"].x > tam_mapa.x + 150:
			n["pos"].x = -150
		if n["pos"].y > tam_mapa.y + 100:
			n["pos"].y = -100
	# niebla: bancos que cruzan la pantalla despacio; se espesa con el gris del sitio
	if niebla > 0.0:
		var gris: float = gestor.gris_en(vista.get_center()) if gestor else 1.0
		var meta := niebla * (0.3 + 0.7 * gris)
		_espesor = meta if _espesor < 0.0 else move_toward(_espesor, meta, delta * 0.15)
		for b in _bancos:
			b["pos"] += Vector2(VIENTO.x * b["vel"], VIENTO.y * 0.3) * delta
			if b["pos"].x > vista.size.x + 160:
				b["pos"] = Vector2(-160, _azar.randf() * (vista.size.y + 40) - 20)
	# hojas: verdes y cobrizas donde hay color; grises y secas donde Giza se lo ha llevado
	if _hojas.size() < HOJAS_MAX * (3 if otono else 1) and _azar.randf() < delta * (9.0 if otono else 3.0):
		var inicio := Vector2(vista.position.x + _azar.randf() * vista.size.x, vista.position.y - 4)
		var seca: bool = gestor != null and gestor.gris_en(inicio + Vector2(0, vista.size.y * 0.5)) > 0.5
		var colores: Array = COLORES_HOJA_SECA if seca else (COLORES_HOJA_OTONO if otono else COLORES_HOJA)
		_hojas.append({"pos": inicio, "vida": 0.0, "fase": _azar.randf() * TAU, "color": colores[_azar.randi() % colores.size()],
			"caida": _azar.randf_range(12, 22), "giro": _azar.randf_range(4.0, 8.0), "alto": _azar.randf_range(8, 16)})
	for i in range(_hojas.size() - 1, -1, -1):
		var h: Dictionary = _hojas[i]
		h["vida"] += delta
		h["pos"] += Vector2(VIENTO.x + sin(h["vida"] * 2.2 + h["fase"]) * 14.0, h["caida"]) * delta
		if h["pos"].y >= vista.end.y + 8:
			_hojas.remove_at(i)
	# motas: polen dorado al sol donde hay vida; ceniza que cae despacio donde todo es gris
	if _motas.size() < MOTAS_MAX and _azar.randf() < delta * 12.0:
		var p := vista.position + Vector2(_azar.randf() * vista.size.x, _azar.randf() * vista.size.y)
		var g: float = gestor.gris_en(p) if gestor else 0.0
		if g > 0.6 or g < 0.3:
			_motas.append({"pos": p, "vida": 0.0, "dura": _azar.randf_range(3.0, 7.0), "fase": _azar.randf() * TAU,
				"ceniza": g > 0.6})
	for i in range(_motas.size() - 1, -1, -1):
		var mo: Dictionary = _motas[i]
		mo["vida"] += delta
		if mo["ceniza"]:
			mo["pos"] += Vector2(VIENTO.x * 0.8 + sin(mo["vida"] * 1.3 + mo["fase"]) * 4.0, 6.0) * delta
		else:
			mo["pos"] += Vector2(sin(mo["vida"] * 0.8 + mo["fase"]) * 5.0 + 2.0, cos(mo["vida"] * 0.6 + mo["fase"]) * 3.0 - 3.0) * delta
		if mo["vida"] >= mo["dura"]:
			_motas.remove_at(i)
	# mariposas: solo donde ya hay color
	if gestor and _mariposas.size() < MARIPOSAS_MAX and _azar.randf() < delta * 2.0:
		var p := vista.position + Vector2(_azar.randf() * vista.size.x, _azar.randf() * vista.size.y)
		if gestor.gris_en(p) < 0.2:
			_mariposas.append({"pos": p, "destino": p, "color": _azar.randi() % 2, "vida": 0.0, "dura": _azar.randf_range(8, 16)})
	for i in range(_mariposas.size() - 1, -1, -1):
		var m: Dictionary = _mariposas[i]
		m["vida"] += delta
		if m["pos"].distance_to(m["destino"]) < 3.0:
			m["destino"] = m["pos"] + Vector2(_azar.randf_range(-40, 40), _azar.randf_range(-30, 30))
		m["pos"] = m["pos"].move_toward(m["destino"], 18.0 * delta)
		if m["vida"] >= m["dura"] or (gestor != null and gestor.gris_en(m["pos"]) >= 0.5):
			_mariposas.remove_at(i)
	# destellos en el agua visible
	if not agua.is_empty() and _azar.randf() < delta * 10.0:
		var c: Vector2 = agua[_azar.randi() % agua.size()]
		if vista.grow(16).has_point(c):
			_destellos.append({"pos": c + Vector2(_azar.randi_range(-6, 6), _azar.randi_range(-6, 6)), "vida": 0.0})
	for i in range(_destellos.size() - 1, -1, -1):
		var d: Dictionary = _destellos[i]
		d["vida"] += delta
		if d["vida"] >= 0.5:
			_destellos.remove_at(i)
	# luciérnagas: aparecen y se apagan despacio, vagando
	if _bichitos.size() < luciernagas and _azar.randf() < delta * 4.0:
		_bichitos.append({"pos": vista.position + Vector2(_azar.randf() * vista.size.x, _azar.randf() * vista.size.y),
			"fase": _azar.randf() * TAU, "vida": 0.0, "dura": _azar.randf_range(4, 9)})
	for i in range(_bichitos.size() - 1, -1, -1):
		var b: Dictionary = _bichitos[i]
		b["vida"] += delta
		b["pos"] += Vector2(sin(b["vida"] * 0.9 + b["fase"]) * 9.0, cos(b["vida"] * 0.7 + b["fase"] * 2.0) * 6.0 - 2.0) * delta
		if b["vida"] >= b["dura"]:
			_bichitos.remove_at(i)
	queue_redraw()


func _draw() -> void:
	var vista := _vista()
	# destellos del agua (a ras de suelo, se dibujan primero)
	for d in _destellos:
		var p: Vector2 = d["pos"].round()
		var brillo := Color("fff8e8") if d["vida"] < 0.25 else Color("6db0b0")
		draw_rect(Rect2(p, Vector2.ONE), brillo)
		if d["vida"] < 0.2:
			draw_rect(Rect2(p + Vector2(-1, 0), Vector2(3, 1)), Color(brillo, 0.6))
	# luciérnagas
	for b in _bichitos:
		var vida: float = b["vida"] / b["dura"]
		var brillo := sin(vida * PI) * (0.6 + 0.4 * sin(b["vida"] * 5.0 + b["fase"]))
		var p: Vector2 = b["pos"].round()
		draw_rect(Rect2(p - Vector2(1, 1), Vector2(3, 3)), Color(1.0, 0.85, 0.45, 0.18 * brillo))
		draw_rect(Rect2(p, Vector2.ONE), Color(1.0, 0.95, 0.7, brillo))
	# mariposas
	for m in _mariposas:
		var abierta := int(m["vida"] * 8.0) % 2 == 0
		var fotograma: int = m["color"] * 2 + (0 if abierta else 1)
		var p: Vector2 = (m["pos"] + Vector2(0, sin(m["vida"] * 5.0) * 2.0)).round()
		draw_texture_rect_region(MARIPOSA, Rect2(p, Vector2(5, 4)), Rect2(fotograma * 5, 0, 5, 4))
	# motas de polen (brillan al sol) y de ceniza
	for mo in _motas:
		var vida: float = mo["vida"] / mo["dura"]
		var a := sin(vida * PI)
		var p: Vector2 = mo["pos"].round()
		if mo["ceniza"]:
			draw_rect(Rect2(p, Vector2.ONE), Color(0.62, 0.6, 0.68, 0.55 * a))
		else:
			var brillo := 0.55 + 0.45 * sin(mo["vida"] * 6.0 + mo["fase"])
			draw_rect(Rect2(p, Vector2.ONE), Color(1.0, 0.95, 0.72, 0.8 * a * brillo))
	# hojas que caen dando vueltas, con su sombra en el suelo
	for h in _hojas:
		var forma: Array = FORMAS_HOJA[int(h["vida"] * h["giro"] + h["fase"] * 4.0) % FORMAS_HOJA.size()]
		var p: Vector2 = h["pos"].round()
		var sombra: Vector2 = (h["pos"] + Vector2(h["alto"] * 0.5, h["alto"])).round()
		var color: Color = h["color"]
		for fila in forma.size():
			var texto: String = forma[fila]
			for col in texto.length():
				var ch := texto[col]
				if ch == ".":
					continue
				draw_rect(Rect2(sombra + Vector2(col, fila), Vector2.ONE), Color(0.02, 0.04, 0.02, 0.18))
				var c := color.lightened(0.25) if ch == "+" else (color.darkened(0.3) if ch == "-" else color)
				draw_rect(Rect2(p + Vector2(col, fila), Vector2.ONE), c)
	# niebla: varias capas suaves por banco, que respiran un poco
	if niebla > 0.0 and _espesor > 0.01:
		var origen := vista.position
		for b in _bancos:
			var forma: PackedVector2Array = b["forma"]
			var respira := 0.85 + 0.15 * sin(_tiempo * 0.4 + b["fase"])
			for capa in 3:
				var escala := 1.0 - capa * 0.25
				var puntos := PackedVector2Array()
				for q in forma:
					puntos.append((origen + b["pos"] + q * escala * respira).round())
				draw_colored_polygon(puntos, Color(COLOR_NIEBLA, 0.075 * _espesor))
	# sombras de nubes visibles en cámara (sin alojar arrays nuevos por nube)
	var vista_nubes := vista.grow(140.0)
	for n in _nubes:
		var pos_n: Vector2 = n["pos"]
		if not vista_nubes.has_point(pos_n):
			continue
		draw_set_transform(pos_n.round())
		draw_colored_polygon(n["forma"], SOMBRA_NUBE)
	draw_set_transform(Vector2.ZERO)
