extends Node2D
## EL GRIMORIO DE TINTA (jefe final de Sigilia, en la Rotonda del Primer Nombre; opción A elegida por Iam): un códice
## colosal de cuero púrpura y oro, abierto de par en par, con dos MANOS DE TINTA de garras de plumilla y la PLUMA DEL
## PRIMER NOMBRE clavada en el lomo. Es el Índice Vivo, que por miedo a olvidar escondió todos los nombres.
##   1. Flota en el centro: no hay forma de darle (el cetro rebota en el cuero).
##   2. Pasa las hojas y abre un CAPÍTULO (de fuego, de hielo o de rayo; su runa se ve sobre las páginas):
##        · FUEGO: letras que arden: un círculo grande bajo Maisha (aviso y estalla).
##        · HIELO: un renglón helado: una franja que cruza la Rotonda a la altura de Maisha.
##        · RAYO: tres rayos pequeños y rápidos, alrededor de Maisha.
##      Y de vez en cuando una MANO sale del suelo junto a Maisha y da un manotazo.
##   3. Cada capítulo se RASGA activando el PEDESTAL que lo deshace (el que late): el fuego se borra con HIELO, el
##      hielo se parte con RAYO y el rayo se pierde en el FUEGO. Rasgado, el Grimorio cae ATURDIDO (ATURDIDO s o 3
##      golpes): cetro 1, semillas 2. Si el capítulo se acaba sin rasgarlo, pasa al siguiente.
##   4. Con la mitad de la vida (FURIA): ataca más deprisa y de sus páginas salen Sombras de Renglón.
##   5. Vencido: se queda abierto en el suelo, quieto. El cierre (Mauti, Kalamu, la Pluma) lo lleva la escena.
## Dibujos: arte/mundos/sigilia/seccion/grimorio.png y mano.png. Música: «jefe_grimorio».

signal destruido
signal vida_cambiada(nueva: int)

const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const DIBUJO := preload("res://arte/mundos/sigilia/seccion/grimorio.png")
const MANO := preload("res://arte/mundos/sigilia/seccion/mano.png")
const SOMBRA := preload("res://scripts/enemigos/sombra_renglon.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const NOMBRE := "El Grimorio de Tinta"
const VIDA_MAX := 12
const ATURDIDO := 5.0
const GOLPES_ATURDIDO := 3
const PASA_HOJAS := 1.2
const CAPITULO := 11.0
const CAPITULOS := ["fuego", "hielo", "rayo"]
## el pedestal que rasga cada capítulo
const DESHACE := {"fuego": "hielo", "hielo": "rayo", "rayo": "fuego"}
const COLORES := {"fuego": Color("ff6a20"), "hielo": Color("a0dcf4"), "rayo": Color("ffe860")}
## cada capítulo: cada cuánto ataca, cuánto avisa
const RITMO := {"fuego": [2.0, 0.9], "hielo": [2.4, 1.0], "rayo": [1.5, 0.55]}
const RUNAS := {
	"fuego": [[Vector2(0, 1), Vector2(0, -0.8)], [Vector2(-0.7, -0.1), Vector2(0, 0.35), Vector2(0.7, -0.1)], [Vector2(-0.45, 0.75), Vector2(0.45, 0.75)]],
	"hielo": [[Vector2(0, -1), Vector2(0.65, 0), Vector2(0, 1), Vector2(-0.65, 0), Vector2(0, -1)], [Vector2(-0.95, -0.55), Vector2(0.95, 0.55)], [Vector2(-0.95, 0.55), Vector2(0.95, -0.55)]],
	"rayo": [[Vector2(0.45, -1), Vector2(-0.45, -0.1), Vector2(0.4, 0.05), Vector2(-0.4, 1)], [Vector2(-0.7, -1), Vector2(0.7, -1)], [Vector2(-0.7, 1), Vector2(0.7, 1)]],
}

enum Fase { DORMIDO, PASA_HOJAS, CAPITULO, ATURDIDO, VENCIDO }

## la Rotonda: su centro y sus semiejes en px (los pone la escena)
var centro := Vector2.ZERO
var radios := Vector2(240, 176)
var vida := VIDA_MAX
var fase := Fase.DORMIDO
var capitulo := ""
var _n_capitulo := -1
var _t := 0.0
var _tiempo := 0.0
var _cd := 0.0
var _cd_mano := 4.0
var _golpes := 0
var _destello := 0.0
var _ultimo_golpe := -1
## los avisos en el suelo: {forma: "circulo"|"franja", p, r, t, aviso, tipo, dio}
var _marcas: Array[Dictionary] = []
## las manos: {p, t} (0 → 0,7 sale y se alza; 0,7 golpea; hasta 1,9 se queda)
var _manos: Array[Dictionary] = []
var _sprite: Sprite2D
var _suelo: Node2D
var _encima: Node2D
var _barra: CanvasLayer = null


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	add_to_group("golpeables")
	_suelo = Node2D.new()                # los avisos, a ras de suelo (bajo todo lo que va de pie)
	_suelo.top_level = true
	_suelo.z_index = -1
	_suelo.draw.connect(_dibujar_suelo)
	add_child(_suelo)
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 34.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -46)
	add_child(_sprite)
	# es un libro de varias casillas: una parte a cada lado para que el cetro lo alcance también por las páginas
	for lado: float in [-1.0, 1.0]:
		var parte: Node2D = preload("res://scripts/enemigos/parte_jefe.gd").new()
		parte.jefe = self
		parte.al_golpe = "recibir_golpe"
		parte.position = Vector2(36.0 * lado, 2.0)
		parte.add_to_group("golpeables")
		add_child(parte)
	_encima = Node2D.new()               # la runa del capítulo, sobre las páginas
	_encima.z_index = 1
	_encima.draw.connect(_dibujar_runa)
	add_child(_encima)


func furia() -> bool:
	return vida <= VIDA_MAX / 2


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	Sonido.musica("jefe_grimorio")
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	for p in get_tree().get_nodes_in_group("pedestales_rotonda"):
		p.activado.connect(_al_activar_pedestal)
	_pasar_hojas()


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


func _pasar_hojas() -> void:
	_cambiar(Fase.PASA_HOJAS)
	capitulo = ""
	_marcas.clear()
	_marcar_pedestal("")
	Sonido.efecto("libro_abrir", 0.0, global_position)
	Sonido.efecto("pagina", -2.0, global_position, 0.2)


## Abre el capítulo siguiente (o el que se le diga)
func abrir_capitulo(cual := "") -> void:
	_n_capitulo += 1
	capitulo = cual if cual != "" else CAPITULOS[_n_capitulo % CAPITULOS.size()]
	_cambiar(Fase.CAPITULO)
	_cd = 1.0
	_marcar_pedestal(DESHACE[capitulo])
	Sonido.efecto("guardian_brama", -6.0, global_position)
	preload("res://scripts/mundo/relieve.gd").destello(get_parent(), position + Vector2(0, -40), COLORES[capitulo], 1.2, 1.2, 0.5)
	if furia() and get_tree().get_nodes_in_group("sombras_renglon").size() < 2:
		var s: Node2D = SOMBRA.new()
		s.position = position + Vector2(randf_range(-40, 40), 26)
		get_parent().add_child(s)


## El pedestal que rasga el capítulo late (los demás, no)
func _marcar_pedestal(tipo: String) -> void:
	for p in get_tree().get_nodes_in_group("pedestales_rotonda"):
		p.marcado = p.tipo == tipo


func _process(delta: float) -> void:
	_t += delta
	_tiempo += delta
	_destello = maxf(0.0, _destello - delta)
	var m := _maisha()
	match fase:
		Fase.PASA_HOJAS:
			if _t >= PASA_HOJAS:
				abrir_capitulo()
		Fase.CAPITULO:
			_cd -= delta
			if _cd <= 0.0 and m:
				_cd = RITMO[capitulo][0] * (0.7 if furia() else 1.0)
				atacar(m.global_position)
			_cd_mano -= delta
			if _cd_mano <= 0.0 and m:
				_cd_mano = 3.2 if furia() else 5.0
				sacar_mano(m.global_position + Vector2(randf_range(-10, 10), randf_range(-6, 6)))
			if _t >= CAPITULO:
				_pasar_hojas()
		Fase.ATURDIDO:
			if _t >= ATURDIDO or _golpes >= GOLPES_ATURDIDO:
				remove_from_group("daniables")
				_pasar_hojas()
	_mover_marcas(delta, m)
	_mover_manos(delta, m)
	_sprite.frame = _fotograma()
	var flota := fase in [Fase.PASA_HOJAS, Fase.CAPITULO]
	_sprite.position.y = (-8.0 + sin(_tiempo * 1.8) * 3.0) if flota else 0.0
	_sprite.position.x = sin(_tiempo * 46.0) * 1.5 if fase == Fase.PASA_HOJAS else 0.0
	_suelo.queue_redraw()
	_encima.queue_redraw()


func _fotograma() -> int:
	if fase in [Fase.ATURDIDO, Fase.VENCIDO]:
		return 4 if _destello > 0.0 else 3
	if fase == Fase.PASA_HOJAS or furia():
		return 2
	return 1 if fmod(_tiempo, 3.6) < 0.15 else 0


## El ataque del capítulo, hacia donde está Maisha
func atacar(hacia: Vector2) -> void:
	var aviso: float = RITMO[capitulo][1]
	match capitulo:
		"fuego":
			_marcas.append({"forma": "circulo", "p": hacia, "r": 30.0, "t": 0.0, "aviso": aviso, "tipo": "fuego", "dio": false})
		"hielo":
			_marcas.append({"forma": "franja", "p": hacia, "r": 13.0, "t": 0.0, "aviso": aviso, "tipo": "hielo", "dio": false})
		"rayo":
			for k in 3:
				var p := hacia + (Vector2.ZERO if k == 0 else Vector2.from_angle(randf() * TAU) * randf_range(26, 44))
				_marcas.append({"forma": "circulo", "p": p, "r": 13.0, "t": -k * 0.18, "aviso": aviso, "tipo": "rayo", "dio": false})
	Sonido.efecto("pluma", -6.0, hacia, 0.2)


func _mover_marcas(delta: float, m: Node2D) -> void:
	for marca in _marcas:
		var antes: float = marca["t"]
		marca["t"] += delta
		if antes < marca["aviso"] and marca["t"] >= marca["aviso"]:
			Sonido.efecto({"fuego": "fuego_quema", "hielo": "hielo_romper", "rayo": "chispa"}[marca["tipo"]], -3.0, marca["p"], 0.15)
			if m and _alcanza(marca, m.global_position):
				m.call("recibir_danio", 1, marca["p"], marca["tipo"])
	_marcas = _marcas.filter(func(marca: Dictionary) -> bool: return marca["t"] < marca["aviso"] + 0.35)


func _alcanza(marca: Dictionary, p: Vector2) -> bool:
	if marca["forma"] == "franja":
		return absf(p.y - marca["p"].y) <= marca["r"]
	var d: Vector2 = p - marca["p"]
	return Vector2(d.x, d.y / 0.6).length() <= marca["r"]


## Una mano de tinta sale del suelo, se alza y da un manotazo
func sacar_mano(donde: Vector2) -> void:
	var s := Sprite2D.new()
	s.texture = MANO
	s.centered = false
	s.region_enabled = true
	s.region_rect = Rect2(0, 0, 48, 1)
	s.position = donde
	s.offset = Vector2(-24, 0)
	s.visible = false
	get_parent().add_child(s)
	_manos.append({"p": donde, "t": 0.0, "sprite": s})
	Sonido.efecto("babosa_chof", -4.0, donde, 0.2)


func _limpiar_manos() -> void:
	for mano in _manos:
		var s: Variant = mano.get("sprite")
		if is_instance_valid(s):
			(s as Node).queue_free()
	_manos.clear()


func _exit_tree() -> void:
	_limpiar_manos()


func _mover_manos(delta: float, m: Node2D) -> void:
	var vivas: Array[Dictionary] = []
	for mano in _manos:
		var antes: float = mano["t"]
		mano["t"] += delta
		var t: float = mano["t"]
		var s: Sprite2D = mano.get("sprite") as Sprite2D
		if t >= 1.9:
			if is_instance_valid(s):
				s.queue_free()
			continue
		if is_instance_valid(s):
			if t < 0.7:
				var sube := clampf(t / 0.5, 0.0, 1.0)
				var alto := 56.0 * sube
				s.visible = alto >= 1.0
				if s.visible:
					s.region_rect = Rect2(0, 0, 48, alto)
					s.offset = Vector2(-24, -52.0 * sube)
					s.modulate.a = 1.0
			else:
				s.visible = true
				s.region_rect = Rect2(48, 0, 48, 56)
				s.offset = Vector2(-24, -44)
				s.modulate.a = 1.0 - clampf((t - 1.5) / 0.4, 0.0, 1.0)
		if antes < 0.7 and t >= 0.7:
			Sonido.efecto("raiz_azota", -3.0, mano["p"], 0.2)
			Impacto.temblar(1.5, 0.12)
			if m and m.global_position.distance_to(mano["p"]) < 20.0:
				m.call("recibir_danio", 1, mano["p"], "contacto")
		vivas.append(mano)
	_manos = vivas


## Un pedestal de la Rotonda se ha activado: si es el que deshace el capítulo, lo rasga
func _al_activar_pedestal(tipo: String) -> void:
	if fase == Fase.CAPITULO and tipo == DESHACE[capitulo]:
		rasgar()


func rasgar() -> void:
	if fase != Fase.CAPITULO:
		return
	_marcas.clear()
	_limpiar_manos()
	_marcar_pedestal("")
	_golpes = 0
	_cambiar(Fase.ATURDIDO)
	add_to_group("daniables")
	Sonido.efecto("pagina", 4.0, global_position)
	Sonido.efecto("kambare_cae", -2.0, global_position)
	Impacto.temblar(5.0, 0.4)
	Impacto.fogonazo(Color(COLORES[DESHACE[capitulo]], 1.0), 0.3, 0.4)


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase in [Fase.VENCIDO, Fase.DORMIDO]:
		return false
	if fase != Fase.ATURDIDO:
		Sonido.efecto("clinc", -4.0, global_position, 0.3)
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if fase != Fase.ATURDIDO or tipo in ["fuego", "rayo"] or _ultimo_golpe == Engine.get_process_frames():
		return                             # (un mismo golpe de cetro puede tocar el lomo y una página: cuenta una vez)
	_ultimo_golpe = Engine.get_process_frames()
	vida = maxi(0, vida - (2 if tipo == "explosion" else cantidad))
	_golpes += 1
	_destello = 0.15
	vida_cambiada.emit(vida)
	Impacto.chispa(global_position + Vector2(0, -20), Vector2.UP, Color("f0d27a"))
	if vida <= 0:
		morir()
	else:
		Sonido.efecto("mzizi_dolor", -4.0, global_position)


func morir() -> void:
	if fase == Fase.VENCIDO:
		return
	_cambiar(Fase.VENCIDO)
	for g in ["golpeables", "daniables", "enemigos"]:
		remove_from_group(g)
	_marcas.clear()
	_limpiar_manos()
	_marcar_pedestal("")
	for s in get_tree().get_nodes_in_group("sombras_renglon"):
		s.morir()
	Estado.marcar("grimorio_vencido")
	Bestiario.vencido("grimorio", self)
	Sonido.efecto("mzizi_vencido", 0.0, global_position)
	Sonido.musica("", 1.5)
	if _barra:
		_barra.queue_free()
		_barra = null
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 20
	astillas.position = global_position + Vector2(0, -20)
	get_parent().add_child(astillas)
	destruido.emit()


## Los avisos en el suelo (se van llenando hasta que estallan) y las manos
func _dibujar_suelo() -> void:
	for marca in _marcas:
		if marca["t"] < 0.0:
			continue
		var col: Color = COLORES[marca["tipo"]]
		var f := clampf(marca["t"] / marca["aviso"], 0.0, 1.0)
		var estalla: bool = marca["t"] >= marca["aviso"]
		var p: Vector2 = marca["p"]
		if marca["forma"] == "franja":
			var x0 := centro.x - radios.x
			var caja := Rect2(x0, p.y - marca["r"], radios.x * 2.0, marca["r"] * 2.0)
			if estalla:
				_suelo.draw_rect(caja, Color(col, 0.75))
				for k in int(radios.x / 6.0):                       # los carámbanos que suben
					var x := x0 + k * 12.0 + 6.0
					_suelo.draw_colored_polygon(PackedVector2Array([Vector2(x - 4, p.y + 8), Vector2(x + 4, p.y + 8), Vector2(x, p.y - 16)]), Color(1, 1, 1, 0.85))
			else:
				_suelo.draw_rect(caja, Color(col, 0.12 + 0.2 * f))
				_suelo.draw_rect(Rect2(caja.position, Vector2(caja.size.x * f, caja.size.y)), Color(col, 0.2))
				_suelo.draw_rect(caja, Color(col, 0.8), false, 1.0)
		else:
			_suelo.draw_set_transform(p, 0.0, Vector2(1.0, 0.6))
			if estalla:
				_suelo.draw_circle(Vector2.ZERO, marca["r"], Color(col, 0.8))
				_suelo.draw_circle(Vector2.ZERO, marca["r"] * 0.55, Color(1, 1, 1, 0.8))
			else:
				_suelo.draw_circle(Vector2.ZERO, marca["r"], Color(col, 0.14))
				_suelo.draw_circle(Vector2.ZERO, marca["r"] * f, Color(col, 0.3))
				_suelo.draw_arc(Vector2.ZERO, marca["r"], 0, TAU, 28, Color(col, 0.9), 1.0)
			_suelo.draw_set_transform(Vector2.ZERO)
	for mano in _manos:
		var t: float = mano["t"]
		var p: Vector2 = mano["p"]
		var r := clampf(t / 0.4, 0.0, 1.0) if t < 0.7 else (1.0 - clampf((t - 1.5) / 0.4, 0.0, 1.0))
		_suelo.draw_set_transform(p, 0.0, Vector2(1.0, 0.5))
		_suelo.draw_circle(Vector2.ZERO, 20.0 * r, Color(0.05, 0.03, 0.1, 0.7 * r))
		_suelo.draw_arc(Vector2.ZERO, 20.0, 0, TAU, 24, Color(0.72, 0.6, 1.0, 0.7 * r), 1.0)
		_suelo.draw_set_transform(Vector2.ZERO)


## La runa del capítulo, brillando sobre las páginas; pasando hojas, páginas que vuelan
func _dibujar_runa() -> void:
	if fase == Fase.CAPITULO:
		var col: Color = COLORES[capitulo]
		var o := _sprite.position + Vector2(0, -78)
		var late := 0.75 + 0.25 * sin(_tiempo * 5.0)
		_encima.draw_circle(o, 11.0, Color(0.04, 0.02, 0.08, 0.75))
		_encima.draw_arc(o, 11.0, 0, TAU, 24, Color(col, late), 1.0)
		for tramo: Array in RUNAS[capitulo]:
			for i in tramo.size() - 1:
				_encima.draw_line(o + tramo[i] * 7.0, o + tramo[i + 1] * 7.0, Color(col, late), 2.0)
		# cuánto le queda al capítulo
		_encima.draw_arc(o, 14.0, -PI / 2, -PI / 2 + TAU * (1.0 - _t / CAPITULO), 24, Color(col, 0.5), 1.0)
	elif fase == Fase.PASA_HOJAS:
		for k in 4:
			var u := fmod(_tiempo * 2.2 + k * 0.25, 1.0)
			var p := _sprite.position + Vector2(-40 + 80 * u, -50 - sin(u * PI) * 26.0)
			_encima.draw_rect(Rect2(p, Vector2(8, 5)), Color(0.95, 0.9, 0.78, 1.0 - u * 0.5))
