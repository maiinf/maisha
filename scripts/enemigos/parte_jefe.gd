extends Node2D
## PARTE DE UN JEFE GRANDE (p. ej. la caldera o el morro de la Cosechadora): un punto que recibe los golpes
## del cetro y las explosiones de su lado y se los pasa al jefe (a la función que se le diga).
## Así el cetro, que mide la distancia al objetivo, alcanza bien a un jefe de varias casillas.

var jefe: Node
var al_golpe := ""
var al_danio := ""


func recibir_golpe(danio: int, direccion: Vector2) -> bool:
	if jefe == null or al_golpe == "":
		return false
	return jefe.call(al_golpe, danio, direccion)


func recibir_danio(cantidad: int, desde: Vector2, tipo: String) -> void:
	if jefe and al_danio != "":
		jefe.call(al_danio, cantidad, desde, tipo)
