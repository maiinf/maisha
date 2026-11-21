extends Node
## Prueba automática del Mercado del Crepúsculo (Jioni, parte 2): con el primer Farol de la Hora colgado descansa
## Kikombe, regala el farol de su puesto y abre su tienda (cuatro cosas); el reloj de bolsillo, la lente de prisma, las
## botas de arena firme y la Capa del Farolillero hacen lo que dicen; y con los doce faroles colgados Kibatari da la
## Bendición del Crepúsculo (+1 hoja de vida).
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_mercado_crepusculo

const RESONANCIA := preload("res://scripts/combate/resonancia_ambar.gd")

var _fallos := 0


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _escena() -> String:
	var e := get_tree().current_scene
	return e.name if e else ""


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 200:
		if not dialogo.hablando:
			await _esperar(0.4)
			if not dialogo.hablando:
				return
		dialogo.pasar()
		await _esperar(0.08)


func _ir(escena: String, puerta: String, nombre: String) -> void:
	Estado.ir_a(escena, puerta)
	for i in 300:
		if _escena() == nombre and not Estado.cambiando:
			break
		await get_tree().process_frame
	await _esperar(1.0)


func _vecino(id: String) -> Node2D:
	for v in get_tree().get_nodes_in_group("aldeanos"):
		if v.id == id and not v.is_queued_for_deletion():
			return v
	return null


func _hablar(m: CharacterBody2D, quien: Node2D) -> void:
	m.global_position = quien.global_position + Vector2(0, 14)
	quien.interactuar()
	await _leer_dialogo()


func _puerta(id: String) -> Node2D:
	for p in get_tree().get_nodes_in_group("puertas"):
		if p.id == id:
			return p
	return null


func _tienda() -> CanvasLayer:
	for i in 80:
		for n in get_tree().current_scene.get_children():
			if n.get("tendero") == "kikombe":
				return n
		var dialogo := get_tree().get_first_node_in_group("dialogo")
		if dialogo.hablando:
			dialogo.pasar()
		await _esperar(0.08)
	return null


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for marca in ["cetro_recibido", "sigilia_libre", "cetro_nexo", "asterhaul_libre", "nexo_despierto", "mirador_ocaso",
			"arco_atardecer_abierto", "jioni", "jioni_llegada", "kibatari_conocido", "kibatari_caminos", "mwanga_reloj"]:
		Estado.marcar(marca)
	Estado.dar("farol_hora", 1)
	Estado.jugando = true
	await _ir("jioni", "mirador", "Jioni")
	var m := get_tree().get_first_node_in_group("maisha") as CharacterBody2D
	m.set("_invulnerable", 900.0)

	print("Kikombe abre el Mercado del Crepúsculo:")
	_comprobar(_vecino("kikombe_desvelado") != null and not Estado.tiene("kikombe_abierto"), "sin faroles, Kikombe sigue sirviendo té de pie")
	var postes := get_tree().get_nodes_in_group("postes_farol")
	m.global_position = (postes[0] as Node2D).global_position + Vector2(0, 14)
	postes[0].interactuar()
	await _esperar(1.2)
	_comprobar(Estado.tiene("jioni/descansa_kikombe") and _vecino("kikombe") != null, "con el primer farol, Kikombe descansa")
	m.global_position = _vecino("kikombe").global_position + Vector2(0, 14)
	_vecino("kikombe").interactuar()
	var tienda := await _tienda()
	_comprobar(tienda != null and tienda.abierto and Estado.tiene("kikombe_abierto"), "Kikombe abre su tienda")
	_comprobar(Estado.cuantos("farol_hora") == 1, "y regala el farol de su puesto (el duodécimo)")
	var lista: Array = tienda.call("_lista")
	_comprobar(lista.size() == 4, "vende cuatro cosas (%d)" % lista.size())
	Estado.extra["cristales_gastados"] = -100
	var aliento: float = Artes.ritmo_aliento()
	var alcance: float = RESONANCIA.alcance()
	for id in ["reloj_bolsillo", "lente_prisma", "botas_arena", "capa_farolillero"]:
		_comprobar(Tienda.comprar(id) == "ok", "se compra: %s" % id)
	_comprobar(is_equal_approx(Artes.ritmo_aliento(), aliento * 1.15), "el reloj: el Aliento se recupera un 15 % más rápido")
	_comprobar(is_equal_approx(RESONANCIA.alcance(), alcance * 1.25), "la lente: la Resonancia llega un 25 % más lejos")
	_comprobar(Estado.tiene("botas_arena"), "las botas, puestas")
	_comprobar(Tienda.lleva("capa_farolillero"), "la Capa del Farolillero se pone sola")
	tienda.cerrar()
	await _esperar(0.6)

	print("Los doce faroles y la Bendición del Crepúsculo:")
	for i in range(1, 11):
		Estado.marcar(postes[i].marca)
	var vida: int = m.vida_maxima()
	m.global_position = (postes[11] as Node2D).global_position + Vector2(0, 14)
	postes[11].interactuar()
	await _esperar(1.2)
	_comprobar(Estado.tiene("jioni/doce_faroles"), "doce faroles colgados en la plaza")
	await _hablar(m, _vecino("kibatari"))
	_comprobar(Estado.tiene("bendicion_crepusculo") and m.vida_maxima() == vida + 1, "Kibatari da la Bendición: una hoja más (%d → %d)" % [vida, m.vida_maxima()])

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
