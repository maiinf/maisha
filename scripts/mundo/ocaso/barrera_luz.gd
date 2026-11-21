extends StaticBody2D
## UNA BARRERA QUE ABRE LA LUZ (el Jardín de los Faroles), en las casillas `casillas`:
##   - la CELOSÍA ILUSORIA (`abre_con` VIOLETA): parece un seto con celosía; la luz violeta la deshace.
##   - la VERJA DEL INVERNADERO (`abre_con` DORADO): su disco de sol se enciende con la luz dorada y la verja baja.
## Cerrada, no se pasa. Abierta (`marca`), se pasa. La luz se para en ella siempre. Dibujo: `dibujo` (con 2
## cuadros, el 1 es abierta; con 1, abierta no se ve).

signal abierta

var casillas := Rect2i()
var abre_con := 2
var marca := ""
var dibujo: Texture2D
var cuadros := 1
var encendido := false
var _sprite: Sprite2D
var _forma: CollisionShape2D


func _ready() -> void:
	add_to_group("opticas")
	_sprite = Sprite2D.new()
	_sprite.texture = dibujo
	_sprite.hframes = cuadros
	_sprite.offset = Vector2(0, -dibujo.get_height() / 2.0)
	add_child(_sprite)
	_forma = CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(casillas.size) * 16.0
	_forma.shape = caja
	_forma.position = Vector2(0, -caja.size.y / 2.0)
	add_child(_forma)
	if abierto():
		_abrirse(false)


func abierto() -> bool:
	return Estado.tiene(marca)


func ocupa(c: Vector2i) -> bool:
	return casillas.has_point(c)


## La luz se queda aquí siempre (el disco de la verja se la bebe; la celosía deshecha deja ver el pasillo vacío)
func desviar(_d: Vector2i, color: int) -> Array:
	if color == abre_con and not abierto():
		Estado.marcar(marca)
		_abrirse.call_deferred(true)
	return []


func _abrirse(con_efecto: bool) -> void:
	_forma.set_deferred("disabled", true)
	if cuadros > 1:
		_sprite.frame = 1
	else:
		if con_efecto:
			create_tween().tween_property(_sprite, "modulate:a", 0.0, 0.8)
		else:
			_sprite.visible = false
	if con_efecto:
		Sonido.efecto("celosia_deshace" if abre_con == 2 else "verja_abre", 0.0, global_position)
		Impacto.chispa(global_position + Vector2(0, -16), Vector2.UP, Color(0.8, 0.55, 1.0) if abre_con == 2 else Color(1.0, 0.85, 0.45))
		abierta.emit()
