// ambang batas: habis = 0, menipis = 1..10, aman > 10
export const BATAS_MENIPIS = 10

export function statusStok(jumlah) {
  if (jumlah === 0) return "habis"
  if (jumlah <= BATAS_MENIPIS) return "menipis"
  return "aman"
}

export const LABEL_STATUS = {
  aman: "Aman",
  menipis: "Menipis",
  habis: "Habis",
}
