extends CharacterBody2D
## MAISHA: movimiento libre, animaciones y combate.
##   Golpe con el cetro (gratis, recarga un poco de Aliento)
##   Semilla (gasta Aliento; cae en la casilla de sus pies y estalla en cruz)
##   Latido (gasta Aliento; empuja lo que está cerca y da un instante de invulnerabilidad)
## Todos los números están en scripts/combate/reglas_combate.gd

signal herida(vida: int)
signal caida

const R := preload("res://scripts/combate/reglas_combate.gd")
const VELOCIDAD := 70.0        # píxeles por segundo
const CORRER := 1.65           # al correr (C o LB), va así de rápido
const ZONA_MUERTA := 0.2       # ignora toques mínimos del stick del mando
const MARGEN_GIRO := 0.15      # en diagonal, evita que el dibujo cambie de dirección sin parar
const ESCENA_SEMILLA := preload("res://scripts/combate/semilla.gd")
const ESCENA_GOLPE := preload("res://scripts/combate/golpe_efecto.gd")
const ESCENA_LATIDO := preload("res://scripts/combate/latido_efecto.gd")
const RASGOS := preload("res://scripts/personajes/rasgos_maisha.gd")

## Hacia dónde mira: "abajo", "arriba" o "lado"
var mirando := "abajo"
var vida: int = R.VIDA_MAXIMA
var aliento: float = R.ALIENTO_MAXIMO
var agotada := false
var esta_caida := false
var puede_actuar := true
var combate_activo := true     # en la aldea y en las casas no se lucha
var lentitud := 1.0            # menos de 1: anda más despacio (al despertar, entumecida)
var corriendo := false
var pegajoso := 0.0            # segundos que le queda pisando óxido de babosa (anda más despacio)

var _invulnerable := 0.0
var _espera_golpe := 0.0
var _espera_latido := 0.0
var _golpeando := false
var _tiempo_agotada := 0.0
var _desde_ultima_semilla := 99.0
var _empuje := Vector2.ZERO
var _ultimo_danio := -100000.0
var _emocion := 0.0           # mientras dure, se ve una expresión (sorpresa, daño, celebrar...) y no se pisa

@onready var _sprite: AnimatedSprite2D = $Sprite
@onready var _ropa: Node = $Ropa


func _ready() -> void:
	vida = vida_maxima()
	aliento = aliento_maximo()
	Artes.arte_subida.connect(func(_id: String, _n: int) -> void:
		vida = vida_maxima()
		aliento = aliento_maximo())
	add_to_group("maisha")
	add_to_group("daniables")
	var rasgos: Node2D = RASGOS.new()
	rasgos.name = "Rasgos"
	add_child(rasgos)
	_sprite.play("reposo_abajo")
	_sprite.animation_finished.connect(_al_terminar_animacion)


func _physics_process(delta: float) -> void:
	_espera_golpe = maxf(0.0, _espera_golpe - delta)
	_espera_latido = maxf(0.0, _espera_latido - delta)
	_invulnerable = maxf(0.0, _invulnerable - delta)
	pegajoso = maxf(0.0, pegajoso - delta)
	_desde_ultima_semilla += delta
	if _emocion > 0.0:
		_emocion -= delta
		if _emocion <= 0.0:
			_fin_emocion()

	if esta_caida or not puede_actuar:
		velocity = Vector2.ZERO
		modulate.a = 1.0
		return

	var direccion := Input.get_vector("mover_izquierda", "mover_derecha", "mover_arriba", "mover_abajo")
	if direccion.length() < ZONA_MUERTA:
		direccion = Vector2.ZERO

	_actualizar_aliento(delta, direccion)

	var rapidez := VELOCIDAD * lentitud
	corriendo = Input.is_action_pressed("correr") and direccion != Vector2.ZERO and not agotada and lentitud > 0.95
	if corriendo:
		rapidez *= CORRER
	if agotada:
		rapidez *= R.VELOCIDAD_AGOTADA
	if _golpeando:
		rapidez *= R.GOLPE_FRENA
	if pegajoso > 0.0:
		rapidez *= 0.55
	velocity = direccion * rapidez + _empuje
	_empuje = _empuje.move_toward(Vector2.ZERO, 600.0 * delta)
	move_and_slide()

	if combate_activo:
		if Input.is_action_just_pressed("golpe"):
			golpear()
		if Input.is_action_just_pressed("explosivo"):
			lanzar_semilla()
		if Input.is_action_just_pressed("latido"):
			latido()

	if Input.is_action_just_pressed("usar"):
		tomar_sopa()

	if direccion != Vector2.ZERO and _emocion > 0.0:
		_emocion = 0.0                 # si se mueve, la expresión se corta
	if not _golpeando and _emocion <= 0.0:
		_actualizar_animacion(direccion)
	# parpadeo mientras es invulnerable tras un daño
	var parpadea := _invulnerable > 0.0 and segundos_desde_danio() < R.INVULNERABLE_TRAS_DANIO
	modulate.a = 0.35 if parpadea and fmod(_invulnerable, 0.16) < 0.08 else 1.0


# --- Acciones de combate ---------------------------------------------------------

func golpear() -> void:
	if _golpeando or _espera_golpe > 0.0:
		return
	_golpeando = true
	_espera_golpe = R.GOLPE_ESPERA
	Sonido.efecto("cetro_golpe")
	_sprite.play("golpe_" + mirando)
	if _ropa.lleva("cetro_raiz"):
		_ropa.ocultar_zona("arma", true)
	var efecto: Node2D = ESCENA_GOLPE.new()
	efecto.direccion = direccion_mirada()
	efecto.con_cetro = _ropa.lleva("cetro_raiz")
	add_child(efecto)
	if mirando == "arriba":
		move_child(efecto, _sprite.get_index())   # de espaldas, el cetro pasa por detrás
	# el golpe acierta en el segundo fotograma
	get_tree().create_timer(0.07).timeout.connect(_comprobar_golpe)


func _comprobar_golpe() -> void:
	var centro := global_position + Vector2(0, -8)
	var mira := direccion_mirada()
	var aciertos := 0
	var alcance := R.GOLPE_ALCANCE * (R.CETRO_TEMPLADO_ALCANCE if Estado.tiene("cetro_templado") else 1.0)
	for nodo in get_tree().get_nodes_in_group("golpeables"):
		var objetivo := nodo as Node2D
		if objetivo == null or not is_instance_valid(objetivo):
			continue
		var hacia := (objetivo.global_position + Vector2(0, -5)) - centro
		if hacia.length() > alcance:
			continue
		if hacia.length() > 4.0 and rad_to_deg(abs(mira.angle_to(hacia))) > R.GOLPE_ANGULO:
			continue
		if objetivo.call("recibir_golpe", R.GOLPE_DANIO, mira):
			aciertos += 1
			Impacto.chispa(objetivo.global_position + Vector2(0, -6) - mira * 4.0, mira)
		else:
			Impacto.chispa(objetivo.global_position + Vector2(0, -10) - mira * 6.0, -mira, Color("a3a4a6"))   # rebota (clinc)
	if aciertos > 0:
		Impacto.pausa(0.045)
		Impacto.temblar(1.5, 0.12)
		Sonido.efecto("golpe_acierto")
		aliento = minf(aliento_maximo(), aliento + Artes.golpe_recarga() * aciertos)


func lanzar_semilla() -> bool:
	if agotada or aliento < Artes.semilla_coste():
		return false
	var casilla := R.casilla_de(global_position)
	for s in get_tree().get_nodes_in_group("semillas"):
		if s.casilla == casilla:
			return false
	var semilla: Node2D = ESCENA_SEMILLA.new()
	semilla.casilla = casilla
	get_parent().add_child(semilla)
	aliento -= Artes.semilla_coste()
	_desde_ultima_semilla = 0.0
	Sonido.efecto("semilla_plantar")
	if aliento < 1.0:
		_agotarse()
	return true


func latido() -> bool:
	if _espera_latido > 0.0 or agotada or aliento < Artes.latido_coste():
		return false
	aliento -= Artes.latido_coste()
	_espera_latido = R.LATIDO_ESPERA
	Sonido.efecto("latido")
	_invulnerable = maxf(_invulnerable, R.LATIDO_INVULNERABLE)
	var centro := global_position + Vector2(0, -8)
	for nodo in get_tree().get_nodes_in_group("golpeables"):
		var objetivo := nodo as Node2D
		if objetivo and objetivo.has_method("empujar"):
			var hacia := objetivo.global_position - global_position
			if hacia.length() <= Artes.latido_radio():
				objetivo.call("empujar", hacia.normalized() * R.LATIDO_EMPUJE)
	# las ondas de los murciélagos de eco se deshacen
	for onda in get_tree().get_nodes_in_group("ondas"):
		if (onda as Node2D).global_position.distance_to(global_position) <= Artes.latido_radio() + 8.0:
			onda.call("disipar")
	for s in get_tree().get_nodes_in_group("semillas"):
		var hacia: Vector2 = s.global_position - global_position
		if hacia.length() <= Artes.latido_radio() and hacia.length() > 1.0:
			s.call("desplazar", _direccion_cardinal(hacia))
	var efecto: Node2D = ESCENA_LATIDO.new()
	efecto.position = Vector2(0, -12)
	add_child(efecto)
	if aliento < 1.0:
		_agotarse()
	return true


# --- Daño, caída y vuelta ----------------------------------------------------------

## Devuelve true si el daño se aplicó (false si era invulnerable o ya había caído)
func recibir_danio(cantidad: int, desde: Vector2, tipo: String) -> bool:
	if esta_caida or _invulnerable > 0.0:
		return false
	if tipo == "explosion":
		cantidad = R.EXPLOSION_AUTODANIO
	vida = maxi(0, vida - cantidad)
	_invulnerable = R.INVULNERABLE_TRAS_DANIO
	_ultimo_danio = Time.get_ticks_msec()
	var lejos := global_position - desde
	if lejos.length() > 0.1:
		_empuje = lejos.normalized() * 140.0
	herida.emit(vida)
	Sonido.efecto("maisha_cae" if vida <= 0 else "maisha_herida")
	Impacto.pausa(0.07)
	Impacto.temblar(3.0, 0.22)
	Impacto.fogonazo(Color("b03a44"), 0.15, 0.3)
	if vida > 0 and not _golpeando:
		expresar("danio", 0.4)
	if vida <= 0:
		esta_caida = true
		_sprite.play("reposo_" + mirando)
		caida.emit()
	return true


func es_invulnerable() -> bool:
	return _invulnerable > 0.0


func revivir(posicion: Vector2) -> void:
	global_position = posicion
	vida = vida_maxima()
	aliento = aliento_maximo()
	agotada = false
	esta_caida = false
	_empuje = Vector2.ZERO
	_invulnerable = 1.0


## Se toma una sopa de Juncia (tecla F o desde la mochila): devuelve hojas de vida.
## Devuelve false si no hay sopa o ya tiene toda la vida.
func tomar_sopa() -> bool:
	var hud := get_tree().get_first_node_in_group("hud")
	if esta_caida:
		return false
	if Estado.cuantos("sopa") <= 0:
		if hud and Estado.tiene("receta_sopa"):
			hud.mostrar_mensaje("No te queda sopa. Juncia cocina más con bayas y junco.")
		return false
	if vida >= vida_maxima():
		if hud:
			hud.mostrar_mensaje("Ya tienes todas las hojas.")
		return false
	Estado.quitar("sopa")
	vida = mini(vida_maxima(), vida + Estado.SOPA_CURA)
	herida.emit(vida)
	Sonido.efecto("sorber")
	Impacto.fogonazo(Color("8fd06a"), 0.12, 0.25)
	if not _golpeando:
		expresar("celebrar", 0.5)
	if hud:
		hud.mostrar_mensaje("¡Sopa de Juncia! +%d hojas" % Estado.SOPA_CURA)
	return true


## Pisa óxido de babosa: anda más despacio un rato
func pisar_oxido(segundos := 0.4) -> void:
	pegajoso = maxf(pegajoso, segundos)


## Con las Artes del Árbol de la Vida aplicadas
func vida_maxima() -> int:
	return Artes.vida_maxima()


func aliento_maximo() -> float:
	return Artes.aliento_maximo()


func segundos_desde_danio() -> float:
	return (Time.get_ticks_msec() - _ultimo_danio) / 1000.0


# --- Aliento --------------------------------------------------------------------

func _actualizar_aliento(delta: float, direccion: Vector2) -> void:
	if agotada:
		_tiempo_agotada -= delta
		if _tiempo_agotada <= 0.0:
			agotada = false
	var ritmo := R.ALIENTO_RECUPERA
	if _desde_ultima_semilla > R.SEGUNDOS_SIN_LANZAR:
		ritmo = R.ALIENTO_RECUPERA_QUIETA if direccion == Vector2.ZERO else R.ALIENTO_RECUPERA_SIN_LANZAR
	aliento = minf(aliento_maximo(), aliento + ritmo * Artes.ritmo_aliento() * delta)


func _agotarse() -> void:
	aliento = 0.0
	agotada = true
	_tiempo_agotada = R.DURACION_AGOTAMIENTO


# --- Animación ------------------------------------------------------------------

## Gira a Maisha hacia una dirección (al llegar por una puerta, por ejemplo)
func mirar(direccion: Vector2) -> void:
	if absf(direccion.x) > absf(direccion.y):
		mirando = "lado"
		_sprite.flip_h = direccion.x < 0.0
	else:
		mirando = "arriba" if direccion.y < 0.0 else "abajo"
		_sprite.flip_h = false
	_reproducir("reposo_" + mirando)


func direccion_mirada() -> Vector2:
	match mirando:
		"arriba":
			return Vector2.UP
		"abajo":
			return Vector2.DOWN
	return Vector2.LEFT if _sprite.flip_h else Vector2.RIGHT


func _direccion_cardinal(v: Vector2) -> Vector2i:
	if abs(v.x) > abs(v.y):
		return Vector2i(int(sign(v.x)), 0)
	return Vector2i(0, int(sign(v.y)))


## Una expresión: "sorpresa", "celebrar", "despertar" (de frente) o "danio" (hacia donde mira).
## segundos = cuánto dura (0 = lo que dure la animación).
func expresar(nombre: String, segundos := 0.0) -> void:
	var anim := nombre + "_" + mirando
	if not _sprite.sprite_frames.has_animation(anim):
		anim = nombre + "_abajo"
		mirando = "abajo"
		_sprite.flip_h = false
	if not _sprite.sprite_frames.has_animation(anim):
		return
	# si corta un golpe a medias, el golpe se da por acabado (celebrar se repite en bucle y nunca avisaría
	# de que el golpe terminó: Maisha se quedaba celebrando para siempre)
	if _golpeando:
		_golpeando = false
		_ropa.ocultar_zona("arma", false)
	_sprite.play(anim)
	if segundos <= 0.0:
		var marcos := _sprite.sprite_frames
		var total := 0.0
		for i in marcos.get_frame_count(anim):
			total += marcos.get_frame_duration(anim, i)
		segundos = total / marcos.get_animation_speed(anim) + 0.15
	_emocion = segundos


func celebrar() -> void:
	expresar("celebrar", 1.6)


func _fin_emocion() -> void:
	_emocion = 0.0
	_reproducir("reposo_" + mirando)


func _al_terminar_animacion() -> void:
	if _golpeando:
		_golpeando = false
		_ropa.ocultar_zona("arma", false)


func _actualizar_animacion(direccion: Vector2) -> void:
	if direccion == Vector2.ZERO:
		_reproducir("reposo_" + mirando)
		return

	var ax: float = abs(direccion.x)
	var ay: float = abs(direccion.y)
	# Solo cambia de dirección si la nueva domina con claridad (o si la actual ya no sirve)
	if mirando == "lado":
		if ay > ax + MARGEN_GIRO or ax < 0.01:
			mirando = "arriba" if direccion.y < 0.0 else "abajo"
	else:
		if ax > ay + MARGEN_GIRO or ay < 0.01:
			mirando = "lado"
		else:
			mirando = "arriba" if direccion.y < 0.0 else "abajo"

	if mirando == "lado" and ax > 0.01:
		_sprite.flip_h = direccion.x < 0.0
	elif mirando != "lado":
		_sprite.flip_h = false
	_reproducir(("correr_" if corriendo else "andar_") + mirando)


func _reproducir(animacion: String) -> void:
	if _sprite.animation != animacion:
		_sprite.play(animacion)
