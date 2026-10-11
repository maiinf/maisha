extends StaticBody2D
## CORAZÓN DE GIZA (el Núcleo): un tocón de raíz de piedra con el ojo violeta de Giza.
## Es donde Giza se agarra a la raíz.
## Solo lo dañan las explosiones (el cetro rebota). Al romperse, la zona se purga.

signal destruido

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")

var vida: int = R.NUCLEO_VIDA
var vida_maxima: int = R.NUCLEO_VIDA
var variante := "raiz"            # el mundo (arte/zonas/<variante>/nucleo.png)
var pequeno := false              # el de las zonas de práctica: más pequeño y con menos vida
var _pupila: Node2D
var _ojo := Vector2(0, -12)       # dónde está el ojo de Giza en el dibujo
var _destello := 0.0
var _tiempo := 0.0
var _roto := false
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("daniables")
	add_to_group("golpeables")
	add_to_group("nucleos")
	collision_layer = 1
	var forma := CollisionShape2D.new()
	var circulo := CircleShape2D.new()
	circulo.radius = 9.0
	forma.shape = circulo
	forma.position = Vector2(0, -3)
	add_child(forma)
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 14.0)
	add_child(sombra)
	if pequeno:
		vida_maxima = R.NUCLEO_VIDA_PEQUENO
		vida = vida_maxima
		circulo.radius = 7.0
		sombra.set("ancho", 10.0)
		_ojo = Vector2(0, -11)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/zonas/%s/%s.png" % [variante, "nucleo_pequeno" if pequeno else "nucleo"])
	_sprite.hframes = 4
	_sprite.offset = Vector2(0, -11 if pequeno else -13)
	add_child(_sprite)
	# la pupila del ojo de Giza: sigue a Maisha
	_pupila = Node2D.new()
	add_child(_pupila)
	_pupila.draw.connect(_dibujar_pupila)


func _process(delta: float) -> void:
	_tiempo += delta
	_destello = maxf(0.0, _destello - delta)
	if _roto:
		return
	var grietas := 0 if vida >= vida_maxima else (2 if vida <= 1 else 1)
	_sprite.frame = 3 if _destello > 0.0 else grietas
	_pupila.queue_redraw()
	# late con un brillo violeta
	var pulso := 0.5 + 0.5 * sin(_tiempo * 3.0)
	_sprite.modulate = Color(1.0 + 0.15 * pulso, 1.0, 1.0 + 0.25 * pulso)
	queue_redraw()


## Halo violeta en el suelo que late: marca el objetivo de la zona desde lejos
func _draw() -> void:
	if _roto:
		return
	var pulso := 0.5 + 0.5 * sin(_tiempo * 3.0)
	var radio := 19.0 + 3.0 * pulso
	for anillo in 3:
		var r := radio - anillo * 4.0
		var puntos := int(r * 2.2)
		for i in puntos:
			var a := TAU * i / puntos
			var p := (Vector2(cos(a) * r, sin(a) * r * 0.5)).round()
			draw_rect(Rect2(p, Vector2.ONE), Color(0.66, 0.33, 0.84, 0.25 + 0.2 * anillo * pulso))


func _dibujar_pupila() -> void:
	if _roto or _destello > 0.0:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var mira := Vector2.ZERO
	if maisha:
		var d := maisha.global_position - (global_position + _ojo)
		mira = Vector2(clampf(d.x / 40.0, -1.0, 1.0), clampf(d.y / 30.0, -1.0, 1.5)).round()
	if pequeno:
		mira = mira.clamp(Vector2(-1, -1), Vector2(1, 1))
	var p := _ojo + mira + Vector2(-1, -1)
	_pupila.draw_rect(Rect2(p - Vector2(1, 0), Vector2(4, 2)), Color("1a0d24"))
	_pupila.draw_rect(Rect2(p, Vector2(2, 2)), Color("fff8e8"))


func reiniciar() -> void:
	vida = vida_maxima
	_destello = 0.0


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	_destello = 0.05     # «clinc»: el cetro rebota y no le hace daño
	Sonido.efecto("clinc", 0.0, global_position)
	return false


func recibir_danio(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _roto or tipo != "explosion":
		return
	Sonido.efecto("corazon_golpeado", 0.0, global_position)
	vida -= 1
	_destello = 0.12
	if vida <= 0:
		_romper()


func _romper() -> void:
	Impacto.pausa(0.12)
	Impacto.temblar(4.5, 0.5)
	Impacto.fogonazo(Color("f1d8fb"), 0.45, 0.6)
	_roto = true
	Sonido.efecto("corazon_roto")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	collision_layer = 0
	destruido.emit()
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 9 if pequeno else 16
	astillas.chispas = 8
	astillas.fuerza = 90.0
	astillas.position = global_position + _ojo * 0.5
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.6, 0.1), 0.35).set_trans(Tween.TRANS_BACK)
	t.tween_property(self, "modulate:a", 0.0, 0.4)
	t.chain().tween_callback(queue_free)
