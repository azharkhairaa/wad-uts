<script setup>
import { computed } from "vue"
import { LABEL_STATUS, statusStok } from "../stok"

const props = defineProps({
  jumlah: { type: Number, required: true },
})

const status = computed(() => statusStok(props.jumlah))
</script>

<template>
  <span
    class="badge"
    :class="{
      'badge-aman': status === 'aman',
      'badge-menipis': status === 'menipis',
      'badge-habis': status === 'habis',
    }"
  >
    {{ LABEL_STATUS[status] }}
  </span>
</template>
