# Tienda Tech (ejercicio de depuración)

Esta tienda con carrito **tiene exactamente 10 errores**: algunos de lógica, otros de datos/API y otros visuales.

## Cómo ejecutarla

```bash
npm install
npm run dev
```

Abre la dirección que muestra la terminal (normalmente http://localhost:5173).

## Tu tarea

1. Usa la aplicación (busca, filtra, agrega al carrito, cambia cantidades, elimina, paga) y anota todo lo que funcione o se vea mal.
2. Encuentra la causa de cada error en el código.
3. Corrígelos. Puedes usar IA, pero debes **entender y probar** cada cambio.
4. Entrega, por cada uno de los 10 errores:
   - Qué pasaba (síntoma).
   - En qué archivo y línea estaba la causa.
   - Cómo lo corregiste.
   - El prompt que usaste con la IA y si tuviste que corregirlo.

Los datos vienen de https://dummyjson.com/products

---

# Reporte QA – rama `Ai-Fixes`

Cada bug incluye **Pasos** para reproducirlo, **Detección** (cómo se encontró y confirmó), la heurística que incumple y el **Fix**.

Escala: **Severidad** (Crítica / Alta / Media / Baja) = impacto en el usuario o en los datos. **Prioridad** (P1 / P2 / P3) = urgencia para corregirlo.
Estado: los bugs 13–16 se reprodujeron en `main` y quedaron corregidos en `4e1d6da Fix v1`; el resto se reprodujo sobre `Fix v1` y se corrigió en esta iteración.

| # | Bug | Severidad | Prioridad | Heurística de Nielsen | Estado |
|---|-----|-----------|-----------|-----------------------|--------|
| 1 | El precio de la tarjeta no coincide con lo que se cobra | Crítica | P1 | #4 Consistencia y estándares | Corregido |
| 2 | La búsqueda acumula productos: al borrarla, el catálogo no vuelve a su estado inicial | Alta | P1 | #1 Visibilidad del estado del sistema | Corregido |
| 3 | La búsqueda oculta resultados que la API sí devolvió | Alta | P1 | #2 Coincidencia sistema–mundo real | Corregido |
| 4 | El filtro de categorías solo tiene 4 de las 24 categorías: laptops, smartphones, tablets, etc. son inalcanzables | Alta | P1 | #4 Consistencia y estándares | Corregido |
| 5 | Si la API falla, el usuario no recibe ningún mensaje | Alta | P1 | #9 Reconocer, diagnosticar y recuperarse de errores | Corregido |
| 6 | Condición de carrera y una petición por cada tecla en la búsqueda | Media | P2 | #1 Visibilidad del estado del sistema | Corregido |
| 7 | El "+" del carrito no avisa cuando se alcanza el stock máximo | Media | P2 | #1 Visibilidad del estado del sistema | Corregido |
| 8 | El "-" con cantidad 1 elimina el producto sin avisar | Media | P2 | #5 Prevención de errores | Corregido |
| 9 | Stock y productos obsoletos desde localStorage (caché sin invalidar) | Media | P2 | #1 Visibilidad del estado del sistema | Corregido |
| 10 | "Sin resultados" no dice por qué ni ofrece cómo salir | Baja | P3 | #3 Control y libertad del usuario | Corregido |
| 11 | El carrito no se cierra con Esc y sigue abierto después de pagar | Baja | P3 | #7 Flexibilidad y eficiencia de uso | Corregido |
| 12 | El carrito no muestra subtotales y las etiquetas de stock son ambiguas | Baja | P3 | #6 Reconocer antes que recordar | Corregido |
| 13 | "Agregar" no agrega el producto al carrito | Crítica | P1 | #1 Visibilidad del estado del sistema | Corregido (Fix v1) |
| 14 | Al abrir el carrito ya no se puede cerrar | Crítica | P1 | #3 Control y libertad del usuario | Corregido (Fix v1) |
| 15 | El carrito no persiste al recargar | Alta | P1 | #6 Reconocer antes que recordar | Corregido (Fix v1) |
| 16 | Comprar no actualiza el stock | Alta | P1 | #2 Coincidencia sistema–mundo real | Corregido (Fix v1) |
| 17 | Con muchos productos, el total y el botón Pagar quedan fuera de la vista | Media | P2 | #1 Visibilidad del estado del sistema | Corregido |
| 18 | "x" elimina un producto del carrito sin confirmar | Media | P2 | #5 Prevención de errores | Corregido |
| 19 | El nombre "Tienda Tech" no corresponde al catálogo (belleza, muebles, comestibles…) | Baja | P3 | #2 Coincidencia sistema–mundo real | Corregido |
| 20 | La interfaz mezcla español e inglés (productos, categorías) y no se puede elegir el idioma | Alta | P1 | #4 Consistencia y estándares | Corregido |
| 21 | La categoría "tops" contiene vestidos y dos categorías se llamarían "Vestidos" | Media | P2 | #2 Coincidencia sistema–mundo real | Corregido |

## Detalle

### 1. El precio de la tarjeta no coincide con lo que se cobra: Crítica / P1
**Pasos:** 1) Abrir la tienda. 2) Ver el precio de "Essence Mascara Lash Princess" en la tarjeta ($9.99). 3) Agregarlo y abrir el carrito: aparece $8.94 (10.48% de descuento) y ese es el total cobrado.
**Detección:** Revisión de código: `ProductCard` mostraba `product.price` y el carrito cobraba el precio con descuento. Se confirmó con la API (`/products/1`: price 9.99, discountPercentage 10.48 → $8.94).
**Heurística #4 (Consistencia):** el mismo producto muestra dos precios distintos y el usuario no sabe cuál se le cobrará, lo que genera desconfianza en el pago.
**Fix:** la tarjeta muestra el precio final con descuento, el precio original tachado y el porcentaje. El cálculo se centralizó en `src/pricing.js` y lo usan la tarjeta, el carrito y el total.

### 2. La búsqueda acumula productos: Alta / P1
**Pasos:** 1) Buscar "phone". 2) Borrar la búsqueda. 3) La grilla muestra más de 30 productos: los resultados de "phone" se quedaron mezclados con el catálogo inicial y se guardan en localStorage.
**Detección:** Revisión de código de `setProducts` en `App.jsx`: fusionaba con un `Map` los resultados nuevos con los anteriores y los guardaba en `localStorage`. Se reprodujo con búsqueda → borrar búsqueda.
**Heurística #1 (Visibilidad del estado):** lo que se ve no refleja el estado real de la consulta.
**Fix:** cada respuesta de la API reemplaza la lista en lugar de fusionarse con la anterior.

### 3. La búsqueda oculta resultados que la API sí devolvió: Alta / P1
**Pasos:** 1) Buscar "phone". 2) La API devuelve "Apple AirPods Max Silver" (coincide en la descripción), pero el filtro local por título lo oculta.
**Detección:** Llamada directa a la API (`/products/search?q=phone`): devuelve "Apple AirPods Max Silver", pero el filtro `title.includes(search)` del cliente lo descartaba.
**Heurística #2 (Mundo real):** el usuario espera ver todo lo que coincide con su búsqueda, no solo lo que coincide con el título.
**Fix:** la búsqueda considera el nombre (en inglés y español), la marca, la categoría y la descripción. No distingue mayúsculas ni tildes ("limon" encuentra "Limón").

### 4. El filtro de categorías solo tiene 4 de las 24 categorías: Alta / P1
**Pasos:** 1) Abrir el selector de categorías: solo aparecen beauty/fragrances/furniture/groceries. 2) El catálogo tiene 194 productos en 24 categorías (laptops, smartphones, tablets, etc.). No hay forma de filtrarlas, y solo aparecen si se buscan por nombre (p. ej. "phone" → "mobile-accessories"), sin poder filtrarlas.
**Detección:** Revisión de código (constante `CATEGORIES` con 4 valores fijos) comparada con `/products/category-list` (24 categorías) y `/products?limit=0` (194 productos). El equipo lo reportó al notar que faltaban celulares y laptops.
**Heurística #4 (Consistencia):** el filtro no corresponde con el catálogo real y deja productos sin categoría accesible.
**Fix:** las 24 categorías se cargan desde `GET /products/category-list` y el catálogo completo desde `GET /products?limit=0` (194 productos), así que celulares, laptops, etc. se ven sin tener que buscarlos. Categoría y búsqueda se combinan en el cliente, y los nombres de las categorías están traducidos (ver #20).

### 5. Si la API falla, el usuario no recibe ningún mensaje: Alta / P1
**Pasos:** 1) DevTools → Network → Offline. 2) Recargar o buscar. 3) Solo aparece "Sin resultados." o datos viejos, sin ninguna explicación.
**Detección:** Revisión de código: el `.catch` devolvía el mismo estado sin avisar al usuario. Se reproduce con DevTools en modo Offline.
**Heurística #9 (Recuperarse de errores):** el error se oculta y el usuario cree que el producto no existe.
**Fix:** mensaje de error claro (`role="alert"`) con un botón **Reintentar**.

### 6. Condición de carrera en la búsqueda: Media / P2
**Pasos:** 1) Escribir rápido "laptop" con la red en "Slow 3G". 2) Se lanza una petición por cada tecla y una respuesta vieja puede llegar al final y pisar la correcta.
**Detección:** Revisión de código: el `useEffect` lanzaba un `fetch` por cada cambio del input, sin debounce ni cancelación. Se reproduce con la red limitada a "Slow 3G".
**Heurística #1 (Visibilidad del estado):** los resultados no corresponden al texto escrito.
**Fix:** el catálogo se pide una sola vez (con `AbortController` al desmontar) y la búsqueda se resuelve en el cliente, así que ya no hay peticiones por tecla ni respuestas desordenadas.

### 7. El "+" del carrito no avisa del stock máximo: Media / P2
**Pasos:** 1) Agregar un producto y pulsar "+" hasta el tope. 2) El botón sigue activo pero no hace nada.
**Detección:** Revisión de código de `changeQty`: al superar el stock devolvía el ítem sin cambios y el botón seguía activo, sin ninguna señal.
**Heurística #1 (Visibilidad del estado):** un clic sin respuesta parece un fallo.
**Fix:** el "+" se deshabilita al llegar al máximo y aparece el aviso "Máximo disponible". En la tarjeta, el botón cambia a "Máximo en carrito".

### 8. El "-" con cantidad 1 elimina el producto sin avisar: Media / P2
**Pasos:** 1) Con un producto en cantidad 1, pulsar "-". 2) El producto desaparece del carrito.
**Detección:** Revisión de código de `changeQty`: con `nextQty <= 0` el ítem se descartaba del carrito.
**Heurística #5 (Prevención de errores):** es fácil eliminar un producto por accidente, cuando ya existe un botón explícito para eliminar.
**Fix:** el "-" se deshabilita en 1 y para eliminar se usa la "x" (que pide confirmación, ver #18).

### 9. Stock y productos obsoletos desde localStorage: Media / P2
**Pasos:** 1) Cargar la tienda. 2) El catálogo se guardaba completo en `tienda-products` y al recargar se mostraba primero el caché viejo, y el stock de la API nunca se actualizaba.
**Detección:** Revisión de código: el catálogo se guardaba en `localStorage` (`tienda-products`) y se usaba como estado inicial, preservando el stock viejo en cada fusión.
**Heurística #1 (Visibilidad del estado):** se muestran datos que ya no son reales.
**Fix:** solo se guardan las unidades compradas (`tienda-purchased`). El stock efectivo es el de la API menos lo comprado.

### 10. "Sin resultados" no dice por qué ni ofrece cómo salir: Baja / P3
**Pasos:** 1) Buscar "phone" y filtrar por una categoría sin coincidencias. 2) Solo aparece "Sin resultados.".
**Detección:** Uso de la app combinando una búsqueda y una categoría sin coincidencias; el estado vacío solo decía "Sin resultados.".
**Heurística #3 (Control y libertad):** el usuario no tiene una salida evidente.
**Fix:** el mensaje indica la búsqueda y la categoría activas, con un botón **Limpiar filtros**.

### 11. El carrito no se cierra con Esc y sigue abierto después de pagar: Baja / P3
**Pasos:** 1) Abrir el carrito y pulsar Esc: no se cierra. 2) Pagar: el panel queda abierto y vacío.
**Detección:** Uso de la app: Esc no hacía nada (no había listener de teclado) y `checkout` no cerraba el panel.
**Heurística #7 (Flexibilidad y eficiencia):** faltan atajos habituales y queda un paso innecesario.
**Fix:** el carrito se cierra con Esc, tiene `aria-expanded` en el botón y se cierra al completar la compra.

### 12. Sin subtotales y etiquetas ambiguas: Baja / P3
**Pasos:** 1) Agregar 3 unidades de un producto. 2) El carrito muestra solo el precio unitario y la tarjeta dice "Stock" cuando en realidad es lo disponible menos lo que está en el carrito.
**Detección:** Uso de la app agregando varias unidades: sin subtotal por línea, y "Stock" mostraba el disponible menos lo que ya está en el carrito.
**Heurística #6 (Reconocer antes que recordar):** el usuario tiene que calcular mentalmente los subtotales.
**Fix:** se muestran "c/u · Subtotal", "Disponibles: N · En carrito: M" y etiquetas `aria-label` específicas por producto.

### 13. "Agregar" no agrega el producto al carrito: Crítica / P1
**Pasos (en `main`):** 1) Pulsar "Agregar" en cualquier producto. 2) El contador del carrito no cambia y el carrito sigue vacío.
**Detección:** Reportado por el equipo. Confirmado en el código de `main` (`git show main:src/App.jsx`): `addToCart` hacía `cart.push()` + `setCart(cart)` con la misma referencia.
**Heurística #1 (Visibilidad del estado):** la acción no produce ningún efecto visible.
**Causa y fix:** `addToCart` hacía `cart.push()` y `setCart(cart)` sobre el mismo array, y React no re-renderizaba. Ahora el estado se actualiza de forma inmutable con `setCart(current => …)`.

### 14. Al abrir el carrito ya no se puede cerrar: Crítica / P1
**Pasos (en `main`):** 1) Pulsar "Carrito". 2) El panel fijo tapa el botón y no tiene forma de cerrarse.
**Detección:** Reportado por el equipo. Confirmado en `main`: `Cart` no tenía botón de cierre y el panel fijo tapaba el botón "Carrito".
**Heurística #3 (Control y libertad):** el usuario queda atrapado, sin una "salida de emergencia".
**Fix:** botón "×" en el encabezado del carrito, cierre con Esc y cierre automático al pagar.

### 15. El carrito no persiste al recargar: Alta / P1
**Pasos (en `main`):** 1) Agregar productos. 2) Recargar la página. 3) El carrito aparece vacío.
**Detección:** Reportado por el equipo. Confirmado en `main`: no había ninguna lectura ni escritura en `localStorage`.
**Heurística #6 (Reconocer antes que recordar):** obliga al usuario a recordar y volver a armar su selección.
**Fix:** el carrito se guarda en `localStorage` (`tienda-cart`) y se normaliza al leerlo.

### 16. Comprar no actualiza el stock: Alta / P1
**Pasos (en `main`):** 1) Agregar 2 unidades de un producto y pagar. 2) La tarjeta muestra el mismo stock que antes.
**Detección:** Reportado por el equipo. Confirmado en `main`: `checkout` solo hacía `alert` + `setCart([])`, sin tocar el stock.
**Heurística #2 (Mundo real):** en una tienda real, lo comprado deja de estar disponible.
**Fix:** las unidades compradas se registran (`tienda-purchased`) y se descuentan del stock de la API. Además, la cantidad en el carrito nunca supera lo disponible.

### 17. El total y el botón Pagar quedan fuera de la vista: Media / P2
**Pasos:** 1) Agregar 10 o más productos distintos. 2) Abrir el carrito: para ver el total y pagar hay que desplazar todo el panel.
**Detección:** Reportado por el equipo. Confirmado en el CSS: `.cart` tenía `overflow-y: auto` en todo el panel, así que el total y "Pagar" se desplazaban junto con la lista.
**Heurística #1 (Visibilidad del estado):** el total y la acción principal deben verse siempre.
**Fix:** el panel usa una columna flex. El encabezado ("Tu carrito") y el pie (total + Pagar) quedan fijos, y solo la lista de productos tiene scroll.

### 18. "x" elimina sin confirmar: Media / P2
**Pasos:** 1) Con productos en el carrito, pulsar "x". 2) El producto desaparece al instante y no hay forma de deshacerlo.
**Detección:** Reportado por el equipo. Confirmado en el código: el botón "x" llamaba a `onRemove` directamente.
**Heurística #5 (Prevención de errores):** es una acción destructiva sin confirmación ni opción de deshacer.
**Fix:** una mini confirmación en línea sobre el mismo producto ("¿Eliminar este producto del carrito?", con Cancelar enfocado por defecto y Eliminar), manteniendo el diseño del panel.

### 19. El nombre no corresponde al catálogo: Baja / P3
**Pasos:** 1) Abrir la tienda: se llama "Tienda Tech", pero vende maquillaje, perfumes, muebles y comestibles.
**Detección:** Reportado por el equipo. Confirmado con `/products/category-list`: el catálogo es general (belleza, muebles, comestibles, vehículos…), no tecnológico.
**Heurística #2 (Mundo real):** el nombre genera una expectativa (tecnología) que el catálogo no cumple.
**Fix:** se renombró a **Bazar Central** (encabezado y `<title>`).

### 20. La interfaz mezcla español e inglés: Alta / P1
**Pasos:** 1) Abrir la tienda: botones y textos están en español, pero los productos ("Blue Frock", "Red Lipstick") y las categorías ("beauty", "mobile-accessories") están en inglés. 2) No hay forma de elegir un idioma.
**Detección:** Reportado por el equipo con una captura: nombres de productos en inglés con la interfaz en español. Confirmado en el código: todos los textos estaban escritos a mano en español y la API solo entrega inglés.
**Heurística #4 (Consistencia y estándares):** mezclar idiomas en la misma pantalla obliga al usuario a cambiar de contexto y a traducir mentalmente. Tampoco hay forma de adaptar la tienda a su idioma (#7 Flexibilidad).
**Fix:** selector **Español / English** en el encabezado, guardado en `localStorage` (`tienda-language`) y aplicado a `<html lang>` y al título de la pestaña. En `src/i18n.js` están todos los textos de la interfaz, incluidos `aria-label`, confirmaciones y alertas, además de las 24 categorías y el formato de moneda y decimales de cada idioma ($9,99 frente a $9.99). En `src/productNames.js` están los nombres en español de los 194 productos (la API solo los da en inglés); las marcas y modelos se conservan (iPhone, Rolex…). Buscar funciona en ambos idiomas.

### 21. La categoría "tops" contiene vestidos: Media / P2
**Pasos:** 1) Filtrar por "tops": aparecen "Blue Frock", "Girl Summer Dress", "Gray Dress"… Son vestidos, no blusas ni tops. 2) La categoría `womens-dresses` también tiene vestidos, así que una traducción literal dejaría dos categorías "Vestidos".
**Detección:** Reportado por el equipo con una captura del filtro. Confirmado con `/products/category/tops`, que devuelve 5 vestidos (ids 162–166).
**Heurística #2 (Mundo real):** la etiqueta debe describir lo que el usuario va a encontrar.
**Fix:** los nombres visibles describen el contenido real: `tops` → "Vestidos casuales / Casual dresses" y `womens-dresses` → "Vestidos de gala y conjuntos / Formal dresses & outfits". El slug de la API no se toca.

## Verificación
- `npm run build`: OK.
- Manual (`npm run dev`): buscar/limpiar, filtrar, agregar hasta el máximo, +/- en el carrito, eliminar con confirmación, carrito con más de 10 productos, pagar, Esc, recargar (persistencia), modo offline y reintentar, cambio de idioma (todos los textos, categorías, productos y precios) y búsqueda en ambos idiomas.
