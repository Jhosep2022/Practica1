# Reglas de puntuación y criterios de desempate

Esta referencia define cómo se calculan los puntos y en qué orden se resuelven los empates.
Consúltala cuando tengas dudas sobre por qué un equipo aparece por encima de otro en la tabla.

## Sistema de puntos

| Resultado | Puntos |
|---|---|
| Victoria | 3 |
| Empate | 1 |
| Derrota | 0 |

Estas constantes están en `scripts/generar_tabla.py` como `PUNTOS_VICTORIA`, `PUNTOS_EMPATE`
y `PUNTOS_DERROTA`. Si una liga usa otro sistema, se cambian ahí y todo el cálculo se ajusta.

## Columnas de la tabla

| Sigla | Significado | Cómo se calcula |
|---|---|---|
| PJ | Partidos jugados | Cada partido en que el equipo aparece como local o visitante |
| PG | Partidos ganados | Marcó más goles que el rival |
| PE | Partidos empatados | Mismo número de goles |
| PP | Partidos perdidos | Marcó menos goles que el rival |
| GF | Goles a favor | Suma de goles marcados |
| GC | Goles en contra | Suma de goles recibidos |
| DG | Diferencia de gol | `GF - GC` |
| Pts | Puntos | `PG × 3 + PE × 1` |

## Criterios de desempate, en orden estricto

Cuando dos o más equipos tienen los mismos puntos, se aplican estos criterios uno tras otro.
Se detiene en el primero que separe a los equipos.

1. **Puntos** (mayor primero).
2. **Diferencia de gol** (mayor primero).
3. **Goles a favor** (mayor primero).
4. **Enfrentamiento directo** entre los equipos aún empatados.
5. **Orden alfabético** del nombre del equipo, sin distinguir mayúsculas.

### Cómo funciona el enfrentamiento directo (criterio 4)

No se mira solo un partido: se arma una **mini-tabla** que incluye únicamente los partidos
jugados **entre los equipos que siguen empatados**, ignorando todos los demás. Esa mini-tabla
se ordena por sus propios puntos, luego su diferencia de gol y luego sus goles a favor.

Esto permite resolver correctamente empates de tres o más equipos, donde un solo partido no
alcanza. Si un equipo del grupo no jugó contra los otros, entra en la mini-tabla con todo en
cero y queda por debajo de quienes sí sumaron.

En el código, esto está en las funciones `_mini_tabla_entre()` y `desempatar_grupo()`.

### Ejemplo real con `assets/ejemplo_liga.csv`

Always Ready y Oriente Petrolero terminan **idénticos** en los tres primeros criterios:

| Equipo | Pts | DG | GF |
|---|---|---|---|
| Always Ready | 7 | +2 | 8 |
| Oriente Petrolero | 7 | +2 | 8 |

Los criterios 1, 2 y 3 no los separan. Se aplica el criterio 4: el único partido entre ellos
fue `2026-09-29, Always Ready 1 - 2 Oriente Petrolero`, así que en la mini-tabla Oriente
Petrolero suma 3 puntos y Always Ready 0.

**Resultado: Oriente Petrolero queda 3.º y Always Ready 4.º.** Nótese que el criterio 5
(alfabético) habría puesto a Always Ready primero, por lo que este caso demuestra que el
enfrentamiento directo realmente se está aplicando.

## Nota sobre el orden de los criterios

Este orden es el que se pidió para esta skill. Otras competencias usan variantes: la CONMEBOL
suele poner el enfrentamiento directo antes que la diferencia de gol, y la Premier League
recurre a un partido de desempate. Si la liga que estás procesando usa otro orden, hay que
modificar `ordenar_tabla()` y actualizar esta referencia para que ambos coincidan.
