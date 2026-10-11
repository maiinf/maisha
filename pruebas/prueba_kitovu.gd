extends Node
## Prueba automática del comienzo del juego: el Kitovu y la granja de Mzee Shamba.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_kitovu

const R := preload("res://scripts/combate/reglas_combate.gd")
const FORMA := preload("res://scripts/combate/forma_zona.gd")
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
	for i in 120:
		if not dialogo.hablando:
			# entre las partes de una historia hay un instante sin texto: esperar un poco
			await _esperar(0.3)
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


func _dialogo() -> Node:
	return get_tree().get_first_node_in_group("dialogo")


## Si hay un diálogo abierto (o a punto de abrirse), lo lee entero
func _atender(espera := 0.0) -> void:
	var t := 0.0
	while t < espera and not _dialogo().hablando:
		await get_tree().process_frame
		t += get_process_delta_time()
	if _dialogo().hablando:
		await _leer_dialogo()


func _usar(nodo: Node2D, desde := Vector2(0, 10)) -> void:
	_maisha().global_position = nodo.global_position + desde
	await _esperar(0.15)
	await _pulsar_accion()


func _entrar_en_casa() -> void:
	var puerta := _puerta("casa_shamba")
	_maisha().global_position = puerta.punto_llegada()
	await _cruzar("mover_arriba", "CasaDeShamba")


func _salir_de_casa() -> void:
	_maisha().global_position = _puerta("salida").punto_llegada()
	await _cruzar("mover_abajo", "Kitovu")


func _hablar_con_shamba() -> void:
	var shamba: Node2D = get_tree().get_nodes_in_group("aldeanos")[0]
	_maisha().global_position = shamba.global_position + Vector2(-18, 8)
	await _esperar(0.15)
	await _pulsar_accion()
	await _leer_dialogo()


## Distancia al borde de aviso de una zona (1.0 = justo en el borde), con su forma natural
func _lejos(zona: Node2D, p: Vector2) -> float:
	var n: Vector2 = (p - zona.global_position) / (zona.radios_umbral + Vector2.ONE * zona.ancho_borde)
	return n.length() / FORMA.factor(zona.forma, n)


## Un punto justo fuera del borde de aviso, al sur de la zona
func _fuera_del_borde(zona: Node2D) -> Vector2:
	var p: Vector2 = zona.global_position
	while _lejos(zona, p) < 1.0:
		p.y += 2.0
	return p + Vector2(0, 12)


## Un punto dentro de la zona, cerca de su umbral (al sur)
func _dentro(zona: Node2D) -> Vector2:
	var p: Vector2 = zona.global_position
	while zona.distancia_normal(p) < 0.8:
		p.y += 2.0
	return p


## Rompe el Corazón de una zona con semillas (como en la prueba de combate)
func _romper_corazon(zona: Node2D) -> void:
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.queue_free()
	zona.set("_invocar", 999.0)
	var nucleo: Node2D = zona.get("_nucleo")
	var c := R.casilla_de(nucleo.global_position)
	for v in nucleo.vida_maxima:
		var maisha := _maisha()
		maisha.aliento = R.ALIENTO_MAXIMO
		maisha.vida = R.VIDA_MAXIMA
		maisha.global_position = R.centro_de(c + Vector2i(-2, 0))
		maisha.lanzar_semilla()
		maisha.global_position = R.centro_de(c + Vector2i(-2, 2))
		await _esperar(0.1)
		await _atender()
		await _esperar(R.SEMILLA_MECHA + 0.2)
		for e in get_tree().get_nodes_in_group("enemigos"):
			e.queue_free()
	await _esperar(3.5)
	await _atender(3.0)


func _ready() -> void:
	Engine.time_scale = 3.0
	Estado.olvidar_todo()
	get_tree().change_scene_to_file("res://escenas/mundo/kitovu.tscn")
	await _esperar_cambio("Kitovu")

	print("El despertar:")
	await _atender(3.0)
	_comprobar(Estado.tiene("kitovu_despierta"), "Maisha despierta y se pregunta dónde está")
	var maisha := _maisha()
	_comprobar(not maisha.get_node("Ropa").lleva("cetro_raiz") and not maisha.combate_activo, "empieza sin cetro y sin poder luchar")
	Input.action_press("explosivo")
	await get_tree().process_frame
	await get_tree().process_frame
	Input.action_release("explosivo")
	_comprobar(get_tree().get_nodes_in_group("semillas").is_empty(), "sin cetro no hay semillas")
	_comprobar(maisha.lentitud < 0.9, "al despertar anda despacio, entumecida (%.2f)" % maisha.lentitud)
	await _atender(4.0)
	_comprobar(get_tree().get_nodes_in_group("chispas").size() == 1, "aparece una chispa de vida")

	print("Sin cetro no se entra en la zona corrupta:")
	var zona: Node2D = get_tree().get_nodes_in_group("zonas")[0]
	maisha.global_position = _fuera_del_borde(zona)
	await _empujar("mover_arriba", 1.5)
	await _atender(0.5)
	var lejos := _lejos(zona, maisha.global_position)
	_comprobar(zona.estado == 0 and lejos > 0.93, "la zona sigue dormida y Maisha no pasa del borde (%.2f)" % lejos)

	print("La granja y las ruinas:")
	var charlas: Array[String] = []
	for n in get_tree().get_nodes_in_group("interactuables"):
		if n.get("charla") != null:
			charlas.append(String(n.get("charla")))
	for c in ["kitovu_ruina", "kitovu_pozo", "kitovu_torre", "kitovu_monumento", "kitovu_carro", "kitovu_raiz_gigante"]:
		_comprobar(c in charlas, "se puede mirar: " + c)
	_comprobar(get_tree().get_nodes_in_group("gallinas").size() == 3, "hay 3 gallinas en la granja")
	var monumento: Node2D = null
	for n in get_tree().get_nodes_in_group("interactuables"):
		if n.get("charla") == "kitovu_monumento":
			monumento = n
	await _usar(monumento, Vector2(0, 12))
	_comprobar(_dialogo().hablando, "el monumento cuenta algo al mirarlo")
	await _leer_dialogo()

	print("Sin permiso no se toca el huerto:")
	var zanahorias := get_tree().get_nodes_in_group("zanahorias")
	_comprobar(zanahorias.size() == 8, "hay 8 zanahorias en el huerto")
	await _usar(zanahorias[0])
	await _atender(0.5)
	_comprobar(Estado.cuantos("zanahoria") == 0, "sin la tarea, Maisha no arranca nada")

	print("La puerta de la granja, cerrada:")
	var puerta_casa := _puerta("casa_shamba")
	maisha = _maisha()
	maisha.global_position = puerta_casa.punto_llegada() + Vector2(0, 16)
	await _esperar(0.3)
	await _empujar("mover_arriba", 0.6)
	await _esperar(0.3)
	_comprobar(_escena() == "Kitovu" and _dialogo().hablando, "nadie abre: dentro alguien refunfuña")
	await _leer_dialogo()

	print("La chispa de vida y los recuerdos:")
	var chispa: Node2D = get_tree().get_nodes_in_group("chispas")[0]
	for i in 3:
		chispa.ir_al_sitio()
		_maisha().global_position = chispa.sitios[i]
		await _esperar(0.4)
		for f in 60:
			if _dialogo().hablando:
				break
			await get_tree().process_frame
		await _leer_dialogo()
		var il: Texture2D = _dialogo().get("_ilustracion")
		_comprobar(Estado.tiene("recuerdo_%d" % (i + 1)) and il != null and il.resource_path.ends_with("recuerdo_%d.png" % (i + 1)), "recuerdo %d, con su imagen" % (i + 1))
	await _esperar(1.5)
	_comprobar(not is_instance_valid(chispa), "la chispa entra en el brote de Maisha")
	await _atender(4.0)
	_comprobar(Estado.tiene("kuku_perdida") and get_tree().get_nodes_in_group("gallina_perdida").size() == 1, "se oye cloquear: hay una gallina perdida")

	print("Kuku, la gallina perdida:")
	var kuku: Node2D = get_tree().get_nodes_in_group("gallina_perdida")[0]
	_maisha().global_position = kuku.global_position + Vector2(20, 0)
	await _esperar(0.6)
	_comprobar(kuku.get("_huidas") >= 1, "al acercarse, huye")
	_comprobar(not kuku.is_in_group("interactuables"), "y así no se deja coger")
	kuku.cansar()
	await _usar(kuku, Vector2(0, 8))
	await _esperar(0.2)
	_comprobar(Estado.tiene("kuku_cogida") and get_tree().current_scene.get("_llevada") != null, "cansada, se coge y Maisha la lleva en brazos")
	await _atender(1.0)

	print("En la puerta, con Kuku:")
	_maisha().global_position = puerta_casa.punto_llegada() + Vector2(0, 6)
	for f in 60:
		if _dialogo().hablando:
			break
		await get_tree().process_frame
	_comprobar(_dialogo().hablando and _dialogo().get("_nombre") == "Mzee Shamba", "Mzee Shamba sale a la puerta, desconfiado")
	await _leer_dialogo()
	await _atender(2.0)
	_comprobar(Estado.tiene("kuku_devuelta") and get_tree().get_nodes_in_group("gallinas").size() == 4, "al ver a Kuku se ablanda; Kuku vuelve a su granja")

	print("Mzee Shamba nota algo:")
	await _entrar_en_casa()
	_comprobar(_escena() == "CasaDeShamba", "se entra en la casa del castor")
	for i in 120:
		if _dialogo()._susurros.size() > 0:
			break
		await get_tree().process_frame
	_comprobar(_dialogo()._susurros.size() > 0, "al entrar, el castor susurra algo para sí")
	await _atender(4.0)
	_comprobar(Estado.tiene("shamba_noto") and Estado.tiene("cena_shamba") and not Estado.tiene("tarea_cosecha"), "luego se presenta y cenan (sin tareas todavía)")

	print("La noche y la mañana siguiente:")
	for i in 160:
		if Estado.tiene("tarea_cosecha"):
			break
		if _dialogo().hablando:
			await _leer_dialogo()
		await _esperar(0.25)
	_comprobar(Estado.tiene("amanecer_granja"), "anochece, Maisha duerme y amanece")
	_comprobar(Estado.tiene("tarea_cosecha"), "a la mañana siguiente, el castor pide las zanahorias")
	await _atender(1.0)

	print("Tarea 1: zanahorias")
	await _salir_de_casa()
	_comprobar(Estado.tiene("amanecer_visto"), "fuera, el valle amanece con luz anaranjada")
	for z in get_tree().get_nodes_in_group("zanahorias").slice(0, 5):
		await _usar(z)
		await _esperar(0.1)
	_comprobar(Estado.cuantos("zanahoria") == 5, "se arrancan 5 zanahorias (%d)" % Estado.cuantos("zanahoria"))
	await _entrar_en_casa()
	await _hablar_con_shamba()
	_comprobar(Estado.tiene("hecha_cosecha") and Estado.cuantos("zanahoria") == 0, "Mzee Shamba las recibe y pide un pez")

	print("Tarea 2: pescar")
	await _salir_de_casa()
	var sitio: Node2D = get_tree().get_nodes_in_group("sitios_pesca")[0]
	await _usar(sitio, Vector2(8, 6))
	_comprobar(sitio.fase == 1, "se lanza el anzuelo y se espera")
	await _pulsar_accion()
	await _esperar(0.2)
	_comprobar(Estado.cuantos("pez") == 0, "si se tira antes de que pique, el pez se espanta")
	await _esperar(1.4)
	await _usar(sitio, Vector2(8, 6))
	for i in 600:
		if sitio.fase == 2:
			break
		await get_tree().process_frame
	_comprobar(sitio.fase == 2, "¡pica!")
	sitio.marca_en_verde()
	await _pulsar_accion()
	await _esperar(0.5)
	_comprobar(Estado.cuantos("pez") == 1, "tirando en lo verde se pesca un pez")
	await _esperar(1.0)
	await _entrar_en_casa()
	await _hablar_con_shamba()
	_comprobar(Estado.tiene("tarea_cerca"), "Mzee Shamba recibe el pez y pide arreglar la cerca")

	print("Tarea 3: la cerca")
	await _salir_de_casa()
	var cerca: Node2D = get_tree().get_nodes_in_group("cercas")[0]
	await _usar(cerca, Vector2(0, 10))
	await _atender(0.5)
	_comprobar(not Estado.tiene("cerca_arreglada"), "sin tablas no se arregla")
	var tronco: Node2D = null
	for n in get_tree().get_nodes_in_group("interactuables"):
		if n.get_script().resource_path.ends_with("tronco.gd"):
			tronco = n
	await _usar(tronco, Vector2(0, 12))
	_comprobar(Estado.cuantos("tablas") == 1, "del tronco salen las tablas")
	await _usar(cerca, Vector2(0, 10))
	await _esperar(0.5)
	_comprobar(Estado.tiene("cerca_arreglada") and Estado.cuantos("tablas") == 0, "con las tablas se arregla la cerca")

	print("El cetro y el mapa:")
	await _entrar_en_casa()
	await _hablar_con_shamba()
	await _atender(2.5)
	_comprobar(Estado.tiene("cetro_recibido") and Estado.tiene("mapa_partido"), "Mzee Shamba da el Cetro de Raíz y el mapa partido")
	var ilustracion: Texture2D = _dialogo().get("_ilustracion")
	_comprobar(ilustracion != null and ilustracion.resource_path.ends_with("6_hoy.png"), "cuenta la historia con ilustraciones, hasta la última")
	_comprobar(_maisha().get_node("Ropa").lleva("cetro_raiz"), "Maisha lleva el cetro")
	_comprobar(not get_tree().current_scene._cetro.visible, "el cetro ya no está en la pared")
	await _salir_de_casa()
	await _atender(2.0)
	_comprobar(Estado.tiene("narr/cetro"), "el narrador explica el golpe")
	maisha = _maisha()
	_comprobar(maisha.combate_activo, "ya se puede luchar")
	var espantapajaros: Node2D = get_tree().get_nodes_in_group("espantapajaros")[0]
	maisha.global_position = espantapajaros.global_position + Vector2(-14, 2)
	maisha.mirar(Vector2.RIGHT)
	for i in 3:
		await _esperar(0.4)
		maisha.golpear()
	await _atender(1.5)
	_comprobar(Estado.tiene("narr/espantapajaros"), "tras 3 golpes al espantapájaros, el narrador señala el arco")

	print("La mochila:")
	await get_tree().process_frame
	Input.action_press("mochila")
	await get_tree().process_frame
	await get_tree().process_frame
	Input.action_release("mochila")
	var mochila := get_tree().get_first_node_in_group("mochila")
	_comprobar(mochila.abierta and get_tree().paused, "Tab abre la mochila y para el juego")
	_comprobar(mochila.pestana == 0 and mochila._lista().size() >= 3, "empieza en el diario de misiones (%d misiones)" % mochila._lista().size())
	mochila.pestana = 1
	var nombres: Array = mochila._lista().map(func(f: Dictionary) -> String: return f["nombre"])
	_comprobar("Cetro de Raíz" in nombres and "Mapa partido" in nombres, "en Objetos están el cetro y el mapa (%s)" % [nombres])
	mochila.pestana = 2
	var habilidades: int = mochila._lista().filter(func(f: Dictionary) -> bool: return not f.get("apagada", false)).size()
	_comprobar(habilidades == 3, "en Habilidades: golpe, semilla y Latido (%d)" % habilidades)
	mochila.pestana = 4
	_comprobar(mochila._lista().size() == 1, "en Lazos: Mzee Shamba")
	mochila.cerrar()
	_comprobar(not get_tree().paused, "al cerrarla, el juego sigue")

	print("Las manchas de Giza (zonas de práctica):")
	var practicas: Array = get_tree().get_nodes_in_group("zonas").filter(func(z: Node2D) -> bool: return z.jefe == "")
	var arena: Node2D = get_tree().get_nodes_in_group("arena_jefe")[0]
	_comprobar(practicas.size() == 3, "en esta partida hay 3 manchas (%d)" % practicas.size())
	_comprobar(practicas.all(func(z: Node2D) -> bool: return z.pequena and z.activa and z.forma.size() == 8), "son pequeñas, están despiertas y tienen forma natural")
	_comprobar(not arena.activa, "la arena de Mzizi sigue dormida")
	for i in practicas.size():
		zona = practicas[i]
		maisha = _maisha()
		# entra andando desde fuera del borde (como un jugador), no de un salto
		var desde := _fuera_del_borde(zona) + Vector2(0, 8)
		var hasta := _dentro(zona)
		for paso in 24:
			maisha.global_position = desde.lerp(hasta, paso / 23.0)
			await get_tree().physics_frame
			if paso == 8:
				await _atender(1.0)
		await _esperar(0.4)
		await _atender(2.0)
		_comprobar(zona.estado == 2, "mancha %d: las raíces de piedra encierran a Maisha" % (i + 1))
		if i == 0:
			_comprobar(Estado.tiene("narr/zona") and Estado.tiene("narr/cerrada"), "el narrador presenta la mancha y explica el golpe")
			var petrino: Node2D = get_tree().get_nodes_in_group("enemigos")[0]
			petrino.call("morir")
			await _esperar(0.8)
			await _atender(1.5)
			_comprobar(Estado.tiene("narr/nucleo"), "al caer un Petrino, el narrador explica las semillas")
		elif i == 1:
			_comprobar(Estado.tiene("narr/zona2"), "en la segunda, el narrador enseña el Latido")
		await _romper_corazon(zona)
		_comprobar(zona.estado == 4, "mancha %d purgada (con %d semillas)" % [i + 1, R.NUCLEO_VIDA_PEQUENO])
	await _esperar(1.0)
	await _atender(2.0)
	_comprobar(Estado.tiene("narr/despierta") and arena.activa, "limpias las tres, la tierra tiembla y la arena despierta")

	print("Mzizi, la raíz del Arco:")
	maisha = _maisha()
	maisha.global_position = _fuera_del_borde(arena) - Vector2(0, 16)
	await _esperar(0.3)
	await _atender(1.0)
	_comprobar(Estado.tiene("narr/arena"), "el narrador avisa al llegar a la arena")
	maisha.global_position = _dentro(arena)
	await _esperar(0.5)
	var mzizi: Node2D = get_tree().get_first_node_in_group("jefes")
	_comprobar(arena.estado == 2 and mzizi.fase == mzizi.Fase.PRESENTACION, "la arena se cierra y Mzizi sale rugiendo")
	await _esperar(1.8)
	await _atender(2.0)
	_comprobar(Estado.tiene("narr/mzizi") and mzizi.get("_barra") != null, "el narrador la presenta y sale su barra de vida")
	# el cetro no le hace nada
	var vida_antes: int = mzizi.vida
	mzizi.recibir_golpe(1, Vector2.RIGHT)
	_comprobar(mzizi.vida == vida_antes, "el cetro rebota en su piedra")
	var golpes := 0
	for intento in 12:
		if golpes >= R.MZIZI_VIDA:
			break
		maisha = _maisha()
		maisha.vida = R.VIDA_MAXIMA
		maisha.aliento = R.ALIENTO_MAXIMO
		# espera a que avise un agujero y planta una semilla a su lado
		for f in 200:
			if mzizi.fase == mzizi.Fase.AVISO:
				break
			await get_tree().process_frame
		var c := R.casilla_de(mzizi.global_position)
		# la primera vez, varias semillas a la vez alrededor del agujero: cada una debe contar
		var varias := intento == 0
		# la segunda vez, tres semillas soltadas una detrás de otra (estallan escalonadas): también cuentan todas
		var seguidas := intento == 1
		for off in ([Vector2i(-1, 0), Vector2i(1, 0), Vector2i(0, 1)] if varias or seguidas else [Vector2i(-2, 0)]):
			maisha.global_position = R.centro_de(c + off)
			await get_tree().physics_frame
			maisha.lanzar_semilla()
			if seguidas:
				await _esperar(0.35)
		maisha.global_position = R.centro_de(c + Vector2i(-3, 3))
		var antes: int = mzizi.vida
		await _esperar(R.SEMILLA_MECHA + 0.3)
		if varias:
			_comprobar(antes - mzizi.vida == 3, "tres semillas a la vez: le quitan tres trozos de vida (%d)" % (antes - mzizi.vida))
		if seguidas:
			await _esperar(0.8)
			_comprobar(antes - mzizi.vida == 3, "tres semillas seguidas (estallan una tras otra): las tres cuentan (%d)" % (antes - mzizi.vida))
		golpes += antes - mzizi.vida
	_comprobar(golpes == R.MZIZI_VIDA, "%d semillas al salir de su agujero la vencen (%d)" % [R.MZIZI_VIDA, golpes])
	_comprobar(mzizi.fase == mzizi.Fase.VENCIDO, "Mzizi se rinde: la piedra se cae y debajo hay madera")
	for e in get_tree().get_nodes_in_group("piedras_mzizi"):
		e.queue_free()
	await _esperar(6.5)
	await _atender(3.0)
	_comprobar(arena.estado == 4, "la arena queda purgada")
	await _esperar(0.5)
	_comprobar(Estado.tiene("portal_raiz"), "el Arco de Raíz despierta")
	var il_final: Texture2D = _dialogo().get("_ilustracion")
	_comprobar(il_final != null and il_final.resource_path.ends_with("8_arco_despierta.png"), "el narrador lo cuenta con las cinemáticas de Mzizi y del Arco")
	_comprobar(_puerta("raiz") != null, "el arco tiene ya su paso abierto")

	print("Al otro lado del arco:")
	maisha = _maisha()
	maisha.global_position = _puerta("raiz").punto_llegada()
	await _cruzar("mover_arriba", "PradosDelEco")
	_comprobar(_escena() == "PradosDelEco", "el arco lleva a los Prados del Eco")
	_comprobar(_maisha().global_position.distance_to(_puerta("kitovu").punto_llegada()) < 4.0, "Maisha llega por el arco del claro de columnas")
	_comprobar(_maisha().get_node("Ropa").lleva("cetro_raiz") and _maisha().combate_activo, "con su cetro")
	_maisha().global_position = _puerta("kitovu").punto_llegada()
	await _cruzar("mover_arriba", "Kitovu")
	_comprobar(_escena() == "Kitovu" and _maisha().global_position.distance_to(_puerta("raiz").punto_llegada()) < 4.0, "y se puede volver al Kitovu")
	_comprobar(get_tree().get_nodes_in_group("zonas").all(func(z: Node2D) -> bool: return z.estado == 4), "las manchas y la arena siguen purgadas")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	await Sonido.callar()
	get_tree().quit(_fallos)
