extends SceneTree

func _init() -> void:
	print("Iniciando captura de Cuna de Musgo 3D...")
	var escena_res: PackedScene = load("res://escenas/mundo/3d/cuna_de_musgo_3d.tscn")
	var escena = escena_res.instantiate()
	root.add_child(escena)

	# Esperar 4 frames para renderizado
	for i in range(4):
		await process_frame

	var img = root.get_texture().get_image()
	if img:
		var ruta = "documentacion/capturas/cuna_de_musgo_3d.png"
		var err = img.save_png(ruta)
		print("Captura guardada en %s (err=%d, tam=%dx%d)" % [ruta, err, img.get_width(), img.get_height()])
	else:
		print("No se pudo obtener imagen del viewport")

	quit(0)
