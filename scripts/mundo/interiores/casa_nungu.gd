extends "res://scripts/mundo/interiores/interior_casa.gd"
## LA CASA DE NUNGU, por dentro: el taller de un erizo científico que estudiaba la piedra de Giza y desapareció.
## Estanterías con piedras etiquetadas, una pizarra con dibujos de la veta, la mesa con su carta a medio escribir (la
## pista: le dejó la llave de repuesto a Corteza) y, al fondo, el ARMARIO cerrado con la cerradura de Corteza.
## Con la llave («llave_nungu») se abre («armario_abierto»): dentro, una escalera baja a la cueva de las setas.
## Dibujos: arte/mundos/raiz/paso/interior_nungu.png y armario.png (herramientas/pintar_paso.py).

const FONDO := preload("res://arte/mundos/raiz/paso/interior_nungu.png")
const ARMARIO := preload("res://scripts/mundo/paso/armario.gd")
const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")


func _fondo() -> Texture2D:
	return FONDO


func _muebles() -> Array[Rect2]:
	return [
		Rect2(134, 64, 52, 14),     # el armario
		Rect2(214, 96, 66, 22),     # la mesa
		Rect2(68, 146, 22, 12),     # la silla volcada
	]


func _cosas() -> Array:
	return [
		["nungu_estanteria", Vector2(70, 84), 26.0, 40.0],
		["nungu_pizarra", Vector2(224, 82), 22.0, 44.0],
		["nungu_mesa", Vector2(246, 124), 24.0, 30.0],
	]


func _preparar() -> void:
	var armario: Node2D = ARMARIO.new()
	armario.position = Vector2(160, 78)
	$Entidades.add_child(armario)
	# la escalera del armario: con el armario abierto, al meterse en él se baja a la cueva de las setas
	var escalera: Area2D = PUERTA.new()
	escalera.id = "armario"
	escalera.destino = "cueva_setas"
	escalera.destino_puerta = "escalera"
	escalera.salida = Vector2.DOWN
	escalera.cerrada_hasta = "armario_abierto"
	escalera.tam = Vector2(24, 8)
	escalera.position = Vector2(160, 84)
	add_child(escalera)
	if not Estado.tiene("nungu_entrar"):
		_pensar_al_entrar.call_deferred()


func _pensar_al_entrar() -> void:
	await get_tree().create_timer(0.8).timeout
	if not is_inside_tree() or Estado.tiene("nungu_entrar"):
		return
	await CHARLA_SCRIPT.hablar(self, "nungu_entrar")
	Estado.marcar("nungu_entrar")


func _dibujar_luces() -> void:
	# el rayo de sol que entra por el tejado roto, con motas de polvo
	var pulso := 0.85 + 0.15 * sin(_tiempo * 0.7)
	for i in 4:
		_luces.draw_circle(Vector2(232, 160), (14.0 + i * 10.0) * pulso, Color(1.0, 0.9, 0.65, 0.035))
	for k in 10:
		var p := Vector2(216 + fmod(k * 37.0 + _tiempo * 3.0, 40.0), 30 + fmod(k * 53.0 + _tiempo * 6.0, 130.0))
		_luces.draw_rect(Rect2(p.round(), Vector2.ONE), Color(1, 0.95, 0.8, 0.4))
