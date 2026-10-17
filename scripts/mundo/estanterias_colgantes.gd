extends "res://scripts/mundo/escena_mundo.gd"
## LAS ESTANTERÍAS COLGANTES (Sigilia, el primer camino desde Maandiko): una biblioteca enorme de cuatro pisos.
##   - LOS HUECOS («ɵ») entre piso y piso no se pisan: solo se cruzan por las ESCALERAS RODANTES («ǝ»,
##     sigilia/escalera_rodante.gd), que se tienden, avisan y se van rodando. Si se van con Maisha encima, cae.
##   - LOS TINTEROS RABIOSOS («ǜ», enemigos/tintero.gd) y las PÁGINAS SUELTAS («ƥ»).
##   - LAS CERRADURAS DE TINTA QUIETA («ẋ», sigilia/charco_tinta.gd): se derriten con el sigilo de fuego.
##   - LA FICHA DEL ÍNDICE de Daftari («ʣ»), en la alcoba del oeste del piso 3.
## Arriba, la sala de lectura con su atril (donde espera el Bibliotecario Hueco: parte 2).

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const ESCALERA := preload("res://scripts/mundo/sigilia/escalera_rodante.gd")
const TINTERO := preload("res://scripts/enemigos/tintero.gd")
const PAGINA := preload("res://scripts/enemigos/pagina_suelta.gd")
const CHARCO := preload("res://scripts/mundo/sigilia/charco_tinta.gd")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const ATRIL := preload("res://arte/mundos/sigilia/estanterias/atril.png")


func _ready() -> void:
	super()
	Estado.marcar("estanterias_colgantes")
	_poner_cosas()
	if not Estado.tiene("estanterias_llegada"):
		_pensar_al_llegar.call_deferred()


func _poner_cosas() -> void:
	var filas: PackedStringArray = $Region._filas
	var carriles := {}                  # casillas de hueco que son de una escalera (no llevan pared fija)
	var n_escalera := 0
	for y in filas.size():
		for x in filas[y].length():
			var c := filas[y][x]
			var pos := Vector2(x, y) * 16.0 + Vector2(8, 14)
			if c == "ǝ":
				# la escalera: su carril sube desde la casilla de encima de «ǝ» hasta el final del hueco
				var largo := 0
				while y - 1 - largo >= 0 and filas[y - 1 - largo][x] == "ɵ":
					largo += 1
				var e: Node2D = ESCALERA.new()
				e.casillas = largo
				e.desfase = n_escalera * 2.3
				e.lado = -1 if x > filas[y].length() / 2 else 1
				e.position = Vector2(x, y) * 16.0
				add_child(e)
				n_escalera += 1
				for k in largo:
					carriles[Vector2i(x, y - 1 - k)] = true
					carriles[Vector2i(x + 1, y - 1 - k)] = true
			elif c == "ǜ":
				var t: CharacterBody2D = TINTERO.new()
				t.position = pos
				$Entidades.add_child(t)
			elif c == "ƥ":
				var p: CharacterBody2D = PAGINA.new()
				p.position = pos + Vector2(0, -4)
				$Entidades.add_child(p)
			elif c == "ẋ":
				var ch: StaticBody2D = CHARCO.new()
				ch.marca = "charco/estanterias/%d,%d" % [x, y]
				ch.position = pos
				$Entidades.add_child(ch)
			elif c == "ʣ":
				var ficha: Node2D = RECOGIBLE.new()
				ficha.objeto = "ficha_daftari"
				ficha.marca = "ficha/daftari"
				ficha.dibujo = "res://arte/mundos/sigilia/paso/ficha.png"
				ficha.color_halo = Color(0.85, 0.7, 1.0)
				ficha.position = pos
				$Entidades.add_child(ficha)
	_crear_huecos(filas, carriles)
	# el atril de la sala de lectura
	var atril := Sprite2D.new()
	atril.texture = ATRIL
	atril.centered = false
	atril.offset = Vector2(-20, -42)
	atril.position = Vector2(30, 6) * 16.0
	$Entidades.add_child(atril)


## Los huecos son paredes (salvo los carriles de las escaleras, que ponen la suya cuando no están tendidas)
func _crear_huecos(filas: PackedStringArray, carriles: Dictionary) -> void:
	var cuerpo := StaticBody2D.new()
	cuerpo.name = "Huecos"
	add_child(cuerpo)
	for y in filas.size():
		var x := 0
		while x < filas[y].length():
			if filas[y][x] != "ɵ" or carriles.has(Vector2i(x, y)):
				x += 1
				continue
			var x0 := x
			while x < filas[y].length() and filas[y][x] == "ɵ" and not carriles.has(Vector2i(x, y)):
				x += 1
			var forma := CollisionShape2D.new()
			var caja := RectangleShape2D.new()
			caja.size = Vector2((x - x0) * 16, 16)
			forma.shape = caja
			forma.position = Vector2((x0 + x) * 8.0, y * 16 + 8)
			cuerpo.add_child(forma)


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.4).timeout
	if not is_inside_tree() or Estado.tiene("estanterias_llegada"):
		return
	await CHARLA_SCRIPT.hablar(self, "estanterias_llegada")
	Estado.marcar("estanterias_llegada")
