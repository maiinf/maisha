extends Node2D
## UN PEÑASCO FLOTANTE (Asterhaul, la Aguja Caída): una roca de cima plana (2×2 casillas) que flota en el viento
## astral, en un pasillo de vacío («=») entre dos MUELLES (`muelle_a`, `muelle_b`: la esquina de arriba a la
## izquierda, en casillas). Suelto, se queda EN MEDIO: no se llega a él desde ninguna orilla.
## Cuando le llega la onda de un monolito que canta (asterhaul/monolito.gd), ACUDE al muelle más cercano a ese
## monolito y allí se queda mientras lo oye (y ESPERA s más). Luego vuelve despacio al medio... con quien lleve
## encima. Desde el medio, la Resonancia de Maisha alcanza al monolito de la otra orilla.
## Sostiene a quien lo pisa (está en «sostenes»: la escena pregunta `firme()`).
## Dibujo: arte/mundos/asterhaul/aguja/penasco.png.

const DIBUJO := preload("res://arte/mundos/asterhaul/aguja/penasco.png")
const MONOLITO := preload("res://scripts/mundo/asterhaul/monolito.gd")
const LADO := 32.0
const ACUDE := 70.0
const VUELVE := 15.0
const ESPERA := 1.5

var muelle_a := Vector2i.ZERO
var muelle_b := Vector2i.ZERO
var _llamado := 0.0
var _destino := Vector2.ZERO
var _sprite: Sprite2D
var _tiempo := 0.0


func _ready() -> void:
	add_to_group("sostenes")
	add_to_group("penascos")
	z_index = -4
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.centered = false
	_sprite.position = Vector2(-4, -2)
	add_child(_sprite)
	global_position = reposo()
	_destino = reposo()


func reposo() -> Vector2:
	return (Vector2(muelle_a) + Vector2(muelle_b)) * 8.0


func centro() -> Vector2:
	return global_position + Vector2(LADO, LADO) / 2.0


func firme(p: Vector2) -> bool:
	return Rect2(global_position, Vector2(LADO, LADO)).grow(1.0).has_point(p)


## ¿Está atracado en ese muelle? («a» o «b»)
func en_muelle(cual: String) -> bool:
	return global_position.distance_to(Vector2(muelle_a if cual == "a" else muelle_b) * 16.0) < 1.0


func _process(delta: float) -> void:
	_tiempo += delta
	var m := MONOLITO.que_suena_en(get_tree(), centro())
	if m != null:
		var a := Vector2(muelle_a) * 16.0
		var b := Vector2(muelle_b) * 16.0
		_destino = a if m.global_position.distance_to(a) <= m.global_position.distance_to(b) else b
		_llamado = ESPERA
	else:
		_llamado = maxf(0.0, _llamado - delta)
		if _llamado <= 0.0:
			_destino = reposo()
	var antes := global_position
	global_position = global_position.move_toward(_destino, (ACUDE if _llamado > 0.0 else VUELVE) * delta)
	# se lleva a Maisha, si la tiene encima
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and global_position != antes and Rect2(antes, Vector2(LADO, LADO)).grow(1.0).has_point(maisha.global_position):
		maisha.global_position += global_position - antes
	_sprite.position.y = -2.0 + (roundf(sin(_tiempo * 1.6)) if global_position == reposo() else 0.0)     # en reposo, se mece
