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
<<<<<<< HEAD
import { getRuntimeMode, onRuntimeModeChange, setRuntimeMode } from '@/services/runtimeMode'
=======
>>>>>>> df712ff (frontend_backend)

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
<<<<<<< HEAD
const mode = ref(getRuntimeMode())

onRuntimeModeChange(async (m) => {
  mode.value = m
  await Promise.allSettled([
    tablesStore.fetchTables(),
    tableGroupsStore.fetchOpenGroups(),
  ])
})
=======
>>>>>>> df712ff (frontend_backend)

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
<<<<<<< HEAD
      <button
        type="button"
        class="mode"
        :data-mode="mode"
        @click="setRuntimeMode(mode === 'demo' ? 'live' : 'demo')"
      >
        Mode: {{ mode }}
      </button>
=======
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    <div v-if="tablesStore.loading" class="state">
      Loading tables…
    </div>

    <div v-else-if="tablesStore.error" class="state error">
      <div class="err-title">Couldn’t load tables</div>
      <div class="err-msg">{{ tablesStore.error }}</div>
      <button
        type="button"
        class="retry"
        @click="tablesStore.fetchTables()"
      >
        Retry
      </button>
      <p class="hint">
        If the backend is failing, switch to <b>demo</b> mode.
      </p>
    </div>

    <div v-else-if="tablesStore.tablesByArea.length === 0" class="state">
      No tables found.
      <div class="hint">
        Switch to <b>demo</b> mode to see UI working with sample data.
      </div>
    </div>

    <div v-else class="table-grid">
=======
    <div class="table-grid">
>>>>>>> df712ff (frontend_backend)
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
  max-width: 720px;
  margin: 0 auto;
  padding: 1.5rem 1rem 2.5rem;
}

.header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.title {
  font-size: 1.6rem;
  font-weight: 800;
  color: #22c55e;
  letter-spacing: 0.05em;
}

.subtitle {
  font-size: 0.9rem;
  color: #9ca3af;
  font-weight: 700;
  letter-spacing: 0.08em;
}

<<<<<<< HEAD
.mode {
  margin-left: auto;
  border: 1px solid var(--pos-border);
  background: white;
  border-radius: 999px;
  padding: 0.4rem 0.75rem;
  font-weight: 800;
  cursor: pointer;
  font-size: 0.75rem;
}

.mode[data-mode='demo'] {
  border-color: #f59e0b;
  color: #92400e;
  background: #fffbeb;
}

=======
>>>>>>> df712ff (frontend_backend)
.banner {
  background: #22c55e;
  color: white;
  padding: 0.75rem 1.1rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.95rem;
  letter-spacing: 0.08em;
  margin-bottom: 1.1rem;
}

.table-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}
<<<<<<< HEAD

.state {
  margin-top: 1rem;
  background: white;
  border: 1px solid var(--pos-border);
  border-radius: 12px;
  padding: 1rem;
  font-weight: 700;
  color: var(--pos-text);
}

.state.error {
  border-color: #fecaca;
  background: #fff1f2;
}

.err-title {
  font-weight: 900;
}

.err-msg {
  margin-top: 0.5rem;
  font-weight: 600;
  color: #7f1d1d;
  white-space: pre-wrap;
}

.retry {
  margin-top: 0.75rem;
  border: none;
  background: var(--pos-primary);
  color: white;
  padding: 0.5rem 0.9rem;
  border-radius: 10px;
  font-weight: 900;
  cursor: pointer;
}

.hint {
  margin-top: 0.6rem;
  color: var(--pos-text-muted);
  font-weight: 600;
}
=======
>>>>>>> df712ff (frontend_backend)
</style>
