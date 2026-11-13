extends Node2D
## KENGELE, LA GRAN CAMPANA MUDA (jefe del Observatorio de la Aurora, Sigilia; opción A elegida por Iam): una campana
## colosal de bronce grabada con constelaciones, con el badajo de tinta helada. Por eso no suena.
##   1. FLOTA sobre la Gran Cúpula, hacia Maisha. No hay forma de darle: el cetro rebota en el bronce.
##   2. TAÑIDO MUDO: se inclina hacia Maisha (el aviso) y suelta una ONDA DE SILENCIO, un abanico que se abre.
##      Si la alcanza: 1 hoja y SILENCIO s sin poder trazar sigilos. Se esquiva saliéndose del abanico.
##   3. EMBISTE: se alza, tiembla (el aviso) y cruza la cúpula en línea recta (1 hoja si la pilla).
##   4. LOS DIAPASONES de la cúpula (sigilia/bobina.gd, «diapasones»): cargados con el Sigilo de Rayo zumban unos
##      segundos. Si Kengele, EMBISTIENDO, pasa junto a uno cargado, RESUENA DE VERDAD: el badajo se resquebraja y
##      cae ATURDIDA (ATURDIDA s o 3 golpes): cetro 1, semillas 2. Luego se alza otra vez.
##   5. Con la mitad de la vida (FURIA): dos ondas seguidas (la segunda, más ancha) y embiste antes y más deprisa.
##   6. Vencida: se queda en el suelo, sonando por fin, y suelta la 3.ª ficha del observatorio (la de Mlinzi).
## Dibujo: arte/mundos/sigilia/observatorio/kengele.png (herramientas/pintar_observatorio.py). Música: «jefe_kengele».

signal destruido
signal vida_cambiada(nueva: int)

const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const DIBUJO := preload("res://arte/mundos/sigilia/observatorio/kengele.png")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const NOMBRE := "Kengele, la Gran Campana Muda"
const VIDA_MAX := 10
const ATURDIDA := 5.0
const GOLPES_ATURDIDA := 3
const FLOTA_VEL := 22.0
const EMBISTE_VEL := 230.0
const EMBISTE_VEL_FURIA := 280.0
const AVISO_TANIDO := 0.7
const AVISO_EMBISTE := 0.95
const AVISO_EMBISTE_FURIA := 0.65
const ONDA_VEL := 95.0
const ONDA_MAX := 170.0
const ONDA_ANCHO := 1.05               # medio abanico, en radianes (60°)
const ONDA_ANCHO_2 := 1.4              # el de la segunda onda de la furia
const SILENCIO := 3.0
const RESUENA_A := 46.0                # a cuánto de un diapasón cargado resuena
const TOCA := 24.0

enum Fase { DORMIDA, FLOTA, AVISA_TANIDO, AVISA_EMBISTE, EMBISTE, ATURDIDA, VENCIDA }

## la Gran Cúpula: su centro y sus semiejes en px (los pone la escena); Kengele no sale de ella
var centro := Vector2.ZERO
var radios := Vector2(220, 160)
var vida := VIDA_MAX
var fase := Fase.DORMIDA
var _t := 0.0
var _tiempo := 0.0
var _cd := 2.0
var _ataques := 0                      # (tañido, tañido, embiste, ...)
var _golpes := 0
var _destello := 0.0
var _rumbo := Vector2.DOWN
var _toco := false
var _ondas: Array[Dictionary] = []     # {origen, angulo, ancho, r, dio}
var _onda_pendiente := -1.0
var _sprite: Sprite2D
var _efectos: Node2D
var _barra: CanvasLayer = null


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	add_to_group("golpeables")
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 26.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -44)
	add_child(_sprite)
	_efectos = Node2D.new()
	_efectos.top_level = true            # (las ondas se quedan donde salieron aunque la campana se mueva)
	_efectos.z_index = 1
	_efectos.draw.connect(_dibujar_efectos)
	add_child(_efectos)


func furia() -> bool:
	return vida <= VIDA_MAX / 2


func despertar() -> void:
	if fase != Fase.DORMIDA:
		return
	Sonido.musica("jefe_kengele")
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	_cambiar(Fase.FLOTA)
	_cd = 1.6


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


## ¿Está el punto dentro de la cúpula? (con un margen hacia dentro)
func _dentro(p: Vector2, margen := 20.0) -> bool:
	var d := (p - centro) / (radios - Vector2(margen, margen))
	return d.length() <= 1.0


func _process(delta: float) -> void:
	_t += delta
	_tiempo += delta
	_destello = maxf(0.0, _destello - delta)
	var m := _maisha()
	match fase:
		Fase.FLOTA:
			if m:
				var d := m.global_position - global_position
				if d.length() > 70.0 and _dentro(global_position + d.normalized() * FLOTA_VEL * delta):
					global_position += d.normalized() * FLOTA_VEL * delta
			_cd -= delta
			if _cd <= 0.0 and m:
				_ataques += 1
				_rumbo = (m.global_position - global_position).normalized()
				if _rumbo == Vector2.ZERO:
					_rumbo = Vector2.DOWN
				if _ataques % 3 == 0:
					_cambiar(Fase.AVISA_EMBISTE)
					Sonido.efecto("guardian_carga", -2.0, global_position)
				else:
					_cambiar(Fase.AVISA_TANIDO)
		Fase.AVISA_TANIDO:
			if _t >= AVISO_TANIDO:
				tanido(_rumbo.angle(), ONDA_ANCHO)
				if furia():
					_onda_pendiente = 0.55
				_cambiar(Fase.FLOTA)
				_cd = 1.5 if furia() else 2.3
		Fase.AVISA_EMBISTE:
			# (apunta hasta el último momento, menos el último tercio: ahí ya se ve por dónde va a pasar)
			var aviso := AVISO_EMBISTE_FURIA if furia() else AVISO_EMBISTE
			if m and _t < aviso * 0.65:
				_rumbo = (m.global_position - global_position).normalized()
			if _t >= aviso:
				_cambiar(Fase.EMBISTE)
				_toco = false
				Sonido.efecto("kengele_embiste", -1.0, global_position)
		Fase.EMBISTE:
			var paso := _rumbo * (EMBISTE_VEL_FURIA if furia() else EMBISTE_VEL) * delta
			if not _dentro(global_position + paso):
				Impacto.temblar(3.0, 0.25)
				Sonido.efecto("cosechadora_choque", -4.0, global_position)
				_cambiar(Fase.FLOTA)
				_cd = 1.2 if furia() else 1.8
			else:
				global_position += paso
				if not _toco and m and m.global_position.distance_to(global_position) < TOCA:
					_toco = true
					m.call("recibir_danio", 1, global_position, "contacto")
				for d in get_tree().get_nodes_in_group("diapasones"):
					if d.encendida and (d as Node2D).global_position.distance_to(global_position) < RESUENA_A:
						resonar(d)
						break
		Fase.ATURDIDA:
			if _t >= ATURDIDA or _golpes >= GOLPES_ATURDIDA:
				_alzarse()
	if _onda_pendiente > 0.0:
		_onda_pendiente -= delta
		if _onda_pendiente <= 0.0 and fase in [Fase.FLOTA, Fase.AVISA_TANIDO] and m:
			tanido((m.global_position - global_position).angle(), ONDA_ANCHO_2)
	_mover_ondas(delta)
	_sprite.frame = _fotograma()
	# flotando se mece; avisando, se inclina o tiembla
	var alto := 0.0 if fase in [Fase.ATURDIDA, Fase.VENCIDA, Fase.DORMIDA] else -10.0 + sin(_tiempo * 2.0) * 3.0
	_sprite.position = Vector2(sin(_tiempo * 50.0) * 1.5 if fase == Fase.AVISA_EMBISTE else 0.0, alto)
	_sprite.rotation = _rumbo.x * 0.22 * clampf(_t / AVISO_TANIDO, 0.0, 1.0) if fase == Fase.AVISA_TANIDO else 0.0
	_efectos.queue_redraw()


func _fotograma() -> int:
	if fase in [Fase.ATURDIDA, Fase.VENCIDA]:
		return 4 if _destello > 0.0 else 3
	if fase in [Fase.AVISA_EMBISTE, Fase.EMBISTE, Fase.AVISA_TANIDO] or (furia() and fase == Fase.FLOTA):
		return 2
	return 1 if fmod(_tiempo, 3.4) < 0.15 else 0


## El tañido mudo: una onda de silencio en abanico hacia `angulo`
func tanido(angulo: float, ancho: float) -> void:
	Sonido.efecto("kengele_tanido", -2.0, global_position, 0.1)
	Impacto.temblar(1.5, 0.15)
	_ondas.append({"origen": global_position + Vector2(0, -8), "angulo": angulo, "ancho": ancho, "r": 18.0, "dio": false})


func _mover_ondas(delta: float) -> void:
	var m := _maisha()
	for o in _ondas:
		o["r"] += ONDA_VEL * delta
		if o["dio"] or m == null:
			continue
		var d: Vector2 = m.global_position + Vector2(0, -6) - o["origen"]
		if absf(d.length() - o["r"]) < 9.0 and absf(angle_difference(d.angle(), o["angulo"])) <= o["ancho"]:
			o["dio"] = true
			if m.call("recibir_danio", 1, o["origen"], "silencio"):
				m.set("_espera_sigilo", SILENCIO)
				var hud := get_tree().get_first_node_in_group("hud")
				if hud:
					hud.mostrar_mensaje("Silencio: las runas no responden")
	_ondas = _ondas.filter(func(o: Dictionary) -> bool: return o["r"] < ONDA_MAX)


## Embistiendo, pasa junto a un diapasón cargado: la campana resuena de verdad y cae
func resonar(diapason: Node) -> void:
	if fase != Fase.EMBISTE:
		return
	diapason.apagar()
	_ondas.clear()
	_onda_pendiente = -1.0
	_golpes = 0
	_cambiar(Fase.ATURDIDA)
	add_to_group("daniables")
	Sonido.efecto("kengele_resuena", 3.0, global_position)
	Sonido.efecto("kambare_cae", -2.0, global_position)
	Impacto.temblar(5.0, 0.4)
	preload("res://scripts/mundo/relieve.gd").destello(get_parent(), position, Color("fff0a0"), 1.2, 1.2, 0.5)


func _alzarse() -> void:
	remove_from_group("daniables")
	_cambiar(Fase.FLOTA)
	_cd = 1.4
	Sonido.efecto("guardian_brama", -6.0, global_position)


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase == Fase.VENCIDA or fase == Fase.DORMIDA:
		return false
	if fase != Fase.ATURDIDA:
		# el bronce no se abolla: suena hueco, sin voz
		Sonido.efecto("clinc", -2.0, global_position, 0.3)
		Impacto.chispa(global_position + Vector2(0, -30), Vector2.UP, Color("c8c2d4"))
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if fase != Fase.ATURDIDA or tipo == "rayo":
		return
	vida = maxi(0, vida - (2 if tipo == "explosion" else cantidad))
	_golpes += 1
	_destello = 0.15
	vida_cambiada.emit(vida)
	Impacto.chispa(global_position + Vector2(0, -24), Vector2.UP, Color("f0d27a"))
	if vida <= 0:
		morir()
	else:
		Sonido.efecto("campanilla", 2.0, global_position, 0.3)
		Sonido.efecto("cosechadora_dolor", -6.0, global_position)


func morir() -> void:
	if fase == Fase.VENCIDA:
		return
	_cambiar(Fase.VENCIDA)
	remove_from_group("golpeables")
	remove_from_group("daniables")
	remove_from_group("enemigos")
	_ondas.clear()
	Estado.marcar("kengele_vencida")
	Bestiario.vencido("kengele", self)
	Sonido.efecto("kengele_resuena", 4.0, global_position)       # (por fin suena)
	Sonido.efecto("kengele_vencida", -4.0, global_position)
	Sonido.musica("victoria")
	if _barra:
		_barra.queue_free()
		_barra = null
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 18
	astillas.position = global_position + Vector2(0, -20)
	get_parent().add_child(astillas)
	# la ficha, que llevaba colgada del badajo, cae a su lado
	var ficha: Node2D = RECOGIBLE.new()
	ficha.objeto = "ficha_mlinzi"
	ficha.marca = "ficha/mlinzi"
	ficha.dibujo = "res://arte/mundos/sigilia/paso/ficha.png"
	ficha.color_halo = Color(0.85, 0.7, 1.0)
	var hacia := (centro - global_position).normalized()
	ficha.position = global_position + (hacia if hacia != Vector2.ZERO else Vector2.DOWN) * 40.0
	get_parent().add_child(ficha)
	destruido.emit()


## Las ondas de silencio (abanicos que se abren) y los avisos (hacia dónde va a tañer o a embestir)
func _dibujar_efectos() -> void:
	for o in _ondas:
		var vida_onda: float = 1.0 - o["r"] / ONDA_MAX
		for k in 3:
			var r: float = o["r"] - k * 7.0
			if r > 4.0:
				_efectos.draw_arc(o["origen"], r, o["angulo"] - o["ancho"], o["angulo"] + o["ancho"], 20,
						Color(0.72, 0.6, 1.0, vida_onda * (0.9 - k * 0.28)), 2.0 if k == 0 else 1.0)
	if fase == Fase.AVISA_TANIDO:
		var f := clampf(_t / AVISO_TANIDO, 0.0, 1.0)
		var o := global_position + Vector2(0, -8)
		_efectos.draw_arc(o, 26.0, _rumbo.angle() - ONDA_ANCHO, _rumbo.angle() + ONDA_ANCHO, 16, Color(0.72, 0.6, 1.0, 0.25 + 0.5 * f), 1.0)
		for lado: float in [-1.0, 1.0]:
			var dir := Vector2.from_angle(_rumbo.angle() + ONDA_ANCHO * lado)
			_efectos.draw_dashed_line(o + dir * 26.0, o + dir * (26.0 + 60.0 * f), Color(0.72, 0.6, 1.0, 0.5), 1.0, 4.0)
	elif fase == Fase.AVISA_EMBISTE:
		var aviso := AVISO_EMBISTE_FURIA if furia() else AVISO_EMBISTE
		var f := clampf(_t / aviso, 0.0, 1.0)
		var lado := _rumbo.orthogonal() * 14.0
		for s: float in [-1.0, 1.0]:
			_efectos.draw_dashed_line(global_position + lado * s, global_position + lado * s + _rumbo * 260.0 * f,
					Color(1.0, 0.75, 0.35, 0.35 + 0.4 * f), 1.0, 6.0)
