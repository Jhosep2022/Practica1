// El precio que realmente se cobra. Vive aqui porque lo usan la tarjeta,
// el carrito y el total: si la formula se duplica, se vuelven a desincronizar.
export function finalPrice(product) {
  const price = product.price ?? 0
  const discount = product.discountPercentage ?? 0
  return price * (1 - discount / 100)
}
