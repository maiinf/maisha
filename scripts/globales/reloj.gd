extends Node
## RELOJ (autoload «Reloj»): la hora del día en los exteriores de Raíz. Solo cambia cómo se ve el mundo
## (la luz, los faroles, las ventanas); no cambia nada del juego.
##
## Un día entero dura DURACION segundos de juego. La hora va de 0 a 1:
##   0,08 de día · 0,62 atardece · 0,72 de noche · 0,94 amanece (el alba cruza el 0 y acaba en 0,08)
## El reloj no corre hasta que Maisha llega por primera vez a Cuna de Musgo (el Kitovu del principio es de día),
## ni con el juego en pausa o fuera de una partida. La hora se guarda con la partida (Estado.extra["hora"]).
##
##   Reloj.luz_dia()     1 = pleno día, 0 = noche cerrada (con atardecer y amanecer en medio)
##   Reloj.oscuridad     lo oscura que está la escena ahora mismo (la pone relieve.gd: en una cueva vale 1)

const DURACION := 16.0 * 60.0          # un día: 16 minutos
const DIA := 0.08
const ATARDECER := 0.62
const NOCHE := 0.72
const AMANECER_OTRA := 0.94
const EMPIEZA := 0.12                  # la hora de una partida nueva (por la mañana)
const MARCA_INICIO := "visto/cuna_de_musgo"

var oscuridad := 0.0

## La luz del sol ha cambiado un poco (o ha pasado de día a noche): las sombras (sombra.gd) se miran entonces,
## en vez de mirar el reloj cada una en cada fotograma (hay mapas con casi 2000)
signal luz_cambiada
const PASO_LUZ := 0.01                 # cuánto tiene que cambiar luz_dia() o calidez() para avisar
var _ultima_luz := Vector2(-1.0, -1.0)


func _process(delta: float) -> void:
	_avisar_luz()
	if not Estado.jugando or get_tree().paused or not Estado.tiene(MARCA_INICIO):
		return
	Estado.extra["hora"] = fposmod(hora() + delta / DURACION, 1.0)


func _avisar_luz() -> void:
	var luz := Vector2(luz_dia(), calidez())
	var cruza := (luz.x > 0.25) != (_ultima_luz.x > 0.25)
	if cruza or absf(luz.x - _ultima_luz.x) > PASO_LUZ or absf(luz.y - _ultima_luz.y) > PASO_LUZ:
		_ultima_luz = luz
		luz_cambiada.emit()


func hora() -> float:
	return float(Estado.extra.get("hora", EMPIEZA))


## Pone la hora a mano (pruebas y capturas)
func poner_hora(h: float) -> void:
	Estado.extra["hora"] = fposmod(h, 1.0)


## 1 = pleno día, 0 = noche cerrada
func luz_dia() -> float:
	if not Estado.tiene(MARCA_INICIO):
		return 1.0
	var h := hora()
	var alba := _avance_alba(h)
	if alba >= 0.0:
		return smoothstep(0.0, 1.0, alba)
	if h < ATARDECER:
		return 1.0
	if h < NOCHE:
		return 1.0 - smoothstep(ATARDECER, NOCHE, h)
	return 0.0


## Lo anaranjado de la luz: sube y baja dentro del atardecer y del amanecer (0 fuera de ellos)
func calidez() -> float:
	if not Estado.tiene(MARCA_INICIO):
		return 0.0
	var h := hora()
	var alba := _avance_alba(h)
	if alba >= 0.0:
		return sin(alba * PI) * 0.8
	if h >= ATARDECER and h < NOCHE:
		return sin((h - ATARDECER) / (NOCHE - ATARDECER) * PI)
	return 0.0


## Cuánto ha avanzado el amanecer (de 0 a 1), que cruza la medianoche del reloj (0,94 → 1 → 0,08); -1 si no es el alba
func _avance_alba(h: float) -> float:
	var largo := (1.0 - AMANECER_OTRA) + DIA
	if h >= AMANECER_OTRA:
		return (h - AMANECER_OTRA) / largo
	if h < DIA:
		return (h + 1.0 - AMANECER_OTRA) / largo
	return -1.0


## El nombre de la hora (para el diario o los diálogos, si hace falta)
func momento() -> String:
	var h := hora()
	if h < DIA or h >= AMANECER_OTRA:
		return "amanecer"
	if h < ATARDECER:
		return "dia"
	if h < NOCHE:
		return "atardecer"
	return "noche"
