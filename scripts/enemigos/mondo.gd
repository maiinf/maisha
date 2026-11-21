extends Node2D
## MONDO, EL SERVAL DE MIL REFLEJOS (jefe del Jardín de los Faroles, el Valle del Ocaso; opción A elegida por Iam):
## un serval de bronce con orejas de cristal dorado. Guarda la Pesa del Este en el Invernadero.
##   1. SE DIVIDE: aparecen él y COPIAS (sus reflejos) delante de los espejos altos del Invernadero (`espejos`,
##      ocaso/espejo_alto.gd). Todos son iguales. Cada uno, por turnos, SALTA hacia Maisha, da un ZARPAZO (1 hoja si
##      la alcanza) y salta a otro espejo.
##   2. LA LUZ los delata: un golpe a un espejo alto suelta un rayo que cruza la sala. Una copia que toca el rayo se
##      ESFUMA; el Mondo de verdad brilla y cae ATURDIDO (las copias que queden se esfuman con él).
##   3. ATURDIDO (ATURDIDO s o GOLPES_ATURDIDO golpes): cetro 1, semillas 2. Luego se levanta y se vuelve a dividir.
##      Sin aturdir, el cetro no le da: se aparta de un salto.
##   4. Con la mitad de la vida (FURIA): una copia más, y espera menos delante de los espejos.
##   5. Vencido: la PESA DEL ESTE («peso_este») y un Farol de la Hora.
## Dibujo: arte/mundos/ocaso/jardin/mondo.png (herramientas/pintar_jardin.py). Música: «jefe_mondo».

signal destruido
signal vida_cambiada(nueva: int)

const BARRA := preload("res://scripts/interfaz/barra_jefe.gd")
const DIBUJO := preload("res://arte/mundos/ocaso/jardin/mondo.png")
const RECOGIBLE := preload("res://scripts/mundo/objetos/recogible.gd")
const ASTILLAS := preload("res://scripts/efectos/astillas.gd")
const NOMBRE := "Mondo, el Serval de Mil Reflejos"
const VIDA_MAX := 9
const GOLPES_ATURDIDO := 3
const ATURDIDO := 4.0
const ATURDIDO_FURIA := 3.2
const POSADO := 1.8
const POSADO_FURIA := 1.1
const SALTO := 0.55
const ZARPA := 0.45
const ALCANCE := 26.0

enum Fase { DORMIDO, CAZA, ATURDIDO, VENCIDO }
enum Fig { POSADO, SALTA, ZARPA }

var espejos: Array = []                  # los espejos altos (los pone la escena)
var vida := VIDA_MAX
var fase := Fase.DORMIDO
var _t := 0.0
var _golpes := 0
var _destello := 0.0
var _inmune := 0.0                       # (recién dividido, la luz aún no los delata)
var _figuras: Array = []                 # [{nodo, sprite, real, estado, t, espera, desde, hasta, espejo, a_maisha}]
var _sprite: Sprite2D
var _barra: CanvasLayer = null


func _ready() -> void:
	add_to_group("jefes")
	add_to_group("enemigos")
	add_to_group("golpeables")
	add_to_group("daniables")
	add_to_group("mondo")
	_sprite = _nuevo_sprite(self)


func _nuevo_sprite(padre: Node2D) -> Sprite2D:
	var sombra := Node2D.new()
	sombra.set_script(preload("res://scripts/personajes/sombra.gd"))
	sombra.set("ancho", 22.0)
	padre.add_child(sombra)
	var s := Sprite2D.new()
	s.texture = DIBUJO
	s.hframes = 6
	s.offset = Vector2(0, -22)
	padre.add_child(s)
	return s


func furia() -> bool:
	return vida <= VIDA_MAX / 2


func despertar() -> void:
	if fase != Fase.DORMIDO:
		return
	Sonido.musica("jefe_mondo" if ResourceLoader.exists("res://audio/musica/jefe_mondo.ogg") else "jefe_kivuli")
	_barra = BARRA.new()
	_barra.nombre = NOMBRE
	_barra.maximo = VIDA_MAX
	add_child(_barra)
	vida_cambiada.connect(_barra.poner)
	_dividirse()


func _sitio(i: int) -> Vector2:
	return (espejos[i] as Node2D).global_position + Vector2(0, 18)


## Él y sus copias, cada uno delante de un espejo distinto
func _dividirse() -> void:
	_quitar_copias()
	fase = Fase.CAZA
	var orden := range(espejos.size())
	orden.shuffle()
	var n := mini(espejos.size(), 4 if furia() else 3)
	for k in n:
		var real := k == 0
		var nodo: Node2D = self
		var sprite := _sprite
		if not real:
			nodo = Node2D.new()
			nodo.name = "ReflejoMondo"
			nodo.add_to_group("reflejos_mondo")
			get_parent().add_child(nodo)
			sprite = _nuevo_sprite(nodo)
			nodo.global_position = _sitio(orden[k])
			Impacto.chispa(nodo.global_position + Vector2(0, -20), Vector2.UP, Color(1.0, 0.85, 0.5))
		_figuras.append({"nodo": nodo, "sprite": sprite, "real": real, "estado": Fig.SALTA if real else Fig.POSADO,
			"t": 0.0, "espera": (POSADO_FURIA if furia() else POSADO) + k * 0.8, "desde": nodo.global_position,
			"hasta": _sitio(orden[k]), "espejo": orden[k], "a_maisha": false})
	_inmune = 1.2
	Sonido.efecto("mondo_divide", 0.0, global_position)


func _quitar_copias() -> void:
	for f in _figuras:
		if not f["real"] and is_instance_valid(f["nodo"]):
			_esfumar(f)
	_figuras.clear()


func _esfumar(f: Dictionary) -> void:
	var nodo: Node2D = f["nodo"]
	if not is_instance_valid(nodo) or nodo.is_queued_for_deletion():
		return
	nodo.remove_from_group("reflejos_mondo")
	Impacto.chispa(nodo.global_position + Vector2(0, -20), Vector2.UP, Color(1.0, 0.95, 0.8))
	Sonido.efecto("mondo_esfuma", -1.0, nodo.global_position, 0.12)
	var t := nodo.create_tween()
	t.tween_property(nodo, "modulate:a", 0.0, 0.3)
	t.tween_callback(nodo.queue_free)


func _process(delta: float) -> void:
	_destello = maxf(0.0, _destello - delta)
	match fase:
		Fase.CAZA:
			_cazar(delta)
		Fase.ATURDIDO:
			_t += delta
			_sprite.frame = 4 if _destello > 0.0 else 3
			_sprite.position = Vector2(roundf(sin(_t * 30.0) * 0.5), 0)
			if _t >= (ATURDIDO_FURIA if furia() else ATURDIDO):
				_dividirse()
		Fase.VENCIDO:
			_sprite.frame = 5
			_sprite.position = Vector2.ZERO


func _cazar(delta: float) -> void:
	_inmune = maxf(0.0, _inmune - delta)
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	for f in _figuras.duplicate():
		var nodo: Node2D = f["nodo"]
		if not is_instance_valid(nodo):
			_figuras.erase(f)
			continue
		var sprite: Sprite2D = f["sprite"]
		f["t"] += delta
		match f["estado"]:
			Fig.POSADO:
				sprite.frame = 0
				sprite.position = Vector2.ZERO
				if maisha:
					sprite.flip_h = maisha.global_position.x < nodo.global_position.x
				if f["t"] >= f["espera"] and maisha and not maisha.get("esta_caida"):
					_saltar(f, maisha.global_position, true)
			Fig.SALTA:
				var k := minf(1.0, f["t"] / SALTO)
				nodo.global_position = (f["desde"] as Vector2).lerp(f["hasta"], k)
				sprite.frame = 1
				sprite.position = Vector2(0, -roundf(sin(k * PI) * 18.0))
				if k >= 1.0:
					f["t"] = 0.0
					if f["a_maisha"]:
						f["estado"] = Fig.ZARPA
						Sonido.efecto("mondo_zarpa", -1.0, nodo.global_position, 0.1)
						if maisha and maisha.global_position.distance_to(nodo.global_position) < ALCANCE:
							maisha.call("recibir_danio", 1, nodo.global_position, "contacto")
					else:
						f["estado"] = Fig.POSADO
						f["espera"] = (POSADO_FURIA if furia() else POSADO) + randf() * 1.2
			Fig.ZARPA:
				sprite.frame = 2
				sprite.position = Vector2.ZERO
				if f["t"] >= ZARPA:
					f["espejo"] = _espejo_libre(f)
					_saltar(f, _sitio(f["espejo"]), false)
		# ¿le da la luz de un espejo?
		for e in (espejos if _inmune <= 0.0 else []):
			if e.toca(nodo.global_position):
				if f["real"]:
					_aturdir()
					return
				_esfumar(f)
				_figuras.erase(f)
				break


func _saltar(f: Dictionary, hacia: Vector2, a_maisha: bool) -> void:
	f["estado"] = Fig.SALTA
	f["t"] = 0.0
	f["desde"] = (f["nodo"] as Node2D).global_position
	f["hasta"] = hacia
	f["a_maisha"] = a_maisha
	(f["sprite"] as Sprite2D).flip_h = hacia.x < f["desde"].x
	Sonido.efecto("mondo_salta", -2.0, f["desde"], 0.12)


## Un espejo al que no vaya ni esté ningún otro
func _espejo_libre(f: Dictionary) -> int:
	var libres: Array = []
	for i in espejos.size():
		var ocupado := false
		for o in _figuras:
			if o != f and o["espejo"] == i:
				ocupado = true
		if not ocupado:
			libres.append(i)
	return libres.pick_random() if not libres.is_empty() else randi() % espejos.size()


func _aturdir() -> void:
	_quitar_copias()
	fase = Fase.ATURDIDO
	_t = 0.0
	_golpes = 0
	_sprite.position = Vector2.ZERO
	Sonido.efecto("mondo_aturdido", 0.0, global_position)
	Impacto.temblar(2.5, 0.3)
	Impacto.chispa(global_position + Vector2(0, -24), Vector2.UP, Color(1.0, 0.9, 0.55))


func expuesto() -> bool:
	return fase == Fase.ATURDIDO


func recibir_golpe(danio: int, _direccion: Vector2) -> bool:
	if not expuesto():
		if fase == Fase.CAZA:
			Sonido.efecto("clinc", -2.0, global_position, 0.2)
		return false
	recibir_danio(danio, global_position, "golpe")
	return true


func recibir_danio(cantidad: int, _desde: Vector2, tipo: String) -> void:
	if not expuesto():
		return
	vida = maxi(0, vida - (2 if tipo == "explosion" else cantidad))
	_destello = 0.12
	vida_cambiada.emit(vida)
	Impacto.chispa(global_position + Vector2(0, -16), Vector2.UP, Color("ffd878"))
	if vida <= 0:
		morir()
		return
	_golpes += 1
	if _golpes >= GOLPES_ATURDIDO:
		_dividirse()


func morir() -> void:
	if fase == Fase.VENCIDO:
		return
	_quitar_copias()
	fase = Fase.VENCIDO
	for g in ["golpeables", "daniables", "enemigos", "mondo"]:
		remove_from_group(g)
	Estado.marcar("mondo_vencido")
	Estado.marcar("peso_este")
	Bestiario.vencido("mondo", self)
	Sonido.efecto("mondo_muere", 0.0, global_position)
	Sonido.musica("victoria")
	Impacto.temblar(5.0, 0.7)
	if _barra:
		_barra.queue_free()
		_barra = null
	var astillas: Node2D = ASTILLAS.new()
	astillas.cantidad = 16
	astillas.position = global_position + Vector2(0, -16)
	get_parent().add_child(astillas)
	var farol: Node2D = RECOGIBLE.new()
	farol.objeto = "farol_hora"
	farol.marca = "farol/jardin_3"
	farol.dibujo = "res://arte/mundos/ocaso/mirador/farol.png"
	farol.color_halo = Color(1.0, 0.75, 0.35)
	farol.position = global_position + Vector2(0, 30)
	get_parent().add_child(farol)
	destruido.emit()
