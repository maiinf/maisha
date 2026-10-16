extends Node3D
## CUNA DE MUSGO 3D — ESCENA COMPLETA EN ESPACIO TRIDIMENSIONAL
## Desarrollado con modelos estilizados de Blender 4.x para Maisha (Godot 4.7).
##
## Características:
## - Maisha 3D jugable con rotación suave, salto, golpe de cetro (J) y siembra de semilla (K).
## - Aldeanos 3D interactivos: Pino (Casa Seta), Corteza (Forja) y Mzee Shamba (Molino).
## - Enemigos 3D activos: Petrinos de Giza y Mzizi (Raíz ancestral).
## - Arquitectura modular: Gran Árbol, Puente de Madera, Faroles con iluminación física.
## - Tecla [1]: Ciclo Día / Atardecer / Noche con faroles.
## - Tecla [3]: Modo de cámara (HD-2D Perspectiva / Isométrica Libre / Cenital Táctica).

# Nodos del sistema
var _maisha_body: CharacterBody3D
var _maisha_mesh: Node3D
var _camara: Camera3D
var _sol: DirectionalLight3D
var _env: WorldEnvironment
var _faroles: Array[OmniLight3D] = []

# Interfaz
var _etiqueta_hud: Label
var _caja_dialogo: Control
var _texto_dialogo: Label
var _icono_retrato: TextureRect
var _sonido: Node = null

# Estado de Maisha
var _velocidad_base := 4.2
var _fuerza_salto := 5.5
var _gravedad := 14.0
var _esta_atacando := false
var _tiempo_ataque := 0.0
var _angulo_suave := 0.0

# Estado de cámara e iluminación
var _modo_camara := 0 # 0: HD-2D Perspectiva, 1: Isométrica, 2: Cenital
var _modo_hora := 0   # 0: Atardecer, 1: Noche, 2: Día
var _dialogando := false

# Lista de enemigos interactivos
var _enemigos: Array[CharacterBody3D] = []

# Modelos precargados (.glb)
var _modelos := {}


func _ready() -> void:
	_precargar_modelos()
	_construir_iluminacion_y_cielo()
	_construir_terreno_aldea()
	_construir_edificios_cuna()
	_construir_personajes()
	_construir_enemigos()
	_construir_camara()
	_construir_interfaz()
	_aplicar_iluminacion(0)

	_sonido = get_node_or_null("/root/Sonido")
	if _sonido and _sonido.has_method("musica") and _sonido.get("_reproductores") != null and _sonido.get("_reproductores").size() > 0:
		_sonido.call("musica", "kitovu")


func _precargar_modelos() -> void:
	var rutas := {
		"maisha": "res://modelos/personajes/maisha.glb",
		"pino": "res://modelos/personajes/pino.glb",
		"shamba": "res://modelos/personajes/mzee_shamba.glb",
		"corteza": "res://modelos/personajes/corteza.glb",
		"petrino": "res://modelos/enemigos/petrino_giza.glb",
		"mzizi": "res://modelos/enemigos/mzizi_raiz.glb",
		"arbol": "res://modelos/entorno/gran_arbol.glb",
		"casa_pino": "res://modelos/entorno/casa_pino.glb",
		"forja": "res://modelos/entorno/forja_corteza.glb",
		"molino": "res://modelos/entorno/molino_shamba.glb",
		"puente": "res://modelos/entorno/puente_madera.glb",
		"farol": "res://modelos/entorno/farol_madera.glb",
		"hierba": "res://modelos/entorno/bloque_hierba.glb",
		"risco": "res://modelos/entorno/bloque_risco.glb",
		"agua": "res://modelos/entorno/bloque_canal_agua.glb",
		"camino": "res://modelos/entorno/bloque_camino.glb",
		"semilla": "res://modelos/objetos/semilla_explosiva.glb"
	}
	for clave in rutas:
		if ResourceLoader.exists(rutas[clave]):
			_modelos[clave] = load(rutas[clave])


func _instanciar_modelo(clave: String) -> Node3D:
	if _modelos.has(clave):
		var escena: PackedScene = _modelos[clave]
		return escena.instantiate() as Node3D
	return Node3D.new()


func _construir_iluminacion_y_cielo() -> void:
	_env = WorldEnvironment.new()
	var env_res := Environment.new()
	env_res.background_mode = Environment.BG_COLOR
	env_res.background_color = Color(0.24, 0.16, 0.22)
	env_res.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env_res.ambient_light_color = Color(0.85, 0.70, 0.55)
	env_res.ambient_light_energy = 0.8
	env_res.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env_res.glow_enabled = true
	env_res.glow_intensity = 0.5
	env_res.glow_bloom = 0.15
	_env.environment = env_res
	add_child(_env)

	_sol = DirectionalLight3D.new()
	_sol.name = "SolDireccional"
	_sol.shadow_enabled = true
	_sol.light_color = Color(1.0, 0.88, 0.72)
	_sol.light_energy = 1.3
	_sol.rotation_degrees = Vector3(-45, -40, 0)
	add_child(_sol)


func _construir_terreno_aldea() -> void:
	var nodo_terreno := Node3D.new()
	nodo_terreno.name = "TerrenoAldea"
	add_child(nodo_terreno)

	# Suelo general con colisión
	var suelo_estatico := StaticBody3D.new()
	var col_suelo := CollisionShape3D.new()
	var box_suelo := BoxShape3D.new()
	box_suelo.size = Vector3(40, 0.5, 40)
	col_suelo.shape = box_suelo
	col_suelo.position = Vector3(0, -0.25, 0)
	suelo_estatico.add_child(col_suelo)
	nodo_terreno.add_child(suelo_estatico)

	# Alfombrado de bloques modulares de hierba y camino
	for x in range(-10, 11, 2):
		for z in range(-10, 11, 2):
			# Acequia de río en z entre 2 y 4
			if z >= 2 and z <= 4 and (x < -2 or x > 2):
				var b_agua := _instanciar_modelo("agua")
				b_agua.position = Vector3(x, -0.2, z)
				b_agua.scale = Vector3(2.0, 1.0, 2.0)
				nodo_terreno.add_child(b_agua)
			elif abs(x) <= 2 and z >= -4 and z <= 6:
				# Camino central empedrado
				var b_cam := _instanciar_modelo("camino")
				b_cam.position = Vector3(x, 0, z)
				b_cam.scale = Vector3(2.0, 1.0, 2.0)
				nodo_terreno.add_child(b_cam)
			else:
				# Bloques de hierba
				var b_hierba := _instanciar_modelo("hierba")
				b_hierba.position = Vector3(x, 0, z)
				b_hierba.scale = Vector3(2.0, 1.0, 2.0)
				nodo_terreno.add_child(b_hierba)


func _construir_edificios_cuna() -> void:
	var nodo_edificios := Node3D.new()
	nodo_edificios.name = "Edificios"
	add_child(nodo_edificios)

	# 1. Gran Árbol ancestral en el norte
	var arbol := _instanciar_modelo("arbol")
	arbol.position = Vector3(0, 0, -8.5)
	arbol.scale = Vector3(1.4, 1.4, 1.4)
	nodo_edificios.add_child(arbol)
	_agregar_colision_cilindro(arbol, 2.2, 5.0, Vector3(0, 2.5, 0))

	# 2. Casa Seta de Pino al oeste
	var casa := _instanciar_modelo("casa_pino")
	casa.position = Vector3(-6.5, 0, -2.5)
	casa.rotation_degrees.y = 45
	nodo_edificios.add_child(casa)
	_agregar_colision_cilindro(casa, 1.8, 3.0, Vector3(0, 1.5, 0))

	# 3. Forja de Corteza al este
	var forja := _instanciar_modelo("forja")
	forja.position = Vector3(6.5, 0, -2.0)
	forja.rotation_degrees.y = -35
	nodo_edificios.add_child(forja)
	_agregar_colision_caja(forja, Vector3(3.2, 2.5, 2.8), Vector3(0, 1.25, 0))

	# 4. Molino de Mzee Shamba al suroeste
	var molino := _instanciar_modelo("molino")
	molino.position = Vector3(-7.5, 0, 7.5)
	molino.rotation_degrees.y = 80
	nodo_edificios.add_child(molino)
	_agregar_colision_caja(molino, Vector3(3.5, 3.2, 3.0), Vector3(0, 1.6, 0))

	# 5. Puente de madera sobre la acequia central
	var puente := _instanciar_modelo("puente")
	puente.position = Vector3(0, 0, 3.0)
	nodo_edificios.add_child(puente)

	# 6. Faroles con luz física omnidireccional
	var coords_faroles := [
		Vector3(-2.2, 0, -4.5),
		Vector3(2.2, 0, -4.5),
		Vector3(-1.8, 0, 1.5),
		Vector3(1.8, 0, 4.8)
	]
	for pos in coords_faroles:
		var farol := _instanciar_modelo("farol")
		farol.position = pos
		nodo_edificios.add_child(farol)

		var luz := OmniLight3D.new()
		luz.light_color = Color(1.0, 0.85, 0.50)
		luz.light_energy = 2.2
		luz.omni_range = 6.0
		luz.shadow_enabled = true
		luz.position = pos + Vector3(0.6, 2.05, 0)
		nodo_edificios.add_child(luz)
		_faroles.append(luz)


func _construir_personajes() -> void:
	# Maisha (Controlable)
	_maisha_body = CharacterBody3D.new()
	_maisha_body.name = "Maisha3D"
	_maisha_body.position = Vector3(0, 0, 0)
	add_child(_maisha_body)

	var col_maisha := CollisionShape3D.new()
	var cap_maisha := CapsuleShape3D.new()
	cap_maisha.radius = 0.35
	cap_maisha.height = 1.3
	col_maisha.shape = cap_maisha
	col_maisha.position = Vector3(0, 0.65, 0)
	_maisha_body.add_child(col_maisha)

	_maisha_mesh = _instanciar_modelo("maisha")
	_maisha_body.add_child(_maisha_mesh)

	# Pino (NPC)
	var pino := _instanciar_modelo("pino")
	pino.position = Vector3(-4.8, 0, -1.8)
	pino.rotation_degrees.y = 120
	pino.set_meta("npc_id", "pino")
	pino.set_meta("nombre", "Pino")
	pino.set_meta("dialogo", "¡Hola, Maisha! Los brotes que plantas con tu cetro alejan la niebla de Giza. ¡Explora el norte!")
	add_child(pino)
	_agregar_area_interaccion(pino, "pino")

	# Corteza (NPC)
	var corteza := _instanciar_modelo("corteza")
	corteza.position = Vector3(4.8, 0, -1.5)
	corteza.rotation_degrees.y = -70
	corteza.set_meta("npc_id", "corteza")
	corteza.set_meta("nombre", "Corteza")
	corteza.set_meta("dialogo", "El metal de mi yunque vibra con la piedra de Raíz. Si necesitas reforzar tu cetro, aquí me tienes.")
	add_child(corteza)
	_agregar_area_interaccion(corteza, "corteza")

	# Mzee Shamba (NPC)
	var shamba := _instanciar_modelo("shamba")
	shamba.position = Vector3(-5.5, 0, 6.2)
	shamba.rotation_degrees.y = 40
	shamba.set_meta("npc_id", "shamba")
	shamba.set_meta("nombre", "Mzee Shamba")
	shamba.set_meta("dialogo", "Ah, la pequeña luz ha vuelto. El trigo crece fuerte desde que cruzaste el arco. Cuida tu corazón.")
	add_child(shamba)
	_agregar_area_interaccion(shamba, "shamba")


func _construir_enemigos() -> void:
	# 1. Tres Petrinos de Giza patrullando el sur
	var posiciones_petrino := [
		Vector3(-2.0, 0, 8.0),
		Vector3(1.5, 0, 9.5),
		Vector3(3.0, 0, 7.5)
	]
	for i in range(posiciones_petrino.size()):
		var body := CharacterBody3D.new()
		body.name = "Petrino_%d" % (i + 1)
		body.position = posiciones_petrino[i]
		add_child(body)

		var col := CollisionShape3D.new()
		var sphere := SphereShape3D.new()
		sphere.radius = 0.45
		col.shape = sphere
		col.position = Vector3(0, 0.45, 0)
		body.add_child(col)

		var mesh := _instanciar_modelo("petrino")
		body.add_child(mesh)

		body.set_meta("vida", 3)
		body.set_meta("patrulla_origen", posiciones_petrino[i])
		_enemigos.append(body)

	# 2. Mzizi (Tocón ancestral de Raíz) en el claro este
	var mzizi := _instanciar_modelo("mzizi")
	mzizi.position = Vector3(7.5, 0, 6.5)
	add_child(mzizi)
	_agregar_colision_cilindro(mzizi, 1.2, 1.5, Vector3(0, 0.75, 0))


func _construir_camara() -> void:
	_camara = Camera3D.new()
	_camara.name = "CamaraCuna3D"
	_camara.current = true
	_camara.fov = 42.0
	add_child(_camara)
	_actualizar_posicion_camara(true)


func _construir_interfaz() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)

	# HUD de controles e información
	_etiqueta_hud = Label.new()
	_etiqueta_hud.text = "CUNA DE MUSGO 3D (BLENDER + GODOT 4)\n[WASD/Flechas] Moverse  |  [Espacio] Saltar  |  [Shift] Correr\n[J] Golpe de Cetro  |  [K] Semilla de Vida  |  [E] Hablar\n[1] Ciclo Horario (Atardecer / Noche / Día)  |  [3] Modo de Cámara"
	_etiqueta_hud.position = Vector2(16, 12)
	_etiqueta_hud.add_theme_color_override("font_color", Color(1.0, 0.95, 0.85))
	_etiqueta_hud.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.9))
	_etiqueta_hud.add_theme_constant_override("shadow_offset_x", 1)
	_etiqueta_hud.add_theme_constant_override("shadow_offset_y", 1)
	canvas.add_child(_etiqueta_hud)

	# Cuadro de diálogo
	_caja_dialogo = Control.new()
	_caja_dialogo.visible = false
	_caja_dialogo.position = Vector2(80, 240)
	_caja_dialogo.size = Vector2(480, 95)

	var fondo := ColorRect.new()
	fondo.color = Color(0.10, 0.08, 0.07, 0.92)
	fondo.size = _caja_dialogo.size
	_caja_dialogo.add_child(fondo)

	var marco := ReferenceRect.new()
	marco.border_color = Color(0.85, 0.70, 0.35)
	marco.border_width = 2.0
	marco.editor_only = false
	marco.size = _caja_dialogo.size
	_caja_dialogo.add_child(marco)

	_texto_dialogo = Label.new()
	_texto_dialogo.position = Vector2(20, 16)
	_texto_dialogo.size = Vector2(440, 65)
	_texto_dialogo.autowrap_mode = TextServer.AUTOWRAP_WORD
	_texto_dialogo.add_theme_color_override("font_color", Color(1, 0.96, 0.88))
	_caja_dialogo.add_child(_texto_dialogo)

	canvas.add_child(_caja_dialogo)


func _agregar_colision_caja(padre: Node3D, tam: Vector3, pos: Vector3) -> void:
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var b := BoxShape3D.new()
	b.size = tam
	col.shape = b
	col.position = pos
	sb.add_child(col)
	padre.add_child(sb)


func _agregar_colision_cilindro(padre: Node3D, radio: float, altura: float, pos: Vector3) -> void:
	var sb := StaticBody3D.new()
	var col := CollisionShape3D.new()
	var c := CylinderShape3D.new()
	c.radius = radio
	c.height = altura
	col.shape = c
	col.position = pos
	sb.add_child(col)
	padre.add_child(sb)


func _agregar_area_interaccion(padre: Node3D, clave: String) -> void:
	var area := Area3D.new()
	area.name = "AreaInteraccion_%s" % clave
	var col := CollisionShape3D.new()
	var s := SphereShape3D.new()
	s.radius = 2.0
	col.shape = s
	area.add_child(col)
	padre.add_child(area)


func _physics_process(delta: float) -> void:
	_procesar_maisha(delta)
	_procesar_enemigos(delta)
	_actualizar_posicion_camara(false)


func _procesar_maisha(delta: float) -> void:
	if not _maisha_body:
		return

	# Aplicar gravedad
	if not _maisha_body.is_on_floor():
		_maisha_body.velocity.y -= _gravedad * delta
	else:
		_maisha_body.velocity.y = 0.0

	if _dialogando:
		_maisha_body.velocity.x = 0
		_maisha_body.velocity.z = 0
		_maisha_body.move_and_slide()
		return

	# Entrada de movimiento
	var input_dir := Vector2.ZERO
	if Input.is_action_pressed("mover_derecha"): input_dir.x += 1
	if Input.is_action_pressed("mover_izquierda"): input_dir.x -= 1
	if Input.is_action_pressed("mover_abajo"): input_dir.y += 1
	if Input.is_action_pressed("mover_arriba"): input_dir.y -= 1
	input_dir = input_dir.normalized()

	var velocidad_actual := _velocidad_base
	if Input.is_action_pressed("correr"):
		velocidad_actual *= 1.5

	if input_dir != Vector2.ZERO:
		_maisha_body.velocity.x = input_dir.x * velocidad_actual
		_maisha_body.velocity.z = input_dir.y * velocidad_actual

		# Rotación hacia la dirección de marcha
		var angulo_objetivo := atan2(-input_dir.x, -input_dir.y)
		_angulo_suave = lerp_angle(_angulo_suave, angulo_objetivo, 14.0 * delta)
		if _maisha_mesh:
			_maisha_mesh.rotation.y = _angulo_suave
	else:
		_maisha_body.velocity.x = move_toward(_maisha_body.velocity.x, 0, velocidad_actual * 8.0 * delta)
		_maisha_body.velocity.z = move_toward(_maisha_body.velocity.z, 0, velocidad_actual * 8.0 * delta)

	# Salto con espacio
	if Input.is_action_just_pressed("ui_accept") and _maisha_body.is_on_floor():
		_maisha_body.velocity.y = _fuerza_salto
		if _sonido and _sonido.has_method("reproducir"):
			_sonido.call("reproducir", "golpe_acierto")

	_maisha_body.move_and_slide()


func _procesar_enemigos(delta: float) -> void:
	var t := Time.get_ticks_msec() / 1000.0
	for i in range(_enemigos.size()):
		var e := _enemigos[i]
		if not is_instance_valid(e):
			continue
		var origen: Vector3 = e.get_meta("patrulla_origen", Vector3.ZERO)
		var radio := 1.2
		var vel := 1.4
		var nuevo_x := origen.x + cos(t * vel + i * 1.8) * radio
		var nuevo_z := origen.z + sin(t * vel + i * 1.8) * radio
		e.position.x = nuevo_x
		e.position.z = nuevo_z
		e.rotation.y = t * 2.0


func _actualizar_posicion_camara(inmediato: bool) -> void:
	if not _camara or not _maisha_body:
		return

	var objetivo: Vector3
	var rot: Vector3

	match _modo_camara:
		0: # HD-2D Perspectiva suave
			objetivo = _maisha_body.position + Vector3(0, 5.2, 7.2)
			rot = Vector3(-35.0, 0.0, 0.0)
		1: # Isométrica de profundidad
			objetivo = _maisha_body.position + Vector3(5.5, 6.0, 5.5)
			rot = Vector3(-38.0, 45.0, 0.0)
		2: # Cenital táctica 3/4
			objetivo = _maisha_body.position + Vector3(0, 9.5, 2.5)
			rot = Vector3(-75.0, 0.0, 0.0)

	if inmediato:
		_camara.position = objetivo
		_camara.rotation_degrees = rot
	else:
		_camara.position = _camara.position.lerp(objetivo, 0.12)
		_camara.rotation_degrees = _camara.rotation_degrees.lerp(rot, 0.12)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_3:
				_modo_camara = (_modo_camara + 1) % 3
			KEY_1:
				_modo_hora = (_modo_hora + 1) % 3
				_aplicar_iluminacion(_modo_hora)
			KEY_E:
				_intentar_interactuar()
			KEY_J:
				_ejecutar_golpe_cetro()
			KEY_K:
				_plantar_semilla_vida()


func _aplicar_iluminacion(hora: int) -> void:
	if not _sol or not _env:
		return

	match hora:
		0: # Atardecer Cálido de Raíz
			_sol.light_color = Color(1.0, 0.78, 0.52)
			_sol.light_energy = 1.3
			_sol.rotation_degrees = Vector3(-35, -45, 0)
			_env.environment.background_color = Color(0.28, 0.16, 0.22)
			_env.environment.ambient_light_color = Color(0.85, 0.65, 0.50)
			for f in _faroles: f.light_energy = 1.5
		1: # Noche Estrellada con Faroles Luminosos
			_sol.light_color = Color(0.35, 0.45, 0.75)
			_sol.light_energy = 0.35
			_sol.rotation_degrees = Vector3(-65, -15, 0)
			_env.environment.background_color = Color(0.06, 0.06, 0.12)
			_env.environment.ambient_light_color = Color(0.20, 0.22, 0.38)
			for f in _faroles: f.light_energy = 3.8
		2: # Mañana Soleada
			_sol.light_color = Color(1.0, 0.98, 0.92)
			_sol.light_energy = 1.5
			_sol.rotation_degrees = Vector3(-55, -30, 0)
			_env.environment.background_color = Color(0.42, 0.62, 0.78)
			_env.environment.ambient_light_color = Color(0.88, 0.90, 0.85)
			for f in _faroles: f.light_energy = 0.4


func _intentar_interactuar() -> void:
	if _dialogando:
		_caja_dialogo.visible = false
		_dialogando = false
		return

	# Buscar NPC más cercano a Maisha
	var pos_m := _maisha_body.position
	for c in get_children():
		if c.has_meta("dialogo"):
			if pos_m.distance_to(c.position) < 2.8:
				_dialogando = true
				_caja_dialogo.visible = true
				_texto_dialogo.text = "[%s]: %s" % [str(c.get_meta("nombre", "Aldeano")), str(c.get_meta("dialogo"))]
				if _sonido and _sonido.has_method("reproducir"):
					_sonido.call("reproducir", "cetro_golpe")
				return


func _ejecutar_golpe_cetro() -> void:
	if _esta_atacando or not _maisha_mesh:
		return
	_esta_atacando = true

	# Pequeña animación de estocada hacia adelante
	var tween := create_tween()
	tween.tween_property(_maisha_mesh, "scale", Vector3(1.2, 1.2, 1.2), 0.10)
	tween.tween_property(_maisha_mesh, "scale", Vector3(1.0, 1.0, 1.0), 0.15)
	tween.finished.connect(func(): _esta_atacando = false)

	# Fogonazo de luz ámbar de Asili
	var luz_impacto := OmniLight3D.new()
	luz_impacto.light_color = Color(1.0, 0.75, 0.20)
	luz_impacto.light_energy = 4.0
	luz_impacto.omni_range = 3.5
	luz_impacto.position = _maisha_body.position + Vector3(0, 0.7, 0)
	add_child(luz_impacto)

	var tween_luz := create_tween()
	tween_luz.tween_property(luz_impacto, "light_energy", 0.0, 0.25)
	tween_luz.finished.connect(luz_impacto.queue_free)

	if _sonido and _sonido.has_method("reproducir"):
		_sonido.call("reproducir", "cetro_golpe")

	# Empuje a enemigos cercanos
	for e in _enemigos:
		if is_instance_valid(e) and _maisha_body.position.distance_to(e.position) < 2.5:
			var dir := (e.position - _maisha_body.position).normalized()
			e.position += dir * 1.2
			if _sonido and _sonido.has_method("reproducir"):
				_sonido.call("reproducir", "golpe_acierto")


func _plantar_semilla_vida() -> void:
	var semilla := _instanciar_modelo("semilla")
	semilla.position = _maisha_body.position + Vector3(0, 0.1, 0)
	add_child(semilla)

	if _sonido and _sonido.has_method("reproducir"):
		_sonido.call("reproducir", "semilla_plantar")

	# Cuenta atrás y explosión vegetal
	var tween := create_tween()
	tween.tween_property(semilla, "scale", Vector3(1.4, 1.4, 1.4), 1.2)
	tween.finished.connect(func():
		var luz_exp := OmniLight3D.new()
		luz_exp.light_color = Color(0.45, 0.95, 0.35)
		luz_exp.light_energy = 6.0
		luz_exp.omni_range = 5.0
		luz_exp.position = semilla.position + Vector3(0, 0.5, 0)
		add_child(luz_exp)

		var tw_exp := create_tween()
		tw_exp.tween_property(luz_exp, "light_energy", 0.0, 0.4)
		tw_exp.finished.connect(luz_exp.queue_free)
		semilla.queue_free()

		if _sonido and _sonido.has_method("reproducir"):
			_sonido.call("reproducir", "golpe_acierto")
	)
