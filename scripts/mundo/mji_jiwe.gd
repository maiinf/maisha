extends "res://scripts/mundo/escena_mundo.gd"
## MJI-JIWE, LA CIUDAD DEL CRÁTER (Asterhaul): un anfiteatro de tres terrazas tallado en el cráter. Se llega por la
## Puerta del Cráter del Desfiladero del Meteorito (suroeste). Las forjas están frías y los artesanos, en gris.
##   - MHUNZI, la maestra fundidora, ante su GRAN FORJA (norte): cuenta lo que pasó, despierta el ARTE DE LA
##     TIERRA («arte_tierra») y da el MAPA DE ASTERHAUL («mapa_asterhaul»). MAUTI anda cerca.
##   - LOS ARTESANOS EN GRIS (sigilia/escriba.gd con «_gris» y «_pulso»): a cada uno se le devuelve el pulso con una
##     ESQUIRLA DE ESTRELLA cualquiera (hay dos escondidas en la ciudad). Por cada pulso despierta un YUNQUE DE
##     MEMORIA de los doce de la terraza baja (asterhaul/yunques.gd).
##   - LOS HORNOS-DIAPASÓN de calle (asterhaul/pilar_diapason.gd con su dibujo): se encienden con la Carga Sísmica.
##     Con los cuatro de la terraza media, CHUMA abre el MERCADO DE LA ESCORIA («mercado_escoria»); con los seis
##     («hornos_mji_jiwe»), MWAMBA lo agradece (y la tienda da 3 Cristales: datos/tienda.json).
##   - EL GRAN DIAPASÓN, en la LOSA DEL NÚCLEO, sellada por tres cadenas (aún no se abre).
##   - Las salidas del oeste (Galerías de Ámbar), el este (Fundición de Escoria) y el norte (La Aguja Caída) tienen
##     la VERJA echada: esos caminos aún no están construidos.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const ESCRIBA := preload("res://scripts/mundo/sigilia/escriba.gd")
const VECINO := preload("res://scripts/mundo/sigilia/vecino.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const HORNO := preload("res://scripts/mundo/asterhaul/pilar_diapason.gd")
const YUNQUES := preload("res://scripts/mundo/asterhaul/yunques.gd")
const YUNQUE := preload("res://arte/mundos/asterhaul/mji_jiwe/yunque.png")
const ARTE := "res://arte/mundos/asterhaul/"
const CENTRO := Vector2(37.5, 28.5)
const RADIOS := Vector2(36.0, 27.0)
## (todo en casillas) adorno: [dibujo, casilla, ancho de su caja, fotograma (-1: no es tira)]
const ADORNOS := [
	["mji_jiwe/gran_forja", Vector2i(28, 14), 112, -1],
	["desfiladero/taller", Vector2i(30, 44), 84, -1],
	["mji_jiwe/casa", Vector2i(11, 17), 58, 0], ["mji_jiwe/casa", Vector2i(22, 9), 58, 1], ["mji_jiwe/casa", Vector2i(53, 9), 58, 1],
	["mji_jiwe/casa", Vector2i(64, 17), 58, 0], ["mji_jiwe/casa", Vector2i(64, 40), 58, 1], ["mji_jiwe/casa", Vector2i(11, 40), 58, 0],
	["mji_jiwe/diapason", Vector2i(37, 29), 44, -1],
]
const MERCADO := Vector2i(45, 44)
## vecino: [dibujo, conversación, casilla, marca que hace falta]
const VECINOS := [
	["mhunzi", "mhunzi", Vector2i(33, 15), ""],
	["mauti", "mauti_mji_jiwe", Vector2i(41, 15), "mauti_desfiladero_libre"],
	["chuma", "chuma", Vector2i(47, 45), ""],
	["mwamba", "mwamba_ciudad", Vector2i(33, 45), "mwamba_pulso"],
]
## artesano en gris: [nombre, tipo de dibujo (a cantero · b herrera · c afinador), casilla]
const ARTESANOS := [
	["jabali", "a", Vector2i(13, 19)], ["kokoto", "a", Vector2i(24, 11)], ["tofali", "a", Vector2i(62, 19)],
	["cheche", "b", Vector2i(14, 42)], ["makaa", "b", Vector2i(20, 24)], ["bati", "b", Vector2i(55, 24)],
	["mlio", "c", Vector2i(55, 11)], ["sauti", "c", Vector2i(62, 42)],
]
## horno: [casilla, terraza]
const HORNOS := [[Vector2i(22, 17), "media"], [Vector2i(53, 17), "media"], [Vector2i(53, 40), "media"], [Vector2i(22, 40), "media"],
	[Vector2i(67, 22), "alta"], [Vector2i(8, 22), "alta"]]
## las dos Esquirlas de Estrella escondidas en la ciudad: [casilla, marca]
const ESQUIRLAS := [[Vector2i(58, 48), "esquirla/mji_jiwe_sur"], [Vector2i(8, 33), "esquirla/mji_jiwe_oeste"]]
## verja: [casilla, lo que se lee]
const VERJAS := [[Vector2i(3, 28), "mji_verja_oeste"], [Vector2i(72, 28), "mji_verja_este"], [Vector2i(37, 3), "mji_verja_norte"]]

var _yunques: Array[Sprite2D] = []
var _mercado: Sprite2D


func _ready() -> void:
	super()
	Estado.marcar("mji_jiwe")
	_poner_cosas()
	if not Estado.tiene("mji_jiwe_llegada"):
		_pensar_al_llegar.call_deferred()


func _sitio(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


func _poner_cosas() -> void:
	for a in ADORNOS:
		_poner_adorno(a[0], a[1], a[2], a[3])
	_mercado = _poner_adorno("mji_jiwe/mercado", MERCADO, 100, 1 if Estado.tiene("mercado_escoria") else 0).get_child(0)
	_leer("mji_diapason", _sitio(Vector2i(37, 29)) + Vector2(0, 6))
	for v in VERJAS:
		_poner_adorno("mji_jiwe/verja", v[0], 44, -1)
		_leer(v[1], _sitio(v[0]) + Vector2(0, 6))
	for v in VECINOS:
		if v[3] != "" and not Estado.tiene(v[3]):
			continue
		var n: StaticBody2D = VECINO.new()
		n.id = v[0]
		n.charla = v[1]
		n.position = _sitio(v[2])
		$Entidades.add_child(n)
	for a in ARTESANOS:
		var artesano: StaticBody2D = ESCRIBA.new()
		artesano.nombre = a[0]
		artesano.dibujo = "artesano_" + a[1]
		artesano.sufijo_apagado = "_gris"
		artesano.sufijo_marca = "_pulso"
		artesano.position = _sitio(a[2])
		$Entidades.add_child(artesano)
	for i in HORNOS.size():
		var horno: StaticBody2D = HORNO.new()
		horno.dibujo = "mji_jiwe/horno"
		horno.marca = "mji_jiwe/horno_%d" % (i + 1)
		horno.position = _sitio(HORNOS[i][0])
		$Entidades.add_child(horno)
		horno.add_to_group("hornos_diapason")
		horno.sonando.connect(_al_encender_horno)
	for e in ESQUIRLAS:
		var esquirla: Node2D = RECOGIBLE.new()
		esquirla.objeto = "esquirla_estrella"
		esquirla.marca = e[1]
		esquirla.dibujo = ARTE + "desfiladero/esquirla.png"
		esquirla.color_halo = Color(1.0, 0.75, 0.3)
		esquirla.position = _sitio(e[0])
		$Entidades.add_child(esquirla)
	# los doce Yunques de Memoria, en corro en la terraza baja (uno por artesano, en su orden)
	for i in YUNQUES.ARTESANOS.size():
		var a := -PI / 2.0 + i * TAU / 12.0
		var yunque := StaticBody2D.new()
		yunque.position = ((CENTRO + Vector2(cos(a), sin(a)) * RADIOS * 0.335) * 16.0 + Vector2(8, 14)).round()
		var sprite := Sprite2D.new()
		sprite.texture = YUNQUE
		sprite.hframes = 2
		sprite.offset = Vector2(0, -9)
		yunque.add_child(sprite)
		var forma := CollisionShape2D.new()
		var caja := RectangleShape2D.new()
		caja.size = Vector2(12, 6)
		forma.shape = caja
		forma.position = Vector2(0, -3)
		yunque.add_child(forma)
		yunque.add_to_group("yunques_memoria")
		$Entidades.add_child(yunque)
		_yunques.append(sprite)
	_despertar_yunques()


## Un adorno que no se atraviesa: su dibujo de pie (o un fotograma de su tira de dos) y una caja en la base
func _poner_adorno(dibujo: String, casilla: Vector2i, ancho: float, fotograma: int) -> StaticBody2D:
	var cuerpo := StaticBody2D.new()
	cuerpo.position = _sitio(casilla)
	var sprite := Sprite2D.new()
	sprite.texture = load(ARTE + dibujo + ".png")
	if fotograma >= 0:
		sprite.hframes = 2
		sprite.frame = fotograma
	sprite.offset = Vector2(0, -sprite.texture.get_height() / 2.0 + 2)
	cuerpo.add_child(sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(ancho, 14)
	forma.shape = caja
	forma.position = Vector2(0, -7)
	cuerpo.add_child(forma)
	$Entidades.add_child(cuerpo)
	return cuerpo


func _leer(charla: String, donde: Vector2) -> void:
	var lectura: Node2D = LECTURA.new()
	lectura.charla = charla
	lectura.position = donde
	$Entidades.add_child(lectura)


func _despertar_yunques() -> void:
	for i in _yunques.size():
		_yunques[i].frame = 1 if Estado.tiene(YUNQUES.marca(YUNQUES.ARTESANOS[i])) else 0


## Cuántos hornos de una terraza («» = todas) están encendidos, y de cuántos
func hornos(terraza := "") -> Vector2i:
	var n := Vector2i.ZERO
	for i in HORNOS.size():
		if terraza == "" or HORNOS[i][1] == terraza:
			n.y += 1
			if Estado.tiene("mji_jiwe/horno_%d" % (i + 1)):
				n.x += 1
	return n


func _al_encender_horno() -> void:
	var media := hornos("media")
	var todos := hornos()
	if todos.x == todos.y and not Estado.tiene("hornos_mji_jiwe"):
		Estado.marcar("hornos_mji_jiwe")
	if media.x == media.y and not Estado.tiene("mercado_escoria"):
		Estado.marcar("mercado_escoria")
	elif todos.x < todos.y:
		_hud.mostrar_mensaje("Hornos encendidos: %d de %d" % [todos.x, todos.y])


func _al_poner_marca(marca: String) -> void:
	super(marca)
	if marca.ends_with("_pulso"):
		_despertar_yunques()
		if YUNQUES.completo():
			Estado.marcar("yunques_completos")
		_hud.mostrar_mensaje("Yunques de Memoria: %d de %d" % [YUNQUES.cuantos(), YUNQUES.ARTESANOS.size()])
	elif marca == "mercado_escoria":
		_mercado.frame = 1
		Sonido.efecto("arte_sube", -4.0, _sitio(MERCADO))
		_hud.mostrar_mensaje("Chuma abre el Mercado de la Escoria")
	elif marca == "hornos_mji_jiwe":
		_hud.mostrar_mensaje("Todos los hornos de Mji-Jiwe arden")
	elif marca == "arte_tierra":
		_hud.mostrar_mensaje("Ha despertado el Arte de la Tierra")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("mji_jiwe_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "mji_jiwe_llegada")
	Estado.marcar("mji_jiwe_llegada")
