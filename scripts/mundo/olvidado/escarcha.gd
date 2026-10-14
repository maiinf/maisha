extends Node2D
## LA ESCARCHA DE LA QUIETUD (Sendero Olvidado). Nungu lo descubrió: Giza «se alimenta de lo que se queda quieto».
## En la montaña, si Maisha se queda quieta, el frío le sube por el cuerpo (cristales de hielo que trepan desde los
## pies, el color se le va al azul y echa vaho al respirar). Si llega arriba, se CONGELA: se queda de piedra un momento
## y pierde una hoja de Vida. Moverse lo deshace poco a poco; junto a un BRASERO encendido, deprisa.
## (Lo contrario del Lago Espejo, donde quedarse quieta lo revelaba todo.)
## Va colgado de Maisha (lo pone sendero_olvidado.gd).

signal congelada

const GRACIA := 1.2              # segundos quieta antes de que empiece a subir el frío
const SUBIR := 5.0               # segundos (tras la gracia) hasta congelarse
const BAJAR := 2.5               # segundos andando para quitarse todo el frío
const CONGELADA_DURA := 1.3
const HIELO := [Color("f4faff"), Color("9cc8f0"), Color("5a94d8")]

var frio := 0.0                  # 0 = nada, 1 = congelada
var quieta := 0.0                # segundos sin moverse
var ultimo_brasero: Node2D       # el último brasero encendido junto al que estuvo (allí vuelve si cae)
var _maisha: CharacterBody2D
var _sprite: AnimatedSprite2D
var _antes := Vector2.ZERO
var _congelada := 0.0
var _tiempo := 0.0
var _vaho: Array[Dictionary] = []
var _cristales: Array[Vector2] = []


func _ready() -> void:
	_maisha = get_parent() as CharacterBody2D
	_sprite = _maisha.get_node("Sprite")
	_antes = _maisha.global_position
	z_index = 2
	var azar := RandomNumberGenerator.new()
	azar.seed = 77
	for i in 80:
		# puntos dentro de la silueta de Maisha (de los pies, 0, a la cabeza, -30)
		var y := -azar.randf() * 30.0
		var ancho := 6.0 if y > -12.0 else (7.5 if y > -24.0 else 5.0)
		_cristales.append(Vector2(azar.randf_range(-ancho, ancho), y))


func _process(delta: float) -> void:
	_tiempo += delta
	var pos := _maisha.global_position
	var se_mueve := pos.distance_to(_antes) > 0.3
	_antes = pos
	var calor := _brasero_cerca(pos)
	if calor:
		ultimo_brasero = calor
	if _congelada > 0.0:
		_congelada -= delta
		if _congelada <= 0.0:
			_descongelar()
	elif not _maisha.get("puede_actuar") or _maisha.get("esta_caida"):
		quieta = 0.0                       # en una conversación o una escena no corre el frío
	elif calor:
		quieta = 0.0
		frio = maxf(0.0, frio - delta / 0.6)
	elif se_mueve:
		quieta = 0.0
		frio = maxf(0.0, frio - delta / BAJAR)
	else:
		quieta += delta
		if quieta > GRACIA:
			frio = minf(1.0, frio + delta / SUBIR)
			if frio >= 1.0:
				_congelar()
	# el vaho al respirar, cuando hace frío y no se mueve
	if frio > 0.15 and fmod(_tiempo, 1.6) < delta:
		var lado := -1.0 if _sprite.flip_h else 1.0
		var cara := Vector2(4.0 * lado if _sprite.animation.ends_with("lado") else 0.0, -18.0)
		if not _sprite.animation.ends_with("arriba"):
			_vaho.append({"p": cara, "t": 0.0})
	for v in _vaho:
		v["t"] += delta
	_vaho = _vaho.filter(func(v: Dictionary) -> bool: return v["t"] < 1.2)
	# el color se le va al azul (sin tocar la transparencia, que la usan las Artes)
	var a := _sprite.self_modulate.a
	var tinte := Color(1, 1, 1).lerp(Color(0.5, 0.7, 1.0), frio * 0.95)
	if _congelada > 0.0:
		tinte = Color(0.62, 0.66, 0.72)
	_sprite.self_modulate = Color(tinte, a)
	queue_redraw()


func _brasero_cerca(pos: Vector2) -> Node2D:
	for b in get_tree().get_nodes_in_group("braseros"):
		if b.call("calienta", pos):
			return b
	return null


func _congelar() -> void:
	_congelada = CONGELADA_DURA
	_maisha.set("puede_actuar", false)
	Sonido.efecto("piedra_rompe", -4.0, _maisha.global_position)
	Impacto.temblar(1.5, 0.15)
	congelada.emit()


func _descongelar() -> void:
	frio = 0.45
	quieta = 0.0
	_maisha.set("puede_actuar", true)
	Sonido.efecto("clinc", -6.0, _maisha.global_position)
	_maisha.call("perder_hoja")


func esta_congelada() -> bool:
	return _congelada > 0.0


## La mitad del ancho de Maisha a cada altura (desde los pies, 0, hasta lo alto de la cabeza, -30): para que la
## costra de hielo siga su silueta (piernas, cuerpo con los brazos, cabeza redonda)
func _ancho_en(y: float) -> float:
	if y > -4.0:
		return 5.0
	if y > -14.0:
		return 8.0 if y < -6.0 else 6.0
	var t := (y + 22.0) / 8.5
	return 8.0 * sqrt(maxf(0.0, 1.0 - t * t))


func _draw() -> void:
	# la costra de hielo sube desde los pies, siguiendo la silueta, con el filo de arriba irregular
	if frio > 0.02 or _congelada > 0.0:
		var hasta := -30.0 * (1.0 if _congelada > 0.0 else frio)
		var fuerza := 0.34 if _congelada > 0.0 else 0.2
		for yy in range(0, int(floor(hasta)) - 1, -1):
			var hw := _ancho_en(float(yy))
			if hw < 0.5:
				continue
			for xx in range(int(-hw), int(hw) + 1):
				var filo := hasta + 1.5 * sin(xx * 1.7 + _tiempo * 1.5)
				if yy < filo:
					continue
				var borde := absf(xx) >= hw - 1.0
				var arriba := yy < filo + 1.0
				var col: Color = HIELO[0] if (borde or arriba) else HIELO[2]
				draw_rect(Rect2(Vector2(xx, yy - 1), Vector2.ONE), Color(col, fuerza + (0.45 if arriba else (0.25 if borde else 0.0))))
		for i in _cristales.size():
			var c: Vector2 = _cristales[i]
			if c.y < hasta:
				continue
			var brillo := 0.55 + 0.45 * sin(_tiempo * 3.0 + i)
			var col: Color = HIELO[i % 3]
			draw_rect(Rect2((c + Vector2(0, -1)).floor(), Vector2.ONE), Color(col, 0.85 * brillo))
			if i % 4 == 0:
				# una agujita de hielo
				draw_rect(Rect2((c + Vector2(0, -2)).floor(), Vector2(1, 2)), Color(HIELO[0], 0.7 * brillo))
		# el filo de la escarcha, una línea que sube
		if _congelada <= 0.0:
			for x in range(-6, 7, 2):
				draw_rect(Rect2(Vector2(x, hasta + sin(_tiempo * 2.0 + x) * 0.8).floor(), Vector2(1, 1)), Color(HIELO[0], 0.6))
	for v in _vaho:
		var t: float = v["t"] / 1.2
		var p: Vector2 = v["p"] + Vector2(t * 6.0, -t * 6.0)
		draw_circle(p, 1.5 + t * 2.5, Color(0.92, 0.96, 1.0, 0.35 * (1.0 - t)))
