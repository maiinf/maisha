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


static func sombra_suave(lienzo: CanvasItem, rect: Rect2, alfa := 1.0, capas := 3) -> void:
	if alfa <= 0.01:
		return
	var r := _redondo(rect)
	for i in range(capas, 0, -1):
		var fi := float(i)
		var sr := _redondo(Rect2(r.position + Vector2(fi * 0.8, fi * 1.4), r.size + Vector2(fi * 0.6, fi * 0.6)))
		var a_capa := (0.24 / fi) * alfa
		# Esquinas biseladas 1px para evitar bloques negros cuadrados
		lienzo.draw_rect(Rect2(sr.position.x + 1.0, sr.position.y, maxf(1.0, sr.size.x - 2.0), sr.size.y), Color(0.0, 0.0, 0.0, a_capa))
		lienzo.draw_rect(Rect2(sr.position.x, sr.position.y + 1.0, sr.size.x, maxf(1.0, sr.size.y - 2.0)), Color(0.0, 0.0, 0.0, a_capa * 0.5))


static func caja(lienzo: CanvasItem, rect: Rect2, tipo := "pergamino", alfa := 1.0, sombra := true) -> void:
	if alfa <= 0.01:
		return
	var r := _redondo(rect)
	if sombra:
		sombra_suave(lienzo, r, alfa, 3)
	if tipo in ["cristal", "terciopelo"]:
		var col_top := Color(0.115, 0.095, 0.175, 0.90 * alfa) if tipo == "terciopelo" else Color(0.085, 0.075, 0.13, 0.80 * alfa)
		var col_bot := Color(0.045, 0.038, 0.082, 0.95 * alfa) if tipo == "terciopelo" else Color(0.035, 0.030, 0.068, 0.88 * alfa)
		# Gradiente vertical sedoso por vértice (sin cortes horizontales) con esquinas biseladas
		var pts := PackedVector2Array([
			Vector2(r.position.x + 1.0, r.position.y),
			Vector2(r.end.x - 1.0, r.position.y),
			Vector2(r.end.x - 1.0, r.end.y),
			Vector2(r.position.x + 1.0, r.end.y),
		])
		lienzo.draw_polygon(pts, PackedColorArray([col_top, col_top, col_bot, col_bot]))
		lienzo.draw_rect(Rect2(r.position.x, r.position.y + 1.0, 1.0, maxf(1.0, r.size.y - 2.0)), col_bot)
		lienzo.draw_rect(Rect2(r.end.x - 1.0, r.position.y + 1.0, 1.0, maxf(1.0, r.size.y - 2.0)), col_bot)
		# Bisel superior especular cálido y contorno fino
		lienzo.draw_line(r.position + Vector2(2, 1), Vector2(r.end.x - 2, r.position.y + 1), Color(ORO_BRILLO, 0.44 * alfa), 1.0)
		lienzo.draw_rect(Rect2(r.position + Vector2(1, 1), r.size - Vector2(2, 2)), Color(ORO, 0.30 * alfa), false, 1.0)
		if r.size.x >= 44.0 and r.size.y >= 26.0:
			lienzo.draw_rect(Rect2(r.position + Vector2(3, 3), r.size - Vector2(6, 6)), Color(ORO, 0.09 * alfa), false, 1.0)
		return
	lienzo.draw_style_box(_estilo_con_alfa(tipo, alfa), r)
	if tipo == "noche" and r.size.x >= 44.0 and r.size.y >= 26.0:
		# Terciopelo profundo con brillo especular superior y filete dorado fino
		var inner := Rect2(r.position + Vector2(6, 6), r.size - Vector2(12, 12))
		lienzo.draw_rect(inner, Color(NOCHE_FONDO, 0.94 * alfa))
		lienzo.draw_rect(Rect2(inner.position, Vector2(inner.size.x, minf(12.0, inner.size.y * 0.35))), Color(0.18, 0.15, 0.28, 0.28 * alfa))
		lienzo.draw_line(r.position + Vector2(5, 4), Vector2(r.end.x - 5, r.position.y + 4), Color(ORO_BRILLO, 0.45 * alfa), 1.0)
		lienzo.draw_rect(Rect2(r.position + Vector2(4, 4), r.size - Vector2(8, 8)), Color(ORO, 0.34 * alfa), false, 1.0)
	elif tipo == "cuero" and r.size.x >= 28.0 and r.size.y >= 18.0:
		lienzo.draw_line(r.position + Vector2(3, 2), Vector2(r.end.x - 3, r.position.y + 2), Color(ORO_BRILLO, 0.32 * alfa), 1.0)
		lienzo.draw_rect(Rect2(r.position + Vector2(2, 2), r.size - Vector2(4, 4)), Color(CUERO_OSCURO, 0.24 * alfa), false, 1.0)
	elif tipo == "pergamino" and r.size.x >= 80.0 and r.size.y >= 60.0:
		lienzo.draw_line(r.position + Vector2(8, 7), Vector2(r.end.x - 8, r.position.y + 7), Color(1.0, 0.98, 0.9, 0.35 * alfa), 1.0)
		lienzo.draw_rect(Rect2(r.position + Vector2(8, 8), r.size - Vector2(16, 16)), Color(TINTA_SUAVE, 0.14 * alfa), false, 1.0)


## Píldora de selección moderna con gradiente cálido, barra lateral luminosa y barrido metálico animado
static func subrayar(lienzo: CanvasItem, rect: Rect2, tiempo := 0.0, alfa := 1.0) -> void:
	if alfa <= 0.01:
		return
	var r := _redondo(rect)
	# Halo exterior sutil
	lienzo.draw_rect(r.grow(1.0), Color(MARCADOR, 0.10 * alfa), false, 1.0)
	# Degradado horizontal suave por vértice (sin bloques escalonados)
	var c_izq := Color(MARCADOR, 0.42 * alfa)
	var c_der := Color(MARCADOR, 0.14 * alfa)
	var pts := PackedVector2Array([
		r.position + Vector2(1.0, 1.0),
		Vector2(r.end.x - 1.0, r.position.y + 1.0),
		r.end - Vector2(1.0, 1.0),
		Vector2(r.position.x + 1.0, r.end.y - 1.0),
	])
	lienzo.draw_polygon(pts, PackedColorArray([c_izq, c_der, c_der, c_izq]))
	# Filo superior e inferior luminosos
	lienzo.draw_line(r.position + Vector2(2, 1), Vector2(r.end.x - 2, r.position.y + 1), Color(ORO_BRILLO, 0.62 * alfa), 1.0)
	lienzo.draw_line(Vector2(r.position.x + 2, r.end.y - 1), Vector2(r.end.x - 2, r.end.y - 1), Color(ORO, 0.30 * alfa), 1.0)
	# Barra vertical izquierda de acento con núcleo brillante
	lienzo.draw_rect(Rect2(r.position.x, r.position.y + 1.0, 3.0, maxf(1.0, r.size.y - 2.0)), Color(ORO_BRILLO, 0.95 * alfa))
	lienzo.draw_rect(Rect2(r.position.x + 3.0, r.position.y + 2.0, 2.0, maxf(1.0, r.size.y - 4.0)), Color(MARCADOR, 0.35 * alfa))
	# Barrido especular diagonal suave si se pasa tiempo
	if r.size.x > 24.0:
		var t_uso := tiempo if tiempo > 0.0 else float(Time.get_ticks_msec()) * 0.001
		var fase := fmod(t_uso * 0.55, 1.35)
		if fase <= 1.0:
			var sx := roundf(r.position.x + 6.0 + (r.size.x - 16.0) * fase)
			var sw := minf(14.0, r.end.x - sx - 2.0)
			if sw > 2.0:
				lienzo.draw_rect(Rect2(sx, r.position.y + 1.0, sw, maxf(1.0, r.size.y - 2.0)), Color(1.0, 0.97, 0.82, 0.16 * alfa))


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


const TACTICO_INFO := {
	"fuego": ["Fuego", Color("ff9a40")],
	"hielo": ["Hielo", Color("7ad7f0")],
	"rayo": ["Rayo", Color("f6e05e")],
	"sismica": ["Carga Sísmica", Color("f8b040")],
	"magnetico": ["Pulso Magnético", Color("6ad0f0")],
	"resonancia": ["Resonancia de Ámbar", Color("ffd878")],
	"semilla": ["Semilla", Color("8fe06a")],
	"escudo": ["Escudo", Color("d6b46e")],
	"latido": ["Latido", Color("e6a852")],
	"atras": ["Por la espalda", Color("c8a0f0")],
	"sol": ["Luz del sol", Color("ffd466")],
}


## Icono vectorial nítido de elemento o táctica (reutilizable entre HUD de combate y Bestiario)
static func icono_tactico(lienzo: CanvasItem, centro: Vector2, clave: String, escala := 1.0, alfa := 1.0) -> void:
	if not TACTICO_INFO.has(clave) or alfa <= 0.01:
		return
	var col: Color = TACTICO_INFO[clave][1]
	var c := centro.round()
	var r := 5.0 * escala
	lienzo.draw_circle(c, r + 1.0, Color(0.06, 0.04, 0.09, 0.94 * alfa))
	lienzo.draw_arc(c, r + 1.0, 0.0, TAU, 16, Color(col, 0.85 * alfa), 1.0)
	var ct := Color(col, alfa)
	match clave:
		"fuego":
			lienzo.draw_colored_polygon(PackedVector2Array([
				c + Vector2(0, -3.8) * escala, c + Vector2(2.8, 0.5) * escala,
				c + Vector2(1.4, 3.2) * escala, c + Vector2(-1.4, 3.2) * escala, c + Vector2(-2.8, 0.5) * escala,
			]), ct)
		"hielo":
			lienzo.draw_line((c + Vector2(0, -3.5) * escala).round(), (c + Vector2(0, 3.5) * escala).round(), ct, 1.0)
			lienzo.draw_line((c + Vector2(-3.2, -1.8) * escala).round(), (c + Vector2(3.2, 1.8) * escala).round(), ct, 1.0)
			lienzo.draw_line((c + Vector2(-3.2, 1.8) * escala).round(), (c + Vector2(3.2, -1.8) * escala).round(), ct, 1.0)
		"rayo":
			lienzo.draw_polyline(PackedVector2Array([
				(c + Vector2(1.8, -3.8) * escala).round(), (c + Vector2(-1.8, -0.3) * escala).round(),
				(c + Vector2(1.6, 0.3) * escala).round(), (c + Vector2(-1.8, 3.8) * escala).round(),
			]), ct, 1.4)
		"sismica":
			lienzo.draw_arc(c, 3.2 * escala, -PI * 0.85, -PI * 0.15, 8, ct, 1.5)
			lienzo.draw_line((c + Vector2(-2.8, 1.8) * escala).round(), (c + Vector2(2.8, 1.8) * escala).round(), ct, 1.5)
		"magnetico":
			lienzo.draw_arc((c + Vector2(0, 0.4) * escala).round(), 2.4 * escala, 0.0, PI, 8, ct, 1.4)
			lienzo.draw_line((c + Vector2(-2.4, 0.4) * escala).round(), (c + Vector2(-2.4, -2.5) * escala).round(), ct, 1.4)
			lienzo.draw_line((c + Vector2(2.4, 0.4) * escala).round(), (c + Vector2(2.4, -2.5) * escala).round(), ct, 1.4)
			lienzo.draw_line((c + Vector2(-2.4, -2.2) * escala).round(), (c + Vector2(-2.4, -3.4) * escala).round(), Color("e6f8ff", alfa), 1.5)
			lienzo.draw_line((c + Vector2(2.4, -2.2) * escala).round(), (c + Vector2(2.4, -3.4) * escala).round(), Color("e6f8ff", alfa), 1.5)
		"resonancia":
			lienzo.draw_line((c + Vector2(0, 0.8) * escala).round(), (c + Vector2(0, 3.6) * escala).round(), ct, 1.4)
			lienzo.draw_polyline(PackedVector2Array([
				(c + Vector2(-1.8, -2.8) * escala).round(),
				(c + Vector2(-1.8, 0.6) * escala).round(),
				(c + Vector2(1.8, 0.6) * escala).round(),
				(c + Vector2(1.8, -2.8) * escala).round(),
			]), ct, 1.3)
			lienzo.draw_arc((c + Vector2(0, -1.5) * escala).round(), 3.6 * escala, -PI * 0.72, -PI * 0.28, 6, Color("fff3c4", 0.85 * alfa), 1.0)
		"semilla":
			lienzo.draw_circle(c, 2.3 * escala, ct)
			lienzo.draw_line(c.round(), (c + Vector2(0, -4.0) * escala).round(), Color("fff3c4", alfa), 1.0)
		"escudo":
			lienzo.draw_colored_polygon(PackedVector2Array([
				c + Vector2(-3.0, -3.0) * escala, c + Vector2(3.0, -3.0) * escala,
				c + Vector2(2.6, 0.8) * escala, c + Vector2(0, 3.6) * escala, c + Vector2(-2.6, 0.8) * escala,
			]), ct)
		"latido":
			lienzo.draw_arc(c, 1.8 * escala, 0.0, TAU, 10, ct, 1.2)
			lienzo.draw_arc(c, 3.4 * escala, 0.0, TAU, 12, Color(col, 0.7 * alfa), 1.0)
		"atras":
			lienzo.draw_polyline(PackedVector2Array([
				(c + Vector2(-3.0, -1.5) * escala).round(), (c + Vector2(0, -3.2) * escala).round(), (c + Vector2(3.0, 0) * escala).round(),
			]), ct, 1.4)
			lienzo.draw_circle((c + Vector2(2.5, 1.5) * escala).round(), 1.3 * escala, ct)
		"sol":
			lienzo.draw_circle(c, 2.0 * escala, ct)
			lienzo.draw_circle(c, 1.0 * escala, Color("fff6cf", alfa))
			for i in 8:
				var ang := float(i) * TAU / 8.0
				var dir := Vector2(cos(ang), sin(ang))
				lienzo.draw_line((c + dir * 2.5 * escala).round(), (c + dir * 3.9 * escala).round(), ct, 1.1)


static func _redondo(r: Rect2) -> Rect2:
	return Rect2(r.position.round(), r.size.round())


## Crea un ColorRect con el shader de desenfoque cinematográfico detrás de un modal
static func crear_fondo_desenfoque(padre: Node, calidez := 0.25) -> ColorRect:
	var cr := ColorRect.new()
	cr.set_anchors_preset(Control.PRESET_FULL_RECT)
	cr.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := load("res://shaders/interfaz_desenfoque.gdshader") as Shader
	if sh != null:
		var mat := ShaderMaterial.new()
		mat.shader = sh
		mat.set_shader_parameter("fuerza", 0.0)
		mat.set_shader_parameter("calidez", calidez)
		cr.material = mat
	else:
		cr.color = Color(0.04, 0.03, 0.08, 0.8)
	padre.add_child(cr)
	padre.move_child(cr, 0)
	return cr


static func actualizar_desenfoque(cr: ColorRect, fuerza: float, calidez := 0.25) -> void:
	if cr == null:
		return
	var f := clampf(fuerza, 0.0, 1.0)
	cr.visible = f > 0.01
	if cr.material is ShaderMaterial:
		var mat := cr.material as ShaderMaterial
		mat.set_shader_parameter("fuerza", f)
		mat.set_shader_parameter("calidez", calidez)
	else:
		cr.color = Color(0.04, 0.03, 0.08, 0.78 * f)


## Interpolación exponencial independiente de FPS
static func resorte(actual: float, destino: float, delta: float, rapidez := 16.0) -> float:
	return lerpf(actual, destino, clampf(1.0 - exp(-rapidez * delta), 0.0, 1.0))


## Tarjeta interactiva moderna con bisel luminoso superior, respuesta de hover y barrido metálico
static func tarjeta(lienzo: CanvasItem, rect: Rect2, alfa := 1.0, seleccionada := false,
		hover := false, col_acento := ORO, tiempo := 0.0, sombra := true) -> void:
	if alfa <= 0.01:
		return
	var r := _redondo(rect)
	if sombra:
		sombra_suave(lienzo, r, alfa * (0.95 if seleccionada or hover else 0.65), 2)
	var col_fondo := Color(0.16, 0.12, 0.20, 0.92 * alfa) if seleccionada else (
		Color(0.13, 0.10, 0.17, 0.88 * alfa) if hover else Color(0.09, 0.07, 0.13, 0.82 * alfa))
	lienzo.draw_rect(Rect2(r.position.x + 1.0, r.position.y, maxf(1.0, r.size.x - 2.0), r.size.y), col_fondo)
	lienzo.draw_rect(Rect2(r.position.x, r.position.y + 1.0, r.size.x, maxf(1.0, r.size.y - 2.0)), col_fondo)
	# Franja superior cálida
	lienzo.draw_rect(Rect2(r.position.x + 1.0, r.position.y + 1.0, maxf(1.0, r.size.x - 2.0), minf(8.0, r.size.y * 0.35)),
		Color(col_acento, (0.16 if seleccionada else (0.10 if hover else 0.04)) * alfa))
	# Contorno y bisel superior
	var borde_a := 0.85 if seleccionada else (0.55 if hover else 0.24)
	lienzo.draw_rect(Rect2(r.position + Vector2(1, 1), r.size - Vector2(2, 2)), Color(col_acento, borde_a * alfa), false, 1.0)
	lienzo.draw_line(r.position + Vector2(2, 1), Vector2(r.end.x - 2, r.position.y + 1),
		Color(ORO_BRILLO if seleccionada or hover else col_acento, (0.75 if seleccionada else 0.38) * alfa), 1.0)
	if seleccionada:
		lienzo.draw_rect(Rect2(r.position.x, r.position.y + 2.0, 3.0, maxf(2.0, r.size.y - 4.0)), Color(ORO_BRILLO, 0.95 * alfa))
		if r.size.x > 28.0:
			var t_uso := tiempo if tiempo > 0.0 else float(Time.get_ticks_msec()) * 0.001
			var fase := fmod(t_uso * 0.5, 1.4)
			if fase <= 1.0:
				var sx := roundf(r.position.x + 6.0 + (r.size.x - 16.0) * fase)
				var sw := minf(16.0, r.end.x - sx - 2.0)
				if sw > 2.0:
					lienzo.draw_rect(Rect2(sx, r.position.y + 1.0, sw, maxf(1.0, r.size.y - 2.0)), Color(ORO_BRILLO, 0.11 * alfa))


## Motas/brasas doradas flotantes suaves para el fondo de menús modales
static func motas_ambiente(lienzo: CanvasItem, tiempo: float, alfa := 1.0, cantidad := 18, col := ORO_BRILLO) -> void:
	if alfa <= 0.01:
		return
	for i in cantidad:
		var fi := float(i)
		var velocidad := 6.0 + fmod(fi * 3.7, 9.0)
		var x := fmod(fi * 47.3 + sin(tiempo * 0.45 + fi * 1.9) * 18.0 + 640.0, 640.0)
		var y := 360.0 - fmod(tiempo * velocidad + fi * 29.1, 360.0)
		var parpadeo := 0.35 + 0.65 * (0.5 + 0.5 * sin(tiempo * (1.6 + fmod(fi, 3.0) * 0.4) + fi * 2.3))
		var tam := 2.0 if i % 4 == 0 else 1.0
		var pos := Vector2(roundf(x), roundf(y))
		if tam > 1.5:
			lienzo.draw_circle(pos, 2.6, Color(col, 0.09 * parpadeo * alfa))
		lienzo.draw_rect(Rect2(pos, Vector2(tam, tam)), Color(col, 0.34 * parpadeo * alfa))


## Anillo de progreso circular fluido («Mantén pulsado» o carga)
static func anillo_progreso(lienzo: CanvasItem, centro: Vector2, radio: float, progreso: float,
		col := ORO_BRILLO, alfa := 1.0, grosor := 2.2) -> void:
	var p := clampf(progreso, 0.0, 1.0)
	if p <= 0.005 or alfa <= 0.01:
		return
	var c := centro.round()
	lienzo.draw_arc(c, radio, 0.0, TAU, 28, Color(0.05, 0.04, 0.09, 0.65 * alfa), grosor + 1.4)
	var a0 := -PI * 0.5
	var a1 := a0 + TAU * p
	lienzo.draw_arc(c, radio, a0, a1, 28, Color(col, 0.95 * alfa), grosor)
	var punta := c + Vector2(cos(a1), sin(a1)) * radio
	lienzo.draw_circle(punta, grosor + 0.8, Color(1.0, 0.98, 0.88, 0.92 * alfa))


## Emite chispas de UI en `origen` dentro del array `chispas`
static func emitir_chispas(chispas: Array, origen: Vector2, cantidad := 14, col := ORO_BRILLO) -> void:
	for i in cantidad:
		var ang := (TAU * float(i) / float(maxi(1, cantidad))) + randf_range(-0.22, 0.22)
		var vel := randf_range(26.0, 78.0)
		chispas.append({
			"p": origen,
			"v": Vector2(cos(ang), sin(ang)) * vel + Vector2(0, -14.0),
			"t": 0.0,
			"d": randf_range(0.32, 0.58),
			"c": col.lightened(randf_range(0.0, 0.25)),
			"s": 2.0 if i % 3 == 0 else 1.0,
		})


## Actualiza y dibuja chispas de UI activas
static func actualizar_chispas(lienzo: CanvasItem, chispas: Array, delta: float, alfa := 1.0) -> void:
	for i in range(chispas.size() - 1, -1, -1):
		var ch: Dictionary = chispas[i]
		var t := float(ch["t"]) + delta
		var d := float(ch["d"])
		if t >= d:
			chispas.remove_at(i)
			continue
		var v: Vector2 = ch["v"]
		v.y += 95.0 * delta
		v *= exp(-3.5 * delta)
		var p: Vector2 = ch["p"] + v * delta
		ch["t"] = t
		ch["v"] = v
		ch["p"] = p
		chispas[i] = ch
		var a := (1.0 - t / d) * alfa
		var col: Color = ch["c"]
		var tam := float(ch["s"])
		var pr := p.round()
		if tam > 1.5:
			lienzo.draw_circle(pr, 2.5, Color(col, 0.22 * a))
		lienzo.draw_rect(Rect2(pr, Vector2(tam, tam)), Color(col, a))
