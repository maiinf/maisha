extends CharacterBody2D
## CANGREJO DE HERRUMBRE: el enemigo de la Orilla de Juncos. Un cangrejo de caparazón de hierro oxidado, con grietas
## de Giza y dos pinzas grandes.
##   - ANDA de lado hacia Maisha. Su caparazón y sus pinzas lo aguantan todo: el cetro REBOTA («clinc») y él se pone
##     en guardia un momento.
##   - Cuando la tiene cerca, AVISA (levanta las pinzas, abiertas) y PELLIZCA dando un pasito hacia delante: hace
##     daño si Maisha sigue delante.
##   - Después de pellizcar se queda EXPUESTO un instante, con las pinzas abiertas: el cetro le quita 1.
##   - La explosión de una semilla lo VUELCA: panza arriba, pataleando, un buen rato. Volcado, el cetro le quita 2.
##     Las raíces de la semilla lo sujetan volcado más tiempo. El Latido lo empuja.
## Dibujo: arte/mundos/raiz/orilla/cangrejo.png (herramientas/pintar_orilla.py): 0-1 andando · 2 guardia ·
## 3 panza arriba · 4 pellizcando · 5 golpeado (blanco en el juego).

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")

enum Fase { ANDA, GUARDIA, AVISA, PELLIZCA, EXPUESTO, VOLCADO }

var variante := "raiz"
var zona: Node = null
var vida := R.CANGREJO_VIDA
var fase := Fase.ANDA
var _t := 0.0
var _tiempo := 0.0
var _destello := 0.0
var _empuje := Vector2.ZERO
var _enraizado := 0.0
var _muriendo := false
var _ya_pellizco := false
var _hacia_pellizco := Vector2.RIGHT
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("daniables")
	add_to_group("golpeables")
	collision_layer = 2
	collision_mask = 1
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(16, 7)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 10.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/mundos/raiz/orilla/cangrejo.png")
	_sprite.hframes = 6
	_sprite.centered = false
	_sprite.offset = Vector2(-13, -19)
	add_child(_sprite)
	Sonido.efecto("cangrejo_chasca", -4.0, global_position, 0.15)


func _cambiar(nueva: int) -> void:
	fase = nueva
	_t = 0.0


func _physics_process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	if _muriendo:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var mov := Vector2.ZERO
	match fase:
		Fase.ANDA:
			if maisha:
				var hacia := maisha.global_position - global_position
				# de lado: deprisa en horizontal, despacio en vertical
				mov = Vector2(signf(hacia.x) * R.CANGREJO_VELOCIDAD if absf(hacia.x) > 4.0 else 0.0,
						clampf(hacia.y, -1.0, 1.0) * R.CANGREJO_VELOCIDAD * 0.45)
				if hacia.length() < R.CANGREJO_ALCANCE * 1.3:
					_cambiar(Fase.AVISA)
					_hacia_pellizco = hacia.normalized()
					Sonido.efecto("cangrejo_chasca", 0.0, global_position)
		Fase.GUARDIA:
			if _t >= R.CANGREJO_GUARDIA:
				_cambiar(Fase.ANDA)
		Fase.AVISA:
			if _t >= R.CANGREJO_AVISO:
				_ya_pellizco = false
				_cambiar(Fase.PELLIZCA)
		Fase.PELLIZCA:
			# da un pasito hacia delante al pellizcar
			mov = _hacia_pellizco * 70.0 if _t < 0.12 else Vector2.ZERO
			if not _ya_pellizco and maisha and _t >= 0.1:
				_ya_pellizco = true
				if maisha.global_position.distance_to(global_position) < R.CANGREJO_ALCANCE:
					maisha.call("recibir_danio", 1, global_position, "contacto")
			if _t >= 0.25:
				_cambiar(Fase.EXPUESTO)
		Fase.EXPUESTO:
			if _t >= R.CANGREJO_EXPUESTO:
				_cambiar(Fase.ANDA)
		Fase.VOLCADO:
			if _t >= R.CANGREJO_VOLCADO and _enraizado <= 0.0:
				_cambiar(Fase.GUARDIA)
				Sonido.efecto("cangrejo_chasca", 0.0, global_position)
	velocity = mov + _empuje
	_empuje = _empuje.move_toward(Vector2.ZERO, 400.0 * delta)
	move_and_slide()
	if zona:
		global_position = zona.limitar(global_position)
	_animar()


func _animar() -> void:
	var frame := 0
	match fase:
		Fase.ANDA:
			frame = int(_tiempo * 8.0) % 2
		Fase.GUARDIA:
			frame = 2
		Fase.AVISA:
			frame = 4 if fmod(_tiempo * 10.0, 1.0) < 0.5 else 2
		Fase.PELLIZCA, Fase.EXPUESTO:
			frame = 4
		Fase.VOLCADO:
			frame = 3
	if _destello > 0.0:
		frame = 5
	_sprite.frame = frame
	_sprite.modulate = Color(3, 3, 3) if _destello > 0.0 else Color.WHITE
	# volcado, patalea (un temblor)
	_sprite.position.x = sin(_tiempo * 30.0) * 0.6 if fase == Fase.VOLCADO else 0.0
	queue_redraw()


func _draw() -> void:
	if fase == Fase.VOLCADO:
		# mareado: estrellitas que dan vueltas
		for k in 3:
			var a := _tiempo * 5.0 + k * TAU / 3.0
			var p := Vector2(cos(a) * 7.0, -16.0 + sin(a) * 2.0).round()
			draw_rect(Rect2(p, Vector2(2, 2)), Color("fff3c4"))


func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo:
		return false
	if fase == Fase.VOLCADO:
		_herir(danio + 1)
		return true
	if fase == Fase.EXPUESTO:
		_empuje = direccion * R.GOLPE_EMPUJE * 0.5
		_herir(danio)
		return true
	# rebota en el caparazón y en las pinzas
	_destello = 0.04
	Sonido.efecto("clinc", 0.0, global_position)
	if fase == Fase.ANDA:
		_cambiar(Fase.GUARDIA)
	return false


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo:
		return
	if tipo == "explosion":
		# la explosión le da la vuelta (y le hace un poco de daño)
		_herir(1)
		if not _muriendo:
			_cambiar(Fase.VOLCADO)
			Sonido.efecto("cangrejo_vuelca", 0.0, global_position)


func _herir(cuanto: int) -> void:
	vida -= cuanto
	_destello = 0.12
	if vida > 0:
		Sonido.efecto("petrino_golpeado", 0.0, global_position)
	else:
		morir()


func enraizar(segundos: float) -> void:
	if fase == Fase.VOLCADO:
		_enraizado = maxf(_enraizado, segundos)


func esta_enraizado() -> bool:
	return _enraizado > 0.0


func empujar(fuerza: Vector2) -> void:
	_empuje = fuerza


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("cangrejo", self)
	Sonido.efecto("petrino_muere", 0.0, global_position)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 10
	astillas.chispas = 4
	astillas.position = global_position + Vector2(0, -8)
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.3), 0.3)
	t.tween_property(_sprite, "modulate:a", 0.0, 0.35)
	t.chain().tween_callback(queue_free)
