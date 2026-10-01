<script setup>
defineProps({
  daftarBarang: { type: Array, required: true },
})
</script>

<template>
  <table class="tabel">
    <thead>
      <tr>
        <th>Nama</th>
        <th>Kategori</th>
        <th class="angka">Stok</th>
        <th>Lokasi Gudang</th>
      </tr>
    </thead>
    <TransitionGroup tag="tbody" name="baris">
      <tr v-for="barang in daftarBarang" :key="barang.id">
        <td>{{ barang.nama }}</td>
        <td>{{ barang.kategori }}</td>
        <td class="angka">{{ barang.jumlah_stok }}</td>
        <td>{{ barang.lokasi_gudang }}</td>
      </tr>
    </TransitionGroup>
  </table>
</template>
