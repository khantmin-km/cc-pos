<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useMenuStore } from '@/stores/menu'
import { useCartStore } from '@/stores/cart'
import { ordersApi } from '@/services/ordersApi'

const route = useRoute()
const router = useRouter()

const tableId = computed(() => String(route.params.tableId || ''))
const tableNumber = computed(() => {
  // tableId is a UUID, but screenshot shows Table - 1; we can show last 2 chars in live,
  // or just show a placeholder "Table - 1" when unknown.
  return 'Table - 1'
})

const menuStore = useMenuStore()
const cartStore = useCartStore()

const showCart = ref(false)
const isConfirming = ref(false)
const confirmError = ref<string | null>(null)

onMounted(async () => {
  await menuStore.fetchMenuItems()
})

/**
 * Handle order confirmation
 */
async function handleConfirmOrder() {
  if (cartStore.lines.length === 0) {
    confirmError.value = 'Please add items to your order'
    return
  }

  isConfirming.value = true
  confirmError.value = null

  try {
    const items = cartStore.lines.map((line) => {
      const menuItem = menuStore.getItemById(line.menuItemId)
      return {
        menu_item_id: line.menuItemId,
        menu_item_name_snap: menuItem?.name ?? 'Unknown',
        unit_price_snap: menuItem?.price ?? 0,
        quantity: line.qty,
      }
    })

    await ordersApi.confirm(tableId.value, {
      idempotency_key: `order-${Date.now()}-${Math.random()}`,
      items,
    })

    // Clear cart and close modal on success
    cartStore.clear()
    showCart.value = false
  } catch (e) {
    confirmError.value = e instanceof Error ? e.message : 'Failed to confirm order'
  } finally {
    isConfirming.value = false
  }
}

const categories = [
  { id: 'all', label: 'All' },
  { id: 'main', label: 'Main Course' },
  { id: 'dessert', label: 'Desserts' },
  { id: 'beverage', label: 'Beverages' },
] as const

function formatPrice(v: number) {
  if (v === 0) return 'Free'
  return `$${v.toLocaleString()}`
}

function priceClass(v: number) {
  return v === 0 ? 'free' : 'paid'
}
</script>

<template>
  <div class="wrap">
    <!-- Top green header -->
    <div class="top">
      <button type="button" class="icon-btn" @click="router.push('/')">
        ←
      </button>

      <div class="brand">
        <div class="kk">KAUNG KAUNG</div>
        <div class="tbl">{{ tableNumber }}</div>
      </div>

      <div class="actions">
        <button type="button" class="cart" @click="showCart = !showCart">
          🧾
          <span v-if="cartStore.count" class="badge">{{ cartStore.count }}</span>
        </button>
        <button type="button" class="menu-btn" @click="showCart = !showCart">
          MENU
        </button>
      </div>
    </div>

    <!-- Category pills -->
    <div class="cats">
      <button
        v-for="c in categories"
        :key="c.id"
        type="button"
        class="cat"
        :data-active="menuStore.category === c.id"
        @click="menuStore.setCategory(c.id)"
      >
        {{ c.label }}
      </button>
    </div>

    <!-- Body -->
    <div v-if="menuStore.loading" class="state">
      Loading menu…
    </div>

    <div v-else-if="menuStore.error" class="state error">
      <div class="t">Couldn’t load menu</div>
      <div class="m">{{ menuStore.error }}</div>
      <button type="button" class="retry" @click="menuStore.fetchMenuItems()">
        Retry
      </button>
    </div>
    <div v-else-if="menuStore.filteredItems.length === 0" class="state">
      <div class="t">No menu items</div>
      <div class="m">Menu is not available right now</div>
    </div>
    <div v-else-if="menuStore.items.length === 0" class="state empty">
      <div class="t">No menu items</div>
      <div class="m">None</div>
    </div>

    <div v-else-if="menuStore.filteredItems.length === 0" class="state empty">
      <div class="t">No items in this category</div>
      <div class="m">None</div>
    </div>

    <div v-else class="list">
      <div
        v-for="item in menuStore.filteredItems"
        :key="item.id"
        class="row"
      >
        <div class="avatar">
          {{ item.name.slice(0, 1).toUpperCase() }}
        </div>

        <div class="info">
          <div class="name">{{ item.name }}</div>
          <div class="price" :class="priceClass(item.price)">
            {{ formatPrice(item.price) }}
          </div>
        </div>

        <button
          type="button"
          class="add"
          @click="cartStore.add(item)"
          aria-label="Add"
        >
          +
        </button>
      </div>
    </div>

    <!-- Cart panel -->
    <div v-if="showCart" class="overlay" @click.self="showCart = false">
      <div class="panel">
        <div class="panel-head">
          <div class="h">Order</div>
          <button type="button" class="close" @click="showCart = false">✕</button>
        </div>

        <div v-if="cartStore.lines.length === 0" class="empty">
          No items yet.
        </div>

        <div v-else class="cart-lines">
          <div v-for="l in cartStore.lines" :key="l.menuItemId" class="line">
            <div class="ln">
              {{ menuStore.getItemById(l.menuItemId)?.name ?? 'Unknown' }}
            </div>
            <div class="qty">
              <button type="button" class="qbtn" @click="cartStore.dec(l.menuItemId)">−</button>
              <span class="q">{{ l.qty }}</span>
              <button
                type="button"
                class="qbtn"
                @click="menuStore.getItemById(l.menuItemId) && cartStore.add(menuStore.getItemById(l.menuItemId)!)"
              >
                +
              </button>
            </div>
          </div>
        </div>

        <div v-if="confirmError" class="error-message">
          {{ confirmError }}
        </div>

        <div class="panel-actions">
          <button type="button" class="clear" @click="cartStore.clear()" :disabled="isConfirming">Clear</button>
          <button
            type="button"
            class="confirm"
            :disabled="isConfirming || cartStore.lines.length === 0"
            @click="handleConfirmOrder"
          >
            {{ isConfirming ? 'Confirming...' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap {
  max-width: 720px;
  margin: 0 auto;
  padding: 18px 14px 40px;
}

.top {
  background: #22c55e;
  border-radius: 18px;
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: 900;
  cursor: pointer;
}

.brand {
  flex: 1;
  color: white;
  min-width: 0;
}

.kk {
  font-weight: 900;
  letter-spacing: 0.03em;
  font-size: 18px;
  line-height: 1.1;
}

.tbl {
  margin-top: 4px;
  font-weight: 700;
  opacity: 0.95;
}

.actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cart {
  position: relative;
  width: 38px;
  height: 38px;
  border-radius: 999px;
  border: none;
  background: rgba(255, 255, 255, 0.25);
  color: white;
  cursor: pointer;
  font-size: 16px;
}

.badge {
  position: absolute;
  top: -6px;
  right: -6px;
  background: #111827;
  color: white;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 900;
  padding: 2px 6px;
}

.menu-btn {
  border: none;
  background: #f5f5f5;
  color: #111827;
  font-weight: 900;
  padding: 10px 14px;
  border-radius: 14px;
  cursor: pointer;
}

.cats {
  display: flex;
  gap: 10px;
  margin: 14px 0 14px;
  flex-wrap: wrap;
}

.cat {
  border: none;
  background: #d1fae5;
  color: #16a34a;
  padding: 8px 14px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 13px;
  cursor: pointer;
}

.cat[data-active='true'] {
  background: #22c55e;
  color: white;
}

.list {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  overflow: hidden;
}

.row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 14px;
  border-top: 1px solid #e5e7eb;
}

.row:first-child {
  border-top: none;
}

.avatar {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  background: #f3f4f6;
  display: grid;
  place-items: center;
  font-weight: 900;
  color: #22c55e;
}

.info {
  flex: 1;
  min-width: 0;
}

.name {
  font-weight: 800;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.price {
  margin-top: 6px;
  font-weight: 900;
  font-size: 13px;
}

.price.paid {
  color: #ef4444;
}

.price.free {
  color: #22c55e;
}

.add {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  border: none;
  background: #22c55e;
  color: white;
  font-size: 22px;
  font-weight: 900;
  cursor: pointer;
}

.state {
  margin-top: 14px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 14px;
  font-weight: 800;
}

.error-message {
  background: #fee2e2;
  color: #991b1b;
  padding: 12px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}

.state.empty {
  background: #f3f4f6;
  border-color: #d1d5db;
  text-align: center;
}

.state.error {
  border-color: #fecaca;
  background: #fff1f2;
}

.t {
  font-weight: 900;
}

.m {
  margin-top: 6px;
  white-space: pre-wrap;
  color: #7f1d1d;
  font-weight: 700;
}

.retry {
  margin-top: 10px;
  border: none;
  background: #111827;
  color: white;
  padding: 8px 12px;
  border-radius: 12px;
  font-weight: 900;
  cursor: pointer;
}

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.5);
  display: grid;
  place-items: end center;
  padding: 14px;
  z-index: 80;
}

.panel {
  width: min(720px, 100%);
  background: white;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid #e5e7eb;
}

.h {
  font-weight: 900;
}

.close {
  border: none;
  background: #f3f4f6;
  border-radius: 10px;
  padding: 6px 10px;
  cursor: pointer;
  font-weight: 900;
}

.empty {
  padding: 14px;
  color: #6b7280;
  font-weight: 700;
}

.cart-lines {
  padding: 8px 14px 6px;
}

.line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-top: 1px solid #f3f4f6;
}

.line:first-child {
  border-top: none;
}

.ln {
  font-weight: 800;
  color: #111827;
  margin-right: 12px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.qty {
  display: flex;
  align-items: center;
  gap: 8px;
}

.qbtn {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: none;
  background: #22c55e;
  color: white;
  font-weight: 900;
  cursor: pointer;
}

.q {
  min-width: 18px;
  text-align: center;
  font-weight: 900;
}

.panel-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 12px 14px;
  border-top: 1px solid #e5e7eb;
}

.clear {
  border: none;
  background: #f3f4f6;
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 900;
  cursor: pointer;
}

.clear:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.confirm {
  border: none;
  background: #111827;
  color: white;
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 900;
  cursor: pointer;
}

.confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>

