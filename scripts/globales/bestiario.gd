extends Node
## EL BESTIARIO (autoload «Bestiario»): cuenta los enemigos que vence Maisha y les da un RANGO, para los logros.
##   - Enemigos: 🥉 bronce, 🥈 plata y 🥇 oro al vencer RANGOS[0], [1] y [2] del mismo (los bichos de la bruja piden más).
##   - Jefes: bronce al vencerlo; plata si te han dado 3 veces o menos en la pelea; oro si no te han dado ni una.
##     (cuenta la mejor pelea; la zona del jefe avisa con empezar_jefe(), al_herir() y jefe_vencido())
## Las cuentas van en Estado.extra["bestiario"] y los rangos son marcas «rango/<bronce|plata|oro>/<tipo>»; las de plata
## y oro dan cristales (datos/tienda.json, «cristales_por_marca»). La ficha de cada uno sale en el diario (Bestiario).
## Lo que lo vence por el camino (la purga de una zona, por ejemplo) no cuenta: lleva la meta «sin_contar».

signal rango_nuevo(tipo: String, rango: int)

const RANGOS := [10, 30, 60]
const NOMBRE_RANGO := ["", "bronce", "plata", "oro"]
const COLOR_RANGO := [Color("8a8aa0"), Color("d08a52"), Color("d8dce8"), Color("f9d77a")]

## tipo: nombre, dónde vive, cómo es, el secreto (se lee con plata), el dibujo [ruta, columnas, filas, fotograma],
## y si es jefe, la marca que deja al vencerlo (para las partidas de antes del Bestiario)
const FICHAS := {
	"petrino": {"nombre": "Petrino", "donde": "Por todo Raíz",
		"texto": "Un trozo de raíz que Giza ha vuelto de piedra y obliga a caminar. Persigue a quien ve y muerde al tocar.",
		"secreto": "No puede pisar los brotes: rodéate de semillas y se queda mirando.", "dibujo": ["res://arte/zonas/raiz/petrino.png", 8, 1, 0]},
	"jabali": {"nombre": "Jabalí de hierro", "donde": "Bosque Cobrizo, Campo Segado",
		"texto": "Giza le cubrió el lomo de placas. Si te ve en línea recta, escarba y embiste muy deprisa.",
		"secreto": "Si se estrella contra un árbol o unos brotes, se queda aturdido: ahí el cetro sí le entra.", "dibujo": ["res://arte/zonas/raiz/jabali.png", 5, 3, 0]},
	"babosa": {"nombre": "Babosa de óxido", "donde": "Ciénaga Quieta, Las Pasarelas",
		"texto": "Se arrastra despacio y deja un rastro de herrumbre que pega los pies al suelo.",
		"secreto": "El rastro se seca a los pocos segundos: a veces basta con esperar.", "dibujo": ["res://arte/mundos/raiz/cienaga/babosa.png", 6, 1, 0]},
	"rana": {"nombre": "Rana de piedra", "donde": "Las Pasarelas, Lago Espejo",
		"texto": "Se agazapa, salta hacia ti y cae con una onda. En el aire no hay quien le dé.",
		"secreto": "Al caer se queda atontada: un golpe entonces le quita el doble.", "dibujo": ["res://arte/mundos/raiz/pasarelas/rana.png", 6, 1, 0]},
	"topo": {"nombre": "Topo de piedra", "donde": "Camino Cobrizo",
		"texto": "Va bajo tierra. Solo se ve el montoncito que avanza... hasta que el suelo tiembla.",
		"secreto": "Cuando sale, se queda fuera un momento, atontado por la luz.", "dibujo": ["res://arte/mundos/raiz/camino/topo.png", 6, 1, 0]},
	"cuervo": {"nombre": "Cuervo de óxido", "donde": "Senda de los Surcos",
		"texto": "Vuela en círculos, apunta y baja en picado por una raya violeta.",
		"secreto": "Después del picado se posa a picotear el suelo. Ese es tu momento.", "dibujo": ["res://arte/mundos/raiz/senda/cuervo.png", 6, 1, 1]},
	"murcielago": {"nombre": "Murciélago de eco", "donde": "Cañada del Eco",
		"texto": "Grita una onda que va y vuelve, como un eco. Hace daño a la ida y a la vuelta.",
		"secreto": "Si se traga su propio eco, se marea y cae al suelo. El Latido deshace la onda.", "dibujo": ["res://arte/mundos/raiz/canada/murcielago.png", 6, 1, 1]},
	"cangrejo": {"nombre": "Cangrejo de herrumbre", "donde": "Orilla de Juncos, La Travesía",
		"texto": "Anda de lado y su caparazón lo aguanta todo. Avisa levantando las pinzas.",
		"secreto": "Por detrás no tiene coraza.", "dibujo": ["res://arte/mundos/raiz/orilla/cangrejo.png", 6, 1, 0]},
	"anguila": {"nombre": "Anguila de óxido", "donde": "La Travesía",
		"texto": "Salta de un lado al otro de la barca. Una sombra marca por dónde va a pasar.",
		"secreto": "Un golpe en pleno salto la tumba en la cubierta, coleteando.", "dibujo": ["res://arte/mundos/raiz/travesia/anguila.png", 5, 1, 1]},
	"espino": {"nombre": "Espino de Giza", "donde": "Gruta de las Raíces",
		"texto": "Una mata de tallos de piedra que se hincha y escupe espinas.",
		"secreto": "El cetro rebota, pero una semilla lo deshace. El escudo para sus espinas.", "dibujo": ["res://arte/mundos/raiz/gruta/espino.png", 3, 1, 0]},
	"bundi": {"nombre": "Bundi, el búho-mago", "donde": "Bosque Cobrizo, Cañada del Eco",
		"texto": "Un hechicero de Giza. No se deja tocar: si te acercas, se esfuma en plumas. Lanza bolas que te persiguen.",
		"secreto": "Pon el escudo de frente y su bola vuelve contra él: se queda atontado y no puede irse.", "dibujo": ["res://arte/mundos/raiz/hechiceros/bundi.png", 6, 1, 0]},
	"buibui": {"nombre": "Buibui, la araña-bruja", "donde": "Camino Cobrizo, Gruta de las Raíces",
		"texto": "Lleva un nido a la espalda y de él salen bichos de óxido sin parar.",
		"secreto": "Una semilla le sella el nido con raíces: sin bichos, es solo una araña vieja.", "dibujo": ["res://arte/mundos/raiz/hechiceros/buibui.png", 4, 1, 0]},
	"mende": {"nombre": "Mende, bicho de óxido", "donde": "Donde haya una araña-bruja",
		"texto": "Un escarabajo de herrumbre que corretea en zigzag. Muere de un golpe, pero nunca viene solo.",
		"secreto": "Si vences a la bruja, no salen más.", "dibujo": ["res://arte/mundos/raiz/hechiceros/mende.png", 3, 1, 0], "rangos": [20, 60, 120]},
	"mzizi": {"nombre": "Mzizi, la raíz del Arco", "donde": "El Kitovu", "jefe": "zona/kitovu/7",
		"texto": "La raíz que alimentaba el Arco de Raíz. Giza la movía como a una serpiente.",
		"secreto": "Solo le hacen daño las semillas que estallan en su agujero.", "dibujo": ["res://arte/zonas/raiz/mzizi_cabeza.png", 12, 1, 0]},
	"pembe": {"nombre": "Pembe, el ciervo de hierro", "donde": "Bosque Cobrizo", "jefe": "zona/bosque_cobrizo/4",
		"texto": "El guardián del bosque, con las astas convertidas en hierro.",
		"secreto": "Embiste en línea recta: si choca con unos brotes, se atasca.", "dibujo": ["res://arte/zonas/raiz/pembe.png", 8, 1, 0]},
	"konokono": {"nombre": "Konokono, la caracola", "donde": "Ciénaga Quieta", "jefe": "zona/cienaga_quieta/4",
		"texto": "La caracola que guardaba el agua de la ciénaga, con la concha llena de herrumbre.",
		"secreto": "Se traga las semillas que encuentra... y le estallan dentro.", "dibujo": ["res://arte/zonas/raiz/konokono.png", 8, 1, 0]},
	"cosechadora": {"nombre": "La Cosechadora Oxidada", "donde": "Campo Segado", "jefe": "zona/campo_segado/3",
		"texto": "Una máquina de siega enorme que Giza despertó. Se rompe por partes.",
		"secreto": "Tiene tres puntos débiles y cada uno se abre de una forma distinta.", "dibujo": ["res://arte/zonas/raiz/cosechadora.png", 8, 1, 0]},
	"kambare": {"nombre": "Kambare, el siluro de cieno", "donde": "Lago Espejo", "jefe": "zona/lago_espejo/1",
		"texto": "Un pez gato enorme lleno de barro. Mientras vivía, el lago no se calmaba.",
		"secreto": "En su charca no se le puede dar: hay que hacerle salir.", "dibujo": ["res://arte/zonas/raiz/kambare.png", 7, 1, 0]},
	"mamba": {"nombre": "Mamba, el cocodrilo", "donde": "Embarcadero Junco", "jefe": "zona/embarcadero_junco/1",
		"texto": "Un cocodrilo viejo cubierto de placas de hierro. Flotaba como un tronco.",
		"secreto": "Bata lo sujeta con la pértiga: es el momento de darle.", "dibujo": ["res://arte/zonas/raiz/mamba.png", 7, 1, 0]},
	"kuvu": {"nombre": "Kuvu, la seta que manda", "donde": "Cueva de las setas", "jefe": "zona/cueva_setas/1",
		"texto": "Una seta enorme de Giza que, en vez de comerse lo que cae, manda. Tenía a Nungu colgado de un hilo.",
		"secreto": "Para la bola de Nungu con el escudo y córtale el hilo: luego él le abre el sombrero.", "dibujo": ["res://arte/zonas/raiz/kuvu.png", 7, 1, 0]},
	"guardian": {"nombre": "El Guardián de la Gruta", "donde": "Gruta de las Raíces", "jefe": "zona/gruta_raices/1",
		"texto": "Un ciervo viejo, mitad raíz, que dormía con una máscara de Giza. Se pelea contra su pesadilla.",
		"secreto": "Si esquivas su embestida, se estrella contra la pared y la máscara se tuerce.", "dibujo": ["res://arte/zonas/raiz/guardian.png", 6, 1, 0]},
}

var _jefe := ""
var _golpes_jefe := 0


func cuantos(tipo: String) -> int:
	var cuentas: Dictionary = Estado.extra.get("bestiario", {})
	return int(cuentas.get(tipo, 0))


func es_jefe(tipo: String) -> bool:
	return FICHAS.get(tipo, {}).has("jefe")


func umbrales(tipo: String) -> Array:
	return FICHAS.get(tipo, {}).get("rangos", RANGOS)


## 0 = sin rango, 1 bronce, 2 plata, 3 oro
func rango(tipo: String) -> int:
	for r in [3, 2, 1]:
		if Estado.tiene("rango/%s/%s" % [NOMBRE_RANGO[r], tipo]):
			return r
	if es_jefe(tipo) and Estado.tiene(String(FICHAS[tipo]["jefe"])):
		return 1
	return 0


## ¿Lo ha visto (vencido alguna vez)?
func conocido(tipo: String) -> bool:
	return cuantos(tipo) > 0 or rango(tipo) > 0


## Un enemigo vencido por Maisha (lo llama el enemigo al morir)
func vencido(tipo: String, nodo: Node = null) -> void:
	if nodo and nodo.has_meta("sin_contar"):
		return
	var cuentas: Dictionary = Estado.extra.get("bestiario", {})
	var n := int(cuentas.get(tipo, 0)) + 1
	cuentas[tipo] = n
	Estado.extra["bestiario"] = cuentas
	if es_jefe(tipo):
		return
	var u := umbrales(tipo)
	for r in [1, 2, 3]:
		if n >= int(u[r - 1]):
			_subir(tipo, r)


func _subir(tipo: String, r: int) -> void:
	if rango(tipo) >= r and Estado.tiene("rango/%s/%s" % [NOMBRE_RANGO[r], tipo]):
		return
	for k in range(1, r + 1):
		Estado.marcar("rango/%s/%s" % [NOMBRE_RANGO[k], tipo])
	rango_nuevo.emit(tipo, r)


# --- Los jefes ------------------------------------------------------------------

func empezar_jefe(tipo: String) -> void:
	_jefe = tipo
	_golpes_jefe = 0


func al_herir(_vida: int = 0) -> void:
	if _jefe != "":
		_golpes_jefe += 1


func jefe_vencido(tipo: String) -> void:
	vencido(tipo)
	var r := 1
	if _jefe == tipo:
		r = 3 if _golpes_jefe == 0 else (2 if _golpes_jefe <= 3 else 1)
	_jefe = ""
	if not Estado.tiene("rango/%s/%s" % [NOMBRE_RANGO[r], tipo]):
		_subir(tipo, r)
