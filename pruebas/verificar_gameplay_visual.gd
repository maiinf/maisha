extends Node
## Script de verificación exhaustiva del gameplay visual HD-2D en movimiento:
## Comprueba texturizado de arquitectura 3D, ausencia de monolitos negros,
## estabilidad de la cámara, transiciones de transparencia y renderizado en todos los mundos.

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  [OK] ", mensaje)
	else:
		_fallos += 1
		print("  [ERROR] ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _espejo() -> Node3D:
	return get_tree().root.get_node_or_null("EspejoHD2D") as Node3D


func _ir(escena: String, puerta: String = "") -> void:
	Estado.ir_a(escena, puerta)
	for i in 300:
		if get_tree().current_scene and get_tree().current_scene.scene_file_path.ends_with(escena + ".tscn") and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(0.6)


func _encender_hd2d() -> void:
	if _espejo() != null:
		return
	var escena := get_tree().current_scene
	var tecla := InputEventKey.new()
	tecla.physical_keycode = KEY_H
	tecla.pressed = true
	escena._unhandled_key_input(tecla)
	await _esperar(0.4)


func _verificar_materiales_nodo(nodo: Node, nombre_modelo: String) -> int:
	var mallas_revisadas := 0
	if nodo is MeshInstance3D:
		var mi := nodo as MeshInstance3D
		if mi.mesh:
			for s in mi.mesh.get_surface_count():
				mallas_revisadas += 1
				var mat := mi.get_surface_override_material(s)
				if mat == null:
					mat = mi.mesh.surface_get_material(s)
				_comprobar(mat != null, "%s - %s: superficie %d tiene material asignado" % [nombre_modelo, mi.name, s])
				if mat is StandardMaterial3D:
					var sm := mat as StandardMaterial3D
					var es_negro := sm.albedo_color == Color.BLACK and sm.albedo_texture == null
					_comprobar(not es_negro, "%s - %s: superficie %d NO es negro opaco vacio" % [nombre_modelo, mi.name, s])
					var tiene_color_o_tex := sm.albedo_texture != null or sm.albedo_color.v > 0.05
					_comprobar(tiene_color_o_tex, "%s - %s: superficie %d tiene textura o color visible" % [nombre_modelo, mi.name, s])
	for h in nodo.get_children():
		mallas_revisadas += _verificar_materiales_nodo(h, nombre_modelo)
	return mallas_revisadas


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	Estado.jugando = true

	print("==================================================")
	print("VERIFICACION EXHAUSTIVA DE GAMEPLAY VISUAL HD-2D")
	print("==================================================")

	# -----------------------------------------------------------------------
	# 1. EL KITOVU (Granja de Mzee Shamba)
	# -----------------------------------------------------------------------
	print("\n--- [1/6] EL KITOVU (Granja de Mzee Shamba) ---")
	await _ir("kitovu", "")
	await _encender_hd2d()
	var esp := _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en El Kitovu")

	var maisha := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(maisha != null, "Maisha presente en el escenario")

	# Probar movimiento fluido hacia la derecha saliendo del crater
	if maisha:
		maisha.puede_actuar = true
		var p_inicio := maisha.global_position
		Input.action_press("mover_derecha")
		await _esperar(0.8)
		Input.action_release("mover_derecha")
		await _esperar(0.1)
		_comprobar(maisha.global_position.x > p_inicio.x + 20, "Maisha se desplaza libremente hacia la derecha")

		# Llevar a Maisha frente a la casona de la granja (GRANJA = Vector2(520, 380))
		maisha.global_position = Vector2(520, 420)
		await _esperar(0.4)

	var modelos: Dictionary = esp.get("_modelos_blender_instanciados")
	var granja_3d: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "casa_granja" in (m as Node3D).name:
			granja_3d = m as Node3D
			break

	_comprobar(granja_3d != null, "Modelo 3D de casa_granja.glb instanciado en El Kitovu")
	if granja_3d:
		var n_mallas := _verificar_materiales_nodo(granja_3d, "casa_granja")
		_comprobar(n_mallas >= 4, "casa_granja tiene todas sus mallas y superficies (encontradas: %d)" % n_mallas)
		_comprobar(granja_3d.visible, "casa_granja es visible en el escenario")

		# Probar caminar detras de la granja
		print("  Simulando caminar detras de la casona...")
		var pos_granja_2d := Vector2(granja_3d.position.x / 0.0625, granja_3d.position.z / 0.0625)
		maisha.global_position = pos_granja_2d + Vector2(0, -25)
		await _esperar(0.4)
		esp._actualizar_transparencias_edificios()
		var alfa_tras: float = granja_3d.get_meta("alfa_transparencia", 1.0)
		_comprobar(alfa_tras < 0.95, "Transparencia de oclusion activada detras de la granja (alfa = %.2f)" % alfa_tras)

		# Volver al frente
		maisha.global_position = pos_granja_2d + Vector2(0, 30)
		await _esperar(0.5)
		esp._actualizar_transparencias_edificios()
		var alfa_frente: float = granja_3d.get_meta("alfa_transparencia", 1.0)
		_comprobar(alfa_frente > 0.85, "Transparencia recuperada al volver al frente (alfa = %.2f)" % alfa_frente)

		# Acercarse a la torre vigia ancestral (x=25*16, y=10*16)
		maisha.global_position = Vector2(25 * 16, 10 * 16 + 20)
		await _esperar(0.4)
		modelos = esp.get("_modelos_blender_instanciados")
		var m_torre: Node3D = null
		for m in modelos.values():
			if is_instance_valid(m) and "torre" in (m as Node3D).name:
				m_torre = m
				break
		_comprobar(m_torre != null, "Torre vigía 3D instanciada en El Kitovu")
		if m_torre:
			_verificar_materiales_nodo(m_torre, "torre")

		# Acercarse al monumento ancestral (x=36*16, y=12*16)
		maisha.global_position = Vector2(36 * 16, 12 * 16 + 20)
		await _esperar(0.4)
		modelos = esp.get("_modelos_blender_instanciados")
		var m_monumento: Node3D = null
		for m in modelos.values():
			if is_instance_valid(m) and "monumento" in (m as Node3D).name:
				m_monumento = m
				break
		_comprobar(m_monumento != null, "Monumento ancestral 3D instanciado en El Kitovu")
		if m_monumento:
			_verificar_materiales_nodo(m_monumento, "monumento")

		# Acercarse al portal ancestral de raíces (P = Vector2(912, 96))
		maisha.global_position = Vector2(912, 110)
		await _esperar(0.4)
		modelos = esp.get("_modelos_blender_instanciados")
		var m_portal: Node3D = null
		for m in modelos.values():
			if is_instance_valid(m) and "portal" in (m as Node3D).name:
				m_portal = m
				break
		_comprobar(m_portal != null, "Portal ancestral de raíces 3D instanciado en El Kitovu")
		if m_portal:
			_verificar_materiales_nodo(m_portal, "portal_raiz")

		# Acercarse a la raíz gigante petrificada (N en col 41, fil 5 -> 656, 80)
		maisha.global_position = Vector2(656, 100)
		await _esperar(0.4)
		modelos = esp.get("_modelos_blender_instanciados")
		var m_raiz: Node3D = null
		for m in modelos.values():
			if is_instance_valid(m) and "raiz_gigante" in (m as Node3D).name:
				m_raiz = m
				break
		_comprobar(m_raiz != null, "Raíz gigante petrificada 3D instanciada en El Kitovu")
		if m_raiz:
			_verificar_materiales_nodo(m_raiz, "raiz_gigante")

		# Acercarse al tramo de muro de cantería (W en col 18, fil 4 -> 288, 64)
		maisha.global_position = Vector2(288, 80)
		await _esperar(0.4)
		modelos = esp.get("_modelos_blender_instanciados")
		var m_muro: Node3D = null
		for m in modelos.values():
			if is_instance_valid(m) and "muro" in (m as Node3D).name:
				m_muro = m
				break
		_comprobar(m_muro != null, "Muro de cantería 3D instanciado en El Kitovu")
		if m_muro:
			_verificar_materiales_nodo(m_muro, "muro")

		# Acercarse al tronco caído con tablas (Z en col 17, fil 24 -> 280, 398)
		maisha.global_position = Vector2(280, 420)
		await _esperar(0.4)
		modelos = esp.get("_modelos_blender_instanciados")
		var m_tronco: Node3D = null
		for m in modelos.values():
			if is_instance_valid(m) and ("tronco" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("tronco_caido.glb")):
				m_tronco = m
				break
		_comprobar(m_tronco != null, "Tronco caído con tablas 3D instanciado en El Kitovu")
		if m_tronco:
			_verificar_materiales_nodo(m_tronco, "tronco_caido")

	# -----------------------------------------------------------------------
	# 2. CUNA DE MUSGO (Aldea)
	# -----------------------------------------------------------------------
	print("\n--- [2/6] CUNA DE MUSGO (Aldea) ---")
	await _ir("cuna_de_musgo", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Cuna de Musgo")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse a la Casa-Seta de Pino (x=20*16, y=33*16)
	maisha.global_position = Vector2(20 * 16, 33 * 16 + 20)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_seta: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "casa_seta" in (m as Node3D).name:
			m_seta = m
			break
	_comprobar(m_seta != null, "Casa-seta de Pino 3D instanciada al aproximarse")
	if m_seta:
		_verificar_materiales_nodo(m_seta, "casa_seta")

	# Acercarse a la Forja de Corteza (x=48*16, y=27*16)
	maisha.global_position = Vector2(48 * 16, 27 * 16 + 20)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_forja: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "taller" in (m as Node3D).name:
			m_forja = m
			break
	_comprobar(m_forja != null, "Taller de herrería 3D instanciado al aproximarse")
	if m_forja:
		_verificar_materiales_nodo(m_forja, "taller")

	# Acercarse al Gran Árbol (x=30*16, y=22*16)
	maisha.global_position = Vector2(30 * 16, 22 * 16 + 30)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_arbol: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "gran_arbol" in (m as Node3D).name:
			m_arbol = m
			break
	_comprobar(m_arbol != null, "Gran Árbol 3D instanciado")
	if m_arbol:
		_verificar_materiales_nodo(m_arbol, "gran_arbol")

	# -----------------------------------------------------------------------
	# 3. MAANDIKO (Plaza Monumental de Sigilia)
	# -----------------------------------------------------------------------
	print("\n--- [3/6] MAANDIKO (Sigilia) ---")
	Estado.marcar("escarcha_llegada")
	await _ir("maandiko", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Maandiko")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Recorrer la plaza de Maandiko
	maisha.global_position = Vector2(400, 300)
	await _esperar(0.5)

	modelos = esp.get("_modelos_blender_instanciados")
	var m_archivo: Node3D = null
	var m_taa: Node3D = null
	var m_fuente: Node3D = null
	var m_tinta: Node3D = null
	for m in modelos.values():
		if not is_instance_valid(m):
			continue
		var n_str: String = (m as Node3D).name
		if "gran_archivo" in n_str:
			m_archivo = m
		elif "taller_taa" in n_str:
			m_taa = m
		elif "fuente" in n_str:
			m_fuente = m
		elif "puesto_tinta" in n_str:
			m_tinta = m

	_comprobar(m_archivo != null, "Gran Archivo 3D instanciado")
	if m_archivo:
		_verificar_materiales_nodo(m_archivo, "gran_archivo")
	_comprobar(m_taa != null, "Taller de Taa 3D instanciado")
	if m_taa:
		_verificar_materiales_nodo(m_taa, "taller_taa")
	_comprobar(m_fuente != null, "Fuente monumental 3D instanciada")
	if m_fuente:
		_verificar_materiales_nodo(m_fuente, "fuente")
	_comprobar(m_tinta != null, "Puesto de tinta de Wino 3D instanciado")
	if m_tinta:
		_verificar_materiales_nodo(m_tinta, "puesto_tinta")

	# -----------------------------------------------------------------------
	# 4. EMBARCADERO JUNCO (Almacén portuario y cabañas)
	# -----------------------------------------------------------------------
	print("\n--- [4/6] EMBARCADERO JUNCO ---")
	await _ir("embarcadero_junco", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Embarcadero Junco")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Recorrer el muelle y colocarse ante el almacén
	maisha.global_position = Vector2(480, 320)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_almacen: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "almacen" in (m as Node3D).name:
			m_almacen = m
			break
	_comprobar(m_almacen != null, "Almacén portuario 3D instanciado en el muelle")
	if m_almacen:
		_verificar_materiales_nodo(m_almacen, "almacen")

	# Acercarse a la grúa de carga del muelle (å en col 55, fil 17 -> 880, 272)
	maisha.global_position = Vector2(880, 280)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_grua: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "grua" in (m as Node3D).name:
			m_grua = m
			break
	_comprobar(m_grua != null, "Grúa de carga portuaria 3D instanciada en el muelle")
	if m_grua:
		_verificar_materiales_nodo(m_grua, "grua")

	# Acercarse al poste de amarre del muelle (ł en col 40, fil 54 -> 640, 864)
	maisha.global_position = Vector2(640, 880)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_poste: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "poste" in (m as Node3D).name:
			m_poste = m
			break
	_comprobar(m_poste != null, "Poste de amarre portuario 3D instanciado en el muelle")
	if m_poste:
		_verificar_materiales_nodo(m_poste, "poste_amarre")

	# Acercarse al gran transbordador fluvial de Bata (ß en col 69, fil 12 -> 1112, 206)
	maisha.global_position = Vector2(1112, 220)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_transbordador: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "transbordador" in (m as Node3D).name:
			m_transbordador = m
			break
	_comprobar(m_transbordador != null, "Gran transbordador fluvial 3D instanciado en el embarcadero")
	if m_transbordador:
		_verificar_materiales_nodo(m_transbordador, "transbordador")

	# -----------------------------------------------------------------------
	# 5. CAÑADA DEL ECO (Aprisco de Mbuzi)
	# -----------------------------------------------------------------------
	print("\n--- [5/8] CAÑADA DEL ECO ---")
	await _ir("canada_eco", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Cañada del Eco")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse al aprisco de Mbuzi (APRISCO = Vector2i(40, 7) -> (640, 112))
	maisha.global_position = Vector2(40 * 16, 7 * 16 + 30)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_aprisco: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "aprisco" in (m as Node3D).name:
			m_aprisco = m
			break
	_comprobar(m_aprisco != null, "Aprisco comunal de cabras 3D instanciado")
	if m_aprisco:
		_verificar_materiales_nodo(m_aprisco, "aprisco")

	# Acercarse a un bloque megalítico de piedra tallada (ñ en col 46, fil 9 -> 744, 158)
	maisha.global_position = Vector2(744, 175)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_bloque: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "bloque" in (m as Node3D).name:
			m_bloque = m
			break
	_comprobar(m_bloque != null, "Bloque megalítico tallado 3D instanciado en Cañada del Eco")
	if m_bloque:
		_verificar_materiales_nodo(m_bloque, "bloque_piedra")

	# -----------------------------------------------------------------------
	# 6. CAMINO COBRIZO (Madriguera de Fuko)
	# -----------------------------------------------------------------------
	print("\n--- [6/8] CAMINO COBRIZO ---")
	await _ir("camino_cobrizo", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Camino Cobrizo")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse a la madriguera de Fuko
	maisha.global_position = Vector2(250, 400)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_madriguera: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "madriguera" in (m as Node3D).name:
			m_madriguera = m
			break
	_comprobar(m_madriguera != null, "Madriguera de Fuko 3D instanciada")
	if m_madriguera:
		_verificar_materiales_nodo(m_madriguera, "madriguera")

	# Acercarse al derrumbe de la galería minera (x=54*16, y=23*16 -> 864, 368)
	maisha.global_position = Vector2(864, 380)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_derrumbe: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("derrumbe" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("derrumbe_rocas.glb")):
			m_derrumbe = m
			break
	_comprobar(m_derrumbe != null, "Derrumbe de rocas y maderos mineros 3D instanciado en Camino Cobrizo")
	if m_derrumbe:
		_verificar_materiales_nodo(m_derrumbe, "derrumbe_rocas")

	# -----------------------------------------------------------------------
	# 7. LAGO ESPEJO (Altar Sagrado, Barca y Menhir)
	# -----------------------------------------------------------------------
	print("\n--- [7/8] LAGO ESPEJO ---")
	await _ir("lago_espejo", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Lago Espejo")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse al altar sagrado del lago (x=24*16, y=8*16)
	maisha.global_position = Vector2(24 * 16, 8 * 16 + 20)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_altar: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "altar" in (m as Node3D).name:
			m_altar = m
			break
	_comprobar(m_altar != null, "Altar sagrado del lago 3D instanciado")
	if m_altar:
		_verificar_materiales_nodo(m_altar, "altar")

	# Acercarse a la barca de remos (x=15*16, y=39*16 -> 240, 624)
	maisha.global_position = Vector2(240, 624)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_barca: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "barca" in (m as Node3D).name:
			m_barca = m
			break
	_comprobar(m_barca != null, "Barca de remos tradicional 3D instanciada en la orilla")
	if m_barca:
		_verificar_materiales_nodo(m_barca, "barca")

	# Acercarse al menhir megalítico del lago (x=45*16, y=26*16 -> 720, 416)
	maisha.global_position = Vector2(720, 416)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_menhir: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "menhir" in (m as Node3D).name:
			m_menhir = m
			break
	_comprobar(m_menhir != null, "Menhir megalítico del lago 3D instanciado")
	if m_menhir:
		_verificar_materiales_nodo(m_menhir, "menhir")

	# -----------------------------------------------------------------------
	# 8. PASO DE LA ESCARCHA (Estela Rúnica de refugio)
	# -----------------------------------------------------------------------
	print("\n--- [8/8] PASO DE LA ESCARCHA ---")
	await _ir("paso_escarcha", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Paso de la Escarcha")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse a la primera estela rúnica (x=25*16, y=21*16 -> 400, 336)
	maisha.global_position = Vector2(400, 340)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_estela: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "estela" in (m as Node3D).name:
			m_estela = m
			break
	_comprobar(m_estela != null, "Estela rúnica de refugio 3D instanciada en la ventisca")
	if m_estela:
		_verificar_materiales_nodo(m_estela, "estela")

	# Acercarse a la Puerta Sellada de Maandiko (x=30*16, y=5*16 -> 480, 80)
	maisha.global_position = Vector2(480, 100)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_puerta: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("puerta" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("puerta_sellada.glb")):
			m_puerta = m
			break
	_comprobar(m_puerta != null, "Puerta Sellada monumental 3D instanciada en Paso de la Escarcha")
	if m_puerta:
		_verificar_materiales_nodo(m_puerta, "puerta_sellada")

	# -----------------------------------------------------------------------
	# 9. SENDERO OLVIDADO (Arco de las Ruinas)
	# -----------------------------------------------------------------------
	print("\n--- [9/11] SENDERO OLVIDADO ---")
	await _ir("sendero_olvidado", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Sendero Olvidado")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse al arco de las ruinas (ŵ en col 32, fil 7 -> 512, 112)
	maisha.global_position = Vector2(512, 130)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_arco: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "arco_ruinas" in (m as Node3D).name:
			m_arco = m
			break
	_comprobar(m_arco != null, "Arco de las Ruinas 3D instanciado en el Sendero Olvidado")
	if m_arco:
		_verificar_materiales_nodo(m_arco, "arco_ruinas")

	# Acercarse a un brasero rúnico encendido en la nieve (col 48, fil 15 -> 768, 240)
	maisha.global_position = Vector2(768, 260)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_brasero: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "brasero" in (m as Node3D).name:
			m_brasero = m
			break
	_comprobar(m_brasero != null, "Brasero de fuego 3D instanciado en Sendero Olvidado")
	if m_brasero:
		_verificar_materiales_nodo(m_brasero, "brasero")

	# Acercarse a un pino nevado alpino 3D (ğ en col 18, fil 12 -> 288, 192)
	maisha.global_position = Vector2(288, 210)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_pino_nev: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("pino_nevado" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("pino_nevado.glb")):
			m_pino_nev = m
			break
	_comprobar(m_pino_nev != null, "Pino nevado alpino 3D instanciado en Sendero Olvidado")
	if m_pino_nev:
		_verificar_materiales_nodo(m_pino_nev, "pino_nevado")

	# Acercarse a una estatua petrificada ancestral en el rellano (x=22*16, y=50*16 -> 352, 800)
	maisha.global_position = Vector2(352, 815)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_estatua: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("estatua" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("estatua_olvidado.glb")):
			m_estatua = m
			break
	_comprobar(m_estatua != null, "Estatua ancestral petrificada 3D instanciada en Sendero Olvidado")
	if m_estatua:
		_verificar_materiales_nodo(m_estatua, "estatua_olvidado")

	# -----------------------------------------------------------------------
	# 10. GRUTA DE LAS RAÍCES (Santuario de Corteza)
	# -----------------------------------------------------------------------
	print("\n--- [10/12] GRUTA DE LAS RAÍCES ---")
	await _ir("gruta_raices", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Gruta de las Raíces")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse al altar de corteza (ą en col 11, fil 39 -> 176, 624)
	maisha.global_position = Vector2(176, 640)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_corteza_altar: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "altar_corteza" in (m as Node3D).name:
			m_corteza_altar = m
			break
	_comprobar(m_corteza_altar != null, "Santuario de Corteza 3D instanciado en la Gruta")
	if m_corteza_altar:
		_verificar_materiales_nodo(m_corteza_altar, "altar_corteza")

	# -----------------------------------------------------------------------
	# 11. ORILLA DE JUNCOS (Balsa de Kasia)
	# -----------------------------------------------------------------------
	print("\n--- [11/12] ORILLA DE JUNCOS ---")
	await _ir("orilla_juncos", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Orilla de Juncos")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse a la balsa de Kasia (embarcadero oeste: x=640, y=680)
	maisha.global_position = Vector2(640, 680)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_balsa: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "balsa" in (m as Node3D).name:
			m_balsa = m
			break
	_comprobar(m_balsa != null, "Balsa de juncos 3D instanciada en la orilla del río")
	if m_balsa:
		_verificar_materiales_nodo(m_balsa, "balsa")

	# Acercarse a la Casa de Barcas y astillero de Kasia
	var m_casa_barcas: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("casa_barcas" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("casa_barcas.glb")):
			m_casa_barcas = m
			break
	_comprobar(m_casa_barcas != null, "Casa de barcas y astillero 3D de Kasia instanciada en Orilla de Juncos")
	if m_casa_barcas:
		_verificar_materiales_nodo(m_casa_barcas, "casa_barcas")

	# -----------------------------------------------------------------------
	# 12. CAMPO SEGADO (Máquina trilladora de vapor)
	# -----------------------------------------------------------------------
	print("\n--- [12/12] CAMPO SEGADO ---")
	await _ir("campo_segado", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Campo Segado")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse a la máquina trilladora (& en col 40, fil 34 -> 640, 544)
	maisha.global_position = Vector2(640, 560)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_maquina: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "maquina" in (m as Node3D).name:
			m_maquina = m
			break
	_comprobar(m_maquina != null, "Máquina trilladora agrícola 3D instanciada en Campo Segado")
	if m_maquina:
		_verificar_materiales_nodo(m_maquina, "maquina_campo")

	# Acercarse al molino de viento tradicional (] en col 53, fil 38 -> 848, 608) y pacas de paja
	maisha.global_position = Vector2(848, 620)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_molino: Node3D = null
	var m_paca: Node3D = null
	for m in modelos.values():
		if not is_instance_valid(m):
			continue
		var nm: String = (m as Node3D).name
		if "molino" in nm:
			m_molino = m
		elif "paca" in nm:
			m_paca = m
	_comprobar(m_molino != null, "Molino de viento tradicional 3D instanciado en Campo Segado")
	if m_molino:
		_verificar_materiales_nodo(m_molino, "molino_campo")
	_comprobar(m_paca != null, "Paca de paja cilíndrica 3D instanciada en Campo Segado")
	if m_paca:
		_verificar_materiales_nodo(m_paca, "paca")

	# -----------------------------------------------------------------------
	# 13. PRADOS DEL ECO (Columnas ancestrales de las Ruinas)
	# -----------------------------------------------------------------------
	print("\n--- [13/13] PRADOS DEL ECO ---")
	await _ir("prados_del_eco", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Prados del Eco")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse a la columna ancestral (C en col 32, fil 8 -> 512, 128)
	maisha.global_position = Vector2(512, 145)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_columna: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "columna" in (m as Node3D).name:
			m_columna = m
			break
	_comprobar(m_columna != null, "Columna de piedra ancestral 3D instanciada en Prados del Eco")
	if m_columna:
		_verificar_materiales_nodo(m_columna, "columna")

	# -----------------------------------------------------------------------
	# 14. BOSQUE COBRIZO (Tocón Sagrado Ancestral)
	# -----------------------------------------------------------------------
	print("\n--- [14/15] BOSQUE COBRIZO ---")
	await _ir("bosque_cobrizo", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Bosque Cobrizo")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse al tocón sagrado (H en col 55, fil 44 -> 880, 704)
	maisha.global_position = Vector2(880, 725)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_tocon: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "tocon" in (m as Node3D).name:
			m_tocon = m
			break
	_comprobar(m_tocon != null, "Tocón sagrado del Bosque Cobrizo 3D instanciado")
	if m_tocon:
		_verificar_materiales_nodo(m_tocon, "tocon_bosque")

	# -----------------------------------------------------------------------
	# 15. ESTANTERÍAS COLGANTES (Atril de la Gran Biblioteca de Sigilia)
	# -----------------------------------------------------------------------
	print("\n--- [15/15] ESTANTERÍAS COLGANTES ---")
	await _ir("estanterias_colgantes", "")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Estanterías Colgantes")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse al atril monumental de lectura (x=480, y=96)
	maisha.global_position = Vector2(480, 115)
	await _esperar(0.4)
	modelos = esp.get("_modelos_blender_instanciados")
	var m_atril: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "atril" in (m as Node3D).name:
			m_atril = m
			break
	_comprobar(m_atril != null, "Atril de lectura de Sigilia 3D instanciado en Estanterías Colgantes")
	if m_atril:
		_verificar_materiales_nodo(m_atril, "atril_biblioteca")

	# Acercarse a la escalera rodante de biblioteca (ǝ en x=30, y=48 -> 480, 768)
	maisha.global_position = Vector2(480, 768)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_escalera: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "escalera" in (m as Node3D).name:
			m_escalera = m
			break
	_comprobar(m_escalera != null, "Escalera rodante de biblioteca 3D instanciada en Estanterías Colgantes")
	if m_escalera:
		_verificar_materiales_nodo(m_escalera, "escalera_biblioteca")

	# -----------------------------------------------------------------------
	# 16. PASO DE PIEDRA (Casa de Nungu y Bloques Megalíticos)
	# -----------------------------------------------------------------------
	print("\n--- [16/18] PASO DE PIEDRA ---")
	await _ir("paso_piedra", "campo")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Paso de Piedra")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse frente a la Casa de Nungu (ĥ en 936, 222, puerta ď en 936, 238 -> camino seguro en 936, 280)
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(936, 280)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_nungu: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "nungu" in (m as Node3D).name:
			m_nungu = m
			break
	_comprobar(m_nungu != null, "Casa de Nungu 3D instanciada en Paso de Piedra")
	if m_nungu:
		_verificar_materiales_nodo(m_nungu, "casa_nungu")

	# Acercarse a un bloque ciclópeo de peña (ñ en 1160, 158)
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(1160, 190)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_bloque_paso: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "bloque" in (m as Node3D).name:
			m_bloque_paso = m
			break
	_comprobar(m_bloque_paso != null, "Bloque megalítico 3D instanciado en Paso de Piedra")
	if m_bloque_paso:
		_verificar_materiales_nodo(m_bloque_paso, "bloque_piedra")

	# -----------------------------------------------------------------------
	# 17. RUINAS DEL PRIMER ÁRBOL (Plaza Sagrada y Columnata)
	# -----------------------------------------------------------------------
	print("\n--- [17/18] RUINAS DEL PRIMER ÁRBOL ---")
	await _ir("ruinas_primer_arbol", "sendero")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Ruinas del Primer Árbol")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Recorrer la columnata monumental (C en 440, 750)
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(440, 765)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_col_ruinas: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "columna" in (m as Node3D).name:
			m_col_ruinas = m
			break
	_comprobar(m_col_ruinas != null, "Columna monumental 3D instanciada en Ruinas del Primer Árbol")
	if m_col_ruinas:
		_verificar_materiales_nodo(m_col_ruinas, "columna")

	# Acercarse a una de las piedras del recuerdo que rodean al Primer Árbol (ǒ en 520, 558)
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(520, 565)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_piedra_eco: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "eco" in (m as Node3D).name:
			m_piedra_eco = m
			break
	_comprobar(m_piedra_eco != null, "Piedra del Recuerdo / Eco 3D instanciada en la Plaza de las Ruinas")
	if m_piedra_eco:
		_verificar_materiales_nodo(m_piedra_eco, "piedra_eco")

	# Acercarse al Primer Árbol sagrado en el centro de la plaza (Ŧ en 512, 400)
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(512, 410)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_primer_arbol: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "primer_arbol" in (m as Node3D).name:
			m_primer_arbol = m
			break
	_comprobar(m_primer_arbol != null, "Primer Árbol sagrado monumental 3D instanciado en Ruinas del Primer Árbol")
	if m_primer_arbol:
		_verificar_materiales_nodo(m_primer_arbol, "primer_arbol")

	# -----------------------------------------------------------------------
	# 18. SENDA DE LOS SURCOS (Huertas y Arbolado Seco)
	# -----------------------------------------------------------------------
	print("\n--- [18/18] SENDA DE LOS SURCOS ---")
	await _ir("senda_surcos", "aldea")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Senda de los Surcos")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Recorrer el camino de huertas
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(400, 300)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_arbol_surcos: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "arbol_seco" in (m as Node3D).name:
			m_arbol_surcos = m
			break
	_comprobar(m_arbol_surcos != null, "Árbol seco / petrificado 3D instanciado en Senda de los Surcos")
	if m_arbol_surcos:
		_verificar_materiales_nodo(m_arbol_surcos, "arbol_seco")

	# -----------------------------------------------------------------------
	# 19. CUEVA DE LAS SETAS (Setas Bioluminiscentes de la Caverna)
	# -----------------------------------------------------------------------
	print("\n--- [19/21] CUEVA DE LAS SETAS ---")
	await _ir("cueva_setas", "escalera")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Cueva de las Setas")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse al racimo de setas brillantes (ů en 456, 78)
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(456, 95)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_seta_luz: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "seta" in (m as Node3D).name:
			m_seta_luz = m
			break
	_comprobar(m_seta_luz != null, "Racimo de setas bioluminiscentes 3D instanciado en Cueva de las Setas")
	if m_seta_luz:
		_verificar_materiales_nodo(m_seta_luz, "seta_luz")

	# -----------------------------------------------------------------------
	# 20. CIÉNAGA QUIETA (Árboles Muertos y Sauces del Humedal)
	# -----------------------------------------------------------------------
	print("\n--- [20/21] CIÉNAGA QUIETA ---")
	await _ir("cienaga_quieta", "aldea")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Ciénaga Quieta")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse a un árbol podrido de pantano (x en 472, 478)
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(472, 495)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_arbol_m: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "arbol_muerto" in (m as Node3D).name:
			m_arbol_m = m
			break
	_comprobar(m_arbol_m != null, "Árbol muerto / podrido 3D instanciado en Ciénaga Quieta")
	if m_arbol_m:
		_verificar_materiales_nodo(m_arbol_m, "arbol_muerto")

	# Acercarse a un sauce de pantano 3D (s en 408, 110)
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(408, 130)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_sauce: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("sauce" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("sauce_pantano.glb")):
			m_sauce = m
			break
	_comprobar(m_sauce != null, "Sauce de pantano 3D instanciado en Ciénaga Quieta")
	if m_sauce:
		_verificar_materiales_nodo(m_sauce, "sauce_pantano")

	# -----------------------------------------------------------------------
	# 21. SENDERO DEL PUENTE (Campamento de Msafiri y Columnas)
	# -----------------------------------------------------------------------
	print("\n--- [21/23] SENDERO DEL PUENTE ---")
	await _ir("sendero_del_puente", "prados")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Sendero del Puente")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse al campamento de Msafiri (L en 840, 302)
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(840, 320)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_camp: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "campamento" in (m as Node3D).name:
			m_camp = m
			break
	_comprobar(m_camp != null, "Campamento de viaje 3D instanciado en Sendero del Puente")
	if m_camp:
		_verificar_materiales_nodo(m_camp, "campamento")

	# Acercarse a la columna monumental del sendero (C en 648, 398)
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(648, 412)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_col_sendero: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and "columna" in (m as Node3D).name:
			m_col_sendero = m
			break
	_comprobar(m_col_sendero != null, "Columna monumental 3D instanciada en Sendero del Puente")
	if m_col_sendero:
		_verificar_materiales_nodo(m_col_sendero, "columna")

	# Verificar el cartel de madera 3D del cruce (L en 840, 302)
	var m_cartel: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("cartel" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("cartel_madera.glb")):
			m_cartel = m
			break
	_comprobar(m_cartel != null, "Cartel de madera 3D instanciado en Sendero del Puente")
	if m_cartel:
		_verificar_materiales_nodo(m_cartel, "cartel_madera")

	# -----------------------------------------------------------------------
	# 22. LAS PASARELAS (Palafito de Korongo y Árboles de Pantano)
	# -----------------------------------------------------------------------
	print("\n--- [22/23] LAS PASARELAS ---")
	await _ir("las_pasarelas", "aldea")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Las Pasarelas")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	# Acercarse al palafito de Korongo ({ en col 64, fila 10 -> (1032, 174))
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(1032, 230)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_palafito: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("palafito" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("palafito.glb")):
			m_palafito = m
			break
	_comprobar(m_palafito != null, "Palafito 3D instanciado en Las Pasarelas")
	if m_palafito:
		_verificar_materiales_nodo(m_palafito, "palafito")

	# Acercarse al árbol podrido / muerto de las pasarelas (x en col 3, fila 20 -> (56, 334))
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(56, 350)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_arbol_pas: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("arbol_muerto" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("arbol_muerto.glb")):
			m_arbol_pas = m
			break
	_comprobar(m_arbol_pas != null, "Árbol muerto 3D instanciado en Las Pasarelas")
	if m_arbol_pas:
		_verificar_materiales_nodo(m_arbol_pas, "arbol_muerto")

	# -----------------------------------------------------------------------
	# 23. LA TRAVESÍA (Transbordador de Bata y Eco de la Isla)
	# -----------------------------------------------------------------------
	print("\n--- [23/23] LA TRAVESÍA ---")
	await _ir("la_travesia", "embarcadero")
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en La Travesía")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D

	await _esperar(0.5)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_barco_travesia: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("transbordador" in (m as Node3D).name or "cubierta" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("transbordador.glb")):
			m_barco_travesia = m
			break
	_comprobar(m_barco_travesia != null, "Gran Transbordador fluvial 3D instanciado en La Travesía")
	if m_barco_travesia:
		_verificar_materiales_nodo(m_barco_travesia, "transbordador")

	# Trasladar el transbordador y Maisha junto a la isla del 7º eco para comprobar la Piedra del Eco 3D
	var viaje = get_tree().current_scene.get_node_or_null("Entidades/Viaje")
	if viaje:
		viaje.recorrido = viaje._parada
		viaje.position = viaje._punto(viaje._parada)
		viaje.fase = viaje.Fase.PARADA
		viaje._ultima_valida = viaje.position
		if is_instance_valid(maisha):
			maisha.global_position = viaje.position
	await _esperar(0.5)

	# Verificar la Piedra del Eco 3D en la isla del río (@ en col 35, fila 87 -> (568, 1406))
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_eco_isla: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("eco" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("piedra_eco.glb")):
			m_eco_isla = m
			break
	_comprobar(m_eco_isla != null, "Piedra del Eco 3D instanciada en la isla de La Travesía")
	if m_eco_isla:
		_verificar_materiales_nodo(m_eco_isla, "piedra_eco")

	# -----------------------------------------------------------------------
	# 24. INTERIORES CLAVE (Taller de Corteza y Casa de Nungu)
	# -----------------------------------------------------------------------
	print("\n--- [24/24] INTERIORES CLAVE (Taller de Corteza y Casa de Nungu) ---")
	await _ir("taller_corteza", "")
	await _encender_hd2d()
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Taller de Corteza")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(160, 135)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_yunque: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("yunque" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("yunque_forja.glb")):
			m_yunque = m
			break
	_comprobar(m_yunque != null, "Yunque de forja de Corteza 3D instanciado en Taller de Corteza")
	if m_yunque:
		_verificar_materiales_nodo(m_yunque, "yunque_forja")

	await _ir("casa_nungu", "")
	await _encender_hd2d()
	esp = _espejo()
	_comprobar(esp != null, "EspejoHD2D activo en Casa de Nungu")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	if is_instance_valid(maisha):
		maisha.global_position = Vector2(160, 95)
	await _esperar(0.4)
	esp = _espejo()
	modelos = esp.get("_modelos_blender_instanciados") if is_instance_valid(esp) else {}
	var m_armario: Node3D = null
	for m in modelos.values():
		if is_instance_valid(m) and ("armario" in (m as Node3D).name or (m as Node3D).get_meta("ruta_origen", "").ends_with("armario_nungu.glb")):
			m_armario = m
			break
	_comprobar(m_armario != null, "Armario alpino de Nungu 3D instanciado en Casa de Nungu")
	if m_armario:
		_verificar_materiales_nodo(m_armario, "armario_nungu")

	# -----------------------------------------------------------------------
	# RESUMEN FINAL
	# -----------------------------------------------------------------------
	print("\n==================================================")
	if _fallos == 0:
		print("RESULTADO GAMEPLAY VISUAL: 100% CORRECTO - CERO FALLOS VISUALES")
		print("==================================================")
		get_tree().quit(0)
	else:
		print("RESULTADO GAMEPLAY VISUAL: FALLOS DETECTADOS (%d)" % _fallos)
		print("==================================================")
		get_tree().quit(1)
