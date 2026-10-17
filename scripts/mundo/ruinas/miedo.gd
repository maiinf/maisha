extends Node2D
## EL MIEDO DEL PRIMER ÁRBOL (el jefe final de Raíz). No es un monstruo: es el miedo del árbol a acabarse, y Giza es
## su forma. Lleva la pelea de la plaza de las Ruinas:
##   - Se gana RECORDANDO: hay que despertar las nueve piedras del recuerdo (ruinas/piedra_recuerdo.gd: mantener
##     Acción a su lado). Con cada una, Maisha recuerda lo que dijo un eco y el árbol se estremece.
##   - Mientras, el miedo ataca (más deprisa con cada tres piedras):
##       RAÍCES DE PIEDRA: una grieta violeta avisa en línea recta desde el árbol hacia Maisha y, al poco, revientan
##         raíces de piedra a lo largo de ella (quitan una hoja).
##       ANILLOS DE QUIETUD: un aro de escarcha que se abre desde el árbol con dos huecos que giran. Si alcanza a
##         Maisha le sube mucho el frío (ruinas: la escarcha también está aquí). Se pasa por un hueco o con el Latido.
##       QUIETOS: desde la segunda fase salen de entre las piedras.
##   - Con las nueve despiertas, se abre el CORAZÓN DE GIZA en el tronco: romperlo cura al árbol (ruinas/primer_arbol.gd).

signal vencido

const QUIETO := preload("res://scripts/enemigos/quieto.gd")
## Por fase (0: 0-2 piedras · 1: 3-5 · 2: 6-8 · 3: el corazón al aire): segundos entre ataques y velocidad de los anillos
const CADA := [3.4, 2.7, 2.2, 1.9]
const VEL_ANILLO := [70.0, 82.0, 95.0, 100.0]
const AVISO_RAIZ := 0.85
const SALE_RAIZ := 0.5
const ANCHO_RAIZ := 9.0
## Lo que recuerda Maisha con cada piedra (una frase corta de cada eco, para que quepa en el aviso de arriba)
const RECUERDOS := [
	"«Para que nadie quedara solo en una orilla.»",
	"«Esas luces son las raíces del Primer Árbol.»",
	"«Tú y yo somos el mismo árbol.»",
	"«Lo que se siega, Mauti lo guarda.»",
	"«El Silencio no tiene eco.»",
	"«Así sabré por dónde volver.»",
	"«Si subes a buscarme, tráemela.»",
	"«Lo necesario casi nunca es bonito.»",
	"«Se abre recordando.»",
]

var centro := Vector2.ZERO        # el pie del árbol (global)
var radio_plaza := 240.0
var arbol: Node2D
var piedras: Array = []
var activo := false
var despiertas := 0
var _t_ataque := 2.5
var _turno := 0
var _anillos: Array[Dictionary] = []
var _raices: Array[Dictionary] = []
var _tiempo := 0.0


func _ready() -> void:
	z_index = -1
	for p in piedras:
		p.despertada.connect(_al_despertar)


func empezar() -> void:
	activo = true
	_t_ataque = 2.5
	for p in piedras:
		p.activa = true
	Bestiario.empezar_jefe("miedo")
	var maisha := get_tree().get_first_node_in_group("maisha")
	if maisha and not maisha.herida.is_connected(_al_herir):
		maisha.herida.connect(_al_herir)


func _al_herir(vida: int) -> void:
	if activo:
		Bestiario.al_herir(vida)


func fase() -> int:
	if despiertas >= 9:
		return 3
	return int(despiertas / 3)


func _al_despertar(piedra: Node) -> void:
	piedra.indice = despiertas
	despiertas += 1
	var hud := get_tree().get_first_node_in_group("hud")
	if hud:
		hud.mostrar_mensaje(RECUERDOS[clampi(despiertas - 1, 0, 8)])
	if arbol:
		arbol.call("temblar", 0.5)
	_t_ataque = maxf(_t_ataque, 1.4)            # un respiro tras recordar
	if despiertas >= 9 and arbol:
		arbol.call("abrir_corazon")


func terminar() -> void:
	activo = false
	_anillos.clear()
	_raices.clear()
	for q in get_tree().get_nodes_in_group("quietos"):
		q.call("morir")
	for p in piedras:
		p.activa = false
	queue_redraw()


func _process(delta: float) -> void:
	_tiempo += delta
	if not activo:
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if maisha == null:
		return
	var f := fase()
	_t_ataque -= delta
	if _t_ataque <= 0.0:
		_t_ataque = CADA[f]
		_atacar(maisha, f)
	# los anillos de quietud se abren
	for a in _anillos:
		a["antes"] = a["r"]
		a["r"] += VEL_ANILLO[f] * delta
		a["giro"] += a["vel_giro"] * delta
		if not a["tocado"] and _anillo_alcanza(a, maisha):
			a["tocado"] = true
			var escarcha := maisha.get_node_or_null("Escarcha")
			if escarcha:
				escarcha.frio = minf(0.95, escarcha.frio + 0.5)
				escarcha.quieta = 1.3
			Sonido.efecto("clinc", -4.0, maisha.global_position)
			Impacto.fogonazo(Color(0.75, 0.88, 1.0), 0.18, 0.25)
	_anillos = _anillos.filter(func(a: Dictionary) -> bool: return a["r"] < radio_plaza + 30.0)
	# las raíces: aviso → salen → se van
	for r in _raices:
		r["t"] += delta
		if r["t"] >= AVISO_RAIZ and not r["salio"]:
			r["salio"] = true
			Sonido.efecto("raiz_azota", 0.0, r["hacia"])
			Impacto.temblar(1.5, 0.15)
		if r["salio"] and not r["dio"] and _dist_segmento(maisha.global_position, r["desde"], r["hacia"]) < ANCHO_RAIZ:
			if maisha.call("recibir_danio", 1, r["desde"], "raiz"):
				r["dio"] = true
	_raices = _raices.filter(func(r: Dictionary) -> bool: return r["t"] < AVISO_RAIZ + SALE_RAIZ)
	queue_redraw()


func _atacar(maisha: Node2D, f: int) -> void:
	_turno += 1
	if f == 3 or _turno % 2 == 1:
		# raíces de piedra hacia donde está Maisha (en la fase del corazón, tres a la vez, en abanico)
		var hacia := (maisha.global_position - centro).normalized()
		var abanico := [0.0] if f < 2 else ([-0.35, 0.35] if f == 2 else [-0.45, 0.0, 0.45])
		for d in abanico:
			var dir := hacia.rotated(d)
			_raices.append({"desde": centro + dir * 30.0, "hacia": centro + dir * radio_plaza, "t": 0.0, "salio": false, "dio": false})
	else:
		_anillos.append({"r": 26.0, "giro": randf() * TAU, "vel_giro": randf_range(-1.2, 1.2), "tocado": false})
		if arbol:
			arbol.call("temblar", 0.3)
	# desde la segunda fase, Quietos entre las piedras (como mucho tres a la vez)
	if f >= 1 and f < 3 and _turno % 3 == 0 and get_tree().get_nodes_in_group("quietos").size() < 3:
		var donde: Node2D = piedras[randi() % piedras.size()]
		var q: CharacterBody2D = QUIETO.new()
		q.position = donde.global_position + Vector2(randf_range(-14, 14), 18)
		get_parent().get_node("Entidades").add_child(q)
		Sonido.efecto("petrino_aparece", 0.0, q.position)


## ¿El aro alcanza a Maisha? (está en su anchura y no en uno de los dos huecos; el Latido la protege)
func _anillo_alcanza(a: Dictionary, maisha: Node2D) -> bool:
	if maisha.call("es_invulnerable"):
		return false
	var v := maisha.global_position - centro
	# (si el aro ha pasado por donde está en este fotograma, aunque vaya a tirones)
	if v.length() < float(a.get("antes", a["r"])) - 7.0 or v.length() > a["r"] + 7.0:
		return false
	var ang := fposmod(v.angle() - a["giro"], TAU)
	for hueco in [0.0, PI]:
		if absf(angle_difference(ang, hueco)) < 0.42:
			return false
	return true


func _dist_segmento(p: Vector2, a: Vector2, b: Vector2) -> float:
	var ab := b - a
	var t := clampf((p - a).dot(ab) / maxf(ab.length_squared(), 0.001), 0.0, 1.0)
	return p.distance_to(a + ab * t)


func _draw() -> void:
	var o := -global_position
	# los anillos de escarcha (con sus dos huecos): una banda de hielo con el borde azul oscuro, para que se vea
	# bien sobre la piedra clara y la nieve
	for a in _anillos:
		var r: float = a["r"]
		var n := int(r * 0.9) + 30
		for k in n:
			var ang: float = k * TAU / n
			var rel := fposmod(ang - a["giro"], TAU)
			if absf(angle_difference(rel, 0.0)) < 0.42 or absf(angle_difference(rel, PI)) < 0.42:
				continue
			var radial := Vector2(cos(ang), sin(ang))
			var p := centro + radial * r + o
			draw_rect(Rect2((p - radial * 3.0).floor(), Vector2(2, 2)), Color(0.18, 0.28, 0.55, 0.85))
			draw_rect(Rect2((p + radial * 3.0).floor(), Vector2(2, 2)), Color(0.18, 0.28, 0.55, 0.85))
			var brillo := 0.7 + 0.3 * sin(_tiempo * 8.0 + k)
			draw_rect(Rect2((p - radial).floor(), Vector2(2, 3)), Color(0.9, 0.96, 1.0, brillo))
			if k % 4 == 0:
				draw_line(p, p + radial * 5.0 + Vector2(0, -3), Color(0.75, 0.88, 1.0, 0.9), 1.0)
	# las raíces: primero una grieta violeta gruesa que avisa (late); luego, pinchos de piedra oscura a lo largo
	for rz in _raices:
		var a: Vector2 = rz["desde"] + o
		var b: Vector2 = rz["hacia"] + o
		var largo := a.distance_to(b)
		var dir := (b - a) / maxf(largo, 1.0)
		var lado := dir.orthogonal()
		if not rz["salio"]:
			var aviso := 0.55 + 0.45 * sin(_tiempo * 18.0)
			var avance := clampf(rz["t"] / (AVISO_RAIZ * 0.6), 0.0, 1.0)        # la grieta corre hacia Maisha
			var k := 0.0
			while k < largo * avance:
				var p := a + dir * k + lado * sin(k * 0.35) * 2.0
				draw_rect(Rect2((p - Vector2(1, 1)).floor(), Vector2(3, 3)), Color(0.2, 0.05, 0.3, 0.7 * aviso))
				draw_rect(Rect2(p.floor(), Vector2(2, 1)), Color(0.75, 0.4, 1.0, 0.95 * aviso))
				k += 2.0
		else:
			var vida: float = 1.0 - (rz["t"] - AVISO_RAIZ) / SALE_RAIZ
			var k2 := 6.0
			var sube := clampf((rz["t"] - AVISO_RAIZ) / 0.12, 0.0, 1.0)      # brotan de golpe
			while k2 < largo:
				var p := (a + dir * k2).floor()
				var alto := int((15.0 + 8.0 * absf(sin(k2 * 0.7) * sin(k2 * 0.23))) * sube)
				# un pincho de piedra en píxeles: más ancho abajo, con el canto izquierdo claro y una veta violeta
				for f in alto:
					var ancho := maxi(1, int(round(7.0 * (1.0 - float(f) / alto))))
					var y := p.y - f
					draw_rect(Rect2(p.x - ancho, y, ancho * 2, 1), Color(0.24, 0.25, 0.3, vida))
					draw_rect(Rect2(p.x - ancho, y, 1, 1), Color(0.6, 0.62, 0.68, vida))
					if f % 3 == 1:
						draw_rect(Rect2(p.x, y, 1, 1), Color(0.72, 0.42, 1.0, vida))
				draw_rect(Rect2(p.x - 6, p.y, 12, 1), Color(0.1, 0.08, 0.14, 0.6 * vida))     # la grieta del suelo
				k2 += 11.0
