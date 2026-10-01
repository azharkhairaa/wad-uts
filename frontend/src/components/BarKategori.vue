<script setup>
import { computed } from "vue"

const props = defineProps({
  daftarBarang: { type: Array, required: true },
})

// total stok & jumlah barang per kategori, lebar bar relatif ke kategori terbesar
const ringkasanKategori = computed(() => {
  const perKategori = props.daftarBarang.reduce((hasil, barang) => {
    const data = hasil[barang.kategori] ?? { kategori: barang.kategori, totalStok: 0, jumlahBarang: 0 }
    data.totalStok += barang.jumlah_stok
    data.jumlahBarang += 1
    hasil[barang.kategori] = data
    return hasil
  }, {})

  const daftar = Object.values(perKategori).sort((a, b) => b.totalStok - a.totalStok)
  const terbesar = Math.max(...daftar.map((kategori) => kategori.totalStok), 1)
  return daftar.map((kategori) => ({ ...kategori, lebar: (kategori.totalStok / terbesar) * 100 }))
})
</script>

<template>
  <section class="kartu-kategori">
    <h2>Ringkasan Stok per Kategori</h2>
    <ul class="bar-kategori">
      <li v-for="kategori in ringkasanKategori" :key="kategori.kategori">
        <div class="bar-label">
          <span>{{ kategori.kategori }}</span>
          <span class="bar-angka">{{ kategori.totalStok }} pack · {{ kategori.jumlahBarang }} barang</span>
        </div>
        <div class="bar-track">
          <div class="bar-isi" :style="{ width: `${kategori.lebar}%` }"></div>
        </div>
      </li>
    </ul>
  </section>
</template>
