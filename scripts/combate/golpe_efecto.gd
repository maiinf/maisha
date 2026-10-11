extends Node2D
## Efecto del GOLPE: el cetro describe un arco delante de Maisha y deja una estela de hojas.
## Se dibuja píxel a píxel para que la estela quede nítida.

const CETRO := preload("res://arte/personajes/maisha/prendas/cetro_raiz.png")
const AGARRE := Vector2(3, 13)   # punto del dibujo del cetro que sujeta la mano
const DURACION := 0.2
const RADIO := 16.0
const ARCO := 140.0              # grados que recorre el golpe

var direccion := Vector2.RIGHT
var con_cetro := true
var _tiempo := 0.0
var _inicio := 0.0
var _giro := 1.0

const VERDE := Color("6fcf4f")
const VERDE_OSCURO := Color("3e9a35")
const LUZ := Color("fff3c4")


func _ready() -> void:
	position = Vector2(0, -12)
	var base := rad_to_deg(direccion.angle())
	# hacia la izquierda el arco gira al revés para que el golpe sea simétrico
	_giro = -1.0 if direccion.x < -0.5 else 1.0
	_inicio = base - _giro * ARCO * 0.6


func _process(delta: float) -> void:
	_tiempo += delta
	if _tiempo >= DURACION:
		queue_free()
		return
	queue_redraw()


func _angulo(t: float) -> float:
	return deg_to_rad(_inicio + _giro * ARCO * t)


func _draw() -> void:
	var t := clampf(_tiempo / DURACION, 0.0, 1.0)
	var avance := 1.0 - pow(1.0 - t, 3.0)          # sale rápido y frena al final
	# estela: puntos a lo largo del arco recorrido, más finos por detrás
	var pasos := 18
	for i in pasos:
		var u := float(i) / pasos
		if u > avance:
			break
		var a := _angulo(u)
		var cola := avance - u                     # 0 = punta del golpe
		if cola > 0.55:
			continue
		var p := Vector2(cos(a), sin(a)) * RADIO
		var color := LUZ if cola < 0.12 else (VERDE if cola < 0.3 else VERDE_OSCURO)
		draw_rect(Rect2(p.round(), Vector2(2, 2)), color)
		if cola < 0.3:
			draw_rect(Rect2((p * 0.8).round(), Vector2(1, 1)), VERDE)
	# el cetro, girando desde la mano
	if con_cetro:
		var a := _angulo(avance)
		draw_set_transform(Vector2.ZERO, a + PI / 2.0, Vector2.ONE)
		draw_texture(CETRO, -AGARRE)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
