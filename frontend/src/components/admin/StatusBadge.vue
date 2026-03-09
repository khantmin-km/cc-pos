<script setup lang="ts">
import type { BillingStatus, TableStatus } from '@/types/pos'

const props = defineProps<{
  status: BillingStatus | TableStatus | string
  type: 'billing' | 'table'
}>()

const label = String(props.status).replace(/_/g, ' ')
</script>

<template>
  <span class="badge" :data-type="type" :data-status="status">
    {{ label }}
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  font-weight: 800;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  background: #e2e8f0;
  color: #0f172a;
}

.badge[data-type='billing'][data-status='active'] {
  background: #dbeafe;
  color: #1e3a8a;
}
.badge[data-type='billing'][data-status='bill_requested'] {
  background: #ffedd5;
  color: #7c2d12;
}
.badge[data-type='billing'][data-status='payment_completed'],
.badge[data-type='billing'][data-status='paid'] {
  background: #dcfce7;
  color: #14532d;
}
.badge[data-type='billing'][data-status='closed'] {
  background: #e5e7eb;
  color: #111827;
}
</style>

