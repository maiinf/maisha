extends Node
## Prueba automática del Paso de la Escarcha (Sigilia): la puerta del norte de las Ruinas (cerrada hasta curar al
## Primer Árbol), la nieve honda (frena y deja surcos), la ventisca (empuja salvo cobijada) y las puertas.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_paso_escarcha

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _maisha() -> CharacterBody2D:
	return get_tree().get_first_node_in_group("maisha") as CharacterBody2D


func _escena() -> String:
	var e := get_tree().current_scene
	return e.name if e else ""


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 120:
		if not dialogo.hablando:
			await _esperar(0.3)
			if not dialogo.hablando:
				return
		dialogo.pasar()
		await _esperar(0.08)


func _puerta(id: String) -> Area2D:
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == id:
			return p
	return null


## Anda en una dirección un rato y devuelve cuánto se ha movido
func _andar(accion: String, segundos: float) -> float:
	var m := _maisha()
	var antes := m.global_position
	Input.action_press(accion)
	await _esperar(segundos)
	Input.action_release(accion)
	return m.global_position.distance_to(antes)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["cetro_recibido", "visto/cuna_de_musgo", "sendero_abierto", "sendero_olvidado"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("Las Ruinas, antes de curar al árbol:")
	get_tree().change_scene_to_file("res://escenas/mundo/ruinas_primer_arbol.tscn")
	await _esperar(1.5)
	var norte := _puerta("escarcha")
	_comprobar(norte != null and norte.destino == "paso_escarcha", "las Ruinas tienen un paso al norte, hacia el Paso de la Escarcha")
	_comprobar(norte != null and norte.cerrada_hasta == "primer_arbol_libre", "cerrado hasta curar al Primer Árbol")

	print("El Paso de la Escarcha:")
	Estado.marcar("primer_arbol_libre")
	Estado.ir_a("paso_escarcha", "sur")
	for i in 300:
		if _escena() == "PasoEscarcha" and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(1.0)
	_comprobar(_escena() == "PasoEscarcha" and Estado.tiene("paso_escarcha"), "se llega al Paso de la Escarcha")
	var m := _maisha()
	_comprobar(m.global_position.y > 100 * 16 - 200, "Maisha aparece abajo, en la puerta del sur")
	await _esperar(1.5)
	await _leer_dialogo()
	_comprobar(Estado.tiene("escarcha_llegada"), "Maisha piensa en la nieve lila al llegar")
	var escena := get_tree().current_scene
	var ventisca: Node2D = escena.ventisca
	var nieve: Node2D = escena.nieve
	_comprobar(get_tree().get_nodes_in_group("puertas").size() >= 2, "tiene sus dos puertas (sur y norte)")
	_comprobar(_puerta("ciudad") != null and _puerta("ciudad").destino == "maandiko", "la del norte lleva a Maandiko")

	# (las páginas sueltas, quietas hasta su apartado: así no empujan a Maisha en las otras comprobaciones)
	for p in get_tree().get_nodes_in_group("paginas"):
		p.set_physics_process(false)

	print("La nieve honda:")
	ventisca.activa = false
	# en el sendero: anda normal
	m.global_position = Vector2(29 * 16 + 8, 104 * 16 + 8)
	await _esperar(0.3)
	var en_sendero := await _andar("mover_arriba", 0.8)
	_comprobar(not nieve.es_honda(Vector2i((m.global_position / 16.0).floor())), "el sendero pisado no es nieve honda")
	# fuera del sendero, al este: se hunde
	m.global_position = Vector2(44 * 16 + 8, 104 * 16 + 8)
	await _esperar(0.3)
	var en_nieve := await _andar("mover_arriba", 0.8)
	_comprobar(en_nieve < en_sendero * 0.75, "en la nieve honda va mucho más despacio (%d frente a %d px)" % [en_nieve, en_sendero])
	_comprobar(m.hundida > 0.0 or en_nieve < en_sendero, "y se hunde")
	var surco := Vector2i(44, 103)
	_comprobar(nieve.tiene_surco(surco) or nieve.tiene_surco(Vector2i(44, 102)), "por donde ha pasado queda un surco")
	m.global_position = Vector2(44 * 16 + 8, 104 * 16 + 8)
	await _esperar(0.3)
	var por_surco := await _andar("mover_arriba", 0.5)
	_comprobar(por_surco > en_nieve * 0.75, "por su propio surco ya no se hunde tanto")
	Input.action_press("correr")
	m.global_position = Vector2(46 * 16 + 8, 100 * 16 + 8)
	await _esperar(0.2)
	Input.action_press("mover_abajo")
	await _esperar(0.3)
	_comprobar(not m.corriendo, "en la nieve honda no puede correr")
	Input.action_release("mover_abajo")
	Input.action_release("correr")

	print("La ventisca:")
	# fuera de cobijo, en medio del valle: la racha la empuja al este
	m.global_position = Vector2(30 * 16 + 8, 90 * 16 + 8)
	await _esperar(0.2)
	ventisca.activa = true
	ventisca.desde = -1
	ventisca.fase = ventisca.Fase.RACHA
	ventisca.set("_t", 2.0)
	var x0 := m.global_position.x
	await _esperar(1.2)
	_comprobar(not ventisca.cobijada, "en medio del valle no hay cobijo")
	_comprobar(m.global_position.x > x0 + 20, "la racha del oeste la empuja al este (%d px)" % int(m.global_position.x - x0))
	# cobijada: justo al este de una estela
	var estela := Vector2(19 * 16 + 8, 96 * 16 + 14)
	m.global_position = estela + Vector2(16, -2)
	await _esperar(0.2)
	ventisca.fase = ventisca.Fase.RACHA
	ventisca.set("_t", 2.0)
	x0 = m.global_position.x
	await _esperar(0.8)
	_comprobar(ventisca.cobijada, "detrás de una estela está cobijada")
	_comprobar(absf(m.global_position.x - x0) < 6, "y el viento no la mueve")
	ventisca.fase = ventisca.Fase.CALMA
	ventisca.set("_t", 30.0)
	await _esperar(0.6)
	_comprobar(m.viento.length() < 1.0, "al pasar la racha, el viento se apaga (no se queda empujando)")
	await _leer_dialogo()

	print("Taa, el farolero en blanco:")
	ventisca.activa = false
	var taa: Node = null
	for a in get_tree().get_nodes_in_group("aldeanos"):
		if String(a.id).begins_with("taa"):
			taa = a
	_comprobar(taa != null and taa.id == "taa_blanco", "a media subida está Taa, en blanco (sin nombre)")
	var faroles := get_tree().get_nodes_in_group("faroles_runicos")
	_comprobar(faroles.size() == 6 and faroles.all(func(f: Node) -> bool: return not f.encendido), "seis faroles rúnicos, todos apagados")
	# sin el sigilo, U no hace nada
	_comprobar(not m.sigilo(), "sin haberlo aprendido, no hay sigilo")
	m.global_position = (taa as Node2D).global_position + Vector2(-14, 4)
	taa.interactuar()
	await _leer_dialogo()
	_comprobar(Estado.tiene("taa_visto") and not Estado.tiene("taa_nombre"), "Maisha nota que está en blanco y le falta algo")
	var ficha: Node2D = null
	for r in get_tree().get_nodes_in_group("recogibles"):
		if r.objeto == "ficha_taa":
			ficha = r
	_comprobar(ficha != null, "su ficha del Índice está tirada en la nieve honda del este")
	_comprobar(ficha != null and nieve.es_honda(Vector2i((ficha.global_position / 16.0).floor())), "(en la nieve honda, adonde la llevó el viento)")
	m.global_position = ficha.global_position + Vector2(0, 2)
	await _esperar(0.5)
	_comprobar(Estado.cuantos("ficha_taa") == 1, "Maisha recoge la ficha")
	m.global_position = (taa as Node2D).global_position + Vector2(-14, 4)
	await _esperar(0.2)
	taa.interactuar()
	await _leer_dialogo()
	await _esperar(1.0)
	await _leer_dialogo()
	await _esperar(0.5)
	_comprobar(Estado.tiene("taa_nombre") and Estado.cuantos("ficha_taa") == 0, "le devuelve la ficha y Taa recupera su nombre")
	_comprobar(taa.id == "taa", "y su color (ya es «Taa»)")
	_comprobar(Estado.tiene("sigilo_fuego"), "Taa le enseña el sigilo de fuego")

	print("El sigilo de fuego y los faroles:")
	var farol: Node2D = faroles[0]
	for f in faroles:
		if (f as Node2D).global_position.y < farol.global_position.y:
			farol = f
	m.aliento = m.aliento_maximo()
	m.global_position = farol.global_position + Vector2(-20, 2)
	m.mirar(Vector2.RIGHT)
	await _esperar(0.2)
	var aliento0: float = m.aliento
	_comprobar(m.sigilo(), "con U traza el sigilo")
	_comprobar(m.aliento < aliento0, "gasta Aliento")
	_comprobar(not m.sigilo(), "y hay que esperar un poco para el siguiente")
	await _esperar(0.6)
	_comprobar(farol.encendido and Estado.tiene(farol.marca), "el farol se enciende (y se queda encendido)")
	# junto al farol encendido: ni viento ni nieve honda
	m.global_position = farol.global_position + Vector2(30, 6)
	await _esperar(0.3)
	_comprobar(nieve.es_honda(Vector2i((m.global_position / 16.0).floor())), "(Maisha está fuera del sendero)")
	await _esperar(0.3)
	_comprobar(m.hundida <= 0.0, "junto al farol la nieve no es honda")
	ventisca.activa = true
	ventisca.desde = -1
	ventisca.fase = ventisca.Fase.RACHA
	ventisca.set("_t", 2.0)
	var xf := m.global_position.x
	await _esperar(0.8)
	_comprobar(ventisca.cobijada and absf(m.global_position.x - xf) < 6, "y el viento no la empuja")
	ventisca.fase = ventisca.Fase.CALMA
	ventisca.set("_t", 30.0)
	ventisca.activa = false

	print("Las puertas:")
	m.revivir(m.global_position)
	_comprobar(m.hundida == 0.0 and m.viento == Vector2.ZERO, "al revivir no queda nieve ni viento que la frenen")

	print("Las páginas sueltas:")
	var paginas := get_tree().get_nodes_in_group("paginas")
	for p in paginas:
		p.set_physics_process(true)
	_comprobar(paginas.size() >= 8, "páginas sueltas vuelan por el paso (%d)" % paginas.size())
	var pagina: Node2D = paginas[0]
	m.global_position = pagina.global_position + Vector2(0, 60)
	await _esperar(0.1)
	var vida0: int = m.vida
	for i in 40:
		await _esperar(0.1)
		if m.vida < vida0:
			break
	_comprobar(m.vida < vida0, "si ve a Maisha, se le echa encima y le quita una hoja")
	m.revivir(m.global_position)
	await _esperar(0.3)
	var otra: Node2D = paginas[1]
	otra.set("_aturdido", 5.0)
	m.global_position = otra.global_position + Vector2(-20, 14)
	m.mirar(Vector2.RIGHT)
	m.aliento = m.aliento_maximo()
	await _esperar(0.8)
	m.sigilo()
	await _esperar(0.6)
	_comprobar(not is_instance_valid(otra) or not otra.is_in_group("paginas"), "el sigilo de fuego la quema de un trazo")
	_comprobar(int(Estado.extra.get("bestiario", {}).get("pagina", 0)) >= 1, "y cuenta en el Bestiario")
	for p in get_tree().get_nodes_in_group("paginas"):
		p.queue_free()

	print("La Puerta Sellada:")
	var puerta: Node2D = get_tree().get_first_node_in_group("puerta_sellada")
	_comprobar(puerta != null and puerta.estado == 0, "arriba, la puerta de Maandiko está tapada de Tinta Quieta")
	m.global_position = puerta.global_position + Vector2(0, 40)
	await _esperar(0.2)
	Input.action_press("mover_arriba")
	await _esperar(1.5)
	Input.action_release("mover_arriba")
	_comprobar(m.global_position.y > puerta.global_position.y - 2, "no se puede pasar (ni rodearla)")
	for i in 3:
		m.global_position = puerta.global_position + Vector2(0, 26)
		m.mirar(Vector2.UP)
		m.aliento = m.aliento_maximo()
		await _esperar(0.8)
		_comprobar(m.sigilo(), "sigilo de fuego contra el sello (%d)" % (i + 1))
		await _esperar(0.5)
	_comprobar(puerta.estado == 3 and Estado.tiene("puerta_sellada_abierta"), "con tres sigilos, la tinta se derrite y la puerta se abre")
	await _esperar(1.5)
	await _leer_dialogo()
	_comprobar(Misiones.estado(Misiones.buscar("paso_escarcha")) == "hecha", "la misión «El Paso de la Escarcha» se cumple")
	m.global_position = puerta.global_position + Vector2(0, 10)
	await _esperar(0.2)
	Input.action_press("mover_arriba")
	await _esperar(1.5)
	Input.action_release("mover_arriba")
	_comprobar(_escena() == "PasoEscarcha" and not Estado.cambiando, "Maandiko aún no existe: la puerta del norte no deja pasar")

	print()
	print("RESULTADO: todo correcto" if _fallos == 0 else "RESULTADO: %d fallos" % _fallos)
	get_tree().quit(1 if _fallos else 0)
