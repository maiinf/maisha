extends Node
## Graba en vídeo la pelea contra la Cosechadora Oxidada, jugando solo:
## Maisha planta semillas en el camino de la máquina para atascarla; atascada, deja una semilla bajo el techo y golpea
## la caldera; cuando avisa de un acelerón, la espera junto al borde y golpea el depósito frontal al estrellarse;
## y con el corazón al aire, esquiva los anillos con el Latido y lo golpea cuando se abre.
## (Para que el vídeo no se corte, si le quedan 2 hojas o menos, recupera la vida: es una grabación, no una prueba.)
## En el Mac, desde la carpeta del proyecto:
##   godot --path . --resolution 640x360 --fixed-fps 30 --write-movie pelea.avi res://pruebas/ejecutar.tscn -- grabar_cosechadora

const R := preload("res://scripts/combate/reglas_combate.gd")

var _modo := "entrar"
var _t := 0.0
var _objetivo := Vector2.ZERO
var _arena: Node2D
var _cos: Node2D
var _maisha: Node2D
var _espera_golpe := 0.0
var _golpes := 0
var _fin := 0.0
var _total := 0.0
var _atascos := 0
var _danio_recibido := 0
var _vida_antes := -1
var _ultima_fase := -1
var _semilla_techo := false
var _plantar_en := Vector2.INF
var _plantar_mira := 1.0
var _partes_antes := ""
var _tiro_techo := false
var _choque_techo := Vector2.ZERO
var _por_fase := {}
const DURACION_MAXIMA := 200.0      # segundos de juego: pase lo que pase, la grabación termina


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Estado.olvidar_todo()
	for m in ["kitovu_despierta", "kuku_devuelta", "cetro_recibido", "mapa_partido", "bibi_conocida", "bibi_meditar", "camino_bosque",
			"camino_cienaga", "zona/bosque_cobrizo/4", "zona/cienaga_quieta/4", "camino_campo", "campo_llegada", "visto/campo_segado",
			"ayuda/WASD mover · C correr · J golpe · K semilla · L latido"]:
		Estado.marcar(m)
	Estado.extra["artes"] = {"raiz": 2, "aliento": 3}
	Estado.jugando = true
	Estado.llegada = "aldea"
	get_tree().change_scene_to_file("res://escenas/mundo/campo_segado.tscn")


func _suelta() -> void:
	for a in ["mover_arriba", "mover_abajo", "mover_izquierda", "mover_derecha", "correr"]:
		Input.action_release(a)


## Anda hacia un punto (con las teclas, para que se vean las animaciones). true si ya ha llegado.
func _ir(p: Vector2) -> bool:
	var d := p - _maisha.global_position
	_suelta()
	if d.length() < 5.0:
		return true
	if d.length() > 20.0:
		Input.action_press("correr")
	if d.x > 3.0:
		Input.action_press("mover_derecha")
	elif d.x < -3.0:
		Input.action_press("mover_izquierda")
	if d.y > 3.0:
		Input.action_press("mover_abajo")
	elif d.y < -3.0:
		Input.action_press("mover_arriba")
	return false


func _pulsa(a: String) -> void:
	Input.action_press(a)
	await get_tree().process_frame
	await get_tree().process_frame
	Input.action_release(a)


func _process(delta: float) -> void:
	_t += delta
	_total += delta
	if _total > DURACION_MAXIMA:
		if _cos:
			print("FIN: vida ", _cos.vida, " ira ", _cos.ira, " atascos ", _atascos, " daño recibido ", _danio_recibido)
		get_tree().quit()
		return
	if _cos and _cos.fase == _cos.Fase.ATASCADA and _ultima_fase != _cos.Fase.ATASCADA:
		_atascos += 1
		print("atasco ", _atascos, " t=", int(_total), " vida ", _cos.vida, " etapa ", _cos.etapa(), " daño recibido ", _danio_recibido)
	if false:
		print("    t=", snappedf(_total, 0.1), " ", _cos.Fase.keys()[_cos.fase], " ira ", int(_cos.ira), " frenesi ", snappedf(_cos._en_frenesi, 0.1), " modo ", _modo)
	if _cos and str(_cos.partes) != _partes_antes:
		_partes_antes = str(_cos.partes)
		print("  partes ", _partes_antes, " fase ", _cos.Fase.keys()[_cos.fase], " estampada ", _cos._estampada, " t=", snappedf(_total, 0.1), " modo ", _modo)
	if _cos:
		if _cos.fase != _ultima_fase and _cos.fase in [_cos.Fase.CHOQUE, _cos.Fase.CORAZON, _cos.Fase.VENCIDA]:
			print(_cos.Fase.keys()[_cos.fase], " t=", int(_total), " partes ", _cos.partes, " daño recibido ", _danio_recibido)
		_ultima_fase = _cos.fase
	var escena := get_tree().current_scene
	if escena == null or escena.name != "CampoSegado":
		return
	_maisha = get_tree().get_first_node_in_group("maisha") as Node2D
	if _arena == null:
		var zonas := get_tree().get_nodes_in_group("zonas").filter(func(z: Node) -> bool: return z.jefe == "cosechadora")
		if zonas.is_empty():
			return
		_arena = zonas[0]
		_maisha.global_position = _arena.global_position + Vector2(-40, _arena.radios_umbral.y + 70)
		return
	_cos = _arena.get("_nucleo")
	if _vida_antes >= 0 and _maisha.vida < _vida_antes:
		_danio_recibido += _vida_antes - _maisha.vida
		var clave: String = _cos.Fase.keys()[_cos.fase] + "/" + _modo
		_por_fase[clave] = _por_fase.get(clave, 0) + _vida_antes - _maisha.vida
	_vida_antes = _maisha.vida
	if _maisha.vida <= 5 and _cos.fase != _cos.Fase.VENCIDA:
		_maisha.vida = _maisha.vida_maxima()
	_maisha.aliento = maxf(_maisha.aliento, maxf(Artes.semilla_coste(), Artes.latido_coste()) + 5.0)
	# leer al narrador (y la pantalla del final)
	var dialogo := get_tree().get_first_node_in_group("dialogo")
	if dialogo and dialogo.hablando:
		_suelta()
		if int(_t * 10.0) % 32 == 0 and dialogo._linea_completa():
			dialogo.pasar()
		return
	if get_tree().get_first_node_in_group("fin_mundo"):
		_fin += delta
		if _fin > 9.0:
			print("FIN: vencida en t=", int(_total), " daño recibido ", _danio_recibido, " ", _por_fase)
			get_tree().quit()
		return
	_espera_golpe = maxf(0.0, _espera_golpe - delta)
	var F = _cos.Fase
	if _cos.fase == F.CORAZON:
		_corazon()
		return
	# aviso de acelerón: si el depósito frontal sigue entero, la espera junto al borde; si no, se aparta de la fila
	if _cos.fase == F.PREPARA and _modo not in ["apartarse", "emboscada", "frontal", "emboscada_techo"]:
		if _cos.partes["frontal"] > 0 and _emboscada():
			_modo = "emboscada"
		elif _cos.partes["techo"] > 0 and _emboscada(true):
			_modo = "emboscada_techo"
			_semilla_techo = false
		else:
			_objetivo = _maisha.global_position + Vector2(0, 56 if _maisha.global_position.y < _arena.global_position.y else -56)
			_modo = "apartarse"
	elif _cos.fase == F.EMBISTE and _modo not in ["apartarse", "emboscada", "emboscada_techo"] \
			and absf(_maisha.global_position.y - _cos.global_position.y) < 34.0:
		_objetivo = _maisha.global_position + Vector2(0, 56 if _maisha.global_position.y < _arena.global_position.y else -56)
		_modo = "apartarse"
	if _cos.fase == F.RESOPLA and _modo not in ["resopla"]:
		_modo = "resopla"
		_semilla_techo = false
	match _modo:
		"resopla":
			if _cos.fase != F.RESOPLA:
				_salir()
				return
			if _cos.partes["techo"] > 0 and not _semilla_techo and _cos._t < 1.8:
				var bajo: Vector2 = _cos._nodos["techo"].global_position + Vector2(0, 32.0 * signf(_maisha.global_position.y - _cos.global_position.y + 0.1))
				if _ir(bajo):
					print("  semilla al techo (sobrecalentada) t=", snappedf(_total, 0.1))
					_pulsa("explosivo")
					_semilla_techo = true
					_objetivo = bajo + Vector2(-_cos._mira * 50.0, 0)
			else:
				_ir(_objetivo)
		"entrar":
			if _ir(_arena.global_position + Vector2(-40, _arena.radios_umbral.y * 0.55)):
				_modo = "mirar"
				_t = 0.0
		"mirar":
			_suelta()
			if _cos.fase == F.AVANZA and _t > 1.0:
				_modo = "plantar"
		"plantar":
			if _cos.fase == F.ATASCADA:
				_modo = "atasco"
				return
			if _cos.fase != F.AVANZA:
				_suelta()
				_plantar_en = Vector2.INF
				return
			# a veces, un tiro al techo: dos filas al lado de su camino, para que estalle justo cuando pasa el techo
			if _tiro_techo and _cos.partes["techo"] > 0:
				var lado := 1.0 if _cos.global_position.y < _arena.global_position.y else -1.0
				var v: float = _cos._velocidad()
				var q: Vector2 = _cos.global_position + Vector2(0, lado * 32.0)
				for i in 5:
					var t_m := q.distance_to(_maisha.global_position) / 110.0
					q = _cos.global_position + Vector2(_cos._mira * (v * (t_m + Artes.semilla_mecha() + 0.05) - 18.0), lado * 32.0)
				if _arena.distancia_normal(q) > 0.85 or (q.x - _cos.global_position.x) * _cos._mira < 0.0:
					_tiro_techo = false
					return
				if _ir(q):
					print("  tiro al techo t=", snappedf(_total, 0.1), " fase ", _cos.Fase.keys()[_cos.fase])
					_pulsa("explosivo")
					_tiro_techo = false
					_objetivo = q + Vector2(-_cos._mira * 52.0, lado * 14.0)
					_modo = "apartarse"
				return
			# un punto de su camino al que Maisha llegue antes que la máquina (y a tiempo de que estalle)
			if _plantar_en == Vector2.INF or _plantar_mira != _cos._mira or absf(_plantar_en.y - _cos.global_position.y) > 6.0:
				var vel: float = _cos._velocidad()
				var dist := 100.0
				for i in 6:
					var punto: Vector2 = _cos.global_position + Vector2(_cos._mira * dist, -2)
					var t_maisha := punto.distance_to(_maisha.global_position) / 110.0
					dist = 52.0 + vel * (t_maisha + Artes.semilla_mecha() + 0.1)
				_plantar_en = _cos.global_position + Vector2(_cos._mira * dist, -2)
				_plantar_mira = _cos._mira
			if _arena.distancia_normal(_plantar_en) > 0.82 or (_plantar_en.x - _cos.global_position.x) * _cos._mira < 70.0:
				_suelta()
				_plantar_en = Vector2.INF
				return
			if _ir(_plantar_en):
				_pulsa("explosivo")
				_tiro_techo = _cos.partes["caldera"] <= 2
				var p := _plantar_en
				_plantar_en = Vector2.INF
				_objetivo = p + Vector2(-_cos._mira * 10.0, 58 if p.y < _arena.global_position.y + 20 else -58)
				_modo = "apartarse"
		"apartarse":
			if _ir(_objetivo) or _cos.fase == F.ATASCADA:
				_suelta()
				_modo = "atasco" if _cos.fase == F.ATASCADA else "esperar"
				_t = 0.0
		"esperar":
			_suelta()
			if _cos.fase == F.ATASCADA:
				_modo = "atasco"
			elif _t > 2.0:
				_modo = "plantar"
		"atasco":
			if _cos.fase != F.ATASCADA:
				_salir()
				return
			if _cos.frontal_al_aire():
				_modo = "frontal"
				return
			_modo = "caldera"
		"caldera":
			if _cos.fase != F.ATASCADA or not _cos.caldera_abierta():
				_salir()
				return
			_golpear_en(_cos._nodos["caldera"].global_position + Vector2(-_cos._mira * 12.0, 0))
		"emboscada":
			if _cos.fase == F.CHOQUE or (_cos.fase == F.ATASCADA and _cos.frontal_al_aire()):
				_modo = "frontal"
				_golpes = 0
			elif _cos.fase not in [F.PREPARA, F.EMBISTE]:
				_modo = "atasco" if _cos.fase == F.ATASCADA else "plantar"
			else:
				_ir(_objetivo)
		"emboscada_techo":
			if _semilla_techo:
				if _ir(_objetivo):
					_suelta()
				if _cos.fase not in [F.PREPARA, F.EMBISTE, F.CHOQUE]:
					_modo = "esperar"
					_t = 0.0
				return
			if _cos.fase not in [F.PREPARA, F.EMBISTE]:
				_modo = "esperar"
				_t = 0.0
				return
			if _ir(_objetivo):
				print("  emboscada al techo t=", snappedf(_total, 0.1), " fase ", _cos.Fase.keys()[_cos.fase])
				_pulsa("explosivo")
				_semilla_techo = true
				var lado := signf(_objetivo.y - _choque_techo.y)
				_objetivo = _objetivo + Vector2(_cos._mira * 40.0, lado * 20.0)
		"frontal":
			if not _cos.frontal_al_aire():
				_salir()
				return
			_golpear_en(_cos._nodos["frontal"].global_position + Vector2(_cos._mira * 12.0, 0))


## Dónde se estrellará el acelerón: se pone allí, fuera de la franja, para golpear el depósito al chocar
func _emboscada(techo := false) -> bool:
	var x: float = _cos.global_position.x
	var y: float = _cos.global_position.y
	for i in 200:
		if _arena.distancia_normal(Vector2(x + _cos._mira * 64.0, y)) > minf(0.92, _cos.borde + 0.08):
			break
		x += _cos._mira * 4.0
	var lado := 1.0 if y < _arena.global_position.y else -1.0
	var filas: int = R.COSECHADORA_FUEGO_ANCHO[_cos.etapa()]
	_objetivo = Vector2(x + _cos._mira * 50.0, y + lado * (30.0 + (filas - 1) * 12.0))
	if techo:
		# una semilla dos filas al lado de donde quedará el techo al estrellarse
		_objetivo = Vector2(x - _cos._mira * 18.0, y + lado * 32.0)
		_choque_techo = Vector2(x, y)
	return _arena.distancia_normal(_objetivo) < 0.88 and absf(x - _maisha.global_position.x) < 260.0


func _salir() -> void:
	_golpes = 0
	_semilla_techo = false
	_objetivo = _maisha.global_position + Vector2(0, 50 if _maisha.global_position.y < _arena.global_position.y else -50)
	_modo = "apartarse"


func _golpear_en(p: Vector2) -> void:
	if _ir(p):
		_suelta()
		var hacia: float = signf(_cos.global_position.x - _maisha.global_position.x)
		if _maisha.mirando != "lado" or _maisha.get_node("Sprite").flip_h != (hacia < 0.0):
			if not _maisha.get("_golpeando"):
				_maisha.mirar(Vector2(hacia, 0))
		if _espera_golpe <= 0.0 and _golpes < 3:
			_maisha.golpear()
			_golpes += 1
			_espera_golpe = 0.45
	elif _golpes >= 3:
		_golpes = 0


## El corazón al aire: espera cerca, pasa los anillos con el Latido y golpea cuando se abre
func _corazon() -> void:
	var centro: Vector2 = _cos.global_position
	var cerca := centro + Vector2(0, 40)
	if _cos.corazon_abierto():
		var p := centro + Vector2(0, 10)
		if _ir(p):
			_suelta()
			if _maisha.mirando != "arriba" and not _maisha.get("_golpeando"):
				_maisha.mirar(Vector2(0, -1))
			if _espera_golpe <= 0.0:
				_maisha.golpear()
				_espera_golpe = 0.45
	else:
		_ir(cerca)
	# un anillo a punto de pasarle por encima (y no por un hueco): ¡Latido!
	var d: Vector2 = _maisha.global_position - (centro + Vector2(0, -6))
	for an in _cos._anillos:
		var falta: float = d.length() - an["r"]
		if falta > 0.0 and falta < 10.0 and not an["hecho"] and not _cos._en_hueco(an, d.angle()):
			_maisha.latido()
