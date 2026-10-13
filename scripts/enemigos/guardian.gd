extends Node2D
## EL GUARDIÁN DE LA GRUTA: el jefe del fondo de la Gruta de las Raíces. Un ciervo enorme y viejo, mitad animal y mitad
## raíz, que duerme abrazado a las raíces del Primer Árbol. Giza le ha puesto una MÁSCARA (su pesadilla) que lo mueve
## dormido como a una marioneta: unos hilos violetas bajan del techo hasta su cuerpo. Se pelea contra la máscara.
##   - EMBESTIDA: escarba el suelo (aviso: una raya marca hacia dónde) y carga en línea recta. Si Maisha la esquiva,
##     choca contra la pared y queda ATURDIDO, con la máscara torcida: el cetro le quita 1; una semilla, 2.
##   - OLA DE RAÍCES: se alza de manos y pisa fuerte; una ola de raíces-látigo avanza por el suelo hacia Maisha.
##     Hace daño... salvo que Maisha la reciba de frente con el ESCUDO de corteza.
##   - Fase 2 (dos tercios de vida): al aturdirse, la pesadilla llama a dos Petrinos.
##   - Fase 3 (un tercio): más deprisa, y a veces dos embestidas seguidas; los hilos tiran más.
## Al vencerlo, la máscara se agrieta y estalla: el Guardián despierta (limpio, ojos dorados, flores en la cornamenta),
## se queda en la sala y habla (marca «gruta_guardian»; la maraña del atajo se aparta).
## Hace de «Corazón» de su zona (zona_corrupta.gd con jefe = "guardian").

signal destruido
signal vida_cambiada(vida: int)

enum Fase { DORMIDO, PRESENTACION, ESPERA, ESCARBA, EMBISTE, ATURDIDO, PISA, VENCIDO }

const R := preload("res://scripts/combate/reglas_combate.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const OSCURIDAD := preload("res://scripts/mundo/gruta/oscuridad.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const NOMBRE := "El Guardián de la Gruta"
const QUIETO := 0
const ESCARBA_F := 1
const EMBISTE_F := 2
const ATURDIDO_F := 3
const PISA_F := 4
const LIBRE := 5
const VELOCIDAD_EMBESTIDA := 250.0
const OLA_VELOCIDAD := 150.0

var zona: Node2D
var variante := "raiz"
var vida: int = R.GUARDIAN_VIDA
var fase: int = Fase.DORMIDO

var _t := 0.0
var _tiempo := 0.0
var _mira := 1.0
var _blanco := 0.0
var _espera := 1.5
var _hacia := Vector2.RIGHT
var _seguidas := 0
var _pillo := false
var _ola := -1.0                         # lo que ha avanzado la ola de raíces (-1: no hay)
var _ola_desde := Vector2.ZERO
var _ola_hacia := Vector2.RIGHT
var _ola_pillo := false
var _grietas := 0                        # cuánto se ha agrietado la máscara (se dibuja)
var _sprite: Sprite2D
var _sombra: Node2D
var _capa: Node2D
var _barra: CanvasLayer
var _luz: PointLight2D


func _ready() -> void:
	add_to_group("jefes")
	_capa = Node2D.new()
	_capa.top_level = true
	_capa.z_index = -1
	_capa.draw.connect(_dibujar_capa)
	add_child(_capa)
	_sombra = Node2D.new()
	_sombra.set_script(SOMBRA)
	_sombra.set("ancho", 40.0)
	add_child(_sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/zonas/%s/guardian.png" % variante)
	_sprite.hframes = 6
	_sprite.offset = Vector2(-2, -46)
	add_child(_sprite)
	# su propia luz: violeta mientras lo mueve la pesadilla, dorada cuando despierta (en la Gruta todo está oscuro)
	_luz = PointLight2D.new()
	_luz.texture = OSCURIDAD.textura_luz()
	_luz.texture_scale = 1.3
	_luz.color = Color(0.75, 0.5, 1.0)
	_luz.energy = 0.0
	_luz.position = Vector2(0, -40)
	add_child(_luz)
	if Estado.tiene("gruta_guardian"):
		# ya despierto: se queda en la sala, tranquilo
		_quedarse_despierto()
		return


func _centro() -> Vector2:
	return zona.global_position if zona else global_position


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	vida = R.GUARDIAN_VIDA
	_grietas = 0
	global_position = _centro() + Vector2(0, -20)
	_cambiar(Fase.PRESENTACION)
	Sonido.efecto("guardian_brama")
	Impacto.temblar(4.0, 0.8)
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = R.GUARDIAN_VIDA
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)


func reiniciar() -> void:
	vida = R.GUARDIAN_VIDA
	_ola = -1.0
	_grietas = 0
	if _barra:
		_barra.queue_free()
		_barra = null
	fase = Fase.DORMIDO
	global_position = _centro() + Vector2(0, -20)
	remove_from_group("golpeables")
	remove_from_group("daniables")


func _cambiar(nueva: int) -> void:
	fase = nueva
	_t = 0.0
	if nueva in [Fase.DORMIDO, Fase.VENCIDO]:
		remove_from_group("golpeables")
		remove_from_group("daniables")
	else:
		add_to_group("golpeables")
		add_to_group("daniables")


func _fase_pelea() -> int:
	if vida <= R.GUARDIAN_VIDA / 3:
		return 3
	if vida <= R.GUARDIAN_VIDA * 2 / 3:
		return 2
	return 1


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_blanco = maxf(0.0, _blanco - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	_encuadrar(delta, maisha)
	_capa.queue_redraw()
	var deprisa := 0.7 if _fase_pelea() == 3 else 1.0
	match fase:
		Fase.DORMIDO:
			_sprite.frame = QUIETO
		Fase.PRESENTACION:
			if _t > 2.0:
				_espera = 1.0
				_cambiar(Fase.ESPERA)
		Fase.ESPERA:
			_espera -= delta
			if maisha and absf(maisha.global_position.x - global_position.x) > 4.0:
				_mira = signf(maisha.global_position.x - global_position.x)
			if _espera <= 0.0 and maisha:
				if randf() < 0.4:
					_cambiar(Fase.PISA)
					Sonido.efecto("guardian_brama", -6.0, global_position)
				else:
					_seguidas = 2 if _fase_pelea() == 3 and randf() < 0.5 else 1
					_escarbar(maisha)
		Fase.ESCARBA:
			if maisha and _t < 0.4 * deprisa:
				_hacia = (maisha.global_position - global_position).normalized()
				if absf(_hacia.x) > 0.1:
					_mira = signf(_hacia.x)
			if _t >= R.GUARDIAN_AVISO * deprisa:
				_pillo = false
				_cambiar(Fase.EMBISTE)
				Sonido.efecto("guardian_carga", 0.0, global_position)
		Fase.EMBISTE:
			global_position += _hacia * VELOCIDAD_EMBESTIDA * delta
			if maisha and not _pillo and maisha.global_position.distance_to(global_position + _hacia * 18.0) < 22.0:
				_pillo = true
				maisha.call("recibir_danio", 1, global_position, "contacto")
			if zona and zona.distancia_normal(global_position + _hacia * 24.0) > 0.9:
				_chocar()
		Fase.ATURDIDO:
			if _t >= R.GUARDIAN_ATURDIDO:
				_seguidas -= 1
				if _seguidas > 0 and maisha:
					_escarbar(maisha)
				else:
					_espera = R.GUARDIAN_ESPERA * deprisa
					_cambiar(Fase.ESPERA)
		Fase.PISA:
			if _t >= 0.7 and _t - delta < 0.7 and maisha:
				_ola = 0.0
				_ola_pillo = false
				_ola_desde = global_position
				_ola_hacia = (maisha.global_position - global_position).normalized()
				Sonido.efecto("raiz_azota", 0.0, global_position)
				Impacto.temblar(3.0, 0.4)
			if _t >= 1.4:
				_espera = R.GUARDIAN_ESPERA * deprisa
				_cambiar(Fase.ESPERA)
		Fase.VENCIDO:
			_proceso_vencido()
	_mover_ola(delta, maisha)
	var luz_meta := 0.0 if fase == Fase.DORMIDO else (1.4 if fase == Fase.ATURDIDO else 1.0)
	if fase == Fase.VENCIDO:
		luz_meta = 0.9
		_luz.color = _luz.color.lerp(Color(1.0, 0.85, 0.5), delta)
	_luz.energy = move_toward(_luz.energy, luz_meta, delta * 2.0)
	_animar()


func _escarbar(maisha: Node2D) -> void:
	_hacia = (maisha.global_position - global_position).normalized()
	_cambiar(Fase.ESCARBA)
	Sonido.efecto("guardian_brama", -8.0, global_position)


func _chocar() -> void:
	_cambiar(Fase.ATURDIDO)
	Sonido.efecto("kambare_cae", 0.0, global_position)
	Impacto.temblar(4.0, 0.4)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 12
	astillas.fuerza = 80.0
	astillas.position = global_position + _hacia * 30.0 + Vector2(0, -20)
	get_parent().add_child(astillas)
	global_position -= _hacia * 6.0
	if _fase_pelea() >= 2 and zona and get_tree().get_nodes_in_group("enemigos").size() < 2:
		# la pesadilla llama a dos Petrinos
		for k in 2:
			zona.call("invocar_petrino_en", _centro() + Vector2(-60 + k * 120, 40))


## La ola de raíces: una línea de raíces-látigo que avanza por el suelo; hace daño al pasar por Maisha
func _mover_ola(delta: float, maisha: Node2D) -> void:
	if _ola < 0.0:
		return
	_ola += OLA_VELOCIDAD * delta
	var frente := _ola_desde + _ola_hacia * _ola
	if maisha and not _ola_pillo and maisha.global_position.distance_to(frente) < 16.0:
		_ola_pillo = true
		maisha.call("recibir_danio", 1, frente - _ola_hacia * 8.0, "raices")
	if _ola > 260.0:
		_ola = -1.0


# --- Daño ---------------------------------------------------------------------------

func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase == Fase.ATURDIDO:
		_herir(danio)
		return true
	_blanco = 0.04
	Sonido.efecto("clinc", 0.0, global_position)
	return false


func recibir_danio(_cantidad: int, _desde_p: Vector2, tipo: String) -> void:
	if tipo == "explosion" and fase == Fase.ATURDIDO:
		_herir(R.GUARDIAN_DANIO_SEMILLA)


func _herir(cuanto: int) -> void:
	if vida <= 0:
		return
	vida = maxi(0, vida - cuanto)
	vida_cambiada.emit(vida)
	_blanco = 0.25
	_grietas = int((1.0 - float(vida) / R.GUARDIAN_VIDA) * 8.0)
	Impacto.pausa(0.07)
	Sonido.efecto("mascara_cruje", 0.0, global_position)
	if vida <= 0:
		_vencer()


func _vencer() -> void:
	_cambiar(Fase.VENCIDO)
	_ola = -1.0
	Sonido.efecto("mascara_rompe")
	Sonido.musica("", 1.5)
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.call("morir")
	Impacto.temblar(5.0, 1.0)
	Impacto.fogonazo(Color("d6a8f0"), 0.5, 0.6)


func _proceso_vencido() -> void:
	if _t < 1.6:
		_blanco = 0.05 if int(_t * 8.0) % 2 == 0 else 0.0
		_sprite.frame = ATURDIDO_F
		if int(_t * 16.0) % 3 == 0:
			var astillas: Node2D = ASTILLAS.new()
			astillas.cantidad = 5
			astillas.chispas = 3
			astillas.fuerza = 70.0
			astillas.position = global_position + Vector2(_mira * 30.0, -50)
			get_parent().add_child(astillas)
	else:
		_sprite.frame = LIBRE
	if _t > 4.0 and is_in_group("jefes"):
		remove_from_group("jefes")
		if _barra:
			_barra.call("cerrar")
		Estado.marcar("gruta_guardian")
		destruido.emit()
		_quedarse_despierto()


## Despierto: se queda en la sala, tranquilo, y se puede hablar con él
func _quedarse_despierto() -> void:
	fase = Fase.VENCIDO
	_t = 99.0
	_sprite.frame = LIBRE
	_mira = -1.0
	_sprite.flip_h = true
	_luz.energy = 0.9
	_luz.color = Color(1.0, 0.85, 0.5)
	add_to_group("interactuables")
	set_meta("despierto", true)


var radio_interaccion := 50.0
var altura_bocadillo := 70.0


func interactuar() -> void:
	if has_meta("despierto"):
		await load("res://scripts/mundo/charla.gd").hablar(self, "guardian")


# --- Dibujo -----------------------------------------------------------------------

func _animar() -> void:
	if fase == Fase.VENCIDO:
		_sprite.modulate = Color(3, 3, 3) if _blanco > 0.0 else Color.WHITE
		return
	_sprite.flip_h = _mira < 0.0
	match fase:
		Fase.PRESENTACION:
			_sprite.frame = PISA_F if _t > 1.0 else QUIETO
		Fase.ESPERA:
			_sprite.frame = QUIETO
		Fase.ESCARBA:
			_sprite.frame = ESCARBA_F if int(_tiempo * 6.0) % 2 == 0 else QUIETO
		Fase.EMBISTE:
			_sprite.frame = EMBISTE_F
		Fase.ATURDIDO:
			_sprite.frame = ATURDIDO_F
		Fase.PISA:
			_sprite.frame = PISA_F if _t < 0.8 else QUIETO
	_sprite.modulate = Color(3, 3, 3) if _blanco > 0.0 else Color.WHITE
	queue_redraw()


func _draw() -> void:
	if fase == Fase.VENCIDO:
		return
	# las grietas de la máscara (más cuanto más daño) y las estrellitas si está aturdido
	var cara := Vector2(_mira * 34.0, -52.0)
	var azar := RandomNumberGenerator.new()
	azar.seed = 7
	for k in _grietas:
		var a := azar.randf() * TAU
		draw_line(cara, cara + Vector2(cos(a), sin(a)) * azar.randf_range(4.0, 8.0), Color("d6a8f0"), 1.0)
	if fase == Fase.ATURDIDO:
		for k in 3:
			var a := _tiempo * 5.0 + k * TAU / 3.0
			draw_rect(Rect2((cara + Vector2(cos(a) * 9.0, -14.0 + sin(a) * 2.0)).round(), Vector2(2, 2)), Color("fff3c4"))


func _dibujar_capa() -> void:
	if fase in [Fase.DORMIDO, Fase.VENCIDO]:
		return
	# los hilos de la marioneta: bajan del techo hasta el lomo, la cabeza y las patas (tiran más en la fase 3)
	var tension := 0.6 + 0.2 * _fase_pelea()
	for k in 4:
		var punto: Vector2 = global_position + [Vector2(-24, -40), Vector2(_mira * 30.0, -60), Vector2(-10, -14), Vector2(_mira * 14.0, -14)][k]
		var techo := Vector2(punto.x + sin(_tiempo * 0.8 + k) * 10.0, _centro().y - 190.0)
		var medio: Vector2 = (techo + punto) / 2.0 + Vector2(sin(_tiempo * 2.0 + k * 1.3) * 6.0 * (1.2 - tension), 0)
		_capa.draw_polyline(PackedVector2Array([techo, medio, punto]), Color(0.66, 0.33, 0.84, 0.35 + 0.3 * tension), 1.0)
	# la raya del aviso de la embestida
	if fase == Fase.ESCARBA:
		var a := 0.3 + 0.3 * sin(_tiempo * 18.0)
		for i in 12:
			if i % 2 == 0:
				var p0 := global_position + _hacia * (20.0 + i * 12.0)
				_capa.draw_line(p0, p0 + _hacia * 8.0, Color(0.85, 0.6, 1.0, a + 0.2), 2.5)
	# la ola de raíces
	if _ola >= 0.0:
		var lado := Vector2(-_ola_hacia.y, _ola_hacia.x)
		for i in 5:
			var d := _ola - i * 10.0
			if d < 0.0:
				continue
			var p := _ola_desde + _ola_hacia * d
			var alto := 10.0 - i * 1.6
			for s in [-1.0, 1.0]:
				var base: Vector2 = p + lado * s * (6.0 + i)
				_capa.draw_line(base, base + Vector2(sin(_tiempo * 20.0 + i) * 2.0, -alto), Color("62442c"), 3.0)
				_capa.draw_line(base, base + Vector2(sin(_tiempo * 20.0 + i) * 2.0, -alto), Color("a855d6"), 1.0)


## Durante la pelea, la cámara enseña la sala entera
func _encuadrar(delta: float, maisha: Node2D) -> void:
	var camara := get_viewport().get_camera_2d()
	if camara == null or maisha == null or camara.get_parent() != maisha:
		return
	var peleando := fase not in [Fase.DORMIDO, Fase.VENCIDO] and is_in_group("jefes")
	var objetivo := Vector2.ZERO
	if peleando:
		objetivo = (_centro() + Vector2(0, -10) - maisha.global_position) * 0.85
	camara.position = camara.position.lerp(objetivo, minf(1.0, delta * 3.0)).round()
