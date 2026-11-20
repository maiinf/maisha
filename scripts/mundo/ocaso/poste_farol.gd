extends StaticBody2D
## UN POSTE DE LA PLAZA DE LOS DOCE FAROLES (Jioni, el Valle del Ocaso). Con Acción, si Maisha lleva un Farol de la
## Hora, lo cuelga (se queda encendido para siempre: `marca`). Cada farol colgado devuelve una hora a la ciudad (lo
## lleva la escena con la señal `colgado`). Dibujo: arte/mundos/ocaso/jioni/poste.png (0 vacío · 1 con su farol).

signal colgado

const CHARLA := preload("res://scripts/mundo/charla.gd")
const DIBUJO := preload("res://arte/mundos/ocaso/jioni/poste.png")
const PREFIJO := "farol/colgado_"

var marca := ""
var radio_interaccion := 22.0
var _sprite: Sprite2D
var _luz: PointLight2D
var _tiempo := 0.0


## Cuántos faroles hay colgados en la plaza
static func colgados() -> int:
	var n := 0
	for m in Estado.marcas:
		if String(m).begins_with(PREFIJO):
			n += 1
	return n


func _ready() -> void:
	add_to_group("interactuables")
	add_to_group("postes_farol")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -20)
	add_child(_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(6, 4)
	forma.shape = caja
	forma.position = Vector2(0, -2)
	add_child(forma)
	if encendido():
		_encender(false)


func encendido() -> bool:
	return Estado.tiene(marca)


func interactuar() -> void:
	if encendido():
		await CHARLA.hablar(self, "jioni_poste_lleno")
	elif Estado.cuantos("farol_hora") > 0:
		Estado.quitar("farol_hora")
		Estado.marcar(marca)
		_encender(true)
		colgado.emit()
	else:
		await CHARLA.hablar(self, "jioni_poste_vacio")


func _encender(ahora: bool) -> void:
	_sprite.frame = 1
	_luz = PointLight2D.new()
	_luz.texture = preload("res://scripts/mundo/relieve.gd").textura_luz(96)
	_luz.color = Color(1.0, 0.75, 0.4)
	_luz.energy = 0.7
	_luz.position = Vector2(5, -26)
	add_child(_luz)
	if ahora:
		Sonido.efecto("farol_colgar", 0.0, global_position)
		Impacto.chispa(global_position + Vector2(5, -26), Vector2.UP, Color(1.0, 0.8, 0.4))
	queue_redraw()


func _process(delta: float) -> void:
	if _luz != null:
		_tiempo += delta
		queue_redraw()


func _draw() -> void:
	if _luz == null:
		return
	var p := Vector2(5.5, -23.5)
	var late := 0.86 + 0.14 * sin(_tiempo * 3.4 + global_position.x * 0.13)
	draw_circle(p, 13.0 * late, Color(1.0, 0.68, 0.22, 0.16 * late))
	draw_circle(p, 8.0 * late, Color(1.0, 0.80, 0.34, 0.30 * late))
	draw_circle(p, 4.2, Color(1.0, 0.92, 0.58, 0.52 * late))
	draw_circle(p + Vector2(-0.5, -0.5), 1.8, Color(1.0, 0.99, 0.88, 0.88))
