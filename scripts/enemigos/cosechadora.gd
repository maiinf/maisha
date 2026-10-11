extends Node2D
## LA COSECHADORA OXIDADA: el jefe de Raíz, en el Campo Segado.
## Una máquina de siega enorme (128×96) que Giza ha despertado. Recorre el campo fila a fila con su molinete
## de cuchillas; las ruedas, los pistones y el molinete se mueven de verdad (capas en arte/zonas/raiz/cosechadora/).
##
## SE ROMPE POR PARTES. Su chapa lo aguanta todo; tiene tres puntos débiles y cada uno se abre de una forma:
##   - La CALDERA (atrás): solo cuando se ATASCA en los brotes de una semilla. Cetro 1, semilla 2.
##     Al tercer golpe de cetro en el mismo atasco (al segundo en Furia y Frenesí) la cierra de golpe y se suelta.
##     Al romperla: revienta, sale volando la rueda grande y la máquina va dando BANDAZOS (y un poco más rápida).
##   - El DEPÓSITO FRONTAL (delante, junto al molinete): solo cuando se estrella contra el borde tras un ACELERÓN
##     (queda aturdida un momento) o cuando se estampa contra unos brotes acelerando. Cetro 1, semilla 2.
##     Al segundo golpe, se suelta de un tirón (hacen falta dos ocasiones).
##     Al romperlo: tiene una FUGA de fuego que va dejando llamas por donde pasa, y las cuchillas arden (+1 de daño).
##   - El DEPÓSITO DEL TECHO: solo le llegan las EXPLOSIONES (está muy alto para el cetro), y solo con la máquina
##     EN MARCHA o recién ESTRELLADA contra el borde (atascada en los brotes, lo tapa la tolva): hay que plantar la
##     semilla a un lado de su fila para que estalle justo cuando pasa el techo, o donde va a estrellarse. 1 por semilla.
##     Al romperlo: las TUERCAS que lanza caen como bolas de fuego que prenden tres casillas.
##   - Con las tres rotas, se DESPLOMA y deja al aire el CORAZÓN de Giza. Lanza ANILLOS DE FUEGO con dos huecos
##     que giran (pasa por un hueco o usa el Latido). Justo después de cada anillo, el corazón se abre un momento:
##     ahí el cetro le quita 1 (y una semilla, 1), y se cierra del golpe. Si estás encima cuando lanza el anillo, te quema.
##   - La IRA sube sola (Calma → Enfado → Furia → Frenesí). Cada golpe en una parte la baja una etapa, pero cada
##     parte rota sube el mínimo una etapa (con una rota no baja de Enfado; con dos, de Furia).
##       Calma:   recorre las filas y barre con las cuchillas.
##       Enfado:  se para a lanzar tuercas que dejan BLOQUES DE CHATARRA (una semilla los deshace).
##       Furia:   llama a babosas de óxido y Giza cierra la arena desde el borde (pisar el borde hace daño).
##       Frenesí: si Maisha se pone en su fila, embiste a toda velocidad. Pero no aguanta mucho así: al rato se
##                SOBRECALIENTA, se para a soltar vapor (con el techo al aire) y la Ira vuelve a su mínimo.
##   - Su habilidad especial, el ACELERÓN INFERNAL: avisa con una franja roja, sale disparada en línea recta y deja
##     un RASTRO DE FUEGO de Giza que quema. Cuanto más enfadada, más «rota»: más a menudo, más rápida, el fuego
##     dura más, en Furia quema tres filas a la vez y en Frenesí el fuego se extiende y repite el acelerón de vuelta.
## Hace de «Corazón» de su zona (zona_corrupta.gd con jefe = "cosechadora").

signal destruido
signal vida_cambiada(vida: int)

enum Fase { DORMIDA, PRESENTACION, AVANZA, GIRA, ATASCADA, LANZA, PREPARA, EMBISTE, CHOQUE, CORAZON, VENCIDA, RESOPLA }

const R := preload("res://scripts/combate/reglas_combate.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const TUERCA := preload("res://scripts/enemigos/tuerca.gd")
const FUEGO := preload("res://scripts/enemigos/fuego_giza.gd")
const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const PARTE := preload("res://scripts/enemigos/parte_jefe.gd")
const NOMBRE := "La Cosechadora Oxidada"
const ETAPAS := ["Calma", "Enfado", "Furia", "Frenesí"]
const ORDEN := ["caldera", "frontal", "techo", "corazon"]
const NOMBRES := {"caldera": "Caldera", "frontal": "Depósito", "techo": "Techo", "corazon": "Corazón"}
## Las capas del dibujo, de atrás adelante: [nombre, fotogramas]
const CAPAS := [["caldera", 3], ["chasis", 3], ["dep_techo", 4], ["piston", 4], ["rueda_g", 4], ["rueda_p", 4],
	["dep_frontal", 4], ["molinete", 5], ["corazon", 4], ["enredaderas", 1]]
## Sitios de la máquina (en píxeles desde sus pies, mirando a la derecha)
const P_CALDERA := Vector2(-42, -36)
const P_TECHO := Vector2(-17, -67)
const P_FRONTAL := Vector2(38, -21)
const P_BOQUILLA := Vector2(52, -14)
const P_CORAZON := Vector2(0, -36)
const P_CHIMENEA := Vector2(0, -88)
const P_ESCAPE := Vector2(-60, -16)
const P_TOLVA := Vector2(18, -60)
const P_RUEDA := Vector2(-16, -14)
const MORRO_X := 46.0              # la punta del molinete
## Dónde reciben los golpes (a ras de suelo, que es donde mide el cetro)
const GOLPE := {"caldera": Vector2(-52, -4), "frontal": Vector2(42, -4), "techo": Vector2(-18, -2), "corazon": Vector2(0, -4)}

var zona: Node2D
var variante := "raiz"
var vida: int = R.COSECHADORA_VIDA
var fase: int = Fase.DORMIDA
var ira := 0.0
var borde := 1.0                   # hasta dónde llega la arena (Furia: Giza la cierra desde fuera)
var partes := {}                   # nombre -> vida que le queda

var _t := 0.0
var _tiempo := 0.0
var _mira := 1.0
var _fila_destino := 0.0
var _desde_tuercas := 0.0
var _desde_babosas := 0.0
var _desde_borde := 0.0
var _desde_fuga := 0.0
var _desde_anillo := 0.0
var _blanco := 0.0
var _golpes_atasco := 0           # golpes de cetro en la caldera en este atasco
var _golpes_frontal := 0           # golpes en el depósito frontal en esta ocasión (al segundo, se suelta)
var _espera_techo := 0.0           # una explosión solo cuenta una vez
var _corazon_golpeado := false     # el corazón se cierra del golpe hasta el siguiente anillo
var _en_frenesi := 0.0             # segundos seguidos en Frenesí (al rato, se sobrecalienta)
var _gracia := 0.0
var _desde_aceleron := 0.0
var _doble_hecho := false          # Frenesí: el acelerón de vuelta (solo uno)
var _estampada := false            # el atasco de ahora es por estamparse acelerando (deja el depósito frontal al aire)
var _recorrido := 0.0              # píxeles andados (mueven las ruedas y los pistones)
var _anillos: Array[Dictionary] = []
var _destellos := {}               # parte -> segundos de destello blanco
var _humo: Array[Dictionary] = []
var _fuego: Node2D
var _cuerpo: Node2D
var _capas := {}
var _nodos := {}
var _rueda_suelta: Sprite2D
var _rueda_vel := Vector2.ZERO
var _capa_borde: Node2D
var _barra: CanvasLayer


func _ready() -> void:
	add_to_group("jefes")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 70.0)
	add_child(sombra)
	_cuerpo = Node2D.new()
	add_child(_cuerpo)
	for capa in CAPAS:
		var s := Sprite2D.new()
		s.texture = load("res://arte/zonas/%s/cosechadora/%s.png" % [variante, capa[0]])
		s.hframes = capa[1]
		s.centered = false
		s.position = Vector2(-64, -94)
		_cuerpo.add_child(s)
		_capas[capa[0]] = s
	for n in ORDEN:
		var p: Node2D = PARTE.new()
		p.set("jefe", self)
		p.set("al_golpe", "_golpe_" + n if n != "techo" else "")
		p.set("al_danio", "_danio_" + n)
		add_child(p)
		_nodos[n] = p
	# el borde de Giza que cierra la arena en Furia (se dibuja en el suelo, en coordenadas del mundo)
	_capa_borde = Node2D.new()
	_capa_borde.top_level = true
	_capa_borde.z_index = -2
	_capa_borde.draw.connect(_dibujar_borde)
	add_child(_capa_borde)
	_reponer_partes()
	visible = false


func _reponer_partes() -> void:
	partes = R.COSECHADORA_PARTES.duplicate()
	vida = R.COSECHADORA_VIDA
	ira = 0.0
	borde = 1.0
	_anillos.clear()
	_destellos.clear()
	_estampada = false
	_capas["rueda_g"].visible = true
	if _rueda_suelta:
		_rueda_suelta.queue_free()
		_rueda_suelta = null


func despertar() -> void:
	if fase != Fase.DORMIDA:
		return
	_reponer_partes()
	visible = true
	modulate.a = 1.0
	global_position = zona.global_position + Vector2(-zona.radios_umbral.x * 0.4, -zona.radios_umbral.y * 0.3)
	_mira = 1.0
	_fila_destino = global_position.y
	_cambiar(Fase.PRESENTACION)
	Sonido.efecto("cosechadora_arranca")
	Impacto.temblar(4.0, 0.8)
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = R.COSECHADORA_VIDA
	_barra.ira = 0.0
	for n in ORDEN:
		_barra.partes.append({"nombre": NOMBRES[n], "maximo": partes[n], "vida": partes[n], "oculta": n == "corazon"})
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	_activar_partes()
	if _fuego == null:
		_fuego = FUEGO.new()
		get_parent().add_child(_fuego)
	_desde_aceleron = 0.0


func reiniciar() -> void:
	_reponer_partes()
	if _barra:
		_barra.queue_free()
		_barra = null
	for n in get_tree().get_nodes_in_group("tuercas") + get_tree().get_nodes_in_group("chatarra"):
		n.queue_free()
	fase = Fase.DORMIDA
	visible = false
	_activar_partes()
	if _fuego:
		_fuego.apagar_todo()
	_capa_borde.queue_redraw()


## Qué partes reciben golpes ahora (las rotas y el corazón escondido, no)
func _activar_partes() -> void:
	var activa := fase != Fase.DORMIDA and fase != Fase.VENCIDA
	for n in ORDEN:
		var p: Node2D = _nodos[n]
		var si: bool = activa and partes[n] > 0 and (n == "corazon") == (fase == Fase.CORAZON)
		for grupo in ["golpeables", "daniables"]:
			if grupo == "golpeables" and n == "techo":
				continue      # el techo está muy alto para el cetro: solo le llegan las explosiones
			if si and not p.is_in_group(grupo):
				p.add_to_group(grupo)
			elif not si and p.is_in_group(grupo):
				p.remove_from_group(grupo)


func etapa() -> int:
	return mini(3, int(ira / 25.0))


func rotas() -> int:
	var n := 0
	for p in ["caldera", "frontal", "techo"]:
		if partes[p] <= 0:
			n += 1
	return n


## Cada parte rota la enfada para siempre: no baja de Enfado con una, de Furia con dos
func _ira_minima() -> float:
	return minf(75.0, rotas() * 25.0)


func _cambiar(nueva: int) -> void:
	if fase == Fase.ATASCADA and nueva != Fase.ATASCADA:
		_estampada = false
	fase = nueva
	_t = 0.0
	if nueva == Fase.ATASCADA:
		_golpes_atasco = 0
	if nueva in [Fase.ATASCADA, Fase.CHOQUE]:
		_golpes_frontal = 0


func caldera_abierta() -> bool:
	var max_golpes := 3 if etapa() < 2 else 2
	return fase == Fase.ATASCADA and partes["caldera"] > 0 and _golpes_atasco < max_golpes


func frontal_al_aire() -> bool:
	return partes["frontal"] > 0 and _golpes_frontal < 2 and (fase == Fase.CHOQUE or (fase == Fase.ATASCADA and _estampada))


## El techo solo se alcanza con la máquina en marcha o recién estrellada (atascada, la tolva lo tapa)
func techo_al_aire() -> bool:
	return partes["techo"] > 0 and fase in [Fase.AVANZA, Fase.GIRA, Fase.LANZA, Fase.PREPARA, Fase.EMBISTE, Fase.CHOQUE, Fase.RESOPLA]


## El corazón se abre justo después de lanzar cada anillo (y se cierra para cargar el siguiente)
func corazon_abierto() -> bool:
	return fase == Fase.CORAZON and _t > 1.2 and not _corazon_golpeado and _desde_anillo > 0.35 and _desde_anillo < 1.6


# --- Cada fotograma -------------------------------------------------------------------

func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	_blanco = maxf(0.0, _blanco - delta)
	_gracia = maxf(0.0, _gracia - delta)
	_espera_techo = maxf(0.0, _espera_techo - delta)
	for n in _destellos:
		_destellos[n] = maxf(0.0, _destellos[n] - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	_encuadrar(delta, maisha)
	_mover_humo(delta)
	_mover_rueda_suelta(delta)
	if fase == Fase.DORMIDA:
		return
	for n in ORDEN:
		_nodos[n].position = Vector2(GOLPE[n].x * _mira, GOLPE[n].y)
	if fase != Fase.VENCIDA:
		_subir_ira(delta)
		_cerrar_borde(delta, maisha)
	match fase:
		Fase.PRESENTACION:
			if _t > 2.0:
				_cambiar(Fase.AVANZA)
		Fase.AVANZA:
			_avanzar(delta, maisha, _velocidad())
		Fase.GIRA:
			_girar(delta)
		Fase.ATASCADA:
			if _t >= R.COSECHADORA_ATASCADA:
				Sonido.efecto("cosechadora_arranca")
				_gracia = 1.6
				_cambiar(Fase.AVANZA)
		Fase.LANZA:
			if _t >= 0.4 and _t - delta < 0.4:
				_lanzar_tuercas(maisha)
			if _t >= 1.0:
				_cambiar(Fase.AVANZA)
		Fase.PREPARA:
			# en Furia y Frenesí apunta: se coloca en la fila de Maisha mientras avisa
			if etapa() >= 2 and maisha and not _doble_hecho:
				var fila := global_position.y + clampf(maisha.global_position.y - global_position.y, -48.0, 48.0)
				if zona.distancia_normal(Vector2(global_position.x, fila)) < 0.75:
					global_position.y = move_toward(global_position.y, fila, 150.0 * delta)
			if _t >= (R.COSECHADORA_ACELERON_AVISO[etapa()] if not _doble_hecho else 0.3):
				Sonido.efecto("cosechadora_embiste")
				Sonido.efecto("cosechadora_fuego")
				_cambiar(Fase.EMBISTE)
		Fase.EMBISTE:
			_avanzar(delta, maisha, maxf(R.COSECHADORA_ACELERON_VEL[etapa()], R.COSECHADORA_EMBESTIDA if etapa() == 3 else 0.0))
			_dejar_fuego()
		Fase.CHOQUE:
			if etapa() == 3 and not _doble_hecho and _t >= 1.0:
				# Frenesí: da la vuelta en el sitio, se pone en la fila de Maisha y acelera otra vez
				_doble_hecho = true
				_mira = -_mira
				if maisha:
					var fila := global_position.y + clampf(maisha.global_position.y - global_position.y, -32.0, 32.0)
					if zona.distancia_normal(Vector2(global_position.x, fila)) < 0.75:
						global_position.y = fila
				_cambiar(Fase.PREPARA)
			elif _t >= R.COSECHADORA_CHOQUE:
				_doble_hecho = false
				_empezar_giro(maisha)
		Fase.RESOPLA:
			# sobrecalentada: suelta vapor por todas partes, quieta; luego se le pasa la Ira
			if randf() < delta * 30.0:
				var desde: Vector2 = [P_CHIMENEA, P_TECHO + Vector2(0, -4), P_ESCAPE, Vector2(10, -50)][randi() % 4]
				_humear(1, Color("e8e4dc"), desde)
			if _t >= R.COSECHADORA_RESOPLA:
				ira = _ira_minima()
				_en_frenesi = 0.0
				if _barra:
					_barra.ira = ira
				Sonido.efecto("cosechadora_arranca")
				_gracia = 1.0
				_cambiar(Fase.AVANZA)
		Fase.CORAZON:
			_proceso_corazon(delta, maisha)
		Fase.VENCIDA:
			_proceso_vencida()
	if fase in [Fase.AVANZA, Fase.GIRA, Fase.EMBISTE]:
		_fugar(delta)
	if maisha and fase in [Fase.AVANZA, Fase.GIRA, Fase.EMBISTE, Fase.PREPARA]:
		_hacer_dano(maisha)
	_animar(delta)


func _velocidad() -> float:
	return R.COSECHADORA_VELOCIDAD[etapa()] * (1.15 if partes["caldera"] <= 0 else 1.0)


func _subir_ira(delta: float) -> void:
	if fase in [Fase.PRESENTACION, Fase.ATASCADA, Fase.CORAZON, Fase.RESOPLA]:
		return
	# en Frenesí no aguanta mucho: al rato se sobrecalienta (si no está a media embestida)
	_en_frenesi = _en_frenesi + delta if etapa() == 3 else 0.0
	if _en_frenesi >= R.COSECHADORA_FRENESI_DURA and fase in [Fase.AVANZA, Fase.GIRA, Fase.CHOQUE]:
		_cambiar(Fase.RESOPLA)
		Sonido.efecto("cosechadora_atascada")
		Impacto.temblar(3.0, 0.4)
		_humear(14, Color("e8e4dc"), P_CHIMENEA)
		_mensaje("¡Se ha sobrecalentado!")
		return
	var antes := etapa()
	ira = minf(100.0, maxf(ira + R.COSECHADORA_IRA_RITMO * delta, _ira_minima()))
	if etapa() > antes:
		Sonido.efecto("cosechadora_ira")
		Impacto.temblar(2.5, 0.4)
		_humear(8, Color("6b2a8f"), P_CHIMENEA)
	if _barra:
		_barra.ira = ira


func _avanzar(delta: float, maisha: Node2D, velocidad: float) -> void:
	var nueva := global_position + Vector2(_mira * velocidad * delta, 0)
	# sin la rueda grande, va dando bandazos de un lado a otro de su fila
	if partes["caldera"] <= 0 and fase == Fase.AVANZA:
		var bandazo := cos(_tiempo * 2.6) * 2.6 * 9.0 * delta
		if zona.distancia_normal(nueva + Vector2(0, bandazo * 4.0)) < 0.8:
			nueva.y += bandazo
	# se mete en los brotes de una semilla: ¡atascada!
	if _gracia <= 0.0 and _brotes_delante():
		var estampada := fase == Fase.EMBISTE
		_atascar()
		if estampada:
			# a toda velocidad contra los brotes: se estampa, se queda atascada más rato y el depósito frontal al aire
			_t = -R.COSECHADORA_ESTAMPADA
			_estampada = true
			_doble_hecho = false
			Sonido.efecto("cosechadora_choque")
			Impacto.temblar(5.0, 0.5)
		return
	# aplasta la chatarra que tiene delante
	for b in get_tree().get_nodes_in_group("chatarra"):
		var d: Vector2 = b.global_position - global_position
		if d.x * _mira > 0 and absf(d.x) < MORRO_X + 10 and absf(d.y) < 16:
			b.call("romper")
	if zona.distancia_normal(nueva + Vector2(_mira * 60.0, 0)) > minf(0.92, borde + 0.08):
		if fase == Fase.EMBISTE:
			Sonido.efecto("cosechadora_choque")
			Impacto.temblar(4.5, 0.45)
			_humear(8, Color("e8e4dc"), Vector2(MORRO_X * _mira, -20))
			_cambiar(Fase.CHOQUE)
		else:
			_empezar_giro(maisha)
		return
	_recorrido += absf(nueva.x - global_position.x)
	global_position = nueva
	if fase != Fase.AVANZA:
		return
	# Enfado o más: de vez en cuando se para a lanzar tuercas
	_desde_tuercas += delta
	if etapa() >= 1 and _desde_tuercas >= R.COSECHADORA_TUERCAS_CADA:
		_desde_tuercas = 0.0
		_cambiar(Fase.LANZA)
		Sonido.efecto("cosechadora_tolva")
		return
	# Furia o más: llama a babosas
	_desde_babosas += delta
	if etapa() >= 2 and _desde_babosas >= R.COSECHADORA_BABOSAS_CADA:
		_desde_babosas = 0.0
		if get_tree().get_nodes_in_group("enemigos").size() < 3:
			var lado := Vector2(randf_range(-0.6, 0.6), -0.55 if randf() < 0.5 else 0.55)
			zona.call("invocar_en", zona.global_position + lado * zona.radios_umbral, "babosa")
	# el acelerón infernal: cada cierto tiempo (más a menudo cuanto más Ira), si tiene sitio por delante;
	# en Frenesí, además, en cuanto Maisha se pone en su fila y delante
	_desde_aceleron += delta
	var sitio: bool = zona.distancia_normal(global_position + Vector2(_mira * 120.0, 0)) < 0.85
	var en_su_fila: bool = maisha != null and absf(maisha.global_position.y - global_position.y) < 14.0 \
			and (maisha.global_position.x - global_position.x) * _mira > 30.0
	if sitio and (_desde_aceleron >= R.COSECHADORA_ACELERON_CADA[etapa()] or (etapa() >= 3 and en_su_fila)):
		_desde_aceleron = 0.0
		_doble_hecho = false
		_cambiar(Fase.PREPARA)
		Sonido.efecto("cosechadora_ira")


func _brotes_delante() -> bool:
	var registro := get_tree().get_first_node_in_group("registro_brotes")
	if registro == null:
		return false
	for dy in [-14.0, -2.0, 8.0]:
		for dx in [40.0, 50.0, 60.0]:
			if registro.hay_brote(R.casilla_de(global_position + Vector2(_mira * dx, dy))):
				return true
	return false


func _atascar() -> void:
	_cambiar(Fase.ATASCADA)
	Sonido.efecto("cosechadora_atascada")
	Impacto.temblar(3.0, 0.3)
	_humear(10, Color("e8e4dc"), Vector2(MORRO_X * _mira, -24))


## Mientras acelera, va dejando fuego detrás (1 fila; en Furia y Frenesí, 3; en Frenesí, además, se extiende)
func _dejar_fuego() -> void:
	if _fuego == null:
		return
	var e := etapa()
	var c := R.casilla_de(global_position + Vector2(-_mira * 34.0, -4))
	var ancho: int = R.COSECHADORA_FUEGO_ANCHO[e]
	for k in range(-(ancho / 2), ancho / 2 + 1):
		var cc := c + Vector2i(0, k)
		if zona.distancia_normal(R.centro_de(cc)) < 0.9:
			_fuego.encender(cc, R.COSECHADORA_FUEGO_DURA[e] + randf_range(-0.3, 0.3), e == 3)


## Con el depósito frontal roto, la fuga va soltando llamas por donde pasa
func _fugar(delta: float) -> void:
	if partes["frontal"] > 0 or _fuego == null:
		return
	_desde_fuga += delta
	if _desde_fuga >= 0.22:
		_desde_fuga = 0.0
		var c := R.casilla_de(global_position + Vector2(_mira * 48.0, -4))
		if zona.distancia_normal(R.centro_de(c)) < 0.9:
			_fuego.encender(c, 2.6)


func _empezar_giro(maisha: Node2D) -> void:
	# baja o sube de fila (hacia la de Maisha) y da la vuelta
	var objetivo := global_position.y + (48.0 if randf() < 0.5 else -48.0)
	if maisha:
		objetivo = global_position.y + clampf(maisha.global_position.y - global_position.y, -64.0, 64.0)
	# que no se salga de la arena
	for k in 8:
		if zona.distancia_normal(Vector2(global_position.x, objetivo)) < 0.7:
			break
		objetivo = lerpf(objetivo, zona.global_position.y, 0.35)
	_fila_destino = objetivo
	_cambiar(Fase.GIRA)


func _girar(delta: float) -> void:
	var antes := global_position.y
	global_position.y = move_toward(global_position.y, _fila_destino, R.COSECHADORA_GIRO * delta)
	_recorrido += absf(global_position.y - antes)
	if absf(global_position.y - _fila_destino) < 1.0 and _t > 0.35:
		_mira = -_mira
		_cambiar(Fase.AVANZA)


func _lanzar_tuercas(maisha: Node2D) -> void:
	if maisha == null:
		return
	var cuantas := 3 if etapa() < 3 else 4
	for k in cuantas:
		var t: Node2D = TUERCA.new()
		var hasta := maisha.global_position + (Vector2.ZERO if k == 0 else Vector2(randf_range(-56, 56), randf_range(-40, 40)))
		if zona.distancia_normal(hasta) > 0.8:
			hasta = zona.global_position + (hasta - zona.global_position) * 0.6
		t.set("desde", global_position + Vector2(P_TOLVA.x * _mira, P_TOLVA.y))
		t.set("hasta", hasta)
		t.set("de_fuego", partes["techo"] <= 0)
		get_parent().add_child(t)


## Furia o más: Giza cierra la arena desde el borde; pisar fuera hace daño y empuja hacia dentro
func _cerrar_borde(delta: float, maisha: Node2D) -> void:
	var meta := 1.0 if etapa() < 2 else R.COSECHADORA_BORDE_MIN
	borde = move_toward(borde, meta, delta * 0.05)
	_capa_borde.queue_redraw()
	_desde_borde += delta
	if maisha and borde < 0.99 and zona.distancia_normal(maisha.global_position) > borde and _desde_borde > 0.8:
		_desde_borde = 0.0
		var fuera := maisha.global_position + (maisha.global_position - zona.global_position).normalized() * 30.0
		maisha.call("recibir_danio", 1, fuera, "contacto")


func _hacer_dano(maisha: Node2D) -> void:
	var d := maisha.global_position - global_position
	if absf(d.y + 4.0) > 16.0:
		return
	if d.x * _mira > 30.0 and d.x * _mira < 64.0:
		var danio: int = R.COSECHADORA_CUCHILLAS + (1 if fase == Fase.EMBISTE else 0) + (1 if partes["frontal"] <= 0 else 0)
		maisha.call("recibir_danio", danio, global_position + Vector2(_mira * 20.0, 0), "contacto")
	elif absf(d.x) < 52.0:
		maisha.call("recibir_danio", 1, global_position, "contacto")


# --- El corazón al aire ------------------------------------------------------------------

func _empezar_corazon() -> void:
	_cambiar(Fase.CORAZON)
	_desde_anillo = 0.4
	_anillos.clear()
	_activar_partes()
	if _barra:
		_barra.mostrar_parte(3)
	for n in get_tree().get_nodes_in_group("tuercas"):
		n.queue_free()
	Sonido.efecto("cosechadora_vencida")
	Impacto.temblar(6.0, 1.0)
	_humear(16, Color("6b2a8f"), P_CORAZON)
	_humear(10, Color("e8e4dc"), Vector2(0, -20))
	_mensaje("¡El corazón de Giza ha quedado al aire!")


func _proceso_corazon(delta: float, maisha: Node2D) -> void:
	_desde_anillo += delta
	var cada: float = R.COSECHADORA_ANILLO_CADA[0 if partes["corazon"] >= R.COSECHADORA_PARTES["corazon"] else 1]
	if _desde_anillo >= cada:
		_desde_anillo = 0.0
		_corazon_golpeado = false
		var a := randf() * TAU
		_anillos.append({"r": 6.0, "hueco": a, "giro": (0.9 if randf() < 0.5 else -0.9), "hecho": false})
		Sonido.efecto("cosechadora_fuego")
		Impacto.temblar(2.0, 0.2)
		# al lanzarlo, quema lo que tenga encima
		if maisha and (maisha.global_position - global_position).length() < 30.0:
			maisha.call("recibir_danio", 1, global_position, "fuego")
	var centro := global_position + Vector2(0, -6)
	for an in _anillos:
		an["r"] += R.COSECHADORA_ANILLO_VEL * delta
		an["hueco"] += an["giro"] * delta
		if maisha and not an["hecho"] and an["r"] > 30.0:
			var d := maisha.global_position - centro
			if absf(d.length() - an["r"]) < 7.0:
				an["hecho"] = true
				if not _en_hueco(an, d.angle()):
					maisha.call("recibir_danio", 1, centro, "fuego")
	_anillos = _anillos.filter(func(an: Dictionary) -> bool: return an["r"] < 460.0)


func _en_hueco(an: Dictionary, angulo: float) -> bool:
	var medio := deg_to_rad(R.COSECHADORA_ANILLO_HUECO) / 2.0
	for k in 2:
		if absf(angle_difference(angulo, an["hueco"] + k * PI)) < medio:
			return true
	return false


# --- Daño ------------------------------------------------------------------------------

func _golpe_caldera(danio: int, direccion: Vector2) -> bool:
	if not caldera_abierta():
		return _golpe_morro(danio, direccion)
	_golpes_atasco += 1
	_herir("caldera", danio)
	if not caldera_abierta() and partes["caldera"] > 0 and fase == Fase.ATASCADA:
		# del susto, cierra la caldera de golpe y se suelta enseguida
		_t = maxf(_t, R.COSECHADORA_ATASCADA - 0.4)
		Sonido.efecto("cosechadora_choque")
	return true


func _danio_caldera(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if tipo == "explosion" and caldera_abierta():
		_herir("caldera", R.COSECHADORA_SEMILLA_DANIO)


func _golpe_frontal(danio: int, direccion: Vector2) -> bool:
	if not frontal_al_aire():
		return _golpe_morro(danio, direccion)
	_golpes_frontal += 1
	_herir("frontal", danio)
	_soltarse_frontal()
	return true


func _danio_frontal(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if tipo == "explosion" and frontal_al_aire():
		_golpes_frontal += 1
		_herir("frontal", R.COSECHADORA_SEMILLA_DANIO)
		_soltarse_frontal()


## Al segundo golpe en el depósito, se suelta de un tirón
func _soltarse_frontal() -> void:
	if _golpes_frontal < 2 or partes["frontal"] <= 0 or fase == Fase.CORAZON:
		return
	Sonido.efecto("cosechadora_choque")
	if fase == Fase.ATASCADA:
		_t = maxf(_t, R.COSECHADORA_ATASCADA - 0.4)
	elif fase == Fase.CHOQUE:
		_t = maxf(_t, R.COSECHADORA_CHOQUE - 0.3)


func _danio_techo(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if tipo == "explosion" and techo_al_aire() and _espera_techo <= 0.0:
		_espera_techo = 0.4
		_herir("techo", 1)


func _golpe_corazon(danio: int, direccion: Vector2) -> bool:
	if not corazon_abierto():
		return _golpe_morro(danio, direccion)
	_corazon_golpeado = true
	_herir("corazon", danio)
	return true


func _danio_corazon(_cantidad: int, _desde: Vector2, tipo: String) -> void:
	if tipo == "explosion" and corazon_abierto():
		_corazon_golpeado = true
		_herir("corazon", 1)


## Un golpe en la chapa: no le hace nada (clinc)
func _golpe_morro(_danio: int, _direccion: Vector2) -> bool:
	_blanco = 0.04
	Sonido.efecto("clinc", 0.0, global_position)
	return false


func _danio_morro(_cantidad: int, _desde: Vector2, _tipo: String) -> void:
	pass


func _sitio(punto: Vector2) -> Vector2:
	return global_position + Vector2(punto.x * _mira, punto.y)


func _herir(parte: String, cuanto: int) -> void:
	if partes[parte] <= 0 or fase == Fase.VENCIDA:
		return
	partes[parte] = maxi(0, partes[parte] - cuanto)
	vida = 0
	for n in ORDEN:
		vida += partes[n]
	vida_cambiada.emit(vida)
	if _barra:
		_barra.poner_parte(ORDEN.find(parte), partes[parte])
	_destellos[parte] = 0.25
	Impacto.pausa(0.08)
	Sonido.efecto("cosechadora_dolor")
	var punto: Vector2 = {"caldera": P_CALDERA, "frontal": P_FRONTAL, "techo": P_TECHO, "corazon": P_CORAZON}[parte]
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 12
	astillas.chispas = 6
	astillas.fuerza = 90.0
	astillas.position = _sitio(punto)
	get_parent().add_child(astillas)
	if parte == "corazon":
		_humear(4, Color("a855d6"), P_CORAZON)
		if partes[parte] <= 0:
			_vencer()
		return
	if partes[parte] <= 0:
		_romper(parte)
	# contrajuego: un golpe en una parte baja la Ira una etapa (pero no por debajo de lo que marcan las rotas)
	ira = maxf(_ira_minima(), (etapa() - 1) * 25.0)
	if _barra:
		_barra.ira = ira


func _romper(parte: String) -> void:
	_activar_partes()
	var punto: Vector2 = {"caldera": P_CALDERA, "frontal": P_FRONTAL, "techo": P_TECHO}[parte]
	Sonido.efecto("explosion", 0.0, _sitio(punto))
	Sonido.efecto("cosechadora_choque")
	Impacto.temblar(6.0, 0.6)
	Impacto.pausa(0.15)
	for k in 2:
		var astillas: Node2D = ASTILLAS.new()
		astillas.cantidad = 20
		astillas.chispas = 12
		astillas.fuerza = 150.0
		astillas.position = _sitio(punto) + Vector2(randf_range(-6, 6), randf_range(-6, 6))
		get_parent().add_child(astillas)
	_humear(12, Color("3a3038"), punto)
	for k in 10:
		_brasa(punto, Vector2(randf_range(-60, 60), randf_range(-90, -30)))
	match parte:
		"caldera":
			_soltar_rueda()
			_mensaje("¡La caldera revienta! Ha perdido una rueda")
			if fase == Fase.ATASCADA:
				_t = maxf(_t, R.COSECHADORA_ATASCADA - 1.0)
		"frontal":
			_mensaje("¡El depósito pierde fuego de Giza!")
		"techo":
			_mensaje("¡El techo arde! Sus tuercas caen en llamas")
	if rotas() >= 3:
		_empezar_corazon.call_deferred()


## La rueda grande sale volando al reventar la caldera
func _soltar_rueda() -> void:
	_capas["rueda_g"].visible = false
	_rueda_suelta = Sprite2D.new()
	_rueda_suelta.texture = _capas["rueda_g"].texture
	_rueda_suelta.region_enabled = true
	_rueda_suelta.region_rect = Rect2(48 - 16, 80 - 16, 32, 32)
	_rueda_suelta.top_level = true
	_rueda_suelta.z_index = 3
	_rueda_suelta.global_position = _sitio(P_RUEDA)
	add_child(_rueda_suelta)
	_rueda_vel = Vector2(-_mira * 110.0, -170.0)


func _mover_rueda_suelta(delta: float) -> void:
	if _rueda_suelta == null:
		return
	_rueda_vel.y += 420.0 * delta
	_rueda_suelta.global_position += _rueda_vel * delta
	_rueda_suelta.rotation += -_rueda_vel.x * 0.06 * delta
	_rueda_suelta.modulate.a = maxf(0.0, _rueda_suelta.modulate.a - delta * 0.6)
	if _rueda_suelta.modulate.a <= 0.0:
		_rueda_suelta.queue_free()
		_rueda_suelta = null


func _mensaje(texto: String) -> void:
	for hud in get_tree().get_nodes_in_group("hud"):
		if hud.has_method("mostrar_mensaje"):
			hud.call("mostrar_mensaje", texto)


func _vencer() -> void:
	_cambiar(Fase.VENCIDA)
	_activar_partes()
	_anillos.clear()
	Sonido.efecto("cosechadora_vencida")
	Sonido.musica("", 1.5)
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.call("morir")
	for n in get_tree().get_nodes_in_group("tuercas"):
		n.queue_free()
	for n in get_tree().get_nodes_in_group("chatarra"):
		n.call("romper")
	borde = 1.0
	_capa_borde.queue_redraw()
	if _fuego:
		_fuego.apagar_todo()
	Impacto.temblar(5.0, 1.2)


func _proceso_vencida() -> void:
	if _t < 1.8:
		_blanco = 0.05 if int(_t * 8.0) % 2 == 0 else 0.0
		_cuerpo.position.x = sin(_t * 50.0) * 1.0
		if int(_t * 12.0) % 3 == 0:
			_humear(1, Color("6b2a8f"), P_CORAZON)
			var astillas: Node2D = ASTILLAS.new()
			astillas.cantidad = 4
			astillas.fuerza = 60.0
			astillas.position = global_position + Vector2(randf_range(-50, 50), -randf_range(10, 80))
			get_parent().add_child(astillas)
	else:
		_cuerpo.position.x = 0.0
	if _t > 5.0 and is_in_group("jefes"):
		remove_from_group("jefes")
		if _barra:
			_barra.call("cerrar")
		destruido.emit()


# --- Dibujo --------------------------------------------------------------------------------

func _animar(delta: float) -> void:
	_cuerpo.scale.x = _mira
	var c: Dictionary = _capas
	var parada := fase in [Fase.ATASCADA, Fase.CHOQUE, Fase.CORAZON, Fase.VENCIDA, Fase.LANZA, Fase.RESOPLA]
	# ruedas y pistones al ritmo de lo que anda; el molinete gira siempre (enredado si está atascada)
	c["rueda_g"].frame = int(_recorrido / 5.0) % 4
	c["rueda_p"].frame = int(_recorrido / 3.0) % 4
	c["piston"].frame = int(_recorrido / 4.0) % 4 if not parada else int(_tiempo * 3.0) % 2
	if fase in [Fase.ATASCADA, Fase.CORAZON, Fase.VENCIDA] or (fase == Fase.PRESENTACION and _t < 0.8):
		c["molinete"].frame = 4
	else:
		var giro := 8.0 + etapa() * 3.0
		if fase in [Fase.PREPARA, Fase.EMBISTE]:
			giro = 22.0
		elif fase == Fase.CHOQUE:
			giro = 3.0
		c["molinete"].frame = int(_tiempo * giro) % 4
	c["caldera"].frame = 2 if partes["caldera"] <= 0 else (1 if caldera_abierta() else 0)
	for n in ["techo", "frontal"]:
		var s: Sprite2D = c["dep_" + n]
		if partes[n] <= 0:
			s.frame = 3
		elif partes[n] < R.COSECHADORA_PARTES[n]:
			s.frame = 2
		else:
			s.frame = int(_tiempo * 4.0) % 2
	c["chasis"].frame = 2 if fase in [Fase.CORAZON, Fase.VENCIDA] else (1 if fase in [Fase.LANZA, Fase.RESOPLA] else 0)
	c["corazon"].visible = fase == Fase.CORAZON
	c["corazon"].frame = int(_tiempo * (12.0 if corazon_abierto() else 5.0)) % 4
	c["enredaderas"].visible = fase == Fase.VENCIDA and _t >= 1.8
	c["rueda_g"].visible = partes["caldera"] > 0
	# destello blanco en la parte golpeada
	var mapa := {"caldera": "caldera", "frontal": "dep_frontal", "techo": "dep_techo", "corazon": "corazon"}
	for n in mapa:
		c[mapa[n]].self_modulate = Color(3, 3, 3) if _destellos.get(n, 0.0) > 0.0 else Color.WHITE
	if fase == Fase.VENCIDA:
		_cuerpo.modulate = Color(3, 3, 3) if _blanco > 0.0 else Color.WHITE
		queue_redraw()
		return
	# traqueteo: la chapa vibra al andar, mucho más antes de embestir; sin rueda grande, va ladeada y da bandazos
	var anda := fase in [Fase.AVANZA, Fase.EMBISTE, Fase.GIRA]
	_cuerpo.position = Vector2(sin(_tiempo * 60.0) * 1.2 if fase == Fase.PREPARA else 0.0,
		-1.0 if anda and int(_recorrido / 4.0) % 2 == 0 else 0.0)
	if fase == Fase.CORAZON:
		_cuerpo.position = Vector2(sin(_tiempo * 40.0) * 0.6 if _desde_anillo > R.COSECHADORA_ANILLO_CADA[1] - 0.5 else 0.0, 2.0)
	var ladeo := 0.0
	if partes["caldera"] <= 0 and fase != Fase.CORAZON:
		ladeo = -0.05 + (sin(_tiempo * 2.6) * 0.03 if anda else 0.0)
	_cuerpo.rotation = ladeo * _mira
	# cuanto más Ira, más al rojo vivo (y en Frenesí, la chapa parpadea como una brasa)
	var calor := clampf(ira / 100.0, 0.0, 1.0)
	var latido := 0.5 + 0.5 * sin(_tiempo * (6.0 + calor * 10.0))
	var tinte := Color(1.0 + 0.35 * calor + 0.15 * calor * latido, 1.0 - 0.1 * calor, 1.0 - 0.35 * calor)
	if fase in [Fase.PREPARA, Fase.EMBISTE]:
		tinte = tinte.lerp(Color(1.6, 0.85, 0.55), 0.5 + 0.5 * latido)
	elif fase == Fase.RESOPLA:
		tinte = tinte.lerp(Color(1.0, 1.0, 1.0), clampf(_t / R.COSECHADORA_RESOPLA, 0.0, 1.0))
	_cuerpo.modulate = Color(3, 3, 3) if _blanco > 0.0 else tinte
	# humo de Giza por la chimenea (y, con Ira, brasas); humo negro por las partes rotas
	if fase != Fase.ATASCADA and randf() < delta * (4.0 + etapa() * 3.0):
		_humear(1, Color("3a1650") if etapa() < 2 else Color("6b2a8f"), P_CHIMENEA)
	if fase != Fase.ATASCADA and etapa() >= 1 and randf() < delta * (6.0 + etapa() * 8.0):
		_brasa(P_CHIMENEA, Vector2(randf_range(-12, 12), randf_range(-50, -25)))
	for n in ["caldera", "frontal", "techo"]:
		if partes[n] <= 0 and randf() < delta * 5.0:
			var punto: Vector2 = {"caldera": P_CALDERA, "frontal": P_FRONTAL, "techo": P_TECHO}[n]
			_humear(1, Color("2a2228"), punto + Vector2(0, -6))
			if randf() < 0.6:
				_brasa(punto, Vector2(randf_range(-14, 14), randf_range(-40, -20)))
	queue_redraw()


func _brasa(desde: Vector2, vel: Vector2) -> void:
	_humo.append({"p": Vector2(desde.x * _mira, desde.y), "v": vel, "t": 0.0, "dura": randf_range(0.4, 0.9), "c": Color("f9b947"), "r": 0.0})


func _humear(n: int, color: Color, desde := Vector2(0, -40)) -> void:
	var p := Vector2(desde.x * _mira, desde.y)
	for k in n:
		_humo.append({"p": p + Vector2(randf_range(-8, 8), randf_range(-4, 4)), "v": Vector2(randf_range(-6, 6), randf_range(-26, -12)),
			"t": 0.0, "dura": randf_range(0.8, 1.6), "c": color, "r": randf_range(2.0, 4.0)})


func _mover_humo(delta: float) -> void:
	for h in _humo:
		h["t"] += delta
		h["p"] += h["v"] * delta
	_humo = _humo.filter(func(h: Dictionary) -> bool: return h["t"] < h["dura"])


func _local(punto: Vector2) -> Vector2:
	return Vector2(punto.x * _mira, punto.y)


func _draw() -> void:
	if fase == Fase.DORMIDA:
		return
	# aviso del acelerón: una franja roja por su fila (tan ancha como el fuego que va a dejar)
	if fase == Fase.PREPARA:
		var largo := 340.0
		var a := 0.22 + 0.22 * sin(_tiempo * 24.0)
		var filas: int = R.COSECHADORA_FUEGO_ANCHO[etapa()]
		var alto := 20.0 + (filas - 1) * 16.0
		draw_rect(Rect2(Vector2(minf(0.0, _mira * largo), -6 - alto / 2.0), Vector2(largo, alto)), Color(0.9, 0.2, 0.08, a))
		for k in 7:
			var x := _mira * (70.0 + k * 38.0)
			draw_line(Vector2(x - _mira * 6, -12), Vector2(x, -6), Color(1, 0.85, 0.5, 0.85), 2.0)
			draw_line(Vector2(x, -6), Vector2(x - _mira * 6, 0), Color(1, 0.85, 0.5, 0.85), 2.0)
	# los anillos de fuego del corazón (con sus dos huecos)
	for an in _anillos:
		_dibujar_anillo(an)
	# llamas por detrás: con Ira, el tubo de escape escupe fuego; al acelerar, un chorro enorme
	if fase not in [Fase.ATASCADA, Fase.VENCIDA, Fase.CORAZON] and (etapa() >= 1 or fase in [Fase.PREPARA, Fase.EMBISTE]):
		var largo_ch := 6.0 + etapa() * 4.0
		if fase == Fase.EMBISTE:
			largo_ch = 30.0 + etapa() * 7.0
		elif fase == Fase.PREPARA:
			largo_ch = 12.0 + _t * 20.0
		_chorro(_local(P_ESCAPE), -_mira, largo_ch, 5.0)
	# fuga del depósito frontal: un chorro que gotea fuego, y las cuchillas en llamas
	if partes["frontal"] <= 0 and fase not in [Fase.CORAZON, Fase.VENCIDA]:
		_chorro(_local(P_BOQUILLA), _mira, 7.0 + sin(_tiempo * 13.0) * 2.0, 3.0)
		for k in 5:
			var x := _mira * (24.0 + k * 8.0)
			var alto := 5.0 + 3.0 * sin(_tiempo * (11.0 + k * 1.7) + k)
			draw_colored_polygon(PackedVector2Array([Vector2(x - 2, -3), Vector2(x + sin(_tiempo * 9.0 + k), -3 - alto).round(), Vector2(x + 2, -3)]),
				Color("ef8a26", 0.9))
			draw_colored_polygon(PackedVector2Array([Vector2(x - 1, -3), Vector2(x, -3 - alto * 0.55).round(), Vector2(x + 1, -3)]), Color("fde27e"))
	# la caldera reventada sigue ardiendo por dentro
	if partes["caldera"] <= 0 and fase != Fase.VENCIDA:
		var p := _local(P_CALDERA) + Vector2(0, -2)
		for k in 3:
			var alto := 6.0 + 4.0 * sin(_tiempo * (9.0 + k * 3.0) + k)
			var x := p.x + (k - 1) * 4.0
			draw_colored_polygon(PackedVector2Array([Vector2(x - 2, p.y + 4), Vector2(x, p.y + 4 - alto).round(), Vector2(x + 2, p.y + 4)]),
				Color("ef8a26", 0.85) if k != 1 else Color("a855d6", 0.9))
	# lo que está al aire brilla (¡aquí hay que golpear!)
	if caldera_abierta():
		_marcar(_local(P_CALDERA), Color(1.0, 0.6, 0.3))
	if frontal_al_aire():
		_marcar(_local(P_FRONTAL), Color(1.0, 0.6, 0.3))
	if techo_al_aire() and etapa() >= 0:
		# el techo no se alcanza con el cetro: un brillo violeta para recordar que ahí van las semillas
		var pulso := 0.5 + 0.5 * sin(_tiempo * 8.0)
		draw_circle(_local(P_TECHO), 9.0 + pulso * 2.0, Color(0.66, 0.33, 0.84, 0.12 + 0.12 * pulso))
	if fase == Fase.CORAZON:
		var abierto := corazon_abierto()
		var pulso := 0.5 + 0.5 * sin(_tiempo * (14.0 if abierto else 5.0))
		var col := Color(1.0, 0.85, 0.5) if abierto else Color(0.66, 0.33, 0.84)
		draw_circle(P_CORAZON, 14.0 + pulso * 4.0, Color(col, 0.12 + 0.16 * pulso))
		if abierto:
			_marcar(P_CORAZON, col)
		elif _desde_anillo > R.COSECHADORA_ANILLO_CADA[1] - 0.5 or _desde_anillo < 0.0:
			# a punto de lanzar un anillo: el suelo alrededor se pone al rojo
			draw_arc(Vector2(0, -6), 28.0, 0, TAU, 32, Color(1.0, 0.3, 0.1, 0.35 + 0.3 * pulso), 3.0)
	for h in _humo:
		var f: float = h["t"] / h["dura"]
		if h["r"] <= 0.0:
			# brasa: un píxel que sube y se apaga (amarillo → naranja → violeta)
			var col: Color = Color("fde27e") if f < 0.3 else (Color("ef8a26") if f < 0.7 else Color("a855d6"))
			draw_rect(Rect2(h["p"].round(), Vector2.ONE), Color(col, 1.0 - f))
			continue
		draw_circle(h["p"], h["r"] * (1.0 + f), Color(h["c"], 0.45 * (1.0 - f)))


func _chorro(base: Vector2, sentido: float, largo: float, gordo_max: float) -> void:
	for k in 3:
		var temblor := sin(_tiempo * (23.0 + k * 7.0) + k) * 0.25 + 0.75
		var l := largo * temblor * (1.0 - k * 0.22)
		var punta := base + Vector2(sentido * l, sin(_tiempo * 17.0 + k * 2.0) * 2.0)
		var col: Color = [Color("6b2a8f"), Color("ef8a26"), Color("fde27e")][k]
		var gordo := gordo_max - k * gordo_max * 0.28
		draw_colored_polygon(PackedVector2Array([(base + Vector2(0, -gordo)).round(), punta.round(), (base + Vector2(0, gordo)).round()]),
			Color(col, 0.9))


func _marcar(p: Vector2, col: Color) -> void:
	var pulso := 0.5 + 0.5 * sin(_tiempo * 10.0)
	draw_circle(p, 10.0 + pulso * 3.0, Color(col, 0.15 + 0.15 * pulso))
	var flecha := p + Vector2(0, -20.0 - pulso * 3.0)
	draw_colored_polygon(PackedVector2Array([flecha + Vector2(0, 6), flecha + Vector2(-4, 0), flecha + Vector2(4, 0)]), Color("fff3c4"))


func _dibujar_anillo(an: Dictionary) -> void:
	var r: float = an["r"]
	var centro := Vector2(0, -6)
	var medio := deg_to_rad(R.COSECHADORA_ANILLO_HUECO) / 2.0
	var vida_a := clampf((460.0 - r) / 80.0, 0.0, 1.0)
	for k in 2:
		# cada mitad va de un hueco al otro
		var desde: float = an["hueco"] + k * PI + medio
		var hasta: float = an["hueco"] + (k + 1) * PI - medio
		var puntos := maxi(12, int(r * 0.25))
		draw_arc(centro, r, desde, hasta, puntos, Color(0.42, 0.16, 0.56, 0.85 * vida_a), 7.0)
		draw_arc(centro, r, desde, hasta, puntos, Color(0.94, 0.54, 0.15, 0.95 * vida_a), 4.0)
		draw_arc(centro, r - 1.0, desde, hasta, puntos, Color(0.99, 0.89, 0.49, vida_a), 1.5)
		# lenguas de fuego a lo largo del anillo
		var n := int(r / 10.0)
		for i in n:
			var a := lerpf(desde, hasta, (i + 0.5) / n)
			var p := centro + Vector2.from_angle(a) * r
			var alto := 3.0 + 2.5 * sin(_tiempo * 12.0 + i * 1.3)
			draw_colored_polygon(PackedVector2Array([p + Vector2(-2, 0), (p + Vector2(0, -alto)).round(), p + Vector2(2, 0)]),
				Color("ef8a26", vida_a))


func _dibujar_borde() -> void:
	if borde >= 0.995 or zona == null:
		return
	# un anillo de espinas de Giza que se cierra desde el borde de la arena
	var rx: float = zona.radios_umbral.x * borde
	var ry: float = zona.radios_umbral.y * borde
	var c: Vector2 = zona.global_position
	var n := 64
	for k in n:
		var a := TAU * k / n
		var p := c + Vector2(cos(a) * rx, sin(a) * ry)
		var fuera := c + Vector2(cos(a) * zona.radios_umbral.x, sin(a) * zona.radios_umbral.y)
		_capa_borde.draw_line(p, fuera, Color(0.16, 0.05, 0.22, 0.6), 7.0)
		var pico := p + (p - c).normalized() * -4.0 + Vector2(0, -9 - (k % 3) * 2)
		_capa_borde.draw_colored_polygon(PackedVector2Array([p + Vector2(-3, 0), pico, p + Vector2(3, 0)]),
			Color("a855d6") if k % 2 == 0 else Color("6b2a8f"))


## Durante la pelea, la cámara enseña el campo entero
func _encuadrar(delta: float, maisha: Node2D) -> void:
	var camara := get_viewport().get_camera_2d()
	if camara == null or maisha == null or camara.get_parent() != maisha:
		return
	var peleando := fase != Fase.DORMIDA and is_in_group("jefes")
	var objetivo := Vector2.ZERO
	if peleando:
		objetivo = (zona.global_position + Vector2(0, -16) - maisha.global_position) * 0.7
	camara.position = camara.position.lerp(objetivo, minf(1.0, delta * 3.0)).round()
