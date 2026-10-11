extends Node
## GESTOR DE LA CORRUPCIÓN de una región: un único material (shader) compartido por el suelo
## y los objetos del mundo, con el gris general de la región y hasta 8 zonas corruptas.
## Al purgar todas las zonas, la región entera recupera el color.

signal region_purgada

const SHADER := preload("res://shaders/suelo_corrupcion.gdshader")
const MAX_ZONAS := 8
const FORMA := preload("res://scripts/combate/forma_zona.gd")

## Gris de la región antes de purgar nada (0 = color, 1 = todo gris)
@export_range(0.0, 1.0) var corrupcion_inicial := 0.0
## Si al purgar zonas se aviva toda la región (en el Kitovu no: allí cada mundo cura un trozo)
@export var purgar_aviva_region := true

var material := ShaderMaterial.new()
var _zonas: Array[Dictionary] = []
var _base := 0.0


func _ready() -> void:
	add_to_group("corrupcion")
	material.shader = SHADER
	_base = corrupcion_inicial
	_subir()


## Cualquier sprite del mundo (suelo, árboles, rocas...) que deba volverse gris
func aplicar_a(nodo: CanvasItem) -> void:
	nodo.material = material


## Un sitio que conserva el color aunque la región esté gris (p. ej. la granja de Mzee Shamba)
func registrar_oasis(centro: Vector2, radios: Vector2, borde: float) -> int:
	var i := registrar(centro, radios, borde)
	if i >= 0:
		_zonas[i]["purga"] = 101.0
		_zonas[i]["oasis"] = true
		_subir()
	return i


func registrar(centro: Vector2, radios: Vector2, borde: float, forma := PackedFloat32Array()) -> int:
	if _zonas.size() >= MAX_ZONAS:
		push_error("Corrupción: como mucho %d zonas por región" % MAX_ZONAS)
		return -1
	_zonas.append({"centro": centro, "radios": radios, "borde": borde, "purga": 0.0, "oasis": false, "forma": forma})
	_subir()
	return _zonas.size() - 1


func poner_purga(indice: int, radio: float) -> void:
	if indice < 0:
		return
	_zonas[indice]["purga"] = radio
	_subir()


## Zona purgada del todo: baja el gris de la región en proporción.
## «inmediato»: sin transición ni aviso (zonas que ya se purgaron en otra visita).
func purgar(indice: int, inmediato := false) -> void:
	if indice < 0:
		return
	# purgada: conserva el color hasta donde llegó la ola (el umbral más el borde)
	var z: Dictionary = _zonas[indice]
	_zonas[indice]["purga"] = 100.0 + 1.1 + z["borde"] / minf(z["radios"].x, z["radios"].y)
	var quedan := _quedan()
	var objetivo := _base_para(quedan)
	if inmediato:
		# las demás zonas de la región aún se están registrando: se calcula al final
		_ajustar_base.call_deferred()
		return
	create_tween().tween_method(_poner_base, _base, objetivo, 2.0)
	if quedan == 0 and _cuantas() > 0:
		region_purgada.emit()


## Cuánto gris hay en un punto (0 = color, 1 = gris). Lo usan, p. ej., las mariposas.
func gris_en(p: Vector2) -> float:
	var t := _base
	for z in _zonas:
		var n: Vector2 = (p - z["centro"]) / z["radios"]
		var r: float = n.length() / FORMA.factor(z["forma"], n)
		if z["purga"] > 50.0:
			if r < z["purga"] - 100.0:
				return 0.0
			continue
		if r < z["purga"]:
			return 0.0
		var n2: Vector2 = (p - z["centro"]) / (z["radios"] + Vector2.ONE * z["borde"])
		if z["purga"] < 50.0 and n2.length() / FORMA.factor(z["forma"], n2) < 1.0:
			t = maxf(t, 0.5 if r > 1.0 else 1.0)
	return t


func _ajustar_base() -> void:
	_poner_base(_base_para(_quedan()))


## Zonas de combate (sin contar los oasis) y las que quedan por purgar
func _cuantas() -> int:
	return _zonas.filter(func(z: Dictionary) -> bool: return not z["oasis"]).size()


func _quedan() -> int:
	return _zonas.filter(func(z: Dictionary) -> bool: return not z["oasis"] and z["purga"] < 50.0).size()


func _base_para(quedan: int) -> float:
	if not purgar_aviva_region:
		return corrupcion_inicial
	return corrupcion_inicial * float(quedan) / maxf(1.0, _cuantas())


func _poner_base(valor: float) -> void:
	_base = valor
	_subir()


func _subir() -> void:
	var centros := PackedVector2Array()
	var radios := PackedVector2Array()
	var bordes := PackedFloat32Array()
	var purgas := PackedFloat32Array()
	var formas := PackedFloat32Array()
	formas.resize(MAX_ZONAS * 8)
	for i in mini(_zonas.size(), MAX_ZONAS):
		var f: PackedFloat32Array = _zonas[i]["forma"]
		for k in mini(f.size(), 8):
			formas[i * 8 + k] = f[k]
	for i in MAX_ZONAS:
		if i < _zonas.size():
			centros.append(_zonas[i]["centro"])
			radios.append(_zonas[i]["radios"])
			bordes.append(_zonas[i]["borde"])
			purgas.append(_zonas[i]["purga"])
		else:
			centros.append(Vector2.ZERO)
			radios.append(Vector2.ONE)
			bordes.append(0.0)
			purgas.append(0.0)
	material.set_shader_parameter("num_zonas", _zonas.size())
	material.set_shader_parameter("centros", centros)
	material.set_shader_parameter("radios", radios)
	material.set_shader_parameter("bordes", bordes)
	material.set_shader_parameter("purgas", purgas)
	material.set_shader_parameter("formas", formas)
	material.set_shader_parameter("corrupcion_base", _base)
