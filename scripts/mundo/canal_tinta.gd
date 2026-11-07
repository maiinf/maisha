extends "res://scripts/mundo/escena_mundo.gd"
## EL CANAL DE TINTA (Sigilia, el segundo camino desde Maandiko, por el este).
##   - EL CAUCE MAYOR («~»): tinta líquida que corre hacia el este; no se pisa. Lo cruza la PASARELA de la esclusa («=»).
##   - LOS MUELLES («%»), con nieve; el norte se acaba antes de la Gran Dársena (más allá, en placa de hielo).
##   - MFEREJI, el esclusista (sigilia/escriba.gd con su dibujo), en blanco junto a la primera compuerta. Su FICHA
##     («ʣ») está en su casa del REMANSO NORTE, tras un tapón de Tinta Quieta («ẋ»). Con su nombre, enseña el
##     SIGILO DE HIELO y da la LLAVE DE COMPUERTA.
##   - LAS COMPUERTAS («ŧ») con su RUEDA DORADA («ŵ», sigilia/compuerta.gd) y las PLACAS DE HIELO (sigilia/placa_hielo.gd).
##   - LA ESCLUSA HUNDIDA: allí la tinta corre hacia el SUR (corriente_en), hasta el andén del fondo; de vuelta, la
##     escalerilla con su TRAMPILLA («ẗ», sigilia/trampilla.gd), que solo se abre desde abajo.
##   - LA ESTELA («ȩ»): se lee.
##   - RUBA, la sanguijuela de tinta (enemigos/ruba.gd), en el cauce y en la Esclusa Hundida; la 2.ª FICHA («ʤ», la de
##     Karatasi, una escriba de Maandiko) en el andén del fondo.
## Luego (parte 4): Pweza en la Gran Dársena.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const CHARCO := preload("res://scripts/mundo/sigilia/charco_tinta.gd")
const ESCRIBA := preload("res://scripts/mundo/sigilia/escriba.gd")
const COMPUERTA := preload("res://scripts/mundo/sigilia/compuerta.gd")
const TRAMPILLA := preload("res://scripts/mundo/sigilia/trampilla.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const RUBA := preload("res://scripts/enemigos/ruba.gd")
## donde nada Ruba (en casillas de tinta): dos en el cauce y dos en la Esclusa Hundida
const RUBAS := [Vector2i(34, 24), Vector2i(58, 27), Vector2i(46, 38), Vector2i(50, 45)]
const MFEREJI := Vector2i(42, 17)
## la Esclusa Hundida (en casillas): ahí la tinta baja hacia el sur
const HUNDIDA := Rect2i(41, 31, 15, 20)


func _ready() -> void:
	super()
	Estado.marcar("canal_tinta")
	_poner_cosas()
	if not Estado.tiene("canal_llegada"):
		_pensar_al_llegar.call_deferred()


## Hacia dónde corre la tinta en un punto (lo preguntan las placas de hielo)
func corriente_en(p: Vector2) -> Vector2:
	var c := Vector2i(floori(p.x / 16.0), floori(p.y / 16.0))
	return Vector2.DOWN if HUNDIDA.has_point(c) else Vector2.RIGHT


func _poner_cosas() -> void:
	var filas: PackedStringArray = $Region._filas
	for y in filas.size():
		for x in filas[y].length():
			var c := filas[y][x]
			var pos := Vector2(x, y) * 16.0 + Vector2(8, 14)
			if c == "ẋ":
				var ch: StaticBody2D = CHARCO.new()
				ch.marca = "charco/canal/%d,%d" % [x, y]
				ch.position = pos
				$Entidades.add_child(ch)
			elif c == "ʣ":
				var ficha: Node2D = RECOGIBLE.new()
				ficha.objeto = "ficha_mfereji"
				ficha.marca = "ficha/mfereji"
				ficha.dibujo = "res://arte/mundos/sigilia/paso/ficha.png"
				ficha.color_halo = Color(0.85, 0.7, 1.0)
				ficha.position = pos
				$Entidades.add_child(ficha)
			elif c == "ʤ":
				var ficha2: Node2D = RECOGIBLE.new()
				ficha2.objeto = "ficha_karatasi"
				ficha2.marca = "ficha/karatasi"
				ficha2.dibujo = "res://arte/mundos/sigilia/paso/ficha.png"
				ficha2.color_halo = Color(0.85, 0.7, 1.0)
				ficha2.position = pos
				$Entidades.add_child(ficha2)
			elif c == "ŵ":
				var compuerta: StaticBody2D = COMPUERTA.new()
				compuerta.columna = x
				compuerta.position = Vector2(x, y) * 16.0 + Vector2(8, 12)
				$Entidades.add_child(compuerta)
			elif c == "ẗ":
				var trampilla: StaticBody2D = TRAMPILLA.new()
				trampilla.marca = "canal/trampilla"
				trampilla.position = Vector2(x, y) * 16.0
				$Entidades.add_child(trampilla)
			elif c == "ȩ":
				var estela: Node2D = LECTURA.new()
				estela.charla = "canal_estela"
				estela.position = pos + Vector2(0, 6)
				$Entidades.add_child(estela)
	var mfereji: StaticBody2D = ESCRIBA.new()
	mfereji.nombre = "mfereji"
	mfereji.dibujo = "mfereji"
	mfereji.position = Vector2(MFEREJI) * 16.0 + Vector2(8, 14)
	$Entidades.add_child(mfereji)
	for r in RUBAS:
		var ruba: Node2D = RUBA.new()
		ruba.position = Vector2(r) * 16.0 + Vector2(8, 8)
		$Entidades.add_child(ruba)


func _al_poner_marca(marca: String) -> void:
	super(marca)
	if marca == "sigilo_hielo":
		var hud := get_tree().get_first_node_in_group("hud")
		if hud:
			hud.mostrar_mensaje("Sigilo de Hielo (R para cambiar)")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("canal_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "canal_llegada")
	Estado.marcar("canal_llegada")
