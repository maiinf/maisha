extends Node2D
## KAA-JIWE, EL CANGREJO DE GEODA (Asterhaul): una piedra redonda con patas. Por fuera es roca; por dentro, ámbar.
##   - RONDA despacio alrededor de su sitio. Si ve a Maisha (VE px), AVISA (se encoge, las pinzas delante) y
##     EMBISTE en línea recta: 1 hoja si la pilla. Si se estampa contra la pared, se queda atontado más rato.
##   - El cetro, las semillas y los sigilos rebotan en la coraza (¡clinc!).
##   - La CARGA SÍSMICA lo VUELCA (está en «sismicos»): panza arriba VOLCADO s, con la geoda al aire: ahí entran el
##     cetro (1) y las semillas (2). 3 de vida. Si no se le vence a tiempo, se da la vuelta.
## Dibujo: arte/mundos/asterhaul/desfiladero/kaa_jiwe.png (herramientas/pintar_desfiladero.py).

signal destruido

const DIBUJO := preload("res://arte/mundos/asterhaul/desfiladero/kaa_jiwe.png")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIDA := 3
const ANDA := 16.0
const EMBISTE := 125.0
const VE := 70.0
const AVISO := 0.55
const DURA_EMBISTE := 0.75
const DESCANSO := 1.1
const ATONTADO := 2.0
const VOLCADO := 4.5

enum Fase { RONDA, AVISA, EMBISTE, DESCANSA, VOLCADO }

var vida := VIDA
var fase := Fase.RONDA
var radio_carga := 4.0
var _puesto := Vector2.ZERO
var _meta := Vector2.ZERO
var _dir := Vector2.ZERO
var _t := 0.0
var _descanso := DESCANSO
var _tiempo := 0.0
var _destello := 0.0
var _muriendo := false
var _toco := false
var _filas: PackedStringArray
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("sismicos")
	add_to_group("kaa_jiwes")
	_puesto = position
	_meta = position
	_filas = get_tree().current_scene.get_node("Region")._filas
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 12.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -11)
	add_child(_sprite)
	_tiempo = randf() * 3.0


func _es_suelo(p: Vector2) -> bool:
	var x := floori(p.x / 16.0)
	var y := floori(p.y / 16.0)
	return y >= 0 and y < _filas.size() and x >= 0 and x < _filas[y].length() and _filas[y][x] != "0"


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


## Da un paso; devuelve false si se lo impide la pared
func _mover(paso: Vector2) -> bool:
	if paso == Vector2.ZERO or not _es_suelo(global_position + paso + paso.normalized() * 9.0):
		return false
	global_position += paso
	return true


func _process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var d := (maisha.global_position - global_position) if maisha else Vector2.INF
	match fase:
		Fase.RONDA:
			if maisha and not maisha.get("esta_caida") and d.length() < VE:
				_dir = d.normalized()
				_cambiar(Fase.AVISA)
				Sonido.efecto("clinc", -6.0, global_position, 0.3)
			else:
				if global_position.distance_to(_meta) < 2.0 or _t > 3.0:
					_meta = _puesto + Vector2(randf_range(-28, 28), randf_range(-18, 18))
					_t = 0.0
				var hacia := _meta - global_position
				if hacia.length() > 1.0 and not _mover(hacia.normalized() * ANDA * delta):
					_meta = _puesto
		Fase.AVISA:
			if _t >= AVISO:
				_toco = false
				_cambiar(Fase.EMBISTE)
				Sonido.efecto("kifaru_embiste", -6.0, global_position, 0.2)
		Fase.EMBISTE:
			if not _mover(_dir * EMBISTE * delta):
				Impacto.temblar(2.0, 0.15)
				Sonido.efecto("cosechadora_choque", -8.0, global_position)
				_descanso = ATONTADO
				_cambiar(Fase.DESCANSA)
			elif _t >= DURA_EMBISTE:
				_descanso = DESCANSO
				_cambiar(Fase.DESCANSA)
			if not _toco and maisha and d.length() < 13.0:
				_toco = true
				maisha.call("recibir_danio", 1, global_position, "contacto")
		Fase.DESCANSA:
			if _t >= _descanso:
				_cambiar(Fase.RONDA)
		Fase.VOLCADO:
			if _t >= VOLCADO:
				Sonido.efecto("cangrejo_vuelca", -6.0, global_position, 0.2)
				_cambiar(Fase.RONDA)
	_dibujar()


func _dibujar() -> void:
	_sprite.position = Vector2.ZERO
	_sprite.flip_h = false
	if fase == Fase.VOLCADO:
		_sprite.frame = 4 if _destello > 0.0 else 3
		# (las patas al aire: se balancea; al final avisa de que se va a dar la vuelta)
		_sprite.rotation = sin(_tiempo * (5.0 if _t < VOLCADO - 1.0 else 18.0)) * 0.08
		return
	_sprite.rotation = 0.0
	if fase == Fase.AVISA:
		_sprite.frame = 2
		_sprite.position.x = roundf(sin(_tiempo * 70.0))
	elif fase == Fase.EMBISTE:
		_sprite.frame = 2
	elif fase == Fase.DESCANSA:
		_sprite.frame = 0
	else:
		_sprite.frame = int(_tiempo * 4.0) % 2


# --- Carga y daño ---------------------------------------------------------------

## La Carga Sísmica lo vuelca
func recibir_carga(direccion: Vector2) -> bool:
	if _muriendo:
		return false
	_cambiar(Fase.VOLCADO)
	Sonido.efecto("cangrejo_vuelca", 0.0, global_position)
	_mover(direccion * 6.0)
	return true


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if _muriendo:
		return false
	if fase != Fase.VOLCADO:
		_rebotar()
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo:
		return
	if fase != Fase.VOLCADO:
		_rebotar()
		return
	vida -= 2 if tipo == "explosion" else cantidad
	_destello = 0.12
	Impacto.chispa(global_position + Vector2(0, -10), Vector2.UP, Color("ffd878"))
	if vida > 0:
		Sonido.efecto("roca_romper", -8.0, global_position, 0.3)
	else:
		morir()


func _rebotar() -> void:
	Sonido.efecto("clinc", -2.0, global_position, 0.2)
	Impacto.chispa(global_position + Vector2(0, -12), Vector2.UP, Color("b89468"))


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("kaa_jiwe", self)
	Sonido.efecto("roca_romper", -2.0, global_position)
	for g in ["enemigos", "golpeables", "daniables", "sismicos", "kaa_jiwes"]:
		remove_from_group(g)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 14
	astillas.position = global_position + Vector2(0, -10)
	get_parent().add_child(astillas)
	destruido.emit()
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.15), 0.3)
	t.tween_property(self, "modulate:a", 0.0, 0.4)
	t.chain().tween_callback(queue_free)
