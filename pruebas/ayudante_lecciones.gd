extends Node
## (pruebas) Si aparece una lección (el mundo parado esperando una tecla), pulsa la tecla que pide, como haría
## quien juega. Cuenta las lecciones que ha visto, por si una prueba quiere comprobarlo.

var vistas: Array[String] = []
var _pulsando := false


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _process(_delta: float) -> void:
	var leccion := get_tree().get_first_node_in_group("leccion")
	if _pulsando or leccion == null or not leccion.get("activa") or float(leccion.get("_fuerza")) < 0.7:
		return
	_pulsar(String(leccion.get("accion")))


func _pulsar(accion: String) -> void:
	_pulsando = true
	vistas.append(accion)
	await get_tree().process_frame
	Input.action_press(accion)
	await get_tree().process_frame
	await get_tree().process_frame
	Input.action_release(accion)
	await get_tree().process_frame
	_pulsando = false
