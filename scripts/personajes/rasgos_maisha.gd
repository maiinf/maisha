extends Node2D
## RASGOS DE MAISHA: lo que le cambia por fuera al despertar Artes en el Árbol de la Vida.
##   brote   (Raíz 3)    le crece una tercera hoja en el brote de la cabeza, con un capullo
##   flores  (Raíz 6)    florecillas por el cuerpo
##   aura    (Aliento 3) una luz suave que la rodea y respira
##   brisa   (Aliento 6) el cuerpo se vuelve un poco transparente y deja una estela al moverse
## La hoja se coloca sola encima de la cabeza en cualquier animación: busca el píxel más alto del dibujo.

const HOJA := Color("6fbf4a")
const HOJA_CLARA := Color("b8e08a")
const HOJA_OSCURA := Color("2f5a20")
const PETALO := Color("ffd7e0")
const CENTRO_FLOR := Color("f9d36a")

var _sprite: AnimatedSprite2D
var _aura: Node2D
var _cimas := {}                 # "animación:fotograma:volteado" -> punto más alto (local del sprite)
var _tiempo := 0.0
var _rasgos: Array = []
var _estela: Array[Dictionary] = []
var _ultima := Vector2.ZERO


func _ready() -> void:
	_sprite = get_parent().get_node("Sprite")
	z_index = 1
	# el aura va por detrás de Maisha y con mezcla de luz
	_aura = Node2D.new()
	_aura.z_index = -1
	_aura.show_behind_parent = true
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_aura.material = suma
	_aura.draw.connect(_dibujar_aura)
	get_parent().add_child.call_deferred(_aura)
	Artes.arte_subida.connect(func(_id: String, _n: int) -> void: _actualizar())
	Estado.partida_cambiada.connect(_actualizar)
	_actualizar()


func _actualizar() -> void:
	_rasgos = Artes.rasgos()
	if _sprite:
		_sprite.self_modulate.a = 0.78 if "brisa" in _rasgos else 1.0


func _process(delta: float) -> void:
	_tiempo += delta
	if _rasgos.is_empty():
		if _estela.size() > 0:
			_estela.clear()
		return
	if "brisa" in _rasgos:
		var pos := (get_parent() as Node2D).global_position
		if pos.distance_to(_ultima) > 3.0:
			_estela.append({"p": pos + Vector2(randf_range(-4, 4), randf_range(-20, -6)), "t": 0.0})
			_ultima = pos
		for e in _estela:
			e["t"] += delta
		_estela = _estela.filter(func(e: Dictionary) -> bool: return e["t"] < 0.7)
	queue_redraw()
	if is_instance_valid(_aura):
		_aura.queue_redraw()


## El píxel más alto del dibujo actual (en coordenadas de Maisha)
func _cima() -> Vector2:
	var clave := "%s:%d:%s" % [_sprite.animation, _sprite.frame, _sprite.flip_h]
	if not _cimas.has(clave):
		var tex := _sprite.sprite_frames.get_frame_texture(_sprite.animation, _sprite.frame)
		var punto := Vector2(0, -32)
		if tex:
			var img := tex.get_image()
			if img:
				if img.is_compressed():
					img.decompress()
				var hallado := false
				for y in img.get_height():
					var xs := []
					for x in img.get_width():
						if img.get_pixel(x, y).a > 0.5:
							xs.append(x)
					if not xs.is_empty():
						var cx: float = (xs[0] + xs[-1]) / 2.0
						if _sprite.flip_h:
							cx = img.get_width() - 1 - cx
						punto = Vector2(cx - img.get_width() / 2.0, y - img.get_height() / 2.0)
						hallado = true
						break
				if not hallado:
					punto = Vector2(0, -img.get_height() / 2.0)
		_cimas[clave] = punto
	return _sprite.position + _cimas[clave]


func _pixel(p: Vector2, color: Color) -> void:
	draw_rect(Rect2(p.floor(), Vector2.ONE), color)


func _draw() -> void:
	if _rasgos.is_empty() or _sprite == null:
		return
	for e in _estela:
		var vida: float = 1.0 - e["t"] / 0.7
		draw_circle(to_local(e["p"]) + Vector2(0, -e["t"] * 8.0), 1.0 + vida, Color(0.85, 0.95, 1.0, 0.25 * vida))
	if "brote" in _rasgos:
		_dibujar_brote()
	if "flores" in _rasgos:
		_dibujar_flores()


## Una tercera hoja que sale recta del brote y se mece, con un capullo que brilla
func _dibujar_brote() -> void:
	var cima := _cima()
	var meneo := roundf(sin(_tiempo * 2.2))
	var base := cima + Vector2(0, 1)
	# tallo
	_pixel(base + Vector2(0, -1), HOJA_OSCURA)
	_pixel(base + Vector2(0, -2), HOJA)
	_pixel(base + Vector2(meneo * 0.5, -3), HOJA)
	# hoja
	var h := base + Vector2(meneo, -6)
	for p in [Vector2(0, 0), Vector2(1, 0), Vector2(-1, 1), Vector2(0, 1), Vector2(1, 1), Vector2(0, 2), Vector2(1, 2), Vector2(0, -1)]:
		_pixel(h + p, HOJA)
	_pixel(h + Vector2(0, 0), HOJA_CLARA)
	_pixel(h + Vector2(-1, 0), HOJA_OSCURA)
	_pixel(h + Vector2(2, 1), HOJA_OSCURA)
	# capullo que late
	var brillo := 0.6 + 0.4 * sin(_tiempo * 3.0)
	_pixel(h + Vector2(0, -2), Color(CENTRO_FLOR, brillo))
	draw_circle(h + Vector2(0.5, -1.5), 2.5, Color(1.0, 0.95, 0.6, 0.12 * brillo))


## Florecillas por el cuerpo (siguen el lado hacia el que mira)
func _dibujar_flores() -> void:
	var lado := -1.0 if _sprite.flip_h else 1.0
	var centro := _sprite.position
	var puntos := [Vector2(-6, 2), Vector2(5, 6), Vector2(-3, 11)]
	if _sprite.animation.ends_with("arriba"):
		puntos = [Vector2(-6, 1), Vector2(6, 4)]
	for p in puntos:
		var q: Vector2 = centro + Vector2(p.x * lado, p.y)
		_pixel(q + Vector2(-1, 0), PETALO)
		_pixel(q + Vector2(1, 0), PETALO)
		_pixel(q + Vector2(0, -1), PETALO)
		_pixel(q + Vector2(0, 1), PETALO)
		_pixel(q, CENTRO_FLOR)


func _dibujar_aura() -> void:
	if not ("aura" in _rasgos):
		return
	var pulso := 0.5 + 0.5 * sin(_tiempo * 1.8)
	var c := Vector2(0, -15)
	for i in 4:
		_aura.draw_circle(c, 9.0 + i * 4.0 + pulso * 2.0, Color(0.55, 0.8, 1.0, 0.05 + 0.02 * pulso))
	# motitas que suben alrededor
	for i in 5:
		var a := _tiempo * 0.9 + i * TAU / 5.0
		var y := -fposmod(_tiempo * 9.0 + i * 7.0, 26.0)
		_aura.draw_circle(Vector2(cos(a) * 10.0, y), 0.8, Color(0.8, 0.95, 1.0, 0.5 * (1.0 + y / 26.0)))
