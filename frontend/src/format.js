// kemasan ditulis seperti di bungkus (gram), semua total ditulis dalam kg
export function formatKemasan(gram) {
  return gram >= 1000 ? `${gram / 1000} kg` : `${gram} gr`
}

export function formatKg(gram) {
  const kg = (gram / 1000).toLocaleString("id-ID", { minimumFractionDigits: 1, maximumFractionDigits: 1 })
  return `${kg} kg`
}
