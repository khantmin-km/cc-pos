<script setup lang="ts">
/**
 * TableCard Component
 * 
 * Displays a table with its status for the table selection view.
 */

import type { Table } from '../types/pos'

defineProps<{
  table: Table
}>()

defineEmits<{
  click: [table: Table]
}>()
</script>

<template>
  <div 
    class="table-card"
    :class="`status-${table.status}`"
    @click="$emit('click', table)"
  >
    <span class="table-number">{{ table.number }}</span>
    <span class="table-status">{{ table.status }}</span>
  </div>
</template>

<style scoped>
.table-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.table-card:hover {
  transform: translateY(-2px);
}

.table-number {
  font-size: 1.5rem;
  font-weight: 700;
}

.table-status {
  font-size: 0.75rem;
  text-transform: uppercase;
  margin-top: 0.25rem;
}

.status-available {
  background: #22c55e;
  color: white;
}

.status-occupied {
  background: #ef4444;
  color: white;
}

.status-reserved {
  background: #f97316;
  color: white;
}
</style>
