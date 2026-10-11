extends Node
## Graba en vídeo el comienzo del juego, jugando solo (de la pantalla de inicio al primer recuerdo).
## En el Mac, desde la carpeta del proyecto:
##   godot --path . --resolution 640x360 --fixed-fps 30 --write-movie video.avi res://pruebas/ejecutar.tscn -- grabar_video
var _modo := "inicio"
var _t := 0.0
var _lee := 0.0
var _fin := 0.0

func _pulsa(a: String) -> void:
	Input.action_press(a)
	await get_tree().process_frame
	await get_tree().process_frame
	Input.action_release(a)

func _suelta_todo() -> void:
	for a in ["mover_arriba", "mover_abajo", "mover_izquierda", "mover_derecha"]:
		Input.action_release(a)

func _ready() -> void:
	Estado.olvidar_todo()
	Estado.borrar_partida()
	get_tree().change_scene_to_file("res://escenas/interfaz/inicio.tscn")

func _process(delta: float) -> void:
	_t += delta
	var d = get_tree().get_first_node_in_group("dialogo")
	var escena := get_tree().current_scene
	match _modo:
		"inicio":
			if _t > 4.5 and escena and escena.name == "Inicio":
				escena._al_elegir(escena._acciones.find("nueva"))
				_modo = "kitovu"
		"kitovu":
			if d and d.hablando:
				_suelta_todo()
				_lee += delta
				var espera := 3.2 if d.get("_ilustracion_objetivo") > 0.5 else 2.2
				if _lee > espera and d._linea_completa():
					_lee = 0.0
					_pulsa("accion")
				return
			_lee = 0.0
			var ch := get_tree().get_first_node_in_group("chispas")
			var m := get_tree().get_first_node_in_group("maisha")
			if ch and m:
				var obj: Vector2 = ch.global_position + Vector2(0, 26)
				var v: Vector2 = obj - m.global_position
				_suelta_todo()
				if v.length() > 10.0:
					if absf(v.x) > 4.0:
						Input.action_press("mover_derecha" if v.x > 0 else "mover_izquierda")
					if absf(v.y) > 4.0:
						Input.action_press("mover_abajo" if v.y > 0 else "mover_arriba")
			if Estado.tiene("recuerdo_1"):
				_fin += delta
				if _fin > 4.0:
					_suelta_todo()
					_modo = "fin"
					await Sonido.callar()
					get_tree().quit()
	if _t > 150.0:
		get_tree().quit()
