extends Node
## Prueba técnica para validar la escena nativa 3D del Kitovu y el controlador Maisha3D.

func _ready() -> void:
	print("\n--- PRUEBA KITOVU 3D ---")
	var escena := load("res://escenas/mundo_3d/kitovu_3d.tscn")
	if not escena:
		print("FALLO: No se pudo cargar res://escenas/mundo_3d/kitovu_3d.tscn")
		get_tree().quit(1)
		return

	var instancia: Node3D = escena.instantiate()
	add_child(instancia)
	print("  bien: Escena Kitovu 3D instanciada con éxito")

	var maisha: CharacterBody3D = instancia.get_node_or_null("Maisha3D")
	if not maisha:
		print("FALLO: No se encontró el nodo Maisha3D en la escena")
		get_tree().quit(1)
		return
	print("  bien: Maisha3D detectado en la escena")

	var granja: Node3D = instancia.get_node_or_null("CasaGranja")
	if not granja:
		print("FALLO: No se encontró la CasaGranja en la escena")
		get_tree().quit(1)
		return
	print("  bien: Modelo 3D sólido de CasaGranja cargado")

	# Esperar fotogramas para que los shaders y renderizado se asienten
	for i in 30:
		await get_tree().process_frame

	var img := get_viewport().get_texture().get_image()
	if img and not img.is_empty():
		var err := img.save_png("captura_kitovu_3d_render.png")
		if err == OK:
			print("  bien: Captura visual 3D guardada en captura_kitovu_3d_render.png")

	print("\nRESULTADO: todo correcto")
	get_tree().quit(0)
