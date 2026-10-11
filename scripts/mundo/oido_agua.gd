extends Node
## OÍDO DEL AGUA: cuanto más cerca está Maisha del agua (estanques, acequias, ríos), más se oye correr.
## Busca las casillas de agua del mapa («~») alrededor de Maisha y sube o baja el ambiente «agua».

const R := preload("res://scripts/combate/reglas_combate.gd")
const ALCANCE := 11            # casillas alrededor en las que se busca agua
const OIDO := 150.0            # a esta distancia (píxeles) del agua ya casi no se oye

var _agua := {}                # Vector2i -> true (casillas con agua)
var _cada := 0.0


func _ready() -> void:
	var region := get_parent().get_node_or_null("Region")
	if region == null:
		return
	var filas: PackedStringArray = region.get("_filas")
	for y in filas.size():
		for x in filas[y].length():
			if filas[y][x] == "~":
				_agua[Vector2i(x, y)] = true


func hay_agua() -> bool:
	return not _agua.is_empty()


## Distancia (en píxeles) de un punto al agua más cercana (o INF si no hay agua cerca)
func distancia_al_agua(p: Vector2) -> float:
	var c := R.casilla_de(p)
	var mejor := INF
	for dy in range(-ALCANCE, ALCANCE + 1):
		for dx in range(-ALCANCE, ALCANCE + 1):
			var k := c + Vector2i(dx, dy)
			if _agua.has(k):
				mejor = minf(mejor, p.distance_to(R.centro_de(k)))
	return mejor


func _process(delta: float) -> void:
	_cada -= delta
	if _cada > 0.0 or _agua.is_empty():
		return
	_cada = 0.15
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var d := distancia_al_agua(maisha.global_position)
	var cerca := clampf(1.0 - (d - 8.0) / OIDO, 0.0, 1.0)
	Sonido.volumen_ambiente("agua", 0.9 * cerca * cerca)
