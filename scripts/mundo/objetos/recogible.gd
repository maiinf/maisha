extends Node2D
## RECOGIBLE: un objeto que Maisha coge al pasar por encima (setas luminosas, mineral...).
## Cada uno tiene su «marca» para no volver a aparecer una vez recogido.
## Brilla con un halo de su color para que se vea incluso en el prado gris.

signal recogido

@export var objeto := "seta_luminosa"
@export var marca := ""
@export var color_halo := Color(0.43, 0.69, 0.69)
## Si es más de 0: vuelve a salir pasados estos segundos de juego (bayas, juncos). Se guarda en Estado.extra.
@export var rebrota := 0.0

var _sprite: Sprite2D
var _halo: Node2D
var _tiempo := 0.0
var _cogido := false


func _ready() -> void:
	if marca != "" and not _disponible():
		queue_free()
		return
	add_to_group("recogibles")
	_halo = Node2D.new()
	var material := CanvasItemMaterial.new()
	material.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_halo.material = material
	_halo.position = Vector2(0, -6)
	_halo.draw.connect(_dibujar_halo)
	add_child(_halo)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/raiz/objetos/%s.png" % objeto)
	_sprite.hframes = 2
	_sprite.centered = false
	_sprite.offset = Vector2(-_sprite.texture.get_width() / 4, -_sprite.texture.get_height() + 1)
	add_child(_sprite)
	_tiempo = randf() * 3.0


func _process(delta: float) -> void:
	if _cogido:
		return
	_tiempo += delta
	_sprite.frame = 1 if fmod(_tiempo, 1.4) < 0.35 else 0
	_halo.queue_redraw()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and maisha.global_position.distance_to(global_position) < 11.0:
		_coger()


func _disponible() -> bool:
	if rebrota <= 0.0:
		return not Estado.tiene(marca)
	var cogido_en = Estado.extra.get("rebrote", {}).get(marca)
	return cogido_en == null or Estado.tiempo_jugado - float(cogido_en) >= rebrota


func _coger() -> void:
	_cogido = true
	Sonido.efecto({"seta_luminosa": "seta_recoger", "campanilla": "campanilla", "cencerro": "cencerro"}.get(objeto, "recoger"))
	if marca != "" and rebrota > 0.0:
		var rebrotes: Dictionary = Estado.extra.get("rebrote", {})
		rebrotes[marca] = Estado.tiempo_jugado
		Estado.extra["rebrote"] = rebrotes
	elif marca != "":
		Estado.marcar(marca)
	Estado.dar(objeto)
	recogido.emit()
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.mostrar_mensaje(Estado.texto_recogido(objeto))
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "position:y", -14.0, 0.4).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	t.tween_property(self, "modulate:a", 0.0, 0.45)
	t.chain().tween_callback(queue_free)


func _dibujar_halo() -> void:
	var pulso := 0.6 + 0.4 * sin(_tiempo * 3.0)
	for i in 4:
		_halo.draw_circle(Vector2.ZERO, (5.0 + i * 5.0) * (0.9 + 0.1 * pulso), Color(color_halo, 0.13 * pulso))
	# chispitas que suben despacio
	for k in 3:
		var t := fmod(_tiempo * 0.6 + k / 3.0, 1.0)
		var p := Vector2(sin(_tiempo * 1.3 + k * 2.1) * 6.0, -t * 18.0).round()
		_halo.draw_rect(Rect2(p, Vector2.ONE), Color(color_halo.lightened(0.5), 0.9 * (1.0 - t)))
