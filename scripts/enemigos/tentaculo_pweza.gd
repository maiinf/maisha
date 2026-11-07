extends Node2D
## UN TENTÁCULO DE PWEZA (la Gran Dársena): sale de la tinta junto a la orilla y AZOTA el muelle con su plumilla.
## El nodo va en la ORILLA (donde la tinta toca el muelle); `fuera` es hacia el muelle. El tentáculo nace un poco
## dentro de la tinta y se alarga hacia fuera.
##   AVISO (ondas, 0,8 s) → ASOMA → ALZADO (0,5 s) → AZOTA (golpe a lo largo de LARGO px: 1 hoja) → ARRIBA (2 s) → se va.
##   - ARRIBA (o alzado), el SIGILO DE HIELO lo deja HELADO HELADO s («congelables» → congelar). Helado, un golpe de
##     cetro tira de él: Pweza vuelca el tintero hacia ese lado (pweza.tirar).
## Dibujo: arte/mundos/sigilia/canal/tentaculo.png (herramientas/pintar_canal.py).

signal se_fue

const DIBUJO := preload("res://arte/mundos/sigilia/canal/tentaculo.png")
const AVISO := 0.8
const ASOMA := 0.25
const ALZADO := 0.5
const AZOTA := 0.3
const ARRIBA := 2.0
const HELADO := 5.0
const LARGO := 44.0
const ANCHO_GOLPE := 11.0

enum Fase { AVISO, ASOMA, ALZADO, AZOTA, ARRIBA, HELADO, FUERA }

var pweza: Node = null
var fuera := Vector2.DOWN
var fase := Fase.AVISO
var _t := 0.0
var _tiempo := 0.0
var _golpeo := false
var _sprite: Sprite2D


func _ready() -> void:
	add_to_group("tentaculos")
	add_to_group("congelables")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 4
	_sprite.offset = Vector2(0, -12)          # (la base, 20 px dentro de la tinta)
	_sprite.rotation = fuera.angle() + PI / 2.0
	_sprite.visible = false
	add_child(_sprite)
	Sonido.efecto("babosa_chof", -6.0, global_position, 0.3)


func _process(delta: float) -> void:
	_t += delta
	_tiempo += delta
	match fase:
		Fase.AVISO:
			if _t >= AVISO:
				_cambiar(Fase.ASOMA)
		Fase.ASOMA:
			if _t >= ASOMA:
				_cambiar(Fase.ALZADO)
		Fase.ALZADO:
			if _t >= ALZADO:
				_cambiar(Fase.AZOTA)
				_golpeo = false
				Sonido.efecto("raiz_azota", -2.0, global_position, 0.15)
		Fase.AZOTA:
			if not _golpeo:
				_golpear()
			if _t >= AZOTA:
				_cambiar(Fase.ARRIBA)
		Fase.ARRIBA:
			if _t >= ARRIBA:
				irse()
		Fase.HELADO:
			if _t >= HELADO:
				Sonido.efecto("hielo_romper", -4.0, global_position)
				irse()
	_sprite.visible = fase != Fase.AVISO
	_sprite.frame = {Fase.ASOMA: 0, Fase.ALZADO: 1, Fase.AZOTA: 2, Fase.ARRIBA: 1, Fase.HELADO: 3}.get(fase, 0)
	queue_redraw()


func _cambiar(f: Fase) -> void:
	fase = f
	_t = 0.0


## El azote: daña a Maisha si está a lo largo del tentáculo, sobre el muelle
func _golpear() -> void:
	_golpeo = true
	Impacto.temblar(2.0, 0.15)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var p := maisha.global_position - global_position
	var a_lo_largo := p.dot(fuera)
	var de_lado := absf(p.dot(Vector2(-fuera.y, fuera.x)))
	if a_lo_largo > -8.0 and a_lo_largo < LARGO and de_lado < ANCHO_GOLPE:
		maisha.call("recibir_danio", 1, global_position, "contacto")


func congelar() -> bool:
	if fase not in [Fase.ALZADO, Fase.ARRIBA, Fase.AZOTA]:
		return false
	_cambiar(Fase.HELADO)
	add_to_group("golpeables")
	Sonido.efecto("hielo_runa", 0.0, global_position)
	return true


func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	if fase != Fase.HELADO:
		return false
	Sonido.efecto("hielo_romper", 0.0, global_position)
	if pweza and is_instance_valid(pweza):
		pweza.tirar(self)
	irse()
	return true


func irse() -> void:
	if fase == Fase.FUERA:
		return
	_cambiar(Fase.FUERA)
	for g in ["tentaculos", "congelables", "golpeables"]:
		remove_from_group(g)
	se_fue.emit()
	var t := create_tween()
	t.tween_property(self, "modulate:a", 0.0, 0.3)
	t.tween_callback(queue_free)


func _draw() -> void:
	# las ondas donde va a salir (y alrededor de la base mientras está fuera)
	var dentro := -fuera * 14.0
	var col := Color(0.62, 0.52, 0.9, 0.6)
	if fase == Fase.AVISO:
		for k in 3:
			var r := fmod(_tiempo * 14.0 + k * 5.0, 15.0)
			draw_arc(dentro, 2.0 + r, 0, TAU, 18, Color(col, col.a * (1.0 - r / 15.0)), 1.0)
		return
	draw_arc(dentro, 7.0 + sin(_tiempo * 6.0), 0, TAU, 16, Color(col, 0.4), 1.0)
