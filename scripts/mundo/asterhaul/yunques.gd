extends RefCounted
## LOS DOCE YUNQUES DE MEMORIA de Mji-Jiwe: uno por cada artesano al que el polvo gris dejó sin pulso. Cada uno
## despierta con la marca «<nombre>_pulso» de su artesano (se la pone su conversación al darle una Esquirla de
## Estrella). Mwamba está en el Desfiladero; Kito, Moto y Pigo, en los otros caminos; los demás, en la ciudad.
## Con los doce (y las tres cadenas rotas) se abrirá el pozo del Núcleo.

const ARTESANOS := ["mwamba", "jabali", "kokoto", "tofali", "cheche", "makaa", "bati", "mlio", "sauti", "kito", "moto", "pigo"]


static func marca(nombre: String) -> String:
	return nombre + "_pulso"


static func cuantos() -> int:
	var n := 0
	for a in ARTESANOS:
		if Estado.tiene(marca(a)):
			n += 1
	return n


static func completo() -> bool:
	return cuantos() == ARTESANOS.size()
