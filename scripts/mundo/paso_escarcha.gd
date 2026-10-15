extends "res://scripts/mundo/escena_mundo.gd"
## EL PASO DE LA ESCARCHA (Sigilia, el primer camino del mundo 2): de las Ruinas del Primer Árbol (sur) a la Puerta
## Sellada de Maandiko (norte). Se abre al curar al Primer Árbol («primer_arbol_libre»).
##   - LA NIEVE HONDA (sigilia/nieve_honda.gd): fuera del sendero pisado Maisha se hunde y va despacio; por donde
##     pasa deja un surco.
##   - LA VENTISCA DE PÁGINAS (sigilia/ventisca.gd): rachas del oeste que la empujan fuera del sendero si no se
##     cobija detrás de las ESTELAS RÚNICAS («ȩ»), las rocas o los pinos.
## Nieva (la nevada del Sendero Olvidado).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const NEVADA := preload("res://scripts/mundo/olvidado/nevada.gd")
const VENTISCA := preload("res://scripts/mundo/sigilia/ventisca.gd")
const NIEVE_HONDA := preload("res://scripts/mundo/sigilia/nieve_honda.gd")

var ventisca: Node2D
var nieve: Node2D


func _ready() -> void:
	super()
	Estado.marcar("paso_escarcha")
	nieve = NIEVE_HONDA.new()
	nieve.name = "NieveHonda"
	nieve.region = $Region
	add_child(nieve)
	add_child(NEVADA.new())
	ventisca = VENTISCA.new()
	ventisca.name = "Ventisca"
	add_child(ventisca)
	ventisca.racha_acaba.connect(_tras_racha)
	if not Estado.tiene("escarcha_llegada"):
		ventisca.activa = false               # (que pueda leer lo que piensa antes de la primera racha)
		_pensar_al_llegar.call_deferred()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.6).timeout
	if not is_inside_tree() or Estado.tiene("escarcha_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "escarcha_llegada")
	Estado.marcar("escarcha_llegada")
	ventisca.activa = true


## Tras la primera racha, Maisha entiende cómo cobijarse
func _tras_racha() -> void:
	if Estado.tiene("escarcha_racha"):
		return
	Estado.marcar("escarcha_racha")
	await get_tree().create_timer(0.6).timeout
	if is_inside_tree():
		ventisca.activa = false
		await CHARLA_SCRIPT.hablar(self, "escarcha_racha")
		ventisca.activa = true
