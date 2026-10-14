extends Node2D
## NUNGU EN LA PELEA CONTRA KUVU: el erizo científico. Lo crea y lo maneja kuvu.gd.
##   - CONTROLADO: un hilo de esporas le sale de la cabeza y llega al sombrero de Kuvu. Anda como una marioneta hacia
##     Maisha, se hace BOLA DE PÚAS (aviso: se encoge) y RUEDA hacia ella. Si Maisha lo para con el ESCUDO de frente,
##     rebota y se MAREA: entonces un golpe de cetro le CORTA EL HILO (libre). Sin marear, el cetro rebota en sus púas.
##   - LIBRE: se pone del lado de Maisha y cada poco embiste rodando el pie de Kuvu, que levanta el sombrero (abrir()).
##   - Kuvu puede volver a atraparlo (atrapar()): vuelve a CONTROLADO.
## Dibujo: arte/zonas/raiz/nungu.png (10 fotogramas, ver herramientas/dibujar_kuvu.py).

enum Fase { CONTROLADO, ENCOGE, RUEDA, MAREADO, LIBRE, AYUDA, QUIETO }

const R := preload("res://scripts/combate/reglas_combate.gd")
const SOMBRA := preload("res://scripts/personajes/sombra.gd")
const OSCURIDAD := preload("res://scripts/mundo/gruta/oscuridad.gd")
const DIBUJO := preload("res://arte/zonas/raiz/nungu.png")

var kuvu: Node2D
var fase: int = Fase.CONTROLADO
var _t := 0.0
var _tiempo := 0.0
var _hacia := Vector2.RIGHT
var _pillo := false
var _sprite: Sprite2D
var _luz: PointLight2D


func _ready() -> void:
	add_to_group("golpeables")
	add_to_group("nungu")
	var sombra := Node2D.new()
	sombra.set_script(SOMBRA)
	sombra.set("ancho", 10.0)
	add_child(sombra)
	_sprite = Sprite2D.new()
	_sprite.texture = DIBUJO
	_sprite.hframes = 10
	_sprite.offset = Vector2(0, -17)
	add_child(_sprite)
	_luz = PointLight2D.new()
	_luz.texture = OSCURIDAD.textura_luz(128)
	_luz.texture_scale = 0.5
	_luz.color = Color(0.75, 0.5, 1.0)
	_luz.energy = 0.6
	_luz.position = Vector2(0, -14)
	add_child(_luz)


func controlado() -> bool:
	return fase in [Fase.CONTROLADO, Fase.ENCOGE, Fase.RUEDA, Fase.MAREADO]


func _maisha() -> Node2D:
	return get_tree().get_first_node_in_group("maisha") as Node2D


func _cambiar(nueva: int) -> void:
	fase = nueva
	_t = 0.0


func _process(delta: float) -> void:
	_tiempo += delta
	_t += delta
	var maisha := _maisha()
	match fase:
		Fase.CONTROLADO:
			if maisha:
				var hacia := (maisha.global_position - global_position)
				if hacia.length() > 40.0:
					global_position += hacia.normalized() * 22.0 * delta
				_sprite.flip_h = hacia.x < 0.0
			if _t >= R.NUNGU_RUEDA_CADA:
				_cambiar(Fase.ENCOGE)
				Sonido.efecto("mende_corre", 0.0, global_position)
		Fase.ENCOGE:
			if maisha and _t < 0.35:
				_hacia = (maisha.global_position - global_position).normalized()
			if _t >= 0.55:
				_pillo = false
				_cambiar(Fase.RUEDA)
				Sonido.efecto("guardian_carga", -6.0, global_position)
		Fase.RUEDA, Fase.AYUDA:
			global_position += _hacia * R.NUNGU_RUEDA * delta
			if fase == Fase.RUEDA:
				_rodar_contra_maisha(maisha)
			elif kuvu and global_position.distance_to(kuvu.global_position + Vector2(0, -8)) < 22.0:
				# ¡choca con el pie de Kuvu!
				kuvu.call("abrir")
				global_position -= _hacia * 10.0
				_cambiar(Fase.LIBRE)
			if fase in [Fase.RUEDA, Fase.AYUDA] and (_t > 1.4 or _fuera()):
				_cambiar(Fase.CONTROLADO if fase == Fase.RUEDA else Fase.LIBRE)
		Fase.MAREADO:
			if _t >= R.NUNGU_MAREADO:
				_cambiar(Fase.CONTROLADO)
		Fase.LIBRE:
			# se queda cerca de Maisha, un poco detrás
			if maisha:
				var sitio := maisha.global_position + Vector2(-30 if maisha.global_position.x > global_position.x else 30, 10)
				if global_position.distance_to(sitio) > 12.0:
					global_position += (sitio - global_position).normalized() * 50.0 * delta
			if kuvu and _t >= R.NUNGU_AYUDA_CADA and kuvu.call("puede_abrirse"):
				_hacia = (kuvu.global_position + Vector2(0, -8) - global_position).normalized()
				_cambiar(Fase.AYUDA)
				Sonido.efecto("guardian_carga", -6.0, global_position)
	if kuvu and kuvu.get("zona"):
		global_position = kuvu.zona.limitar(global_position)
	_animar()


func _fuera() -> bool:
	return kuvu != null and kuvu.get("zona") != null and kuvu.zona.distancia_normal(global_position + _hacia * 12.0) > 0.9


func _rodar_contra_maisha(maisha: Node2D) -> void:
	if maisha == null or _pillo or maisha.global_position.distance_to(global_position) > 16.0:
		return
	_pillo = true
	if maisha.call("recibir_danio", 1, global_position, "contacto"):
		return
	if maisha.get("escudo"):
		# ¡el escudo lo para! rebota y se marea: ahora se le puede cortar el hilo
		global_position -= _hacia * 18.0
		_cambiar(Fase.MAREADO)
		Sonido.efecto("clinc", 0.0, global_position)
		Impacto.temblar(2.0, 0.2)


func _animar() -> void:
	var paso := int(_tiempo * 4.0) % 2
	match fase:
		Fase.CONTROLADO:
			_sprite.frame = paso
		Fase.ENCOGE:
			_sprite.frame = 2
			_sprite.position.x = sin(_tiempo * 40.0)
		Fase.RUEDA:
			_sprite.frame = 2 + int(_tiempo * 12.0) % 2
		Fase.MAREADO:
			_sprite.frame = 4
		Fase.LIBRE, Fase.QUIETO:
			_sprite.frame = 5 + paso
		Fase.AYUDA:
			_sprite.frame = 7 + int(_tiempo * 12.0) % 2
	if fase != Fase.ENCOGE:
		_sprite.position.x = 0.0
	_luz.color = Color(0.75, 0.5, 1.0) if controlado() else Color(1.0, 0.9, 0.7)


## El cetro: solo le corta el hilo si está mareado (y controlado); si no, rebota en las púas
func recibir_golpe(_danio: int, _direccion: Vector2) -> bool:
	if fase == Fase.MAREADO:
		liberar()
		return true
	Sonido.efecto("clinc", 0.0, global_position)
	return false


func liberar() -> void:
	_cambiar(Fase.LIBRE)
	remove_from_group("golpeables")
	Sonido.efecto("orbe_rebota", 0.0, global_position)
	Impacto.fogonazo(Color("f0d8ff"), 0.2, 0.3)
	if kuvu:
		kuvu.call("nungu_libre")


func atrapar() -> void:
	_cambiar(Fase.CONTROLADO)
	add_to_group("golpeables")
	Sonido.efecto("bundi_conjura", 0.0, global_position)


## Punto de la cabeza (donde se ata el hilo)
func cabeza() -> Vector2:
	return global_position + Vector2(0, -28)


## Al acabar la pelea: se queda quieto, libre
func calmar() -> void:
	_cambiar(Fase.QUIETO)
	remove_from_group("golpeables")


## Lo que dice al acabar la pelea (si se le habla)
var radio_interaccion := 26.0
var altura_bocadillo := 36.0


func interactuar() -> void:
	if fase == Fase.QUIETO:
		await load("res://scripts/mundo/charla.gd").hablar(self, "nungu_libre")
