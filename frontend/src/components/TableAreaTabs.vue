<script setup lang="ts">
import type { TableArea } from '../types/pos'

defineProps<{
  currentArea: TableArea
}>()

defineEmits<{
  select: [area: TableArea]
}>()

const areas: TableArea[] = ['indoor', 'outdoor', 'garden']
</script>

<template>
  <div class="area-tabs">
    <button
      v-for="area in areas"
      :key="area"
      class="tab"
      :class="{ active: currentArea === area }"
      @click="$emit('select', area)"
    >
      {{ area }}
    </button>
  </div>
</template>

<style scoped>
.area-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tab {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: #e5e7eb;
  cursor: pointer;
  text-transform: capitalize;
}

.tab.active {
  background: var(--pos-primary);
  color: white;
}
</style>
