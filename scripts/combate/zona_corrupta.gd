extends Node2D
## ZONA CORRUPTA: una zona de combate dentro del propio mundo.
## Es «el nudo de raíces de piedra»: Giza se agarra a una raíz del mundo, le bebe la vida y la vuelve
## de piedra. Por las grietas corre su luz violeta hacia el Corazón de Giza (el Núcleo), y una sombra
## viva se mueve alrededor de él. Al purgarla, la raíz vuelve a ser madera y la vida corre hacia fuera.
## El suelo de cada zona lo dibuja herramientas/dibujar_zona.py (arte/zonas/<mapa>_<zona>.png).
##
##   DORMIDA   → Maisha está lejos. Se ve el gris y las espinas bajas del umbral.
##   AVISO     → Maisha entra en el BORDE: suena la tensión y aparecen Vida y Aliento.
##   CERRADA   → Maisha cruza el UMBRAL: las raíces-espina suben y no se puede salir.
##               El Núcleo de Giza invoca Petrinos; solo las semillas lo dañan.
##   PURGANDO  → El Núcleo se rompe: los enemigos se desmoronan y el color vuelve en una ola.
##   PURGADA   → La zona vuelve a estar viva.
## Si Maisha cae dentro, vuelve al borde con la zona reiniciada y sin perder lo recogido.

signal estado_cambiado(estado: int)
signal mensaje(texto: String)

enum Estado { DORMIDA, AVISO, CERRADA, PURGANDO, PURGADA }

const R := preload("res://scripts/combate/reglas_combate.gd")
const PETRINO := preload("res://scripts/enemigos/petrino.gd")
const NUCLEO := preload("res://scripts/enemigos/nucleo_giza.gd")
const FORMA := preload("res://scripts/combate/forma_zona.gd")
const RESCOLDO := preload("res://scripts/mundo/objetos/rescoldo.gd")
const JEFES := {"mzizi": preload("res://scripts/enemigos/mzizi.gd"), "pembe": preload("res://scripts/enemigos/pembe.gd"),
	"konokono": preload("res://scripts/enemigos/konokono.gd"), "cosechadora": preload("res://scripts/enemigos/cosechadora.gd"),
	"kambare": preload("res://scripts/enemigos/kambare.gd"), "mamba": preload("res://scripts/enemigos/mamba.gd"),
	"guardian": preload("res://scripts/enemigos/guardian.gd")}
## Los enemigos que puede invocar una zona (según la región): petrino (errante) y jabalí de hierro (cazador)
const ENEMIGOS := {"petrino": preload("res://scripts/enemigos/petrino.gd"), "jabali": preload("res://scripts/enemigos/jabali.gd"),
	"babosa": preload("res://scripts/enemigos/babosa.gd"), "rana": preload("res://scripts/enemigos/rana.gd"),
	"topo": preload("res://scripts/enemigos/topo.gd"), "cuervo": preload("res://scripts/enemigos/cuervo.gd"),
	"murcielago": preload("res://scripts/enemigos/murcielago.gd"), "cangrejo": preload("res://scripts/enemigos/cangrejo.gd"),
	"bundi": preload("res://scripts/enemigos/bundi.gd"), "buibui": preload("res://scripts/enemigos/buibui.gd")}
const SOMBRA_GIZA := Color(0.10, 0.05, 0.14)
const LUZ_GIZA := Color("a855d6")
const LUZ_VIDA := Color("fff3c4")
const LUZ_BROTE := Color("6fcf4f")

@export var radios_umbral := Vector2(240, 176)   # tamaño de la zona cerrada (semiejes, en píxeles)
@export var ancho_borde := 112.0                  # anchura del borde de aviso (7 casillas)
@export var entidades: NodePath                   # nodo con orden de profundidad donde viven Maisha y los enemigos
@export var enemigos_al_cerrar := 2               # Petrinos que aparecen al cerrarse
@export var nombre := ""                          # para los mensajes (opcional)
@export var ya_purgada := false                   # se purgó en otra visita: empieza viva, sin combate
@export var activa := true                        # dormida del todo (no avisa ni se cierra) mientras sea false
@export var mensajes := true                      # sus avisos arriba (en el Kitovu los da el narrador)
@export var variante := "raiz"                    # el mundo: de qué está hecha (arte/zonas/<variante>/)
@export var dibujo := ""                          # su suelo: arte/zonas/<dibujo>.png y datos/zonas/<dibujo>.json
@export var pequena := false                      # zona de práctica: Corazón pequeño, con menos vida
@export var jefe := ""                            # en vez de Corazón, un jefe (p. ej. «mzizi»)
@export var tipos_enemigo: PackedStringArray = ["petrino"]   # se van turnando al invocar

var estado: int = Estado.DORMIDA
var _maisha: Node2D
var _entidades: Node2D
var _gestor: Node                 # gestor de la corrupción de la región (grupo "corrupcion")
var _indice := -1
var _nucleo: Node2D
var _espinas: Array[Sprite2D] = []
var _altura_espinas := 0.0       # 0 = bajas, 3 = altas
var _invocar := 0.0
var _punto_entrada := Vector2.ZERO
var _radio_purga := 0.0
var _flores: Array[Vector2] = []
var _avisada := false             # el aviso «Prepárate» solo sale la primera vez
var _suelo_piedra: Sprite2D
var _suelo_vivo: Sprite2D
var _raices: Array[PackedVector2Array] = []
var _tiempo := 0.0
var _vida_raices := 0.0           # 0..1: la luz de la vida que corre hacia fuera al purgar
var forma := PackedFloat32Array() # la forma natural del borde (ver forma_zona.gd)
var _invocados := 0
var modo_eco := false             # la pelea de ahora es el ECO de un jefe ya vencido (ver revivir_eco)
var _rescoldo: Node2D
var _ocultos: Array[Node2D] = []   # durante el eco, el jefe despierto de verdad (el Guardián) se aparta


func _ready() -> void:
	add_to_group("zonas")
	if jefe != "":
		add_to_group("arena_jefe")
	_entidades = get_node(entidades)
	_gestor = get_tree().get_first_node_in_group("corrupcion")
	_crear_suelo()
	if _gestor:
		_indice = _gestor.registrar(global_position, radios_umbral, ancho_borde, forma)
	if ya_purgada:
		if _gestor:
			_gestor.purgar(_indice, true)
		_brotar_flores()
		if _suelo_piedra:
			_suelo_piedra.visible = false
			_suelo_vivo.modulate.a = 1.0
		estado = Estado.PURGADA
		queue_redraw()
		_poner_rescoldo.call_deferred()
		return
	_crear_espinas.call_deferred()
	_crear_nucleo.call_deferred()


## El suelo de la zona: la raíz de piedra y, debajo, la misma raíz viva (aparece al purgar)
func _crear_suelo() -> void:
	if dibujo == "":
		return
	var ruta := "res://arte/zonas/%s.png" % dibujo
	if not ResourceLoader.exists(ruta):
		return
	var textura: Texture2D = load(ruta)
	_suelo_vivo = _sprite_suelo(textura, 1)
	_suelo_vivo.modulate.a = 0.0
	_suelo_piedra = _sprite_suelo(textura, 0)
	var datos := "res://datos/zonas/%s.json" % dibujo
	if ResourceLoader.exists(datos):
		var json: Dictionary = (load(datos) as JSON).data
		for v in json.get("forma", []):
			forma.append(float(v))
		for raiz in json["raices"]:
			var puntos := PackedVector2Array()
			for p in raiz:
				puntos.append(Vector2(float(p[0]), float(p[1])))
			if puntos.size() > 2:
				_raices.append(puntos)


func _sprite_suelo(textura: Texture2D, fotograma: int) -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.texture = textura
	sprite.hframes = 2
	sprite.frame = fotograma
	sprite.z_index = -1          # sobre el suelo, debajo de la luz y las flores de la zona
	sprite.z_as_relative = true
	add_child(sprite)
	move_child(sprite, 0)
	return sprite


## Un punto del umbral (el borde que se cierra) en la dirección del ángulo «a»
func punto_del_umbral(a: float, escala := 1.0) -> Vector2:
	var v := Vector2(cos(a), sin(a))
	return global_position + v * radios_umbral * FORMA.factor(forma, v) * escala


func _crear_espinas() -> void:
	# una raíz-espina cada ~9 píxeles a lo largo del umbral, siguiendo su forma natural
	var azar := RandomNumberGenerator.new()
	azar.seed = 5
	var puntos: Array[Vector2] = []
	var anterior := punto_del_umbral(0.0)
	var recorrido := 9.0
	for k in 720:
		var p := punto_del_umbral(TAU * k / 720.0)
		recorrido += p.distance_to(anterior)
		anterior = p
		if recorrido >= 9.0:
			recorrido = 0.0
			puntos.append(p)
	for p in puntos:
		var espina := Sprite2D.new()
		espina.texture = load("res://arte/zonas/%s/espinas.png" % variante)
		espina.hframes = 4
		espina.offset = Vector2(0, -9)
		espina.flip_h = azar.randf() < 0.5
		espina.position = p + Vector2(azar.randf_range(-1, 1), 0).round()
		_entidades.add_child(espina)
		_espinas.append(espina)
	_poner_altura_espinas(0.0)


func _crear_nucleo() -> void:
	if JEFES.has(jefe):
		_nucleo = JEFES[jefe].new()
		_nucleo.zona = self
	else:
		_nucleo = NUCLEO.new()
		_nucleo.pequeno = pequena
	_nucleo.variante = variante
	_nucleo.position = global_position
	_entidades.add_child(_nucleo)
	_nucleo.destruido.connect(_al_romper_nucleo)


func _process(delta: float) -> void:
	_tiempo += delta
	if estado != Estado.PURGADA or _vida_raices > 0.0:
		queue_redraw()
	if _maisha == null:
		_maisha = get_tree().get_first_node_in_group("maisha") as Node2D
		if _maisha:
			_maisha.caida.connect(_al_caer_maisha)
		return
	var p := _maisha.global_position
	# mientras Maisha pelea en otra mancha, esta no despierta (si dos manchas quedan muy juntas,
	# se cerrarían las dos a la vez)
	if estado in [Estado.DORMIDA, Estado.AVISO] and _otra_cerrada():
		if estado == Estado.AVISO:
			_cambiar(Estado.DORMIDA)
		return
	if not activa and estado in [Estado.DORMIDA, Estado.AVISO]:
		if estado == Estado.AVISO:
			_cambiar(Estado.DORMIDA)
		return
	match estado:
		Estado.DORMIDA:
			if en_borde(p):
				_cambiar(Estado.AVISO)
				Sonido.efecto("zona_aviso")
				if not _avisada:
					_avisada = true
					mensaje.emit("Una zona corrupta... Prepárate")
		Estado.AVISO:
			if not en_borde(p):
				_cambiar(Estado.DORMIDA)
			elif distancia_normal(p) < 0.97:
				_cerrar()
		Estado.CERRADA:
			_maisha.global_position = limitar(p)
			if jefe != "":
				return                    # el jefe invoca a sus propios Petrinos
			_invocar -= delta
			if _invocar <= 0.0:
				_invocar = R.NUCLEO_INVOCA_CADA
				if get_tree().get_nodes_in_group("enemigos").size() < R.NUCLEO_MAX_ENEMIGOS:
					_invocar_petrino(true)
		Estado.PURGANDO:
			queue_redraw()


# --- Geometría ------------------------------------------------------------------

## 1.0 en el umbral, menos de 1 dentro de la zona cerrada (con su forma natural)
func distancia_normal(p: Vector2) -> float:
	var n := (p - global_position) / radios_umbral
	return n.length() / FORMA.factor(forma, n)


func en_borde(p: Vector2) -> bool:
	var n := (p - global_position) / (radios_umbral + Vector2.ONE * ancho_borde)
	return n.length() / FORMA.factor(forma, n) < 1.0


## Mantiene un punto dentro de la zona mientras está cerrada (las espinas no dejan salir)
func limitar(p: Vector2) -> Vector2:
	if estado != Estado.CERRADA:
		return p
	var r := distancia_normal(p)
	var maximo := 0.92
	if r > maximo:
		return global_position + (p - global_position) * (maximo / r)
	return p


# --- Estados ----------------------------------------------------------------------

func _cambiar(nuevo: int) -> void:
	estado = nuevo
	estado_cambiado.emit(estado)


func _cerrar() -> void:
	_cambiar(Estado.CERRADA)
	_punto_entrada = _maisha.global_position
	create_tween().tween_method(_poner_altura_espinas, 0.0, 3.0, 0.45).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	Sonido.efecto("espinas_suben")
	Sonido.musica(_musica_de_jefe() if jefe != "" else "combate", 0.8)
	_invocar = R.NUCLEO_INVOCA_CADA
	if jefe != "":
		# el Bestiario cuenta los golpes que se lleva Maisha en la pelea (para el rango del jefe)
		Bestiario.empezar_jefe(jefe)
		if _maisha and _maisha.has_signal("herida") and not _maisha.is_connected("herida", Bestiario.al_herir):
			_maisha.connect("herida", Bestiario.al_herir)
		_nucleo.call("despertar")
		return
	mensaje.emit("¡Las raíces de piedra te encierran! Rompe el Corazón de Giza con semillas")
	for i in enemigos_al_cerrar:
		_invocar_petrino(false)


## Un Petrino que sale de un punto concreto (p. ej. de un agujero de Mzizi)
## Cada jefe con su música, si la tiene (audio/musica/jefe_<nombre>.ogg); si no, la de Mzizi
func _musica_de_jefe() -> String:
	return "jefe_" + jefe if ResourceLoader.exists("res://audio/musica/jefe_%s.ogg" % jefe) else "jefe"


## El siguiente enemigo que toca invocar (se turnan los tipos de la región)
func _nuevo_enemigo() -> Node2D:
	var tipo: String = tipos_enemigo[_invocados % tipos_enemigo.size()] if not tipos_enemigo.is_empty() else "petrino"
	_invocados += 1
	return ENEMIGOS.get(tipo, PETRINO).new()


## Un enemigo de un tipo concreto que sale en un punto (p. ej. los jabalíes que llama Pembe)
func invocar_en(posicion: Vector2, tipo: String) -> void:
	var enemigo: Node2D = ENEMIGOS.get(tipo, PETRINO).new()
	enemigo.zona = self
	enemigo.variante = variante
	enemigo.position = posicion
	_entidades.add_child(enemigo)
	enemigo.scale = Vector2(0.2, 0.2)
	create_tween().tween_property(enemigo, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK)


func invocar_petrino_en(posicion: Vector2) -> void:
	var enemigo: Node2D = PETRINO.new()
	enemigo.zona = self
	enemigo.variante = variante
	enemigo.position = posicion
	_entidades.add_child(enemigo)
	enemigo.scale = Vector2(0.2, 0.2)
	create_tween().tween_property(enemigo, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK)


func _invocar_petrino(desde_nucleo: bool) -> void:
	var enemigo: Node2D = _nuevo_enemigo()
	enemigo.zona = self
	enemigo.variante = variante
	var posicion: Vector2
	if desde_nucleo and is_instance_valid(_nucleo):
		posicion = _nucleo.global_position + Vector2.from_angle(randf() * TAU) * 14.0
	else:
		# lejos de Maisha, entre ella y el núcleo no
		for intento in 12:
			posicion = global_position + Vector2(randf_range(-0.7, 0.7) * radios_umbral.x, randf_range(-0.7, 0.7) * radios_umbral.y)
			if posicion.distance_to(_maisha.global_position) > 90.0:
				break
	enemigo.position = posicion
	_entidades.add_child(enemigo)
	# aparece brotando del suelo
	enemigo.scale = Vector2(0.2, 0.2)
	create_tween().tween_property(enemigo, "scale", Vector2.ONE, 0.3).set_trans(Tween.TRANS_BACK)


func _al_romper_nucleo() -> void:
	_cambiar(Estado.PURGANDO)
	Sonido.efecto("ola_purga")
	mensaje.emit("¡Zona purgada!")
	if jefe != "":
		Bestiario.jefe_vencido(jefe)
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.set_meta("sin_contar", true)          # (los que se desmoronan con la purga no cuentan en el Bestiario)
		e.call("morir")
	var t := create_tween()
	t.tween_method(_poner_radio_purga, 0.0, 1.0 + ancho_borde / radios_umbral.x + 0.1, 2.4).set_trans(Tween.TRANS_SINE)
	t.parallel().tween_method(_poner_altura_espinas, 3.0, 0.0, 0.6).set_delay(0.4)
	if _suelo_piedra:
		# la piedra se deshace y debajo aparece la raíz viva, con la luz corriendo hacia fuera
		t.parallel().tween_property(_suelo_vivo, "modulate:a", 1.0, 1.6).set_delay(0.3)
		t.parallel().tween_property(_suelo_piedra, "modulate:a", 0.0, 1.8).set_delay(0.5)
		t.parallel().tween_property(self, "_vida_raices", 1.0, 2.4)
	t.tween_callback(_terminar_purga)


func _terminar_purga() -> void:
	if _gestor and not modo_eco:
		_gestor.purgar(_indice)
	for espina in _espinas:
		espina.queue_free()
	_espinas.clear()
	_brotar_flores()
	if _suelo_piedra:
		_suelo_piedra.visible = false
	_cambiar(Estado.PURGADA)
	if modo_eco:
		_acabar_eco()
	modo_eco = false
	_poner_rescoldo()
	_volver_a_la_musica()
	Sonido.fanfarria("victoria" if jefe != "" else "purga")
	create_tween().tween_property(self, "_vida_raices", 0.0, 1.2)
	queue_redraw()


## Brotan flores donde antes había gris
func _brotar_flores() -> void:
	var azar := RandomNumberGenerator.new()
	azar.seed = 9
	for i in 70:
		var a := azar.randf() * TAU
		var r := sqrt(azar.randf()) * 0.95
		_flores.append(Vector2(cos(a) * radios_umbral.x, sin(a) * radios_umbral.y) * r * FORMA.factor(forma, Vector2(cos(a), sin(a))))


func _al_caer_maisha() -> void:
	if estado != Estado.CERRADA:
		return
	if modo_eco:
		# en el eco no pasa nada: el eco se deshace y el rescoldo vuelve
		var hud_eco := get_tree().get_first_node_in_group("hud")
		if hud_eco:
			hud_eco.call("fundido", _deshacer_eco)
		else:
			_deshacer_eco()
		return
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.call("fundido", _reiniciar_tras_caida)
	else:
		_reiniciar_tras_caida()


# --- El eco de un jefe ya vencido (para mejorar su rango en el Bestiario) ---------------------------

## El rescoldo de Giza, en medio de la arena de un jefe vencido, mientras no tenga el oro
func _poner_rescoldo() -> void:
	if jefe == "" or Bestiario.rango(jefe) >= 3 or is_instance_valid(_rescoldo) or _entidades == null:
		return
	_rescoldo = RESCOLDO.new()
	_rescoldo.zona = self
	_rescoldo.position = global_position + Vector2(0, radios_umbral.y * 0.45)      # (abajo: el centro es del jefe)
	_entidades.add_child(_rescoldo)


## Revive el eco del jefe: las espinas vuelven y el jefe despierta. Al vencerlo solo cuenta para el Bestiario.
func revivir_eco() -> void:
	if jefe == "" or estado != Estado.PURGADA:
		return
	modo_eco = true
	_avisada = true
	var nombre_jefe := String(Bestiario.FICHAS.get(jefe, {}).get("nombre", jefe))
	var falta := "la plata" if Bestiario.rango(jefe) < 2 else "el oro"
	mensaje.emit("El eco de %s despierta (buscas %s)" % [nombre_jefe.get_slice(",", 0), falta])
	Sonido.efecto("bundi_conjura", 0.0, global_position)
	# el jefe despierto de verdad (si se queda en la sala, como el Guardián) se aparta mientras dura el eco
	_ocultos.clear()
	for n in _entidades.get_children():
		if n.has_meta("despierto") and n is Node2D:
			_ocultos.append(n)
			n.visible = false
			n.remove_from_group("interactuables")
	_crear_espinas()
	_crear_nucleo()
	# Maisha se aparta hacia el borde (el jefe sale en medio)
	if _maisha:
		var lado := (_maisha.global_position - global_position).normalized()
		_maisha.global_position = punto_del_umbral((lado if lado != Vector2.ZERO else Vector2.DOWN).angle(), 0.8)
	_cambiar(Estado.DORMIDA)


## Al acabar el eco: el jefe del eco se desvanece y vuelve el de verdad
func _acabar_eco() -> void:
	if is_instance_valid(_nucleo):
		var eco := _nucleo
		eco.remove_from_group("interactuables")
		var t := eco.create_tween()
		t.tween_interval(1.5)
		t.tween_property(eco, "modulate:a", 0.0, 1.0)
		t.tween_callback(eco.queue_free)
	for n in _ocultos:
		if is_instance_valid(n):
			n.visible = true
			n.add_to_group("interactuables")
	_ocultos.clear()


func _deshacer_eco() -> void:
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.queue_free()
	for s in get_tree().get_nodes_in_group("semillas"):
		s.queue_free()
	if is_instance_valid(_nucleo):
		_nucleo.queue_free()
	for espina in _espinas:
		espina.queue_free()
	_espinas.clear()
	_acabar_eco()
	modo_eco = false
	var fuera := (_punto_entrada - global_position).normalized()
	_cambiar(Estado.PURGADA)
	_volver_a_la_musica()
	_maisha.call("revivir", punto_del_umbral((fuera if fuera != Vector2.ZERO else Vector2.LEFT).angle(), 1.12))
	mensaje.emit("El eco se deshace. El rescoldo sigue ahí")
	_poner_rescoldo()


func _reiniciar_tras_caida() -> void:
	for e in get_tree().get_nodes_in_group("enemigos"):
		e.queue_free()
	for s in get_tree().get_nodes_in_group("semillas"):
		s.queue_free()
	var registro := get_tree().get_first_node_in_group("registro_brotes")
	if registro:
		registro.limpiar()
	if is_instance_valid(_nucleo):
		_nucleo.reiniciar()
	_poner_altura_espinas(0.0)
	_volver_a_la_musica()
	# vuelve al borde, por donde entró
	var fuera := (_punto_entrada - global_position).normalized()
	if fuera == Vector2.ZERO:
		fuera = Vector2.LEFT
	# justo fuera de las espinas (el borde cercano al umbral siempre está despejado)
	var punto := punto_del_umbral(fuera.angle(), 1.12)
	_cambiar(Estado.AVISO)
	_maisha.call("revivir", punto)
	mensaje.emit("Has vuelto al borde. La zona sigue corrupta")


func _volver_a_la_musica() -> void:
	var escena := get_tree().current_scene
	if escena and escena.has_method("volver_a_su_musica"):
		escena.call("volver_a_su_musica")
	else:
		Sonido.musica("", 2.0)


# --- Dibujo -----------------------------------------------------------------------

func _poner_altura_espinas(valor: float) -> void:
	_altura_espinas = valor
	for espina in _espinas:
		espina.frame = clampi(int(round(valor)), 0, 3)


func _poner_radio_purga(valor: float) -> void:
	_radio_purga = valor
	if _gestor:
		_gestor.poner_purga(_indice, valor)
	queue_redraw()


func _draw() -> void:
	if estado != Estado.PURGADA and estado != Estado.PURGANDO:
		_dibujar_giza()
	if _vida_raices > 0.0:
		_dibujar_vida()
	# la ola de purga: un anillo de chispas de luz que avanza
	if estado == Estado.PURGANDO and _radio_purga > 0.0:
		var puntos := 120
		for i in puntos:
			var a := TAU * i / puntos
			var v := Vector2(cos(a), sin(a))
			var p := (v * radios_umbral * FORMA.factor(forma, v) * _radio_purga).round()
			var color := Color("fff3c4") if i % 3 else Color("6fcf4f")
			draw_rect(Rect2(p, Vector2(2, 2)), color)
	# flores tras la purga
	for f in _flores:
		var q := f.round()
		draw_rect(Rect2(q, Vector2.ONE), Color("e6a852") if int(q.x) % 2 else Color("de6771"))
		draw_rect(Rect2(q + Vector2(0, 1), Vector2.ONE), Color("3e9a35"))


## La sombra viva de Giza alrededor del Corazón y su luz violeta, que corre por las raíces hacia él
func _dibujar_giza() -> void:
	var fuerza := 1.0 if estado == Estado.CERRADA else (0.75 if estado == Estado.AVISO else 0.5)
	# sombra: manchas que respiran y se mueven alrededor del centro, por escalones de píxel
	for k in 7:
		var a := TAU * k / 7.0 + _tiempo * 0.25 + sin(_tiempo * 0.7 + k) * 0.3
		var lejos := 10.0 + 6.0 * sin(_tiempo * 0.9 + k * 1.7)
		var centro := (Vector2(cos(a) * lejos * 1.6, sin(a) * lejos * 0.8)).round()
		var r := 9.0 + 3.0 * sin(_tiempo * 1.3 + k * 2.1)
		_mancha(centro, Vector2(r * 1.5, r * 0.7), Color(SOMBRA_GIZA, 0.30 * fuerza))
	_mancha(Vector2(0, 2), Vector2(22, 9), Color(SOMBRA_GIZA, 0.25 * fuerza))
	# la luz violeta que Giza le bebe a la raíz: gotas que viajan desde las puntas hasta el centro
	if _raices.is_empty():
		return
	var velocidad := 0.22 if estado == Estado.CERRADA else 0.12
	for i in _raices.size():
		var raiz := _raices[i]
		for gota in 2:
			var u := fposmod(_tiempo * velocidad + i * 0.37 + gota * 0.5, 1.0)
			var p := _punto_en(raiz, 1.0 - u).round()
			var alfa := fuerza * sin(u * PI)
			draw_rect(Rect2(p - Vector2(1, 1), Vector2(2, 2)), Color(LUZ_GIZA, alfa))
			var cola := _punto_en(raiz, minf(1.0, 1.0 - u + 0.05)).round()
			draw_rect(Rect2(cola, Vector2.ONE), Color(LUZ_GIZA, alfa * 0.5))


## Al purgar: la vida corre desde el centro hacia las puntas de las raíces
func _dibujar_vida() -> void:
	for i in _raices.size():
		var raiz := _raices[i]
		for gota in 3:
			var u := fposmod(_tiempo * 0.5 + i * 0.29 + gota * 0.33, 1.0)
			var p := _punto_en(raiz, u).round()
			var alfa := _vida_raices * sin(u * PI)
			draw_rect(Rect2(p - Vector2(1, 1), Vector2(2, 2)), Color(LUZ_VIDA if gota % 2 else LUZ_BROTE, alfa))


func _punto_en(raiz: PackedVector2Array, t: float) -> Vector2:
	var f := clampf(t, 0.0, 1.0) * (raiz.size() - 1)
	var i := mini(int(f), raiz.size() - 2)
	return raiz[i].lerp(raiz[i + 1], f - i)


## Una mancha elíptica hecha de bloques de 2x2 (para que se vea pixel art y no un degradado)
func _mancha(centro: Vector2, radios: Vector2, color: Color) -> void:
	var y := -radios.y
	while y <= radios.y:
		var ancho := radios.x * sqrt(maxf(0.0, 1.0 - (y / radios.y) * (y / radios.y)))
		ancho = floorf(ancho / 2.0) * 2.0
		if ancho > 0.0:
			draw_rect(Rect2(centro + Vector2(-ancho, y), Vector2(ancho * 2.0, 2.0)), color)
		y += 2.0


func _otra_cerrada() -> bool:
	for z in get_tree().get_nodes_in_group("zonas"):
		if z != self and z.get("estado") in [Estado.CERRADA, Estado.PURGANDO]:
			return true
	return false
