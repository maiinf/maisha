extends CanvasLayer
## OBJETIVO EN PANTALLA: arriba a la derecha, la misión que se sigue y lo que hay que hacer ahora.
##   - Una flechita señala adónde ir: encima del sitio si se ve, o en el borde de la pantalla si no.
##     Si el sitio está en otra escena, señala la puerta por la que se va hacia allí.
##   - Avisos al salir una misión nueva o cumplirse una («Misión nueva», «Misión cumplida»).
##   - Se esconde mientras se habla, en plena pelea y con la mochila abierta.
## Se puede quitar desde la pausa («Objetivo en pantalla»).

const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const PIEL := preload("res://scripts/interfaz/piel.gd")
const PANEL := Color(0.08, 0.07, 0.10, 0.72)
const FILO := Color("d6b46e")
const TEXTO := Color("fff3c4")
const APAGADO := Color("c9b07e")
const AMBAR := Color("e6a852")
const VERDE := Color("9be07a")
const ANCHO_MAX := 230.0
const CRISTAL := preload("res://arte/interfaz/cristal.png")
const COLOR_TIPO := {"historia": Color("e6a852"), "encargo": Color("8fd0c4"), "secreto": Color("c9a7e8"), "lazo": Color("f29bb0")}

var _lienzo: Control
var _fuente: FontFile
var _alfa := 0.0
var _tiempo := 0.0
var _destello := 0.0                 # el panel brilla un momento al cumplirse un paso
var _objetivo: Variant = null        # adónde apunta: la cosa (Node2D, se sigue aunque se mueva), una posición o null
var _buscar := 0.0
var _avisos: Array[Dictionary] = []  # {titulo, texto, color, tiempo}
var _aviso_t := 0.0
var _texto_paso := ""
var _texto_anterior := ""
var _cambio := 1.0                   # 0 → 1 al cambiar el texto del paso (se desliza)
var _esencias: Array[Dictionary] = []   # «+2 Esencia» que salen arriba a la izquierda: {n, motivo, t}


func _ready() -> void:
	add_to_group("objetivo")
	layer = 11
	process_mode = Node.PROCESS_MODE_ALWAYS
	_fuente = FUENTE
	_lienzo = Control.new()
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.draw.connect(_dibujar)
	add_child(_lienzo)
	Misiones.mision_nueva.connect(_al_salir_mision)
	Misiones.mision_cumplida.connect(_al_cumplir_mision)
	Misiones.paso_cumplido.connect(_al_cumplir_paso)
	Artes.esencia_ganada.connect(_al_ganar_esencia)
	Tienda.cristales_ganados.connect(_al_ganar_cristales)
	Bestiario.rango_nuevo.connect(_al_subir_rango)


func _al_subir_rango(tipo: String, rango: int) -> void:
	var nombre := String(Bestiario.FICHAS.get(tipo, {}).get("nombre", tipo))
	_avisos.append({"titulo": "Bestiario: rango de " + String(Bestiario.NOMBRE_RANGO[rango]), "texto": nombre,
		"color": Bestiario.COLOR_RANGO[rango], "sonido": "rango_nuevo"})


func _al_ganar_esencia(n: int, motivo: String) -> void:
	_esencias.append({"n": n, "motivo": motivo, "t": 0.0})
	Sonido.efecto("esencia")


func _al_ganar_cristales(n: int, motivo: String) -> void:
	_esencias.append({"n": n, "motivo": motivo, "t": 0.0, "cristal": true})
	Sonido.efecto("cristal")


func _al_salir_mision(m: Dictionary) -> void:
	_avisos.append({"titulo": "Misión nueva", "texto": String(m["titulo"]), "color": COLOR_TIPO.get(m.get("tipo", ""), AMBAR), "sonido": "mision_nueva"})


func _al_cumplir_mision(m: Dictionary) -> void:
	_avisos.append({"titulo": "Misión cumplida", "texto": String(m["titulo"]), "color": VERDE, "sonido": "mision_cumplida"})


func _al_cumplir_paso(_m: Dictionary) -> void:
	_destello = 1.0
	Sonido.efecto("mision_paso")


func _hablando() -> bool:
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	return dialogo != null and dialogo.hablando


## La mochila, la pausa o el Árbol de la Vida tapan la pantalla: los avisos esperan
func oculto_por_menu() -> bool:
	for grupo in ["mochila", "pausa", "arbol_vida"]:
		var n := get_tree().get_first_node_in_group(grupo)
		if n and n.visible:
			return true
	return false


func _oculto() -> bool:
	if not Estado.jugando or Estado.cambiando or _hablando():
		return true
	var mochila := get_tree().get_first_node_in_group("mochila")
	if mochila and mochila.abierta:
		return true
	var arbol := get_tree().get_first_node_in_group("arbol_vida")
	if arbol and arbol.visible:
		return true
	var pausa := get_tree().get_first_node_in_group("pausa")
	if pausa and pausa.abierto:
		return true
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado in [1, 2, 3]:          # en plena pelea
			return true
	return false


func _process(delta: float) -> void:
	_tiempo += delta
	_destello = maxf(0.0, _destello - delta * 1.2)
	_cambio = minf(1.0, _cambio + delta * 3.0)
	var oculto := _oculto()
	var m := Misiones.seguida()
	var hay := not m.is_empty() and Misiones.ver_objetivo
	_alfa = move_toward(_alfa, 0.0 if oculto or not hay else 1.0, delta * 4.0)
	# el texto del paso: si cambia, se desliza
	var texto := String(Misiones.paso_actual(m).get("texto", "")) if hay else ""
	if texto != _texto_paso:
		_texto_anterior = _texto_paso
		_texto_paso = texto
		_cambio = 0.0
	# adónde apunta la flecha (no hace falta buscarlo en cada fotograma)
	_buscar -= delta
	if _buscar <= 0.0:
		_buscar = 0.2
		var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
		# (la cosa misma, si es algo que se mueve, como la chispa o el castor: así la flecha la sigue al momento)
		_objetivo = Misiones.objetivo_aqui(maisha.global_position, true) if maisha and hay else null
	# los avisos esperan a que acabe la conversación
	if not _avisos.is_empty() and not oculto_por_menu() and not _hablando() and not Estado.cambiando:
		if _aviso_t <= 0.0:
			_aviso_t = 3.2
			Sonido.efecto(String(_avisos[0]["sonido"]))
		_aviso_t -= delta
		if _aviso_t <= 0.0:
			_avisos.pop_front()
	if not _esencias.is_empty() and not _hablando() and not oculto_por_menu():
		_esencias[0]["t"] += delta
		if _esencias[0]["t"] > 2.6:
			_esencias.pop_front()
	_lienzo.queue_redraw()


# --- Dibujo ---------------------------------------------------------------------------

func _texto(texto: String, pos: Vector2, color: Color) -> void:
	_lienzo.draw_string(_fuente, pos + Vector2(1, 1), texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(0, 0, 0, 0.6 * color.a))
	_lienzo.draw_string(_fuente, pos, texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, color)


func _ancho(texto: String) -> float:
	return _fuente.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x


## Parte un texto en líneas que quepan en «ancho»
func _lineas(texto: String, ancho: float) -> PackedStringArray:
	var salida := PackedStringArray()
	var linea := ""
	for palabra in texto.split(" "):
		var prueba := palabra if linea == "" else linea + " " + palabra
		if _ancho(prueba) > ancho and linea != "":
			salida.append(linea)
			linea = palabra
		else:
			linea = prueba
	if linea != "":
		salida.append(linea)
	return salida


func _dibujar() -> void:
	if _alfa > 0.01:
		_dibujar_panel()
		_dibujar_flecha()
	if oculto_por_menu():
		return
	if not _avisos.is_empty() and _aviso_t > 0.0:
		_dibujar_aviso(_avisos[0])
	if not _esencias.is_empty() and not _hablando():
		_dibujar_esencia(_esencias[0])


## «+2 Esencia · Zona purgada», arriba a la izquierda (debajo de la Vida)
func _dibujar_esencia(e: Dictionary) -> void:
	var t: float = e["t"]
	var a := clampf(minf(t / 0.25, (2.6 - t) / 0.5), 0.0, 1.0)
	var cristal: bool = e.get("cristal", false)
	var texto := ("+%d Cristal" + ("es" if int(e["n"]) != 1 else "")) % int(e["n"]) if cristal else "+%d Esencia" % int(e["n"])
	var motivo := String(e["motivo"])
	var ancho := _ancho(texto) + 24 + (_ancho(" · " + motivo) if motivo != "" else 0.0)
	var caja := Rect2(8 - (1.0 - a) * 10.0, 38, ancho + 8, 20)
	PIEL.caja(_lienzo, caja.grow(2), "cuero", 0.92 * a)
	var tinte := Color(0.6, 0.85, 1.0) if cristal else Color(0.75, 1.0, 0.55)
	var c := caja.position + Vector2(11, 10)
	for i in 3:
		_lienzo.draw_circle(c, 3.0 + i * 2.5, Color(tinte, 0.12 * a / (i + 1)))
	if cristal:
		_lienzo.draw_texture(CRISTAL, c - Vector2(4, 5), Color(1, 1, 1, a))
	else:
		_lienzo.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -5), c + Vector2(3.5, 0), c + Vector2(0, 5), c + Vector2(-3.5, 0)]), Color(tinte, a))
	_texto(texto, caja.position + Vector2(22, 15), Color(TEXTO, a))
	if motivo != "":
		_texto(" · " + motivo, caja.position + Vector2(22 + _ancho(texto), 15), Color(APAGADO, a))


func _dibujar_panel() -> void:
	var m := Misiones.seguida()
	if m.is_empty():
		return
	var a := _alfa
	var titulo := String(m["titulo"])
	var color_tipo: Color = COLOR_TIPO.get(m.get("tipo", ""), AMBAR)
	var lineas := _lineas("› " + _texto_paso, ANCHO_MAX - 16)
	var ancho := maxf(_ancho(titulo) + 26, 0.0)
	for l in lineas:
		ancho = maxf(ancho, _ancho(l) + 16)
	ancho = minf(ancho, ANCHO_MAX)
	var alto := 22.0 + lineas.size() * 15.0
	var caja := Rect2(640 - 8 - ancho, 8, ancho, alto)
	PIEL.caja(_lienzo, caja.grow(3), "cuero", 0.88 * a)
	if _destello > 0.0:
		_lienzo.draw_rect(caja.grow(1), Color(VERDE, _destello * a), false, 1.0)
	# rombo del tipo de misión
	var r := caja.position + Vector2(10, 11)
	_lienzo.draw_colored_polygon(PackedVector2Array([r + Vector2(0, -4), r + Vector2(4, 0), r + Vector2(0, 4), r + Vector2(-4, 0)]), Color(color_tipo, a))
	_texto(titulo, caja.position + Vector2(18, 16), Color(color_tipo, a))
	# el paso (se desliza un poco al cambiar)
	var desliz := (1.0 - _cambio) * 6.0
	for i in lineas.size():
		_texto(lineas[i], caja.position + Vector2(8 + desliz, 31 + i * 15), Color(TEXTO, a * _cambio))


func _dibujar_flecha() -> void:
	if _objetivo == null:
		return
	# la posición se lee en cada fotograma (si el objetivo se mueve, la flecha va con él)
	var donde: Vector2
	var altura := 26.0
	if _objetivo is Node2D:
		if not is_instance_valid(_objetivo) or not (_objetivo as Node2D).is_inside_tree():
			return
		donde = (_objetivo as Node2D).global_position
		var alto = (_objetivo as Node2D).get("altura_bocadillo")
		if alto != null:
			altura = float(alto) + 10.0
	elif _objetivo is Vector2:
		donde = _objetivo
	else:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var en_pantalla := _a_pantalla(donde)
	if maisha and (maisha.global_position.distance_to(donde) < 22.0):
		return
	var margen := Rect2(Vector2(14, 14), Vector2(640, 360) - Vector2(28, 28))
	var a := _alfa
	if margen.has_point(en_pantalla):
		# encima del sitio: una flechita que bota
		var p := en_pantalla + Vector2(0, -altura + sin(_tiempo * 4.0) * 2.0)
		_punta(p, Vector2.DOWN, a)
		return
	# fuera de la pantalla: en el borde, apuntando hacia allí
	var centro := Vector2(320, 180)
	var dir := (en_pantalla - centro).normalized()
	var t := INF
	if dir.x != 0.0:
		t = minf(t, ((margen.end.x if dir.x > 0 else margen.position.x) - centro.x) / dir.x)
	if dir.y != 0.0:
		t = minf(t, ((margen.end.y if dir.y > 0 else margen.position.y) - centro.y) / dir.y)
	var borde := centro + dir * t - dir * (2.0 + sin(_tiempo * 4.0) * 2.0)
	_punta(borde, dir, a)


## De posición del mundo a posición en la pantalla (según la cámara)
func _a_pantalla(p: Vector2) -> Vector2:
	var camara := get_viewport().get_camera_2d()
	if camara == null:
		return get_viewport().get_canvas_transform() * p
	return (p - camara.get_screen_center_position()) * camara.zoom + Vector2(320, 180)


## Una punta de flecha con borde oscuro
func _punta(p: Vector2, dir: Vector2, a: float) -> void:
	var lado := Vector2(-dir.y, dir.x)
	var punta := PackedVector2Array([p + dir * 8.0, p - dir * 4.0 + lado * 7.0, p - dir * 1.0, p - dir * 4.0 - lado * 7.0])
	_lienzo.draw_circle(p, 9.0 + sin(_tiempo * 5.0), Color(AMBAR, 0.12 * a))
	var sombra := PackedVector2Array()
	for q in punta:
		sombra.append(q + Vector2(1, 1))
	_lienzo.draw_colored_polygon(sombra, Color(0, 0, 0, 0.5 * a))
	var brillo := 0.8 + 0.2 * sin(_tiempo * 5.0)
	_lienzo.draw_colored_polygon(punta, Color(AMBAR.lightened(0.15 * brillo), a))
	_lienzo.draw_polyline(PackedVector2Array([punta[0], punta[1], punta[2], punta[3], punta[0]]), Color(0.2, 0.1, 0.05, 0.8 * a), 1.0)


func _dibujar_aviso(aviso: Dictionary) -> void:
	var t := 3.2 - _aviso_t
	var a := clampf(minf(t / 0.3, _aviso_t / 0.4), 0.0, 1.0)
	var titulo := String(aviso["titulo"])
	var texto := String(aviso["texto"])
	var color: Color = aviso["color"]
	var ancho := maxf(_ancho(titulo), _ancho(texto)) + 40
	var caja := Rect2(round((640 - ancho) / 2.0), 84 - (1.0 - a) * 8.0, ancho, 40)
	PIEL.caja(_lienzo, caja.grow(2), "cuero", a)
	_lienzo.draw_rect(Rect2(caja.position + Vector2(5, 5), caja.size - Vector2(10, 10)), Color(color, 0.35 * a), false, 1.0)
	# hojitas a los lados
	for s in [-1, 1]:
		var c := caja.get_center() + Vector2(s * (ancho / 2.0 - 12), 0)
		_lienzo.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -5), c + Vector2(4, 0), c + Vector2(0, 5), c + Vector2(-4, 0)]), Color(color, a))
	_texto(titulo, Vector2(round(caja.get_center().x - _ancho(titulo) / 2.0), caja.position.y + 16), Color(color, a))
	_texto(texto, Vector2(round(caja.get_center().x - _ancho(texto) / 2.0), caja.position.y + 33), Color(TEXTO, a))
