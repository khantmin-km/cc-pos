<script setup lang="ts">
import type { TableArea } from '@/types/pos'

const props = defineProps<{
  currentArea: TableArea
}>()

const emit = defineEmits<{
  (e: 'select', area: TableArea): void
}>()

const areas: { key: TableArea; label: string }[] = [
  { key: 'indoor', label: 'IN-door' },
  { key: 'outdoor', label: 'Out-door' },
  { key: 'garden', label: 'Garden' },
]
</script>

<template>
  <div class="tabs">
    <button
      v-for="a in areas"
      :key="a.key"
      type="button"
      class="tab"
      :data-active="a.key === props.currentArea"
      @click="emit('select', a.key)"
    >
      {{ a.label }}
    </button>
  </div>
</template>

<style scoped>
.tabs {
  display: flex;
  gap: 0.5rem;
  margin: 0 0 1.2rem;
}

.tab {
  border: 1px solid #22c55e;
  background: white;
  color: #16a34a;
  padding: 0.45rem 0.95rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.8rem;
  cursor: pointer;
}

.tab[data-active='true'] {
  background: #22c55e;
  border-color: #22c55e;
  color: #ffffff;
}
</style>

