extends Node2D
## RASGOS DE MAISHA: lo que se dibuja con código (y se mueve) al despertar Artes en el Árbol de la Vida.
## La ropa (raíces, hombreras, capa, corona, bufanda, cetro) va en ropa_maisha.gd; esto es lo vivo:
##   brote        (Raíz 3)     un brote de dos hojas grandes con capullo, que se mece
##   flores       (Raíz 6)     florecillas por el cuerpo
##   aura         (Aliento 3)  una luz suave que respira
##   anillos      (Aliento 3)  un anillo de viento que gira en la cintura (la mitad de atrás pasa por detrás)
##   remolino     (Aliento 4)  un remolino de aire bajo los pies
##   alitas       (Aliento 5)  alitas de brisa que aletean
##   alas         (Aliento 6)  alas grandes de brisa
##   brisa        (Aliento 6)  el cuerpo se vuelve un poco transparente y deja una estela al moverse
## Todo es sutil a propósito y sin brillitos sueltos: con todo despierto, Maisha no debe verse cargada.
## El brote se coloca solo encima de la cabeza en cualquier animación: busca el píxel más alto del dibujo.
## Qué rasgos se ven lo decide Artes.aspecto(). Con «niveles» se pueden enseñar otros (la vista previa del diario).

const PALETA := {
	"k": Color("152814"), "d": Color("2e5a22"), "m": Color("4f8a32"), "h": Color("7fc04a"), "l": Color("b8e08a"),
	"G": Color("3e9a35"), "r": Color("e86a8a"), "F": Color("f9d36a"), "f": Color("ffd7e0"),
}
const BRISA := {"o": Color(0.62, 0.85, 0.91, 0.5), "O": Color(0.88, 0.96, 0.98, 0.6), "V": Color(1, 1, 1, 0.7), "q": Color(0.35, 0.69, 0.78, 0.35)}
const PETALO := Color("ffd7e0")
const CENTRO_FLOR := Color("f9d36a")
## La hoja izquierda del brote (la derecha es su espejo); el tallo queda abajo a la derecha
const HOJA_BROTE := [
	"..kk...",
	".khlk..",
	"khmmhk.",
	"kdmmmhk",
	".kddmmk",
	"..kkkGk",
]
const CAPULLO := [".r.", "rFr", ".G."]
## Las alas (la izquierda; la derecha es su espejo): dos fotogramas, arriba y abajo
const ALITA := [
	["....oO", "..oOVO", "oOVOo.", "OOoq..", "oq...."],
	["......", "...oOO", ".oOVVO", "oOVOo.", "Oqq..."],
]
const ALA := [
	["........ooO", "......ooOVO", "....ooOVVOo", "..oOVVOOoq.", ".oOVOOoq...", "oOVOoq.....", "OOoq.......", "oq........."],
	["...........", ".........oO", "......ooOVO", "...ooOVVVOo", ".oOVVOOooq.", "oOVOOoqq...", "OVOoq......", "Ooq........"],
]
const VIENTO := Color(0.85, 0.96, 1.0)

var _sprite: AnimatedSprite2D
var _aura: Node2D               # lo que va por DETRÁS de Maisha (aura, mitad de atrás de los anillos, alas)
var _cimas := {}                 # "animación:fotograma:volteado" -> punto más alto (local del sprite)
var _tiempo := 0.0
var _rasgos: Array = []
var _estela: Array[Dictionary] = []
var _ultima := Vector2.ZERO
var niveles: Dictionary = {}     # vacío = los niveles de verdad de Maisha


func _ready() -> void:
	_sprite = get_parent().get_node("Sprite")
	z_index = 1
	# lo de detrás va en un nodo aparte, por debajo de Maisha y con mezcla de luz
	_aura = Node2D.new()
	_aura.z_index = -1
	_aura.show_behind_parent = true
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_aura.material = suma
	_aura.draw.connect(_dibujar_detras)
	get_parent().add_child.call_deferred(_aura)
	Artes.arte_subida.connect(func(_id: String, _n: int) -> void: _actualizar())
	Estado.partida_cambiada.connect(_actualizar)
	_actualizar()


func _actualizar() -> void:
	_rasgos = Artes.aspecto(niveles)["rasgos"]
	if _sprite:
		_sprite.self_modulate.a = 0.78 if "brisa" in _rasgos else 1.0


func _process(delta: float) -> void:
	_tiempo += delta
	if _rasgos.is_empty():
		if _estela.size() > 0:
			_estela.clear()
		return
	if "brisa" in _rasgos:
		var pos := (get_parent() as Node2D).global_position
		if pos.distance_to(_ultima) > 3.0:
			_estela.append({"p": pos + Vector2(randf_range(-4, 4), randf_range(-20, -6)), "t": 0.0})
			_ultima = pos
		for e in _estela:
			e["t"] += delta
		_estela = _estela.filter(func(e: Dictionary) -> bool: return e["t"] < 0.7)
	queue_redraw()
	if is_instance_valid(_aura):
		_aura.queue_redraw()


## El píxel más alto del dibujo actual (en coordenadas de Maisha)
func _cima() -> Vector2:
	var clave := "%s:%d:%s" % [_sprite.animation, _sprite.frame, _sprite.flip_h]
	if not _cimas.has(clave):
		var tex := _sprite.sprite_frames.get_frame_texture(_sprite.animation, _sprite.frame)
		var punto := Vector2(0, -32)
		if tex:
			var img := tex.get_image()
			if img:
				if img.is_compressed():
					img.decompress()
				var hallado := false
				for y in img.get_height():
					var xs := []
					for x in img.get_width():
						if img.get_pixel(x, y).a > 0.5:
							xs.append(x)
					if not xs.is_empty():
						var cx: float = (xs[0] + xs[-1]) / 2.0
						if _sprite.flip_h:
							cx = img.get_width() - 1 - cx
						punto = Vector2(cx - img.get_width() / 2.0, y - img.get_height() / 2.0)
						hallado = true
						break
				if not hallado:
					punto = Vector2(0, -img.get_height() / 2.0)
		_cimas[clave] = punto
	return _sprite.position + _cimas[clave]


func _pixel(p: Vector2, color: Color, lienzo: CanvasItem = self) -> void:
	lienzo.draw_rect(Rect2(p.floor(), Vector2.ONE), color)


## Dibuja una cuadrícula de letras (como las de herramientas/dibujar_prendas.py) con su paleta
func _cuadricula(origen: Vector2, filas: Array, paleta: Dictionary, espejo := false, alfa := 1.0, lienzo: CanvasItem = self) -> void:
	for y in filas.size():
		var fila: String = filas[y]
		for x in fila.length():
			var letra := fila[x]
			if paleta.has(letra):
				var c: Color = paleta[letra]
				var px := fila.length() - 1 - x if espejo else x
				_pixel(origen + Vector2(px, y), Color(c, c.a * alfa), lienzo)


func _mirando() -> String:
	return String(_sprite.animation).get_slice("_", String(_sprite.animation).get_slice_count("_") - 1)


func _draw() -> void:
	if _rasgos.is_empty() or _sprite == null:
		return
	for e in _estela:
		var vida: float = 1.0 - e["t"] / 0.7
		draw_circle(to_local(e["p"]) + Vector2(0, -e["t"] * 8.0), 1.0 + vida, Color(0.85, 0.95, 1.0, 0.25 * vida))
	if "anillos" in _rasgos:
		_dibujar_anillos(true, self)
	if "remolino" in _rasgos:
		_dibujar_remolino(true, self)
	if _mirando() == "arriba":
		# de espaldas, las alas quedan por delante
		if "alitas" in _rasgos:
			_dibujar_alas(ALITA, self)
		if "alas" in _rasgos:
			_dibujar_alas(ALA, self)
	if "brote" in _rasgos:
		_dibujar_brote()
	if "flores" in _rasgos:
		_dibujar_flores()


## Un brote de dos hojas grandes que sale de la cabeza y se mece, con un capullo
func _dibujar_brote() -> void:
	var cima := _cima()
	var meneo := roundf(sin(_tiempo * 2.0))
	var tallo := cima + Vector2(0, 1)
	var ancho := (HOJA_BROTE[0] as String).length()
	# las hojas nacen del brote de siempre y suben y bajan a destiempo, como si respiraran
	_cuadricula(tallo + Vector2(-ancho, -5 + meneo), HOJA_BROTE, PALETA)
	_cuadricula(tallo + Vector2(1, -5 - meneo), HOJA_BROTE, PALETA, true)
	_pixel(tallo + Vector2(0, -1), PALETA["G"])
	_pixel(tallo + Vector2(0, -2), PALETA["G"])
	_cuadricula(tallo + Vector2(-1, -5), CAPULLO, PALETA)


## Florecillas por el cuerpo (siguen el lado hacia el que mira)
func _dibujar_flores() -> void:
	var lado := -1.0 if _sprite.flip_h else 1.0
	var centro := _sprite.position
	var puntos := [Vector2(-6, 2), Vector2(5, 6), Vector2(-3, 11)]
	if _mirando() == "arriba":
		puntos = [Vector2(-6, 1), Vector2(6, 4)]
	for p in puntos:
		var q: Vector2 = centro + Vector2(p.x * lado, p.y)
		_pixel(q + Vector2(-1, 0), PETALO)
		_pixel(q + Vector2(1, 0), PETALO)
		_pixel(q + Vector2(0, -1), PETALO)
		_pixel(q + Vector2(0, 1), PETALO)
		_pixel(q, CENTRO_FLOR)


## Un anillo de viento que gira en la cintura. La mitad de delante va en este nodo; la de atrás, en el de detrás.
func _dibujar_anillos(delante: bool, lienzo: CanvasItem) -> void:
	for anillo in [[Vector2(0, -9), 12.0, 3.0, 2.2, 0.5]]:
		var centro: Vector2 = anillo[0]
		var n := 28
		for k in n:
			if k % 7 >= 5:
				continue                     # huecos: así se ve que corre
			var a: float = _tiempo * anillo[3] + k * TAU / n
			if (sin(a) > 0.0) != delante:
				continue
			var p := centro + Vector2(cos(a) * anillo[1], sin(a) * anillo[2])
			var cola := float(k % 7) / 5.0
			_pixel(p, Color(VIENTO, anillo[4] * (1.0 - cola * 0.5) * (1.0 if delante else 0.6)), lienzo)


## Un remolino de aire bajo los pies
func _dibujar_remolino(delante: bool, lienzo: CanvasItem) -> void:
	for k in 10:
		var a := -_tiempo * 4.0 + k * TAU / 10.0
		if (sin(a) > 0.0) != delante:
			continue
		var r := 6.0 + (k % 2) * 2.0
		_pixel(Vector2(cos(a) * r, -1.0 + sin(a) * 1.5), Color(VIENTO, 0.4 if k % 3 else 0.6), lienzo)


## Las alas de brisa (alitas o grandes) en los hombros, aleteando despacio
func _dibujar_alas(forma: Array, lienzo: CanvasItem) -> void:
	var marco: Array = forma[int(_tiempo * 2.5) % 2]
	var ancho := (marco[0] as String).length()
	var alto := marco.size()
	var hombro := Vector2(4, -12)
	var mirando := _mirando()
	if mirando == "lado":
		# de perfil se ve un ala, por la espalda
		var atras := 1.0 if _sprite.flip_h else -1.0
		var origen := Vector2(atras * 2.0, hombro.y) + Vector2(-ancho if atras < 0 else 0, -alto + 2)
		_cuadricula(origen, marco, BRISA, atras > 0, 1.0, lienzo)
		return
	_cuadricula(Vector2(-hombro.x - ancho, hombro.y - alto + 2), marco, BRISA, false, 1.0, lienzo)
	_cuadricula(Vector2(hombro.x, hombro.y - alto + 2), marco, BRISA, true, 1.0, lienzo)


## Lo que va por detrás: el aura, la mitad de atrás de los anillos y del remolino, y las alas
func _dibujar_detras() -> void:
	if _sprite == null:
		return
	if "aura" in _rasgos:
		var pulso := 0.5 + 0.5 * sin(_tiempo * 1.8)
		var c := Vector2(0, -15)
		for i in 3:
			_aura.draw_circle(c, 10.0 + i * 4.0 + pulso * 2.0, Color(0.55, 0.8, 1.0, 0.03 + 0.012 * pulso))
	if "anillos" in _rasgos:
		_dibujar_anillos(false, _aura)
	if "remolino" in _rasgos:
		_dibujar_remolino(false, _aura)
	if _mirando() != "arriba":
		if "alitas" in _rasgos:
			_dibujar_alas(ALITA, _aura)
		if "alas" in _rasgos:
			_dibujar_alas(ALA, _aura)
