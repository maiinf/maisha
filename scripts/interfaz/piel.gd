extends RefCounted
## LA PIEL DE LA INTERFAZ: todo parece salido del diario de cuero de Maisha.
## Cajas que se estiran en 9 trozos (arte/interfaz/diario/, herramientas/pintar_interfaz.py) y los colores de tinta.
##   PIEL.caja(lienzo, rect, "pergamino")     caja de pergamino con borde de cuero cosido
##   PIEL.caja(lienzo, rect, "papel")         papel suelto con el borde rasgado
##   PIEL.caja(lienzo, rect, "cuero")         etiqueta de cuero cosida
##   PIEL.caja(lienzo, rect, "noche")         azul de noche con filigrana dorada (el narrador)

const TINTA := Color("3a2414")          # texto sobre el papel
const TINTA_SUAVE := Color("6b4a2e")    # texto secundario
const TINTA_APAGADA := Color("8e7656")  # lo cumplido, lo que no se puede
const ROJO := Color("8c281e")           # la historia, lo importante
const VERDE := Color("3e6a2a")          # hecho
const AZUL := Color("2a5a58")           # encargos
const MORADO := Color("5e3270")         # secretos
const ROSA := Color("8e3a5a")           # lazos
const ORO := Color("d6b46e")
const CREMA := Color("f8efd6")          # texto sobre el cuero
const MARCADOR := Color("f2c94a")       # el subrayador de lo elegido

const MARGENES := {"pergamino": 12, "papel": 12, "cuero": 8, "noche": 14}

static var _estilos := {}


static func estilo(tipo: String) -> StyleBoxTexture:
	if not _estilos.has(tipo):
		var s := StyleBoxTexture.new()
		s.texture = load("res://arte/interfaz/diario/%s.png" % tipo)
		var m: int = MARGENES.get(tipo, 12)
		s.texture_margin_left = m
		s.texture_margin_right = m
		s.texture_margin_top = m
		s.texture_margin_bottom = m
		s.axis_stretch_horizontal = StyleBoxTexture.AXIS_STRETCH_MODE_TILE_FIT
		s.axis_stretch_vertical = StyleBoxTexture.AXIS_STRETCH_MODE_TILE_FIT
		_estilos[tipo] = s
	return _estilos[tipo]


static func caja(lienzo: CanvasItem, rect: Rect2, tipo := "pergamino", alfa := 1.0, sombra := true) -> void:
	if sombra:
		lienzo.draw_rect(Rect2(rect.position + Vector2(3, 4), rect.size), Color(0, 0, 0, 0.35 * alfa))
	if alfa < 0.999:
		var s := estilo(tipo).duplicate() as StyleBoxTexture
		s.modulate_color = Color(1, 1, 1, alfa)
		lienzo.draw_style_box(s, _redondo(rect))
		return
	lienzo.draw_style_box(estilo(tipo), _redondo(rect))


## Un subrayado de rotulador amarillo, con los bordes algo irregulares (lo elegido en una lista)
static func subrayar(lienzo: CanvasItem, rect: Rect2, tiempo := 0.0, alfa := 1.0) -> void:
	var r := _redondo(rect)
	lienzo.draw_rect(Rect2(r.position + Vector2(2, 1), r.size - Vector2(4, 2)), Color(MARCADOR, 0.42 * alfa))
	var x := r.position.x
	var k := 0
	while x < r.end.x:
		var arriba := 1.0 if (k * 7) % 3 == 0 else 0.0
		var abajo := 1.0 if (k * 5) % 4 == 0 else 0.0
		lienzo.draw_rect(Rect2(x, r.position.y + arriba, 3, r.size.y - arriba - abajo), Color(MARCADOR, 0.18 * alfa))
		x += 3
		k += 1


## Una cinta roja de marcapáginas que señala una fila
static func marcapaginas(lienzo: CanvasItem, punta: Vector2, alfa := 1.0) -> void:
	var p := punta.round()
	lienzo.draw_colored_polygon(PackedVector2Array([p + Vector2(-14, -6), p + Vector2(-2, -6), p, p + Vector2(-2, 6), p + Vector2(-14, 6),
		p + Vector2(-10, 0)]), Color(ROJO, alfa))
	lienzo.draw_rect(Rect2(p + Vector2(-14, -6), Vector2(12, 2)), Color(Color("b44634"), alfa))


## Un trazo de tinta (raya hecha a mano) entre dos puntos
static func raya(lienzo: CanvasItem, a: Vector2, b: Vector2, color := TINTA_SUAVE, alfa := 0.6) -> void:
	var pasos := int(a.distance_to(b) / 6.0) + 1
	for i in pasos:
		var p0 := a.lerp(b, float(i) / pasos)
		var p1 := a.lerp(b, float(i + 1) / pasos)
		var d := Vector2(0, 0.5 if i % 3 == 0 else 0.0)
		lienzo.draw_line((p0 + d).round(), (p1 + d).round(), Color(color, alfa), 1.0)


static func _redondo(r: Rect2) -> Rect2:
	return Rect2(r.position.round(), r.size.round())
