extends Node2D
## RAÍZ DORMIDA (el pasillo de la Gruta de las Raíces, «ŕ» en el mapa): una raíz enorme atravesada de pared a pared,
## que duerme y ronca. Se puede pasar por encima andando. Pero el RUIDO la despierta: correr cerca, golpear con el
## cetro, una semilla o el Latido a su lado.
##   - Con un poco de ruido SE INQUIETA: abre su ojo violeta (el aviso). Si el ruido para, se vuelve a dormir.
##   - Si sigue el ruido, AZOTA: se levanta en arco y da un latigazo a lo largo del pasillo (daño y empujón).
##   - Luego vuelve a dormirse.
## Dibujo: arte/mundos/raiz/gruta/raiz_dormida.png (0-1 dormida, 2 despertando, 3 azotando).

const DIBUJO := preload("res://arte/mundos/raiz/gruta/raiz_dormida.png")
const OSCURIDAD := preload("res://scripts/mundo/gruta/oscuridad.gd")
const OIDO := 74.0                         # hasta dónde oye
const ALCANCE := 40.0                      # hasta dónde llega el latigazo
const PACIENCIA := 0.55                    # segundos de ruido seguido antes de azotar

enum Fase { DUERME, INQUIETA, AZOTA, VUELVE }

var fase: int = Fase.DUERME
var _ruido := 0.0
var _t := 0.0
var _tiempo := 0.0
var _ronquido := 0.0
var _espera_latido_antes := 0.0
var _pillo := false
var _sprite: Sprite2D
var _ojo: PointLight2D


func _ready() -> void:
	add_to_group("raices_dormidas")
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 4
	_sprite.offset = Vector2(0, -12)
	_sprite.scale = Vector2(1.25, 1.25)
	add_child(_sprite)
	# el ojo violeta da luz cuando se despierta (en la oscuridad, es el aviso)
	_ojo = PointLight2D.new()
	_ojo.texture = OSCURIDAD.textura_luz()
	_ojo.texture_scale = 0.35
	_ojo.color = Color(0.75, 0.45, 1.0)
	_ojo.energy = 0.0
	_ojo.position = Vector2(0, -20)
	add_child(_ojo)
	_tiempo = randf() * 3.0


## ¿Hace Maisha ruido cerca? (correr, golpear, una semilla o el Latido)
func _hay_ruido(maisha: Node2D) -> bool:
	var cerca := maisha.global_position.distance_to(global_position) < OIDO
	var espera := float(maisha.get("_espera_latido"))
	var latido := espera > _espera_latido_antes + 0.5
	_espera_latido_antes = espera
	if cerca and (bool(maisha.get("corriendo")) or bool(maisha.get("_golpeando")) or latido):
		return true
	for s in get_tree().get_nodes_in_group("semillas"):
		if (s as Node2D).global_position.distance_to(global_position) < OIDO:
			return true
	return false


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var ruido := _hay_ruido(maisha)
	match fase:
		Fase.DUERME:
			_sprite.frame = int(_tiempo * 0.8) % 2
			_ronquido -= delta
			if _ronquido <= 0.0 and maisha.global_position.distance_to(global_position) < 160.0:
				_ronquido = 3.2
				Sonido.efecto("raiz_ronca", 0.0, global_position)
			if ruido:
				fase = Fase.INQUIETA
				_t = 0.0
				_ruido = 0.0
				Sonido.efecto("raiz_despierta", 0.0, global_position)
		Fase.INQUIETA:
			_sprite.frame = 2
			_ruido = _ruido + delta if ruido else maxf(0.0, _ruido - delta * 0.6)
			if _ruido >= PACIENCIA:
				fase = Fase.AZOTA
				_t = 0.0
				_pillo = false
				Sonido.efecto("raiz_azota", 0.0, global_position)
				Impacto.temblar(2.5, 0.3)
			elif not ruido and _t > 1.4:
				fase = Fase.DUERME
		Fase.AZOTA:
			_sprite.frame = 3
			if not _pillo and _t > 0.12 and maisha.global_position.distance_to(global_position) < ALCANCE:
				_pillo = true
				maisha.call("recibir_danio", 1, global_position, "contacto")
			if _t > 0.7:
				fase = Fase.VUELVE
				_t = 0.0
		Fase.VUELVE:
			_sprite.frame = 2
			if _t > 1.2:
				fase = Fase.DUERME
	var luz := {Fase.DUERME: 0.0, Fase.INQUIETA: 0.9, Fase.AZOTA: 1.4, Fase.VUELVE: 0.6}[fase] as float
	_ojo.energy = move_toward(_ojo.energy, luz, delta * 4.0)
	queue_redraw()


func _draw() -> void:
	if fase == Fase.DUERME:
		# zzz: tres letras que suben despacio
		for k in 3:
			var f := fmod(_tiempo * 0.45 + k * 0.33, 1.0)
			var p := Vector2(6 + f * 8.0, -20 - f * 18.0)
			var c := Color(0.85, 0.8, 0.95, (1.0 - f) * 0.7)
			draw_line(p, p + Vector2(4, 0), c, 1.0)
			draw_line(p + Vector2(4, 0), p + Vector2(0, 4), c, 1.0)
			draw_line(p + Vector2(0, 4), p + Vector2(4, 4), c, 1.0)
	elif fase == Fase.AZOTA:
		# el latigazo: un arco de aire a lo largo del pasillo
		var f := clampf(_t / 0.3, 0.0, 1.0)
		draw_arc(Vector2(0, -10), ALCANCE * f, PI * 0.15, PI * 0.85, 16, Color(0.85, 0.75, 1.0, 1.0 - f), 2.0)
		draw_arc(Vector2(0, -10), ALCANCE * f, -PI * 0.85, -PI * 0.15, 16, Color(0.85, 0.75, 1.0, 1.0 - f), 2.0)
