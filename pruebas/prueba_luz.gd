extends Node
## Prueba automática de la luz (el 2.5D): el reloj del día, el relieve de los dibujos, las ventanas que se
## encienden de noche y que las escenas con su propia penumbra (las cuevas) no se mezclan con el ciclo.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_luz

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

	print("El reloj del día:")
	_comprobar(is_equal_approx(Reloj.luz_dia(), 1.0), "antes de llegar a Cuna de Musgo siempre es de día")
	Estado.jugando = true
	var antes := Reloj.hora()
	await _esperar(0.3)
	_comprobar(is_equal_approx(Reloj.hora(), antes), "y el reloj no corre")
	Estado.marcar("visto/cuna_de_musgo")
	Reloj.poner_hora(0.3)
	_comprobar(is_equal_approx(Reloj.luz_dia(), 1.0) and Reloj.momento() == "dia", "a media mañana, pleno día")
	Reloj.poner_hora(0.8)
	_comprobar(is_equal_approx(Reloj.luz_dia(), 0.0) and Reloj.momento() == "noche", "a 0,8, noche cerrada")
	Reloj.poner_hora(0.67)
	_comprobar(Reloj.luz_dia() > 0.1 and Reloj.luz_dia() < 0.9 and Reloj.calidez() > 0.5, "al atardecer, luz a medias y cálida")
	Reloj.poner_hora(0.9999)
	var antes_cero := Reloj.luz_dia()
	Reloj.poner_hora(0.0)
	_comprobar(absf(Reloj.luz_dia() - antes_cero) < 0.02, "el amanecer no da saltos al pasar por el 0 (%.3f y %.3f)" % [antes_cero, Reloj.luz_dia()])
	Reloj.poner_hora(0.5)
	await _esperar(0.5)
	_comprobar(Reloj.hora() > 0.5, "jugando, el reloj avanza")

	print("La aldea, de día y de noche:")
	for m in ["construido_casa_seta", "construido_taller"]:
		Estado.marcar(m)
	get_tree().change_scene_to_file("res://escenas/mundo/cuna_de_musgo.tscn")
	await _esperar(1.5)
	var escena := get_tree().current_scene
	var con_relieve := 0
	for s in escena.find_children("*", "Sprite2D", true, false):
		if (s as Sprite2D).texture is CanvasTexture:
			con_relieve += 1
	_comprobar(con_relieve > 20, "los dibujos del mundo llevan su relieve (%d)" % con_relieve)
	_comprobar(escena.get_node_or_null("Sol") != null and escena.get_node_or_null("LuzDelDia") != null, "hay sol y luz del día")
	var casa: Node2D = null
	for n in escena.find_children("*", "", true, false):
		if n.get_script() and String(n.get_script().resource_path).ends_with("edificio.gd") and n.get("id") == "casa_seta":
			casa = n
	var ventanas: Array = []
	if casa:
		for l in casa.find_children("*", "PointLight2D", true, false):
			if l.has_meta("luz_edificio"):
				ventanas.append(l)
	_comprobar(ventanas.size() == 3, "la casa-seta reconstruida tiene sus 2 ventanas y su farol (%d)" % ventanas.size())
	Reloj.poner_hora(0.3)
	await _esperar(0.2)
	_comprobar(ventanas.size() > 0 and not (ventanas[0] as PointLight2D).visible, "de día, las ventanas están apagadas")
	Reloj.poner_hora(0.8)
	await _esperar(0.2)
	_comprobar(ventanas.size() > 0 and (ventanas[0] as PointLight2D).visible and (ventanas[0] as PointLight2D).energy > 0.5, "de noche, se encienden")
	var tinte := (escena.get_node("LuzDelDia") as CanvasModulate).color
	_comprobar(tinte.b > tinte.r and tinte.v < 0.5, "y el mundo se vuelve oscuro y azulado")

	print("Las cuevas tienen su propia luz:")
	get_tree().change_scene_to_file("res://escenas/mundo/cueva_setas.tscn")
	await _esperar(1.5)
	escena = get_tree().current_scene
	var nuestra := escena.get_node_or_null("LuzDelDia") as CanvasModulate
	_comprobar(nuestra != null and not nuestra.visible, "en la cueva, el ciclo de día y noche se aparta")
	_comprobar(is_equal_approx(Reloj.oscuridad, 1.0), "y los fogonazos se ven enteros (oscuridad %.2f)" % Reloj.oscuridad)

	Estado.jugando = false
	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
