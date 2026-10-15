extends "res://scripts/mundo/escena_mundo.gd"
## LAS RUINAS DEL PRIMER ÁRBOL: la cima, al final del Sendero Olvidado. El final de Raíz.
##   - Una columnata rota lleva a la PLAZA: el PRIMER ÁRBOL en el centro («Ŧ», ruinas/primer_arbol.gd), MAUTI hecha
##     piedra a sus pies («ṁ») y las NUEVE PIEDRAS DEL RECUERDO en corro («ǒ», ruinas/piedra_recuerdo.gd).
##   - Al pisar la plaza por primera vez: lo que dice el árbol (con la ilustración 22_ruinas_mauti) y empieza la pelea
##     contra su MIEDO (ruinas/miedo.gd): la columnata se cierra hasta el final.
##   - Al romper el corazón de Giza: el árbol se cura, Mauti queda libre, cae la Semilla del Primer Árbol
##     (23_arbol_libre) y sale la pantalla del final del mundo. Después, Mauti se queda junto al árbol.
## Hace frío (la escarcha del Sendero, olvidado/escarcha.gd) y nieva.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const ARBOL := preload("res://scripts/mundo/ruinas/primer_arbol.gd")
const PIEDRA := preload("res://scripts/mundo/ruinas/piedra_recuerdo.gd")
const MIEDO := preload("res://scripts/mundo/ruinas/miedo.gd")
const ESCARCHA := preload("res://scripts/mundo/olvidado/escarcha.gd")
const NEVADA := preload("res://scripts/mundo/olvidado/nevada.gd")
const MAUTI := preload("res://arte/mundos/raiz/ruinas/mauti.png")
const FIN := preload("res://scripts/interfaz/fin_mundo.gd")
const RADIO_PLAZA := 15 * 16.0

var arbol: Node2D
var miedo: Node2D
var escarcha: Node2D
var _mauti: StaticBody2D
var _mauti_sprite: Sprite2D
var _cierre: StaticBody2D
var _centro := Vector2.ZERO
var _empezada := false


func _ready() -> void:
	super()
	var piedras: Array = []
	var filas: PackedStringArray = $Region._filas
	for y in filas.size():
		for x in filas[y].length():
			var c := filas[y][x]
			var pos := Vector2(x, y) * 16.0 + Vector2(8, 14)
			if c == "Ŧ":
				arbol = ARBOL.new()
				arbol.position = pos
				_centro = pos
				$Entidades.add_child(arbol)
			elif c == "ǒ":
				var p: StaticBody2D = PIEDRA.new()
				p.position = pos
				$Entidades.add_child(p)
				piedras.append(p)
			elif c == "ṁ":
				_poner_mauti(pos)
	miedo = MIEDO.new()
	miedo.centro = _centro
	miedo.radio_plaza = RADIO_PLAZA
	miedo.arbol = arbol
	miedo.piedras = piedras
	add_child(miedo)
	miedo.vencido.connect(_al_vencer)
	arbol.corazon_roto.connect(func() -> void: miedo.emit_signal("vencido"))
	escarcha = ESCARCHA.new()
	escarcha.name = "Escarcha"
	_maisha.add_child(escarcha)
	add_child(NEVADA.new())
	_maisha.caida.connect(_al_caer)
	if Estado.tiene("primer_arbol_libre"):
		arbol.call("curar")
		for p in piedras:
			p.call("despertar")
		_liberar_mauti(false)


func _poner_mauti(pos: Vector2) -> void:
	_mauti = StaticBody2D.new()
	_mauti.position = pos
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 8.0)
	_mauti.add_child(sombra)
	_mauti_sprite = Sprite2D.new()
	_mauti_sprite.texture = MAUTI
	_mauti_sprite.hframes = 2
	_mauti_sprite.centered = false
	_mauti_sprite.offset = Vector2(-12, -31)
	_mauti.add_child(_mauti_sprite)
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(12, 6)
	forma.shape = caja
	forma.position = Vector2(0, -3)
	_mauti.add_child(forma)
	$Entidades.add_child(_mauti)


func _process(_delta: float) -> void:
	if _empezada or Estado.tiene("primer_arbol_libre") or arbol == null:
		return
	# (empieza ya dentro de la plaza, no en la columnata)
	if _maisha.global_position.distance_to(_centro) < RADIO_PLAZA - 56.0 and _maisha.get("puede_actuar"):
		_empezada = true
		_empezar_pelea()


func _empezar_pelea() -> void:
	# la columnata se cierra (unas raíces de piedra la tapan) hasta que acabe
	_cierre = StaticBody2D.new()
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2(8 * 16, 12)
	forma.shape = caja
	_cierre.add_child(forma)
	_cierre.position = _centro + Vector2(0, RADIO_PLAZA + 18)
	add_child(_cierre)
	if not Estado.tiene("ruinas_llegada"):
		await CHARLA_SCRIPT.hablar(self, "ruinas_llegada")
		Estado.marcar("ruinas_llegada")
	if not is_inside_tree():
		return
	Sonido.musica("jefe_arbol", 1.0)
	miedo.call("empezar")


## Si cae en la pelea, vuelve a la entrada de la plaza (las piedras que ya despertó siguen despiertas)
func _al_caer() -> void:
	var punto := _centro + Vector2(0, RADIO_PLAZA - 20)
	_hud.fundido(func() -> void:
		_maisha.revivir(punto)
		escarcha.frio = 0.0)


func _al_vencer() -> void:
	miedo.call("terminar")
	Bestiario.jefe_vencido("miedo")
	Sonido.musica("", 1.5)
	await get_tree().create_timer(1.2).timeout
	if not is_inside_tree():
		return
	arbol.call("curar")
	Impacto.fogonazo(Color(1.0, 0.9, 0.6), 0.6, 0.8)
	Sonido.efecto("raiz_libre", 0.0, _centro)
	await get_tree().create_timer(1.5).timeout
	_liberar_mauti(true)
	await get_tree().create_timer(1.0).timeout
	await CHARLA_SCRIPT.hablar(self, "primer_arbol_final")
	if is_instance_valid(_cierre):
		_cierre.queue_free()
	Estado.guardar_pronto()
	_mostrar_fin()


func _liberar_mauti(con_efecto: bool) -> void:
	if _mauti_sprite == null:
		return
	_mauti_sprite.frame = 1
	if con_efecto:
		Sonido.efecto("piedra_rompe", 0.0, _mauti.global_position)
		Impacto.onda(_mauti.global_position + Vector2(0, -14))
	# libre: se puede hablar con Mauti
	var charla: Node2D = preload("res://scripts/mundo/objetos/cosa.gd").new()
	if charla:
		charla.set("charla", "mauti")
		charla.set("radio_interaccion", 26.0)
		charla.set("altura_bocadillo", 30.0)
		_mauti.add_child(charla)


func _mostrar_fin() -> void:
	if Estado.tiene("fin_raiz_final"):
		return
	Estado.marcar("fin_raiz_final")
	var fin: CanvasLayer = FIN.new()
	fin.ilustracion = load("res://arte/historia/23_arbol_libre.png")
	fin.titulo = "Raíz es libre"
	fin.subtitulo = "Fin del primer mundo"
	fin.pie = "Continuará en Sigilia..."
	fin.mapas = ["kitovu", "prados_del_eco", "bosque_cobrizo", "cienaga_quieta", "campo_segado", "sendero_del_puente",
		"las_pasarelas", "camino_cobrizo", "senda_surcos", "canada_eco", "lago_espejo", "orilla_juncos", "embarcadero_junco",
		"la_travesia", "gruta_raices", "paso_piedra", "cueva_setas", "sendero_olvidado"]
	add_child(fin)
	fin.abrir()
