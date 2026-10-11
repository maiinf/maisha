extends Node2D
## SECRETO: una esencia de luz escondida. Se recoge al pasar por encima.
## Con la torre del vigía de Pino (marca «vigia»), cada secreto lanza un haz de luz
## hacia el cielo que se ve desde lejos.

signal recogida

const TEXTURA := preload("res://arte/mundos/raiz/objetos/esencia.png")

var _sprite: Sprite2D
var _tiempo := 0.0
var _recogida := false
var _haz: Node2D


func _ready() -> void:
	add_to_group("secretos")
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -8)
	add_child(_sprite)
	_tiempo = randf() * 3.0
	if Estado.tiene("vigia"):
		_haz = Node2D.new()
		_haz.z_index = 4
		var material := CanvasItemMaterial.new()
		material.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		_haz.material = material
		_haz.draw.connect(_dibujar_haz)
		add_child(_haz)


func _process(delta: float) -> void:
	if _recogida:
		return
	_tiempo += delta
	_sprite.frame = int(_tiempo * 3.0) % 2
	_sprite.position.y = round(sin(_tiempo * 2.5) * 1.5)
	if _haz:
		_haz.queue_redraw()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and maisha.global_position.distance_to(global_position) < 10.0:
		_recoger()


func _recoger() -> void:
	_recogida = true
	Sonido.efecto("esencia")
	if _haz:
		_haz.queue_free()
		_haz = null
	recogida.emit()
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "position:y", -14.0, 0.4).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	t.tween_property(_sprite, "scale", Vector2(1.6, 1.6), 0.4)
	t.tween_property(_sprite, "modulate:a", 0.0, 0.45)
	t.chain().tween_callback(queue_free)


## Haz de luz del vigía: una columna fina que sube y late
func _dibujar_haz() -> void:
	var pulso := 0.7 + 0.3 * sin(_tiempo * 2.0)
	for i in 4:
		var ancho := 3.0 + i * 4.0
		_haz.draw_rect(Rect2(-ancho / 2.0, -180.0, ancho, 172.0), Color(1.0, 0.82, 0.45, 0.09 * pulso))
	_haz.draw_rect(Rect2(-1.0, -180.0, 2.0, 172.0), Color(1.0, 0.95, 0.8, 0.45 * pulso))
	# brillo en el suelo y motas que suben por el haz
	_haz.draw_circle(Vector2(0, -6), 10.0, Color(1.0, 0.85, 0.5, 0.12 * pulso))
	for k in 5:
		var t := fmod(_tiempo * 0.35 + k / 5.0, 1.0)
		_haz.draw_rect(Rect2(Vector2(round(sin(k * 1.9 + _tiempo) * 3.0), -8.0 - t * 170.0), Vector2.ONE), Color(1, 0.95, 0.8, 0.8 * (1.0 - t)))
