extends CharacterBody2D
## EL BIBLIOTECARIO HUECO (Las Estanterías Colgantes, Sigilia): el jefe de la gran biblioteca de cuatro pisos.
## La toga morada encantada del viejo armiño Mwalimu, que flota sin nadie dentro.
##
## Mecánica del combate (Opción A: El abrigo vacío):
##   1. ESCUDO DE LIBROS: Flota por la sala rodeado de 3 libros encantados que absorben cualquier golpe.
##      El jugador debe quemarlos con el Sigilo de Fuego (U) o destruirlos con el cetro/semillas.
##   2. ATAQUES: El Bibliotecario alza su puntero de oro y dispara proyectiles de tinta, o lanza uno de sus
##      libros orbitantes directamente contra Maisha.
##   3. ATURDIDO: Al perder los 3 libros del escudo, la toga pierde su flotabilidad y cae al suelo aturdida.
##      ¡Es el momento de golpearle con el cetro (1) o semillas (2)!
##   4. SEGUNDA FASE (< 6 vida): Se desplaza más rápido, lanza andanadas de tinta y deja caer tomos del techo.
##   5. DERROTA: La toga se desploma suavemente en el suelo y libera la FICHA DE MWALIMU, el Maestro de la Memoria.

signal destruido
signal vida_cambiada(nueva_vida: int)

enum Fase { DORMIDO, PRESENTACION, FLOTANDO_ESCUDO, DISPARANDO, ATURDIDO, VENCIDO }

const R := preload("res://scripts/combate/reglas_combate.gd")
const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const DIBUJO := preload("res://arte/mundos/sigilia/estanterias/bibliotecario.png")
const LIBRO_ESCUDO := preload("res://scripts/enemigos/libro_escudo.gd")
const PROYECTIL_TINTA := preload("res://scripts/enemigos/proyectil_tinta.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")

const NOMBRE := "El Bibliotecario Hueco"
const VIDA_MAX := 12

var zona: Node2D = null
var vida := VIDA_MAX
var fase := Fase.DORMIDO

var _t := 0.0
var _tiempo := 0.0
var _destello := 0.0
var _cd_ataque := 2.5
var _cd_invocar := 8.0
var _cd_lanzar_libro := 4.5
var _danio_en_aturdido := 0
var _rumbo := Vector2.ZERO
var _centro_sala := Vector2.ZERO

var _libros: Array[Node2D] = []
var _sprite: Sprite2D
var _sombra: Node2D
var _barra: CanvasLayer = null
var _luz: PointLight2D = null


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	collision_layer = 2
	collision_mask = 1
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING

	var col := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(24, 38)
	col.shape = caja
	col.position = Vector2(0, -20)
	add_child(col)

	_sombra = Node2D.new()
	_sombra.set_script(SOMBRA)
	_sombra.set("ancho", 26.0)
	add_child(_sombra)

	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 7
	_sprite.offset = Vector2(0, -38)
	add_child(_sprite)

	_centro_sala = global_position


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	vida = VIDA_MAX
	_danio_en_aturdido = 0
	_centro_sala = global_position
	_cambiar(Fase.PRESENTACION)

	Sonido.musica("jefe_bibliotecario")
	Impacto.temblar(2.5, 0.5)

	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)

	_invocar_escudo()


func reiniciar() -> void:
	vida = VIDA_MAX
	_limpiar_libros()
	if _barra:
		_barra.queue_free()
		_barra = null
	_cambiar(Fase.DORMIDO)
	global_position = _centro_sala


func _cambiar(nueva: Fase) -> void:
	fase = nueva
	_t = 0.0
	if nueva == Fase.ATURDIDO:
		add_to_group("golpeables")
		add_to_group("daniables")
	else:
		remove_from_group("golpeables")
		remove_from_group("daniables")


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)

	var maisha := _maisha()

	match fase:
		Fase.PRESENTACION:
			if _t > 1.8:
				_cambiar(Fase.FLOTANDO_ESCUDO)

		Fase.FLOTANDO_ESCUDO:
			_proceso_flotando(delta, maisha)

		Fase.DISPARANDO:
			if _t > 0.8:
				_cambiar(Fase.FLOTANDO_ESCUDO)

		Fase.ATURDIDO:
			_proceso_aturdido(delta)

		Fase.VENCIDO:
			pass

	_actualizar_sprite()


func _proceso_flotando(delta: float, maisha: Node2D) -> void:
	# Movimiento suave de levitación por la sala
	if maisha:
		var hacia_maisha := (maisha.global_position - global_position).normalized()
		var distancia := global_position.distance_to(maisha.global_position)
		if distancia < 70.0:
			_rumbo = -hacia_maisha * R.BIBLIOTECARIO_VELOCIDAD
		elif distancia > 140.0:
			_rumbo = hacia_maisha * R.BIBLIOTECARIO_VELOCIDAD
		else:
			_rumbo = Vector2(-hacia_maisha.y, hacia_maisha.x) * R.BIBLIOTECARIO_VELOCIDAD * 0.8
	velocity = velocity.move_toward(_rumbo, delta * 80.0)
	move_and_slide()

	# Ataque 1: Disparo de tinta con el puntero
	_cd_ataque -= delta
	if _cd_ataque <= 0.0:
		_cd_ataque = R.BIBLIOTECARIO_DISPARO_CADA * (0.75 if vida <= 6 else 1.0)
		_disparar_tinta(maisha)

	# Ataque 2: Lanzar un libro del escudo
	if _libros.size() > 1:
		_cd_lanzar_libro -= delta
		if _cd_lanzar_libro <= 0.0:
			_cd_lanzar_libro = 5.0
			_lanzar_libro_escudo(maisha)


func _disparar_tinta(maisha: Node2D) -> void:
	if not maisha:
		return
	_cambiar(Fase.DISPARANDO)
	Sonido.efecto("cetro_golpe", -3.0, global_position)
	var dir := (maisha.global_position + Vector2(0, -6) - (global_position + Vector2(0, -32))).normalized()
	var p: Area2D = PROYECTIL_TINTA.new()
	p.direccion = dir
	p.global_position = global_position + Vector2(dir.x * 16.0, -32)
	get_parent().add_child(p)


func _lanzar_libro_escudo(maisha: Node2D) -> void:
	if not maisha or _libros.is_empty():
		return
	var libro: Node2D = _libros.pop_back()
	if is_instance_valid(libro):
		libro.call("lanzar", (maisha.global_position - libro.global_position))


func _proceso_aturdido(delta: float) -> void:
	velocity = Vector2.ZERO
	if _t >= R.BIBLIOTECARIO_ATURDIDO or _danio_en_aturdido >= 4:
		# Se recupera, emite onda de choque y vuelve a invocar su escudo
		_recuperar_escudo()


func _recuperar_escudo() -> void:
	_danio_en_aturdido = 0
	Impacto.temblar(1.8, 0.4)
	Sonido.efecto("bundi_conjura", -2.0, global_position)
	Impacto.chispa(global_position + Vector2(0, -20), Vector2.UP, Color("c084fc"))
	_invocar_escudo()
	_cambiar(Fase.FLOTANDO_ESCUDO)


func _invocar_escudo() -> void:
	_limpiar_libros()
	for i in range(R.BIBLIOTECARIO_LIBROS):
		var l: CharacterBody2D = LIBRO_ESCUDO.new()
		l.bibliotecario = self
		l.angulo = (float(i) / R.BIBLIOTECARIO_LIBROS) * TAU
		get_parent().add_child(l)
		_libros.append(l)
	Sonido.efecto("cristal", -2.0, global_position)


func _limpiar_libros() -> void:
	for l in _libros:
		if is_instance_valid(l):
			l.queue_free()
	_libros.clear()


func libro_destruido(libro: Node2D) -> void:
	_libros.erase(libro)
	if _libros.is_empty() and fase == Fase.FLOTANDO_ESCUDO:
		# ¡Todos los libros destruidos! El jefe cae aturdido
		_cambiar(Fase.ATURDIDO)
		Sonido.efecto("cangrejo_vuelca", -2.0, global_position)
		Impacto.temblar(2.0, 0.3)


# --- Combate y Daño -----------------------------------------------------------

func recibir_golpe(danio_golpe: int, _direccion: Vector2) -> bool:
	if fase == Fase.FLOTANDO_ESCUDO:
		# Escudo activo: el cetro rebota con chispas de papel
		Sonido.efecto("golpe_acierto", -2.0, global_position)
		Impacto.chispa(global_position + Vector2(0, -20), Vector2.UP, Color("fef08a"))
		return false
	if fase == Fase.ATURDIDO:
		recibir_danio(danio_golpe, global_position, "golpe")
		return true
	return false


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if fase != Fase.ATURDIDO or fase == Fase.VENCIDO:
		return
	var danio_real: int = maxi(cantidad, 2) if (tipo == "explosion" or tipo == "fuego") else cantidad
	vida = maxi(0, vida - danio_real)
	_danio_en_aturdido += danio_real
	_destello = 0.18
	vida_cambiada.emit(vida)

	Impacto.chispa(global_position + Vector2(0, -20), Vector2.UP, Color("c084fc"))
	Sonido.efecto("kambare_dolor", -2.0, global_position)

	if vida <= 0:
		morir()


func morir() -> void:
	if fase == Fase.VENCIDO:
		return
	_cambiar(Fase.VENCIDO)
	_limpiar_libros()
	remove_from_group("enemigos")
	remove_from_group("golpeables")
	remove_from_group("daniables")

	Estado.marcar("bibliotecario_vencido")
	Bestiario.vencido("bibliotecario", self)
	Sonido.musica("victoria")
	Impacto.temblar(3.0, 0.8)

	if _barra:
		_barra.queue_free()
		_barra = null

	# Aparece la Ficha del Índice de Mwalimu
	var ficha: Node2D = RECOGIBLE.new()
	ficha.objeto = "ficha_mwalimu"
	ficha.marca = "ficha/mwalimu"
	ficha.dibujo = "res://arte/mundos/sigilia/paso/ficha.png"
	ficha.color_halo = Color(0.95, 0.8, 0.4)
	if get_parent():
		get_parent().add_child(ficha)
	else:
		add_child(ficha)

	destruido.emit()


func _actualizar_sprite() -> void:
	if _destello > 0.0:
		_sprite.frame = 5
	elif fase == Fase.VENCIDO:
		_sprite.frame = 6
	elif fase == Fase.ATURDIDO:
		_sprite.frame = 4
	elif fase == Fase.DISPARANDO:
		_sprite.frame = 3 if _t > 0.2 else 2
	else:
		_sprite.frame = int(_tiempo * 3.0) % 2


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D
