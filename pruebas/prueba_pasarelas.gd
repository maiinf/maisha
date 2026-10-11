extends Node
## Prueba automática de Las Pasarelas (el segundo camino de Raíz): de Cuna de Musgo a la Ciénaga Quieta por
## pasarelas sobre el agua; la rana de piedra (enemigo nuevo), Korongo y sus nasas, la pasarela rota que arregla
## y el segundo eco perdido.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_pasarelas

const R := preload("res://scripts/combate/reglas_combate.gd")
const ECO := preload("res://scripts/mundo/objetos/eco_perdido.gd")
const RANA := preload("res://scripts/enemigos/rana.gd")
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
			"visto/cuna_de_musgo", "bibi_conocida", "bibi_aldea_viva", "camino_bosque", "camino_cienaga", "eco/sendero_del_puente"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("De la aldea a Las Pasarelas:")
	Estado.llegada = "prados"
	get_tree().change_scene_to_file("res://escenas/mundo/cuna_de_musgo.tscn")
	await _esperar(1.5)
	var salida := _puerta("cienaga")
	_comprobar(salida != null and salida.destino == "las_pasarelas", "el camino del este de la aldea lleva a Las Pasarelas")
	_maisha().global_position = salida.global_position + Vector2(-30, 0)
	await _cruzar("mover_derecha", "LasPasarelas")
	_comprobar(_escena() == "LasPasarelas", "se llega a Las Pasarelas")
	_comprobar(_maisha().global_position.distance_to(_puerta("aldea").punto_llegada()) < 4.0, "Maisha aparece al oeste, en la orilla")
	await _esperar(2.5)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al llegar")
	await _leer_dialogo()

	print("Las Pasarelas:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	_comprobar(region.tam.x >= 140 * 16, "mide unas 3,5 pantallas de largo")
	var zonas := get_tree().get_nodes_in_group("zonas")
	_comprobar(zonas.size() == 1 and zonas[0].tipos_enemigo.has("rana"), "una zona corrupta, donde salen ranas de piedra")
	_comprobar(region.secretos_total == 1, "un secreto en el islote del sur")
	var nasas := get_tree().get_nodes_in_group("recogibles").filter(func(n: Node) -> bool: return n.objeto == "nasa")
	_comprobar(nasas.size() == 3, "tres nasas de Korongo")
	var korongo: Node2D = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "korongo")[0]
	_comprobar(korongo != null, "Korongo, la garza pescadora, junto a su palafito")
	var rota: Node2D = get_tree().get_first_node_in_group("pasarelas_rotas")
	_comprobar(rota != null and not rota.arreglada(), "un tramo de pasarela roto, al sureste")
	_comprobar(_puerta("cienaga") != null and _puerta("cienaga").destino == "cienaga_quieta", "al este, la Ciénaga Quieta")
	for z in zonas:
		z.set("activa", false)          # (aquí no se pelea con la zona: se prueba la rana a mano)

	print("Las pasarelas sobre el agua:")
	var maisha := _maisha()
	maisha.global_position = Vector2(18 * 16, 22 * 16 + 8)
	await _empujar("mover_derecha", 1.0)
	_comprobar(maisha.global_position.x > 18 * 16 + 40, "por las tablas se anda sobre el agua")
	await _empujar("mover_arriba", 0.8)
	_comprobar(maisha.global_position.y > 21 * 16, "pero fuera de la pasarela hay agua y no se puede pisar")
	maisha.global_position = Vector2(100 * 16 + 8, 38 * 16 + 10)
	await _esperar(0.2)
	await _empujar("mover_derecha", 1.4)
	_comprobar(maisha.global_position.x < 102 * 16, "el tramo roto no deja pasar (%.0f)" % maisha.global_position.x)

	print("La rana de piedra:")
	var zona: Node2D = zonas[0]
	var rana: CharacterBody2D = RANA.new()
	rana.position = zona.global_position
	region.get_node(region.entidades).add_child(rana)
	maisha.global_position = zona.global_position + Vector2(70, 0)
	maisha.vida = maisha.vida_maxima()
	var agazapada := false
	var volo := false
	for i in 80:
		await _esperar(0.05)
		if rana.fase == rana.Fase.AGAZAPA:
			agazapada = true
		if rana.fase == rana.Fase.VUELA:
			volo = true
			_comprobar(not rana.recibir_golpe(1, Vector2.LEFT) and rana.vida == R.RANA_VIDA, "en el aire no se le puede dar")
			break
	_comprobar(agazapada and volo, "al ver a Maisha cerca se agazapa (sombra de aviso) y salta hacia ella")
	for i in 40:
		await _esperar(0.05)
		if rana.fase == rana.Fase.ATONTADA:
			break
	_comprobar(rana.fase == rana.Fase.ATONTADA, "al caer se queda atontada")
	_comprobar(maisha.vida < maisha.vida_maxima(), "y si Maisha estaba donde cae, la onda le hace daño")
	_comprobar(rana.recibir_golpe(1, Vector2.LEFT) and rana.vida == R.RANA_VIDA - 2, "atontada, el cetro le quita 2")
	await _esperar(R.RANA_ATONTADA + 0.3)
	rana.vida = R.RANA_VIDA
	rana.recibir_golpe(1, Vector2.LEFT)
	_comprobar(rana.vida == R.RANA_VIDA - 1 and rana.fase == rana.Fase.ESQUIVA, "sin estar atontada, el cetro le quita 1 y salta para apartarse")
	await _esperar(0.6)
	rana.recibir_danio(1, rana.global_position, "explosion")
	_comprobar(rana.get("_muriendo"), "una semilla le quita 2: se deshace")
	maisha.vida = maisha.vida_maxima()

	print("Korongo y sus nasas:")
	maisha.global_position = korongo.global_position + Vector2(0, 16)
	await _hablar_con(korongo)
	_comprobar(Estado.tiene("encargo_korongo"), "Korongo pide sus tres nasas")
	_comprobar(Misiones.activas().any(func(m: Dictionary) -> bool: return m["id"] == "nasas_korongo"), "sale el encargo en el diario")
	for n in nasas:
		maisha.global_position = n.global_position
		await _esperar(0.25)
	_comprobar(Estado.cuantos("nasa") == 3, "se recogen al pasar (%d/3)" % Estado.cuantos("nasa"))
	var sopas: int = Estado.cuantos("sopa")
	maisha.global_position = korongo.global_position + Vector2(0, 16)
	await _esperar(0.3)
	await _hablar_con(korongo)
	_comprobar(Estado.tiene("korongo_nasas") and Estado.cuantos("nasa") == 0, "se las entrega")
	_comprobar(Estado.cuantos("sopa") == sopas + 2, "y Korongo le da dos sopas")
	await _esperar(1.5)
	_comprobar(rota.arreglada(), "Korongo arregla la pasarela rota (tabla a tabla)")
	maisha.global_position = Vector2(100 * 16 + 8, 38 * 16 + 10)
	await _esperar(0.2)
	await _empujar("mover_derecha", 2.0)
	_comprobar(maisha.global_position.x > 106 * 16, "ahora se cruza hasta el islote del sureste (%.0f)" % maisha.global_position.x)

	print("El segundo eco perdido:")
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
	_comprobar(con_imagen, "el recuerdo tiene su ilustración (13_eco_pasarelas)")
	_comprobar(Estado.tiene("eco/las_pasarelas") and ECO.cuantos_escuchados() == 2, "segundo eco apuntado (2/9)")

	print("Hacia la ciénaga y de vuelta:")
	maisha.global_position = _puerta("cienaga").global_position + Vector2(-40, 0)
	await _cruzar("mover_derecha", "CienagaQuieta")
	_comprobar(_escena() == "CienagaQuieta", "por el este se llega a la Ciénaga Quieta")
	await _esperar(2.5)
	await _leer_dialogo()
	_maisha().global_position = _puerta("aldea").global_position + Vector2(30, 0)
	await _cruzar("mover_izquierda", "LasPasarelas")
	_comprobar(_escena() == "LasPasarelas", "y de la ciénaga se vuelve a Las Pasarelas")
	_comprobar(_maisha().global_position.distance_to(_puerta("cienaga").punto_llegada()) < 4.0, "apareciendo por el este")
	_maisha().global_position = _puerta("aldea").global_position + Vector2(40, 0)
	await _cruzar("mover_izquierda", "CunaDeMusgo")
	_comprobar(_escena() == "CunaDeMusgo", "y por el oeste, a la aldea")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
