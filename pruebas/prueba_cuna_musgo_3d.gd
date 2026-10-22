extends Node
## Prueba técnica para validar la escena nativa 3D de Cuna de Musgo y la Cámara en Tercera Persona.

func _ready() -> void:
	print("\n--- PRUEBA CUNA DE MUSGO 3D & CÁMARA TERCERA PERSONA ---")
	var escena := load("res://escenas/mundo_3d/cuna_de_musgo_3d.tscn")
	if not escena:
		print("FALLO: No se pudo cargar res://escenas/mundo_3d/cuna_de_musgo_3d.tscn")
		get_tree().quit(1)
		return

	var instancia: Node3D = escena.instantiate()
	add_child(instancia)
	print("  bien: Escena Cuna de Musgo 3D instanciada con éxito")

	var maisha: CharacterBody3D = instancia.get_node_or_null("Maisha3D")
	if not maisha:
		print("FALLO: No se encontró Maisha3D en Cuna de Musgo")
		get_tree().quit(1)
		return
	print("  bien: Maisha3D con controlador en tercera persona detectado")

	var cam: Node3D = instancia.get_node_or_null("CamaraTerceraPersona")
	if not cam:
		print("FALLO: No se encontró CamaraTerceraPersona")
		get_tree().quit(1)
		return
	print("  bien: Cámara orbital en tercera persona activa")

	var arbol: Node3D = instancia.get_node_or_null("GranArbol")
	if not arbol:
		print("FALLO: No se encontró GranArbol")
		get_tree().quit(1)
		return
	print("  bien: El Gran Árbol Sagrado cargado en el centro del poblado")

	var forja: Node3D = instancia.get_node_or_null("ForjaCorteza")
	if not forja:
		print("FALLO: No se encontró ForjaCorteza")
		get_tree().quit(1)
		return
	print("  bien: La Forja de Corteza cargada con éxito")

	# Esperar fotogramas para asentar shaders y render
	for i in 35:
		await get_tree().process_frame

	var img := get_viewport().get_texture().get_image()
	if img and not img.is_empty():
		var err := img.save_png("captura_cuna_musgo_3d_render.png")
		if err == OK:
			print("  bien: Captura visual 3D guardada en captura_cuna_musgo_3d_render.png")

	print("\nRESULTADO: todo correcto en Cuna de Musgo 3D")
	get_tree().quit(0)
