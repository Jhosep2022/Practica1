import { useState, useEffect, useCallback } from 'react'
import ProductCard from './ProductCard'
import Cart from './Cart'
import { getDiscountedPrice } from './pricing'
import { LANGUAGES, getMessages } from './i18n'
import { productNamesEs } from './productNames'
import './App.css'

const API_URL = 'https://dummyjson.com/products'
const CART_STORAGE_KEY = 'tienda-cart'
const CART_OPEN_STORAGE_KEY = 'tienda-cart-open'
const PURCHASED_STORAGE_KEY = 'tienda-purchased'
const LANGUAGE_STORAGE_KEY = 'tienda-language'

// Minúsculas y sin tildes para que "limon" encuentre "Limón"
function normalizeText(value) {
  return String(value || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
}

function readStorageValue(key, fallback) {
  if (typeof window === 'undefined') {
    return fallback
  }

  try {
    const rawValue = window.localStorage.getItem(key)
    return rawValue ? JSON.parse(rawValue) : fallback
  } catch {
    return fallback
  }
}

function writeStorageValue(key, value) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value))
  } catch {
    // ignore localStorage write errors
  }
}

function normalizeCart(items) {
  if (!Array.isArray(items)) {
    return []
  }

  const mergedItems = new Map()

  items.forEach((item) => {
    if (!item || !item.id) {
      return
    }

    const quantity = Number(item.quantity) || 1

    if (mergedItems.has(item.id)) {
      const currentItem = mergedItems.get(item.id)
      currentItem.quantity += quantity
      return
    }

    mergedItems.set(item.id, { ...item, quantity })
  })

  return [...mergedItems.values()].filter((item) => item.quantity > 0)
}

function App() {
  const [products, setProducts] = useState([])
  const [cart, setCart] = useState(() => normalizeCart(readStorageValue(CART_STORAGE_KEY, [])))
  const [purchased, setPurchased] = useState(() => readStorageValue(PURCHASED_STORAGE_KEY, {}))
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('all')
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [reloadKey, setReloadKey] = useState(0)
  const [showCart, setShowCart] = useState(() => readStorageValue(CART_OPEN_STORAGE_KEY, false))
  const [language, setLanguage] = useState(() => readStorageValue(LANGUAGE_STORAGE_KEY, 'es'))
  const t = getMessages(language)

  const cartQuantityByProduct = cart.reduce((acc, item) => {
    acc[item.id] = (acc[item.id] || 0) + item.quantity
    return acc
  }, {})

  // Stock real = stock de la API menos lo ya comprado en esta tienda
  const getStock = useCallback(
    (product) => Math.max((Number(product.stock) || 0) - (purchased[product.id] || 0), 0),
    [purchased]
  )

  useEffect(() => writeStorageValue(CART_STORAGE_KEY, cart), [cart])
  useEffect(() => writeStorageValue(CART_OPEN_STORAGE_KEY, showCart), [showCart])
  useEffect(() => writeStorageValue(PURCHASED_STORAGE_KEY, purchased), [purchased])
  useEffect(() => {
    writeStorageValue(LANGUAGE_STORAGE_KEY, language)
    document.documentElement.lang = language
    document.title = getMessages(language).storeName
  }, [language])

  useEffect(() => {
    const controller = new AbortController()

    fetch(`${API_URL}/category-list`, { signal: controller.signal })
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => setCategories(Array.isArray(data) ? data : []))
      .catch(() => {
        // si falla, el selector usa las categorías de los productos cargados
      })

    return () => controller.abort()
  }, [reloadKey])

  useEffect(() => {
    const controller = new AbortController()
    // Se carga el catálogo completo una vez; búsqueda y filtros se resuelven en el cliente
    // para poder buscar por los nombres traducidos
    const url = `${API_URL}?limit=0`

    setLoading(true)
    setError(false)

    fetch(url, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) {
          throw new Error('Error fetching products')
        }
        return res.json()
      })
      .then((data) => {
        setProducts(Array.isArray(data.products) ? data.products : [])
        setLoading(false)
      })
      .catch((err) => {
        if (err.name === 'AbortError') {
          return
        }
        setError(true)
        setLoading(false)
      })

    return () => controller.abort()
  }, [reloadKey])

  useEffect(() => {
    if (!showCart) {
      return
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        setShowCart(false)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [showCart])

  function addToCart(product) {
    const productStock = getStock(product)

    setCart((currentCart) => {
      const existingItem = currentCart.find((item) => item.id === product.id)
      const nextQty = (existingItem?.quantity || 0) + 1

      if (nextQty > productStock) {
        return currentCart
      }

      if (existingItem) {
        return currentCart.map((item) =>
          item.id === product.id ? { ...item, quantity: nextQty } : item
        )
      }

      return [...currentCart, { ...product, quantity: 1 }]
    })
  }

  function changeQty(productId, delta) {
    setCart((currentCart) =>
      currentCart.map((item) => {
        if (item.id !== productId) {
          return item
        }

        const nextQty = item.quantity + delta

        if (nextQty < 1 || nextQty > getStock(item)) {
          return item
        }

        return { ...item, quantity: nextQty }
      })
    )
  }

  function removeFromCart(productId) {
    setCart((currentCart) => currentCart.filter((item) => item.id !== productId))
  }

  const total = cart.reduce(
    (sum, item) => sum + getDiscountedPrice(item) * item.quantity,
    0
  )

  function checkout() {
    if (cart.length === 0) {
      return
    }

    const confirmed = window.confirm(t.confirmCheckout(t.money(total)))
    if (!confirmed) {
      return
    }

    setPurchased((currentPurchased) => {
      const nextPurchased = { ...currentPurchased }
      cart.forEach((item) => {
        nextPurchased[item.id] = (nextPurchased[item.id] || 0) + item.quantity
      })
      return nextPurchased
    })

    setCart([])
    setShowCart(false)
    alert(t.checkoutDone(t.money(total)))
  }

  const categoryOptions = categories.length > 0
    ? categories
    : [...new Set(products.map((product) => product.category))]
  const sortedCategoryOptions = [...categoryOptions].sort((a, b) =>
    t.category(a).localeCompare(t.category(b), language)
  )
  const searchTerms = normalizeText(search).split(/\s+/).filter(Boolean)
  const visibleProducts = products.filter((product) => {
    if (category !== 'all' && product.category !== category) {
      return false
    }

    if (searchTerms.length === 0) {
      return true
    }

    const haystack = normalizeText(
      [
        product.title,
        productNamesEs[product.id],
        product.brand,
        product.category,
        t.category(product.category),
        product.description,
      ].join(' ')
    )

    return searchTerms.every((term) => haystack.includes(term))
  })
  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0)

  return (
    <div className="app">
      <header className="header">
        <h1>{t.storeName}</h1>
        <input
          className="search"
          type="search"
          aria-label={t.searchLabel}
          placeholder={t.searchPlaceholder}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          aria-label={t.categoryLabel}
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="all">{t.allCategories}</option>
          {sortedCategoryOptions.map((c) => (
            <option key={c} value={c}>
              {t.category(c)}
            </option>
          ))}
        </select>
        <button
          className="cart-btn"
          aria-expanded={showCart}
          onClick={() => setShowCart(!showCart)}
        >
          {t.cartButton(cartCount)}
        </button>
        <select
          className="language"
          aria-label={t.languageLabel}
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          {LANGUAGES.map((option) => (
            <option key={option.code} value={option.code} lang={option.code}>
              {option.label}
            </option>
          ))}
        </select>
      </header>

      <main aria-busy={loading}>
        {loading && <p className="loading">{t.loading}</p>}

        {error && (
          <div className="error" role="alert">
            <p>{t.loadError}</p>
            <button onClick={() => setReloadKey((key) => key + 1)}>{t.retry}</button>
          </div>
        )}

        {!loading && !error && visibleProducts.length === 0 && (
          <div className="empty">
            <p>
              {t.noResults}
              {search.trim() && t.noResultsFor(search.trim())}
              {category !== 'all' && t.noResultsIn(t.category(category))}.
            </p>
            <button
              onClick={() => {
                setSearch('')
                setCategory('all')
              }}
            >
              {t.clearFilters}
            </button>
          </div>
        )}

        {!error && (
          <div className="grid">
            {visibleProducts.map((product) => {
              const availableStock = Math.max(getStock(product) - (cartQuantityByProduct[product.id] || 0), 0)

              return (
                <ProductCard
                  key={product.id}
                  product={product}
                  availableStock={availableStock}
                  inCart={cartQuantityByProduct[product.id] || 0}
                  t={t}
                  onAdd={() => addToCart(product)}
                />
              )
            })}
          </div>
        )}
      </main>

      {showCart && (
        <Cart
          items={cart}
          total={total}
          getStock={getStock}
          t={t}
          onQty={changeQty}
          onRemove={removeFromCart}
          onCheckout={checkout}
          onClose={() => setShowCart(false)}
        />
      )}
    </div>
  )
}

export default App
