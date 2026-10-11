extends RefCounted
## FORMA NATURAL DE UNA ZONA: el borde no es una elipse perfecta, se aleja o se acerca según la dirección.
## forma = [a2, a3, a4, a5, fase2, fase3, fase4, fase5] (armónicos 2 a 5). Vacía = elipse.
## La crea herramientas/dibujar_zona.py (datos/zonas/<zona>.json) y la usan la zona, el gestor y el shader.


## Cuánto se aleja el borde en la dirección «v» (1.0 = como la elipse)
static func factor(forma: PackedFloat32Array, v: Vector2) -> float:
	if forma.size() < 8:
		return 1.0
	var a := v.angle()
	var f := 1.0
	for k in 4:
		f += forma[k] * sin(float(k + 2) * a + forma[k + 4])
	return f
