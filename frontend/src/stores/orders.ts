/**
 * Orders Store (Pinia)
 * 
 * Manages order items and calculations.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { OrderItem } from '../types/pos'
import { useMenuStore } from './menu'

export const useOrdersStore = defineStore('orders', () => {
  const menuStore = useMenuStore()
  
  // State
  const orderItems = ref<OrderItem[]>([])

  // Getters
  function getOrderItemsByTableGroup(groupId: string): OrderItem[] {
    return orderItems.value.filter(item => item.tableGroupId === groupId)
  }

  function totalForTableGroup(groupId: string): number {
    return getOrderItemsByTableGroup(groupId)
      .filter(item => !item.removed)
      .reduce((sum, item) => {
        const menuItem = menuStore.getItemById(item.menuItemId)
        const price = item.priceOverride ?? menuItem?.price ?? 0
        return sum + (price * item.quantity)
      }, 0)
  }

  return { 
    orderItems, 
    getOrderItemsByTableGroup, 
    totalForTableGroup 
  }
})
