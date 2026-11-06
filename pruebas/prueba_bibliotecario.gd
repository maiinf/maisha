extends Node
## Prueba automática del Bibliotecario Hueco (jefe de Las Estanterías Colgantes, Sigilia):
##   - Empieza en la sala de lectura ante el atril.
##   - Despierta y levanta su escudo de 3 libros orbitantes.
##   - El escudo absorbe los golpes directos (el cetro rebota).
##   - Al destruir/quemar los libros, cae aturdido y pasa a ser vulnerable.
##   - Recibe daño con cetro o semillas.
##   - Al llegar a 0 de vida, es derrotado, la toga cae al suelo y libera la ficha de Mwalimu.
## Se ejecuta con:  /Applications/Godot.app/Contents/MacOS/Godot --headless res://pruebas/ejecutar.tscn -- prueba_bibliotecario

const BIBLIOTECARIO := preload("res://scripts/enemigos/bibliotecario.gd")

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	Estado.jugando = true

	print("El Bibliotecario Hueco:")
	var jefe: CharacterBody2D = BIBLIOTECARIO.new()
	add_child(jefe)
	await get_tree().process_frame

	_comprobar(jefe.vida == 12, "empieza con 12 de vida")
	_comprobar(jefe.fase == BIBLIOTECARIO.Fase.DORMIDO, "empieza dormido")

	print("Despertar y escudo:")
	jefe.despertar()
	await get_tree().process_frame
	_comprobar(jefe.fase in [BIBLIOTECARIO.Fase.PRESENTACION, BIBLIOTECARIO.Fase.FLOTANDO_ESCUDO], "se presenta y empieza a flotar")
	await _esperar(2.0)
	_comprobar(jefe.fase == BIBLIOTECARIO.Fase.FLOTANDO_ESCUDO, "está flotando con su escudo")
	_comprobar(jefe._libros.size() == 3, "tiene 3 libros orbitando en escudo")

	print("El escudo protector:")
	var golpe_absorbido: bool = jefe.recibir_golpe(1, Vector2.RIGHT)
	_comprobar(not golpe_absorbido and jefe.vida == 12, "el escudo absorbe el golpe directo del cetro (no le hace daño)")

	print("Destrucción de libros y aturdimiento:")
	while not jefe._libros.is_empty():
		var l: Node2D = jefe._libros[0]
		l.call("recibir_danio", 2, l.global_position, "fuego")
		await get_tree().process_frame

	await _esperar(0.3)
	_comprobar(jefe.fase == BIBLIOTECARIO.Fase.ATURDIDO, "al perder los 3 libros cae al suelo aturdido")
	_comprobar(jefe.is_in_group("golpeables") and jefe.is_in_group("daniables"), "aturdido es vulnerable al daño")

	print("Daño en aturdimiento:")
	jefe.recibir_golpe(1, Vector2.DOWN)
	_comprobar(jefe.vida == 11, "un golpe de cetro le quita 1 de vida")
	jefe.recibir_danio(2, jefe.global_position, "explosion")
	_comprobar(jefe.vida == 9, "una explosión de semilla le quita 2 de vida")

	print("Derrota y Ficha de Mwalimu:")
	jefe.recibir_danio(9, jefe.global_position, "fuego")
	await get_tree().process_frame
	_comprobar(jefe.vida == 0, "su vida baja a 0")
	_comprobar(jefe.fase == BIBLIOTECARIO.Fase.VENCIDO, "queda derrotado y la toga cae desinflada")
	_comprobar(Estado.tiene("bibliotecario_vencido"), "queda marcada la victoria en Estado")

	var ficha: Node2D = null
	for r in get_tree().get_nodes_in_group("recogibles"):
		if r.get("objeto") == "ficha_mwalimu":
			ficha = r
			break
	_comprobar(ficha != null and ficha.get("objeto") == "ficha_mwalimu", "aparece la Ficha de Mwalimu, el Guardián de la Memoria")

	if _fallos == 0:
		print("RESULTADO: todo correcto")
		get_tree().quit(0)
	else:
		print("RESULTADO: con fallos (%d)" % _fallos)
		get_tree().quit(1)
