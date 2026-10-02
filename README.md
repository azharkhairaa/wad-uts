# Dashboard Inventaris Roastery

UTS Web Application Development — **Soal B: Dashboard Inventaris**.

| | |
|---|---|
| Nama | Muhammad Azhar Khaira |
| NIM | 25120300010 |
| Soal | B |

Mini dashboard full-stack untuk memantau stok biji kopi di gudang roastery:
menampilkan daftar barang, mencari, mengurutkan, menambah dan menghapus data,
serta menambah stok dan mencatat penjualan.

## Tech Stack

- **Backend:** FastAPI + Pydantic, data in-memory yang di-seed dari file JSON
- **Frontend:** Vue 3 (Composition API) + Vite, komunikasi dengan `fetch`
- Tanpa library tambahan

## Cara Menjalankan

Menggunakan **Python 3.10+** dan **Node.js 20.19+ / 22.12+**. Backend dan frontend
dijalankan di dua terminal terpisah.

**1. Backend** (http://127.0.0.1:8000)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # untuk Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Dokumentasi API (Swagger): http://127.0.0.1:8000/docs

**2. Frontend** (http://localhost:5173)

```bash
cd frontend
npm install
npm run dev
```

Frontend memanggil backend di `http://127.0.0.1:8000` (lihat `frontend/src/api.js`).
CORS di backend mengizinkan `http://localhost:5173` dan `http://127.0.0.1:5173`.

Data disimpan di memori, jadi setiap kali backend di-restart isinya akan kembali ke
25 data awal dari `backend/data/seed_barang.json`.

## Ambang Batas Status Stok

Status dihitung dari `jumlah_stok` (dalam **pack**) di `frontend/src/stok.js`:

| Status | Jumlah stok | Badge |
|---|---|---|
| **Habis** | 0 pack | merah |
| **Menipis** | 1–10 pack | krem |
| **Aman** | lebih dari 10 pack | hijau |

**Alasan angka 10:** diasumsikan satu produk terjual kira-kira 10 pack per minggu.
Biji kopi perlu disangrai ulang lalu diistirahatkan (*degassing*) beberapa hari
sebelum dikemas, jadi begitu stok tinggal sekitar satu minggu penjualan, produk
itu sudah perlu dijadwalkan roasting. Angkanya ditaruh di satu konstanta
(`BATAS_MENIPIS = 10`), jadi mudah diubah.

Catatan: ambang dihitung per pack tanpa membedakan ukuran kemasan. 10 pack 100 gr
dan 10 pack 1 kg sama-sama dianggap Menipis.

## Data Seed

25 produk di `backend/data/seed_barang.json`, dibagi ke 4 kategori:
Arabika Single Origin (12), Robusta Single Origin (5), Blend (4), dan Spesial (4).

Nama produk terinspirasi dari etalase kopi single origin **Arutala Coffee**
(Tokopedia). Jumlah stok, ukuran kemasan, dan lokasi gudang adalah data fiktif
buatan sendiri. Stoknya sengaja dibuat bervariasi supaya ketiga status muncul:
15 Aman, 6 Menipis, 4 Habis. Totalnya 533 pack atau 176,7 kg.

Setiap barang punya field wajib soal (`id`, `nama`, `kategori`, `jumlah_stok`,
`lokasi_gudang`) ditambah satu field `berat_gram` (berat per pack).

## Fitur

- Daftar barang dengan status **loading**, **kosong**, **error** (dengan tombol coba lagi), dan **berhasil**
- Pencarian berdasarkan **nama atau kategori** (`computed`)
- Urutkan nama **A-Z / Z-A** (`computed` berantai di atas hasil pencarian)
- Badge status stok dengan *conditional class binding*
- 4 tile ringkasan dari `computed`: **Total Barang**, **Stok Menipis + Habis**, **Jumlah Kategori**, **Total Unit**
- Form tambah barang (state lokal `ref`) → `POST`, lalu daftar dimuat ulang dari backend
- Tombol hapus per baris → `DELETE`, dengan konfirmasi
- Responsif: desktop, tablet, dan mobile (tabel berubah jadi kartu di layar kecil)
- **Tambah Stok** (`PATCH`) dengan pratinjau stok dan status sebelum disimpan
- **Jual** (`PATCH`): stok berkurang, ditolak kalau melebihi stok yang ada
- Dokumentasi **`/docs`** yang dirapikan: grup endpoint, ringkasan, deskripsi, contoh body, dan respons error
- **Ringkasan Stok per Kategori** berupa bar CSS yang lebarnya dihitung dari `computed`
- Kategori, kemasan, dan lokasi gudang dipilih dari dropdown (diambil dari `GET /referensi`); hanya nama yang bebas diisi
- Berat kemasan per pack dan total berat stok dalam kg
- Transisi antar-status, animasi baris saat dicari/diurutkan, dan notifikasi sukses/gagal

## Endpoint API

| Metode | Path | Keterangan | Status |
|---|---|---|---|
| GET | `/` | cek status backend | 200 |
| GET | `/referensi` | pilihan kategori, kemasan, dan lokasi gudang | 200 |
| GET | `/barang` | semua barang | 200 |
| POST | `/barang` | tambah barang (ID dibuat backend) | 201, 422 |
| DELETE | `/barang/{id}` | hapus barang | 200, 404 |
| PATCH | `/barang/{id}/stok` | tambah stok, body `{"jumlah": n}` | 200, 404, 422 |
| PATCH | `/barang/{id}/jual` | jual barang, body `{"jumlah": n}` | 200, 404, 409, 422 |

## Aturan Validasi (Backend)

Semua aturan berikut ditegakkan Pydantic di backend, jadi tetap berlaku walaupun
frontend dilewati (misalnya lewat `/docs` atau Postman).

- `nama` wajib diisi; spasi saja ditolak
- `kategori` hanya salah satu dari 4 kategori (`Enum`)
- `berat_gram` hanya 100, 200, 500, atau 1000
- `lokasi_gudang` hanya salah satu dari 19 lokasi yang terdaftar
- `jumlah_stok` bilangan bulat ≥ 0, dan `jumlah` (tambah stok / jual) bilangan bulat ≥ 1.
  Mode *strict*: `"12"` (teks), `12.5`, dan `true` ditolak, tidak diubah otomatis jadi angka
- Body tambah stok / jual hanya boleh berisi `jumlah`; field lain ditolak
- Jual melebihi stok ditolak **409 Conflict** dengan pesan "Stok tidak cukup, tersisa X pack"

## Desain API

- **`PATCH` untuk tambah stok dan jual.** Yang berubah hanya sebagian data
  barang yang sudah ada (`jumlah_stok`). `POST` untuk membuat data baru sedangkan
  `PUT` untuk mengganti seluruh data dan harus idempoten.
- **Jumlahnya relatif (+n / −n), bukan langsung mengirim stok akhir.**
  Supaya aturan "tidak boleh jual melebihi stok" bisa dicek di backend dan supaya dua perubahan yang terjadi bersamaan tidak saling menimpa.
- **Kenapa 409, bukan 422?** Format permintaannya benar, tapi bertentangan dengan
  kondisi stok saat itu. Permintaan yang sama bisa berhasil setelah stok ditambah.
- **Satuan:** stok disimpan dalam pack, berat dalam gram (bilangan bulat). Di layar,
  ukuran kemasan ditulis dalam gram ("200 gr"), semua total ditulis dalam kg.

## Struktur Folder

```
wad-uts/
├── backend/
│   ├── data/seed_barang.json   data awal (25 produk)
│   ├── main.py                 FastAPI: skema, endpoint, CORS
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.vue             state utama, computed pencarian/urutan/tile
        ├── api.js              semua fetch ke backend
        ├── stok.js             ambang batas & label status
        ├── format.js           format kemasan (gram) & berat (kg)
        ├── style.css           seluruh CSS + media query responsif
        └── components/
            ├── TabelBarang.vue   tabel / kartu barang
            ├── BadgeStok.vue     badge status stok
            ├── FormBarang.vue    form tambah barang
            ├── DialogStok.vue    dialog tambah stok & jual
            └── BarKategori.vue   ringkasan stok per kategori
```
