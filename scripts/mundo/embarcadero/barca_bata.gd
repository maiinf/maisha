extends Node2D
## LA BARCA DE BATA en la pelea contra Mamba (2 contra 1). Bata rema alrededor de la plataforma de la dársena
## persiguiendo a Mamba. Cuando lo alcanza mientras acecha en el agua, lo SUJETA con la pértiga contra el borde de la
## plataforma («¡Lo tengo! ¡Dale!»): Mamba queda a tiro desde el borde un rato. En la fase 2, Mamba se revuelve y le
## muerde la barca: Bata se aparta asustado unos segundos. Lo crea mamba.gd al despertar (si Bata ya está libre).

const R := preload("res://scripts/combate/reglas_combate.gd")
const BARCA := preload("res://arte/mundos/raiz/embarcadero/barca_bata.png")
const BATA := preload("res://arte/personajes/aldeanos/bata_frente.png")
const RONDA := 1.22                       # su círculo, un poco más fuera que el de Mamba
const VELOCIDAD := 0.55                   # radianes por segundo, remando
const MURO := 0.45                        # no rema por el oeste (±PI), donde está la pasarela de la plataforma

var mamba: Node2D
var _angulo := -PI * 0.5
var _tiempo := 0.0
var _asustado := 0.0
var _pinchando := 0.0
var _espera := 3.0                        # entre sujeción y sujeción
var _barca: Sprite2D
var _bata: Sprite2D


func _ready() -> void:
	z_index = 1
	_barca = Sprite2D.new()
	_barca.texture = BARCA
	_barca.hframes = 2
	_barca.offset = Vector2(0, -13)
	add_child(_barca)
	_bata = Sprite2D.new()
	_bata.texture = BATA
	_bata.offset = Vector2(-2, -30)
	add_child(_bata)
	position = _en_ronda(_angulo)


func _centro() -> Vector2:
	return mamba.call("_centro")


func _en_ronda(a: float) -> Vector2:
	return _centro() + Vector2(cos(a) * R.MAMBA_RONDA.x, sin(a) * R.MAMBA_RONDA.y) * RONDA


func _process(delta: float) -> void:
	_tiempo += delta
	_asustado = maxf(0.0, _asustado - delta)
	_pinchando = maxf(0.0, _pinchando - delta)
	_espera = maxf(0.0, _espera - delta)
	if not is_instance_valid(mamba):
		return
	# rema hacia Mamba (o, asustado, lejos de él); no cruza el muelle del oeste (ángulo PI)
	var objetivo := wrapf(float(mamba.get("_angulo")) + (PI if _asustado > 0.0 else 0.0), -PI, PI)
	# (el ángulo va de -PI a PI, con el muelle justo en ±PI: así basta con no pasar de un extremo al otro)
	objetivo = clampf(objetivo, -PI + MURO, PI - MURO)
	var dif := objetivo - _angulo
	var paso := clampf(dif, -1.0, 1.0) * VELOCIDAD * (1.6 if _asustado > 0.0 else 1.0) * delta
	_angulo = clampf(_angulo + paso, -PI + MURO, PI - MURO)
	var antes := position
	position = _en_ronda(_angulo)
	_barca.flip_h = position.x < antes.x
	_barca.frame = int(_tiempo * 3.0) % 2
	_bata.position.y = sin(_tiempo * 3.0) * 0.8
	_barca.position.y = sin(_tiempo * 3.0) * 0.8
	# ¿lo alcanza? lo sujeta con la pértiga
	if _asustado <= 0.0 and _espera <= 0.0 and mamba.fase == mamba.Fase.ACECHA \
			and (mamba as Node2D).global_position.distance_to(global_position) < 34.0:
		_espera = 7.0
		_pinchando = 0.6
		mamba.call("sujetar", self)
	queue_redraw()


## Mamba se revuelve y le muerde la barca: se aparta asustado
func asustar() -> void:
	_asustado = 6.0
	var t := create_tween()
	for i in 6:
		t.tween_property(_barca, "rotation", 0.15 if i % 2 == 0 else -0.15, 0.06)
	t.tween_property(_barca, "rotation", 0.0, 0.06)


func _draw() -> void:
	# la pértiga: apoyada, o clavada hacia Mamba cuando lo sujeta
	var mano := Vector2(5, -20)
	var punta := mano + Vector2(18, 10)
	if is_instance_valid(mamba) and (mamba.fase == mamba.Fase.SUJETO or _pinchando > 0.0):
		var hacia := ((mamba as Node2D).global_position - global_position)
		punta = mano + hacia.normalized() * minf(hacia.length(), 46.0)
	draw_line(mano, punta, Color("3a2414"), 2.0)
	draw_line(mano, punta, Color("8a6440"), 1.0)
	if _asustado > 0.0:
		# gotitas de susto sobre la cabeza
		for k in 2:
			var p := Vector2(-6 + k * 8, -38 - fmod(_tiempo * 20.0 + k * 7.0, 6.0))
			draw_rect(Rect2(p.round(), Vector2(2, 3)), Color("9fd0d0"))
