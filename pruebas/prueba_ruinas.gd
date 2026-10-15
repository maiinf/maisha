extends Node
## Prueba automática de las Ruinas del Primer Árbol (el final de Raíz): la llegada, la pelea contra el miedo del
## árbol (despertar las nueve piedras del recuerdo y romper el corazón de Giza), el final y volver después.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_ruinas

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 120:
		if not dialogo.hablando:
			return
		dialogo.pasar()
		await _esperar(0.06)


## Lee una conversación entera (con ilustraciones, que tiene pausas entre partes) hasta que se pone una marca
func _leer_hasta(marca: String, segundos := 25.0) -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	var t := 0.0
	while t < segundos and not Estado.tiene(marca):
		if dialogo.hablando:
			dialogo.pasar()
		await _esperar(0.06)
		t += 0.06
	await _esperar(0.3)


func _escena() -> String:
	var e := get_tree().current_scene
	return e.name if e else ""


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["cetro_recibido", "visto/cuna_de_musgo", "gruta_guardian", "nueve_ecos", "sendero_abierto", "sendero_olvidado"]:
		Estado.marcar(m)
	Estado.jugando = true
	get_tree().change_scene_to_file("res://escenas/mundo/ruinas_primer_arbol.tscn")
	await _esperar(1.5)
	var esc := get_tree().current_scene
	var maisha := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var arbol: Node2D = esc.get("arbol")
	var miedo: Node = esc.get("miedo")

	print("Las Ruinas:")
	_comprobar(_escena() == "RuinasPrimerArbol" and Sonido.musica_actual == "ruinas", "se llega a las Ruinas, con su música")
	_comprobar(Misiones.estado(Misiones.buscar("sendero_olvidado")) == "hecha", "la misión del Sendero Olvidado se cumple al llegar")
	_comprobar(get_tree().get_nodes_in_group("piedras_recuerdo").size() == 9, "nueve piedras del recuerdo en corro")

	print("La pelea contra el miedo del árbol:")
	maisha.global_position = arbol.global_position + Vector2(0, 150)
	await _esperar(1.0)
	await _leer_hasta("ruinas_llegada")
	await _esperar(0.3)
	_comprobar(Estado.tiene("ruinas_llegada") and miedo.activo, "al pisar la plaza, el árbol habla y empieza la pelea")
	_comprobar(Sonido.musica_actual == "jefe_arbol", "con la música del jefe")
	_comprobar(Misiones.estado(Misiones.buscar("primer_arbol")) == "activa", "y la misión «El Primer Árbol»")
	maisha.set("vida", 99)
	var piedras := get_tree().get_nodes_in_group("piedras_recuerdo")
	var p0: Node2D = piedras[0]
	maisha.global_position = p0.global_position + Vector2(0, 14)
	await _esperar(0.2)
	Input.action_press("accion")
	await _esperar(2.0)
	Input.action_release("accion")
	_comprobar(p0.despierta and miedo.despiertas == 1, "manteniendo Acción junto a una piedra, se despierta")
	_comprobar(p0.is_in_group("braseros"), "y da calor")
	for p in piedras:
		p.call("despertar")
	await _esperar(0.3)
	_comprobar(miedo.despiertas == 9 and arbol.corazon_abierto, "con las nueve, se abre el corazón de Giza")

	print("El corazón de Giza:")
	maisha.global_position = arbol.global_position + Vector2(0, 26)
	maisha.call("mirar", Vector2.UP)
	await _esperar(0.3)
	for i in 8:
		if not arbol.corazon_abierto:
			break
		maisha.global_position = arbol.global_position + Vector2(0, 26)
		maisha.call("golpear")
		await _esperar(0.55)
	_comprobar(not arbol.corazon_abierto, "a golpes de cetro, el corazón se rompe")
	await _esperar(4.0)
	await _leer_hasta("primer_arbol_libre", 40.0)
	await _esperar(1.0)
	_comprobar(Estado.tiene("primer_arbol_libre") and Estado.tiene("mauti_libre"), "el árbol se cura y Mauti queda libre")
	_comprobar(Estado.tiene("semilla_primer_arbol"), "y cae la Semilla del Primer Árbol")
	_comprobar(arbol.curado and not miedo.activo, "la pelea termina")
	var fin := false
	for n in esc.get_children():
		if n.get_script() and String(n.get_script().resource_path).ends_with("fin_mundo.gd"):
			fin = n.abierto
	_comprobar(fin, "sale la pantalla del final del mundo")
	_comprobar(Misiones.estado(Misiones.buscar("primer_arbol")) == "hecha", "y se cumple la misión")
	_comprobar(Bestiario.rango("miedo") >= 1, "el miedo del árbol entra en el Bestiario (rango %d)" % Bestiario.rango("miedo"))

	print("Volver después:")
	get_tree().change_scene_to_file("res://escenas/mundo/ruinas_primer_arbol.tscn")
	await _esperar(1.5)
	esc = get_tree().current_scene
	arbol = esc.get("arbol")
	_comprobar(arbol.curado and not esc.get("miedo").activo, "el árbol sigue curado y no hay pelea")
	maisha = get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	var salida: Area2D = null
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == "sendero":
			salida = p
	maisha.global_position = salida.global_position + Vector2(0, -30)
	await _esperar(0.3)
	Input.action_press("mover_abajo")
	for i in 400:
		if Estado.cambiando:
			break
		await get_tree().process_frame
	Input.action_release("mover_abajo")
	for i in 300:
		if _escena() == "SenderoOlvidado" and not Estado.cambiando:
			break
		await get_tree().process_frame
	_comprobar(_escena() == "SenderoOlvidado", "por el sur se baja al Sendero Olvidado")

	Estado.jugando = false
	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
