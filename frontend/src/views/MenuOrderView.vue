<script setup lang="ts">
/**
 * Menu Selection & Ordering View
 * 
 * Restaurant POS: Waiters browse menu items, add to cart with add-ons,
 * and submit orders to the kitchen.
 */

import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMenuItemsStore } from '@/stores/menuItems'
import { useOrdersStore } from '@/stores/orders'
import { useTablesStore } from '@/stores/tables'
import { tablesApi } from '@/services/tablesApi'

import type { MenuItem } from '@/types/pos'

// --------------------------------
// Setup
// --------------------------------

const router = useRouter()
const route = useRoute()
const menuStore = useMenuItemsStore()
const ordersStore = useOrdersStore()
const tablesStore = useTablesStore()

// --------------------------------
// State
// --------------------------------

const tableId = route.params.tableId as string
const selectedCategory = ref<string>('all')
const loading = ref(false)
const error = ref<string | null>(null)
const showCart = ref(false)

// Cart: map of menuItemId -> quantity
const cart = ref<Map<string, number>>(new Map())
// Add-ons selections per cart line: map of menuItemId -> Set<addonMenuItemId>
const cartAddons = ref<Map<string, Set<string>>>(new Map())
// Expanded add-ons section per menu item
const expandedItem = ref<string | null>(null)

// --------------------------------
// Computed
// --------------------------------

const currentTable = computed(() => tablesStore.tables.find((t) => t.id === tableId))

const isServiceStarted = computed(() => {
  return currentTable.value?.tableGroupId !== null && currentTable.value?.tableGroupId !== undefined
})

const displayItems = computed(() => {
  if (selectedCategory.value === 'all') {
    return menuStore.mainItems
  }
  if (selectedCategory.value === 'Add-on') {
    return menuStore.addonItems
  }
  return menuStore.mainItems.filter((item) => item.category === selectedCategory.value)
})

const categories = computed(() => {
  const cats = new Set(menuStore.mainItems.map((item) => item.category))
  cats.add('Add-on')
  return Array.from(cats).sort()
})

const cartItemCount = computed(() => {
  let count = 0
  cart.value.forEach(qty => count += qty)
  cartAddons.value.forEach(addons => count += addons.size)
  return count
})

interface CartLine {
  itemId: string
  name: string
  price: number
  quantity: number
  subtotal: number
  isAddon: boolean
  parentItemId?: string
}

const cartLines = computed<CartLine[]>(() => {
  const lines: CartLine[] = []
  cart.value.forEach((quantity, itemId) => {
    const menuItem = menuStore.getItem(itemId)
    if (menuItem && quantity > 0) {
      lines.push({
        itemId,
        name: menuItem.name,
        price: Number(menuItem.price),
        quantity,
        subtotal: Number(menuItem.price) * quantity,
        isAddon: menuItem.category === 'Add-on',
      })
      // Add selected add-ons for this item
      const addons = cartAddons.value.get(itemId)
      if (addons) {
        addons.forEach(addonId => {
          const addonItem = menuStore.getItem(addonId)
          if (addonItem) {
            lines.push({
              itemId: addonId,
              name: addonItem.name,
              price: Number(addonItem.price),
              quantity,
              subtotal: Number(addonItem.price) * quantity,
              isAddon: true,
              parentItemId: itemId,
            })
          }
        })
      }
    }
  })
  return lines
})

const cartTotal = computed(() => {
  return cartLines.value.reduce((sum, line) => sum + line.subtotal, 0)
})

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  loading.value = true
  try {
    await menuStore.fetchMenuItems()
    await tablesStore.fetchTables()
    if (route.query.addons === 'true') {
      selectedCategory.value = 'Add-on'
    }
  } catch (e) {
    error.value = 'Failed to load menu items'
  } finally {
    loading.value = false
  }
})

// --------------------------------
// Cart Actions
// --------------------------------

function addToCart(itemId: string) {
  const current = cart.value.get(itemId) || 0
  cart.value.set(itemId, current + 1)
}

function removeFromCart(itemId: string) {
  const current = cart.value.get(itemId) || 0
  if (current > 1) {
    cart.value.set(itemId, current - 1)
  } else {
    cart.value.delete(itemId)
    cartAddons.value.delete(itemId)
  }
}

function getCartItemQty(itemId: string): number {
  return cart.value.get(itemId) || 0
}

function toggleAddonForItem(parentItemId: string, addonId: string) {
  const addons = cartAddons.value.get(parentItemId) || new Set()
  if (addons.has(addonId)) {
    addons.delete(addonId)
  } else {
    addons.add(addonId)
  }
  cartAddons.value.set(parentItemId, addons)
}

function isAddonSelected(parentItemId: string, addonId: string): boolean {
  return cartAddons.value.get(parentItemId)?.has(addonId) || false
}

function toggleExpandItem(itemId: string) {
  expandedItem.value = expandedItem.value === itemId ? null : itemId
}

function clearCart() {
  cart.value.clear()
  cartAddons.value.clear()
  showCart.value = false
}

function removeCartLine(itemId: string, parentItemId?: string) {
  if (parentItemId) {
    // Remove an addon from a parent item
    const addons = cartAddons.value.get(parentItemId)
    if (addons) {
      addons.delete(itemId)
      if (addons.size === 0) {
        cartAddons.value.delete(parentItemId)
      }
    }
  } else {
    cart.value.delete(itemId)
    cartAddons.value.delete(itemId)
  }
}

// --------------------------------
// Order Submission
// --------------------------------

async function handleSubmitOrder() {
  if (cart.value.size === 0) {
    error.value = 'Please add items to order'
    return
  }

  loading.value = true
  error.value = null

  try {
    // Ensure service is started
    const table = currentTable.value
    if (!table) {
      error.value = 'Table not found'
      return
    }

    if (!table.tableGroupId) {
      const group = await tablesApi.startService(tableId)
      await tablesStore.fetchTables()
    }

    // Add all cart items to ordersStore draft
    ordersStore.clearDraft()
    cart.value.forEach((quantity, itemId) => {
      const menuItem = menuStore.getItem(itemId)
      if (menuItem) {
        ordersStore.addDraftItem({
          id: `draft_${itemId}`,
          menuItemId: itemId,
          tableId,
          quantity,
          notes: undefined,
          status: 'pending',
          kitchenPrinted: false,
          served: false,
          removed: false,
          priceOverride: Number(menuItem.price),
          menuItem,
        })
      }
      // Add selected add-ons for this item (same quantity as parent)
      const addons = cartAddons.value.get(itemId)
      if (addons) {
        addons.forEach(addonId => {
          const addonItem = menuStore.getItem(addonId)
          if (addonItem) {
            ordersStore.addDraftItem({
              id: `draft_${addonId}`,
              menuItemId: addonId,
              tableId,
              quantity,
              notes: undefined,
              status: 'pending',
              kitchenPrinted: false,
              served: false,
              removed: false,
              priceOverride: Number(addonItem.price),
              menuItem: addonItem,
            })
          }
        })
      }
    })

    // Submit order via API
    await ordersStore.confirmOrder(tableId)

    // Clear cart and redirect
    cart.value.clear()
    cartAddons.value.clear()
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
        <button v-if="cartItemCount > 0" class="cart-toggle-btn" @click="toggleCart">
          🛒 {{ cartItemCount }}
        </button>
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
      <div v-for="item in displayItems" :key="item.id" class="menu-item-row">
        <!-- Main item row -->
        <div class="menu-item-card">
          <div class="item-badge">{{ item.name.charAt(0).toUpperCase() }}</div>
          <div class="item-content">
            <h3 class="item-name">{{ item.name }}</h3>
            <p class="item-price">${{ Number(item.price).toFixed(2) }}</p>
          </div>
          <!-- Quantity controls if in cart -->
          <div v-if="getCartItemQty(item.id) > 0" class="qty-controls">
            <button class="qty-btn minus" @click="removeFromCart(item.id)">−</button>
            <span class="qty-value">{{ getCartItemQty(item.id) }}</span>
            <button class="qty-btn plus" @click="addToCart(item.id)">+</button>
          </div>
          <!-- Add button if not in cart -->
          <button v-else class="add-btn" @click="addToCart(item.id)">+</button>
          <!-- Expand add-ons toggle -->
          <button
            v-if="menuStore.getAddonsForItem(item.id).length > 0"
            class="addons-toggle"
            :class="{ expanded: expandedItem === item.id }"
            @click="toggleExpandItem(item.id)"
          >
            ▸ Add-ons
          </button>
        </div>

        <!-- Inline add-ons section (expanded) -->
        <div v-if="expandedItem === item.id && menuStore.getAddonsForItem(item.id).length > 0" class="addons-section">
          <div
            v-for="addon in menuStore.getAddonsForItem(item.id)"
            :key="addon.id"
            class="addon-row"
            :class="{ selected: isAddonSelected(item.id, addon.id) }"
            @click="toggleAddonForItem(item.id, addon.id)"
          >
            <div class="addon-checkbox-visual">
              <span v-if="isAddonSelected(item.id, addon.id)">✓</span>
            </div>
            <div class="addon-info">
              <span class="addon-name">{{ addon.name }}</span>
              <span class="addon-price">+${{ Number(addon.price).toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else class="loading">Loading menu...</div>

    <!-- Floating Cart Button -->
    <div v-if="cartItemCount > 0 && !showCart" class="cart-fab" @click="toggleCart">
      🛒 <span class="cart-fab-count">{{ cartItemCount }}</span>
    </div>

    <!-- Cart Drawer -->
    <div v-if="showCart" class="cart-overlay" @click="toggleCart">
      <div class="cart-drawer" @click.stop>
        <div class="cart-header">
          <h2>🛒 Order</h2>
          <button class="close-btn" @click="toggleCart">×</button>
        </div>

        <div v-if="cartLines.length === 0" class="cart-empty">
          No items yet
        </div>

        <div v-else class="cart-items">
          <div v-for="line in cartLines" :key="line.parentItemId ? `${line.parentItemId}-${line.itemId}` : line.itemId" class="cart-line" :class="{ 'is-addon': line.isAddon }">
            <div class="cart-line-info">
              <span class="cart-line-name">{{ line.isAddon ? '  ↳ ' : '' }}{{ line.name }}</span>
              <span class="cart-line-detail">${{ line.price.toFixed(2) }} × {{ line.quantity }}</span>
            </div>
            <div class="cart-line-subtotal">${{ line.subtotal.toFixed(2) }}</div>
            <button class="cart-line-remove" @click="removeCartLine(line.itemId, line.parentItemId)">✕</button>
          </div>
        </div>

        <div v-if="cartLines.length > 0" class="cart-footer">
          <div class="cart-total">
            <strong>Total: ${{ cartTotal.toFixed(2) }}</strong>
          </div>
          <div class="cart-actions">
            <button class="clear-btn" @click="clearCart">Clear</button>
            <button class="send-order-btn" @click="handleSubmitOrder" :disabled="loading">
              {{ loading ? 'Sending...' : 'Send Order 🚀' }}
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
  position: sticky;
  top: 0;
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

.cart-toggle-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.25);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 700;
  font-size: 14px;
  transition: background 0.2s;
}

.cart-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.4);
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
  background: white;
  border: 2px solid #d1d5db;
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
  gap: 8px;
  padding: 16px 20px;
  padding-bottom: 100px;
}

.menu-item-row {
  display: flex;
  flex-direction: column;
}

.menu-item-card {
  display: flex;
  align-items: center;
  background: white;
  border-radius: 10px;
  padding: 14px 16px;
  gap: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.2s;
}

.menu-item-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.item-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: #ecfdf5;
  color: #059669;
  border-radius: 10px;
  font-weight: 700;
  font-size: 18px;
  flex-shrink: 0;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-name {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-price {
  margin: 2px 0 0 0;
  font-size: 14px;
  font-weight: 700;
  color: #dc2626;
}

/* Quantity controls */
.qty-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.qty-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.qty-btn.minus {
  background: #fee2e2;
  color: #dc2626;
}

.qty-btn.minus:hover {
  background: #fecaca;
}

.qty-btn.plus {
  background: #d1fae5;
  color: #059669;
}

.qty-btn.plus:hover {
  background: #a7f3d0;
}

.qty-value {
  font-weight: 700;
  font-size: 16px;
  min-width: 24px;
  text-align: center;
  color: #1f2937;
}

.add-btn {
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 12px;
  background: #10b981;
  color: white;
  font-weight: 700;
  font-size: 22px;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-btn:hover {
  background: #059669;
  transform: scale(1.05);
}

/* Add-ons toggle button */
.addons-toggle {
  padding: 6px 12px;
  background: #f3e8ff;
  color: #7c3aed;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 12px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.addons-toggle:hover {
  background: #ede9fe;
}

.addons-toggle.expanded {
  background: #7c3aed;
  color: white;
}

/* Inline add-ons section */
.addons-section {
  background: #faf5ff;
  border-radius: 0 0 10px 10px;
  margin: -4px 16px 0 72px;
  padding: 8px 12px;
  border: 1px solid #e9d5ff;
  border-top: none;
}

.addon-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.addon-row:hover {
  background: #f3e8ff;
}

.addon-row.selected {
  background: #ede9fe;
}

.addon-checkbox-visual {
  width: 20px;
  height: 20px;
  border: 2px solid #a78bfa;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #7c3aed;
  flex-shrink: 0;
  transition: all 0.15s;
}

.addon-row.selected .addon-checkbox-visual {
  background: #7c3aed;
  border-color: #7c3aed;
  color: white;
}

.addon-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.addon-name {
  font-size: 13px;
  font-weight: 500;
  color: #4c1d95;
}

.addon-price {
  font-size: 13px;
  font-weight: 600;
  color: #7c3aed;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #64748b;
  font-size: 16px;
}

/* Floating cart button */
.cart-fab {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background: #3b82f6;
  color: white;
  border-radius: 28px;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
  z-index: 100;
  transition: transform 0.2s;
}

.cart-fab:hover {
  transform: scale(1.05);
}

.cart-fab-count {
  background: #ef4444;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

/* Cart drawer overlay */
.cart-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
}

.cart-drawer {
  background: white;
  border-radius: 20px 20px 0 0;
  width: 100%;
  max-width: 500px;
  max-height: 85vh;
  overflow: hidden;
  box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.2);
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

.cart-empty {
  padding: 40px 20px;
  text-align: center;
  color: #9ca3af;
  font-size: 16px;
}

.cart-items {
  max-height: 50vh;
  overflow-y: auto;
  padding: 16px 20px;
}

.cart-line {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f1f5f9;
  gap: 8px;
}

.cart-line.is-addon {
  padding-left: 16px;
  background: #f8fafc;
  border-radius: 4px;
}

.cart-line-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.cart-line-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.cart-line.is-addon .cart-line-name {
  font-size: 13px;
  font-weight: 500;
  color: #6b7280;
}

.cart-line-detail {
  font-size: 12px;
  color: #9ca3af;
}

.cart-line-subtotal {
  font-weight: 700;
  font-size: 14px;
  color: #059669;
}

.cart-line-remove {
  background: none;
  border: none;
  color: #d1d5db;
  cursor: pointer;
  font-size: 14px;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.15s;
}

.cart-line-remove:hover {
  color: #ef4444;
  background: #fee2e2;
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
