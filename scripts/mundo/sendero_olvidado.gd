extends "res://scripts/mundo/escena_mundo.gd"
## EL SENDERO OLVIDADO: la subida de la Gruta de las Raíces (sur) a las Ruinas del Primer Árbol (norte). Se abre con
## las nueve voces (el Guardián aparta las raíces: «sendero_abierto»). Montaña, nieve, niebla y frío:
##   - LA ESCARCHA DE LA QUIETUD (olvidado/escarcha.gd): quedarse quieta congela; moverse o un brasero, no.
##   - BRASEROS («ŭ», olvidado/brasero.gd): se encienden con el fuego de una semilla; calientan y, si Maisha cae,
##     vuelve al último junto al que estuvo. El primero, junto a la Gruta, ya está encendido.
##   - LAS ESTATUAS («ŝ», olvidado/estatua_quieta.gd): quienes se quedaron quietos para no perder algo.
##   - LOS QUIETOS («ŧ», enemigos/quieto.gd): estatuas que solo se mueven cuando Maisha no las mira.
##   - Arriba, el ARCO DE LAS RUINAS («ŵ», olvidado/arco_ruinas.gd) con su niebla.
## Nieva (olvidado/nevada.gd) y hay niebla baja (la del Ambiente).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const BRASERO := preload("res://scripts/mundo/olvidado/brasero.gd")
const ESTATUA := preload("res://scripts/mundo/olvidado/estatua_quieta.gd")
const ARCO := preload("res://scripts/mundo/olvidado/arco_ruinas.gd")
const ESCARCHA := preload("res://scripts/mundo/olvidado/escarcha.gd")
const NEVADA := preload("res://scripts/mundo/olvidado/nevada.gd")
const QUIETO := preload("res://scripts/enemigos/quieto.gd")

var escarcha: Node2D


func _ready() -> void:
	super()
	Estado.marcar("sendero_olvidado")
	_poner_cosas()
	escarcha = ESCARCHA.new()
	escarcha.name = "Escarcha"
	_maisha.add_child(escarcha)
	escarcha.congelada.connect(_al_congelarse)
	add_child(NEVADA.new())
	_maisha.caida.connect(_al_caer)
	$Corrupcion.region_purgada.connect(_al_purgar_region)
	if not Estado.tiene("olvidado_llegada"):
		_pensar_al_llegar.call_deferred()


func _poner_cosas() -> void:
	var filas: PackedStringArray = $Region._filas
	var estatuas := 0
	for y in filas.size():
		var fila := filas[y]
		for x in fila.length():
			var c := fila[x]
			var pos := Vector2(x, y) * 16.0 + Vector2(8, 14)
			if c == "ŭ":
				var b: StaticBody2D = BRASERO.new()
				b.marca = "brasero/sendero_olvidado/%d,%d" % [x, y]
				b.encendido_al_empezar = y > filas.size() - 12      # el de la entrada, junto a la Gruta
				b.position = pos
				$Entidades.add_child(b)
			elif c == "ŝ":
				var e: StaticBody2D = ESTATUA.new()
				e.cual = estatuas
				estatuas += 1
				e.position = pos
				$Entidades.add_child(e)
			elif c == "ŧ":
				var q: CharacterBody2D = QUIETO.new()
				q.position = pos
				$Entidades.add_child(q)
			elif c == "ŵ":
				var a: Node2D = ARCO.new()
				a.position = pos
				$Entidades.add_child(a)


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.8).timeout
	if not is_inside_tree() or Estado.tiene("olvidado_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "olvidado_llegada")
	Estado.marcar("olvidado_llegada")


## La primera vez que se congela, Maisha entiende lo que pasa
func _al_congelarse() -> void:
	if Estado.tiene("olvidado_congelada"):
		return
	Estado.marcar("olvidado_congelada")
	await get_tree().create_timer(1.6).timeout
	if is_inside_tree():
		await CHARLA_SCRIPT.hablar(self, "olvidado_congelada")


## Si cae, vuelve al último brasero encendido junto al que estuvo (o al de la entrada)
func _al_caer() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var brasero: Node2D = escarcha.ultimo_brasero
	if brasero == null:
		for b in get_tree().get_nodes_in_group("braseros"):
			if b.encendido and (brasero == null or (b as Node2D).global_position.y > brasero.global_position.y):
				brasero = b
	var punto := brasero.global_position + Vector2(0, 22) if brasero else _maisha.global_position
	_hud.fundido(func() -> void:
		_maisha.revivir(punto)
		escarcha.frio = 0.0)


func _al_purgar_region() -> void:
	await get_tree().create_timer(2.5).timeout
	_hud.mostrar_mensaje("En el Sendero Olvidado ya no se oye a Giza: solo el viento")
