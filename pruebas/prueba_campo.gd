extends Node
## Prueba automática del Campo Segado: las grandes espinas del norte de la aldea (se abren al liberar a los dos
## minijefes), el campo, y la Cosechadora Oxidada: se atasca en los brotes, la caldera de atrás es su punto débil,
## la Ira sube por etapas (tuercas y chatarra, el borde de Giza, la embestida) y baja al golpear la caldera.
## Al final, el narrador y Bibi cierran Raíz.
## Se ejecuta sin abrir el editor:  godot --headless --path . res://pruebas/ejecutar.tscn -- prueba_campo

const R := preload("res://scripts/combate/reglas_combate.gd")
const SEMILLA := preload("res://scripts/combate/semilla.gd")
var _fallos := 0


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


func _escena() -> String:
	var e := get_tree().current_scene
	return e.name if e else ""


func _empujar(accion: String, segundos: float) -> void:
	Input.action_press(accion)
	await _esperar(segundos)
	Input.action_release(accion)


func _leer_dialogo() -> void:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	for i in 80:
		if not dialogo.hablando:
			return
		dialogo.pasar()
		await _esperar(0.08)


func _hablar_con(aldeano: Node) -> void:
	aldeano.interactuar()
	await _esperar(0.2)
	await _leer_dialogo()
	await _esperar(0.5)


func _semilla_en(pos: Vector2) -> Node2D:
	var s: Node2D = SEMILLA.new()
	s.casilla = R.casilla_de(pos)
	get_tree().get_first_node_in_group("maisha").get_parent().add_child(s)
	return s


func _purgar(zona: Node2D) -> void:
	var maisha := _maisha()
	maisha.global_position = zona.global_position + Vector2(-zona.radios_umbral.x - 20, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	maisha.global_position = zona.global_position + Vector2(-zona.radios_umbral.x * 0.8, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.queue_free()
	zona.set("_invocar", 999.0)
	var nucleo: Node2D = zona.get("_nucleo")
	var c := R.casilla_de(nucleo.global_position)
	for v in 3:
		maisha.aliento = maisha.aliento_maximo()
		maisha.vida = maisha.vida_maxima()
		maisha.global_position = R.centro_de(c + Vector2i(-2, 0))
		maisha.lanzar_semilla()
		maisha.global_position = R.centro_de(c + Vector2i(-3, 3))
		await _esperar(R.SEMILLA_MECHA + 0.2)
	await _esperar(3.2)


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "portal_raiz", "visto/prados_del_eco",
			"rescatado_pino", "rescatado_corteza", "bibi_conocida", "bibi_meditar", "bibi_aldea_viva", "visto/cuna_de_musgo",
			"camino_bosque", "camino_cienaga", "visto/bosque_cobrizo", "visto/cienaga_quieta", "bibi_pembe", "bibi_konokono"]:
		Estado.marcar(m)
	Estado.jugando = true

	print("Las grandes espinas del norte de la aldea:")
	Estado.llegada = "prados"
	get_tree().change_scene_to_file("res://escenas/mundo/cuna_de_musgo.tscn")
	await _esperar(1.5)
	var puertas := get_tree().get_nodes_in_group("puertas").filter(func(p: Node) -> bool: return p.destino == "senda_surcos")
	_comprobar(puertas.size() == 1, "hay un camino hacia el Campo Segado (la Senda de los Surcos)")
	var puerta: Area2D = puertas[0]
	var maisha := _maisha()
	var bibi: Node = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "bibi")[0]
	maisha.global_position = bibi.global_position + Vector2(0, 16)
	await _hablar_con(bibi)
	_comprobar(not Estado.tiene("camino_campo"), "con un solo minijefe libre (o ninguno), las espinas siguen ahí")
	Estado.marcar("zona/bosque_cobrizo/4")
	Estado.marcar("zona/cienaga_quieta/4")
	await _hablar_con(bibi)
	_comprobar(Estado.tiene("camino_campo"), "con Pembe y Konokono libres, Bibi nota que caen las grandes espinas")
	_comprobar(Misiones.activas().any(func(m: Dictionary) -> bool: return m["id"] == "campo"), "sale la misión del Campo Segado")
	await _esperar(1.8)
	maisha.global_position = puerta.global_position + Vector2(0, 30)
	await _esperar(0.3)
	await _empujar("mover_arriba", 0.9)
	await _esperar(2.0)
	_comprobar(_escena() == "SendaSurcos", "el camino sube por la Senda de los Surcos")
	await _esperar(2.5)
	await _leer_dialogo()
	var arriba: Area2D = get_tree().get_nodes_in_group("puertas").filter(func(p: Node) -> bool: return p.destino == "campo_segado")[0]
	_maisha().global_position = arriba.global_position + Vector2(0, 30)
	maisha = _maisha()
	await _esperar(0.3)
	await _empujar("mover_arriba", 0.9)
	await _esperar(2.0)
	_comprobar(_escena() == "CampoSegado", "y al final de la senda está el Campo Segado")
	await _esperar(2.5)
	await _leer_dialogo()
	_comprobar(Estado.tiene("campo_llegada"), "Maisha piensa algo al llegar")

	print("El campo:")
	var region: Node2D = get_tree().get_first_node_in_group("region")
	var zonas := get_tree().get_nodes_in_group("zonas")
	_comprobar(zonas.size() == 3, "3 zonas: dos corruptas y el gran campo de la Cosechadora (%d)" % zonas.size())
	_comprobar(region.secretos_total == 1, "1 secreto tras un matorral")
	_comprobar(get_tree().get_nodes_in_group("espantapajaros").size() >= 5, "espantapájaros en los campos")
	var zona1: Node2D = zonas.filter(func(z: Node) -> bool: return z.get_meta("clave") == "1")[0]
	_comprobar(zona1.tipos_enemigo.has("jabali") and zona1.tipos_enemigo.has("babosa"), "aquí salen jabalíes, babosas y Petrinos")
	await _purgar(zona1)
	_comprobar(zona1.estado == zona1.Estado.PURGADA, "la primera zona, purgada")

	print("La Cosechadora Oxidada:")
	var arena: Node2D = zonas.filter(func(z: Node) -> bool: return z.jefe == "cosechadora")[0]
	maisha = _maisha()
	maisha.vida = maisha.vida_maxima()
	maisha.global_position = arena.global_position + Vector2(0, arena.radios_umbral.y + 40)
	await get_tree().process_frame
	await get_tree().process_frame
	maisha.global_position = arena.global_position + Vector2(0, arena.radios_umbral.y * 0.6)
	await _esperar(0.4)
	var cos: Node2D = arena.get("_nucleo")
	_comprobar(arena.estado == arena.Estado.CERRADA and cos.fase != cos.Fase.DORMIDA, "al entrar en el campo, la Cosechadora arranca")
	await _esperar(2.2)
	_comprobar(cos.fase == cos.Fase.AVANZA, "recorre el campo fila a fila")
	_comprobar(cos.vida == 13 and cos.partes.size() == 4, "se rompe por partes: caldera, depósito, techo y corazón (13 en total)")
	_comprobar(cos._capas.size() == 10 and cos._capas["molinete"].hframes == 5, "dibujada por capas (ruedas, pistones y molinete animados)")
	var rueda0: int = cos._capas["rueda_g"].frame
	await _esperar(0.25)
	_comprobar(cos._capas["rueda_g"].frame != rueda0, "las ruedas giran al andar")
	_comprobar(not cos._golpe_morro(1, Vector2.RIGHT) and not cos._golpe_caldera(1, Vector2.RIGHT) and not cos._golpe_frontal(1, Vector2.RIGHT)
		and cos.vida == R.COSECHADORA_VIDA, "mientras anda, el cetro rebota en su chapa (caldera y depósito cerrados)")
	cos._danio_caldera(3, cos.global_position, "explosion")
	cos._danio_frontal(3, cos.global_position, "explosion")
	_comprobar(cos.vida == R.COSECHADORA_VIDA, "y las semillas no le hacen nada a la caldera ni al depósito")
	_comprobar(not cos._nodos["techo"].is_in_group("golpeables") and cos._nodos["techo"].is_in_group("daniables"),
		"el techo no se alcanza con el cetro, solo con explosiones")
	cos._danio_techo(3, cos.global_position, "explosion")
	_comprobar(cos.partes["techo"] == 2 and cos.vida == R.COSECHADORA_VIDA - 1, "una semilla en el techo le quita 1")
	cos.partes["techo"] = 3
	cos.vida = R.COSECHADORA_VIDA
	# una semilla en su camino: los brotes la atascan
	cos.global_position = arena.global_position + Vector2(-cos._mira * 140.0, 0)
	cos.ira = 0.0
	cos._desde_aceleron = 0.0
	cos._desde_tuercas = 0.0
	cos._gracia = 0.0
	cos._cambiar(cos.Fase.AVANZA)
	maisha.global_position = cos.global_position + Vector2(0, 80)
	_semilla_en(cos.global_position + Vector2(cos._mira * 130.0, -4))
	var atascada := false
	for i in 60:
		await _esperar(0.05)
		maisha.vida = maisha.vida_maxima()
		if cos.fase == cos.Fase.ATASCADA:
			atascada = true
			break
	_comprobar(atascada, "al meterse en los brotes de una semilla, se atasca")
	_comprobar(cos.caldera_abierta() and cos._capas["caldera"].frame == 1, "atascada, la caldera de atrás se abre (y se ve abierta)")
	_comprobar(not cos._golpe_frontal(1, Vector2.RIGHT), "pero el depósito frontal sigue cerrado")
	var techo_antes: int = cos.partes["techo"]
	cos._danio_techo(1, cos.global_position, "explosion")
	_comprobar(cos.partes["techo"] == techo_antes, "(%d) y parada, la tolva tapa el techo (solo se le alcanza en marcha)" % cos.partes["techo"])
	cos.ira = 30.0
	var ira_antes: int = cos.etapa()
	_comprobar(cos._golpe_caldera(1, Vector2.RIGHT) and cos.partes["caldera"] == 3, "el cetro le quita 1 a la caldera")
	_comprobar(cos.etapa() == ira_antes - 1, "y cada golpe en una parte baja la Ira una etapa")
	cos._danio_caldera(3, cos.global_position, "explosion")
	_comprobar(cos.partes["caldera"] == 1, "una semilla junto a la caldera abierta le quita 2")
	await _esperar(R.COSECHADORA_ATASCADA + 0.3)
	_comprobar(cos.fase != cos.Fase.ATASCADA, "al rato se suelta y sigue")
	# el acelerón infernal: avisa, sale disparada y deja un rastro de fuego
	cos.ira = 0.0
	cos.global_position = Vector2(arena.global_position.x - cos._mira * arena.radios_umbral.x * 0.45, arena.global_position.y)
	cos._cambiar(cos.Fase.AVANZA)
	cos._desde_aceleron = 99.0
	maisha.global_position = cos.global_position + Vector2(0, 90)
	var acelera := false
	for i in 60:
		await _esperar(0.05)
		maisha.vida = maisha.vida_maxima()
		if cos.fase == cos.Fase.EMBISTE:
			acelera = true
			break
	_comprobar(acelera, "el acelerón infernal: avisa con una franja y sale disparada")
	await _esperar(0.5)
	var fuego: Node2D = get_tree().get_first_node_in_group("fuego_giza")
	_comprobar(fuego != null and fuego.cuantas() >= 3, "deja un rastro de fuego de Giza (%d casillas)" % (fuego.cuantas() if fuego else 0))
	var filas_calma := {}
	for c in fuego._llamas:
		filas_calma[c.y] = true
	_comprobar(filas_calma.size() == 1, "en Calma, el rastro es de una fila")
	# el fuego quema
	await _esperar(0.3)
	var una: Vector2i = fuego._llamas.keys()[0]
	maisha.vida = maisha.vida_maxima()
	maisha.global_position = R.centro_de(una)
	await _esperar(0.7)
	_comprobar(maisha.vida < maisha.vida_maxima(), "pisar el fuego quema")
	maisha.global_position = arena.global_position + Vector2(0, arena.radios_umbral.y * 0.7)
	for i in 80:
		await _esperar(0.05)
		maisha.vida = maisha.vida_maxima()
		if cos.fase in [cos.Fase.AVANZA, cos.Fase.GIRA]:
			break
	# en Furia, el rastro es de tres filas
	fuego._llamas.clear()
	cos.ira = 55.0
	cos.global_position = Vector2(arena.global_position.x - cos._mira * arena.radios_umbral.x * 0.45, arena.global_position.y)
	cos._cambiar(cos.Fase.AVANZA)
	cos._desde_aceleron = 99.0
	for i in 60:
		await _esperar(0.05)
		maisha.vida = maisha.vida_maxima()
		if cos.fase == cos.Fase.EMBISTE:
			break
	await _esperar(0.5)
	var filas := {}
	for c in fuego._llamas:
		filas[c.y] = true
	_comprobar(filas.size() >= 3, "en Furia, el rastro quema tres filas (%d)" % filas.size())
	# acelerar contra unos brotes: se estampa y se queda atascada más rato
	cos._cambiar(cos.Fase.EMBISTE)
	var registro := get_tree().get_first_node_in_group("registro_brotes")
	registro.plantar(R.casilla_de(cos.global_position + Vector2(cos._mira * 40.0, -2)))
	await get_tree().process_frame
	await get_tree().process_frame
	_comprobar(cos.fase == cos.Fase.ATASCADA and cos._t < 0.0, "si acelera contra unos brotes, se estampa (atascada más rato)")
	_comprobar(cos.frontal_al_aire() and cos._golpe_frontal(1, Vector2.RIGHT) and cos.partes["frontal"] == 2,
		"estampada, el depósito frontal queda al aire: el cetro le quita 1")
	cos._golpe_frontal(1, Vector2.RIGHT)
	_comprobar(cos.partes["frontal"] == 1 and not cos.frontal_al_aire() and cos._t >= R.COSECHADORA_ATASCADA - 0.5,
		"al segundo golpe en el depósito, se suelta de un tirón")
	cos.partes["frontal"] = 2
	await _esperar(R.COSECHADORA_ATASCADA + R.COSECHADORA_ESTAMPADA + 0.4)
	cos.ira = 0.0
	# la Ira sube sola
	var ira0: float = cos.ira
	await _esperar(1.0)
	_comprobar(cos.ira > ira0, "la Ira sube poco a poco (%.1f → %.1f)" % [ira0, cos.ira])
	# Enfado: tuercas y chatarra
	cos.ira = 30.0
	cos._cambiar(cos.Fase.LANZA)
	maisha.global_position = cos.global_position + Vector2(0, 90)
	await _esperar(2.0)
	maisha.vida = maisha.vida_maxima()
	var chatarra := get_tree().get_nodes_in_group("chatarra")
	_comprobar(chatarra.size() >= 1, "en Enfado lanza tuercas que dejan bloques de chatarra (%d)" % chatarra.size())
	if not chatarra.is_empty():
		var bloque: Node2D = chatarra[0]
		_comprobar(not bloque.recibir_golpe(1, Vector2.RIGHT), "el cetro rebota en la chatarra")
		bloque.recibir_danio(3, bloque.global_position, "explosion")
		_comprobar(not bloque.is_in_group("chatarra"), "una semilla la deshace")
	# Furia: Giza cierra la arena desde el borde
	cos.ira = 55.0
	await _esperar(2.0)
	maisha.vida = maisha.vida_maxima()
	_comprobar(cos.borde < 0.99, "en Furia, Giza cierra la arena desde el borde (%.2f)" % cos.borde)
	# Frenesí: embiste por la fila de Maisha
	cos.ira = 80.0
	cos.global_position = arena.global_position + Vector2(-cos._mira * 60.0, 0)
	cos._gracia = 3.0
	cos._cambiar(cos.Fase.AVANZA)
	maisha.global_position = Vector2(cos.global_position.x + cos._mira * 90.0, cos.global_position.y)
	var embiste := false
	for i in 40:
		await _esperar(0.05)
		maisha.vida = maisha.vida_maxima()
		if cos.fase in [cos.Fase.PREPARA, cos.Fase.EMBISTE]:
			embiste = true
			break
	_comprobar(embiste, "en Frenesí, si Maisha se pone en su fila, se prepara para embestir")
	maisha.global_position = cos.global_position + Vector2(0, 90)
	# estrellarse contra el borde tras un acelerón deja el depósito al aire
	cos.ira = 0.0
	cos._cambiar(cos.Fase.CHOQUE)
	_comprobar(cos.frontal_al_aire(), "al estrellarse contra el borde, se queda aturdida con el depósito al aire")
	# romper la caldera: revienta y pierde la rueda grande
	cos._cambiar(cos.Fase.ATASCADA)
	cos._golpe_caldera(1, Vector2.RIGHT)
	await get_tree().process_frame
	_comprobar(cos.partes["caldera"] == 0 and not cos._capas["rueda_g"].visible and cos._rueda_suelta != null,
		"la caldera revienta: la rueda grande sale volando")
	_comprobar(cos.etapa() >= 1, "con una parte rota, no baja de Enfado")
	_comprobar(not cos._nodos["caldera"].is_in_group("golpeables"), "la caldera rota ya no recibe golpes")
	cos._cambiar(cos.Fase.AVANZA)
	cos.global_position = arena.global_position
	var y0: float = cos.global_position.y
	var ymax := 0.0
	for i in 20:
		await _esperar(0.05)
		maisha.vida = maisha.vida_maxima()
		if cos.fase == cos.Fase.AVANZA:
			ymax = maxf(ymax, absf(cos.global_position.y - y0))
	_comprobar(ymax > 0.5 and cos._velocidad() > R.COSECHADORA_VELOCIDAD[cos.etapa()], "sin rueda va dando bandazos (y un poco más rápida)")
	# romper el depósito frontal: fuga de fuego
	while cos.partes["frontal"] > 0:
		cos._cambiar(cos.Fase.CHOQUE)
		cos._golpe_frontal(1, Vector2.RIGHT)
	_comprobar(cos.etapa() >= 2, "con dos partes rotas, no baja de Furia")
	fuego._llamas.clear()
	cos.global_position = arena.global_position + Vector2(-60, 0)
	cos._cambiar(cos.Fase.AVANZA)
	maisha.global_position = cos.global_position + Vector2(0, 90)
	await _esperar(0.8)
	maisha.vida = maisha.vida_maxima()
	_comprobar(fuego.cuantas() >= 2, "el depósito roto pierde fuego: deja llamas por donde pasa (%d)" % fuego.cuantas())
	# romper el techo: tuercas de fuego
	cos._cambiar(cos.Fase.AVANZA)
	while cos.partes["techo"] > 0:
		cos._espera_techo = 0.0
		cos._danio_techo(1, cos.global_position, "explosion")
	cos._lanzar_tuercas(maisha)
	var tuercas := get_tree().get_nodes_in_group("tuercas")
	_comprobar(not tuercas.is_empty() and tuercas.all(func(t: Node) -> bool: return t.de_fuego), "con el techo roto, las tuercas caen en llamas")
	await get_tree().process_frame
	await get_tree().process_frame
	_comprobar(cos.fase == cos.Fase.CORAZON and cos._capas["corazon"].visible and cos._capas["chasis"].frame == 2,
		"con las tres partes rotas, se desploma y deja el corazón de Giza al aire")
	_comprobar(cos._nodos["corazon"].is_in_group("golpeables") and not cos.corazon_abierto(), "el corazón empieza cerrado")
	_comprobar(not cos._golpe_corazon(1, Vector2.RIGHT), "cerrado, el cetro rebota")
	# los anillos de fuego
	maisha.global_position = cos.global_position + Vector2(0, 70)
	maisha.vida = maisha.vida_maxima()
	var dano_anillo := false
	for i in 160:
		await _esperar(0.05)
		if maisha.vida < maisha.vida_maxima():
			dano_anillo = true
			break
	_comprobar(not cos._anillos.is_empty() and dano_anillo, "lanza anillos de fuego que queman (si no pasas por un hueco)")
	var an: Dictionary = {"hueco": 0.0}
	_comprobar(cos._en_hueco(an, 0.1) and cos._en_hueco(an, PI) and not cos._en_hueco(an, PI / 2.0), "cada anillo tiene dos huecos")
	# con el Latido no quema
	maisha.vida = maisha.vida_maxima()
	maisha.set("_invulnerable", 5.0)
	cos._anillos.append({"r": 60.0, "hueco": PI / 2.0, "giro": 0.0, "hecho": false})
	await _esperar(0.3)
	_comprobar(maisha.vida == maisha.vida_maxima(), "con el Latido (invulnerable) el anillo no quema")
	maisha.set("_invulnerable", 0.0)
	# el corazón se abre después de cada anillo
	var abierto := false
	for i in 80:
		await _esperar(0.05)
		maisha.vida = maisha.vida_maxima()
		if cos.corazon_abierto():
			abierto = true
			break
	_comprobar(abierto, "justo después de cada anillo, el corazón se abre")
	_comprobar(cos._golpe_corazon(1, Vector2.RIGHT) and cos.partes["corazon"] == 2, "abierto, el cetro le quita 1")
	_comprobar(not cos.corazon_abierto(), "y del golpe se cierra hasta el siguiente anillo")
	maisha.global_position = cos.global_position + Vector2(0, 140)
	while cos.partes["corazon"] > 0:
		cos._desde_anillo = 1.0
		cos._corazon_golpeado = false
		cos._golpe_corazon(1, Vector2.RIGHT)
		await get_tree().process_frame
	_comprobar(cos.fase == cos.Fase.VENCIDA, "al romper el corazón, la Cosechadora cae")
	for i in 30:
		maisha.vida = maisha.vida_maxima()
		await _esperar(0.5)
		if arena.estado == arena.Estado.PURGADA:
			break
	_comprobar(arena.estado == arena.Estado.PURGADA and Estado.tiene("zona/campo_segado/3"), "la Cosechadora se apaga y el campo queda purgado")
	for i in 16:
		await _esperar(0.5)
		await _leer_dialogo()
		if Estado.tiene("raiz_libre"):
			break
	_comprobar(Estado.tiene("narr/cosechadora") and Estado.tiene("raiz_libre"), "el narrador lo cuenta: Raíz es libre")
	_comprobar(Misiones.hechas().any(func(m: Dictionary) -> bool: return m["id"] == "campo"), "misión del Campo Segado cumplida")

	print("Bibi cierra Raíz:")
	Estado.llegada = "campo"
	get_tree().change_scene_to_file("res://escenas/mundo/cuna_de_musgo.tscn")
	await _esperar(1.5)
	bibi = get_tree().get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.id == "bibi")[0]
	_maisha().global_position = bibi.global_position + Vector2(0, 16)
	await _hablar_con(bibi)
	_comprobar(Estado.tiene("bibi_raiz_libre"), "Bibi lo nota en las raíces: Raíz entera respira")

	print("RESULTADO: ", "todo correcto" if _fallos == 0 else "%d fallos" % _fallos)
	get_tree().quit(_fallos)
