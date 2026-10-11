extends Node
## Prueba automática de la región Prados del Eco.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_prados

const R := preload("res://scripts/combate/reglas_combate.gd")
var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _empujar(maisha: Node2D, accion: String, segundos: float) -> void:
	Input.action_press(accion)
	await _esperar(segundos)
	Input.action_release(accion)


func _ready() -> void:
	Engine.time_scale = 3.0
	Estado.marcar("cetro_recibido")       # en los prados, Maisha ya trae el cetro del Kitovu
	var escena: Node = load("res://escenas/mundo/prados_del_eco.tscn").instantiate()
	get_tree().root.add_child(escena)
	for i in 5:
		await get_tree().process_frame
	var region: Node2D = escena.get_node("Region")
	var maisha: Node2D = escena.get_node("Entidades/Maisha")
	var gestor: Node = escena.get_node("Corrupcion")
	var filas: Array = (load("res://datos/mapas/prados_del_eco.json") as JSON).data["filas"]

	print("Carga del mapa:")
	_comprobar(get_tree().get_nodes_in_group("zonas").size() == 3, "3 zonas corruptas")
	_comprobar(region.inicio != Vector2.ZERO and maisha.global_position.distance_to(region.inicio) < 2.0, "Maisha empieza en el claro del despertar")
	_comprobar(region.secretos_total == 2, "2 secretos")
	_comprobar(get_tree().get_nodes_in_group("piedras_eco").size() == 3, "3 piedras-eco")
	_comprobar(gestor.gris_en(region.inicio) > 0.5, "al empezar, el prado está gris")
	var deco: Node2D = region.get_node_or_null("Decorado")
	_comprobar(deco != null and deco._piezas.size() > 100, "la hierba tiene decorado (%d piezas)" % (deco._piezas.size() if deco else 0))
	_comprobar(deco != null and deco._barandillas.size() >= 2, "el puente tiene barandillas")

	print("No se atraviesa el agua ni los árboles:")
	# agua: busca una casilla de agua con hierba a su izquierda
	var objetivo := Vector2i(-1, -1)
	for y in range(5, filas.size() - 5):
		var f: String = filas[y]
		var x := f.find("~")
		if x > 2 and f[x - 1] == "." and f[x - 2] == ".":
			objetivo = Vector2i(x, y)
			break
	maisha.global_position = R.centro_de(objetivo + Vector2i(-2, 0))
	await _empujar(maisha, "mover_derecha", 1.0)
	_comprobar(maisha.global_position.x < objetivo.x * R.CASILLA, "el río frena a Maisha")
	# árbol
	var arbol := Vector2i(-1, -1)
	for y in range(8, filas.size() - 8):
		var f: String = filas[y]
		for x in range(8, f.length() - 12):
			if f[x] == "T" and f.substr(x - 3, 3) == "..." and filas[y - 1][x - 1] == "." and filas[y + 1][x - 1] == ".":
				arbol = Vector2i(x, y)
				break
		if arbol.x >= 0:
			break
	maisha.global_position = R.centro_de(arbol + Vector2i(-2, 0)) + Vector2(0, 6)
	await _empujar(maisha, "mover_derecha", 1.0)
	_comprobar(maisha.global_position.x < arbol.x * R.CASILLA + 4, "el tronco del árbol frena a Maisha")

	print("El matorral de la esquina guarda un secreto:")
	var puerta: Node2D = null
	for m in get_tree().get_nodes_in_group("matorrales"):
		if R.casilla_de(m.global_position) == Vector2i(9, 9):
			puerta = m
	var dentro: int = region.secretos_encontrados
	maisha.global_position = R.centro_de(Vector2i(11, 9))
	await _empujar(maisha, "mover_izquierda", 1.2)
	_comprobar(region.secretos_encontrados == dentro, "con el matorral entero no se llega al secreto")
	maisha.golpear()
	await _esperar(0.3)
	_comprobar(not puerta.roto, "el golpe no rompe el matorral")
	maisha.aliento = R.ALIENTO_MAXIMO
	maisha.global_position = R.centro_de(Vector2i(11, 9))
	maisha.lanzar_semilla()
	maisha.global_position = R.centro_de(Vector2i(11, 12))   # fuera de la cruz
	await _esperar(R.SEMILLA_MECHA + 0.3)
	_comprobar(puerta.roto, "la semilla rompe el matorral")
	maisha.vida = R.VIDA_MAXIMA
	maisha.global_position = R.centro_de(Vector2i(11, 9))
	await _empujar(maisha, "mover_izquierda", 1.2)
	_comprobar(region.secretos_encontrados == dentro + 1, "roto el matorral, Maisha llega al secreto")

	print("Piedras-eco y escondite:")
	var roca: Node = get_tree().get_first_node_in_group("rocas_moviles")
	_comprobar(not roca.abierta, "el escondite empieza cerrado")
	for piedra in get_tree().get_nodes_in_group("piedras_eco"):
		piedra.recibir_golpe(1, Vector2.RIGHT)
	await _esperar(0.2)
	_comprobar(roca.abierta, "al encender las 3 piedras, la roca se aparta")

	print("El escondite de las piedras-eco:")
	var antes: int = region.secretos_encontrados
	var secreto: Node2D = get_tree().get_nodes_in_group("secretos").filter(func(n: Node) -> bool: return not n.is_queued_for_deletion())[0]
	maisha.global_position = secreto.global_position + Vector2(0, 40)   # delante de la roca que se ha apartado
	await _empujar(maisha, "mover_arriba", 1.2)
	_comprobar(region.secretos_encontrados == antes + 1, "por el hueco de la roca se llega al secreto (%d/%d)" % [region.secretos_encontrados, region.secretos_total])

	print("Purgar las tres zonas devuelve el color a toda la región:")
	var purgada := [false]
	gestor.region_purgada.connect(func() -> void: purgada[0] = true)
	for zona in get_tree().get_nodes_in_group("zonas"):
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
			maisha.aliento = R.ALIENTO_MAXIMO
			maisha.vida = R.VIDA_MAXIMA
			maisha.global_position = R.centro_de(c + Vector2i(-2, 0))
			maisha.lanzar_semilla()
			maisha.global_position = R.centro_de(c + Vector2i(-3, 3))
			await _esperar(R.SEMILLA_MECHA + 0.2)
		await _esperar(3.2)
		_comprobar(zona.estado == zona.Estado.PURGADA, "zona purgada")
	await _esperar(2.5)
	_comprobar(purgada[0], "aviso de región purgada")
	_comprobar(gestor.gris_en(region.inicio) < 0.05, "el claro del despertar ya tiene color")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	await Sonido.callar()
	get_tree().quit(_fallos)
