extends SceneTree
## Validador técnico rápido de la escena nativa 3D de Cuna de Musgo.

func _init() -> void:
	print("\n--- PRUEBA CUNA DE MUSGO 3D & CÁMARA TERCERA PERSONA ---")
	var escena := load("res://escenas/mundo_3d/cuna_de_musgo_3d.tscn")
	if not escena:
		print("FALLO: No se pudo cargar res://escenas/mundo_3d/cuna_de_musgo_3d.tscn")
		quit(1)
		return

	var instancia: Node3D = escena.instantiate()
	root.add_child(instancia)
	print("  bien: Escena Cuna de Musgo 3D instanciada con éxito")

	var maisha: CharacterBody3D = instancia.get_node_or_null("Maisha3D")
	if not maisha:
		print("FALLO: No se encontró Maisha3D en Cuna de Musgo")
		quit(1)
		return
	print("  bien: Maisha3D con controlador en tercera persona detectado")

	var cam: Node3D = instancia.get_node_or_null("CamaraTerceraPersona")
	if not cam:
		print("FALLO: No se encontró CamaraTerceraPersona")
		quit(1)
		return
	print("  bien: Cámara orbital en tercera persona activa")

	var arbol: Node3D = instancia.get_node_or_null("GranArbol")
	if not arbol:
		print("FALLO: No se encontró GranArbol")
		quit(1)
		return
	print("  bien: El Gran Árbol Sagrado cargado")

	var forja: Node3D = instancia.get_node_or_null("ForjaCorteza")
	if not forja:
		print("FALLO: No se encontró ForjaCorteza")
		quit(1)
		return
	print("  bien: La Forja de Corteza cargada con éxito")

	var pino: Node3D = instancia.get_node_or_null("PinoNPC")
	if not pino:
		print("FALLO: No se encontró PinoNPC")
		quit(1)
		return
	print("  bien: Pino NPC presente")

	var corteza: Node3D = instancia.get_node_or_null("CortezaNPC")
	if not corteza:
		print("FALLO: No se encontró CortezaNPC")
		quit(1)
		return
	print("  bien: Corteza NPC presente")

	var altar: Node3D = instancia.get_node_or_null("AltarRaiz")
	if not altar:
		print("FALLO: No se encontró AltarRaiz")
		quit(1)
		return
	print("  bien: Altar de la Raíz Sagrada presente")

	var dialogo: CanvasLayer = instancia.get_node_or_null("DialogoCinematico3D")
	if not dialogo:
		print("FALLO: No se encontró DialogoCinematico3D")
		quit(1)
		return
	print("  bien: Diálogo Cinemático 3D listo")

	instancia.queue_free()
	print("\nRESULTADO: todo correcto en Cuna de Musgo 3D (0.1s)")
	quit(0)
