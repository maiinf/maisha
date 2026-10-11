extends Node
## IMPACTO: lo que hace que un golpe «se sienta». Se usa desde cualquier sitio:
##   Impacto.pausa(0.05)              congela el juego un instante (al acertar un golpe)
##   Impacto.temblar(2.0, 0.2)        tiembla la cámara
##   Impacto.chispa(pos, direccion)   estrella de chispas donde acierta el cetro
##   Impacto.onda(pos)                destello, onda, humo y chispas de una explosión
##   Impacto.fogonazo(color, a)       la pantalla entera se tiñe un instante (daño, Corazón roto)
## Todo se puede apagar con «activo = false» (para quien se maree con los temblores).

const CHISPA := preload("res://scripts/efectos/chispa_golpe.gd")
const ONDA := preload("res://scripts/efectos/onda_explosion.gd")

var activo := true
var temblores := true

var _pausas := 0
var _escala := 1.0
var _temblor := 0.0
var _temblor_dura := 0.0
var _temblor_tiempo := 0.0
var _capa: CanvasLayer
var _velo: ColorRect


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
	if _pausas == 0:
		_escala = Engine.time_scale
	_pausas += 1
	Engine.time_scale = _escala * 0.05
	await get_tree().create_timer(segundos, true, false, true).timeout
	_pausas -= 1
	if _pausas <= 0:
		_pausas = 0
		Engine.time_scale = _escala


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
