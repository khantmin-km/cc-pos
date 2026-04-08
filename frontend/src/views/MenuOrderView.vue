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
const showCart = ref(false)

// --------------------------------
// Computed
// --------------------------------

const currentTable = computed(() => tablesStore.tables.find((t) => t.id === tableId))

const isServiceStarted = computed(() => {
  return currentTable.value?.tableGroupId !== null && currentTable.value?.tableGroupId !== undefined
})

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

const cartItems = computed(() => {
  const items: Array<MenuItem & { quantity: number; notes: string | undefined; subtotal: number }> = []
  itemQuantities.value.forEach((quantity, itemId) => {
    if (quantity > 0) {
      const menuItem = menuStore.getItem(itemId)
      if (menuItem) {
        items.push({
          ...menuItem,
          quantity,
          notes: itemNotes.value.get(itemId),
          subtotal: menuItem.price * quantity
        })
      }
    }
  })
  return items
})

const cartTotal = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.subtotal, 0)
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

async function handleStartService() {
  if (isServiceStarted.value) {
    alert('Service already started for this table')
    return
  }

  loading.value = true
  error.value = null

  try {
    await tablesApi.startService(tableId)
    // Refresh table data to update tableGroupId
    await tablesStore.fetchTables()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to start service'
    console.error('Start service failed:', e)
  } finally {
    loading.value = false
  }
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

function toggleCart() {
  showCart.value = !showCart.value
}

function removeFromCart(itemId: string) {
  itemQuantities.value.delete(itemId)
  itemNotes.value.delete(itemId)
}

function clearCart() {
  itemQuantities.value.clear()
  itemNotes.value.clear()
  showCart.value = false
}
</script>

<template>
  <div class="menu-view">
    <!-- Header -->
    <header class="header">
      <div class="header-left">
        <button class="back-btn" @click="handleGoBack">←</button>
        <div class="header-title-section">
          <div class="restaurant-name">KAUNG KAUNG</div>
          <div class="table-info">{{ currentTable?.tableCode || 'Menu' }}</div>
        </div>
      </div>
      <div class="header-right">
        <button class="menu-btn">MENU</button>
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
        All
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

    <!-- Menu Items List -->
    <div v-if="!loading" class="menu-list">
      <div v-for="item in displayItems" :key="item.id" class="menu-item-card">
        <!-- Item Badge/Initial -->
        <div class="item-badge">{{ item.name.charAt(0).toUpperCase() }}</div>
        
        <!-- Item Info -->
        <div class="item-content">
          <h3 class="item-name">{{ item.name }}</h3>
          <p class="item-price">${{ item.price.toFixed(2) }}</p>
        </div>
        
        <!-- Add Button -->
        <button class="add-btn" @click="handleAddItem(item)">+</button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else class="loading">Loading menu...</div>

    <!-- Cart Icon -->
    <div v-if="draftItemsCount > 0" class="cart-icon" @click="toggleCart">
      🛒
      <span class="cart-count">{{ draftItemsCount }}</span>
    </div>

    <!-- Cart Modal -->
    <div v-if="showCart" class="cart-overlay" @click="toggleCart">
      <div class="cart-modal" @click.stop>
        <div class="cart-header">
          <h2>🛒 Order Cart</h2>
          <button class="close-btn" @click="toggleCart">×</button>
        </div>
        
        <div class="cart-items">
          <div v-for="item in cartItems" :key="item.id" class="cart-item">
            <div class="cart-item-info">
              <h4>{{ item.name }}</h4>
              <p class="cart-item-price">${{ item.price.toFixed(2) }} × {{ item.quantity }}</p>
              <p v-if="item.notes" class="cart-item-notes">📝 {{ item.notes }}</p>
            </div>
            <div class="cart-item-total">
              ${{ item.subtotal.toFixed(2) }}
            </div>
            <button class="remove-btn" @click="removeFromCart(item.id)">
              🗑️
            </button>
          </div>
        </div>
        
        <div class="cart-footer">
          <div class="cart-total">
            <strong>Total: ${{ cartTotal.toFixed(2) }}</strong>
          </div>
          <div class="cart-actions">
            <button class="clear-btn" @click="clearCart">Clear Cart</button>
            <button class="send-order-btn" @click="handleSubmitOrder" :disabled="loading">
              {{ loading ? 'Sending...' : 'Send Order' }}
            </button>
          </div>
        </div>
      </div>
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
  background: #10b981;
  border-bottom: none;
  sticky: top;
  z-index: 10;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.back-btn {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 18px;
  color: white;
  transition: background 0.2s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.header-title-section {
  display: flex;
  flex-direction: column;
}

.restaurant-name {
  font-size: 16px;
  font-weight: 700;
  color: white;
  margin: 0;
}

.table-info {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: background 0.2s;
}

.menu-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.error-banner {
  background: #fee2e2;
  color: #dc2626;
  padding: 12px 20px;
  font-size: 14px;
}

.category-tabs {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  background: white;
  overflow-x: auto;
  border-bottom: 1px solid #e2e8f0;
}

.tab {
  padding: 8px 16px;
  background: white;
  border: 2px solid #c6c6c6;
  border-radius: 20px;
  cursor: pointer;
  white-space: nowrap;
  font-weight: 600;
  color: #6b7280;
  transition: all 0.2s;
  font-size: 14px;
}

.tab:hover {
  border-color: #10b981;
  color: #10b981;
}

.tab.active {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

.menu-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px 20px;
  padding-bottom: 100px;
}

.menu-item-card {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 8px;
  padding: 16px;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.menu-item-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.item-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: #e0f2fe;
  color: #0284c7;
  border-radius: 8px;
  font-weight: 700;
  font-size: 18px;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.item-name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.item-price {
  margin: 4px 0 0 0;
  font-size: 14px;
  font-weight: 700;
  color: #dc2626;
}

.add-btn {
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 50%;
  background: #10b981;
  color: white;
  font-weight: 700;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-btn:hover {
  background: #059669;
  transform: scale(1.1);
}

.quantity {
  font-weight: 700;
  font-size: 1.1rem;
  color: #1e293b;
  min-width: 20px;
  text-align: center;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #64748b;
  font-size: 16px;
}

.cart-icon {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 60px;
  height: 60px;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  transition: all 0.2s;
  z-index: 100;
}

.cart-icon:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
}

.cart-count {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.cart-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.cart-modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.cart-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #1e293b;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #f3f4f6;
}

.cart-items {
  max-height: 400px;
  overflow-y: auto;
  padding: 20px;
}

.cart-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
}

.cart-item:last-child {
  border-bottom: none;
}

.cart-item-info {
  flex: 1;
}

.cart-item-info h4 {
  margin: 0;
  font-size: 1rem;
  color: #1e293b;
}

.cart-item-price {
  margin: 2px 0;
  font-size: 0.9rem;
  color: #6b7280;
}

.cart-item-notes {
  margin: 2px 0;
  font-size: 0.8rem;
  color: #059669;
}

.cart-item-total {
  font-weight: 700;
  color: #059669;
  margin: 0 16px;
}

.remove-btn {
  background: #fee2e2;
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.remove-btn:hover {
  background: #fecaca;
}

.cart-footer {
  padding: 20px;
  border-top: 1px solid #e2e8f0;
}

.cart-total {
  margin-bottom: 16px;
  font-size: 1.1rem;
  color: #1e293b;
}

.cart-actions {
  display: flex;
  gap: 12px;
}

.clear-btn {
  flex: 1;
  padding: 12px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.clear-btn:hover {
  background: #e5e7eb;
}

.send-order-btn {
  flex: 2;
  padding: 12px;
  background: #059669;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}

.send-order-btn:hover:not(:disabled) {
  background: #047857;
}

.send-order-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
</style>
