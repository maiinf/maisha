extends Node
## Prueba automática de El Observatorio de la Aurora (Sigilia): se llega desde Maandiko por el noroeste, suena su
## música, Maisha piensa al llegar, el cielo no se pisa, los puentes no están hasta encender sus bobinas, Nyota y su
## ficha (tras un tapón de Tinta Quieta), el Sigilo de Rayo, las bobinas que se apagan solas, los puentes de una y
## de dos bobinas, Saa (el cetro rebota, el mazazo, la sobrecarga y vencido), la bobina mayor del estanque (con el
## hielo, que aquí no deriva) y la tapada de tinta (con el fuego), el puente del norte, Kengele (el tañido mudo que
## apaga las runas, la embestida, el diapasón que la hace resonar, la furia y su ficha) y, en Maandiko, Darubini y
## Mlinzi recuperan su nombre.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_observatorio_aurora

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


func _puente(nombre: String) -> Node:
	for p in get_tree().get_nodes_in_group("puentes_constelacion"):
		if p.marca == "observatorio/puente_" + nombre:
			return p
	return null


func _ficha(objeto: String) -> Node2D:
	for r in get_tree().get_nodes_in_group("recogibles"):
		if r.objeto == objeto:
			return r
	return null


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "visto/cuna_de_musgo", "sigilo_fuego", "sigilo_hielo", "maandiko_llegada", "kalamu_conocida", "mapa_norte"]:
		Estado.marcar(marca)
	Estado.jugando = true

	print("La llegada:")
	await _ir("observatorio_aurora", "ciudad", "ObservatorioAurora")
	_comprobar(_escena() == "ObservatorioAurora" and Estado.tiene("observatorio_aurora"), "se llega al Observatorio de la Aurora desde Maandiko")
	_comprobar(Sonido.musica_actual == "observatorio_aurora", "suena «Donde miran las estrellas» (%s)" % Sonido.musica_actual)
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("observatorio_llegada"), "Maisha mira el cielo y la aurora al llegar")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var saas := get_tree().get_nodes_in_group("saas")
	_comprobar(saas.size() == 4, "cuatro Saa hacen su ronda por las terrazas (%d)" % saas.size())
	for s in saas:
		s.set_process(false)              # (quietos hasta su parte de la prueba)
	_comprobar(m.global_position.y > 74 * 16 and absf(m.global_position.x - 36 * 16) < 40, "aparece en la escalera del sur")

	print("Las terrazas y el cielo:")
	m.global_position = _sitio(21, 66)
	await _andar(m, "mover_izquierda", 1.2)
	_comprobar(m.global_position.x > 20 * 16, "el cielo no se pisa: la terraza se acaba y Maisha no cae")
	m.global_position = _sitio(36, 60)
	await _andar(m, "mover_arriba", 1.5)
	_comprobar(m.global_position.y > 59 * 16, "sin su bobina encendida, el puente al Claustro no está")
	_comprobar(get_tree().get_nodes_in_group("puentes_constelacion").size() == 4, "hay cuatro Puentes de Constelación")
	_comprobar(get_tree().get_nodes_in_group("charcos_tinta").size() == 2, "dos tapones de Tinta Quieta (el rincón del sur y el de las Campanas)")

	print("Nyota y su ficha:")
	var nyota: Node = null
	for a in get_tree().get_nodes_in_group("escribas"):
		if a.nombre == "nyota":
			nyota = a
	_comprobar(nyota != null and nyota.id == "nyota_blanco", "junto a su cúpula, Nyota está en blanco")
	m.global_position = (nyota as Node2D).global_position + Vector2(-18, 6)
	nyota.interactuar()
	await _leer_dialogo()
	_comprobar(not Estado.tiene("nyota_nombre"), "sin su ficha, solo se la mira")
	var bobina_sur := _cerca("bobinas", 38, 61)
	bobina_sur.interactuar()
	await _leer_dialogo()
	_comprobar(not bobina_sur.encendida and not m.cambiar_sigilo() == false, "la bobina está dormida (y con fuego y hielo, R cambia de uno a otro)")
	_elegir(m, "fuego")
	var tapon := _cerca("charcos_tinta", 46, 74)
	for i in 3:
		await _trazar(m, tapon, Vector2(0, -28))
		await _esperar(0.4)
	await _esperar(0.7)
	_comprobar(not is_instance_valid(tapon) or not tapon.is_in_group("charcos_tinta"), "el fuego derrite el tapón del rincón del sur")
	m.global_position = _ficha("ficha_nyota").global_position
	await _esperar(0.4)
	_comprobar(Estado.cuantos("ficha_nyota") == 1, "en el rincón, la ficha de Nyota")
	m.global_position = (nyota as Node2D).global_position + Vector2(-18, 6)
	nyota.interactuar()
	await _leer_dialogo()
	await _esperar(1.0)
	await _leer_dialogo()
	_comprobar(Estado.tiene("nyota_nombre") and nyota.id == "nyota", "al darle su ficha, recupera el nombre y el color")
	_comprobar(Estado.tiene("sigilo_rayo"), "y enseña el Sigilo de Rayo")

	print("El Sigilo de Rayo, las bobinas y los puentes:")
	var hojas: int = m.vida
	_elegir(m, "rayo")
	_comprobar(m.sigilo_elegido() == "rayo", "con R se llega al Sigilo de Rayo")
	hojas = m.vida
	_comprobar(await _trazar(m, bobina_sur) and bobina_sur.encendida, "el rayo enciende la bobina")
	_comprobar(m.vida == hojas, "(y a Maisha su propio rayo no le hace nada)")
	_comprobar(_puente("sur").encendido and Estado.tiene("observatorio/puente_sur"), "y con ella se tiende el puente al Claustro")
	await _esperar(1.3)
	m.global_position = _sitio(36, 60)
	await _andar(m, "mover_arriba", 3.0)
	_comprobar(m.global_position.y < 55 * 16, "el Puente de Constelación se pisa y lleva al Claustro de los Telescopios")
	var b1 := _cerca("bobinas", 28, 43)
	var b2 := _cerca("bobinas", 28, 49)
	b1.cargar()
	b1.set("_queda", 0.3)
	await _esperar(0.5)
	_comprobar(not b1.encendida and not _puente("oeste").encendido, "una bobina sola se apaga al rato, y el puente del oeste (que pide dos) no se tiende")
	await _trazar(m, b1)
	await _trazar(m, b2)
	_comprobar(_puente("oeste").encendido, "las dos a la vez: se tiende el puente a la Galería del Solsticio")
	b1.set("_queda", 0.0)
	await _esperar(0.3)
	_comprobar(b1.encendida, "(y sus bobinas ya no se apagan)")
	await _trazar(m, _cerca("bobinas", 44, 43))
	await _trazar(m, _cerca("bobinas", 44, 49))
	_comprobar(_puente("este").encendido, "y lo mismo con el de la Galería de las Campanas")
	_comprobar(not _puente("norte").encendido, "el del norte sigue apagado: pide las dos bobinas mayores")

	print("Saa, el autómata de relojería:")
	var saa: Node2D = _cerca("saas", 36, 46)
	saa.set_process(true)
	m.global_position = saa.global_position + Vector2(-40, 0)
	hojas = m.vida
	for i in 50:
		await _esperar(0.1)
		if m.vida < hojas:
			break
	_comprobar(m.vida < hojas, "ve a Maisha, la sigue despacio y le da un mazazo")
	_comprobar(not saa.recibir_golpe(1, Vector2.UP) and saa.vida == saa.VIDA, "el cetro rebota en el latón")
	_comprobar(await _trazar(m, saa, Vector2(-16, 0)) and saa.fase == saa.Fase.SOBRECARGADO, "el Sigilo de Rayo lo deja sobrecargado")
	var vencidos := int(Estado.extra.get("bestiario", {}).get("saa", 0))
	for i in 3:
		m.global_position = saa.global_position + Vector2(-14, 0)
		m.mirar(Vector2.RIGHT)
		m.golpear()
		await _esperar(0.5)
	await _esperar(0.5)
	_comprobar(not is_instance_valid(saa) or saa.is_queued_for_deletion() or saa.vida <= 0, "tres golpes de cetro y se desarma")
	_comprobar(int(Estado.extra.get("bestiario", {}).get("saa", 0)) == vencidos + 1, "y cuenta en el Bestiario")
	var otro: Node2D = _cerca("saas", 61, 46)
	m.global_position = _sitio(36, 50)
	otro.set_process(true)
	otro.cargar()
	await _esperar(4.8)
	_comprobar(otro.fase != otro.Fase.SOBRECARGADO, "si no se le da a tiempo, se vuelve a dar cuerda")
	otro.set_process(false)

	print("La Galería del Solsticio (hielo y rayo):")
	_elegir(m, "hielo")
	m.global_position = Vector2(16 * 16 + 5, 46 * 16 + 8)
	m.mirar(Vector2.LEFT)
	m.aliento = m.aliento_maximo()
	m.set("_espera_sigilo", 0.0)
	m.sigilo()
	await _esperar(0.5)
	var placas := get_tree().get_nodes_in_group("placas_hielo")
	_comprobar(placas.size() == 1, "el Sigilo de Hielo endurece la tinta del estanque")
	var donde: Vector2 = placas[0].global_position if not placas.is_empty() else Vector2.ZERO
	await _andar(m, "mover_izquierda", 3.0)
	_comprobar(not placas.is_empty() and placas[0].global_position.distance_to(donde) < 1.0, "aquí la tinta está quieta: la placa no deriva")
	_comprobar(m.global_position.x < 13 * 16 + 2, "y por ella se cruza a la isleta (x=%d)" % int(m.global_position.x / 16))
	_elegir(m, "rayo")
	var mayor_o := _cerca("bobinas", 11, 46)
	await _trazar(m, mayor_o, Vector2(14, 6))
	_comprobar(mayor_o.encendida and Estado.tiene("observatorio/mayor_oeste"), "en la isleta, la bobina mayor del oeste se enciende")
	mayor_o.set("_queda", 0.0)
	await _esperar(0.3)
	_comprobar(mayor_o.encendida, "(y esta se queda encendida)")
	m.global_position = _ficha("ficha_darubini").global_position
	await _esperar(0.4)
	_comprobar(Estado.cuantos("ficha_darubini") == 1, "al fondo de la galería, la ficha de Darubini")

	print("La Galería de las Campanas (fuego y rayo):")
	_elegir(m, "fuego")
	var tapon2 := _cerca("charcos_tinta", 63, 36)
	for i in 3:
		await _trazar(m, tapon2, Vector2(0, 26))
		await _esperar(0.4)
	await _esperar(0.7)
	_comprobar(not is_instance_valid(tapon2) or not tapon2.is_in_group("charcos_tinta"), "el fuego derrite el tapón del rincón de las Campanas")
	_elegir(m, "rayo")
	await _trazar(m, _cerca("bobinas", 63, 33), Vector2(0, 18))
	_comprobar(Estado.tiene("observatorio/mayor_este"), "la bobina mayor del este se enciende")
	_comprobar(_puente("norte").encendido, "con las dos mayores, se tiende el puente a la Gran Cúpula")
	await _esperar(1.3)
	m.global_position = _sitio(36, 38)
	await _andar(m, "mover_arriba", 3.5)
	_comprobar(m.global_position.y < 32 * 16, "y se cruza")

	print("Kengele, la Gran Campana Muda:")
	var k: Node2D = get_tree().get_nodes_in_group("jefes")[0]
	_comprobar(k.fase == k.Fase.DORMIDA, "en medio de la Gran Cúpula cuelga una campana enorme")
	_comprobar(get_tree().get_nodes_in_group("diapasones").size() == 4, "con cuatro diapasones alrededor")
	m.global_position = _sitio(36, 27)
	await _esperar(0.5)
	await _leer_dialogo()
	await _esperar(0.3)
	_comprobar(k.fase != k.Fase.DORMIDA and Sonido.musica_actual == "jefe_kengele", "al entrar, despierta (y suena «La campana que no suena»)")
	_comprobar(not k.recibir_golpe(1, Vector2.UP) and k.vida == k.VIDA_MAX, "flotando, el cetro rebota en el bronce")
	k.set_process(false)
	k._cambiar(k.Fase.FLOTA)
	k._ondas.clear()
	k.global_position = k.centro
	m.global_position = k.centro + Vector2(70, 0)
	m.vida = m.vida_maxima()
	m.set("_invulnerable", 0.0)
	hojas = m.vida
	k.tanido(0.0, k.ONDA_ANCHO)
	for i in 12:
		k._mover_ondas(0.1)
	_comprobar(m.vida < hojas, "el tañido mudo: la onda de silencio alcanza a Maisha")
	m.aliento = m.aliento_maximo()
	_comprobar(not m.sigilo(), "y le apaga las runas un momento")
	m.set("_espera_sigilo", 0.0)
	m.set("_invulnerable", 0.0)
	hojas = m.vida
	m.global_position = k.centro + Vector2(0, 80)
	k.tanido(0.0, k.ONDA_ANCHO)
	for i in 12:
		k._mover_ondas(0.1)
	_comprobar(m.vida == hojas, "fuera del abanico, la onda no la toca")
	# la embestida
	k._ondas.clear()
	m.vida = m.vida_maxima()
	m.set("_invulnerable", 0.0)
	hojas = m.vida
	k.global_position = k.centro + Vector2(-90, 0)
	m.global_position = k.centro + Vector2(10, 0)
	k._rumbo = Vector2.RIGHT
	k._cambiar(k.Fase.EMBISTE)
	k._toco = false
	k.set_process(true)
	await _esperar(1.6)
	_comprobar(m.vida < hojas, "la embestida cruza la cúpula y se lleva a Maisha por delante")
	_comprobar(k.fase != k.Fase.ATURDIDA, "sin diapasones cargados, no hay forma de pararla")
	# el diapasón cargado
	k.set_process(false)
	var d: Node2D = _cerca("diapasones", 46, 13)
	m.set("_espera_sigilo", 0.0)
	m.set("_invulnerable", 5.0)
	_comprobar(await _trazar(m, d) and d.encendida, "el Sigilo de Rayo carga un diapasón: zumba")
	m.global_position = d.global_position + Vector2(40, 30)
	k.global_position = d.global_position + Vector2(-110, 10)
	k._rumbo = Vector2.RIGHT
	k._cambiar(k.Fase.EMBISTE)
	k.set_process(true)
	await _esperar(0.6)
	_comprobar(k.fase == k.Fase.ATURDIDA, "embistiendo junto al diapasón cargado, Kengele resuena de verdad y cae aturdida")
	_comprobar(not d.encendida, "(y el diapasón se descarga)")
	for i in 3:
		m.global_position = k.global_position + Vector2(-20, 0)
		m.mirar(Vector2.RIGHT)
		m.golpear()
		await _esperar(0.45)
	_comprobar(k.vida == k.VIDA_MAX - 3, "aturdida, el cetro le entra (%d de vida)" % k.vida)
	await _esperar(0.3)
	_comprobar(k.fase != k.Fase.ATURDIDA, "tras tres golpes se alza otra vez")
	k.vida = 5
	_comprobar(k.furia(), "con la mitad de la vida, se enfurece (dos ondas seguidas y embiste antes)")
	k.set_process(false)
	k.vida = 1
	d.cargar()
	k.global_position = d.global_position + Vector2(-110, 10)
	k._rumbo = Vector2.RIGHT
	k._cambiar(k.Fase.EMBISTE)
	k.set_process(true)
	await _esperar(0.6)
	m.global_position = k.global_position + Vector2(-20, 0)
	m.mirar(Vector2.RIGHT)
	m.golpear()
	await _esperar(0.6)
	_comprobar(Estado.tiene("kengele_vencida") and k.fase == k.Fase.VENCIDA, "vencida, se queda en el suelo: por fin ha sonado")
	_comprobar(int(Estado.extra.get("bestiario", {}).get("kengele", 0)) == 1, "y cuenta en el Bestiario")
	var ficha3 := _ficha("ficha_mlinzi")
	_comprobar(ficha3 != null, "del badajo cae la 3.ª ficha del observatorio")
	m.global_position = ficha3.global_position
	await _esperar(0.4)
	_comprobar(Estado.cuantos("ficha_mlinzi") == 1, "es la de Mlinzi, el campanero")

	print("De vuelta:")
	await _ir("maandiko", "observatorio", "Maandiko")
	_comprobar(_escena() == "Maandiko", "se vuelve a Maandiko por la salida del noroeste")
	m = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	for nombre in ["darubini", "mlinzi"]:
		var e: Node = null
		for a in get_tree().get_nodes_in_group("escribas"):
			if a.nombre == nombre:
				e = a
		_comprobar(e != null and e.id == "escriba_blanco", "en Maandiko, %s está en blanco" % nombre.capitalize())
		m.global_position = (e as Node2D).global_position + Vector2(-18, 6)
		e.interactuar()
		await _leer_dialogo()
		await _esperar(1.0)
		await _leer_dialogo()
		_comprobar(Estado.tiene(nombre + "_nombre") and e.id == "escriba" and Estado.tiene(nombre + "_hablado"), "al darle su ficha, recupera el nombre y habla")

	print()
	print("RESULTADO: todo correcto" if _fallos == 0 else "RESULTADO: %d fallos" % _fallos)
	get_tree().quit(1 if _fallos else 0)
