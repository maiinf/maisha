extends Node2D
## BUIBUI, LA ARAÑA-BRUJA: una hechicera de Giza. Una araña de piedra con chal de telaraña, seis ojos y un cesto-nido
## atado a la espalda.
##   - Se queda en su sitio (se recoloca muy despacio) y cada poco INVOCA: el nido brilla (aviso) y salen BUIBUI_BICHOS
##     bichos de óxido (mende.gd), hasta BUIBUI_MAX_BICHOS a la vez.
##   - Si Maisha se le pega, le muerde con los colmillos.
##   - El cetro le quita 1. Una SEMILLA que la alcance le quita 2 y le SELLA el nido con raíces: ya no invoca más.
## Dibujo: arte/mundos/raiz/hechiceros/buibui.png (0-1 quieta, 2 invoca, 3 golpeada).

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const MENDE := preload("res://scripts/enemigos/mende.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const DIBUJO := preload("res://arte/mundos/raiz/hechiceros/buibui.png")

var variante := "raiz"
var zona: Node = null
var vida: int = R.BUIBUI_VIDA
var sellado := false
var _t := 0.0
var _aviso := 0.0
var _tiempo := 0.0
var _destello := 0.0
var _mordisco := 0.0
var _enraizado := 0.0
var _bichos: Array = []
var _muriendo := false
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("daniables")
	add_to_group("golpeables")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 14.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 4
	_sprite.offset = Vector2(0, -12)
	add_child(_sprite)
	_t = R.BUIBUI_CADA * 0.4
	_tiempo = randf() * 2.0


func _physics_process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_destello = maxf(0.0, _destello - delta)
	_mordisco = maxf(0.0, _mordisco - delta)
	_enraizado = maxf(0.0, _enraizado - delta)
	_bichos = _bichos.filter(func(b: Node2D) -> bool: return is_instance_valid(b) and b.is_in_group("enemigos"))
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var lejos := global_position.distance_to(maisha.global_position) if maisha else 9999.0
	var activa: bool = maisha != null and not maisha.get("esta_caida") and lejos < R.BUIBUI_VE
	if _aviso > 0.0:
		_aviso -= delta
		if _aviso <= 0.0:
			_invocar()
	elif activa and not sellado and _enraizado <= 0.0:
		_t -= delta
		if _t <= 0.0 and _bichos.size() < R.BUIBUI_MAX_BICHOS:
			_aviso = R.BUIBUI_AVISO
			Sonido.efecto("buibui_invoca", 0.0, global_position)
	# se recoloca despacito, guardando un poco las distancias
	if activa and _aviso <= 0.0 and _enraizado <= 0.0 and maisha:
		var hacia := (global_position - maisha.global_position).normalized()
		var quiere := 70.0
		var mov := hacia * (1.0 if lejos < quiere else -0.4) * R.BUIBUI_ANDA * delta
		global_position += mov
		if zona:
			global_position = zona.limitar(global_position)
	# muerde si Maisha se le pega
	if maisha and lejos < 13.0 and _mordisco <= 0.0:
		if maisha.call("recibir_danio", 1, global_position, "contacto"):
			_mordisco = 1.0
	modulate = Color(3, 3, 3) if _destello > 0.0 else Color.WHITE
	if _destello > 0.0:
		_sprite.frame = 3
	elif _aviso > 0.0:
		_sprite.frame = 2
		_sprite.position.x = sin(_tiempo * 40.0) * 0.6
	else:
		_sprite.frame = int(_tiempo * 2.0) % 2
		_sprite.position.x = 0.0
	queue_redraw()


func _invocar() -> void:
	_t = R.BUIBUI_CADA
	for i in R.BUIBUI_BICHOS:
		if _bichos.size() >= R.BUIBUI_MAX_BICHOS:
			break
		var bicho: Node2D = MENDE.new()
		bicho.zona = zona
		bicho.position = global_position + Vector2(randf_range(-8, 8), -18)
		bicho.salto = Vector2((i * 2 - 1) * randf_range(14, 22), randf_range(18, 26))
		get_parent().add_child(bicho)
		_bichos.append(bicho)


func _draw() -> void:
	if _muriendo:
		return
	if _aviso > 0.0:
		# el nido se ilumina por dentro
		var k := 1.0 - _aviso / R.BUIBUI_AVISO
		draw_circle(Vector2(0, -26), 3.0 + 5.0 * k, Color(0.75, 0.4, 0.95, 0.15 + 0.3 * k))
	if sellado:
		# raíces verdes cerrando el nido
		var vaiven := int(_tiempo * 3.0) % 2
		for x in [-4, -2, 0, 2, 4]:
			draw_line(Vector2(x, -30 - (vaiven if x % 4 == 0 else 0)), Vector2(x * 0.6, -23), Color("3e9a35"), 1.0)
		draw_line(Vector2(-5, -27), Vector2(5, -27), Color("6fcf4f"), 1.0)


# --- Daño ---------------------------------------------------------------------

func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if _muriendo:
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo:
		return
	vida -= cantidad
	_destello = 0.12
	if tipo == "explosion" and not sellado:
		sellado = true
		_aviso = 0.0
	if vida <= 0:
		morir()
		return
	Sonido.efecto("petrino_golpeado", 0.0, global_position)


func enraizar(segundos: float) -> void:
	_enraizado = maxf(_enraizado, segundos)


func empujar(fuerza: Vector2) -> void:
	_aviso = 0.0                       # el Latido le corta la invocación
	global_position += fuerza.normalized() * 6.0


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("buibui", self)
	Sonido.efecto("petrino_muere", 0.0, global_position)
	Impacto.temblar(1.5, 0.15)
	remove_from_group("enemigos")
	remove_from_group("daniables")
	remove_from_group("golpeables")
	_sprite.frame = 3
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 14
	astillas.position = global_position + Vector2(0, -8)
	get_parent().add_child(astillas)
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.4, 0.2), 0.3)
	t.tween_property(self, "modulate:a", 0.0, 0.35)
	t.chain().tween_callback(queue_free)
