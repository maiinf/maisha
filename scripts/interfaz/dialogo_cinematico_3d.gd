extends CanvasLayer
## DIÁLOGO CINEMÁTICO EN TIEMPO REAL 3D (ESTILO GOD OF WAR / ZELDA TOTK)
## Subtítulos limpios y editoriales en la parte inferior, encuadre sobre el hombro
## y avance con [E] o [Espacio] sin pausar bruscamente el mundo.

signal dialogo_iniciado
signal dialogo_terminado

var hablando := false
var _lineas: Array[String] = []
var _indice_linea := 0
var _nombre_hablante := ""
var _camara_3p: Node3D = null
var _maisha: CharacterBody3D = null

# Nodos de UI
var _contenedor_dialogo: Control = null
var _label_nombre: Label = null
var _label_texto: Label = null
var _label_indicador: Label = null
var _prompt_interactuar: Control = null


func _ready() -> void:
	layer = 10
	_crear_interfaz_cinematica()


func _unhandled_input(event: InputEvent) -> void:
	if not hablando:
		return

	if event.is_action_pressed("ui_accept") or (event is InputEventKey and event.keycode == KEY_E and event.pressed):
		_avanzar_dialogo()


func iniciar_dialogo(nombre: String, lineas: Array[String], camara: Node3D = null, maisha: CharacterBody3D = null) -> void:
	if hablando or lineas.is_empty():
		return

	hablando = true
	_nombre_hablante = nombre
	_lineas = lineas
	_indice_linea = 0
	_camara_3p = camara
	_maisha = maisha

	if _maisha:
		_maisha.puede_moverse = false

	_label_nombre.text = _nombre_hablante.to_upper()
	_mostrar_linea_actual()

	_contenedor_dialogo.visible = true
	_contenedor_dialogo.modulate.a = 0.0
	var tween := create_tween()
	tween.tween_property(_contenedor_dialogo, "modulate:a", 1.0, 0.25)

	emit_signal("dialogo_iniciado")


func _avanzar_dialogo() -> void:
	_indice_linea += 1
	if _indice_linea < _lineas.size():
		_mostrar_linea_actual()
	else:
		_cerrar_dialogo()


func _mostrar_linea_actual() -> void:
	_label_texto.text = _lineas[_indice_linea]
	_label_texto.visible_ratio = 0.0

	var duracion_texto := clampf(_label_texto.text.length() * 0.022, 0.35, 1.4)
	var tween := create_tween()
	tween.tween_property(_label_texto, "visible_ratio", 1.0, duracion_texto)


func _cerrar_dialogo() -> void:
	var tween := create_tween()
	tween.tween_property(_contenedor_dialogo, "modulate:a", 0.0, 0.2)
	tween.tween_callback(func():
		_contenedor_dialogo.visible = false
		hablando = false
		if _maisha:
			_maisha.puede_moverse = true
		emit_signal("dialogo_terminado")
	)


func mostrar_prompt(texto: String = "[E] Hablar") -> void:
	if hablando:
		return
	if _prompt_interactuar:
		_prompt_interactuar.visible = true
		var lbl: Label = _prompt_interactuar.get_node_or_null("LabelPrompt")
		if lbl:
			lbl.text = texto


func ocultar_prompt() -> void:
	if _prompt_interactuar:
		_prompt_interactuar.visible = false


func _crear_interfaz_cinematica() -> void:
	# Contenedor raíz a pantalla completa
	var raiz := Control.new()
	raiz.name = "RaizDialogo"
	raiz.set_anchors_preset(Control.PRESET_FULL_RECT)
	raiz.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(raiz)

	# 1. Prompt flotante central de interactuar
	_prompt_interactuar = Control.new()
	_prompt_interactuar.name = "PromptInteractuar"
	_prompt_interactuar.set_anchors_preset(Control.PRESET_CENTER)
	_prompt_interactuar.position.y += 120.0
	_prompt_interactuar.visible = false
	raiz.add_child(_prompt_interactuar)

	var fondo_prompt := PanelContainer.new()
	var style_p := StyleBoxFlat.new()
	style_p.bg_color = Color(0.08, 0.09, 0.12, 0.75)
	style_p.border_color = Color(0.85, 0.72, 0.40, 0.6)
	style_p.set_border_width_all(1)
	style_p.set_corner_radius_all(4)
	style_p.set_content_margin_all(8)
	fondo_prompt.add_theme_stylebox_override("panel", style_p)
	_prompt_interactuar.add_child(fondo_prompt)

	var lbl_p := Label.new()
	lbl_p.name = "LabelPrompt"
	lbl_p.text = "[E] Hablar"
	lbl_p.add_theme_color_override("font_color", Color(1.0, 0.92, 0.75))
	lbl_p.add_theme_font_size_override("font_size", 14)
	fondo_prompt.add_child(lbl_p)

	# 2. Contenedor de subtítulos cinematográficos abajo
	_contenedor_dialogo = Control.new()
	_contenedor_dialogo.name = "ContenedorSubtitulos"
	_contenedor_dialogo.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_contenedor_dialogo.custom_minimum_size = Vector2(0, 160)
	_contenedor_dialogo.visible = false
	raiz.add_child(_contenedor_dialogo)

	# Fondo degradado cinemático muy sutil
	var degradado := ColorRect.new()
	degradado.set_anchors_preset(Control.PRESET_FULL_RECT)
	degradado.color = Color(0.04, 0.05, 0.07, 0.65)
	_contenedor_dialogo.add_child(degradado)

	var margen := MarginContainer.new()
	margen.set_anchors_preset(Control.PRESET_FULL_RECT)
	margen.add_theme_constant_override("margin_left", 80)
	margen.add_theme_constant_override("margin_right", 80)
	margen.add_theme_constant_override("margin_top", 16)
	margen.add_theme_constant_override("margin_bottom", 20)
	_contenedor_dialogo.add_child(margen)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 6)
	margen.add_child(vbox)

	# Nombre del personaje en oro pálido
	_label_nombre = Label.new()
	_label_nombre.text = "MZEE SHAMBA"
	_label_nombre.add_theme_color_override("font_color", Color(0.95, 0.82, 0.48))
	_label_nombre.add_theme_font_size_override("font_size", 15)
	vbox.add_child(_label_nombre)

	# Texto editorial de subtítulos
	_label_texto = Label.new()
	_label_texto.text = "Texto de diálogo cinematográfico..."
	_label_texto.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_label_texto.add_theme_color_override("font_color", Color(0.96, 0.94, 0.90))
	_label_texto.add_theme_font_size_override("font_size", 17)
	vbox.add_child(_label_texto)

	# Indicador de continuación
	_label_indicador = Label.new()
	_label_indicador.text = "[E / Espacio para continuar]"
	_label_indicador.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_label_indicador.add_theme_color_override("font_color", Color(0.65, 0.68, 0.72, 0.75))
	_label_indicador.add_theme_font_size_override("font_size", 12)
	vbox.add_child(_label_indicador)
