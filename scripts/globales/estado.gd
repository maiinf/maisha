extends Node
## ESTADO DE LA PARTIDA (se carga solo al arrancar el juego: Proyecto → Ajustes → Autoload).
## Recuerda lo que ya ha pasado aunque se cambie de escena:
##   - zonas purgadas, secretos recogidos, escondites abiertos
##   - aldeanos rescatados y lo que se ha hablado con ellos
## Todo se apunta como «marcas» de texto, por ejemplo:
##   "zona/prados_del_eco/2", "secreto/prados_del_eco/8,9", "rescatado_pino", "bibi_conocida"
##
## La partida se guarda sola en user://partida.json (en el Mac:
## ~/Library/Application Support/Godot/app_userdata/Maisha/partida.json):
##   - al llegar a cada escena
##   - cada vez que pasa algo importante (se pone una marca o se recoge algo)
## Se guarda la escena y el sitio donde está Maisha, salvo si está en plena pelea:
## entonces se guarda el último sitio seguro.
##
## También hace los cambios de escena con fundido a negro:  Estado.ir_a("cuna_de_musgo", "prados")

signal marca_puesta(marca: String)
signal objetos_cambiados
signal guardado
## La partida entera ha cambiado de golpe (se ha cargado o se ha empezado de cero)
signal partida_cambiada

const VERSION_PARTIDA := 1

## Objetos que se pueden llevar: nombre, cuántos piden en su encargo (y la marca de encargo hecho),
## su icono en arte/interfaz/objetos.png y lo que dice la mochila de ellos
const OBJETOS := {
	"zanahoria": {"uno": "Zanahoria", "encargo": 5, "hecho": "hecha_cosecha", "icono": 0,
		"texto": "Del huerto de Mzee Shamba. Crujiente y algo terrosa."},
	"pez": {"uno": "Pez", "encargo": 1, "hecho": "hecha_pesca", "icono": 1,
		"texto": "Pescado en el estanque de la granja. Aún se mueve."},
	"tablas": {"uno": "Tablas", "encargo": 1, "hecho": "cerca_arreglada", "icono": 2,
		"texto": "Tablas de un tronco caído. Sirven para arreglar la cerca."},
	"seta_luminosa": {"uno": "Seta luminosa", "encargo": 3, "hecho": "construido_casa_seta", "icono": 5,
		"texto": "Brilla con una luz fría. Pino las necesita para su casa."},
	"mineral": {"uno": "Mineral", "encargo": 2, "hecho": "construido_taller", "icono": 6,
		"texto": "Cristal ámbar de las rocas de los prados. Para la forja de Corteza."},
	"madera": {"uno": "Madera", "encargo": 3, "hecho": "construido_puesto", "icono": 7,
		"texto": "Madera de los troncos caídos del Bosque Cobrizo. Tawi la necesita para su puesto."},
	"bayas": {"uno": "Bayas de ciénaga", "encargo": 4, "hecho": "construido_cocina", "icono": 8,
		"texto": "Moradas y ácidas. Crecen en las matas de la Ciénaga Quieta y vuelven a salir al cabo de un rato."},
	"junco": {"uno": "Junco", "encargo": 3, "hecho": "construido_cocina", "icono": 9,
		"texto": "Tallos dorados de la orilla de la ciénaga. Juncia los usa para su cabaña y para dar sabor."},
	"pagina": {"uno": "Página del diario", "encargo": 3, "hecho": "msafiri_diario", "icono": 18,
		"texto": "Una hoja del diario de viaje de Msafiri, escrita con letra apretada. El viento la llevó lejos de su campamento."},
	"nasa": {"uno": "Nasa", "encargo": 3, "hecho": "korongo_nasas", "icono": 19,
		"texto": "Una cesta de mimbre para pescar, de Korongo. Las ranas de piedra se la llevaron."},
	"campanilla": {"uno": "Campanilla de cobre", "encargo": 3, "hecho": "fuko_campanillas", "icono": 20,
		"texto": "Una campanilla de cobre de Fuko. Colgada en un cruce de galerías, le dice por dónde va sin necesidad de ver."},
	"cencerro": {"uno": "Cencerro de Mbuzi", "encargo": 3, "hecho": "mbuzi_cencerros", "icono": 22,
		"texto": "Un cencerro de cobre viejo, con su correa de cuero. En la Cañada del Eco suena tres veces: una tuya y dos de la peña."},
	"remo": {"uno": "Remo de Kasia", "encargo": 3, "hecho": "kasia_remos", "icono": 23,
		"texto": "Un remo de madera de fresno, con una cinta roja atada en el mango. Kasia ata una cinta a cada remo para saber cuál es cuál."},
	"mazorca": {"uno": "Mazorca antigua", "encargo": 3, "hecho": "sungura_mazorcas", "icono": 21,
		"texto": "Maíz de los antiguos labradores de Raíz, de granos dorados y alguno rojo. Sungura guarda sus semillas para que no se pierdan."},
	"ficha_taa": {"uno": "Ficha del Índice", "encargo": 0, "hecho": "", "icono": 27,
		"texto": "Una tarjeta del Índice del Archivo de Maandiko, con su pestaña morada. Pone, con letra muy pulcra: «Taa, farolero del Paso de la Escarcha»."},
	"sopa": {"uno": "Sopa de Juncia", "encargo": 0, "hecho": "", "icono": 10, "usable": true,
		"texto": "Calentita. Devuelve 3 hojas de vida. Tómala con F (o desde aquí, con Acción), incluso en plena pelea."},
}
## Cuántas hojas devuelve una sopa
const SOPA_CURA := 3

const CARPETAS := ["res://escenas/mundo/%s.tscn", "res://escenas/interiores/%s.tscn", "res://escenas/interfaz/%s.tscn"]

var marcas := {}
## Lo que lleva Maisha: nombre del objeto -> cuántos
var objetos := {}
## Otros datos que se guardan con la partida (la misión que se sigue, la Esencia, las Artes...)
var extra := {}
## Por qué puerta hay que aparecer al cargar la escena siguiente ("" = el inicio del mapa)
var llegada := ""
var cambiando := false

## Dónde se guarda la partida (las pruebas automáticas usan otro archivo)
var ruta_partida := "user://partida.json"
## Escena en la que está Maisha, el nombre del sitio y su posición (los pone cada escena al empezar)
var escena_actual := ""
var lugar := ""
var posicion := Vector2.ZERO
## Al continuar una partida: dónde aparece Maisha (null = por la puerta de llegada)
var posicion_carga: Variant = null
var tiempo_jugado := 0.0
## true mientras se juega (en la pantalla de inicio no cuenta el tiempo ni se guarda)
var jugando := false
var _guardar_pronto := false

var _capa: CanvasLayer
var _negro: ColorRect


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	marca_puesta.connect(func(_m: String) -> void: guardar_pronto())
	objetos_cambiados.connect(guardar_pronto)
	_capa = CanvasLayer.new()
	_capa.layer = 100
	add_child(_capa)
	_negro = ColorRect.new()
	_negro.color = Color(0.03, 0.03, 0.04, 0.0)
	_negro.set_anchors_preset(Control.PRESET_FULL_RECT)
	_negro.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_capa.add_child(_negro)


# --- Marcas ------------------------------------------------------------------------

func marcar(marca: String) -> void:
	if not marcas.has(marca):
		marcas[marca] = true
		marca_puesta.emit(marca)


func tiene(marca: String) -> bool:
	return marcas.has(marca)


## Cumple una condición del tipo «estas marcas sí y estas no»
func cumple(si: Array, no: Array) -> bool:
	for m in si:
		if not tiene(String(m)):
			return false
	for m in no:
		if tiene(String(m)):
			return false
	return true


func zona_purgada(mapa: String, zona: String) -> bool:
	return tiene("zona/%s/%s" % [mapa, zona])


func rescatado(aldeano: String) -> bool:
	return tiene("rescatado_" + aldeano)


# --- Objetos ---------------------------------------------------------------------

func cuantos(objeto: String) -> int:
	return int(objetos.get(objeto, 0))


func dar(objeto: String, cantidad := 1) -> void:
	objetos[objeto] = cuantos(objeto) + cantidad
	objetos_cambiados.emit()


## Quita objetos si los hay. Devuelve false (y no quita nada) si no hay bastantes.
func quitar(objeto: String, cantidad := 1) -> bool:
	if cuantos(objeto) < cantidad:
		return false
	objetos[objeto] = cuantos(objeto) - cantidad
	objetos_cambiados.emit()
	return true


## «Seta luminosa 2/3», «Seta luminosa 3/3: ¡ya tienes bastantes!» o «Seta luminosa (tienes 4)»
func texto_recogido(objeto: String) -> String:
	var datos: Dictionary = OBJETOS.get(objeto, {"uno": objeto, "encargo": 0, "hecho": ""})
	var texto: String = String(datos["uno"])
	var encargo := int(datos["encargo"])
	var n := cuantos(objeto)
	if encargo > 0 and n <= encargo and not tiene(String(datos["hecho"])):
		texto += " %d/%d" % [n, encargo]
		if n == encargo:
			texto += ": ¡ya tienes bastantes!"
	else:
		texto += " (tienes %d)" % n
	return texto


func olvidar_todo() -> void:
	marcas.clear()
	objetos.clear()
	llegada = ""
	escena_actual = ""
	lugar = ""
	posicion = Vector2.ZERO
	posicion_carga = null
	tiempo_jugado = 0.0
	extra.clear()
	partida_cambiada.emit()


# --- Guardar y cargar la partida -------------------------------------------------------

func _process(delta: float) -> void:
	if jugando and not get_tree().paused:
		tiempo_jugado += delta
	if _guardar_pronto:
		_guardar_pronto = false
		guardar()


## Guarda en el siguiente fotograma (si pasan varias cosas a la vez, se guarda una sola vez)
func guardar_pronto() -> void:
	if jugando:
		_guardar_pronto = true


## Apunta dónde está Maisha, si es un sitio seguro (no en plena pelea ni cambiando de escena)
func _apuntar_posicion() -> void:
	if cambiando:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null or not maisha.is_inside_tree():
		return
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado in [1, 2, 3]:      # AVISO, CERRADA, PURGANDO
			return
	posicion = maisha.global_position


func guardar() -> bool:
	if not jugando or escena_actual == "":
		return false
	_apuntar_posicion()
	var datos := {
		"version": VERSION_PARTIDA,
		"fecha": Time.get_datetime_string_from_system(false, true),
		"escena": escena_actual,
		"lugar": lugar,
		"posicion": [posicion.x, posicion.y],
		"tiempo": tiempo_jugado,
		"marcas": marcas.keys(),
		"objetos": objetos,
		"extra": extra,
	}
	var ruta_tmp := ruta_partida + ".tmp"
	var ruta_bak := ruta_partida + ".bak"
	var contenido := JSON.stringify(datos, "\t")
	# 1. Escritura atómica previa en archivo temporal
	var archivo := FileAccess.open(ruta_tmp, FileAccess.WRITE)
	if archivo == null:
		push_error("No se pudo guardar la partida temporal en %s" % ruta_tmp)
		return false
	archivo.store_string(contenido)
	archivo.close()
	# 2. Respaldo previo de la partida existente
	if FileAccess.file_exists(ruta_partida):
		var dir := DirAccess.open("user://")
		if dir:
			dir.copy(ruta_partida, ruta_bak)
	# 3. Sustitución definitiva del archivo principal
	var dir_tmp := DirAccess.open("user://")
	if dir_tmp:
		var err := dir_tmp.rename(ruta_tmp, ruta_partida)
		if err != OK:
			var archivo_dest := FileAccess.open(ruta_partida, FileAccess.WRITE)
			if archivo_dest:
				archivo_dest.store_string(contenido)
				archivo_dest.close()
				dir_tmp.remove(ruta_tmp)
	guardado.emit()
	return true


func hay_partida() -> bool:
	return (FileAccess.file_exists(ruta_partida) or FileAccess.file_exists(ruta_partida + ".bak")) and not leer_partida().is_empty()


## Lee el archivo de la partida sin cargarla ({} si no hay o está estropeado; recupera .bak si el principal se truncó o falta)
func leer_partida() -> Dictionary:
	var texto := ""
	if FileAccess.file_exists(ruta_partida):
		texto = FileAccess.get_file_as_string(ruta_partida)
		if texto.is_empty() and FileAccess.file_exists(ruta_partida + ".bak"):
			texto = FileAccess.get_file_as_string(ruta_partida + ".bak")
	elif FileAccess.file_exists(ruta_partida + ".bak"):
		texto = FileAccess.get_file_as_string(ruta_partida + ".bak")
	else:
		return {}

	if texto.is_empty():
		return {}
	var json := JSON.new()
	if json.parse(texto) != OK:
		return {}
	var datos = json.data
	if not datos is Dictionary or not datos.has("escena") or not datos.has("marcas"):
		return {}
	return datos


## Carga la partida guardada en Estado (no cambia de escena: eso lo hace continuar())
func cargar() -> bool:
	var datos := leer_partida()
	if datos.is_empty():
		return false
	olvidar_todo()
	for m in datos["marcas"]:
		marcas[String(m)] = true
	var guardados: Dictionary = datos.get("objetos", {})
	for o in guardados:
		objetos[String(o)] = int(guardados[o])
	escena_actual = String(datos["escena"])
	lugar = String(datos.get("lugar", ""))
	var p: Array = datos.get("posicion", [0, 0])
	posicion = Vector2(float(p[0]), float(p[1]))
	tiempo_jugado = float(datos.get("tiempo", 0.0))
	var guardado_extra = datos.get("extra", {})
	if guardado_extra is Dictionary:
		extra = guardado_extra.duplicate(true)
	partida_cambiada.emit()
	return true


## Carga la partida y lleva a Maisha al sitio donde se guardó
func continuar() -> bool:
	if not cargar():
		return false
	posicion_carga = posicion
	ir_a(escena_actual, "")
	return true


func borrar_partida() -> void:
	var extensiones: Array[String] = ["", ".bak", ".tmp"]
	for ext: String in extensiones:
		var r: String = ruta_partida + ext
		if FileAccess.file_exists(r):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(r))


## «1 h 05 min», «12 min»
static func texto_tiempo(segundos: float) -> String:
	var minutos := int(segundos / 60.0)
	if minutos >= 60:
		return "%d h %02d min" % [minutos / 60, minutos % 60]
	return "%d min" % minutos


# --- Cambio de escena -----------------------------------------------------------------

## ¿Existe ya esa escena? (sin avisar de error: para puertas a lugares que aún no se han hecho)
func existe_escena(escena: String) -> bool:
	for plantilla in CARPETAS:
		if ResourceLoader.exists(plantilla % escena):
			return true
	return false


func ruta_de(escena: String) -> String:
	for plantilla in CARPETAS:
		var ruta: String = plantilla % escena
		if ResourceLoader.exists(ruta):
			return ruta
	push_error("Estado: no existe la escena «%s»" % escena)
	return ""


## Funde a negro, cambia de escena y aparece por la puerta «puerta» de la escena nueva
func ir_a(escena: String, puerta: String) -> void:
	if cambiando:
		return
	var ruta := ruta_de(escena)
	if ruta == "":
		return
	if jugando:
		guardar()          # antes de salir de la escena, con Maisha aún en su sitio
	cambiando = true
	llegada = puerta
	var t := create_tween()
	t.tween_property(_negro, "color:a", 1.0, 0.3)
	await t.finished
	get_tree().change_scene_to_file(ruta)
	# espera a que la escena nueva esté lista antes de volver a mostrar la imagen
	await get_tree().process_frame
	await get_tree().process_frame
	t = create_tween()
	t.tween_property(_negro, "color:a", 0.0, 0.35)
	await t.finished
	cambiando = false
