extends Node
## Prueba automática del blindaje de estabilidad:
##   - Watchdog de pausas de impacto y cámara lenta en Impacto
##   - Restablecimiento total de estados, temporizadores y fuerzas en Maisha.revivir()
##   - Disipación de fuerzas (empuje y viento) durante cinemáticas/inacción
##   - Cierre forzado y desbloqueo seguro de diálogos en Dialogo.cerrar()
##   - Guardado atómico (.tmp), respaldo (.bak) y recuperación ante partidas corruptas en Estado
## Se ejecuta con:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_estabilidad

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _ready() -> void:
	print("Blindaje de Impacto y velocidad:")
	_probar_impacto()

	print("Blindaje de Maisha y revivir():")
	_probar_maisha()

	print("Blindaje de Diálogo:")
	_probar_dialogo()

	print("Blindaje de guardado atómico y recuperación .bak:")
	_probar_guardado()

	if _fallos == 0:
		print("RESULTADO: todo correcto")
	else:
		print("RESULTADO: %d fallos" % _fallos)
	get_tree().quit(0 if _fallos == 0 else 1)


func _probar_impacto() -> void:
	# 1. restablecer_velocidad limpia pausas y lentitud
	Impacto.poner_lenta(0.3)
	Impacto.set("_pausas", 3)
	Impacto.restablecer_velocidad()
	_comprobar(is_equal_approx(Engine.time_scale, 1.0), "restablecer_velocidad() restaura Engine.time_scale a 1.0")
	_comprobar(Impacto.get("_pausas") == 0, "_pausas queda en 0 tras restablecer")

	# 2. Watchdog de pausa de impacto si un timer se interrumpe
	Impacto.set("_pausas", 1)
	Impacto.call("_aplicar_velocidad")
	_comprobar(Engine.time_scale < 0.1, "pausa de impacto reduce velocidad (< 0.1)")
	# Simular paso del tiempo acumulado en el watchdog (> 1.2 s)
	Impacto.set("_pausa_desde", 1.3)
	Impacto._process(0.016)
	_comprobar(Impacto.get("_pausas") == 0, "el watchdog apaga _pausas tras exceder 1.2 s")
	_comprobar(is_equal_approx(Engine.time_scale, 1.0), "la velocidad vuelve a 1.0 automáticamente")

	# 3. Watchdog de cámara lenta
	Impacto.poner_lenta(0.2)
	_comprobar(Engine.time_scale < 0.3, "poner_lenta(0.2) reduce velocidad")
	Impacto.set("_lenta_desde", 8.5)
	Impacto._process(0.016)
	_comprobar(is_equal_approx(Engine.time_scale, 1.0), "el watchdog apaga la cámara lenta tras exceder 8 s")


func _probar_maisha() -> void:
	var maisha_escena: PackedScene = load("res://escenas/personajes/maisha.tscn")
	var maisha = maisha_escena.instantiate()
	add_child(maisha)

	# Simular estados alterados y bloqueo de acción
	maisha.vida = 1
	maisha.aliento = 0.0
	maisha.agotada = true
	maisha.esta_caida = true
	maisha.puede_actuar = false
	maisha.corriendo = true
	maisha.lentitud = 0.4
	maisha.pegajoso = 5.0
	maisha.hundida = 3.0
	maisha.mareo = 4.0
	maisha.viento = Vector2(100, 0)
	maisha.set("_empuje", Vector2(80, 0))
	maisha.set("_emocion", 2.0)
	maisha.set("_tiempo_agotada", 1.5)
	maisha.set("_lentitud_vuelve", 0.05)
	maisha.set("_lenta_sin_motivo", 15.0)

	# Revivir
	maisha.revivir(Vector2(50, 50))

	_comprobar(maisha.global_position == Vector2(50, 50), "revivir() coloca a Maisha en la posición indicada")
	_comprobar(maisha.vida == maisha.vida_maxima(), "vida restaurada al máximo")
	_comprobar(maisha.aliento == maisha.aliento_maximo(), "aliento restaurado al máximo")
	_comprobar(maisha.puede_actuar == true, "puede_actuar restablecido a true")
	_comprobar(maisha.esta_caida == false, "esta_caida restablecido a false")
	_comprobar(maisha.agotada == false, "agotada restablecido a false")
	_comprobar(maisha.corriendo == false, "corriendo restablecido a false")
	_comprobar(maisha.lentitud == 1.0, "lentitud restablecida a 1.0")
	_comprobar(maisha.pegajoso == 0.0, "pegajoso restablecido a 0.0")
	_comprobar(maisha.hundida == 0.0, "hundida restablecido a 0.0")
	_comprobar(maisha.mareo == 0.0, "mareo restablecido a 0.0")
	_comprobar(maisha.viento == Vector2.ZERO, "viento restablecido a cero")
	_comprobar(maisha.get("_empuje") == Vector2.ZERO, "_empuje restablecido a cero")
	_comprobar(maisha.get("_emocion") == 0.0, "_emocion restablecida a 0.0")
	_comprobar(maisha.get("_tiempo_agotada") == 0.0, "_tiempo_agotada restablecida a 0.0")

	# Probar disipación de empuje mientras puede_actuar es false
	maisha.puede_actuar = false
	maisha.set("_empuje", Vector2(100, 0))
	maisha.viento = Vector2(100, 0)
	maisha._physics_process(0.1)
	_comprobar(maisha.get("_empuje").x < 100.0, "el empuje se disipa aunque puede_actuar sea false")
	_comprobar(maisha.viento.x < 100.0, "el viento se disipa aunque puede_actuar sea false")

	maisha.queue_free()


func _probar_dialogo() -> void:
	var dialogo_script: GDScript = load("res://scripts/interfaz/dialogo.gd")
	var dialogo = dialogo_script.new()
	add_child(dialogo)

	# Simular diálogo abierto y congelación del árbol
	dialogo.hablando = true
	dialogo.set("_pause_mio", true)
	get_tree().paused = true

	# Cerrar forzado
	dialogo.cerrar()

	_comprobar(dialogo.hablando == false, "cerrar() pone hablando a false")
	_comprobar(get_tree().paused == false, "cerrar() quita la pausa del árbol")
	dialogo.queue_free()


func _probar_guardado() -> void:
	var ruta_test := "user://test_estabilidad_partida.json"
	Estado.ruta_partida = ruta_test
	Estado.borrar_partida()

	# Configurar partida
	Estado.olvidar_todo()
	Estado.jugando = true
	Estado.escena_actual = "prados_del_eco"
	Estado.lugar = "Prados del Eco"
	Estado.marcar("test_marca_1")
	Estado.marcar("test_marca_2")
	Estado.guardar()

	_comprobar(FileAccess.file_exists(ruta_test), "guardar() crea el archivo principal")
	_comprobar(Estado.hay_partida(), "hay_partida() detecta la partida")

	# Segundo guardado crea la copia .bak
	Estado.marcar("test_marca_3")
	Estado.guardar()
	_comprobar(FileAccess.file_exists(ruta_test + ".bak"), "guardar() genera la copia de respaldo .bak")

	# Simular corte de corriente con truncamiento a 0 bytes en el archivo principal
	var archivo_roto := FileAccess.open(ruta_test, FileAccess.WRITE)
	archivo_roto.store_string("")
	archivo_roto.close()

	# leer_partida debe recuperarse automáticamente desde .bak
	var datos_recuperados := Estado.leer_partida()
	_comprobar(not datos_recuperados.is_empty(), "leer_partida() se recupera del archivo .bak ante archivo principal truncado a 0 bytes")
	_comprobar(datos_recuperados.get("escena") == "prados_del_eco", "la escena recuperada de .bak es correcta")

	# Limpiar
	Estado.borrar_partida()
	_comprobar(not FileAccess.file_exists(ruta_test), "borrar_partida() elimina el archivo principal")
	_comprobar(not FileAccess.file_exists(ruta_test + ".bak"), "borrar_partida() elimina el archivo .bak")
	_comprobar(not FileAccess.file_exists(ruta_test + ".tmp"), "borrar_partida() elimina el archivo .tmp")
