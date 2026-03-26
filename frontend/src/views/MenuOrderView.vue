<script setup lang="ts">
/**
 * Menu Selection & Ordering View
 * 
 * Allows waiters to browse menu items and create orders
 * for customers at a specific table.
 */

import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMenuItemsStore } from '@/stores/menuItems'
import { useOrdersStore } from '@/stores/orders'
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'
import { tablesApi } from '@/services/tablesApi'

import type { MenuItem, OrderItem } from '@/types/pos'

// --------------------------------
// Setup
// --------------------------------

const router = useRouter()
const route = useRoute()
const menuStore = useMenuItemsStore()
const ordersStore = useOrdersStore()
const tablesStore = useTablesStore()
const groupsStore = useTableGroupsStore()

// --------------------------------
// State
// --------------------------------

const tableId = route.params.tableId as string
const selectedCategory = ref<string>('all')
const itemQuantities = ref<Map<string, number>>(new Map())
const loading = ref(false)
const error = ref<string | null>(null)
const showNotesInput = ref<string | null>(null)
const itemNotes = ref<Map<string, string>>(new Map())

// --------------------------------
// Computed
// --------------------------------

const currentTable = computed(() => tablesStore.tables.find((t) => t.id === tableId))

const displayItems = computed(() => {
  if (selectedCategory.value === 'all') {
    return menuStore.availableItems
  }
  return menuStore.availableItems.filter((item) => item.category === selectedCategory.value)
})

const categories = computed(() => {
  const cats = new Set(menuStore.availableItems.map((item) => item.category))
  return Array.from(cats).sort()
})

const draftItemsCount = computed(() => {
  return Array.from(itemQuantities.value.values()).reduce((sum, qty) => sum + qty, 0)
})

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  loading.value = true
  try {
    await menuStore.fetchMenuItems()
  } catch (e) {
    error.value = 'Failed to load menu items'
  } finally {
    loading.value = false
  }
})

// --------------------------------
// Event Handlers
// --------------------------------

function handleAddItem(item: MenuItem) {
  const current = itemQuantities.value.get(item.id) || 0
  itemQuantities.value.set(item.id, current + 1)
}

function handleRemoveItem(item: MenuItem) {
  const current = itemQuantities.value.get(item.id) || 0
  if (current > 1) {
    itemQuantities.value.set(item.id, current - 1)
  } else {
    itemQuantities.value.delete(item.id)
  }
}

function handleShowNotes(itemId: string) {
  showNotesInput.value = showNotesInput.value === itemId ? null : itemId
}

async function handleSubmitOrder() {
  if (itemQuantities.value.size === 0) {
    error.value = 'Please add items to order'
    return
  }

  loading.value = true
  error.value = null

  try {
    // Create order items
    const items: OrderItem[] = []
    itemQuantities.value.forEach((quantity, itemId) => {
      const menuItem = menuStore.getItem(itemId)
      if (menuItem) {
        items.push({
          id: `draft_${itemId}`,
          menuItemId: itemId,
          tableId,
          quantity,
          notes: itemNotes.value.get(itemId),
          status: 'pending',
          kitchenPrinted: false,
          served: false,
          removed: false,
          priceOverride: menuItem.price,
          menuItem,
        })
      }
    })

    // Get table group or create one
    const table = currentTable.value
    if (!table) {
      error.value = 'Table not found'
      return
    }

    let tableGroupId = table.tableGroupId
    if (!tableGroupId) {
      // Need to start service first
      const group = await tablesApi.startService(tableId)
      tableGroupId = group.id
    }

    // Confirm order
    await ordersStore.confirmOrder(tableId)

    // Redirect to order view
    router.push(`/waiter/orders/${tableId}`)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to place order'
  } finally {
    loading.value = false
  }
}

function handleGoBack() {
  router.push('/waiter')
}
</script>

<template>
  <div class="menu-view">
    <!-- Header -->
    <header class="header">
      <button class="back-btn" @click="handleGoBack">← Back</button>
      <h1>{{ currentTable?.number ? `Table ${currentTable.number} - Menu` : 'Menu' }}</h1>
      <div class="order-info">
        <span v-if="draftItemsCount > 0" class="item-count">{{ draftItemsCount }} items</span>
      </div>
    </header>

    <!-- Error Message -->
    <div v-if="error" class="error-banner">
      {{ error }}
    </div>

    <!-- Category Tabs -->
    <div class="category-tabs">
      <button
        class="tab"
        :class="{ active: selectedCategory === 'all' }"
        @click="selectedCategory = 'all'"
      >
        All Items
      </button>
      <button
        v-for="cat in categories"
        :key="cat"
        class="tab"
        :class="{ active: selectedCategory === cat }"
        @click="selectedCategory = cat"
      >
        {{ cat }}
      </button>
    </div>

    <!-- Menu Items Grid -->
    <div v-if="!loading" class="menu-grid">
      <div v-for="item in displayItems" :key="item.id" class="menu-item-card">
        <div class="item-header">
          <h3>{{ item.name }}</h3>
          <span class="price">{{ item.price.toFixed(2) }}</span>
        </div>

        <div class="item-controls">
          <div class="quantity-control">
            <button
              class="qty-btn"
              @click="handleRemoveItem(item)"
              v-show="(itemQuantities.get(item.id) || 0) > 0"
            >
              −
            </button>
            <span v-if="(itemQuantities.get(item.id) || 0) > 0" class="qty">
              {{ itemQuantities.get(item.id) }}
            </span>
            <button class="qty-btn" @click="handleAddItem(item)">
              +
            </button>
          </div>

          <button
            v-if="(itemQuantities.get(item.id) || 0) > 0"
            class="notes-btn"
            @click="handleShowNotes(item.id)"
            :class="{ active: showNotesInput === item.id }"
          >
            📝
          </button>
        </div>

        <!-- Notes Input -->
        <textarea
          v-if="showNotesInput === item.id"
          :value="itemNotes.get(item.id) || ''"
          class="notes-input"
          placeholder="Special instructions..."
          @update:modelValue="(val: string) => itemNotes.set(item.id, val)"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-else class="loading">Loading menu...</div>

    <!-- Submit Button -->
    <div v-if="draftItemsCount > 0" class="submit-section">
      <button class="submit-btn" @click="handleSubmitOrder" :disabled="loading">
        {{ loading ? 'Placing Order...' : `Place Order (${draftItemsCount} items)` }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.menu-view {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #f8fafc;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  sticky: top;
  z-index: 10;
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

.header h1 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.order-info {
  font-size: 14px;
  color: #64748b;
}

.item-count {
  background: #22c55e;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 600;
}

.error-banner {
  background: #fee2e2;
  color: #dc2626;
  padding: 12px 20px;
  font-size: 14px;
}

.category-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  overflow-x: auto;
  border-bottom: 1px solid #e2e8f0;
}

.tab {
  padding: 8px 16px;
  background: #f1f5f9;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  font-weight: 500;
  transition: all 0.2s;
}

.tab:hover {
  background: #e2e8f0;
}

.tab.active {
  background: #667eea;
  color: white;
}

.menu-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  padding: 20px;
  overflow-y: auto;
}

.menu-item-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;
}

.menu-item-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 12px;
}

.item-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  flex: 1;
}

.price {
  font-size: 18px;
  font-weight: 700;
  color: #667eea;
}

.item-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f1f5f9;
  padding: 4px 8px;
  border-radius: 4px;
  flex: 1;
}

.qty-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.qty-btn:hover {
  background: #e2e8f0;
}

.qty {
  font-weight: 600;
  font-size: 14px;
}

.notes-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.notes-btn:hover {
  background: #f1f5f9;
}

.notes-btn.active {
  background: #fef3c7;
  border-color: #fbbf24;
}

.notes-input {
  margin-top: 8px;
  width: 100%;
  padding: 8px;
  border: 1px solid #fbbf24;
  border-radius: 4px;
  font-family: inherit;
  font-size: 12px;
  resize: vertical;
  min-height: 60px;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #64748b;
  font-size: 16px;
}

.submit-section {
  padding: 20px;
  background: white;
  border-top: 1px solid #e2e8f0;
  sticky: bottom;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background: #22c55e;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 700;
  font-size: 16px;
  cursor: pointer;
   transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #16a34a;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
