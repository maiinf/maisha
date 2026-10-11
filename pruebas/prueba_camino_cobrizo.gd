extends Node
## Prueba automática del Camino Cobrizo (el tercer camino de Raíz): de los Prados del Eco al Bosque Cobrizo;
## el topo de piedra (enemigo nuevo), Fuko y sus campanillas, la peña que no se cruza, el derrumbe que despeja
## y el tercer eco perdido.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_camino_cobrizo

const R := preload("res://scripts/combate/reglas_combate.gd")
const ECO := preload("res://scripts/mundo/objetos/eco_perdido.gd")
const TOPO := preload("res://scripts/enemigos/topo.gd")
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


func _puerta(id: String) -> Area2D:
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == id:
			return p
	return null


func _empujar(accion: String, segundos: float) -> void:
	Input.action_press(accion)
	await _esperar(segundos)
	Input.action_release(accion)


func _cruzar(accion: String, nombre: String) -> void:
	Input.action_press(accion)
	for i in 400:
		if Estado.cambiando:
			break
		await get_tree().process_frame
	Input.action_release(accion)
	for i in 300:
		if _escena() == nombre and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(0.3)


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 80:
		if not dialogo.hablando:
			return
		dialogo.pasar()
		await _esperar(0.08)


func _hablar_con(n: Node) -> void:
	n.interactuar()
	await _esperar(0.2)
	await _leer_dialogo()
	await _esperar(2.2)            # (lo que se dice «después»)
	await _leer_dialogo()
	await _esperar(0.4)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco",
			"visto/cuna_de_musgo", "bibi_conocida", "bibi_aldea_viva", "camino_bosque", "camino_cienaga",
			"eco/sendero_del_puente", "eco/las_pasarelas", "prados_secreto_visto"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("De los prados al Camino Cobrizo:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/prados_del_eco.tscn")
	await _esperar(1.5)
	var norte := _puerta("bosque")
	_comprobar(norte != null and norte.destino == "camino_cobrizo", "el camino del norte de los prados lleva al Camino Cobrizo")
	await _leer_dialogo()
	_maisha().global_position = norte.global_position + Vector2(0, 30)
	await _cruzar("mover_arriba", "CaminoCobrizo")
	_comprobar(_escena() == "CaminoCobrizo", "se llega al Camino Cobrizo")
	_comprobar(_maisha().global_position.distance_to(_puerta("prados").punto_llegada()) < 4.0, "Maisha aparece al sur, viniendo de los prados")
	await _esperar(2.5)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al llegar")
	await _leer_dialogo()

	print("El Camino Cobrizo:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	_comprobar(region.tam.y >= 100 * 16, "sube de sur a norte: unas 4 pantallas de alto")
	var zonas := get_tree().get_nodes_in_group("zonas")
	_comprobar(zonas.size() == 1 and zonas[0].tipos_enemigo.has("topo"), "una zona corrupta, donde salen topos de piedra")
	_comprobar(region.secretos_total == 1, "un secreto entre los árboles del noroeste")
	var campanillas := get_tree().get_nodes_in_group("recogibles").filter(func(n: Node) -> bool: return n.objeto == "campanilla")
	_comprobar(campanillas.size() == 3, "tres campanillas de Fuko")
	var fuko: Node2D = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "fuko")[0]
	_comprobar(fuko != null, "Fuko, el topo minero, junto a su madriguera")
	var derrumbe: Node2D = get_tree().get_first_node_in_group("derrumbes")
	_comprobar(derrumbe != null and not derrumbe.despejado(), "un derrumbe tapa la boca de la galería")
	_comprobar(_puerta("bosque") != null and _puerta("bosque").destino == "bosque_cobrizo", "al norte, el Bosque Cobrizo")
	var arboles := get_tree().get_nodes_in_group("arboles")
	_comprobar(arboles.size() > 150, "muchos árboles a los lados (%d)" % arboles.size())
	for z in zonas:
		z.set("activa", false)          # (aquí no se pelea con la zona: se prueba el topo a mano)

	print("La peña y el derrumbe:")
	var maisha := _maisha()
	maisha.global_position = Vector2(38 * 16, 12 * 16 + 8)
	await _esperar(0.2)
	await _empujar("mover_derecha", 1.4)
	_comprobar(maisha.global_position.x < 42 * 16, "la peña no deja pasar a la hondonada (%.0f)" % maisha.global_position.x)
	maisha.global_position = Vector2(53 * 16 + 16, 27 * 16)
	await _esperar(0.2)
	await _empujar("mover_arriba", 1.4)
	_comprobar(maisha.global_position.y > 25 * 16, "el derrumbe tapa la galería (%.0f)" % maisha.global_position.y)

	print("El topo de piedra:")
	var zona: Node2D = zonas[0]
	var topo: CharacterBody2D = TOPO.new()
	topo.position = zona.global_position
	region.get_node(region.entidades).add_child(topo)
	maisha.global_position = zona.global_position + Vector2(60, 0)
	maisha.vida = maisha.vida_maxima()
	await _esperar(0.3)
	_comprobar(topo.bajo_tierra() and not topo.recibir_golpe(1, Vector2.LEFT) and topo.vida == R.TOPO_VIDA, "bajo tierra no se le puede dar")
	var se_acerco := false
	var aviso := false
	var inicio := topo.global_position
	for i in 100:
		await _esperar(0.05)
		if topo.global_position.distance_to(inicio) > 20.0:
			se_acerco = true
		if topo.fase == topo.Fase.AVISO:
			aviso = true
			break
	_comprobar(se_acerco and aviso, "va bajo tierra hacia Maisha y, al llegar, el suelo tiembla (aviso)")
	for i in 40:
		await _esperar(0.05)
		if topo.fase == topo.Fase.ATONTADO:
			break
	_comprobar(topo.fase == topo.Fase.ATONTADO, "sale de golpe y se queda atontado, fuera")
	_comprobar(maisha.vida < maisha.vida_maxima(), "y si Maisha estaba encima, el mordisco le hace daño")
	_comprobar(topo.recibir_golpe(1, Vector2.LEFT) and topo.vida == R.TOPO_VIDA - 2, "atontado, el cetro le quita 2")
	await _esperar(R.TOPO_ATONTADO + 0.6)
	_comprobar(topo.bajo_tierra(), "luego se vuelve a hundir")
	topo.enraizar(1.0)
	await _esperar(0.2)
	_comprobar(not topo.bajo_tierra() and topo.fase == topo.Fase.ATONTADO, "las raíces de una semilla lo sacan a la fuerza")
	topo.recibir_danio(1, topo.global_position, "explosion")
	_comprobar(topo.get("_muriendo"), "y la explosión lo deshace")
	maisha.vida = maisha.vida_maxima()

	print("Fuko y sus campanillas:")
	maisha.global_position = fuko.global_position + Vector2(0, 16)
	await _hablar_con(fuko)
	_comprobar(Estado.tiene("encargo_fuko") and Estado.tiene("fuko_conocido"), "Fuko pide sus tres campanillas")
	_comprobar(Misiones.activas().any(func(m: Dictionary) -> bool: return m["id"] == "campanillas_fuko"), "sale el encargo en el diario")
	for n in campanillas:
		maisha.global_position = n.global_position
		await _esperar(0.25)
	_comprobar(Estado.cuantos("campanilla") == 3, "se recogen al pasar (%d/3)" % Estado.cuantos("campanilla"))
	var sopas: int = Estado.cuantos("sopa")
	maisha.global_position = fuko.global_position + Vector2(0, 16)
	await _esperar(0.3)
	await _hablar_con(fuko)
	_comprobar(Estado.tiene("fuko_campanillas") and Estado.cuantos("campanilla") == 0, "se las entrega")
	_comprobar(Estado.cuantos("sopa") == sopas + 2, "y Fuko le da dos sopas")
	await _esperar(2.5)
	_comprobar(derrumbe.despejado(), "Fuko despeja el derrumbe (montón a montón)")
	maisha.global_position = Vector2(53 * 16 + 16, 27 * 16)
	await _esperar(0.2)
	await _empujar("mover_arriba", 2.0)
	_comprobar(maisha.global_position.y < 22 * 16, "ahora se entra en la vieja galería (%.0f)" % maisha.global_position.y)

	print("El tercer eco perdido:")
	var eco: Node2D = get_tree().get_first_node_in_group("ecos_perdidos")
	maisha.global_position = eco.global_position + Vector2(-14, 4)
	await _esperar(0.3)
	eco.interactuar()
	await _esperar(1.2)
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	var con_imagen := false
	for i in 120:
		if dialogo.get("_ilustracion") != null and dialogo.get("_ilustracion_alfa") > 0.5:
			con_imagen = true
		if not dialogo.hablando:
			break
		dialogo.pasar()
		await _esperar(0.12)
	await _esperar(1.2)
	_comprobar(con_imagen, "el recuerdo tiene su ilustración (14_eco_cobrizo)")
	_comprobar(Estado.tiene("eco/camino_cobrizo") and ECO.cuantos_escuchados() == 3, "tercer eco apuntado (3/9)")

	print("Al bosque y de vuelta:")
	maisha.global_position = _puerta("bosque").global_position + Vector2(0, 40)
	await _cruzar("mover_arriba", "BosqueCobrizo")
	_comprobar(_escena() == "BosqueCobrizo", "por el norte se llega al Bosque Cobrizo")
	await _esperar(2.5)
	await _leer_dialogo()
	_maisha().global_position = _puerta("prados").global_position + Vector2(0, -30)
	await _cruzar("mover_abajo", "CaminoCobrizo")
	_comprobar(_escena() == "CaminoCobrizo", "y del bosque se baja al Camino Cobrizo")
	_comprobar(_maisha().global_position.distance_to(_puerta("bosque").punto_llegada()) < 4.0, "apareciendo por el norte")
	_maisha().global_position = _puerta("prados").global_position + Vector2(0, -40)
	await _cruzar("mover_abajo", "PradosDelEco")
	_comprobar(_escena() == "PradosDelEco", "y por el sur, a los prados")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
