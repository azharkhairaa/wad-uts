const API_URL = "http://127.0.0.1:8000"

// ubah "detail" error FastAPI (string atau daftar validasi 422) jadi satu kalimat
function pesanDariDetail(detail) {
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) {
    return detail.map((galat) => `${galat.loc.at(-1)}: ${galat.msg}`).join("; ")
  }
  return null
}

async function request(path, options) {
  let response
  try {
    response = await fetch(`${API_URL}${path}`, options)
  } catch {
    // fetch gagal total = backend tidak bisa dihubungi
    throw new Error("Tidak bisa terhubung ke backend. Pastikan server FastAPI berjalan.")
  }

  if (!response.ok) {
    const isi = await response.json().catch(() => null)
    throw new Error(pesanDariDetail(isi?.detail) ?? `Permintaan gagal (HTTP ${response.status})`)
  }
  return response.json()
}

export function ambilSemuaBarang() {
  return request("/barang")
}

export function ambilReferensi() {
  return request("/referensi")
}

export function tambahBarang(barang) {
  return request("/barang", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(barang),
  })
}

export function hapusBarang(id) {
  return request(`/barang/${id}`, { method: "DELETE" })
}

export function tambahStok(id, jumlah) {
  return request(`/barang/${id}/stok`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jumlah }),
  })
}

export function jualBarang(id, jumlah) {
  return request(`/barang/${id}/jual`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jumlah }),
  })
}
