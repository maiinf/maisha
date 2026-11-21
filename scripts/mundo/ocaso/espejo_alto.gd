extends StaticBody2D
## UN ESPEJO DEL INVERNADERO (el Jardín de los Faroles): una luna ovalada que guarda la luz del atardecer. Un golpe
## de cetro la suelta: un RAYO cruza el Invernadero hasta `apunta` (el espejo de enfrente) durante DURA s. Lo que
## toca el rayo (`toca()`) queda a la luz: así se delatan los reflejos de Mondo (enemigos/mondo.gd).
## Dibujo: arte/mundos/ocaso/jardin/espejo_alto.png (0 quieto · 1 echa su rayo).

const DIBUJO := preload("res://arte/mundos/ocaso/jardin/espejo_alto.png")
const DURA := 2.4
const DESCANSA := 0.8
const ANCHO := 12.0

var apunta := Vector2.ZERO               # (global)
var dura := DURA                         # (en el Altar del Sol, más: los dos espejos están lejos)
var _t := 0.0                            # lo que le queda de rayo
var _descanso := 0.0
var _sprite: Sprite2D
var _rayo: Node2D


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("espejos_altos")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -21)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(16, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	_rayo = Node2D.new()
	_rayo.z_index = 2
	_rayo.top_level = true
	_rayo.draw.connect(_dibujar_rayo)
	add_child(_rayo)


func activo() -> bool:
	return _t > 0.0


func _origen() -> Vector2:
	return global_position + Vector2(0, -2)


## ¿Pasa el rayo por ese punto (en el suelo)?
func toca(p: Vector2) -> bool:
	if not activo():
		return false
	return Geometry2D.get_closest_point_to_segment(p, _origen(), apunta).distance_to(p) < ANCHO


func _process(delta: float) -> void:
	_descanso = maxf(0.0, _descanso - delta)
	if _t > 0.0:
		_t = maxf(0.0, _t - delta)
		if _t == 0.0:
			_descanso = DESCANSA
	_sprite.frame = 1 if activo() else 0
	_rayo.queue_redraw()


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	if activo() or _descanso > 0.0:
		return false
	_t = dura
	Sonido.efecto("espejo_enciende", 0.0, global_position)
	return true


func _dibujar_rayo() -> void:
	if not activo():
		return
	var f := minf(1.0, _t / 0.3) * minf(1.0, (dura - _t) / 0.12 + 0.2)
	var a := _origen() + Vector2(0, -16)
	var b := apunta + Vector2(0, -16)
	var col := Color(1.0, 0.85, 0.5)
	_rayo.draw_line(a, b, Color(col, 0.16 * f), ANCHO * 1.6)
	_rayo.draw_line(a, b, Color(col, 0.4 * f), 4.0)
	_rayo.draw_line(a, b, Color(1, 1, 0.95, 0.9 * f), 1.5)
	# y en el suelo, la mancha de luz por donde pasa
	_rayo.draw_line(_origen(), apunta, Color(col, 0.14 * f), ANCHO * 2.0)
