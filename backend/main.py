import json
from enum import Enum
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Path as PathParam
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

SEED_FILE = Path(__file__).parent / "data" / "seed_barang.json"

# grup endpoint di /docs
TAGS = [
    {"name": "Root", "description": "Cek status backend."},
    {"name": "Referensi", "description": "Daftar pilihan kategori dan lokasi gudang."},
    {"name": "Barang", "description": "Ambil, tambah dan hapus data barang inventaris."},
    {"name": "Stok", "description": "Ubah stok barang: tambah stok (barang masuk) atau jual (barang keluar)."},
]

app = FastAPI(
    title="Inventory Roastery API",
    description=(
        "Backend dashboard inventaris biji kopi roastery (UTS Web Application Development, Soal B).\n\n"
        "**Status stok:** Habis = 0 · Menipis = 1-10 pack · Aman = lebih dari 10 pack.\n\n"
        "**Aturan perubahan data:** nama bebas diisi; kategori dan lokasi gudang hanya dari daftar."
        "`/referensi`; stok hanya bisa berubah lewat endpoint tambah stok atau jual."
    ),
    version="1.0.0",
    openapi_tags=TAGS,
)

# allow frontend Vite (5173).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# kategori & lokasi dibatasi, hanya nama yang bebas diisi
class Kategori(str, Enum):
    arabika = "Arabika Single Origin"
    robusta = "Robusta Single Origin"
    blend = "Blend"
    spesial = "Spesial"

LOKASI_GUDANG = (
    "Gudang Tangerang - Rak A1",
    "Gudang Tangerang - Rak A2",
    "Gudang Tangerang - Rak A3",
    "Gudang Tangerang - Rak A4",
    "Gudang Tangerang - Rak A5",
    "Gudang Tangerang - Rak B1",
    "Gudang Tangerang - Rak B2",
    "Gudang Tangerang - Rak C1",
    "Gudang Tangerang - Rak C2",
    "Gudang Tangerang - Ruang Sejuk D1",
    "Gudang Tangerang - Ruang Sejuk D2",
    "Gudang Bandung - Rak A1",
    "Gudang Bandung - Rak A2",
    "Gudang Bandung - Rak A3",
    "Gudang Bandung - Rak A4",
    "Gudang Bandung - Rak B1",
    "Gudang Bandung - Rak B2",
    "Gudang Bandung - Rak C1",
    "Gudang Bandung - Ruang Sejuk D1",
)
LokasiGudang = Literal[LOKASI_GUDANG]

# skema request: field wajib, stok harus angka bulat >= 0 (string ditolak)
class BarangIn(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "nama": "Arabika Kerinci 200 gr",
                    "kategori": "Arabika Single Origin",
                    "jumlah_stok": 20,
                    "lokasi_gudang": "Gudang Bandung - Rak A4",
                }
            ]
        },
    )

    nama: str = Field(min_length=1, description="Nama produk, bebas diisi")
    kategori: Kategori = Field(description="Salah satu kategori dari /referensi")
    jumlah_stok: int = Field(ge=0, strict=True, description="Stok awal dalam pack, bilangan bulat >= 0")
    lokasi_gudang: LokasiGudang = Field(description="Salah satu lokasi dari /referensi")

# body tambah stok & jual: hanya jumlah, field lain ditolak
class JumlahStokIn(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={"examples": [{"jumlah": 5}]})

    jumlah: int = Field(ge=1, strict=True, description="Jumlah pack, bilangan bulat >= 1")

# skema response
class Barang(BaseModel):
    id: int
    nama: str
    kategori: Kategori
    jumlah_stok: int
    lokasi_gudang: LokasiGudang

class Referensi(BaseModel):
    kategori: list[str]
    lokasi_gudang: list[str]

class PesanRespons(BaseModel):
    pesan: str

class PesanError(BaseModel):
    detail: str

IdBarang = Annotated[int, PathParam(description="ID barang", examples=[1])]
GALAT_404 = {404: {"model": PesanError, "description": "Barang tidak ditemukan"}}

def muat_seed() -> list[dict]:
    with SEED_FILE.open(encoding="utf-8") as f:
        # validasi seed lewat skema
        return [Barang(**item).model_dump(mode="json") for item in json.load(f)]

# data in-memory, kembali ke seed tiap restart
barang_db: list[dict] = muat_seed()

def cari_barang(barang_id: int) -> dict:
    for barang in barang_db:
        if barang["id"] == barang_id:
            return barang
    raise HTTPException(status_code=404, detail="Barang tidak ditemukan")

@app.get("/", tags=["Root"], response_model=PesanRespons, summary="Cek status backend")
def baca_root():
    return {"pesan": "Backend inventory roastery jalan"}

@app.get(
    "/referensi",
    tags=["Referensi"],
    response_model=Referensi,
    summary="Ambil pilihan kategori & lokasi gudang",
    description="Dipakai frontend untuk mengisi dropdown form tambah barang.",
)
def ambil_referensi():
    return {"kategori": [k.value for k in Kategori], "lokasi_gudang": list(LOKASI_GUDANG)}

@app.get(
    "/barang",
    tags=["Barang"],
    response_model=list[Barang],
    summary="Ambil semua barang",
    description="Mengembalikan seluruh data barang. Pencarian, urutan, dan ringkasan dihitung di frontend.",
)
def ambil_semua_barang():
    return barang_db

@app.post(
    "/barang",
    tags=["Barang"],
    response_model=Barang,
    status_code=201,
    summary="Tambah barang baru",
    description="ID dibuat otomatis oleh backend. Kategori dan lokasi di luar daftar /referensi ditolak (422).",
)
def tambah_barang(barang: BarangIn):
    id_baru = max((b["id"] for b in barang_db), default=0) + 1
    barang_baru = {"id": id_baru, **barang.model_dump(mode="json")}
    barang_db.append(barang_baru)
    return barang_baru

@app.delete(
    "/barang/{barang_id}",
    tags=["Barang"],
    response_model=PesanRespons,
    responses=GALAT_404,
    summary="Hapus barang",
)
def hapus_barang(barang_id: IdBarang):
    for indeks, barang in enumerate(barang_db):
        if barang["id"] == barang_id:
            barang_db.pop(indeks)
            return {"pesan": "Barang dihapus"}
    raise HTTPException(status_code=404, detail="Barang tidak ditemukan")

@app.patch(
    "/barang/{barang_id}/stok",
    tags=["Stok"],
    response_model=Barang,
    responses=GALAT_404,
    summary="Tambah stok (barang masuk)",
    description="Stok bertambah sebanyak `jumlah`. Hanya stok yang berubah; field lain di body ditolak (422).",
)
def tambah_stok(barang_id: IdBarang, data: JumlahStokIn):
    barang = cari_barang(barang_id)
    barang["jumlah_stok"] += data.jumlah
    return barang

# jual: stok berkurang, tidak boleh melebihi stok yang ada
@app.patch(
    "/barang/{barang_id}/jual",
    tags=["Stok"],
    response_model=Barang,
    responses={
        **GALAT_404,
        409: {"model": PesanError, "description": "Jumlah melebihi stok yang tersedia"},
    },
    summary="Jual barang (barang keluar)",
    description="Stok berkurang sebanyak `jumlah`. Ditolak 409 kalau `jumlah` melebihi stok saat ini.",
)
def jual_barang(barang_id: IdBarang, data: JumlahStokIn):
    barang = cari_barang(barang_id)
    if data.jumlah > barang["jumlah_stok"]:
        raise HTTPException(status_code=409, detail=f"Stok tidak cukup, tersisa {barang['jumlah_stok']} pack")
    barang["jumlah_stok"] -= data.jumlah
    return barang
