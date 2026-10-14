extends Area2D
## PUERTA: al pisarla, Maisha pasa a otra escena (otra región, una casa por dentro...).
## Cada puerta tiene un nombre («id»): la escena de destino busca la puerta con ese nombre
## para saber dónde hacer aparecer a Maisha.
##
##   id              nombre de esta puerta
##   destino         escena a la que lleva (p. ej. "cuna_de_musgo"); vacío = solo sirve de llegada
##   destino_puerta  por qué puerta se aparece allí
##   salida          hacia dónde da un paso Maisha al llegar por aquí (para no volver a pisarla)
##   cerrada_hasta   marca que hace falta para poder pasar (si no se tiene, emite «cerrada» y no deja pasar)

signal cerrada

@export var id := ""
@export var destino := ""
@export var destino_puerta := ""
@export var salida := Vector2.DOWN
@export var tam := Vector2(16, 16)
@export var cerrada_hasta := ""

var _armada := false        # no se activa hasta que Maisha se ha apartado de ella


func _ready() -> void:
	add_to_group("puertas")
	monitoring = true
	monitorable = false
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = tam
	forma.shape = caja
	add_child(forma)
	body_entered.connect(_al_entrar)


func _physics_process(_delta: float) -> void:
	if _armada:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and not overlaps_body(maisha):
		_armada = true


## Donde aparece Maisha al llegar por esta puerta: un paso fuera de ella
func punto_llegada() -> Vector2:
	var paso := salida.normalized() * (absf(salida.normalized().dot(tam)) / 2.0 + 10.0)
	return global_position + paso


func _al_entrar(cuerpo: Node) -> void:
	if not _armada or destino == "" or not cuerpo.is_in_group("maisha"):
		return
	_armada = false
	# (una puerta a una escena que aún no existe se porta como cerrada: si no, Maisha se quedaría sin poder moverse)
	if (cerrada_hasta != "" and not Estado.tiene(cerrada_hasta)) or not Estado.existe_escena(destino):
		# cerrada: Maisha da un paso atrás (la puerta vuelve a armarse cuando se aparta)
		(cuerpo as Node2D).global_position = punto_llegada()
		cerrada.emit()
		return
	cuerpo.set("puede_actuar", false)
	if not get_parent().has_method("abierto"):
		Sonido.efecto("puerta")              # (los arcos de raíz no son puertas de madera)
	Estado.ir_a(destino, destino_puerta)
