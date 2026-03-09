/**
 * Orders Store (Pinia)
 *
 * The current frontend screens expect an orders store for billing totals.
 * Until the backend order endpoints are wired, this store provides a small
 * in-memory model so the app can run without runtime errors.
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import type { OrderItem } from '@/types/pos'

export const useOrdersStore = defineStore('orders', () => {
  const orderItems = ref<OrderItem[]>([])

  const getOrderItemsByTableGroup = (tableGroupId: string) => {
    return orderItems.value.filter((o) => o.tableGroupId === tableGroupId)
  }

  const totalForTableGroup = (tableGroupId: string) => {
    return getOrderItemsByTableGroup(tableGroupId).reduce((sum, item) => {
      const unitPrice =
        item.priceOverride ??
        item.menuItem?.price ??
        0
      return sum + unitPrice * item.quantity
    }, 0)
  }

  const totalAll = computed(() => {
    return orderItems.value.reduce((sum, item) => {
      const unitPrice =
        item.priceOverride ??
        item.menuItem?.price ??
        0
      return sum + unitPrice * item.quantity
    }, 0)
  })

  return {
    orderItems,
    getOrderItemsByTableGroup,
    totalForTableGroup,
    totalAll,
  }
})

