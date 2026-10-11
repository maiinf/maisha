extends Node
## MISIONES (autoload «Misiones»): el diario de Maisha.
## Las misiones están en datos/misiones.json y se leen solas a partir de las marcas de la partida:
## no guardan nada propio salvo cuál se está siguiendo (Estado.extra["mision_seguida"]).
##
##   Misiones.activas()             las que están en marcha (las de historia primero)
##   Misiones.seguida()             la que se ve en pantalla ({} si ninguna)
##   Misiones.seguir("granja")      cambia la que se sigue
##   Misiones.paso_actual(m)        el objetivo de ahora: {texto, ir, indice} ({} si está cumplida)
##   Misiones.objetivo_aqui(nodo)   adónde apunta la flecha en la escena actual (null si a ningún sitio)
##
## Avisa con señales cuando sale una misión nueva, se cumple un paso o se cumple una misión.

signal mision_nueva(m: Dictionary)
signal paso_cumplido(m: Dictionary)
signal mision_cumplida(m: Dictionary)
signal cambiada            # cualquier cambio (para redibujar)

const ARCHIVO := "res://datos/misiones.json"
const TIPOS := {"historia": "Historia", "encargo": "Encargo", "secreto": "Secreto", "lazo": "Lazo"}

const AJUSTES := "user://ajustes.cfg"

var lista: Array = []
## Si se ve el objetivo arriba a la derecha (se cambia en la pausa y se guarda en los ajustes)
var ver_objetivo := true
var caminos: Dictionary = {}
## Para saber qué ha cambiado: id -> {estado, paso}
var _antes := {}
var _revisar := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var datos: Dictionary = (load(ARCHIVO) as JSON).data
	lista = datos.get("misiones", [])
	caminos = datos.get("caminos", {})
	Estado.marca_puesta.connect(func(_m: String) -> void: _revisar = true)
	Estado.objetos_cambiados.connect(func() -> void: _revisar = true)
	Estado.partida_cambiada.connect(_tomar_foto)
	var cfg := ConfigFile.new()
	if cfg.load(AJUSTES) == OK:
		ver_objetivo = bool(cfg.get_value("juego", "objetivo", true))
	_tomar_foto()


func poner_ver_objetivo(si: bool) -> void:
	ver_objetivo = si
	var cfg := ConfigFile.new()
	cfg.load(AJUSTES)
	cfg.set_value("juego", "objetivo", si)
	cfg.save(AJUSTES)


## Al cargar o empezar partida: se apunta cómo está todo sin avisar de nada
func _tomar_foto() -> void:
	_antes.clear()
	for m in lista:
		_antes[m["id"]] = {"estado": estado(m), "paso": paso_actual(m).get("indice", -1)}
	cambiada.emit()


func _process(_delta: float) -> void:
	if _revisar:
		_revisar = false
		_comparar()


func _comparar() -> void:
	for m in lista:
		var id: String = m["id"]
		var ahora := {"estado": estado(m), "paso": paso_actual(m).get("indice", -1)}
		var antes: Dictionary = _antes.get(id, {"estado": "oculta", "paso": -1})
		_antes[id] = ahora
		if ahora["estado"] == antes["estado"] and ahora["paso"] == antes["paso"]:
			continue
		if ahora["estado"] == "hecha" and antes["estado"] != "hecha":
			if antes["estado"] == "activa":
				mision_cumplida.emit(m)
			if seguida_id() == id:
				Estado.extra.erase("mision_seguida")
		elif ahora["estado"] == "activa" and antes["estado"] == "oculta":
			mision_nueva.emit(m)
			# una misión de historia nueva pasa a ser la que se sigue (si no se seguía otra de historia)
			var actual := seguida()
			if m.get("tipo", "") == "historia" and (actual.is_empty() or actual.get("tipo", "") != "historia"):
				Estado.extra["mision_seguida"] = id
		elif ahora["estado"] == "activa" and int(ahora["paso"]) > int(antes["paso"]):
			paso_cumplido.emit(m)
	cambiada.emit()


# --- Consultas ------------------------------------------------------------------------

func buscar(id: String) -> Dictionary:
	for m in lista:
		if m["id"] == id:
			return m
	return {}


## "oculta", "activa" o "hecha"
func estado(m: Dictionary) -> String:
	if not Estado.cumple(m.get("aparece", []), []):
		return "oculta"
	var hecha: Array = m.get("hecha", [])
	if not hecha.is_empty():
		return "hecha" if Estado.cumple(hecha, []) else "activa"
	return "hecha" if _cumplido(m["pasos"].back()) else "activa"


func activas() -> Array:
	var salida := lista.filter(func(m: Dictionary) -> bool: return estado(m) == "activa")
	salida.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		return _orden(a) < _orden(b))
	return salida


func hechas() -> Array:
	return lista.filter(func(m: Dictionary) -> bool: return estado(m) == "hecha")


func _orden(m: Dictionary) -> int:
	return ["historia", "encargo", "lazo", "secreto"].find(String(m.get("tipo", "encargo"))) * 1000 + lista.find(m)


func seguida_id() -> String:
	return String(Estado.extra.get("mision_seguida", ""))


## La misión que se ve en pantalla: la elegida; si no hay, la primera activa
func seguida() -> Dictionary:
	var m := buscar(seguida_id())
	if not m.is_empty() and estado(m) == "activa":
		return m
	var a := activas()
	return a[0] if not a.is_empty() else {}


func seguir(id: String) -> void:
	Estado.extra["mision_seguida"] = id
	Estado.guardar_pronto()
	cambiada.emit()


## Cuánto lleva un paso con contador: [n, total] ([0, 0] si no tiene)
func progreso(paso: Dictionary) -> Array:
	if paso.has("objeto"):
		var o: Dictionary = paso["objeto"]
		var nombre: String = o.keys()[0]
		return [mini(Estado.cuantos(nombre), int(o[nombre])), int(o[nombre])]
	if paso.has("cuenta"):
		var c: Dictionary = paso["cuenta"]
		var prefijo: String = c["prefijo"]
		var n := 0
		for marca in Estado.marcas:
			if String(marca).begins_with(prefijo):
				n += 1
		return [mini(n, int(c["total"])), int(c["total"])]
	return [0, 0]


func _cumplido(paso: Dictionary) -> bool:
	if paso.has("hecho_tambien") and Estado.cumple(paso["hecho_tambien"], []):
		return true
	if paso.has("objeto") or paso.has("cuenta"):
		var p := progreso(paso)
		if p[0] >= p[1]:
			return true
		if not paso.has("hecho"):
			return false
	return Estado.cumple(paso.get("hecho", []), [])


## El paso de ahora: el primero sin cumplir que no tenga uno posterior ya cumplido
func paso_actual(m: Dictionary) -> Dictionary:
	if estado(m) != "activa":
		return {}
	var pasos: Array = m["pasos"]
	var ultimo_hecho := -1
	for i in pasos.size():
		if _cumplido(pasos[i]):
			ultimo_hecho = i
	var i := ultimo_hecho + 1
	if i >= pasos.size():
		return {}
	return {"texto": texto_paso(pasos[i]), "ir": pasos[i].get("ir", {}), "indice": i}


func texto_paso(paso: Dictionary) -> String:
	var p := progreso(paso)
	return String(paso["texto"]).replace("{n}", str(p[0])).replace("{total}", str(p[1]))


## Los pasos que ya se ven en el diario (los cumplidos y el actual), cada uno {texto, hecho}
func pasos_visibles(m: Dictionary) -> Array:
	var salida := []
	var actual := int(paso_actual(m).get("indice", m["pasos"].size()))
	for i in m["pasos"].size():
		if i > actual:
			break
		salida.append({"texto": texto_paso(m["pasos"][i]), "hecho": i < actual})
	return salida


# --- Adónde ir ------------------------------------------------------------------------

## La siguiente escena de camino a «destino» desde «desde» ("" si no hay camino)
func siguiente_escena(desde: String, destino: String) -> String:
	if desde == destino:
		return destino
	var visitadas := {desde: ""}
	var cola := [desde]
	while not cola.is_empty():
		var e: String = cola.pop_front()
		for v in caminos.get(e, []):
			if visitadas.has(v):
				continue
			visitadas[v] = e
			if v == destino:
				var paso: String = v
				while visitadas[paso] != desde:
					paso = visitadas[paso]
				return paso
			cola.append(v)
	return ""


## Dónde está el objetivo en esta escena (posición global) o null.
## «cerca_de»: para elegir el más cercano cuando hay varios (p. ej. zanahorias)
func objetivo_aqui(cerca_de: Vector2) -> Variant:
	var m := seguida()
	if m.is_empty():
		return null
	var ir: Dictionary = paso_actual(m).get("ir", {})
	if ir.is_empty():
		return null
	var aqui := Estado.escena_actual
	var escena := String(ir.get("escena", aqui))
	if escena != aqui:
		var siguiente := siguiente_escena(aqui, escena)
		if siguiente == "":
			return null
		return _buscar_en_escena("puerta:" + siguiente, cerca_de)
	return _buscar_en_escena(String(ir.get("buscar", "")), cerca_de)


func _buscar_en_escena(que: String, cerca_de: Vector2) -> Variant:
	var partes := que.split(":", true, 1)
	if partes.size() < 2:
		return null
	var tipo := partes[0]
	var valor := partes[1]
	var arbol := get_tree()
	var candidatos: Array = []
	match tipo:
		"casilla":
			var xy := valor.split(",")
			return Vector2(float(xy[0]), float(xy[1])) * 16.0 + Vector2(8, 8)
		"aldeano":
			candidatos = arbol.get_nodes_in_group("aldeanos").filter(func(n: Node) -> bool: return n.get("id") == valor)
		"edificio":
			candidatos = arbol.get_nodes_in_group("edificios").filter(func(n: Node) -> bool: return n.get("id") == valor)
		"puerta":
			candidatos = arbol.get_nodes_in_group("puertas").filter(func(n: Node) -> bool: return n.get("destino") == valor)
			candidatos += arbol.get_nodes_in_group("portales").filter(func(n: Node) -> bool: return n.get("destino") == valor)
		"grupo":
			candidatos = arbol.get_nodes_in_group(valor).filter(_sigue_valiendo.bind(valor))
	var mejor: Variant = null
	var distancia := INF
	for n in candidatos:
		if not (n is Node2D) or not n.is_inside_tree() or n.is_queued_for_deletion():
			continue
		var d: float = (n as Node2D).global_position.distance_squared_to(cerca_de)
		if d < distancia:
			distancia = d
			mejor = (n as Node2D).global_position
	return mejor


## Lo que ya no sirve como objetivo: zonas purgadas, rocas rotas, setas cogidas, estatuas despiertas...
func _sigue_valiendo(n: Node, grupo: String) -> bool:
	if grupo == "zonas":
		return n.get("estado") != 4 and String(n.get("jefe")) == ""     # 4 = PURGADA
	for propiedad in ["rota", "_cogido", "despierto", "abierta"]:
		if n.get(propiedad) == true:
			return false
	return not (n is CanvasItem) or (n as CanvasItem).is_visible_in_tree()
