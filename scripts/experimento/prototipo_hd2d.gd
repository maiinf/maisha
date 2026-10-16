extends Node3D
## PROTOTIPO EXPERIMENTAL HD-2D / 2.5D
## Muestra a Maisha y los elementos del mundo en un espacio 3D real con:
## - Cámara en perspectiva cinematográfica (tipo diorama / tilt-shift)
## - Sombras dinámicas reales proyectadas sobre el terreno y colinas
## - Terreno con desniveles (río hundido, puente, terraza elevada)
## - Capas de primer plano (árboles entre la cámara y Maisha)
## - Luces de farol con atenuación física y ciclos de luz (Atardecer, Noche, Día)
## - Alternancia instantánea con tecla 3 entre Vista HD-2D y Vista Plana 2D

const PIXEL_SCALE := 0.038   # Escala física de cada píxel en el mundo 3D (32 px = ~1.2 metros)

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
var _particulas_luz: GPUParticles3D
var _etiqueta_info: Label

# Estado de movimiento y animación
var _mirando := "abajo"
var _tiempo_anim := 0.0
var _esta_corriendo := false
var _modo_hd2d := true
var _hora_indice := 0   # 0: Atardecer dorado, 1: Noche mística, 2: Mañana clara

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
	_construir_camara_e_iluminacion()
	_construir_interfaz_ayuda()
	_aplicar_modo_iluminacion(0)


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
	# Hierba verde musgo con textura mate
	_mat_hierba = StandardMaterial3D.new()
	_mat_hierba.albedo_color = Color("4b7437")
	_mat_hierba.roughness = 0.9

	# Camino de tierra batida y arena cobriza
	_mat_camino = StandardMaterial3D.new()
	_mat_camino.albedo_color = Color("9c8053")
	_mat_camino.roughness = 0.85

	# Piedra y risco
	_mat_piedra = StandardMaterial3D.new()
	_mat_piedra.albedo_color = Color("5b5853")
	_mat_piedra.roughness = 0.75

	# Madera oscura de puente y postes
	_mat_madera = StandardMaterial3D.new()
	_mat_madera.albedo_color = Color("68472f")
	_mat_madera.roughness = 0.8

	# Agua translúcida con brillo especular
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

	# 4. Camino de tierra sinuoso que va hacia el puente
	_crear_bloque(raiz_mundo, Vector3(-4.0, 0.01, 0.0), Vector3(8.0, 0.04, 2.2), _mat_camino, false)
	_crear_bloque(raiz_mundo, Vector3(5.5, 0.01, 0.0), Vector3(5.0, 0.04, 2.2), _mat_camino, false)

	# 5. Puente de madera cruzando el río
	_crear_bloque(raiz_mundo, Vector3(1.5, 0.08, 0.0), Vector3(3.6, 0.18, 2.4), _mat_madera, true)
	# Barandillas del puente
	_crear_bloque(raiz_mundo, Vector3(1.5, 0.45, -1.2), Vector3(3.6, 0.6, 0.1), _mat_madera, true)
	_crear_bloque(raiz_mundo, Vector3(1.5, 0.45, 1.2), Vector3(3.6, 0.6, 0.1), _mat_madera, true)

	# 6. Terraza / Colina elevada de piedra (+1.2m en la parte noroeste)
	_crear_bloque(raiz_mundo, Vector3(-6.5, 0.6, -4.5), Vector3(7.0, 1.2, 5.0), _mat_hierba, true)
	_crear_bloque(raiz_mundo, Vector3(-6.5, 0.5, -1.95), Vector3(7.0, 1.0, 0.1), _mat_piedra, false)

	# Rampa de acceso a la terraza
	_crear_rampa(raiz_mundo, Vector3(-2.2, 0.55, -4.5), Vector3(1.6, 1.2, 2.2), _mat_camino)

	# 7. PROPS EN BILLBOARD 3D CON SOMBRAS REALES
	# Casa Seta de Pino (al fondo a la izquierda)
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/aldea/casa_seta.png", Vector3(-4.8, 0.0, -2.8), 0.9)

	# Gran Árbol en la terraza elevada noroeste
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/aldea/gran_arbol.png", Vector3(-6.8, 1.2, -6.0), 1.0)

	# Árboles a media distancia y fondo
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/objetos/arbol_a.png", Vector3(-8.8, 0.0, 0.5), 1.1)
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/objetos/arbol_b.png", Vector3(6.5, 0.0, -3.5), 1.15)
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/objetos/arbol_a.png", Vector3(8.0, 0.0, 2.5), 1.1)

	# Árbol de PRIMER PLANO (Foreground): colocado cerca de la cámara a la derecha para crear marco de profundidad
	_crear_prop_sprite(raiz_mundo, "res://arte/mundos/raiz/objetos/arbol_b.png", Vector3(3.8, 0.0, 4.2), 1.35)

	# Farolillos en postes con luz real parpadeante
	_crear_farol(raiz_mundo, Vector3(-0.5, 0.0, -1.5))
	_crear_farol(raiz_mundo, Vector3(3.5, 0.0, 1.5))
	_crear_farol(raiz_mundo, Vector3(-2.8, 0.0, -1.2))

	# Estatua petrificada junto al camino
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
	var alto_px := sp.texture.get_height()
	sp.offset = Vector2(-ancho_px / 2.0, 0)
	sp.position = pos
	padre.add_child(sp)
	return sp


func _crear_farol(padre: Node, pos: Vector3) -> void:
	# Poste
	_crear_bloque(padre, pos + Vector3(0, 0.8, 0), Vector3(0.08, 1.6, 0.08), _mat_madera, false)
	# Farolito sprite
	var sp := _crear_prop_sprite(padre, "res://arte/mundos/raiz/aldea/farol.png", pos + Vector3(0, 1.3, 0), 0.9)
	# Luz 3D omnidireccional cálida
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
	_maisha.position = Vector3(-1.5, 0.1, 0.0)
	add_child(_maisha)

	# Colisión cilíndrica de Maisha
	var cs := CollisionShape3D.new()
	var col_cilindro := CylinderShape3D.new()
	col_cilindro.height = 1.2
	col_cilindro.radius = 0.35
	cs.shape = col_cilindro
	cs.position = Vector3(0, 0.6, 0)
	_maisha.add_child(cs)

	# Sprite 3D de Maisha con Y-Billboard y proyección de sombras en el suelo
	_sprite_maisha = Sprite3D.new()
	_sprite_maisha.pixel_size = PIXEL_SCALE
	_sprite_maisha.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	_sprite_maisha.alpha_cut = Sprite3D.ALPHA_CUT_DISCARD
	_sprite_maisha.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	_sprite_maisha.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	_sprite_maisha.hframes = 4
	_sprite_maisha.centered = false
	_sprite_maisha.offset = Vector2(-12.0, 0.0) # 24x32 centrado horizontalmente
	_sprite_maisha.texture = _texturas_reposo.get("abajo")
	_maisha.add_child(_sprite_maisha)


func _construir_camara_e_iluminacion() -> void:
	# 1. Cámara en perspectiva cinematográfica
	_camara = Camera3D.new()
	_camara.name = "CamaraCinematica"
	_camara.fov = 36.0
	_camara.rotation_degrees = Vector3(-34.0, 0.0, 0.0)
	_camara.position = _maisha.position + Vector3(0, 5.8, 7.8)
	_camara.current = true
	add_child(_camara)

	# 2. Sol direccional
	_sol = DirectionalLight3D.new()
	_sol.name = "SolDorado"
	_sol.shadow_enabled = true
	_sol.shadow_bias = 0.02
	_sol.shadow_blur = 1.4
	add_child(_sol)

	# 3. Entorno de renderizado y post-procesado
	_env = WorldEnvironment.new()
	_env.name = "WorldEnvironment"
	var medio := Environment.new()
	medio.background_mode = Environment.BG_COLOR
	medio.background_color = Color("5c789a")
	medio.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	medio.ambient_light_color = Color("a8a096")
	medio.ambient_light_energy = 0.45

	# Tonemapper cinematográfico para colores ricos
	medio.tonemap_mode = Environment.TONE_MAPPER_ACES
	medio.tonemap_exposure = 1.05

	# Resplandor suave para faroles y fuego
	medio.glow_enabled = true
	medio.glow_intensity = 0.7
	medio.glow_bloom = 0.2
	medio.glow_blend_mode = Environment.GLOW_BLEND_MODE_SOFTLIGHT

	# Niebla volumétrica de profundidad
	medio.fog_enabled = true
	medio.fog_light_color = Color("d4aa78")
	medio.fog_density = 0.015
	medio.fog_aerial_perspective = 0.3

	_env.environment = medio
	add_child(_env)


func _construir_interfaz_ayuda() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)

	var fondo_ui := ColorRect.new()
	fondo_ui.color = Color(0.05, 0.04, 0.08, 0.75)
	fondo_ui.custom_minimum_size = Vector2(640, 54)
	fondo_ui.set_anchors_preset(Control.PRESET_TOP_WIDE)
	canvas.add_child(fondo_ui)

	_etiqueta_info = Label.new()
	_etiqueta_info.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_etiqueta_info.offset_left = 12
	_etiqueta_info.offset_top = 6
	_etiqueta_info.offset_right = -12
	_etiqueta_info.text = "PROTOTIPO HD-2D / 2.5D: WASD/Flechas: Mover · Shift/C: Correr · Espacio: Saltar\n[3] Alternar Vista: HD-2D (Profundidad) vs 2D Plana | [1] Iluminación: Atardecer/Noche/Día"
	_etiqueta_info.add_theme_color_override("font_color", Color("fdf6e2"))
	canvas.add_child(_etiqueta_info)


func _physics_process(delta: float) -> void:
	_actualizar_controles_maisha(delta)
	_actualizar_camara(delta)
	_parpadear_faroles(delta)


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_3:
			_alternar_modo_vista()
		elif event.keycode == KEY_1:
			_hora_indice = (_hora_indice + 1) % 3
			_aplicar_modo_iluminacion(_hora_indice)
		elif event.keycode == KEY_4:
			_guardar_captura()
		elif event.keycode == KEY_ESCAPE:
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

	# Gravedad simple
	if not _maisha.is_on_floor():
		_maisha.velocity.y -= 16.0 * delta
	else:
		_maisha.velocity.y = 0.0
		if Input.is_key_pressed(KEY_SPACE):
			_maisha.velocity.y = 5.8

	_maisha.velocity.x = entrada.x * velocidad
	_maisha.velocity.z = entrada.y * velocidad
	_maisha.move_and_slide()

	# Dirección y animación
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
		# Vista ortográfica cenital fija (emula la proyección 2D plana clásica sin perspectiva)
		var objetivo := _maisha.position + Vector3(0.0, 7.5, 6.0)
		_camara.position = _camara.position.lerp(objetivo, 6.0 * delta)
		_camara.rotation_degrees = Vector3(-45.0, 0.0, 0.0)


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
		0: # Atardecer dorado (Golden Hour)
			_sol.rotation_degrees = Vector3(-30.0, -42.0, 0.0)
			_sol.light_color = Color("ffecdb")
			_sol.light_energy = 1.9
			env.background_color = Color("c47942")
			env.ambient_light_color = Color("c28a5e")
			env.ambient_light_energy = 0.5
			env.fog_light_color = Color("e09c5a")
			for f in _faroles:
				f.light_energy = 1.5
		1: # Noche mística con faroles encendidos
			_sol.rotation_degrees = Vector3(-70.0, 20.0, 0.0)
			_sol.light_color = Color("4b689a")
			_sol.light_energy = 0.35
			env.background_color = Color("0d1220")
			env.ambient_light_color = Color("1a263e")
			env.ambient_light_energy = 0.3
			env.fog_light_color = Color("151f33")
			for f in _faroles:
				f.light_energy = 3.2
		2: # Mañana clara y brillante
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


func _guardar_captura() -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	if img:
		img.save_png("res://documentacion/experimento/captura_hd2d.png")
		print("Captura guardada en documentacion/experimento/captura_hd2d.png")
