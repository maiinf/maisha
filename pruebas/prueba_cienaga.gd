extends Node
## Prueba automática de la Ciénaga Quieta: el camino del este de la aldea, la niebla, las babosas de óxido,
## las bayas y juncos (que vuelven a salir), Juncia y su cocina (con la sopa que cura) y Konokono, la caracola de óxido.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_cienaga

const R := preload("res://scripts/combate/reglas_combate.gd")
const BABOSA := preload("res://scripts/enemigos/babosa.gd")
const SEMILLA := preload("res://scripts/combate/semilla.gd")
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


func _hablar_con(aldeano: Node) -> void:
	aldeano.interactuar()
	await _esperar(0.2)
	await _leer_dialogo()
	await _esperar(2.0)
	await _leer_dialogo()
	await _esperar(0.3)


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
			"rescatado_pino", "rescatado_corteza", "bibi_conocida", "bibi_meditar", "bibi_aldea_viva", "visto/cuna_de_musgo",
			"bibi_meditar", "pasarelas_llegada"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("El camino del este de la aldea:")
	Estado.llegada = "prados"
	get_tree().change_scene_to_file("res://escenas/mundo/cuna_de_musgo.tscn")
	await _esperar(1.5)
	var puertas := get_tree().get_nodes_in_group("puertas").filter(func(p: Node) -> bool: return p.destino == "las_pasarelas")
	_comprobar(puertas.size() == 1, "hay un camino hacia la ciénaga (por Las Pasarelas)")
	var puerta: Area2D = puertas[0]
	var maisha := _maisha()
	maisha.global_position = puerta.global_position + Vector2(-30, 0)
	await _esperar(0.3)
	await _empujar("mover_derecha", 0.8)
	await _esperar(0.3)
	_comprobar(_escena() == "CunaDeMusgo", "sin la ayuda de Bibi, las espinas no dejan pasar")
	await _leer_dialogo()
	var bibi: Node = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "bibi")[0]
	maisha.global_position = bibi.global_position + Vector2(0, 16)
	await _hablar_con(bibi)
	_comprobar(Estado.tiene("camino_bosque") and Estado.tiene("camino_cienaga"), "Bibi abre a la vez el camino del bosque y el de la ciénaga (se elige el orden)")
	_comprobar(Misiones.activas().any(func(m: Dictionary) -> bool: return m["id"] == "cienaga"), "sale la misión de la ciénaga")
	await _esperar(1.8)
	maisha.global_position = puerta.global_position + Vector2(-30, 0)
	await _esperar(0.3)
	await _empujar("mover_derecha", 0.8)
	await _esperar(2.0)
	_comprobar(_escena() == "LasPasarelas", "el camino lleva a Las Pasarelas")
	var hacia_cienaga: Area2D = get_tree().get_nodes_in_group("puertas").filter(func(p: Node) -> bool: return p.destino == "cienaga_quieta")[0]
	_maisha().global_position = hacia_cienaga.global_position + Vector2(-30, 0)
	await _esperar(0.3)
	await _empujar("mover_derecha", 0.8)
	await _esperar(2.0)
	_comprobar(_escena() == "CienagaQuieta", "y Las Pasarelas, a la Ciénaga Quieta")
	await _esperar(2.5)
	await _leer_dialogo()
	_comprobar(Estado.tiene("cienaga_llegada"), "Maisha piensa algo al llegar")

	print("La ciénaga:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	var zonas := get_tree().get_nodes_in_group("zonas")
	_comprobar(zonas.size() == 4, "4 zonas: tres corruptas y la poza de Konokono (%d)" % zonas.size())
	_comprobar(zonas.filter(func(z: Node) -> bool: return z.jefe == "konokono").size() == 1, "una es la arena de Konokono")
	_comprobar(region.secretos_total == 3, "3 secretos (dos en islas, para más adelante) (%d)" % region.secretos_total)
	_comprobar(get_tree().get_nodes_in_group("estatuas").size() == 1, "Juncia, de piedra, junto a una zona")
	var recogibles := get_tree().get_nodes_in_group("recogibles")
	var bayas := recogibles.filter(func(n: Node) -> bool: return n.objeto == "bayas")
	var juncos := recogibles.filter(func(n: Node) -> bool: return n.objeto == "junco")
	_comprobar(bayas.size() >= 4 and juncos.size() >= 3, "bayas (%d) y juncos (%d) para Juncia" % [bayas.size(), juncos.size()])
	var ambiente := get_tree().get_first_node_in_group("ambiente")
	_comprobar(ambiente.niebla > 0.5, "hay niebla")

	print("Bayas que vuelven a salir:")
	maisha = _maisha()
	var baya: Node2D = bayas[0]
	var donde: Vector2 = baya.global_position
	maisha.global_position = donde
	await _esperar(0.3)
	_comprobar(Estado.cuantos("bayas") == 1, "se recogen al pasar por encima")
	_comprobar(not Estado.tiene(baya.marca) and Estado.extra.get("rebrote", {}).has(baya.marca), "no se marcan para siempre: vuelven a salir")
	Estado.tiempo_jugado += 300.0
	var otra: Node2D = baya.duplicate()
	otra.marca = Estado.extra["rebrote"].keys()[0]
	otra.objeto = "bayas"
	otra.rebrota = 240.0
	maisha.global_position = donde + Vector2(0, 80)
	region.add_child(otra)
	await _esperar(0.1)
	_comprobar(is_instance_valid(otra) and otra.is_inside_tree(), "al cabo de un rato, la mata vuelve a dar bayas")

	print("La babosa de óxido:")
	var zona1: Node2D = zonas.filter(func(z: Node) -> bool: return z.jefe == "" and z.get_meta("clave") == "1")[0]
	_comprobar(zona1.tipos_enemigo.has("babosa"), "en la ciénaga salen babosas")
	zona1.activa = false
	var babosa: CharacterBody2D = BABOSA.new()
	babosa.position = zona1.global_position
	region.get_node(region.entidades).add_child(babosa)
	maisha.global_position = zona1.global_position + Vector2(-zona1.radios_umbral.x - 200, 0)
	var rastro: Array = []
	for i in 30:
		await _esperar(0.25)
		rastro = babosa.get("_rastro")
		if rastro.size() >= 2:
			break
	_comprobar(rastro.size() >= 2, "deja un rastro de óxido al arrastrarse (%d manchas)" % rastro.size())
	maisha.global_position = rastro[0]["p"]
	await _esperar(0.1)
	_comprobar(maisha.pegajoso > 0.0, "pisar el rastro frena a Maisha")
	maisha.global_position = babosa.global_position + Vector2(0, 60)
	babosa.recibir_golpe(1, Vector2.RIGHT)
	babosa.recibir_golpe(1, Vector2.RIGHT)
	await _esperar(1.0)
	_comprobar(not is_instance_valid(babosa) or babosa.vida <= 0, "dos golpes de cetro la deshacen")

	print("Juncia:")
	var zona2: Node2D = zonas.filter(func(z: Node) -> bool: return z.get_meta("clave") == "2")[0]
	await _purgar(zona2)
	_comprobar(zona2.estado == zona2.Estado.PURGADA, "la zona de Juncia, purgada")
	await _esperar(1.5)
	await _leer_dialogo()
	await _esperar(1.0)
	_comprobar(Estado.tiene("rescatado_juncia"), "Juncia vuelve a la vida")

	print("Konokono, la caracola de óxido:")
	var arena: Node2D = zonas.filter(func(z: Node) -> bool: return z.jefe == "konokono")[0]
	maisha = _maisha()
	maisha.vida = maisha.vida_maxima()
	maisha.global_position = arena.global_position + Vector2(-arena.radios_umbral.x - 40, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	maisha.global_position = arena.global_position + Vector2(-arena.radios_umbral.x * 0.7, 0)
	await _esperar(0.4)
	var kono: Node2D = arena.get("_nucleo")
	_comprobar(arena.estado == arena.Estado.CERRADA and kono.fase != kono.Fase.DORMIDO, "al entrar en la poza, Konokono despierta")
	await _esperar(2.0)
	_comprobar(kono.fase == kono.Fase.ARRASTRA, "se arrastra hacia Maisha")
	_comprobar(not kono.recibir_golpe(1, Vector2.RIGHT) and kono.fase == kono.Fase.ESCONDIDA, "el cetro rebota y se esconde en la concha")
	await _esperar(R.KONOKONO_ESCONDIDA + 0.2)
	kono.recibir_danio(3, kono.global_position, "explosion")
	_comprobar(kono.vida == R.KONOKONO_VIDA, "una semilla de fuera no le hace nada (la concha la aguanta)")
	# una semilla delante de la boca: se la traga
	var semilla: Node2D = SEMILLA.new()
	semilla.casilla = R.casilla_de(kono._boca())
	kono.get_parent().add_child(semilla)
	semilla.global_position = kono._boca() + Vector2(0, 6)
	maisha.vida = maisha.vida_maxima()
	await _esperar(0.15)
	_comprobar(not is_instance_valid(semilla) or semilla.is_queued_for_deletion(), "se traga la semilla")
	var mareada := false
	for i in 80:
		await _esperar(0.05)
		maisha.vida = maisha.vida_maxima()
		if kono.fase == kono.Fase.MAREADA:
			mareada = true
			break
	_comprobar(mareada and kono.vida == R.KONOKONO_VIDA - R.KONOKONO_DANIO_DENTRO, "le estalla dentro: pierde 2 y se marea")
	_comprobar(kono.recibir_golpe(1, Vector2.RIGHT) and kono.vida == R.KONOKONO_VIDA - R.KONOKONO_DANIO_DENTRO - 1, "mareada, el cetro le hace daño")
	# la mitad de la vida: llama a dos babosas
	kono._herir(1)
	await _esperar(0.4)
	_comprobar(get_tree().get_nodes_in_group("enemigos").size() >= 2, "con la mitad de vida llama a dos babosas")
	_comprobar(kono._en_fase_2(), "pasa a la segunda fase (rueda y escupe)")
	kono._cambiar(kono.Fase.ESCUPE)
	await _esperar(0.8)
	_comprobar(get_tree().get_nodes_in_group("bolas_oxido").size() >= 1, "escupe bolas de óxido")
	while kono.vida > 0:
		kono._cambiar(kono.Fase.MAREADA)
		kono.recibir_golpe(1, Vector2.RIGHT)
		await get_tree().process_frame
	for i in 30:
		maisha.vida = maisha.vida_maxima()
		await _esperar(0.5)
		if arena.estado == arena.Estado.PURGADA:
			break
	_comprobar(arena.estado == arena.Estado.PURGADA and Estado.tiene("zona/cienaga_quieta/4"), "Konokono queda libre y la poza, purgada")
	for i in 12:
		await _esperar(0.5)
		await _leer_dialogo()
		if Estado.tiene("narr/konokono"):
			break
	_comprobar(Estado.tiene("narr/konokono"), "el narrador lo cuenta con su ilustración")
	_comprobar(Misiones.hechas().any(func(m: Dictionary) -> bool: return m["id"] == "cienaga"), "misión de la ciénaga cumplida")

	print("La cocina de Juncia y la sopa:")
	Estado.objetos["bayas"] = 0
	Estado.objetos["junco"] = 0
	Estado.llegada = "cienaga"
	get_tree().change_scene_to_file("res://escenas/mundo/cuna_de_musgo.tscn")
	await _esperar(1.5)
	var juncias := get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "juncia")
	_comprobar(juncias.size() == 1, "Juncia está en la aldea, junto a su cocina")
	var juncia: Node2D = juncias[0]
	maisha = _maisha()
	maisha.global_position = juncia.global_position + Vector2(0, 16)
	await _hablar_con(juncia)
	_comprobar(Estado.tiene("encargo_juncia"), "Juncia pide bayas y juncos")
	_comprobar(Misiones.activas().any(func(m: Dictionary) -> bool: return m["id"] == "cocina_juncia"), "sale el encargo de la cocina")
	Estado.dar("bayas", 4)
	Estado.dar("junco", 3)
	await _hablar_con(juncia)
	_comprobar(Estado.tiene("construido_cocina") and Estado.cuantos("sopa") == 2 and Estado.cuantos("bayas") == 0,
		"con 4 bayas y 3 juncos arregla la cocina y da dos sopas")
	_comprobar(Estado.tiene("receta_sopa"), "y aprende a tomar sopa (F)")
	maisha.vida = 1
	await get_tree().process_frame
	Input.action_press("usar")
	await get_tree().physics_frame
	await get_tree().physics_frame
	Input.action_release("usar")
	await _esperar(0.1)
	_comprobar(maisha.vida == mini(maisha.vida_maxima(), 1 + Estado.SOPA_CURA) and Estado.cuantos("sopa") == 1, "con F se toma una sopa: +3 hojas")
	maisha.vida = maisha.vida_maxima()
	_comprobar(not maisha.tomar_sopa() and Estado.cuantos("sopa") == 1, "con toda la vida no se gasta")
	Estado.dar("bayas", 2)
	Estado.dar("junco", 1)
	await _hablar_con(juncia)
	_comprobar(Estado.cuantos("sopa") == 2 and Estado.cuantos("bayas") == 0 and Estado.cuantos("junco") == 0, "con 2 bayas y 1 junco cocina otra sopa")
	var mochila := get_tree().get_first_node_in_group("mochila")
	maisha.vida = 2
	mochila.abrir(1)
	await _esperar(0.2)
	var filas: Array = mochila._lista()
	mochila.seleccion = filas.find(filas.filter(func(f: Dictionary) -> bool: return f.get("objeto", "") == "sopa")[0])
	mochila._usar_elegido()
	_comprobar(maisha.vida == mini(maisha.vida_maxima(), 2 + Estado.SOPA_CURA) and Estado.cuantos("sopa") == 1, "también se toma desde la mochila (Acción)")
	mochila.cerrar()

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
