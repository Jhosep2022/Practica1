import { useState, useEffect, useCallback } from 'react'
import ProductCard from './ProductCard'
import Cart from './Cart'
import { finalPrice } from './price'
import './App.css'

const API_URL = 'https://dummyjson.com/products'
const CATEGORIES = ['beauty', 'fragrances', 'furniture', 'groceries']
const PAGE_LIMIT = 30
const SEARCH_DEBOUNCE_MS = 300

function App() {
  const [products, setProducts] = useState([])
  const [cart, setCart] = useState([])
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCart, setShowCart] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    // Solo la búsqueda se retrasa: el primer render y los cambios de
    // categoría no tienen por qué esperar.
    const delay = search ? SEARCH_DEBOUNCE_MS : 0

    const timer = setTimeout(() => {
      setLoading(true)
      setError('')

      let url
      if (search) {
        url = `${API_URL}/search?q=${encodeURIComponent(search)}&limit=${PAGE_LIMIT}`
      } else if (category === 'all') {
        url = `${API_URL}?limit=${PAGE_LIMIT}`
      } else {
        url = `${API_URL}/category/${encodeURIComponent(category)}?limit=${PAGE_LIMIT}`
      }

      fetch(url, { signal: controller.signal })
        .then((res) => {
          if (!res.ok) throw new Error(`HTTP ${res.status}`)
          return res.json()
        })
        .then((data) => {
          setProducts(Array.isArray(data.products) ? data.products : [])
          setLoading(false)
        })
        .catch((err) => {
          if (err.name === 'AbortError') return
          setProducts([])
          setError('No se pudieron cargar los productos. Inténtalo de nuevo.')
          setLoading(false)
        })
    }, delay)

    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [search, category])

  function addToCart(product) {
    setCart((prev) => {
      const inCart = prev.find((item) => item.id === product.id)
      // No dejamos pasar del stock disponible.
      if ((inCart?.quantity ?? 0) >= product.stock) return prev
      if (!inCart) return [...prev, { ...product, quantity: 1 }]
      return prev.map((item) =>
        item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
      )
    })
  }

  function changeQty(index, delta) {
    setCart((prev) =>
      prev.map((item, i) => {
        if (i !== index) return item
        const max = item.stock ?? Infinity
        const quantity = Math.min(Math.max(item.quantity + delta, 1), max)
        return { ...item, quantity }
      })
    )
  }

  function removeFromCart(index) {
    setCart((prev) => prev.filter((_, i) => i !== index))
  }

  // useCallback: Cart la usa como dependencia de su efecto; una funcion
  // nueva en cada render le robaria el foco al usuario.
  const closeCart = useCallback(() => setShowCart(false), [])

  function checkout() {
    alert(`Compra realizada. Total: $${total.toFixed(2)}`)
    setCart([])
  }

  const total = cart.reduce(
    (sum, item) => sum + finalPrice(item) * item.quantity,
    0
  )

  const itemCount = cart.reduce((count, item) => count + item.quantity, 0)

  // La API ya filtró por búsqueda o por categoría; esto solo hace falta
  // cuando se combinan las dos, porque /search ignora la categoría.
  const visibleProducts = products.filter(
    (p) => category === 'all' || p.category === category
  )

  return (
    <div className="app">
      <header className="header">
        <h1>Tienda Tech</h1>
        <input
          className="search"
          type="search"
          aria-label="Buscar productos"
          placeholder="Buscar..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className="filter"
          aria-label="Filtrar por categoría"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="all">Todas</option>
          {CATEGORIES.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <button className="cart-btn" onClick={() => setShowCart((v) => !v)}>
          Carrito ({itemCount})
        </button>
      </header>

      <main>
        {loading && <p className="loading">Cargando...</p>}

        {error && <p className="error">{error}</p>}

        {!loading && !error && visibleProducts.length === 0 && (
          <p>Sin resultados.</p>
        )}

        {!loading && !error && (
          <div className="grid">
            {visibleProducts.map((p) => (
              <ProductCard key={p.id} product={p} onAdd={() => addToCart(p)} />
            ))}
          </div>
        )}
      </main>

      {showCart && (
        <Cart
          items={cart}
          total={total}
          onQty={changeQty}
          onRemove={removeFromCart}
          onCheckout={checkout}
          onClose={closeCart}
        />
      )}
    </div>
  )
}

export default App
