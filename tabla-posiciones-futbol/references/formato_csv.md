# Formato del CSV de entrada

Esta referencia describe exactamente qué debe contener el archivo CSV de resultados.
Consúltala antes de preparar un archivo nuevo o cuando el script rechace una fila.

## Estructura general

- Archivo de texto plano con extensión **`.csv`**.
- Codificación **UTF-8** (se acepta UTF-8 con BOM, como el que exporta Excel).
- Separador: **coma** (`,`).
- **La primera fila es el encabezado** con los nombres de las columnas.
- Cada fila siguiente es **un partido ya jugado**. Las líneas en blanco se ignoran.

## Columnas obligatorias

Deben estar las cinco, con estos nombres exactos y sin columnas adicionales.
El orden de las columnas no importa; los nombres se comparan en minúsculas y sin espacios
sobrantes.

| Columna | Tipo | Regla |
|---|---|---|
| `fecha` | Texto `AAAA-MM-DD` | Fecha real del calendario. `2026-13-01` es inválida |
| `local` | Texto | Nombre del equipo local, no puede estar vacío |
| `visitante` | Texto | Nombre del equipo visitante, no puede estar vacío ni ser igual al local |
| `goles_local` | Entero | Mayor o igual a 0. Sin decimales ni texto |
| `goles_visitante` | Entero | Mayor o igual a 0. Sin decimales ni texto |

### Detalles importantes

- Los nombres de equipo se usan **tal cual** como identificador. `Bolívar` y `bolivar` se
  tratarían como dos equipos distintos, así que hay que escribirlos de forma consistente.
  La única excepción es la comprobación de "equipo contra sí mismo", que sí ignora
  mayúsculas y minúsculas.
- Los espacios al principio y al final de cada valor se eliminan automáticamente.
- Si un nombre de equipo contiene una coma, debe ir entre comillas dobles:
  `2026-09-01,"Club Bolívar, S.A.",Blooming,2,1`.
- No hace falta que la liga esté completa: la tabla se calcula con los partidos que haya.

## Ejemplo válido

```csv
fecha,local,visitante,goles_local,goles_visitante
2026-09-01,Bolívar,The Strongest,2,1
2026-09-01,Always Ready,Wilstermann,2,0
2026-09-08,Oriente Petrolero,The Strongest,4,0
2026-09-08,Blooming,Wilstermann,1,1
```

El archivo `assets/ejemplo_liga.csv` es un ejemplo válido completo con 6 equipos y 15 partidos.

## Ejemplos inválidos

Cada caso muestra la fila problemática y el mensaje que devuelve el script.
En `tests/datos/` hay un archivo CSV por cada uno de estos casos.

### Falta una columna

```csv
fecha,local,visitante,goles_local
2026-09-01,Bolívar,The Strongest,2
```
> `ERROR: Faltan columnas obligatorias en el CSV: goles_visitante. Se esperaban exactamente: fecha, local, visitante, goles_local, goles_visitante.`

### Columna con nombre incorrecto

```csv
fecha,equipo_local,visitante,goles_local,goles_visitante
```
> `ERROR: Faltan columnas obligatorias en el CSV: local. Se esperaban exactamente: fecha, local, visitante, goles_local, goles_visitante.`

Al escribir `equipo_local` en lugar de `local`, la columna `local` pasa a faltar. El script
revisa primero las columnas faltantes, así que ese es el mensaje que verás; una vez
corregido, si sobrara alguna columna extra, aparecería el mensaje
`El CSV tiene columnas no reconocidas: ...`.

### Goles no numéricos

```csv
2026-09-01,Bolívar,The Strongest,dos,1
```
> `ERROR: Fila 2: los goles del equipo local deben ser un número entero, se encontró 'dos'.`

### Goles negativos

```csv
2026-09-01,Bolívar,The Strongest,-2,1
```
> `ERROR: Fila 2: los goles del equipo local no pueden ser negativos, se encontró '-2'.`

### Equipo jugando contra sí mismo

```csv
2026-09-01,Bolívar,Bolívar,2,1
```
> `ERROR: Fila 2: el equipo 'Bolívar' no puede jugar contra sí mismo.`

### Fecha inválida

```csv
01/09/2026,Bolívar,The Strongest,2,1
```
> `ERROR: Fila 2: la fecha '01/09/2026' no tiene el formato válido AAAA-MM-DD (ejemplo: 2026-09-01).`

### Nombre de equipo vacío

```csv
2026-09-01,,The Strongest,2,1
```
> `ERROR: Fila 2: el nombre del equipo local está vacío.`

### Archivo sin partidos

Un archivo que solo tiene el encabezado:
> `ERROR: El archivo 'X.csv' no contiene ningún partido (solo encabezados).`

### Archivo completamente vacío

> `ERROR: El archivo CSV está vacío: no tiene fila de encabezados.`

## Cómo se numeran las filas en los errores

El número que aparece en el mensaje es el **número de línea del archivo**, contando el
encabezado como línea 1. Así, el primer partido es la fila 2, y ese número coincide con el
que muestra Excel o cualquier editor de texto.
