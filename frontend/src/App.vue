<script setup>
import { onMounted, ref } from "vue"
import { ambilSemuaBarang } from "./api"
import TabelBarang from "./components/TabelBarang.vue"

const daftarBarang = ref([])
const status = ref("loading") // loading | error | success
const pesanError = ref("")

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

    <p v-else-if="daftarBarang.length === 0" class="info">Belum ada barang di gudang.</p>

    <TabelBarang v-else :daftar-barang="daftarBarang" />
  </main>
</template>
