extends Node
## Prueba automática de la Senda de los Surcos (el cuarto camino de Raíz): de Cuna de Musgo al Campo Segado;
## el cuervo de óxido (enemigo nuevo), Sungura y sus mazorcas, la acequia, el foso que se vacía y el cuarto eco.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_senda_surcos

const R := preload("res://scripts/combate/reglas_combate.gd")
const ECO := preload("res://scripts/mundo/objetos/eco_perdido.gd")
const CUERVO := preload("res://scripts/enemigos/cuervo.gd")
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
			"visto/cuna_de_musgo", "bibi_conocida", "bibi_aldea_viva", "camino_bosque", "camino_cienaga", "camino_campo",
			"eco/sendero_del_puente", "eco/las_pasarelas", "eco/camino_cobrizo"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("De la aldea a la Senda de los Surcos:")
	Estado.llegada = "prados"
	get_tree().change_scene_to_file("res://escenas/mundo/cuna_de_musgo.tscn")
	await _esperar(1.5)
	var norte := _puerta("campo")
	_comprobar(norte != null and norte.destino == "senda_surcos", "el camino del norte de la aldea lleva a la Senda de los Surcos")
	await _leer_dialogo()
	_maisha().global_position = norte.global_position + Vector2(0, 30)
	await _cruzar("mover_arriba", "SendaSurcos")
	_comprobar(_escena() == "SendaSurcos", "se llega a la Senda de los Surcos")
	_comprobar(_maisha().global_position.distance_to(_puerta("aldea").punto_llegada()) < 4.0, "Maisha aparece al sur, viniendo de la aldea")
	await _esperar(2.5)
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "Maisha piensa algo al llegar")
	await _leer_dialogo()

	print("La Senda de los Surcos:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	_comprobar(region.tam.y >= 100 * 16, "sube de sur a norte: unas 4 pantallas de alto")
	var zonas := get_tree().get_nodes_in_group("zonas")
	_comprobar(zonas.size() == 1 and zonas[0].tipos_enemigo.has("cuervo"), "una zona corrupta, donde salen cuervos de óxido")
	_comprobar(region.secretos_total == 1, "un secreto en el seto del oeste")
	var mazorcas := get_tree().get_nodes_in_group("recogibles").filter(func(n: Node) -> bool: return n.objeto == "mazorca")
	_comprobar(mazorcas.size() == 3, "tres mazorcas de Sungura")
	var sungura: Node2D = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "sungura")[0]
	_comprobar(sungura != null, "Sungura, la liebre guardasemillas, junto a su hórreo")
	var foso: Node2D = get_tree().get_first_node_in_group("acequias")
	_comprobar(foso != null and not foso.vacia(), "el huerto del eco está rodeado de agua")
	_comprobar(_puerta("campo") != null and _puerta("campo").destino == "campo_segado", "al norte, el Campo Segado")
	for z in zonas:
		z.set("activa", false)          # (aquí no se pelea con la zona: se prueba el cuervo a mano)

	print("La acequia y el foso:")
	var maisha := _maisha()
	maisha.global_position = Vector2(30 * 16 + 16, 68 * 16)
	await _esperar(0.2)
	await _empujar("mover_arriba", 1.6)
	_comprobar(maisha.global_position.y < 62 * 16, "por el puentecito se cruza la acequia (%.0f)" % maisha.global_position.y)
	maisha.global_position = Vector2(20 * 16, 67 * 16)
	await _esperar(0.2)
	await _empujar("mover_arriba", 1.2)
	_comprobar(maisha.global_position.y > 65 * 16, "fuera del puente, el agua no deja pasar (%.0f)" % maisha.global_position.y)
	maisha.global_position = Vector2(41 * 16, 18 * 16 + 8)
	await _esperar(0.2)
	await _empujar("mover_derecha", 1.4)
	_comprobar(maisha.global_position.x < 44 * 16, "el foso no deja entrar en el huerto (%.0f)" % maisha.global_position.x)

	print("El cuervo de óxido:")
	var zona: Node2D = zonas[0]
	var cuervo: CharacterBody2D = CUERVO.new()
	cuervo.position = zona.global_position
	region.get_node(region.entidades).add_child(cuervo)
	maisha.global_position = zona.global_position + Vector2(50, 10)
	maisha.vida = maisha.vida_maxima()
	await _esperar(0.3)
	_comprobar(cuervo.en_el_aire() and not cuervo.recibir_golpe(1, Vector2.LEFT) and cuervo.vida == R.CUERVO_VIDA, "volando no se le puede dar")
	var apunto := false
	for i in 120:
		await _esperar(0.05)
		if cuervo.fase == cuervo.Fase.APUNTA:
			apunto = true
			break
	_comprobar(apunto, "al ver a Maisha cerca, se para y apunta (raya en el suelo)")
	var pico := false
	for i in 60:
		await _esperar(0.05)
		if cuervo.fase == cuervo.Fase.PICADO:
			pico = true
		if cuervo.fase == cuervo.Fase.POSADO:
			break
	_comprobar(pico and cuervo.fase == cuervo.Fase.POSADO, "se lanza en picado y se queda posado")
	_comprobar(maisha.vida < maisha.vida_maxima(), "y si Maisha estaba en la raya, el picado le hace daño")
	_comprobar(cuervo.recibir_golpe(1, Vector2.LEFT) and cuervo.vida == R.CUERVO_VIDA - 2, "posado, el cetro le quita 2")
	cuervo.enraizar(2.5)
	await _esperar(R.CUERVO_POSADO + 0.2)
	_comprobar(cuervo.fase == cuervo.Fase.POSADO, "las raíces de una semilla no lo dejan despegar")
	await _esperar(1.5)
	_comprobar(cuervo.en_el_aire(), "y cuando se sueltan, vuelve a subir")
	cuervo.recibir_danio(1, cuervo.global_position, "explosion")
	_comprobar(cuervo.get("_muriendo"), "la explosión le da aunque vuele: se deshace")
	maisha.vida = maisha.vida_maxima()

	print("Sungura y sus mazorcas:")
	maisha.global_position = sungura.global_position + Vector2(0, 16)
	await _hablar_con(sungura)
	_comprobar(Estado.tiene("encargo_sungura") and Estado.tiene("sungura_conocida"), "Sungura pide sus tres mazorcas")
	_comprobar(Misiones.activas().any(func(m: Dictionary) -> bool: return m["id"] == "mazorcas_sungura"), "sale el encargo en el diario")
	for n in mazorcas:
		maisha.global_position = n.global_position
		await _esperar(0.25)
	_comprobar(Estado.cuantos("mazorca") == 3, "se recogen al pasar (%d/3)" % Estado.cuantos("mazorca"))
	var sopas: int = Estado.cuantos("sopa")
	maisha.global_position = sungura.global_position + Vector2(0, 16)
	await _esperar(0.3)
	await _hablar_con(sungura)
	_comprobar(Estado.tiene("sungura_mazorcas") and Estado.cuantos("mazorca") == 0, "se las entrega")
	_comprobar(Estado.cuantos("sopa") == sopas + 2, "y Sungura le da dos sopas")
	await _esperar(2.0)
	_comprobar(foso.vacia(), "Sungura cierra la compuerta y el foso se vacía")
	maisha.global_position = Vector2(41 * 16, 18 * 16 + 8)
	await _esperar(0.2)
	await _empujar("mover_derecha", 1.6)
	_comprobar(maisha.global_position.x > 46 * 16, "ahora se entra en el huerto por el barro (%.0f)" % maisha.global_position.x)

	print("El cuarto eco perdido:")
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
	_comprobar(con_imagen, "el recuerdo tiene su ilustración (15_eco_surcos)")
	_comprobar(Estado.tiene("eco/senda_surcos") and ECO.cuantos_escuchados() == 4, "cuarto eco apuntado (4/9)")

	print("Al campo y de vuelta:")
	maisha.global_position = _puerta("campo").global_position + Vector2(0, 40)
	await _cruzar("mover_arriba", "CampoSegado")
	_comprobar(_escena() == "CampoSegado", "por el norte se llega al Campo Segado")
	await _esperar(2.5)
	await _leer_dialogo()
	_maisha().global_position = _puerta("aldea").global_position + Vector2(0, -30)
	await _cruzar("mover_abajo", "SendaSurcos")
	_comprobar(_escena() == "SendaSurcos", "y del campo se baja a la Senda de los Surcos")
	_comprobar(_maisha().global_position.distance_to(_puerta("campo").punto_llegada()) < 4.0, "apareciendo por el norte")
	_maisha().global_position = _puerta("aldea").global_position + Vector2(0, -40)
	await _cruzar("mover_abajo", "CunaDeMusgo")
	_comprobar(_escena() == "CunaDeMusgo", "y por el sur, a la aldea")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
