<script setup lang="ts">
/**
 * Table Selection View
 * 
 * Main entry point for waiter UI.
 * Displays available and occupied tables with color coding:
 * - Available: Green
 * - Occupied: Red
 * 
 * Waiter can:
 * - Click available table → Start Service → Order Menu
 * - Click occupied table → View Orders → Order More / Request Bill
 * - Switch tables between occupied tables
 * - Attach multiple tables together
 * - Request receipt from occupied tables
 */

// Vue core imports
import {
  ref,
  onMounted,
  computed,
} from 'vue'

// Router imports
import { useRouter } from 'vue-router'

// Store imports
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'

// Type imports
import type { Table } from '@/types/pos'

// Component imports
import EnhancedTableCard from '@/components/EnhancedTableCard.vue'
import SwitchTableModal from '@/components/SwitchTableModal.vue'
import AttachTablesModal from '@/components/AttachTablesModal.vue'

// --------------------------------
// Setup
// --------------------------------

// Initialize router
const router = useRouter()

// Initialize stores
const tablesStore = useTablesStore()
const tableGroupsStore = useTableGroupsStore()

// Modal states
const showSwitchModal = ref(false)
const showAttachModal = ref(false)

// Computed properties
const availableTables = computed(() => 
  tablesStore.tables.filter(table => table.status === 'available')
)

const occupiedTables = computed(() => 
  tablesStore.tables.filter(table => table.status === 'occupied')
)

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
    router.push(`/waiter/menu/${table.id}`)
  } else if (table.status === 'occupied') {
    // Navigate to order management
    router.push(`/waiter/orders/${table.id}`)
  }
}

/**
 * Handle receipt request for occupied table
 * 
 * @param tableId - Table ID
 */
function handleReceiptRequest(tableId: string) {
  // Find the table group for this table
  const table = tablesStore.tables.find(t => t.id === tableId)
  if (table?.tableGroupId) {
    // Request bill for the table group
    tableGroupsStore.requestBill(table.tableGroupId)
  }
}

/**
 * Handle attach tables modal
 */
function handleAttachTables() {
  showAttachModal.value = true
}

/**
 * Handle switch tables modal
 */
function handleSwitchTables() {
  showSwitchModal.value = true
}

/**
 * Handle attach tables from modal
 */
function handleAttach(payload: { baseTableId: string; attachTableIds: string[] }) {
  // Add tables to the group
  payload.attachTableIds.forEach(tableId => {
    tableGroupsStore.addTableToGroup(payload.baseTableId, tableId)
  })
}

/**
 * Handle switch tables from modal
 */
function handleSwitch(payload: { fromTableId: string; toTableId: string }) {
  // Find the table group for the source table
  const sourceTable = tablesStore.tables.find(t => t.id === payload.fromTableId)
  if (sourceTable?.tableGroupId) {
    // Switch tables within the group
    tableGroupsStore.switchTable(sourceTable.tableGroupId, payload.fromTableId, payload.toTableId)
  }
}

/**
 * Handle bill request
 */
function handleBillRequest() {
  // This would open a modal to select which table to request bill for
  alert('Bill request feature - select occupied table to request bill')
}

/**
 * Handle logout
 */
function handleLogout() {
  // Clear session and redirect to login
  localStorage.removeItem('currentSession')
  router.push('/login')
}

/**
 * Get table items count
 */
function getTableItemsCount(table: Table) {
  // This would get actual items count from orders
  // For now, return a mock count
  return Math.floor(Math.random() * 10) + 1
}

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
</script>

<template>
  <div class="table-selection">
    <!-- Header -->
    <div class="header">
      <div class="header-left">
        <h1 class="title">KAUNG KAUNG</h1>
        <span class="subtitle">WAITER UI</span>
      </div>
      <div class="header-right">
        <div class="waiter-info">
          <span class="waiter-label">Waiter:</span>
          <span class="waiter-name">John Doe</span>
        </div>
        <button class="logout-btn" @click="handleLogout">
          Logout
        </button>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="action-buttons">
      <button class="action-btn attach-btn" @click="handleAttachTables">
        📎 Attach Tables
      </button>
      <button class="action-btn switch-btn" @click="handleSwitchTables">
        🔄 Switch Tables
      </button>
      <button class="action-btn bill-btn" @click="handleBillRequest">
        💳 Bill Request
      </button>
    </div>

    <!-- Table Grid -->
    <div v-if="tablesStore.loading" class="state">
      Loading tables…
    </div>

    <div v-else-if="tablesStore.error" class="state error">
      <div class="err-title">Couldn't load tables</div>
      <div class="err-msg">{{ tablesStore.error }}</div>
      <button
        type="button"
        class="retry"
        @click="tablesStore.fetchTables()"
      >
        Retry
      </button>
    </div>

    <div v-else-if="tablesStore.tablesByArea.length === 0" class="state">
      No tables found.
    </div>

    <div v-else class="table-grid">
      <EnhancedTableCard
        v-for="table in tablesStore.tablesByArea"
        :key="table.id"
        :table="table"
        @click="handleTableClick"
        @receipt-request="handleReceiptRequest"
      />
    </div>

    <!-- Modals -->
    <AttachTablesModal
      v-if="showAttachModal"
      :tables="tablesStore.tables"
      @close="showAttachModal = false"
      @attach="handleAttach"
    />

    <SwitchTableModal
      v-if="showSwitchModal"
      :tables="tablesStore.tables"
      @close="showSwitchModal = false"
      @switch="handleSwitch"
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

.header-actions {
  margin-left: auto;
}

.logout-btn {
  border: 1px solid var(--pos-border);
  background: white;
  border-radius: 999px;
  padding: 0.4rem 0.75rem;
  font-weight: 800;
  cursor: pointer;
}

.logout-btn:hover {
  background: var(--pos-primary);
  color: white;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  justify-content: center;
}

.action-btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.attach-btn {
  background: #3b82f6;
  color: white;
}

.attach-btn:hover {
  background: #2563eb;
  transform: translateY(-1px);
}

.switch-btn {
  background: #10b981;
  color: white;
}

.switch-btn:hover {
  background: #059669;
  transform: translateY(-1px);
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
</style>
