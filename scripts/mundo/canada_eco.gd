extends "res://scripts/mundo/escena_mundo.gd"
## CAÑADA DEL ECO: el camino del Bosque Cobrizo al Lago Espejo (el quinto de los caminos de Raíz).
## Una garganta entre dos paredes de peña, con mesetas de hierba encima; un arroyo baja hacia el lago y el camino
## lo cruza por un puentecito y un vado. MBUZI, la cabra montés pastora, vive en su aprisco del norte (encargo:
## tres cencerros que el eco esparció; al devolverlos descuelga la ESCALA DE CUERDA hasta la cornisa del quinto
## ECO PERDIDO). Una zona corrupta en el ensanche del sur y un secreto tras un matorral al noroeste.
## Al oeste, el paso al Lago Espejo (aún cerrado).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const PEDREGAL := preload("res://scripts/mundo/canada/pedregal.gd")
const CABRAS := preload("res://scripts/mundo/canada/cabras.gd")
const APRISCO := Vector2i(40, 7)          # la casilla del aprisco («{» en el mapa)


func _ready() -> void:
	super()
	var filas: PackedStringArray = $Region.get("_filas")
	var pedregal: Node2D = PEDREGAL.new()
	pedregal.name = "Pedregal"
	pedregal.preparar(filas)
	$Region.add_child(pedregal)
	get_tree().get_first_node_in_group("corrupcion").aplicar_a(pedregal)
	_poner_cabras(filas)
	_maisha.caida.connect(_al_caer_fuera_de_zona)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("canada_llegada"):
		_pensar_al_llegar.call_deferred()


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(2.0).timeout
	if not is_inside_tree() or Estado.tiene("canada_llegada"):
		return
	Estado.marcar("canada_llegada")
	await CHARLA_SCRIPT.hablar(self, "canada_llegada")


func _al_caer_fuera_de_zona() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("¡La Cañada del Eco vuelve a sonar a agua y a viento!")


## Las doce cabras: arriba, en el borde de la meseta del norte (sobre la cara de la peña), repartidas a lo largo de
## la cañada; y su corral, junto al aprisco
func _poner_cabras(filas: PackedStringArray) -> void:
	var cabras: Node2D = CABRAS.new()
	cabras.name = "Cabras"
	for x in [14, 22, 27, 33, 47, 52, 58, 63, 70, 76, 90, 96]:
		var y := 0
		while y < filas.size() - 1 and filas[y + 1][x] == "0":
			y += 1
		# (y es la última casilla de peña sobre el fondo: el borde de la meseta queda unas casillas más arriba)
		cabras.arriba.append(Vector2(x, maxi(1, y - 3)) * 16.0 + Vector2(8, 12))
	var pie := Vector2(APRISCO) * 16.0 + Vector2(8, 14)
	cabras.corral = Rect2(pie + Vector2(4, -26), Vector2(38, 18))
	$Entidades.add_child(cabras)
	get_tree().get_first_node_in_group("corrupcion").aplicar_a(cabras)

