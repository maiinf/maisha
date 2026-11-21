extends Node
## Prueba automática de El Horizonte Inmóvil (el final): con las tres pesas aparece la misión; Maisha piensa al
## llegar; el pedestal (las pesas encajan y baja un puente de cristal); los tres pilares dorados de la pasarela (la
## vela al oeste, los dos espejos, el obelisco al este) y el puente al altar; Jua-Giza (la llamarada no hace nada a la
## sombra; el contrapeso, con dos Cargas; el velo, con los dos espejos altos a la vez; el candado, entre las olas); la
## calma, Mauti, la Primera Noche y la pantalla del final.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_horizonte_inmovil

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


func _cerca(grupo: String, x: int, y: int) -> Node2D:
	var mejor: Node2D = null
	for n in get_tree().get_nodes_in_group(grupo):
		if mejor == null or (n as Node2D).global_position.distance_to(_sitio(x, y)) < mejor.global_position.distance_to(_sitio(x, y)):
			mejor = n
	return mejor


func _cargar(m: CharacterBody2D, algo: Node2D, desde: Vector2) -> bool:
	m.global_position = algo.global_position + desde
	m.mirar(-desde.normalized())
	m.aliento = m.aliento_maximo()
	m.set("_espera_carga", 0.0)
	var si: bool = m.carga()
	await _esperar(0.6)
	return si


func _pisar(m: Node2D, x: int, y: int) -> void:
	m.global_position = _sitio(x, y)
	await _esperar(0.3)


func _fase(saa: Node2D, f: int, maximo := 12.0) -> void:
	for i in int(maximo * 10):
		if saa.fase == f:
			return
		await _esperar(0.1)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "asterhaul_libre", "nexo_despierto", "mirador_ocaso",
			"arco_atardecer_abierto", "jioni", "kibatari_conocido", "kibatari_caminos", "mwanga_reloj", "carga_sismica",
			"arte_tierra", "tres_pesos"]:
		Estado.marcar(marca)
	for p in ["peso_oeste", "peso_este", "peso_sur"]:
		Estado.dar(p, 1)
	Estado.extra["sol"] = 1
	Estado.jugando = true
	_comprobar(Misiones.estado(Misiones.buscar("horizonte_inmovil")) == "activa", "con las tres pesas aparece la misión del final")

	print("La Llegada:")
	await _ir("horizonte_inmovil", "jioni", "HorizonteInmovil")
	_comprobar(_escena() == "HorizonteInmovil", "se llega a El Horizonte Inmóvil (%s)" % _escena())
	var escena := get_tree().current_scene
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("horizonte_llegada"), "piensa al llegar")
	m.set("_invulnerable", 900.0)
	var mauti := get_tree().get_nodes_in_group("aldeanos").filter(func(a: Node) -> bool: return a.id == "mauti")
	_comprobar(mauti.size() == 1, "Mauti espera en la Llegada")
	var sol: Node2D = escena.sol
	var vacio: Node = escena.get_node("Vacio")
	_comprobar(not escena._puente_pesas.hecho(), "antes de las pesas, no hay puente")
	var pedestal := _cerca("interactuables", 32, 7)
	pedestal.interactuar()
	await _esperar(0.4)
	await _leer_dialogo()
	_comprobar(Estado.tiene("horizonte/pesas") and Estado.cuantos("peso_sur") == 0 and escena._puente_pesas.firme(_sitio(32, 11)), "las tres pesas encajan y baja un puente de cristal")
	await _pisar(m, 32, 11)
	await _pisar(m, 32, 16)
	_comprobar(not vacio.cayendo, "se baja a la pasarela")

	print("La Pasarela de los Tres Pesos:")
	var reloj := _cerca("relojes_sol", 12, 20)
	reloj.recibir_golpe(1, Vector2.UP)
	reloj.recibir_golpe(1, Vector2.UP)
	await _esperar(0.2)
	_comprobar(sol.hora == 0 and not Estado.tiene("horizonte/pilar_oeste"), "sol al oeste, pero la vela de canto no da sombra")
	_cerca("velas_sombra", 14, 17).recibir_golpe(1, Vector2.UP)
	await _esperar(0.2)
	_comprobar(Estado.tiene("horizonte/pilar_oeste"), "la vela de cara: su sombra enciende el pilar del oeste")
	var a := _cerca("espejos", 27, 19)
	var b := _cerca("espejos", 38, 19)
	for i in 3:
		a.recibir_golpe(1, Vector2.UP)
		b.recibir_golpe(1, Vector2.UP)
	await _esperar(0.2)
	_comprobar(a.encendido and b.encendido and Estado.tiene("horizonte/pilar_centro"), "los dos espejos encendidos: el pilar del centro")
	_cerca("relojes_sol", 53, 20).recibir_golpe(1, Vector2.UP)
	_cerca("relojes_sol", 53, 20).recibir_golpe(1, Vector2.UP)
	await _esperar(0.2)
	_comprobar(sol.hora == 2 and Estado.tiene("horizonte/pilar_este"), "sol al este: la sombra del obelisco enciende el pilar del este")
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(escena._puente_altar.hecho(), "con los tres pilares, baja el puente al altar")

	print("Jua-Giza, el Sol Encadenado:")
	var jua: Node2D = escena.jua
	_comprobar(jua != null and jua.fase == jua.Fase.DORMIDO, "Jua-Giza espera encadenado")
	await _pisar(m, 32, 25)
	m.global_position = _sitio(32, 33)
	await _esperar(1.0)
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(jua.fase == jua.Fase.OESTE, "al entrar en el altar, despierta (la Cadena del Oeste)")
	m.global_position = _sitio(22, 40)
	m.set("_invulnerable", 0.0)
	var vida: int = m.vida
	_comprobar(sol.en_sombra(m.global_position), "Maisha, a la sombra de un obelisco")
	await _esperar(5.5)
	_comprobar(m.vida == vida, "la llamarada no hace nada a la sombra")
	m.global_position = _sitio(32, 47)
	await _esperar(5.2)
	_comprobar(m.vida < vida, "fuera de la sombra, la llamarada quema")
	m.set("_invulnerable", 900.0)
	var contrapeso := escena.get_node("Entidades").get_children().filter(func(n: Node) -> bool: return n.get("roto") != null)[0] as Node2D
	await _cargar(m, contrapeso, Vector2(24, 0))
	_comprobar(jua.vida == 10, "una Carga agrieta el contrapeso")
	await _cargar(m, contrapeso, Vector2(24, 0))
	_comprobar(contrapeso.roto and jua.fase == jua.Fase.ESTE, "a la segunda se rompe: se suelta la Cadena del Oeste")
	_comprobar(not jua.recibir_golpe(1, Vector2.UP), "con el velo de Giza, el cetro no le da")
	var altos := get_tree().get_nodes_in_group("espejos_altos")
	for vuelta in 2:
		for i in 100:
			if altos.all(func(e: Node) -> bool: return not e.activo() and e._descanso <= 0.0):
				break
			await _esperar(0.1)
		altos[0].recibir_golpe(1, Vector2.UP)
		await _esperar(0.3)
		_comprobar(not jua.expuesto(), "con un solo espejo, el velo aguanta")
		altos[1].recibir_golpe(1, Vector2.UP)
		await _esperar(0.1)
		_comprobar(jua.expuesto(), "con los dos espejos a la vez, el velo se abre y se ve el broche")
		jua.recibir_golpe(1, Vector2.UP)
		jua.recibir_golpe(1, Vector2.UP)
		if vuelta == 0:
			_comprobar(jua.vida == 6 and not jua.expuesto(), "dos golpes al broche y el velo se cierra")
	_comprobar(jua.fase == jua.Fase.SUR, "se suelta la Cadena del Este")
	_comprobar(not escena.get_node("Entidades").get_children().filter(func(n: Node) -> bool: return n.get("brilla") != null)[0].recibir_golpe(1, Vector2.UP), "el candado, sin brillar, no se deja")
	var candado := escena.get_node("Entidades").get_children().filter(func(n: Node) -> bool: return n.get("brilla") != null)[0] as Node2D
	var olas := false
	for golpe in 4:
		for i in 200:
			olas = olas or not jua._olas.is_empty()
			if candado.brilla:
				break
			await _esperar(0.1)
		candado.recibir_golpe(1, Vector2.UP)
		_comprobar(not candado.recibir_golpe(1, Vector2.UP) or jua.fase == jua.Fase.CALMA, "un golpe por cada vez que brilla (%d)" % (golpe + 1))
	_comprobar(olas, "entre golpe y golpe, olas de penumbra")
	_comprobar(jua.fase == jua.Fase.CALMA, "se suelta la Cadena del Sur: Jua-Giza, en calma")

	print("La Primera Noche:")
	for i in 100:
		await _leer_dialogo()
		if Estado.tiene("fin_ocaso_visto"):
			break
		await _esperar(0.2)
	_comprobar(Estado.tiene("ocaso_libre"), "Mauti llega y calman el sol con el Cetro del Nexo")
	_comprobar(Estado.tiene("fin_ocaso_visto"), "la pantalla del final: La Primera Noche")
	_comprobar(Misiones.estado(Misiones.buscar("horizonte_inmovil")) == "hecha", "la misión, hecha")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
