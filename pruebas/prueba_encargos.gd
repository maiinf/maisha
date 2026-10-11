extends Node
## Prueba automática de los encargos: setas luminosas, mineral, reconstrucción e interiores.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_encargos

const R := preload("res://scripts/combate/reglas_combate.gd")
const CHARLA := preload("res://scripts/mundo/charla.gd")
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


func _pulsar_accion() -> void:
	# se pulsa al empezar un fotograma (como una tecla de verdad), no a mitad
	await get_tree().process_frame
	Input.action_press("accion")
	await get_tree().process_frame
	await get_tree().process_frame
	Input.action_release("accion")
	await get_tree().process_frame


## Pasa todas las líneas del diálogo abierto
func _leer_dialogo() -> int:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	var lineas := 0
	for i in 60:
		if not dialogo.hablando:
			break
		await _pulsar_accion()
		await _pulsar_accion()
		lineas += 1
	await _esperar(0.25)
	return lineas


## Camina en una dirección hasta cruzar una puerta y llegar a la escena «nombre»
func _cruzar(accion: String, nombre: String) -> void:
	Input.action_press(accion)
	for i in 400:
		if Estado.cambiando:
			break
		await get_tree().process_frame
	Input.action_release(accion)
	await _esperar_cambio(nombre)


## Espera a que termine un cambio de escena
func _esperar_cambio(nombre: String) -> void:
	for i in 300:
		if _escena() == nombre and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(0.2)


## Purga una zona de los prados con semillas, como en prueba_prados
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
		maisha.aliento = R.ALIENTO_MAXIMO
		maisha.vida = R.VIDA_MAXIMA
		maisha.global_position = R.centro_de(c + Vector2i(-2, 0))
		maisha.lanzar_semilla()
		maisha.global_position = R.centro_de(c + Vector2i(-3, 3))
		await _esperar(R.SEMILLA_MECHA + 0.2)


func _hablar_con(nodo: Node2D) -> void:
	_maisha().global_position = nodo.global_position + Vector2(0, 16)
	await _esperar(0.1)
	await _pulsar_accion()
	await _leer_dialogo()


func _aldeano(id: String) -> Node2D:
	for a in get_tree().get_nodes_in_group("aldeanos"):
		if a.id == id and not a.is_queued_for_deletion():
			return a
	return null


func _edificio(id: String) -> Node2D:
	for e in get_tree().get_nodes_in_group("edificios"):
		if e.id == id:
			return e
	return null


func _ir_a_prados_desde_aldea() -> void:
	_maisha().global_position = _puerta("prados").global_position + Vector2(30, 0)
	await _por_el_sendero("mover_izquierda", "PradosDelEco")


func _ir_a_aldea_desde_prados() -> void:
	_maisha().global_position = _puerta("aldea").global_position + Vector2(-40, 0)
	await _por_el_sendero("mover_derecha", "CunaDeMusgo")


func _ready() -> void:
	Engine.time_scale = 3.0
	Estado.olvidar_todo()
	Estado.marcar("cetro_recibido")       # en los prados, Maisha ya trae el cetro del Kitovu
	get_tree().change_scene_to_file("res://escenas/mundo/prados_del_eco.tscn")
	await _esperar_cambio("PradosDelEco")

	print("Setas luminosas:")
	var setas := get_tree().get_nodes_in_group("recogibles")
	_comprobar(setas.size() == 4, "hay 4 setas luminosas en los prados (%d)" % setas.size())
	for i in 3:
		_maisha().global_position = setas[i].global_position
		await _esperar(0.2)
	_comprobar(Estado.cuantos("seta_luminosa") == 3, "al pasar por encima se recogen (%d)" % Estado.cuantos("seta_luminosa"))

	print("Mineral:")
	var rocas := get_tree().get_nodes_in_group("rocas_mineral")
	_comprobar(rocas.size() == 3, "hay 3 rocas con mineral (%d)" % rocas.size())
	var maisha := _maisha()
	var roca: Node2D = rocas[0]
	maisha.global_position = roca.global_position + Vector2(-14, 3)
	maisha.mirar(Vector2.RIGHT)
	await _esperar(0.1)
	maisha.golpear()
	await _esperar(0.5)
	_comprobar(not roca.rota, "el cetro rebota en la roca")
	for i in 2:
		roca = rocas[i]
		maisha.aliento = R.ALIENTO_MAXIMO
		maisha.global_position = R.centro_de(R.casilla_de(roca.global_position) + Vector2i(-1, 0))
		maisha.lanzar_semilla()
		maisha.global_position = R.centro_de(R.casilla_de(roca.global_position) + Vector2i(-3, 3))
		await _esperar(R.SEMILLA_MECHA + 0.4)
		_comprobar(roca.rota, "una semilla rompe la roca %d" % (i + 1))
		var minerales := get_tree().get_nodes_in_group("recogibles").filter(func(r: Node) -> bool: return r.objeto == "mineral")
		maisha.global_position = minerales[0].global_position
		await _esperar(0.3)
	_comprobar(Estado.cuantos("mineral") == 2, "se recogen 2 trozos de mineral (%d)" % Estado.cuantos("mineral"))

	print("Sin templar, el cetro no llega lejos:")
	var piedra: Node2D = get_tree().get_nodes_in_group("piedras_eco")[0]
	maisha.vida = R.VIDA_MAXIMA
	maisha.global_position = piedra.global_position + Vector2(-29, 3)
	maisha.mirar(Vector2.RIGHT)
	await _esperar(0.1)
	maisha.golpear()
	await _esperar(0.5)
	_comprobar(not piedra.encendida_ya, "a 29 píxeles el golpe no llega")

	print("Los prados recuerdan lo recogido:")
	Estado.marcar("rescatado_pino")
	Estado.marcar("rescatado_corteza")
	await _ir_a_aldea_desde_prados()
	await _ir_a_prados_desde_aldea()
	_comprobar(get_tree().get_nodes_in_group("recogibles").size() == 1, "solo queda la seta que no se cogió")
	var rotas := get_tree().get_nodes_in_group("rocas_mineral").filter(func(r: Node) -> bool: return r.rota).size()
	_comprobar(rotas == 2, "las 2 rocas siguen rotas (%d)" % rotas)
	_comprobar(get_tree().get_nodes_in_group("secretos").all(func(s: Node) -> bool: return s.get("_haz") == null), "aún no hay haces de luz sobre los secretos")

	print("Encargo de Pino:")
	await _ir_a_aldea_desde_prados()
	var pino := _aldeano("pino")
	await _hablar_con(pino)
	_comprobar(Estado.tiene("encargo_pino"), "Pino hace su encargo")
	_comprobar(CHARLA.tiene_novedad("pino"), "con 3 setas, Pino tiene algo nuevo (!)")
	await _hablar_con(pino)
	await _esperar(2.5)
	await _leer_dialogo()
	_comprobar(Estado.tiene("construido_casa_seta") and Estado.tiene("vigia"), "al darle las setas, se reconstruye su casa y llega el vigía")
	_comprobar(Estado.cuantos("seta_luminosa") == 0, "las setas se han entregado")
	_comprobar(_edificio("casa_seta")._sprite.frame == 1, "la casa-seta se ve reconstruida")
	_comprobar(_puerta("casa_seta") != null, "la casa-seta tiene puerta")

	print("Encargo de Corteza:")
	var corteza := _aldeano("corteza")
	await _hablar_con(corteza)
	await _hablar_con(corteza)
	await _esperar(2.5)
	await _leer_dialogo()
	_comprobar(Estado.tiene("construido_taller") and Estado.tiene("cetro_templado"), "con 2 trozos de mineral, el taller se levanta y templa el cetro")
	await _esperar(6.0)
	_comprobar(_aldeano("corteza") == null, "Corteza se mete en su taller")

	print("Dentro de la casa de Pino:")
	_maisha().global_position = _puerta("casa_seta").punto_llegada()
	await _cruzar("mover_arriba", "CasaDePino")
	_comprobar(_escena() == "CasaDePino", "por la puerta de la seta se entra en su casa")
	_maisha().global_position = Vector2(118, 96)
	await _esperar(0.1)
	await _pulsar_accion()
	_comprobar(get_tree().get_first_node_in_group("dialogo").hablando, "se puede mirar el mapa de Pino")
	await _leer_dialogo()
	await _empujar("mover_arriba", 1.5)
	_comprobar(_maisha().global_position.y > 80.0, "la pared del fondo no se atraviesa (y = %d)" % _maisha().global_position.y)
	_maisha().global_position = _puerta("salida").punto_llegada()
	await _cruzar("mover_abajo", "CunaDeMusgo")
	_comprobar(_maisha().global_position.distance_to(_puerta("casa_seta").punto_llegada()) < 4.0, "al salir, Maisha aparece delante de la casa-seta")

	print("Dentro del taller:")
	_maisha().global_position = _puerta("taller").punto_llegada()
	await _cruzar("mover_arriba", "TallerDeCorteza")
	_comprobar(_escena() == "TallerDeCorteza", "por la puerta del taller se entra")
	_comprobar(_aldeano("corteza") != null, "Corteza está dentro, junto al yunque")
	_maisha().global_position = _puerta("salida").punto_llegada()
	await _cruzar("mover_abajo", "CunaDeMusgo")

	print("Recompensas en los prados:")
	await _ir_a_prados_desde_aldea()
	var haces := get_tree().get_nodes_in_group("secretos").filter(func(s: Node) -> bool: return s.get("_haz") != null).size()
	_comprobar(haces == get_tree().get_nodes_in_group("secretos").size() and haces > 0, "los secretos lanzan su haz de luz (%d)" % haces)
	piedra = get_tree().get_nodes_in_group("piedras_eco")[0]
	maisha = _maisha()
	maisha.global_position = piedra.global_position + Vector2(-29, 3)
	maisha.mirar(Vector2.RIGHT)
	await _esperar(0.1)
	maisha.golpear()
	await _esperar(0.5)
	_comprobar(piedra.encendida_ya, "con el cetro templado, el golpe llega a 29 píxeles")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	await Sonido.callar()
	get_tree().quit(_fallos)


## Desde la entrada de los prados hasta la aldea: se cruza el Sendero del Puente (dos cambios de escena)
func _por_el_sendero(accion: String, nombre: String) -> void:
	var sendero_puerta := "aldea" if accion == "mover_derecha" else "prados"
	await _cruzar(accion, "SenderoDelPuente")
	var p := _puerta(sendero_puerta)
	_maisha().global_position = p.global_position + (Vector2(-40, 0) if accion == "mover_derecha" else Vector2(40, 0))
	await _esperar(0.2)
	await _cruzar(accion, nombre)
