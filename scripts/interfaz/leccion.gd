extends CanvasLayer
## LECCIÓN: enseña una acción como en otros juegos. Para el mundo, oscurece la pantalla salvo un círculo de luz sobre
## lo importante (Maisha y aquello sobre lo que hay que usar la acción), enseña la tecla grande latiendo y un texto,
## y no deja seguir hasta que se pulsa. Al pulsarla, el mundo vuelve a moverse y se hace la acción.
##   await leccion.ensenar("golpe", "J", "Pulsa J para golpear", [maisha, espantapajaros])
## Después se puede poner el tiempo a cámara lenta con un aviso («¡Sal de la cruz!») mientras haga falta:
##   await leccion.camara_lenta("¡Sal de la cruz!", func() -> bool: return ya_ha_salido)

signal pulsada

const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const PIEL := preload("res://scripts/interfaz/piel.gd")
const AMBAR := Color("e6a852")
const PERGAMINO := Color("efe6cf")
const TINTA := Color("3b2416")
const SOMBRA := """
shader_type canvas_item;
uniform vec2 foco1 = vec2(320.0, 180.0);
uniform vec2 foco2 = vec2(320.0, 180.0);
uniform float radio = 44.0;
uniform float fuerza = 0.0;
uniform vec2 tam = vec2(640.0, 360.0);
void fragment() {
	vec2 p = UV * tam;
	float d = min(distance(p, foco1), distance(p, foco2));
	float a = smoothstep(radio, radio + 30.0, d) * 0.72 * fuerza;
	COLOR = vec4(0.03, 0.02, 0.06, a);
}
"""

var activa := false
var accion := ""
var _tecla := ""
var _texto := ""
var _focos: Array = []
var _fuerza := 0.0
var _tiempo := 0.0
var _lenta := false
var _aviso_lento := ""
var _velo: ColorRect
var _lienzo: Control
var _ultimo := {}                 # dónde se vio por última vez cada cosa iluminada (por si desaparece)


func _ready() -> void:
	add_to_group("leccion")
	layer = 18
	process_mode = Node.PROCESS_MODE_ALWAYS
	_velo = ColorRect.new()
	_velo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_velo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var material := ShaderMaterial.new()
	var shader := Shader.new()
	shader.code = SOMBRA
	material.shader = shader
	_velo.material = material
	add_child(_velo)
	_lienzo = Control.new()
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.draw.connect(_dibujar)
	add_child(_lienzo)


## Para el mundo y espera a que se pulse la acción
func ensenar(accion_: String, tecla: String, texto: String, focos: Array) -> void:
	activa = true
	accion = accion_
	_tecla = tecla
	_texto = texto
	_focos = focos
	get_tree().paused = true
	Sonido.efecto("mision_nueva")
	await pulsada
	activa = false
	get_tree().paused = false
	await get_tree().create_timer(0.4, true).timeout
	if not activa:
		_focos = []
		_ultimo.clear()


## Cámara lenta, con un aviso, hasta que «sigue_haciendo_falta» diga que no (o pasen unos segundos)
func camara_lenta(aviso: String, sigue_haciendo_falta: Callable, maximo := 2.5) -> void:
	_lenta = true
	_aviso_lento = aviso
	Impacto.poner_lenta(0.35)
	var t := 0.0
	while t < maximo and is_inside_tree() and sigue_haciendo_falta.is_valid() and sigue_haciendo_falta.call():
		await get_tree().process_frame
		t += get_process_delta_time() / maxf(Engine.time_scale, 0.01)
	Impacto.poner_lenta(1.0)
	_lenta = false


## Si la lección desaparece a mitad de la cámara lenta, la velocidad vuelve a la normal
func _exit_tree() -> void:
	if _lenta:
		_lenta = false
		Impacto.poner_lenta(1.0)


func _process(delta: float) -> void:
	_tiempo += delta
	_fuerza = move_toward(_fuerza, 1.0 if activa else 0.0, delta * 4.0)
	if activa and _fuerza > 0.6 and Input.is_action_just_pressed(accion):
		pulsada.emit()
	# el círculo de luz sigue a lo importante
	var m := _velo.material as ShaderMaterial
	var p1 := _a_pantalla(_focos[0]) if _focos.size() > 0 else Vector2(320, 180)
	var p2 := _a_pantalla(_focos[1]) if _focos.size() > 1 else p1
	m.set_shader_parameter("foco1", p1)
	m.set_shader_parameter("foco2", p2)
	m.set_shader_parameter("radio", 40.0 + sin(_tiempo * 3.0) * 3.0)
	m.set_shader_parameter("fuerza", _fuerza)
	_lienzo.queue_redraw()


func _a_pantalla(n: Variant) -> Vector2:
	# (si lo iluminado ya no existe, p. ej. un Petrino que ha caído, la luz se queda donde estaba)
	if n == null or not is_instance_valid(n) or not (n is Node2D):
		return _ultimo.get(n, Vector2(320, 180)) if n != null else Vector2(320, 180)
	var camara := get_viewport().get_camera_2d()
	var p: Vector2 = (n as Node2D).global_position + Vector2(0, -12)
	if camara == null:
		_ultimo[n] = p
		return p
	var en_pantalla := (p - camara.get_screen_center_position()) * camara.zoom + Vector2(320, 180)
	_ultimo[n] = en_pantalla
	return en_pantalla


func _unhandled_input(evento: InputEvent) -> void:
	if activa and _fuerza > 0.6 and evento is InputEventMouseButton and evento.button_index == MOUSE_BUTTON_LEFT and evento.pressed:
		if evento.position.distance_to(Vector2(320, 260)) < 48.0:
			pulsada.emit()
			get_viewport().set_input_as_handled()


func _dibujar() -> void:
	var fuente: Font = FUENTE
	if _fuerza > 0.02:
		var a := _fuerza
		# la tecla con pulsación física simulada (press down) y doble onda expansiva
		var onda_pulso := 0.5 + 0.5 * sin(_tiempo * 6.0)
		var hundimiento := roundf(onda_pulso * 2.5)
		var centro := Vector2(320, 258 + hundimiento)
		var tam := Vector2(40, 38)
		var base_sombra := Rect2(Vector2(320, 262) - tam / 2.0, tam)
		_lienzo.draw_rect(base_sombra, Color(0.05, 0.03, 0.02, 0.85 * a))
		var caja := Rect2(centro - tam / 2.0, tam)
		PIEL.caja(_lienzo, caja, "pergamino", a, false)
		PIEL.esquinas_oro(_lienzo, caja, PIEL.ORO_BRILLO, a, 5.0)
		var ancho_l := fuente.get_string_size(_tecla, HORIZONTAL_ALIGNMENT_LEFT, -1, 22).x
		_lienzo.draw_string(fuente, centro + Vector2(-ancho_l / 2.0, 8), _tecla, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, Color(TINTA, a))
		# dos halos concéntricos que se abren alrededor de la tecla
		for k in 2:
			var f := fmod(_tiempo * 0.85 + float(k) * 0.5, 1.0)
			_lienzo.draw_arc(Vector2(320, 259), 22.0 + f * 20.0, 0, TAU, 32, Color(AMBAR, (1.0 - f) * 0.55 * a), 1.4)
		# el texto debajo en una tarjeta moderna translúcida con resorte
		var tw := fuente.get_string_size(_texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
		var dy_t := roundf((1.0 - a) * 8.0)
		var tcaja := Rect2(roundf(320.0 - tw / 2.0 - 16.0), 289 + dy_t, tw + 32.0, 26.0)
		PIEL.caja(_lienzo, tcaja, "terciopelo", 0.94 * a)
		PIEL.esquinas_oro(_lienzo, tcaja, PIEL.ORO, 0.85 * a, 4.0)
		_texto_sombra(_texto, Vector2(320, 306 + dy_t), 16, Color(PERGAMINO, a))
	if _lenta:
		var parpadeo := 0.7 + 0.3 * sin(_tiempo * 10.0)
		var aw := fuente.get_string_size(_aviso_lento, HORIZONTAL_ALIGNMENT_LEFT, -1, 18).x
		var acaja := Rect2(roundf(320.0 - aw / 2.0 - 16.0), 50, aw + 32.0, 28.0)
		PIEL.caja(_lienzo, acaja, "terciopelo", 0.94)
		PIEL.esquinas_oro(_lienzo, acaja, AMBAR, parpadeo, 5.0)
		_texto_sombra(_aviso_lento, Vector2(320, 70), 18, Color(AMBAR, parpadeo))


func _texto_sombra(texto: String, centro: Vector2, tam: int, color: Color) -> void:
	var fuente: Font = FUENTE
	var ancho := fuente.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x
	var p := centro + Vector2(-ancho / 2.0, 0)
	_lienzo.draw_string(fuente, p + Vector2(1, 1), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, Color(0, 0, 0, color.a * 0.8))
	_lienzo.draw_string(fuente, p, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, color)
