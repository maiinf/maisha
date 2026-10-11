extends CharacterBody2D
## JABALÍ DE HIERRO: el «cazador» de Raíz. Giza le ha cubierto el lomo de placas de hierro.
##   - Deambula despacio. Si ve a Maisha en su misma fila o columna (y no muy lejos), escarba un instante
##     y EMBISTE en línea recta, muy deprisa.
##   - Al chocar con algo (un árbol, una roca, los brotes de una semilla, el borde de la zona) se queda
##     ATURDIDO un rato: es el momento de golpearle. Mientras no está aturdido, el cetro rebota en su hierro.
##   - Las explosiones sí le hacen daño siempre. Las raíces de una semilla lo sujetan.
## Dibujo: arte/zonas/raiz/jabali.png (herramientas/dibujar_jabali.py).

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const FILAS := {"lado": 0, "abajo": 1, "arriba": 2}

const VIDA := 4
const VELOCIDAD := 22.0
const EMBESTIDA := 165.0
const VE_A := 150.0                 # hasta dónde ve en línea recta
const ALINEADO := 9.0               # cuánto puede desviarse de la fila o columna de Maisha
const PREPARA := 0.55               # escarba antes de lanzarse (el aviso)
const ATURDIDO_CHOQUE := 1.6
const DESCANSO := 1.2               # tras embestir, no vuelve a lanzarse enseguida
const DANIO_EMBESTIDA := 2

enum Fase { ANDAR, PREPARAR, EMBESTIR, ATURDIDO }

var variante := "raiz"
var zona: Node = null
var vida := VIDA
var fase := Fase.ANDAR
var _t_fase := 0.0
var _dir := Vector2.RIGHT          # hacia dónde embiste
var _mira := "lado"
var _rumbo := Vector2.ZERO
var _cambio_rumbo := 0.0
var _descanso := 0.0
var _enraizado := 0.0
var _destello := 0.0
var _empuje := Vector2.ZERO
var _tiempo := 0.0
var _muriendo := false
var _recorrido := 0.0
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
	caja.size = Vector2(14, 7)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	add_child(forma)
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 11.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/zonas/%s/jabali.png" % variante)
	_sprite.hframes = 5
	_sprite.vframes = 3
	_sprite.offset = Vector2(0, -10)
	add_child(_sprite)
	_tiempo = randf() * 2.0
	_descanso = 1.0
	Sonido.efecto("petrino_aparece", 0.0, global_position, 0.1)


func _physics_process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_t_fase += delta
	_destello = maxf(0.0, _destello - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	_descanso = maxf(0.0, _descanso - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var mov := Vector2.ZERO
	match fase:
		Fase.ANDAR:
			mov = _andar(maisha, delta)
		Fase.PREPARAR:
			if _t_fase >= PREPARA:
				_cambiar(Fase.EMBESTIR)
				_recorrido = 0.0
				Sonido.efecto("petrino_embiste", 0.0, global_position)
		Fase.EMBESTIR:
			mov = _dir * EMBESTIDA
		Fase.ATURDIDO:
			if _t_fase >= ATURDIDO_CHOQUE:
				_cambiar(Fase.ANDAR)
				_descanso = DESCANSO
	if _enraizado > 0.0:
		mov = Vector2.ZERO
		if fase == Fase.EMBESTIR:
			_chocar(false)
	if fase == Fase.EMBESTIR:
		# los brotes de una semilla le cortan el paso como un muro
		var registro := get_tree().get_first_node_in_group("registro_brotes")
		if registro and registro.hay_brote(R.casilla_de(global_position + _dir * 9.0)):
			_chocar(true)
			mov = Vector2.ZERO
	var antes := global_position
	velocity = mov + _empuje
	_empuje = _empuje.move_toward(Vector2.ZERO, 500.0 * delta)
	move_and_slide()
	if zona:
		global_position = zona.limitar(global_position)
	if fase == Fase.EMBESTIR:
		var avanzado := global_position.distance_to(antes)
		_recorrido += avanzado
		# se ha parado contra algo (o el borde de la zona no le deja seguir)
		if get_slide_collision_count() > 0 or avanzado < EMBESTIDA * delta * 0.35:
			_chocar(true)
		elif _recorrido > VE_A * 1.6:
			_cambiar(Fase.ANDAR)
			_descanso = DESCANSO
	# daño por contacto (más fuerte si embiste)
	if maisha and global_position.distance_to(maisha.global_position) < 12.0 and fase != Fase.ATURDIDO:
		var danio := DANIO_EMBESTIDA if fase == Fase.EMBESTIR else 1
		if maisha.call("recibir_danio", danio, global_position, "contacto"):
			_empuje = (global_position - maisha.global_position).normalized() * 90.0
			if fase == Fase.EMBESTIR:
				_cambiar(Fase.ANDAR)
				_descanso = DESCANSO
	_animar(mov)
	queue_redraw()


func _andar(maisha: Node2D, delta: float) -> Vector2:
	# ¿Maisha en su fila o en su columna, y cerca? → escarba y embiste
	if maisha and not maisha.get("esta_caida") and _descanso <= 0.0 and _enraizado <= 0.0:
		var d := maisha.global_position - global_position
		if d.length() < VE_A and (absf(d.y) < ALINEADO or absf(d.x) < ALINEADO) and d.length() > 14.0:
			_dir = Vector2(signf(d.x), 0) if absf(d.y) < ALINEADO else Vector2(0, signf(d.y))
			_cambiar(Fase.PREPARAR)
			Sonido.efecto("jabali_grunido", 0.0, global_position, 0.15)
			return Vector2.ZERO
	_cambio_rumbo -= delta
	if _cambio_rumbo <= 0.0:
		_cambio_rumbo = randf_range(1.2, 2.6)
		# deambula en las cuatro direcciones (así acaba alineado con Maisha)
		var opciones := [Vector2.RIGHT, Vector2.LEFT, Vector2.UP, Vector2.DOWN, Vector2.ZERO]
		if maisha:
			var d := maisha.global_position - global_position
			opciones.append(Vector2(signf(d.x), 0) if absf(d.x) > absf(d.y) else Vector2(0, signf(d.y)))
		_rumbo = opciones[randi() % opciones.size()]
	return _rumbo * VELOCIDAD


func _cambiar(nueva: int) -> void:
	fase = nueva
	_t_fase = 0.0


func _chocar(fuerte: bool) -> void:
	_cambiar(Fase.ATURDIDO)
	if fuerte:
		Sonido.efecto("piedra_rompe", 0.0, global_position)
		Impacto.temblar(2.0, 0.15)
		Impacto.chispa(global_position + _dir * 10.0 + Vector2(0, -8), -_dir, Color("a3a4a6"))
		_empuje = -_dir * 60.0


func _animar(mov: Vector2) -> void:
	var d := _dir if fase != Fase.ANDAR else mov
	if d.length() > 0.1:
		if absf(d.x) >= absf(d.y):
			_mira = "lado"
			_sprite.flip_h = d.x < 0.0
		else:
			_mira = "abajo" if d.y > 0.0 else "arriba"
			_sprite.flip_h = false
	var f := 0
	match fase:
		Fase.ANDAR:
			f = int(_tiempo * 6.0) % 2 if mov.length() > 1.0 else 0
		Fase.PREPARAR:
			f = 2
			_sprite.position.x = sin(_t_fase * 60.0) * 0.8       # tiembla de rabia
		Fase.EMBESTIR:
			f = 3 + int(_tiempo * 12.0) % 2
			_sprite.position.x = 0.0
		Fase.ATURDIDO:
			f = 0
			_sprite.position.x = 0.0
	_sprite.frame = FILAS[_mira] * 5 + f
	_sprite.modulate = Color(3, 3, 3) if _destello > 0.0 else Color.WHITE


func _draw() -> void:
	if _muriendo:
		return
	# el halo violeta de Giza en el suelo
	var pulso := 0.5 + 0.5 * sin(_tiempo * 4.0)
	for y in range(-2, 3):
		var ancho := int(round(11.0 * sqrt(1.0 - (y / 3.0) * (y / 3.0))))
		draw_rect(Rect2(-ancho, y, ancho * 2, 1), Color(0.66, 0.33, 0.84, 0.16 + 0.1 * pulso))
	# aviso: «!» encima mientras escarba
	if fase == Fase.PREPARAR:
		var y := -26.0 - _t_fase * 4.0
		draw_rect(Rect2(-1, y, 2, 5), Color("ffe08a"))
		draw_rect(Rect2(-1, y + 6, 2, 2), Color("ffe08a"))
		draw_rect(Rect2(-2, y - 1, 4, 10), Color(0, 0, 0, 0.25), false, 1.0)
	# aturdido: estrellitas que giran sobre la cabeza
	if fase == Fase.ATURDIDO:
		for k in 3:
			var a := _tiempo * 5.0 + k * TAU / 3.0
			var p := Vector2(cos(a) * 7.0, -22.0 + sin(a) * 2.0).round()
			draw_rect(Rect2(p, Vector2(2, 2)), Color("fff3c4"))
			draw_rect(Rect2(p + Vector2(-1, 0.5).round(), Vector2(4, 1)), Color(1, 0.95, 0.6, 0.6))
	if _enraizado > 0.0:
		for p in [Vector2(-9, 0), Vector2(-7, -2), Vector2(8, 0), Vector2(6, -2), Vector2(0, 1)]:
			draw_rect(Rect2(p, Vector2.ONE), Color("3e9a35"))


# --- Daño ---------------------------------------------------------------------

## El cetro rebota en su hierro... salvo cuando está aturdido
func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo:
		return false
	if fase != Fase.ATURDIDO and _enraizado <= 0.0:
		Sonido.efecto("clinc", 0.0, global_position)
		_empuje = direccion * 40.0
		return false
	_empuje = direccion * R.GOLPE_EMPUJE * 0.6
	recibir_danio(danio, global_position - direccion * 10.0, "golpe")
	return true


func enraizar(segundos: float) -> void:
	_enraizado = maxf(_enraizado, segundos)
	_empuje = Vector2.ZERO


func esta_enraizado() -> bool:
	return _enraizado > 0.0


func empujar(fuerza: Vector2) -> void:
	_empuje = fuerza
	if fase == Fase.EMBESTIR or fase == Fase.PREPARAR:
		_cambiar(Fase.ATURDIDO)        # el Latido le corta la embestida


func recibir_danio(cantidad: int, desde: Vector2, _tipo: String) -> void:
	if _muriendo:
		return
	vida -= cantidad
	_destello = 0.1
	if vida > 0:
		Sonido.efecto("petrino_golpeado", 0.0, global_position)
	var lejos := global_position - desde
	if lejos.length() > 0.1 and _empuje == Vector2.ZERO:
		_empuje = lejos.normalized() * 100.0
	if vida <= 0:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Sonido.efecto("petrino_muere", 0.0, global_position)
	Impacto.temblar(1.5, 0.14)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 14
	astillas.position = global_position + Vector2(0, -4)
	get_parent().add_child(astillas)
	queue_redraw()
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.2), 0.3)
	t.tween_property(self, "modulate:a", 0.0, 0.35)
	t.chain().tween_callback(queue_free)
