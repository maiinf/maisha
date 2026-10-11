extends "res://scripts/mundo/interiores/interior_casa.gd"
## CASA DE MZEE SHAMBA, por dentro. En la pared, el Cetro de Raíz de su familia.
## La primera vez que entra Maisha, el brote de su cabeza brilla y el castor lo nota...
## pero no dice nada: solo se le escapa un susurro.
## Luego, la cena junto al fuego (sin tareas): anochece, Maisha se duerme y, a la mañana siguiente,
## el castor le pide ayuda con el huerto.

const FONDO := preload("res://arte/mundos/kitovu/interior_casa_shamba.png")
const CETRO := preload("res://arte/mundos/kitovu/cetro_pared.png")
const ALDEANO := preload("res://scripts/mundo/aldea/aldeano.gd")
const CHARLA := preload("res://scripts/mundo/charla.gd")
const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const NOCHE := Color(0.42, 0.38, 0.56)          # la casa de noche (el fuego sigue brillando)
const MANANA := Color(1.0, 0.9, 0.78)           # la luz de la mañana
const TEXTOS_NOCHE := ["Esa noche, junto al fuego, Maisha soñó con raíces de luz.", "A la mañana siguiente..."]

var _shamba: Node2D
var _cetro: Sprite2D
var _brillo := 0.0
var _luz: CanvasModulate
var _noche := 0.0                 # 0 = de día, 1 = de noche (el fuego brilla más)


func _fondo() -> Texture2D:
	return FONDO


func _muebles() -> Array[Rect2]:
	return [
		Rect2(40, 40, 46, 36),      # chimenea
		Rect2(118, 104, 60, 26),    # mesa
		Rect2(102, 118, 12, 8),     # taburete
		Rect2(182, 118, 12, 8),     # taburete
		Rect2(248, 66, 40, 48),     # cama
		Rect2(34, 148, 20, 22),     # saco de semillas
	]


func _cosas() -> Array:
	return [
		["casa_shamba_chimenea", Vector2(62, 92), 24.0, 30.0],
		["casa_shamba_tarros", Vector2(225, 82), 22.0, 26.0],
		["casa_shamba_cetro", Vector2(160, 84), 22.0, 28.0],
		["casa_shamba_cama", Vector2(268, 122), 22.0, 22.0],
	]


func _preparar() -> void:
	_cetro = Sprite2D.new()
	_cetro.texture = CETRO
	_cetro.centered = false
	_cetro.position = Vector2(149, 29)
	_cetro.z_index = -5
	_cetro.visible = not Estado.tiene("cetro_recibido")
	add_child(_cetro)
	_shamba = ALDEANO.new()
	_shamba.id = "shamba"
	_shamba.position = Vector2(214, 136)
	$Entidades.add_child(_shamba)


func _ready() -> void:
	super()
	_luz = CanvasModulate.new()
	_luz.color = Color.WHITE
	add_child(_luz)
	if not Estado.tiene("shamba_noto"):
		_nota_algo.call_deferred()
	elif Estado.tiene("cena_shamba") and not Estado.tiene("amanecer_granja"):
		_pasar_la_noche.call_deferred()            # se cerró el juego a media cena: se sigue


func _al_poner_marca(marca: String) -> void:
	super(marca)
	if marca == "cena_shamba":
		_pasar_la_noche.call_deferred()
	if marca == "cetro_recibido":
		# el castor descuelga el cetro de la pared
		var t := create_tween()
		t.tween_property(_cetro, "modulate:a", 0.0, 0.5)
		t.tween_callback(func() -> void: _cetro.visible = false)


## Al entrar por primera vez: el brote de Maisha brilla y el castor se queda mirando
func _nota_algo() -> void:
	_maisha.set("puede_actuar", false)
	await get_tree().create_timer(0.9).timeout
	_brillo = 1.0
	var t := create_tween()
	t.tween_property(_shamba, "position:y", _shamba.position.y - 5.0, 0.1)
	t.tween_property(_shamba, "position:y", _shamba.position.y, 0.15)
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	dialogo.susurrar(_shamba, "(...¿Ese brillo? No puede ser...)", 3.2)
	await get_tree().create_timer(3.0).timeout
	Estado.marcar("shamba_noto")
	await CHARLA.hablar(_shamba, "shamba")


## La cena, la noche y el amanecer (el castor no pide nada hasta la mañana siguiente)
func _pasar_la_noche() -> void:
	# esperar a que acabe la conversación
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	while dialogo.hablando:
		await get_tree().process_frame
	_maisha.set("puede_actuar", false)
	Sonido.musica("noche", 3.0)
	var t := create_tween().set_parallel(true)
	t.tween_property(_luz, "color", NOCHE, 3.0)
	t.tween_property(self, "_noche", 1.0, 3.0)
	await get_tree().create_timer(1.5).timeout
	Sonido.efecto("sopa")
	await dialogo.decir("Maisha", ["La sopa de zanahoria está caliente.", "Hacía... no sé cuánto que no comía nada.",
		"El fuego cruje. Se me cierran los ojos..."], "pensamiento")
	_maisha.set("puede_actuar", false)
	dialogo.susurrar(_shamba, "(Duerme, pequeño brote. Mañana será otro día.)", 3.5)
	await get_tree().create_timer(3.0).timeout
	await _fundido_con_textos()
	# a la mañana siguiente: Maisha junto a la cama y la luz entrando por la ventana
	Estado.marcar("amanecer_granja")
	_maisha.position = Vector2(258, 150)
	_maisha.call("mirar", Vector2.LEFT)
	_luz.color = MANANA
	_noche = 0.0
	Sonido.musica("interior", 2.0)
	Sonido.fanfarria("amanece")
	await _quitar_fundido()
	create_tween().tween_property(_luz, "color", Color.WHITE, 12.0)
	await get_tree().create_timer(0.8).timeout
	await CHARLA.hablar(_shamba, "shamba")
	_maisha.set("puede_actuar", true)


var _negro: CanvasLayer
var _negro_alfa := 0.0
var _negro_texto := ""
var _negro_texto_alfa := 0.0


func _fundido_con_textos() -> void:
	_negro = CanvasLayer.new()
	_negro.layer = 40
	var lienzo := Control.new()
	lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	lienzo.draw.connect(_dibujar_negro.bind(lienzo))
	_negro.add_child(lienzo)
	add_child(_negro)
	var t := create_tween()
	t.tween_property(self, "_negro_alfa", 1.0, 2.0)
	await t.finished
	for texto in TEXTOS_NOCHE:
		_negro_texto = texto
		var u := create_tween()
		u.tween_property(self, "_negro_texto_alfa", 1.0, 0.8)
		u.tween_interval(2.4)
		u.tween_property(self, "_negro_texto_alfa", 0.0, 0.8)
		await u.finished


func _quitar_fundido() -> void:
	var t := create_tween()
	t.tween_property(self, "_negro_alfa", 0.0, 2.0)
	await t.finished
	_negro.queue_free()
	_negro = null


func _dibujar_negro(lienzo: Control) -> void:
	lienzo.draw_rect(Rect2(0, 0, 640, 360), Color(0.03, 0.02, 0.05, _negro_alfa))
	if _negro_texto != "" and _negro_texto_alfa > 0.0:
		var ancho := FUENTE.get_string_size(_negro_texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		lienzo.draw_string(FUENTE, Vector2(round(320 - ancho / 2.0), 184), _negro_texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(1.0, 0.95, 0.77, _negro_texto_alfa))


func _process(delta: float) -> void:
	if _negro:
		(_negro.get_child(0) as Control).queue_redraw()
	super(delta)
	_brillo = maxf(0.0, _brillo - delta * 0.5)


func _dibujar_luces() -> void:
	super()
	# la chimenea
	var temblor := 0.8 + 0.2 * sin(_tiempo * 8.0) * sin(_tiempo * 3.1)
	for i in 4:
		_luces.draw_circle(Vector2(62, 64), (10.0 + i * 9.0) * temblor * (1.0 + _noche * 0.6), Color(1.0, 0.6, 0.25, 0.05 + 0.07 * _noche))
	# el brote de Maisha cuando brilla
	if _brillo > 0.0 and is_instance_valid(_maisha):
		var cabeza := _maisha.position + Vector2(0, -30)
		for i in 4:
			_luces.draw_circle(cabeza, 4.0 + i * 6.0 + (1.0 - _brillo) * 10.0, Color(0.45, 0.95, 0.4, 0.12 * _brillo))
	# el cetro en su soporte late muy despacio, esperando
	if _cetro.visible:
		var p := 0.5 + 0.5 * sin(_tiempo * 1.2)
		_luces.draw_circle(Vector2(160, 36), 6.0 + p * 4.0, Color(0.45, 0.95, 0.4, 0.06 + 0.04 * p))
