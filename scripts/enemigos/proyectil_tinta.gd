extends Area2D
## PROYECTIL DE TINTA (Las Estanterías Colgantes, Sigilia): una gota afilada de tinta mágica
## disparada por el Bibliotecario Hueco con su puntero de oro.

const DIBUJO := preload("res://arte/mundos/sigilia/estanterias/proyectil_tinta.png")

var direccion := Vector2.RIGHT
var velocidad := 160.0
var tiempo_vida := 3.5


func _ready() -> void:
	add_to_group("proyectiles_enemigos")
	collision_layer = 0
	collision_mask = 1 | 4  # colisiona con el mundo (1) y con Maisha (4)
	body_entered.connect(_al_chocar)

	var col := CollisionShape2D.new()
	var circ := CircleShape2D.new()
	circ.radius = 5.0
	col.shape = circ
	add_child(col)

	var sp := Sprite2D.new()
	sp.texture = DIBUJO
	sp.rotation = direccion.angle()
	add_child(sp)


func _process(delta: float) -> void:
	global_position += direccion * velocidad * delta
	tiempo_vida -= delta
	if tiempo_vida <= 0.0:
		queue_free()


func _al_chocar(cuerpo: Node2D) -> void:
	if cuerpo and cuerpo.is_in_group("maisha"):
		cuerpo.call("recibir_danio", 1, global_position)
		cuerpo.call("pisar_oxido", 0.5)
	Impacto.chispa(global_position, -direccion, Color("a855f7"))
	queue_free()
