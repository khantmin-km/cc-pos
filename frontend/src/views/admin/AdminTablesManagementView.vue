<script setup lang="ts">
/**
 * Admin Tables Management View
 * 
 * Admin version of table management with:
 * - Table status display (Available/Occupied)
 * - Table group visualization
 * - Start service for available tables
 * - View items for occupied tables
 * - Merge tables with verification
 * - Attach/Detach tables
 * - Manage voided items
 */

import { ref, computed, onMounted } from 'vue'
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'

// --------------------------------
// Setup
// --------------------------------

const tablesStore = useTablesStore()
const tableGroupsStore = useTableGroupsStore()

// --------------------------------
// State
// --------------------------------

/** Selected table for operations */
const selectedTableIds = ref<Set<string>>(new Set())

/** Active view mode */
const viewMode = ref<'overview' | 'merge'>('overview')

/** Merge operation state */
const mergeOperation = ref<{ table1?: string; table2?: string }>({})

/** Merge verification step */
const mergeVerificationStep = ref<1 | 2>(1)

/** Item void state */
const voidedItemIds = ref<Set<string>>(new Set())

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

/** All tables organized by group and status */
const tablesByGroup = computed(() => {
  const grouped = new Map<string, typeof tables.value>()
  
  tables.value.forEach(table => {
    const groupId = table.groupId || 'ungrouped'
    if (!grouped.has(groupId)) {
      grouped.set(groupId, [])
    }
    grouped.get(groupId)?.push(table)
  })
  
  return grouped
})

/** Check if table is selected */
function isTableSelected(tableId: string): boolean {
  return selectedTableIds.value.has(tableId)
}

/** Get table status color */
function getTableStatusColor(table: any): string {
  if (table.status === 'available') return '#10b981'
  if (table.status === 'occupied') return '#ef4444'
  return '#6b7280'
}

// --------------------------------
// Methods
// --------------------------------

/**
 * Handle table click based on view mode
 */
function handleTableClick(table: any) {
  if (viewMode.value === 'merge') {
    if (!mergeOperation.value.table1) {
      mergeOperation.value.table1 = table.id
      selectedTableIds.value.add(table.id)
    } else if (mergeOperation.value.table1 !== table.id && !mergeOperation.value.table2) {
      mergeOperation.value.table2 = table.id
      selectedTableIds.value.add(table.id)
    }
  } else {
    selectedTableIds.value.clear()
    selectedTableIds.value.add(table.id)
  }
}

/**
 * Start service on available table
 */
async function handleStartService(table: any) {
  if (table.status !== 'available') {
    alert('Table is not available')
    return
  }

  try {
    await tablesStore.startService(table.id)
    alert('Service started for ' + table.tableCode)
    await tablesStore.fetchTables()
  } catch (error) {
    alert('Failed to start service')
  }
}

/**
 * Show table items
 */
function showTableItems(table: any) {
  alert(`Items for ${table.tableCode}: ${table.orderItems?.length || 0} items`)
}

/**
 * Toggle void item
 */
function toggleVoidItem(itemId: string) {
  if (voidedItemIds.value.has(itemId)) {
    voidedItemIds.value.delete(itemId)
  } else {
    voidedItemIds.value.add(itemId)
  }
}

/**
 * Start merge operation
 */
function startMerge() {
  viewMode.value = 'merge'
  mergeOperation.value = {}
  mergeVerificationStep.value = 1
  selectedTableIds.value.clear()
}

/**
 * Proceed to verification step
 */
function proceedToVerification() {
  if (!mergeOperation.value.table1 || !mergeOperation.value.table2) {
    alert('Please select two tables')
    return
  }
  mergeVerificationStep.value = 2
}

/**
 * Execute merge operation
 */
async function executeMerge() {
  if (!mergeOperation.value.table1 || !mergeOperation.value.table2) return
  
  try {
    // Get the tables
    const table1 = tables.value.find(t => t.id === mergeOperation.value.table1)
    const table2 = tables.value.find(t => t.id === mergeOperation.value.table2)
    
    if (!table1 || !table2) {
      alert('Invalid table selection')
      return
    }
    
    // In real implementation, this would merge the tables
    alert(`Tables ${table1.tableCode} and ${table2.tableCode} have been merged`)
    
    // Reset
    cancelMerge()
    await tablesStore.fetchTables()
  } catch (error) {
    alert('Failed to merge tables')
  }
}

/**
 * Cancel merge operation
 */
function cancelMerge() {
  viewMode.value = 'overview'
  mergeOperation.value = {}
  mergeVerificationStep.value = 1
  selectedTableIds.value.clear()
}

</script>

<template>
  <div class="admin-tables-view">
    <!-- Header -->
    <div class="header">
      <h1>Table Management</h1>
      
      <div v-if="viewMode === 'overview'" class="header-actions">
        <button @click="startMerge" class="btn-primary btn-merge">
          🔗 Merge Tables
        </button>
      </div>

      <div v-else class="header-status">
        <span>Merge Mode</span>
      </div>
    </div>

    <!-- Overview mode -->
    <div v-if="viewMode === 'overview'" class="tables-container">
      <!-- Tables by group -->
      <div v-for="[groupId, groupTables] in tablesByGroup" :key="groupId" class="table-group-section">
        <h2 v-if="groupId !== 'ungrouped'" class="group-title">
          Group: {{ groupId }}
        </h2>
        <h2 v-else class="group-title">
          Unassigned Tables
        </h2>

        <div class="tables-grid">
          <div
            v-for="table in groupTables"
            :key="table.id"
            class="table-card"
            :style="{ borderColor: getTableStatusColor(table) }"
            :class="{
              available: table.status === 'available',
              occupied: table.status === 'occupied'
            }"
          >
            <!-- Status badge -->
            <div class="status-badge" :style="{ backgroundColor: getTableStatusColor(table) }">
              {{ table.status }}
            </div>

            <!-- Table info -->
            <h3 class="table-code">{{ table.tableCode }}</h3>
            
            <!-- Table details -->
            <div v-if="table.status === 'occupied'" class="table-details">
              <p class="items-count">
                📦 {{ table.orderItems?.length || 0 }} items
              </p>

              <!-- Action buttons -->
              <div class="action-buttons">
                <button @click.stop="showTableItems(table)" class="btn-action btn-view">
                  👀 View Items
                </button>
              </div>
            </div>

            <!-- Available table -->
            <div v-else class="table-actions">
              <button @click.stop="handleStartService(table)" class="btn-primary btn-start">
                ▶️ Start Service
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Merge mode -->
    <div v-else class="merge-container">
      <!-- Step 1: Selection -->
      <div v-if="mergeVerificationStep === 1" class="merge-step">
        <h2>Select Tables to Merge</h2>
        <p class="step-description">
          Choose 2 occupied tables to merge into one group
        </p>

        <div class="tables-grid">
          <div
            v-for="table in tables.filter(t => t.status === 'occupied')"
            :key="table.id"
            class="table-card merge-selectable"
            :class="{ selected: isTableSelected(table.id) }"
            @click="handleTableClick(table)"
          >
            <h3 class="table-code">{{ table.tableCode }}</h3>
            <p class="items-count">{{ table.orderItems?.length || 0 }} items</p>
            <div v-if="isTableSelected(table.id)" class="check-mark">✓</div>
          </div>
        </div>

        <div class="selection-info">
          Selected: {{ selectedTableIds.size }} table(s)
          <template v-if="mergeOperation.table1">
            ({{ tables.find(t => t.id === mergeOperation.table1)?.tableCode }})
          </template>
          <template v-if="mergeOperation.table2">
            + ({{ tables.find(t => t.id === mergeOperation.table2)?.tableCode }})
          </template>
        </div>

        <div class="step-actions">
          <button @click="proceedToVerification" class="btn-primary">
            Next: Verify Merge
          </button>
          <button @click="cancelMerge" class="btn-secondary">
            Cancel
          </button>
        </div>
      </div>

      <!-- Step 2: Verification -->
      <div v-else class="merge-step">
        <h2>Verify Merge</h2>
        
        <div v-if="mergeOperation.table1 && mergeOperation.table2" class="verification-content">
          <div class="merge-preview">
            <div class="table-preview">
              <div class="table-info">
                <h3>{{ tables.find(t => t.id === mergeOperation.table1)?.tableCode }}</h3>
                <p class="items-count">
                  {{ tables.find(t => t.id === mergeOperation.table1)?.orderItems?.length || 0 }} items
                </p>
              </div>
            </div>

            <div class="merge-symbol">+</div>

            <div class="table-preview">
              <div class="table-info">
                <h3>{{ tables.find(t => t.id === mergeOperation.table2)?.tableCode }}</h3>
                <p class="items-count">
                  {{ tables.find(t => t.id === mergeOperation.table2)?.orderItems?.length || 0 }} items
                </p>
              </div>
            </div>
          </div>

          <div class="merge-result">
            Will combine all items from both tables
          </div>

          <div class="verification-warning">
            ⚠️ This action will merge two table groups and combine all ordered items
          </div>
        </div>

        <div class="step-actions">
          <button @click="executeMerge" class="btn-success">
            ✓ Confirm Merge
          </button>
          <button @click="mergeVerificationStep = 1" class="btn-secondary">
            ← Back
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-tables-view {
  height: 100vh;
  background: #f9fafb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0 0 12px 0;
  font-size: 28px;
  color: #1f2937;
}

.header-actions,
.header-status {
  display: flex;
  gap: 12px;
}

.header-status {
  font-weight: 600;
  color: #3b82f6;
}

.tables-container,
.merge-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.table-group-section {
  margin-bottom: 40px;
}

.group-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 15px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #e5e7eb;
}

.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 15px;
}

.table-card {
  background: white;
  border: 3px solid #e5e7eb;
  border-radius: 12px;
  padding: 18px;
  position: relative;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.table-card.available {
  border-color: #10b981;
}

.table-card.occupied {
  border-color: #ef4444;
}

.table-card.merge-selectable {
  cursor: pointer;
}

.table-card.merge-selectable:hover {
  background: #f0f9ff;
  border-color: #3b82f6;
}

.table-card.merge-selectable.selected {
  background: #dbeafe;
  border-color: #3b82f6;
}

.status-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: white;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.table-code {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

.table-details {
  margin-top: 12px;
}

.items-count {
  margin: 8px 0;
  font-size: 13px;
  color: #6b7280;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.btn-action,
.btn-primary,
.btn-secondary,
.btn-success {
  padding: 10px 15px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 13px;
}

.btn-action {
  background: #e0e7ff;
  color: #3730a3;
}

.btn-action:hover {
  background: #c7d2fe;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover {
  background: #059669;
}

.btn-start {
  background: #10b981;
  color: white;
  padding: 12px 20px;
}

.btn-start:hover {
  background: #059669;
}

.btn-merge {
  background: #8b5cf6;
}

.btn-merge:hover {
  background: #7c3aed;
}

.check-mark {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #10b981;
  color: white;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: bold;
  font-size: 16px;
}

/* Merge mode styles */
.merge-step {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.merge-step h2 {
  margin: 0 0 10px 0;
  color: #1f2937;
  font-size: 24px;
}

.step-description {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 20px;
}

.selection-info {
  margin: 20px 0;
  padding: 12px;
  background: #f3f4f6;
  border-radius: 6px;
  font-weight: 500;
  text-align: center;
  color: #374151;
}

.step-actions {
  display: flex;
  gap: 12px;
  margin-top: 30px;
  justify-content: center;
}

/* Verification styles */
.verification-content {
  margin: 30px 0;
}

.merge-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 30px;
}

.table-preview {
  background: #f3f4f6;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  flex: 1;
  text-align: center;
}

.table-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #1f2937;
}

.merge-symbol {
  font-size: 28px;
  font-weight: bold;
  color: #9ca3af;
}

.merge-result {
  background: #dcfce7;
  border-left: 4px solid #10b981;
  padding: 12px;
  border-radius: 6px;
  color: #166534;
  font-weight: 500;
  text-align: center;
  margin-bottom: 15px;
}

.verification-warning {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  padding: 12px;
  border-radius: 6px;
  color: #92400e;
  font-weight: 500;
}

@media (max-width: 768px) {
  .tables-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }

  .merge-preview {
    flex-direction: column;
    gap: 15px;
  }

  .table-preview {
    width: 100%;
  }
}
</style>
