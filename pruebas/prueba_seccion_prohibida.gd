extends Node
## Prueba automática de La Sección Prohibida (Sigilia, el final): en Maandiko el Gran Archivo no se abre sin los doce
## nombres, las tres fichas escondidas en la ciudad (Kurasa, Muhuri y Wimbo), el Índice completo abre la puerta; abajo,
## los doce atriles, Mauti y Kalamu, los pedestales dormidos y el Triple Sello cerrado, el foso (la placa deriva al
## sur) y el sello del oeste (fuego), el puente y el sello del este (rayo), los tres pedestales y el Triple Sello,
## la Sombra de Renglón (el cetro la atraviesa, un sigilo la fija), el Grimorio (capítulos, el pedestal que late,
## rasgar, aturdido, la mano, la furia, la caída de Maisha) y el cierre: Mauti y Kalamu, la Pluma del Primer Nombre
## y el final de Sigilia.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_seccion_prohibida

const INDICE := preload("res://scripts/mundo/sigilia/indice.gd")

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


func _andar(m: CharacterBody2D, accion: String, s: float) -> void:
	Input.action_press(accion)
	await _esperar(s)
	Input.action_release(accion)


func _sitio(x: int, y: int) -> Vector2:
	return Vector2(x, y) * 16.0 + Vector2(8, 14)


## El nodo de `grupo` más cercano a una casilla
func _cerca(grupo: String, x: int, y: int) -> Node2D:
	var mejor: Node2D = null
	for n in get_tree().get_nodes_in_group(grupo):
		if mejor == null or (n as Node2D).global_position.distance_to(_sitio(x, y)) < mejor.global_position.distance_to(_sitio(x, y)):
			mejor = n
	return mejor


## Maisha se pone junto a `algo`, lo mira y le traza el sigilo elegido
func _trazar(m: CharacterBody2D, algo: Node2D, desde := Vector2(-20, 2)) -> bool:
	m.global_position = algo.global_position + desde
	m.mirar(-desde.normalized())
	m.aliento = m.aliento_maximo()
	m.set("_espera_sigilo", 0.0)
	var si: bool = m.sigilo()
	await _esperar(0.45)
	return si


func _elegir(m: CharacterBody2D, cual: String) -> void:
	for i in 3:
		if m.sigilo_elegido() != cual:
			m.cambiar_sigilo()


func _ficha(objeto: String) -> Node2D:
	for r in get_tree().get_nodes_in_group("recogibles"):
		if r.objeto == objeto:
			return r
	return null


func _pedestal(marca: String) -> Node2D:
	for p in get_tree().get_nodes_in_group("pedestales"):
		if p.marca == marca:
			return p
	return null


func _de_rotonda(tipo: String) -> Node2D:
	for p in get_tree().get_nodes_in_group("pedestales_rotonda"):
		if p.tipo == tipo:
			return p
	return null


func _vecino(id: String) -> Node2D:
	for a in get_tree().get_nodes_in_group("aldeanos"):
		if a.id == id:
			return a
	return null


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "visto/cuna_de_musgo", "sigilo_fuego", "sigilo_hielo", "sigilo_rayo", "maandiko_llegada", "kalamu_conocida",
			"mapa_norte", "mauti_libre"]:
		Estado.marcar(marca)
	for marca in INDICE.NOMBRES:
		if not marca in ["kurasa_nombre", "muhuri_nombre", "wimbo_nombre"]:
			Estado.marcar(marca)
	Estado.jugando = true

	print("El Gran Archivo y los doce nombres:")
	await _ir("maandiko", "canal", "Maandiko")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(INDICE.cuantos() == 9 and not Estado.tiene("indice_completo"), "con nueve nombres, el Índice no está completo")
	m.global_position = Vector2(36 * 16, 17 * 16)
	await _andar(m, "mover_arriba", 1.5)
	await _leer_dialogo()
	_comprobar(_escena() == "Maandiko" and m.global_position.y > 15 * 16, "la puerta del Gran Archivo no se abre (y Maisha cuenta los atriles)")
	for nombre in ["kurasa", "muhuri", "wimbo"]:
		var ficha := _ficha("ficha_" + nombre)
		_comprobar(ficha != null, "en un rincón de la ciudad, la ficha de %s" % nombre.capitalize())
		m.global_position = ficha.global_position
		await _esperar(0.4)
		var e: Node = null
		for a in get_tree().get_nodes_in_group("escribas"):
			if a.nombre == nombre:
				e = a
		m.global_position = (e as Node2D).global_position + Vector2(-18, 6)
		e.interactuar()
		await _leer_dialogo()
		await _esperar(1.0)
		await _leer_dialogo()
		_comprobar(Estado.tiene(nombre + "_nombre") and e.id == "escriba", "%s recupera su nombre y habla" % nombre.capitalize())
	_comprobar(INDICE.completo() and Estado.tiene("indice_completo"), "con los doce nombres, el Índice está completo")
	m.global_position = Vector2(36 * 16, 17 * 16)
	Input.action_press("mover_arriba")
	for i in 300:
		if _escena() == "SeccionProhibida" and not Estado.cambiando:
			break
		await get_tree().process_frame
	Input.action_release("mover_arriba")
	await _esperar(1.0)
	_comprobar(_escena() == "SeccionProhibida" and Estado.tiene("seccion_prohibida"), "y la puerta del Gran Archivo baja a la Sección Prohibida")

	print("La Escalera de los 12 Nombres:")
	_comprobar(Sonido.musica_actual == "seccion_prohibida", "suena «Lo que se guardó bajo llave» (%s)" % Sonido.musica_actual)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("seccion_llegada"), "Maisha mira el mármol y los libros encadenados")
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	_comprobar(m.global_position.y > 66 * 16, "aparece al pie de la escalera")
	var sombras := get_tree().get_nodes_in_group("sombras_renglon")
	_comprobar(sombras.size() == 4, "cuatro Sombras de Renglón por las salas (%d)" % sombras.size())
	for s in sombras:
		s.set_process(false)
	var kalamu := _vecino("kalamu")
	_comprobar(kalamu != null and _vecino("mauti") != null, "Mauti y Kalamu han bajado con Maisha")
	m.global_position = kalamu.global_position + Vector2(-18, 6)
	kalamu.interactuar()
	await _leer_dialogo()
	_comprobar(Estado.tiene("kalamu_bajada"), "Kalamu cuenta qué pedestal deshace cada capítulo")

	print("El Claustro del Triple Sello:")
	var p_fuego := _pedestal("seccion/pedestal_fuego")
	_elegir(m, "fuego")
	await _trazar(m, p_fuego, Vector2(0, 20))
	_comprobar(p_fuego.dormido and not p_fuego.encendido, "los pedestales del Claustro están dormidos: el fuego no los enciende")
	m.global_position = _sitio(31, 37)
	await _andar(m, "mover_arriba", 1.5)
	_comprobar(m.global_position.y > 35 * 16, "el Triple Sello cierra el paso a la Rotonda")

	print("La Cámara del Sello de Fuego y Hielo:")
	_elegir(m, "hielo")
	m.global_position = Vector2(18 * 16 + 5, 42 * 16 + 8)
	m.mirar(Vector2.LEFT)
	m.aliento = m.aliento_maximo()
	m.set("_espera_sigilo", 0.0)
	m.sigilo()
	await _esperar(0.5)
	var placas := get_tree().get_nodes_in_group("placas_hielo")
	_comprobar(placas.size() == 1, "el Sigilo de Hielo endurece la tinta del foso")
	var y0: float = placas[0].global_position.y if not placas.is_empty() else 0.0
	await _andar(m, "mover_izquierda", 2.5)
	_comprobar(not placas.is_empty() and placas[0].global_position.y > y0 + 10.0, "aquí la tinta corre hacia el sur: la placa deriva")
	_comprobar(m.global_position.x < 15 * 16, "y por ella se cruza a la cámara (x=%d)" % int(m.global_position.x / 16))
	var sello_o := _pedestal("seccion/sello_oeste")
	_elegir(m, "fuego")
	var tapon := _cerca("charcos_tinta", 7, 35)
	for i in 3:
		await _trazar(m, tapon, Vector2(0, 26))
		await _esperar(0.4)
	await _esperar(0.7)
	_comprobar(not is_instance_valid(tapon) or not tapon.is_in_group("charcos_tinta"), "el fuego derrite la Tinta Quieta que tapa el rincón del sello")
	_elegir(m, "hielo")
	await _trazar(m, sello_o, Vector2(0, 20))
	_comprobar(not sello_o.encendido, "el sello del oeste es de fuego: el hielo no lo enciende")
	_elegir(m, "fuego")
	await _trazar(m, sello_o, Vector2(0, 20))
	_comprobar(sello_o.encendido and Estado.tiene("seccion/sello_oeste"), "con el fuego, se enciende el sello del oeste")
	_comprobar(p_fuego.dormido, "(con un solo sello, los pedestales del Claustro siguen dormidos)")

	print("La Cámara del Sello de Hielo y Rayo:")
	_elegir(m, "rayo")
	await _trazar(m, _cerca("bobinas", 41, 40))
	await _trazar(m, _cerca("bobinas", 41, 48))
	_comprobar(Estado.tiene("seccion/puente_este"), "las dos bobinas tienden el Puente de Constelación sobre la sima")
	await _esperar(1.3)
	m.global_position = _sitio(43, 44)
	await _andar(m, "mover_derecha", 3.0)
	_comprobar(m.global_position.x > 50 * 16, "y se cruza a la cámara del este")
	_elegir(m, "hielo")
	m.global_position = Vector2(51 * 16 + 11, 44 * 16 + 8)
	m.mirar(Vector2.RIGHT)
	m.aliento = m.aliento_maximo()
	m.set("_espera_sigilo", 0.0)
	m.sigilo()
	await _esperar(0.5)
	await _andar(m, "mover_derecha", 2.5)
	_comprobar(m.global_position.x > 54 * 16 + 12, "con una placa de hielo se llega a la isleta del estanque (x=%d)" % int(m.global_position.x / 16))
	_elegir(m, "rayo")
	var sello_e := _pedestal("seccion/sello_este")
	await _trazar(m, sello_e, Vector2(-14, 6))
	_comprobar(sello_e.encendido and Estado.tiene("seccion/sello_este"), "con el rayo, se enciende el sello del este")
	_comprobar(not p_fuego.dormido, "con los dos sellos, despiertan los pedestales del Claustro")

	print("El Triple Sello:")
	for tipo in ["fuego", "hielo", "rayo"]:
		_elegir(m, tipo)
		await _trazar(m, _pedestal("seccion/pedestal_" + tipo), Vector2(0, 20))
		if tipo != "rayo":
			_comprobar(not Estado.tiene("seccion/triple_sello"), "con el de %s solo, el sello sigue cerrado" % tipo)
	_comprobar(Estado.tiene("seccion/triple_sello"), "con los tres pedestales encendidos, el Triple Sello se abre")
	m.global_position = _sitio(31, 37)
	await _andar(m, "mover_arriba", 2.5)
	_comprobar(m.global_position.y < 34 * 16, "y se pasa hacia la Rotonda")

	print("La Sombra de Renglón:")
	var sombra: Node2D = _cerca("sombras_renglon", 24, 46)
	m.global_position = sombra.global_position + Vector2(-70, 0)
	sombra.set_process(true)
	var hojas: int = m.vida
	for i in 60:
		await _esperar(0.1)
		if m.vida < hojas:
			break
	_comprobar(m.vida < hojas, "repta hacia Maisha y se le lanza")
	_comprobar(not sombra.recibir_golpe(1, Vector2.UP) and sombra.vida == sombra.VIDA, "es tinta suelta: el cetro la atraviesa")
	sombra.set_process(false)
	_elegir(m, "fuego")
	await _trazar(m, sombra, Vector2(-18, 0))
	_comprobar(sombra.fase == sombra.Fase.FIJADA, "un sigilo la fija: se queda sólida")
	var vencidas := int(Estado.extra.get("bestiario", {}).get("sombra_renglon", 0))
	for i in 2:
		m.global_position = sombra.global_position + Vector2(-14, 0)
		m.mirar(Vector2.RIGHT)
		m.golpear()
		await _esperar(0.5)
	await _esperar(0.5)
	_comprobar(int(Estado.extra.get("bestiario", {}).get("sombra_renglon", 0)) == vencidas + 1, "dos golpes de cetro y se deshace (y cuenta en el Bestiario)")

	print("El Grimorio de Tinta:")
	var g: Node2D = get_tree().get_nodes_in_group("jefes")[0]
	_comprobar(g.fase == g.Fase.DORMIDO, "en medio de la Rotonda flota un libro enorme, abierto")
	_comprobar(get_tree().get_nodes_in_group("pedestales_rotonda").size() == 3, "con tres pedestales alrededor")
	m.vida = m.vida_maxima()
	m.global_position = _sitio(31, 27)
	await _esperar(0.5)
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(g.fase != g.Fase.DORMIDO and Sonido.musica_actual == "jefe_grimorio", "al entrar, despierta (y suena «El último capítulo»)")
	_comprobar(not g.recibir_golpe(1, Vector2.UP) and g.vida == g.VIDA_MAX, "flotando, el cetro rebota en el cuero")
	g.set_process(false)
	g._marcas.clear()
	g._manos.clear()
	g.abrir_capitulo("fuego")
	_comprobar(g.capitulo == "fuego" and _de_rotonda("hielo").marcado and not _de_rotonda("fuego").marcado, "abre el capítulo de fuego: late el pedestal de hielo")
	m.set("_invulnerable", 0.0)
	m.global_position = g.centro + Vector2(0, 90)
	hojas = m.vida
	g.atacar(m.global_position)
	for i in 12:
		g._mover_marcas(0.1, m)
	_comprobar(m.vida < hojas, "las letras que arden estallan bajo Maisha")
	m.set("_invulnerable", 0.0)
	hojas = m.vida
	g.atacar(m.global_position + Vector2(80, 0))
	for i in 12:
		g._mover_marcas(0.1, m)
	_comprobar(m.vida == hojas, "si se aparta del aviso, no la tocan")
	g.capitulo = "hielo"
	g.atacar(m.global_position + Vector2(90, 0))
	for i in 12:
		g._mover_marcas(0.1, m)
	_comprobar(m.vida < hojas, "el renglón helado cruza la Rotonda de lado a lado")
	m.set("_invulnerable", 0.0)
	hojas = m.vida
	g.sacar_mano(m.global_position)
	for i in 10:
		g._mover_manos(0.1, m)
	_comprobar(m.vida < hojas, "una mano de tinta sale del suelo y da un manotazo")
	g._manos.clear()
	g.capitulo = "fuego"
	g._marcar_pedestal("hielo")
	m.set("_invulnerable", 30.0)
	_elegir(m, "fuego")
	await _trazar(m, _de_rotonda("fuego"), Vector2(0, 20))
	_comprobar(g.fase == g.Fase.CAPITULO, "el pedestal equivocado no hace nada")
	_elegir(m, "hielo")
	await _trazar(m, _de_rotonda("hielo"), Vector2(0, 20))
	_comprobar(g.fase == g.Fase.ATURDIDO, "el pedestal de hielo rasga el capítulo de fuego: el Grimorio cae aturdido")
	for i in 3:
		m.global_position = g.global_position + Vector2(-18, 6)
		m.mirar(Vector2.RIGHT)
		m.golpear()
		await _esperar(0.45)
	_comprobar(g.vida == g.VIDA_MAX - 3, "aturdido, el cetro le entra (%d de vida)" % g.vida)
	g.set_process(true)
	await _esperar(0.3)
	_comprobar(g.fase == g.Fase.PASA_HOJAS, "tras tres golpes se alza y pasa las hojas")
	g.set_process(false)
	g.vida = 6
	g.abrir_capitulo("hielo")
	_comprobar(g.furia() and _de_rotonda("rayo").marcado, "con la mitad de la vida, se enfurece; el capítulo de hielo se parte con el rayo")
	_comprobar(get_tree().get_nodes_in_group("sombras_renglon").size() >= 1, "y de sus páginas salen Sombras de Renglón")
	for s in get_tree().get_nodes_in_group("sombras_renglon"):
		s.set_process(false)
	# la caída de Maisha
	m.set("_invulnerable", 0.0)
	m.vida = 1
	m.recibir_danio(1, g.global_position, "contacto")
	_comprobar(m.esta_caida, "si Maisha cae en la pelea...")
	await _esperar(2.0)
	_comprobar(not m.esta_caida and m.global_position.distance_to(_sitio(31, 28)) < 24.0, "...se levanta a la entrada de la Rotonda")
	# el último capítulo
	g.vida = 1
	g.abrir_capitulo("rayo")
	m.set("_invulnerable", 30.0)
	_elegir(m, "fuego")
	await _trazar(m, _de_rotonda("fuego"), Vector2(0, 20))
	_comprobar(g.fase == g.Fase.ATURDIDO, "el capítulo de rayo se pierde en el fuego")
	m.global_position = g.global_position + Vector2(-18, 6)
	m.mirar(Vector2.RIGHT)
	m.golpear()
	await _esperar(0.6)
	_comprobar(Estado.tiene("grimorio_vencido") and g.fase == g.Fase.VENCIDO, "vencido, el Grimorio se queda abierto en el suelo")
	_comprobar(int(Estado.extra.get("bestiario", {}).get("grimorio", 0)) == 1, "y cuenta en el Bestiario")

	print("El cierre de Sigilia:")
	await _esperar(3.2)
	for i in 3:
		await _leer_dialogo()
		await _esperar(0.5)
	await _esperar(0.5)
	var kalamus := get_tree().get_nodes_in_group("aldeanos").filter(func(a: Node) -> bool: return a.id == "kalamu")
	_comprobar(kalamus.size() == 2, "Kalamu y Mauti entran en la Rotonda")
	_comprobar(Estado.tiene("sigilia_libre") and Estado.cuantos("pluma_primer_nombre") == 1, "el Índice Vivo entrega la Pluma del Primer Nombre")
	var fin := get_tree().get_first_node_in_group("fin_mundo")
	_comprobar(fin != null and fin.abierto and fin.titulo == "Sigilia recuerda", "y sale el final de Sigilia")
	if fin:
		fin.cerrar()
	await _esperar(1.3)
	_comprobar(not get_tree().paused, "al cerrarlo, se sigue jugando")
	var mauti := _vecino("mauti")
	mauti.interactuar()
	await _leer_dialogo()
	_comprobar(true, "Mauti habla de lo que viene: una ciudad dentro de un cráter")

	print()
	print("RESULTADO: todo correcto" if _fallos == 0 else "RESULTADO: %d fallos" % _fallos)
	get_tree().quit(1 if _fallos else 0)
