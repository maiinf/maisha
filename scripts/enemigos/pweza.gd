extends Node2D
## PWEZA, EL CALAMAR DEL TINTERO REAL (jefe del Canal de Tinta, Sigilia; opción A elegida por Iam): un calamar metido
## en un tintero enorme de latón y cristal agrietado que flota en medio de la GRAN DÁRSENA.
##   1. FLOTA en el centro, fuera del alcance. Saca TENTÁCULOS con plumilla de oro (enemigos/tentaculo_pweza.gd) junto
##      a la orilla, hacia donde está Maisha, que AZOTAN el muelle.
##   2. Un tentáculo alzado se HIELA con el Sigilo de Hielo; helado, un golpe de cetro TIRA de él: el tintero se va
##      hacia ese lado y VUELCA contra el muelle. VOLCADO (VOLCADO s o 3 golpes), Pweza queda fuera, mareado:
##      cetro 1, semillas 2. Luego se endereza y vuelve al centro.
##   3. Con la mitad de la vida (FURIA): dos tentáculos a la vez, y escupe gotas de tinta desde la boca del tintero.
##   4. Vencido: se queda volcado y quieto, y suelta la 3.ª ficha del canal (la de Chapa, una escriba de Maandiko).
## Dibujo: arte/mundos/sigilia/canal/pweza.png (herramientas/pintar_canal.py). Música: «jefe_pweza».

signal destruido
signal vida_cambiada(nueva: int)

const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const DIBUJO := preload("res://arte/mundos/sigilia/canal/pweza.png")
const TENTACULO := preload("res://scripts/enemigos/tentaculo_pweza.gd")
const PROYECTIL := preload("res://scripts/enemigos/proyectil_tinta.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const NOMBRE := "Pweza, el Calamar del Tintero"
const VIDA_MAX := 9
const VOLCADO := 4.5
const GOLPES_VOLCADO := 3
const ENTRE_TENTACULOS := 2.6
const ENTRE_TENTACULOS_FURIA := 1.7
const ENTRE_GOTAS := 3.2

enum Fase { DORMIDO, FLOTA, YENDO, VOLCADO, VUELVE, VENCIDO }

## la Dársena: su centro y los semiejes de la orilla (los pone la escena)
var orilla := Vector2(168, 151)
var vida := VIDA_MAX
var fase := Fase.DORMIDO
var _centro := Vector2.ZERO
var _t := 0.0
var _tiempo := 0.0
var _cd := 1.5
var _cd_gota := ENTRE_GOTAS
var _golpes := 0
var _destello := 0.0
var _sprite: Sprite2D
var _barra: CanvasLayer = null


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	_centro = position
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -36)
	add_child(_sprite)


func furia() -> bool:
	return vida <= VIDA_MAX / 2


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	Sonido.musica("jefe_pweza")
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	_cambiar(Fase.FLOTA)
	_cd = 1.2


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


func _process(delta: float) -> void:
	_t += delta
	_tiempo += delta
	_destello = maxf(0.0, _destello - delta)
	match fase:
		Fase.FLOTA:
			position = _centro + Vector2(sin(_tiempo * 0.7) * 10.0, sin(_tiempo * 1.3) * 3.0)
			_cd -= delta
			var maximo := 2 if furia() else 1
			if _cd <= 0.0 and get_tree().get_nodes_in_group("tentaculos").size() < maximo:
				_cd = ENTRE_TENTACULOS_FURIA if furia() else ENTRE_TENTACULOS
				sacar_tentaculo()
			if furia():
				_cd_gota -= delta
				if _cd_gota <= 0.0:
					_cd_gota = ENTRE_GOTAS
					_escupir()
		Fase.VOLCADO:
			if _t >= VOLCADO or _golpes >= GOLPES_VOLCADO:
				_enderezarse()
	_sprite.frame = _fotograma()
	var m := _maisha()
	if m and fase in [Fase.FLOTA, Fase.DORMIDO]:
		_sprite.flip_h = false


func _fotograma() -> int:
	if fase in [Fase.VOLCADO, Fase.VENCIDO]:
		return 4 if _destello > 0.0 else 3
	if fase == Fase.YENDO or _destello > 0.0 or (furia() and fase == Fase.FLOTA):
		return 2
	return 1 if fmod(_tiempo, 3.2) < 0.15 else 0


## Un punto de la orilla en el ángulo `a` (y hacia fuera, hacia el muelle)
func punto_orilla(a: float) -> Vector2:
	return _centro + Vector2(cos(a) * orilla.x, sin(a) * orilla.y)


## Saca un tentáculo junto a la orilla, más o menos hacia donde está Maisha
func sacar_tentaculo() -> Node2D:
	var m := _maisha()
	var a := randf() * TAU
	if m:
		a = (m.global_position - _centro).angle() + randf_range(-0.35, 0.35)
	var t: Node2D = TENTACULO.new()
	t.pweza = self
	t.fuera = Vector2(cos(a) * orilla.y, sin(a) * orilla.x).normalized()
	t.global_position = punto_orilla(a)
	get_parent().add_child(t)
	return t


func _escupir() -> void:
	var m := _maisha()
	if m == null:
		return
	Sonido.efecto("kambare_escupe", -3.0, global_position)
	var boca := global_position + Vector2(0, -56)
	var p: Area2D = PROYECTIL.new()
	p.direccion = (m.global_position + Vector2(0, -6) - boca).normalized()
	p.velocidad = 120.0
	p.global_position = boca
	get_parent().add_child(p)


## Un tentáculo helado ha recibido un golpe: el tintero se va hacia allí y vuelca contra el muelle
func tirar(tentaculo: Node2D) -> void:
	if fase != Fase.FLOTA:
		return
	for t in get_tree().get_nodes_in_group("tentaculos"):
		t.irse()
	_cambiar(Fase.YENDO)
	var fuera: Vector2 = tentaculo.fuera
	var hasta: Vector2 = tentaculo.global_position - fuera * 10.0
	Sonido.efecto("cristal", 0.0, global_position)
	var tw := create_tween()
	tw.tween_property(self, "position", hasta, 0.7).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
	await tw.finished
	if fase != Fase.YENDO:
		return
	Impacto.temblar(4.0, 0.3)
	Sonido.efecto("kambare_cae", 0.0, global_position)
	_golpes = 0
	_sprite.flip_h = fuera.x > 0.0            # (la boca del tintero, hacia el muelle)
	_cambiar(Fase.VOLCADO)
	add_to_group("golpeables")
	add_to_group("daniables")


func _enderezarse() -> void:
	remove_from_group("golpeables")
	remove_from_group("daniables")
	_cambiar(Fase.VUELVE)
	var tw := create_tween()
	tw.tween_property(self, "position", _centro, 1.0).set_trans(Tween.TRANS_SINE)
	await tw.finished
	if fase == Fase.VUELVE:
		_cambiar(Fase.FLOTA)
		_cd = 1.0


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase != Fase.VOLCADO:
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if fase != Fase.VOLCADO:
		return
	vida = maxi(0, vida - (2 if tipo == "explosion" else cantidad))
	_golpes += 1
	_destello = 0.15
	vida_cambiada.emit(vida)
	Impacto.chispa(global_position + Vector2(0, -20), Vector2.UP, Color("a862c0"))
	if vida <= 0:
		morir()
	else:
		Sonido.efecto("kambare_dolor", -2.0, global_position)


func morir() -> void:
	if fase == Fase.VENCIDO:
		return
	_cambiar(Fase.VENCIDO)
	remove_from_group("golpeables")
	remove_from_group("daniables")
	remove_from_group("enemigos")
	for t in get_tree().get_nodes_in_group("tentaculos"):
		t.irse()
	Estado.marcar("pweza_vencido")
	Bestiario.vencido("pweza", self)
	Sonido.efecto("kambare_vencido", 0.0, global_position)
	Sonido.musica("victoria")
	if _barra:
		_barra.queue_free()
		_barra = null
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 16
	astillas.position = global_position + Vector2(0, -20)
	get_parent().add_child(astillas)
	# la ficha sale despedida del tintero, hacia el muelle
	var ficha: Node2D = RECOGIBLE.new()
	ficha.objeto = "ficha_chapa"
	ficha.marca = "ficha/chapa"
	ficha.dibujo = "res://arte/mundos/sigilia/paso/ficha.png"
	ficha.color_halo = Color(0.85, 0.7, 1.0)
	var fuera := (global_position - _centro).normalized()
	ficha.position = global_position + (fuera if fuera != Vector2.ZERO else Vector2.DOWN) * 36.0
	get_parent().add_child(ficha)
	destruido.emit()
