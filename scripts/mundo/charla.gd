extends RefCounted
## CHARLAS: elige qué dice cada personaje según lo que ya ha pasado.
## Los textos están en datos/dialogos/*.json (se pueden editar sin tocar el código):
##   kitovu.json (el comienzo: Mzee Shamba, el narrador, los pensamientos de Maisha) y raiz.json.
## Cada conversación puede tener:
##   "si" / "no"     marcas que tienen que estar (o no estar) puestas
##   "tiene"         objetos que Maisha tiene que llevar, p. ej. {"seta_luminosa": 3}
##   "lineas"        lo que se dice. {seta_luminosa} se cambia por cuántas lleva Maisha
##   "entrega"       objetos que Maisha entrega al terminar
##   "recibe"        objetos que Maisha recibe al terminar, p. ej. {"sopa": 1}
##   "marca"         una marca (o una lista de marcas) que se pone al terminar
##   "despues"       líneas que se dicen un poco después (p. ej. tras reconstruir una casa)
##   "aviso"         mensaje que sale arriba al final de todo (p. ej. «¡Cetro templado!»)
##   "estilo"        "normal", "pensamiento" o "narrador" (también puede ir en el personaje)
##   "historia"      lista de {"imagen": "1_kitovu_antes", "lineas": [...]}: se cuenta con ilustraciones
##                   (arte/historia/<imagen>.png) después de «lineas»
##   "abre"          al terminar abre algo: "tienda" (el puesto de Tawi)
##   "tras_historia" líneas que se dicen al acabar la historia, antes de poner las marcas

const ARCHIVOS := ["res://datos/dialogos/kitovu.json", "res://datos/dialogos/raiz.json"]

static var _datos: Dictionary = {}


static func datos() -> Dictionary:
	if _datos.is_empty():
		for ruta in ARCHIVOS:
			var datos: Dictionary = (load(ruta) as JSON).data
			_datos.merge(datos)
	return _datos


## La primera conversación de «id» que cumple sus condiciones ({} si no hay ninguna)
static func elegir(id: String) -> Dictionary:
	var personaje: Dictionary = datos().get(id, {})
	for conv in personaje.get("conversaciones", []):
		if Estado.cumple(conv.get("si", []), conv.get("no", [])) and _lleva(conv.get("tiene", {})):
			return conv
	return {}


static func _lleva(objetos: Dictionary) -> bool:
	for o in objetos:
		if Estado.cuantos(String(o)) < int(objetos[o]):
			return false
	return true


## Cambia {objeto} por cuántos lleva Maisha
static func _rellenar(lineas: Array) -> Array:
	var salida := []
	for l in lineas:
		var texto := String(l)
		for o in Estado.OBJETOS:
			texto = texto.replace("{%s}" % o, str(Estado.cuantos(o)))
		salida.append(texto)
	return salida


static func _marcas(conv: Dictionary) -> Array:
	var m = conv.get("marca", [])
	return m if m is Array else [m]


## Retrato para la caja de diálogo (arte/retratos/<id>.png), si lo hay
static func retrato_de(id: String) -> Texture2D:
	var ruta := "res://arte/retratos/%s.png" % id
	return load(ruta) if ResourceLoader.exists(ruta) else null


static func nombre(id: String) -> String:
	return String(datos().get(id, {}).get("nombre", ""))


## ¿Tiene algo nuevo que contar? (una conversación que deja marca y aún no se ha oído)
static func tiene_novedad(id: String) -> bool:
	var conv := elegir(id)
	for m in _marcas(conv):
		if not Estado.tiene(String(m)):
			return true
	return false


## Muestra la conversación en la caja de diálogo y pone su marca al terminar
static func hablar(desde: Node, id: String) -> void:
	var conv := elegir(id)
	var dialogo := desde.get_tree().get_first_node_in_group("dialogo")
	if conv.is_empty() or dialogo == null:
		return
	var estilo := String(conv.get("estilo", datos().get(id, {}).get("estilo", "normal")))
	var retrato := retrato_de(id)
	await dialogo.decir(nombre(id), _rellenar(conv["lineas"]), estilo, retrato)
	if conv.has("historia"):
		for parte in conv["historia"]:
			dialogo.mostrar_ilustracion(load("res://arte/historia/%s.png" % parte["imagen"]))
			await dialogo.decir(nombre(id), _rellenar(parte["lineas"]), estilo, retrato)
		dialogo.ocultar_ilustracion()
	if conv.has("tras_historia"):
		await dialogo.decir(nombre(id), _rellenar(conv["tras_historia"]), estilo, retrato)
	var entrega: Dictionary = conv.get("entrega", {})
	if not entrega.is_empty():
		Sonido.efecto("entregar")
		if not conv.has("aviso"):
			Sonido.fanfarria("tarea")                # ¡tarea cumplida!
	for o in entrega:
		Estado.quitar(String(o), int(entrega[o]))
	var recibe: Dictionary = conv.get("recibe", {})
	for o in recibe:
		Estado.dar(String(o), int(recibe[o]))
	for m in _marcas(conv):
		Estado.marcar(String(m))
	var arbol := dialogo.get_tree()
	if conv.has("despues"):
		# una pausa (p. ej. mientras se reconstruye una casa) sin que Maisha se mueva
		var maisha := arbol.get_first_node_in_group("maisha")
		if maisha:
			maisha.set("puede_actuar", false)
		await arbol.create_timer(1.6).timeout
		if not is_instance_valid(dialogo) or not dialogo.is_inside_tree():
			return
		await dialogo.decir(nombre(id), _rellenar(conv["despues"]), estilo, retrato)
	if String(conv.get("abre", "")) == "tienda":
		var tienda: CanvasLayer = load("res://scripts/interfaz/tienda_tawi.gd").new()
		arbol.current_scene.add_child(tienda)
		tienda.abrir()
		await tienda.cerrado
	if conv.has("aviso"):
		Sonido.fanfarria("objeto")             # ¡has conseguido algo!
		var hud := arbol.get_first_node_in_group("hud")
		if hud:
			hud.mostrar_mensaje(String(conv["aviso"]))
