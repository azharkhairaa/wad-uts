const API_URL = "http://127.0.0.1:8000"

async function request(path, options) {
  let response
  try {
    response = await fetch(`${API_URL}${path}`, options)
  } catch {
    // fetch gagal total = backend tidak bisa dihubungi
    throw new Error("Tidak bisa terhubung ke backend. Pastikan server FastAPI berjalan.")
  }

  if (!response.ok) {
    throw new Error(`Permintaan gagal (HTTP ${response.status})`)
  }
  return response.json()
}

export function ambilSemuaBarang() {
  return request("/barang")
}
