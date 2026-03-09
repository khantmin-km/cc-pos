<script setup lang="ts">
import type { TableArea } from '@/types/pos'

const props = defineProps<{
  currentArea: TableArea
}>()

const emit = defineEmits<{
  (e: 'select', area: TableArea): void
}>()

const areas: { key: TableArea; label: string }[] = [
  { key: 'indoor', label: 'Indoor' },
  { key: 'outdoor', label: 'Outdoor' },
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
  margin: 0 0 1rem;
}

.tab {
  border: 1px solid var(--pos-border);
  background: white;
  color: var(--pos-text);
  padding: 0.5rem 0.75rem;
  border-radius: 999px;
  font-weight: 700;
  cursor: pointer;
}

.tab[data-active='true'] {
  background: var(--pos-primary);
  border-color: var(--pos-primary);
  color: white;
}
</style>

