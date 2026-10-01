<script setup>
import { computed, onMounted, ref } from "vue"
import { tambahStok } from "../api"
import BadgeStok from "./BadgeStok.vue"

const props = defineProps({
  barang: { type: Object, required: true },
})
const emit = defineEmits(["tersimpan", "batal"])

const jumlah = ref(1)
const menyimpan = ref(false)
const pesanError = ref("")
const inputJumlah = ref(null)

// review stok setelah ditambah, hitung kalau input valid
const stokBaru = computed(() => {
  const tambah = Number.isInteger(jumlah.value) && jumlah.value > 0 ? jumlah.value : 0
  return props.barang.jumlah_stok + tambah
})

async function simpan() {
  menyimpan.value = true
  pesanError.value = ""
  try {
    const barangBaru = await tambahStok(props.barang.id, jumlah.value)
    emit("tersimpan", { barang: barangBaru, jumlah: jumlah.value })
  } catch (error) {
    pesanError.value = error.message
  } finally {
    menyimpan.value = false
  }
}

onMounted(() => inputJumlah.value?.focus())
</script>

<template>
  <div class="dialog-latar" @click.self="emit('batal')">
    <form class="dialog" role="dialog" aria-modal="true" @submit.prevent="simpan" @keydown.esc="emit('batal')">
      <h2>Tambah Stok</h2>
      <p class="dialog-nama">{{ barang.nama }}</p>

      <div class="dialog-stok">
        <span>Stok sekarang</span>
        <strong>{{ barang.jumlah_stok }} pack</strong>
        <BadgeStok :jumlah="barang.jumlah_stok" />
      </div>

      <label class="dialog-input">
        Jumlah ditambahkan
        <input ref="inputJumlah" v-model.number="jumlah" type="number" min="1" step="1" required />
      </label>

      <div class="dialog-stok">
        <span>Setelah ditambah</span>
        <strong>{{ stokBaru }} pack</strong>
        <BadgeStok :jumlah="stokBaru" />
      </div>

      <p v-if="pesanError" class="form-error">{{ pesanError }}</p>

      <div class="form-aksi">
        <button type="button" class="tombol-sekunder" @click="emit('batal')">Batal</button>
        <button type="submit" class="tombol-stok" :disabled="menyimpan">
          {{ menyimpan ? "Menyimpan..." : "Simpan" }}
        </button>
      </div>
    </form>
  </div>
</template>
