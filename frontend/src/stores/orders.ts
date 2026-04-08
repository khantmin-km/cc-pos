/**
 * Orders Store (Pinia)
 * 
 * Manages orders and order placement workflow.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

import type { OrderItem, OrderConfirmRequest } from '@/types/pos'
import { ordersApi, orderItemsApi, tablesApi } from '@/services/tablesApi'
import type { PhysicalTable } from '@/types/pos'

/**
 * Orders Store
 */
export const useOrdersStore = defineStore('orders', () => {
  // --------------------------------
  // State
  // --------------------------------

  /** Order items by table group */
  const orderItems = ref<OrderItem[]>([])

  /** Current draft order items being built */
  const draftItems = ref<OrderItem[]>([])

  /** Loading state */
  const loading = ref(false)

  /** Error message */
  const error = ref<string | null>(null)

  // --------------------------------
  // Getters (Computed)
  // --------------------------------

  /**
   * Get order items by table group
   */
  const getOrderItemsByTableGroup = (tableGroupId: string) => {
    return orderItems.value.filter((o) => o.tableGroupId === tableGroupId)
  }

  /**
   * Get total for specific table group
   */
  const totalForTableGroup = (tableGroupId: string) => {
    return getOrderItemsByTableGroup(tableGroupId).reduce((sum, item) => {
      const unitPrice =
        item.priceOverride ??
        item.menuItem?.price ??
        0
      return sum + unitPrice * item.quantity
    }, 0)
  }

  /** Get draft order total */
  const draftTotal = computed(() => {
    return draftItems.value.reduce((sum, item) => {
      return sum + item.quantity * (item.priceOverride ?? 0)
    }, 0)
  })

  /** Get draft item count */
  const draftItemCount = computed(() => {
    return draftItems.value.reduce((sum, item) => sum + item.quantity, 0)
  })

  const totalAll = computed(() => {
    return orderItems.value.reduce((sum, item) => {
      const unitPrice =
        item.priceOverride ??
        item.menuItem?.price ??
        0
      return sum + unitPrice * item.quantity
    }, 0)
  })

  // --------------------------------
  // Actions (Methods)
  // --------------------------------

  /**
   * Add item to draft order
   */
  function addDraftItem(item: OrderItem) {
    const existing = draftItems.value.find(
      (di) => di.menuItemId === item.menuItemId && di.notes === item.notes
    )

    if (existing) {
      existing.quantity += item.quantity
    } else {
      draftItems.value.push({
        ...item,
        status: 'pending',
        kitchenPrinted: false,
        served: false,
        removed: false,
      })
    }
  }

  /**
   * Remove item from draft order
   */
  function removeDraftItem(menuItemId: string, notes?: string) {
    draftItems.value = draftItems.value.filter((item) => {
      return !(item.menuItemId === menuItemId && item.notes === notes)
    })
  }

  /**
   * Update draft item quantity
   */
  function updateDraftItem(menuItemId: string, quantity: number, notes?: string) {
    const item = draftItems.value.find(
      (item) => item.menuItemId === menuItemId && item.notes === notes
    )

    if (item) {
      item.quantity = Math.max(0, quantity)
    }
  }

  /**
   * Confirm and place the draft order
   */
  async function confirmOrder(tableId: string) {
    if (draftItems.value.length === 0) {
      error.value = 'No items in order'
      return
    }

    loading.value = true
    error.value = null

    try {
      const request: OrderConfirmRequest = {
        idempotencyKey: `order_${Date.now()}_${Math.random()}`,
        items: draftItems.value.map((item) => ({
          menuItemId: item.menuItemId,
          quantity: item.quantity,
          notes: item.notes,
        })),
      }

      const response = await ordersApi.confirmOrder(tableId, request)

      // Add to order items
      draftItems.value.forEach((draftItem, idx) => {
        orderItems.value.push({
          ...draftItem,
          id: response.orderItemIds[idx],
          tableGroupId: response.tableGroupId,
        })
      })

      // Clear draft
      draftItems.value = []

      return response
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to confirm order'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear draft order without confirming
   */
  function clearDraft() {
    draftItems.value = []
    error.value = null
  }

  /**
   * Void an order item
   */
  async function voidOrderItem(orderItemId: string) {
    loading.value = true
    error.value = null

    try {
      await orderItemsApi.void(orderItemId)

      // Update local state
      const item = orderItems.value.find((i) => i.id === orderItemId)
      if (item) {
        item.removed = true
        item.status = 'removed'
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to void item'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Mark order item as served
   */
  async function markOrderItemServed(orderItemId: string) {
    loading.value = true
    error.value = null

    try {
      await orderItemsApi.markServed(orderItemId)

      // Update local state
      const item = orderItems.value.find((i) => i.id === orderItemId)
      if (item) {
        item.served = true
        item.status = 'served'
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to mark served'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Reprint an order item
   */
  async function reprintOrderItem(orderItemId: string) {
    loading.value = true
    error.value = null

    try {
      await orderItemsApi.reprint(orderItemId)
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to reprint item'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Fetch order items for a specific table
   */
  async function fetchOrderItems(tableId: string) {
    loading.value = true
    error.value = null

    try {
      // First get table to find its table group ID
      const tablesResponse = await tablesApi.list()
      const table: PhysicalTable | undefined = tablesResponse.find((t: PhysicalTable) => t.id === tableId)
      
      if (table?.current_table_group_id) {
        // Use table group endpoint to get order items
        await orderItemsApi.getByTableGroup(table.current_table_group_id)
        console.log('[ORDERS] Fetched order items for table group:', table.current_table_group_id)
      } else {
        console.log('[ORDERS] Table has no group, no order items to fetch')
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to fetch order items'
      error.value = msg
      console.error('Fetch failed:', e)
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    orderItems,
    draftItems,
    loading,
    error,

    // Getters
    getOrderItemsByTableGroup,
    totalForTableGroup,
    draftTotal,
    draftItemCount,
    totalAll,

    // Actions
    addDraftItem,
    removeDraftItem,
    updateDraftItem,
    confirmOrder,
    clearDraft,
    voidOrderItem,
    markOrderItemServed,
    reprintOrderItem,
    fetchOrderItems,
  }
})

