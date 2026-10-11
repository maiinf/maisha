# Guía de instalación (Mac) — Maisha

Pensada para tu **MacBook Pro 13" (2019, Intel, macOS Sequoia)**.
Sigue los pasos en orden. Cada uno termina con una **comprobación**: si se cumple, pasa al siguiente.
Todo es gratuito.

> **Atajos del Mac que usaremos:** `⌘` = tecla Comando · `⌥` = Opción · `⇧` = Mayúsculas.

---

## Paso 1. Crear la carpeta del proyecto (fuera de iCloud)

1. Abre el **Finder**.
2. Pulsa `⌘ + ⇧ + H` para ir a tu **carpeta de inicio** (la que tiene una casita y tu nombre).
3. Crea una carpeta nueva (`⌘ + ⇧ + N`) llamada **`Proyectos`**.

> ¿Por qué no en Escritorio o Documentos? Si tienes activada la sincronización de iCloud, esas carpetas se suben a iCloud, e iCloud y Git se pelean por los mismos archivos. La carpeta de inicio no se sincroniza, así que es el sitio seguro.

✅ **Comprobación:** en el Finder ves `Proyectos` dentro de tu carpeta de inicio.

---

## Paso 2. Instalar Godot

1. Entra en **https://godotengine.org/download** y elige **macOS**.
2. Descarga la versión **Godot Engine** normal (serie 4.6 o la más reciente). **No** la que pone **.NET**.
   La descarga sirve tanto para Mac Intel como para Apple Silicon.
3. Abre el `.zip` descargado (se descomprime solo) y **arrastra `Godot.app` a la carpeta Aplicaciones**.
4. Ábrelo desde Aplicaciones o con Spotlight (`⌘ + espacio` y escribe «Godot»).

Si macOS dice que no puede abrirlo porque no ha podido verificar al desarrollador:
abre **Ajustes del Sistema → Privacidad y seguridad**, baja hasta el aviso sobre Godot y pulsa **Abrir igualmente**.

✅ **Comprobación:** se abre el **Administrador de proyectos** de Godot (una ventana con la lista de proyectos, vacía).

---

## Paso 3. Instalar Pixelorama y cargar la paleta de Raíz

1. Descarga Pixelorama para **macOS** desde su página oficial (**https://pixelorama.org**) o desde itch.io. Es gratis.
2. Abre el archivo descargado y **arrastra Pixelorama a Aplicaciones**.
3. Ábrelo. Si macOS lo bloquea, haz lo mismo que con Godot: **Ajustes del Sistema → Privacidad y seguridad → Abrir igualmente**.
4. Crea un lienzo nuevo de **24×32 píxeles** (el tamaño de Maisha).
5. Activa la cuadrícula de píxeles en el menú **Ver** (para ver cada píxel separado).
6. Carga la paleta: en el panel de **Paletas**, abre su menú y elige **Importar paleta**. Selecciona `arte/paletas/raiz.gpl` (está dentro del proyecto; lo tendrás en el paso 5, así que puedes volver a este punto después).

> **Consejo para dibujar en el Mac:** con el trackpad se dibuja bien, pero un ratón sencillo da más precisión píxel a píxel. Si tienes uno por casa, úsalo.
> Los nombres exactos de los menús pueden cambiar un poco según la versión. Si no encuentras algo, mándame una captura (`⌘ + ⇧ + 4`) y te guío.

✅ **Comprobación:** ves un lienzo pequeño con cuadrícula y, en el panel de paletas, los **57 colores** de Raíz.

---

## Paso 4. Crear la cuenta de GitHub e instalar GitHub Desktop

1. Crea una cuenta gratuita en **https://github.com**.
2. Descarga **GitHub Desktop para macOS** desde **https://desktop.github.com**.
3. Abre el `.zip` y **arrastra GitHub Desktop a Aplicaciones**. Ábrelo.
4. Inicia sesión con tu cuenta (**Sign in to GitHub.com**). Se abrirá el navegador para autorizarlo; acepta y vuelve a la app.

✅ **Comprobación:** GitHub Desktop muestra tu nombre de usuario.

---

## Paso 5. Poner el proyecto en su sitio y subirlo a GitHub

1. Haz doble clic en `maisha_base.zip` (se descomprime en Descargas) y **mueve la carpeta `maisha`** a tu carpeta `Proyectos`.
   Debe quedar así: `Proyectos/maisha/project.godot`.
2. En GitHub Desktop: **File → Add Local Repository…** y elige la carpeta `Proyectos/maisha`.
3. Te dirá que esa carpeta aún no es un repositorio: pulsa **create a repository**.
   - **Name:** `maisha`
   - **Git Ignore:** None (el proyecto ya trae el suyo)
   - Pulsa **Create Repository**.
4. Abajo a la izquierda, en **Summary**, escribe `Estructura inicial del proyecto` y pulsa **Commit to main**.
5. Arriba, pulsa **Publish repository**. **Deja marcada la casilla «Keep this code private»** y confirma.

> Un *commit* es una «foto» del proyecto que puedes recuperar siempre. *Push* (o *Publish*) la sube a GitHub.
> Si el Mac te pide instalar las «herramientas de línea de comandos» de Apple, acepta: son gratuitas y Git las necesita.

✅ **Comprobación:** en https://github.com aparece tu repositorio `maisha` con un candado (privado).

---

## Paso 6. Abrir el proyecto en Godot

1. En el Administrador de proyectos de Godot pulsa **Importar**.
2. Elige `Proyectos/maisha/project.godot` y pulsa **Importar y editar**.
3. Si Godot pregunta por convertir o actualizar el proyecto a tu versión, acepta.
4. Para jugar, pulsa **`⌘ + B`** o el triángulo **▶** de arriba a la derecha.
   (En Windows sería F5; en Mac el atajo es `⌘ + B`.)

✅ **Comprobación:** se abre una ventana oscura con el título **«MAISHA - proyecto base»**, la paleta de Raíz (57 cuadritos de color) y un círculo dorado que late. Los cuadritos se ven nítidos, sin bordes borrosos.

---

## Paso 7. El portátil Windows (opcional)

Puedes seguir trabajando solo en el Mac. Si algún día quieres usar el portátil Windows (por ejemplo, para generar imágenes con IA en local con su tarjeta NVIDIA), instala GitHub Desktop allí, inicia sesión con la misma cuenta y usa **File → Clone repository** para descargar el proyecto. La rutina de abajo mantiene los dos ordenadores sincronizados.

---

## Rutina de trabajo con Git (lo único que tienes que recordar)

| Cuándo | Qué hacer en GitHub Desktop |
| --- | --- |
| **Al empezar a trabajar** | Pulsa **Fetch origin** y, si aparece, **Pull origin**. Así traes lo último. |
| **Al terminar algo que funciona** | Escribe un resumen (ej.: «Maisha: animación de andar hacia abajo») y pulsa **Commit to main**. |
| **Al acabar la sesión** | Pulsa **Push origin** para subirlo a GitHub. |

**Regla de oro:** si usas los dos ordenadores, no trabajes en el mismo archivo en ambos a la vez sin haber hecho *Push* en uno y *Pull* en el otro.

## Copia de seguridad mensual

El primer día de cada mes: conecta un USB o disco externo, copia la carpeta `Proyectos/maisha` entera y renómbrala con la fecha, por ejemplo `maisha_2026-11-01`.
(Si tienes un disco externo libre, **Time Machine** del Mac también sirve y lo hace solo.)
