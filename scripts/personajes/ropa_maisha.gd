extends Node2D
## ROPA POR CAPAS de Maisha.
## Cada prenda se dibuja una vez por dirección y se cuelga de un punto de anclaje
## (cabeza, cuerpo, brazos...). Este nodo la recoloca sola en cada fotograma de cada animación.
##
## Las prendas están en datos/prendas.json y los anclajes en datos/maisha_anclajes.json
## (los generan los programas de la carpeta herramientas/).
##
## Uso desde otro script:
##   $Ropa.poner("corona_hojas")      # se pone la prenda (sustituye a la que hubiera en su zona)
##   $Ropa.quitar_zona("cabeza")      # deja esa zona sin ropa
##   $Ropa.alternar("capa_musgo")     # se la pone o se la quita

signal ropa_cambiada

const ZONAS := ["cabeza", "cara", "espalda", "torso", "brazos", "piernas", "aura", "arma"]
const ANCHO_FOTOGRAMA := 24
const ALTO_FOTOGRAMA := 32

## Prendas que lleva al empezar (por su clave en prendas.json)
@export var prendas_iniciales: Array[String] = []

var _catalogo: Dictionary = {}
var _anclajes: Dictionary = {}
var _puestas: Dictionary = {}      # zona -> clave de la prenda
var _capas: Array[Sprite2D] = []
var _direccion := ""
var _detras: Node2D               # contenedor de las piezas que van detrás de Maisha
var _ocultas: Dictionary = {}     # zonas ocultadas un momento (p. ej. el cetro mientras se golpea)

@onready var _sprite: AnimatedSprite2D = get_parent().get_node("Sprite")


func _ready() -> void:
	# Las piezas de detrás van en un nodo hermano colocado JUSTO ANTES del dibujo de Maisha.
	# (No se usa z_index negativo porque entonces quedarían debajo del suelo.)
	_detras = Node2D.new()
	_detras.name = "RopaDetras"
	get_parent().add_child.call_deferred(_detras)
	_colocar_detras.call_deferred()
	_catalogo = _leer_json("res://datos/prendas.json")
	_anclajes = _leer_json("res://datos/maisha_anclajes.json")
	_sprite.frame_changed.connect(_actualizar)
	_sprite.animation_changed.connect(_actualizar)
	for clave in prendas_iniciales:
		poner(clave)
	_actualizar()


# --- Lo que se usa desde fuera -------------------------------------------------

func poner(clave: String) -> void:
	if not _catalogo.has(clave):
		push_warning("Ropa: no existe la prenda '%s' en datos/prendas.json" % clave)
		return
	var zona: String = _catalogo[clave]["zona"]
	_puestas[zona] = clave
	_reconstruir()


func quitar_zona(zona: String) -> void:
	if _puestas.erase(zona):
		_reconstruir()


func alternar(clave: String) -> void:
	if not _catalogo.has(clave):
		return
	var zona: String = _catalogo[clave]["zona"]
	if _puestas.get(zona, "") == clave:
		quitar_zona(zona)
	else:
		poner(clave)


## Pasa a la siguiente prenda del catálogo para esa zona (y, tras la última, a ninguna)
func siguiente_en_zona(zona: String) -> void:
	var opciones: Array[String] = []
	for clave in _catalogo:
		if _catalogo[clave]["zona"] == zona:
			opciones.append(clave)
	if opciones.is_empty():
		return
	opciones.sort()
	var actual: String = _puestas.get(zona, "")
	var i := opciones.find(actual)
	if i == opciones.size() - 1:
		quitar_zona(zona)
	else:
		poner(opciones[i + 1])


func lleva(clave: String) -> bool:
	return clave in _puestas.values()


func puestas() -> Dictionary:
	return _puestas.duplicate()


## Oculta o muestra un momento lo que se lleva en una zona (sin quitárselo)
func ocultar_zona(zona: String, ocultar: bool) -> void:
	if ocultar:
		_ocultas[zona] = true
	else:
		_ocultas.erase(zona)
	_actualizar()


# --- Funcionamiento interno ----------------------------------------------------

func _colocar_detras() -> void:
	get_parent().move_child(_detras, _sprite.get_index())

func _leer_json(ruta: String) -> Dictionary:
	# load() trata el .json como un recurso de Godot: así se incluye solo al exportar el juego
	var recurso := load(ruta) as JSON
	if recurso == null or not (recurso.data is Dictionary):
		push_error("Ropa: no se pudo leer " + ruta)
		return {}
	return recurso.data


func _direccion_de(animacion: String) -> String:
	return animacion.get_slice("_", animacion.get_slice_count("_") - 1)


## Crea una capa (Sprite2D) por cada pieza de la ropa puesta, para la dirección actual
func _reconstruir() -> void:
	for capa in _capas:
		capa.queue_free()
	_capas.clear()
	_direccion = _direccion_de(_sprite.animation)
	for zona in ZONAS:   # el orden de las zonas decide quién queda encima si dos se tocan
		if not _puestas.has(zona):
			continue
		var prenda: Dictionary = _catalogo[_puestas[zona]]
		for pieza in prenda["piezas"].get(_direccion, []):
			var capa := Sprite2D.new()
			capa.texture = load(pieza["textura"])
			capa.centered = false
			capa.set_meta("ancla", pieza["ancla"])
			capa.set_meta("zona", zona)
			capa.set_meta("desplazamiento", Vector2(pieza["desplazamiento"][0], pieza["desplazamiento"][1]))
			if pieza["delante"]:
				add_child(capa)
			else:
				_detras.add_child(capa)
			_capas.append(capa)
	_actualizar()
	ropa_cambiada.emit()


## Coloca cada capa en el anclaje del fotograma que se está viendo
func _actualizar() -> void:
	if _direccion_de(_sprite.animation) != _direccion:
		_reconstruir()
		return
	var lista: Array = _anclajes.get(String(_sprite.animation), [])
	if lista.is_empty():
		return
	var anclas: Dictionary = lista[clampi(_sprite.frame, 0, lista.size() - 1)]
	var esquina := _sprite.position - Vector2(ANCHO_FOTOGRAMA, ALTO_FOTOGRAMA) / 2.0
	for capa in _capas:
		var ancla: String = capa.get_meta("ancla")
		if not anclas.has(ancla) or _ocultas.has(capa.get_meta("zona")):
			capa.visible = false
			continue
		capa.visible = true
		var desplazamiento: Vector2 = capa.get_meta("desplazamiento")
		var punto := Vector2(anclas[ancla][0], anclas[ancla][1]) + desplazamiento
		if _sprite.flip_h:
			# mirando a la izquierda: se refleja la prenda igual que el dibujo de Maisha
			punto.x = ANCHO_FOTOGRAMA - punto.x - capa.texture.get_width()
		capa.flip_h = _sprite.flip_h
		capa.position = esquina + punto
