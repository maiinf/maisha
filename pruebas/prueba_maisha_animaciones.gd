extends Node
## Prueba automática de las animaciones de Maisha.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_maisha_animaciones
## Comprueba que existen las 6 animaciones con 4 fotogramas y que Maisha mira hacia donde camina.

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _ready() -> void:
	var escena: Node = load("res://escenas/personajes/maisha.tscn").instantiate()
	get_tree().root.add_child(escena)
	var sprite: AnimatedSprite2D = escena.get_node("Sprite")
	var marcos: SpriteFrames = sprite.sprite_frames

	print("Animaciones:")
	for nombre in ["reposo_abajo", "reposo_arriba", "reposo_lado", "andar_abajo", "andar_arriba", "andar_lado"]:
		_comprobar(marcos.has_animation(nombre) and marcos.get_frame_count(nombre) == 4,
			nombre + " tiene 4 fotogramas")
		var tex: Texture2D = marcos.get_frame_texture(nombre, 0)
		_comprobar(tex != null and tex.get_width() == 24 and tex.get_height() == 32, nombre + " mide 24x32")

	print("Direcciones:")
	var casos := [
		["mover_abajo", "andar_abajo", false],
		["mover_arriba", "andar_arriba", false],
		["mover_derecha", "andar_lado", false],
		["mover_izquierda", "andar_lado", true],
	]
	for caso in casos:
		Input.action_press(caso[0])
		for i in 6:
			await get_tree().physics_frame
		_comprobar(sprite.animation == caso[1] and sprite.flip_h == caso[2],
			"%s -> %s (reflejado: %s)" % [caso[0], caso[1], caso[2]])
		Input.action_release(caso[0])
		for i in 3:
			await get_tree().physics_frame
		var reposo: String = String(caso[1]).replace("andar", "reposo")
		_comprobar(sprite.animation == reposo, "al soltar -> " + reposo)

	print("Diagonal (no debe parpadear entre direcciones):")
	Input.action_press("mover_derecha")
	for i in 4:
		await get_tree().physics_frame
	Input.action_press("mover_abajo")
	var cambios := 0
	var anterior := sprite.animation
	for i in 30:
		await get_tree().physics_frame
		if sprite.animation != anterior:
			cambios += 1
			anterior = sprite.animation
	_comprobar(cambios == 0, "en diagonal mantiene la dirección (cambios: %d)" % cambios)
	Input.action_release("mover_derecha")
	Input.action_release("mover_abajo")

	print("Correr y expresiones:")
	for nombre in ["correr_abajo", "correr_arriba", "correr_lado", "sorpresa_abajo", "danio_abajo", "danio_arriba",
			"danio_lado", "celebrar_abajo", "despertar_abajo"]:
		_comprobar(marcos.has_animation(nombre), "existe " + nombre)
	for i in 5:
		await get_tree().physics_frame
	Input.action_press("correr")
	Input.action_press("mover_derecha")
	for i in 8:
		await get_tree().physics_frame
	var maisha: CharacterBody2D = escena
	_comprobar(sprite.animation == "correr_lado" and maisha.velocity.x > maisha.VELOCIDAD * 1.5, "con C corre (%.0f px/s)" % maisha.velocity.x)
	Input.action_release("mover_derecha")
	Input.action_release("correr")
	for i in 3:
		await get_tree().physics_frame
	maisha.celebrar()
	await get_tree().physics_frame
	_comprobar(sprite.animation == "celebrar_abajo", "celebra mirando a la pantalla")
	await get_tree().create_timer(1.8).timeout
	_comprobar(sprite.animation == "reposo_abajo", "y vuelve a estar quieta")
	# celebrar justo a mitad de un golpe (al purgar una zona dando cetrazos): no se queda celebrando
	maisha.golpear()
	await get_tree().physics_frame
	maisha.celebrar()
	await get_tree().create_timer(0.4).timeout
	Input.action_press("mover_abajo")
	for i in 6:
		await get_tree().physics_frame
	_comprobar(sprite.animation == "andar_abajo", "si celebra a mitad de un golpe y echa a andar, anda (%s)" % sprite.animation)
	Input.action_release("mover_abajo")
	for i in 3:
		await get_tree().physics_frame
	maisha.golpear()
	await get_tree().physics_frame
	_comprobar(String(sprite.animation).begins_with("golpe_"), "y puede volver a golpear")
	await get_tree().create_timer(0.5).timeout
	maisha.recibir_danio(1, maisha.global_position + Vector2(10, 0), "golpe")
	await get_tree().physics_frame
	_comprobar(String(sprite.animation).begins_with("danio_"), "al recibir daño pone cara de dolor")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	await Sonido.callar()
	get_tree().quit(_fallos)
