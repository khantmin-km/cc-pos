<script setup lang="ts">
/**
 * Order Items Management View
 * 
 * Allows waiters to view order items and manage
 * item operations (mark served, void, reprint).
 */

import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import { useMenuItemsStore } from '@/stores/menuItems'
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'

// --------------------------------
// Setup
// --------------------------------

const router = useRouter()
const route = useRoute()
const ordersStore = useOrdersStore()
const menuStore = useMenuItemsStore()
const tablesStore = useTablesStore()
const groupsStore = useTableGroupsStore()

// --------------------------------
// State
// --------------------------------

const tableId = route.params.tableId as string
const selectedTab = ref<'active' | 'served' | 'voided'>('active')
const loading = ref(false)
const error = ref<string | null>(null)

// --------------------------------
// Computed
// --------------------------------

const currentTable = computed(() => tablesStore.tables.find((t) => t.id === tableId))

const tableGroupId = computed(() => currentTable.value?.tableGroupId)

const allOrderItems = computed(() => {
  if (!tableGroupId.value) return []
  return ordersStore.getOrderItemsByTableGroup(tableGroupId.value)
})

const activeItems = computed(() => {
  return allOrderItems.value.filter((item) => !item.served && !item.removed)
})

const servedItems = computed(() => {
  return allOrderItems.value.filter((item) => item.served)
})

const voidedItems = computed(() => {
  return allOrderItems.value.filter((item) => item.removed)
})

const displayItems = computed(() => {
  switch (selectedTab.value) {
    case 'served':
      return servedItems.value
    case 'voided':
      return voidedItems.value
    default:
      return activeItems.value
  }
})

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([
      menuStore.fetchMenuItems(),
      tablesStore.fetchTables(),
      groupsStore.fetchOpenGroups(),
    ])
  } catch (e) {
    error.value = 'Failed to load data'
  } finally {
    loading.value = false
  }
})

// --------------------------------
// Event Handlers
// --------------------------------

async function handleMarkServed(itemId: string) {
  try {
    await ordersStore.markOrderItemServed(itemId)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to mark served'
  }
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

function handleBackToMenu() {
  router.push(`/waiter/menu/${tableId}`)
}

function handleBackToTables() {
  router.push('/waiter')
}

function getItemColor(item: any): string {
  if (item.removed) return '#fees2e2'
  if (item.served) return '#dcfce7'
  if (item.kitchenPrinted) return '#fef3c7'
  return '#f0f4ff'
}

function getStatusLabel(item: any): string {
  if (item.removed) return 'VOIDED'
  if (item.served) return 'SERVED'
  if (item.kitchenPrinted) return 'PRINTED'
  return 'PENDING'
}
</script>

<template>
  <div class="order-items-view">
    <!-- Header -->
    <header class="header">
      <div class="nav-buttons">
        <button class="nav-btn" @click="handleBackToMenu">← Order More</button>
        <button class="nav-btn" @click="handleBackToTables">↩ Back to Tables</button>
      </div>
      <h1>{{ currentTable?.number ? `Table ${currentTable.number}` : 'Table' }} - Items</h1>
      <div class="spacer"></div>
    </header>

    <!-- Error Message -->
    <div v-if="error" class="error-banner">
      {{ error }}
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
          <button class="btn btn-serve" @click="handleMarkServed(item.id)" :disabled="ordersStore.loading">
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
