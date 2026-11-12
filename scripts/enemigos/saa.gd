extends Node2D
## SAA, EL AUTÓMATA DE RELOJERÍA (Sigilia, el Observatorio de la Aurora): un centinela de latón al que nadie le ha
## quitado la cuerda. Barrigudo, con un ojo de lente, patitas cortas y una llave de cuerda que gira en la espalda.
##   - RONDA: va y viene entre los puntos de su `ronda`, tic-tac.
##   - Si ve a Maisha cerca (VE px), la PERSIGUE despacio (no se sale de las terrazas ni se aleja de su puesto más de
##     CORREA px) y, al alcanzarla, le da un MAZAZO (1 hoja) y se queda un momento dándose cuerda.
##   - El cetro y las semillas rebotan en el latón (¡clinc!): no hay forma de pararlo...
##   - ...salvo con el SIGILO DE RAYO (está en «cargables»): la cuerda se le pasa de vueltas y se queda SOBRECARGADO
##     (quieto, temblando, echando chispas) SOBRECARGA s: ahí entran el cetro (1) y las semillas (2). 3 de vida.
##     Si no se le vence a tiempo, se vuelve a dar cuerda y sigue su ronda.
## Dibujo: arte/mundos/sigilia/observatorio/saa.png (herramientas/pintar_observatorio.py).

signal destruido

const DIBUJO := preload("res://arte/mundos/sigilia/observatorio/saa.png")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIDA := 3
const ANDA := 24.0
const CORRE := 38.0
const VE := 76.0
const CORREA := 130.0
const PEGA := 15.0
const MAZAZO := 0.45                    # lo que tarda en caer el mazazo (el aviso)
const CUERDA := 1.3                     # lo que tarda en darse cuerda después
const SOBRECARGA := 4.5

enum Fase { RONDA, PERSIGUE, MAZAZO, CUERDA, SOBRECARGADO }

## por dónde ronda (puntos en px); si está vacía, se queda en su puesto
var ronda: Array[Vector2] = []
var vida := VIDA
var fase := Fase.RONDA
var _puesto := Vector2.ZERO
var _hacia := 0
var _t := 0.0
var _tiempo := 0.0
var _destello := 0.0
var _muriendo := false
var _pego := false
var _filas: PackedStringArray
var _sprite: Sprite2D
var _chispas: Node2D


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("cargables")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("saas")
	_puesto = position
	_filas = get_tree().current_scene.get_node("Region")._filas
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 10.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -15)
	add_child(_sprite)
	_chispas = Node2D.new()
	_chispas.z_index = 1
	_chispas.draw.connect(_dibujar_chispas)
	add_child(_chispas)
	_tiempo = randf() * 3.0


## ¿Se puede pisar ahí? (terraza: ni cielo, ni tinta, ni puente)
func _es_suelo(p: Vector2) -> bool:
	var x := floori(p.x / 16.0)
	var y := floori(p.y / 16.0)
	return y >= 0 and y < _filas.size() and x >= 0 and x < _filas[y].length() and not (_filas[y][x] in ["0", "~", "="])


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _andar(hacia: Vector2, velocidad: float, delta: float) -> void:
	var d := hacia - global_position
	if d.length() < 1.0:
		return
	var paso := d.normalized() * minf(velocidad * delta, d.length())
	for intento: Vector2 in [paso, Vector2(paso.x, 0), Vector2(0, paso.y)]:
		if intento != Vector2.ZERO and _es_suelo(global_position + intento + intento.normalized() * 6.0):
			global_position += intento
			_sprite.flip_h = paso.x < 0.0
			return


func _process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var d := (maisha.global_position - global_position) if maisha else Vector2.INF
	var la_ve: bool = maisha != null and not maisha.get("esta_caida") and d.length() < VE and maisha.global_position.distance_to(_puesto) < CORREA
	match fase:
		Fase.RONDA:
			if la_ve:
				_cambiar(Fase.PERSIGUE)
				Sonido.efecto("clinc", -6.0, global_position, 0.2)
			elif ronda.is_empty():
				_andar(_puesto, ANDA, delta)
			else:
				if global_position.distance_to(ronda[_hacia]) < 3.0:
					_hacia = (_hacia + 1) % ronda.size()
				_andar(ronda[_hacia], ANDA, delta)
		Fase.PERSIGUE:
			if not la_ve:
				_cambiar(Fase.RONDA)
			elif d.length() < PEGA:
				_cambiar(Fase.MAZAZO)
				_pego = false
			else:
				_andar(maisha.global_position, CORRE, delta)
		Fase.MAZAZO:
			if _t >= MAZAZO and not _pego:
				_pego = true
				Sonido.efecto("cetro_golpe", -2.0, global_position, 0.2)
				if maisha and d.length() < PEGA + 8.0:
					maisha.call("recibir_danio", 1, global_position, "contacto")
			if _t >= MAZAZO + 0.25:
				_cambiar(Fase.CUERDA)
		Fase.CUERDA:
			if _t >= CUERDA:
				_cambiar(Fase.RONDA)
		Fase.SOBRECARGADO:
			if _t >= SOBRECARGA:
				Sonido.efecto("rueda_abrir", -8.0, global_position, 0.3)
				_cambiar(Fase.CUERDA)
	_dibujar()


func _dibujar() -> void:
	if _destello > 0.0:
		_sprite.frame = 4
	elif fase == Fase.SOBRECARGADO:
		_sprite.frame = 3
		_sprite.position.x = sin(_tiempo * 60.0) * 1.0
	elif fase == Fase.MAZAZO:
		_sprite.frame = 2
	elif fase == Fase.CUERDA:
		_sprite.frame = 0
	else:
		_sprite.frame = int(_tiempo * (6.0 if fase == Fase.PERSIGUE else 3.5)) % 2
	if fase != Fase.SOBRECARGADO:
		_sprite.position.x = 0.0
	_chispas.queue_redraw()


## Sobrecargado: rayitos que le saltan del cuerpo. Dándose cuerda: un arco que gira en la llave.
func _dibujar_chispas() -> void:
	if fase == Fase.SOBRECARGADO:
		var semilla := int(_tiempo * 16.0)
		for k in 4:
			var a := float((semilla * 53 + k * 97) % 360) * PI / 180.0
			var desde := Vector2(cos(a) * 6.0, -14.0 + sin(a) * 8.0)
			var fin := desde + Vector2(cos(a), sin(a)) * (5.0 + (semilla + k) % 4)
			_chispas.draw_polyline(PackedVector2Array([desde, ((desde + fin) * 0.5 + Vector2(sin(a * 5.0), cos(a * 3.0)) * 2.0).round(), fin.round()]),
					Color(1.0, 0.95, 0.5) if (semilla + k) % 2 == 0 else Color(0.5, 0.85, 1.0), 1.0)
		# cuánto le queda de sobrecarga: se le va apagando el halo
		var queda := 1.0 - _t / SOBRECARGA
		_chispas.draw_arc(Vector2(0, -14), 15.0, -PI / 2, -PI / 2 + TAU * queda, 20, Color(1.0, 0.95, 0.5, 0.6), 1.0)
	elif fase == Fase.CUERDA:
		_chispas.draw_arc(Vector2(0, -30), 4.0, _tiempo * 9.0, _tiempo * 9.0 + PI * 1.3, 8, Color(0.94, 0.82, 0.48, 0.9), 1.0)


# --- Rayo y daño --------------------------------------------------------------

## El Sigilo de Rayo: la cuerda se le pasa de vueltas
func cargar() -> void:
	if _muriendo:
		return
	_cambiar(Fase.SOBRECARGADO)
	Sonido.efecto("geoda_encender", 0.0, global_position, 0.2)
	Impacto.chispa(global_position + Vector2(0, -14), Vector2.UP, Color("fff0a0"))


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if _muriendo:
		return false
	if fase != Fase.SOBRECARGADO:
		_rebotar()
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo or tipo == "rayo":
		return
	if fase != Fase.SOBRECARGADO:
		_rebotar()
		return
	vida -= 2 if tipo == "explosion" else cantidad
	_destello = 0.12
	Impacto.chispa(global_position + Vector2(0, -14), Vector2.UP, Color("f0d27a"))
	if vida > 0:
		Sonido.efecto("cosechadora_tuerca", -4.0, global_position, 0.2)
	else:
		morir()


## El latón no se abolla: suena y salta una chispa
func _rebotar() -> void:
	Sonido.efecto("clinc", -2.0, global_position, 0.2)
	Impacto.chispa(global_position + Vector2(0, -14), Vector2.UP, Color("c8c2d4"))


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("saa", self)
	Sonido.efecto("cangrejo_vuelca", 0.0, global_position)
	for g in ["enemigos", "cargables", "golpeables", "daniables", "saas"]:
		remove_from_group(g)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 14
	astillas.position = global_position + Vector2(0, -12)
	get_parent().add_child(astillas)
	destruido.emit()
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.3, 0.15), 0.3)
	t.tween_property(self, "modulate:a", 0.0, 0.4)
	t.chain().tween_callback(queue_free)
