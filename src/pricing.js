export function getDiscountedPrice(product) {
  const basePrice = Number(product.price) || 0
  const discount = Number(product.discountPercentage) || 0
  return basePrice * (1 - discount / 100)
}
