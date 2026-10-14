extends Node
## ARTES (autoload «Artes»): el Árbol de la Vida de Maisha.
##   - La ESENCIA se gana sola: al purgar zonas, vencer a Mzizi, encontrar secretos y ver crecer la aldea
##     (las reglas están en datos/artes.json). No se guarda aparte: se cuenta a partir de las marcas.
##   - Se gasta MEDITANDO en un Claro de Calma, para subir de nivel las Artes (Raíz, Aliento...).
##     Los niveles sí se guardan con la partida (Estado.extra["artes"]).
##   - Cada nivel cambia números del combate y algunos dan a Maisha un rasgo visual (un brote, un aura...).
##
##   Artes.esencia()            la que hay para gastar
##   Artes.nivel("raiz")        el nivel de un Arte
##   Artes.subir("raiz")        sube un nivel si hay Esencia (true si ha subido)
##   Artes.valor("semilla_coste")   suma de ese efecto en los niveles conseguidos
##   Artes.semilla_coste() ...  los números del combate ya con las Artes aplicadas
##   Artes.aspecto()            lo que se le VE a Maisha con sus niveles (o con otros: la vista previa del diario)

signal esencia_ganada(cantidad: int, motivo: String)
signal arte_subida(id: String, nivel: int)

const R := preload("res://scripts/combate/reglas_combate.gd")
const ARCHIVO := "res://datos/artes.json"

var lista: Array = []
var _reglas: Array = []


func _ready() -> void:
	var datos: Dictionary = (load(ARCHIVO) as JSON).data
	lista = datos.get("artes", [])
	_reglas = datos.get("esencia_por_marca", [])
	Estado.marca_puesta.connect(_al_poner_marca)


func _al_poner_marca(marca: String) -> void:
	var regla := _regla_de(marca)
	if not regla.is_empty():
		esencia_ganada.emit(int(regla["esencia"]), String(regla.get("motivo", "")))


func _regla_de(marca: String) -> Dictionary:
	for regla in _reglas:
		if marca.begins_with(String(regla["prefijo"])):
			return regla
	return {}


# --- Esencia -----------------------------------------------------------------------

## Toda la Esencia conseguida en la partida (a partir de las marcas)
func esencia_ganada_total() -> int:
	var total := 0
	for marca in Estado.marcas:
		var regla := _regla_de(String(marca))
		if not regla.is_empty():
			total += int(regla["esencia"])
	return total


## La que ya se ha gastado en niveles (subir al nivel N cuesta N)
func esencia_gastada() -> int:
	var total := 0
	for arte in lista:
		var n := nivel(String(arte["id"]))
		total += n * (n + 1) / 2
	return total


func esencia() -> int:
	return maxi(0, esencia_ganada_total() - esencia_gastada())


# --- Niveles -----------------------------------------------------------------------

func buscar(id: String) -> Dictionary:
	for arte in lista:
		if arte["id"] == id:
			return arte
	return {}


func nivel(id: String) -> int:
	var niveles: Dictionary = Estado.extra.get("artes", {})
	return int(niveles.get(id, 0))


func nivel_maximo(id: String) -> int:
	return buscar(id).get("niveles", []).size()


func coste_siguiente(id: String) -> int:
	return nivel(id) + 1


## Los nodos grandes (los niveles 3 y 6) cuestan también Cristales del Nexo
func cristales_siguiente(id: String) -> int:
	var niveles: Array = buscar(id).get("niveles", [])
	var n := nivel(id)
	return int(niveles[n].get("cristales", 0)) if n < niveles.size() else 0


func es_grande(id: String, nivel_n: int) -> bool:
	var niveles: Array = buscar(id).get("niveles", [])
	return nivel_n >= 1 and nivel_n <= niveles.size() and bool(niveles[nivel_n - 1].get("grande", false))


## Los Cristales gastados en los nodos grandes (se cuentan a partir de los niveles, como la Esencia)
func cristales_gastados() -> int:
	var total := 0
	for arte in lista:
		var niveles: Array = arte.get("niveles", [])
		for i in mini(nivel(String(arte["id"])), niveles.size()):
			total += int(niveles[i].get("cristales", 0))
	return total


func puede_subir(id: String) -> bool:
	var arte := buscar(id)
	if arte.is_empty() or arte.has("bloqueada"):
		return false
	return nivel(id) < nivel_maximo(id) and esencia() >= coste_siguiente(id) \
			and Tienda.cristales() >= cristales_siguiente(id)


func subir(id: String) -> bool:
	if not puede_subir(id):
		return false
	var niveles: Dictionary = Estado.extra.get("artes", {}).duplicate()
	niveles[id] = nivel(id) + 1
	Estado.extra["artes"] = niveles
	arte_subida.emit(id, int(niveles[id]))
	Estado.guardar_pronto()
	return true


## La semilla del olvido (tienda de Tawi): se olvidan todos los niveles y vuelve toda la Esencia
func olvidar() -> void:
	Estado.extra["artes"] = {}
	arte_subida.emit("", 0)
	Estado.guardar_pronto()


## Suma de un efecto en todos los niveles conseguidos
func valor(efecto: String) -> float:
	var total := 0.0
	for arte in lista:
		var niveles: Array = arte.get("niveles", [])
		for i in mini(nivel(String(arte["id"])), niveles.size()):
			total += float(niveles[i].get("efectos", {}).get(efecto, 0.0))
	return total


## Los rasgos visuales conseguidos («brote», «aura», «flores», «brisa»...)
func rasgos() -> Array:
	var salida := []
	for arte in lista:
		var niveles: Array = arte.get("niveles", [])
		for i in mini(nivel(String(arte["id"])), niveles.size()):
			if niveles[i].has("rasgo"):
				salida.append(String(niveles[i]["rasgo"]))
	return salida


func tiene_rasgo(rasgo: String) -> bool:
	return rasgo in rasgos()


# --- Lo que se le ve a Maisha ----------------------------------------------------------

## Lo que cambia por fuera cada nivel de cada rama (para la vista previa del diario)
const CAMBIO_VISIBLE := {
	"raiz": ["Brazaletes de raíz", "A los brazaletes les brota una hoja", "Una hoja nueva con capullo",
		"Corona de hojas", "Capa de musgo", "Flores por todo el cuerpo"],
	"cetro": ["Una cinta verde en el cetro", "Una gema más grande", "Cetro de corteza de roble",
		"Hojas de cobre", "Gema dorada con chispas", "El Cetro del Primer Árbol"],
	"aliento": ["Bufanda de brisa", "La bufanda se alarga y vuela", "Un aura de luz",
		"Motas de luz alrededor", "Destellos en el aura", "Cuerpo de brisa"],
}


## Lo que se le ve a Maisha con unos niveles (los que falten, los suyos):
##   "prendas": ropa por capas que dan las Artes (brazaletes, corona, capa, bufanda)
##   "cetro":   el dibujo del cetro que lleva en la mano
##   "rasgos":  lo que pinta rasgos_maisha.gd (brote, flores, aura, motas, brillo, brisa)
func aspecto(niveles: Dictionary = {}) -> Dictionary:
	var r := int(niveles.get("raiz", nivel("raiz")))
	var c := int(niveles.get("cetro", nivel("cetro")))
	var a := int(niveles.get("aliento", nivel("aliento")))
	var prendas := []
	if r >= 2:
		prendas.append("brazaletes_hoja")
	elif r >= 1:
		prendas.append("brazaletes_raiz")
	if r >= 4:
		prendas.append("corona_hojas")
	if r >= 5:
		prendas.append("capa_musgo")
	if a >= 2:
		prendas.append("bufanda_viento")
	elif a >= 1:
		prendas.append("bufanda_brisa")
	var visibles := []
	for d in [["brote", r >= 3], ["flores", r >= 6], ["aura", a >= 3], ["motas", a >= 4], ["brillo", a >= 5], ["brisa", a >= 6]]:
		if d[1]:
			visibles.append(d[0])
	return {"prendas": prendas, "cetro": "cetro_%d" % c if c >= 1 else "cetro_raiz", "rasgos": visibles}


# --- Los números del combate, con las Artes ------------------------------------------

func vida_maxima() -> int:
	return R.VIDA_MAXIMA + int(valor("vida_maxima"))


func aliento_maximo() -> float:
	return R.ALIENTO_MAXIMO + valor("aliento_maximo")


func ritmo_aliento() -> float:
	return 1.0 + valor("ritmo_aliento")


func semilla_coste() -> float:
	return R.SEMILLA_COSTE - valor("semilla_coste")


func semilla_alcance() -> int:
	return R.SEMILLA_ALCANCE + int(valor("semilla_alcance"))


func semilla_raices() -> float:
	return R.SEMILLA_RAICES + valor("semilla_raices")


func semilla_mecha() -> float:
	return R.SEMILLA_MECHA - valor("semilla_mecha")


func latido_coste() -> float:
	return R.LATIDO_COSTE - valor("latido_coste")


func latido_radio() -> float:
	return R.LATIDO_RADIO + valor("latido_radio")


func golpe_recarga() -> float:
	return R.GOLPE_RECARGA_ALIENTO + valor("golpe_recarga")


func golpe_alcance() -> float:
	return R.GOLPE_ALCANCE + valor("golpe_alcance")


func golpe_angulo() -> float:
	return R.GOLPE_ANGULO + valor("golpe_angulo")


func golpe_danio() -> int:
	return R.GOLPE_DANIO + int(valor("golpe_danio"))


func golpe_espera() -> float:
	return R.GOLPE_ESPERA - valor("golpe_espera")
