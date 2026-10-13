extends Node
## Prueba automática de los hechiceros de Giza (Bundi, el búho-mago, y Buibui, la araña-bruja, con sus bichos) y del
## Bestiario (las cuentas, los rangos, sus cristales y su bolsillo en el diario).
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_hechiceros

const R := preload("res://scripts/combate/reglas_combate.gd")
const BUNDI := preload("res://scripts/enemigos/bundi.gd")
const BUIBUI := preload("res://scripts/enemigos/buibui.gd")
var _fallos := 0
var _rangos := []


func _comprobar(condicion: bool, mensaje: String) -> void:
	if condicion:
		print("  bien: ", mensaje)
	else:
		_fallos += 1
		print("  FALLO: ", mensaje)


func _esperar(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 80:
		if not dialogo.hablando:
			return
		dialogo.pasar()
		await _esperar(0.08)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco",
			"visto/cuna_de_musgo", "bibi_conocida", "bibi_aldea_viva", "camino_bosque", "camino_cienaga",
			"visto/bosque_cobrizo", "bosque_llegada", "cobrizo_llegada", "escudo_corteza"]:
		Estado.marcar(m)
	Estado.jugando = true
	Bestiario.rango_nuevo.connect(func(tipo: String, r: int) -> void: _rangos.append([tipo, r]))

	print("El Bestiario:")
	_comprobar(Bestiario.rango("petrino") == 0 and not Bestiario.conocido("petrino"), "al empezar no conoces a ningún enemigo")
	var cristales := Tienda.cristales()
	for i in 9:
		Bestiario.vencido("petrino")
	_comprobar(Bestiario.rango("petrino") == 0 and Bestiario.cuantos("petrino") == 9, "con 9 petrinos aún no hay rango")
	Bestiario.vencido("petrino")
	_comprobar(Bestiario.rango("petrino") == 1 and _rangos.back() == ["petrino", 1], "con 10, rango de bronce (y un aviso)")
	for i in 20:
		Bestiario.vencido("petrino")
	_comprobar(Bestiario.rango("petrino") == 2 and Estado.tiene("rango/plata/petrino"), "con 30, rango de plata")
	_comprobar(Tienda.cristales() == cristales + 2, "el rango de plata da 2 cristales (%d → %d)" % [cristales, Tienda.cristales()])
	var sin_contar := Node.new()
	sin_contar.set_meta("sin_contar", true)
	Bestiario.vencido("petrino", sin_contar)
	sin_contar.free()
	_comprobar(Bestiario.cuantos("petrino") == 30, "lo que se desmorona con la purga no cuenta")
	Bestiario.empezar_jefe("pembe")
	Bestiario.jefe_vencido("pembe")
	_comprobar(Bestiario.rango("pembe") == 3, "un jefe vencido sin que te den: rango de oro")
	Bestiario.empezar_jefe("kambare")
	for i in 4:
		Bestiario.al_herir(5)
	Bestiario.jefe_vencido("kambare")
	_comprobar(Bestiario.rango("kambare") == 1, "y con 4 golpes encajados, solo bronce")
	Estado.marcar("zona/kitovu/7")
	_comprobar(Bestiario.rango("mzizi") == 1, "los jefes vencidos antes del Bestiario cuentan como bronce")

	print("Bundi, el búho-mago:")
	Estado.llegada = ""
	get_tree().change_scene_to_file("res://escenas/mundo/bosque_cobrizo.tscn")
	await _esperar(1.5)
	await _leer_dialogo()
	var region: Node2D = get_tree().get_first_node_in_group("region")
	var zonas := get_tree().get_nodes_in_group("zonas")
	_comprobar(zonas.any(func(z: Node) -> bool: return z.tipos_enemigo.has("bundi")), "en el Bosque Cobrizo, las zonas invocan búhos-mago")
	for z in zonas:
		z.set("activa", false)
	var maisha := _maisha()
	var sitio := Vector2(40 * 16, 30 * 16)
	maisha.global_position = sitio
	maisha.vida = maisha.vida_maxima()
	Input.action_press("mover_derecha")
	await _esperar(0.1)
	Input.action_release("mover_derecha")
	maisha.global_position = sitio
	var bundi: Node2D = BUNDI.new()
	bundi.position = sitio + Vector2(80, -8)
	region.get_node(region.entidades).add_child(bundi)
	var orbe: Node2D = null
	for i in 120:
		orbe = get_tree().get_first_node_in_group("ondas") as Node2D
		if orbe:
			break
		await _esperar(0.05)
	_comprobar(orbe != null, "conjura y lanza una bola de Giza")
	# con el escudo, de frente, se la devuelve
	Input.action_press("golpe")
	var vida_maisha: int = maisha.vida
	for i in 160:
		if not is_instance_valid(orbe) or orbe.devuelta:
			break
		maisha.global_position = sitio
		await _esperar(0.05)
	_comprobar(is_instance_valid(orbe) and orbe.devuelta, "el escudo la devuelve")
	for i in 100:
		if bundi.vida < R.BUNDI_VIDA:
			break
		await _esperar(0.05)
	Input.action_release("golpe")
	_comprobar(bundi.vida == R.BUNDI_VIDA - R.ORBE_DANIO_DEVUELTA and bundi.estado == bundi.ATONTADO, "su propia bola le da y se queda atontado (vida %d)" % bundi.vida)
	_comprobar(maisha.vida == vida_maisha, "a Maisha no le ha hecho nada")
	await _esperar(R.BUNDI_ATONTADO + R.BUNDI_ESFUMA * 2 + 0.3)
	maisha.global_position = bundi.global_position + Vector2(-20, 0)
	var antes: Vector2 = bundi.global_position
	await _esperar(0.15)
	_comprobar(bundi.estado == bundi.ESFUMA, "si Maisha se le acerca, se esfuma")
	await _esperar(R.BUNDI_ESFUMA + 0.2)
	_comprobar(bundi.global_position.distance_to(antes) > 20.0, "y aparece en otro sitio")
	for i in 40:
		if bundi.estado != bundi.ESFUMA and bundi.estado != bundi.VUELVE:
			break
		await _esperar(0.05)
	bundi.recibir_danio(5, bundi.global_position, "explosion")
	await _esperar(0.1)
	_comprobar(Bestiario.cuantos("bundi") == 1 and Bestiario.conocido("bundi"), "al vencerlo, entra en el Bestiario")

	print("Buibui, la araña-bruja:")
	for o in get_tree().get_nodes_in_group("ondas"):
		o.disipar()
	sitio = zonas[0].global_position + Vector2(-45, 0)          # (en el claro de una zona: sin árboles en medio)
	maisha.global_position = sitio
	maisha.vida = maisha.vida_maxima()
	var buibui: Node2D = BUIBUI.new()
	buibui.position = sitio + Vector2(90, 0)
	region.get_node(region.entidades).add_child(buibui)
	await _esperar(R.BUIBUI_CADA * 0.4 + R.BUIBUI_AVISO + 0.6)
	var bichos := get_tree().get_nodes_in_group("enemigos").filter(func(e: Node) -> bool: return e.get_script() == preload("res://scripts/enemigos/mende.gd"))
	_comprobar(bichos.size() == R.BUIBUI_BICHOS, "invoca %d bichos de óxido (%d)" % [R.BUIBUI_BICHOS, bichos.size()])
	var mas_cerca := 9999.0
	for i in 25:
		for b in bichos:
			if is_instance_valid(b):
				mas_cerca = minf(mas_cerca, b.global_position.distance_to(maisha.global_position))
		await _esperar(0.04)
	_comprobar(mas_cerca < 30.0, "los bichos corren hacia Maisha (llegan a %.0f px)" % mas_cerca)
	for b in bichos:
		if is_instance_valid(b):
			b.recibir_golpe(1, Vector2.RIGHT)
	await _esperar(0.3)
	_comprobar(Bestiario.cuantos("mende") == 2, "mueren de un golpe (y cuentan en el Bestiario)")
	buibui.recibir_danio(2, buibui.global_position, "explosion")
	_comprobar(buibui.sellado and buibui.vida == R.BUIBUI_VIDA - 2, "una semilla le sella el nido")
	maisha.global_position = sitio
	await _esperar(R.BUIBUI_CADA + R.BUIBUI_AVISO + 0.3)
	bichos = get_tree().get_nodes_in_group("enemigos").filter(func(e: Node) -> bool: return e.get_script() == preload("res://scripts/enemigos/mende.gd"))
	_comprobar(bichos.is_empty(), "con el nido sellado ya no invoca")
	buibui.recibir_golpe(1, Vector2.RIGHT)
	buibui.recibir_golpe(1, Vector2.RIGHT)
	await _esperar(0.5)
	_comprobar(not is_instance_valid(buibui) or buibui.vida <= 0, "con dos golpes más cae")
	_comprobar(Bestiario.cuantos("buibui") == 1, "y entra en el Bestiario")

	print("El bolsillo del Bestiario:")
	var mochila := get_tree().get_first_node_in_group("mochila")
	mochila.abrir(5)
	await _esperar(0.6)
	var filas: Array = mochila._lista()
	_comprobar(filas.size() == Bestiario.FICHAS.size(), "salen todos los enemigos (%d)" % filas.size())
	var petrino: Dictionary = filas.filter(func(f: Dictionary) -> bool: return f["bestia"] == "petrino")[0]
	_comprobar(petrino["rango"] == 2 and petrino["cantidad"] == 30, "el petrino, con su rango de plata y 30 vencidos")
	var rana: Dictionary = filas.filter(func(f: Dictionary) -> bool: return f["bestia"] == "rana")[0]
	_comprobar(rana["nombre"] == "???" and rana["apagada"], "los que no has vencido salen como «???»")
	mochila.cerrar()
	await _esperar(0.4)

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
