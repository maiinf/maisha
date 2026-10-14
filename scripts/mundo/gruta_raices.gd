extends "res://scripts/mundo/escena_mundo.gd"
## LA GRUTA DE LAS RAÍCES: una cueva por dentro, al final de La Travesía (las raíces de la boca se apartan con la hoja
## de Mauti). A oscuras (scripts/mundo/gruta/oscuridad.gd): solo alumbran Maisha, las semillas dormidas de los nichos
## y las huellas lilas de Mauti, que llevan al fondo. Salas: el vestíbulo de las semillas, el pasillo de las raíces
## dormidas, el santuario de corteza (el escudo), la galería de las espinas y el fondo, donde algo duerme.

const CHARLA_SCRIPT := preload("res://scripts/mundo/charla.gd")
const OSCURIDAD := preload("res://scripts/mundo/gruta/oscuridad.gd")
const RAIZ_DORMIDA := preload("res://scripts/mundo/gruta/raiz_dormida.gd")
const TAPON := preload("res://arte/mundos/raiz/gruta/raiz_tapon.png")
const ALTAR := preload("res://scripts/mundo/gruta/altar_corteza.gd")
const ESPINO := preload("res://scripts/enemigos/espino.gd")
const GUARDIAN := preload("res://scripts/enemigos/guardian.gd")


func _ready() -> void:
	super()
	var oscuridad: Node2D = OSCURIDAD.new()
	oscuridad.name = "Oscuridad"
	add_child(oscuridad)
	_crear_raices()
	Estado.marca_puesta.connect(_al_poner_marca_gruta)
	if Estado.tiene("gruta_guardian"):
		# ya despierto: se queda en el fondo, tranquilo (su zona ya está purgada)
		var guardian: Node2D = GUARDIAN.new()
		guardian.position = Vector2(32, 15) * 16.0 + Vector2(8, -12)
		$Entidades.add_child(guardian)
	_maisha.caida.connect(_al_caer)
	if not Estado.tiene("gruta_llegada"):
		_pensar_al_llegar.call_deferred()


## Las raíces del mapa: «ŕ» las dormidas del pasillo (cada par, una raíz) y «ř» la maraña que tapa el atajo
func _crear_raices() -> void:
	var filas: PackedStringArray = $Region._filas
	for y in filas.size():
		var fila := filas[y]
		for x in fila.length():
			var c := fila[x]
			if c == "ą":
				var altar: Node2D = ALTAR.new()
				altar.position = Vector2(x, y) * 16.0 + Vector2(8, 14)
				$Entidades.add_child(altar)
			elif c == "ę":
				var marca := "espino/%d,%d" % [x, y]
				if not Estado.tiene(marca):
					var espino: Node2D = ESPINO.new()
					espino.marca = marca
					espino.position = Vector2(x, y) * 16.0 + Vector2(8, 14)
					$Entidades.add_child(espino)
			if (c == "ŕ" or c == "ř") and (x == 0 or fila[x - 1] != c):
				var pos := Vector2(x + 1, y) * 16.0 + Vector2(0, 14)
				if c == "ŕ":
					var raiz: Node2D = RAIZ_DORMIDA.new()
					raiz.position = pos
					$Entidades.add_child(raiz)
				elif not Estado.tiene("gruta_guardian"):
					var tapon := StaticBody2D.new()
					tapon.add_to_group("tapon_raices")
					tapon.position = pos
					var forma := CollisionShape2D.new()
					var caja := RectangleShape2D.new()
					caja.size = Vector2(44, 14)
					forma.shape = caja
					forma.position = Vector2(0, -6)
					tapon.add_child(forma)
					var sprite := Sprite2D.new()
					sprite.texture = TAPON
					sprite.offset = Vector2(0, -26)
					tapon.add_child(sprite)
					var cosa := Node2D.new()
					cosa.set_script(load("res://scripts/mundo/objetos/cosa.gd"))
					cosa.set("charla", "gruta_tapon_oeste" if x < 10 else "gruta_tapon")       # (el del oeste da al Paso de Piedra)
					cosa.set("radio_interaccion", 34.0)
					tapon.add_child(cosa)
					$Entidades.add_child(tapon)


## Al despertar el Guardián, la maraña del atajo se aparta; y al poco, habla
func _al_poner_marca_gruta(marca: String) -> void:
	if marca != "gruta_guardian":
		return
	for tapon in get_tree().get_nodes_in_group("tapon_raices"):
		var t := create_tween()
		t.tween_property(tapon, "modulate:a", 0.0, 1.5)
		t.tween_callback(tapon.queue_free)
	await get_tree().create_timer(2.0).timeout
	if is_inside_tree():
		await CHARLA_SCRIPT.hablar(self, "guardian_despierta")


func _pensar_al_llegar() -> void:
	await get_tree().create_timer(1.5).timeout
	if not is_inside_tree() or Estado.tiene("gruta_llegada"):
		return
	Estado.marcar("gruta_llegada")
	await CHARLA_SCRIPT.hablar(self, "gruta_llegada")


func _al_caer() -> void:
	for zona in get_tree().get_nodes_in_group("zonas"):
		if zona.estado == zona.Estado.CERRADA:
			return
	var punto := _maisha.global_position
	_hud.fundido(func() -> void: _maisha.revivir(punto))
