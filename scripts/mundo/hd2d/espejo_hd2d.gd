extends Node3D
## EL ESPEJO HD-2D: dibuja en 3D la escena 2D que se está jugando, sin cambiar nada del juego.
## El juego sigue siendo 2D por dentro (física, enemigos, zonas, diálogos...); esto solo cambia CÓMO SE VE:
##   - EL SUELO: el suelo pintado del mapa (arte/mundos/<mundo>/suelos/<mapa>_suelo.png) es el suelo 3D.
##   - LAS PEÑAS («0» del mapa) se levantan como bloques de roca, con el suelo pintado encima.
##   - CADA DIBUJO del mundo (Sprite2D y AnimatedSprite2D) tiene su gemelo 3D DE PIE (Sprite3D que mira a la cámara),
##     en su sitio del suelo y con SOMBRA real; lo que va pegado al suelo (z por debajo de -4) se tumba en el suelo.
##     Las capas de un mismo personaje (cuerpo, ropa, cetro) se apoyan en el mismo punto del suelo.
##   - UNA CÁMARA en perspectiva que sigue a Maisha, el sol (con el reloj del día), niebla y resplandor.
## Medidas: 16 px = 1 m (una casilla).
## Lo que se dibuja con código (_draw: llamas, auras, la ventisca...) todavía no tiene gemelo 3D: se ve en 2D encima.

const PX := 1.0 / 16.0
const ALTO_PENA := 1.25            # metros que se levanta una peña
const SUELO_BAJO := -4             # dibujos con z_index por debajo: se tumban en el suelo
const CAMARA_INCLINACION := -48.0  # grados (mirando hacia abajo)
const CAMARA_DISTANCIA := 30.0     # metros hasta Maisha (se ve más o menos lo mismo que en 2D)
const CAMARA_FOV := 30.0
const LEJOS := 30.0                # metros: más allá de esto (de la cámara), los gemelos no se copian

var escena: Node2D
var region: Node2D
var camara: Camera3D
var sol: DirectionalLight3D
var _gemelos := {}                 # id del dibujo 2D -> Sprite3D
var _maisha: Node2D
var _foco := Vector3.ZERO
var _tinte := Color.WHITE


func _ready() -> void:
	region = escena.get_node_or_null("Region")
	_maisha = escena.get_tree().get_first_node_in_group("maisha") as Node2D
	_crear_ambiente()
	_crear_suelo()
	_crear_camara()
	for n in _todos(escena):
		_registrar(n)
	escena.get_tree().node_added.connect(_registrar)
	escena.get_tree().node_removed.connect(_quitar)


func _todos(nodo: Node) -> Array:
	var lista := [nodo]
	for h in nodo.get_children():
		lista.append_array(_todos(h))
	return lista


# --- El ambiente: sol, cielo, niebla -------------------------------------------------------------------------

func _crear_ambiente() -> void:
	var entorno := Environment.new()
	entorno.background_mode = Environment.BG_COLOR
	entorno.background_color = RenderingServer.get_default_clear_color()
	entorno.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	entorno.ambient_light_color = Color(1, 1, 1)
	entorno.ambient_light_energy = 0.62
	entorno.tonemap_mode = Environment.TONE_MAPPER_LINEAR      # (los colores del pixel art, tal cual)
	entorno.fog_enabled = true
	entorno.fog_light_color = RenderingServer.get_default_clear_color()
	entorno.fog_density = 0.0035
	entorno.glow_enabled = false
	var mundo := WorldEnvironment.new()
	mundo.environment = entorno
	add_child(mundo)
	sol = DirectionalLight3D.new()
	sol.shadow_enabled = true
	sol.light_energy = 0.48
	sol.light_color = Color(1.0, 0.95, 0.86)
	sol.rotation_degrees = Vector3(-50, -35, 0)          # (desde arriba a la izquierda y algo por detrás: sombras hacia delante y a la derecha, como las pintadas)
	sol.directional_shadow_max_distance = 60.0
	add_child(sol)


# --- El suelo y las peñas -------------------------------------------------------------------------------------

func _textura_suelo() -> Texture2D:
	var mundo := String(region.get("mundo")) if region and region.get("mundo") else "raiz"
	var ruta := "res://arte/mundos/%s/suelos/%s_suelo.png" % [mundo, String(region.get("mapa"))]
	return load(ruta) if region and ResourceLoader.exists(ruta) else null


func _crear_suelo() -> void:
	if region == null:
		return
	var tex := _textura_suelo()
	var filas: PackedStringArray = region.get("_filas")
	var ancho: float = filas[0].length()
	var alto: float = filas.size()
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = tex
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	mat.roughness = 0.95
	# el suelo: una sola malla del tamaño del mapa con el suelo pintado
	var plano := PlaneMesh.new()
	plano.size = Vector2(ancho, alto)
	var suelo := MeshInstance3D.new()
	suelo.mesh = plano
	suelo.material_override = mat
	suelo.position = Vector3(ancho / 2.0, 0.0, alto / 2.0)
	add_child(suelo)
	# las peñas: bloques que se levantan, con el suelo pintado encima y los lados de roca oscura
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var lados := SurfaceTool.new()
	lados.begin(Mesh.PRIMITIVE_TRIANGLES)
	for y in filas.size():
		var x := 0
		var fila := filas[y]
		while x < fila.length():
			if fila[x] != "0":
				x += 1
				continue
			var x0 := x
			while x < fila.length() and fila[x] == "0":
				x += 1
			_bloque(st, lados, x0, x, y, ancho, alto, filas)
	var techo := MeshInstance3D.new()
	techo.mesh = st.commit()
	techo.material_override = mat
	add_child(techo)
	var mat_roca := StandardMaterial3D.new()
	mat_roca.albedo_color = Color(0.36, 0.33, 0.34)
	mat_roca.roughness = 1.0
	var paredes := MeshInstance3D.new()
	paredes.mesh = lados.commit()
	paredes.material_override = mat_roca
	add_child(paredes)


## Un tramo de peña de x0 a x1 (casillas) en la fila y: techo con el suelo pintado y paredes donde no hay peña al lado
func _bloque(st: SurfaceTool, lados: SurfaceTool, x0: int, x1: int, y: int, ancho: float, alto: float, filas: PackedStringArray) -> void:
	var h := ALTO_PENA
	var uv := func(px: float, pz: float) -> Vector2: return Vector2(px / ancho, pz / alto)
	_cuad(st, Vector3(x0, h, y), Vector3(x1, h, y), Vector3(x1, h, y + 1), Vector3(x0, h, y + 1),
		uv.call(x0, y), uv.call(x1, y), uv.call(x1, y + 1), uv.call(x0, y + 1))
	# la pared de delante (sur), si abajo no hay peña: es la que se ve
	for x in range(x0, x1):
		if y + 1 >= filas.size() or filas[y + 1][x] != "0":
			_cuad(lados, Vector3(x, h, y + 1), Vector3(x + 1, h, y + 1), Vector3(x + 1, 0, y + 1), Vector3(x, 0, y + 1))
		if y == 0 or filas[y - 1][x] != "0":
			_cuad(lados, Vector3(x + 1, h, y), Vector3(x, h, y), Vector3(x, 0, y), Vector3(x + 1, 0, y))
	if x0 > 0:
		_cuad(lados, Vector3(x0, h, y), Vector3(x0, h, y + 1), Vector3(x0, 0, y + 1), Vector3(x0, 0, y))
	if x1 < filas[y].length():
		_cuad(lados, Vector3(x1, h, y + 1), Vector3(x1, h, y), Vector3(x1, 0, y), Vector3(x1, 0, y + 1))


func _cuad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, ua := Vector2.ZERO, ub := Vector2.ZERO, uc := Vector2.ZERO, ud := Vector2.ZERO) -> void:
	var n := (b - a).cross(c - a).normalized() * -1.0
	for p in [[a, ua], [b, ub], [c, uc], [a, ua], [c, uc], [d, ud]]:
		st.set_normal(n)
		st.set_uv(p[1])
		st.add_vertex(p[0])


# --- La cámara ------------------------------------------------------------------------------------------------

func _crear_camara() -> void:
	camara = Camera3D.new()
	camara.fov = CAMARA_FOV
	camara.rotation_degrees = Vector3(CAMARA_INCLINACION, 0, 0)
	add_child(camara)
	camara.current = true
	if _maisha:
		_foco = _al_suelo(_maisha.global_position)
	_colocar_camara(1.0)


func _colocar_camara(suave: float) -> void:
	if _maisha and is_instance_valid(_maisha):
		_foco = _foco.lerp(_al_suelo(_maisha.global_position), suave)
	# sin salirse del mapa (como la cámara 2D): deja un margen de media pantalla a cada lado
	if region:
		var tam: Vector2 = region.get("tam") * PX
		var mx := minf(16.0, tam.x / 2.0)
		_foco.x = clampf(_foco.x, mx, tam.x - mx)
		_foco.z = clampf(_foco.z, minf(7.0, tam.y / 2.0), tam.y - minf(11.0, tam.y / 2.0))
	var atras := camara.global_transform.basis.z * CAMARA_DISTANCIA
	camara.global_position = _foco + atras


func _al_suelo(p: Vector2) -> Vector3:
	return Vector3(p.x * PX, 0.0, p.y * PX)


# --- Los gemelos de los dibujos -------------------------------------------------------------------------------

func _registrar(n: Node) -> void:
	if not (n is Sprite2D or n is AnimatedSprite2D):
		return
	if not escena.is_ancestor_of(n) or n.name == "Suelo":
		return
	if _gemelos.has(n.get_instance_id()):
		return
	var g := Sprite3D.new()
	g.pixel_size = PX
	g.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	g.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	g.shaded = false                 # (sus colores de pixel art; de noche se oscurecen con «_tinte»)
	g.double_sided = true
	g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	var tumbado := _z(n) < SUELO_BAJO
	if tumbado:
		g.axis = Vector3.AXIS_Y
		g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	else:
		g.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	g.set_meta("tumbado", tumbado)
	add_child(g)
	# (lo que no cambia: el cuerpo en el que se apoya y su orden de dibujo; se calcula una vez)
	_gemelos[n.get_instance_id()] = [n, g, null, _z(n)]


func _quitar(n: Node) -> void:
	var id := n.get_instance_id()
	if _gemelos.has(id):
		(_gemelos[id][1] as Node).queue_free()
		_gemelos.erase(id)


## El z_index de verdad de un dibujo (sumando el de sus padres, si es relativo)
func _z(n: CanvasItem) -> int:
	var z := 0
	var c: Node = n
	while c and c is CanvasItem and c != escena:
		z += (c as CanvasItem).z_index
		if not (c as CanvasItem).z_as_relative:
			break
		c = c.get_parent()
	return z


## El punto del suelo en el que se apoya un dibujo: el de su «cuerpo» (el hijo directo de Entidades, que se
## ordena por altura), o el suyo propio
func _ancla(n: Node2D) -> Node2D:
	var c: Node = n
	while c and c.get_parent() and c.get_parent() != escena:
		var p := c.get_parent()
		if p is CanvasItem and (p as CanvasItem).y_sort_enabled:
			return c as Node2D
		c = p
	return n


## ¿Se ve? (su visibilidad hasta la escena, sin contar la escena, que está oculta)
func _visible(n: CanvasItem) -> bool:
	var c: Node = n
	while c and c != escena:
		if c is CanvasItem and not (c as CanvasItem).visible:
			return false
		c = c.get_parent()
	return true


func _process(_delta: float) -> void:
	for id in _gemelos.keys():
		var par: Array = _gemelos[id]
		var n: Node2D = par[0]
		var g: Sprite3D = par[1]
		if not is_instance_valid(n):
			g.queue_free()
			_gemelos.erase(id)
			continue
		# (solo los que están cerca de la cámara: los demás, ocultos y sin copiar; así no pesa en los mapas grandes)
		var p := n.global_position * PX
		if absf(p.x - _foco.x) > LEJOS or absf(p.y - _foco.z) > LEJOS:
			g.visible = false
			continue
		if par[2] == null or not is_instance_valid(par[2]):
			par[2] = _ancla(n)
		_copiar(n, g, par[2], par[3])
	_colocar_camara(0.12)
	# el sol sigue la hora del día (de día, cálido; de noche, frío y flojo), y los dibujos se tiñen igual
	var dia: float = Reloj.luz_dia() if Reloj.has_method("luz_dia") else 1.0
	sol.light_energy = lerpf(0.12, 0.48, dia)
	sol.light_color = Color(0.6, 0.66, 0.95).lerp(Color(1.0, 0.95, 0.86), dia)
	_tinte = Color(0.42, 0.46, 0.68).lerp(Color.WHITE, dia)


func _copiar(n: Node2D, g: Sprite3D, ancla: Node2D, z: int) -> void:
	g.visible = _visible(n)
	if not g.visible:
		return
	var tex: Texture2D = null
	if n is AnimatedSprite2D:
		var a := n as AnimatedSprite2D
		if a.sprite_frames:
			tex = a.sprite_frames.get_frame_texture(a.animation, a.frame)
		g.hframes = 1
		g.vframes = 1
		g.frame = 0
		g.region_enabled = false
	else:
		var s := n as Sprite2D
		tex = s.texture
		g.hframes = s.hframes
		g.vframes = s.vframes
		g.frame = mini(s.frame, s.hframes * s.vframes - 1)
		g.region_enabled = s.region_enabled
		g.region_rect = s.region_rect
	if tex is CanvasTexture:
		tex = (tex as CanvasTexture).diffuse_texture          # (en 3D, sin el relieve 2D)
	g.texture = tex
	g.flip_h = n.flip_h
	g.flip_v = n.flip_v
	g.centered = n.centered
	g.modulate = n.modulate * n.self_modulate * _tinte
	var escala := n.global_scale
	g.scale = Vector3(escala.x, escala.y, 1.0)
	if g.get_meta("tumbado"):
		# pegado al suelo: en su sitio, mirando hacia arriba
		var o: Vector2 = n.offset
		g.offset = Vector2(o.x, -o.y)
		g.position = _al_suelo(n.global_position) + Vector3(0, 0.01 + z * 0.0005 + 0.05, 0)
		return
	# de pie: apoyado en el suelo de su cuerpo; lo que en 2D está más arriba que el cuerpo, en 3D está más alto
	var sube: Vector2 = n.global_position - ancla.global_position
	var o2: Vector2 = n.offset + Vector2(sube.x, sube.y)
	g.offset = Vector2(o2.x, -o2.y)
	# (las capas de un mismo cuerpo, un pelín hacia la cámara según su orden de dibujo, para que no parpadeen)
	var orden := z * 0.004 + n.get_index() * 0.0015
	g.position = _al_suelo(ancla.global_position) + Vector3(0, 0, orden)
