extends "res://scripts/mundo/escena_mundo.gd"
## EL PASO DE LA ESCARCHA (Sigilia, el primer camino del mundo 2): de las Ruinas del Primer Árbol (sur) a la Puerta
## Sellada de Maandiko (norte). Se abre al curar al Primer Árbol («primer_arbol_libre»).
##   - LA NIEVE HONDA (sigilia/nieve_honda.gd): fuera del sendero pisado Maisha se hunde y va despacio; por donde
##     pasa deja un surco.
##   - LA VENTISCA DE PÁGINAS (sigilia/ventisca.gd): rachas del oeste que la empujan fuera del sendero si no se
##     cobija detrás de las ESTELAS RÚNICAS («ȩ»), las rocas o los pinos.
##   - TAA («ţ», sigilia/taa.gd), el farolero en blanco: su FICHA DEL ÍNDICE («ǩ») está en la nieve honda del este.
##     Al devolvérsela recupera el nombre y enseña el SIGILO DE FUEGO (marca «sigilo_fuego»).
##   - LOS FAROLES RÚNICOS («ƒ», sigilia/farol_runico.gd): se encienden con el sigilo; a su lado no empuja el viento
##     y la nieve no es honda.
##   - LAS PÁGINAS SUELTAS («ƥ», enemigos/pagina_suelta.gd): el sigilo de fuego las quema de un trazo.
##   - LA PUERTA SELLADA (sigilia/puerta_sellada.gd), arriba: Tinta Quieta que se derrite con tres sigilos de fuego
##     («puerta_sellada_abierta»); detrás, Maandiko.
## Nieva (la nevada del Sendero Olvidado).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const NEVADA := preload("res://scripts/mundo/olvidado/nevada.gd")
const VENTISCA := preload("res://scripts/mundo/sigilia/ventisca.gd")
const NIEVE_HONDA := preload("res://scripts/mundo/sigilia/nieve_honda.gd")
const TAA := preload("res://scripts/mundo/sigilia/taa.gd")
const FAROL := preload("res://scripts/mundo/sigilia/farol_runico.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const PAGINA := preload("res://scripts/enemigos/pagina_suelta.gd")
const PUERTA_SELLADA := preload("res://scripts/mundo/sigilia/puerta_sellada.gd")

var ventisca: Node2D
var nieve: Node2D


func _ready() -> void:
	super()
	Estado.marcar("paso_escarcha")
	_poner_cosas()
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


func _poner_cosas() -> void:
	var filas: PackedStringArray = $Region._filas
	for y in filas.size():
		var fila := filas[y]
		for x in fila.length():
			var c := fila[x]
			var pos := Vector2(x, y) * 16.0 + Vector2(8, 14)
			if c == "ţ":
				var t: StaticBody2D = TAA.new()
				t.position = pos
				$Entidades.add_child(t)
			elif c == "ƒ":
				var f: StaticBody2D = FAROL.new()
				f.marca = "farol/paso_escarcha/%d,%d" % [x, y]
				f.position = pos
				$Entidades.add_child(f)
			elif c == "ƥ":
				var pg: CharacterBody2D = PAGINA.new()
				pg.position = pos + Vector2(0, -4)
				$Entidades.add_child(pg)
			elif c == "ǩ":
				var ficha: Node2D = RECOGIBLE.new()
				ficha.objeto = "ficha_taa"
				ficha.marca = "ficha/taa"
				ficha.dibujo = "res://arte/mundos/sigilia/paso/ficha.png"
				ficha.color_halo = Color(0.85, 0.7, 1.0)
				ficha.position = pos
				$Entidades.add_child(ficha)


	# la Puerta Sellada, delante de la puerta del norte (en medio del sendero, al final de la subida)
	var puerta: StaticBody2D = PUERTA_SELLADA.new()
	puerta.position = Vector2(30 * 16, 5 * 16)
	$Entidades.add_child(puerta)
	puerta.abierta.connect(_al_abrir_puerta)


func _al_abrir_puerta() -> void:
	await get_tree().create_timer(1.2).timeout
	if is_inside_tree():
		await CHARLA_SCRIPT.hablar(self, "escarcha_puerta_abierta")


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
