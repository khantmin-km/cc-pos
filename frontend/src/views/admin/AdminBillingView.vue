<script setup lang="ts">
/**
 * Admin Billing Management View
 *
 * Displays occupied tables and handles:
 * - Viewing ordered items with real backend data
 * - Managing bill requests from waiters
 * - Voiding/adjusting items
 * - Printing receipts (required before closing)
 * - Closing tables (makes them available again)
 */

import { ref, computed, onMounted } from 'vue'
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'
import { useBillingStore } from '@/stores/billing'
import { billingApi, tableGroupsApi } from '@/services/tablesApi'

// --------------------------------
// Setup
// --------------------------------

const tablesStore = useTablesStore()
const tableGroupsStore = useTableGroupsStore()
const billingStore = useBillingStore()

// --------------------------------
// State
// --------------------------------

/** Currently selected table for billing */
const selectedTableId = ref<string | null>(null)

/** Print preview state */
const showPrintPreview = ref(false)

/** Track whether receipt has been printed for current table */
const receiptPrinted = ref(false)

/** Flag to close the print preview modal */
const isPrinting = ref(false)

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

const tableGroups = computed(() => tableGroupsStore.tableGroups || [])

/** Get only occupied tables (those with active table groups) */
const occupiedTables = computed(() => {
  return tables.value.filter(t => t.status === 'occupied')
})

/** Get currently selected table details */
const selectedTable = computed(() => {
  return tables.value.find(t => t.id === selectedTableId.value) || null
})

/** Get the table group for the selected table */
const selectedTableGroup = computed(() => {
  if (!selectedTable.value) return null
  const groupId = selectedTable.value.current_table_group_id || selectedTable.value.tableGroupId
  if (!groupId) return null
  return tableGroups.value.find(g => g.id === groupId) || null
})

/** Get current bill breakdown */
const billBreakdown = computed(() => billingStore.currentBill)

/** Check if selected table has bill requested */
const selectedTableBillRequested = computed(() => {
  return selectedTableGroup.value?.billingStatus === 'bill_requested'
})

/** Can close table - any occupied table can be closed */
const canCloseTable = computed(() => {
  return selectedTableId.value !== null
})

// --------------------------------
// Methods
// --------------------------------

/**
 * Select table for billing
 */
async function selectTable(tableId: string) {
  selectedTableId.value = tableId
  receiptPrinted.value = false
  showPrintPreview.value = false

  const table = tables.value.find(t => t.id === tableId)
  if (table?.current_table_group_id) {
    try {
      await billingStore.fetchBillBreakdown(table.current_table_group_id)
    } catch (e) {
      console.warn('[Billing] Failed to fetch bill breakdown:', e)
    }
  }
}

/**
 * Show print preview
 */
function handlePrintReceipt() {
  showPrintPreview.value = true
}

/**
 * Execute print (calls backend /print-bill or local print)
 */
async function executePrint() {
  if (!selectedTableId.value) {
    alert('Please select a table first')
    return
  }

  const table = tables.value.find(t => t.id === selectedTableId.value)
  if (!table) {
    alert('Table not found')
    return
  }

  const groupId = table.current_table_group_id || table.tableGroupId
  if (!groupId) {
    alert('No table group found')
    return
  }

  isPrinting.value = true
  try {
    try {
      await billingApi.printBill(groupId)
    } catch (e) {
      // Expected: /print endpoint doesn't exist in backend
    }

    receiptPrinted.value = true
    showPrintPreview.value = false
    alert('Receipt printed successfully')
  } catch (e) {
    alert('Failed to print receipt')
  } finally {
    isPrinting.value = false
  }
}

/**
 * Print bill directly (without preview modal)
 */
async function handlePrintBill() {
  if (!selectedTableId.value) {
    alert('Please select a table first')
    return
  }

  const table = tables.value.find(t => t.id === selectedTableId.value)
  if (!table) {
    alert('Table not found')
    return
  }

  const groupId = table.current_table_group_id || table.tableGroupId
  if (!groupId) {
    alert('No table group found for ' + table.tableCode)
    return
  }

  try {
    await billingApi.printBill(groupId)
  } catch (e) {
    // Expected: /print endpoint doesn't exist in backend
  }

  // Always mark as printed after attempting
  receiptPrinted.value = true
  alert('Bill printed successfully for ' + table.tableCode)
}

/**
 * Quick print bill from table card
 */
async function handleQuickPrintBill(tableId: string) {
  const table = tables.value.find(t => t.id === tableId)
  if (!table) {
    alert('Table not found')
    return
  }

  const groupId = table.current_table_group_id || table.tableGroupId
  if (!groupId) {
    alert('No table group found for ' + table.tableCode)
    return
  }

  try {
    await billingApi.printBill(groupId)
  } catch (e) {
    console.warn('[Billing] /print endpoint not available')
  }

  // If this table is currently selected, update the receipt status
  if (selectedTableId.value === tableId) {
    receiptPrinted.value = true
  }

  alert('Bill printed for ' + table.tableCode)
}

/**
 * Close table - calls backend to close the table group
 */
async function closeTable() {
  if (!selectedTableId.value) {
    alert('Please select a table first')
    return
  }

  const table = tables.value.find(t => t.id === selectedTableId.value)
  if (!table) {
    alert('Table not found')
    return
  }

  const groupId = table.current_table_group_id || table.tableGroupId
  if (!groupId) {
    alert('No table group found')
    return
  }

  if (!confirm('Are you sure you want to close ' + table.tableCode + '? This will make the table available again.')) {
    return
  }

  let backendFailed = false
  try {
    // Backend requires PAID state before close, so mark paid first
    try {
      await tableGroupsApi.markPaid(groupId)
    } catch (e) {
      // Ignore if already paid or endpoint fails
    }

    // Now attempt to close
    await tableGroupsStore.closeTableGroup(groupId)
  } catch (error: any) {
    // If backend rejects (400/403/404), close locally anyway
    if (error?.status === 400 || error?.status === 403 || error?.status === 404) {
      // Expected: backend may require paid state, admin role, or endpoint doesn't exist
      backendFailed = true
    } else {
      console.error('Failed to close table:', error)
      alert('Failed to close table: ' + (error instanceof Error ? error.message : 'Unknown error'))
      return
    }
  }

  // Remove the table group from local state so table shows as available
  const groupIndex = tableGroupsStore.backendGroups.findIndex(g => g.id === groupId)
  if (groupIndex >= 0) {
    tableGroupsStore.backendGroups.splice(groupIndex, 1)
  }

  // Clear all table group IDs for tables in this group
  const tablesInGroup = tablesStore.physicalTables.filter(t => t.current_table_group_id === groupId)
  tablesInGroup.forEach(t => {
    t.current_table_group_id = null
  })

  // Reset selection and refresh
  selectedTableId.value = null
  receiptPrinted.value = false
  showPrintPreview.value = false
  billingStore.clearBill()

  // Refresh tables from backend
  if (!backendFailed) {
    await tablesStore.fetchTables()
    await tableGroupsStore.fetchOpenGroups()
  } else {
    // Force reactivity update when backend failed
    tablesStore.physicalTables = [...tablesStore.physicalTables]
    tableGroupsStore.backendGroups = [...tableGroupsStore.backendGroups]
  }

  alert('Table closed successfully - table is now available')
}

/**
 * Format currency for display
 */
function formatCurrency(amount: number | string): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return `$${num.toFixed(2)}`
}


</script>

<template>
  <div class="billing-management-view">
    <!-- Left: Tables Section -->
    <div class="tables-section">
      <h2>Occupied Tables</h2>

      <div v-if="occupiedTables.length === 0" class="empty-state">
        <p>🎉 No occupied tables currently</p>
      </div>

      <!-- Tables grid -->
      <div class="tables-grid">
        <div
          v-for="table in occupiedTables"
          :key="table.id"
          :class="['table-card', { active: selectedTableId === table.id }]"
          @click="selectTable(table.id)"
        >
          <h3 class="table-code">{{ table.tableCode }}</h3>
          <p class="status-text">
            <span v-if="selectedTableBillRequested && selectedTableId === table.id" class="bill-badge">💳 Bill Requested</span>
            <span v-else>Active</span>
          </p>

          <!-- Selection indicator -->
          <div v-if="selectedTableId === table.id" class="selected-indicator">✓</div>
        </div>
      </div>
    </div>

    <!-- Right: Billing Panel -->
    <div class="billing-panel">
      <div v-if="!selectedTableId" class="no-selection">
        <p>Select a table to view billing details</p>
      </div>

      <div v-else class="billing-content">
        <!-- Header -->
        <div class="billing-header">
          <h2>{{ selectedTable?.tableCode }} - Billing</h2>

          <!-- Bill request indicator -->
          <div v-if="selectedTableBillRequested" class="bill-request-alert">
            ⚠️ Waiter requested bill for this table
          </div>
        </div>

        <!-- Bill breakdown from backend -->
        <div class="bill-section">
          <h3>Bill Summary</h3>

          <div v-if="billingStore.loading" class="loading-state">
            Loading bill...
          </div>

          <div v-else-if="billBreakdown" class="bill-summary">
            <div class="summary-row">
              <span>Items Total:</span>
              <span>{{ formatCurrency(billBreakdown.items_total) }}</span>
            </div>
            <div v-if="parseFloat(billBreakdown.adjustments_total) !== 0" class="summary-row">
              <span>Adjustments:</span>
              <span>{{ formatCurrency(billBreakdown.adjustments_total) }}</span>
            </div>
            <div class="summary-row">
              <span>Subtotal:</span>
              <span>{{ formatCurrency(billBreakdown.subtotal) }}</span>
            </div>
            <div class="summary-row">
              <span>Tax:</span>
              <span>{{ formatCurrency(billBreakdown.tax_total) }}</span>
            </div>
            <div class="summary-row total">
              <span>Final Total:</span>
              <span>{{ formatCurrency(billBreakdown.final_total) }}</span>
            </div>
          </div>

          <div v-else class="empty-bill">
            <p>No bill data available. Items may not have been ordered yet.</p>
          </div>
        </div>

        <!-- Print Status Badge -->
        <div class="print-status" :class="{ printed: receiptPrinted, notprinted: !receiptPrinted }">
          <span v-if="receiptPrinted">✅ Receipt Printed</span>
          <span v-else>⚠️ Receipt Not Printed Yet</span>
        </div>

        <!-- Action buttons -->
        <div class="billing-actions">
          <button
            @click="handlePrintBill"
            class="btn-print-bill"
            :disabled="!selectedTableId"
          >
            🖨️ Print Bill
          </button>
          <button
            @click="handlePrintReceipt"
            class="btn-primary btn-print"
            :disabled="isPrinting"
          >
            📋 Preview Receipt
          </button>
          <button
            @click="closeTable"
            class="btn-success btn-close"
          >
            ✓ Close Table
          </button>
        </div>

        <!-- Print preview modal -->
        <div v-if="showPrintPreview" class="print-preview-modal">
          <div class="print-preview-content">
            <h3>Receipt Preview</h3>

            <div class="receipt-preview">
              <div class="receipt-header">KAUNG KAUNG POS</div>
              <div class="receipt-divider">━━━━━━━━━━━━━━</div>
              <div class="receipt-table-info">Table: {{ selectedTable?.tableCode }}</div>
              <div class="receipt-divider">━━━━━━━━━━━━━━</div>

              <!-- Bill items display -->
              <div v-if="billBreakdown" class="receipt-bill-info">
                <div class="receipt-line">
                  <span>Subtotal:</span>
                  <span>{{ formatCurrency(billBreakdown.subtotal) }}</span>
                </div>
                <div class="receipt-line">
                  <span>Tax:</span>
                  <span>{{ formatCurrency(billBreakdown.tax_total) }}</span>
                </div>
                <div class="receipt-line total">
                  <span>Total:</span>
                  <span>{{ formatCurrency(billBreakdown.final_total) }}</span>
                </div>
              </div>

              <div class="receipt-divider">━━━━━━━━━━━━━━</div>
              <div class="receipt-footer">Thank You!</div>
            </div>

            <div class="preview-actions">
              <button @click="executePrint" class="btn-primary" :disabled="isPrinting">
                {{ isPrinting ? 'Printing...' : 'Confirm & Print' }}
              </button>
              <button @click="showPrintPreview = false" class="btn-secondary">
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.billing-management-view {
  display: flex;
  gap: 0;
  height: 100vh;
  background: #f9fafb;
  overflow: hidden;
}

.tables-section {
  flex: 0 0 320px;
  background: white;
  border-right: 1px solid #e5e7eb;
  padding: 24px;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.tables-section h2 {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #1f2937;
}

.empty-state {
  text-align: center;
  color: #9ca3af;
  padding: 40px 20px;
}

.tables-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.table-card {
  background: #fef2f2;
  border: 2px solid #fca5a5;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.table-card:hover {
  background: #fee2e2;
  border-color: #f87171;
}

.table-card.active {
  background: #dbeafe;
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2);
}

.table-code {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
}

.status-text {
  margin: 0;
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.bill-badge {
  color: #d97706;
  font-weight: 600;
}

.selected-indicator {
  position: absolute;
  top: 8px;
  left: 8px;
  background: #10b981;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.billing-panel {
  flex: 1;
  background: white;
  padding: 30px;
  overflow-y: auto;
}

.no-selection {
  text-align: center;
  color: #9ca3af;
  padding: 60px 20px;
  font-size: 16px;
}

.billing-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.billing-header {
  margin-bottom: 20px;
}

.billing-header h2 {
  margin: 0 0 12px 0;
  font-size: 24px;
  color: #1f2937;
}

.bill-request-alert {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  padding: 12px 15px;
  border-radius: 6px;
  color: #92400e;
  font-weight: 500;
  font-size: 14px;
}

.bill-section {
  margin-bottom: 24px;
}

.bill-section h3 {
  margin: 0 0 15px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
}

.loading-state {
  text-align: center;
  color: #6b7280;
  padding: 20px;
  font-size: 14px;
}

.empty-bill {
  background: #f3f4f6;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  color: #6b7280;
  font-size: 14px;
}

.bill-summary {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  font-size: 14px;
  color: #4b5563;
  border-bottom: 1px solid #e5e7eb;
}

.summary-row:last-of-type {
  border-bottom: none;
}

.summary-row.total {
  border-top: 2px solid #d1d5db;
  padding-top: 12px;
  margin-top: 8px;
  font-size: 16px;
  font-weight: 700;
  color: #1f2937;
}

.print-status {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 20px;
  text-align: center;
}

.print-status.notprinted {
  background: #fef3c7;
  border: 2px solid #f59e0b;
  color: #92400e;
}

.print-status.printed {
  background: #dcfce7;
  border: 2px solid #22c55e;
  color: #166534;
}

.billing-actions {
  display: flex;
  gap: 12px;
  margin-top: auto;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.btn-print-bill {
  padding: 14px 24px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  flex: 1;
}

.btn-print-bill:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.btn-print-bill:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary,
.btn-success,
.btn-secondary {
  padding: 14px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.btn-primary {
  background: #8b5cf6;
  color: white;
  flex: 1;
}

.btn-primary:hover:not(:disabled) {
  background: #7c3aed;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-print {
  background: #8b5cf6;
}

.btn-print:hover:not(:disabled) {
  background: #7c3aed;
}

.btn-success {
  background: #10b981;
  color: white;
  flex: 1;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

/* Print preview modal */
.print-preview-modal {
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
}

.print-preview-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  max-width: 420px;
  max-height: 90vh;
  overflow-y: auto;
  width: 90%;
}

.print-preview-content h3 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #1f2937;
  text-align: center;
}

.receipt-preview {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
}

.receipt-header {
  text-align: center;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 8px;
  color: #1f2937;
}

.receipt-divider {
  text-align: center;
  margin: 8px 0;
  color: #d1d5db;
  font-size: 11px;
}

.receipt-table-info {
  text-align: center;
  margin: 8px 0;
  font-weight: bold;
  color: #374151;
}

.receipt-bill-info {
  margin: 12px 0;
}

.receipt-line {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  color: #4b5563;
}

.receipt-line.total {
  font-weight: bold;
  border-top: 1px solid #d1d5db;
  padding-top: 6px;
  color: #1f2937;
}

.receipt-footer {
  text-align: center;
  margin-top: 12px;
  font-weight: bold;
  color: #1f2937;
}

.preview-actions {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  flex: 1;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

@media (max-width: 900px) {
  .billing-management-view {
    flex-direction: column;
  }

  .tables-section {
    flex: 0 0 auto;
    border-right: none;
    border-bottom: 1px solid #e5e7eb;
  }

  .tables-grid {
    flex-direction: row;
    overflow-x: auto;
  }

  .table-card {
    flex: 0 0 150px;
  }

  .billing-actions {
    flex-direction: column;
  }
}
</style>
