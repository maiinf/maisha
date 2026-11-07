extends "res://scripts/mundo/escena_mundo.gd"
## EL CANAL DE TINTA (Sigilia, el segundo camino desde Maandiko, por el este).
##   - EL CAUCE MAYOR («~»): tinta líquida que corre hacia el este; no se pisa.
##   - LOS MUELLES («%»), con nieve; el norte va de punta a punta hasta la Gran Dársena.
##   - EL REMANSO NORTE: la casa de Mfereji, tras un tapón de Tinta Quieta («ẋ», sigilia/charco_tinta.gd).
## Parte 1: el canal y sus muelles. Luego: el Sigilo de Hielo, las placas, las compuertas, Ruba y Pweza.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const CHARCO := preload("res://scripts/mundo/sigilia/charco_tinta.gd")


func _ready() -> void:
	super()
	Estado.marcar("canal_tinta")
	_poner_cosas()
	if not Estado.tiene("canal_llegada"):
		_pensar_al_llegar.call_deferred()


func _poner_cosas() -> void:
	var filas: PackedStringArray = $Region._filas
	for y in filas.size():
		for x in filas[y].length():
			if filas[y][x] == "ẋ":
				var ch: StaticBody2D = CHARCO.new()
				ch.marca = "charco/canal/%d,%d" % [x, y]
				ch.position = Vector2(x, y) * 16.0 + Vector2(8, 14)
				$Entidades.add_child(ch)


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("canal_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "canal_llegada")
	Estado.marcar("canal_llegada")
