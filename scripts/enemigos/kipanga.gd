extends Node2D
## KIPANGA ASTRAL, EL HALCÓN DE OBSIDIANA Y CRISTAL (jefe de la Aguja Caída, Asterhaul; opción A elegida por Iam):
## una rapaz titánica de lajas de obsidiana con el corazón de cristal resonante. Anida en la cima y guarda la
## tercera Cadena del Cráter.
##   1. PLANEA en círculos sobre el Nido (su sombra, en el suelo). En el aire no hay forma de darle.
##   2. PLUMAS: se frena, adelanta las alas (el aviso) y lanza un abanico de PLUMAS-CUCHILLA hacia Maisha (1 hoja).
##      Las que no dan se CLAVAN y zumban (asterhaul/pluma_cuchilla.gd): ENMUDECEN al monolito que tengan cerca.
##   3. PICADO: su sombra persigue a Maisha, se fija (el aviso)... y cae en picado (1 hoja). Se queda un momento
##      POSADO (el cetro rebota en las lajas) y remonta.
##   4. LOS MONOLITOS del Nido (asterhaul/monolito.gd): si vuela por donde alcanza la onda de uno que CANTA, la onda
##      le rompe el vuelo y cae ATURDIDO (ATURDIDO s o GOLPES golpes): el corazón al aire: cetro 1, semillas 2.
##      Al remontar, lo primero que hace es clavarle dos plumas al monolito que lo tiró.
##   5. Con la mitad de la vida (FURIA): más plumas, avisa menos y cae en picado dos veces seguidas.
##   6. Vencido: suelta la tercera Cadena del Cráter («cadena_norte_rota») y una Esquirla de Estrella.
## Dibujo: arte/mundos/asterhaul/aguja/kipanga.png (herramientas/pintar_aguja.py). Música: «jefe_kipanga».

signal destruido
signal vida_cambiada(nueva: int)

const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const DIBUJO := preload("res://arte/mundos/asterhaul/aguja/kipanga.png")
const PLUMA := preload("res://arte/mundos/asterhaul/aguja/pluma.png")
const PLUMA_CLAVADA := preload("res://scripts/mundo/asterhaul/pluma_cuchilla.gd")
const MONOLITO := preload("res://scripts/mundo/asterhaul/monolito.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const PARTE := preload("res://scripts/enemigos/parte_jefe.gd")
const NOMBRE := "Kipanga Astral"
const VIDA_MAX := 12
const ATURDIDO := 5.0
const GOLPES := 4
const ALTURA := 46.0
const GIRO := 0.55                     # radianes por segundo planeando
const AVISO_PLUMAS := 0.7
const PLUMA_VEL := 165.0
const AVISO_PICADO := 0.95
const AVISO_PICADO_FURIA := 0.65
const CAE := 0.32
const POSADO := 0.8
const INMUNE := 3.0                    # al remontar, lo que tarda en poder volver a tirarlo una onda
const MAX_PLUMAS := 6

enum Fase { DORMIDO, PLANEA, AVISA_PLUMAS, AVISA_PICADO, PICADO, POSADO, ATURDIDO, VENCIDO }

## el Nido: su centro y sus semiejes en px (los pone la escena)
var centro := Vector2.ZERO
var radios := Vector2(240, 176)
var vida := VIDA_MAX
var fase := Fase.DORMIDO
var altura := 0.0
var _t := 0.0
var _tiempo := 0.0
var _cd := 2.2
var _angulo := -PI / 2.0
var _ataques := 0
var _golpes := 0
var _seguidos := 0
var _destello := 0.0
var _inmune := 0.0
var _toco := false
var _desde := Vector2.ZERO
var _blanco := Vector2.ZERO            # adónde cae en picado
var _culpable: Node2D = null           # el monolito que lo tiró la última vez
var _plumas: Array[Dictionary] = []    # las que van por el aire: {p, v, queda, dio}
var _sprite: Sprite2D
var _suelo: Node2D
var _aire: Node2D
var _barra: CanvasLayer = null


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	add_to_group("kipangas")
	_suelo = Node2D.new()
	_suelo.top_level = true
	_suelo.z_index = -1
	_suelo.draw.connect(_dibujar_suelo)
	add_child(_suelo)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 6
	_sprite.offset = Vector2(0, -46)
	add_child(_sprite)
	_aire = Node2D.new()
	_aire.top_level = true
	_aire.z_index = 3
	_aire.draw.connect(_dibujar_plumas)
	add_child(_aire)
	# en el suelo el cetro le llega por delante y por las alas
	for donde: Vector2 in [Vector2(0, 8), Vector2(-28, 0), Vector2(28, 0)]:
		var parte: Node2D = PARTE.new()
		parte.jefe = self
		parte.al_golpe = "recibir_golpe"
		parte.al_danio = "recibir_danio"
		parte.position = donde
		parte.add_to_group("golpeables")
		parte.add_to_group("daniables")
		add_child(parte)


func furia() -> bool:
	return vida <= VIDA_MAX / 2


func volando() -> bool:
	return fase in [Fase.PLANEA, Fase.AVISA_PLUMAS, Fase.AVISA_PICADO]


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	Sonido.musica("jefe_kipanga")
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	_angulo = ((global_position - centro) / radios).angle()
	_cambiar(Fase.PLANEA)
	_inmune = 2.0
	_cd = 2.4


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_inmune = maxf(0.0, _inmune - delta)
	_mover_plumas(delta)
	_suelo.queue_redraw()
	_aire.queue_redraw()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null or fase == Fase.DORMIDO or fase == Fase.VENCIDO:
		_dibujar()
		return
	# la onda de un monolito que canta le rompe el vuelo
	if volando() and _inmune <= 0.0:
		var m := MONOLITO.que_suena_en(get_tree(), global_position)
		if m != null:
			caer(m)
			_dibujar()
			return
	match fase:
		Fase.PLANEA:
			altura = move_toward(altura, ALTURA, 90.0 * delta)
			_angulo += GIRO * (1.35 if furia() else 1.0) * delta
			var meta := centro + Vector2(cos(_angulo), sin(_angulo)) * radios * 0.6
			global_position = global_position.move_toward(meta, 110.0 * delta)
			_cd -= delta
			if _cd <= 0.0 and altura >= ALTURA - 1.0 and not maisha.get("esta_caida"):
				_ataques += 1
				if is_instance_valid(_culpable) or _ataques % 3 != 0:
					_cambiar(Fase.AVISA_PLUMAS)
					Sonido.efecto("kaa_avisa", 0.0, global_position)
				else:
					_seguidos = 0
					_blanco = maisha.global_position
					_cambiar(Fase.AVISA_PICADO)
					Sonido.efecto("kaa_avisa", 2.0, global_position)
		Fase.AVISA_PLUMAS:
			if _t >= AVISO_PLUMAS * (0.75 if furia() else 1.0):
				_lanzar_plumas(maisha)
				_cd = 1.6 if furia() else 2.3
				_cambiar(Fase.PLANEA)
		Fase.AVISA_PICADO:
			var aviso := AVISO_PICADO_FURIA if furia() else AVISO_PICADO
			if _t < aviso * 0.6:
				_blanco = maisha.global_position        # la sombra la sigue; luego se fija
			if _t >= aviso:
				_desde = global_position
				_toco = false
				_cambiar(Fase.PICADO)
				Sonido.efecto("kipanga_picado", 0.0, global_position)
		Fase.PICADO:
			var f := clampf(_t / CAE, 0.0, 1.0)
			global_position = _desde.lerp(_blanco, f)
			altura = ALTURA * (1.0 - f)
			if f >= 1.0:
				Impacto.temblar(4.0, 0.25)
				Sonido.efecto("cosechadora_choque", -2.0, global_position)
				if not _toco and maisha.global_position.distance_to(global_position) < 20.0:
					_toco = true
					maisha.call("recibir_danio", 1, global_position, "contacto")
				_cambiar(Fase.POSADO)
		Fase.POSADO:
			altura = 0.0
			if _t >= POSADO:
				if furia() and _seguidos < 1:
					_seguidos += 1
					_blanco = maisha.global_position
					altura = ALTURA * 0.6
					_cambiar(Fase.AVISA_PICADO)
				else:
					_angulo = ((global_position - centro) / radios).angle()
					_cd = 1.4 if furia() else 2.0
					_cambiar(Fase.PLANEA)
		Fase.ATURDIDO:
			altura = move_toward(altura, 0.0, 260.0 * delta)
			if _t >= ATURDIDO or _golpes >= GOLPES:
				_remontar()
	_dibujar()


## Lanza el abanico: al monolito que lo tiró (para enmudecerlo), o a Maisha
func _lanzar_plumas(maisha: Node2D) -> void:
	var blancos: Array[Vector2] = []
	if is_instance_valid(_culpable):
		for dx: float in [-15.0, 15.0]:
			blancos.append(_culpable.global_position + Vector2(dx, 14.0))
		_culpable = null
	else:
		var hacia := maisha.global_position - global_position
		var n := 5 if furia() else 3
		for k in n:
			blancos.append(global_position + hacia.rotated((k - (n - 1) / 2.0) * 0.22))
	for b in blancos:
		var d := b - global_position
		_plumas.append({"p": global_position, "v": d.normalized() * PLUMA_VEL, "queda": d.length(), "dio": false})
	Sonido.efecto("kipanga_pluma", 0.0, global_position)


## Las plumas por el aire: bajan en línea recta hasta su sitio y allí se clavan (si no le han dado a Maisha)
func _mover_plumas(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	for pl in _plumas:
		var paso := (pl["v"] as Vector2) * delta
		pl["p"] += paso
		pl["queda"] -= paso.length()
		var p: Vector2 = pl["p"]
		if maisha and not pl["dio"] and float(pl["queda"]) < 46.0 and maisha.global_position.distance_to(p) < 9.0:
			pl["dio"] = true
			pl["queda"] = -1.0
			maisha.call("recibir_danio", 1, p, "pluma")
		elif float(pl["queda"]) <= 0.0 and get_tree().get_nodes_in_group("plumas_cuchilla").size() < MAX_PLUMAS:
			var clavada: Node2D = PLUMA_CLAVADA.new()
			clavada.position = p
			get_parent().add_child(clavada)
	_plumas = _plumas.filter(func(pl: Dictionary) -> bool: return float(pl["queda"]) > 0.0)


## La onda de un monolito le rompe el vuelo
func caer(monolito: Node2D) -> void:
	if fase in [Fase.DORMIDO, Fase.VENCIDO, Fase.ATURDIDO]:
		return
	_culpable = monolito
	_golpes = 0
	_cambiar(Fase.ATURDIDO)
	Impacto.temblar(5.0, 0.35)
	Impacto.fogonazo(Color(0.6, 0.9, 1.0), 0.3, 0.3)
	Sonido.efecto("kaa_vuelca", 2.0, global_position)
	Sonido.efecto("diapason_ambar", 4.0, global_position)


func _remontar() -> void:
	_inmune = INMUNE
	_angulo = ((global_position - centro) / radios).angle()
	_cd = 0.9                              # (lo primero: las plumas al monolito que lo tiró)
	_cambiar(Fase.PLANEA)
	Sonido.efecto("kipanga_picado", -4.0, global_position)


func _dibujar() -> void:
	_sprite.position = Vector2(0, -altura)
	match fase:
		Fase.DORMIDO:
			_sprite.frame = 0
		Fase.PLANEA:
			_sprite.frame = int(_tiempo * 2.4) % 2
		Fase.AVISA_PLUMAS:
			_sprite.frame = 2
			_sprite.position.x = roundf(sin(_tiempo * 60.0))
		Fase.AVISA_PICADO:
			_sprite.frame = 1
			_sprite.position.x = roundf(sin(_tiempo * 60.0))
		Fase.PICADO:
			_sprite.frame = 3
		Fase.POSADO:
			_sprite.frame = 0
		Fase.ATURDIDO, Fase.VENCIDO:
			_sprite.frame = 5 if _destello > 0.0 else 4


## En el suelo: su sombra y, cuando va a caer en picado, el cerco de donde va a caer
func _dibujar_suelo() -> void:
	if fase != Fase.VENCIDO and altura > 2.0:
		var s := 1.0 - altura / (ALTURA * 2.2)
		_suelo.draw_set_transform(global_position, 0.0, Vector2(1.0, 0.5))
		_suelo.draw_circle(Vector2.ZERO, 30.0 * s, Color(0.02, 0.02, 0.06, 0.35 * s))
		_suelo.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	if fase == Fase.AVISA_PICADO or fase == Fase.PICADO:
		var a := 1.0 if fase == Fase.PICADO else clampf(_t / (AVISO_PICADO_FURIA if furia() else AVISO_PICADO), 0.0, 1.0)
		_suelo.draw_circle(_blanco, 20.0, Color(0.42, 0.82, 0.94, 0.10 + 0.2 * a))
		_suelo.draw_arc(_blanco, 20.0, 0, TAU, 28, Color(0.75, 0.96, 1.0, 0.35 + 0.55 * a), 1.5)


func _dibujar_plumas() -> void:
	for pl in _plumas:
		var p: Vector2 = pl["p"]
		var alto := clampf(float(pl["queda"]) / 120.0, 0.0, 1.0) * ALTURA      # bajan según se acercan
		_aire.draw_set_transform(p + Vector2(0, -alto - 6.0), (pl["v"] as Vector2).angle() + PI / 2.0, Vector2.ONE)
		_aire.draw_texture(PLUMA, Vector2(-7, -14))
	_aire.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


# --- El daño ---------------------------------------------------------------------

func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase != Fase.ATURDIDO:
		if fase == Fase.POSADO:
			Sonido.efecto("clinc", -2.0, global_position, 0.2)
			Impacto.chispa(global_position + Vector2(0, -24), Vector2.UP, Color("566690"))
		return false                                  # (en el aire no le llega el cetro)
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde_: Vector2, tipo: String) -> void:
	if fase != Fase.ATURDIDO or _destello > 0.06:
		return
	vida = maxi(0, vida - (2 if tipo == "explosion" else cantidad))
	_golpes += 1
	_destello = 0.12
	vida_cambiada.emit(vida)
	Impacto.chispa(global_position + Vector2(0, -30), Vector2.UP, Color("c0f4ff"))
	Sonido.efecto("roca_romper", -8.0, global_position, 0.3)
	if vida <= 0:
		morir()


func morir() -> void:
	if fase == Fase.VENCIDO:
		return
	_cambiar(Fase.VENCIDO)
	altura = 0.0
	for g in ["enemigos", "kipangas"]:
		remove_from_group(g)
	for hijo in get_children():
		hijo.remove_from_group("golpeables")
		hijo.remove_from_group("daniables")
	_plumas.clear()
	for p in get_tree().get_nodes_in_group("plumas_cuchilla"):
		p.call("romper")
	Estado.marcar("kipanga_vencido")
	Estado.marcar("cadena_norte_rota")
	Bestiario.vencido("kipanga", self)
	Sonido.efecto("puerta_crater", 0.0, global_position)
	Sonido.musica("victoria")
	Impacto.temblar(6.0, 0.8)
	if _barra:
		_barra.queue_free()
		_barra = null
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 20
	astillas.position = global_position + Vector2(0, -30)
	get_parent().add_child(astillas)
	var esquirla: Node2D = RECOGIBLE.new()
	esquirla.objeto = "esquirla_estrella"
	esquirla.marca = "esquirla/kipanga"
	esquirla.dibujo = "res://arte/mundos/asterhaul/desfiladero/esquirla.png"
	esquirla.color_halo = Color(1.0, 0.75, 0.3)
	var hacia := (centro - global_position).normalized()
	esquirla.position = global_position + (hacia if hacia != Vector2.ZERO else Vector2.DOWN) * 40.0
	get_parent().add_child(esquirla)
	destruido.emit()
