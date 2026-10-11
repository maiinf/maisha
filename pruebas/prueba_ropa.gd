extends Node
## Prueba automática de la ropa por capas.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_ropa

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _capas(ropa: Node) -> Array[Sprite2D]:
	var lista: Array[Sprite2D] = []
	var detras: Node = ropa.get_parent().get_node("RopaDetras")
	for hijo in ropa.get_children() + detras.get_children():
		if hijo is Sprite2D and not hijo.is_queued_for_deletion():
			lista.append(hijo)
	return lista


## true si la pieza se dibuja detrás de Maisha (está en RopaDetras, antes del dibujo)
func _va_detras(capa: Sprite2D, sprite: Node) -> bool:
	return capa.get_parent().name == "RopaDetras" and capa.get_parent().get_index() < sprite.get_index()


func _ready() -> void:
	var maisha: Node = load("res://escenas/personajes/maisha.tscn").instantiate()
	get_tree().root.add_child(maisha)
	await get_tree().process_frame
	var ropa: Node = maisha.get_node("Ropa")
	var sprite: AnimatedSprite2D = maisha.get_node("Sprite")

	print("Poner y quitar:")
	_comprobar(_capas(ropa).is_empty(), "empieza sin ropa")
	ropa.poner("corona_hojas")
	ropa.poner("capa_musgo")
	await get_tree().process_frame
	_comprobar(ropa.lleva("corona_hojas") and ropa.lleva("capa_musgo"), "lleva corona y capa")
	_comprobar(_capas(ropa).size() == 3, "mirando abajo: corona + capa + broche = 3 capas (%d)" % _capas(ropa).size())
	ropa.alternar("corona_hojas")
	await get_tree().process_frame
	_comprobar(not ropa.lleva("corona_hojas") and _capas(ropa).size() == 2, "alternar quita la corona")
	ropa.poner("corona_hojas")
	await get_tree().process_frame

	print("Cambiar por zonas (teclas 1 a 7 de la escena de prueba):")
	ropa.quitar_zona("cabeza")
	ropa.siguiente_en_zona("cabeza")
	_comprobar(ropa.lleva("corona_hojas"), "zona cabeza: nada -> corona")
	ropa.siguiente_en_zona("cabeza")
	_comprobar(ropa.lleva("sombrero_paja"), "zona cabeza: corona -> sombrero de paja")
	ropa.siguiente_en_zona("cabeza")
	_comprobar(not ropa.puestas().has("cabeza"), "zona cabeza: sombrero -> nada")
	ropa.siguiente_en_zona("cara")
	_comprobar(not ropa.puestas().has("cara"), "zona sin prendas: no hace nada")
	ropa.poner("corona_hojas")
	await get_tree().process_frame

	print("Delante y detrás:")
	var capa_abajo: Sprite2D = null
	for c in _capas(ropa):
		if c.texture.resource_path.ends_with("capa_musgo_abajo.png"):
			capa_abajo = c
	_comprobar(capa_abajo != null and _va_detras(capa_abajo, sprite), "mirando abajo, la capa va detrás")
	maisha.mirando = "arriba"
	await get_tree().physics_frame
	await get_tree().process_frame
	var capa_arriba: Sprite2D = null
	for c in _capas(ropa):
		if c.texture.resource_path.ends_with("capa_musgo_arriba.png"):
			capa_arriba = c
	_comprobar(capa_arriba != null and not _va_detras(capa_arriba, sprite), "mirando arriba, la capa va delante")

	print("Sigue a la cabeza al respirar:")
	maisha.mirando = "abajo"
	await get_tree().physics_frame
	sprite.pause()
	sprite.frame = 0
	await get_tree().process_frame
	var corona: Sprite2D = null
	for c in _capas(ropa):
		if c.texture.resource_path.ends_with("corona_hojas_abajo.png"):
			corona = c
	var y0 := corona.position.y
	sprite.frame = 1   # en este fotograma la cabeza baja 1 píxel
	await get_tree().process_frame
	_comprobar(corona.position.y == y0 + 1.0, "la corona baja 1 píxel con la cabeza (%s -> %s)" % [y0, corona.position.y])

	print("Reflejo al mirar a la izquierda:")
	maisha.mirando = "lado"
	await get_tree().physics_frame
	sprite.pause()
	sprite.frame = 0
	sprite.flip_h = false
	await get_tree().process_frame
	var capa_lado: Sprite2D = null
	for c in _capas(ropa):
		if c.texture.resource_path.ends_with("capa_musgo_lado.png"):
			capa_lado = c
	_comprobar(capa_lado != null and _va_detras(capa_lado, sprite), "de perfil, la capa va detrás")
	var x_derecha := capa_lado.position.x
	var ancho := capa_lado.texture.get_width()
	sprite.flip_h = true
	sprite.frame = 1
	sprite.frame = 0
	await get_tree().process_frame
	# la capa reflejada debe quedar simétrica respecto al centro del dibujo (x = 0)
	_comprobar(capa_lado.flip_h and is_equal_approx(capa_lado.position.x, -(x_derecha + ancho)),
		"reflejada y simétrica (%s -> %s)" % [x_derecha, capa_lado.position.x])

	print("El cetro se mueve limpio al andar (1 píxel como mucho entre fotogramas):")
	var anclajes: Dictionary = (load("res://datos/maisha_anclajes.json") as JSON).data
	for nombre in ["andar_abajo", "andar_arriba", "andar_lado", "reposo_abajo", "reposo_arriba", "reposo_lado"]:
		var lista: Array = anclajes[nombre]
		var salto := 0.0
		for i in lista.size():
			var a: Array = lista[i]["mano"]
			var b: Array = lista[(i + 1) % lista.size()]["mano"]
			salto = maxf(salto, maxf(absf(a[0] - b[0]), absf(a[1] - b[1])))
		_comprobar(salto <= 1.0, "%s: salto máximo %d px" % [nombre, salto])

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	await Sonido.callar()
	get_tree().quit(_fallos)
