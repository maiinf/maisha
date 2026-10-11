extends Node2D
## PEMBE, EL CIERVO DE HIERRO: el minijefe del Bosque Cobrizo.
## El guardián del bosque. Giza le convirtió las astas en hierro y le cubrió el lomo de placas: ya no
## distingue a nadie y embiste contra todo lo que se mueve.
##
## Ciclo:  ACECHO (camina mirando a Maisha) → PREPARA (escarba; una línea roja marca por dónde irá)
##         → EMBISTE en línea recta → choca:
##            · contra un ÁRBOL de la arena: se le clavan las astas y queda ATASCADO un rato.
##              Es el momento: el cetro le quita 1 y cada semilla que le estalle al lado, 2.
##            · contra el borde de la arena: se aturde un instante y vuelve a acechar (no se le puede dañar).
## Fase 2 (con la mitad de vida): se prepara más rápido, llama a dos jabalíes de hierro una vez y, al
## soltarse de un árbol, sacude las astas y caen trozos de hierro del cielo (con su sombra de aviso).
## Al vencerlo, el hierro se le cae a trozos: las astas vuelven a ser ramas con hojas cobrizas. Se inclina
## ante Maisha y se va al bosque. Hace de «Corazón» de su zona (zona_corrupta.gd con jefe = "pembe").

signal destruido
signal vida_cambiada(vida: int)

enum Fase { DORMIDO, PRESENTACION, ACECHO, PREPARA, EMBISTE, ATASCADO, ATURDIDO, VENCIDO }

const R := preload("res://scripts/combate/reglas_combate.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const ASTA := preload("res://scripts/enemigos/asta_cae.gd")
const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const NOMBRE := "Pembe, el ciervo de hierro"
const ANDAR := [0, 1]
const PREPARAR := 2
const GALOPE := [3, 4]
const CLAVADO := 5
const LIBRE := 6
const INCLINA := 7

var zona: Node2D
var variante := "raiz"
var vida: int = R.PEMBE_VIDA
var fase: int = Fase.DORMIDO

var _t := 0.0
var _tiempo := 0.0
var _dir := Vector2.RIGHT
var _mira := 1.0                 # 1 = a la derecha, -1 = a la izquierda
var _arboles: Array[Node2D] = []
var _arbol_clavado: Node2D
var _llamados := false
var _blanco := 0.0
var _sacudida := 0.0
var _sprite: Sprite2D
var _sombra: Node2D
var _linea: Node2D
var _barra: CanvasLayer
var _fin_linea := Vector2.ZERO
var _origen := Vector2.ZERO


func _ready() -> void:
	add_to_group("jefes")
	_sombra = Node2D.new()
	_sombra.set_script(SOMBRA)
	_sombra.set("ancho", 26.0)
	add_child(_sombra)
	_linea = Node2D.new()
	_linea.z_index = -2
	_linea.draw.connect(_dibujar_linea)
	add_child(_linea)
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://arte/zonas/%s/pembe.png" % variante)
	_sprite.hframes = 8
	_sprite.offset = Vector2(-4, -31)
	add_child(_sprite)
	visible = false
	_origen = position


# --- La pelea -------------------------------------------------------------------

func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	vida = R.PEMBE_VIDA
	_llamados = false
	visible = true
	modulate.a = 1.0
	_arboles.clear()
	for a in get_tree().get_nodes_in_group("arboles"):
		if zona.distancia_normal(a.global_position) < 0.95:
			_arboles.append(a)
	global_position = zona.global_position + Vector2(0, -zona.radios_umbral.y * 0.45)
	_cambiar(Fase.PRESENTACION)
	Sonido.efecto("pembe_bramido")
	Impacto.temblar(3.5, 0.8)
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = R.PEMBE_VIDA
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)


func reiniciar() -> void:
	vida = R.PEMBE_VIDA
	if _barra:
		_barra.queue_free()
		_barra = null
	for a in get_tree().get_nodes_in_group("astas_cayendo"):
		a.queue_free()
	remove_from_group("daniables")
	remove_from_group("golpeables")
	fase = Fase.DORMIDO
	visible = false
	_arbol_clavado = null


func _cambiar(nueva: int) -> void:
	fase = nueva
	_t = 0.0
	if nueva in [Fase.ATASCADO]:
		add_to_group("golpeables")
		add_to_group("daniables")
	elif nueva in [Fase.ACECHO, Fase.PREPARA, Fase.EMBISTE, Fase.ATURDIDO, Fase.PRESENTACION]:
		# también se le puede golpear (rebota en el hierro): así se nota que hay que esperar
		add_to_group("golpeables")
		add_to_group("daniables")
	else:
		remove_from_group("golpeables")
		remove_from_group("daniables")


func _en_fase_2() -> bool:
	return vida <= R.PEMBE_VIDA / 2


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_blanco = maxf(0.0, _blanco - delta)
	_sacudida = maxf(0.0, _sacudida - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	_encuadrar(delta)
	match fase:
		Fase.DORMIDO:
			return
		Fase.PRESENTACION:
			if _t > 2.0:
				_cambiar(Fase.ACECHO)
		Fase.ACECHO:
			if maisha:
				var hacia := maisha.global_position - global_position
				# camina de lado, sin acercarse del todo: busca ponerse de cara
				var lateral := Vector2(-hacia.y, hacia.x).normalized() * (1.0 if int(_tiempo / 2.0) % 2 == 0 else -1.0)
				var mov := (lateral * 0.7 + hacia.normalized() * (0.3 if hacia.length() > 90.0 else -0.3)) * R.PEMBE_ANDA
				var nueva := global_position + mov * delta
				if zona.distancia_normal(nueva) < 0.85 and not _choca_arbol(nueva, 12.0):
					global_position = nueva
				if absf(hacia.x) > 4.0:
					_mira = signf(hacia.x)
			if _t >= R.PEMBE_ACECHA * (0.65 if _en_fase_2() else 1.0):
				_preparar(maisha)
		Fase.PREPARA:
			var espera: float = R.PEMBE_PREPARA_FASE2 if _en_fase_2() else R.PEMBE_PREPARA
			if int(_t * 10.0) % 3 == 0:
				_polvo(global_position + Vector2(_mira * 14.0, 0), 1)
			if _t >= espera:
				_cambiar(Fase.EMBISTE)
				Sonido.efecto("pembe_galope")
		Fase.EMBISTE:
			_embestir(delta, maisha)
		Fase.ATASCADO:
			_sacudida = 0.05 if int(_t * 12.0) % 2 == 0 else 0.0
			if _t >= R.PEMBE_ATASCADO:
				_soltarse()
		Fase.ATURDIDO:
			if _t >= R.PEMBE_ATURDIDO:
				_cambiar(Fase.ACECHO)
		Fase.VENCIDO:
			_proceso_vencido()
	# daño por contacto (más fuerte si embiste)
	if maisha and fase in [Fase.ACECHO, Fase.EMBISTE, Fase.PREPARA] and _toca(maisha.global_position):
		var danio := R.PEMBE_DANIO if fase == Fase.EMBISTE else 1
		maisha.call("recibir_danio", danio, global_position, "contacto")
	_animar()
	_linea.queue_redraw()


func _preparar(maisha: Node2D) -> void:
	if maisha == null:
		return
	_dir = (maisha.global_position - global_position).normalized()
	if _dir == Vector2.ZERO:
		_dir = Vector2.RIGHT
	if absf(_dir.x) > 0.05:
		_mira = signf(_dir.x)
	# hasta dónde llegaría (para dibujar la línea de aviso)
	_fin_linea = global_position
	for i in 80:
		var p := _fin_linea + _dir * 6.0
		if zona.distancia_normal(p) > 0.9 or _choca_arbol(p, 14.0):
			break
		_fin_linea = p
	_cambiar(Fase.PREPARA)
	Sonido.efecto("pembe_escarba")


func _embestir(delta: float, maisha: Node2D) -> void:
	var nueva := global_position + _dir * R.PEMBE_EMBISTE * delta
	if int(_t * 14.0) % 2 == 0:
		_polvo(global_position - _dir * 10.0, 1)
	# ¿un árbol delante? → se clava
	var arbol := _arbol_en(nueva + _dir * 10.0, 13.0)
	if arbol:
		_arbol_clavado = arbol
		_cambiar(Fase.ATASCADO)
		Sonido.efecto("pembe_choque")
		Impacto.temblar(4.0, 0.3)
		Impacto.pausa(0.06)
		_astillas(global_position + _dir * 16.0 + Vector2(0, -20), 10)
		# el árbol tiembla
		var t := create_tween()
		t.tween_property(arbol, "position:x", arbol.position.x + 2.0, 0.05)
		t.tween_property(arbol, "position:x", arbol.position.x - 2.0, 0.08)
		t.tween_property(arbol, "position:x", arbol.position.x, 0.05)
		return
	# ¿el borde de la arena? → se aturde un momento (sin clavarse)
	if zona.distancia_normal(nueva) > 0.9 or _t > 3.0:
		_cambiar(Fase.ATURDIDO)
		Sonido.efecto("piedra_rompe", 0.0, global_position)
		Impacto.temblar(2.0, 0.2)
		return
	global_position = nueva


func _soltarse() -> void:
	_arbol_clavado = null
	Sonido.efecto("pembe_bramido", -6.0)
	_cambiar(Fase.ACECHO)
	# se echa un poco atrás
	global_position -= _dir * 10.0
	if _en_fase_2():
		var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
		for k in R.PEMBE_ASTAS_FASE2:
			var asta: Node2D = ASTA.new()
			asta.add_to_group("astas_cayendo")
			var cerca := maisha.global_position if maisha and k == 0 else zona.global_position
			var p := cerca + Vector2(randf_range(-60, 60), randf_range(-40, 40)) * (0.4 if k == 0 else 1.0)
			if zona.distancia_normal(p) > 0.85:
				p = zona.global_position + (p - zona.global_position) * 0.6
			asta.position = p
			get_parent().add_child(asta)


func _toca(p: Vector2) -> bool:
	# el cuerpo es alargado: un óvalo de 34×12 alrededor de las patas
	var d := p - (global_position + Vector2(-4 * _mira, 0))
	return (d.x / 20.0) ** 2 + (d.y / 9.0) ** 2 < 1.0


func _arbol_en(p: Vector2, radio: float) -> Node2D:
	for a in _arboles:
		if is_instance_valid(a) and a.global_position.distance_to(p) < radio:
			return a
	return null


func _choca_arbol(p: Vector2, radio: float) -> bool:
	return _arbol_en(p, radio) != null


## Durante la pelea, la cámara enseña el claro entero (Maisha no siempre va en el centro)
func _encuadrar(delta: float) -> void:
	var camara := get_viewport().get_camera_2d()
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if camara == null or maisha == null or camara.get_parent() != maisha:
		return
	var peleando := fase != Fase.DORMIDO and is_in_group("jefes")
	var objetivo := Vector2.ZERO
	if peleando:
		objetivo = (zona.global_position + Vector2(0, -10) - maisha.global_position) * 0.85
	camara.position = camara.position.lerp(objetivo, minf(1.0, delta * 3.0)).round()


# --- Daño ---------------------------------------------------------------------------

func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if fase != Fase.ATASCADO:
		_blanco = 0.04
		Sonido.efecto("clinc", 0.0, global_position)
		return false
	_herir(danio)
	return true


func recibir_danio(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if tipo != "explosion" or fase != Fase.ATASCADO:
		return
	_herir(R.PEMBE_SEMILLA_DANIO)


func _herir(cuanto: int) -> void:
	if vida <= 0:
		return
	var antes_fase_2 := _en_fase_2()
	vida = maxi(0, vida - cuanto)
	vida_cambiada.emit(vida)
	_blanco = 0.25
	Impacto.pausa(0.07)
	Impacto.temblar(2.5, 0.2)
	Sonido.efecto("pembe_dolor")
	_astillas(global_position + Vector2(0, -26), 8)
	if vida <= 0:
		_vencer()
		return
	if _en_fase_2() and not antes_fase_2 and not _llamados:
		_llamados = true
		for k in 2:
			var p: Vector2 = zona.global_position + Vector2(-1 + k * 2, 0.5) * zona.radios_umbral * 0.55
			_polvo(p, 6)
			zona.call("invocar_en", p, "jabali")


func _vencer() -> void:
	_cambiar(Fase.VENCIDO)
	Sonido.efecto("pembe_vencido")
	Sonido.musica("", 1.5)
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.call("morir")
	for a in get_tree().get_nodes_in_group("astas_cayendo"):
		a.queue_free()
	Impacto.temblar(5.0, 1.0)


## Vencido: tiembla, se le cae el hierro a trozos, se inclina ante Maisha y se va al bosque
func _proceso_vencido() -> void:
	if _t < 1.2:
		_blanco = 0.05 if int(_t * 8.0) % 2 == 0 else 0.0
		_sprite.frame = CLAVADO
	elif _t < 2.6:
		_sprite.frame = LIBRE if _t > 1.9 else CLAVADO
		if int(_t * 20.0) % 3 == 0:
			_astillas(global_position + Vector2(randf_range(-16, 16), -randf_range(10, 50)), 4)
	elif _t < 4.4:
		_sprite.frame = INCLINA if _t < 3.8 else LIBRE
		var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
		if maisha and absf(maisha.global_position.x - global_position.x) > 4.0:
			_mira = signf(maisha.global_position.x - global_position.x)
	else:
		# se va trotando, y se desvanece entre los árboles
		_sprite.frame = ANDAR[int(_tiempo * 6.0) % 2]
		global_position += Vector2(-_mira, -0.4) * 40.0 * get_process_delta_time()
		_sprite.flip_h = _mira > 0.0
		modulate.a = maxf(0.0, 1.0 - (_t - 4.4) / 1.4)
	if _t > 5.8 and is_in_group("jefes"):
		remove_from_group("jefes")
		if _barra:
			_barra.call("cerrar")
		destruido.emit()
		visible = false


# --- Dibujo -----------------------------------------------------------------------

func _animar() -> void:
	if fase == Fase.VENCIDO:
		return
	_sprite.flip_h = _mira < 0.0
	match fase:
		Fase.PRESENTACION:
			_sprite.frame = PREPARAR if _t < 1.2 else ANDAR[0]
		Fase.ACECHO:
			_sprite.frame = ANDAR[int(_tiempo * 4.0) % 2]
		Fase.PREPARA:
			_sprite.frame = PREPARAR
		Fase.EMBISTE:
			_sprite.frame = GALOPE[int(_tiempo * 10.0) % 2]
		Fase.ATASCADO:
			_sprite.frame = CLAVADO
		Fase.ATURDIDO:
			_sprite.frame = ANDAR[0]
	_sprite.position.x = (1.0 if _sacudida > 0.0 else 0.0)
	var pulso := 0.5 + 0.5 * sin(_tiempo * 3.0)
	_sprite.modulate = Color(3, 3, 3) if _blanco > 0.0 else Color(1.0 + 0.08 * pulso, 1.0, 1.0 + 0.14 * pulso)
	queue_redraw()


func _draw() -> void:
	if fase == Fase.DORMIDO:
		return
	# halo de Giza bajo sus patas
	if fase != Fase.VENCIDO:
		var pulso := 0.5 + 0.5 * sin(_tiempo * 4.0)
		for y in range(-3, 4):
			var ancho := int(round(24.0 * sqrt(1.0 - (y / 4.0) * (y / 4.0))))
			draw_rect(Rect2(-ancho, y, ancho * 2, 1), Color(0.66, 0.33, 0.84, 0.14 + 0.08 * pulso))
	# atascado: estrellitas y un aviso de «¡ahora!»
	if fase == Fase.ATASCADO:
		for k in 3:
			var a := _tiempo * 5.0 + k * TAU / 3.0
			var p := Vector2(_mira * 14.0 + cos(a) * 8.0, -50.0 + sin(a) * 2.0).round()
			draw_rect(Rect2(p, Vector2(2, 2)), Color("fff3c4"))


## La línea roja que marca por dónde va a embestir
func _dibujar_linea() -> void:
	if fase != Fase.PREPARA:
		return
	var espera: float = R.PEMBE_PREPARA_FASE2 if _en_fase_2() else R.PEMBE_PREPARA
	var f := clampf(_t / espera, 0.0, 1.0)
	var hasta := _linea.to_local(_fin_linea)
	var largo := hasta.length()
	var dir := hasta.normalized()
	var lado := Vector2(-dir.y, dir.x)
	var parpadeo := 0.75 + 0.25 * sin(_tiempo * 18.0)
	# una franja roja translúcida por donde pasará, con flechas que avanzan
	var puntos := PackedVector2Array([lado * 7.0, dir * largo * f + lado * 7.0, dir * largo * f - lado * 7.0, -lado * 7.0])
	_linea.draw_colored_polygon(puntos, Color(0.9, 0.2, 0.15, 0.16 * parpadeo))
	_linea.draw_line(lado * 7.0, dir * largo * f + lado * 7.0, Color(1.0, 0.35, 0.25, 0.6 * parpadeo), 1.0)
	_linea.draw_line(-lado * 7.0, dir * largo * f - lado * 7.0, Color(1.0, 0.35, 0.25, 0.6 * parpadeo), 1.0)
	var k := fmod(_tiempo * 60.0, 16.0)
	while k < largo * f - 4.0:
		var c := dir * k
		_linea.draw_polyline(PackedVector2Array([c + lado * 4.0 - dir * 3.0, c, c - lado * 4.0 - dir * 3.0]), Color(1.0, 0.5, 0.35, 0.7 * parpadeo), 2.0)
		k += 16.0


func _polvo(p: Vector2, n: int) -> void:
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = n
	astillas.fuerza = 40.0
	astillas.position = p
	get_parent().add_child(astillas)


func _astillas(p: Vector2, n: int) -> void:
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = n
	astillas.chispas = 3
	astillas.fuerza = 90.0
	astillas.position = p
	get_parent().add_child(astillas)
