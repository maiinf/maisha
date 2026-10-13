extends Node2D
## LA BOLA DE GIZA que lanza Bundi, el búho-mago. Va despacio y persigue a Maisha (puede torcer un poco).
##   - Si toca a Maisha, le hace 1 de daño y se apaga.
##   - El ESCUDO (J mantenida, de frente) la DEVUELVE: vuelve más rápida y persigue a quien la lanzó; si toca a un
##     enemigo le quita ORBE_DANIO_DEVUELTA (a Bundi lo deja atontado).
##   - El Latido la deshace («disipar», grupo «ondas»). Se apaga sola a los ORBE_DURA segundos.

const R := preload("res://scripts/combate/reglas_combate.gd")
const DIBUJO := preload("res://arte/mundos/raiz/hechiceros/orbe.png")

var direccion := Vector2.RIGHT
var dueno: Node2D = null
var devuelta := false
var _vida := 0.0
var _tiempo := 0.0
var _apagandose := false
var _sprite: Sprite2D
var _estela: Array[Vector2] = []


func _ready() -> void:
	add_to_group("ondas")
	z_index = 3
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 2
	add_child(_sprite)


func _physics_process(delta: float) -> void:
	_tiempo += delta
	_sprite.frame = int(_tiempo * 8.0) % 2
	queue_redraw()
	if _apagandose:
		return
	_vida += delta
	if _vida > R.ORBE_DURA:
		disipar()
		return
	var meta := _meta()
	if meta != Vector2.INF:
		var quiere := (meta - global_position).normalized()
		var giro := clampf(direccion.angle_to(quiere), -R.ORBE_GIRO * delta, R.ORBE_GIRO * delta)
		direccion = direccion.rotated(giro * (2.5 if devuelta else 1.0))
	global_position += direccion * R.ORBE_VELOCIDAD * (1.7 if devuelta else 1.0) * delta
	_estela.push_front(global_position)
	if _estela.size() > 6:
		_estela.pop_back()
	if devuelta:
		_tocar_enemigos()
	else:
		_tocar_a_maisha()


func _meta() -> Vector2:
	if devuelta:
		return dueno.global_position + Vector2(0, -12) if is_instance_valid(dueno) else Vector2.INF
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	return maisha.global_position + Vector2(0, -8) if maisha else Vector2.INF


func _tocar_a_maisha() -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null or maisha.global_position.distance_to(global_position + Vector2(0, 8)) > R.ORBE_RADIO + 2.0:
		return
	if maisha.call("recibir_danio", 1, global_position, "magia"):
		disipar()
	elif maisha.get("escudo"):
		# ¡el escudo la devuelve!
		devuelta = true
		_vida = 0.0
		direccion = -direccion
		Sonido.efecto("orbe_rebota", 0.0, global_position)
		Impacto.chispa(global_position, direccion, Color("f9d77a"))
	else:
		disipar()


func _tocar_enemigos() -> void:
	for nodo in get_tree().get_nodes_in_group("daniables"):
		var e := nodo as Node2D
		if e == null or e.is_in_group("maisha"):
			continue
		if e.global_position.distance_to(global_position + Vector2(0, 12)) < R.ORBE_RADIO + 4.0:
			e.call("recibir_danio", R.ORBE_DANIO_DEVUELTA, global_position, "magia")
			Impacto.chispa(global_position, direccion, Color("c890f0"))
			disipar()
			return


func _draw() -> void:
	# la estela violeta (dorada si la ha devuelto el escudo)
	var color := Color(0.98, 0.84, 0.48) if devuelta else Color(0.7, 0.4, 0.95)
	for i in _estela.size():
		var p := _estela[i] - global_position
		draw_circle(p, 3.0 - i * 0.4, Color(color, 0.35 - i * 0.05))
	# su sombra en el suelo (va por el aire)
	draw_circle(Vector2(0, 10), 2.5, Color(0, 0, 0, 0.25))


func disipar() -> void:
	if _apagandose:
		return
	_apagandose = true
	remove_from_group("ondas")
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(2, 2), 0.2)
	t.tween_property(self, "modulate:a", 0.0, 0.2)
	t.chain().tween_callback(queue_free)
