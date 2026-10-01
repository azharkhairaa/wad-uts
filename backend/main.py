import json
from enum import Enum
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

SEED_FILE = Path(__file__).parent / "data" / "seed_barang.json"

app = FastAPI(title="Inventory Roastery API")

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
    model_config = ConfigDict(str_strip_whitespace=True)

    nama: str = Field(min_length=1)
    kategori: Kategori
    jumlah_stok: int = Field(ge=0, strict=True)
    lokasi_gudang: LokasiGudang

# tambah stok: hanya boleh menambah, field lain tidak bisa diubah
class TambahStokIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    jumlah: int = Field(ge=1, strict=True)

# skema response
class Barang(BaseModel):
    id: int
    nama: str
    kategori: Kategori
    jumlah_stok: int
    lokasi_gudang: LokasiGudang

def muat_seed() -> list[dict]:
    with SEED_FILE.open(encoding="utf-8") as f:
        # validasi seed lewat skema
        return [Barang(**item).model_dump(mode="json") for item in json.load(f)]

# data in-memory, kembali ke seed tiap restart
barang_db: list[dict] = muat_seed()

@app.get("/")
def baca_root():
    return {"pesan": "Backend inventory roastery jalan"}

# pilihan dropdown di frontend
@app.get("/referensi")
def ambil_referensi():
    return {"kategori": [k.value for k in Kategori], "lokasi_gudang": list(LOKASI_GUDANG)}

@app.get("/barang", response_model=list[Barang])
def ambil_semua_barang():
    return barang_db

@app.post("/barang", response_model=Barang, status_code=201)
def tambah_barang(barang: BarangIn):
    id_baru = max((b["id"] for b in barang_db), default=0) + 1
    barang_baru = {"id": id_baru, **barang.model_dump(mode="json")}
    barang_db.append(barang_baru)
    return barang_baru

@app.delete("/barang/{barang_id}")
def hapus_barang(barang_id: int):
    for indeks, barang in enumerate(barang_db):
        if barang["id"] == barang_id:
            barang_db.pop(indeks)
            return {"pesan": "Barang dihapus"}
    raise HTTPException(status_code=404, detail="Barang tidak ditemukan")

@app.patch("/barang/{barang_id}/stok", response_model=Barang)
def tambah_stok(barang_id: int, data: TambahStokIn):
    for barang in barang_db:
        if barang["id"] == barang_id:
            barang["jumlah_stok"] += data.jumlah
            return barang
    raise HTTPException(status_code=404, detail="Barang tidak ditemukan")
