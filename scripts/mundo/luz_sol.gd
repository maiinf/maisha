extends CanvasLayer
## LUZ DEL SOL en la pantalla: rayos que entran en diagonal desde arriba, se mecen despacio y
## laten un poco, y una viñeta suave en las esquinas. Más cálidos donde hay color; más fríos y
## débiles donde Giza lo ha dejado todo gris.

const RAYOS := 5
var _tiempo := 0.0
var _lienzo: Node2D
var _vineta: TextureRect
var _calidez := 1.0            # 1 = al sol con color; 0 = gris


func _ready() -> void:
	layer = 3
	_lienzo = Node2D.new()
	var suma := CanvasItemMaterial.new()
	suma.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	_lienzo.material = suma
	_lienzo.draw.connect(_dibujar)
	add_child(_lienzo)
	# viñeta: un degradado radial transparente en el centro y oscuro en las esquinas
	var grad := Gradient.new()
	grad.set_color(0, Color(0, 0, 0, 0))
	grad.set_color(1, Color(0.03, 0.02, 0.06, 0.38))
	grad.add_point(0.62, Color(0, 0, 0, 0))
	var tex := GradientTexture2D.new()
	tex.gradient = grad
	tex.fill = GradientTexture2D.FILL_RADIAL
	tex.fill_from = Vector2(0.5, 0.5)
	tex.fill_to = Vector2(1.08, 1.08)
	tex.width = 128
	tex.height = 72
	_vineta = TextureRect.new()
	_vineta.texture = tex
	_vineta.stretch_mode = TextureRect.STRETCH_SCALE
	_vineta.set_anchors_preset(Control.PRESET_FULL_RECT)
	_vineta.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_vineta)


func _process(delta: float) -> void:
	_tiempo += delta
	# ¿hay color alrededor de Maisha?
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	var gestor := get_tree().get_first_node_in_group("corrupcion")
	var objetivo := 1.0
	if maisha and gestor:
		objetivo = 1.0 - clampf(gestor.gris_en(maisha.global_position), 0.0, 1.0)
	_calidez = move_toward(_calidez, objetivo, delta * 0.5)
	_lienzo.queue_redraw()


func _dibujar() -> void:
	var tam := Vector2(640, 360)
	var caliente := Color(1.0, 0.86, 0.55)
	var frio := Color(0.55, 0.6, 0.75)
	var color := frio.lerp(caliente, _calidez)
	var fuerza := lerpf(0.05, 0.12, _calidez)
	var inclina := Vector2(150, tam.y + 40)          # los rayos bajan hacia la derecha
	for i in RAYOS:
		var fase := i * 1.7
		var x := -120.0 + i * 150.0 + sin(_tiempo * 0.07 + fase) * 40.0
		var ancho := 26.0 + 16.0 * sin(fase * 2.3)
		var a := fuerza * (0.55 + 0.45 * sin(_tiempo * 0.35 + fase))
		var arriba := Vector2(x, -20)
		var abajo := arriba + inclina
		# un rayo: borde transparente, centro con luz, borde transparente (dos tiras)
		var c0 := Color(color, 0.0)
		var c1 := Color(color, a)
		var izq := Vector2(-ancho / 2.0, 0)
		var der := Vector2(ancho / 2.0, 0)
		# la luz se apaga hacia abajo
		var c1b := Color(color, a * 0.25)
		_lienzo.draw_polygon(PackedVector2Array([arriba + izq, arriba, abajo, abajo + izq]),
			PackedColorArray([c0, c1, c1b, c0]))
		_lienzo.draw_polygon(PackedVector2Array([arriba, arriba + der, abajo + der, abajo]),
			PackedColorArray([c1, c0, c0, c1b]))
