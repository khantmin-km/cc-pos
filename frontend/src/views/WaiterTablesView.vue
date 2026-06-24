<script setup lang="ts">
/**
 * Enhanced Waiter Tables View
 * 
 * Main entry point for waiter operations.
 * Displays table status cards with full workflow:
 * - Available tables (green) → Start Service
 * - Occupied tables (red) → View Items, Request Bill, Add Orders
 * - Switch & Attach tables functionality
 */

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'
import { getRuntimeMode } from '@/services/runtimeMode'

// --------------------------------
// Setup
// --------------------------------

const router = useRouter()
const tablesStore = useTablesStore()
const tableGroupsStore = useTableGroupsStore()

// --------------------------------
// State
// --------------------------------

/** Modal visibility */
const showSwitchModal = ref(false)
const showAttachModal = ref(false)

/** Switch operation - source and target tables */
const switchFromTable = ref<string | null>(null)
const switchToTable = ref<string | null>(null)

/** Attach operation - tables to attach */
const attachSelectedTableIds = ref<Set<string>>(new Set())

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  await tablesStore.fetchTables()
  await tableGroupsStore.fetchOpenGroups()
})

// --------------------------------
// Computed
// --------------------------------

const tables = computed(() => tablesStore.tables || [])

const tableGroups = computed(() => tableGroupsStore.openGroups || [])

/** Occupied tables for switch modal */
const occupiedTables = computed(() => {
  return tables.value.filter(t => t.status === 'occupied')
})

/** Available tables for switch modal */
const availableTablesForSwitch = computed(() => {
  return tables.value.filter(t => t.status === 'available')
})

/** Available tables for attach modal */
const availableTablesForAttach = computed(() => {
  return tables.value.filter(t => t.status === 'available')
})

/** Get table status color */
function getTableStatusColor(table: any): string {
  if (table.status === 'available') return '#10b981' // Green
  if (table.status === 'occupied') return '#ef4444' // Red
  return '#6b7280' // Gray for reserved
}

/** Get a table by ID */
function getTableById(tableId: string | null) {
  if (!tableId) return null
  return tables.value.find(t => t.id === tableId) || null
}

// --------------------------------
// Event Handlers
// --------------------------------

/**
 * Handle table card click - navigate to table details or start service
 */
function handleTableClick(table: any) {
  if (table.status === 'available') {
    handleStartService(table)
  } else if (table.status === 'occupied') {
    showTableDetails(table)
  }
}

/**
 * Open switch tables modal
 */
function handleSwitchTables() {
  switchFromTable.value = null
  switchToTable.value = null
  showSwitchModal.value = true
}

/**
 * Open attach tables modal
 */
function handleAttachTables() {
  attachSelectedTableIds.value.clear()
  showAttachModal.value = true
}

/**
 * Select table in switch modal (FROM column - occupied)
 */
function selectSwitchFrom(tableId: string) {
  switchFromTable.value = tableId
}

/**
 * Select table in switch modal (TO column - available)
 */
function selectSwitchTo(tableId: string) {
  switchToTable.value = tableId
}

/**
 * Execute switch tables operation
 */
async function executeSwitchTables() {
  if (!switchFromTable.value || !switchToTable.value) {
    alert('Please select both an occupied table (FROM) and an available table (TO)')
    return
  }

  const fromTable = getTableById(switchFromTable.value)
  const toTable = getTableById(switchToTable.value)

  if (!fromTable?.tableGroupId) {
    alert('Source table has no active table group')
    return
  }

  try {
    await tableGroupsStore.switchTable(
      fromTable.tableGroupId,
      switchFromTable.value,
      switchToTable.value
    )

    alert(`Tables switched: ${fromTable.tableCode} → ${toTable?.tableCode}\n${fromTable.tableCode} is now available`)
    closeSwitchModal()
    await tablesStore.fetchTables()
    await tableGroupsStore.fetchOpenGroups()
  } catch (error) {
    console.error('Failed to switch tables:', error)
    alert('Failed to switch tables: ' + (error instanceof Error ? error.message : 'Unknown error'))
  }
}

/**
 * Toggle table selection in attach modal
 */
function toggleAttachTable(tableId: string) {
  if (attachSelectedTableIds.value.has(tableId)) {
    attachSelectedTableIds.value.delete(tableId)
  } else {
    attachSelectedTableIds.value.add(tableId)
  }
}

/**
 * Execute attach tables operation
 */
async function executeAttachTables() {
  if (attachSelectedTableIds.value.size < 2) {
    alert('Please select at least 2 available tables to attach')
    return
  }

  const selectedTables = tables.value.filter(t => attachSelectedTableIds.value.has(t.id))
  const tableNames = selectedTables.map(t => t.tableCode).join(', ')

  try {
    // Create new group with first table
    const baseTableId = Array.from(attachSelectedTableIds.value)[0]
    const group = await tablesStore.startService(baseTableId)

    // Attach remaining tables
    const remainingTables = Array.from(attachSelectedTableIds.value).slice(1)
    for (const tableId of remainingTables) {
      await tableGroupsStore.addTableToGroup(group.id, tableId)
    }

    alert(`Tables attached: ${tableNames}`)
    closeAttachModal()
    await tablesStore.fetchTables()
    await tableGroupsStore.fetchOpenGroups()
  } catch (error) {
    console.error('Failed to attach tables:', error)
    alert('Failed to attach tables: ' + (error instanceof Error ? error.message : 'Unknown error'))
  }
}

/**
 * Close switch modal
 */
function closeSwitchModal() {
  showSwitchModal.value = false
  switchFromTable.value = null
  switchToTable.value = null
}

/**
 * Close attach modal
 */
function closeAttachModal() {
  showAttachModal.value = false
  attachSelectedTableIds.value.clear()
}

/**
 * Start service on available table
 */
async function handleStartService(table: any) {
  try {
    await tablesStore.startService(table.id)
    router.push(`/waiter/menu/${table.id}`)
  } catch (error) {
    console.error('Failed to start service:', error)
    alert('Failed to start service. Please try again.')
  }
}

/**
 * Show occupied table details
 */
function showTableDetails(table: any) {
  router.push(`/waiter/orders/${table.id}`)
}

/**
 * Go to menu for occupied table
 */
function goToMenu(table: any) {
  router.push(`/waiter/menu/${table.id}`)
}

/**
 * Request bill for occupied table
 */
async function requestBill(table: any) {
  if (!table.tableGroupId) {
    alert('No active group for this table')
    return
  }
  
  try {
    await tableGroupsStore.requestBill(table.tableGroupId)
    alert(`Bill requested for ${table.tableCode}`)
  } catch (error) {
    console.error('Failed to request bill:', error)
    alert('Failed to request bill')
  }
}

</script>

<template>
  <div class="waiter-tables-view">
    <!-- Header -->
    <div class="page-header">
      <div class="brand">KAUNG KAUNG <span class="brand-subtitle">WAITER UI</span></div>
    </div>

    <!-- Table Selection Section -->
    <div class="table-selection-header">
      <h2>TABLE SELECTION</h2>
    </div>

    <!-- Status Legend -->
    <div class="status-legend">
      <div class="legend-item">
        <div class="legend-dot" style="background-color: #10b981;"></div>
        <span>Available</span>
      </div>
      <div class="legend-item">
        <div class="legend-dot" style="background-color: #ef4444;"></div>
        <span>Occupied</span>
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
    </div>

    <!-- Main content -->
    <div class="content">
      <div class="tables-grid">
        <div
          v-for="table in tables"
          :key="table.id"
          class="table-card"
          :class="{ occupied: table.status === 'occupied', available: table.status === 'available' }"
        >
          <div class="table-header" @click="handleTableClick(table)">
            <div class="table-name">{{ table.tableCode }}</div>
            <div class="status-pill" :style="{ backgroundColor: getTableStatusColor(table) }"></div>
          </div>
          
          <!-- Action buttons for available tables -->
          <div v-if="table.status === 'available'" class="table-actions">
            <button class="action-btn-small start-service-btn" @click.stop="handleStartService(table)">
              ▶️ Start Service
            </button>
          </div>
          
          <!-- Action buttons for occupied tables -->
          <div v-if="table.status === 'occupied'" class="table-actions">
            <button class="action-btn-small menu-btn" @click.stop="goToMenu(table)">
              📝 Order
            </button>
            <button class="action-btn-small bill-btn" @click.stop="requestBill(table)">
              🧾 Bill
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Switch Tables Modal -->
    <div v-if="showSwitchModal" class="modal-overlay" @click.self="closeSwitchModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>🔄 Switch Tables</h2>
          <button class="close-btn" @click="closeSwitchModal">✕</button>
        </div>

        <p class="modal-description">
          Move an occupied table's orders to an available table, making the occupied one available again.
        </p>

        <div class="modal-columns">
          <!-- FROM Column (Occupied Tables) -->
          <div class="column">
            <div class="column-header from-header">
              <h3>FROM (Occupied)</h3>
              <span class="selection-badge" v-if="switchFromTable">
                {{ getTableById(switchFromTable)?.tableCode }}
              </span>
            </div>
            <div class="column-body">
              <div v-if="occupiedTables.length === 0" class="empty-column">
                No occupied tables
              </div>
              <div
                v-for="table in occupiedTables"
                :key="table.id"
                class="table-option"
                :class="{ selected: switchFromTable === table.id }"
                @click="selectSwitchFrom(table.id)"
              >
                <div class="table-option-name">{{ table.tableCode }}</div>
                <div class="table-option-status">🔴 Occupied</div>
              </div>
            </div>
          </div>

          <!-- TO Column (Available Tables) -->
          <div class="column">
            <div class="column-header to-header">
              <h3>TO (Available)</h3>
              <span class="selection-badge" v-if="switchToTable">
                {{ getTableById(switchToTable)?.tableCode }}
              </span>
            </div>
            <div class="column-body">
              <div v-if="availableTablesForSwitch.length === 0" class="empty-column">
                No available tables
              </div>
              <div
                v-for="table in availableTablesForSwitch"
                :key="table.id"
                class="table-option"
                :class="{ selected: switchToTable === table.id }"
                @click="selectSwitchTo(table.id)"
              >
                <div class="table-option-name">{{ table.tableCode }}</div>
                <div class="table-option-status">🟢 Available</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Swap arrow indicator -->
        <div class="swap-arrow">
          <span>→</span>
        </div>

        <!-- Action buttons -->
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeSwitchModal">Cancel</button>
          <button
            class="btn-confirm"
            :disabled="!switchFromTable || !switchToTable"
            @click="executeSwitchTables"
          >
            Switch Tables
          </button>
        </div>
      </div>
    </div>

    <!-- Attach Tables Modal -->
    <div v-if="showAttachModal" class="modal-overlay" @click.self="closeAttachModal">
      <div class="modal-content attach-modal">
        <div class="modal-header">
          <h2>📎 Attach Tables</h2>
          <button class="close-btn" @click="closeAttachModal">✕</button>
        </div>

        <p class="modal-description">
          Select 2 or more available tables to group them together into one table group.
        </p>

        <div class="selection-summary">
          Selected: <strong>{{ attachSelectedTableIds.size }}</strong> table(s)
          <span v-if="attachSelectedTableIds.size >= 2" class="valid-selection">✓ Valid</span>
          <span v-else class="invalid-selection">(need at least 2)</span>
        </div>

        <div class="attach-grid">
          <div
            v-for="table in availableTablesForAttach"
            :key="table.id"
            class="attach-table-card"
            :class="{ selected: attachSelectedTableIds.has(table.id) }"
            @click="toggleAttachTable(table.id)"
          >
            <div class="attach-table-name">{{ table.tableCode }}</div>
            <div class="attach-table-status">🟢 Available</div>
            <div v-if="attachSelectedTableIds.has(table.id)" class="check-badge">✓</div>
          </div>
        </div>

        <div v-if="availableTablesForAttach.length === 0" class="empty-grid">
          No available tables to attach
        </div>

        <!-- Action buttons -->
        <div class="modal-actions">
          <button class="btn-cancel" @click="closeAttachModal">Cancel</button>
          <button
            class="btn-confirm"
            :disabled="attachSelectedTableIds.size < 2"
            @click="executeAttachTables"
          >
            Attach {{ attachSelectedTableIds.size }} Tables
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.waiter-tables-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f5f5f5;
}

.page-header {
  background: white;
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #e5e7eb;
}

.brand {
  font-size: 24px;
  font-weight: 700;
  color: #10b981;
  margin: 0;
}

.brand-subtitle {
  font-size: 14px;
  color: #6b7280;
  font-weight: 400;
  margin-left: 8px;
}

.table-selection-header {
  background: #10b981;
  padding: 20px;
  margin: 15px;
  border-radius: 12px;
  text-align: center;
}

.table-selection-header h2 {
  margin: 0;
  color: white;
  font-size: 18px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-legend {
  display: flex;
  gap: 24px;
  padding: 15px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  justify-content: center;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.legend-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin: 20px 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 20px;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.attach-btn {
  background: #3b82f6;
  color: white;
}

.attach-btn:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.switch-btn {
  background: #10b981;
  color: white;
}

.switch-btn:hover {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.content {
  flex: 1;
  padding: 30px 20px;
  overflow-y: auto;
}

.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 40px 30px;
  max-width: 1000px;
  margin: 0 auto;
}

.table-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  border-radius: 12px;
  background: white;
  border: 2px solid #e5e7eb;
  transition: all 0.2s ease;
}

.table-card:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.table-card.occupied {
  border-color: #ef4444;
}

.table-card.available {
  border-color: #10b981;
}

.table-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  width: 100%;
}

.table-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.action-btn-small {
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.menu-btn {
  background: #3b82f6;
  color: white;
}

.menu-btn:hover {
  background: #2563eb;
}

.bill-btn {
  background: #f59e0b;
  color: white;
}

.bill-btn:hover {
  background: #d97706;
}

.start-service-btn {
  background: #10b981;
  color: white;
}

.start-service-btn:hover {
  background: #059669;
}

.table-name {
  font-size: 16px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 16px;
}

.status-pill {
  width: 65px;
  height: 32px;
  border-radius: 16px;
  transition: all 0.2s ease;
}

.table-card:hover .status-pill {
  width: 75px;
  height: 36px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 22px;
  color: #1f2937;
}

.close-btn {
  background: #f3f4f6;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 20px;
  color: #6b7280;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.modal-description {
  padding: 16px 24px;
  margin: 0;
  color: #6b7280;
  font-size: 14px;
  border-bottom: 1px solid #e5e7eb;
}

/* Switch Modal Columns */
.modal-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  position: relative;
}

.column {
  display: flex;
  flex-direction: column;
}

.column-header {
  padding: 16px;
  border-bottom: 2px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.column-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  color: #374151;
}

.selection-badge {
  background: #3b82f6;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
}

.column-body {
  padding: 12px;
  max-height: 350px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-column {
  text-align: center;
  color: #9ca3af;
  padding: 40px 20px;
  font-size: 14px;
}

.table-option {
  padding: 14px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.table-option:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.table-option.selected {
  background: #dbeafe;
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

.table-option-name {
  font-weight: 700;
  font-size: 16px;
  color: #1f2937;
  margin-bottom: 4px;
}

.table-option-status {
  font-size: 12px;
  color: #6b7280;
}

.swap-arrow {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border: 3px solid #3b82f6;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  z-index: 10;
}

.swap-arrow span {
  font-size: 24px;
  font-weight: bold;
  color: #3b82f6;
}

/* Attach Modal */
.attach-modal {
  max-width: 800px;
}

.selection-summary {
  padding: 16px 24px;
  font-size: 16px;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.valid-selection {
  color: #22c55e;
  font-weight: 700;
  margin-left: 8px;
}

.invalid-selection {
  color: #ef4444;
  margin-left: 8px;
  font-size: 14px;
}

.attach-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 12px;
  padding: 24px;
  max-height: 400px;
  overflow-y: auto;
}

.empty-grid {
  text-align: center;
  color: #9ca3af;
  padding: 40px 20px;
  font-size: 14px;
}

.attach-table-card {
  padding: 20px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.attach-table-card:hover {
  background: #f0fdf4;
  border-color: #22c55e;
}

.attach-table-card.selected {
  background: #dcfce7;
  border-color: #22c55e;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.attach-table-name {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.attach-table-status {
  font-size: 12px;
  color: #6b7280;
}

.check-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #22c55e;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
}

/* Modal Actions */
.modal-actions {
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
}

.btn-cancel {
  flex: 1;
  padding: 14px;
  background: #f3f4f6;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 700;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-confirm {
  flex: 1;
  padding: 14px;
  background: #3b82f6;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 700;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-confirm:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-confirm:disabled {
  background: #d1d5db;
  color: #9ca3af;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .modal-columns {
    grid-template-columns: 1fr;
  }

  .swap-arrow {
    display: none;
  }

  .attach-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>
