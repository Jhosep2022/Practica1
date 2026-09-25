---
name: tabla-posiciones-futbol
description: Genera tablas de posiciones y reportes HTML de ligas de fútbol a partir de un archivo CSV de resultados de partidos, calculando PJ, PG, PE, PP, GF, GC, DG y puntos, aplicando los criterios de desempate y produciendo estadísticas del torneo. Úsala cuando el usuario tenga resultados de partidos (en CSV o que puedan pasarse a CSV) y quiera la clasificación de la liga, el reporte del torneo o estadísticas como el equipo más goleador, la mejor defensa o el promedio de goles.
---

# Tabla de posiciones de fútbol

Convierte un CSV de resultados de partidos en una tabla de posiciones ordenada y un reporte
HTML con estadísticas del torneo.

## Cuándo usar esta skill

Úsala cuando el usuario:

- tenga un archivo CSV con resultados de partidos y pida la tabla o clasificación;
- pegue resultados en el chat y quiera saber quién va primero o cómo queda la liga;
- pida estadísticas de un torneo: equipo más goleador, mejor defensa, promedio de goles;
- pida un reporte o informe en HTML de una liga.

No la uses para predecir resultados, para calcular fixtures o para ligas con sistemas de
puntuación que no sean 3-1-0, salvo que se ajusten las constantes del script.

## Flujo paso a paso

### 1. Conseguir el CSV de entrada

El script necesita un archivo `.csv` con las columnas `fecha`, `local`, `visitante`,
`goles_local`, `goles_visitante`.

- Si el usuario **ya tiene el archivo**, usa su ruta directamente.
- Si el usuario **pegó los resultados en el chat**, crea el CSV a partir de ellos. Antes de
  escribirlo, lee `references/formato_csv.md` para respetar el formato exacto (tipos,
  formato de fecha, comillas cuando un nombre contiene comas).
- Si el usuario **solo quiere ver una demostración**, usa `assets/ejemplo_liga.csv`, que
  contiene una liga de 6 equipos con 15 partidos e incluye a propósito un empate que se
  resuelve por enfrentamiento directo.

### 2. Ejecutar el script

```bash
python scripts/generar_tabla.py <archivo.csv> [--salida reporte.html]
```

Ejemplo con la liga de ejemplo:

```bash
python scripts/generar_tabla.py assets/ejemplo_liga.csv --salida reporte.html
```

El script hace todo el trabajo en un solo paso: valida el CSV, calcula la tabla, la ordena
aplicando los desempates, rellena la plantilla y escribe el HTML. Solo usa la librería
estándar de Python 3.8 o superior, así que no hay nada que instalar.

### 3. Interpretar la salida

El script imprime en la terminal la tabla completa y las estadísticas destacadas, y escribe
el reporte HTML en la ruta indicada por `--salida` (por defecto `reporte.html`).

Muestra al usuario el resumen de la terminal y dile dónde quedó el HTML. Si el usuario
pregunta por qué un equipo está por encima de otro cuando tienen los mismos puntos, lee
`references/reglas_puntuacion.md` y explícale qué criterio de desempate decidió el orden.

### 4. Manejar los errores

Si el CSV tiene problemas, el script no muestra un traceback: imprime un único mensaje en
español que empieza con `ERROR:` y termina con código de salida 1. Cuando el problema está
en una fila concreta, el mensaje incluye el número de línea del archivo.

Lee ese mensaje, corrige el CSV (o pide al usuario el dato que falta) y vuelve a ejecutar.
`references/formato_csv.md` lista cada error posible con un ejemplo de la fila que lo
provoca, así que consúltalo para saber cómo arreglarlo.

## Archivos de la skill

| Archivo | Cuándo usarlo |
|---|---|
| `scripts/generar_tabla.py` | Siempre. Es el único ejecutable: hace validación, cálculo, ordenamiento y HTML |
| `assets/plantilla_reporte.html` | El script la lee solo. Edítala si el usuario quiere cambiar el diseño del reporte |
| `assets/ejemplo_liga.csv` | Para demostrar la skill o probar que todo funciona sin datos del usuario |
| `references/reglas_puntuacion.md` | Cuando haya dudas sobre el orden de la tabla o los criterios de desempate |
| `references/formato_csv.md` | Antes de crear un CSV nuevo, y al interpretar un mensaje de error de validación |
| `README.md` | Documentación para personas: instalación, ejemplo completo y catálogo de errores |
| `tests/` | Para verificar la skill tras modificarla: `python -m unittest discover tests` |

## Reglas de cálculo (resumen)

Victoria 3 puntos, empate 1, derrota 0. La tabla se ordena por: **1)** puntos,
**2)** diferencia de gol, **3)** goles a favor, **4)** enfrentamiento directo entre los
equipos empatados, **5)** orden alfabético.

El detalle completo, incluido cómo se construye la mini-tabla de enfrentamientos directos
cuando hay tres o más equipos empatados, está en `references/reglas_puntuacion.md`.
