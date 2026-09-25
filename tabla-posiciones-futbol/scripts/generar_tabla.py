#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera la tabla de posiciones y un reporte HTML a partir de un CSV de resultados.

Uso desde la terminal:
    python scripts/generar_tabla.py <archivo.csv> [--salida reporte.html]

Solo usa la libreria estandar de Python (csv, argparse, html, pathlib, datetime).
Las reglas de puntuacion y desempate estan documentadas en
references/reglas_puntuacion.md y el formato de entrada en references/formato_csv.md.
"""

import argparse
import csv
import html
import sys
from datetime import date, datetime
from pathlib import Path

# Columnas que el CSV de entrada debe tener, exactamente con estos nombres.
COLUMNAS_REQUERIDAS = ["fecha", "local", "visitante", "goles_local", "goles_visitante"]

# Puntos por resultado (ver references/reglas_puntuacion.md).
PUNTOS_VICTORIA = 3
PUNTOS_EMPATE = 1
PUNTOS_DERROTA = 0

# La plantilla vive en assets/, al lado de la carpeta scripts/.
CARPETA_SKILL = Path(__file__).resolve().parent.parent
RUTA_PLANTILLA = CARPETA_SKILL / "assets" / "plantilla_reporte.html"


class ErrorDatos(Exception):
    """Error de datos de entrada que se muestra al usuario sin traceback."""


# ---------------------------------------------------------------------------
# 1. Lectura y validacion
# ---------------------------------------------------------------------------

def validar_archivo(ruta_texto):
    """Comprueba que la ruta exista, sea un archivo y tenga extension .csv."""
    ruta = Path(ruta_texto)
    if not ruta.exists():
        raise ErrorDatos("El archivo '{}' no existe.".format(ruta))
    if not ruta.is_file():
        raise ErrorDatos("La ruta '{}' no es un archivo.".format(ruta))
    if ruta.suffix.lower() != ".csv":
        raise ErrorDatos(
            "El archivo '{}' no es un CSV (se esperaba la extensión .csv).".format(ruta)
        )
    return ruta


def validar_encabezados(encabezados):
    """Verifica que el CSV traiga exactamente las columnas requeridas."""
    if not encabezados:
        raise ErrorDatos("El archivo CSV está vacío: no tiene fila de encabezados.")

    # Se limpian espacios y BOM para que un CSV exportado de Excel siga siendo valido.
    limpios = [(columna or "").strip().lstrip("\ufeff").lower() for columna in encabezados]

    faltantes = [columna for columna in COLUMNAS_REQUERIDAS if columna not in limpios]
    if faltantes:
        raise ErrorDatos(
            "Faltan columnas obligatorias en el CSV: {}. "
            "Se esperaban exactamente: {}.".format(
                ", ".join(faltantes), ", ".join(COLUMNAS_REQUERIDAS)
            )
        )

    sobrantes = [columna for columna in limpios if columna not in COLUMNAS_REQUERIDAS]
    if sobrantes:
        raise ErrorDatos(
            "El CSV tiene columnas no reconocidas: {}. "
            "Se esperaban exactamente: {}.".format(
                ", ".join(sobrantes), ", ".join(COLUMNAS_REQUERIDAS)
            )
        )

    return limpios


def validar_fecha(valor, numero_fila):
    """Valida que la fecha tenga el formato AAAA-MM-DD y sea una fecha real."""
    texto = (valor or "").strip()
    if not texto:
        raise ErrorDatos("Fila {}: la fecha está vacía.".format(numero_fila))
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except ValueError:
        raise ErrorDatos(
            "Fila {}: la fecha '{}' no tiene el formato válido AAAA-MM-DD "
            "(ejemplo: 2026-09-01).".format(numero_fila, texto)
        )


def validar_equipo(valor, numero_fila, etiqueta):
    """Valida que el nombre de un equipo no este vacio."""
    nombre = (valor or "").strip()
    if not nombre:
        raise ErrorDatos(
            "Fila {}: el nombre del equipo {} está vacío.".format(numero_fila, etiqueta)
        )
    return nombre


def validar_goles(valor, numero_fila, etiqueta):
    """Valida que los goles sean un entero mayor o igual a cero."""
    texto = (valor or "").strip()
    if not texto:
        raise ErrorDatos(
            "Fila {}: los goles del {} están vacíos.".format(numero_fila, etiqueta)
        )
    try:
        goles = int(texto)
    except ValueError:
        raise ErrorDatos(
            "Fila {}: los goles del {} deben ser un número entero, "
            "se encontró '{}'.".format(numero_fila, etiqueta, texto)
        )
    if goles < 0:
        raise ErrorDatos(
            "Fila {}: los goles del {} no pueden ser negativos, "
            "se encontró '{}'.".format(numero_fila, etiqueta, goles)
        )
    return goles


def validar_fila(fila, numero_fila):
    """Valida una fila completa del CSV y devuelve un partido normalizado."""
    partido = {
        "fecha": validar_fecha(fila.get("fecha"), numero_fila),
        "local": validar_equipo(fila.get("local"), numero_fila, "local"),
        "visitante": validar_equipo(fila.get("visitante"), numero_fila, "visitante"),
        "goles_local": validar_goles(fila.get("goles_local"), numero_fila, "equipo local"),
        "goles_visitante": validar_goles(
            fila.get("goles_visitante"), numero_fila, "equipo visitante"
        ),
    }

    if partido["local"].casefold() == partido["visitante"].casefold():
        raise ErrorDatos(
            "Fila {}: el equipo '{}' no puede jugar contra sí mismo.".format(
                numero_fila, partido["local"]
            )
        )

    return partido


def leer_partidos(ruta_texto):
    """Lee el CSV, valida cada fila y devuelve la lista de partidos."""
    ruta = validar_archivo(ruta_texto)

    try:
        # newline="" es lo que recomienda el modulo csv para no romper saltos de linea.
        with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo)
            validar_encabezados(lector.fieldnames)

            partidos = []
            # La fila 1 del archivo es el encabezado, por eso se empieza a contar en 2.
            for numero_fila, fila in enumerate(lector, start=2):
                # csv.DictReader entrega filas vacias cuando hay lineas en blanco.
                if all((valor or "").strip() == "" for valor in fila.values()):
                    continue
                partidos.append(validar_fila(fila, numero_fila))
    except UnicodeDecodeError:
        raise ErrorDatos(
            "El archivo '{}' no se pudo leer como texto UTF-8. "
            "Guárdalo nuevamente con codificación UTF-8.".format(ruta)
        )
    except OSError as error:
        raise ErrorDatos("No se pudo abrir el archivo '{}': {}".format(ruta, error))

    if not partidos:
        raise ErrorDatos(
            "El archivo '{}' no contiene ningún partido (solo encabezados).".format(ruta)
        )

    return partidos


# ---------------------------------------------------------------------------
# 2. Calculo de la tabla
# ---------------------------------------------------------------------------

def _equipo_vacio(nombre):
    """Crea el registro inicial de estadisticas de un equipo."""
    return {
        "equipo": nombre,
        "pj": 0, "pg": 0, "pe": 0, "pp": 0,
        "gf": 0, "gc": 0, "dg": 0, "pts": 0,
    }


def calcular_tabla(partidos):
    """Acumula PJ, PG, PE, PP, GF, GC, DG y Pts de cada equipo."""
    tabla = {}

    for partido in partidos:
        local = partido["local"]
        visitante = partido["visitante"]
        goles_local = partido["goles_local"]
        goles_visitante = partido["goles_visitante"]

        for nombre in (local, visitante):
            if nombre not in tabla:
                tabla[nombre] = _equipo_vacio(nombre)

        tabla[local]["pj"] += 1
        tabla[visitante]["pj"] += 1
        tabla[local]["gf"] += goles_local
        tabla[local]["gc"] += goles_visitante
        tabla[visitante]["gf"] += goles_visitante
        tabla[visitante]["gc"] += goles_local

        if goles_local > goles_visitante:
            tabla[local]["pg"] += 1
            tabla[local]["pts"] += PUNTOS_VICTORIA
            tabla[visitante]["pp"] += 1
            tabla[visitante]["pts"] += PUNTOS_DERROTA
        elif goles_local < goles_visitante:
            tabla[visitante]["pg"] += 1
            tabla[visitante]["pts"] += PUNTOS_VICTORIA
            tabla[local]["pp"] += 1
            tabla[local]["pts"] += PUNTOS_DERROTA
        else:
            tabla[local]["pe"] += 1
            tabla[visitante]["pe"] += 1
            tabla[local]["pts"] += PUNTOS_EMPATE
            tabla[visitante]["pts"] += PUNTOS_EMPATE

    for registro in tabla.values():
        registro["dg"] = registro["gf"] - registro["gc"]

    return tabla


# ---------------------------------------------------------------------------
# 3. Ordenamiento con criterios de desempate
# ---------------------------------------------------------------------------

def _clave_alfabetica(nombre):
    """Clave de orden alfabetico insensible a mayusculas."""
    return nombre.casefold()


def _mini_tabla_entre(equipos, partidos):
    """Calcula una tabla parcial usando solo los partidos entre los equipos dados."""
    involucrados = set(equipos)
    partidos_directos = [
        partido for partido in partidos
        if partido["local"] in involucrados and partido["visitante"] in involucrados
    ]
    mini = calcular_tabla(partidos_directos)

    # Un equipo que no jugo contra los demas del grupo igual necesita un registro.
    for nombre in equipos:
        mini.setdefault(nombre, _equipo_vacio(nombre))

    return mini


def desempatar_grupo(equipos, partidos):
    """Ordena un grupo empatado en Pts, DG y GF.

    Criterio 4: enfrentamiento directo (mini-tabla solo entre los empatados).
    Criterio 5: orden alfabetico.
    """
    if len(equipos) == 1:
        return list(equipos)

    mini = _mini_tabla_entre(equipos, partidos)
    return sorted(
        equipos,
        key=lambda nombre: (
            -mini[nombre]["pts"],
            -mini[nombre]["dg"],
            -mini[nombre]["gf"],
            _clave_alfabetica(nombre),
        ),
    )


def ordenar_tabla(tabla, partidos):
    """Devuelve la lista de equipos ordenada segun los cinco criterios.

    1) puntos, 2) diferencia de gol, 3) goles a favor,
    4) enfrentamiento directo, 5) orden alfabetico.
    """
    # Primer pase: los tres criterios numericos globales.
    nombres = sorted(
        tabla.keys(),
        key=lambda nombre: (
            -tabla[nombre]["pts"],
            -tabla[nombre]["dg"],
            -tabla[nombre]["gf"],
            _clave_alfabetica(nombre),
        ),
    )

    # Segundo pase: se reordena cada bloque que quedo identico en Pts, DG y GF.
    ordenados = []
    bloque = []
    clave_bloque = None

    for nombre in nombres:
        clave = (tabla[nombre]["pts"], tabla[nombre]["dg"], tabla[nombre]["gf"])
        if clave != clave_bloque:
            if bloque:
                ordenados.extend(desempatar_grupo(bloque, partidos))
            bloque = [nombre]
            clave_bloque = clave
        else:
            bloque.append(nombre)

    if bloque:
        ordenados.extend(desempatar_grupo(bloque, partidos))

    return [tabla[nombre] for nombre in ordenados]


# ---------------------------------------------------------------------------
# 4. Estadisticas destacadas
# ---------------------------------------------------------------------------

def calcular_estadisticas(partidos, clasificacion):
    """Calcula las estadisticas destacadas del torneo."""
    total_partidos = len(partidos)
    total_goles = sum(p["goles_local"] + p["goles_visitante"] for p in partidos)

    # max()/min() conservan el primer elemento ante empate, y la lista ya viene ordenada.
    mas_goleador = max(clasificacion, key=lambda e: e["gf"])
    mejor_defensa = min(clasificacion, key=lambda e: e["gc"])
    partido_top = max(partidos, key=lambda p: p["goles_local"] + p["goles_visitante"])
    goles_partido_top = partido_top["goles_local"] + partido_top["goles_visitante"]

    return {
        "total_partidos": total_partidos,
        "total_equipos": len(clasificacion),
        "total_goles": total_goles,
        "promedio_goles": total_goles / total_partidos if total_partidos else 0.0,
        "mas_goleador": mas_goleador,
        "mejor_defensa": mejor_defensa,
        "partido_top": partido_top,
        "goles_partido_top": goles_partido_top,
    }


# ---------------------------------------------------------------------------
# 5. Generacion del HTML
# ---------------------------------------------------------------------------

def _escapar(texto):
    """Escapa texto para insertarlo sin riesgo dentro del HTML."""
    return html.escape(str(texto))


def _formatear_dg(diferencia):
    """Muestra la diferencia de gol con signo explicito cuando es positiva."""
    return "+{}".format(diferencia) if diferencia > 0 else str(diferencia)


def _construir_filas(clasificacion):
    """Construye las filas <tr> de la tabla de posiciones."""
    filas = []
    for posicion, equipo in enumerate(clasificacion, start=1):
        filas.append(
            '      <tr>\n'
            '        <td class="pos">{pos}</td>\n'
            '        <td class="equipo">{equipo}</td>\n'
            '        <td>{pj}</td><td>{pg}</td><td>{pe}</td><td>{pp}</td>\n'
            '        <td>{gf}</td><td>{gc}</td><td>{dg}</td>\n'
            '        <td class="pts">{pts}</td>\n'
            '      </tr>'.format(
                pos=posicion,
                equipo=_escapar(equipo["equipo"]),
                pj=equipo["pj"], pg=equipo["pg"], pe=equipo["pe"], pp=equipo["pp"],
                gf=equipo["gf"], gc=equipo["gc"], dg=_formatear_dg(equipo["dg"]),
                pts=equipo["pts"],
            )
        )
    return "\n".join(filas)


def _construir_tarjetas(estadisticas):
    """Construye las tarjetas de estadisticas destacadas."""
    partido = estadisticas["partido_top"]
    resumen_partido = "{} {} - {} {}".format(
        _escapar(partido["local"]), partido["goles_local"],
        partido["goles_visitante"], _escapar(partido["visitante"]),
    )

    tarjetas = [
        ("Equipo más goleador",
         _escapar(estadisticas["mas_goleador"]["equipo"]),
         "{} goles a favor".format(estadisticas["mas_goleador"]["gf"])),
        ("Mejor defensa",
         _escapar(estadisticas["mejor_defensa"]["equipo"]),
         "{} goles en contra".format(estadisticas["mejor_defensa"]["gc"])),
        ("Partido con más goles",
         resumen_partido,
         "{} goles el {}".format(estadisticas["goles_partido_top"], partido["fecha"])),
        ("Partidos jugados",
         str(estadisticas["total_partidos"]),
         "{} equipos en el torneo".format(estadisticas["total_equipos"])),
        ("Promedio de goles",
         "{:.2f}".format(estadisticas["promedio_goles"]),
         "{} goles en total".format(estadisticas["total_goles"])),
    ]

    bloques = []
    for titulo, valor, detalle in tarjetas:
        bloques.append(
            '      <div class="tarjeta">\n'
            '        <p class="tarjeta-titulo">{}</p>\n'
            '        <p class="tarjeta-valor">{}</p>\n'
            '        <p class="tarjeta-detalle">{}</p>\n'
            '      </div>'.format(_escapar(titulo), valor, _escapar(detalle))
        )
    return "\n".join(bloques)


def cargar_plantilla(ruta_plantilla=RUTA_PLANTILLA):
    """Lee la plantilla HTML de assets/."""
    ruta = Path(ruta_plantilla)
    if not ruta.is_file():
        raise ErrorDatos(
            "No se encontró la plantilla '{}'. "
            "Verifica que la carpeta assets/ esté completa.".format(ruta)
        )
    return ruta.read_text(encoding="utf-8")


def generar_html(clasificacion, estadisticas, nombre_origen, ruta_plantilla=RUTA_PLANTILLA):
    """Rellena la plantilla de assets/ con la tabla y las estadisticas."""
    plantilla = cargar_plantilla(ruta_plantilla)

    reemplazos = {
        "{{TITULO}}": "Tabla de posiciones",
        "{{ARCHIVO_ORIGEN}}": _escapar(nombre_origen),
        "{{FECHA_GENERACION}}": date.today().isoformat(),
        "{{FILAS_TABLA}}": _construir_filas(clasificacion),
        "{{TARJETAS}}": _construir_tarjetas(estadisticas),
    }

    for marcador, valor in reemplazos.items():
        plantilla = plantilla.replace(marcador, valor)

    return plantilla


def escribir_html(contenido, ruta_salida):
    """Guarda el reporte HTML en disco."""
    ruta = Path(ruta_salida)
    try:
        if ruta.parent and not ruta.parent.exists():
            ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(contenido, encoding="utf-8")
    except OSError as error:
        raise ErrorDatos("No se pudo escribir el reporte en '{}': {}".format(ruta, error))
    return ruta


# ---------------------------------------------------------------------------
# 6. Resumen en terminal
# ---------------------------------------------------------------------------

def formatear_resumen(clasificacion, estadisticas):
    """Arma el resumen de texto que se muestra en la terminal."""
    ancho = max([len(e["equipo"]) for e in clasificacion] + [len("Equipo")])
    formato = "{:>3}  {:<" + str(ancho) + "}  {:>3} {:>3} {:>3} {:>3} {:>3} {:>3} {:>4} {:>4}"

    encabezado = formato.format(
        "#", "Equipo", "PJ", "PG", "PE", "PP", "GF", "GC", "DG", "Pts"
    )
    lineas = ["", "TABLA DE POSICIONES", encabezado, "-" * len(encabezado)]

    for posicion, equipo in enumerate(clasificacion, start=1):
        lineas.append(
            formato.format(
                posicion, equipo["equipo"], equipo["pj"], equipo["pg"], equipo["pe"],
                equipo["pp"], equipo["gf"], equipo["gc"],
                _formatear_dg(equipo["dg"]), equipo["pts"],
            )
        )

    partido = estadisticas["partido_top"]
    lineas.extend([
        "",
        "ESTADÍSTICAS DESTACADAS",
        "  Equipo más goleador  : {} ({} goles a favor)".format(
            estadisticas["mas_goleador"]["equipo"], estadisticas["mas_goleador"]["gf"]),
        "  Mejor defensa        : {} ({} goles en contra)".format(
            estadisticas["mejor_defensa"]["equipo"], estadisticas["mejor_defensa"]["gc"]),
        "  Partido con más goles: {} {} - {} {} ({} goles, {})".format(
            partido["local"], partido["goles_local"],
            partido["goles_visitante"], partido["visitante"],
            estadisticas["goles_partido_top"], partido["fecha"]),
        "  Partidos jugados     : {}".format(estadisticas["total_partidos"]),
        "  Promedio de goles    : {:.2f} por partido".format(estadisticas["promedio_goles"]),
        "",
    ])
    return "\n".join(lineas)


def imprimir_resumen(clasificacion, estadisticas):
    """Muestra el resumen de la tabla en la terminal."""
    print(formatear_resumen(clasificacion, estadisticas))


# ---------------------------------------------------------------------------
# 7. Punto de entrada
# ---------------------------------------------------------------------------

def construir_parser():
    """Define los argumentos de la linea de comandos."""
    parser = argparse.ArgumentParser(
        prog="generar_tabla.py",
        description=(
            "Calcula la tabla de posiciones de una liga de futbol a partir de un CSV "
            "de resultados y genera un reporte HTML."
        ),
    )
    parser.add_argument("csv", help="Ruta del archivo CSV con los resultados de los partidos.")
    parser.add_argument(
        "--salida",
        default="reporte.html",
        help="Ruta del archivo HTML a generar (por defecto: reporte.html).",
    )
    return parser


def procesar(ruta_csv, ruta_salida):
    """Ejecuta el flujo completo: CSV -> validacion -> calculo -> orden -> HTML."""
    partidos = leer_partidos(ruta_csv)
    tabla = calcular_tabla(partidos)
    clasificacion = ordenar_tabla(tabla, partidos)
    estadisticas = calcular_estadisticas(partidos, clasificacion)
    contenido = generar_html(clasificacion, estadisticas, Path(ruta_csv).name)
    ruta_generada = escribir_html(contenido, ruta_salida)
    return clasificacion, estadisticas, ruta_generada


def _forzar_utf8():
    """Evita que la consola de Windows rompa acentos como en 'Bolivar'."""
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError, OSError):
            pass  # Si la consola no lo permite, se continua sin cambiar nada.


def main(argv=None):
    """Punto de entrada: convierte cualquier ErrorDatos en un mensaje claro."""
    _forzar_utf8()
    argumentos = construir_parser().parse_args(argv)
    try:
        clasificacion, estadisticas, ruta_generada = procesar(
            argumentos.csv, argumentos.salida
        )
    except ErrorDatos as error:
        print("ERROR: {}".format(error), file=sys.stderr)
        return 1

    imprimir_resumen(clasificacion, estadisticas)
    print("Reporte HTML generado en: {}".format(ruta_generada))
    return 0


if __name__ == "__main__":
    sys.exit(main())
