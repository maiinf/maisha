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
const ORO_BRILLO := Color("f4df9a")
const CREMA := Color("f8efd6")          # texto sobre el cuero
const MARCADOR := Color("f2c94a")       # el subrayador de lo elegido
const CUERO_OSCURO := Color("24150d")
const NOCHE_FONDO := Color("120f1c")

const MARGENES := {"pergamino": 12, "papel": 12, "cuero": 8, "noche": 14}

static var _estilos := {}
static var _estilos_alfa := {}


static func estilo(tipo: String) -> StyleBoxTexture:
	if not _estilos.has(tipo):
		var s := StyleBoxTexture.new()
		s.texture = load("res://arte/interfaz/diario/%s.png" % tipo)
		var m: int = MARGENES.get(tipo, 12)
		s.texture_margin_left = m
		s.texture_margin_right = m
		s.texture_margin_top = m
		s.texture_margin_bottom = m
		var modo := StyleBoxTexture.AXIS_STRETCH_MODE_STRETCH if tipo in ["noche", "cuero"] else StyleBoxTexture.AXIS_STRETCH_MODE_TILE_FIT
		s.axis_stretch_horizontal = modo
		s.axis_stretch_vertical = modo
		_estilos[tipo] = s
	return _estilos[tipo]


static func _estilo_con_alfa(tipo: String, alfa: float) -> StyleBoxTexture:
	if alfa >= 0.999:
		return estilo(tipo)
	var paso := int(round(clampf(alfa, 0.0, 1.0) * 20.0))
	var clave := "%s|%d" % [tipo, paso]
	if not _estilos_alfa.has(clave):
		var s := estilo(tipo).duplicate() as StyleBoxTexture
		s.modulate_color = Color(1.0, 1.0, 1.0, float(paso) / 20.0)
		_estilos_alfa[clave] = s
	return _estilos_alfa[clave]


static func caja(lienzo: CanvasItem, rect: Rect2, tipo := "pergamino", alfa := 1.0, sombra := true) -> void:
	if alfa <= 0.01:
		return
	var r := _redondo(rect)
	if sombra:
		lienzo.draw_rect(Rect2(r.position + Vector2(3, 4), r.size), Color(0.0, 0.0, 0.0, 0.36 * alfa))
		lienzo.draw_rect(Rect2(r.position + Vector2(2, 2), r.size), Color(0.0, 0.0, 0.0, 0.18 * alfa))
	lienzo.draw_style_box(_estilo_con_alfa(tipo, alfa), r)
	if tipo == "noche" and r.size.x >= 44.0 and r.size.y >= 32.0:
		# Terciopelo uniforme sobre el centro de noche.png + filete dorado interior sutil
		var inner := Rect2(r.position + Vector2(7, 7), r.size - Vector2(14, 14))
		lienzo.draw_rect(inner, Color(NOCHE_FONDO, 0.92 * alfa))
		lienzo.draw_rect(Rect2(r.position + Vector2(4, 4), r.size - Vector2(8, 8)), Color(ORO, 0.32 * alfa), false, 1.0)
	elif tipo == "cuero" and r.size.x >= 28.0 and r.size.y >= 18.0:
		lienzo.draw_line(r.position + Vector2(3, 2), Vector2(r.end.x - 3, r.position.y + 2), Color(ORO, 0.24 * alfa), 1.0)
		lienzo.draw_rect(Rect2(r.position + Vector2(2, 2), r.size - Vector2(4, 4)), Color(CUERO_OSCURO, 0.28 * alfa), false, 1.0)
	elif tipo == "pergamino" and r.size.x >= 80.0 and r.size.y >= 60.0:
		lienzo.draw_rect(Rect2(r.position + Vector2(8, 8), r.size - Vector2(16, 16)), Color(TINTA_SUAVE, 0.16 * alfa), false, 1.0)


## Un subrayado de rotulador amarillo, con los bordes algo irregulares (lo elegido en una lista)
static func subrayar(lienzo: CanvasItem, rect: Rect2, _tiempo := 0.0, alfa := 1.0) -> void:
	var r := _redondo(rect)
	lienzo.draw_rect(Rect2(r.position + Vector2(2, 1), r.size - Vector2(4, 2)), Color(MARCADOR, 0.44 * alfa))
	lienzo.draw_rect(Rect2(r.position + Vector2(1, 0), Vector2(2, r.size.y)), Color(ORO, 0.85 * alfa))
	var x := r.position.x
	var k := 0
	while x < r.end.x:
		var arriba := 1.0 if (k * 7) % 3 == 0 else 0.0
		var abajo := 1.0 if (k * 5) % 4 == 0 else 0.0
		var paso := minf(3.0, r.end.x - x)
		lienzo.draw_rect(Rect2(x, r.position.y + arriba, paso, maxf(1.0, r.size.y - arriba - abajo)), Color(MARCADOR, 0.22 * alfa))
		x += 3.0
		k += 1


## Una cinta roja de marcapáginas que señala una fila
static func marcapaginas(lienzo: CanvasItem, punta: Vector2, alfa := 1.0) -> void:
	var p := punta.round()
	lienzo.draw_colored_polygon(PackedVector2Array([p + Vector2(-14, -6), p + Vector2(-2, -6), p, p + Vector2(-2, 6), p + Vector2(-14, 6),
		p + Vector2(-10, 0)]), Color(ROJO, alfa))
	lienzo.draw_rect(Rect2(p + Vector2(-14, -6), Vector2(12, 2)), Color(Color("b44634"), alfa))
	lienzo.draw_rect(Rect2(p + Vector2(-4, -1), Vector2(2, 2)), Color(ORO_BRILLO, 0.85 * alfa))


## Un trazo de tinta (raya hecha a mano) entre dos puntos
static func raya(lienzo: CanvasItem, a: Vector2, b: Vector2, color := TINTA_SUAVE, alfa := 0.6) -> void:
	var pasos := int(a.distance_to(b) / 6.0) + 1
	for i in pasos:
		var p0 := a.lerp(b, float(i) / pasos)
		var p1 := a.lerp(b, float(i + 1) / pasos)
		var d := Vector2(0, 0.5 if i % 3 == 0 else 0.0)
		lienzo.draw_line((p0 + d).round(), (p1 + d).round(), Color(color, alfa), 1.0)


## Separador ornamental con rombo dorado en el centro
static func divisor(lienzo: CanvasItem, x0: float, x1: float, y: float, color := TINTA_SUAVE, alfa := 0.6) -> void:
	var cy := roundf(y)
	var cx := roundf((x0 + x1) * 0.5)
	if x1 - x0 < 18.0:
		raya(lienzo, Vector2(x0, cy), Vector2(x1, cy), color, alfa)
		return
	raya(lienzo, Vector2(x0, cy), Vector2(cx - 7.0, cy), color, alfa)
	raya(lienzo, Vector2(cx + 7.0, cy), Vector2(x1, cy), color, alfa)
	var pts := PackedVector2Array([
		Vector2(cx, cy - 3.0), Vector2(cx + 3.0, cy),
		Vector2(cx, cy + 3.0), Vector2(cx - 3.0, cy),
	])
	lienzo.draw_colored_polygon(pts, Color(ORO, 0.85 * alfa))
	lienzo.draw_rect(Rect2(cx - 1.0, cy - 1.0, 2.0, 2.0), Color(CREMA, 0.6 * alfa))


## Esquineras doradas / remaches en las cuatro esquinas de una caja
static func esquinas_oro(lienzo: CanvasItem, rect: Rect2, col := ORO, alfa := 1.0, largo := 6.0) -> void:
	var r := _redondo(rect)
	var c := Color(col, 0.85 * alfa)
	var cd := Color(col, 0.35 * alfa)
	# Sup izq
	lienzo.draw_line(r.position, r.position + Vector2(largo, 0), c, 1.0)
	lienzo.draw_line(r.position, r.position + Vector2(0, largo), c, 1.0)
	# Sup der
	lienzo.draw_line(Vector2(r.end.x - 1, r.position.y), Vector2(r.end.x - 1 - largo, r.position.y), c, 1.0)
	lienzo.draw_line(Vector2(r.end.x - 1, r.position.y), Vector2(r.end.x - 1, r.position.y + largo), c, 1.0)
	# Inf izq
	lienzo.draw_line(Vector2(r.position.x, r.end.y - 1), Vector2(r.position.x + largo, r.end.y - 1), c, 1.0)
	lienzo.draw_line(Vector2(r.position.x, r.end.y - 1), Vector2(r.position.x, r.end.y - 1 - largo), c, 1.0)
	# Inf der
	lienzo.draw_line(r.end - Vector2(1, 1), r.end - Vector2(1 + largo, 1), c, 1.0)
	lienzo.draw_line(r.end - Vector2(1, 1), r.end - Vector2(1, 1 + largo), c, 1.0)
	# Puntos centrales suaves si cabe
	if r.size.x >= 40.0:
		lienzo.draw_rect(Rect2(r.position + Vector2(2, 2), Vector2(2, 2)), cd)
		lienzo.draw_rect(Rect2(Vector2(r.end.x - 4, r.position.y + 2), Vector2(2, 2)), cd)
		lienzo.draw_rect(Rect2(Vector2(r.position.x + 2, r.end.y - 4), Vector2(2, 2)), cd)
		lienzo.draw_rect(Rect2(r.end - Vector2(4, 4), Vector2(2, 2)), cd)


## Marco rebajado para retratos o iconos destacados
static func marco_retrato(lienzo: CanvasItem, rect: Rect2, col_acento := ORO, alfa := 1.0) -> void:
	var r := _redondo(rect)
	lienzo.draw_rect(Rect2(r.position + Vector2(2, 2), r.size), Color(0, 0, 0, 0.35 * alfa))
	lienzo.draw_rect(r, Color(0.10, 0.07, 0.05, 0.92 * alfa))
	lienzo.draw_rect(r, Color(col_acento, 0.72 * alfa), false, 1.0)
	lienzo.draw_rect(Rect2(r.position + Vector2(2, 2), r.size - Vector2(4, 4)), Color(col_acento, 0.25 * alfa), false, 1.0)
	esquinas_oro(lienzo, Rect2(r.position + Vector2(1, 1), r.size - Vector2(2, 2)), col_acento, alfa, 4.0)


## Barra / medidor pixel-art biselado con cola animada, brillo y muescas opcionales
static func medidor(lienzo: CanvasItem, rect: Rect2, prop: float, col_relleno: Color, cola := -1.0,
		col_cola := Color(0.95, 0.85, 0.55), alfa := 1.0, marcas := 0, umbral := -1.0) -> void:
	var r := _redondo(rect)
	var p := clampf(prop, 0.0, 1.0)
	# Sombra y bisel exterior
	lienzo.draw_rect(Rect2(r.position + Vector2(1, 1), r.size), Color(0, 0, 0, 0.45 * alfa))
	lienzo.draw_rect(r, Color(0.09, 0.06, 0.04, 0.96 * alfa))
	var interior := Rect2(r.position + Vector2(1, 1), Vector2(maxf(2.0, r.size.x - 2.0), maxf(2.0, r.size.y - 2.0)))
	lienzo.draw_rect(interior, Color(0.16, 0.10, 0.07, 0.92 * alfa))
	lienzo.draw_line(interior.position, Vector2(interior.end.x, interior.position.y), Color(0.32, 0.22, 0.14, 0.55 * alfa), 1.0)
	if cola > p:
		var cw := roundf(interior.size.x * clampf(cola, 0.0, 1.0))
		if cw > 0.0:
			lienzo.draw_rect(Rect2(interior.position, Vector2(cw, interior.size.y)), Color(col_cola, 0.85 * alfa))
	var rw := roundf(interior.size.x * p)
	if rw > 0.0:
		var fill := Rect2(interior.position, Vector2(rw, interior.size.y))
		lienzo.draw_rect(fill, Color(col_relleno, alfa))
		if interior.size.y >= 3.0:
			lienzo.draw_rect(Rect2(fill.position, Vector2(rw, 1.0)), Color(col_relleno.lightened(0.32), 0.9 * alfa))
			lienzo.draw_rect(Rect2(fill.position.x, fill.end.y - 1.0, rw, 1.0), Color(col_relleno.darkened(0.28), 0.9 * alfa))
	if marcas > 1:
		for i in range(1, marcas):
			var tx := roundf(interior.position.x + interior.size.x * float(i) / float(marcas))
			lienzo.draw_line(Vector2(tx, interior.position.y), Vector2(tx, interior.end.y), Color(0.08, 0.05, 0.03, 0.48 * alfa), 1.0)
	if umbral > 0.0 and umbral < 1.0:
		var ux := roundf(interior.position.x + interior.size.x * umbral)
		lienzo.draw_rect(Rect2(ux, r.position.y - 1.0, 1.0, r.size.y + 2.0), Color(ORO_BRILLO, 0.9 * alfa))


## Base vertical centrada para un texto dentro de una caja
static func texto_centrado_y(box_y: float, box_h: float, fuente: Font, tam := 16) -> float:
	if fuente == null:
		return roundf(box_y + box_h * 0.72)
	return roundf(box_y + (box_h + fuente.get_ascent(tam) - fuente.get_descent(tam)) * 0.5)


## Pastilla / tecla tactil con bisel 3D. Devuelve su ancho en pixeles.
static func tecla(lienzo: CanvasItem, pos: Vector2, etiqueta: String, fuente: Font, tam := 16,
		alfa := 1.0, iluminada := false) -> float:
	if fuente == null or alfa <= 0.01:
		return 0.0
	var p := pos.round()
	var tw := fuente.get_string_size(etiqueta, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x
	var w := roundf(tw + 9.0)
	var h := 14.0
	var base := Rect2(p + Vector2(0, 1), Vector2(w, h))
	var cara := Rect2(p, Vector2(w, h - 1.0))
	lienzo.draw_rect(base, Color(0.06, 0.04, 0.02, 0.92 * alfa))
	var col_cara := Color("4c331e") if iluminada else Color("302014")
	var col_borde := ORO_BRILLO if iluminada else ORO
	var col_txt := ORO_BRILLO if iluminada else CREMA
	lienzo.draw_rect(cara, Color(col_cara, 0.95 * alfa))
	lienzo.draw_line(cara.position + Vector2(1, 0), Vector2(cara.end.x - 1, cara.position.y), Color(col_borde, 0.75 * alfa), 1.0)
	lienzo.draw_rect(cara, Color(col_borde, 0.45 * alfa), false, 1.0)
	var ty := texto_centrado_y(cara.position.y - 1.0, cara.size.y, fuente, tam)
	lienzo.draw_string(fuente, Vector2(p.x + 4.0, ty), etiqueta, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, Color(col_txt, alfa))
	return w


## Barra horizontal centrada de teclas y acciones: items = [["Espacio", "Aceptar"], ...]
static func barra_teclas(lienzo: CanvasItem, cx: float, y_centro: float, items: Array, fuente: Font,
		tam := 16, alfa := 1.0, oscura := true) -> void:
	if fuente == null or items.is_empty() or alfa <= 0.01:
		return
	var total := 0.0
	var anchos_t := []
	var anchos_d := []
	for par_v: Variant in items:
		var par: Array = par_v
		var tk := String(par[0])
		var ds := String(par[1])
		var wt := 8.0 if tk == "·" else roundf(fuente.get_string_size(tk, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x + 9.0)
		var wd := roundf(fuente.get_string_size(ds, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x) if not ds.is_empty() else 0.0
		anchos_t.append(wt)
		anchos_d.append(wd)
		total += wt + (4.0 + wd if wd > 0.0 else 0.0)
	total += float(maxi(items.size() - 1, 0)) * 10.0
	var alto := 20.0
	var x_ini := clampf(roundf(cx - total * 0.5 - 8.0), 6.0, maxf(6.0, 634.0 - roundf(total + 16.0)))
	var marco := Rect2(x_ini, roundf(y_centro - alto * 0.5), roundf(total + 16.0), alto)
	if oscura:
		lienzo.draw_rect(Rect2(marco.position + Vector2(1, 2), marco.size), Color(0, 0, 0, 0.35 * alfa))
		lienzo.draw_rect(marco, Color(0.08, 0.05, 0.03, 0.84 * alfa))
		lienzo.draw_rect(marco, Color(ORO, 0.38 * alfa), false, 1.0)
	var x := marco.position.x + 8.0
	var ty := texto_centrado_y(marco.position.y, marco.size.y, fuente, tam)
	var col_desc := Color(CREMA, 0.92 * alfa) if oscura else Color(TINTA_SUAVE, 0.95 * alfa)
	for i in items.size():
		var par: Array = items[i]
		var tk := String(par[0])
		var ds := String(par[1])
		var wt := float(anchos_t[i])
		if tk == "·":
			var dc := Vector2(x + 3.0, roundf(marco.get_center().y))
			lienzo.draw_colored_polygon(PackedVector2Array([dc + Vector2(0, -2.5), dc + Vector2(2.5, 0), dc + Vector2(0, 2.5), dc + Vector2(-2.5, 0)]), Color(ORO, 0.85 * alfa))
		else:
			wt = tecla(lienzo, Vector2(x, roundf(marco.position.y + 3.0)), tk, fuente, tam, alfa)
		x += wt
		if not ds.is_empty():
			x += 4.0
			lienzo.draw_string(fuente, Vector2(x, ty), ds, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, col_desc)
			x += float(anchos_d[i])
		x += 10.0


## Pastilla con texto para etiquetas de estado, zonas, monedas y precios. Devuelve el rectangulo usado.
static func insignia(lienzo: CanvasItem, pos: Vector2, texto: String, fuente: Font,
		fondo := CUERO_OSCURO, borde := ORO, col_texto := CREMA, alfa := 1.0, tam := 16, pad_x := 6.0) -> Rect2:
	if fuente == null or alfa <= 0.01:
		return Rect2()
	var tw := fuente.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam).x
	var r := Rect2(pos.round(), Vector2(roundf(tw + pad_x * 2.0), 16.0))
	lienzo.draw_rect(Rect2(r.position + Vector2(1, 1), r.size), Color(0, 0, 0, 0.32 * alfa))
	lienzo.draw_rect(r, Color(fondo, 0.92 * alfa))
	lienzo.draw_rect(r, Color(borde, 0.7 * alfa), false, 1.0)
	var ty := texto_centrado_y(r.position.y, r.size.y, fuente, tam)
	lienzo.draw_string(fuente, Vector2(r.position.x + pad_x, ty), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, tam, Color(col_texto, alfa))
	return r


## Deslizador grafico para volumen o ajustes continuos (reemplaza puntos ASCII)
static func deslizador(lienzo: CanvasItem, rect: Rect2, valor: float, activo := false, col_acento := ORO, alfa := 1.0) -> void:
	var r := _redondo(rect)
	var p := clampf(valor, 0.0, 1.0)
	var pista := Rect2(r.position.x, roundf(r.position.y + r.size.y * 0.5 - 3.0), r.size.x, 6.0)
	lienzo.draw_rect(pista, Color(0.14, 0.09, 0.06, 0.9 * alfa))
	lienzo.draw_rect(pista, Color(TINTA_SUAVE, 0.65 * alfa), false, 1.0)
	var fw := roundf((pista.size.x - 2.0) * p)
	if fw > 0.0:
		var fill_col := col_acento if activo else Color(ORO, 0.75)
		lienzo.draw_rect(Rect2(pista.position + Vector2(1, 1), Vector2(fw, 4.0)), Color(fill_col, alfa))
	var kx := clampf(pista.position.x + pista.size.x * p, pista.position.x + 3.0, pista.end.x - 3.0)
	var perilla := Rect2(roundf(kx - 3.0), roundf(r.position.y + r.size.y * 0.5 - 5.0), 6.0, 10.0)
	lienzo.draw_rect(perilla, Color(CREMA if activo else ORO, alfa))
	lienzo.draw_rect(perilla, Color(CUERO_OSCURO, alfa), false, 1.0)


## Interruptor grafico Activada/Desactivada
static func interruptor(lienzo: CanvasItem, pos: Vector2, encendido: bool, fuente: Font, activo := false, alfa := 1.0) -> void:
	var r := Rect2(pos.round(), Vector2(28.0, 12.0))
	var fondo := Color(VERDE if encendido else CUERO_OSCURO, 0.9 * alfa)
	lienzo.draw_rect(r, fondo)
	lienzo.draw_rect(r, Color(ORO_BRILLO if activo else TINTA_SUAVE, 0.85 * alfa), false, 1.0)
	var kx := r.end.x - 10.0 if encendido else r.position.x + 2.0
	lienzo.draw_rect(Rect2(kx, r.position.y + 2.0, 8.0, 8.0), Color(CREMA, alfa))
	if fuente != null:
		var lbl := "Sí" if encendido else "No"
		var ty := texto_centrado_y(r.position.y, r.size.y, fuente, 16)
		lienzo.draw_string(fuente, Vector2(r.end.x + 6.0, ty), lbl, HORIZONTAL_ALIGNMENT_LEFT, -1, 16,
			Color(VERDE if encendido else TINTA_SUAVE, alfa))


static func _redondo(r: Rect2) -> Rect2:
	return Rect2(r.position.round(), r.size.round())
