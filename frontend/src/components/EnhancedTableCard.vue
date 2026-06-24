<script setup lang="ts">
import type { Table } from '@/types/pos'

const props = defineProps<{
  table: Table
}>()

const emit = defineEmits<{
  (e: 'click', table: Table): void
  (e: 'receipt-request', tableId: string): void
}>()

function onClick() {
  emit('click', props.table)
}

function onReceiptRequest(event: Event) {
  event.stopPropagation() // Prevent card click
  emit('receipt-request', props.table.id)
}
</script>

<template>
  <button type="button" class="card" @click="onClick">
    <div class="num">
      {{ table.number }}
    </div>
    <div class="meta">
      <span class="status" :data-status="table.status">
        {{ table.status }}
      </span>
      <span class="area">
        {{ table.area }}
      </span>
    </div>
    
    <!-- Receipt Request Button for Occupied Tables -->
    <button 
      v-if="table.status === 'occupied'"
      type="button"
      class="receipt-btn"
      @click="onReceiptRequest"
    >
      🧾 Receipt Request
    </button>
  </button>
</template>

<style scoped>
.card {
  width: 100%;
  border: 1px solid var(--pos-border);
  background: white;
  border-radius: 12px;
  padding: 0.75rem;
  cursor: pointer;
  text-align: left;
  transition: transform 0.05s ease, box-shadow 0.15s ease;
  position: relative;
}

.card:hover {
  box-shadow: 0 10px 20px rgba(2, 6, 23, 0.08);
  transform: translateY(-1px);
}

.num {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--pos-text);
  line-height: 1;
}

.meta {
  margin-top: 0.5rem;
  display: flex;
  justify-content: space-between;
  color: var(--pos-text-muted);
  font-weight: 600;
  font-size: 0.85rem;
}

.status {
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  background: #e2e8f0;
  color: #0f172a;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.7rem;
}

.status[data-status='available'] {
  background: #dcfce7;
  color: #14532d;
}

.status[data-status='reserved'] {
  background: #ffedd5;
  color: #7c2d12;
}

.status[data-status='occupied'] {
  background: #fee2e2;
  color: #7f1d1d;
}

.area {
  text-transform: capitalize;
}

.receipt-btn {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  background: #f59e0b;
  color: #78350f;
  border: none;
  border-radius: 8px;
  padding: 0.4rem 0.8rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.3rem;
  box-shadow: 0 2px 4px rgba(245, 158, 11, 0.2);
}

.receipt-btn:hover {
  background: #d97706;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(245, 158, 11, 0.3);
}

.receipt-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(245, 158, 11, 0.2);
}

/* Adjust card padding to accommodate receipt button */
.card {
  padding-bottom: 3rem;
}
</style>
