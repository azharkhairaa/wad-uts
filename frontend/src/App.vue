<script setup>
import { computed, onMounted, ref } from "vue"
import { ambilReferensi, ambilSemuaBarang, hapusBarang } from "./api"
import { formatKg } from "./format"
import { statusStok } from "./stok"
import BarKategori from "./components/BarKategori.vue"
import DialogHapus from "./components/DialogHapus.vue"
import DialogStok from "./components/DialogStok.vue"
import FormBarang from "./components/FormBarang.vue"
import TabelBarang from "./components/TabelBarang.vue"

const daftarBarang = ref([])
const referensi = ref({ kategori: [], berat_gram: [], lokasi_gudang: [] })
const status = ref("loading") // loading | error | success
const pesanError = ref("")
const kataKunci = ref("")
const urutan = ref("az") // az | za
const formTerbuka = ref(false)
const idSedangDihapus = ref(null)
const barangAkanDihapus = ref(null) // barang yang menunggu konfirmasi hapus
const aksiStok = ref(null) // { barang, mode: tambah | jual }
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

const totalBeratGram = computed(() =>
  daftarBarang.value.reduce((total, barang) => total + barang.jumlah_stok * barang.berat_gram, 0),
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

async function onStokDiubah({ barang, jumlah, mode }) {
  aksiStok.value = null
  const pesan =
    mode === "jual"
      ? `"${barang.nama}" terjual ${jumlah}, sisa ${barang.jumlah_stok} pack`
      : `Stok "${barang.nama}" +${jumlah}, sekarang ${barang.jumlah_stok} pack`
  tampilkanNotifikasi("sukses", pesan)
  await segarkanBarang()
}

// dipanggil setelah konfirmasi di DialogHapus
async function hapusTerkonfirmasi() {
  const barang = barangAkanDihapus.value
  idSedangDihapus.value = barang.id
  try {
    await hapusBarang(barang.id)
    tampilkanNotifikasi("sukses", `"${barang.nama}" dihapus`)
    await segarkanBarang()
  } catch (error) {
    tampilkanNotifikasi("error", error.message)
  } finally {
    idSedangDihapus.value = null
    barangAkanDihapus.value = null
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
            <p class="tile-sub">produk</p>
          </div>
          <div class="tile tile-peringatan">
            <p class="tile-label">Stok Menipis + Habis</p>
            <p class="tile-nilai">{{ jumlahPerluRestok }}</p>
            <p class="tile-sub">produk perlu restok</p>
          </div>
          <div class="tile">
            <p class="tile-label">Jumlah Kategori</p>
            <p class="tile-nilai">{{ jumlahKategori }}</p>
            <p class="tile-sub">kategori produk</p>
          </div>
          <div class="tile">
            <p class="tile-label">Total Unit (pack)</p>
            <p class="tile-nilai">{{ totalUnit.toLocaleString("id-ID") }}</p>
            <p class="tile-sub">total berat {{ formatKg(totalBeratGram) }}</p>
          </div>
        </section>

        <BarKategori :daftar-barang="daftarBarang" />

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
            :daftar-berat="referensi.berat_gram"
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
            <TabelBarang :daftar-barang="barangTerurut" :id-sedang-dihapus="idSedangDihapus" @hapus="barangAkanDihapus = $event" @tambah-stok="aksiStok = { barang: $event, mode: 'tambah' }"
              @jual="aksiStok = { barang: $event, mode: 'jual' }"
            />
          </div>
        </Transition>
      </div>
    </Transition>
  </main>

  <Transition name="dialog">
    <DialogStok
      v-if="aksiStok"
      :barang="aksiStok.barang"
      :mode="aksiStok.mode"
      @tersimpan="onStokDiubah"
      @batal="aksiStok = null"
    />
  </Transition>

  <Transition name="dialog">
    <DialogHapus
      v-if="barangAkanDihapus"
      :barang="barangAkanDihapus"
      :menghapus="idSedangDihapus !== null"
      @ya="hapusTerkonfirmasi"
      @batal="barangAkanDihapus = null"
    />
  </Transition>

  <Transition name="notif">
    <div v-if="notifikasi" class="notifikasi" :class="`notifikasi-${notifikasi.jenis}`" role="status">
      {{ notifikasi.pesan }}
    </div>
  </Transition>
</template>
