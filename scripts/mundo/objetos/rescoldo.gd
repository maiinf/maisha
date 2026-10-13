extends Node2D
## RESCOLDO DE GIZA: lo que queda de un jefe en su arena después de vencerlo. Un anillo de piedras rotas con una llama
## violeta y dorada. Si Maisha lo usa (Acción), la zona revive el ECO del jefe (zona_corrupta.revivir_eco) para pelear
## otra vez y mejorar su rango del Bestiario. No cambia nada de la historia. Cuando ya tiene el oro, se apaga.
## Lo pone la propia zona (zona_corrupta.gd). Dibujo: arte/mundos/raiz/hechiceros/rescoldo.png.

const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const DIBUJO := preload("res://arte/mundos/raiz/hechiceros/rescoldo.png")

var zona: Node = null
var radio_interaccion := 26.0
var _sprite: Sprite2D
var _tiempo := 0.0
var _usado := false


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("rescoldos")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 10.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -12)
	add_child(_sprite)
	_tiempo = randf() * 2.0


func _process(delta: float) -> void:
	_tiempo += delta
	_sprite.frame = int(_tiempo * 5.0) % 2
	queue_redraw()


func _draw() -> void:
	# un halo que late, como una brasa que respira
	var pulso := 0.5 + 0.5 * sin(_tiempo * 2.5)
	draw_circle(Vector2(0, -10), 12.0 + pulso * 3.0, Color(0.7, 0.4, 0.95, 0.08 + 0.05 * pulso))


func interactuar() -> void:
	if _usado or zona == null:
		return
	_usado = true
	remove_from_group("interactuables")
	zona.call("revivir_eco")
	var t := create_tween()
	t.tween_property(self, "scale", Vector2(1.6, 0.1), 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	t.tween_callback(queue_free)
