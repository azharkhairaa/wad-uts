import json
from pathlib import Path

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


# skema request: field wajib, stok harus angka bulat >= 0 (string ditolak)
class BarangIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nama: str = Field(min_length=1)
    kategori: str = Field(min_length=1)
    jumlah_stok: int = Field(ge=0, strict=True)
    lokasi_gudang: str = Field(min_length=1)


# skema response
class Barang(BaseModel):
    id: int
    nama: str
    kategori: str
    jumlah_stok: int
    lokasi_gudang: str


def muat_seed() -> list[dict]:
    with SEED_FILE.open(encoding="utf-8") as f:
        # validasi seed lewat skema
        return [Barang(**item).model_dump() for item in json.load(f)]


# data in-memory, kembali ke seed tiap restart
barang_db: list[dict] = muat_seed()


@app.get("/")
def baca_root():
    return {"pesan": "Backend inventory roastery jalan"}


@app.get("/barang", response_model=list[Barang])
def ambil_semua_barang():
    return barang_db


@app.post("/barang", response_model=Barang, status_code=201)
def tambah_barang(barang: BarangIn):
    id_baru = max((b["id"] for b in barang_db), default=0) + 1
    barang_baru = {"id": id_baru, **barang.model_dump()}
    barang_db.append(barang_baru)
    return barang_baru


@app.delete("/barang/{barang_id}")
def hapus_barang(barang_id: int):
    for indeks, barang in enumerate(barang_db):
        if barang["id"] == barang_id:
            barang_db.pop(indeks)
            return {"pesan": "Barang dihapus"}
    raise HTTPException(status_code=404, detail="Barang tidak ditemukan")
