extends "res://scripts/mundo/escena_mundo.gd"
## LA CUEVA DE LAS SETAS, bajo la casa de Nungu (se baja por la escalera del armario). A oscuras: alumbran Maisha y las
## SETAS que brillan («ů», verde-agua y violetas). Las NUBES DE ESPORAS («ǯ», nube_esporas.gd) marean; las tres
## PÁGINAS del diario de Nungu («ǹ», pagina_nungu.gd) cuentan qué le pasó; al este, el OCTAVO ECO; al sur, la
## CORTINA DE MICELIO («ǫ») que tapa la sala de Kuvu, la seta que manda.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const OSCURIDAD := preload("res://scripts/mundo/gruta/oscuridad.gd")
const NUBE := preload("res://scripts/mundo/cueva/nube_esporas.gd")
const PAGINA := preload("res://scripts/mundo/cueva/pagina_nungu.gd")
const SETA := preload("res://arte/mundos/raiz/paso/seta_luz.png")
const CORTINA := preload("res://arte/mundos/raiz/paso/cortina.png")
const PENUMBRA := Color(0.11, 0.09, 0.15)

var _setas: Array[PointLight2D] = []
var _cortina: Sprite2D
var _tiempo := 0.0


func _ready() -> void:
	super()
	_oscurecer()
	_poner_cosas()
	_maisha.caida.connect(_al_caer)
	if not Estado.tiene("cueva_llegada"):
		_pensar_al_llegar.call_deferred()


func _oscurecer() -> void:
	var penumbra := CanvasModulate.new()
	penumbra.color = PENUMBRA
	add_child(penumbra)
	var luz := PointLight2D.new()
	luz.texture = OSCURIDAD.textura_luz()
	luz.texture_scale = 1.3
	luz.energy = 1.15
	luz.color = Color(1.0, 0.92, 0.75)
	luz.position = Vector2(0, -10)
	_maisha.add_child(luz)


func _poner_cosas() -> void:
	var filas: PackedStringArray = $Region._filas
	var tex := OSCURIDAD.textura_luz()
	var paginas := 0
	for y in filas.size():
		var fila := filas[y]
		for x in fila.length():
			var c := fila[x]
			var pos := Vector2(x, y) * 16.0 + Vector2(8, 14)
			if c == "ů":
				var k := (x * 7 + y * 3) % 4
				var s := Sprite2D.new()
				s.texture = SETA
				s.hframes = 4
				s.frame = k
				s.offset = Vector2(0, -8)
				s.position = pos
				var luz := PointLight2D.new()
				luz.texture = tex
				luz.texture_scale = 0.6
				luz.color = Color(0.4, 0.95, 0.8) if k < 2 else Color(0.72, 0.45, 0.95)
				luz.energy = 0.85
				luz.position = Vector2(0, -10)
				luz.set_meta("fase", float(x * 5 + y * 3) * 0.41)
				s.add_child(luz)
				$Entidades.add_child(s)
				_setas.append(luz)
			elif c == "ǯ":
				var nube: Node2D = NUBE.new()
				nube.position = pos + Vector2(0, -6)
				$Entidades.add_child(nube)
			elif c == "ǹ":
				paginas += 1
				var p: Node2D = PAGINA.new()
				p.numero = paginas
				p.position = pos
				$Entidades.add_child(p)
			elif c == "ǫ" and (x == 0 or fila[x - 1] != "ǫ") and _cortina == null:
				_crear_cortina(filas, y)


## La cortina de micelio: tapa todo el paso (las «ǫ» de su fila y el hueco de en medio)
func _crear_cortina(filas: PackedStringArray, y: int) -> void:
	var xs: Array[int] = []
	for x in filas[y].length():
		if filas[y][x] == "ǫ":
			xs.append(x)
	var centro := Vector2((xs.min() + xs.max() + 1) * 8.0, y * 16.0 + 14)
	var cuerpo := StaticBody2D.new()
	cuerpo.add_to_group("cortina")
	cuerpo.position = centro
	var forma := CollisionShape2D.new()
	var caja := RectangleShape2D.new()
	caja.size = Vector2((xs.max() - xs.min() + 1) * 16.0, 14)
	forma.shape = caja
	forma.position = Vector2(0, -6)
	cuerpo.add_child(forma)
	_cortina = Sprite2D.new()
	_cortina.texture = CORTINA
	_cortina.hframes = 2
	_cortina.offset = Vector2(0, -20)
	_cortina.modulate = Color(0.75, 0.7, 0.8)
	cuerpo.add_child(_cortina)
	var luz := PointLight2D.new()
	luz.texture = OSCURIDAD.textura_luz()
	luz.texture_scale = 0.6
	luz.color = Color(0.7, 0.4, 0.95)
	luz.energy = 0.35
	luz.position = Vector2(0, -20)
	cuerpo.add_child(luz)
	var cosa := Node2D.new()
	cosa.set_script(load("res://scripts/mundo/objetos/cosa.gd"))
	cosa.set("charla", "cueva_cortina")
	cosa.set("radio_interaccion", 36.0)
	cuerpo.add_child(cosa)
	$Entidades.add_child(cuerpo)


func _process(delta: float) -> void:
	_tiempo += delta
	# las setas respiran despacio, cada una a su ritmo
	for luz in _setas:
		luz.energy = 0.85 + 0.3 * sin(_tiempo * 1.4 + float(luz.get_meta("fase")))
	if _cortina:
		_cortina.frame = 1 if fmod(_tiempo, 2.4) < 0.6 else 0


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.2).timeout
	if not is_inside_tree() or Estado.tiene("cueva_llegada"):
		return
	Estado.marcar("cueva_llegada")
	await CHARLA_SCRIPT.hablar(self, "cueva_llegada")


func _al_caer() -> void:
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))
