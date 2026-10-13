extends Node2D
## ARREGLAR EL TRANSBORDADOR (Embarcadero Junco), con los poderes de Maisha y sin recados. Solo cuando Mamba ya no
## está (Bata no trabaja «con eso suelto»):
##   1. Una SEMILLA que estalle junto al boquete del casco (desde la punta del muelle) hace crecer juncos que se tejen
##      solos y lo tapan (marca «boquete_tapado»; el dibujo pasa a «tapado pero escorado»).
##   2. El LATIDO, pegado al casco, la empuja y la endereza: vuelve a flotar (marca «transbordador_listo»).
## Lo crea scripts/mundo/embarcadero_junco.gd con la base del transbordador («ß») y su dibujo.

const CHARLA := preload("res://scripts/mundo/charla.gd")
const BOQUETE := Vector2(-54, -26)       # dónde está el boquete, desde la base del transbordador
const VERDE := Color("6fcf4f")
const JUNCO := Color("c9b77d")

var base := Vector2.ZERO                 # la base del transbordador
var sprite: Sprite2D                     # su dibujo (0 varado, 1 a flote, 2 tapado y escorado)
var _vigiladas: Array = []
var _tejiendo := -1.0                    # 0..1 mientras crecen los juncos
var _espera_latido_antes := 0.0
var _enderezando := false


func _ready() -> void:
	z_index = 2
	if Estado.tiene("transbordador_listo"):
		_poner_embarque()


## Ya flota: en la punta del muelle, el sitio para subir (Bata zarpa río arriba: La Travesía)
func _poner_embarque() -> void:
	var embarque := _Embarque.new()
	embarque.position = _boquete() + Vector2(-6, 26)
	add_child(embarque)


class _Embarque:
	extends Node2D
	var radio_interaccion := 26.0
	var altura_bocadillo := 30.0

	func _ready() -> void:
		add_to_group("interactuables")

	func interactuar() -> void:
		await CHARLA.hablar(self, "embarcadero_zarpar")
		Estado.ir_a("la_travesia", "embarcadero")


func _boquete() -> Vector2:
	return base + BOQUETE


func _process(delta: float) -> void:
	if Estado.tiene("transbordador_listo"):
		return
	var maisha := get_tree().get_first_node_in_group("maisha") as Node2D
	if not Estado.tiene("mamba_vencido") or maisha == null:
		return
	# 1. las semillas que estallan junto al boquete
	if not Estado.tiene("boquete_tapado"):
		for s in get_tree().get_nodes_in_group("semillas"):
			if s in _vigiladas:
				continue
			if (s as Node2D).global_position.distance_to(_boquete()) < 48.0:
				_vigiladas.append(s)
				s.tree_exiting.connect(_tejer)
	if _tejiendo >= 0.0:
		_tejiendo = minf(1.0, _tejiendo + delta / 1.4)
		queue_redraw()
		if _tejiendo >= 1.0:
			_tejiendo = -1.0
			sprite.frame = 2
			Estado.marcar("boquete_tapado")
			queue_redraw()
			CHARLA.hablar(self, "embarcadero_juncos_crecen")
	# 2. el Latido pegado al casco la endereza
	var espera := float(maisha.get("_espera_latido"))
	if Estado.tiene("boquete_tapado") and not _enderezando and espera > _espera_latido_antes + 0.5 \
			and maisha.global_position.distance_to(base + Vector2(-20, -10)) < 80.0:
		_enderezar()
	_espera_latido_antes = espera


func _tejer() -> void:
	if Estado.tiene("boquete_tapado") or _tejiendo >= 0.0:
		return
	_tejiendo = 0.0
	Sonido.efecto("brotes", 0.0, _boquete())


func _draw() -> void:
	if _tejiendo < 0.0:
		return
	# los juncos crecen desde el agua y se cruzan sobre el boquete
	var c := _boquete()
	for k in 9:
		var t := clampf(_tejiendo * 1.6 - k * 0.07, 0.0, 1.0)
		var desde := c + Vector2(-9 + k * 2.2, 10)
		var hasta := c + Vector2(-6 + (k % 3) * 6 - (k * 1.3), -6 + (k % 2) * 3)
		draw_line(desde, desde.lerp(hasta, t), VERDE.lerp(JUNCO, t), 1.0)
	if _tejiendo > 0.6:
		draw_circle(c, 7.0 * (_tejiendo - 0.6) / 0.4, Color(JUNCO, 0.8))


func _enderezar() -> void:
	_enderezando = true
	Sonido.efecto("mamba_salta", -4.0, base)
	Impacto.temblar(2.5, 0.5)
	var t := create_tween()
	for i in 6:
		t.tween_property(sprite, "rotation", 0.06 if i % 2 == 0 else -0.04, 0.12)
	t.tween_callback(func() -> void: sprite.frame = 1)
	t.tween_property(sprite, "rotation", 0.0, 0.25).set_trans(Tween.TRANS_BACK)
	await t.finished
	Estado.marcar("transbordador_listo")
	await CHARLA.hablar(self, "embarcadero_flota")
	_poner_embarque()
