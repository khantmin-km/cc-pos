<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
  type?: 'table' | 'billing' | 'order'
}>()

const statusClass = computed(() => {
  const map: Record<string, string> = {
    pending: 'status-orange',
    kitchen_printed: 'status-orange',
    served: 'status-green',
    removed: 'status-gray',
    active: 'status-green',
    bill_requested: 'status-red',
    payment_completed: 'status-green',
    closed: 'status-gray',
    available: 'status-green',
    reserved: 'status-orange',
    occupied: 'status-red'
  }
  return `status-badge ${map[props.status] || 'status-gray'}`
})

const statusLabel = computed(() => {
  const map: Record<string, string> = {
    pending: 'Pending',
    kitchen_printed: 'Kitchen Printed',
    served: 'Served',
    removed: 'Removed',
    active: 'Active',
    bill_requested: 'Bill Requested',
    payment_completed: 'Payment Completed',
    closed: 'Closed',
    available: 'Available',
    reserved: 'Reserved',
    occupied: 'Occupied'
  }
  return map[props.status] || props.status
})
</script>

<template>
  <span :class="statusClass">{{ statusLabel }}</span>
</template>

<style scoped>
.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-green {
  background: #22c55e;
  color: white;
}

.status-orange {
  background: #f97316;
  color: white;
}

.status-red {
  background: #ef4444;
  color: white;
}

.status-gray {
  background: #6b7280;
  color: white;
}
</style>
