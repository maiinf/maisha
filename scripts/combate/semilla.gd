extends Node2D
## SEMILLA: cae en una casilla, espera la mecha y estalla en cruz.
## Daña a todo lo que esté en las casillas de la cruz (también a Maisha), hace estallar
## otras semillas que pille (reacción en cadena) y deja brotes durante unos segundos.

const R := preload("res://scripts/combate/reglas_combate.gd")
const TEXTURA := preload("res://arte/efectos/semilla.png")
const EXPLOSION := preload("res://scripts/combate/explosion.gd")
const RELIEVE := preload("res://scripts/mundo/relieve.gd")

var casilla := Vector2i.ZERO
var _mecha: float = Artes.semilla_mecha()
var _estallada := false
var _sprite: Sprite2D
var _atrapados: Array[Node2D] = []


func _ready() -> void:
	add_to_group("semillas")
	position = R.centro_de(casilla) + Vector2(0, 5)
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURA
	_sprite.hframes = 2
	_sprite.offset = Vector2(0, -4)
	add_child(_sprite)
	# pequeña caída al aparecer
	_sprite.position.y = -6
	create_tween().tween_property(_sprite, "position:y", 0.0, 0.12).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)


func _process(delta: float) -> void:
	_mecha -= delta
	# parpadea cada vez más deprisa al acercarse el final
	var ritmo := 0.5 if _mecha > 1.0 else 0.12
	_sprite.frame = 1 if fmod(_mecha, ritmo) < ritmo / 2.0 else 0
	_atrapar_cercanos()
	queue_redraw()
	if _mecha <= 0.0:
		estallar()


## La semilla echa raíces: los enemigos que se acercan quedan sujetos hasta que estalla
func _atrapar_cercanos() -> void:
	for nodo in get_tree().get_nodes_in_group("enemigos"):
		var enemigo := nodo as Node2D
		if enemigo == null or not enemigo.has_method("enraizar"):
			continue
		if enemigo.global_position.distance_to(global_position) <= Artes.semilla_raices():
			enemigo.call("enraizar", _mecha + 0.15)
			if not enemigo in _atrapados:
				_atrapados.append(enemigo)


## Dibuja las raíces que van de la semilla a cada enemigo atrapado
func _draw() -> void:
	for enemigo in _atrapados:
		if not is_instance_valid(enemigo):
			continue
		var hasta := to_local(enemigo.global_position)
		var pasos := int(hasta.length() / 2.0)
		for i in range(1, pasos):
			var t := float(i) / pasos
			var p := (hasta * t + Vector2(0, sin(t * PI * 3.0 + _mecha * 8.0) * 1.5)).round()
			draw_rect(Rect2(p, Vector2.ONE), Color("3e9a35") if i % 3 else Color("6fcf4f"))


## La empuja el Latido: se mueve una casilla si está libre
func desplazar(direccion: Vector2i) -> void:
	var destino := casilla + direccion
	for s in get_tree().get_nodes_in_group("semillas"):
		if s != self and s.casilla == destino:
			return
	casilla = destino
	create_tween().tween_property(self, "position", R.centro_de(casilla) + Vector2(0, 5), 0.1)


func casillas_de_la_cruz() -> Array[Vector2i]:
	var lista: Array[Vector2i] = [casilla]
	for dir in [Vector2i.RIGHT, Vector2i.LEFT, Vector2i.UP, Vector2i.DOWN]:
		for paso in range(1, Artes.semilla_alcance() + 1):
			lista.append(casilla + dir * paso)
	return lista


func _toca_la_cruz(pos: Vector2, cruz: Array[Vector2i]) -> bool:
	for punto in [Vector2.ZERO, Vector2(-5, -3), Vector2(5, -3), Vector2(-5, 2), Vector2(5, 2), Vector2(0, -8)]:
		if R.casilla_de(pos + punto) in cruz:
			return true
	return false


func estallar() -> void:
	if _estallada:
		return
	_estallada = true
	Sonido.efecto("explosion", 0.0, global_position)
	Sonido.efecto("brotes", 0.0, global_position)
	Impacto.onda(global_position)
	Impacto.temblar(2.5, 0.22)
	var cruz := casillas_de_la_cruz()
	var padre := get_parent()
	# un fogonazo naranja que ilumina alrededor (de noche y en las cuevas se nota mucho más)
	RELIEVE.destello(padre, position + Vector2(0, -4), Color(1.0, 0.7, 0.35), 1.7, 1.3, 0.45)
	for c in cruz:
		var fx: Node2D = EXPLOSION.new()
		fx.position = R.centro_de(c) + Vector2(0, 8)
		padre.add_child(fx)
	# daño a todo lo que esté en la cruz: cuenta todo el cuerpo, no solo el centro
	# (si un enemigo está a caballo entre dos casillas, también le alcanza)
	# Las raíces conducen la explosión: lo que esté atrapado también la recibe, aunque esté en diagonal.
	for nodo in get_tree().get_nodes_in_group("daniables"):
		var objetivo := nodo as Node2D
		if objetivo and (_toca_la_cruz(objetivo.global_position, cruz) or objetivo in _atrapados):
			objetivo.call("recibir_danio", R.EXPLOSION_DANIO, global_position, "explosion")
	# el fuego enciende lo que se puede encender (los braseros del Sendero Olvidado)
	for nodo in get_tree().get_nodes_in_group("encendibles"):
		if _toca_la_cruz((nodo as Node2D).global_position, cruz):
			nodo.call("encender")
	# reacción en cadena: otras semillas en la cruz estallan justo después
	for s in get_tree().get_nodes_in_group("semillas"):
		if s != self and s.casilla in cruz:
			get_tree().create_timer(0.08).timeout.connect(s.estallar)
	# brotes
	var registro := get_tree().get_first_node_in_group("registro_brotes")
	if registro:
		for c in cruz:
			registro.plantar(c)
	remove_from_group("semillas")
	queue_free()
