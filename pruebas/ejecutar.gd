extends Node
## Lanza una prueba automática sin abrir el editor:
##   godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_prados
## (Se hace con una escena, y no con --script, para que funcione Estado, que se carga solo al arrancar.)


func _ready() -> void:
	var argumentos := OS.get_cmdline_user_args()
	if argumentos.is_empty():
		print("Falta el nombre de la prueba, por ejemplo:  -- prueba_prados")
		get_tree().quit(1)
		return
	# las pruebas guardan en otro archivo, para no tocar la partida de verdad
	Estado.ruta_partida = "user://partida_pruebas.json"
	Estado.borrar_partida()
	var prueba := Node.new()
	prueba.set_script(load("res://pruebas/%s.gd" % argumentos[0]))
	# cuelga de la raíz, no de esta escena: así sobrevive a los cambios de escena
	get_tree().root.add_child.call_deferred(prueba)
