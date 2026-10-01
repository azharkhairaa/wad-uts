<script setup>
import { ref } from "vue"
import { tambahBarang } from "../api"

defineProps({
  daftarKategori: { type: Array, default: () => [] },
  daftarLokasi: { type: Array, default: () => [] },
})
const emit = defineEmits(["tersimpan", "batal"])

const formKosong = () => ({ nama: "", kategori: "", jumlah_stok: 0, lokasi_gudang: "" })

// state lokal form
const form = ref(formKosong())
const menyimpan = ref(false)
const pesanError = ref("")

async function simpan() {
  menyimpan.value = true
  pesanError.value = ""
  try {
    const barangBaru = await tambahBarang(form.value)
    form.value = formKosong()
    emit("tersimpan", barangBaru)
  } catch (error) {
    pesanError.value = error.message
  } finally {
    menyimpan.value = false
  }
}
</script>

<template>
  <form class="form-barang" @submit.prevent="simpan">
    <h2>Tambah Barang</h2>

    <div class="form-grid">
      <label>
        Nama
        <input v-model="form.nama" required placeholder="mis. Arabika Kerinci 200 gr" />
      </label>
      <label>
        Kategori
        <select v-model="form.kategori" required>
          <option value="" disabled>Pilih kategori</option>
          <option v-for="kategori in daftarKategori" :key="kategori" :value="kategori">{{ kategori }}</option>
        </select>
      </label>
      <label>
        Jumlah Stok
        <input v-model.number="form.jumlah_stok" type="number" min="0" step="1" required />
      </label>
      <label>
        Lokasi Gudang
        <select v-model="form.lokasi_gudang" required>
          <option value="" disabled>Pilih lokasi gudang</option>
          <option v-for="lokasi in daftarLokasi" :key="lokasi" :value="lokasi">{{ lokasi }}</option>
        </select>
      </label>
    </div>

    <p v-if="pesanError" class="form-error">{{ pesanError }}</p>

    <div class="form-aksi">
      <button type="button" class="tombol-sekunder" @click="emit('batal')">Batal</button>
      <button type="submit" class="tombol-simpan" :disabled="menyimpan">{{ menyimpan ? "Menyimpan..." : "Simpan" }}</button>
    </div>
  </form>
</template>
