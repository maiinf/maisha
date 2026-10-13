extends Node
## Prueba automática del prototipo de combate (flujo completo de una zona corrupta).
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_combate

const R := preload("res://scripts/combate/reglas_combate.gd")
var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(segundos: float) -> void:
	await get_tree().create_timer(segundos).timeout


func _escena() -> Node:
	var escena: Node = load("res://escenas/prueba_combate.tscn").instantiate()
	get_tree().root.add_child(escena)
	for i in 3:
		await get_tree().process_frame
	return escena


func _ready() -> void:
	Engine.time_scale = 3.0
	var escena: Node = await _escena()
	var maisha: Node2D = escena.get_node("Entidades/Maisha")
	var zona: Node2D = escena.get_node("ZonaCorrupta")
	var centro := zona.global_position

	print("Acercarse a la zona:")
	_comprobar(zona.estado == zona.Estado.DORMIDA, "lejos: la zona duerme")
	maisha.global_position = centro + Vector2(-zona.radios_umbral.x - zona.ancho_borde * 0.5, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	_comprobar(zona.estado == zona.Estado.AVISO, "en el borde: aviso")
	maisha.global_position = centro + Vector2(-zona.radios_umbral.x * 0.85, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	_comprobar(zona.estado == zona.Estado.CERRADA, "al cruzar el umbral: se cierra")
	await _esperar(0.4)
	_comprobar(get_tree().get_nodes_in_group("enemigos").size() == 2, "aparecen 2 Petrinos")

	print("No se puede salir:")
	maisha.global_position = centro + Vector2(-zona.radios_umbral.x * 1.3, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	_comprobar(zona.distancia_normal(maisha.global_position) <= 0.95, "las espinas la mantienen dentro")

	print("Golpe con el cetro:")
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.queue_free()
	await get_tree().process_frame
	zona.set("_invocar", 999.0)   # que no aparezcan más mientras se prueba
	maisha.global_position = centro + Vector2(-120, 60)
	maisha.mirando = "lado"
	maisha.get_node("Sprite").flip_h = false
	var enemigo: Node2D = load("res://scripts/enemigos/petrino.gd").new()
	enemigo.zona = zona
	enemigo.position = maisha.global_position + Vector2(14, 0)
	maisha.get_parent().add_child(enemigo)
	await get_tree().process_frame
	enemigo.set_physics_process(false)    # quieto para la prueba
	maisha.aliento = 50.0
	maisha.golpear()
	await _esperar(0.2)
	_comprobar(enemigo.vida == R.PETRINO_VIDA - 1, "le quita 1 de vida (%d)" % enemigo.vida)
	_comprobar(maisha.aliento > 50.0 + R.GOLPE_RECARGA_ALIENTO - 1.0, "recarga Aliento (%.1f)" % maisha.aliento)
	_comprobar(is_equal_approx(Engine.time_scale, 3.0), "tras la pausa del golpe, el juego vuelve a su velocidad")
	var vida_enemigo: int = enemigo.vida
	maisha.golpear()                       # demasiado pronto: debe ignorarse
	await _esperar(0.12)
	_comprobar(enemigo.vida == vida_enemigo, "no se puede golpear sin esperar entre golpes")
	enemigo.queue_free()

	print("El Petrino muerde y rebota (no se queda pegado):")
	var mordedor: Node2D = load("res://scripts/enemigos/petrino.gd").new()
	mordedor.zona = zona
	mordedor.position = maisha.global_position + Vector2(6, 0)
	maisha.get_parent().add_child(mordedor)
	var vida_m: int = maisha.vida
	await _esperar(0.15)
	_comprobar(maisha.vida == vida_m - R.PETRINO_DANIO, "le quita %d de vida al tocarla" % R.PETRINO_DANIO)
	await _esperar(0.45)
	_comprobar(mordedor.global_position.distance_to(maisha.global_position) > 14.0, "y se aparta (%.0f px)" % mordedor.global_position.distance_to(maisha.global_position))
	mordedor.queue_free()
	maisha.vida = R.VIDA_MAXIMA

	print("La semilla atrapa con raíces y la explosión no falla:")
	maisha.aliento = R.ALIENTO_MAXIMO
	maisha.global_position = centro + Vector2(-140, -40)
	maisha.lanzar_semilla()
	var semilla_t: Node2D = get_tree().get_first_node_in_group("semillas")
	var victima: Node2D = load("res://scripts/enemigos/petrino.gd").new()
	victima.zona = zona
	victima.position = semilla_t.global_position + Vector2(13, 13)   # en diagonal: fuera de la cruz
	maisha.get_parent().add_child(victima)
	maisha.global_position = centro + Vector2(-140, 40)               # Maisha se aparta
	await _esperar(0.3)
	_comprobar(victima.esta_enraizado(), "el enemigo cercano queda atrapado por las raíces")
	var donde: Vector2 = victima.global_position
	await _esperar(0.6)
	_comprobar(victima.global_position.distance_to(donde) < 1.0, "atrapado no se mueve")
	await _esperar(R.SEMILLA_MECHA)
	_comprobar(not is_instance_valid(victima) or victima.vida <= 0, "la explosión lo alcanza aunque esté en diagonal")
	maisha.vida = R.VIDA_MAXIMA

	print("Semillas contra el Núcleo:")
	var nucleo: Node2D = get_tree().get_first_node_in_group("nucleos")
	var casilla_nucleo := R.casilla_de(nucleo.global_position)
	for vez in 3:
		maisha.aliento = R.ALIENTO_MAXIMO
		maisha.agotada = false
		maisha.global_position = R.centro_de(casilla_nucleo + Vector2i(-2, 0))
		var ok: bool = maisha.lanzar_semilla()
		_comprobar(ok, "semilla %d lanzada a 2 casillas del Núcleo" % (vez + 1))
		maisha.global_position = R.centro_de(casilla_nucleo + Vector2i(-2, 3))   # se aparta de la cruz
		await _esperar(R.SEMILLA_MECHA + 0.3)
	_comprobar(zona.estado == zona.Estado.PURGANDO or zona.estado == zona.Estado.PURGADA, "3 explosiones rompen el Núcleo y la zona se purga")
	var registro := get_tree().get_first_node_in_group("registro_brotes")
	_comprobar(registro.hay_brote(casilla_nucleo + Vector2i(-1, 0)), "la explosión deja brotes")
	await _esperar(3.0)
	_comprobar(zona.estado == zona.Estado.PURGADA, "la ola termina: zona purgada")
	_comprobar(get_tree().get_nodes_in_group("enemigos").is_empty(), "no queda ningún enemigo")
	escena.queue_free()
	await get_tree().process_frame

	print("Aliento y agotamiento:")
	escena = await _escena()
	maisha = escena.get_node("Entidades/Maisha")
	maisha.aliento = R.SEMILLA_COSTE
	_comprobar(maisha.lanzar_semilla(), "lanza con el Aliento justo")
	_comprobar(maisha.agotada, "al vaciarse queda agotada")
	_comprobar(not maisha.lanzar_semilla(), "agotada no puede lanzar")
	print("Autodaño:")
	var vida_antes: int = maisha.vida
	await _esperar(R.SEMILLA_MECHA + 0.3)
	_comprobar(maisha.vida == vida_antes - R.EXPLOSION_AUTODANIO, "su propia semilla le quita %d (vida %d)" % [R.EXPLOSION_AUTODANIO, maisha.vida])
	escena.queue_free()
	await get_tree().process_frame

	print("Caer dentro de la zona:")
	escena = await _escena()
	maisha = escena.get_node("Entidades/Maisha")
	zona = escena.get_node("ZonaCorrupta")
	centro = zona.global_position
	maisha.global_position = centro + Vector2(-zona.radios_umbral.x - 20, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	maisha.global_position = centro + Vector2(-zona.radios_umbral.x * 0.85, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	_comprobar(zona.estado == zona.Estado.CERRADA, "zona cerrada")
	maisha.vida = 1
	maisha.set("_invulnerable", 0.0)
	maisha.recibir_danio(1, maisha.global_position + Vector2(5, 0), "contacto")
	_comprobar(maisha.esta_caida, "Maisha cae")
	await _esperar(2.5)
	_comprobar(not maisha.esta_caida and maisha.vida == R.VIDA_MAXIMA, "vuelve con la vida llena")
	_comprobar(zona.estado == zona.Estado.AVISO, "la zona se reinicia y queda en aviso")
	var r: float = zona.distancia_normal(maisha.global_position)
	_comprobar(r > 1.0 and zona.en_borde(maisha.global_position), "aparece en el borde, fuera de las espinas (r=%.2f)" % r)
	_comprobar(get_tree().get_first_node_in_group("nucleos").vida == R.NUCLEO_VIDA, "el Núcleo vuelve a estar entero")

	print("Impacto:")
	var escala := Engine.time_scale
	Impacto.pausa(0.05)
	_comprobar(Engine.time_scale < escala * 0.1, "al acertar, el juego se congela un instante")
	await get_tree().create_timer(0.1, true, false, true).timeout
	_comprobar(is_equal_approx(Engine.time_scale, escala), "y vuelve solo")
	Impacto.poner_temblores(false)
	Impacto.temblar(4.0, 0.3)
	await get_tree().process_frame
	var cam := get_viewport().get_camera_2d()
	_comprobar(cam == null or cam.offset == Vector2.ZERO, "sin temblores, la cámara no tiembla")
	Impacto.poner_temblores(true)

	print("La velocidad del juego (cámara lenta y parón de impacto):")
	var normal := Engine.time_scale
	Impacto.poner_lenta(0.35)
	Impacto.pausa(0.1)                    # un parón que empieza durante la cámara lenta...
	await get_tree().create_timer(0.02, true, false, true).timeout
	Impacto.poner_lenta(1.0)              # ...la cámara lenta acaba antes que el parón...
	await get_tree().create_timer(0.3, true, false, true).timeout
	_comprobar(is_equal_approx(Engine.time_scale, normal), "...y el juego vuelve a su velocidad normal (%.2f)" % Engine.time_scale)
	Impacto.poner_lenta(0.35)
	Impacto.restablecer_velocidad()
	_comprobar(is_equal_approx(Engine.time_scale, normal), "al cambiar de escena, todo a velocidad normal")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	await Sonido.callar()
	get_tree().quit(_fallos)
