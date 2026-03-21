<script setup lang="ts">
/**
 * Billing & Orders Overview View (Admin)
 * 
 * Allows admin to:
 * - View active orders and pending kitchen items
 * - See bill status for each table
 * - Create bill adjustments (discounts, surcharges)
 * - Mark bills as paid
 */

import { ref, computed, onMounted } from 'vue'
import { useTableGroupsStore } from '@/stores/tableGroups'
import { useOrdersStore } from '@/stores/orders'
import { useBillingStore } from '@/stores/billing'
import { useTablesStore } from '@/stores/tables'

import type { BillAdjustmentCreateRequest } from '@/types/pos'

// --------------------------------
// Setup
// --------------------------------

const groupsStore = useTableGroupsStore()
const ordersStore = useOrdersStore()
const billingStore = useBillingStore()
const tablesStore = useTablesStore()

// --------------------------------
// State
// --------------------------------

const selectedGroupId = ref<string | null>(null)
const showBillDetails = ref(false)
const showAdjustmentForm = ref(false)

const adjustmentForm = ref<Partial<BillAdjustmentCreateRequest>>({
  amount: 0,
  description: '',
  reason: 'discount',
  category: 'manual',
  createdBy: 'admin',
})

const loading = ref(false)
const error = ref<string | null>(null)
const successMsg = ref<string | null>(null)

// --------------------------------
// Computed
// --------------------------------

const selectedGroup = computed(() => {
  return groupsStore.tableGroups.find((g) => g.id === selectedGroupId.value)
})

const groupBillStatus = computed(() => {
  if (!selectedGroup.value) return null
  
  const backendGroupState = groupsStore.backendGroups.find(g => g.id === selectedGroup.value?.id)?.state
  if (!backendGroupState) return 'Open'
  if (backendGroupState === 'closed') return 'Closed'
  if (backendGroupState === 'paid') return 'Paid'
  if (backendGroupState === 'bill_requested') return 'Bill Requested'
  return 'Open'
})

const openGroups = computed(() => {
  const openBackendStates = ['open', 'bill_requested']
  return groupsStore.tableGroups.filter((g) => {
    const backendGroup = groupsStore.backendGroups.find(bg => bg.id === g.id)
    return backendGroup && openBackendStates.includes(backendGroup.state)
  })
})

const paidGroups = computed(() => {
  return groupsStore.tableGroups.filter((g) => {
    const backendGroup = groupsStore.backendGroups.find(bg => bg.id === g.id)
    return backendGroup && backendGroup.state === 'paid'
  })
})

const closedGroups = computed(() => {
  return groupsStore.tableGroups.filter((g) => {
    const backendGroup = groupsStore.backendGroups.find(bg => bg.id === g.id)
    return backendGroup && backendGroup.state === 'closed'
  })
})

const pendingItems = computed(() => {
  if (!billingStore.currentBill?.items) return []
  return billingStore.currentBill.items.filter((item) => {
    // Find order item to check status
    return true // Placeholder - would check order item status
  })
})

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  try {
    await Promise.all([
      groupsStore.fetchOpenGroups(),
      tablesStore.fetchTables(),
    ])
  } catch (e) {
    error.value = 'Failed to load table groups'
  }
})

// --------------------------------
// Event Handlers
// --------------------------------

async function handleSelectGroup(groupId: string) {
  selectedGroupId.value = groupId
  showBillDetails.value = true
  showAdjustmentForm.value = false
  
  try {
    await billingStore.fetchBillBreakdown(groupId)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to fetch bill'
  }
}

async function handleMarkPaid() {
  if (!selectedGroup.value) return
  
  if (!confirm('Mark this bill as paid?')) return

  loading.value = true
  error.value = null

  try {
    await groupsStore.markPaid(selectedGroup.value.id)
    successMsg.value = 'Bill marked as paid'
    billingStore.clearBill()
    showBillDetails.value = false
    selectedGroupId.value = null
    await groupsStore.fetchOpenGroups()
    setTimeout(() => (successMsg.value = null), 3000)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to mark paid'
  } finally {
    loading.value = false
  }
}

async function handleCloseTables() {
  if (!selectedGroup.value) return
  if (getGroupState(selectedGroup.value.id) !== 'paid') return

  if (!confirm('Close this table group? Tables will become available.')) return

  loading.value = true
  error.value = null

  try {
    await groupsStore.closeTableGroup(selectedGroup.value.id)
    await Promise.all([
      groupsStore.fetchOpenGroups(),
      tablesStore.fetchTables(),
    ])
    successMsg.value = 'Tables closed and set to available'
    billingStore.clearBill()
    showBillDetails.value = false
    selectedGroupId.value = null
    setTimeout(() => (successMsg.value = null), 3000)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to close tables'
  } finally {
    loading.value = false
  }
}

async function handleCreateAdjustment() {
  if (!selectedGroupId.value) return
  if (!adjustmentForm.value.description || adjustmentForm.value.amount === undefined) {
    error.value = 'Please fill in adjustment details'
    return
  }

  loading.value = true
  error.value = null

  try {
    await billingStore.createAdjustment(selectedGroupId.value, adjustmentForm.value as BillAdjustmentCreateRequest)
    successMsg.value = 'Adjustment added successfully'
    adjustmentForm.value = {
      amount: 0,
      description: '',
      reason: 'discount',
      category: 'manual',
      createdBy: 'admin',
    }
    showAdjustmentForm.value = false
    setTimeout(() => (successMsg.value = null), 3000)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to create adjustment'
  } finally {
    loading.value = false
  }
}

// Helper function to get group state from backend
function getGroupState(groupId: string): string {
  return groupsStore.backendGroups.find(g => g.id === groupId)?.state || 'open'
}

function getTableLabel(tableId: string): string {
  const table = tablesStore.getTableById(tableId)
  if (table && table.number > 0) return `Table ${table.number}`
  return `Table ${tableId.slice(0, 8)}`
}

function getGroupTableLabels(tableIds: string[]): string[] {
  return [...tableIds]
    .map((id) => {
      const table = tablesStore.getTableById(id)
      return {
        id,
        number: table?.number ?? Number.MAX_SAFE_INTEGER,
        label: getTableLabel(id),
      }
    })
    .sort((a, b) => a.number - b.number)
    .map((t) => t.label)
}

function closeBillDetails() {
  showBillDetails.value = false
  selectedGroupId.value = null
  billingStore.clearBill()
}
</script>

<template>
  <div class="billing-view">
    <!-- Header -->
    <div class="header">
      <h2>Billing & Orders</h2>
    </div>

    <!-- Messages -->
    <div v-if="successMsg" class="message success">
      ✓ {{ successMsg }}
    </div>
    <div v-if="error" class="message error">
      ✗ {{ error }}
    </div>

    <div class="main-content">
      <!-- Groups List -->
      <div v-if="!showBillDetails" class="groups-section">
        <!-- Open Groups -->
        <div v-if="openGroups.length > 0" class="group-list">
          <h3>Open & Bill Pending ({{ openGroups.length }})</h3>
          <div class="group-cards">
            <div
              v-for="group in openGroups"
              :key="group.id"
              class="group-card"
              @click="handleSelectGroup(group.id)"
            >
              <div class="card-header">
                <h4>Tables</h4>
                <span class="status-badge" :data-status="getGroupState(group.id)">
                  {{ getGroupState(group.id) === 'bill_requested' ? '🧾' : '📝' }}
                  {{ getGroupState(group.id) === 'bill_requested' ? 'Bill Ready' : 'Open' }}
                </span>
              </div>
              <div class="table-tags">
                <span
                  v-for="tableLabel in getGroupTableLabels(group.tableIds)"
                  :key="`${group.id}-${tableLabel}`"
                  class="table-tag"
                >
                  {{ tableLabel }}
                </span>
              </div>
              <p class="time">{{ new Date(group.createdAt).toLocaleTimeString() }}</p>
            </div>
          </div>
        </div>

        <!-- Paid Groups -->
        <div v-if="paidGroups.length > 0" class="group-list">
          <h3>Paid ({{ paidGroups.length }})</h3>
          <div class="group-cards">
            <div
              v-for="group in paidGroups"
              :key="group.id"
              class="group-card paid"
              @click="handleSelectGroup(group.id)"
            >
              <div class="card-header">
                <h4>Tables</h4>
                <span class="status-badge paid">✓ Paid</span>
              </div>
              <div class="table-tags">
                <span
                  v-for="tableLabel in getGroupTableLabels(group.tableIds)"
                  :key="`${group.id}-${tableLabel}`"
                  class="table-tag"
                >
                  {{ tableLabel }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Closed Groups -->
        <div v-if="closedGroups.length > 0" class="group-list">
          <h3>Closed ({{ closedGroups.length }})</h3>
          <div class="group-cards">
            <div
              v-for="group in closedGroups"
              :key="group.id"
              class="group-card closed"
            >
              <div class="card-header">
                <h4>Tables</h4>
                <span class="status-badge closed">✕ Closed</span>
              </div>
              <div class="table-tags">
                <span
                  v-for="tableLabel in getGroupTableLabels(group.tableIds)"
                  :key="`${group.id}-${tableLabel}`"
                  class="table-tag"
                >
                  {{ tableLabel }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="openGroups.length === 0 && paidGroups.length === 0 && closedGroups.length === 0" class="empty">
          No table groups
        </div>
      </div>

      <!-- Bill Details -->
      <div v-else-if="showBillDetails && billingStore.currentBill" class="bill-section">
        <div class="bill-header">
          <button class="back-btn" @click="closeBillDetails">← Back</button>
          <h3>{{ groupBillStatus }}</h3>
          <div></div>
        </div>

        <!-- Bill Items -->
        <div v-if="billingStore.currentBill.items.length > 0" class="bill-items">
          <h4>Items</h4>
          <div class="item-list">
            <div v-for="item in billingStore.currentBill.items" :key="item.orderItemId" class="item-row">
              <div class="item-details">
                <p class="item-name">{{ item.itemName }}</p>
                <p class="item-qty">× {{ item.quantity }}</p>
              </div>
              <p class="item-price">{{ item.lineTotal.toFixed(2) }}</p>
            </div>
          </div>
        </div>

        <!-- Totals -->
        <div class="bill-totals">
          <div class="total-row">
            <span>Subtotal:</span>
            <span>{{ billingStore.currentBill.subtotal.toFixed(2) }}</span>
          </div>
          <div class="total-row">
            <span>Tax:</span>
            <span>{{ billingStore.currentBill.tax.toFixed(2) }}</span>
          </div>
          <div class="total-row">
            <span>Service Charge:</span>
            <span>{{ billingStore.currentBill.serviceCharge.toFixed(2) }}</span>
          </div>

          <!-- Adjustments -->
          <div v-if="billingStore.currentBill.adjustments && billingStore.currentBill.adjustments.length > 0">
            <div v-for="adj in billingStore.currentBill.adjustments" :key="adj.id" class="adjustment-row">
              <span>{{ adj.description }}:</span>
              <span :class="adj.amount < 0 ? 'negative' : 'positive'">
                {{ (adj.amount < 0 ? '-' : '+') }}{{ Math.abs(adj.amount).toFixed(2) }}
              </span>
            </div>
          </div>

          <div class="total-row grand-total">
            <span>Total:</span>
            <span>{{ billingStore.currentBill.total.toFixed(2) }}</span>
          </div>
        </div>

        <!-- Add Adjustment Form -->
        <div v-if="!showAdjustmentForm" class="adjustment-button">
          <button class="btn btn-secondary" @click="showAdjustmentForm = true">
            + Add Adjustment
          </button>
        </div>

        <div v-else class="adjustment-form">
          <h4>Add Adjustment</h4>
          <div class="form-group">
            <label>Description</label>
            <input
              v-model="adjustmentForm.description"
              placeholder="e.g., Discount, Service Error"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Amount</label>
              <input
                v-model.number="adjustmentForm.amount"
                type="number"
                step="0.01"
                placeholder="Negative for discount"
              />
            </div>
            <div class="form-group">
              <label>Reason</label>
              <select v-model="adjustmentForm.reason">
                <option value="discount">Discount</option>
                <option value="surcharge">Surcharge</option>
                <option value="error">Error Correction</option>
              </select>
            </div>
          </div>

          <div class="form-actions">
            <button class="btn btn-primary" @click="handleCreateAdjustment" :disabled="loading">
              {{ loading ? 'Adding...' : 'Add' }}
            </button>
            <button class="btn btn-secondary" @click="showAdjustmentForm = false">
              Cancel
            </button>
          </div>
        </div>

        <!-- Payment Buttons -->
        <div v-if="selectedGroup && getGroupState(selectedGroup.id) !== 'paid'" class="payment-section">
          <button
            class="btn btn-success btn-large"
            @click="handleMarkPaid"
            :disabled="loading"
          >
            {{ loading ? 'Processing...' : '✓ Mark as Paid' }}
          </button>
        </div>

        <div v-else-if="selectedGroup && getGroupState(selectedGroup.id) === 'paid'" class="payment-section">
          <button
            class="btn btn-danger btn-large"
            @click="handleCloseTables"
            :disabled="loading"
          >
            {{ loading ? 'Closing...' : '✕ Close Tables' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.billing-view {
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  font-size: 24px;
}

.message {
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-weight: 500;
}

.message.success {
  background: #dcfce7;
  color: #166534;
}

.message.error {
  background: #fee2e2;
  color: #dc2626;
}

.main-content {
  display: flex;
  gap: 20px;
}

.groups-section {
  flex: 1;
}

.group-list {
  margin-bottom: 24px;
}

.group-list h3 {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #64748b;
  margin: 0 0 12px;
  text-transform: uppercase;
}

.group-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.group-card {
  background: white;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.group-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.group-card.paid {
  background: #dcfce7;
  border-color: #22c55e;
  cursor: default;
}

.group-card.paid:hover {
  border-color: #22c55e;
  box-shadow: none;
}

.group-card.closed {
  background: #f3f4f6;
  border-color: #d1d5db;
  cursor: default;
}

.group-card.closed:hover {
  border-color: #d1d5db;
  box-shadow: none;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 8px;
}

.card-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.table-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.table-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #334155;
  font-size: 12px;
  font-weight: 700;
}

.status-badge {
  padding: 4px 8px;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}

.status-badge.paid {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.closed {
  background: #f3f4f6;
  color: #6b7280;
}

.time {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

.empty {
  padding: 40px 20px;
  text-align: center;
  color: #64748b;
}

.bill-section {
  flex: 1;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
}

.bill-header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.back-btn {
  padding: 8px 12px;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #e2e8f0;
}

.bill-header h3 {
  margin: 0;
  font-size: 18px;
}

.bill-items {
  margin-bottom: 20px;
}

.bill-items h4 {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
}

.item-list {
  background: #f8fafc;
  border-radius: 6px;
  padding: 12px;
}

.item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.item-row:last-child {
  border-bottom: none;
}

.item-name {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
}

.item-qty {
  margin: 2px 0 0;
  font-size: 12px;
  color: #64748b;
}

.item-price {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.bill-totals {
  background: #f8fafc;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 20px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.total-row span:first-child {
  color: #64748b;
}

.adjustment-row {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
  font-size: 13px;
}

.adjustment-row .negative {
  color: #22c55e;
}

.adjustment-row .positive {
  color: #ef4444;
}

.grand-total {
  border-top: 2px solid #667eea;
  margin-top: 12px;
  padding-top: 12px;
  font-weight: 700;
  font-size: 16px;
}

.adjustment-button {
  margin-bottom: 16px;
}

.adjustment-form {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 16px;
}

.adjustment-form h4 {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 600;
  font-size: 12px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
  font-family: inherit;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.payment-section {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
}

.btn-secondary {
  background: #f1f5f9;
  color: #1e293b;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn-success {
  background: #22c55e;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #16a34a;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-large {
  flex: 1;
  padding: 12px;
  font-size: 16px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
