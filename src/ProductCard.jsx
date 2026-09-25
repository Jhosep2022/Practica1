import { getDiscountedPrice } from './pricing'

function ProductCard({ product, availableStock, inCart, t, onAdd }) {
  const isOutOfStock = availableStock <= 0
  const price = Number(product.price) || 0
  const finalPrice = getDiscountedPrice(product)
  const hasDiscount = finalPrice < price
  const title = t.productTitle(product)

  return (
    <article className="card">
      <img src={product.thumbnail} alt={title} loading="lazy" />
      <h3>{title}</h3>
      <p className="price">
        {t.money(finalPrice)}
        {hasDiscount && (
          <>
            {' '}
            <s className="price-old">{t.money(price)}</s>
            <span className="discount"> -{Math.round(product.discountPercentage)}%</span>
          </>
        )}
      </p>
      <p className="meta">
        {t.rating}: {(Number(product.rating) || 0).toLocaleString(t.locale, { minimumFractionDigits: 1, maximumFractionDigits: 1 })} · {t.available}: {availableStock}
        {inCart > 0 && <> · {t.inCart}: {inCart}</>}
      </p>
      <button className="add-btn" onClick={onAdd} disabled={isOutOfStock}>
        {isOutOfStock ? (inCart > 0 ? t.maxInCart : t.outOfStock) : t.add}
      </button>
    </article>
  )
}

export default ProductCard
