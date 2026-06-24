<script setup lang="ts">
/**
 * Order Items View (Waiter Serving Screen)
 * 
 * Shows ordered items for a table with serving controls.
 * Waiter can:
 * - View all ordered items
 * - Mark items as served
 * - Void items (cancel)
 * - Order more items
 * - Request bill
 */

// Vue imports
import {
  ref,
  computed,
  onMounted,
} from 'vue'

// Router imports
import { useRouter, useRoute } from 'vue-router'

// Store imports
import { useOrdersStore } from '@/stores/orders'
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'

// Type imports
import type { OrderItem, Table } from '@/types/pos'

// --------------------------------
// Setup
// --------------------------------

const router = useRouter()
const route = useRoute()
const tableId = route.params.tableId as string

// Initialize stores
const ordersStore = useOrdersStore()
const tablesStore = useTablesStore()
const tableGroupsStore = useTableGroupsStore()

// State
const selectedTab = ref<'active' | 'served' | 'voided'>('active')
const loading = ref(false)
const error = ref<string | null>(null)
const billRequested = ref(false)

// Computed properties
const currentTable = computed(() =>
  tablesStore.tables.find((t: any) => t.id === tableId)
)

const tableGroup = computed(() => {
  if (!currentTable.value) return null
  const groupId = currentTable.value.current_table_group_id || currentTable.value.tableGroupId
  if (!groupId) return null
  return tableGroupsStore.tableGroups.find(g => g.id === groupId) || null
})

const tableGroupIdValue = computed(() => {
  return currentTable.value?.current_table_group_id || currentTable.value?.tableGroupId
})

const hasServiceStarted = computed(() => !!tableGroupIdValue.value)

const tableGroupState = computed(() => {
  const group = tableGroupsStore.backendGroups.find(g => g.id === tableGroupIdValue.value)
  return group?.state || null
})

const isBillRequested = computed(() => {
  return billRequested.value || tableGroup.value?.billingStatus === 'bill_requested' || tableGroupState.value === 'bill_requested'
})

const canRequestBill = computed(() => {
  return hasServiceStarted.value && tableGroupState.value === 'open' && !isBillRequested.value
})

// Filter order items by status
const activeItems = computed(() => {
  return ordersStore.orderItems.filter((item) => !item.served && !item.removed)
})

const servedItems = computed(() => {
  return ordersStore.orderItems.filter((item) => item.served)
})

const voidedItems = computed(() => {
  return ordersStore.orderItems.filter((item) => item.removed)
})

// --------------------------------
// Event Handlers
// --------------------------------

function handleBackToTables() {
  router.push('/waiter')
}

function handleBackToMenu() {
  if (tableId) {
    router.push(`/waiter/menu/${tableId}`)
  }
}

function handleMarkServed(item: OrderItem) {
  ordersStore.markOrderItemServed(item.id)
}

function handleVoidItem(item: OrderItem) {
  if (confirm(`Are you sure you want to void this item?\n${item.menuItemId}`)) {
    ordersStore.voidOrderItem(item.id)
  }
}

async function handleRequestBill() {
  if (!tableGroupIdValue.value) {
    alert('No active table group found')
    return
  }

  if (isBillRequested.value) {
    alert('Bill already requested for this table')
    return
  }

  loading.value = true
  error.value = null

  try {
    await tableGroupsStore.requestBill(tableGroupIdValue.value)
    billRequested.value = true
    alert('Bill request sent to admin successfully!')
  } catch (e) {
    const msg = e instanceof Error ? e.message : 'Failed to request bill'
    error.value = msg
    console.error('Bill request failed:', e)
    alert('Failed to request bill: ' + msg)
  } finally {
    loading.value = false
  }
}

function handleTabChange(tab: 'active' | 'served' | 'voided') {
  selectedTab.value = tab
}

function getItemColor(item: OrderItem): string {
  if (item.removed) return '#fees2e2'
  if (item.served) return '#dcfce7'
  if (item.kitchenPrinted) return '#fef3c7'
  return '#f0f4ff'
}

function getStatusLabel(item: OrderItem): string {
  if (item.removed) return 'VOIDED'
  if (item.served) return 'SERVED'
  if (item.kitchenPrinted) return 'PRINTED'
  return 'PENDING'
}

async function handleVoid(itemId: string) {
  if (confirm('Are you sure you want to void this item?')) {
    try {
      await ordersStore.voidOrderItem(itemId)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to void item'
    }
  }
}

async function handleReprint(itemId: string) {
  try {
    await ordersStore.reprintOrderItem(itemId)
    error.value = null
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to reprint item'
  }
}

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  if (!tableId) return
  
  try {
    loading.value = true
    
    // Load current table info
    await tablesStore.fetchTables()
    
    // Load table groups
    await tableGroupsStore.fetchOpenGroups()
    
    // Load order items for this table
    await ordersStore.fetchOrderItems(tableId)
    
  } catch (e) {
    error.value = 'Failed to load order items'
    console.error('Load failed:', e)
  } finally {
    loading.value = false
  }
})

// Computed properties for display items
const displayItems = computed(() => {
  switch (selectedTab.value) {
    case 'active': return activeItems.value
    case 'served': return servedItems.value  
    case 'voided': return voidedItems.value
    default: return []
  }
})
</script>

<template>
  <div class="order-items-view">
    <!-- Header -->
    <header class="header">
      <div class="nav-buttons">
        <button class="nav-btn" @click="handleBackToMenu">← Order More</button>
        <button class="nav-btn" @click="handleBackToTables">↩ Back to Tables</button>
      </div>
      <h1>{{ currentTable?.tableCode || 'Table' }} - Items</h1>
      <div class="spacer"></div>
    </header>

    <!-- Error Message -->
    <div v-if="error" class="error-banner">
      {{ error }}
    </div>

    <!-- Bill Requested Banner -->
    <div v-if="isBillRequested" class="bill-requested-banner">
      ✅ Bill has been requested - Waiting for admin to process
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        class="tab"
        :class="{ active: selectedTab === 'active' }"
        @click="selectedTab = 'active'"
      >
        🍽 Active ({{ activeItems.length }})
      </button>
      <button
        class="tab"
        :class="{ active: selectedTab === 'served' }"
        @click="selectedTab = 'served'"
      >
        ✅ Served ({{ servedItems.length }})
      </button>
      <button
        class="tab"
        :class="{ active: selectedTab === 'voided' }"
        @click="selectedTab = 'voided'"
      >
        ❌ Voided ({{ voidedItems.length }})
      </button>
    </div>

    <!-- Items List -->
    <div class="items-list">
      <div v-if="displayItems.length === 0" class="empty-state">
        <p v-if="selectedTab === 'active'">No active items. Order more?</p>
        <p v-else>No items in this category.</p>
      </div>

      <div
        v-for="item in displayItems"
        :key="item.id"
        class="item-card"
        :style="{ background: getItemColor(item) }"
      >
        <div class="item-main">
          <div class="item-info">
            <h3>{{ item.menuItem?.name || 'Unknown Item' }}</h3>
            <p v-if="item.notes" class="notes">📝 {{ item.notes }}</p>
          </div>

          <div class="item-meta">
            <span class="qty">×{{ item.quantity }}</span>
            <span class="status" :data-status="item.status">
              {{ getStatusLabel(item) }}
            </span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div v-if="selectedTab === 'active'" class="actions">
          <button class="btn btn-serve" @click="handleMarkServed(item)" :disabled="ordersStore.loading">
            ✓ Served
          </button>
          <button class="btn btn-reprint" @click="handleReprint(item.id)" :disabled="ordersStore.loading">
            🔄
          </button>
          <button class="btn btn-void" @click="handleVoid(item.id)" :disabled="ordersStore.loading">
            ✕ Void
          </button>
        </div>
      </div>
    </div>

    <!-- Fixed Request Bill Button at Bottom -->
    <div v-if="hasServiceStarted" class="fixed-bottom-bar">
      <button
        class="request-bill-btn"
        :class="{ requested: isBillRequested }"
        @click="handleRequestBill"
        :disabled="loading"
      >
        <span v-if="isBillRequested">✅ Bill Already Requested</span>
        <span v-else-if="loading">Sending Request...</span>
        <span v-else>💳 Request Bill</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.order-items-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f8fafc;
}

.header {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.nav-buttons {
  display: flex;
  gap: 8px;
}

.nav-btn {
  padding: 8px 12px;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 12px;
  transition: background 0.2s;
}

.nav-btn:hover {
  background: #e2e8f0;
}

.header h1 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  text-align: center;
}

.spacer {
  width: 0;
}

.error-banner {
  background: #fee2e2;
  color: #dc2626;
  padding: 12px 20px;
  font-size: 14px;
}

.bill-requested-banner {
  background: #fef3c7;
  color: #92400e;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  text-align: center;
  border-bottom: 2px solid #f59e0b;
}

.tabs {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  overflow-x: auto;
}

.tab {
  padding: 8px 16px;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.2s;
}

.tab:hover {
  background: #e2e8f0;
}

.tab.active {
  background: #667eea;
  color: white;
}

.items-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #64748b;
  font-size: 16px;
}

.item-card {
  padding: 16px;
  background: #f0f4ff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.item-main {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 12px;
}

.item-info {
  flex: 1;
}

.item-info h3 {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.notes {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
  font-style: italic;
}

.item-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.qty {
  font-weight: 700;
  font-size: 18px;
  color: #667eea;
}

.status {
  padding: 4px 8px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.status[data-status='pending'] {
  background: #fee2e2;
  color: #dc2626;
}

.status[data-status='kitchen_printed'] {
  background: #fef3c7;
  color: #92400e;
}

.status[data-status='served'] {
  background: #dcfce7;
  color: #166534;
}

.status[data-status='removed'] {
  background: #f3f4f6;
  color: #6b7280;
}

.actions {
  display: flex;
  gap: 8px;
}

.btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-serve {
  background: #22c55e;
  color: white;
}

.btn-serve:hover:not(:disabled) {
  background: #16a34a;
}

.btn-reprint {
  background: #3b82f6;
  color: white;
  padding: 8px;
  width: auto;
}

.btn-reprint:hover:not(:disabled) {
  background: #2563eb;
}

.btn-void {
  background: #ef4444;
  color: white;
}

.btn-void:hover:not(:disabled) {
  background: #dc2626;
}

.bill-request-btn {
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.bill-request-btn:hover {
  background: #d97706;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(245, 158, 11, 0.3);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Fixed bottom bar for Request Bill */
.fixed-bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 16px 20px;
  border-top: 2px solid #e2e8f0;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.request-bill-btn {
  width: 100%;
  padding: 16px;
  background: #f59e0b;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.request-bill-btn:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4);
}

.request-bill-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.request-bill-btn.requested {
  background: #22c55e;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.request-bill-btn.requested:hover {
  background: #16a34a;
}

/* Add padding to items list to account for fixed bottom bar */
.items-list {
  padding-bottom: 100px;
}
</style>
