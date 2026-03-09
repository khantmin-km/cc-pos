<script setup lang="ts">
/**
 * Billing & Payment View (Admin)
 * 
 * Admin interface for managing billing and payments.
 * Displays active table groups with their order totals
 * and provides actions for billing workflow.
 */

// Vue core imports
import {
  ref,
  computed,
  onMounted,
} from 'vue'

// Store imports
import { useTableGroupsStore } from '@/stores/tableGroups'
import { useOrdersStore } from '@/stores/orders'
import { useTablesStore } from '@/stores/tables'

// Type imports
import type {
  TableGroupUI,
  BillingStatus,
} from '@/types/pos'

// Component imports
import AdminCard from '@/components/admin/AdminCard.vue'
import StatusBadge from '@/components/admin/StatusBadge.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'

// --------------------------------
// Setup
// --------------------------------

// Initialize stores
const tableGroupsStore = useTableGroupsStore()
const ordersStore = useOrdersStore()
const tablesStore = useTablesStore()

// --------------------------------
// State
// --------------------------------

/** Show request bill modal */
const showRequestBillModal = ref(false)

/** Show payment modal */
const showPaymentModal = ref(false)

/** Show close group modal */
const showCloseModal = ref(false)

/** Selected group for operations */
const selectedGroup = ref<TableGroupUI | null>(null)

/** Track bill print count per group */
const printCount = ref<Record<string, number>>({})

// --------------------------------
// Computed
// --------------------------------

/** All table groups */
const allGroups = computed(() => {
  return tableGroupsStore.tableGroups
})

/** Only active (not closed) groups */
const activeGroups = computed(() => {
  return allGroups.value.filter((g) => {
    return g.billingStatus !== 'closed'
  })
})

/** Confirmation message for close */
const closeMessage = computed(() => {
  const name = selectedGroup.value?.name ?? ''
  return `Close ${name}? This cannot be undone.`
})

// --------------------------------
// Lifecycle
// --------------------------------

/**
 * Load data on mount
 */
onMounted(async () => {
  await tablesStore.fetchTables()
  await tableGroupsStore.fetchOpenGroups()
})

// --------------------------------
// Helper Functions
// --------------------------------

/**
 * Format price with currency
 * 
 * @param price - Price amount
 */
function formatPrice(price: number) {
  return `$${price.toLocaleString()}`
}

/**
 * Get tables in a group
 * 
 * @param groupId - Group ID
 */
function getTablesForGroup(groupId: string) {
  const group = tableGroupsStore.getTableGroupById(
    groupId
  )

  if (!group) return []

  return group.tableIds
    .map((id) => tablesStore.getTableById(id))
    .filter((t) => t !== undefined)
}

/**
 * Get order items for a group
 * 
 * @param groupId - Group ID
 */
function getOrderItemsForGroup(groupId: string) {
  return ordersStore
    .getOrderItemsByTableGroup(groupId)
    .filter((o) => !o.removed)
}

/**
 * Calculate total for a group
 * 
 * @param groupId - Group ID
 */
function getTotalForGroup(groupId: string) {
  return ordersStore.totalForTableGroup(groupId)
}

// --------------------------------
// Billing Actions
// --------------------------------

/**
 * Request bill for a group
 * 
 * @param groupId - Group ID
 */
async function requestBill(groupId: string) {
  await tableGroupsStore.requestBill(groupId)
}

/**
 * Mark payment as completed
 * 
 * @param groupId - Group ID
 */
async function markPaymentCompleted(groupId: string) {
  await tableGroupsStore.markPaid(groupId)
}

/**
 * Close table group handler
 */
async function closeTableGroupHandler() {
  if (selectedGroup.value) {
    await tableGroupsStore.closeTableGroup(
      selectedGroup.value.id
    )
    selectedGroup.value = null
    showCloseModal.value = false
  }
}

// --------------------------------
// UI Helpers
// --------------------------------

/**
 * Print bill (simulated)
 * 
 * @param groupId - Group ID
 */
function printBill(groupId: string) {
  // Increment print count
  const current = printCount.value[groupId] || 0
  printCount.value[groupId] = current + 1

  // Log for debugging
  console.log(
    `Printing bill for group ${groupId}` +
    ` (Print #${current + 1})`
  )
}

/**
 * Check if bill can be requested
 * 
 * @param group - Table group
 */
function canRequestBill(group: TableGroupUI) {
  return group.billingStatus === 'active'
}

/**
 * Check if payment can be marked
 * 
 * @param group - Table group
 */
function canMarkPayment(group: TableGroupUI) {
  return group.billingStatus === 'bill_requested'
}

/**
 * Check if group can be closed
 * 
 * @param group - Table group
 */
function canCloseGroup(group: TableGroupUI) {
  return tableGroupsStore.canCloseGroup(group.id)
}

/**
 * Open close modal for a group
 * 
 * @param group - Group to close
 */
function openCloseModalForGroup(group: TableGroupUI) {
  selectedGroup.value = group
  showCloseModal.value = true
}
</script>

<template>
  <div class="admin-view">
    <div class="admin-container">
      <!-- Header -->
      <div class="admin-header">
        <h2>
          Billing & Payment
        </h2>
      </div>

      <!-- Billing Grid -->
      <div class="billing-grid">
        <AdminCard
          v-for="group in activeGroups"
          :key="group.id"
          :title="group.name"
        >
          <!-- Group Info -->
          <div class="group-info">
            <div class="group-tables">
              <span
                v-for="table in getTablesForGroup(group.id)"
                :key="table.id"
                class="table-badge"
              >
                Table {{ table.number }}
              </span>
            </div>
            <StatusBadge
              :status="group.billingStatus"
              type="billing"
            />
          </div>

          <!-- Order Items -->
          <div class="order-items-summary">
            <div
              v-for="item in getOrderItemsForGroup(group.id)"
              :key="item.id"
              class="bill-item"
            >
              <span class="item-name">
                {{ item.menuItem?.name || 'Unknown' }}
              </span>
              <span class="item-qty">
                ×{{ item.quantity }}
              </span>
              <span class="item-price">
                {{
                  formatPrice(
                    (item.priceOverride ??
                      item.menuItem?.price ??
                      0) * item.quantity
                  )
                }}
              </span>
            </div>
          </div>

          <!-- Totals -->
          <div class="bill-total">
            <div class="total-line">
              <span>Subtotal:</span>
              <span>
                {{ formatPrice(getTotalForGroup(group.id)) }}
              </span>
            </div>
            <div class="total-line total-final">
              <span>Total:</span>
              <span>
                {{ formatPrice(getTotalForGroup(group.id)) }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="bill-actions">
            <!-- Request Bill Button -->
            <button
              v-if="canRequestBill(group)"
              type="button"
              class="btn btn-warning"
              @click="requestBill(group.id)"
            >
              Request Bill
            </button>

            <!-- Payment Actions -->
            <template
              v-if="group.billingStatus === 'bill_requested'"
            >
              <button
                type="button"
                class="btn btn-secondary"
                @click="printBill(group.id)"
              >
                Print Bill
                <span
                  v-if="printCount[group.id]"
                  class="print-count"
                >
                  ({{ printCount[group.id] }})
                </span>
              </button>
              <button
                type="button"
                class="btn btn-success"
                @click="markPaymentCompleted(group.id)"
              >
                Mark Payment Completed
              </button>
            </template>

            <!-- Close Button -->
            <button
              v-if="canCloseGroup(group)"
              type="button"
              class="btn btn-danger"
              @click="openCloseModalForGroup(group)"
            >
              Close Table Group
            </button>
          </div>
        </AdminCard>
      </div>
    </div>

    <!-- Close Confirmation Modal -->
    <ConfirmModal
      v-if="showCloseModal"
      title="Close Table Group"
      :message="closeMessage"
      confirm-text="Close"
      danger
      @confirm="closeTableGroupHandler"
      @cancel="showCloseModal = false"
    />
  </div>
</template>

<style scoped>
.admin-view {
  min-height: 100vh;
  background: var(--pos-background);
}

.admin-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.admin-header {
  margin-bottom: 2rem;
}

.admin-header h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--pos-text);
  margin: 0;
}

.billing-grid {
  display: grid;
  grid-template-columns: repeat(
    auto-fill,
    minmax(400px, 1fr)
  );
  gap: 1.5rem;
}

.group-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--pos-border);
}

.group-tables {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.table-badge {
  background: var(--pos-primary);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.order-items-summary {
  margin-bottom: 1rem;
  max-height: 300px;
  overflow-y: auto;
}

.bill-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--pos-border);
}

.item-name {
  flex: 1;
  font-weight: 500;
  color: var(--pos-text);
}

.item-qty {
  margin: 0 1rem;
  color: var(--pos-text-muted);
}

.item-price {
  font-weight: 600;
  color: var(--pos-text);
  min-width: 80px;
  text-align: right;
}

.bill-total {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px solid var(--pos-border);
}

.total-line {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  color: var(--pos-text-muted);
}

.total-final {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--pos-text);
  border-top: 1px solid var(--pos-border);
  padding-top: 0.75rem;
  margin-top: 0.5rem;
}

.bill-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-warning {
  background: #f97316;
  color: white;
}

.btn-success {
  background: #22c55e;
  color: white;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.print-count {
  font-size: 0.8em;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .billing-grid {
    grid-template-columns: 1fr;
  }

  .bill-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
