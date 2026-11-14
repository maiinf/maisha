extends Node
## Prueba automática de El Desfiladero del Meteorito (Asterhaul): se llega desde el Kitovu por el este, suena su
## música, Maisha piensa al llegar, las vías se pisan, Mwamba en gris y su esquirla (en la cantera), los Kaa-Jiwe a
## los que el cetro no hace nada, la Carga Sísmica (embiste, gasta Aliento), el muro agrietado y la 2.ª esquirla,
## el derrumbe que solo aparta la vagoneta (que sigue la vía y su curva), Mauti, el Kaa-Jiwe volcado y vencido, los
## tres pilares y la Puerta del Cráter, que todo queda como estaba al volver, y la puerta del Kitovu.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_desfiladero_meteorito

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _escena() -> String:
	var e := get_tree().current_scene
	return e.name if e else ""


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 200:
		if not dialogo.hablando:
			await _esperar(0.4)
			if not dialogo.hablando:
				return
		dialogo.pasar()
		await _esperar(0.08)


func _ir(escena: String, puerta: String, nombre: String) -> void:
	Estado.ir_a(escena, puerta)
	for i in 300:
		if _escena() == nombre and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(1.0)


func _sitio(x: int, y: int) -> Vector2:
	return Vector2(x, y) * 16.0 + Vector2(8, 14)


## El nodo de `grupo` más cercano a una casilla
func _cerca(grupo: String, x: int, y: int) -> Node2D:
	var mejor: Node2D = null
	for n in get_tree().get_nodes_in_group(grupo):
		if mejor == null or (n as Node2D).global_position.distance_to(_sitio(x, y)) < mejor.global_position.distance_to(_sitio(x, y)):
			mejor = n
	return mejor


## Maisha se pone junto a `algo`, lo mira y embiste
func _cargar(m: CharacterBody2D, algo: Node2D, desde: Vector2) -> bool:
	m.global_position = algo.global_position + desde
	m.mirar(-desde.normalized())
	m.aliento = m.aliento_maximo()
	m.set("_espera_carga", 0.0)
	var si: bool = m.carga()
	await _esperar(0.6)
	return si


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo"]:
		Estado.marcar(marca)
	Estado.jugando = true

	print("Llegar al Desfiladero:")
	await _ir("desfiladero_meteorito", "oeste", "DesfiladeroMeteorito")
	_comprobar(_escena() == "DesfiladeroMeteorito", "se llega a El Desfiladero del Meteorito (%s)" % _escena())
	_comprobar(Sonido.musica_actual == "desfiladero_meteorito", "suena «El eco de la piedra» (%s)" % Sonido.musica_actual)
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.x < 60.0, "Maisha aparece en la puerta del oeste (%s)" % m.global_position)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("desfiladero_llegada"), "piensa al llegar")
	_comprobar(Misiones.estado(Misiones.buscar("desfiladero_meteorito")) == "activa", "la misión está activa (%s)" % Misiones.estado(Misiones.buscar("desfiladero_meteorito")))
	m.global_position = _sitio(14, 39)
	Input.action_press("mover_abajo")
	await _esperar(0.9)
	Input.action_release("mover_abajo")
	_comprobar(m.global_position.y > _sitio(14, 41).y + 4.0, "las vías se pisan (%.0f)" % m.global_position.y)
	m.global_position = _sitio(40, 12)
	Input.action_press("mover_arriba")
	await _esperar(0.6)
	Input.action_release("mover_arriba")
	_comprobar(m.global_position.y > 12.0 * 16.0, "la pared del cañón no se atraviesa (%.0f)" % m.global_position.y)

	print("Mwamba, en gris:")
	var mwamba := _cerca("escribas", 47, 21)
	_comprobar(mwamba != null and mwamba.id == "mwamba_gris", "el viejo cantero está en gris")
	m.global_position = mwamba.global_position + Vector2(0, 14)
	mwamba.interactuar()
	await _leer_dialogo()
	_comprobar(Estado.tiene("mwamba_visto") and not Estado.tiene("mwamba_pulso"), "no habla: Maisha lo mira")
	_comprobar(not m.carga(), "sin aprenderla, no hay Carga")

	print("La Cantera Hundida:")
	var kaa := _cerca("kaa_jiwes", 58, 42)
	_comprobar(kaa != null and get_tree().get_nodes_in_group("kaa_jiwes").size() == 5, "hay cinco Kaa-Jiwe (%d)" % get_tree().get_nodes_in_group("kaa_jiwes").size())
	_comprobar(not kaa.recibir_golpe(1, Vector2.RIGHT) and kaa.vida == 3, "el cetro rebota en la coraza")
	m.global_position = kaa.global_position + Vector2(50, 0)       # (por el este: al oeste tiene una peña)
	await _esperar(0.2)
	_comprobar(kaa.fase == kaa.Fase.AVISA, "si ve a Maisha, avisa (%d)" % kaa.fase)
	await _esperar(0.7)
	_comprobar(kaa.fase == kaa.Fase.EMBISTE, "y embiste (%d)" % kaa.fase)
	var esquirla := _cerca("recogibles", 73, 47)
	m.global_position = esquirla.global_position
	await _esperar(0.5)
	_comprobar(Estado.cuantos("esquirla_mwamba") == 1 and Estado.tiene("esquirla/mwamba"), "la Esquirla de Mwamba está en la cantera")

	print("Mwamba recupera el pulso y enseña la Carga:")
	m.global_position = mwamba.global_position + Vector2(0, 14)
	m.set("_invulnerable", 5.0)
	mwamba.interactuar()
	await _leer_dialogo()
	_comprobar(Estado.tiene("mwamba_pulso") and Estado.cuantos("esquirla_mwamba") == 0, "se le devuelve la esquirla")
	await _esperar(1.2)
	await _leer_dialogo()
	_comprobar(mwamba.id == "mwamba" and Estado.tiene("carga_sismica"), "le vuelve el color y enseña la Carga Sísmica")
	m.global_position = _sitio(36, 28)
	m.mirar(Vector2.RIGHT)
	m.aliento = m.aliento_maximo()
	var x0 := m.global_position.x
	_comprobar(m.carga(), "con I, Maisha embiste")
	_comprobar(is_equal_approx(m.aliento, m.aliento_maximo() - 20.0), "gasta 20 de Aliento (%.0f)" % m.aliento)
	await _esperar(0.6)
	_comprobar(m.global_position.x - x0 > 30.0, "y avanza de golpe (%.0f px)" % (m.global_position.x - x0))
	_comprobar(not m.carga(), "hay que esperar un momento entre carga y carga")

	print("El muro agrietado y el secreto:")
	var muro := _cerca("sismicos", 20, 34)
	m.global_position = muro.global_position + Vector2(0, 40)
	Input.action_press("mover_arriba")
	await _esperar(0.8)
	Input.action_release("mover_arriba")
	_comprobar(m.global_position.y > muro.global_position.y, "el muro no deja pasar (%.0f)" % m.global_position.y)
	_comprobar(await _cargar(m, muro, Vector2(0, 26)), "se le embiste")
	_comprobar(muro.esta_roto() and Estado.tiene("desfiladero/muro_secreto"), "y se viene abajo")
	m.global_position = _cerca("recogibles", 20, 30).global_position
	await _esperar(0.5)
	_comprobar(Estado.cuantos("esquirla_estrella") == 1 and Estado.tiene("esquirla/desfiladero"), "detrás, la 2.ª Esquirla de Estrella")

	print("El derrumbe y la vagoneta:")
	var derrumbe := _cerca("derrumbes", 30, 12)
	await _cargar(m, derrumbe, Vector2(0, 26))
	_comprobar(not derrumbe.esta_roto(), "la Carga sola no aparta el derrumbe")
	var corta := _cerca("vagonetas", 8, 41)
	await _cargar(m, corta, Vector2(0, 22))
	_comprobar(not corta.rodando and corta.casilla() == Vector2i(8, 41), "contra el sentido de la vía, la vagoneta no se mueve")
	var vagoneta := _cerca("vagonetas", 46, 24)
	await _cargar(m, vagoneta, Vector2(24, 0))
	_comprobar(vagoneta.rodando, "empujada a lo largo de la vía, rueda")
	for i in 80:
		if not vagoneta.rodando:
			break
		await _esperar(0.1)
	_comprobar(vagoneta.casilla() == Vector2i(30, 14), "sigue la vía y su curva hasta el final (%s)" % vagoneta.casilla())
	_comprobar(derrumbe.esta_roto() and Estado.tiene("desfiladero/derrumbe_mauti"), "y aparta el derrumbe")
	var mauti: Node2D = null
	for n in get_tree().get_nodes_in_group("interactuables"):
		if n.get("id") == "mauti":
			mauti = n
	m.global_position = mauti.global_position + Vector2(0, 14)
	mauti.interactuar()
	await _leer_dialogo()
	_comprobar(Estado.tiene("mauti_desfiladero_libre"), "detrás estaba Mauti")
	await _cargar(m, corta, Vector2(-24, 0))
	for i in 60:
		if not corta.rodando:
			break
		await _esperar(0.1)
	_comprobar(corta.casilla() == Vector2i(23, 41) and Estado.tiene("secreto/desfiladero_meteorito/25,41"), "la otra vagoneta aparta el montón de rocas: un secreto (%s)" % corta.casilla())

	print("Kaa-Jiwe, con la Carga:")
	kaa = _cerca("kaa_jiwes", 58, 9)
	kaa.fase = kaa.Fase.DESCANSA
	await _cargar(m, kaa, Vector2(-22, 0))
	_comprobar(kaa.fase == kaa.Fase.VOLCADO, "la Carga lo vuelca (%d)" % kaa.fase)
	_comprobar(kaa.recibir_golpe(1, Vector2.RIGHT) and kaa.vida == 2, "panza arriba, el cetro sí entra")
	kaa.recibir_golpe(1, Vector2.RIGHT)
	kaa.recibir_golpe(1, Vector2.RIGHT)
	await _esperar(0.6)
	_comprobar(get_tree().get_nodes_in_group("kaa_jiwes").size() == 4 and int(Estado.extra.get("bestiario", {}).get("kaa_jiwe", 0)) == 1, "tres golpes y cuenta en el Bestiario")

	print("La Puerta del Cráter:")
	muro = _cerca("sismicos", 66, 17)
	await _cargar(m, muro, Vector2(0, 26))
	_comprobar(Estado.tiene("desfiladero/muro_puerta"), "el muro del noreste cae")
	var pilares := get_tree().get_nodes_in_group("pilares_diapason")
	_comprobar(pilares.size() == 3, "hay tres pilares-diapasón")
	for i in 2:
		await _cargar(m, pilares[i], Vector2(0, 20))
	_comprobar(pilares[0].encendido and pilares[1].encendido and not Estado.tiene("puerta_crater_abierta"), "con dos sonando, la puerta sigue cerrada")
	await _cargar(m, pilares[2], Vector2(0, 20))
	await _esperar(1.2)
	_comprobar(Estado.tiene("puerta_crater_abierta"), "con los tres, la Puerta del Cráter se abre")
	_comprobar(Misiones.estado(Misiones.buscar("desfiladero_meteorito")) == "hecha", "misión cumplida")

	print("Al volver, todo sigue como quedó:")
	await _ir("desfiladero_meteorito", "oeste", "DesfiladeroMeteorito")
	_comprobar(_cerca("vagonetas", 30, 14).casilla() == Vector2i(30, 14), "la vagoneta, al final del ramal")
	_comprobar(get_tree().get_nodes_in_group("derrumbes").is_empty(), "los derrumbes, apartados")
	_comprobar(get_tree().get_nodes_in_group("pilares_diapason").all(func(p: Node) -> bool: return p.encendido), "los pilares, sonando")
	_comprobar(_cerca("escribas", 47, 21).id == "mwamba", "y Mwamba, con su color")

	print("El sendero del este del Kitovu:")
	await _ir("kitovu", "desfiladero", "Kitovu")
	var puerta: Node2D = null
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == "desfiladero":
			puerta = p
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(puerta != null and puerta.destino == "desfiladero_meteorito", "en el Kitovu está la puerta al Desfiladero")
	_comprobar(puerta != null and m.global_position.distance_to(puerta.global_position) < 48.0, "y se vuelve por ella (%s)" % m.global_position)

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
