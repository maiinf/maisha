extends Node
## Prueba automática del Bosque Cobrizo: el paso desde los prados, los troncos podridos, el jabalí de hierro,
## Tawi y su puesto (con el mapa de Raíz) y Pembe, el ciervo de hierro.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_bosque

const R := preload("res://scripts/combate/reglas_combate.gd")
const JABALI := preload("res://scripts/enemigos/jabali.gd")
var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


func _escena() -> String:
	var e := get_tree().current_scene
	return e.name if e else ""


func _empujar(accion: String, segundos: float) -> void:
	Input.action_press(accion)
	await _esperar(segundos)
	Input.action_release(accion)


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 60:
		if not dialogo.hablando:
			return
		dialogo.pasar()
		await _esperar(0.08)


func _purgar(zona: Node2D) -> void:
	var maisha := _maisha()
	maisha.global_position = zona.global_position + Vector2(-zona.radios_umbral.x - 20, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	maisha.global_position = zona.global_position + Vector2(-zona.radios_umbral.x * 0.8, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.queue_free()
	zona.set("_invocar", 999.0)
	var nucleo: Node2D = zona.get("_nucleo")
	var c := R.casilla_de(nucleo.global_position)
	for v in 3:
		maisha.aliento = maisha.aliento_maximo()
		maisha.vida = maisha.vida_maxima()
		maisha.global_position = R.centro_de(c + Vector2i(-2, 0))
		maisha.lanzar_semilla()
		maisha.global_position = R.centro_de(c + Vector2i(-3, 3))
		await _esperar(R.SEMILLA_MECHA + 0.2)
	await _esperar(3.2)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco",
			"rescatado_pino", "rescatado_corteza", "bibi_conocida", "bibi_meditar", "bibi_aldea_viva", "visto/cuna_de_musgo"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("El camino del norte de los prados:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/prados_del_eco.tscn")
	await _esperar(1.5)
	var puerta: Area2D = get_tree().get_nodes_in_group("puertas").filter(func(p: Node) -> bool: return p.destino == "camino_cobrizo")[0]
	var espinas := get_tree().get_root().find_children("*", "Node2D", true, false).filter(func(n: Node) -> bool: return n.get_script() == preload("res://scripts/mundo/objetos/espinas_paso.gd"))
	_comprobar(espinas.size() >= 4, "unas espinas de Giza tapan el camino del bosque (%d)" % espinas.size())
	var maisha := _maisha()
	maisha.global_position = puerta.global_position + Vector2(0, 30)
	await _esperar(0.3)
	await _empujar("mover_arriba", 0.8)
	await _esperar(0.3)
	_comprobar(_escena() == "PradosDelEco", "sin la ayuda de Bibi, las espinas no dejan pasar")
	await _leer_dialogo()
	Estado.marcar("camino_bosque")
	await _esperar(1.8)
	espinas = espinas.filter(func(n) -> bool: return is_instance_valid(n))
	_comprobar(espinas.is_empty(), "cuando Bibi habla del bosque, las espinas se marchitan")
	_comprobar(Misiones.seguida().get("id", "") in ["bosque", "prados"], "sale la misión del bosque")
	maisha.global_position = puerta.global_position + Vector2(0, 30)
	await _esperar(0.3)
	await _empujar("mover_arriba", 0.8)
	await _esperar(2.0)
	_comprobar(_escena() == "CaminoCobrizo", "el camino del norte sube por el Camino Cobrizo")
	await _esperar(2.5)
	await _leer_dialogo()
	var arriba: Area2D = get_tree().get_nodes_in_group("puertas").filter(func(p: Node) -> bool: return p.destino == "bosque_cobrizo")[0]
	_maisha().global_position = arriba.global_position + Vector2(0, 30)
	await _esperar(0.3)
	await _empujar("mover_arriba", 0.8)
	await _esperar(2.0)
	_comprobar(_escena() == "BosqueCobrizo", "y al final del camino está el Bosque Cobrizo")
	await _esperar(2.5)
	await _leer_dialogo()

	print("El bosque:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	var zonas := get_tree().get_nodes_in_group("zonas")
	_comprobar(zonas.size() == 4, "4 zonas: tres corruptas y el claro de Pembe (%d)" % zonas.size())
	_comprobar(zonas.filter(func(z: Node) -> bool: return z.jefe == "pembe").size() == 1, "una es la arena de Pembe")
	_comprobar(region.secretos_total == 2, "2 claros secretos")
	_comprobar(get_tree().get_nodes_in_group("troncos_podridos").size() >= 5, "troncos podridos con madera")
	_comprobar(get_tree().get_nodes_in_group("estatuas").size() == 1, "Tawi, de piedra, junto a una zona")
	_comprobar(get_tree().get_nodes_in_group("arboles").size() > 300, "un bosque espeso (%d árboles)" % get_tree().get_nodes_in_group("arboles").size())

	print("Troncos podridos:")
	var tronco: Node2D = get_tree().get_nodes_in_group("troncos_podridos")[0]
	_comprobar(not tronco.recibir_golpe(1, Vector2.RIGHT) and not tronco.rota, "el cetro solo lo hace temblar")
	tronco.recibir_danio(3, tronco.global_position, "explosion")
	await _esperar(0.2)
	_comprobar(tronco.rota, "una semilla lo parte")
	var madera := get_tree().get_nodes_in_group("recogibles").filter(func(n: Node) -> bool: return n.objeto == "madera")
	_comprobar(madera.size() == 1, "y deja madera en el suelo")
	maisha = _maisha()
	maisha.global_position = madera[0].global_position
	await _esperar(0.3)
	_comprobar(Estado.cuantos("madera") == 1, "se recoge al pasar por encima")

	print("El jabalí de hierro:")
	var zona1: Node2D = zonas.filter(func(z: Node) -> bool: return z.jefe == "" and z.get_meta("clave") == "1")[0]
	_comprobar(zona1.tipos_enemigo.has("jabali"), "en el bosque salen jabalíes")
	zona1.activa = false          # (para probar al jabalí sin que se cierre la zona)
	var jabali: CharacterBody2D = JABALI.new()
	jabali.position = zona1.global_position
	region.get_node(region.entidades).add_child(jabali)
	maisha.global_position = zona1.global_position + Vector2(-zona1.radios_umbral.x - 200, 0)     # lejos, fuera
	await _esperar(1.3)
	maisha.global_position = jabali.global_position + Vector2(70, 0)
	await _esperar(0.25)
	_comprobar(jabali.fase in [jabali.Fase.PREPARAR, jabali.Fase.EMBESTIR], "al verla en su fila, escarba y embiste")
	_comprobar(not jabali.recibir_golpe(1, Vector2.LEFT) or jabali.fase == jabali.Fase.ATURDIDO, "el cetro rebota en su hierro mientras no está aturdido")
	maisha.global_position = jabali.global_position + Vector2(0, 120)          # se aparta: sigue recto
	var aturdido := false
	for i in 60:
		await _esperar(0.05)
		if jabali.fase == jabali.Fase.ATURDIDO:
			aturdido = true
			break
	_comprobar(aturdido, "al chocar con algo se queda aturdido")
	var vida: int = jabali.vida
	_comprobar(jabali.recibir_golpe(1, Vector2.RIGHT) and jabali.vida == vida - 1, "aturdido, el cetro le hace daño")
	jabali.morir()

	print("Tawi:")
	var zona2: Node2D = zonas.filter(func(z: Node) -> bool: return z.get_meta("clave") == "2")[0]
	await _purgar(zona2)
	_comprobar(zona2.estado == zona2.Estado.PURGADA, "la zona de Tawi, purgada")
	await _esperar(1.5)
	await _leer_dialogo()
	await _esperar(1.0)
	_comprobar(Estado.tiene("rescatado_tawi"), "Tawi vuelve a la vida")

	print("Pembe, el ciervo de hierro:")
	var arena: Node2D = zonas.filter(func(z: Node) -> bool: return z.jefe == "pembe")[0]
	maisha = _maisha()
	maisha.vida = maisha.vida_maxima()
	maisha.global_position = arena.global_position + Vector2(0, arena.radios_umbral.y + 40)
	await get_tree().process_frame
	await get_tree().process_frame
	maisha.global_position = arena.global_position + Vector2(0, arena.radios_umbral.y * 0.7)
	await _esperar(0.4)
	var pembe: Node2D = arena.get("_nucleo")
	_comprobar(arena.estado == arena.Estado.CERRADA and pembe.fase != pembe.Fase.DORMIDO, "al entrar en el claro, Pembe despierta")
	_comprobar(pembe._arboles.size() >= 3, "conoce los árboles de su claro (%d)" % pembe._arboles.size())
	_comprobar(not pembe.recibir_golpe(1, Vector2.RIGHT), "el cetro rebota en sus placas")
	# que embista contra un árbol
	var arbol: Node2D = pembe._arboles[0]
	pembe.global_position = arbol.global_position + Vector2(-40, 0)
	pembe.set("_dir", Vector2.RIGHT)
	pembe._cambiar(pembe.Fase.EMBISTE)
	var atascado := false
	for i in 40:
		await _esperar(0.05)
		maisha.vida = maisha.vida_maxima()
		if pembe.fase == pembe.Fase.ATASCADO:
			atascado = true
			break
	_comprobar(atascado, "al embestir contra un árbol se le clavan las astas")
	_comprobar(pembe.recibir_golpe(1, Vector2.RIGHT) and pembe.vida == R.PEMBE_VIDA - 1, "atascado, el cetro le hace daño")
	pembe.recibir_danio(3, pembe.global_position, "explosion")
	_comprobar(pembe.vida == R.PEMBE_VIDA - 1 - R.PEMBE_SEMILLA_DANIO, "y cada semilla, más")
	# la mitad de la vida: llama a los jabalíes
	pembe._herir(2)
	await _esperar(0.4)
	_comprobar(get_tree().get_nodes_in_group("enemigos").size() >= 2, "con la mitad de vida llama a dos jabalíes")
	while pembe.vida > 0:
		pembe._cambiar(pembe.Fase.ATASCADO)
		pembe.recibir_golpe(1, Vector2.RIGHT)
		await get_tree().process_frame
	for i in 30:
		maisha.vida = maisha.vida_maxima()
		await _esperar(0.5)
		if arena.estado == arena.Estado.PURGADA:
			break
	_comprobar(arena.estado == arena.Estado.PURGADA and Estado.tiene("zona/bosque_cobrizo/4"), "Pembe queda libre y el claro, purgado")
	await _esperar(1.0)

	print("El puesto de Tawi y el mapa de Raíz:")
	Estado.dar("madera", 2)
	Estado.llegada = "prados"
	get_tree().change_scene_to_file("res://escenas/mundo/cuna_de_musgo.tscn")
	await _esperar(1.5)
	var tawi: Node2D = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "tawi")[0]
	maisha = _maisha()
	maisha.global_position = tawi.global_position + Vector2(0, 16)
	await _esperar(0.2)
	tawi.interactuar()
	await _esperar(0.2)
	await _leer_dialogo()
	await _esperar(0.2)
	_comprobar(Estado.tiene("encargo_tawi"), "Tawi pide madera para su puesto")
	await _esperar(0.3)
	tawi.interactuar()
	await _esperar(0.2)
	await _leer_dialogo()
	await _esperar(2.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("construido_puesto") and Estado.tiene("mapa_raiz") and Estado.cuantos("madera") == 0, "con tres maderas arregla el puesto y da el mapa de Raíz")
	var mochila := get_tree().get_first_node_in_group("mochila")
	mochila.abrir(3)
	await _esperar(0.2)
	_comprobar(mochila.pestana == 3 and not mochila._mapa_mundo, "la pestaña Mapa enseña el mapa de Raíz")
	mochila.cerrar()

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
