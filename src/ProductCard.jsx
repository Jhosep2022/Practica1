import { finalPrice } from './price'

function ProductCard({ product, onAdd }) {
  const outOfStock = product.stock === 0
  const price = product.price ?? 0
  const discounted = finalPrice(product)
  const hasDiscount = discounted < price

  return (
    <article className="card">
      <img
        src={product.thumbnail}
        alt={product.title}
        loading="lazy"
        decoding="async"
      />
      <h3>{product.title}</h3>
      <p className="price">
        ${discounted.toFixed(2)}
        {hasDiscount && <span className="price-old">${price.toFixed(2)}</span>}
      </p>
      <p className="meta">
        Rating: {product.rating?.toFixed(1) ?? '—'} · Stock: {product.stock ?? 0}
      </p>
      <button className="add-btn" onClick={onAdd} disabled={outOfStock}>
        {outOfStock ? 'Sin stock' : 'Agregar'}
      </button>
    </article>
  )
}

export default ProductCard
