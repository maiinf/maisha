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
const ESCRIBAS := ["daftari", "karatasi", "chapa", "darubini", "mlinzi", "kurasa", "muhuri", "wimbo"]
const INDICE := preload("res://scripts/mundo/sigilia/indice.gd")
const PUERTA := preload("res://scripts/mundo/puerta.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
## las tres fichas del Índice que el viento dejó dentro de la ciudad, en sus rincones: [objeto, casilla]
const FICHAS := [["ficha_kurasa", Vector2i(4, 6)], ["ficha_muhuri", Vector2i(66, 50)], ["ficha_wimbo", Vector2i(5, 50)]]
## la puerta del Gran Archivo (baja a la Sección Prohibida con los doce nombres)
const ARCHIVO := Vector2i(36, 15)
const FAROL := preload("res://scripts/mundo/sigilia/farol_runico.gd")
## vecino: [id del dibujo, conversación, casilla, marca que hace falta]
const VECINOS := [
	["kalamu", "", Vector2i(21, 21), ""],
	["mauti", "", Vector2i(39, 29), "mauti_libre"],
	["wino", "", Vector2i(55, 22), ""],
	["taa", "taa_ciudad", Vector2i(41, 47), "taa_nombre"],
	["daftari", "", Vector2i(30, 30), ""],
	["karatasi", "", Vector2i(44, 24), ""],
	["chapa", "", Vector2i(10, 22), ""],
	["darubini", "", Vector2i(14, 36), ""],
	["mlinzi", "", Vector2i(58, 35), ""],
	["kurasa", "", Vector2i(34, 44), ""],
	["muhuri", "", Vector2i(48, 40), ""],
	["wimbo", "", Vector2i(24, 38), ""],
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
	_poner_fichas()
	_poner_archivo()
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


func _poner_fichas() -> void:
	for f in FICHAS:
		var ficha: Node2D = RECOGIBLE.new()
		ficha.objeto = f[0]
		ficha.marca = "ficha/" + String(f[0]).trim_prefix("ficha_")
		ficha.dibujo = "res://arte/mundos/sigilia/paso/ficha.png"
		ficha.color_halo = Color(0.85, 0.7, 1.0)
		ficha.position = Vector2(f[1]) * 16.0 + Vector2(8, 14)
		$Entidades.add_child(ficha)


## La puerta del Gran Archivo: cerrada hasta que el Índice tiene sus doce nombres («indice_completo»)
func _poner_archivo() -> void:
	if INDICE.completo():
		Estado.marcar("indice_completo")
	var puerta: Area2D = PUERTA.new()
	puerta.id = "archivo"
	puerta.destino = "seccion_prohibida"
	puerta.destino_puerta = "archivo"
	puerta.salida = Vector2.DOWN
	puerta.tam = Vector2(32, 12)
	puerta.cerrada_hasta = "indice_completo"
	puerta.position = Vector2(ARCHIVO) * 16.0 + Vector2(0, 8)
	add_child(puerta)
	puerta.cerrada.connect(func() -> void:
		_hud.mostrar_mensaje("Nombres del Índice: %d de %d" % [INDICE.cuantos(), INDICE.NOMBRES.size()])
		CHARLA_SCRIPT.hablar(self, "archivo_cerrado"))


## Cada nombre que vuelve: si ya están los doce, el Gran Archivo se abre
func _al_poner_marca(marca: String) -> void:
	super(marca)
	if marca in INDICE.NOMBRES and INDICE.completo() and not Estado.tiene("indice_completo"):
		Estado.marcar("indice_completo")
		_hud.mostrar_mensaje("Los doce nombres han vuelto: el Gran Archivo se abre")
		Sonido.efecto("arte_sube", 0.0, Vector2(ARCHIVO) * 16.0)


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.6).timeout
	if not is_inside_tree() or Estado.tiene("maandiko_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "maandiko_llegada")
	Estado.marcar("maandiko_llegada")
