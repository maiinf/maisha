extends Node2D
## SOMBRA DE RENGLÓN (Sigilia, la Sección Prohibida): una tira de tinta viva, hecha de frases borradas, que sale de
## los libros encadenados. Repta por el mármol hacia Maisha y se le LANZA (1 hoja).
##   - Es tinta suelta: el cetro y las semillas la atraviesan (se deshace y se rehace).
##   - CUALQUIER SIGILO la FIJA: el fuego la seca, el hielo la congela, el rayo la cuaja. FIJADA s se queda sólida y
##     pálida: ahí entran el cetro (1) y las semillas (2). 2 de vida. Si no se le vence a tiempo, vuelve a ser tinta.
## Está en «encendibles», «congelables» y «cargables» (cada sigilo llama al suyo).
## Dibujo: arte/mundos/sigilia/seccion/sombra.png (herramientas/pintar_seccion_prohibida.py).

signal destruido

const DIBUJO := preload("res://arte/mundos/sigilia/seccion/sombra.png")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIDA := 2
const REPTA := 34.0
const VE := 110.0
const SALTA_A := 26.0
const AVISO := 0.5
const SALTO := 0.3
const DESCANSO := 1.6
const FIJADA := 4.0

enum Fase { REPTA, AVISA, SALTA, DESCANSA, FIJADA }

var vida := VIDA
var fase := Fase.REPTA
var _t := 0.0
var _tiempo := 0.0
var _destello := 0.0
var _muriendo := false
var _mordio := false
var _rumbo := Vector2.ZERO
var _cambio := 0.0
var _filas: PackedStringArray
var _sprite: Sprite2D


func _ready() -> void:
	for g in ["enemigos", "encendibles", "congelables", "cargables", "golpeables", "daniables", "sombras_renglon"]:
		add_to_group(g)
	_filas = get_tree().current_scene.get_node("Region")._filas
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -11)
	add_child(_sprite)
	_tiempo = randf() * 3.0


func _es_suelo(p: Vector2) -> bool:
	var x := floori(p.x / 16.0)
	var y := floori(p.y / 16.0)
	return y >= 0 and y < _filas.size() and x >= 0 and x < _filas[y].length() and not (_filas[y][x] in ["0", "~", "="])


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _mover(paso: Vector2) -> void:
	for intento: Vector2 in [paso, Vector2(paso.x, 0), Vector2(0, paso.y)]:
		if intento != Vector2.ZERO and _es_suelo(global_position + intento + intento.normalized() * 6.0):
			global_position += intento
			return
	_cambio = 0.0


func _process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_t += delta
	_destello = maxf(0.0, _destello - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var d := (maisha.global_position - global_position) if maisha else Vector2.INF
	match fase:
		Fase.REPTA:
			if maisha and d.length() < VE and not maisha.get("esta_caida"):
				# (repta ondulando: no va recta)
				_mover((d.normalized() + d.orthogonal().normalized() * sin(_tiempo * 4.0) * 0.5) * REPTA * delta)
				_sprite.flip_h = d.x < 0.0
				if d.length() < SALTA_A:
					_cambiar(Fase.AVISA)
			else:
				_cambio -= delta
				if _cambio <= 0.0:
					_cambio = randf_range(1.0, 2.5)
					_rumbo = Vector2.from_angle(randf() * TAU) * REPTA * 0.4
				_mover(_rumbo * delta)
				_sprite.flip_h = _rumbo.x < 0.0
		Fase.AVISA:
			if _t >= AVISO:
				_cambiar(Fase.SALTA)
				_mordio = false
				_rumbo = d.normalized() if d != Vector2.INF else Vector2.ZERO
				Sonido.efecto("babosa_chof", -2.0, global_position, 0.2)
		Fase.SALTA:
			_mover(_rumbo * 120.0 * delta)
			if not _mordio and maisha and d.length() < 14.0:
				_mordio = true
				maisha.call("recibir_danio", 1, global_position, "contacto")
			if _t >= SALTO:
				_cambiar(Fase.DESCANSA)
		Fase.DESCANSA:
			if _t >= DESCANSO:
				_cambiar(Fase.REPTA)
		Fase.FIJADA:
			if _t >= FIJADA:
				Sonido.efecto("babosa_chof", -6.0, global_position, 0.2)
				_cambiar(Fase.REPTA)
	if _destello > 0.0:
		_sprite.frame = 4
	elif fase == Fase.FIJADA:
		_sprite.frame = 3
	elif fase in [Fase.AVISA, Fase.SALTA]:
		_sprite.frame = 2
	else:
		_sprite.frame = int(_tiempo * 4.0) % 2
	_sprite.modulate.a = 1.0 if fase == Fase.FIJADA else 0.86


# --- Los sigilos y el daño ------------------------------------------------------

func encender() -> void:
	_fijar()


func congelar() -> bool:
	_fijar()
	return not _muriendo


func cargar() -> void:
	_fijar()


func _fijar() -> void:
	if _muriendo:
		return
	_cambiar(Fase.FIJADA)
	Sonido.efecto("hielo_runa", -4.0, global_position, 0.2)
	Impacto.chispa(global_position + Vector2(0, -8), Vector2.UP, Color("d8d4ec"))


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if _muriendo or fase != Fase.FIJADA:
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo or fase != Fase.FIJADA or tipo in ["fuego", "rayo"]:
		return
	vida -= 2 if tipo == "explosion" else cantidad
	_destello = 0.12
	Impacto.chispa(global_position + Vector2(0, -8), Vector2.UP, Color("8a70c0"))
	if vida > 0:
		Sonido.efecto("petrino_golpeado", -2.0, global_position)
	else:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("sombra_renglon", self)
	Sonido.efecto("pagina", 0.0, global_position)
	for g in ["enemigos", "encendibles", "congelables", "cargables", "golpeables", "daniables", "sombras_renglon"]:
		remove_from_group(g)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 10
	astillas.position = global_position + Vector2(0, -6)
	get_parent().add_child(astillas)
	destruido.emit()
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.4, 0.1), 0.3)
	t.tween_property(self, "modulate:a", 0.0, 0.35)
	t.chain().tween_callback(queue_free)
