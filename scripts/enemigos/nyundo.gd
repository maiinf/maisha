extends Node2D
## NYUNDO, EL HERRERO DE 4 TENAZAS (jefe de la Fundición de Escoria, Asterhaul; opción B elegida por Iam): un
## autómata de forja colosal, atornillado al centro de la Gran Fragua, con cuatro brazos de tenaza al rojo.
## Guarda la Cadena del Este. No se mueve del sitio: pelea con los brazos.
##   1. EN GUARDIA: los cuatro brazos recogidos. No hay forma de darle: el cetro rebota en el peto de bronce.
##   2. TENAZAZO: un brazo se enciende y apunta (el aviso: se ve la línea)... y sale disparado hacia Maisha
##      (1 hoja si la agarra). Se queda un momento estirado y vuelve.
##      - Si Maisha suelta el PULSO MAGNÉTICO con la tenaza cerca (está en «magneticos»), la tenaza SALE REPELIDA
##        y le da a él en el peto: una abolladura.
##   3. BLOQUE: saca un bloque de hierro de la escoria y lo lanza por el aire a donde está Maisha (su sombra
##      avisa; 1 hoja). Un Pulso con el bloque ya cayendo se lo devuelve: otra abolladura.
##   4. Con REPELES abolladuras se le ABRE EL PETO (ABIERTO s o GOLPES_ABIERTO golpes): el núcleo de ámbar al
##      aire: cetro 1, semillas 2.
##   5. Con la mitad de la vida (FURIA): avisa menos y da dos tenazazos seguidos, con dos brazos.
##   6. Vencido: suelta la segunda Cadena del Cráter («cadena_este_rota») y una Esquirla de Estrella.
## Dibujo: arte/mundos/asterhaul/fundicion/nyundo.png (el cuerpo) y tenaza.png; los brazos se dibujan aquí.
## Música: «jefe_nyundo».

signal destruido
signal vida_cambiada(nueva: int)

const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const DIBUJO := preload("res://arte/mundos/asterhaul/fundicion/nyundo.png")
const TENAZA := preload("res://arte/mundos/asterhaul/fundicion/tenaza.png")
const BLOQUE := preload("res://arte/mundos/asterhaul/fundicion/bloque.png")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const PARTE := preload("res://scripts/enemigos/parte_jefe.gd")
const NOMBRE := "Nyundo, el Herrero de 4 Tenazas"
const VIDA_MAX := 12
const ABIERTO := 5.0
const GOLPES_ABIERTO := 4
const REPELES := 2
const AVISO := 0.9
const AVISO_FURIA := 0.6
const SALE := 0.32                     # lo que tarda la tenaza en llegar
const QUIETA := 0.5                    # lo que se queda estirada
const VUELVE := 0.3
const ALCANCE := 128.0
const AGARRA := 13.0
const REPELE_A := 70.0                 # a cuánto de Maisha tiene que estar la tenaza (o el bloque) para repelerla
const BLOQUE_CAE := 1.1
## de dónde sale cada brazo (desde el pie del dibujo) y dónde descansa su tenaza
const HOMBROS: Array[Vector2] = [Vector2(-30, -66), Vector2(30, -66), Vector2(-33, -40), Vector2(33, -40)]
const REPOSO: Array[Vector2] = [Vector2(-46, -86), Vector2(46, -86), Vector2(-50, -22), Vector2(50, -22)]
const ROJO := [Color("a02408"), Color("e04a10"), Color("f88a20"), Color("ffc850")]
const HIERRO := [Color("2a2e3a"), Color("464c5c"), Color("949cae")]

enum Fase { DORMIDO, GUARDIA, AVISA, TENAZA, BLOQUE, ABIERTO, VENCIDO }

var vida := VIDA_MAX
var fase := Fase.DORMIDO
var abolladuras := 0
var _t := 0.0
var _tiempo := 0.0
var _cd := 2.0
var _ataques := 0
var _brazo := 0
var _etapa := 0                        # del tenazazo: 0 sale · 1 quieta · 2 vuelve
var _punta := Vector2.ZERO             # dónde está la tenaza que ataca (desde el pie)
var _objetivo := Vector2.ZERO          # adónde va (desde el pie)
var _repelida := false
var _toco := false
var _segunda := false
var _golpes := 0
var _destello := 0.0
var _cae := Vector2.ZERO               # dónde cae el bloque (global)
var _devuelto := false
var _sprite: Sprite2D
var _brazos: Node2D
var _suelo: Node2D
var _barra: CanvasLayer = null


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	add_to_group("magneticos")
	add_to_group("nyundos")
	_suelo = Node2D.new()
	_suelo.top_level = true
	_suelo.z_index = -1
	_suelo.draw.connect(_dibujar_suelo)
	add_child(_suelo)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -56)
	add_child(_sprite)
	_brazos = Node2D.new()
	_brazos.draw.connect(_dibujar_brazos)
	add_child(_brazos)
	# no se atraviesa, y el cetro le llega por delante y por los lados
	var cuerpo := StaticBody2D.new()
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(52, 14)
	forma.shape = caja
	forma.position = Vector2(0, -6)
	cuerpo.add_child(forma)
	add_child(cuerpo)
	for donde: Vector2 in [Vector2(0, 8), Vector2(-30, -2), Vector2(30, -2)]:
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


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	Sonido.musica("jefe_nyundo")
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	_cambiar(Fase.GUARDIA)
	_cd = 1.8


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


## Dónde está (global) la tenaza que ataca
func punta() -> Vector2:
	return global_position + _punta


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	_brazos.queue_redraw()
	_suelo.queue_redraw()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null or fase == Fase.DORMIDO or fase == Fase.VENCIDO:
		_dibujar()
		return
	var hacia := maisha.global_position + Vector2(0, -8) - global_position
	match fase:
		Fase.GUARDIA:
			_cd -= delta
			if _cd <= 0.0 and not maisha.get("esta_caida"):
				_ataques += 1
				if _ataques % 3 == 0:
					_cae = maisha.global_position
					_devuelto = false
					_cambiar(Fase.BLOQUE)
					Sonido.efecto("kovu_sumerge", 0.0, global_position)
				else:
					_segunda = false
					_apuntar(hacia)
		Fase.AVISA:
			var aviso := AVISO_FURIA if furia() else AVISO
			if _t < aviso * 0.6:
				_fijar_objetivo(hacia)
			if _t >= aviso:
				_etapa = 0
				_repelida = false
				_toco = false
				_cambiar(Fase.TENAZA)
				Sonido.efecto("nyundo_tenaza", 0.0, global_position)
		Fase.TENAZA:
			_mover_tenaza(maisha)
		Fase.BLOQUE:
			if _t < 0.45:
				_cae = maisha.global_position            # apunta un momento; luego el bloque ya va por el aire
			if _t >= BLOQUE_CAE:
				_caer_bloque(maisha)
		Fase.ABIERTO:
			if _t >= ABIERTO or _golpes >= GOLPES_ABIERTO:
				abolladuras = 0
				_cd = 1.4
				_cambiar(Fase.GUARDIA)
				Sonido.efecto("clinc", 0.0, global_position)
	_dibujar()


## Elige el brazo que queda más a mano y empieza el aviso
func _apuntar(hacia: Vector2) -> void:
	var mejor := 0
	for i in HOMBROS.size():
		if i != _brazo or not _segunda:
			if (hacia - HOMBROS[i]).length() < (hacia - HOMBROS[mejor]).length() or (_segunda and mejor == _brazo):
				mejor = i
	_brazo = mejor
	_punta = REPOSO[_brazo]
	_fijar_objetivo(hacia)
	_cambiar(Fase.AVISA)
	Sonido.efecto("kaa_avisa", 0.0, global_position)


func _fijar_objetivo(hacia: Vector2) -> void:
	var d := hacia - HOMBROS[_brazo]
	_objetivo = HOMBROS[_brazo] + d.normalized() * minf(d.length() + 8.0, ALCANCE)


func _mover_tenaza(maisha: Node2D) -> void:
	match _etapa:
		0:
			_punta = REPOSO[_brazo].lerp(_objetivo, clampf(_t / SALE, 0.0, 1.0))
			if _t >= SALE:
				_etapa = 1
				_t = 0.0
		1:
			_punta = _objetivo
			if _t >= QUIETA:
				_etapa = 2
				_t = 0.0
		2:
			var dura := VUELVE * (0.5 if _repelida else 1.0)
			_punta = _objetivo.lerp(REPOSO[_brazo] if not _repelida else Vector2(0, -46), clampf(_t / dura, 0.0, 1.0))
			if _t >= dura:
				if _repelida:
					_abollar()
				elif furia() and not _segunda:
					_segunda = true
					_apuntar(maisha.global_position + Vector2(0, -8) - global_position)
				else:
					_cd = 0.8 if furia() else 1.3
					_cambiar(Fase.GUARDIA)
				return
	if _etapa < 2 and not _toco and maisha.global_position.distance_to(punta() + Vector2(0, 8)) < AGARRA:
		_toco = true
		maisha.call("recibir_danio", 1, punta(), "contacto")


func _caer_bloque(maisha: Node2D) -> void:
	if _devuelto:
		_abollar()
		return
	Sonido.efecto("roca_romper", -2.0, _cae)
	Impacto.temblar(3.0, 0.2)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 8
	astillas.position = _cae
	get_parent().add_child(astillas)
	if maisha.global_position.distance_to(_cae) < 15.0:
		maisha.call("recibir_danio", 1, _cae, "roca")
	_cd = 0.9 if furia() else 1.4
	_cambiar(Fase.GUARDIA)


## Le dan con lo suyo: una abolladura en el peto; con REPELES, se abre
func _abollar() -> void:
	abolladuras += 1
	Impacto.temblar(4.0, 0.3)
	Impacto.chispa(global_position + Vector2(0, -46), Vector2.UP, Color("ffc850"))
	Sonido.efecto("cosechadora_choque", 0.0, global_position)
	if abolladuras >= REPELES:
		abrir()
	else:
		_cd = 1.0
		_cambiar(Fase.GUARDIA)


func abrir() -> void:
	if fase == Fase.VENCIDO or fase == Fase.DORMIDO:
		return
	_golpes = 0
	_cambiar(Fase.ABIERTO)
	Impacto.fogonazo(Color(1.0, 0.8, 0.4), 0.3, 0.3)
	Sonido.efecto("kaa_vuelca", 2.0, global_position)
	Sonido.efecto("geoda_encender", 0.0, global_position)


func _dibujar() -> void:
	_sprite.position = Vector2.ZERO
	match fase:
		Fase.VENCIDO:
			_sprite.frame = 4
		Fase.ABIERTO:
			_sprite.frame = 3 if _destello > 0.0 else 2
		_:
			_sprite.frame = 1 if abolladuras > 0 else 0
			if fase == Fase.AVISA:
				_sprite.position.x = roundf(sin(_tiempo * 50.0) * 0.6)


## Los cuatro brazos: dos tramos articulados (un codo que cuelga) y la tenaza en la punta
func _dibujar_brazos() -> void:
	for i in HOMBROS.size():
		var fin: Vector2 = REPOSO[i]
		var caliente := 0.0
		if fase == Fase.VENCIDO or fase == Fase.ABIERTO:
			fin = HOMBROS[i] + Vector2(signf(HOMBROS[i].x) * 14.0, 30.0)          # caídos
		elif i == _brazo and fase in [Fase.AVISA, Fase.TENAZA]:
			fin = _punta
			caliente = clampf(_t / AVISO, 0.3, 1.0) if fase == Fase.AVISA else 1.0
		elif fase == Fase.BLOQUE and i == 0:
			fin = HOMBROS[i] + Vector2(-20, -44)                                  # el brazo que lanza, en alto
		else:
			fin += Vector2(0, sin(_tiempo * 1.6 + i * 1.3) * 2.0)                 # respiran
		var codo: Vector2 = (HOMBROS[i] + fin) / 2.0 + Vector2(signf(HOMBROS[i].x) * 6.0, 9.0) * (1.0 - clampf((fin - HOMBROS[i]).length() / ALCANCE, 0.0, 1.0))
		for tramo: Array in [[HOMBROS[i], codo], [codo, fin]]:
			_brazos.draw_line(tramo[0], tramo[1], HIERRO[0], 5.0)
			_brazos.draw_line(tramo[0] + Vector2(0, -1), tramo[1] + Vector2(0, -1), HIERRO[1].lerp(ROJO[1], caliente * 0.6), 3.0)
		_brazos.draw_circle(codo, 3.0, HIERRO[0])
		_brazos.draw_circle(codo, 2.0, HIERRO[2])
		var ang := (fin - codo).angle()
		_brazos.draw_set_transform(fin, ang, Vector2.ONE)
		_brazos.draw_texture(TENAZA, Vector2(-6, -10), Color(1, 1, 1) if caliente > 0.0 else Color(0.62, 0.5, 0.5))
		_brazos.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


## En el suelo: la línea del tenazazo que viene y la sombra del bloque que cae (y el bloque, por el aire)
func _dibujar_suelo() -> void:
	if fase == Fase.AVISA:
		var a := clampf(_t / (AVISO_FURIA if furia() else AVISO), 0.0, 1.0)
		var desde := global_position + HOMBROS[_brazo] + Vector2(0, 8)
		var fin := global_position + _objetivo + Vector2(0, 8)
		_suelo.draw_line(desde, fin, Color(1.0, 0.5, 0.12, 0.12 + 0.3 * a), 9.0)
		_suelo.draw_arc(fin, 11.0, 0, TAU, 20, Color(1.0, 0.5, 0.12, 0.3 + 0.5 * a), 1.5)
	elif fase == Fase.BLOQUE:
		var f := clampf(_t / BLOQUE_CAE, 0.0, 1.0)
		_suelo.draw_circle(_cae, 5.0 + 10.0 * f, Color(0.05, 0.03, 0.02, 0.25 + 0.35 * f))
		_suelo.draw_arc(_cae, 15.0, 0, TAU, 20, Color(1.0, 0.4, 0.2, 0.6 * f), 1.0)
		if _t > 0.45:
			# el bloque, por el aire: sube desde Nyundo y cae en la sombra (o vuelve, si se lo devuelven)
			var g := clampf((_t - 0.45) / (BLOQUE_CAE - 0.45), 0.0, 1.0)
			var desde := global_position + Vector2(-50, -110)
			var hasta := (global_position + Vector2(0, -46)) if _devuelto else _cae
			var p := (_cae if _devuelto else desde).lerp(hasta, g) + Vector2(0, -sin(g * PI) * (20.0 if _devuelto else 60.0))
			_suelo.draw_texture_rect_region(BLOQUE, Rect2(p - Vector2(12, 24), Vector2(24, 28)), Rect2(24 if _devuelto else 0, 0, 24, 28))


# --- El Pulso y el daño ---------------------------------------------------------------

## El Pulso Magnético: repele la tenaza que viene (o que acaba de llegar) y el bloque que cae
func recibir_pulso(origen: Vector2) -> bool:
	if fase == Fase.TENAZA and _etapa < 2 and not _repelida and punta().distance_to(origen + Vector2(0, -8)) < REPELE_A:
		_repelida = true
		_etapa = 2
		_t = 0.0
		_objetivo = _punta
		Sonido.efecto("clinc", 2.0, punta())
		Impacto.chispa(punta(), (punta() - origen).normalized(), Color("6ad0f0"))
		return true
	if fase == Fase.BLOQUE and not _devuelto and _t > 0.45 and _cae.distance_to(origen) < REPELE_A:
		_devuelto = true
		_t = 0.45 + (BLOQUE_CAE - 0.45) * 0.4
		Sonido.efecto("clinc", 2.0, _cae)
		return true
	return false


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase != Fase.ABIERTO:
		if fase != Fase.VENCIDO and fase != Fase.DORMIDO:
			Sonido.efecto("clinc", -2.0, global_position, 0.2)
			Impacto.chispa(global_position + Vector2(0, -30), Vector2.UP, Color("d0a450"))
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if fase != Fase.ABIERTO or _destello > 0.06:
		return
	vida = maxi(0, vida - (2 if tipo == "explosion" else cantidad))
	_golpes += 1
	_destello = 0.12
	vida_cambiada.emit(vida)
	Impacto.chispa(global_position + Vector2(0, -46), Vector2.UP, Color("ffd878"))
	Sonido.efecto("roca_romper", -8.0, global_position, 0.3)
	if vida <= 0:
		morir()


func morir() -> void:
	if fase == Fase.VENCIDO:
		return
	_cambiar(Fase.VENCIDO)
	for g in ["enemigos", "magneticos", "nyundos"]:
		remove_from_group(g)
	for hijo in get_children():
		hijo.remove_from_group("golpeables")
		hijo.remove_from_group("daniables")
	Estado.marcar("nyundo_vencido")
	Estado.marcar("cadena_este_rota")
	Bestiario.vencido("nyundo", self)
	Sonido.efecto("puerta_crater", 0.0, global_position)
	Sonido.musica("victoria")
	Impacto.temblar(6.0, 0.8)
	if _barra:
		_barra.queue_free()
		_barra = null
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 20
	astillas.position = global_position + Vector2(0, -40)
	get_parent().add_child(astillas)
	var esquirla: Node2D = RECOGIBLE.new()
	esquirla.objeto = "esquirla_estrella"
	esquirla.marca = "esquirla/nyundo"
	esquirla.dibujo = "res://arte/mundos/asterhaul/desfiladero/esquirla.png"
	esquirla.color_halo = Color(1.0, 0.75, 0.3)
	esquirla.position = global_position + Vector2(0, 34)
	get_parent().add_child(esquirla)
	destruido.emit()
