extends CharacterBody2D
## QUIETO (Sendero Olvidado): una figurita de piedra que juega a no moverse.
##   - Si Maisha lo MIRA (está delante de ella, hacia donde mira, y no muy lejos), se tapa los ojos y no se mueve.
##   - Si NO lo mira (se da la vuelta, está de lado o la ha congelado la escarcha), baja las manos, abre unos ojos
##     violetas y se le acerca muy deprisa. Si la toca, le quita una hoja y salta hacia atrás.
##   - El cetro solo le hace daño mirándolo (que es como se le golpea): 3 golpes lo rompen; una semilla quita 2.
## La trampa: quedarse quieta para vigilarlo hace subir la escarcha. Hay que ir hacia él sin pararse.

const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const DIBUJO := preload("res://arte/mundos/raiz/olvidado/quieto.png")
const VIDA := 3
const VELOCIDAD := 92.0
const VE_A := 230.0              # hasta dónde nota a Maisha (con la niebla, no más)
const MIRADA := 0.35             # cuánto tiene que estar delante de Maisha para que cuente como «mirado»
const FOTO_MUEVE := 3
const FOTO_GOLPE := 4

var zona: Node = null
var variante := "raiz"           # (la pone la zona al invocarlo; el Quieto tiene un solo dibujo)
var vida := VIDA
var mirado := true
var _empuje := Vector2.ZERO
var _aturdido := 0.0
var _enraizado := 0.0
var _destello := 0.0
var _tiempo := 0.0
var _muriendo := false
var _sprite: Sprite2D
var _ultimo_paso := 0.0


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("daniables")
	add_to_group("golpeables")
	add_to_group("quietos")
	collision_layer = 2
	collision_mask = 1
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var forma := CollisionShape2D.new()
	var circulo := CircleShape2D.new()
	circulo.radius = 6.0
	forma.shape = circulo
	forma.position = Vector2(0, -4)
	add_child(forma)
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 10.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -17)
	add_child(_sprite)
	_tiempo = randf() * 2.0


## ¿Lo está mirando Maisha?
func _lo_mira(maisha: Node2D) -> bool:
	if maisha.get("esta_caida"):
		return false
	var escarcha := maisha.get_node_or_null("Escarcha")
	if escarcha and escarcha.call("esta_congelada"):
		return false                     # congelada no puede vigilar
	var hacia := global_position - maisha.global_position
	if hacia.length() > VE_A:
		return false
	if hacia.length() < 14.0:
		return true
	var mirando: Vector2 = maisha.call("direccion_mirada")
	return hacia.normalized().dot(mirando) > MIRADA


func _physics_process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_aturdido = maxf(0.0, _aturdido - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	_destello = maxf(0.0, _destello - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var antes := mirado
	mirado = maisha == null or _lo_mira(maisha)
	if mirado and not antes:
		Sonido.efecto("clinc", -12.0, global_position, 0.2)          # se queda de piedra de golpe
	var mov := Vector2.ZERO
	var cerca := maisha != null and global_position.distance_to(maisha.global_position) < VE_A
	if not mirado and cerca and _aturdido <= 0.0 and _enraizado <= 0.0 and not maisha.get("esta_caida"):
		mov = (maisha.global_position - global_position).normalized() * VELOCIDAD
		if _tiempo - _ultimo_paso > 0.35:
			_ultimo_paso = _tiempo
			Sonido.efecto("piedra_rompe", -16.0, global_position, 0.3)   # el roce de la piedra al avanzar
	velocity = mov + _empuje
	_empuje = _empuje.move_toward(Vector2.ZERO, 500.0 * delta)
	move_and_slide()
	if zona:
		global_position = zona.limitar(global_position)
	# si la alcanza, le quita una hoja y salta hacia atrás
	if maisha and not mirado and global_position.distance_to(maisha.global_position) < 12.0:
		if maisha.call("recibir_danio", 1, global_position, "contacto"):
			_empuje = (global_position - maisha.global_position).normalized() * 150.0
			_aturdido = 0.8
	# el dibujo: tapándose los ojos (con sus grietas) o moviéndose; blanco al recibir un golpe
	if _destello > 0.0:
		_sprite.frame = FOTO_GOLPE
	elif not mirado and mov != Vector2.ZERO:
		_sprite.frame = FOTO_MUEVE
		_sprite.position.x = sin(_tiempo * 30.0) * 0.5              # tiembla al deslizarse
	else:
		_sprite.frame = clampi(VIDA - vida, 0, 2)
		_sprite.position.x = 0.0
	if mov.x != 0.0:
		_sprite.flip_h = mov.x < 0.0
	queue_redraw()


func _draw() -> void:
	if _muriendo:
		return
	# sin mirar: un halo violeta en el suelo (Giza lo mueve); y polvo de nieve al deslizarse
	if not mirado:
		var pulso := 0.5 + 0.5 * sin(_tiempo * 6.0)
		for y in range(-2, 3):
			var ancho := int(round(10.0 * sqrt(1.0 - (y / 3.0) * (y / 3.0))))
			draw_rect(Rect2(-ancho, y, ancho * 2, 1), Color(0.6, 0.3, 0.85, 0.15 + 0.12 * pulso))
		if velocity.length() > 10.0:
			for k in 4:
				var p := Vector2(-velocity.normalized().x * (6 + k * 3), -1 - k % 2) + Vector2(sin(_tiempo * 20 + k) * 2, 0)
				draw_rect(Rect2(p.floor(), Vector2.ONE), Color(0.9, 0.94, 1.0, 0.6 - k * 0.12))
	if _enraizado > 0.0:
		for p in [Vector2(-7, 0), Vector2(-5, -2), Vector2(6, 0), Vector2(4, -2), Vector2(0, 1)]:
			draw_rect(Rect2(p, Vector2.ONE), Color("3e9a35"))


# --- Daño ---------------------------------------------------------------------

func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if _muriendo:
		return false
	_empuje = direccion * 30.0                 # (poco: así se le pueden encadenar los golpes)
	recibir_danio(danio, global_position - direccion * 10.0, "golpe")
	return true


func enraizar(segundos: float) -> void:
	_enraizado = maxf(_enraizado, segundos)
	_empuje = Vector2.ZERO


func esta_enraizado() -> bool:
	return _enraizado > 0.0


func empujar(fuerza: Vector2) -> void:
	_empuje = fuerza
	_aturdido = maxf(_aturdido, 0.3)


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo:
		return
	vida -= 2 if tipo == "explosion" else cantidad
	_destello = 0.12
	Impacto.chispa(global_position + Vector2(0, -16), Vector2.UP, Color("c890ff"))
	if vida > 0:
		Sonido.efecto("petrino_golpeado", -2.0, global_position)
	else:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("quieto", self)
	Sonido.efecto("piedra_rompe", 0.0, global_position)
	Impacto.temblar(1.4, 0.14)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	remove_from_group("quietos")
	_sprite.frame = FOTO_GOLPE
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 12
	astillas.position = global_position + Vector2(0, -4)
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.2), 0.25)
	t.tween_property(self, "modulate:a", 0.0, 0.3)
	t.chain().tween_callback(queue_free)
