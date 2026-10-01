<script setup>
import { LABEL_STATUS, statusStok } from "../stok"

defineProps({
  daftarBarang: { type: Array, required: true },
  idSedangDihapus: { type: Number, default: null },
})
const emit = defineEmits(["hapus"])
</script>

<template>
  <table class="tabel">
    <thead>
      <tr>
        <th>Nama</th>
        <th>Kategori</th>
        <th class="angka">Stok</th>
        <th>Status</th>
        <th>Lokasi Gudang</th>
        <th></th>
      </tr>
    </thead>
    <TransitionGroup tag="tbody" name="baris">
      <tr v-for="barang in daftarBarang" :key="barang.id">
        <td>{{ barang.nama }}</td>
        <td>{{ barang.kategori }}</td>
        <td class="angka">{{ barang.jumlah_stok }}</td>
        <td>
          <span
            class="badge"
            :class="{
              'badge-aman': statusStok(barang.jumlah_stok) === 'aman',
              'badge-menipis': statusStok(barang.jumlah_stok) === 'menipis',
              'badge-habis': statusStok(barang.jumlah_stok) === 'habis',
            }"
          >
            {{ LABEL_STATUS[statusStok(barang.jumlah_stok)] }}
          </span>
        </td>
        <td>{{ barang.lokasi_gudang }}</td>
        <td class="kolom-aksi">
          <button
            type="button"
            class="tombol-hapus"
            :disabled="idSedangDihapus === barang.id"
            @click="emit('hapus', barang)"
          >
            {{ idSedangDihapus === barang.id ? "Menghapus..." : "Hapus" }}
          </button>
        </td>
      </tr>
    </TransitionGroup>
  </table>
</template>
