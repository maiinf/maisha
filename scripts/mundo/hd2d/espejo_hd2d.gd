extends Node3D
## EL ESPEJO HD-2D: dibuja en 3D la escena 2D que se está jugando, sin cambiar nada del juego.
## El juego sigue siendo 2D por dentro (física, enemigos, zonas, diálogos...); esto solo cambia CÓMO SE VE:
##   - EL SUELO: cerca de Maisha, la capa de suelo (abajo); más lejos, el suelo pintado del mapa
##     (arte/mundos/<mundo>/suelos/<mapa>_suelo.png).
##   - LAS PEÑAS («0» del mapa) se levantan como bloques de roca, con el suelo pintado encima.
##   - CADA DIBUJO del mundo (Sprite2D y AnimatedSprite2D) tiene su gemelo 3D DE PIE (Sprite3D que mira a la cámara),
##     en su sitio del suelo y con SOMBRA real; lo que va pegado al suelo (z por debajo de -4) se tumba en el suelo.
##     Las capas de un mismo personaje (cuerpo, ropa, cetro) se apoyan en el mismo punto del suelo.
##   - LO QUE SE DIBUJA CON CÓDIGO (_draw) va por capas (el «canal» visibility_layer de cada dibujo):
##       · lo del suelo y los efectos (zonas de Giza, hierba, brotes, avisos, golpes...): se pinta en una CAPA DE
##         SUELO (un SubViewport que mira la misma escena 2D) que se tumba sobre el suelo 3D alrededor de Maisha;
##       · lo de pantalla (niebla, hojas, nevada, ventisca, rayos de sol): CAPA DE PANTALLA, delante, como en 2D;
##       · lo que va de pie (llamas, halos, el «!»...: DE_PIE): en una VENTANITA de pie sobre su objeto;
##       · las sombras ovaladas pintadas (sombra.gd): no se ven (ya hay sombras de verdad).
##     Los dibujos pegados al suelo (z por debajo de -4) también van a la capa de suelo.
##   - UNA CÁMARA en perspectiva que sigue a Maisha, el sol (con el reloj del día) y algo de niebla.
## La escena 2D no se oculta: solo deja de pintarse en la pantalla principal (canvas_cull_mask); la interfaz
## (CanvasLayer) sigue igual. Medidas: 16 px = 1 m (una casilla).

const PX := 1.0 / 16.0
const ALTO_PENA := 1.25            # metros que se levanta una peña (lo que mide su pared pintada: unos 20 px)
## Mapas en los que la pared pintada es el doble de alta (gargantas y montaña: pintar_suelo, «cara=2»)
const PARED_DOBLE := ["canada_eco", "paso_piedra", "sendero_olvidado", "ruinas_primer_arbol", "paso_escarcha"]
const SUELO_BAJO := -4             # dibujos con z_index por debajo: se tumban en el suelo
const CAMARA_INCLINACION := -48.0  # grados (mirando hacia abajo)
const CAMARA_DISTANCIA := 30.0     # metros hasta Maisha (se ve más o menos lo mismo que en 2D)
const CAMARA_FOV := 30.0
const LEJOS := 30.0                # metros: más allá de esto (de la cámara), los gemelos no se copian
## Los canales de dibujo (visibility_layer) del mundo; la interfaz se queda en el 1, el de siempre. La pantalla
## principal deja de pintar estos canales y las capas pintan solo el suyo.
const CANAL_SUELO := 1 << 12
const CANAL_GEMELO := 1 << 13
const CANAL_PANTALLA := 1 << 14
const CANAL_NADA := 1 << 15
const CANAL_PIE := 1 << 16
const CANALES_MUNDO := CANAL_SUELO | CANAL_GEMELO | CANAL_PANTALLA | CANAL_NADA | CANAL_PIE
## Los que dibujan con código algo que va DE PIE (llamas, halos, el «!» de los aldeanos, la niebla de un arco):
## lo que dibujan ellos (o sus hijos sin script) se ve en una VENTANITA de pie sobre ellos (_ventanas)
const DE_PIE := ["brasero.gd", "fogata.gd", "farol.gd", "farol_runico.gd", "eco_perdido.gd", "esencia.gd",
	"recogible.gd", "arco_ruinas.gd", "portal.gd", "aldeano.gd", "taa.gd"]
const VENTANA := Vector2i(128, 160)       # píxeles de cada ventanita
const VENTANA_PIE := Vector2(64, 148)     # dónde cae el pie del objeto dentro de la ventanita
const VENTANAS := 10                      # como mucho, las de los 10 objetos de pie más cerca de la cámara
const LADO_CAPA := 1024            # píxeles de la capa de suelo (64 m alrededor de Maisha)
## El suelo cercano: la capa de suelo, con luz (para las sombras)
## Con «hundido» = 0 es el suelo, con un agujero donde hay agua; con 1, el agua (más abajo, algo más oscura y azul,
## con un brillo que se mueve). «agua» es la máscara del mapa (1 píxel por casilla).
const SOMBREADOR_CAPA := """
shader_type spatial;
render_mode diffuse_lambert, specular_disabled;
uniform sampler2D capa : filter_nearest;
uniform sampler2D agua : filter_linear;
uniform vec2 origen = vec2(0.0);
uniform vec2 casillas = vec2(1.0);
uniform float lado = 1024.0;
uniform float hundido = 0.0;
void fragment() {
	vec2 px = origen + UV * lado;
	// (la máscara, suavizada y con un temblor, para que la orilla sea curva como la pintada y no en escalones)
	float temblor = sin(px.x * 0.37 + px.y * 0.21) * 0.06 + sin(px.y * 0.53 - px.x * 0.17) * 0.05;
	float es_agua = texture(agua, px / 16.0 / casillas).r + temblor;
	if (hundido < 0.5 && es_agua > 0.5) { discard; }
	if (hundido > 0.5 && es_agua <= 0.5) { discard; }
	vec3 c = texture(capa, UV).rgb;
	if (hundido > 0.5) {
		float brillo = sin(px.x * 0.07 + TIME * 1.3) * sin(px.y * 0.11 - TIME * 0.9);
		c = mix(c, vec3(0.08, 0.16, 0.24), 0.22) + vec3(0.05, 0.07, 0.08) * smoothstep(0.75, 1.0, brillo);
		// junto a la orilla, la sombra del borde (se nota que el agua está más abajo)
		c *= mix(0.55, 1.0, smoothstep(0.5, 0.72, es_agua));
	}
	ALBEDO = c;
	ROUGHNESS = 1.0;
}
"""
## El suelo lejano (todo el mapa): igual, pero con el suelo pintado y la máscara a la medida del mapa
const SOMBREADOR_LEJANO := """
shader_type spatial;
render_mode diffuse_lambert, specular_disabled;
uniform sampler2D suelo : filter_nearest, source_color;
uniform sampler2D agua : filter_linear;
uniform float hundido = 0.0;
void fragment() {
	float es_agua = texture(agua, UV).r;
	if (hundido < 0.5 && es_agua > 0.5) { discard; }
	if (hundido > 0.5 && es_agua <= 0.5) { discard; }
	vec3 c = texture(suelo, UV).rgb;
	if (hundido > 0.5) { c = mix(c, vec3(0.08, 0.16, 0.24), 0.22) * mix(0.55, 1.0, smoothstep(0.5, 0.72, es_agua)); }
	ALBEDO = c;
	ROUGHNESS = 1.0;
}
"""
const HONDO_AGUA := 0.35             # metros que baja el agua
const LETRAS_AGUA := "~\\"
## Dibujos de pantalla (por su script): van a la capa de pantalla, con sus hijos
const DE_PANTALLA := ["ambiente.gd", "nevada.gd", "ventisca.gd", "luz_sol.gd"]

var escena: Node2D
var region: Node2D
var camara: Camera3D
var sol: DirectionalLight3D
var _gemelos := {}                 # id del dibujo 2D -> Sprite3D
var _maisha: Node2D
var _foco := Vector3.ZERO
var _alto_pena := ALTO_PENA
var _mats_capa: Array[ShaderMaterial] = []
var _plano_agua: MeshInstance3D
var _mascara_agua: ImageTexture
var _suelos_lejanos: Array[ShaderMaterial] = []
var _tinte := Color.WHITE
var _canales := {}                 # id de cada dibujo -> [dibujo, su canal de antes] (para devolverlo al apagar)
var _capa_suelo: SubViewport
var _plano_capa: MeshInstance3D
var _capa_pantalla: SubViewport
var _ventanas: Array = []          # [SubViewport, Sprite3D] (se reparten entre los objetos de pie más cercanos)
var _de_pie := {}                  # id del objeto de pie (su cuerpo) -> el cuerpo
var _velo_pantalla: CanvasLayer
var _mascara_antes := 0xFFFFFFFF


func _ready() -> void:
	region = escena.get_node_or_null("Region")
	_maisha = escena.get_tree().get_first_node_in_group("maisha") as Node2D
	_crear_ambiente()
	_crear_suelo()
	_crear_camara()
	_crear_capas()
	for n in _todos(escena):
		_registrar(n)
	# la raíz de la escena, en los canales de las dos capas (si no, se llevaría por delante a todos sus hijos)
	_canales[escena.get_instance_id()] = [escena, escena.visibility_layer]
	escena.visibility_layer = escena.visibility_layer | CANAL_SUELO | CANAL_PANTALLA | CANAL_PIE
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
	entorno.ambient_light_energy = 0.4     # (medido: con esto y el sol, el suelo al sol sale igual de claro que en 2D)
	entorno.tonemap_mode = Environment.TONE_MAPPER_LINEAR      # (los colores del pixel art, tal cual)
	entorno.fog_enabled = false        # (la niebla aclaraba los oscuros: la del juego ya la pinta la capa de pantalla)
	entorno.glow_enabled = false
	var mundo := WorldEnvironment.new()
	mundo.environment = entorno
	add_child(mundo)
	sol = DirectionalLight3D.new()
	sol.shadow_enabled = true
	sol.light_energy = 0.27
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
	_alto_pena = ALTO_PENA * (2.0 if String(region.get("mapa")) in PARED_DOBLE else 1.0)
	var filas: PackedStringArray = region.get("_filas")
	var ancho: float = filas[0].length()
	var alto: float = filas.size()
	var mat := StandardMaterial3D.new()
	mat.albedo_texture = tex
	mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	mat.roughness = 1.0
	# el suelo: una sola malla del tamaño del mapa con el suelo pintado (con el agujero del agua) y, debajo, el agua
	var plano := PlaneMesh.new()
	plano.size = Vector2(ancho, alto)
	var lejano := Shader.new()
	lejano.code = SOMBREADOR_LEJANO
	_suelos_lejanos.clear()
	for hundido in [0.0, 1.0]:
		var m := ShaderMaterial.new()
		m.shader = lejano
		m.set_shader_parameter("suelo", tex)
		m.set_shader_parameter("hundido", hundido)
		_suelos_lejanos.append(m)
		var suelo := MeshInstance3D.new()
		suelo.mesh = plano
		suelo.material_override = m
		suelo.position = Vector3(ancho / 2.0, -HONDO_AGUA if hundido > 0.5 else 0.0, alto / 2.0)
		add_child(suelo)
	# el agua: una máscara (1 píxel por casilla) para hundirla (la orilla la dibujan los sombreadores, curva y con su
	# sombra)
	var img := Image.create(int(ancho), int(alto), false, Image.FORMAT_L8)
	for y in filas.size():
		for x in filas[y].length():
			if not LETRAS_AGUA.contains(filas[y][x]):
				continue
			img.set_pixel(x, y, Color.WHITE)
	_mascara_agua = ImageTexture.create_from_image(img)
	for m in _suelos_lejanos:
		m.set_shader_parameter("agua", _mascara_agua)
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
	# las paredes: la del sur, con la pared de roca que ya está pintada en el suelo; las demás, de roca oscura
	var paredes := MeshInstance3D.new()
	paredes.mesh = lados.commit()
	paredes.material_override = mat
	add_child(paredes)


## Un tramo de peña de x0 a x1 (casillas) en la fila y: techo con el suelo pintado y paredes donde no hay peña al lado
func _bloque(st: SurfaceTool, lados: SurfaceTool, x0: int, x1: int, y: int, ancho: float, alto: float, filas: PackedStringArray) -> void:
	# En el dibujo 2D (vista 3/4) la peña ya está pintada como se vería: su pared del sur ocupa una franja de
	# «h» casillas dentro de la peña, y lo de encima está corrido hacia el norte esa misma altura. Por eso, en 3D:
	# el techo (a «h» de alto) toma el dibujo de «h» casillas más al norte, y la pared del sur, la franja pintada.
	var h := _alto_pena
	var uv := func(px: float, pz: float) -> Vector2: return Vector2(px / ancho, clampf(pz, 0.0, alto) / alto)
	_cuad(st, Vector3(x0, h, y), Vector3(x1, h, y), Vector3(x1, h, y + 1), Vector3(x0, h, y + 1),
		uv.call(x0, y - h), uv.call(x1, y - h), uv.call(x1, y + 1 - h), uv.call(x0, y + 1 - h))
	for x in range(x0, x1):
		if y + 1 >= filas.size() or filas[y + 1][x] != "0":
			_cuad(lados, Vector3(x, h, y + 1), Vector3(x + 1, h, y + 1), Vector3(x + 1, 0, y + 1), Vector3(x, 0, y + 1),
				uv.call(x, y + 1 - h), uv.call(x + 1, y + 1 - h), uv.call(x + 1, y + 1), uv.call(x, y + 1))
		if y == 0 or filas[y - 1][x] != "0":
			_cuad(lados, Vector3(x + 1, h, y), Vector3(x, h, y), Vector3(x, 0, y), Vector3(x + 1, 0, y),
				uv.call(x + 1, y - h), uv.call(x, y - h), uv.call(x, y), uv.call(x + 1, y))
	# los lados este y oeste: la pared pintada de la casilla de la esquina, estirada (se ven poco)
	if x0 > 0:
		_cuad(lados, Vector3(x0, h, y), Vector3(x0, h, y + 1), Vector3(x0, 0, y + 1), Vector3(x0, 0, y),
			uv.call(x0, y + 1 - h), uv.call(x0 + 1, y + 1 - h), uv.call(x0 + 1, y + 1), uv.call(x0, y + 1))
	if x1 < filas[y].length():
		_cuad(lados, Vector3(x1, h, y + 1), Vector3(x1, h, y), Vector3(x1, 0, y), Vector3(x1, 0, y + 1),
			uv.call(x1 - 1, y + 1 - h), uv.call(x1, y + 1 - h), uv.call(x1, y + 1), uv.call(x1 - 1, y + 1))


func _cuad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, ua := Vector2.ZERO, ub := Vector2.ZERO, uc := Vector2.ZERO, ud := Vector2.ZERO) -> void:
	var n := (b - a).cross(c - a).normalized() * -1.0
	for p in [[a, ua], [b, ub], [c, uc], [a, ua], [c, uc], [d, ud]]:
		st.set_normal(n)
		st.set_uv(p[1])
		st.add_vertex(p[0])


# --- Las capas de lo que se dibuja con código -----------------------------------------------------------------

func _crear_capas() -> void:
	var vista := escena.get_viewport()
	# la capa de suelo: mira la escena 2D alrededor de Maisha y se tumba sobre el suelo
	_capa_suelo = SubViewport.new()
	_capa_suelo.size = Vector2i(LADO_CAPA, LADO_CAPA)
	_capa_suelo.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_capa_suelo.world_2d = vista.world_2d
	_capa_suelo.canvas_cull_mask = CANAL_SUELO
	_capa_suelo.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	add_child(_capa_suelo)
	# (el suelo cercano ES esta capa: el suelo pintado, con el gris de Giza donde lo hay, y todo lo que se dibuja
	# encima; con luz, para que reciba las sombras de verdad)
	var sombreador := Shader.new()
	sombreador.code = SOMBREADOR_CAPA
	var plano := PlaneMesh.new()
	plano.size = Vector2(LADO_CAPA * PX, LADO_CAPA * PX)
	for hundido in [0.0, 1.0]:
		var mat := ShaderMaterial.new()
		mat.shader = sombreador
		mat.set_shader_parameter("capa", _capa_suelo.get_texture())
		mat.set_shader_parameter("agua", _mascara_agua)
		mat.set_shader_parameter("casillas", Vector2(_mascara_agua.get_width(), _mascara_agua.get_height()) if _mascara_agua else Vector2.ONE)
		mat.set_shader_parameter("lado", float(LADO_CAPA))
		mat.set_shader_parameter("hundido", hundido)
		_mats_capa.append(mat)
		var p := MeshInstance3D.new()
		p.mesh = plano
		p.material_override = mat
		p.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(p)
		if hundido > 0.5:
			_plano_agua = p
		else:
			_plano_capa = p
	# la capa de pantalla: lo mismo que verían los ojos en 2D, delante del 3D (y detrás de la interfaz)
	_capa_pantalla = SubViewport.new()
	_capa_pantalla.size = vista.get_visible_rect().size
	_capa_pantalla.transparent_bg = true
	_capa_pantalla.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	_capa_pantalla.world_2d = vista.world_2d
	_capa_pantalla.canvas_cull_mask = CANAL_PANTALLA
	_capa_pantalla.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
	add_child(_capa_pantalla)
	_velo_pantalla = CanvasLayer.new()
	_velo_pantalla.layer = 5
	var cuadro := TextureRect.new()
	cuadro.texture = _capa_pantalla.get_texture()
	cuadro.set_anchors_preset(Control.PRESET_FULL_RECT)
	cuadro.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cuadro.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_velo_pantalla.add_child(cuadro)
	add_child(_velo_pantalla)
	# las ventanitas de lo que va de pie
	for i in VENTANAS:
		var v := SubViewport.new()
		v.size = VENTANA
		v.transparent_bg = true
		v.world_2d = vista.world_2d
		v.canvas_cull_mask = CANAL_PIE
		v.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		v.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST
		add_child(v)
		var g := Sprite3D.new()
		g.texture = v.get_texture()
		g.pixel_size = PX
		g.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
		g.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
		g.shaded = false
		g.alpha_cut = SpriteBase3D.ALPHA_CUT_DISABLED
		g.transparent = true
		g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		g.offset = Vector2(VENTANA.x / 2.0 - VENTANA_PIE.x, VENTANA_PIE.y - VENTANA.y / 2.0)
		g.visible = false
		add_child(g)
		_ventanas.append([v, g])
	# la pantalla principal deja de pintar el mundo 2D (sigue vivo y viéndose en las capas); la interfaz, sí
	_mascara_antes = vista.canvas_cull_mask
	vista.canvas_cull_mask = _mascara_antes & ~CANALES_MUNDO


func _mover_capas() -> void:
	# la capa de suelo, centrada en el foco (a píxeles enteros, para que no tiemble)
	var centro := Vector2(roundf(_foco.x / PX), roundf(_foco.z / PX))
	_capa_suelo.canvas_transform = Transform2D(0.0, -(centro - Vector2(LADO_CAPA, LADO_CAPA) / 2.0))
	_plano_capa.position = Vector3(centro.x * PX, 0.005, centro.y * PX)
	_plano_agua.position = Vector3(centro.x * PX, -HONDO_AGUA, centro.y * PX)
	for mat in _mats_capa:
		mat.set_shader_parameter("origen", centro - Vector2(LADO_CAPA, LADO_CAPA) / 2.0)
	_capa_pantalla.canvas_transform = escena.get_viewport().canvas_transform
	# las ventanitas: para los objetos de pie más cercanos a la cámara, cada una mirando su trocito de la escena
	var cerca := []
	for id in _de_pie.keys():
		var c: Node2D = _de_pie[id]
		if not is_instance_valid(c):
			_de_pie.erase(id)
			continue
		var d := _al_suelo(c.global_position).distance_to(_foco)
		if d < LEJOS * 0.7:
			cerca.append([d, c])
	cerca.sort_custom(func(a: Array, b: Array) -> bool: return a[0] < b[0])
	for i in _ventanas.size():
		var v: SubViewport = _ventanas[i][0]
		var g: Sprite3D = _ventanas[i][1]
		if i >= cerca.size():
			g.visible = false
			continue
		var c: Node2D = cerca[i][1]
		var pie := c.global_position.round()
		v.canvas_transform = Transform2D(0.0, -(pie - VENTANA_PIE))
		g.position = _al_suelo(pie) + Vector3(0, 0, 0.06)        # (un pelín hacia la cámara: por delante de su dibujo)
		g.modulate = _tinte
		g.visible = true


func _exit_tree() -> void:
	# todo como estaba: la escena vuelve a pintarse y cada dibujo a su canal
	if is_instance_valid(escena) and escena.is_inside_tree():
		escena.get_viewport().canvas_cull_mask = _mascara_antes
	else:
		get_viewport().canvas_cull_mask = _mascara_antes
	for par in _canales.values():
		if is_instance_valid(par[0]):
			(par[0] as CanvasItem).visibility_layer = par[1]


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
	if not (n is CanvasItem) or not escena.is_ancestor_of(n) or _en_interfaz(n):
		return
	var ci := n as CanvasItem
	if not _canales.has(ci.get_instance_id()):
		_canales[ci.get_instance_id()] = [ci, ci.visibility_layer]
	# ¿a qué capa va?
	if n.get_script() and String(n.get_script().resource_path).ends_with("sombra.gd"):
		ci.visibility_layer = CANAL_NADA
		return
	if _de_pantalla(n):
		ci.visibility_layer = CANAL_PANTALLA
		return
	if not (n is Sprite2D or n is AnimatedSprite2D) or _z(n) < SUELO_BAJO:
		var dueno := _dueno_de_pie(n)
		if _contenedor(n):
			# un contenedor (no pinta nada): en todos los canales, para que sus hijos se vean en su capa
			ci.visibility_layer = CANAL_SUELO | CANAL_PIE
		else:
			# lo que pinta (con código, o un sprite pegado al suelo): de pie (en su ventanita) o en el suelo
			ci.visibility_layer = CANAL_PIE if dueno and _dibuja(n) else CANAL_SUELO
		if dueno:
			var cuerpo := _ancla(dueno as Node2D)
			_de_pie[cuerpo.get_instance_id()] = cuerpo
		return
	ci.visibility_layer = CANAL_GEMELO
	if _gemelos.has(n.get_instance_id()):
		return
	var g := Sprite3D.new()
	g.pixel_size = PX
	g.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
	g.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	g.shaded = false                 # (sus colores de pixel art; de noche se oscurecen con «_tinte»)
	g.double_sided = true
	g.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	g.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
	add_child(g)
	# (lo que no cambia: el cuerpo en el que se apoya y su orden de dibujo; se calcula una vez)
	_gemelos[n.get_instance_id()] = [n, g, null, _z(n)]


## ¿Cuelga de una CanvasLayer (la interfaz: el HUD, los diálogos, la mochila...)? Eso no se toca.
func _en_interfaz(n: Node) -> bool:
	var c: Node = n
	while c and c != escena:
		if c is CanvasLayer:
			return true
		c = c.get_parent()
	return false


## ¿No pinta nada él mismo? (un Node2D, un cuerpo, una forma de choque, una luz... sin _draw)
func _contenedor(n: Node) -> bool:
	if _dibuja(n):
		return false
	return n.get_class() == "Node2D" or n is CollisionObject2D or n is CollisionShape2D or n is CollisionPolygon2D \
		or n is Light2D or n is LightOccluder2D or n is Marker2D or n is RemoteTransform2D or n is CanvasModulate


## ¿Dibuja algo con código? (_draw en su script, o alguien conectado a su señal «draw»)
func _dibuja(n: Node) -> bool:
	return (n.get_script() != null and n.has_method("_draw")) or not n.get_signal_connection_list("draw").is_empty()


## El objeto de pie al que pertenece este dibujo (él mismo o su padre, si es de los DE_PIE), o null
func _dueno_de_pie(n: Node) -> Node:
	for c in [n, n.get_parent()]:
		if c and c != escena and c.get_script():
			var ruta := String(c.get_script().resource_path)
			for nombre in DE_PIE:
				if ruta.ends_with("/" + nombre):
					return c
	return null


## ¿Es un dibujo de pantalla (o cuelga de uno)?
func _de_pantalla(n: Node) -> bool:
	var c: Node = n
	while c and c != escena:
		if c.get_script():
			var ruta := String(c.get_script().resource_path)
			for nombre in DE_PANTALLA:
				if ruta.ends_with(nombre):
					return true
		c = c.get_parent()
	return false


func _quitar(n: Node) -> void:
	var id := n.get_instance_id()
	_canales.erase(id)
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
	_mover_capas()
	# el sol sigue la hora del día (de día, cálido; de noche, frío y flojo), y los dibujos se tiñen igual
	var dia: float = Reloj.luz_dia() if Reloj.has_method("luz_dia") else 1.0
	sol.light_energy = lerpf(0.07, 0.27, dia)
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
	# de pie: apoyado en el suelo de su cuerpo; lo que en 2D está más arriba que el cuerpo, en 3D está más alto
	var sube: Vector2 = n.global_position - ancla.global_position
	var o2: Vector2 = n.offset + Vector2(sube.x, sube.y)
	# (en 2D la «y» crece hacia abajo y en 3D hacia arriba: sin centrar, el dibujo va de o2.y a o2.y + alto en 2D,
	# así que en 3D su borde de abajo está en -(o2.y + alto); centrado, se queda donde está, solo cambia el signo)
	var alto := 0.0
	if not g.centered and tex:
		alto = (g.region_rect.size.y if g.region_enabled else tex.get_height() / float(maxi(g.vframes, 1)))
	g.offset = Vector2(o2.x, -(o2.y + alto))
	# (las capas de un mismo cuerpo, un pelín hacia la cámara según su orden de dibujo, para que no parpadeen)
	var orden := z * 0.004 + n.get_index() * 0.0015
	g.position = _al_suelo(ancla.global_position) + Vector3(0, 0, orden)
