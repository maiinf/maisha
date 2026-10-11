extends Node2D
## CHISPA DE VIDA: una lucecita verde y dorada que guía a Maisha por el valle al despertar.
## Espera a que Maisha se acerque, vuela hacia el siguiente sitio (sin dejarla atrás) y se queda
## flotando encima. Cuando Maisha llega, avisa con «llegada» (el Kitovu muestra el recuerdo) y espera
## a que le digan «seguir()». Tras el último sitio, vuela hasta el brote de Maisha y entra en él.

signal llegada(indice: int)
signal terminada

const VELOCIDAD := 58.0
const ESPERA_A := 80.0           # si Maisha se queda más lejos, la chispa la espera (cerca, para no perderla)
const LLEGA_A := 34.0            # distancia al sitio para que salte el recuerdo

var sitios: Array[Vector2] = []
## Puntos de paso antes de cada sitio (rutas[i] = camino hacia sitios[i]): así la chispa lleva a Maisha
## por los caminos y no por encima de las manchas dormidas, que no la dejarían pasar
var rutas: Array = []
var indice := 0
var _paso := 0
var _estado := "esperar"          # esperar, guiar, sobre_sitio, recordando, entrar, fin
var _tiempo := 0.0
var _estela: Array[Dictionary] = []
var _suena := 0.0
var _alfa := 0.0


func _ready() -> void:
	add_to_group("chispas")
	z_index = 6
	create_tween().tween_property(self, "_alfa", 1.0, 1.2)


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


## Tras el recuerdo: a por el siguiente sitio (o, si era el último, a entrar en el brote)
func seguir() -> void:
	indice += 1
	_paso = 0
	_estado = "entrar" if indice >= sitios.size() else "esperar"


func _process(delta: float) -> void:
	_tiempo += delta
	_suena -= delta
	var maisha := _maisha()
	if maisha == null:
		return
	var a_maisha := global_position.distance_to(maisha.global_position + Vector2(0, -16))
	match _estado:
		"esperar":
			if a_maisha < 70.0:
				_estado = "guiar"
				Sonido.efecto("chispa", 0.0, global_position)
		"guiar":
			var ruta: Array = rutas[indice] if indice < rutas.size() else []
			var final := _paso >= ruta.size()
			var destino: Vector2 = (sitios[indice] if final else ruta[_paso]) + Vector2(0, -26)
			if a_maisha < ESPERA_A:
				global_position = global_position.move_toward(destino, VELOCIDAD * delta)
			if global_position.distance_to(destino) < 2.0:
				if final:
					_estado = "sobre_sitio"
				else:
					_paso += 1
			if _suena <= 0.0:
				_suena = 3.5
				Sonido.efecto("chispa", -4.0, global_position)
		"sobre_sitio":
			if maisha.global_position.distance_to(sitios[indice]) < LLEGA_A:
				_estado = "recordando"
				llegada.emit(indice)
		"entrar":
			var brote := maisha.global_position + Vector2(0, -30)
			global_position = global_position.move_toward(brote, 90.0 * delta)
			if global_position.distance_to(brote) < 3.0:
				_estado = "fin"
				Sonido.efecto("chispa_entra")
				terminada.emit()
				var t := create_tween()
				t.tween_property(self, "_alfa", 0.0, 0.4)
				t.tween_callback(queue_free)
	# estela de motas que se apagan
	if _estado in ["guiar", "entrar"] or int(_tiempo * 10.0) % 3 == 0:
		_estela.append({"p": global_position + Vector2(randf_range(-2, 2), randf_range(-2, 2)), "vida": 1.0})
	for m in _estela:
		m["vida"] -= delta * 1.4
		m["p"] += Vector2(0, -6.0 * delta)
	_estela = _estela.filter(func(m: Dictionary) -> bool: return m["vida"] > 0.0)
	queue_redraw()


## Para las pruebas automáticas: lleva la chispa directamente encima del siguiente sitio
func ir_al_sitio() -> void:
	global_position = sitios[indice] + Vector2(0, -26)
	_estado = "sobre_sitio"


func _draw() -> void:
	var flota := Vector2(0, roundf(sin(_tiempo * 2.4) * 2.0))
	for m in _estela:
		var q: Vector2 = (m["p"] - global_position).round()
		draw_rect(Rect2(q, Vector2.ONE), Color(0.44, 0.81, 0.31, 0.6 * m["vida"] * _alfa))
	var pulso := 0.5 + 0.5 * sin(_tiempo * 4.0)
	for r in [9.0, 6.0, 4.0]:
		draw_circle(flota, r + pulso * 1.5, Color(0.44, 0.81, 0.31, 0.10 * _alfa))
	draw_rect(Rect2(flota + Vector2(-1, -1), Vector2(3, 3)), Color(1.0, 0.95, 0.76, _alfa))
	draw_rect(Rect2(flota + Vector2(0, -2), Vector2(1, 5)), Color(1.0, 0.95, 0.76, 0.7 * _alfa))
	draw_rect(Rect2(flota + Vector2(-2, 0), Vector2(5, 1)), Color(1.0, 0.95, 0.76, 0.7 * _alfa))
