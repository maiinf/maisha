extends Node
## TIENDA (autoload «Tienda»): los CRISTALES DEL NEXO y lo que vende Tawi en su puesto.
##   - Los Cristales se ganan al cumplir misiones (según su tipo) y con algunas marcas (jefes, secretos).
##     No se guardan aparte: se cuentan a partir de las misiones cumplidas y las marcas. Lo gastado, sí.
##   - Lo que vende Tawi está en datos/tienda.json (prendas, ingredientes, el mapa de los secretos,
##     la semilla del olvido...). Lo comprado se guarda en Estado.extra["comprado"].
##   - Las prendas compradas se ponen y se quitan desde la mochila (Estado.extra["ropa"]).
##
##   Tienda.cristales()          los que hay para gastar
##   Tienda.disponibles()        lo que sale ahora en la tienda
##   Tienda.precio(articulo)     su precio (la semilla del olvido sube cada vez)
##   Tienda.comprar(id)          "ok", "caro", "agotado" o "no_hay"

signal cristales_ganados(cantidad: int, motivo: String)
signal comprado(id: String)

const ARCHIVO := "res://datos/tienda.json"

var articulos: Array = []
var _por_tipo: Dictionary = {}
var _reglas: Array = []


func _ready() -> void:
	var datos: Dictionary = (load(ARCHIVO) as JSON).data
	articulos = datos.get("articulos", [])
	_por_tipo = datos.get("cristales_por_tipo", {})
	_reglas = datos.get("cristales_por_marca", [])
	Estado.marca_puesta.connect(_al_poner_marca)
	Misiones.mision_cumplida.connect(_al_cumplir_mision)


func _regla_de(marca: String) -> Dictionary:
	for regla in _reglas:
		if marca.begins_with(String(regla["prefijo"])):
			return regla
	return {}


func _al_poner_marca(marca: String) -> void:
	var regla := _regla_de(marca)
	if not regla.is_empty():
		cristales_ganados.emit(int(regla["cristales"]), String(regla.get("motivo", "")))


func _al_cumplir_mision(m: Dictionary) -> void:
	var n := cristales_de_mision(m)
	if n > 0:
		cristales_ganados.emit(n, String(m["titulo"]))


func cristales_de_mision(m: Dictionary) -> int:
	return int(m.get("cristales", _por_tipo.get(String(m.get("tipo", "encargo")), 0)))


# --- Cristales ----------------------------------------------------------------------

func cristales_ganados_total() -> int:
	var total := 0
	for m in Misiones.hechas():
		total += cristales_de_mision(m)
	for marca in Estado.marcas:
		var regla := _regla_de(String(marca))
		if not regla.is_empty():
			total += int(regla["cristales"])
	return total


func cristales_gastados() -> int:
	return int(Estado.extra.get("cristales_gastados", 0))


func cristales() -> int:
	# (también los que se han gastado en los nodos grandes del árbol de habilidades)
	return maxi(0, cristales_ganados_total() - cristales_gastados() - Artes.cristales_gastados())


# --- Artículos ----------------------------------------------------------------------

func buscar(id: String) -> Dictionary:
	for a in articulos:
		if a["id"] == id:
			return a
	return {}


func veces_comprado(id: String) -> int:
	return int(Estado.extra.get("comprado", {}).get(id, 0))


func tiene(id: String) -> bool:
	return veces_comprado(id) > 0


func precio(articulo: Dictionary) -> int:
	var p := int(articulo["precio"])
	if articulo.get("tipo", "") == "olvido":
		p += int(articulo.get("sube", 0)) * veces_comprado(String(articulo["id"]))
	return p


func agotado(articulo: Dictionary) -> bool:
	return not articulo.get("repetible", false) and tiene(String(articulo["id"]))


## Lo que sale en la tienda ahora (lo que pide una marca que aún no se tiene no sale)
func disponibles() -> Array:
	return articulos.filter(func(a: Dictionary) -> bool:
		var req := String(a.get("requiere", ""))
		return req == "" or Estado.tiene(req))


func comprar(id: String) -> String:
	var a := buscar(id)
	if a.is_empty():
		return "no_hay"
	if agotado(a):
		return "agotado"
	var p := precio(a)
	if cristales() < p:
		return "caro"
	if a.get("tipo", "") == "olvido" and Artes.esencia_gastada() == 0:
		return "nada_que_olvidar"
	Estado.extra["cristales_gastados"] = cristales_gastados() + p
	var hechas: Dictionary = Estado.extra.get("comprado", {}).duplicate()
	hechas[id] = veces_comprado(id) + 1
	Estado.extra["comprado"] = hechas
	match String(a.get("tipo", "")):
		"objeto":
			var da: Dictionary = a.get("da", {})
			for o in da:
				Estado.dar(String(o), int(da[o]))
		"marca":
			Estado.marcar(String(a["marca"]))
		"olvido":
			Artes.olvidar()
		"prenda":
			poner_prenda(id, true)
	comprado.emit(id)
	Estado.guardar_pronto()
	return "ok"


# --- Ropa ---------------------------------------------------------------------------

func prendas_compradas() -> Array:
	return articulos.filter(func(a: Dictionary) -> bool: return a.get("tipo", "") == "prenda" and tiene(String(a["id"])))


func lleva(id: String) -> bool:
	return id in Estado.extra.get("ropa", [])


## Se pone (o se quita) una prenda comprada; si hay otra en su zona, la sustituye
func poner_prenda(id: String, puesta: bool) -> void:
	var ropa: Array = Estado.extra.get("ropa", []).duplicate()
	ropa.erase(id)
	if puesta:
		var zona := zona_de(id)
		ropa = ropa.filter(func(otra: String) -> bool: return zona_de(otra) != zona)
		ropa.append(id)
	Estado.extra["ropa"] = ropa
	var maisha := get_tree().get_first_node_in_group("maisha")
	if maisha and maisha.has_node("Ropa"):
		vestir(maisha.get_node("Ropa"))
	Estado.guardar_pronto()


var _prendas: Dictionary = {}


func zona_de(id: String) -> String:
	if _prendas.is_empty():
		_prendas = (load("res://datos/prendas.json") as JSON).data
	return String(_prendas.get(id, {}).get("zona", id))


## Viste a Maisha con lo que lleva puesto (se llama al empezar cada escena)
func vestir(ropa: Node) -> void:
	for a in prendas_compradas():
		var id := String(a["id"])
		if lleva(id):
			ropa.call("poner", id)
		elif ropa.call("lleva", id):
			ropa.call("quitar_zona", zona_de(id))
