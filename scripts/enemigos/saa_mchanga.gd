extends Node2D
## SAA-MCHANGA, EL AUTÓMATA RELOJ DE ARENA (jefe de la Calzada de los Obeliscos, el Valle del Ocaso; opción A
## elegida por Iam): un coloso de bronce con dos ampollas, la de arriba de luz y la de abajo de sombra, dentro de un
## aro de relojería. Guarda la Pesa del Sur en la Rotonda. No se mueve de su sitio.
##   1. SE CARGA: la arena de luz cae (CARGA s).
##   2. BARRE la Rotonda con un RAYO de sol que da la vuelta entera (BARRIDO s). Le quita 1 hoja a Maisha si la
##      toca, salvo si está a la SOMBRA de un obelisco (ocaso/sol.gd → `en_sombra()`).
##   3. Con la arena gastada, SE INCLINA (INCLINADO s): una CARGA SÍSMICA o girar un Reloj de Sol lo VUELCA.
##      Si no, se endereza y vuelve a empezar.
##   4. VOLCADO (VOLCADO s o GOLPES_VOLCADO golpes): el aro de relojería, al aire: cetro 1, semillas 2.
##   5. Con la mitad de la vida (FURIA): dos rayos, uno enfrente del otro, y barre más deprisa.
##   6. Vencido: la PESA DEL SUR («peso_sur») y un Farol de la Hora.
## Dibujo: arte/mundos/ocaso/calzada/saa.png (herramientas/pintar_calzada.py). Música: «jefe_saa».

signal destruido
signal vida_cambiada(nueva: int)

const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const DIBUJO := preload("res://arte/mundos/ocaso/calzada/saa.png")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const NOMBRE := "Saa-Mchanga, el Autómata Reloj de Arena"
const VIDA_MAX := 9
const CARGA := 2.2
const BARRIDO := 4.6
const BARRIDO_FURIA := 3.6
const INCLINADO := 3.5
const VOLCADO := 4.0
const GOLPES_VOLCADO := 3
const LARGO := 230.0
const ANCHO := 10.0

enum Fase { DORMIDO, CARGA, BARRE, INCLINADO, VOLCADO, VENCIDO }

var vida := VIDA_MAX
var fase := Fase.DORMIDO
var radio_carga := 30.0
var _t := 0.0
var _angulo := 0.0
var _golpes := 0
var _destello := 0.0
var _sprite: Sprite2D
var _rayo: Node2D
var _barra: CanvasLayer = null
var _sol: Node


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("sismicos")
	add_to_group("saa_mchanga")
	var cuerpo := StaticBody2D.new()
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(56, 14)
	forma.shape = caja
	forma.position = Vector2(0, -7)
	cuerpo.add_child(forma)
	add_child(cuerpo)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 6
	_sprite.offset = Vector2(0, -46)
	add_child(_sprite)
	_rayo = Node2D.new()
	_rayo.z_index = 2
	_rayo.draw.connect(_dibujar_rayo)
	add_child(_rayo)
	_sol = get_tree().get_first_node_in_group("sol")
	_sol.cambiada.connect(func(_h: int) -> void:
		if fase == Fase.INCLINADO:
			_volcar())


func furia() -> bool:
	return vida <= VIDA_MAX / 2


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	Sonido.musica("jefe_saa" if ResourceLoader.exists("res://audio/musica/jefe_saa.ogg") else "jefe_kivuli")
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	_cambiar(Fase.CARGA)


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


## La punta del rayo (o rayos) de ahora
func rayos() -> Array:
	if fase != Fase.BARRE:
		return []
	var r: Array = [Vector2.from_angle(_angulo) * LARGO]
	if furia():
		r.append(-r[0])
	return r


func _origen() -> Vector2:
	return global_position + Vector2(0, -6)


## ¿Toca un rayo ese punto?
func toca(p: Vector2) -> bool:
	for punta in rayos():
		if Geometry2D.get_closest_point_to_segment(p, _origen(), _origen() + punta).distance_to(p) < ANCHO:
			return true
	return false


func _process(delta: float) -> void:
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_sprite.rotation = 0.0
	match fase:
		Fase.DORMIDO:
			_sprite.frame = 0
		Fase.CARGA:
			_sprite.frame = 0 if _t < CARGA * 0.5 else 1
			if _t >= CARGA:
				_cambiar(Fase.BARRE)
				_angulo = randf() * TAU
				Sonido.efecto("saa_barre", 0.0, global_position)
		Fase.BARRE:
			_sprite.frame = 1
			var dura := BARRIDO_FURIA if furia() else BARRIDO
			_angulo += TAU / dura * delta
			var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
			if maisha and not maisha.get("esta_caida") and toca(maisha.global_position) and not _sol.en_sombra(maisha.global_position):
				maisha.call("recibir_danio", 1, global_position, "rayo")
			if _t >= dura:
				_cambiar(Fase.INCLINADO)
				Sonido.efecto("saa_inclina", -1.0, global_position)
		Fase.INCLINADO:
			_sprite.frame = 2
			_sprite.rotation = 0.14 + sin(_t * 9.0) * 0.02
			if _t >= INCLINADO:
				_cambiar(Fase.CARGA)
				Sonido.efecto("saa_endereza", -1.0, global_position)
		Fase.VOLCADO:
			_sprite.frame = 4 if _destello > 0.0 else 3
			if _t >= VOLCADO:
				_levantarse()
		Fase.VENCIDO:
			_sprite.frame = 5
	_rayo.queue_redraw()


func _volcar() -> void:
	_cambiar(Fase.VOLCADO)
	_golpes = 0
	Sonido.efecto("saa_vuelca", 0.0, global_position)
	Impacto.temblar(4.0, 0.5)
	Impacto.chispa(global_position + Vector2(0, -20), Vector2.UP, Color(1.0, 0.85, 0.5))


func _levantarse() -> void:
	_cambiar(Fase.CARGA)
	Sonido.efecto("saa_endereza", -1.0, global_position)


func recibir_carga(_direccion: Vector2) -> bool:
	if fase != Fase.INCLINADO:
		return false
	_volcar()
	return true


func expuesto() -> bool:
	return fase == Fase.VOLCADO


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if not expuesto():
		if fase != Fase.DORMIDO and fase != Fase.VENCIDO:
			Sonido.efecto("clinc", -2.0, global_position, 0.2)
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if not expuesto():
		return
	vida = maxi(0, vida - (2 if tipo == "explosion" else cantidad))
	_destello = 0.12
	vida_cambiada.emit(vida)
	Impacto.chispa(global_position + Vector2(0, -16), Vector2.UP, Color("ffd878"))
	if vida <= 0:
		morir()
		return
	_golpes += 1
	if _golpes >= GOLPES_VOLCADO:
		_levantarse()


func morir() -> void:
	if fase == Fase.VENCIDO:
		return
	_cambiar(Fase.VENCIDO)
	for g in ["golpeables", "daniables", "enemigos", "sismicos", "saa_mchanga"]:
		remove_from_group(g)
	Estado.marcar("saa_vencido")
	Estado.marcar("peso_sur")
	Bestiario.vencido("saa_mchanga", self)
	Sonido.efecto("saa_muere", 0.0, global_position)
	Sonido.musica("victoria")
	Impacto.temblar(6.0, 0.8)
	if _barra:
		_barra.queue_free()
		_barra = null
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 22
	astillas.position = global_position + Vector2(0, -30)
	get_parent().add_child(astillas)
	var farol: Node2D = RECOGIBLE.new()
	farol.objeto = "farol_hora"
	farol.marca = "farol/calzada_3"
	farol.dibujo = "res://arte/mundos/ocaso/mirador/farol.png"
	farol.color_halo = Color(1.0, 0.75, 0.35)
	farol.position = global_position + Vector2(0, 40)
	get_parent().add_child(farol)
	destruido.emit()


func _dibujar_rayo() -> void:
	var o := Vector2(0, -6)
	if fase == Fase.CARGA and _t > CARGA * 0.6:           # (el aviso: el ojo se enciende)
		_rayo.draw_circle(Vector2(0, -46), 5.0 + sin(_t * 30.0) * 1.5, Color(1.0, 0.9, 0.5, 0.7))
	for punta in rayos():
		var col := Color(1.0, 0.85, 0.45)
		_rayo.draw_line(o, o + punta, Color(col, 0.18), ANCHO * 2.2)
		_rayo.draw_line(o, o + punta, Color(col, 0.5), ANCHO * 0.8)
		_rayo.draw_line(o, o + punta, Color(1, 1, 0.92, 0.95), 2.0)
