extends Node
## Prueba automática del Embarcadero Junco: se sube desde la Orilla de Juncos tras el sexto eco; el pueblo de barqueros
## (casas de juncos, grúa, almacén), el transbordador varado, las zonas y los secretos, Mamba, el cocodrilo de
## herrumbre (se clava en los postes), Bata de piedra junto a la dársena (despierta y se va a su transbordador) y el paso de La Travesía, aún cerrado.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_embarcadero_junco

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


func _fijos_con(dibujo: String) -> Array:
	var r: Array = []
	for n in get_tree().get_nodes_in_group("entidades_fijas") + get_tree().current_scene.get_node("Entidades").get_children():
		for h in n.get_children():
			if h is Sprite2D and h.texture and h.texture.resource_path.ends_with(dibujo):
				r.append(h)
	return r


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco",
			"visto/cuna_de_musgo", "camino_cienaga", "visto/cienaga_quieta", "cienaga_llegada", "orilla_llegada",
			"eco/orilla_juncos"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("De la Orilla al Embarcadero Junco:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/orilla_juncos.tscn")
	await _esperar(1.5)
	await _leer_dialogo()
	_maisha().global_position = _puerta("embarcadero").global_position + Vector2(0, 30)
	await _cruzar("mover_arriba", "EmbarcaderoJunco")
	_comprobar(_escena() == "EmbarcaderoJunco", "con el sexto eco escuchado, se sube al Embarcadero Junco")
	_comprobar(_maisha().global_position.distance_to(_puerta("orilla").punto_llegada()) < 4.0, "Maisha aparece al sur, viniendo de la Orilla")
	await _esperar(2.5)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al llegar")
	await _leer_dialogo()
	_comprobar(Sonido.musica_actual == "embarcadero", "suena su propia música («Canción de barqueros»)")

	print("El pueblo de barqueros:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	_comprobar(region.tam == Vector2(96, 72) * 16, "un lugar de 96×72 casillas")
	_comprobar(get_tree().get_nodes_in_group("zonas").size() == 3, "tres zonas corruptas")
	_comprobar(region.secretos_total == 3, "tres secretos")
	_comprobar(_fijos_con("casa_juncos.png").size() >= 6, "casas de juncos sobre pilotes (%d)" % _fijos_con("casa_juncos.png").size())
	_comprobar(_fijos_con("grua.png").size() == 1 and _fijos_con("almacen.png").size() == 1, "la grúa rota y el almacén")
	var barca: Array = _fijos_con("transbordador.png")
	_comprobar(barca.size() == 1 and barca[0].frame == 0, "el transbordador, varado")

	print("La Travesía, cerrada:")
	var norte := _puerta("travesia")
	_comprobar(norte != null and norte.destino == "la_travesia" and norte.cerrada_hasta == "travesia_abierta", "al norte, La Travesía (cerrada: se irá en el transbordador)")
	_maisha().global_position = norte.global_position + Vector2(0, 30)
	await _esperar(0.3)
	await _empujar("mover_arriba", 1.2)
	await _esperar(0.3)
	_comprobar(_escena() == "EmbarcaderoJunco" and get_tree().get_first_node_in_group("dialogo").hablando, "no deja pasar, y Maisha piensa por qué")
	await _leer_dialogo()

	print("La casa sellada de Bata:")
	var casa_s: Node2D = get_tree().current_scene.get_node("CasaSellada")
	_comprobar(casa_s != null and casa_s.get("_sello") != null, "la casa de Bata, junto al muelle, sellada por raíces de piedra")
	_comprobar(get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.get("id") == "bata").is_empty(), "Bata no está fuera: está encerrado dentro")
	_comprobar(get_tree().get_nodes_in_group("estatuas").is_empty(), "y ya no hay ninguna estatua de Bata")
	var zona1: Node2D = null
	for z in get_tree().get_nodes_in_group("zonas"):
		if z.get_meta("clave") == "1":
			zona1 = z
	_comprobar(not zona1.activa, "mientras Bata siga encerrado, la dársena duerme (sola, Maisha no se atreve)")
	_maisha().global_position = casa_s.casa + Vector2(-18, 22)
	await _esperar(0.3)
	var puerta_casa: Node2D = null
	for n in get_tree().get_nodes_in_group("interactuables"):
		if n.get("charla") == "embarcadero_casa_bata":
			puerta_casa = n
	await _hablar_con(puerta_casa)
	_comprobar(Estado.tiene("bata_puerta"), "Bata habla a través de la puerta y da la pista del almacén")
	var nudo: Node2D = casa_s.get("_nudo")
	var sacos: Array = casa_s.get("_sacos")
	_comprobar(nudo != null and sacos.size() == 4 and casa_s.nudo_tapado(), "las venas llevan a un nudo de Giza tapado por sacos, delante del almacén")
	nudo.recibir_danio(1, nudo.global_position, "explosion")
	_comprobar(is_instance_valid(nudo) and not Estado.tiene("casa_bata_abierta") and casa_s.get("_seca") < 0.0, "con los sacos encima, la semilla no le alcanza")
	_maisha().global_position = nudo.global_position + Vector2(0, 22)
	_maisha().set("aliento", 100.0)
	await _esperar(0.3)
	_maisha().latido()
	await _esperar(0.6)
	_comprobar(not casa_s.nudo_tapado(), "el Latido aparta los sacos")
	_comprobar(not nudo.recibir_golpe(1, Vector2.UP), "el cetro rebota en el nudo")
	nudo.recibir_danio(1, nudo.global_position, "explosion")
	await _esperar(0.2)
	_comprobar(casa_s.get("_seca") >= 0.0, "una semilla lo revienta: las venas se secan hacia la casa")
	var bata: Node2D = null
	for i in 60:
		await _esperar(0.25)
		await _leer_dialogo()
		for n in get_tree().get_nodes_in_group("aldeanos"):
			if n.get("id") == "bata":
				bata = n
		if bata and Estado.tiene("casa_bata_abierta"):
			break
	_comprobar(Estado.tiene("casa_bata_abierta") and bata != null, "las raíces de la puerta se deshacen y Bata sale")
	for i in 30:
		await _leer_dialogo()
		await _esperar(0.3)
	var sitio := Vector2(region.get("_sitio_viajero"))
	_comprobar(bata.global_position.distance_to(sitio) < 6.0, "y se va a su muelle, junto al transbordador")
	_maisha().global_position = bata.global_position + Vector2(-18, 0)
	await _esperar(0.3)
	await _hablar_con(bata)
	_comprobar(Estado.tiene("bata_conocido"), "Bata cuenta lo del transbordador, la Gruta y lo que se mueve en la dársena")

	var darsena: Node2D = null
	for z in get_tree().get_nodes_in_group("zonas"):
		if z.get_meta("clave") == "1":
			darsena = z
	_comprobar(darsena.jefe == "mamba", "en la dársena vive Mamba, el cocodrilo de herrumbre")
	var postes := get_tree().get_nodes_in_group("postes")
	_comprobar(postes.size() == 4, "cuatro postes de amarre en la plataforma")

	print("Mamba, el cocodrilo de herrumbre:")
	var maisha := _maisha()
	maisha.global_position = darsena.global_position + Vector2(0, 20)
	await _esperar(1.0)
	var mamba: Node2D = get_tree().get_first_node_in_group("jefes")
	_comprobar(mamba != null and mamba.fase != mamba.Fase.DORMIDO, "al pisar la plataforma se cierra la zona y Mamba sale del agua")
	_comprobar(Sonido.musica_actual == "jefe_mamba", "con su propia música")
	for i in 60:
		await _esperar(0.1)
		if mamba.fase == mamba.Fase.ACECHA:
			break
	_comprobar(mamba.fase == mamba.Fase.ACECHA and mamba.global_position.distance_to(darsena.global_position) > 90.0, "acecha en el agua, alrededor de la plataforma")
	_comprobar(not mamba.recibir_golpe(1, Vector2.RIGHT), "en el agua, el cetro no le hace nada")
	var barca_bata: Node2D = mamba.get("_barca")
	_comprobar(is_instance_valid(barca_bata), "Bata pelea a su lado, en su barca (2 contra 1)")
	mamba.sujetar(barca_bata)
	_comprobar(mamba.fase == mamba.Fase.SUJETO, "Bata lo sujeta con la pértiga contra el borde")
	var vida0: int = mamba.vida
	_comprobar(mamba.recibir_golpe(1, Vector2.RIGHT) and mamba.vida == vida0 - 1, "sujeto, el cetro le quita 1")
	barca_bata.set("_espera", 999.0)       # (para probar los postes a solas, Bata espera)
	for i in 60:
		await _esperar(0.1)
		if mamba.fase == mamba.Fase.ACECHA:
			break
	# cuando avisa, Maisha se pone detrás del poste que tiene más cerca (el poste entre ella y Mamba)
	for i in 80:
		await _esperar(0.05)
		if mamba.fase == mamba.Fase.AVISA:
			break
	_comprobar(mamba.fase == mamba.Fase.AVISA, "se para y avisa: una raya marca por dónde va a embestir")
	var poste: Node2D = postes[0]
	for pt in postes:
		if (pt as Node2D).global_position.distance_to(mamba.global_position) < poste.global_position.distance_to(mamba.global_position):
			poste = pt
	maisha.global_position = poste.global_position + (poste.global_position - mamba.global_position).normalized() * 26.0
	for i in 80:
		await _esperar(0.05)
		if mamba.fase in [mamba.Fase.ATASCADO, mamba.Fase.AL_AGUA]:
			break
	_comprobar(mamba.fase == mamba.Fase.ATASCADO, "embiste... y se le clavan los dientes en el poste")
	var vida: int = mamba.vida
	_comprobar(mamba.recibir_golpe(1, Vector2.RIGHT) and mamba.vida == vida - 1, "atascado, el cetro le quita 1")
	mamba.vida = 1
	mamba.recibir_golpe(1, Vector2.RIGHT)
	_comprobar(mamba.fase == mamba.Fase.VENCIDO and Estado.tiene("mamba_vencido"), "vencido: se le cae la herrumbre")
	for i in 40:
		await _esperar(0.3)
		await _leer_dialogo()
		if darsena.estado == darsena.Estado.PURGADA:
			break
	_comprobar(darsena.estado == darsena.Estado.PURGADA, "Mamba se va nadando y la dársena queda purgada")

	print("Arreglar el transbordador con los poderes de Maisha:")
	var arreglo: Node2D = get_tree().current_scene.get_node("ArregloTransbordador")
	var boquete: Vector2 = arreglo.call("_boquete")
	_maisha().global_position = boquete + Vector2(4, 22)
	_maisha().set("aliento", 100.0)
	await _esperar(0.4)
	_comprobar(_maisha().lanzar_semilla(), "Maisha planta una semilla en la punta del muelle, junto al boquete")
	_maisha().global_position = boquete + Vector2(-60, 40)
	for i in 40:
		await _esperar(0.2)
		await _leer_dialogo()
		if Estado.tiene("boquete_tapado"):
			break
	_comprobar(Estado.tiene("boquete_tapado") and arreglo.sprite.frame == 2, "al estallar, crecen juncos que se tejen y tapan el boquete")
	await _leer_dialogo()
	_maisha().global_position = arreglo.base + Vector2(-40, 14)
	_maisha().set("aliento", 100.0)
	await _esperar(3.0)
	_maisha().latido()
	for i in 30:
		await _esperar(0.2)
		await _leer_dialogo()
		if Estado.tiene("transbordador_listo"):
			break
	_comprobar(Estado.tiene("transbordador_listo") and arreglo.sprite.frame == 1, "el Latido, pegado al casco, la endereza: vuelve a flotar")
	await _leer_dialogo()

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
