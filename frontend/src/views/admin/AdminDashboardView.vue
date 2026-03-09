<script setup lang="ts">
import { computed, onMounted } from 'vue'

import AdminCard from '@/components/admin/AdminCard.vue'
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'

const tablesStore = useTablesStore()
const groupsStore = useTableGroupsStore()

onMounted(async () => {
  await Promise.allSettled([tablesStore.fetchTables(), groupsStore.fetchOpenGroups()])
})

const activeGroups = computed(() => groupsStore.tableGroups.length)
const pendingKitchenOrders = computed(() => 0)
const totalMenuItems = computed(() => 11)
const availableItems = computed(() => 11)
</script>

<template>
  <div class="grid">
    <AdminCard title="Active Table Groups">
      <div class="metric">
        <div class="num">{{ activeGroups }}</div>
        <div class="label">ACTIVE TABLE GROUPS</div>
      </div>
    </AdminCard>

    <AdminCard title="Pending Kitchen Orders">
      <div class="metric">
        <div class="num">{{ pendingKitchenOrders }}</div>
        <div class="label">PENDING KITCHEN ORDERS</div>
      </div>
    </AdminCard>

    <AdminCard title="Total Menu Items">
      <div class="metric">
        <div class="num">{{ totalMenuItems }}</div>
        <div class="label">TOTAL MENU ITEMS</div>
      </div>
    </AdminCard>

    <AdminCard title="Available Items">
      <div class="metric">
        <div class="num">{{ availableItems }}</div>
        <div class="label">AVAILABLE ITEMS</div>
      </div>
    </AdminCard>
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.metric {
  padding: 6px 2px;
  text-align: center;
}

.num {
  font-size: 32px;
  font-weight: 900;
  color: #22c55e;
}

.label {
  margin-top: 6px;
  font-size: 11px;
  letter-spacing: 0.08em;
  font-weight: 900;
  color: #94a3b8;
}

@media (max-width: 1100px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>

