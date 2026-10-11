class_name SueloPrado
## Genera el suelo de un prado de Raíz (provisional hasta tener el tileset dibujado).
## Usa solo colores de la paleta oficial: Hierba 2, 3 y 4 y las flores de Raíz.

const HIERBA_OSCURA := Color("3f582f")   # Hierba 2
const HIERBA := Color("6a8246")          # Hierba 3
const HIERBA_CLARA := Color("9aa95f")    # Hierba 4
const FLORES := [Color("e6a852"), Color("de6771"), Color("fff3c4")]   # Flor ámbar 3, Flor roja 3, Maisha 4
const CASILLA := 16


## Devuelve una textura con todo el prado (ancho x alto casillas), lista para un Sprite2D
static func generar(ancho: int, alto: int, semilla: int = 7) -> ImageTexture:
	var azar := RandomNumberGenerator.new()
	azar.seed = semilla
	var variantes: Array[Image] = []
	for v in 6:
		variantes.append(_casilla(azar, v))
	var img := Image.create(ancho * CASILLA, alto * CASILLA, false, Image.FORMAT_RGBA8)
	var zona := Rect2i(0, 0, CASILLA, CASILLA)
	for y in alto:
		for x in ancho:
			var v := (x * 7 + y * 13 + (x * y) % 5) % 6
			if v == 5 and azar.randf() < 0.6:
				v = 0                       # pocas casillas con flores
			img.blit_rect(variantes[v], zona, Vector2i(x * CASILLA, y * CASILLA))
	return ImageTexture.create_from_image(img)


static func _casilla(azar: RandomNumberGenerator, variante: int) -> Image:
	var img := Image.create(CASILLA, CASILLA, false, Image.FORMAT_RGBA8)
	img.fill(HIERBA)
	# motas oscuras sueltas
	for k in 5:
		img.set_pixel(azar.randi_range(0, 15), azar.randi_range(0, 15), HIERBA_OSCURA)
	# matas de hierba: punta clara y base oscura
	for k in 3:
		var x := azar.randi_range(1, 13)
		var y := azar.randi_range(2, 14)
		img.set_pixel(x, y, HIERBA_CLARA)
		img.set_pixel(x + 1, y - 1, HIERBA_CLARA)
		img.set_pixel(x, y + 1, HIERBA_OSCURA)
		img.set_pixel(x + 1, y + 1, HIERBA_OSCURA)
	if variante == 5:
		for k in 2:
			var x := azar.randi_range(2, 13)
			var y := azar.randi_range(2, 13)
			img.set_pixel(x, y, FLORES[(k + variante) % FLORES.size()])
			img.set_pixel(x, y + 1, HIERBA_OSCURA)
	return img
