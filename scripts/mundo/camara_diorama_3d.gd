extends Camera3D
## Cámara diorama 3D que sigue suavemente al objetivo con perspectiva de teleobjetivo maqueta.

@export var objetivo_path: NodePath = NodePath("../Maisha3D")
@export var distancia := Vector3(0.0, 7.2, 9.2)
@export var suavidad := 6.0

var _objetivo: Node3D = null


func _ready() -> void:
	if not objetivo_path.is_empty():
		_objetivo = get_node_or_null(objetivo_path)
	current = true


func _physics_process(delta: float) -> void:
	if not _objetivo:
		return
	var pos_meta := _objetivo.global_position + distancia
	global_position = global_position.lerp(pos_meta, suavidad * delta)
	look_at(_objetivo.global_position + Vector3(0, 0.4, 0), Vector3.UP)
