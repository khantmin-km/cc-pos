<script setup lang="ts">
import type { Table } from '@/types/pos'

const props = defineProps<{
  table: Table
}>()

const emit = defineEmits<{
  (e: 'click', table: Table): void
}>()

function onClick() {
  emit('click', props.table)
}
</script>

<template>
  <button type="button" class="card" @click="onClick">
    <div class="label">
      Table - {{ table.number }}
    </div>
    <span class="status-pill" :data-status="table.status" />
  </button>
</template>

<style scoped>
.card {
  width: 100%;
  border: none;
  background: #f8fafc;
  border-radius: 14px;
  padding: 0.9rem 1rem;
  cursor: pointer;
  text-align: left;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: box-shadow 0.12s ease, transform 0.06s ease;
}

.card:hover {
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.08);
  transform: translateY(-1px);
}

.label {
  font-size: 0.98rem;
  font-weight: 700;
  color: #4b5563;
}

.status-pill {
  width: 28px;
  height: 10px;
  border-radius: 999px;
  background: #d1d5db;
}

.status-pill[data-status='available'] {
  background: #22c55e;
}

.status-pill[data-status='reserved'] {
  background: #facc15;
}

.status-pill[data-status='occupied'] {
  background: #ef4444;
}
</style>

