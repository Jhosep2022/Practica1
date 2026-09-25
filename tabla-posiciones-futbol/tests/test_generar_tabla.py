# -*- coding: utf-8 -*-
"""Pruebas de la skill tabla-posiciones-futbol.

Ejecutar desde la carpeta de la skill:
    python -m unittest discover tests
"""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

# Se agrega scripts/ al path para poder importar el modulo sin instalarlo.
CARPETA_SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CARPETA_SKILL / "scripts"))

import generar_tabla  # noqa: E402  (el import va despues de ajustar sys.path)

DATOS = Path(__file__).resolve().parent / "datos"
EJEMPLO = CARPETA_SKILL / "assets" / "ejemplo_liga.csv"


def clasificar(ruta_csv):
    """Atajo: lee un CSV y devuelve la clasificacion ya ordenada."""
    partidos = generar_tabla.leer_partidos(str(ruta_csv))
    tabla = generar_tabla.calcular_tabla(partidos)
    return partidos, generar_tabla.ordenar_tabla(tabla, partidos)


def ejecutar_main(argumentos):
    """Llama a main() capturando su salida para que las pruebas no la impriman."""
    salida, errores = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
        codigo = generar_tabla.main(argumentos)
    return codigo, salida.getvalue(), errores.getvalue()


def nombres(clasificacion):
    """Devuelve solo los nombres de equipo, en orden de posicion."""
    return [equipo["equipo"] for equipo in clasificacion]


class PruebasCalculoDePuntos(unittest.TestCase):
    """Verifica que PJ, PG, PE, PP, GF, GC, DG y Pts se calculen bien."""

    def test_puntos_victoria_empate_derrota(self):
        _, clasificacion = clasificar(DATOS / "valido_simple.csv")
        por_equipo = {e["equipo"]: e for e in clasificacion}

        # Bolivar gano 2-1 y empato 1-1: 3 + 1 = 4 puntos.
        bolivar = por_equipo["Bolivar"]
        self.assertEqual(bolivar["pj"], 2)
        self.assertEqual((bolivar["pg"], bolivar["pe"], bolivar["pp"]), (1, 1, 0))
        self.assertEqual(bolivar["pts"], 4)
        self.assertEqual((bolivar["gf"], bolivar["gc"], bolivar["dg"]), (3, 2, 1))

        # The Strongest perdio los dos partidos: 0 puntos.
        strongest = por_equipo["The Strongest"]
        self.assertEqual((strongest["pg"], strongest["pe"], strongest["pp"]), (0, 0, 2))
        self.assertEqual(strongest["pts"], 0)
        self.assertEqual((strongest["gf"], strongest["gc"], strongest["dg"]), (1, 5, -4))

    def test_suma_de_goles_es_coherente(self):
        """Los goles a favor de todos los equipos igualan a los goles en contra."""
        _, clasificacion = clasificar(EJEMPLO)
        self.assertEqual(
            sum(e["gf"] for e in clasificacion),
            sum(e["gc"] for e in clasificacion),
        )

    def test_partidos_jugados_por_equipo(self):
        _, clasificacion = clasificar(EJEMPLO)
        self.assertEqual(len(clasificacion), 6)
        for equipo in clasificacion:
            self.assertEqual(equipo["pj"], 5, equipo["equipo"])


class PruebasDesempate(unittest.TestCase):
    """Verifica el orden de la tabla y los cinco criterios de desempate."""

    def test_desempate_por_diferencia_de_gol(self):
        _, clasificacion = clasificar(DATOS / "valido_desempate_diferencia.csv")
        # Rojo y Azul tienen 3 puntos; Rojo gana por diferencia de gol (+4 contra +1).
        self.assertEqual(nombres(clasificacion), ["Rojo", "Azul", "Verde"])

    def test_desempate_por_enfrentamiento_directo(self):
        """Beta debe superar a Alfa pese a que el orden alfabetico diria lo contrario."""
        _, clasificacion = clasificar(DATOS / "valido_desempate_directo.csv")
        por_equipo = {e["equipo"]: e for e in clasificacion}

        # Los tres primeros criterios no los separan.
        for clave in ("pts", "dg", "gf"):
            self.assertEqual(por_equipo["Alfa"][clave], por_equipo["Beta"][clave], clave)

        # Beta le gano 2-1 a Alfa, asi que queda por encima.
        self.assertLess(nombres(clasificacion).index("Beta"),
                        nombres(clasificacion).index("Alfa"))

    def test_desempate_alfabetico_como_ultimo_recurso(self):
        """Dos equipos sin partido entre si y con todo igual se ordenan alfabeticamente."""
        partidos = [
            {"fecha": "2026-09-01", "local": "Zeta", "visitante": "Neutral",
             "goles_local": 1, "goles_visitante": 0},
            {"fecha": "2026-09-01", "local": "Alfa", "visitante": "Otro",
             "goles_local": 1, "goles_visitante": 0},
        ]
        tabla = generar_tabla.calcular_tabla(partidos)
        clasificacion = generar_tabla.ordenar_tabla(tabla, partidos)
        self.assertEqual(nombres(clasificacion)[:2], ["Alfa", "Zeta"])

    def test_orden_de_la_liga_de_ejemplo(self):
        """La liga de ejemplo tiene un orden conocido, con desempate directo incluido."""
        _, clasificacion = clasificar(EJEMPLO)
        self.assertEqual(nombres(clasificacion), [
            "Bolívar",
            "Wilstermann",
            "Oriente Petrolero",
            "Always Ready",
            "The Strongest",
            "Blooming",
        ])


class PruebasEstadisticas(unittest.TestCase):
    """Verifica las estadisticas destacadas del torneo."""

    def test_estadisticas_de_la_liga_de_ejemplo(self):
        partidos, clasificacion = clasificar(EJEMPLO)
        estadisticas = generar_tabla.calcular_estadisticas(partidos, clasificacion)

        self.assertEqual(estadisticas["total_partidos"], 15)
        self.assertEqual(estadisticas["total_equipos"], 6)
        self.assertEqual(estadisticas["mas_goleador"]["equipo"], "Bolívar")
        self.assertEqual(estadisticas["mejor_defensa"]["equipo"], "Bolívar")
        self.assertEqual(estadisticas["goles_partido_top"], 6)
        self.assertAlmostEqual(
            estadisticas["promedio_goles"],
            estadisticas["total_goles"] / 15,
        )


class PruebasGeneracionHTML(unittest.TestCase):
    """Verifica que el reporte HTML se genere completo y sin marcadores sueltos."""

    def setUp(self):
        self.partidos, self.clasificacion = clasificar(EJEMPLO)
        self.estadisticas = generar_tabla.calcular_estadisticas(
            self.partidos, self.clasificacion
        )

    def test_html_contiene_equipos_y_no_deja_marcadores(self):
        contenido = generar_tabla.generar_html(
            self.clasificacion, self.estadisticas, "ejemplo_liga.csv"
        )
        self.assertIn("<table>", contenido)
        for equipo in self.clasificacion:
            self.assertIn(equipo["equipo"], contenido)
        # Ningun marcador de la plantilla debe quedar sin reemplazar.
        self.assertNotIn("{{", contenido)

    def test_html_respeta_el_orden_de_la_tabla(self):
        contenido = generar_tabla.generar_html(
            self.clasificacion, self.estadisticas, "ejemplo_liga.csv"
        )
        posiciones = [contenido.index(e["equipo"]) for e in self.clasificacion]
        self.assertEqual(posiciones, sorted(posiciones))

    def test_flujo_completo_escribe_el_archivo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            salida = Path(carpeta) / "reporte.html"
            codigo, _, _ = ejecutar_main([str(EJEMPLO), "--salida", str(salida)])
            self.assertEqual(codigo, 0)
            self.assertTrue(salida.is_file())
            self.assertIn("<!DOCTYPE html>", salida.read_text(encoding="utf-8"))

    def test_resumen_de_terminal_incluye_encabezados(self):
        resumen = generar_tabla.formatear_resumen(self.clasificacion, self.estadisticas)
        self.assertIn("TABLA DE POSICIONES", resumen)
        self.assertIn("ESTADÍSTICAS DESTACADAS", resumen)
        self.assertIn("Pts", resumen)


class PruebasManejoDeErrores(unittest.TestCase):
    """Cada caso invalido debe lanzar ErrorDatos con un mensaje util en espanol."""

    def afirmar_error(self, ruta, fragmento):
        """Comprueba que leer el archivo falle y que el mensaje contenga el fragmento."""
        with self.assertRaises(generar_tabla.ErrorDatos) as contexto:
            generar_tabla.leer_partidos(str(ruta))
        mensaje = str(contexto.exception)
        self.assertIn(fragmento, mensaje)
        return mensaje

    def test_archivo_inexistente(self):
        self.afirmar_error(DATOS / "no_existe_este_archivo.csv", "no existe")

    def test_archivo_que_no_es_csv(self):
        self.afirmar_error(DATOS / "no_es_csv.txt", "no es un CSV")

    def test_archivo_vacio(self):
        self.afirmar_error(DATOS / "invalido_vacio.csv", "está vacío")

    def test_csv_sin_partidos(self):
        self.afirmar_error(DATOS / "invalido_sin_partidos.csv", "no contiene ningún partido")

    def test_columna_faltante(self):
        mensaje = self.afirmar_error(
            DATOS / "invalido_columna_faltante.csv", "Faltan columnas obligatorias"
        )
        self.assertIn("goles_visitante", mensaje)

    def test_columna_mal_nombrada(self):
        mensaje = self.afirmar_error(
            DATOS / "invalido_columna_mal_nombrada.csv", "Faltan columnas obligatorias"
        )
        self.assertIn("local", mensaje)

    def test_goles_no_numericos(self):
        mensaje = self.afirmar_error(
            DATOS / "invalido_goles_texto.csv", "deben ser un número entero"
        )
        # El error esta en la tercera linea del archivo.
        self.assertIn("Fila 3", mensaje)

    def test_goles_negativos(self):
        mensaje = self.afirmar_error(
            DATOS / "invalido_goles_negativos.csv", "no pueden ser negativos"
        )
        self.assertIn("Fila 2", mensaje)

    def test_equipo_contra_si_mismo(self):
        mensaje = self.afirmar_error(
            DATOS / "invalido_equipo_contra_si_mismo.csv", "no puede jugar contra sí mismo"
        )
        self.assertIn("Fila 3", mensaje)

    def test_fecha_con_formato_invalido(self):
        mensaje = self.afirmar_error(DATOS / "invalido_fecha.csv", "formato válido AAAA-MM-DD")
        self.assertIn("Fila 2", mensaje)

    def test_fecha_inexistente_en_el_calendario(self):
        # 2026-02-30 tiene el formato correcto pero no es un dia real.
        self.afirmar_error(DATOS / "invalido_fecha_inexistente.csv", "formato válido")

    def test_nombre_de_equipo_vacio(self):
        mensaje = self.afirmar_error(
            DATOS / "invalido_equipo_vacio.csv", "nombre del equipo local está vacío"
        )
        self.assertIn("Fila 2", mensaje)

    def test_main_devuelve_codigo_distinto_de_cero(self):
        """main() no debe lanzar traceback: devuelve 1 y escribe el error en stderr."""
        with tempfile.TemporaryDirectory() as carpeta:
            salida = Path(carpeta) / "reporte.html"
            codigo, _, errores = ejecutar_main(
                [str(DATOS / "invalido_goles_negativos.csv"), "--salida", str(salida)]
            )
            self.assertEqual(codigo, 1)
            # El mensaje va a stderr y no incluye traceback.
            self.assertTrue(errores.startswith("ERROR:"))
            self.assertNotIn("Traceback", errores)
            # Ante un error no debe quedar ningun reporte a medias.
            self.assertFalse(salida.exists())

    def test_main_devuelve_cero_con_datos_validos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            salida = Path(carpeta) / "reporte.html"
            codigo, texto, _ = ejecutar_main([str(EJEMPLO), "--salida", str(salida)])
            self.assertEqual(codigo, 0)
            self.assertIn("TABLA DE POSICIONES", texto)


if __name__ == "__main__":
    unittest.main()
