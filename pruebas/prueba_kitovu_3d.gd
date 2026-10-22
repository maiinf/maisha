extends SceneTree
## Validador técnico rápido de la escena nativa 3D del Kitovu.

func _init() -> void:
	print("\n--- PRUEBA KITOVU 3D ---")
	var escena := load("res://escenas/mundo_3d/kitovu_3d.tscn")
	if not escena:
		print("FALLO: No se pudo cargar res://escenas/mundo_3d/kitovu_3d.tscn")
		quit(1)
		return

	var instancia: Node3D = escena.instantiate()
	root.add_child(instancia)
	print("  bien: Escena Kitovu 3D instanciada con éxito")

	var maisha: CharacterBody3D = instancia.get_node_or_null("Maisha3D")
	if not maisha:
		print("FALLO: No se encontró Maisha3D")
		quit(1)
		return
	print("  bien: Maisha3D detectado")

	var granja: Node3D = instancia.get_node_or_null("CasaGranja")
	if not granja:
		print("FALLO: No se encontró CasaGranja")
		quit(1)
		return
	print("  bien: CasaGranja 360° cargada")

	var portal: Node3D = instancia.get_node_or_null("PortalRaiz")
	if not portal:
		print("FALLO: No se encontró PortalRaiz")
		quit(1)
		return
	print("  bien: Portal de Raíz presente")

	var shamba: Node3D = instancia.get_node_or_null("MzeeShambaNPC")
	if not shamba:
		print("FALLO: No se encontró MzeeShambaNPC")
		quit(1)
		return
	print("  bien: MzeeShambaNPC presente")

	instancia.queue_free()
	print("\nRESULTADO: todo correcto (0.1s)")
	quit(0)
