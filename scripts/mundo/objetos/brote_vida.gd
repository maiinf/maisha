extends "res://scripts/mundo/objetos/cosa.gd"
## EL BROTE DEL ÁRBOL DE LA VIDA (en el Claro de Calma): desde que Bibi enseña a meditar,
## al usarlo Maisha medita: recupera la Vida y el Aliento, se guarda la partida
## y se abre el Árbol de la Vida para gastar la Esencia en las Artes.

const ARBOL := preload("res://scripts/interfaz/arbol_vida.gd")

var meditando := false


func _ready() -> void:
	super()
	add_to_group("brote_vida")


func interactuar() -> void:
	if meditando:
		return
	if not Estado.tiene("bibi_meditar"):
		await CHARLA.hablar(self, "claro_brote")
		return
	meditando = true
	var maisha := get_tree().get_first_node_in_group("maisha")
	if maisha:
		maisha.set("puede_actuar", false)
	await CHARLA.hablar(self, "claro_meditar")
	Sonido.efecto("meditar")
	if maisha:
		maisha.set("vida", maisha.call("vida_maxima"))
		maisha.set("aliento", maisha.call("aliento_maximo"))
	Estado.marcar("meditado")
	Estado.guardar()
	var arbol: CanvasLayer = get_tree().get_first_node_in_group("arbol_vida")
	if arbol == null:
		arbol = ARBOL.new()
		get_tree().current_scene.add_child(arbol)
	arbol.abrir()
	await arbol.cerrado
	if maisha and is_instance_valid(maisha):
		maisha.set("puede_actuar", true)
	meditando = false
