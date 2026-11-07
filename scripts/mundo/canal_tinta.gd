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
##   - PWEZA, el jefe (enemigos/pweza.gd), en la GRAN DÁRSENA: despierta al pisar su anillo de muelle. Suelta la 3.ª
##     ficha (la de Chapa). La VERJA («ṽ») del paso al muelle norte solo se abre desde la Dársena (el atajo de vuelta).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const CHARCO := preload("res://scripts/mundo/sigilia/charco_tinta.gd")
const ESCRIBA := preload("res://scripts/mundo/sigilia/escriba.gd")
const COMPUERTA := preload("res://scripts/mundo/sigilia/compuerta.gd")
const TRAMPILLA := preload("res://scripts/mundo/sigilia/trampilla.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const LECTURA := preload("res://scripts/mundo/sigilia/lectura.gd")
const RUBA := preload("res://scripts/enemigos/ruba.gd")
const PWEZA := preload("res://scripts/enemigos/pweza.gd")
## la Gran Dársena: su centro (en casillas) y los semiejes de la orilla de tinta (px)
const DARSENA := Vector2(86, 26)
const ORILLA := Vector2(168, 151)
## donde nada Ruba (en casillas de tinta): dos en el cauce y dos en la Esclusa Hundida
const RUBAS := [Vector2i(34, 24), Vector2i(58, 27), Vector2i(46, 38), Vector2i(50, 45)]
const MFEREJI := Vector2i(42, 17)
## la Esclusa Hundida (en casillas): ahí la tinta baja hacia el sur
const HUNDIDA := Rect2i(41, 31, 15, 20)

var _pweza: Node2D = null
var _despertando := false


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
			elif c == "ṽ":
				var verja: StaticBody2D = TRAMPILLA.new()
				verja.marca = "canal/verja"
				verja.desde = Vector2.RIGHT
				verja.charla_cerrada = "canal_verja_fuera"
				verja.position = Vector2(x, y) * 16.0
				$Entidades.add_child(verja)
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
	if not Estado.tiene("pweza_vencido"):
		_pweza = PWEZA.new()
		_pweza.orilla = ORILLA
		_pweza.position = DARSENA * 16.0 + Vector2(8, 8)
		$Entidades.add_child(_pweza)
		_pweza.destruido.connect(_al_vencer_pweza)
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


## Al pisar el anillo de la Gran Dársena, despierta Pweza. Mientras pelean, la cámara se va hacia la mitad entre
## Maisha y el tintero, para que se vean los dos (si no, el tintero queda fuera de la pantalla).
func _process(delta: float) -> void:
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var hacia := Vector2.ZERO
	if _despertando and is_instance_valid(_pweza) and not Estado.tiene("pweza_vencido"):
		hacia = ((_pweza.global_position + Vector2(0, -30) - maisha.global_position) * 0.5).clamp(Vector2(-200, -110), Vector2(200, 110))
	Impacto.encuadre = Impacto.encuadre.lerp(hacia, clampf(delta * 3.0, 0.0, 1.0)).round()
	if _despertando or not is_instance_valid(_pweza) or Estado.tiene("pweza_vencido"):
		return
	var d := (maisha.global_position - (DARSENA * 16.0 + Vector2(8, 8))) / (ORILLA + Vector2(56, 50))
	if d.length() < 1.0:
		_despertando = true
		if not Estado.tiene("pweza_visto"):
			Estado.marcar("pweza_visto")
			await CHARLA_SCRIPT.hablar(self, "pweza_encuentro")
		if is_instance_valid(_pweza):
			_pweza.despertar()


func _exit_tree() -> void:
	Impacto.encuadre = Vector2.ZERO      # (que la cámara de la pelea no se quede corrida en otra escena)


func _al_vencer_pweza() -> void:
	await get_tree().create_timer(3.0).timeout
	if is_inside_tree():
		Sonido.musica("canal_tinta")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("canal_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "canal_llegada")
	Estado.marcar("canal_llegada")
