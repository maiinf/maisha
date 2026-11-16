extends Node2D
## EL KIFARU DE BASALTO Y GEODA (jefe de las Galerías de Ámbar, Asterhaul; opción A elegida por Iam): un rinoceronte
## colosal de placas de basalto negro con un cuerno-taladro de ámbar. Guarda la Cadena del Oeste.
##   1. PASEA hacia Maisha, despacio. No hay forma de darle: el cetro y la Carga rebotan en el basalto.
##   2. AVISA: agacha la cabeza, escarba y el cuerno se enciende (se ve la línea por donde va a pasar)...
##   3. ...y EMBISTE en línea recta, de lado a lado de la cámara (1 hoja si la pilla).
##      - Contra la pared: se queda ATONTADO un momento (y, en la furia, caen piedras del techo: su sombra avisa).
##      - Contra un PILAR DE BASALTO («pilares_basalto»): el pilar se parte y a él se le ABRE LA CORAZA.
##      - Si le da una VAGONETA lanzada (asterhaul/vagoneta.gd → recibir_vagoneta): también se le abre.
##   4. ABIERTO (ABIERTO s o GOLPES_ABIERTO golpes): la geoda del lomo al aire: cetro 1, semillas 2.
##   5. Con la mitad de la vida (FURIA): avisa menos, embiste más deprisa y dos veces seguidas.
##   6. Vencido: suelta la primera Cadena del Cráter («cadena_oeste_rota») y una Esquirla de Estrella.
## Dibujo: arte/mundos/asterhaul/galerias/kifaru.png (herramientas/pintar_galerias.py). Música: «jefe_kifaru».

signal destruido
signal vida_cambiada(nueva: int)

const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const DIBUJO := preload("res://arte/mundos/asterhaul/galerias/kifaru.png")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const NOMBRE := "El Kifaru de Basalto"
const VIDA_MAX := 12
const ABIERTO := 5.0
const GOLPES_ABIERTO := 4
const PASEA_VEL := 24.0
const EMBISTE_VEL := 200.0
const EMBISTE_VEL_FURIA := 245.0
const AVISO := 0.95
const AVISO_FURIA := 0.65
const ATONTADO := 1.3
const TOCA := 24.0
const ROCA_CAE := 0.9                  # lo que tarda en caer cada piedra (su sombra crece)

enum Fase { DORMIDO, PASEA, AVISA, EMBISTE, ATONTADO, ABIERTO, VENCIDO }

## la cámara: su centro y sus semiejes en px (los pone la escena); el Kifaru no sale de ella
var centro := Vector2.ZERO
var radios := Vector2(200, 168)
var vida := VIDA_MAX
var fase := Fase.DORMIDO
var _t := 0.0
var _tiempo := 0.0
var _cd := 2.0
var _golpes := 0
var _seguidas := 0
var _destello := 0.0
var _rumbo := Vector2.RIGHT
var _toco := false
var _rocas: Array[Dictionary] = []     # {p, t}
var _sprite: Sprite2D
var _efectos: Node2D
var _barra: CanvasLayer = null


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("sismicos")
	add_to_group("kifarus")
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 34.0)
	add_child(sombra)
	_efectos = Node2D.new()
	_efectos.top_level = true
	_efectos.z_index = -1
	_efectos.draw.connect(_dibujar_efectos)
	add_child(_efectos)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 6
	_sprite.offset = Vector2(-6, -34)
	add_child(_sprite)


func furia() -> bool:
	return vida <= VIDA_MAX / 2


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	Sonido.musica("jefe_kifaru")
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	_cambiar(Fase.PASEA)
	_cd = 1.8


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _dentro(p: Vector2) -> bool:
	return ((p - centro) / radios).length() < 0.9


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_caer_rocas(delta)
	_efectos.queue_redraw()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null or fase == Fase.DORMIDO or fase == Fase.VENCIDO:
		_dibujar()
		return
	var d := maisha.global_position - global_position
	match fase:
		Fase.PASEA:
			_cd -= delta
			if d.length() > 70.0 and _dentro(global_position + d.normalized() * PASEA_VEL * delta):
				global_position += d.normalized() * PASEA_VEL * delta
			_rumbo = d.normalized() if d.length() > 1.0 else _rumbo
			if _cd <= 0.0 and not maisha.get("esta_caida"):
				_seguidas = 0
				_cambiar(Fase.AVISA)
				Sonido.efecto("kaa_avisa", 2.0, global_position)
		Fase.AVISA:
			if _t < 0.5 * (AVISO_FURIA if furia() else AVISO) and d.length() > 1.0:
				_rumbo = d.normalized()                 # apunta hasta la mitad del aviso; luego ya no corrige
			if _t >= (AVISO_FURIA if furia() else AVISO):
				_toco = false
				_cambiar(Fase.EMBISTE)
				Sonido.efecto("kifaru_embiste", 0.0, global_position)
		Fase.EMBISTE:
			var paso := _rumbo * (EMBISTE_VEL_FURIA if furia() else EMBISTE_VEL) * delta
			if not _toco and d.length() < TOCA:
				_toco = true
				maisha.call("recibir_danio", 1, global_position, "contacto")
			for p in get_tree().get_nodes_in_group("pilares_basalto"):
				if not p.roto and (p as Node2D).global_position.distance_to(global_position + _rumbo * 18.0) < 22.0:
					p.call("romper")
					abrir()
					return
			if not _dentro(global_position + paso):
				_chocar_pared()
			else:
				global_position += paso
		Fase.ATONTADO:
			if _t >= ATONTADO:
				if furia() and _seguidas < 1:
					_seguidas += 1
					_rumbo = d.normalized() if d.length() > 1.0 else _rumbo
					_cambiar(Fase.AVISA)
				else:
					_cd = 1.2 if furia() else 2.0
					_cambiar(Fase.PASEA)
		Fase.ABIERTO:
			if _t >= ABIERTO or _golpes >= GOLPES_ABIERTO:
				_cerrar()
	_dibujar()


func _chocar_pared() -> void:
	Impacto.temblar(4.0, 0.3)
	Sonido.efecto("cosechadora_choque", -2.0, global_position)
	if furia():
		var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
		for k in 3:
			var cerca := Vector2(randf_range(-34, 34), randf_range(-26, 26)) if k > 0 else Vector2.ZERO
			_rocas.append({"p": (maisha.global_position if maisha else centro) + cerca, "t": -k * 0.25})
	_cambiar(Fase.ATONTADO)


## Las piedras del techo: su sombra crece ROCA_CAE s y entonces caen (1 hoja a quien esté debajo)
func _caer_rocas(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	for r in _rocas:
		var antes: float = r["t"]
		r["t"] = antes + delta
		if antes < ROCA_CAE and float(r["t"]) >= ROCA_CAE:
			Sonido.efecto("roca_romper", -6.0, r["p"], 0.2)
			Impacto.temblar(1.5, 0.1)
			var astillas: Node2D = ASTILLAS.new()
			astillas.cantidad = 6
			astillas.position = r["p"]
			get_parent().add_child(astillas)
			if maisha and maisha.global_position.distance_to(r["p"]) < 13.0:
				maisha.call("recibir_danio", 1, r["p"], "roca")
	_rocas = _rocas.filter(func(r: Dictionary) -> bool: return float(r["t"]) < ROCA_CAE + 0.2)


func _dibujar() -> void:
	_sprite.position = Vector2.ZERO
	_sprite.flip_h = _rumbo.x < 0.0
	_sprite.offset.x = 6.0 if _sprite.flip_h else -6.0
	match fase:
		Fase.DORMIDO:
			_sprite.frame = 0
		Fase.PASEA:
			_sprite.frame = int(_tiempo * 3.0) % 2
		Fase.AVISA:
			_sprite.frame = 2
			_sprite.position.x = roundf(sin(_tiempo * 60.0))
		Fase.EMBISTE:
			_sprite.frame = 3
		Fase.ATONTADO:
			_sprite.frame = 0
			_sprite.position.y = roundf(sin(_tiempo * 40.0) * maxf(0.0, 1.0 - _t * 2.0))
		Fase.ABIERTO, Fase.VENCIDO:
			_sprite.frame = 5 if _destello > 0.0 else 4


## El aviso (la línea por donde va a embestir) y las sombras de las piedras que caen
func _dibujar_efectos() -> void:
	if fase == Fase.AVISA:
		var a := clampf(_t / (AVISO_FURIA if furia() else AVISO), 0.0, 1.0)
		var perp := Vector2(-_rumbo.y, _rumbo.x) * 13.0
		var desde := global_position + Vector2(0, -6)
		var largo := 0.0
		while largo < 440.0 and _dentro(desde + _rumbo * (largo + 12.0)):
			largo += 12.0
		_efectos.draw_colored_polygon(PackedVector2Array([desde + perp, desde + _rumbo * largo + perp, desde + _rumbo * largo - perp, desde - perp]),
				Color(1.0, 0.55, 0.15, 0.10 + 0.22 * a))
	for r in _rocas:
		var t := clampf(float(r["t"]) / ROCA_CAE, 0.0, 1.0)
		if float(r["t"]) < 0.0:
			continue
		_efectos.draw_circle(r["p"], 4.0 + 9.0 * t, Color(0.05, 0.03, 0.02, 0.25 + 0.35 * t))
		_efectos.draw_arc(r["p"], 13.0, 0, TAU, 20, Color(1.0, 0.4, 0.2, 0.5 * t), 1.0)


# --- La coraza y el daño ------------------------------------------------------------

func abrir() -> void:
	if fase == Fase.VENCIDO or fase == Fase.DORMIDO:
		return
	_golpes = 0
	_cambiar(Fase.ABIERTO)
	Impacto.temblar(5.0, 0.35)
	Impacto.fogonazo(Color(1.0, 0.8, 0.4), 0.3, 0.3)
	Sonido.efecto("kaa_vuelca", 2.0, global_position)
	Sonido.efecto("geoda_encender", 0.0, global_position)


func _cerrar() -> void:
	_cd = 1.4
	_cambiar(Fase.PASEA)
	Sonido.efecto("clinc", 0.0, global_position)


## Una vagoneta lanzada le da: true si le ha hecho algo (entonces la vagoneta se para)
func recibir_vagoneta() -> bool:
	if fase in [Fase.DORMIDO, Fase.VENCIDO, Fase.ABIERTO]:
		return false
	abrir()
	return true


## La Carga rebota en el basalto (pero Maisha se para en seco)
func recibir_carga(_direccion: Vector2) -> bool:
	if fase == Fase.VENCIDO:
		return false
	if fase != Fase.ABIERTO:
		_rebotar()
	return true


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase != Fase.ABIERTO:
		if fase != Fase.VENCIDO:
			_rebotar()
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if fase != Fase.ABIERTO:
		return
	vida = maxi(0, vida - (2 if tipo == "explosion" else cantidad))
	_golpes += 1
	_destello = 0.12
	vida_cambiada.emit(vida)
	Impacto.chispa(global_position + Vector2(0, -34), Vector2.UP, Color("ffd878"))
	Sonido.efecto("roca_romper", -8.0, global_position, 0.3)
	if vida <= 0:
		morir()


func _rebotar() -> void:
	Sonido.efecto("clinc", -2.0, global_position, 0.2)
	Impacto.chispa(global_position + Vector2(0, -24), Vector2.UP, Color("807e98"))


func morir() -> void:
	if fase == Fase.VENCIDO:
		return
	_cambiar(Fase.VENCIDO)
	for g in ["golpeables", "daniables", "enemigos", "sismicos", "kifarus"]:
		remove_from_group(g)
	_rocas.clear()
	Estado.marcar("kifaru_vencido")
	Estado.marcar("cadena_oeste_rota")
	Bestiario.vencido("kifaru", self)
	Sonido.efecto("puerta_crater", 0.0, global_position)
	Sonido.musica("victoria")
	Impacto.temblar(6.0, 0.8)
	if _barra:
		_barra.queue_free()
		_barra = null
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 20
	astillas.position = global_position + Vector2(0, -24)
	get_parent().add_child(astillas)
	# la esquirla que llevaba incrustada en el lomo cae a su lado
	var esquirla: Node2D = RECOGIBLE.new()
	esquirla.objeto = "esquirla_estrella"
	esquirla.marca = "esquirla/kifaru"
	esquirla.dibujo = "res://arte/mundos/asterhaul/desfiladero/esquirla.png"
	esquirla.color_halo = Color(1.0, 0.75, 0.3)
	var hacia := (centro - global_position).normalized()
	esquirla.position = global_position + (hacia if hacia != Vector2.ZERO else Vector2.DOWN) * 44.0
	get_parent().add_child(esquirla)
	destruido.emit()
