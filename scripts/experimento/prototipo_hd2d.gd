extends Node3D
## PROTOTIPO EXPERIMENTAL HD-2D / 2.5D INTERACTIVO
## Demostración jugable de exploración, diálogo y combate en espacio 3D real:
## - Maisha con animaciones 2D y sombras 3D dinámicas
## - Aldeano interactivo (Pino) con diálogo y retrato
## - Combate HD-2D: Golpe de cetro (J) y Semilla explosiva (K) con físicas y partículas 3D
## - Enemigo de prueba (Petrino de Giza) reactivo a impactos
## - Terreno con desniveles, río hundido con agua y puente de madera
## - Música ambiental de Raíz ("Raíces dormidas") y efectos de sonido originales
## - Tecla [3]: Alternar en vivo entre Vista HD-2D (Profundidad) y Vista Plana 2D
## - Tecla [1]: Ciclo de Iluminación (Atardecer Dorado / Noche con Faroles / Día Claro)

const PIXEL_SCALE := 0.038

# Texturas de Maisha
var _texturas_andar := {}
var _texturas_reposo := {}
var _texturas_correr := {}

# Nodos principales
var _maisha: CharacterBody3D
var _sprite_maisha: Sprite3D
var _camara: Camera3D
var _sol: DirectionalLight3D
var _env: WorldEnvironment
var _faroles: Array[OmniLight3D] = []
var _etiqueta_info: Label
var _caja_dialogo: Control
var _texto_dialogo: Label
var _icono_retrato: TextureRect
var _sonido: Node = null

# Estado de movimiento y animación
var _mirando := "abajo"
var _tiempo_anim := 0.0
var _esta_corriendo := false
var _modo_hd2d := true
var _hora_indice := 0
var _dialogando := false

# Aldeano Pino
var _nodo_pino: Node3D
var _sprite_pino: Sprite3D
var _tiempo_pino := 0.0
var _bocadillo_pino: Sprite3D

# Petrino (enemigo de prueba)
var _nodo_petrino: CharacterBody3D
var _sprite_petrino: Sprite3D
var _vida_petrino := 3
var _empuje_petrino := Vector3.ZERO

# Materiales para el terreno
var _mat_hierba: StandardMaterial3D
var _mat_camino: StandardMaterial3D
var _mat_piedra: StandardMaterial3D
var _mat_madera: StandardMaterial3D
var _mat_agua: StandardMaterial3D


func _ready() -> void:
	_cargar_texturas_maisha()
	_crear_materiales()
	_construir_entorno_3d()
	_construir_maisha()
	_construir_pino()
	_construir_petrino()
	_construir_camara_e_iluminacion()
	_construir_interfaz_ayuda()
	_construir_interfaz_dialogo()
	_aplicar_modo_iluminacion(0)

	_sonido = get_node_or_null("/root/Sonido")
	if _sonido and _sonido.has_method("musica") and _sonido.get("_reproductores") != null and _sonido.get("_reproductores").size() > 0:
		_sonido.call("musica", "kitovu")


func _cargar_texturas_maisha() -> void:
	var rutas := {
		"abajo": "res://arte/personajes/maisha/maisha_andar_abajo.png",
		"arriba": "res://arte/personajes/maisha/maisha_andar_arriba.png",
		"lado": "res://arte/personajes/maisha/maisha_andar_lado.png"
	}
	for dir in rutas:
		if ResourceLoader.exists(rutas[dir]):
			_texturas_andar[dir] = load(rutas[dir])
	var rutas_rep := {
		"abajo": "res://arte/personajes/maisha/maisha_reposo_abajo.png",
		"arriba": "res://arte/personajes/maisha/maisha_reposo_arriba.png",
		"lado": "res://arte/personajes/maisha/maisha_reposo_lado.png"
	}
	for dir in rutas_rep:
		if ResourceLoader.exists(rutas_rep[dir]):
			_texturas_reposo[dir] = load(rutas_rep[dir])
	var rutas_corr := {
		"abajo": "res://arte/personajes/maisha/maisha_correr_abajo.png",
		"arriba": "res://arte/personajes/maisha/maisha_correr_arriba.png",
		"lado": "res://arte/personajes/maisha/maisha_correr_lado.png"
	}
	for dir in rutas_corr:
		if ResourceLoader.exists(rutas_corr[dir]):
			_texturas_correr[dir] = load(rutas_corr[dir])


func _crear_materiales() -> void:
	_mat_hierba = StandardMaterial3D.new()
	_mat_hierba.albedo_color = Color("4b7437")
	_mat_hierba.roughness = 0.9

	_mat_camino = StandardMaterial3D.new()
	_mat_camino.albedo_color = Color("9c8053")
	_mat_camino.roughness = 0.85

	_mat_piedra = StandardMaterial3D.new()
	_mat_piedra.albedo_color = Color("5b5853")
	_mat_piedra.roughness = 0.75

	_mat_madera = StandardMaterial3D.new()
	_mat_madera.albedo_color = Color("68472f")
	_mat_madera.roughness = 0.8

	_mat_agua = StandardMaterial3D.new()
	_mat_agua.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_mat_agua.albedo_color = Color(0.18, 0.52, 0.65, 0.72)
	_mat_agua.roughness = 0.08
	_mat_agua.metallic = 0.15


func _construir_entorno_3d() -> void:
	var raiz_mundo := Node3D.new()
	raiz_mundo.name = "TerrenoYObjetos"
	add_child(raiz_mundo)

	# 1. Llanura base izquierda (hierba)
	_crear_bloque(raiz_mundo, Vector3(-5.5, -0.5, 0), Vector3(11.0, 1.0, 16.0), _mat_hierba, true)

	# 2. Llanura base derecha (hierba)
	_crear_bloque(raiz_mundo, Vector3(7.5, -0.5, 0), Vector3(9.0, 1.0, 16.0), _mat_hierba, true)

	# 3. Lecho del río hundido (entre x = 0 y x = 3, y = -0.6)
	_crear_bloque(raiz_mundo, Vector3(1.5, -1.2, 0), Vector3(3.4, 1.0, 16.0), _mat_piedra, true)

	# Lámina de agua
	var agua := MeshInstance3D.new()
	var malla_agua := PlaneMesh.new()
	malla_agua.size = Vector2(3.4, 16.0)
	agua.mesh = malla_agua
	agua.material_override = _mat_agua
	agua.position = Vector3(1.5, -0.42, 0)
	raiz_mundo.add_child(agua)

	# 4. Camino de tierra hacia el puente
	_crear_bloque(raiz_mundo, Vector3(-4.0, 0.01, 0.0), Vector3(8.0, 0.04, 2.2), _mat_camino, false)
	_crear_bloque(raiz_mundo, Vector3(5.5, 0.01, 0.0), Vector3(5.0, 0.04, 2.2), _mat_camino, false)

	# 5. Puente de madera
	_crear_bloque(raiz_mundo, Vector3(1.5, 0.08, 0.0), Vector3(3.6, 0.18, 2.4), _mat_madera, true)
	_crear_bloque(raiz_mundo, Vector3(1.5, 0.45, -1.2), Vector3(3.6, 0.6, 0.1), _mat_madera, true)
	_crear_bloque(raiz_mundo, Vector3(1.5, 0.45, 1.2), Vector3(3.6, 0.6, 0.1), _mat_madera, true)

	# 6. Terraza elevada (+1.2m)
	_crear_bloque(raiz_mundo, Vector3(-6.5, 0.6, -4.5), Vector3(7.0, 1.2, 5.0), _mat_hierba, true)
	_crear_bloque(raiz_mundo, Vector3(-6.5, 0.5, -1.95), Vector3(7.0, 1.0, 0.1), _mat_piedra, false)
	_crear_rampa(raiz_mundo, Vector3(-2.2, 0.55, -4.5), Vector3(1.6, 1.2, 2.2), _mat_camino)

	# 7. Props en billboard 3D con sombras
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/aldea/casa_seta.png", Vector3(-4.8, 0.0, -2.8), 0.9)
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/aldea/gran_arbol.png", Vector3(-6.8, 1.2, -6.0), 1.0)
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/objetos/arbol_a.png", Vector3(-8.8, 0.0, 0.5), 1.1)
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/objetos/arbol_b.png", Vector3(6.5, 0.0, -3.5), 1.15)
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/objetos/arbol_a.png", Vector3(8.0, 0.0, 2.5), 1.1)
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/objetos/arbol_b.png", Vector3(3.8, 0.0, 4.2), 1.35)

	# Farolillos
	_crear_farol(raiz_mundo, Vector3(-0.5, 0.0, -1.5))
	_crear_farol(raiz_mundo, Vector3(3.5, 0.0, 1.5))
	_crear_farol(raiz_mundo, Vector3(-2.8, 0.0, -1.2))

	# Estatua de Corteza
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/aldea/estatua_corteza.png", Vector3(-1.8, 0.0, 1.6), 1.0)


func _crear_bloque(padre: Node, pos: Vector3, tam: Vector3, mat: Material, colision: bool) -> void:
	var mi := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = tam
	mi.mesh = box
	mi.material_override = mat
	mi.position = pos
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	padre.add_child(mi)
	if colision:
		var sb := StaticBody3D.new()
		sb.position = pos
		var cs := CollisionShape3D.new()
		var forma := BoxShape3D.new()
		forma.size = tam
		cs.shape = forma
		sb.add_child(cs)
		padre.add_child(sb)


func _crear_rampa(padre: Node, pos: Vector3, tam: Vector3, mat: Material) -> void:
	var mi := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = tam
	mi.mesh = box
	mi.material_override = mat
	mi.position = pos
	mi.rotation_degrees.x = 22.0
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	padre.add_child(mi)
	var sb := StaticBody3D.new()
	sb.position = pos
	sb.rotation_degrees.x = 22.0
	var cs := CollisionShape3D.new()
	var forma := BoxShape3D.new()
	forma.size = tam
	cs.shape = forma
	sb.add_child(cs)
	padre.add_child(sb)


func _crear_prop_sprite(padre: Node, ruta: String, pos: Vector3, escala := 1.0) -> Sprite3D:
	if not ResourceLoader.exists(ruta):
		return null
	var sp := Sprite3D.new()
	sp.texture = load(ruta)
	sp.pixel_size = PIXEL_SCALE * escala
	sp.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	sp.alpha_cut = Sprite3D.ALPHA_CUT_DISCARD
	sp.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	sp.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	sp.centered = false
	var ancho_px := sp.texture.get_width()
	sp.offset = Vector2(-ancho_px / 2.0, 0)
	sp.position = pos
	padre.add_child(sp)
	return sp


func _crear_farol(padre: Node, pos: Vector3) -> void:
	_crear_bloque(padre, pos + Vector3(0, 0.8, 0), Vector3(0.08, 1.6, 0.08), _mat_madera, false)
	_crear_prop_sprite(padre, "res://arte/mundos/raiz/aldea/farol.png", pos + Vector3(0, 1.3, 0), 0.9)
	var luz := OmniLight3D.new()
	luz.position = pos + Vector3(0, 1.45, 0)
	luz.light_color = Color("ffa538")
	luz.light_energy = 2.2
	luz.omni_range = 4.5
	luz.omni_attenuation = 1.3
	luz.shadow_enabled = true
	padre.add_child(luz)
	_faroles.append(luz)


func _construir_maisha() -> void:
	_maisha = CharacterBody3D.new()
	_maisha.name = "Maisha"
	_maisha.position = Vector3(-1.0, 0.1, 0.0)
	add_child(_maisha)

	var cs := CollisionShape3D.new()
	var col_cilindro := CylinderShape3D.new()
	col_cilindro.height = 1.2
	col_cilindro.radius = 0.35
	cs.shape = col_cilindro
	cs.position = Vector3(0, 0.6, 0)
	_maisha.add_child(cs)

	_sprite_maisha = Sprite3D.new()
	_sprite_maisha.pixel_size = PIXEL_SCALE
	_sprite_maisha.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	_sprite_maisha.alpha_cut = Sprite3D.ALPHA_CUT_DISCARD
	_sprite_maisha.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	_sprite_maisha.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	_sprite_maisha.hframes = 4
	_sprite_maisha.centered = false
	_sprite_maisha.offset = Vector2(-12.0, 0.0)
	_sprite_maisha.texture = _texturas_reposo.get("abajo")
	_maisha.add_child(_sprite_maisha)


func _construir_pino() -> void:
	_nodo_pino = Node3D.new()
	_nodo_pino.name = "PinoAldeano"
	_nodo_pino.position = Vector3(-3.5, 0.0, -1.8)
	add_child(_nodo_pino)

	_sprite_pino = Sprite3D.new()
	_sprite_pino.pixel_size = PIXEL_SCALE
	_sprite_pino.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	_sprite_pino.alpha_cut = Sprite3D.ALPHA_CUT_DISCARD
	_sprite_pino.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	_sprite_pino.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	_sprite_pino.hframes = 4
	_sprite_pino.centered = false
	_sprite_pino.offset = Vector2(-12.0, 0.0)
	var ruta_anim := "res://arte/personajes/aldeanos/pino_anim.png"
	if ResourceLoader.exists(ruta_anim):
		_sprite_pino.texture = load(ruta_anim)
	_nodo_pino.add_child(_sprite_pino)

	# Bocadillo flotante sobre Pino para invitar al diálogo
	_bocadillo_pino = Sprite3D.new()
	_bocadillo_pino.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_bocadillo_pino.pixel_size = PIXEL_SCALE * 0.9
	_bocadillo_pino.position = Vector3(0, 1.45, 0)
	_bocadillo_pino.visible = false
	_nodo_pino.add_child(_bocadillo_pino)


func _construir_petrino() -> void:
	_nodo_petrino = CharacterBody3D.new()
	_nodo_petrino.name = "PetrinoEnemigo"
	_nodo_petrino.position = Vector3(4.8, 0.1, 0.0)
	add_child(_nodo_petrino)

	var cs := CollisionShape3D.new()
	var esfe := SphereShape3D.new()
	esfe.radius = 0.4
	cs.shape = esfe
	cs.position = Vector3(0, 0.4, 0)
	_nodo_petrino.add_child(cs)

	_sprite_petrino = Sprite3D.new()
	_sprite_petrino.pixel_size = PIXEL_SCALE
	_sprite_petrino.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	_sprite_petrino.alpha_cut = Sprite3D.ALPHA_CUT_DISCARD
	_sprite_petrino.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	_sprite_petrino.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	_sprite_petrino.centered = false
	var ruta := "res://arte/zonas/raiz/petrino.png"
	if ResourceLoader.exists(ruta):
		_sprite_petrino.texture = load(ruta)
		_sprite_petrino.offset = Vector2(-_sprite_petrino.texture.get_width() / 2.0, 0)
	_nodo_petrino.add_child(_sprite_petrino)


func _construir_camara_e_iluminacion() -> void:
	_camara = Camera3D.new()
	_camara.name = "CamaraCinematica"
	_camara.fov = 34.0
	_camara.rotation_degrees = Vector3(-32.0, 0.0, 0.0)
	_camara.position = _maisha.position + Vector3(0, 5.2, 7.5)
	_camara.current = true
	add_child(_camara)

	_sol = DirectionalLight3D.new()
	_sol.name = "SolDorado"
	_sol.shadow_enabled = true
	_sol.shadow_bias = 0.02
	_sol.shadow_blur = 1.4
	add_child(_sol)

	_env = WorldEnvironment.new()
	_env.name = "WorldEnvironment"
	var medio := Environment.new()
	medio.background_mode = Environment.BG_COLOR
	medio.background_color = Color("5c789a")
	medio.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	medio.ambient_light_color = Color("a8a096")
	medio.ambient_light_energy = 0.45
	medio.tonemap_mode = Environment.TONE_MAPPER_ACES
	medio.tonemap_exposure = 1.05
	medio.glow_enabled = true
	medio.glow_intensity = 0.7
	medio.glow_bloom = 0.2
	medio.glow_blend_mode = Environment.GLOW_BLEND_MODE_SOFTLIGHT
	medio.fog_enabled = true
	medio.fog_light_color = Color("d4aa78")
	medio.fog_density = 0.015
	medio.fog_aerial_perspective = 0.3
	_env.environment = medio
	add_child(_env)


func _construir_interfaz_ayuda() -> void:
	var canvas := CanvasLayer.new()
	canvas.layer = 5
	add_child(canvas)

	var fondo_ui := ColorRect.new()
	fondo_ui.color = Color(0.04, 0.03, 0.07, 0.8)
	fondo_ui.custom_minimum_size = Vector2(640, 54)
	fondo_ui.set_anchors_preset(Control.PRESET_TOP_WIDE)
	canvas.add_child(fondo_ui)

	_etiqueta_info = Label.new()
	_etiqueta_info.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_etiqueta_info.offset_left = 12
	_etiqueta_info.offset_top = 6
	_etiqueta_info.offset_right = -12
	_etiqueta_info.text = "PROTOTIPO HD-2D: WASD: Mover · Shift/C: Correr · Espacio: Saltar · [J] Golpe Cetro · [K] Semilla · [E] Hablar\n[3] Alternar Vista (HD-2D vs 2D Plana) | [1] Iluminación (Atardecer/Noche/Día)"
	_etiqueta_info.add_theme_color_override("font_color", Color("fdf6e2"))
	canvas.add_child(_etiqueta_info)


func _construir_interfaz_dialogo() -> void:
	var canvas := CanvasLayer.new()
	canvas.layer = 10
	add_child(canvas)

	_caja_dialogo = Control.new()
	_caja_dialogo.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_caja_dialogo.offset_top = -90.0
	_caja_dialogo.offset_bottom = 0.0
	_caja_dialogo.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_caja_dialogo.visible = false
	canvas.add_child(_caja_dialogo)

	var fondo := ColorRect.new()
	fondo.set_anchors_preset(Control.PRESET_FULL_RECT)
	fondo.color = Color(0.06, 0.05, 0.09, 0.9)
	_caja_dialogo.add_child(fondo)

	var marco := ReferenceRect.new()
	marco.set_anchors_preset(Control.PRESET_FULL_RECT)
	marco.border_color = Color("e09c5a")
	marco.border_width = 2.0
	marco.editor_only = false
	_caja_dialogo.add_child(marco)

	_icono_retrato = TextureRect.new()
	_icono_retrato.position = Vector2(16, 12)
	_icono_retrato.custom_minimum_size = Vector2(48, 64)
	_icono_retrato.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	var ruta_pino := "res://arte/personajes/aldeanos/pino_frente.png"
	if ResourceLoader.exists(ruta_pino):
		_icono_retrato.texture = load(ruta_pino)
	_caja_dialogo.add_child(_icono_retrato)

	_texto_dialogo = Label.new()
	_texto_dialogo.position = Vector2(76, 16)
	_texto_dialogo.size = Vector2(540, 60)
	_texto_dialogo.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_texto_dialogo.text = "Pino: ¡Maisha! Mira cómo se proyectan las sombras ahora con el sol bajo... ¡Casi parece que el bosque tiene relieve de verdad! Pulsa [J] para usar el cetro o [K] para plantar una semilla."
	_texto_dialogo.add_theme_color_override("font_color", Color("fff4dd"))
	_caja_dialogo.add_child(_texto_dialogo)


func _physics_process(delta: float) -> void:
	if not _dialogando:
		_actualizar_controles_maisha(delta)
	_actualizar_camara(delta)
	_actualizar_pino(delta)
	_actualizar_petrino(delta)
	_parpadear_faroles(delta)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_3:
			_alternar_modo_vista()
		elif event.keycode == KEY_1:
			_hora_indice = (_hora_indice + 1) % 3
			_aplicar_modo_iluminacion(_hora_indice)
		elif event.keycode == KEY_E:
			_interactuar()
		elif event.keycode == KEY_J and not _dialogando:
			_ejecutar_golpe_cetro()
		elif event.keycode == KEY_K and not _dialogando:
			_plantar_semilla()
		elif event.keycode == KEY_ESCAPE:
			if _dialogando:
				_cerrar_dialogo()
			else:
				get_tree().change_scene_to_file("res://escenas/interfaz/inicio.tscn")


func _actualizar_controles_maisha(delta: float) -> void:
	var entrada := Vector2.ZERO
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT):
		entrada.x -= 1.0
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT):
		entrada.x += 1.0
	if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP):
		entrada.y -= 1.0
	if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN):
		entrada.y += 1.0
	entrada = entrada.normalized()

	_esta_corriendo = Input.is_key_pressed(KEY_SHIFT) or Input.is_key_pressed(KEY_C)
	var velocidad := 6.5 if _esta_corriendo else 3.8

	if not _maisha.is_on_floor():
		_maisha.velocity.y -= 16.0 * delta
	else:
		_maisha.velocity.y = 0.0
		if Input.is_key_pressed(KEY_SPACE):
			_maisha.velocity.y = 5.8

	_maisha.velocity.x = entrada.x * velocidad
	_maisha.velocity.z = entrada.y * velocidad
	_maisha.move_and_slide()

	if entrada != Vector2.ZERO:
		if abs(entrada.x) > abs(entrada.y):
			_mirando = "lado"
			_sprite_maisha.flip_h = entrada.x < 0.0
		else:
			_mirando = "arriba" if entrada.y < 0.0 else "abajo"
			_sprite_maisha.flip_h = false

		_tiempo_anim += delta * (13.0 if _esta_corriendo else 8.5)
		var dicc_anim := _texturas_correr if _esta_corriendo else _texturas_andar
		_sprite_maisha.texture = dicc_anim.get(_mirando, _texturas_andar.get("abajo"))
		_sprite_maisha.frame = int(_tiempo_anim) % 4
	else:
		_tiempo_anim += delta * 2.2
		_sprite_maisha.texture = _texturas_reposo.get(_mirando, _texturas_reposo.get("abajo"))
		_sprite_maisha.frame = int(_tiempo_anim) % 4


func _actualizar_camara(delta: float) -> void:
	if _modo_hd2d:
		var objetivo := _maisha.position + Vector3(0.0, 5.2, 7.5)
		_camara.position = _camara.position.lerp(objetivo, 5.0 * delta)
		_camara.rotation_degrees = Vector3(-32.0, 0.0, 0.0)
	else:
		var objetivo := _maisha.position + Vector3(0.0, 7.5, 6.0)
		_camara.position = _camara.position.lerp(objetivo, 6.0 * delta)
		_camara.rotation_degrees = Vector3(-45.0, 0.0, 0.0)


func _actualizar_pino(delta: float) -> void:
	_tiempo_pino += delta
	if _sprite_pino:
		_sprite_pino.frame = 1 if fmod(_tiempo_pino, 2.0) < 0.3 else 0

	var dist := _maisha.position.distance_to(_nodo_pino.position)
	if dist < 2.4 and not _dialogando:
		_etiqueta_info.text = "Cerca de Pino: Pulsa [E] para hablar · [J] Golpe de Cetro · [K] Semilla Explosiva"
	elif not _dialogando:
		_etiqueta_info.text = "PROTOTIPO HD-2D: WASD: Mover · Shift/C: Correr · Espacio: Saltar · [J] Golpe · [K] Semilla · [E] Hablar\n[3] Alternar Vista (HD-2D vs 2D Plana) | [1] Iluminación (Atardecer/Noche/Día)"


func _actualizar_petrino(delta: float) -> void:
	if _nodo_petrino == null or not is_instance_valid(_nodo_petrino):
		return
	if not _nodo_petrino.is_on_floor():
		_nodo_petrino.velocity.y -= 14.0 * delta
	_nodo_petrino.velocity.x = _empuje_petrino.x
	_nodo_petrino.velocity.z = _empuje_petrino.z
	_empuje_petrino = _empuje_petrino.move_toward(Vector3.ZERO, 10.0 * delta)
	_nodo_petrino.move_and_slide()


func _interactuar() -> void:
	var dist := _maisha.position.distance_to(_nodo_pino.position)
	if dist < 2.5:
		if not _dialogando:
			_abrir_dialogo()
		else:
			_cerrar_dialogo()


func _abrir_dialogo() -> void:
	_dialogando = true
	_caja_dialogo.visible = true
	if _sonido and _sonido.has_method("efecto"):
		_sonido.call("efecto", "dialogo_pasar")


func _cerrar_dialogo() -> void:
	_dialogando = false
	_caja_dialogo.visible = false
	if _sonido and _sonido.has_method("efecto"):
		_sonido.call("efecto", "dialogo_cerrar")


func _ejecutar_golpe_cetro() -> void:
	if _sonido and _sonido.has_method("efecto"):
		_sonido.call("efecto", "cetro_golpe")

	# Destello visual de golpe en 3D
	var flash := OmniLight3D.new()
	flash.light_color = Color("fff3aa")
	flash.light_energy = 3.0
	flash.omni_range = 2.5
	flash.position = _maisha.position + Vector3(0, 0.5, 0) + _direccion_mirada_3d() * 0.9
	add_child(flash)

	var t := create_tween()
	t.tween_property(flash, "light_energy", 0.0, 0.18)
	t.tween_callback(flash.queue_free)

	# Comprobar impacto con el Petrino
	if _nodo_petrino and is_instance_valid(_nodo_petrino):
		var dist := _maisha.position.distance_to(_nodo_petrino.position)
		if dist < 2.2:
			if _sonido and _sonido.has_method("efecto"):
				_sonido.call("efecto", "golpe_acierto")
			_empuje_petrino = (_nodo_petrino.position - _maisha.position).normalized() * 6.0
			_vida_petrino -= 1
			if _vida_petrino <= 0:
				if _sonido and _sonido.has_method("efecto"):
					_sonido.call("efecto", "petrino_muere")
				_nodo_petrino.queue_free()
				_nodo_petrino = null


func _plantar_semilla() -> void:
	if _sonido and _sonido.has_method("efecto"):
		_sonido.call("efecto", "semilla_plantar")

	# Semilla 3D con luz de mecha pulsante
	var semilla := Node3D.new()
	semilla.position = _maisha.position + _direccion_mirada_3d() * 1.0 + Vector3(0, 0.15, 0)
	add_child(semilla)

	var sp := Sprite3D.new()
	sp.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	sp.pixel_size = PIXEL_SCALE * 0.85
	sp.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	sp.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	var ruta := "res://arte/efectos/semilla.png"
	if ResourceLoader.exists(ruta):
		sp.texture = load(ruta)
	semilla.add_child(sp)

	var luz := OmniLight3D.new()
	luz.light_color = Color("ff6d22")
	luz.light_energy = 2.0
	luz.omni_range = 2.0
	semilla.add_child(luz)

	# Temporizador de detonación a los 1.8 s
	var tw := create_tween()
	tw.tween_interval(1.8)
	tw.tween_callback(func():
		if is_instance_valid(semilla):
			_detonar_semilla(semilla.position)
			semilla.queue_free()
	)


func _detonar_semilla(pos: Vector3) -> void:
	if _sonido and _sonido.has_method("efecto"):
		_sonido.call("efecto", "explosion")

	# Fogonazo 3D de explosión
	var luz_exp := OmniLight3D.new()
	luz_exp.position = pos + Vector3(0, 0.8, 0)
	luz_exp.light_color = Color("ffa538")
	luz_exp.light_energy = 5.0
	luz_exp.omni_range = 6.0
	add_child(luz_exp)

	var t := create_tween()
	t.tween_property(luz_exp, "light_energy", 0.0, 0.35)
	t.tween_callback(luz_exp.queue_free)

	# Empuje a Maisha y al Petrino
	var dist_maisha := _maisha.position.distance_to(pos)
	if dist_maisha < 3.0:
		_maisha.velocity += (_maisha.position - pos).normalized() * 7.0

	if _nodo_petrino and is_instance_valid(_nodo_petrino):
		var dist_enemigo := _nodo_petrino.position.distance_to(pos)
		if dist_enemigo < 3.5:
			_empuje_petrino = (_nodo_petrino.position - pos).normalized() * 9.0
			_vida_petrino -= 2
			if _vida_petrino <= 0:
				if _sonido and _sonido.has_method("efecto"):
					_sonido.call("efecto", "petrino_muere")
				_nodo_petrino.queue_free()
				_nodo_petrino = null


func _direccion_mirada_3d() -> Vector3:
	match _mirando:
		"arriba":
			return Vector3.FORWARD
		"abajo":
			return Vector3.BACK
		"lado":
			return Vector3.LEFT if _sprite_maisha.flip_h else Vector3.RIGHT
	return Vector3.BACK


func _alternar_modo_vista() -> void:
	_modo_hd2d = not _modo_hd2d
	if _modo_hd2d:
		_camara.projection = Camera3D.PROJECTION_PERSPECTIVE
		_camara.fov = 34.0
		_etiqueta_info.text = "MODO: HD-2D PERSPECTIVA 3D (Profundidad, Sombras y Capas) | Pulsa [3] para cambiar a 2D Plana"
	else:
		_camara.projection = Camera3D.PROJECTION_ORTHOGONAL
		_camara.size = 8.0
		_etiqueta_info.text = "MODO: 2D CENITAL CLÁSICA (Plana) | Pulsa [3] para volver a HD-2D"


func _aplicar_modo_iluminacion(modo: int) -> void:
	var env := _env.environment
	match modo:
		0:
			_sol.rotation_degrees = Vector3(-30.0, -42.0, 0.0)
			_sol.light_color = Color("ffecdb")
			_sol.light_energy = 1.9
			env.background_color = Color("c47942")
			env.ambient_light_color = Color("c28a5e")
			env.ambient_light_energy = 0.5
			env.fog_light_color = Color("e09c5a")
			for f in _faroles:
				f.light_energy = 1.5
		1:
			_sol.rotation_degrees = Vector3(-70.0, 20.0, 0.0)
			_sol.light_color = Color("4b689a")
			_sol.light_energy = 0.35
			env.background_color = Color("0d1220")
			env.ambient_light_color = Color("1a263e")
			env.ambient_light_energy = 0.3
			env.fog_light_color = Color("151f33")
			for f in _faroles:
				f.light_energy = 3.2
		2:
			_sol.rotation_degrees = Vector3(-55.0, -25.0, 0.0)
			_sol.light_color = Color("fffcf0")
			_sol.light_energy = 1.7
			env.background_color = Color("7da3c8")
			env.ambient_light_color = Color("b4bece")
			env.ambient_light_energy = 0.6
			env.fog_light_color = Color("92b5d4")
			for f in _faroles:
				f.light_energy = 0.6


func _parpadear_faroles(delta: float) -> void:
	var t := Time.get_ticks_msec() / 1000.0
	for i in _faroles.size():
		var f := _faroles[i]
		var osc := sin(t * 7.0 + i * 2.1) * 0.12 + sin(t * 19.0 + i * 1.5) * 0.05
		f.light_energy = maxf(0.5, f.light_energy * (1.0 + osc * delta * 5.0))
