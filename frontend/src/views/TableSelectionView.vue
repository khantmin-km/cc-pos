<script setup lang="ts">
/**
 * Table Selection View
 * 
 * Main entry point for the waiter UI.
 * Displays all tables and allows navigation
 * to menu or order management.
 */

// Vue core imports
import {
  ref,
  computed,
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
import ReservedTableModal from '@/components/ReservedTableModal.vue'

// --------------------------------
// Setup
// --------------------------------

// Initialize router
const router = useRouter()

// Initialize stores
const tablesStore = useTablesStore()
const tableGroupsStore = useTableGroupsStore()

// Show all tables
const allTables = computed(() => tablesStore.tables)

// --------------------------------
// State
// --------------------------------

/** Show reserved table warning modal */
const showReservedModal = ref(false)

/** Table number for reserved modal */
const reservedTableNumber = ref(0)

/** Show create group modal */
const showCreateGroupModal = ref(false)

/** Selected tables for new group */
const selectedTablesForGroup = ref<string[]>([])

/** Available tables for group creation (not occupied) */
const availableTables = computed(() => {
  return allTables.value.filter(t => t.status === 'available')
})

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

/**
 * Toggle table selection for group creation
 * 
 * @param tableId - Table ID to select/deselect
 */
function toggleTableSelection(tableId: string) {
  const idx = selectedTablesForGroup.value.indexOf(tableId)
  if (idx > -1) {
    selectedTablesForGroup.value.splice(idx, 1)
  } else {
    selectedTablesForGroup.value.push(tableId)
  }
}

/**
 * Handle creating a new table group from selected tables
 */
async function handleCreateTableGroup() {
  if (selectedTablesForGroup.value.length > 0) {
    // Start service on first selected table (creates a group)
    const firstTableId = selectedTablesForGroup.value[0]
    await tablesStore.startService(firstTableId)
    
    // Add remaining tables to the group if more than one selected
    if (selectedTablesForGroup.value.length > 1) {
      const groupId = tablesStore.tables.find(
        (t) => t.id === firstTableId
      )?.tableGroupId
      
      if (groupId) {
        for (let i = 1; i < selectedTablesForGroup.value.length; i++) {
          await tableGroupsStore.addTableToGroup(
            groupId,
            selectedTablesForGroup.value[i]
          )
        }
      }
    }
    
    // Reset and close modal
    selectedTablesForGroup.value = []
    showCreateGroupModal.value = false
    
    // Refresh data
    await Promise.all([
      tablesStore.fetchTables(),
      tableGroupsStore.fetchOpenGroups(),
    ])
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

    <!-- Action buttons -->
    <div class="actions">
      <button
        type="button"
        class="create-group-btn"
        @click="showCreateGroupModal = true"
      >
        ➕ Create Group
      </button>
    </div>

    <!-- Table Grid -->
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

    <div v-else-if="tablesStore.tables.length === 0" class="state">
      No tables found.
      <div class="hint">
        Switch to <b>demo</b> mode to see UI working with sample data.
      </div>
    </div>

    <div v-else class="table-grid">
      <TableCard
        v-for="table in allTables"
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

    <!-- Create Group Modal -->
    <div v-if="showCreateGroupModal" class="modal-overlay" @click.self="showCreateGroupModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Create Table Group</h2>
          <button type="button" class="close-btn" @click="showCreateGroupModal = false">✕</button>
        </div>

        <div class="modal-body">
          <p class="instruction">Select tables to group together:</p>
          
          <div class="table-selection-grid">
            <button
              v-for="table in availableTables"
              :key="table.id"
              type="button"
              class="table-selector"
              :data-selected="selectedTablesForGroup.includes(table.id)"
              @click="toggleTableSelection(table.id)"
            >
              Table {{ table.number }}
            </button>
          </div>

          <p v-if="selectedTablesForGroup.length === 0" class="no-selection">
            Select at least one table
          </p>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="btn-cancel"
            @click="showCreateGroupModal = false"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn-create"
            :disabled="selectedTablesForGroup.length === 0"
            @click="handleCreateTableGroup"
          >
            Create Group
          </button>
        </div>
      </div>
    </div>
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

.actions {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.1rem;
  flex-wrap: wrap;
}

.create-group-btn {
  border: none;
  background: #3b82f6;
  color: white;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  font-size: 0.9rem;
}

.create-group-btn:hover {
  background: #2563eb;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 100%;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  font-size: 1.25rem;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.close-btn {
  border: none;
  background: transparent;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.modal-body {
  padding: 1.5rem;
}

.instruction {
  margin: 0 0 1rem;
  font-weight: 700;
  color: #111827;
}

.table-selection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.table-selector {
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  color: #111827;
}

.table-selector:hover {
  border-color: #22c55e;
  background: #f0fdf4;
}

.table-selector[data-selected='true'] {
  background: #22c55e;
  color: white;
  border-color: #16a34a;
}

.no-selection {
  color: #9ca3af;
  font-weight: 600;
  font-size: 0.9rem;
}

.modal-footer {
  display: flex;
  gap: 0.75rem;
  padding: 1.25rem;
  border-top: 1px solid #e5e7eb;
  justify-content: flex-end;
}

.btn-cancel {
  padding: 0.6rem 1rem;
  border: 1px solid #e5e7eb;
  background: white;
  color: #111827;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}

.btn-create {
  padding: 0.6rem 1rem;
  border: none;
  background: #22c55e;
  color: white;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}

.btn-create:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}
</style>
