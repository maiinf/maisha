extends RefCounted
## EL ÍNDICE DE MAANDIKO: los doce nombres que la Tinta Quieta borró. Cada uno vuelve con su marca (casi todos,
## «<nombre>_nombre», al darle su ficha; el de Mwalimu, el Bibliotecario, al recoger la suya). Con los doce, el Gran
## Archivo abre la escalera a la Sección Prohibida (marca «indice_completo»).

const NOMBRES := ["taa_nombre", "daftari_nombre", "ficha/mwalimu", "mfereji_nombre", "karatasi_nombre", "chapa_nombre",
	"nyota_nombre", "darubini_nombre", "mlinzi_nombre", "kurasa_nombre", "muhuri_nombre", "wimbo_nombre"]


static func cuantos() -> int:
	var n := 0
	for marca in NOMBRES:
		if Estado.tiene(marca):
			n += 1
	return n


static func completo() -> bool:
	return cuantos() == NOMBRES.size()
