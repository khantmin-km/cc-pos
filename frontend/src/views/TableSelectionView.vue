<script setup lang="ts">
/**
 * Table Selection View
 * 
 * Main entry point for the waiter UI.
 * Displays available tables and allows navigation
 * to menu or order management.
 */

// Vue core imports
import {
  ref,
  onMounted,
} from 'vue'

// Router imports
import { useRouter } from 'vue-router'

// Store imports
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'

// Type imports
import type { Table } from '@/types/pos'

// Component imports
import TableCard from '@/components/TableCard.vue'
import TableAreaTabs from '@/components/TableAreaTabs.vue'
import ReservedTableModal from '@/components/ReservedTableModal.vue'

// --------------------------------
// Setup
// --------------------------------

// Initialize router
const router = useRouter()

// Initialize stores
const tablesStore = useTablesStore()
const tableGroupsStore = useTableGroupsStore()

// --------------------------------
// State
// --------------------------------

/** Show reserved table warning modal */
const showReservedModal = ref(false)

/** Table number for reserved modal */
const reservedTableNumber = ref(0)

// --------------------------------
// Lifecycle
// --------------------------------

/**
 * On component mount:
 * Load data from backend API
 */
onMounted(async () => {
  // Fetch all tables
  await tablesStore.fetchTables()

  // Fetch open table groups
  await tableGroupsStore.fetchOpenGroups()
})

// --------------------------------
// Event Handlers
// --------------------------------

/**
 * Handle table card click
 * 
 * @param table - Clicked table object
 */
function handleTableClick(table: Table) {
  if (table.status === 'available') {
    // Navigate to menu for ordering
    router.push(`/menu/${table.id}`)

  } else if (table.status === 'reserved') {
    // Show reserved warning
    reservedTableNumber.value = table.number
    showReservedModal.value = true

  } else if (table.status === 'occupied') {
    // Navigate to order management
    router.push(`/orders/${table.id}`)
  }
}
</script>

<template>
  <div class="table-selection">
    <!-- Header -->
    <div class="header">
      <h1 class="title">
        KAUNG KAUNG
      </h1>
      <span class="subtitle">
        WAITER UI
      </span>
    </div>

    <!-- Banner -->
    <div class="banner">
      TABLE SELECTION
    </div>

    <!-- Area Filter Tabs -->
    <TableAreaTabs
      :current-area="tablesStore.currentArea"
      @select="tablesStore.setCurrentArea"
    />

    <!-- Table Grid -->
    <div class="table-grid">
      <TableCard
        v-for="table in tablesStore.tablesByArea"
        :key="table.id"
        :table="table"
        @click="handleTableClick"
      />
    </div>

    <!-- Reserved Modal -->
    <ReservedTableModal
      v-if="showReservedModal"
      :table-number="reservedTableNumber"
      @close="showReservedModal = false"
    />
  </div>
</template>

<style scoped>
.table-selection {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}

.header {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--pos-primary);
}

.subtitle {
  font-size: 0.9rem;
  color: var(--pos-text-muted);
}

.banner {
  background: var(--pos-primary);
  color: white;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 1rem;
}

.table-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
</style>
