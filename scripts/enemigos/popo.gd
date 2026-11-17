extends Node2D
## POPO DE OBSIDIANA, EL MURCIÉLAGO RESONANTE (Asterhaul, la Aguja Caída): revolotea alrededor de su sitio, fuera
## del alcance del cetro.
##   - Si ve a Maisha (VE px), AVISA (toma aire, las orejas tiesas) y CHILLA: un anillo de ultrasonido que se abre
##     hasta CHILLIDO px. Si la alcanza, la ATURDE (los controles van al revés ATURDE s: malo en un puente de
##     cristal) y se le tira en PICADO (1 hoja).
##   - Si en ese momento hay un monolito cantando que le alcance a ÉL (asterhaul/monolito.gd), su propio eco le
##     vuelve: cae al suelo ATURDIDO (CAIDO s): ahí entran el cetro (1) y las semillas (2). 2 de vida.
##   - Y si el que canta alcanza a MAISHA, el chillido no le hace nada.
## Dibujo: arte/mundos/asterhaul/aguja/popo.png (herramientas/pintar_aguja.py).

signal destruido

const DIBUJO := preload("res://arte/mundos/asterhaul/aguja/popo.png")
const MONOLITO := preload("res://scripts/mundo/asterhaul/monolito.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIDA := 2
const VE := 112.0
const AVISO := 0.7
const CHILLIDO := 100.0
const ONDA_VEL := 190.0
const ATURDE := 1.6
const CADA := 3.4
const PICADO_VEL := 130.0
const CAIDO := 4.5
const ALTURA := 20.0

enum Fase { VUELA, AVISA, CHILLA, PICADO, CAIDO }

var vida := VIDA
var fase := Fase.VUELA
var _puesto := Vector2.ZERO
var _t := 0.0
var _tiempo := 0.0
var _cd := 1.5
var _onda := 0.0
var _dio := false
var _toco := false
var _destello := 0.0
var _muriendo := false
var _sprite: Sprite2D
var _sombra: Node2D
var _efectos: Node2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("popos")
	_puesto = position
	_sombra = Node2D.new()
	_sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	_sombra.set("ancho", 8.0)
	add_child(_sombra)
	_efectos = Node2D.new()
	_efectos.z_index = 2
	_efectos.draw.connect(_dibujar_onda)
	add_child(_efectos)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -12)
	add_child(_sprite)
	_tiempo = randf() * 4.0


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_efectos.queue_redraw()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var d := (maisha.global_position - global_position) if maisha else Vector2.INF
	match fase:
		Fase.VUELA:
			# revolotea en ocho alrededor de su sitio
			var meta := _puesto + Vector2(sin(_tiempo * 1.1) * 22.0, sin(_tiempo * 2.2) * 9.0)
			global_position = global_position.move_toward(meta, 46.0 * delta)
			_cd -= delta
			if _cd <= 0.0 and maisha and not maisha.get("esta_caida") and d.length() < VE:
				_cambiar(Fase.AVISA)
		Fase.AVISA:
			if _t >= AVISO:
				_chillar()
		Fase.CHILLA:
			_onda += ONDA_VEL * delta
			if not _dio and maisha and d.length() <= _onda:
				_dio = true
				# (si a Maisha la alcanza un monolito que canta, el chillido no puede con ella)
				if MONOLITO.que_suena_en(get_tree(), maisha.global_position) == null:
					maisha.set("mareo", ATURDE)
					_toco = false
					_cambiar(Fase.PICADO)
					Sonido.efecto("kipanga_picado", -6.0, global_position, 0.3)
					return
			if _onda >= CHILLIDO:
				_cd = CADA
				_cambiar(Fase.VUELA)
		Fase.PICADO:
			if maisha and d.length() > 4.0:
				global_position += d.normalized() * PICADO_VEL * delta
			if maisha and not _toco and d.length() < 10.0:
				_toco = true
				maisha.call("recibir_danio", 1, global_position, "contacto")
			if _toco or _t >= 1.3:
				_cd = CADA
				_cambiar(Fase.VUELA)
		Fase.CAIDO:
			if _t >= CAIDO:
				_cd = 1.0
				_cambiar(Fase.VUELA)
	_dibujar()


func _chillar() -> void:
	Sonido.efecto("popo_chillido", 0.0, global_position, 0.1)
	# con un monolito cantando encima, el eco le vuelve a él
	if MONOLITO.que_suena_en(get_tree(), global_position) != null:
		_cambiar(Fase.CAIDO)
		Sonido.efecto("kaa_vuelca", -2.0, global_position)
		Impacto.chispa(global_position + Vector2(0, -ALTURA), Vector2.UP, Color("ffd878"))
		return
	_onda = 6.0
	_dio = false
	_cambiar(Fase.CHILLA)


func _dibujar() -> void:
	var alto := ALTURA
	_sprite.rotation = 0.0
	match fase:
		Fase.VUELA:
			_sprite.frame = int(_tiempo * 9.0) % 2
		Fase.AVISA, Fase.CHILLA:
			_sprite.frame = 2
			_sprite.position.x = roundf(sin(_tiempo * 60.0)) if fase == Fase.AVISA else 0.0
		Fase.PICADO:
			_sprite.frame = 1
			alto = maxf(4.0, ALTURA - _t * 30.0)
		Fase.CAIDO:
			_sprite.frame = 4 if _destello > 0.0 else 3
			alto = 0.0
			_sprite.rotation = sin(_tiempo * (5.0 if _t < CAIDO - 1.0 else 18.0)) * 0.08
	_sprite.position.y = -alto


## El chillido: dos anillos finos de ultrasonido que se abren
func _dibujar_onda() -> void:
	if fase != Fase.CHILLA:
		return
	var a := 1.0 - _onda / CHILLIDO
	for k in 2:
		var r := _onda - k * 9.0
		if r > 2.0:
			_efectos.draw_arc(Vector2(0, -ALTURA), r, 0, TAU, 32, Color(0.75, 0.96, 1.0, 0.8 * a), 1.0)


# --- Daño ------------------------------------------------------------------------

func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if _muriendo or fase != Fase.CAIDO:
		return false                                  # (en el aire no le llega el cetro)
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo or fase != Fase.CAIDO:
		return
	vida -= 2 if tipo == "explosion" else cantidad
	_destello = 0.12
	Impacto.chispa(global_position + Vector2(0, -6), Vector2.UP, Color("6ad0f0"))
	if vida <= 0:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("popo", self)
	Sonido.efecto("roca_romper", -4.0, global_position)
	for g in ["enemigos", "golpeables", "daniables", "popos"]:
		remove_from_group(g)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 10
	astillas.position = global_position + Vector2(0, -6)
	get_parent().add_child(astillas)
	destruido.emit()
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.15), 0.3)
	t.tween_property(self, "modulate:a", 0.0, 0.4)
	t.chain().tween_callback(queue_free)
