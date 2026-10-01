<script setup>
import { computed, onMounted, ref } from "vue"
import { jualBarang, tambahStok } from "../api"
import BadgeStok from "./BadgeStok.vue"

const props = defineProps({
  barang: { type: Object, required: true },
  mode: { type: String, default: "tambah" }, // tambah | jual
})
const emit = defineEmits(["tersimpan", "batal"])

const jumlah = ref(1)
const menyimpan = ref(false)
const pesanError = ref("")
const inputJumlah = ref(null)

const modeJual = computed(() => props.mode === "jual")
const jumlahValid = computed(() => Number.isInteger(jumlah.value) && jumlah.value > 0)
const melebihiStok = computed(() => modeJual.value && jumlah.value > props.barang.jumlah_stok)

// review stok setelah disimpan, hitung kalau input valid
const stokBaru = computed(() => {
  if (!jumlahValid.value) return props.barang.jumlah_stok
  return modeJual.value
    ? Math.max(props.barang.jumlah_stok - jumlah.value, 0)
    : props.barang.jumlah_stok + jumlah.value
})

async function simpan() {
  menyimpan.value = true
  pesanError.value = ""
  try {
    const simpanKe = modeJual.value ? jualBarang : tambahStok
    const barangBaru = await simpanKe(props.barang.id, jumlah.value)
    emit("tersimpan", { barang: barangBaru, jumlah: jumlah.value, mode: props.mode })
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
    <form
      class="dialog"
      :class="{ 'dialog-jual': modeJual }"
      role="dialog"
      aria-modal="true"
      @submit.prevent="simpan"
      @keydown.esc="emit('batal')"
    >
      <h2>{{ modeJual ? "Jual Barang" : "Tambah Stok" }}</h2>
      <p class="dialog-nama">{{ barang.nama }}</p>

      <div class="dialog-stok">
        <span>Stok sekarang</span>
        <strong>{{ barang.jumlah_stok }} pack</strong>
        <BadgeStok :jumlah="barang.jumlah_stok" />
      </div>

      <label class="dialog-input">
        {{ modeJual ? "Jumlah dijual" : "Jumlah ditambahkan" }}
        <input
          ref="inputJumlah"
          v-model.number="jumlah"
          type="number"
          min="1"
          :max="modeJual ? barang.jumlah_stok : null"
          step="1"
          required
        />
      </label>

      <p v-if="melebihiStok" class="dialog-peringatan">Melebihi stok, maksimal {{ barang.jumlah_stok }} pack</p>

      <div class="dialog-stok">
        <span>{{ modeJual ? "Setelah dijual" : "Setelah ditambah" }}</span>
        <strong>{{ stokBaru }} pack</strong>
        <BadgeStok :jumlah="stokBaru" />
      </div>

      <p v-if="pesanError" class="form-error">{{ pesanError }}</p>

      <div class="form-aksi">
        <button type="button" class="tombol-sekunder" @click="emit('batal')">Batal</button>
        <button
          type="submit"
          :class="modeJual ? 'tombol-jual' : 'tombol-stok'"
          :disabled="menyimpan || melebihiStok"
        >
          {{ menyimpan ? "Menyimpan..." : modeJual ? "Jual" : "Simpan" }}
        </button>
      </div>
    </form>
  </div>
</template>
