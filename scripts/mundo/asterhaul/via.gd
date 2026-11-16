extends RefCounted
## LAS VÍAS de Asterhaul (las casillas «=» del mapa): lo que comparten las vagonetas y los Mchimbaji para rodar.
##   - `seguir()`: hacia dónde sigue algo que llega a una casilla: manda el CAMBIO DE AGUJAS si lo hay
##     (asterhaul/aguja.gd, salvo que venga justo de ese ramal); si no, recto; si no, gira por donde siga la vía.
##   - `tope()`: lo que corta la vía en una casilla (grupo «topes_via» con `es_tope()`): una barricada entera, la
##     reja cerrada, otra vagoneta...


static func casilla(p: Vector2) -> Vector2i:
	return Vector2i(floori(p.x / 16.0), floori((p.y - 6.0) / 16.0))


static func centro(c: Vector2i) -> Vector2:
	return Vector2(c) * 16.0 + Vector2(8, 14)


static func es_via(filas: PackedStringArray, c: Vector2i) -> bool:
	return c.y >= 0 and c.y < filas.size() and c.x >= 0 and c.x < filas[c.y].length() and filas[c.y][c.x] == "="


## Vector2i.ZERO si la vía se acaba
static func seguir(arbol: SceneTree, filas: PackedStringArray, aqui: Vector2i, dir: Vector2i) -> Vector2i:
	var opciones: Array[Vector2i] = []
	for a in arbol.get_nodes_in_group("agujas"):
		if a.casilla == aqui and a.direccion() != -dir:
			opciones.append(a.direccion())
	opciones.append_array([dir, Vector2i(dir.y, dir.x), Vector2i(-dir.y, -dir.x)])
	for d in opciones:
		if es_via(filas, aqui + d):
			return d
	return Vector2i.ZERO


static func tope(arbol: SceneTree, c: Vector2i, quien: Node = null) -> Node:
	for t in arbol.get_nodes_in_group("topes_via"):
		if t != quien and casilla((t as Node2D).global_position) == c and t.call("es_tope"):
			return t
	return null
