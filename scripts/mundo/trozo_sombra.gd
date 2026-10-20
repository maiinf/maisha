extends Node2D
## Un TROZO DE SOMBRA: las sombras de los árboles y rocas de un trozo del mapa (las pone region.gd), juntas en UNA
## malla a ras de suelo: una sola llamada de dibujo por trozo. (Antes cada árbol tenía la suya, un polígono suelto
## entre su dibujo y el del vecino: una llamada por sombra y además partía los lotes de dibujo de los árboles.)
## Las elipses son las de sombra.gd (los mismos puntos y color), y Godot salta los trozos que no se ven.
## Se rehace solo cuando el sol se mueve lo bastante (Reloj.luz_cambiada), con la misma regla que sombra.gd.
## (El nombre acaba en «sombra.gd» a propósito: el espejo HD-2D esconde esas sombras pintadas, porque allí las hay de verdad.)

const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const FUERZA := 0.35                    # la de sombra.gd por defecto

var centros := PackedVector2Array()     # (relativos al trozo)
var anchos := PackedFloat32Array()
var _malla := ArrayMesh.new()
var _ultimo_desp := Vector2.ZERO


func _ready() -> void:
	_ultimo_desp = SOMBRA.desplazamiento()
	_rehacer.call_deferred()              # (cuando la región ya ha puesto todas sus sombras)
	Reloj.luz_cambiada.connect(_al_cambiar_luz)


func _al_cambiar_luz() -> void:
	var desp := SOMBRA.desplazamiento()
	if desp.distance_squared_to(_ultimo_desp) > 0.02:
		_ultimo_desp = desp
		_rehacer()


## Cada elipse en abanico (12 triángulos; el polígono es convexo, así que tapa justo lo mismo que el de sombra.gd)
func _rehacer() -> void:
	_malla.clear_surfaces()
	queue_redraw()
	if centros.is_empty():
		return
	var vertices := PackedVector2Array()
	var color := SOMBRA.color(FUERZA)
	for i in centros.size():
		var p := SOMBRA.puntos(centros[i], anchos[i])
		for k in range(1, p.size() - 1):
			vertices.append_array([p[0], p[k], p[k + 1]])
	var colores := PackedColorArray()
	colores.resize(vertices.size())
	colores.fill(color)
	var datos := []
	datos.resize(Mesh.ARRAY_MAX)
	datos[Mesh.ARRAY_VERTEX] = vertices
	datos[Mesh.ARRAY_COLOR] = colores
	_malla.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, datos)


func _draw() -> void:
	draw_mesh(_malla, null)
