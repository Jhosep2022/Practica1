import { useEffect, useRef } from 'react'
import { finalPrice } from './price'

function Cart({ items, total, onQty, onRemove, onCheckout, onClose }) {
  const closeRef = useRef(null)

  useEffect(() => {
    const previous = document.activeElement
    closeRef.current?.focus()

    function onKeyDown(e) {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      previous?.focus?.()
    }
  }, [onClose])

  return (
    <>
      <div className="cart-overlay" aria-hidden="true" onClick={onClose} />

      <aside
        className="cart"
        role="dialog"
        aria-modal="true"
        aria-labelledby="cart-title"
      >
        <div className="cart-header">
          <h2 id="cart-title">Tu carrito</h2>
          <button
            ref={closeRef}
            className="cart-close"
            aria-label="Cerrar carrito"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        {items.length === 0 && <p>El carrito está vacío.</p>}

        <ul className="cart-list">
          {items.map((item, index) => (
            <li key={item.id} className="cart-item">
              <img
                src={item.thumbnail}
                alt={item.title}
                width="60"
                height="60"
                loading="lazy"
                decoding="async"
              />
              <span className="cart-title">{item.title}</span>
              <span>${finalPrice(item).toFixed(2)}</span>
              <div className="qty">
                <button
                  aria-label="Quitar uno"
                  onClick={() => onQty(index, -1)}
                  disabled={item.quantity <= 1}
                >
                  -
                </button>
                <span>{item.quantity}</span>
                <button
                  aria-label="Agregar uno"
                  onClick={() => onQty(index, 1)}
                  disabled={item.quantity >= (item.stock ?? Infinity)}
                >
                  +
                </button>
              </div>
              <button
                className="remove"
                aria-label={`Eliminar ${item.title}`}
                onClick={() => onRemove(index)}
              >
                x
              </button>
            </li>
          ))}
        </ul>

        <h3>Total: ${total.toFixed(2)}</h3>
        <button className="pay-btn" onClick={onCheckout} disabled={items.length === 0}>
          Pagar
        </button>
      </aside>
    </>
  )
}

export default Cart
