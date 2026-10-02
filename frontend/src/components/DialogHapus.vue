<script setup>
import { onMounted, ref } from "vue"
import { formatKemasan } from "../format"

defineProps({
  barang: { type: Object, required: true },
  menghapus: { type: Boolean, default: false },
})
const emit = defineEmits(["ya", "batal"])

const tombolBatal = ref(null)

// fokus ke Batal supaya Enter tidak langsung menghapus
onMounted(() => tombolBatal.value?.focus())
</script>

<template>
  <div class="dialog-latar" @click.self="emit('batal')">
    <div class="dialog dialog-hapus" role="alertdialog" aria-modal="true" @keydown.esc="emit('batal')">
      <h2>Hapus Barang</h2>
      <p class="dialog-nama">{{ barang.nama }} · {{ formatKemasan(barang.berat_gram) }}</p>
      <p class="dialog-pesan">
        Barang ini akan dihapus dari inventaris beserta stoknya ({{ barang.jumlah_stok }} pack).
        Tindakan ini tidak bisa dibatalkan.
      </p>

      <div class="form-aksi">
        <button ref="tombolBatal" type="button" class="tombol-sekunder" @click="emit('batal')">Batal</button>
        <button type="button" class="tombol-hapus" :disabled="menghapus" @click="emit('ya')">
          {{ menghapus ? "Menghapus..." : "Hapus" }}
        </button>
      </div>
    </div>
  </div>
</template>
