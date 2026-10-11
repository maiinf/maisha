extends Node2D
## ESCENA DEL MUNDO: lo que comparten todas las escenas jugables (regiones, la aldea, interiores).
##   - coloca a Maisha: en el inicio del mapa o junto a la puerta por la que llega
##   - la cámara, que sigue a Maisha sin salirse del mapa
##   - el cetro (solo desde que Mzee Shamba se lo da), y si se puede combatir (en la aldea y en las casas no)
##   - la pausa (Esc), la mochila (Tab) y el objetivo de la misión en pantalla
##   - el título al llegar
##   - le dice a Estado dónde estamos y guarda la partida al llegar

@export var titulo := ""
@export var combate := true
@export var color_fondo := Color("1d2e18")
@export var ayuda := "WASD mover · C correr · J golpe · K semilla · L latido"

## Música y ambiente de cada escena (por el nombre de su archivo)
const MUSICA_DE := {"kitovu": "kitovu", "prados_del_eco": "prados", "cuna_de_musgo": "aldea", "bosque_cobrizo": "bosque", "cienaga_quieta": "cienaga", "campo_segado": "campo", "sendero_del_puente": "sendero", "las_pasarelas": "pasarelas", "camino_cobrizo": "cobrizo", "senda_surcos": "surcos", "canada_eco": "cobrizo", "casa_shamba": "interior",
	"casa_pino": "interior", "taller_corteza": "interior", "claro_de_calma": "interior"}
## (los pájaros no se usan aquí: quedan guardados para un bioma de selva)
const AMBIENTE_DE := {
	"kitovu": {"brisa": 0.3, "viento": 0.55},
	"prados_del_eco": {"brisa": 0.65, "viento": 0.2},
	"cuna_de_musgo": {"brisa": 0.5},
	"bosque_cobrizo": {"viento": 0.45, "brisa": 0.4},
	"cienaga_quieta": {"cienaga": 0.7, "brisa": 0.2},
	"campo_segado": {"viento": 0.6, "brisa": 0.35},
	"sendero_del_puente": {"brisa": 0.55, "viento": 0.15},
	"las_pasarelas": {"cienaga": 0.35, "brisa": 0.4},
	"camino_cobrizo": {"viento": 0.3, "brisa": 0.5},
	"senda_surcos": {"brisa": 0.55, "viento": 0.25},
	"canada_eco": {"viento": 0.55, "brisa": 0.3},
	"casa_shamba": {"fuego": 0.75},
	"casa_pino": {"brisa": 0.15},
	"taller_corteza": {"fuego": 0.45},
	"claro_de_calma": {"brisa": 0.3},
}
const OIDO_AGUA := preload("res://scripts/mundo/oido_agua.gd")
const PAUSA := preload("res://scripts/interfaz/menu_pausa.gd")
const MOCHILA := preload("res://scripts/interfaz/mochila.gd")
const OBJETIVO := preload("res://scripts/interfaz/objetivo.gd")

@onready var _maisha: Node2D = $Entidades/Maisha
@onready var _hud: CanvasLayer = $HUD
var _region: Node2D
var _oido_agua: Node


func _ready() -> void:
	get_tree().paused = false            # por si se cambió de escena con algo en pausa (un narrador, un menú)
	RenderingServer.set_default_clear_color(color_fondo)
	_region = get_node_or_null("Region")
	_oido_agua = OIDO_AGUA.new()
	_oido_agua.name = "OidoAgua"
	add_child(_oido_agua)
	var pausa: CanvasLayer = PAUSA.new()
	pausa.name = "Pausa"
	add_child(pausa)
	var mochila: CanvasLayer = MOCHILA.new()
	mochila.name = "Mochila"
	add_child(mochila)
	var objetivo: CanvasLayer = OBJETIVO.new()
	objetivo.name = "Objetivo"
	add_child(objetivo)
	_preparar_cetro()
	Tienda.vestir(_maisha.get_node("Ropa"))
	Estado.marca_puesta.connect(_al_poner_marca)
	_hud.set("texto_ayuda", ayuda)
	var continuando: bool = Estado.posicion_carga != null
	_colocar_maisha()
	_crear_camara()
	Estado.jugando = true
	Estado.escena_actual = scene_file_path.get_file().get_basename()
	Estado.marcar("visto/" + Estado.escena_actual)
	_poner_sonido()
	Estado.lugar = titulo
	Estado.guardar.call_deferred()
	if Estado.llegada == "" or continuando:
		# empieza la partida aquí: aparece desde negro con el nombre del sitio
		_hud.despertar(titulo)
	elif titulo != "":
		_hud.mostrar_mensaje(titulo)
	Estado.llegada = ""


## La música y el ambiente de esta escena (el Kitovu lo cambia para el despertar)
func _poner_sonido() -> void:
	volver_a_su_musica()
	Sonido.ambiente(_ambiente_de_escena())


## Los ambientes de la escena y, si hay agua en el mapa, el del agua (que sube al acercarse)
func _ambiente_de_escena() -> Dictionary:
	var amb: Dictionary = AMBIENTE_DE.get(Estado.escena_actual, {}).duplicate()
	if _oido_agua and _oido_agua.hay_agua():
		amb["agua"] = 0.0
	return amb


## Tras una pelea o una fanfarria, vuelve la música de la escena
func volver_a_su_musica() -> void:
	Sonido.musica(MUSICA_DE.get(scene_file_path.get_file().get_basename(), ""), 2.0)


## Sin cetro no se lucha (ni se lleva el cetro en la mano)
func _preparar_cetro() -> void:
	var tiene := Estado.tiene("cetro_recibido")
	_maisha.set("combate_activo", combate and tiene)
	if tiene:
		_maisha.get_node("Ropa").poner("cetro_raiz")


func _al_poner_marca(marca: String) -> void:
	if marca == "cetro_recibido":
		_preparar_cetro()
		_destello_cetro()


## El momento de recibir el cetro: un destello de luz que crece sobre Maisha
var _luz_cetro: Node2D
var _radio_cetro := 0.0


func _destello_cetro() -> void:
	_luz_cetro = Node2D.new()
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_luz_cetro.material = suma
	_luz_cetro.z_index = 5
	_luz_cetro.draw.connect(_dibujar_destello_cetro)
	_maisha.add_child(_luz_cetro)
	var t := create_tween()
	t.tween_method(_crecer_destello_cetro, 0.0, 50.0, 1.2)
	t.tween_callback(_luz_cetro.queue_free)


func _crecer_destello_cetro(valor: float) -> void:
	_radio_cetro = valor
	if is_instance_valid(_luz_cetro):
		_luz_cetro.queue_redraw()


func _dibujar_destello_cetro() -> void:
	for i in 4:
		_luz_cetro.draw_circle(Vector2(0, -16), _radio_cetro * (1.0 + i * 0.5), Color(1.0, 0.95, 0.6, 0.12 * (1.0 - _radio_cetro / 50.0)))


func _colocar_maisha() -> void:
	if Estado.posicion_carga != null:
		# se continúa una partida guardada: Maisha aparece donde estaba
		_maisha.global_position = Estado.posicion_carga
		Estado.posicion_carga = null
		return
	if Estado.llegada != "":
		for puerta in get_tree().get_nodes_in_group("puertas"):
			if puerta.id == Estado.llegada:
				_maisha.global_position = puerta.punto_llegada()
				_maisha.call("mirar", puerta.salida)
				return
		push_warning("No hay ninguna puerta llamada «%s»; Maisha aparece en el inicio" % Estado.llegada)
	if _region:
		_maisha.global_position = _region.inicio


func _crear_camara() -> void:
	var camara := Camera2D.new()
	if _region:
		camara.limit_left = 0
		camara.limit_top = 0
		camara.limit_right = int(_region.tam.x)
		camara.limit_bottom = int(_region.tam.y)
	camara.position_smoothing_enabled = true
	camara.position_smoothing_speed = 6.0
	_maisha.add_child(camara)
	camara.reset_smoothing()
