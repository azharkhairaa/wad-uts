<script setup>
import { computed, onMounted, ref } from "vue"
import { ambilSemuaBarang } from "./api"
import TabelBarang from "./components/TabelBarang.vue"

const daftarBarang = ref([])
const status = ref("loading") // loading | error | success
const pesanError = ref("")
const kataKunci = ref("")
const urutan = ref("az") // az | za

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

async function muatBarang() {
  status.value = "loading"
  try {
    daftarBarang.value = await ambilSemuaBarang()
    status.value = "success"
  } catch (error) {
    pesanError.value = error.message
    status.value = "error"
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
    <p v-if="status === 'loading'" class="info">Memuat data barang...</p>

    <div v-else-if="status === 'error'" class="info info-error">
      <p>{{ pesanError }}</p>
      <button type="button" @click="muatBarang">Coba lagi</button>
    </div>

    <template v-else>
      <div class="toolbar">
        <input v-model="kataKunci" type="search" class="input-cari" placeholder="Cari nama atau kategori..." />
        <div class="grup-urut">
          <button type="button" :class="{ aktif: urutan === 'az' }" @click="urutan = 'az'">A-Z</button>
          <button type="button" :class="{ aktif: urutan === 'za' }" @click="urutan = 'za'">Z-A</button>
        </div>
      </div>

      <p v-if="daftarBarang.length === 0" class="info">Belum ada barang di gudang.</p>
      <p v-else-if="barangTerurut.length === 0" class="info">
        Tidak ada barang yang cocok dengan "{{ kataKunci }}".
      </p>
      <template v-else>
        <p class="jumlah-hasil">Menampilkan {{ barangTerurut.length }} dari {{ daftarBarang.length }} barang</p>
        <TabelBarang :daftar-barang="barangTerurut" />
      </template>
    </template>
  </main>
</template>
