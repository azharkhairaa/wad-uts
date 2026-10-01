<script setup>
import { formatKemasan } from "../format"
import BadgeStok from "./BadgeStok.vue"

defineProps({
  daftarBarang: { type: Array, required: true },
  idSedangDihapus: { type: Number, default: null },
})
const emit = defineEmits(["hapus", "tambah-stok", "jual"])
</script>

<template>
  <div class="tabel-wrapper">
    <table class="tabel">
      <thead>
        <tr>
          <th>Nama</th>
          <th>Kategori</th>
          <th>Kemasan</th>
          <th class="angka">Stok (pack)</th>
          <th>Status</th>
          <th>Lokasi Gudang</th>
          <th></th>
        </tr>
      </thead>
      <TransitionGroup tag="tbody" name="baris">
        <tr v-for="barang in daftarBarang" :key="barang.id">
          <td class="kolom-nama">{{ barang.nama }}</td>
          <td data-label="Kategori">{{ barang.kategori }}</td>
          <td data-label="Kemasan">{{ formatKemasan(barang.berat_gram) }}</td>
          <td class="angka" data-label="Stok (pack)">{{ barang.jumlah_stok }}</td>
          <td data-label="Status">
            <BadgeStok :jumlah="barang.jumlah_stok" />
          </td>
          <td data-label="Lokasi">{{ barang.lokasi_gudang }}</td>
          <td class="kolom-aksi">
            <div class="aksi-baris">
              <button type="button" class="tombol-stok" @click="emit('tambah-stok', barang)">Tambah Stok</button>
              <button
                type="button"
                class="tombol-jual"
                :disabled="barang.jumlah_stok === 0"
                @click="emit('jual', barang)"
              >
                Jual
              </button>
              <button
                type="button"
                class="tombol-hapus"
                :disabled="idSedangDihapus === barang.id"
                @click="emit('hapus', barang)"
              >
                {{ idSedangDihapus === barang.id ? "Menghapus..." : "Hapus" }}
              </button>
            </div>
          </td>
        </tr>
      </TransitionGroup>
    </table>
  </div>
</template>
