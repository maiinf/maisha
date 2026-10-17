extends "res://scripts/mundo/escena_mundo.gd"
## MAANDIKO, la Ciudad-Archivo (Sigilia): la ciudad de los escribas armiños, con sus calles nevadas, la Plaza del
## Índice, el Gran Archivo, el Barrio de los Copistas y el Mercado de Tinta. Se llega por la Puerta Sellada del Paso
## de la Escarcha. La Tinta Quieta ha dejado a casi todos en blanco.
##   - KALAMU, la archivera mayor (junto a su casa): cuenta lo que pasó y da el TROZO DEL NORTE del mapa («mapa_norte»).
##   - MAUTI, en la plaza, junto a la fuente (si ya es libre: «mauti_libre»); WINO, en el mercado; TAA, en su taller.
##   - LOS ESCRIBAS EN BLANCO por las calles (cada uno con su ficha del Índice perdida por los caminos).
##   - Tres salidas tapadas por CHARCOS DE TINTA QUIETA (sigilia/charco_tinta.gd): se derriten con el sigilo de fuego.
##     Al deshelar la primera, Wino abre su tienda («calle_deshelada»).
##   - LOS FAROLES RÚNICOS de las calles («ƒ»), apagados: con todos encendidos («faroles_maandiko»), Taa lo agradece
##     (y la tienda da 3 Cristales del Nexo por ello: datos/tienda.json).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const NEVADA := preload("res://scripts/mundo/olvidado/nevada.gd")
const VECINO := preload("res://scripts/mundo/sigilia/vecino.gd")
const CHARCO := preload("res://scripts/mundo/sigilia/charco_tinta.gd")
const ESCRIBA := preload("res://scripts/mundo/sigilia/escriba.gd")
## los escribas con nombre (los que se pueden curar con su ficha del Índice)
const ESCRIBAS := ["daftari"]
const FAROL := preload("res://scripts/mundo/sigilia/farol_runico.gd")
## vecino: [id del dibujo, conversación, casilla, marca que hace falta]
const VECINOS := [
	["kalamu", "", Vector2i(21, 21), ""],
	["mauti", "", Vector2i(39, 29), "mauti_libre"],
	["wino", "", Vector2i(55, 22), ""],
	["taa", "taa_ciudad", Vector2i(41, 47), "taa_nombre"],
	["daftari", "", Vector2i(30, 30), ""],
	["escriba_blanco", "", Vector2i(44, 24), ""],
	["escriba_blanco", "", Vector2i(10, 22), ""],
	["escriba_blanco", "", Vector2i(14, 36), ""],
	["escriba_blanco", "", Vector2i(58, 35), ""],
	["escriba_blanco", "", Vector2i(34, 44), ""],
]
## los charcos de Tinta Quieta que tapan las salidas: casilla (el centro de la calle, junto a la muralla)
const CHARCOS := [Vector2i(4, 25), Vector2i(67, 25), Vector2i(15, 3)]


func _ready() -> void:
	super()
	Estado.marcar("maandiko")
	add_child(NEVADA.new())
	_poner_vecinos()
	_poner_charcos()
	_poner_faroles()
	if not Estado.tiene("maandiko_llegada"):
		_pensar_al_llegar.call_deferred()


func _poner_vecinos() -> void:
	for v in VECINOS:
		if v[3] != "" and not Estado.tiene(v[3]):
			continue
		var n: StaticBody2D
		if v[0] in ESCRIBAS:
			n = ESCRIBA.new()
			n.nombre = v[0]
		else:
			n = VECINO.new()
			n.id = v[0]
			n.charla = v[1]
		n.position = Vector2(v[2]) * 16.0 + Vector2(8, 14)
		$Entidades.add_child(n)


func _poner_charcos() -> void:
	for c in CHARCOS:
		var charco: StaticBody2D = CHARCO.new()
		charco.marca = "charco/maandiko/%d,%d" % [c.x, c.y]
		charco.position = Vector2(c) * 16.0 + Vector2(8, 14)
		$Entidades.add_child(charco)
		charco.derretido.connect(func() -> void: Estado.marcar("calle_deshelada"))


func _poner_faroles() -> void:
	var filas: PackedStringArray = $Region._filas
	for y in filas.size():
		for x in filas[y].length():
			if filas[y][x] != "ƒ":
				continue
			var f: StaticBody2D = FAROL.new()
			f.marca = "farol/maandiko/%d,%d" % [x, y]
			f.position = Vector2(x, y) * 16.0 + Vector2(8, 14)
			$Entidades.add_child(f)
			f.encendido_ahora.connect(_al_encender_farol)


func _al_encender_farol() -> void:
	for f in get_tree().get_nodes_in_group("faroles_runicos"):
		if not f.encendido:
			return
	if not Estado.tiene("faroles_maandiko"):
		Estado.marcar("faroles_maandiko")
		_hud.mostrar_mensaje("Todos los faroles de Maandiko están encendidos")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.6).timeout
	if not is_inside_tree() or Estado.tiene("maandiko_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "maandiko_llegada")
	Estado.marcar("maandiko_llegada")
