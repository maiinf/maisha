extends Node2D
## EL CORAZÓN DEL METEORITO (jefe final de Asterhaul, en el Santuario del Núcleo; opción A elegida por Iam: la
## Semilla Estelar Encadenada): un núcleo poliédrico de ámbar vivo que flota dentro de TRES AROS de hierro meteórico.
## Cada aro cede ante un poder de la Tierra, en orden; luego el núcleo queda al aire.
##   SIEMPRE: el LATIDO. Se contrae (el aviso) y suelta una onda que se abre hasta LATIDO_R px (1 hoja a quien pille
##   en el borde). Lejos, o pegada a él, no pasa nada.
##   1. EL ARO SÍSMICO (fuera, de piedra con grietas de ámbar): tras cada latido el Corazón SE POSA un momento y el
##      aro toca el suelo. Una CARGA SÍSMICA contra él entonces lo agrieta (está en «sismicos»). Dos, y se parte.
##   2. EL ARO MAGNÉTICO (en medio, de hierro): lanza FRAGMENTOS de hierro meteórico por el aire hacia Maisha (su
##      sombra avisa; 1 hoja). Un PULSO MAGNÉTICO con el fragmento ya cayendo se lo devuelve contra el aro (está en
##      «magneticos»). Dos, y se parte.
##   3. EL ARO DE ÁMBAR (dentro, de cristal): el Corazón DERIVA por el Santuario y dispara RAYOS en línea (el aviso:
##      la línea). Si pasa por donde llega la onda de un monolito que canta (asterhaul/monolito.gd), el aro resuena y
##      se raja. Dos, y se rompe.
##   4. EL NÚCLEO, al aire: baja hasta casi el suelo y deriva despacio; el cetro (1) y las semillas (2) le llegan.
##      Latidos y rayos más seguidos. 6 golpes.
##   5. No muere: se CALMA. Se posa en el altar y se ve lo que guardaba dentro (señal «calmado»).
## La vida (12) se cuenta de una vez en la barra: 2 por aro y 6 el núcleo.
## Dibujo: arte/mundos/asterhaul/nucleo/corazon.png (pintar_nucleo.py); los aros y los ataques se dibujan aquí.
## Música: «jefe_corazon».

signal calmado
signal vida_cambiada(nueva: int)

const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const DIBUJO := preload("res://arte/mundos/asterhaul/nucleo/corazon.png")
const BLOQUE := preload("res://arte/mundos/asterhaul/fundicion/bloque.png")
const MONOLITO := preload("res://scripts/mundo/asterhaul/monolito.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const PARTE := preload("res://scripts/enemigos/parte_jefe.gd")
const NOMBRE := "El Corazón del Meteorito"
const VIDA_MAX := 12
const GOLPES_ARO := 2
const ALTURA := 34.0
const ALTURA_NUCLEO := 10.0
const LATIDO_AVISO := 0.7
const LATIDO_R := 112.0
const LATIDO_VEL := 150.0
const LATIDO_BANDA := 12.0
const POSADO := 1.7
const FRAG_CAE := 1.15
const REPELE_A := 70.0
const RAYO_AVISO := 0.85
const RAYO_DURA := 0.35
const RAYO_LARGO := 300.0
const RAYO_ANCHO := 10.0
const DERIVA := 22.0
const INMUNE_ARO := 2.5
## los tres aros: [nombre, radio, color del metal, color de la luz]
const AROS := [["sismico", 40.0, Color("6a503a"), Color("ffb040")], ["magnetico", 32.0, Color("464c5c"), Color("6ad0f0")],
	["ambar", 25.0, Color("8a5a1a"), Color("ffd878")]]

enum Fase { DORMIDO, FLOTA, LATE, POSADO, FRAGMENTO, AVISA_RAYO, RAYO, CALMADO }

## el Santuario: su centro y sus semiejes en px (los pone la escena)
var centro := Vector2.ZERO
var radios := Vector2(240, 160)
var vida := VIDA_MAX
var fase := Fase.DORMIDO
var altura := ALTURA
var _t := 0.0
var _tiempo := 0.0
var _cd := 2.0
var _ataques := 0
var _destello := 0.0
var _inmune := 0.0
var _onda := -1.0                      # el radio de la onda del latido (−1: no hay)
var _dio := false
var _frag := Vector2.ZERO              # dónde cae el fragmento
var _devuelto := false
var _rayo := Vector2.RIGHT
var _rayo_dio := false
var _rumbo := 0.0
var _sprite: Sprite2D
var _aros: Node2D
var _suelo: Node2D
var _barra: CanvasLayer = null
var radio_carga := 30.0


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	add_to_group("sismicos")
	add_to_group("magneticos")
	add_to_group("corazones")
	_suelo = Node2D.new()
	_suelo.top_level = true
	_suelo.z_index = -1
	_suelo.draw.connect(_dibujar_suelo)
	add_child(_suelo)
	_aros = Node2D.new()
	_aros.draw.connect(_dibujar_aros)
	add_child(_aros)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	add_child(_sprite)
	_aros.z_index = 1
	for donde: Vector2 in [Vector2(0, 8), Vector2(-24, 0), Vector2(24, 0)]:
		var parte: Node2D = PARTE.new()
		parte.jefe = self
		parte.al_golpe = "recibir_golpe"
		parte.al_danio = "recibir_danio"
		parte.position = donde
		parte.add_to_group("golpeables")
		parte.add_to_group("daniables")
		add_child(parte)


## Qué aro queda (0 sísmico, 1 magnético, 2 de ámbar) o 3 si el núcleo ya está al aire
func aro() -> int:
	return clampi((VIDA_MAX - vida) / GOLPES_ARO, 0, 3)


func expuesto() -> bool:
	return aro() >= 3


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	Sonido.musica("jefe_corazon")
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	_cambiar(Fase.FLOTA)
	_cd = 1.8


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_inmune = maxf(0.0, _inmune - delta)
	_aros.queue_redraw()
	_suelo.queue_redraw()
	_mover_onda(delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null or fase == Fase.DORMIDO or fase == Fase.CALMADO:
		_dibujar()
		return
	# con el aro de ámbar (y con el núcleo al aire) deriva por el Santuario
	if aro() >= 2 and fase in [Fase.FLOTA, Fase.AVISA_RAYO, Fase.RAYO]:
		_rumbo += delta * 0.45
		var meta := centro + Vector2(cos(_rumbo), sin(_rumbo * 1.3)) * radios * 0.55
		global_position = global_position.move_toward(meta, DERIVA * (0.6 if expuesto() else 1.0) * delta)
	# el aro de ámbar resuena con la onda de un monolito
	if aro() == 2 and _inmune <= 0.0 and MONOLITO.que_suena_en(get_tree(), global_position) != null:
		_romper_aro()
	altura = move_toward(altura, _altura_meta(), 70.0 * delta)
	match fase:
		Fase.FLOTA:
			_cd -= delta
			if _cd <= 0.0 and not maisha.get("esta_caida"):
				_ataques += 1
				if aro() == 1 and _ataques % 2 == 0:
					_frag = maisha.global_position
					_devuelto = false
					_cambiar(Fase.FRAGMENTO)
					Sonido.efecto("corazon_aro", 0.0, global_position)
				elif aro() >= 2 and _ataques % 2 == 0:
					_rayo = (maisha.global_position - global_position).normalized()
					_cambiar(Fase.AVISA_RAYO)
				else:
					_cambiar(Fase.LATE)
		Fase.LATE:
			if _t >= LATIDO_AVISO:
				_onda = 6.0
				_dio = false
				Sonido.efecto("corazon_latido", 2.0, global_position)
				Impacto.temblar(2.0, 0.2)
				if aro() == 0:
					_cambiar(Fase.POSADO)
					Sonido.efecto("cosechadora_choque", -4.0, global_position)
				else:
					_seguir()
		Fase.POSADO:
			if _t >= POSADO:
				_seguir()
		Fase.FRAGMENTO:
			if _t < 0.45:
				_frag = maisha.global_position            # apunta un momento; luego el fragmento ya vuela
			if _t >= FRAG_CAE:
				_caer_fragmento(maisha)
		Fase.AVISA_RAYO:
			if _t < RAYO_AVISO * 0.6:
				_rayo = (maisha.global_position - global_position).normalized()
			if _t >= RAYO_AVISO:
				_rayo_dio = false
				_cambiar(Fase.RAYO)
				Sonido.efecto("corazon_rayo", 0.0, global_position)
		Fase.RAYO:
			if not _rayo_dio:
				var rel := maisha.global_position - global_position
				var a_lo_largo := rel.dot(_rayo)
				if a_lo_largo > 0.0 and a_lo_largo < RAYO_LARGO and absf(rel.cross(_rayo)) < RAYO_ANCHO:
					_rayo_dio = true
					maisha.call("recibir_danio", 1, global_position, "rayo")
			if _t >= RAYO_DURA:
				_seguir()
	_dibujar()


func _altura_meta() -> float:
	if fase == Fase.CALMADO:
		return 0.0
	if fase == Fase.POSADO:
		return 2.0
	return ALTURA_NUCLEO if expuesto() else ALTURA


func _seguir() -> void:
	_cd = (0.9 if expuesto() else 1.5)
	_cambiar(Fase.FLOTA)


## La onda del latido: se abre; a quien esté en su borde, 1 hoja
func _mover_onda(delta: float) -> void:
	if _onda < 0.0:
		return
	_onda += LATIDO_VEL * delta
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and not _dio and absf(maisha.global_position.distance_to(global_position) - _onda) < LATIDO_BANDA:
		_dio = true
		maisha.call("recibir_danio", 1, global_position, "latido")
	if _onda >= LATIDO_R:
		_onda = -1.0


func _caer_fragmento(maisha: Node2D) -> void:
	if _devuelto:
		_romper_aro()
		_seguir()
		return
	Sonido.efecto("roca_romper", -2.0, _frag)
	Impacto.temblar(3.0, 0.2)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 8
	astillas.position = _frag
	get_parent().add_child(astillas)
	if maisha.global_position.distance_to(_frag) < 15.0:
		maisha.call("recibir_danio", 1, _frag, "roca")
	_seguir()


## Un golpe al aro que toca (o, si es el último golpe de un aro, se parte)
func _romper_aro() -> void:
	if expuesto() or fase == Fase.CALMADO:
		return
	var antes := aro()
	vida -= 1
	_inmune = INMUNE_ARO
	_destello = 0.2
	vida_cambiada.emit(vida)
	Impacto.temblar(4.0, 0.3)
	Impacto.chispa(global_position + Vector2(0, -altura), Vector2.UP, AROS[antes][3])
	if aro() != antes:
		Sonido.efecto("corazon_abierto" if expuesto() else "corazon_roto", 2.0, global_position)
		Impacto.fogonazo(Color(1.0, 0.85, 0.5), 0.35, 0.35)
		var astillas: Node2D = ASTILLAS.new()
		astillas.cantidad = 14
		astillas.position = global_position + Vector2(0, -altura)
		get_parent().add_child(astillas)
	else:
		Sonido.efecto("corazon_golpeado", 0.0, global_position)


func _dibujar() -> void:
	_sprite.position = Vector2(0, -altura - 2.0 + sin(_tiempo * 2.0) * 1.5)
	if fase == Fase.CALMADO:
		_sprite.frame = 4
	elif expuesto():
		_sprite.frame = 3 if _destello > 0.0 else 2
	elif fase == Fase.LATE:
		_sprite.frame = 1 if int(_t * 10.0) % 2 == 0 else 0
	else:
		_sprite.frame = 1 if fmod(_tiempo, 1.1) < 0.12 else 0          # late solo, despacio


## Los aros que quedan: elipses que giran, cada una con su metal y su luz; el que toca romper, parpadea al golpearlo
func _dibujar_aros() -> void:
	if fase == Fase.CALMADO:
		return
	var c := Vector2(0, -altura - 2.0 + sin(_tiempo * 2.0) * 1.5)
	for i in range(aro(), AROS.size()):
		var d: Array = AROS[i]
		var r: float = d[1]
		var giro := _tiempo * (0.8 + i * 0.5) * (1.0 if i % 2 == 0 else -1.0)
		var inclina := 0.35 + 0.25 * sin(_tiempo * 0.7 + i)
		_aros.draw_set_transform(c, giro * 0.15, Vector2(1.0, inclina))
		var metal: Color = d[2]
		if i == aro() and _destello > 0.0:
			metal = Color.WHITE
		_aros.draw_arc(Vector2.ZERO, r, 0, TAU, 40, Color(0.05, 0.03, 0.06), 5.0)
		_aros.draw_arc(Vector2.ZERO, r, 0, TAU, 40, metal, 3.0)
		_aros.draw_arc(Vector2.ZERO, r - 1.0, giro, giro + PI * 0.6, 14, Color(d[3], 0.75), 1.0)
		for k in 6:                                                  # remaches
			var a := giro + k * TAU / 6.0
			_aros.draw_circle(Vector2(cos(a), sin(a)) * r, 1.4, Color(d[3], 0.9))
		# las grietas que lleva el aro que toca
		if i == aro():
			for k in (VIDA_MAX - vida) % GOLPES_ARO:
				var a := 0.8 + k * 2.1
				_aros.draw_line(Vector2(cos(a), sin(a)) * (r - 3.0), Vector2(cos(a + 0.12), sin(a + 0.12)) * (r + 3.0), Color(d[3]), 1.5)
	_aros.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


## En el suelo: su sombra, la onda del latido, la línea del rayo y la sombra del fragmento (y el fragmento)
func _dibujar_suelo() -> void:
	var p := global_position
	_suelo.draw_set_transform(p, 0.0, Vector2(1.0, 0.5))
	_suelo.draw_circle(Vector2.ZERO, 22.0, Color(0.02, 0.01, 0.03, 0.35))
	if fase == Fase.LATE:
		var a := clampf(_t / LATIDO_AVISO, 0.0, 1.0)
		_suelo.draw_arc(Vector2.ZERO, LATIDO_R, 0, TAU, 48, Color(1.0, 0.6, 0.2, 0.15 + 0.35 * a), 1.0)
	if _onda > 0.0:
		var f := _onda / LATIDO_R
		_suelo.draw_arc(Vector2.ZERO, _onda, 0, TAU, 48, Color(1.0, 0.75, 0.3, 0.85 * (1.0 - f * 0.6)), 3.0)
		_suelo.draw_arc(Vector2.ZERO, _onda - 5.0, 0, TAU, 48, Color(1.0, 0.95, 0.7, 0.4 * (1.0 - f)), 1.0)
	_suelo.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	if fase == Fase.AVISA_RAYO or fase == Fase.RAYO:
		var fin := p + _rayo * RAYO_LARGO
		if fase == Fase.AVISA_RAYO:
			var a := clampf(_t / RAYO_AVISO, 0.0, 1.0)
			_suelo.draw_line(p, fin, Color(1.0, 0.85, 0.4, 0.12 + 0.3 * a), RAYO_ANCHO * 2.0)
		else:
			_suelo.draw_line(p + Vector2(0, -altura), fin, Color(1.0, 0.7, 0.25, 0.55), RAYO_ANCHO * 1.6)
			_suelo.draw_line(p + Vector2(0, -altura), fin, Color(1.0, 0.98, 0.85), 3.0)
	if fase == Fase.FRAGMENTO:
		var f := clampf(_t / FRAG_CAE, 0.0, 1.0)
		_suelo.draw_circle(_frag, 5.0 + 10.0 * f, Color(0.05, 0.03, 0.02, 0.25 + 0.35 * f))
		_suelo.draw_arc(_frag, 15.0, 0, TAU, 20, Color(0.42, 0.82, 0.94, 0.6 * f), 1.0)
		if _t > 0.45:
			var g := clampf((_t - 0.45) / (FRAG_CAE - 0.45), 0.0, 1.0)
			var desde := p + Vector2(0, -altura)
			var q := (_frag.lerp(desde, g) if _devuelto else desde.lerp(_frag, g)) + Vector2(0, -sin(g * PI) * 50.0)
			_suelo.draw_texture_rect_region(BLOQUE, Rect2(q - Vector2(12, 24), Vector2(24, 28)), Rect2(24 if _devuelto else 0, 0, 24, 28))


# --- Los poderes y el daño ------------------------------------------------------------

## La Carga Sísmica: con el aro sísmico posado en el suelo, lo agrieta
func recibir_carga(_direccion: Vector2) -> bool:
	if fase == Fase.CALMADO or fase == Fase.DORMIDO:
		return false
	if aro() == 0 and fase == Fase.POSADO and _inmune <= 0.0:
		_romper_aro()
		_inmune = 0.6
	else:
		Sonido.efecto("clinc", -2.0, global_position, 0.2)
	return true


## El Pulso Magnético: devuelve el fragmento que ya cae
func recibir_pulso(origen: Vector2) -> bool:
	if fase == Fase.FRAGMENTO and not _devuelto and _t > 0.45 and _frag.distance_to(origen) < REPELE_A:
		_devuelto = true
		_t = 0.45 + (FRAG_CAE - 0.45) * 0.35
		Sonido.efecto("clinc", 2.0, _frag)
		return true
	return false


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if not expuesto() or fase == Fase.CALMADO:
		if fase != Fase.DORMIDO and fase != Fase.CALMADO:
			Sonido.efecto("clinc", -2.0, global_position, 0.2)
			Impacto.chispa(global_position + Vector2(0, -altura), Vector2.UP, Color("9aa2b6"))
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if not expuesto() or fase == Fase.CALMADO or _destello > 0.06:
		return
	vida = maxi(0, vida - (2 if tipo == "explosion" else cantidad))
	_destello = 0.12
	vida_cambiada.emit(vida)
	Impacto.chispa(global_position + Vector2(0, -altura), Vector2.UP, Color("ffd878"))
	Sonido.efecto("corazon_golpeado", 0.0, global_position)
	if vida <= 0:
		calmar()


## No muere: se calma, y se posa en el altar
func calmar() -> void:
	if fase == Fase.CALMADO:
		return
	_cambiar(Fase.CALMADO)
	_onda = -1.0
	for g in ["enemigos", "sismicos", "magneticos", "corazones"]:
		remove_from_group(g)
	for hijo in get_children():
		hijo.remove_from_group("golpeables")
		hijo.remove_from_group("daniables")
	Estado.marcar("corazon_calmado")
	Bestiario.vencido("corazon", self)
	Sonido.efecto("corazon_abierto", 4.0, global_position)
	Impacto.temblar(6.0, 1.0)
	Impacto.fogonazo(Color(1.0, 0.9, 0.6), 0.6, 0.8)
	if _barra:
		_barra.queue_free()
		_barra = null
	var t := create_tween()
	t.tween_property(self, "global_position", centro, 1.2)
	calmado.emit()
