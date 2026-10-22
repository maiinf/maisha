extends Node
## Comprueba que todas las escenas piden archivos que existen (modelos .glb, sonidos, scripts, shaders...).
## Si una escena de Godot nombra un recurso que no está, la escena entera no carga: esta prueba lo avisa
## antes, con la lista de lo que falta. Sirve para que Claude y Gemini no se pisen al sincronizar.

const CARPETAS := ["res://escenas"]


func _ready() -> void:
	print("\n--- PRUEBA RECURSOS DE LAS ESCENAS ---")
	var escenas: Array[String] = []
	for carpeta in CARPETAS:
		_buscar_escenas(carpeta, escenas)
	var faltan := 0
	for ruta in escenas:
		for recurso in _recursos(ruta):
			if not FileAccess.file_exists(recurso):
				print("FALLO: %s pide %s, que no existe" % [ruta, recurso])
				faltan += 1
	print("  bien: revisadas %d escenas" % escenas.size())
	if faltan > 0:
		print("FALLO: faltan %d recursos" % faltan)
		get_tree().quit(1)
		return
	print("\nRESULTADO: todo correcto")
	get_tree().quit(0)


func _buscar_escenas(carpeta: String, lista: Array[String]) -> void:
	var dir := DirAccess.open(carpeta)
	if dir == null:
		return
	for sub in dir.get_directories():
		_buscar_escenas(carpeta.path_join(sub), lista)
	for archivo in dir.get_files():
		if archivo.ends_with(".tscn"):
			lista.append(carpeta.path_join(archivo))


func _recursos(ruta: String) -> Array[String]:
	var lista: Array[String] = []
	var texto := FileAccess.get_file_as_string(ruta)
	var patron := RegEx.create_from_string('\\[ext_resource[^\\]]*path="(res://[^"]+)"')
	for m in patron.search_all(texto):
		lista.append(m.get_string(1))
	return lista
