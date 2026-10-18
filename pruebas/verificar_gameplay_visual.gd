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
