<script setup>
import { computed, onMounted, ref } from "vue"
import { ambilReferensi, ambilSemuaBarang, hapusBarang } from "./api"
import { statusStok } from "./stok"
import FormBarang from "./components/FormBarang.vue"
import TabelBarang from "./components/TabelBarang.vue"

const daftarBarang = ref([])
const referensi = ref({ kategori: [], lokasi_gudang: [] })
const status = ref("loading") // loading | error | success
const pesanError = ref("")
const kataKunci = ref("")
const urutan = ref("az") // az | za
const formTerbuka = ref(false)
const idSedangDihapus = ref(null)
const notifikasi = ref(null) // { jenis: sukses | error, pesan }

// cari berdasarkan nama atau kategori
const barangTersaring = computed(() => {
  const kunci = kataKunci.value.trim().toLowerCase()
  if (!kunci) return daftarBarang.value
  return daftarBarang.value.filter(
    (barang) =>
      barang.nama.toLowerCase().includes(kunci) ||
      barang.kategori.toLowerCase().includes(kunci),
  )
})

// urutkan hasil pencarian berdasarkan nama (computed berantai)
const barangTerurut = computed(() => {
  const hasil = [...barangTersaring.value].sort((a, b) => a.nama.localeCompare(b.nama, "id"))
  return urutan.value === "az" ? hasil : hasil.reverse()
})

// ringkasan dihitung dari seluruh data
const totalBarang = computed(() => daftarBarang.value.length)

const jumlahPerluRestok = computed(
  () => daftarBarang.value.filter((barang) => statusStok(barang.jumlah_stok) !== "aman").length,
)

const jumlahKategori = computed(() => new Set(daftarBarang.value.map((barang) => barang.kategori)).size)

const totalUnit = computed(() =>
  daftarBarang.value.reduce((total, barang) => total + barang.jumlah_stok, 0),
)

async function muatBarang() {
  status.value = "loading"
  try {
    const [barang, dataReferensi] = await Promise.all([ambilSemuaBarang(), ambilReferensi()])
    daftarBarang.value = barang
    referensi.value = dataReferensi
    status.value = "success"
  } catch (error) {
    pesanError.value = error.message
    status.value = "error"
  }
}

// muat ulang tanpa layar loading, dipakai setelah tambah/hapus
async function segarkanBarang() {
  try {
    daftarBarang.value = await ambilSemuaBarang()
  } catch (error) {
    tampilkanNotifikasi("error", error.message)
  }
}

let timerNotifikasi
function tampilkanNotifikasi(jenis, pesan) {
  notifikasi.value = { jenis, pesan }
  clearTimeout(timerNotifikasi)
  timerNotifikasi = setTimeout(() => (notifikasi.value = null), 3000)
}

async function onBarangTersimpan(barang) {
  formTerbuka.value = false
  tampilkanNotifikasi("sukses", `"${barang.nama}" ditambahkan`)
  await segarkanBarang()
}

async function onHapus(barang) {
  if (!confirm(`Hapus "${barang.nama}" dari inventaris?`)) return
  idSedangDihapus.value = barang.id
  try {
    await hapusBarang(barang.id)
    tampilkanNotifikasi("sukses", `"${barang.nama}" dihapus`)
    await segarkanBarang()
  } catch (error) {
    tampilkanNotifikasi("error", error.message)
  } finally {
    idSedangDihapus.value = null
  }
}

onMounted(muatBarang)
</script>

<template>
  <header class="header">
    <h1>Roastery Inventory</h1>
    <p>Stok biji kopi di gudang</p>
  </header>

  <main class="konten">
    <Transition name="pudar" mode="out-in">
      <div v-if="status === 'loading'" class="info info-loading">
        <span class="spinner" aria-hidden="true"></span>
        <p>Memuat data barang...</p>
      </div>

      <div v-else-if="status === 'error'" class="info info-error">
        <p>{{ pesanError }}</p>
        <button type="button" @click="muatBarang">Coba lagi</button>
      </div>

      <div v-else>
        <section class="ringkasan">
          <div class="tile">
            <p class="tile-label">Total Barang</p>
            <p class="tile-nilai">{{ totalBarang }}</p>
          </div>
          <div class="tile tile-peringatan">
            <p class="tile-label">Stok Menipis + Habis</p>
            <p class="tile-nilai">{{ jumlahPerluRestok }}</p>
          </div>
          <div class="tile">
            <p class="tile-label">Jumlah Kategori</p>
            <p class="tile-nilai">{{ jumlahKategori }}</p>
          </div>
          <div class="tile">
            <p class="tile-label">Total Unit</p>
            <p class="tile-nilai">{{ totalUnit.toLocaleString("id-ID") }}</p>
          </div>
        </section>

        <div class="toolbar">
          <input v-model="kataKunci" type="search" class="input-cari" placeholder="Cari nama atau kategori..." />
          <div class="grup-urut">
            <button type="button" :class="{ aktif: urutan === 'az' }" @click="urutan = 'az'">A-Z</button>
            <button type="button" :class="{ aktif: urutan === 'za' }" @click="urutan = 'za'">Z-A</button>
          </div>
          <button type="button" class="tombol-tambah" @click="formTerbuka = !formTerbuka">
            {{ formTerbuka ? "Tutup Form" : "+ Tambah Barang" }}
          </button>
        </div>

        <Transition name="pudar">
          <FormBarang
            v-if="formTerbuka"
            :daftar-kategori="referensi.kategori"
            :daftar-lokasi="referensi.lokasi_gudang"
            @tersimpan="onBarangTersimpan"
            @batal="formTerbuka = false"
          />
        </Transition>

        <Transition name="pudar" mode="out-in">
          <p v-if="daftarBarang.length === 0" class="info">Belum ada barang di gudang.</p>
          <p v-else-if="barangTerurut.length === 0" class="info">
            Tidak ada barang yang cocok dengan "{{ kataKunci }}".
          </p>
          <div v-else>
            <p class="jumlah-hasil">Menampilkan {{ barangTerurut.length }} dari {{ daftarBarang.length }} barang</p>
            <TabelBarang :daftar-barang="barangTerurut" :id-sedang-dihapus="idSedangDihapus" @hapus="onHapus" />
          </div>
        </Transition>
      </div>
    </Transition>
  </main>

  <Transition name="notif">
    <div v-if="notifikasi" class="notifikasi" :class="`notifikasi-${notifikasi.jenis}`" role="status">
      {{ notifikasi.pesan }}
    </div>
  </Transition>
</template>
