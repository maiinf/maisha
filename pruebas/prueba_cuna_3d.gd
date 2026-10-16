extends Node
## Prueba automática de la escena Cuna de Musgo 3D y modelos importados de Blender.
## Se ejecuta con: godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_cuna_3d

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
	print("Comprobando modelos 3D generados en Blender:")
	var modelos := [
		"res://modelos/personajes/maisha.glb",
		"res://modelos/personajes/pino.glb",
		"res://modelos/personajes/mzee_shamba.glb",
		"res://modelos/personajes/corteza.glb",
		"res://modelos/enemigos/petrino_giza.glb",
		"res://modelos/enemigos/mzizi_raiz.glb",
		"res://modelos/entorno/gran_arbol.glb",
		"res://modelos/entorno/casa_pino.glb",
		"res://modelos/entorno/forja_corteza.glb",
		"res://modelos/entorno/molino_shamba.glb",
		"res://modelos/entorno/puente_madera.glb",
		"res://modelos/entorno/farol_madera.glb",
		"res://modelos/entorno/bloque_hierba.glb",
		"res://modelos/entorno/bloque_risco.glb",
		"res://modelos/entorno/bloque_canal_agua.glb",
		"res://modelos/entorno/bloque_camino.glb",
		"res://modelos/objetos/semilla_explosiva.glb",
		"res://modelos/objetos/cetro_raiz.glb"
	]
	for m in modelos:
		_comprobar(FileAccess.file_exists(m), "existe el archivo %s" % m.get_file())

	print("\nInstanciando escena Cuna de Musgo 3D:")
	var escena_res: PackedScene = load("res://escenas/mundo/3d/cuna_de_musgo_3d.tscn")
	_comprobar(escena_res != null, "se carga la escena cuna_de_musgo_3d.tscn")
	var escena = escena_res.instantiate()
	_comprobar(escena != null, "se instancia la escena")
	get_tree().root.add_child(escena)

	await _esperar(0.5)

	# Comprobaciones de nodos en la escena 3D
	var maisha = escena.find_child("Maisha3D", true, false)
	_comprobar(maisha != null, "Maisha3D existe y está en la escena")
	_comprobar(maisha is CharacterBody3D, "Maisha3D es CharacterBody3D con físicas")

	var camara = escena.find_child("CamaraCuna3D", true, false)
	_comprobar(camara != null and camara is Camera3D, "CamaraCuna3D existe y es Camera3D")

	var sol = escena.find_child("SolDireccional", true, false)
	_comprobar(sol != null and sol is DirectionalLight3D, "SolDireccional existe y proyecta sombras")

	var edificios = escena.find_child("Edificios", true, false)
	_comprobar(edificios != null, "Edificios de Cuna de Musgo existen")

	var pino = null
	var corteza = null
	var shamba = null
	for c in escena.get_children():
		if c.get_meta("npc_id", "") == "pino": pino = c
		if c.get_meta("npc_id", "") == "corteza": corteza = c
		if c.get_meta("npc_id", "") == "shamba": shamba = c

	_comprobar(pino != null, "Pino (NPC) está en la aldea")
	_comprobar(corteza != null, "Corteza (NPC) está en la forja")
	_comprobar(shamba != null, "Mzee Shamba (NPC) está junto al molino")

	print("\nProbando ciclo horario y funciones de escena:")
	escena.call("_aplicar_iluminacion", 1) # Noche
	_comprobar(sol.light_energy < 0.5, "iluminación nocturna atenúa el sol")
	escena.call("_aplicar_iluminacion", 0) # Atardecer
	_comprobar(sol.light_energy > 1.0, "iluminación de atardecer restaura tono cálido")

	print("\nResultado final prueba Cuna 3D:")
	if _fallos == 0:
		print("  TODAS LAS COMPROBACIONES HAN PASADO (0 fallos)")
		get_tree().quit(0)
	else:
		print("  FALLOS DETECTADOS: %d" % _fallos)
		get_tree().quit(1)
