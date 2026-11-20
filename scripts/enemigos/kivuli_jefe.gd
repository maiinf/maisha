extends Node2D
## KIVULI, EL ALACRÁN DE RELOJ DE ARENA (jefe de las Dunas de Penumbra, el Valle del Ocaso; opción A elegida por
## Iam): un alacrán de obsidiana del tamaño de una casa, con un reloj de arena dorado en el vientre. Guarda la Pesa
## del Oeste. Vive en la sombra: el sol del valle lo deslumbra.
##   1. ENTERRADO: un montículo de arena que avanza bajo el suelo hasta la sombra (de un obelisco del Cráter) más
##      cercana a Maisha. Así no hay forma de tocarlo.
##   2. EMERGE en esa sombra y ACECHA: si Maisha se acerca, AVISA (la cola en alto, el aguijón brilla) y PICA
##      (1 hoja si está a su alcance). Al rato se vuelve a enterrar y busca otra sombra.
##   3. Si mientras acecha GIRA EL SOL (un Reloj de Sol del Cráter) y su sombra se va, le da la luz de lleno: se
##      deslumbra y SE VUELCA panza arriba. VOLCADO (VOLCADO s o GOLPES_VOLCADO golpes), el reloj del vientre está al
##      aire: cetro 1, semillas 2.
##   4. Con la mitad de la vida (FURIA): se mueve más deprisa bajo la arena, acecha menos y pica dos veces.
##   5. Vencido: suelta la PESA DEL OESTE («peso_oeste») y un Farol de la Hora.
## Dibujo: arte/mundos/ocaso/dunas/kivuli.png (herramientas/pintar_dunas.py). Música: «jefe_kivuli».

signal destruido
signal vida_cambiada(nueva: int)

const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const DIBUJO := preload("res://arte/mundos/ocaso/dunas/kivuli.png")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const NOMBRE := "Kivuli, el Alacrán de Reloj de Arena"
const VIDA_MAX := 9
const VOLCADO := 4.0
const VOLCADO_FURIA := 3.0
const GOLPES_VOLCADO := 3              # a los tres golpes se da la vuelta y se entierra (hay que volcarlo tres veces)
const ACECHA := 4.5
const ACECHA_FURIA := 3.2
const ENTERRADO_VEL := 85.0
const ENTERRADO_VEL_FURIA := 120.0
const EMERGE := 0.6
const AVISO := 0.8
const AVISO_FURIA := 0.55
const ALCANCE := 44.0
const VE := 90.0

enum Fase { DORMIDO, ENTERRADO, EMERGE, ACECHA, AVISA, VOLCADO, VENCIDO }

## el Cráter: su centro y sus semiejes en px (los pone la escena); Kivuli no sale de él
var centro := Vector2.ZERO
var radios := Vector2(170, 140)
var vida := VIDA_MAX
var fase := Fase.DORMIDO
var _t := 0.0
var _tiempo := 0.0
var _meta := Vector2.ZERO
var _picadas := 0
var _golpes := 0
var _destello := 0.0
var _sprite: Sprite2D
var _barra: CanvasLayer = null
var _sol: Node


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("kivuli_jefe")
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 30.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 6
	_sprite.offset = Vector2(0, -26)
	add_child(_sprite)
	_sol = get_tree().get_first_node_in_group("sol")
	_meta = position


func furia() -> bool:
	return vida <= VIDA_MAX / 2


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	Sonido.musica("jefe_kivuli" if ResourceLoader.exists("res://audio/musica/jefe_kivuli.ogg") else "jefe_kifaru")
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	_enterrarse()


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _dentro(p: Vector2) -> bool:
	return ((p - centro) / radios).length() < 0.92


## La casilla de sombra del Cráter más cercana a Maisha (si no hay ninguna, se queda donde está)
func _buscar_sombra() -> Vector2:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var mejor := global_position
	var mejor_d := INF
	for c: Vector2i in _sol._sombra:
		var p := Vector2(c) * 16.0 + Vector2(8, 8)
		if not _dentro(p):
			continue
		var d := p.distance_to(maisha.global_position) if maisha else 0.0
		if d < mejor_d:
			mejor_d = d
			mejor = p
	return mejor


func _enterrarse() -> void:
	_meta = _buscar_sombra()
	_cambiar(Fase.ENTERRADO)
	Sonido.efecto("kivuli_arena", -1.5, global_position, 0.15)


func expuesto() -> bool:
	return fase == Fase.VOLCADO


func _process(delta: float) -> void:
	if fase == Fase.DORMIDO or fase == Fase.VENCIDO:
		_dibujar()
		return
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var d := (maisha.global_position - global_position) if maisha else Vector2.INF
	match fase:
		Fase.ENTERRADO:
			global_position = global_position.move_toward(_meta, (ENTERRADO_VEL_FURIA if furia() else ENTERRADO_VEL) * delta)
			if global_position.distance_to(_meta) < 2.0:
				_cambiar(Fase.EMERGE)
				Sonido.efecto("kivuli_emerge", -1.0, global_position, 0.08)
				Impacto.temblar(2.0, 0.3)
		Fase.EMERGE:
			if _t >= EMERGE:
				_cambiar(Fase.ACECHA)
		Fase.ACECHA:
			if _al_sol():
				_volcar()
			elif maisha and not maisha.get("esta_caida") and d.length() < VE:
				_picadas = 0
				_cambiar(Fase.AVISA)
			elif _t >= (ACECHA_FURIA if furia() else ACECHA):
				_enterrarse()
		Fase.AVISA:
			if _al_sol():
				_volcar()
			elif _t >= (AVISO_FURIA if furia() else AVISO):
				_picar(maisha, d)
		Fase.VOLCADO:
			if _t >= (VOLCADO_FURIA if furia() else VOLCADO):
				_enterrarse()
	_dibujar()


func _al_sol() -> bool:
	return _sol != null and not _sol.en_sombra(global_position)


func _picar(maisha: Node2D, d: Vector2) -> void:
	Sonido.efecto("kivuli_pica", 0.0, global_position, 0.1)
	if maisha and d.length() < ALCANCE:
		maisha.call("recibir_danio", 1, global_position, "contacto")
	_picadas += 1
	if furia() and _picadas < 2:
		_cambiar(Fase.AVISA)
		_t = (AVISO_FURIA if furia() else AVISO) * 0.5
	else:
		_cambiar(Fase.ACECHA)
		_t = ACECHA * 0.5


func _volcar() -> void:
	_cambiar(Fase.VOLCADO)
	_golpes = 0
	Sonido.efecto("kivuli_vuelca", 0.0, global_position)
	Impacto.temblar(3.0, 0.4)
	Impacto.chispa(global_position + Vector2(0, -30), Vector2.UP, Color(1.0, 0.85, 0.5))


func _dibujar() -> void:
	_sprite.position = Vector2.ZERO
	match fase:
		Fase.DORMIDO, Fase.ENTERRADO:
			_sprite.frame = 0
		Fase.EMERGE:
			_sprite.frame = 1
			_sprite.position.y = (1.0 - _t / EMERGE) * 10.0
		Fase.ACECHA:
			_sprite.frame = 1
		Fase.AVISA:
			_sprite.frame = 2
			_sprite.position.x = roundf(sin(_tiempo * 50.0) * 0.8)
		Fase.VOLCADO:
			_sprite.frame = 4 if _destello > 0.0 else 3
		Fase.VENCIDO:
			_sprite.frame = 5


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if not expuesto():
		if fase != Fase.VENCIDO and fase != Fase.ENTERRADO:
			Sonido.efecto("clinc", -2.0, global_position, 0.2)
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if not expuesto():
		return
	vida = maxi(0, vida - (2 if tipo == "explosion" else cantidad))
	_destello = 0.12
	vida_cambiada.emit(vida)
	Impacto.chispa(global_position + Vector2(0, -26), Vector2.UP, Color("ffd878"))
	if vida <= 0:
		morir()
		return
	_golpes += 1
	if _golpes >= GOLPES_VOLCADO:
		_enterrarse()


func morir() -> void:
	if fase == Fase.VENCIDO:
		return
	_cambiar(Fase.VENCIDO)
	for g in ["golpeables", "daniables", "enemigos", "kivuli_jefe"]:
		remove_from_group(g)
	Estado.marcar("kivuli_vencido")
	Estado.marcar("peso_oeste")
	Bestiario.vencido("kivuli", self)
	Sonido.efecto("kivuli_muere", 0.0, global_position)
	Sonido.musica("victoria")
	Impacto.temblar(6.0, 0.8)
	if _barra:
		_barra.queue_free()
		_barra = null
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 20
	astillas.position = global_position + Vector2(0, -20)
	get_parent().add_child(astillas)
	# el Farol de la Hora que guardaba cae a su lado
	var farol: Node2D = RECOGIBLE.new()
	farol.objeto = "farol_hora"
	farol.marca = "farol/dunas_3"
	farol.dibujo = "res://arte/mundos/ocaso/mirador/farol.png"
	farol.color_halo = Color(1.0, 0.75, 0.35)
	var hacia := (centro - global_position).normalized()
	farol.position = global_position + (hacia if hacia != Vector2.ZERO else Vector2.DOWN) * 40.0
	get_parent().add_child(farol)
	destruido.emit()
