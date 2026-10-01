import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

SEED_FILE = Path(__file__).parent / "data" / "seed_barang.json"

app = FastAPI(title="Inventory Roastery API")

# allow frontend Vite (5173).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
