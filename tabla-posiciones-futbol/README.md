# tabla-posiciones-futbol

Skill de Claude que convierte un archivo CSV con resultados de partidos en la **tabla de
posiciones** de una liga de fútbol y en un **reporte HTML** con estadísticas del torneo.

## Qué hace

A partir de un CSV con los resultados ya jugados, la skill:

1. **Valida** el archivo: que exista, que sea un CSV, que tenga las columnas correctas y que
   cada fila tenga datos coherentes.
2. **Calcula** para cada equipo: PJ (partidos jugados), PG (ganados), PE (empatados),
   PP (perdidos), GF (goles a favor), GC (goles en contra), DG (diferencia de gol) y Pts.
3. **Ordena** la tabla aplicando los criterios de desempate.
4. **Genera** un archivo HTML con la clasificación y las estadísticas destacadas.
5. **Muestra** un resumen de la tabla en la terminal.

Puntuación: victoria 3 puntos, empate 1, derrota 0.

Criterios de desempate, en este orden: **1)** puntos, **2)** diferencia de gol,
**3)** goles a favor, **4)** enfrentamiento directo entre los equipos empatados,
**5)** orden alfabético.

## Cuándo usarla

Úsala cuando tengas resultados de partidos y quieras la clasificación de la liga o las
estadísticas del torneo: quién va primero, qué equipo es el más goleador, cuál tiene la mejor
defensa, cuántos goles se marcan en promedio.

No sirve para predecir resultados ni para armar el calendario de una liga.

## Requisitos

- **Python 3.8 o superior.** Nada más.
- **No necesita instalar dependencias:** el script usa solo la librería estándar
  (`csv`, `argparse`, `html`, `pathlib`, `datetime`, `sys`, `unittest`).

Para comprobar tu versión de Python:

```bash
python --version
```

## Instalación

### Opción A: usarla como skill en Claude

Copia la carpeta completa `tabla-posiciones-futbol/` dentro del directorio de skills de
Claude Code:

- **Para un solo proyecto:** `<tu-proyecto>/.claude/skills/tabla-posiciones-futbol/`
- **Para todos tus proyectos:** `~/.claude/skills/tabla-posiciones-futbol/`
  (en Windows: `C:\Users\<tu-usuario>\.claude\skills\tabla-posiciones-futbol\`)

Pasos concretos, desde la raíz de este repositorio:

```bash
mkdir -p ~/.claude/skills
cp -r tabla-posiciones-futbol ~/.claude/skills/
```

En Windows con PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills"
Copy-Item -Recurse tabla-posiciones-futbol "$HOME\.claude\skills\"
```

Reinicia Claude Code. A partir de ahí, la skill se activa sola cuando le pidas algo como
*"tengo los resultados de la liga en este CSV, arma la tabla de posiciones"*.

La estructura que debe quedar es exactamente la de este repositorio: el archivo `SKILL.md`
tiene que estar en la raíz de la carpeta, junto a `scripts/`, `assets/` y `references/`.

### Opción B: ejecutar el script directamente desde la terminal

No hace falta instalar nada. Basta con entrar a la carpeta de la skill y ejecutar el script:

```bash
cd tabla-posiciones-futbol
python scripts/generar_tabla.py assets/ejemplo_liga.csv --salida reporte.html
```

Uso general:

```
python scripts/generar_tabla.py <archivo.csv> [--salida reporte.html]
```

| Argumento | Obligatorio | Descripción |
|---|---|---|
| `<archivo.csv>` | Sí | Ruta del CSV con los resultados |
| `--salida` | No | Ruta del HTML a generar. Por defecto `reporte.html` |

## Ejemplo completo

Con la liga de ejemplo incluida en `assets/ejemplo_liga.csv` (6 equipos, 15 partidos):

```bash
python scripts/generar_tabla.py assets/ejemplo_liga.csv --salida reporte.html
```

Salida real en la terminal:

```
TABLA DE POSICIONES
  #  Equipo              PJ  PG  PE  PP  GF  GC   DG  Pts
---------------------------------------------------------
  1  Bolívar              5   4   1   0   9   3   +6   13
  2  Wilstermann          5   2   2   1   6   6    0    8
  3  Oriente Petrolero    5   2   1   2   8   6   +2    7
  4  Always Ready         5   2   1   2   8   6   +2    7
  5  The Strongest        5   1   1   3   8  12   -4    4
  6  Blooming             5   0   2   3   4  10   -6    2

ESTADÍSTICAS DESTACADAS
  Equipo más goleador  : Bolívar (9 goles a favor)
  Mejor defensa        : Bolívar (3 goles en contra)
  Partido con más goles: The Strongest 4 - 2 Blooming (6 goles, 2026-09-29)
  Partidos jugados     : 15
  Promedio de goles    : 2.87 por partido

Reporte HTML generado en: reporte.html
```

Abre `reporte.html` en cualquier navegador para ver la versión con estilos.

### Fíjate en el 3.º y el 4.º puesto

Oriente Petrolero y Always Ready terminan **idénticos** en los tres primeros criterios:
7 puntos, +2 de diferencia de gol y 8 goles a favor. El orden lo decide el cuarto criterio,
el **enfrentamiento directo**: el 29 de septiembre Oriente Petrolero le ganó 2-1, así que
queda por encima. Si se hubiera usado el orden alfabético, Always Ready estaría tercero.

La liga de ejemplo fue diseñada a propósito para que ese caso ocurra y se pueda demostrar.

## Formato del CSV de entrada

```csv
fecha,local,visitante,goles_local,goles_visitante
2026-09-01,Bolívar,The Strongest,2,1
2026-09-01,Always Ready,Wilstermann,2,0
```

| Columna | Tipo | Regla |
|---|---|---|
| `fecha` | `AAAA-MM-DD` | Fecha real del calendario |
| `local` | Texto | No puede estar vacío |
| `visitante` | Texto | No puede estar vacío ni ser igual al local |
| `goles_local` | Entero | Mayor o igual a 0 |
| `goles_visitante` | Entero | Mayor o igual a 0 |

El archivo debe estar en UTF-8 y tener extensión `.csv`. La especificación completa, con más
ejemplos, está en [`references/formato_csv.md`](references/formato_csv.md).

## Estructura de archivos

```
tabla-posiciones-futbol/
├── SKILL.md                        Instrucciones que Claude lee para usar la skill
├── README.md                       Este archivo
├── scripts/
│   └── generar_tabla.py            Único ejecutable: valida, calcula, ordena y genera el HTML
├── assets/
│   ├── plantilla_reporte.html      Plantilla con los estilos que el script rellena
│   └── ejemplo_liga.csv            Liga de ejemplo: 6 equipos, 15 partidos, con desempate
├── references/
│   ├── reglas_puntuacion.md        Sistema de puntos y criterios de desempate explicados
│   └── formato_csv.md              Especificación del CSV, con ejemplos válidos e inválidos
└── tests/
    ├── test_generar_tabla.py       26 pruebas con unittest
    ├── datos/                      CSVs válidos e inválidos, uno por caso de error
    └── evidencia/                  Salidas guardadas de ejecuciones exitosas y con error
```

### Cómo está organizado el script

`scripts/generar_tabla.py` separa el trabajo en funciones, cada una con una sola
responsabilidad:

| Función | Qué hace |
|---|---|
| `validar_archivo()` | Comprueba que la ruta exista y sea un `.csv` |
| `validar_encabezados()` | Verifica que estén las cinco columnas y ninguna de más |
| `validar_fecha()`, `validar_equipo()`, `validar_goles()` | Validan un valor individual |
| `validar_fila()` | Valida una fila completa y detecta el equipo contra sí mismo |
| `leer_partidos()` | Abre el CSV y devuelve la lista de partidos ya validados |
| `calcular_tabla()` | Acumula PJ, PG, PE, PP, GF, GC, DG y Pts de cada equipo |
| `ordenar_tabla()` | Aplica los criterios 1, 2 y 3, y delega los empates restantes |
| `desempatar_grupo()`, `_mini_tabla_entre()` | Resuelven el enfrentamiento directo (criterio 4) |
| `calcular_estadisticas()` | Calcula las estadísticas destacadas del torneo |
| `generar_html()`, `escribir_html()` | Rellenan la plantilla y guardan el reporte |
| `formatear_resumen()`, `imprimir_resumen()` | Arman y muestran el resumen de la terminal |
| `main()` | Lee los argumentos y convierte cualquier error en un mensaje claro |

## Pruebas

Desde la carpeta de la skill:

```bash
python -m unittest discover tests
```

Resultado esperado:

```
..........................
----------------------------------------------------------------------
Ran 26 tests in 0.083s

OK
```

Las pruebas verifican el cálculo de puntos, cada criterio de desempate (incluido el
enfrentamiento directo), la generación del HTML y los doce casos de error. En
`tests/evidencia/` están guardadas las salidas de una ejecución exitosa y de cada caso
fallido, como respaldo.

## Manejo de errores

Cuando algo está mal, el script **no muestra un traceback de Python**. Imprime un único
mensaje en español que empieza con `ERROR:` y termina con **código de salida 1**. Cuando el
problema está en una fila concreta, el mensaje dice en qué línea del archivo está, contando
el encabezado como línea 1 (así el número coincide con el que ves en Excel).

| Situación | Mensaje |
|---|---|
| El archivo no existe | `ERROR: El archivo 'liga.csv' no existe.` |
| El archivo no es un CSV | `ERROR: El archivo 'notas.txt' no es un CSV (se esperaba la extensión .csv).` |
| El archivo está vacío | `ERROR: El archivo CSV está vacío: no tiene fila de encabezados.` |
| Solo tiene encabezados | `ERROR: El archivo 'liga.csv' no contiene ningún partido (solo encabezados).` |
| Falta una columna | `ERROR: Faltan columnas obligatorias en el CSV: goles_visitante. Se esperaban exactamente: fecha, local, visitante, goles_local, goles_visitante.` |
| Columna con nombre incorrecto | `ERROR: Faltan columnas obligatorias en el CSV: local. Se esperaban exactamente: fecha, local, visitante, goles_local, goles_visitante.` |
| Hay una columna de más | `ERROR: El CSV tiene columnas no reconocidas: arbitro. Se esperaban exactamente: fecha, local, visitante, goles_local, goles_visitante.` |
| Goles no numéricos | `ERROR: Fila 3: los goles del equipo local deben ser un número entero, se encontró 'dos'.` |
| Goles negativos | `ERROR: Fila 2: los goles del equipo local no pueden ser negativos, se encontró '-2'.` |
| Equipo contra sí mismo | `ERROR: Fila 3: el equipo 'Bolivar' no puede jugar contra sí mismo.` |
| Fecha mal formateada | `ERROR: Fila 2: la fecha '01/09/2026' no tiene el formato válido AAAA-MM-DD (ejemplo: 2026-09-01).` |
| Fecha que no existe | `ERROR: Fila 2: la fecha '2026-02-30' no tiene el formato válido AAAA-MM-DD (ejemplo: 2026-09-01).` |
| Nombre de equipo vacío | `ERROR: Fila 2: el nombre del equipo local está vacío.` |
| Falta la plantilla | `ERROR: No se encontró la plantilla 'assets/plantilla_reporte.html'. Verifica que la carpeta assets/ esté completa.` |

Si hay un error, **no se genera ningún archivo HTML a medias**: el script se detiene antes de
escribir nada.

Para comprobar el código de salida después de ejecutar:

```bash
python scripts/generar_tabla.py tests/datos/invalido_goles_negativos.csv
echo $?      # imprime 1
```

En PowerShell:

```powershell
python scripts/generar_tabla.py tests/datos/invalido_goles_negativos.csv
$LASTEXITCODE   # imprime 1
```

## Personalización

- **Cambiar el diseño del reporte:** edita `assets/plantilla_reporte.html`. Los marcadores
  `{{TITULO}}`, `{{ARCHIVO_ORIGEN}}`, `{{FECHA_GENERACION}}`, `{{FILAS_TABLA}}` y
  `{{TARJETAS}}` son los que rellena el script; el resto del HTML y el CSS son libres.
- **Cambiar el sistema de puntos:** modifica las constantes `PUNTOS_VICTORIA`,
  `PUNTOS_EMPATE` y `PUNTOS_DERROTA` al inicio de `scripts/generar_tabla.py`.
- **Cambiar el orden de los desempates:** modifica `ordenar_tabla()` y actualiza
  `references/reglas_puntuacion.md` para que documentación y código coincidan.
