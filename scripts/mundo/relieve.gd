extends Node
## RELIEVE Y LUZ (el 2.5D de Maisha): da volumen a los dibujos con luz, sin tocar colisiones ni movimiento.
## La lógica del juego sigue siendo 2D plana y no sabe que esto existe. Lo pone escena_mundo.gd en todas las escenas.
##   - RELIEVE: cada dibujo con su «mapa de normales» (<dibujo>_n.png, lo hace herramientas/relieve.py) pasa a ser
##     una CanvasTexture (el dibujo más hacia dónde mira cada píxel), y la luz resbala por tejados, copas y piedras.
##   - HORA DEL DÍA (solo en los exteriores; la lleva el autoload Reloj): de día, un sol bajo desde arriba a la
##     izquierda; al atardecer, la luz se vuelve naranja; de noche, una luna azulada y todo más oscuro.
##   - LUCES DE NOCHE: las ventanas, faroles y fuegos de cada edificio (tabla LUCES) y los faroles de la aldea se
##     encienden al anochecer; las hogueras también. Alrededor de Maisha, una luz suave para que se juegue bien.
##   - Si la escena tiene su propia penumbra (las cuevas, la Gruta, el amanecer del Kitovu, la casa de Shamba), el
##     ciclo se aparta mientras dure: allí mandan sus luces, que también ven el relieve.
##   - Relieve.destello(...): un fogonazo de luz (semillas que estallan, el Latido, el golpe del cetro).

const DIA := Color(0.86, 0.86, 0.92)
const TARDE := Color(0.8, 0.63, 0.7)
const NOCHE := Color(0.2, 0.24, 0.45)
const SOL_DIA := Color(1.0, 0.92, 0.76)
const SOL_TARDE := Color(1.0, 0.66, 0.42)
const LUNA := Color(0.62, 0.72, 1.0)
const CALIDO := Color(1.0, 0.74, 0.4)
const FUEGO := Color(1.0, 0.55, 0.22)

## Las luces de cada edificio: [tipo, x, y] en píxeles del dibujo entero (si tiene varios fotogramas, solo se
## encienden las del fotograma que se ve). Tipos: v ventana · f farol · h fuego (hoguera, forja, caldero)
const LUCES := {
	"casa_seta.png": [["v", 166, 90], ["v", 196, 96], ["f", 195, 112]],
	"taller.png": [["v", 217, 77], ["v", 238, 77], ["h", 174, 120], ["f", 242, 107]],
	"cocina.png": [["v", 195, 90], ["h", 149, 118]],
	"puesto.png": [["f", 143, 46], ["f", 174, 46], ["f", 203, 46]],
	"gran_arbol.png": [["v", 98, 122], ["v", 88, 186], ["f", 66, 158]],
	"campamento.png": [["f", 52, 28]],
	"palafito.png": [["f", 27, 51], ["v", 47, 52], ["v", 81, 53]],
	"madriguera.png": [["v", 29, 66], ["f", 59, 68], ["f", 85, 68]],
	"horreo.png": [["v", 58, 58]],
	"aprisco.png": [["v", 30, 92], ["f", 75, 85], ["f", 42, 82]],
	"casa_barcas.png": [["v", 55, 50], ["f", 113, 48]],
	"casa_bata.png": [["v", 52, 43], ["f", 10, 51]],
	"casa_juncos.png": [["v", 55, 43], ["v", 127, 43], ["f", 185, 37]],
	"farol.png": [["f", 4, 4]],
}
## Los edificios que cambian de fotograma al reconstruirse (ruina → casa): sus luces se rehacen con el fotograma.
## (El farol cambia de fotograma para que la llama tiemble: ahí la luz se queda donde está.)
const CAMBIAN_AL_RECONSTRUIRSE := ["casa_seta.png", "taller.png", "cocina.png", "puesto.png"]
## Dibujos cuyos fotogramas son solo una animación (la llama del farol): sus luces van siempre con el primero
const ANIMADOS := ["farol.png"]
## Por tipo: [tamaño de la luz, fuerza, color]
const TIPOS := {"v": [0.34, 0.9, CALIDO], "f": [0.62, 1.0, CALIDO], "h": [0.8, 1.15, FUEGO]}

@export var fuerza_sol := 0.6
@export var altura_sol := 0.25          # 0 = rasante (mucho relieve), 1 = desde arriba (casi nada)

var exterior := false                   # ¿hay ciclo de día y noche aquí?
var _sombra: CanvasModulate
var _sol: DirectionalLight2D
var _luz_maisha: PointLight2D
var _de_noche: Array[Dictionary] = []   # {"luz": PointLight2D, "fuerza": float, "fuego": bool}
var _ajenas := 0                        # penumbras propias de la escena (mientras haya, el ciclo se aparta)
var _tiempo := 0.0
var _cache := {}                        # ruta del dibujo -> CanvasTexture con relieve (o null)
var _textura_luz_cache: GradientTexture2D


## Para comparar (capturas): con esto a true, las escenas nuevas salen sin relieve ni luz
static var desactivado := false


func _ready() -> void:
	if desactivado:
		return
	exterior = get_parent().scene_file_path.begins_with("res://escenas/mundo/")
	_aplicar.call_deferred()


func _aplicar() -> void:
	var escena := get_parent()
	for n in escena.find_children("*", "", true, false):
		_al_entrar(n)
	get_tree().node_added.connect(_al_entrar)
	if exterior:
		_sombra = CanvasModulate.new()
		_sombra.name = "LuzDelDia"
		_sombra.color = DIA
		escena.add_child(_sombra)
		_sol = DirectionalLight2D.new()
		_sol.name = "Sol"
		_sol.height = altura_sol
		escena.add_child(_sol)
		var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
		if maisha:
			_luz_maisha = _nueva_luz(Color(0.8, 0.88, 1.0), 1.15)
			_luz_maisha.position = Vector2(0, -10)
			maisha.add_child(_luz_maisha)
	_actualizar_luz()


## Cada nodo que aparece: si es un dibujo, su relieve y sus luces; si es otra penumbra, el ciclo se aparta
func _al_entrar(n: Node) -> void:
	if n is Sprite2D:
		_dar_relieve.call_deferred(n)
	elif n is CanvasModulate and n != _sombra and not (n.name == "LuzDelDia"):
		_ajenas += 1
		n.tree_exiting.connect(_al_irse_penumbra, CONNECT_ONE_SHOT)
	elif n is PointLight2D and is_zero_approx((n as PointLight2D).height):
		# las luces de la escena (setas de la cueva, la Gruta...) a ras de suelo apenas tocarían lo que tiene relieve
		(n as PointLight2D).height = 24.0
	elif n.get_script() != null and String((n.get_script() as Script).resource_path).ends_with("/fogata.gd"):
		_poner_luz.call_deferred(n, Vector2(0, -4), "h")


func _al_irse_penumbra() -> void:
	_ajenas -= 1


## Cambia la textura del dibujo por la misma con su relieve (si lo tiene) y le pone las luces de su tabla
func _dar_relieve(s: Sprite2D) -> void:
	if not is_instance_valid(s) or s.texture == null or s.has_meta("relieve"):
		return
	var tex := s.texture
	var ruta := tex.resource_path
	if ruta == "":
		return
	s.set_meta("relieve", true)
	if not _cache.has(ruta):
		_cache[ruta] = null
		var ruta_n := ruta.get_basename() + "_n.png"
		if ResourceLoader.exists(ruta_n):
			var con_relieve := CanvasTexture.new()
			con_relieve.diffuse_texture = tex
			con_relieve.normal_texture = load(ruta_n)
			con_relieve.resource_name = ruta      # (para quien quiera saber qué dibujo es)
			_cache[ruta] = con_relieve
	if _cache[ruta] != null:
		s.texture = _cache[ruta]
	var puntos: Array = LUCES.get(ruta.get_file(), [])
	if puntos.is_empty():
		return
	_luces_de(s, tex, puntos)
	if ruta.get_file() in CAMBIAN_AL_RECONSTRUIRSE:
		s.frame_changed.connect(_luces_de.bind(s, tex, puntos))


## Las luces del fotograma que se ve (un edificio en ruinas no tiene las ventanas encendidas)
func _luces_de(s: Sprite2D, tex: Texture2D, puntos: Array) -> void:
	for h in s.get_children():
		if h.has_meta("luz_edificio"):
			_de_noche = _de_noche.filter(func(d: Dictionary) -> bool: return d["luz"] != h)
			h.queue_free()
	var tam_fotograma := tex.get_size() / Vector2(s.hframes, s.vframes)
	# (los demás dibujos de varios fotogramas son variantes: la casa de juncos de un lado o del otro)
	var fotograma := 0 if tex.resource_path.get_file() in ANIMADOS else s.frame
	var esquina := Vector2(fotograma % s.hframes, fotograma / s.hframes) * tam_fotograma
	var origen := (-tam_fotograma / 2.0 if s.centered else Vector2.ZERO) + s.offset
	for p in puntos:
		var en_dibujo := Vector2(p[1], p[2])
		if not Rect2(esquina, tam_fotograma).has_point(en_dibujo):
			continue
		var local := origen + (en_dibujo - esquina)
		if s.flip_h:
			local.x = -local.x if s.centered else tam_fotograma.x - local.x
		var luz := _poner_luz(s, local, String(p[0]))
		luz.set_meta("luz_edificio", true)


func _poner_luz(padre: Node, pos: Vector2, tipo: String) -> PointLight2D:
	var t: Array = TIPOS[tipo]
	var luz := _nueva_luz(t[2], t[0])
	luz.position = pos
	luz.energy = 0.0
	luz.visible = false
	padre.add_child(luz)
	_de_noche.append({"luz": luz, "fuerza": t[1], "fuego": tipo == "h", "fase": randf() * TAU})
	return luz


func _nueva_luz(color: Color, escala: float) -> PointLight2D:
	var luz := PointLight2D.new()
	luz.color = color
	luz.texture = _textura_luz()
	luz.texture_scale = escala
	luz.height = 16.0
	return luz


## Un círculo de luz que se apaga hacia el borde por escalones suaves
func _textura_luz() -> GradientTexture2D:
	if _textura_luz_cache:
		return _textura_luz_cache
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.3, 0.62, 1.0])
	g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(1, 1, 1, 0.6), Color(1, 1, 1, 0.2), Color(1, 1, 1, 0)])
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5)
	t.fill_to = Vector2(1.0, 0.5)
	t.width = 112
	t.height = 112
	_textura_luz_cache = t
	return t


func _process(delta: float) -> void:
	_tiempo += delta
	_actualizar_luz()


## La luz según la hora: el color del mundo, el sol (o la luna) y las luces de noche
func _actualizar_luz() -> void:
	var ciclo := exterior and _ajenas <= 0
	var dia := Reloj.luz_dia() if ciclo else 1.0
	var calido := Reloj.calidez() if ciclo else 0.0
	# (en un interior iluminado, los fogonazos se notan a medias)
	Reloj.oscuridad = 1.0 if _ajenas > 0 else (0.3 if not exterior else 1.0 - dia)
	if not exterior:
		return
	_sombra.visible = ciclo
	_sol.visible = ciclo
	if ciclo:
		var base := NOCHE.lerp(DIA, dia).lerp(TARDE, calido * 0.6)
		_sombra.color = base
		# de día y al atardecer, el sol (desde arriba a la izquierda); de noche, la luna (desde arriba a la derecha)
		if dia > 0.25:
			_sol.color = SOL_DIA.lerp(SOL_TARDE, calido)
			_sol.energy = fuerza_sol * clampf((dia - 0.25) / 0.35, 0.0, 1.0)
			_sol.rotation_degrees = -45.0
			_sol.height = altura_sol - calido * 0.1
		else:
			_sol.color = LUNA
			_sol.energy = 0.26 * clampf((0.25 - dia) / 0.25, 0.0, 1.0)
			_sol.rotation_degrees = 40.0
			_sol.height = 0.4
	var noche := 1.0 - dia if ciclo else 0.0
	var encendidas := smoothstep(0.15, 0.6, noche)
	for d in _de_noche:
		var luz: PointLight2D = d["luz"]
		if not is_instance_valid(luz):
			continue
		var vacila := 0.12 * sin(_tiempo * (7.0 if d["fuego"] else 2.0) + d["fase"]) \
				+ (0.08 * sin(_tiempo * 13.0 + d["fase"] * 2.0) if d["fuego"] else 0.0)
		luz.energy = float(d["fuerza"]) * encendidas * (1.0 + vacila)
		luz.visible = luz.energy > 0.02
	if _luz_maisha and is_instance_valid(_luz_maisha):
		_luz_maisha.energy = 0.38 * encendidas
		_luz_maisha.visible = _luz_maisha.energy > 0.02


## Un fogonazo de luz que se apaga solo (semillas, Latido, golpe). Se nota más cuanto más oscuro está.
static func destello(padre: Node, pos: Vector2, color: Color, escala: float, fuerza: float, dura: float) -> void:
	if padre == null or not padre.is_inside_tree():
		return
	var oscuro: float = padre.get_tree().root.get_node("Reloj").get("oscuridad")
	var energia := fuerza * (0.25 + 0.75 * oscuro)
	if energia < 0.05:
		return
	var luz := PointLight2D.new()
	luz.color = color
	luz.texture_scale = escala
	luz.height = 20.0
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.45, 1.0])
	g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(1, 1, 1, 0.35), Color(1, 1, 1, 0)])
	var t := GradientTexture2D.new()
	t.gradient = g
	t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5)
	t.fill_to = Vector2(1.0, 0.5)
	t.width = 96
	t.height = 96
	luz.texture = t
	luz.position = pos
	luz.energy = energia
	padre.add_child(luz)
	var tw := luz.create_tween()
	tw.tween_property(luz, "energy", 0.0, dura).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_callback(luz.queue_free)
