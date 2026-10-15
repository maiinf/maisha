extends Node
## IMPACTO: lo que hace que un golpe «se sienta». Se usa desde cualquier sitio:
##   Impacto.pausa(0.05)              congela el juego un instante (al acertar un golpe)
##   Impacto.temblar(2.0, 0.2)        tiembla la cámara
##   Impacto.chispa(pos, direccion)   estrella de chispas donde acierta el cetro
##   Impacto.onda(pos)                destello, onda, humo y chispas de una explosión
##   Impacto.fogonazo(color, a)       la pantalla entera se tiñe un instante (daño, Corazón roto)
##   Impacto.poner_lenta(0.35)        cámara lenta (1.0 = velocidad normal)
## La velocidad del juego (Engine.time_scale) solo la toca este script: cámara lenta × parón de impacto. Así un parón
## que empieza durante la cámara lenta no puede dejar el juego lento para siempre al terminar.
## Todo se puede apagar con «activo = false» (para quien se maree con los temblores).

const CHISPA := preload("res://scripts/efectos/chispa_golpe.gd")
const ONDA := preload("res://scripts/efectos/onda_explosion.gd")

var activo := true
var temblores := true

var _pausas := 0
var _lenta := 1.0                  # la cámara lenta (1.0 = normal)
var _base := 1.0                   # la velocidad sin efectos (las pruebas la suben para ir más deprisa)
var _temblor := 0.0
var _temblor_dura := 0.0
var _temblor_tiempo := 0.0
var _capa: CanvasLayer
var _velo: ColorRect
var _lenta_desde := 0.0            # segundos reales en cámara lenta (si se olvida quitarla, se quita sola)


const AJUSTES := "user://ajustes.cfg"


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var cfg := ConfigFile.new()
	if cfg.load(AJUSTES) == OK:
		temblores = bool(cfg.get_value("juego", "temblores", true))
	_capa = CanvasLayer.new()
	_capa.layer = 12
	add_child(_capa)
	_velo = ColorRect.new()
	_velo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_velo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_velo.color = Color(1, 1, 1, 0)
	_capa.add_child(_velo)


## Activa o quita los temblores de pantalla (se guarda)
func poner_temblores(si: bool) -> void:
	temblores = si
	if not si:
		_temblor = 0.0
	var cfg := ConfigFile.new()
	cfg.load(AJUSTES)
	cfg.set_value("juego", "temblores", si)
	cfg.save(AJUSTES)


## Congela el juego unos instantes (en tiempo real, aunque el juego vaya más rápido o más lento)
func pausa(segundos: float) -> void:
	if not activo or segundos <= 0.0:
		return
	_tomar_base()
	_pausas += 1
	_aplicar_velocidad()
	await get_tree().create_timer(segundos, true, false, true).timeout
	_pausas = maxi(0, _pausas - 1)
	_aplicar_velocidad()


## Cámara lenta (1.0 = velocidad normal)
func poner_lenta(factor: float) -> void:
	_tomar_base()
	_lenta = clampf(factor, 0.05, 1.0)
	_aplicar_velocidad()


## Todo a velocidad normal (al cambiar de escena, por si algo se quedó a medias)
func restablecer_velocidad() -> void:
	if _pausas == 0 and is_equal_approx(_lenta, 1.0):
		return                         # (no hay nada a medias: no se toca)
	_lenta = 1.0
	_pausas = 0
	_aplicar_velocidad()


## Si no hay ningún efecto en marcha, la velocidad que haya ahora es la de base
func _tomar_base() -> void:
	if _pausas == 0 and is_equal_approx(_lenta, 1.0):
		_base = Engine.time_scale


func _aplicar_velocidad() -> void:
	Engine.time_scale = _base * _lenta * (0.05 if _pausas > 0 else 1.0)


func temblar(fuerza: float, segundos: float) -> void:
	if not activo or not temblores:
		return
	# si ya está temblando más fuerte, no lo rebaja
	var queda := _temblor * (1.0 - _temblor_tiempo / maxf(_temblor_dura, 0.001))
	if fuerza >= queda:
		_temblor = fuerza
		_temblor_dura = segundos
		_temblor_tiempo = 0.0


func chispa(pos: Vector2, direccion: Vector2, color := Color("fff3c4")) -> void:
	if not activo:
		return
	var nodo: Node2D = CHISPA.new()
	nodo.global_position = pos
	nodo.direccion = direccion
	nodo.color = color
	_al_mundo(nodo)


func onda(pos: Vector2, fuerza := 1.0) -> void:
	if not activo:
		return
	var nodo: Node2D = ONDA.new()
	nodo.global_position = pos
	nodo.fuerza = fuerza
	_al_mundo(nodo)


func fogonazo(color: Color, alfa := 0.35, segundos := 0.25) -> void:
	if not activo:
		return
	_velo.color = Color(color, alfa)
	var t := create_tween()
	t.tween_property(_velo, "color:a", 0.0, segundos)


func _al_mundo(nodo: Node2D) -> void:
	var escena := get_tree().current_scene
	if escena:
		escena.add_child(nodo)


func _process(delta: float) -> void:
	# seguridad: una cámara lenta no dura nunca tanto; si alguien olvidó quitarla, se quita
	if _lenta < 1.0:
		_lenta_desde += delta / maxf(Engine.time_scale, 0.001)
		if _lenta_desde > 8.0:
			push_warning("Impacto: la cámara lenta llevaba demasiado tiempo puesta; se quita")
			_lenta = 1.0
			_aplicar_velocidad()
	else:
		_lenta_desde = 0.0
	var camara := get_viewport().get_camera_2d()
	if _temblor <= 0.0:
		return
	# el temblor corre en tiempo real (no se para con la pausa del golpe)
	var real := delta / maxf(Engine.time_scale, 0.001)
	_temblor_tiempo += real
	var resto := 1.0 - _temblor_tiempo / maxf(_temblor_dura, 0.001)
	if resto <= 0.0:
		_temblor = 0.0
		if camara:
			camara.offset = Vector2.ZERO
		return
	if camara:
		var f := _temblor * resto
		camara.offset = Vector2(randf_range(-f, f), randf_range(-f, f)).round()
