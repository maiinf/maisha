extends CanvasLayer
## LA MOCHILA (Tab, I o el botón Select del mando), como en Pokémon. El juego se para mientras está abierta.
##   Misiones     el diario: lo que está en marcha y lo cumplido (Acción elige cuál se sigue en pantalla)
##   Objetos      lo que lleva Maisha, con su descripción (y los objetos clave: el cetro, el mapa)
##   Habilidades  golpe, semilla, Latido y las mejoras conseguidas
##   Mapa         el mapa del mundo de Mzee Shamba (roto: falta el trozo de Sigilia)
##   Lazos        los aldeanos que Maisha conoce
## ← → cambian de pestaña · ↑ ↓ eligen · Tab o Esc cierran
##
## ACCIONES RÁPIDAS
##   1 Misiones · 2 Objetos · 3 Habilidades · 4 Mapa (también M) · 5 Lazos: abren la mochila en esa pestaña.
##   Rueda rápida: mantén pulsado Tab (o Select en el mando) y aparece una rueda con las 5 pestañas;
##   inclina hacia una (WASD, flechas o el stick) y suelta para abrirla. Si sueltas sin elegir, se cierra.

const FUENTE := preload("res://fuentes/pixelify_sans.woff")
const ICONOS := preload("res://arte/interfaz/objetos.png")
const MAPA := preload("res://arte/interfaz/mapa_mundo.png")
const MAPA_RAIZ := preload("res://arte/interfaz/mapa_raiz.png")
## El diario de cuero (herramientas/pintar_interfaz.py)
const PIEL := preload("res://scripts/interfaz/piel.gd")
const LIBRO := preload("res://arte/interfaz/diario/libro.png")
const TAPA := preload("res://arte/interfaz/diario/tapa.png")
const CINTAS := preload("res://arte/interfaz/diario/cintas.png")
const SELLO := preload("res://arte/interfaz/diario/sello.png")
const PAG_IZQ := Rect2(38, 48, 272, 282)
const PAG_DER := Rect2(332, 48, 270, 282)
const LOMO := 320.0
const ABRIR_DURA := 0.5
const PAGINA_DURA := 0.32
## EL MAPA DE RAÍZ (Maisha lo va dibujando al andar). Lugares: [nombre, posición en el dibujo, marca de haber estado]
## (las posiciones son las de herramientas/dibujar_mapa_raiz.py: si se cambia una, hay que cambiar la otra)
const LUGARES_RAIZ := [
	["Prados del Eco", Vector2(105, 182), "visto/prados_del_eco"],
	["Cuna de Musgo", Vector2(208, 140), "visto/cuna_de_musgo"],
	["Bosque Cobrizo", Vector2(118, 76), "visto/bosque_cobrizo"],
	["Campo Segado", Vector2(208, 40), "visto/campo_segado"],
	["Ciénaga Quieta", Vector2(322, 186), "visto/cienaga_quieta"],
	["Lago Espejo", Vector2(40, 110), "visto/lago_espejo"],
	["Gruta de las Raíces", Vector2(318, 64), "visto/gruta_raices"],
	["Embarcadero Junco", Vector2(388, 120), "visto/embarcadero_junco"],
	["Ruinas del Primer Árbol", Vector2(384, 30), "visto/ruinas_primer_arbol"],
]
## Los caminos entre los lugares: [nombre, escena, puntos del trazo]. Aparecen al pisarlos por primera vez.
const CAMINOS_RAIZ := [
	["Sendero del Puente", "sendero_del_puente", [Vector2(126, 178), Vector2(146, 172), Vector2(166, 162), Vector2(186, 148)]],
	["Camino Cobrizo", "camino_cobrizo", [Vector2(102, 160), Vector2(104, 130), Vector2(112, 104)]],
	["Las Pasarelas", "las_pasarelas", [Vector2(238, 150), Vector2(268, 166), Vector2(290, 178)]],
	["Senda de los Surcos", "senda_surcos", [Vector2(208, 118), Vector2(204, 90), Vector2(208, 62)]],
	["Orilla de Juncos", "orilla_juncos", [Vector2(350, 172), Vector2(370, 148), Vector2(382, 132)]],
	["Cañada del Eco", "canada_eco", [Vector2(74, 86), Vector2(62, 96)]],
	["Paso de Piedra", "paso_piedra", [Vector2(252, 42), Vector2(278, 50), Vector2(294, 58)]],
	["La Travesía", "la_travesia", [Vector2(378, 108), Vector2(356, 90), Vector2(336, 74)]],
	["Sendero Olvidado", "sendero_olvidado", [Vector2(338, 52), Vector2(358, 40), Vector2(370, 34)]],
]
## Dónde está Maisha en el mapa de Raíz según la escena (en un camino: en medio de su trazo)
const PUNTO_RAIZ := {"prados_del_eco": Vector2(110, 178), "bosque_cobrizo": Vector2(118, 72), "cuna_de_musgo": Vector2(208, 146),
	"claro_de_calma": Vector2(206, 142), "casa_pino": Vector2(200, 148), "taller_corteza": Vector2(214, 148), "kitovu": Vector2(53, 196),
	"casa_shamba": Vector2(53, 196), "cienaga_quieta": Vector2(322, 182), "campo_segado": Vector2(208, 44),
	"sendero_del_puente": Vector2(160, 166), "las_pasarelas": Vector2(268, 166),
	"camino_cobrizo": Vector2(104, 132), "senda_surcos": Vector2(205, 90),
	"canada_eco": Vector2(68, 91), "lago_espejo": Vector2(40, 110), "orilla_juncos": Vector2(370, 150), "embarcadero_junco": Vector2(388, 124), "la_travesia": Vector2(356, 90), "gruta_raices": Vector2(318, 64)}
const NIEBLA := Color("e2cea0")
const NIEBLA_SOMBRA := Color("c9b07e")
const TINTA := Color("5c3e26")
const PANEL := Color(0.08, 0.07, 0.10, 0.94)
const FILO := Color("d6b46e")
const TEXTO := Color("fff3c4")
const APAGADO := Color("c9b07e")
const AMBAR := Color("e6a852")
const VERDE := Color("6fcf4f")
const CAJA := Rect2(24, 22, 592, 316)
const PESTANAS := ["Misiones", "Objetos", "Habilidades", "Mapa", "Lazos"]
const ICONOS_PESTANA := preload("res://arte/interfaz/pestanas.png")
enum { P_MISIONES, P_OBJETOS, P_HABILIDADES, P_MAPA, P_LAZOS }
## Teclas de acceso directo a cada pestaña
const ATAJOS := {KEY_1: 0, KEY_2: 1, KEY_3: 2, KEY_4: 3, KEY_5: 4, KEY_M: 3}
## Cuánto hay que mantener Tab para que salga la rueda (segundos)
const ESPERA_RUEDA := 0.28
## Los colores de lo que se escribe en las páginas de noche (el cielo es oscuro: letras claras)
const TN_TINTA := Color("efe6cf")       # el texto
const TN_SUAVE := Color("c8c8e4")       # lo secundario
const TN_APAGADA := Color("7f86a8")     # lo cumplido, lo que no se puede
const TN_ROJO := Color("f2a07a")        # la historia, lo importante (coral)
const TN_VERDE := Color("a8e890")       # hecho
const TN_TITULO := Color("f0d89a")      # los títulos, en oro
const TN_ELEGIDA := Color("1a1410")     # la fila elegida, sobre la banda dorada
const ORO_CLARO := Color("f9d77a")
const COLOR_TIPO := {"historia": Color("f2a07a"), "encargo": Color("7fd8d0"), "secreto": Color("c8a0f0"), "lazo": Color("f0a0c0")}
const FILAS_VISIBLES := 9
const ALTO_FILA := 24

## EL ÁRBOL DE HABILIDADES (pestaña Habilidades): las ramas, de izquierda a derecha, y dónde está cada nodo en el
## libro (las mismas posiciones que RAMAS en herramientas/pintar_interfaz.py, que pinta las ramas)
const ARBOL_RAMAS := preload("res://arte/interfaz/diario/arbol_ramas.png")
const NODOS_ICONOS := preload("res://arte/interfaz/diario/nodos.png")
const RAMAS_ARBOL := ["raiz", "cetro", "aliento"]
const NODOS_ARBOL := {
	"raiz": [Vector2(262, 236), Vector2(220, 222), Vector2(182, 204), Vector2(150, 180), Vector2(124, 152), Vector2(104, 120), Vector2(92, 84)],
	"cetro": [Vector2(320, 214), Vector2(320, 186), Vector2(320, 160), Vector2(320, 134), Vector2(320, 108), Vector2(320, 84), Vector2(320, 60)],
	"aliento": [Vector2(378, 236), Vector2(420, 222), Vector2(458, 204), Vector2(490, 180), Vector2(516, 152), Vector2(536, 120), Vector2(548, 84)],
}
const COLOR_RAMA := {"raiz": Color("8fe06a"), "cetro": Color("f9c46a"), "aliento": Color("8fd8f0")}
const NOMBRE_RAMA := {"raiz": "RAÍZ", "cetro": "CETRO", "aliento": "ALIENTO"}
const ICONO_RAMA := {"raiz": 0, "cetro": 1, "aliento": 2}
## la habilidad básica de cada rama (la raíz de la rama): índice en HABILIDADES
const BASICA_RAMA := {"raiz": 1, "cetro": 0, "aliento": 2}
const MANTENER := 0.8            # segundos manteniendo Acción para despertar un nodo
## Objetos clave: marca -> [nombre, icono, descripción]
const CLAVE := {
	"cetro_recibido": ["Cetro de Raíz", 4, "El cetro de la familia de Mzee Shamba. Despierta en manos de quien trae la vida de vuelta."],
	"mapa_partido": ["Mapa partido", 3, "Un mapa de todas las tierras. Le falta el trozo del norte: Mzee Shamba cree que está en Sigilia."],
	"hoja_mauti": ["Hoja de Mauti", 24, "Una hoja seca de cobre, todavía tibia. Mauti la dejó bajo una piedra de la isla del río, para Maisha: «Si subes a buscarme, tráemela»."],
	"cuaderno_ecos": ["Cuaderno de ecos", 18, "El regalo de Msafiri. Cada eco perdido que escuchas queda apuntado aquí. Juntos cuentan qué le pasó al Primer Árbol."],
	"mapa_raiz": ["Mapa de Tawi", 3, "Tawi lo dibujó volando por encima de Raíz: en tu mapa ya se ven todos los lugares (los caminos hay que andarlos)."],
}
## Habilidades: [nombre, tecla, marca que la desbloquea, descripción]
const HABILIDADES := [
	["Golpe con el cetro", "J", "cetro_recibido", "Gratis. Aparta y daña a los enemigos, y te devuelve un poco de Aliento."],
	["Semilla", "K", "cetro_recibido", "Gasta Aliento. Estalla en cruz al poco rato: rompe Corazones de Giza, matorrales y rocas. ¡Apártate de la cruz!"],
	["Latido", "L", "cetro_recibido", "Gasta Aliento. Empuja a todo lo que esté cerca y te protege un instante."],
	["Cetro templado", "", "cetro_templado", "Corteza templó el cetro en su forja: el golpe llega más lejos."],
	["Torre del vigía", "", "vigia", "Desde el tejado de Pino, los secretos de los prados se ven desde lejos."],
	["Tomar sopa", "F", "receta_sopa", "Si llevas sopa de Juncia, devuelve 3 hojas de vida al momento, también en plena pelea."],
]
## Lazos: [id, nombre, marca para conocerle, descripción]
const LAZOS := [
	["shamba", "Mzee Shamba", "shamba_conocido", "Castor anciano y agricultor del Kitovu. Su familia guardaba el Cetro de Raíz."],
	["bibi", "Bibi Musgo", "bibi_conocida", "Guardiana del Gran Árbol de Cuna de Musgo. Hay recuerdos suyos que no encuentra."],
	["pino", "Pino", "rescatado_pino", "Niño-seta y vigía de Cuna de Musgo. Quiere ser explorador."],
	["corteza", "Corteza", "rescatado_corteza", "Herrera de Cuna de Musgo. Gruñona y orgullosa, pero de buen corazón."],
	["kasia", "Kasia", "kasia_conocida", "Nutria barquera de la Orilla de Juncos. Habla sin parar y rema sin cansarse."],
	["mdiria", "Mdiria", "mdiria_conocido", "Martín pescador viejo del Lago Espejo. Hizo el embarcadero (casi todo)."],
	["bata", "Bata", "bata_conocido", "El pato barquero del Embarcadero Junco. Llevaba el transbordador río arriba, hasta la Gruta de las Raíces."],
	["mbuzi", "Mbuzi", "mbuzi_conocida", "Cabra montés pastora de la Cañada del Eco. Habla despacio y escucha todavía más despacio."],
	["sungura", "Sungura", "sungura_conocida", "Liebre guardasemillas de la Senda de los Surcos. Habla deprisa, siembra despacio."],
	["fuko", "Fuko", "fuko_conocido", "Topo minero del Camino Cobrizo. No ve más allá de sus gafas, pero oye crecer las raíces."],
	["korongo", "Korongo", "korongo_conocida", "Garza pescadora de Las Pasarelas. Paciente con los peces, no tanto con las ranas."],
	["msafiri", "Msafiri", "msafiri_conocido", "Pangolín viajero y cronista. Va de mundo en mundo apuntando historias en su diario."],
	["tawi", "Tawi", "rescatado_tawi", "Pájaro mercader, charlatán y siempre de paso. Trae noticias de otros mundos."],
	["juncia", "Juncia", "rescatado_juncia", "Rana cocinera de la Ciénaga Quieta. Canta mientras remueve la olla y nunca mide nada."],
]

var abierta := false
var pestana := 0
var seleccion := 0
var _rama := 1                   # árbol de habilidades: la rama elegida (0 Raíz, 1 Cetro, 2 Aliento)
var _nodo := 0                   # y el nodo de esa rama (0 = la habilidad básica)
var _mantenido := 0.0            # cuánto se lleva manteniendo Acción sobre el nodo
var _soltar := false             # tras despertar un nodo, hay que soltar Acción antes de otro
var _destello_nodo := 0.0
var _lienzo: Control
var _fuente: FontFile
var _tiempo := 0.0
var _abierta_en := -1
var _retratos := {}
var _desplazamiento := 0          # primera fila que se ve (si hay más de las que caben)
## Rueda rápida
var rueda := false
var _pulsada := 0.0               # cuánto tiempo lleva pulsado Tab desde que se abrió
var _eleccion_rueda := -1
var _rueda_alfa := 0.0
var _mapa_mundo := false          # en la pestaña Mapa: false = el de Raíz (si se tiene), true = el del mundo
## Animaciones del diario
var _abre := 0.0                  # 0 = cerrado, 1 = abierto del todo
var _cerrando := false
var _pagina := 1.0                # pasar la página al cambiar de pestaña (0 → 1)
var _sentido := 1                 # hacia dónde se pasa (1 = adelante)
var _sel_y := -1.0                # el subrayado de lo elegido se desliza hasta su fila


func _ready() -> void:
	add_to_group("mochila")
	layer = 29
	process_mode = Node.PROCESS_MODE_ALWAYS
	_fuente = FUENTE
	_fuente.antialiasing = TextServer.FONT_ANTIALIASING_NONE
	_fuente.hinting = TextServer.HINTING_NONE
	_lienzo = Control.new()
	_lienzo.set_anchors_preset(Control.PRESET_FULL_RECT)
	_lienzo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_lienzo.draw.connect(_dibujar)
	add_child(_lienzo)
	visible = false


## Atajos: 1-5 (y M) abren la mochila directamente en una pestaña
func _unhandled_input(evento: InputEvent) -> void:
	if not (evento is InputEventKey) or not evento.pressed or evento.echo:
		return
	var tecla: int = (evento as InputEventKey).physical_keycode
	if not ATAJOS.has(tecla):
		return
	var cual: int = ATAJOS[tecla]
	if abierta and not rueda:
		if pestana == cual:
			cerrar()
		else:
			_ir_a_pestana(cual)
		get_viewport().set_input_as_handled()
	elif not abierta and _se_puede_abrir():
		abrir(cual)
		get_viewport().set_input_as_handled()


func _process(delta: float) -> void:
	_tiempo += delta
	_rueda_alfa = move_toward(_rueda_alfa, 1.0 if rueda else 0.0, delta * 8.0)
	_pagina = minf(1.0, _pagina + delta / PAGINA_DURA)
	if _cerrando:
		_abre = maxf(0.0, _abre - delta / (ABRIR_DURA * 0.6))
		_lienzo.queue_redraw()
		if _abre <= 0.0:
			_cerrando = false
			visible = false
	elif abierta:
		_abre = minf(1.0, _abre + delta / ABRIR_DURA)
	if not abierta:
		if Input.is_action_just_pressed("mochila") and _se_puede_abrir():
			abrir()
			_pulsada = 0.0001
		return
	_lienzo.queue_redraw()
	if Engine.get_process_frames() == _abierta_en:
		return
	# la rueda rápida: mientras se mantiene Tab
	if _pulsada > 0.0:
		if Input.is_action_pressed("mochila"):
			_pulsada += delta
			if _pulsada >= ESPERA_RUEDA and not rueda:
				rueda = true
				_eleccion_rueda = -1
				Sonido.efecto("rueda_abrir")
		else:
			_pulsada = 0.0
			if rueda:
				_soltar_rueda()
			return
	if rueda:
		_mover_rueda()
		return
	if Input.is_action_just_pressed("mochila") or Input.is_action_just_pressed("menu"):
		cerrar()
		return
	if pestana == P_HABILIDADES:
		_mover_arbol(delta)
		return
	if Input.is_action_just_pressed("mover_derecha") or Input.is_action_just_pressed("ui_right"):
		_ir_a_pestana((pestana + 1) % PESTANAS.size())
	elif Input.is_action_just_pressed("mover_izquierda") or Input.is_action_just_pressed("ui_left"):
		_ir_a_pestana((pestana - 1 + PESTANAS.size()) % PESTANAS.size())
	if pestana == P_MAPA and _raiz_conocida():
		if Input.is_action_just_pressed("mover_abajo") or Input.is_action_just_pressed("ui_down") \
				or Input.is_action_just_pressed("mover_arriba") or Input.is_action_just_pressed("ui_up"):
			_mapa_mundo = not _mapa_mundo
			Sonido.efecto("menu_mover")
	var n := _lista().size()
	if n > 0:
		if Input.is_action_just_pressed("mover_abajo") or Input.is_action_just_pressed("ui_down"):
			seleccion = (seleccion + 1) % n
			Sonido.efecto("menu_mover")
		elif Input.is_action_just_pressed("mover_arriba") or Input.is_action_just_pressed("ui_up"):
			seleccion = (seleccion - 1 + n) % n
			Sonido.efecto("menu_mover")
		if pestana == P_MISIONES and Input.is_action_just_pressed("accion"):
			_seguir_elegida()
		elif pestana == P_OBJETOS and Input.is_action_just_pressed("accion"):
			_usar_elegido()


func _ir_a_pestana(cual: int) -> void:
	if cual != pestana:
		Sonido.efecto("pagina")
		_sentido = 1 if cual > pestana else -1
		_pagina = 0.0
		_sel_y = -1.0
	pestana = cual
	seleccion = 0
	_desplazamiento = 0


## En Objetos: Acción usa el objeto elegido si se puede usar (la sopa) o se pone / quita una prenda
func _usar_elegido() -> void:
	var filas := _lista()
	if seleccion < filas.size() and filas[seleccion].has("prenda"):
		var id := String(filas[seleccion]["prenda"])
		Tienda.poner_prenda(id, not Tienda.lleva(id))
		Sonido.efecto("menu_aceptar")
		return
	if seleccion >= filas.size() or String(filas[seleccion].get("objeto", "")) != "sopa":
		return
	var maisha := get_tree().get_first_node_in_group("maisha")
	if maisha and maisha.tomar_sopa():
		seleccion = mini(seleccion, maxi(0, _lista().size() - 1))
	else:
		Sonido.efecto("menu_mover")


## En el diario: Acción hace que la misión elegida sea la que se ve en pantalla
func _seguir_elegida() -> void:
	var filas := _lista()
	if seleccion >= filas.size():
		return
	var f: Dictionary = filas[seleccion]
	if f.get("hecha", true):
		Sonido.efecto("menu_atras")
		return
	Misiones.seguir(String(f["id"]))
	Sonido.efecto("menu_aceptar")


func _se_puede_abrir() -> bool:
	if Estado.cambiando or get_tree().paused or not Estado.jugando:
		return false
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	return not (dialogo and dialogo.hablando)


func abrir(cual := -1) -> void:
	abierta = true
	visible = true
	rueda = false
	_pulsada = 0.0
	if cual >= 0:
		pestana = cual
	seleccion = 0
	_desplazamiento = 0
	# en el diario, empieza por la misión que se está siguiendo
	if pestana == P_MISIONES:
		var seguida := Misiones.seguida()
		var filas := _lista()
		for i in filas.size():
			if not seguida.is_empty() and filas[i].get("id", "") == seguida["id"]:
				seleccion = i
	get_tree().paused = true
	_abierta_en = Engine.get_process_frames()
	_redibujar_hud()
	if not _cerrando and _abre <= 0.0:
		_abre = 0.0
	_cerrando = false
	_sel_y = -1.0
	_pagina = 1.0
	Sonido.efecto("libro_abrir")


## El HUD está parado mientras la mochila está abierta: se le pide que se redibuje (sin la ayuda de controles)
func _redibujar_hud() -> void:
	var hud := get_tree().get_first_node_in_group("hud")
	if hud and hud.get("_lienzo"):
		hud.get("_lienzo").queue_redraw()


func cerrar() -> void:
	if abierta:
		Sonido.efecto("libro_cerrar")
		_cerrando = not rueda and _abre > 0.0
	abierta = false
	visible = _cerrando
	rueda = false
	_pulsada = 0.0
	get_tree().paused = false
	# para que la misma pulsación de Esc no abra también la pausa
	get_tree().set_meta("menu_cerrado_en", Engine.get_process_frames())


# --- Rueda rápida ----------------------------------------------------------------------

## Ángulo (en la pantalla) de cada pestaña en la rueda: Misiones arriba y el resto en el sentido del reloj
func _angulo_rueda(i: int) -> float:
	return -PI / 2.0 + TAU * i / PESTANAS.size()


func _mover_rueda() -> void:
	var dir := Input.get_vector("mover_izquierda", "mover_derecha", "mover_arriba", "mover_abajo", 0.35)
	if dir.length() < 0.35:
		return
	var angulo := dir.angle()
	var mejor := -1
	var menor := INF
	for i in PESTANAS.size():
		var d := absf(angle_difference(angulo, _angulo_rueda(i)))
		if d < menor:
			menor = d
			mejor = i
	if mejor != _eleccion_rueda:
		_eleccion_rueda = mejor
		Sonido.efecto("menu_mover")


func _soltar_rueda() -> void:
	rueda = false
	if _eleccion_rueda < 0:
		cerrar()
		return
	_ir_a_pestana(_eleccion_rueda)
	abrir(_eleccion_rueda)


# --- Contenido de cada pestaña -----------------------------------------------------------

## Las filas de la pestaña actual: cada una {nombre, icono, cantidad, texto, apagada}
func _lista() -> Array:
	var filas := []
	match pestana:
		P_MISIONES:
			for m in Misiones.activas():
				filas.append({"id": m["id"], "nombre": m["titulo"], "tipo": m.get("tipo", ""), "hecha": false, "mision": m})
			for m in Misiones.hechas():
				filas.append({"id": m["id"], "nombre": m["titulo"], "tipo": m.get("tipo", ""), "hecha": true, "mision": m, "apagada": true})
		P_OBJETOS:
			for m in CLAVE:
				if Estado.tiene(m):
					filas.append({"nombre": CLAVE[m][0], "icono": CLAVE[m][1], "texto": CLAVE[m][2], "clave": true})
			if Tienda.cristales_ganados_total() > 0:
				filas.append({"nombre": "Cristales del Nexo", "icono": 16, "cantidad": Tienda.cristales(),
					"texto": "Trocitos del Nexo roto. Tawi los acepta en su puesto. Se ganan cumpliendo misiones, venciendo a los guardianes y encontrando secretos."})
			for a in Tienda.prendas_compradas():
				var puesta := Tienda.lleva(String(a["id"]))
				filas.append({"nombre": String(a["nombre"]), "icono": int(a["icono"]), "tecla": "puesta" if puesta else "",
					"texto": String(a["texto"]).get_slice(".", 0) + ". " + ("Acción: quitártela." if puesta else "Acción: ponértela."),
					"prenda": String(a["id"])})
			for o in Estado.OBJETOS:
				var n := Estado.cuantos(o)
				if n > 0:
					var d: Dictionary = Estado.OBJETOS[o]
					filas.append({"nombre": d["uno"], "icono": int(d["icono"]), "cantidad": n, "texto": d["texto"], "objeto": o})
		P_HABILIDADES:
			for h in HABILIDADES:
				var tiene := Estado.tiene(h[2])
				if not tiene and h[1] == "":
					continue           # las mejoras no se ven hasta conseguirlas
				filas.append({"nombre": h[0] if tiene else "???", "tecla": h[1] if tiene else "",
					"texto": h[3] if tiene else "Aún no sabes hacer esto.", "apagada": not tiene})
			# las Artes del Árbol de la Vida (desde que Bibi enseña a meditar)
			if Estado.tiene("bibi_meditar"):
				for arte in Artes.lista:
					var id := String(arte["id"])
					if arte.has("bloqueada"):
						continue
					var n := Artes.nivel(id)
					var texto := String(arte["texto"])
					var despiertos: Array = arte["niveles"].slice(0, n).map(func(d: Dictionary) -> String: return d["nombre"])
					texto += " Despierto: " + (", ".join(despiertos) if not despiertos.is_empty() else "nada aún") + "."
					texto += " Esencia para gastar: %d (se gasta meditando en el Claro de Calma)." % Artes.esencia()
					filas.append({"nombre": arte["nombre"], "tecla": "%d/%d" % [n, Artes.nivel_maximo(id)], "texto": texto, "arte": id})
		P_LAZOS:
			for z in LAZOS:
				if Estado.tiene(z[2]):
					filas.append({"nombre": z[1], "retrato": z[0], "texto": z[3]})
	return filas


# --- Dibujo -----------------------------------------------------------------------------

func _texto(texto: String, pos: Vector2, color: Color, ancho := -1.0, tam := 16) -> void:
	# sobre el papel, la tinta no lleva sombra negra (solo un poco de brillo); lo claro, sí
	if color.get_luminance() > 0.5:
		_lienzo.draw_string(_fuente, pos + Vector2(1, 1), texto, HORIZONTAL_ALIGNMENT_LEFT, ancho, tam, Color(0, 0, 0, 0.6 * color.a))
	_lienzo.draw_string(_fuente, pos, texto, HORIZONTAL_ALIGNMENT_LEFT, ancho, tam, color)


## Un título a mano, grande, con su raya debajo
func _titulo(texto: String, pos: Vector2, color: Color, ancho_raya := 0.0) -> void:
	_texto(texto, pos, color, -1.0, 32)
	var ancho := ancho_raya if ancho_raya > 0.0 else _fuente.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 32).x
	PIEL.raya(_lienzo, pos + Vector2(0, 6), pos + Vector2(ancho, 5), color, 0.5)


func _ancho(texto: String) -> float:
	return _fuente.get_string_size(texto, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x


## Texto en varias líneas dentro de un ancho. Devuelve la y de debajo de la última línea.
func _parrafo(texto: String, pos: Vector2, ancho: float, color: Color, interlineado := 17.0) -> float:
	var linea := ""
	var y := pos.y
	for palabra in texto.split(" "):
		var prueba := palabra if linea == "" else linea + " " + palabra
		if _ancho(prueba) > ancho and linea != "":
			_texto(linea, Vector2(pos.x, y), color)
			y += interlineado
			linea = palabra
		else:
			linea = prueba
	if linea != "":
		_texto(linea, Vector2(pos.x, y), color)
		y += interlineado
	return y


func _icono(indice: int, pos: Vector2, escala := 1.0) -> void:
	_lienzo.draw_texture_rect_region(ICONOS, Rect2(pos, Vector2(16, 16) * escala), Rect2(indice * 16, 0, 16, 16))


func _icono_pestana(indice: int, pos: Vector2, escala := 1.0, mod := Color.WHITE) -> void:
	_lienzo.draw_texture_rect_region(ICONOS_PESTANA, Rect2(pos, Vector2(16, 16) * escala), Rect2(indice * 16, 0, 16, 16), mod)


## Una marca de «hecho» (✓) dibujada, que la letra no la tiene
func _palomita(c: Vector2, color: Color) -> void:
	var puntos := PackedVector2Array([c + Vector2(-4, 0), c + Vector2(-1, 3), c + Vector2(4, -3)])
	_lienzo.draw_polyline(puntos, Color(0, 0, 0, 0.5 * color.a), 3.0)
	_lienzo.draw_polyline(puntos, color, 2.0)


func _rombo(c: Vector2, r: float, color: Color) -> void:
	_lienzo.draw_colored_polygon(PackedVector2Array([c + Vector2(0, -r), c + Vector2(r, 0), c + Vector2(0, r), c + Vector2(-r, 0)]), color)


## En el detalle: su retrato grande si lo tiene; si no, su dibujo a doble tamaño
func _retrato(id: String, pos: Vector2, escala := 1.0) -> void:
	var grande := "res://arte/retratos/%s.png" % id
	if ResourceLoader.exists(grande):
		_lienzo.draw_texture(load(grande), pos - Vector2(8, 0))
		return
	var t := _cargar_retrato(id)
	_lienzo.draw_texture_rect(t, Rect2(pos, t.get_size() * escala), false)


func _ease(t: float) -> float:
	return 1.0 - pow(1.0 - clampf(t, 0.0, 1.0), 3.0)


func _dibujar() -> void:
	if rueda or _rueda_alfa > 0.01:
		_dibujar_rueda()
		if rueda:
			return
	var a := _abre
	_lienzo.draw_rect(Rect2(0, 0, 640, 360), Color(0.03, 0.02, 0.05, 0.55 * _ease(a * 2.0)))
	# el libro sube desde abajo mientras se abre
	var baja := (1.0 - _ease(a / 0.45)) * 50.0
	_lienzo.draw_set_transform(Vector2(0, round(baja)))
	var giro := clampf((a - 0.3) / 0.7, 0.0, 1.0)         # la tapa: 0 = cerrada, 1 = abierta del todo
	giro = giro * giro * (3.0 - 2.0 * giro)
	if giro < 0.5:
		# cerrado: solo se ve la mitad derecha (la tapa), que se va levantando hacia el lomo
		_lienzo.draw_texture_rect_region(LIBRO, Rect2(LOMO, 0, 320, 360), Rect2(LOMO, 0, 320, 360))
		var w := (1.0 - giro * 2.0) * TAPA.get_width()
		if w > 1.0:
			_lienzo.draw_texture_rect(TAPA, Rect2(LOMO + 2, 30, w, TAPA.get_height()), false, Color(1, 1, 1).darkened(giro * 0.8))
	else:
		# la tapa ya ha pasado al otro lado: se ve la página de la izquierda, que se despliega desde el lomo
		var w := (giro - 0.5) * 2.0 * LOMO
		_lienzo.draw_texture_rect_region(LIBRO, Rect2(LOMO, 0, 320, 360), Rect2(LOMO, 0, 320, 360))
		_lienzo.draw_texture_rect_region(LIBRO, Rect2(LOMO - w, 0, w, 360), Rect2(0, 0, LOMO, 360), Color(1, 1, 1).darkened((1.0 - giro) * 0.9))
	_dibujar_cintas(giro)
	var tinta := clampf((a - 0.8) / 0.2, 0.0, 1.0)
	if tinta > 0.0 and not _cerrando or (_cerrando and a > 0.85):
		_dibujar_paginas(tinta if not _cerrando else 1.0)
	_dibujar_hoja_que_pasa()
	_lienzo.draw_set_transform(Vector2.ZERO)


## Las cintas de marcapáginas (las pestañas): asoman por arriba del libro; la elegida, más alta
func _dibujar_cintas(giro: float) -> void:
	for i in PESTANAS.size():
		var x := 44.0 + i * 114.0
		if giro < 0.5 and x < LOMO:
			continue                      # con el libro cerrado, solo asoman las de la mitad derecha
		var activa := i == pestana
		var y := 0.0 if activa else 8.0
		# cuelgan por encima del canto del libro hasta el borde de la página (y = 40)
		var alto := 40.0 - y
		_lienzo.draw_texture_rect_region(CINTAS, Rect2(x, y, 100, alto), Rect2(i * 100, 0, 100, alto))
		_lienzo.draw_rect(Rect2(x + 2, 40, 96, 2), Color(0, 0, 0, 0.25))
		var icono := Vector2(x + 8, y + 12)
		_icono_pestana(i, icono, 1.0, Color(1, 1, 1, 1.0 if activa else 0.8))
		if activa:
			_texto(PESTANAS[i], Vector2(x + 28, y + 24), PIEL.CREMA)
		else:
			_texto(str(i + 1), Vector2(x + 28, y + 24), Color(PIEL.CREMA, 0.75))


## La hoja que se pasa al cambiar de pestaña: se levanta de una página, se estrecha hacia el lomo y cae en la otra
func _dibujar_hoja_que_pasa() -> void:
	if _pagina >= 1.0:
		return
	var k := _pagina
	var desde_der := _sentido > 0
	if k < 0.5:
		var w := (1.0 - k * 2.0) * 280.0
		var x := LOMO if desde_der else LOMO - w
		var origen := Rect2(LOMO, 0, 280, 360) if desde_der else Rect2(LOMO - 280, 0, 280, 360)
		_lienzo.draw_texture_rect_region(LIBRO, Rect2(x, 40, w, 298), Rect2(origen.position + Vector2(0, 40), Vector2(280, 298)),
			Color(1, 1, 1).darkened(k * 0.6))
	else:
		var w := (k - 0.5) * 2.0 * 280.0
		var x := LOMO - w if desde_der else LOMO
		var alfa := 1.0 - clampf((k - 0.75) / 0.25, 0.0, 1.0)
		var origen := Rect2(LOMO - 280, 40, 280, 298) if desde_der else Rect2(LOMO, 40, 280, 298)
		_lienzo.draw_texture_rect_region(LIBRO, Rect2(x, 40, w, 298), origen, Color(1, 1, 1, alfa).darkened((1.0 - k) * 0.6))
	# la sombra que echa la hoja sobre el lomo
	_lienzo.draw_rect(Rect2(LOMO - 6, 42, 12, 294), Color(0, 0, 0, 0.12 * sin(k * PI)))


## Lo que hay escrito en las dos páginas
func _dibujar_paginas(tinta: float) -> void:
	var ayuda := "← → pestañas · ↑ ↓ elegir · Tab cerrar"
	if pestana == P_MISIONES:
		ayuda = "↑ ↓ elegir · Acción: seguir · Tab cerrar"
	elif pestana == P_OBJETOS and (Estado.cuantos("sopa") > 0 or not Tienda.prendas_compradas().is_empty()):
		ayuda = "↑ ↓ elegir · Acción: usar o ponerse"
	if pestana == P_MAPA:
		_dibujar_mapa()
		return
	if pestana == P_HABILIDADES:
		_dibujar_arbol(tinta)
		return
	_titulo(PESTANAS[pestana], PAG_IZQ.position + Vector2(6, 28), Color(TN_TITULO, tinta), 0.0)
	_texto(ayuda, Vector2(PAG_DER.position.x + 16, PAG_DER.end.y - 14), Color(TN_APAGADA, 0.9 * tinta))
	var filas := _lista()
	var area := Rect2(PAG_IZQ.position + Vector2(6, 42), Vector2(PAG_IZQ.size.x - 12, FILAS_VISIBLES * ALTO_FILA))
	if filas.is_empty():
		var vacio: String = {P_MISIONES: "No hay nada apuntado en el diario.", P_OBJETOS: "La mochila está vacía.",
			P_LAZOS: "Aún no conoces a nadie."}.get(pestana, "")
		_texto(vacio, area.position + Vector2(4, 16), Color(TN_APAGADA, tinta))
		return
	seleccion = clampi(seleccion, 0, filas.size() - 1)
	# si hay más filas de las que caben, la lista se desplaza para que se vea la elegida
	if seleccion < _desplazamiento:
		_desplazamiento = seleccion
	elif seleccion >= _desplazamiento + FILAS_VISIBLES:
		_desplazamiento = seleccion - FILAS_VISIBLES + 1
	var seguida := Misiones.seguida_id() if pestana == P_MISIONES else ""
	if pestana == P_MISIONES and seguida == "" and not Misiones.seguida().is_empty():
		seguida = Misiones.seguida()["id"]
	# el subrayado de lo elegido, que se desliza hasta su fila
	var y_obj := area.position.y + (seleccion - _desplazamiento) * ALTO_FILA
	_sel_y = y_obj if _sel_y < 0.0 else lerpf(_sel_y, y_obj, minf(1.0, get_process_delta_time() * 18.0))
	PIEL.subrayar(_lienzo, Rect2(area.position.x + 10, _sel_y + 2, area.size.x - 10, ALTO_FILA - 3), _tiempo, tinta)
	PIEL.marcapaginas(_lienzo, Vector2(area.position.x + 6, _sel_y + ALTO_FILA / 2.0), tinta)
	var hechas_desde := -1
	for i in range(_desplazamiento, mini(filas.size(), _desplazamiento + FILAS_VISIBLES)):
		var f: Dictionary = filas[i]
		var y := area.position.y + (i - _desplazamiento) * ALTO_FILA
		var elegida := i == seleccion
		if f.get("hecha", false) and hechas_desde < 0:
			hechas_desde = i
			if i > _desplazamiento:
				PIEL.raya(_lienzo, Vector2(area.position.x + 14, y), Vector2(area.end.x - 6, y), TN_APAGADA, 0.5 * tinta)
		var color := TN_TINTA
		if f.get("apagada", false):
			color = TN_APAGADA
		if elegida:
			color = TN_ELEGIDA
		color.a *= tinta
		var tx := area.position.x + 16
		if f.has("tipo"):
			var ct: Color = COLOR_TIPO.get(f["tipo"], TN_TINTA)
			if f.get("hecha", false):
				_palomita(Vector2(tx + 4, y + 12), Color(TN_VERDE, 0.8 * tinta))
			elif f["tipo"] == "historia":
				_lienzo.draw_texture_rect(SELLO, Rect2(tx - 2, y + 5, 13, 13), false, Color(1, 1, 1, tinta))
			else:
				_rombo(Vector2(tx + 4, y + 12), 4.0, Color(ct, tinta))
			tx += 14
		if f.has("icono"):
			_icono(f["icono"], Vector2(tx, y + 4))
			tx += 22
		if f.has("retrato"):
			var t := _cargar_retrato(f["retrato"])
			var ancho_t := t.get_width()
			_lienzo.draw_texture_rect_region(t, Rect2(tx - 2, y, 18, 24), Rect2(ancho_t / 2 - 9, 2 + (t.get_height() - 32), 18, 24))
			tx += 22
		var nombre := String(f["nombre"])
		_texto(nombre, Vector2(tx, y + 17), color)
		if f.get("hecha", false):
			PIEL.raya(_lienzo, Vector2(tx, y + 12), Vector2(tx + _ancho(nombre), y + 12), TN_APAGADA, 0.8 * tinta)
		if f.has("cantidad"):
			_texto("x%d" % f["cantidad"], Vector2(area.end.x - 30, y + 17), Color(TN_SUAVE, tinta))
		if f.get("clave", false):
			_texto("clave", Vector2(area.end.x - 40, y + 17), Color(TN_ROJO, 0.85 * tinta))
		if f.get("tecla", "") != "":
			# la tecla, en una etiqueta de cuero
			var tecla := String(f["tecla"])
			var r := Rect2(area.end.x - 14 - _ancho(tecla), y + 3, _ancho(tecla) + 10, 18)
			PIEL.caja(_lienzo, r, "cuero", tinta, false)
			_texto(tecla, r.position + Vector2(5, 14), Color(PIEL.CREMA, tinta))
		if f.get("id", "") == seguida and seguida != "" and not f.get("hecha", false):
			# la que se sigue en pantalla: una flechita roja que late
			var c := Vector2(area.end.x - 8 + sin(_tiempo * 4.0), y + 12)
			_lienzo.draw_colored_polygon(PackedVector2Array([c + Vector2(-5, -4), c + Vector2(3, 0), c + Vector2(-5, 4)]), Color(TN_ROJO, tinta))
	# flechas de que hay más arriba o abajo
	if _desplazamiento > 0:
		var c := Vector2(area.get_center().x, area.position.y - 4)
		_lienzo.draw_colored_polygon(PackedVector2Array([c + Vector2(-4, 2), c + Vector2(0, -2), c + Vector2(4, 2)]), Color(TN_SUAVE, tinta))
	if _desplazamiento + FILAS_VISIBLES < filas.size():
		var c := Vector2(area.get_center().x, area.position.y + FILAS_VISIBLES * ALTO_FILA + 3)
		_lienzo.draw_colored_polygon(PackedVector2Array([c + Vector2(-4, -2), c + Vector2(0, 2), c + Vector2(4, -2)]), Color(TN_SUAVE, tinta))
	# el detalle de lo elegido, en la página de la derecha
	var f: Dictionary = filas[seleccion]
	var detalle := Rect2(PAG_DER.position + Vector2(4, 4), PAG_DER.size - Vector2(8, 26))
	if f.has("mision"):
		_detalle_mision(f["mision"], detalle, f.get("id", "") == seguida)
		return
	var dy := detalle.position.y + 8
	if f.has("icono"):
		# el dibujo, pegado en la página con cuatro esquinitas de papel
		var r := Rect2(detalle.get_center().x - 30, dy, 60, 60)
		_lienzo.draw_rect(r, Color("efe0bc"))
		_lienzo.draw_rect(r, Color(TN_APAGADA, 0.5), false, 1.0)
		_icono(f["icono"], r.position + Vector2(6, 6), 3.0)
		_esquinas_foto(r)
		dy += 72
	elif f.has("retrato"):
		_retrato_pegado(f["retrato"], Vector2(detalle.get_center().x - 26, dy))
		dy += 86
	_texto(String(f["nombre"]), Vector2(detalle.position.x + 10, dy + 14), TN_TITULO, -1, 16)
	PIEL.raya(_lienzo, Vector2(detalle.position.x + 10, dy + 19), Vector2(detalle.position.x + 10 + _ancho(String(f["nombre"])), dy + 19), TN_TITULO, 0.5)
	_parrafo(String(f["texto"]), Vector2(detalle.position.x + 10, dy + 36), detalle.size.x - 20, TN_TINTA)


## Esquinitas de papel que sujetan una foto o un dibujo pegado en el diario
func _esquinas_foto(r: Rect2) -> void:
	var c := Color("c9ae80")
	for esq: Vector2 in [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]:
		var sx := 1.0 if esq.x == r.position.x else -1.0
		var sy := 1.0 if esq.y == r.position.y else -1.0
		_lienzo.draw_colored_polygon(PackedVector2Array([esq + Vector2(-2 * sx, -2 * sy), esq + Vector2(9 * sx, -2 * sy), esq + Vector2(-2 * sx, 9 * sy)]), c)
		_lienzo.draw_line(esq + Vector2(9 * sx, -2 * sy), esq + Vector2(-2 * sx, 9 * sy), Color(TN_APAGADA, 0.6), 1.0)


## El retrato de un lazo, como una foto pegada en el diario
func _retrato_pegado(id: String, pos: Vector2) -> void:
	var t := _cargar_retrato(id)
	var grande := "res://arte/retratos/%s.png" % id
	if ResourceLoader.exists(grande):
		if not _retratos.has(grande):
			_retratos[grande] = load(grande)
		t = _retratos[grande]
	var tam := t.get_size() * (1.0 if t.get_width() > 40 else 2.0)
	var marco := Rect2(pos, tam + Vector2(8, 8))
	_lienzo.draw_rect(Rect2(marco.position + Vector2(2, 3), marco.size), Color(0, 0, 0, 0.2))
	_lienzo.draw_rect(marco, Color("f8efd6"))
	_lienzo.draw_rect(Rect2(pos + Vector2(4, 4), tam), Color("c9ae80"))
	_lienzo.draw_texture_rect(t, Rect2(pos + Vector2(4, 4), tam), false)
	_esquinas_foto(marco)


func _desplazamiento_libro() -> float:
	return (1.0 - _ease(_abre / 0.45)) * 50.0


## El detalle de una misión: de quién es, qué pasa, los pasos y lo que da
func _detalle_mision(m: Dictionary, caja: Rect2, es_seguida: bool) -> void:
	var x := caja.position.x + 10
	var ancho := caja.size.x - 20
	var tipo := String(m.get("tipo", ""))
	var ct: Color = COLOR_TIPO.get(tipo, TN_TINTA)
	var y := caja.position.y + 14
	var cabecera := String(Misiones.TIPOS.get(tipo, ""))
	var quien := String(m.get("quien", ""))
	if quien != "":
		for z in LAZOS:
			if z[0] == quien and Estado.tiene(z[2]):
				cabecera += " · " + z[1]
	if tipo == "historia":
		_lienzo.draw_texture_rect(SELLO, Rect2(x - 2, y - 13, 15, 15), false)
	else:
		_rombo(Vector2(x + 4, y - 5), 4.0, ct)
	_texto(cabecera, Vector2(x + 16, y), ct)
	if es_seguida and Misiones.estado(m) == "activa":
		# «en pantalla»: un sello de tinta
		var r := Rect2(caja.end.x - 16 - _ancho("en pantalla"), y - 13, _ancho("en pantalla") + 10, 17)
		_lienzo.draw_rect(r, Color(TN_ROJO, 0.12))
		_lienzo.draw_rect(r, Color(TN_ROJO, 0.7), false, 1.0)
		_texto("en pantalla", r.position + Vector2(5, 13), Color(TN_ROJO, 0.85))
	y += 22
	var titulo := String(m["titulo"])
	_texto(titulo, Vector2(x, y), TN_TINTA)
	_texto(titulo, Vector2(x + 1, y), TN_TINTA)                 # (en negrita)
	PIEL.raya(_lienzo, Vector2(x, y + 6), Vector2(x + ancho, y + 5), TN_SUAVE, 0.5)
	y = _parrafo(String(m.get("texto", "")), Vector2(x, y + 22), ancho, TN_SUAVE, 15.0) + 6
	for paso in Misiones.pasos_visibles(m):
		var hecho: bool = paso["hecho"]
		if hecho:
			_palomita(Vector2(x + 4, y - 4), TN_VERDE)
		else:
			_lienzo.draw_rect(Rect2(x, y - 10, 9, 9), Color(TN_TINTA, 0.8), false, 1.0)      # casilla por marcar
		y = _parrafo(String(paso["texto"]), Vector2(x + 14, y + 1), ancho - 14, TN_APAGADA if hecho else TN_TINTA, 15.0) + 3
		if y > caja.end.y - 26:
			break
	var premio := String(m.get("premio", ""))
	if premio != "":
		var py := maxf(y + 8, caja.end.y - 26)
		_parrafo("Recompensa: " + premio, Vector2(x, py), ancho, TN_VERDE if Misiones.estado(m) == "hecha" else TN_ROJO, 15.0)


func _cargar_retrato(id: String) -> Texture2D:
	if not _retratos.has(id):
		_retratos[id] = load("res://arte/personajes/aldeanos/%s_frente.png" % id)
	return _retratos[id]


func _dibujar_mapa() -> void:
	var area := Rect2(PAG_IZQ.position.x, PAG_IZQ.position.y + 4, PAG_DER.end.x - PAG_IZQ.position.x, PAG_IZQ.size.y - 4)
	if not Estado.tiene("mapa_partido"):
		_titulo("Mapa", PAG_IZQ.position + Vector2(6, 28), TN_TITULO)
		_texto("Aún no tienes ningún mapa.", PAG_IZQ.position + Vector2(10, 64), TN_APAGADA)
		return
	if _raiz_conocida() and not _mapa_mundo:
		_dibujar_mapa_raiz(area)
		return
	var pos := (area.position + (area.size - Vector2(MAPA.get_size())) / 2.0 - Vector2(0, 10)).round()
	_lienzo.draw_texture(MAPA, pos)
	# Maisha está en el Kitovu (o en Raíz): un punto que late
	var aqui := pos + (Vector2(78, 120) if PUNTO_RAIZ.has(Estado.escena_actual) and not Estado.escena_actual in ["kitovu", "casa_shamba"] else Vector2(152, 108))
	_punto(aqui)
	var pie := "Falta el trozo del norte. Mzee Shamba cree que está en Sigilia."
	if _raiz_conocida():
		pie = "↑ ↓ ver el mapa de Raíz · " + "Falta el trozo de Sigilia."
	_texto(pie, Vector2(area.position.x + 16, area.end.y - 12), TN_SUAVE)


func _punto(aqui: Vector2) -> void:
	var pulso := 2.0 + roundf(sin(_tiempo * 4.0))
	_lienzo.draw_circle(aqui, pulso + 1.0, Color(0, 0, 0, 0.5))
	_lienzo.draw_circle(aqui, pulso, VERDE)


## El mapa de Raíz existe desde que Maisha pisa Raíz (lo va dibujando ella)
func _raiz_conocida() -> bool:
	return Estado.tiene("visto/prados_del_eco")


## El mapa de Raíz: los caminos que ya ha pisado (con tinta), niebla sobre lo que no conoce, los nombres de los
## lugares (con el mapa de Tawi se ven todos) y dónde está Maisha
func _dibujar_mapa_raiz(area: Rect2) -> void:
	var pos := (area.position + (area.size - Vector2(MAPA_RAIZ.get_size())) / 2.0 - Vector2(0, 8)).round()
	_lienzo.draw_texture(MAPA_RAIZ, pos)
	var con_tawi := Estado.tiene("mapa_raiz")
	var caminos_vistos := 0
	for k in CAMINOS_RAIZ.size():
		var cam: Array = CAMINOS_RAIZ[k]
		var puntos: Array = cam[2]
		if Estado.tiene("visto/" + String(cam[1])):
			caminos_vistos += 1
			_trazo_tinta(pos, puntos)
		else:
			# niebla sobre el tramo de en medio (los extremos tocan los lugares, que tienen la suya)
			var medio: Array = puntos.slice(1, puntos.size() - 1) if puntos.size() > 2 else [(Vector2(puntos[0]) + Vector2(puntos[-1])) / 2.0]
			for j in medio.size():
				_nube(pos + Vector2(medio[j]), Vector2(13, 9), k * 7 + j)
	for k in LUGARES_RAIZ.size():
		var r: Array = LUGARES_RAIZ[k]
		if not Estado.tiene(String(r[2])) and not con_tawi:
			_nube(pos + Vector2(r[1]), Vector2(40, 22), k * 13 + 100)
			_texto("?", (pos + Vector2(r[1]) + Vector2(-2, 5)).round(), Color(NIEBLA_SOMBRA, 0.9))
	for r in LUGARES_RAIZ:
		var conocida := Estado.tiene(String(r[2]))
		if not conocida and not con_tawi:
			continue
		var tinta := TINTA if conocida else Color(TINTA, 0.6)
		# el nombre en dos líneas («Bosque / Cobrizo»), centrado: así no se pisan los rótulos vecinos
		var nombre: String = r[0]
		var partes: PackedStringArray = nombre.split(" ", false, 1)
		for k in partes.size():
			var linea := partes[k]
			var x_txt := clampf(Vector2(r[1]).x - _ancho(linea) / 2.0, 6.0, MAPA_RAIZ.get_width() - 6.0 - _ancho(linea))
			var p: Vector2 = pos + Vector2(x_txt, Vector2(r[1]).y + 8 + k * 11)
			_lienzo.draw_string(_fuente, p.round() + Vector2(1, 1), linea, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color("e2cea0"))
			_lienzo.draw_string(_fuente, p.round(), linea, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, tinta)
		# con el mapa de los secretos (tienda de Tawi): cuántos se han encontrado en cada sitio
		if conocida and Estado.tiene("mapa_secretos"):
			var mapa := String(r[2]).trim_prefix("visto/")
			var total := _secretos_total(mapa)
			if total > 0:
				var hallados := 0
				for m in Estado.marcas:
					if String(m).begins_with("secreto/%s/" % mapa):
						hallados += 1
				var txt := "%d/%d" % [hallados, total]
				var q: Vector2 = pos + Vector2(r[1]) + Vector2(-(_ancho(txt) + 10) / 2.0, 33)
				_lienzo.draw_colored_polygon(PackedVector2Array([q + Vector2(3, -9), q + Vector2(6, -6), q + Vector2(3, -3), q + Vector2(0, -6)]),
					Color("6b2a8f") if hallados < total else Color("3e7a2a"))
				_lienzo.draw_string(_fuente, q.round() + Vector2(10, 0), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 16,
					Color("6b2a8f") if hallados < total else Color("3e7a2a"))
	if PUNTO_RAIZ.has(Estado.escena_actual):
		_aqui(pos + PUNTO_RAIZ[Estado.escena_actual])
	var pie := "Caminos descubiertos: %d/%d" % [caminos_vistos, CAMINOS_RAIZ.size()]
	for cam in CAMINOS_RAIZ:
		if cam[1] == Estado.escena_actual:
			pie = "Estás en: %s · %s" % [cam[0], pie]
	_texto(pie + " · ↑ ↓ mundo", Vector2(area.position.x + 16, area.end.y - 12), TN_SUAVE)
	# el mapa está pegado sobre las dos páginas: el lomo lo dobla un poco
	_lienzo.draw_rect(Rect2(LOMO - 4, pos.y, 8, MAPA_RAIZ.get_height()), Color(0.2, 0.12, 0.05, 0.18))


## Un camino trazado con tinta: rayitas, como lo dibujaría Maisha al andar
func _trazo_tinta(pos: Vector2, puntos: Array) -> void:
	for j in puntos.size() - 1:
		var a: Vector2 = pos + Vector2(puntos[j])
		var b: Vector2 = pos + Vector2(puntos[j + 1])
		var pasos := maxi(1, int(a.distance_to(b) / 3.0))
		for k in pasos:
			if k % 2 == 0:
				var p0 := a.lerp(b, float(k) / pasos).round()
				var p1 := a.lerp(b, float(k + 1) / pasos).round()
				_lienzo.draw_line(p0 + Vector2(1, 1), p1 + Vector2(1, 1), Color("e2cea0"), 2.0)
				_lienzo.draw_line(p0, p1, Color("3a2414"), 2.0)


## «Estás aquí»: un alfiler verde que late
func _aqui(p: Vector2) -> void:
	var pulso := roundf(sin(_tiempo * 4.0))
	_lienzo.draw_circle(p, 7.0 + pulso, Color(VERDE, 0.25))
	_lienzo.draw_circle(p + Vector2(0, 1), 4.0, Color(0, 0, 0, 0.6))
	_lienzo.draw_circle(p, 4.0, Color("3a2414"))
	_lienzo.draw_circle(p, 3.0, VERDE)
	_lienzo.draw_rect(Rect2(p + Vector2(-1, -2), Vector2(1, 1)), Color("fff3c4"))


## Un banco de niebla de pergamino (con su sombrita y unos rizos) que se mueve muy despacio
func _nube(centro: Vector2, radios: Vector2, semilla: int) -> void:
	var azar := RandomNumberGenerator.new()
	azar.seed = semilla
	var bolas: Array[Vector3] = []
	for k in 7:
		var a := azar.randf() * TAU
		var d := azar.randf() * 0.6
		var r := minf(radios.x, radios.y) * (0.55 + azar.randf() * 0.4)
		var deriva := Vector2(sin(_tiempo * 0.4 + semilla + k), cos(_tiempo * 0.33 + k)) * 1.2
		bolas.append(Vector3(centro.x + cos(a) * radios.x * d + deriva.x, centro.y + sin(a) * radios.y * d + deriva.y, r))
	for b in bolas:
		_lienzo.draw_circle(Vector2(b.x + 1.5, b.y + 2.0), b.z, Color(NIEBLA_SOMBRA, 0.8))
	for b in bolas:
		_lienzo.draw_circle(Vector2(b.x, b.y), b.z, NIEBLA)
	for b in bolas:
		_lienzo.draw_arc(Vector2(b.x - b.z * 0.2, b.y - b.z * 0.15), b.z * 0.45, PI * 1.1, PI * 1.9, 8, Color(NIEBLA_SOMBRA, 0.7), 1.0)


var _secretos_cache := {}


## Cuántos secretos («X») tiene un mapa (se lee una vez de datos/mapas/<mapa>.json)
func _secretos_total(mapa: String) -> int:
	if not _secretos_cache.has(mapa):
		var ruta := "res://datos/mapas/%s.json" % mapa
		var total := 0
		if ResourceLoader.exists(ruta):
			for fila in (load(ruta) as JSON).data.get("filas", []):
				total += String(fila).count("X")
		_secretos_cache[mapa] = total
	return _secretos_cache[mapa]


## La rueda rápida: las 5 pestañas en círculo sobre el juego parado
func _dibujar_rueda() -> void:
	var a := _rueda_alfa
	var centro := Vector2(320, 180)
	_lienzo.draw_rect(Rect2(0, 0, 640, 360), Color(0.03, 0.02, 0.05, 0.45 * a))
	var radio := 74.0 * (0.85 + 0.15 * a)
	# un disco de pergamino con el canto de cuero cosido
	_lienzo.draw_circle(centro + Vector2(3, 4), radio + 28.0, Color(0, 0, 0, 0.35 * a))
	_lienzo.draw_circle(centro, radio + 28.0, Color(Color("552a19"), a))
	_lienzo.draw_arc(centro, radio + 24.0, 0.0, TAU, 96, Color(PIEL.ORO, 0.8 * a), 1.0)
	_lienzo.draw_circle(centro, radio + 21.0, Color(Color("e6d3a8"), a))
	_lienzo.draw_arc(centro, radio - 26.0, 0.0, TAU, 48, Color(PIEL.TINTA_APAGADA, 0.5 * a), 1.0)
	for i in PESTANAS.size():
		var ang := _angulo_rueda(i)
		var p := centro + Vector2.from_angle(ang) * radio
		var elegida := i == _eleccion_rueda
		if elegida:
			_lienzo.draw_circle(p, 19.0, Color(PIEL.MARCADOR, 0.45 * a))
			_lienzo.draw_arc(p, 19.0, 0.0, TAU, 32, Color(PIEL.ROJO, a), 1.0)
		var escala := 2.0 if elegida else 1.5
		_icono_pestana(i, p - Vector2(8, 8) * escala, escala, Color(1, 1, 1, a * (1.0 if elegida or _eleccion_rueda < 0 else 0.6)))
		_texto(str(i + 1), p + Vector2(12, -10), Color(PIEL.ROJO, 0.8 * a))
	# en el centro, el nombre de lo elegido
	var nombre: String = PESTANAS[_eleccion_rueda] if _eleccion_rueda >= 0 else "Mochila"
	_texto(nombre, Vector2(round(centro.x - _ancho(nombre) / 2.0), centro.y + 5), Color(PIEL.TINTA, a))
	var pista := "inclina y suelta" if _eleccion_rueda < 0 else "suelta para abrir"
	_texto(pista, Vector2(round(centro.x - _ancho(pista) / 2.0), centro.y + radio + 46), Color(PIEL.CREMA, 0.9 * a))


# --- El árbol de habilidades --------------------------------------------------------------------------

func _mover_arbol(delta: float) -> void:
	_destello_nodo = maxf(0.0, _destello_nodo - delta)
	var antes := Vector2i(_rama, _nodo)
	if Input.is_action_just_pressed("mover_derecha") or Input.is_action_just_pressed("ui_right"):
		if _rama < RAMAS_ARBOL.size() - 1:
			_rama += 1
		else:
			_ir_a_pestana((pestana + 1) % PESTANAS.size())
			return
	elif Input.is_action_just_pressed("mover_izquierda") or Input.is_action_just_pressed("ui_left"):
		if _rama > 0:
			_rama -= 1
		else:
			_ir_a_pestana((pestana - 1 + PESTANAS.size()) % PESTANAS.size())
			return
	if Input.is_action_just_pressed("mover_arriba") or Input.is_action_just_pressed("ui_up"):
		_nodo = mini(_nodo + 1, NODOS_ARBOL[RAMAS_ARBOL[_rama]].size() - 1)
	elif Input.is_action_just_pressed("mover_abajo") or Input.is_action_just_pressed("ui_down"):
		_nodo = maxi(_nodo - 1, 0)
	if Vector2i(_rama, _nodo) != antes:
		Sonido.efecto("menu_mover")
		_mantenido = 0.0
	# mantener Acción sobre el siguiente nodo (si se puede pagar) lo despierta
	var id: String = RAMAS_ARBOL[_rama]
	if _soltar:
		_soltar = Input.is_action_pressed("accion")
		return
	if Input.is_action_pressed("accion") and _nodo == Artes.nivel(id) + 1 and Artes.puede_subir(id):
		_mantenido += delta
		if _mantenido >= MANTENER:
			_mantenido = 0.0
			_soltar = true
			if Artes.subir(id):
				Sonido.efecto("arte_sube")
				_destello_nodo = 0.6
	else:
		_mantenido = maxf(0.0, _mantenido - delta * 3.0)


## El estado de un nodo: "basica", "despierto", "siguiente" o "dormido"
func _estado_nodo(id: String, i: int) -> String:
	if i == 0:
		return "basica"
	var n := Artes.nivel(id)
	if i <= n:
		return "despierto"
	if i == n + 1:
		return "siguiente"
	return "dormido"


func _dibujar_arbol(tinta: float) -> void:
	_lienzo.draw_texture(ARBOL_RAMAS, Vector2.ZERO, Color(1, 1, 1, tinta))
	# lo despierto de cada rama brilla por encima de la madera
	for id in RAMAS_ARBOL:
		var pts: Array = NODOS_ARBOL[id]
		var n := Artes.nivel(id)
		var col: Color = COLOR_RAMA[id]
		for i in range(0, mini(n, pts.size() - 1)):
			var pulso := 0.55 + 0.25 * sin(_tiempo * 3.0 - i * 0.6)
			_lienzo.draw_line(pts[i], pts[i + 1], Color(col, 0.35 * tinta), 5.0)
			_lienzo.draw_line(pts[i], pts[i + 1], Color(col.lightened(0.4), pulso * tinta), 2.0)
	# las ramas dormidas: Runa y Tierra, en la niebla
	for d in [[Vector2(64, 236), "Runa"], [Vector2(576, 236), "Tierra"]]:
		var c: Vector2 = d[0]
		_lienzo.draw_circle(c, 11.0, Color(0.05, 0.06, 0.12, 0.85 * tinta))
		_lienzo.draw_arc(c, 11.0, 0, TAU, 24, Color(0.45, 0.5, 0.7, 0.6 * tinta), 1.5)
		_texto("?", c + Vector2(-3, 6), Color(0.6, 0.65, 0.85, 0.8 * tinta))
		_texto(String(d[1]), c + Vector2(-_ancho(String(d[1])) / 2.0, -16), Color(TN_APAGADA, 0.8 * tinta))
	# los nodos
	for r in RAMAS_ARBOL.size():
		var id: String = RAMAS_ARBOL[r]
		var pts: Array = NODOS_ARBOL[id]
		for i in pts.size():
			_dibujar_nodo(id, i, pts[i], tinta, r == _rama and i == _nodo)
		# el nombre de la rama, encima de su último nodo, con lo que lleva despierto
		var arriba: Vector2 = pts[pts.size() - 1]
		var nombre: String = NOMBRE_RAMA[id] + "  %d/%d" % [Artes.nivel(id), Artes.nivel_maximo(id)]
		# (al lado del último nodo: Raíz y Cetro a su derecha, Aliento a su izquierda)
		var x_n := arriba.x - 20.0 - _ancho(nombre) if id == "aliento" else arriba.x + 20.0
		var y_n := arriba.y + (12.0 if id == "cetro" else 5.0)
		_texto(nombre, Vector2(x_n, y_n), Color(COLOR_RAMA[id], tinta))
	_dibujar_panel_nodo(tinta)


func _dibujar_nodo(id: String, i: int, p: Vector2, tinta: float, elegido: bool) -> void:
	var estado := _estado_nodo(id, i)
	var grande := Artes.es_grande(id, i)
	var r := 12.0 if grande else (10.0 if i == 0 else 9.0)
	var col: Color = COLOR_RAMA[id]
	match estado:
		"basica", "despierto":
			var halo := 0.18 + 0.08 * sin(_tiempo * 2.5 + i)
			_lienzo.draw_circle(p, r + 7.0, Color(col, halo * tinta))
			_lienzo.draw_circle(p, r + 1.5, Color(0.05, 0.04, 0.08, 0.9 * tinta))
			_lienzo.draw_circle(p, r, Color(col.darkened(0.35), tinta))
			_lienzo.draw_arc(p, r, 0, TAU, 32, Color(col.lightened(0.5), tinta), 1.5)
		"siguiente":
			var late := 0.5 + 0.5 * sin(_tiempo * 4.0)
			_lienzo.draw_circle(p, r + 1.5, Color(0.05, 0.04, 0.08, 0.95 * tinta))
			_lienzo.draw_circle(p, r, Color(0.12, 0.13, 0.24, tinta))
			_lienzo.draw_arc(p, r + 3.0 + late * 2.0, 0, TAU, 32, Color(col, (0.3 + 0.4 * late) * tinta), 1.5)
			_lienzo.draw_arc(p, r, 0, TAU, 32, Color(col, tinta), 1.5)
		_:
			_lienzo.draw_circle(p, r + 1.5, Color(0.04, 0.04, 0.07, 0.95 * tinta))
			_lienzo.draw_circle(p, r, Color(0.09, 0.09, 0.16, tinta))
			_lienzo.draw_arc(p, r, 0, TAU, 32, Color(0.35, 0.37, 0.52, tinta), 1.0)
	if grande:
		# los nodos grandes llevan una corona de cuatro puntas
		for k in 4:
			var a := k * PI / 2.0 + PI / 4.0
			var q := p + Vector2(cos(a), sin(a)) * (r + 4.0)
			_lienzo.draw_circle(q, 1.6, Color(ORO_CLARO if estado in ["despierto", "basica"] else Color(0.5, 0.48, 0.4), tinta))
	# el icono de la rama
	var mod := Color(1, 1, 1, tinta) if estado in ["basica", "despierto"] else Color(0.55, 0.55, 0.7, 0.75 * tinta)
	var lado := 16.0 if r >= 10.0 else 14.0
	_lienzo.draw_texture_rect_region(NODOS_ICONOS, Rect2(p - Vector2.ONE * lado / 2.0, Vector2.ONE * lado), Rect2(ICONO_RAMA[id] * 16, 0, 16, 16), mod)
	if i == 0:
		# la tecla de la habilidad básica
		var tecla: String = HABILIDADES[BASICA_RAMA[id]][1]
		var c := p + Vector2(r + 6, r - 2)
		_lienzo.draw_rect(Rect2(c - Vector2(5, 7), Vector2(11, 12)), Color(0.08, 0.06, 0.1, 0.9 * tinta))
		_lienzo.draw_rect(Rect2(c - Vector2(5, 7), Vector2(11, 12)), Color(TN_TITULO, tinta), false, 1.0)
		_texto(tecla, c + Vector2(-3, 4), Color(TN_TITULO, tinta), -1, 12)
	if elegido:
		# el aro dorado de lo elegido, que gira, y lo que se lleva manteniendo Acción
		var giro := _tiempo * 2.0
		for k in 8:
			var a0 := giro + k * TAU / 8.0
			_lienzo.draw_arc(p, r + 5.0, a0, a0 + TAU / 16.0, 6, Color(ORO_CLARO, tinta), 2.0)
		if _mantenido > 0.0:
			_lienzo.draw_arc(p, r + 9.0, -PI / 2.0, -PI / 2.0 + TAU * (_mantenido / MANTENER), 32, Color(col.lightened(0.5), tinta), 3.0)
		if _destello_nodo > 0.0:
			_lienzo.draw_circle(p, r + 20.0 * (1.0 - _destello_nodo / 0.6), Color(col.lightened(0.6), _destello_nodo * tinta))


func _dibujar_panel_nodo(tinta: float) -> void:
	var caja := Rect2(46, 262, 548, 66)
	_lienzo.draw_rect(caja, Color(0.04, 0.04, 0.09, 0.88 * tinta))
	_lienzo.draw_rect(caja, Color(TN_TITULO, 0.8 * tinta), false, 1.0)
	_lienzo.draw_rect(caja.grow(-3), Color(TN_TITULO, 0.3 * tinta), false, 1.0)
	var id: String = RAMAS_ARBOL[_rama]
	var col: Color = COLOR_RAMA[id]
	var x := caja.position.x + 12
	var y := caja.position.y + 18
	# lo que tienes, abajo a la derecha del panel
	var bolsa := "◆ Esencia %d   ✧ Cristales %d" % [Artes.esencia(), Tienda.cristales()]
	_texto(bolsa, Vector2(caja.end.x - 10 - _ancho(bolsa), caja.end.y - 6), Color(TN_TITULO, tinta))
	if _nodo == 0:
		var h: Array = HABILIDADES[BASICA_RAMA[id]]
		_texto("%s  (%s)" % [h[0], h[1]], Vector2(x, y), Color(col, tinta))
		_parrafo(String(h[3]), Vector2(x, y + 18), caja.size.x - 24, Color(TN_TINTA, tinta), 15.0)
		return
	var niveles: Array = Artes.buscar(id).get("niveles", [])
	var nivel_d: Dictionary = niveles[_nodo - 1]
	var titulo := "%s %s · %s" % [NOMBRE_RAMA[id].capitalize(), _romano(_nodo), String(nivel_d["nombre"])]
	if bool(nivel_d.get("grande", false)):
		titulo += "  ✦"
	_texto(titulo, Vector2(x, y), Color(col, tinta))
	_parrafo(String(nivel_d["texto"]), Vector2(x, y + 18), caja.size.x - 200, Color(TN_TINTA, tinta), 15.0)
	# a la derecha: lo que cuesta y si se puede
	var estado := _estado_nodo(id, _nodo)
	var xd := caja.end.x - 176
	if estado == "despierto":
		_texto("Despierto", Vector2(xd + 50, y + 22), Color(TN_VERDE, tinta))
		return
	var esencia := _nodo
	var cristales := int(nivel_d.get("cristales", 0))
	var coste := "◆ %d Esencia" % esencia + ("   ✧ %d" % cristales if cristales > 0 else "")
	_texto(coste, Vector2(xd, y), Color(TN_TITULO, tinta))
	var aviso := ""
	var color_aviso := TN_APAGADA
	if estado == "dormido":
		aviso = "Primero el anterior"
	elif Artes.esencia() < esencia:
		aviso = "Te falta Esencia"
		color_aviso = TN_ROJO
	elif Tienda.cristales() < cristales:
		aviso = "Te faltan Cristales"
		color_aviso = TN_ROJO
	else:
		aviso = "Mantén Acción"
		color_aviso = col
		var barra := Rect2(xd, y + 26, 160, 4)
		_lienzo.draw_rect(barra, Color(0.1, 0.1, 0.2, tinta))
		_lienzo.draw_rect(Rect2(barra.position, Vector2(barra.size.x * (_mantenido / MANTENER), barra.size.y)), Color(col, tinta))
	_texto(aviso, Vector2(xd, y + 22), Color(color_aviso, tinta))


func _romano(n: int) -> String:
	return ["", "I", "II", "III", "IV", "V", "VI"][clampi(n, 0, 6)]

