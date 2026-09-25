import { useState } from 'react'
import { getDiscountedPrice } from './pricing'

function Cart({ items, total, getStock, t, onQty, onRemove, onCheckout, onClose }) {
  const [pendingRemoveId, setPendingRemoveId] = useState(null)

  return (
    <aside className="cart" aria-label={t.cartLabel}>
      <div className="cart-header">
        <h2>{t.cartTitle}</h2>
        <button className="cart-close" aria-label={t.closeCart} title={t.closeCartHint} onClick={onClose}>
          ×
        </button>
      </div>

      {items.length === 0 && <p>{t.emptyCart}</p>}

      <ul className="cart-list">
        {items.map((item) => {
          const maxQty = getStock(item)
          const atMax = item.quantity >= maxQty
          const title = t.productTitle(item)

          return (
            <li key={item.id} className="cart-item">
              <img src={item.thumbnail} alt="" width="60" />
              <div className="cart-details">
                <span className="cart-title">{title}</span>
                <span className="cart-price">
                  {t.money(getDiscountedPrice(item))} {t.each} · {t.subtotal} {t.money(getDiscountedPrice(item) * item.quantity)}
                </span>
                {atMax && <span className="cart-limit">{t.maxAvailable}</span>}
              </div>
              <div className="qty">
                <button
                  aria-label={t.removeOne(title)}
                  onClick={() => onQty(item.id, -1)}
                  disabled={item.quantity <= 1}
                >
                  -
                </button>
                <span aria-live="polite">{item.quantity}</span>
                <button
                  aria-label={t.addOne(title)}
                  onClick={() => onQty(item.id, 1)}
                  disabled={atMax}
                >
                  +
                </button>
              </div>
              <button
                className="remove"
                aria-label={t.removeItem(title)}
                title={t.removeHint}
                onClick={() => setPendingRemoveId(item.id)}
              >
                x
              </button>
              {pendingRemoveId === item.id && (
                <div
                  className="remove-confirm"
                  role="alertdialog"
                  aria-label={t.confirmRemoveLabel(title)}
                  onKeyDown={(e) => {
                    // Esc cancela solo la confirmación, no cierra el carrito
                    if (e.key === 'Escape') {
                      e.stopPropagation()
                      setPendingRemoveId(null)
                    }
                  }}
                >
                  <span>{t.confirmRemove}</span>
                  <div className="remove-confirm-actions">
                    <button onClick={() => setPendingRemoveId(null)} autoFocus>
                      {t.cancel}
                    </button>
                    <button
                      className="danger"
                      onClick={() => {
                        onRemove(item.id)
                        setPendingRemoveId(null)
                      }}
                    >
                      {t.remove}
                    </button>
                  </div>
                </div>
              )}
            </li>
          )
        })}
      </ul>

      <div className="cart-footer">
        <h3>{t.total}: {t.money(total)}</h3>
        <button className="pay-btn" onClick={onCheckout} disabled={items.length === 0}>
          {t.pay}
        </button>
      </div>
    </aside>
  )
}

export default Cart
