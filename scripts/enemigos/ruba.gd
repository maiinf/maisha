extends Node2D
## RUBA, LA SANGUIJUELA DE TINTA (Sigilia, el Canal de Tinta): vive dentro de la tinta líquida («~») y no sale de ella.
##   - OCULTA: nada bajo la tinta (solo se ven las ondas) hacia Maisha si la nota cerca (en la orilla o en una placa).
##   - Al llegar, ASOMA un momento (el aviso) y SE LANZA: muerde (1 hoja) y, si Maisha va en una placa de hielo,
##     se la agrieta (le quita vida a la placa). Luego se vuelve a hundir y descansa.
##   - Mientras está oculta o asomada no hay forma de darle (el cetro se pierde en la tinta).
##   - EL SIGILO DE HIELO sobre ella la deja ATRAPADA en un témpano, con media cabeza fuera, ATRAPADA s: ahí entran
##     el cetro (1) y las semillas (2). 3 de vida. Después rompe el hielo y se hunde.
## Dibujo: arte/mundos/sigilia/canal/ruba.png (herramientas/pintar_canal.py).

signal destruido

const DIBUJO := preload("res://arte/mundos/sigilia/canal/ruba.png")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const VIDA := 3
const NADA := 46.0
const NOTA := 120.0                     # a cuánto nota a Maisha
const ALCANCE := 20.0                   # a cuánto asoma y se lanza (al alcance del cetro, si se la hiela)
const MUERDE := 24.0
const ASOMA := 0.7
const LANZA := 0.35
const DESCANSO := 2.2
const ATRAPADA := 4.0
const GRIETA := 7.0                     # lo que le quita a una placa al morderla

enum Fase { OCULTA, ASOMA, LANZA, ATRAPADA }

var vida := VIDA
var fase := Fase.OCULTA
var _t := 0.0
var _descanso := 0.0
var _destello := 0.0
var _tiempo := 0.0
var _muriendo := false
var _rumbo := Vector2.ZERO
var _cambio := 0.0
var _filas: PackedStringArray
var _sprite: Sprite2D
var _mordio := false


func _ready() -> void:
	add_to_group("enemigos")
	add_to_group("congelables")
	add_to_group("rubas")
	_filas = get_tree().current_scene.get_node("Region")._filas
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 5
	_sprite.offset = Vector2(0, -12)
	_sprite.visible = false
	add_child(_sprite)
	_tiempo = randf() * 3.0


func _es_tinta(p: Vector2) -> bool:
	var x := floori(p.x / 16.0)
	var y := floori(p.y / 16.0)
	return y >= 0 and y < _filas.size() and x >= 0 and x < _filas[y].length() and _filas[y][x] == "~"


func _process(delta: float) -> void:
	if _muriendo:
		return
	_tiempo += delta
	_t += delta
	_descanso = maxf(0.0, _descanso - delta)
	_destello = maxf(0.0, _destello - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	match fase:
		Fase.OCULTA:
			var mov := Vector2.ZERO
			var d := (maisha.global_position - global_position) if maisha else Vector2.INF
			if maisha and _descanso <= 0.0 and d.length() < NOTA and not maisha.get("esta_caida"):
				mov = d.normalized() * NADA
				if d.length() < ALCANCE:
					_cambiar(Fase.ASOMA)
					Sonido.efecto("babosa_chof", -2.0, global_position, 0.2)
			else:
				_cambio -= delta
				if _cambio <= 0.0:
					_cambio = randf_range(1.0, 2.4)
					_rumbo = Vector2.from_angle(randf() * TAU) * NADA * 0.4
				mov = _rumbo
			# (no sale de la tinta: si el paso la saca, prueba solo en horizontal o en vertical)
			var p := global_position + mov * delta
			if not _es_tinta(p):
				p = global_position + Vector2(mov.x, 0) * delta
				if not _es_tinta(p):
					p = global_position + Vector2(0, mov.y) * delta
					if not _es_tinta(p):
						p = global_position
						_cambio = 0.0
			global_position = p
		Fase.ASOMA:
			if _t >= ASOMA:
				_cambiar(Fase.LANZA)
				_mordio = false
				Sonido.efecto("mamba_muerde", -4.0, global_position, 0.2)
		Fase.LANZA:
			if not _mordio and maisha and global_position.distance_to(maisha.global_position) < MUERDE:
				_mordio = true
				maisha.call("recibir_danio", 1, global_position, "contacto")
				var placa: Node = maisha.get_meta("placa") if maisha.has_meta("placa") else null
				if placa:
					placa.vida -= GRIETA
					Impacto.temblar(1.5, 0.15)
			if _t >= LANZA:
				_hundirse()
		Fase.ATRAPADA:
			if _t >= ATRAPADA:
				Sonido.efecto("hielo_romper", -2.0, global_position)
				_hundirse()
	_dibujar()


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


func _hundirse() -> void:
	_cambiar(Fase.OCULTA)
	_descanso = DESCANSO
	remove_from_group("daniables")
	remove_from_group("golpeables")


func _dibujar() -> void:
	_sprite.visible = fase != Fase.OCULTA
	if _destello > 0.0:
		_sprite.frame = 4
	elif fase == Fase.ATRAPADA:
		_sprite.frame = 3
	elif fase == Fase.LANZA:
		_sprite.frame = 2
	else:
		_sprite.frame = int(_tiempo * 3.0) % 2
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha and fase != Fase.ATRAPADA:
		_sprite.flip_h = maisha.global_position.x < global_position.x
	queue_redraw()


func _draw() -> void:
	# las ondas en la tinta (oculta, se ve por dónde va; asomada, el remolino alrededor)
	var col := Color(0.62, 0.52, 0.9, 0.55)
	if fase == Fase.ATRAPADA:
		# el témpano que la sujeta
		var hielo := PackedVector2Array([Vector2(-14, -2), Vector2(-8, -8), Vector2(7, -9), Vector2(15, -3), Vector2(12, 5), Vector2(-10, 6)])
		draw_colored_polygon(hielo, Color("3c6d93"))
		var cara := PackedVector2Array()
		for q in hielo:
			cara.append((q * 0.8 + Vector2(-1, -1)).round())
		draw_colored_polygon(cara, Color("7fb6d8"))
		var filo := hielo.duplicate()
		filo.append(hielo[0])
		draw_polyline(filo, Color("0e1626"), 1.0)
		draw_line(Vector2(-7, -6), Vector2(5, -7), Color("eefaff"), 1.0)
		var vida_hielo := 1.0 - _t / ATRAPADA
		if vida_hielo < 0.4:
			draw_line(Vector2(-2, -8), Vector2(2, 4), Color("0e1626"), 1.0)
		return
	for k in 2:
		var r := fmod(_tiempo * 9.0 + k * 6.0, 12.0)
		draw_arc(Vector2(0, 0), 3.0 + r, 0, TAU, 16, Color(col, col.a * (1.0 - r / 12.0)), 1.0)
	if fase == Fase.OCULTA:
		draw_rect(Rect2(-1, -1, 1, 1), Color(0.75, 0.35, 0.95, 0.5 + 0.4 * sin(_tiempo * 5.0)))
		draw_rect(Rect2(2, -1, 1, 1), Color(0.75, 0.35, 0.95, 0.5 + 0.4 * sin(_tiempo * 5.0)))


# --- Hielo y daño --------------------------------------------------------------

## El Sigilo de Hielo: la deja atrapada (devuelve true para que el sigilo no haga además una placa)
func congelar() -> bool:
	if _muriendo:
		return false
	_cambiar(Fase.ATRAPADA)
	add_to_group("daniables")
	add_to_group("golpeables")
	Sonido.efecto("hielo_runa", 0.0, global_position)
	return true


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if _muriendo or fase != Fase.ATRAPADA:
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if _muriendo or fase != Fase.ATRAPADA:
		return
	vida -= 2 if tipo == "explosion" else cantidad
	_destello = 0.12
	Impacto.chispa(global_position + Vector2(0, -12), Vector2.UP, Color("8a70c0"))
	if vida > 0:
		Sonido.efecto("petrino_golpeado", -2.0, global_position)
	else:
		morir()


func morir() -> void:
	if _muriendo:
		return
	_muriendo = true
	Bestiario.vencido("ruba", self)
	Sonido.efecto("hielo_romper", 0.0, global_position)
	for g in ["enemigos", "congelables", "rubas", "daniables", "golpeables"]:
		remove_from_group(g)
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 12
	astillas.position = global_position + Vector2(0, -8)
	get_parent().add_child(astillas)
	destruido.emit()
	var t := create_tween().set_parallel(true)
	t.tween_property(_sprite, "scale", Vector2(1.2, 0.2), 0.3)
	t.tween_property(self, "modulate:a", 0.0, 0.35)
	t.chain().tween_callback(queue_free)
