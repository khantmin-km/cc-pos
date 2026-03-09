/**
 * Menu Store (Pinia)
 * 
 * Manages menu items and categories.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { MenuItem } from '../types/pos'

export const useMenuStore = defineStore('menu', () => {
  // State
  const items = ref<MenuItem[]>([
    { id: '1', name: 'Burger', price: 10, category: 'main', available: true },
    { id: '2', name: 'Fries', price: 5, category: 'side', available: true },
    { id: '3', name: 'Coke', price: 3, category: 'beverage', available: true }
  ])

  // Getters
  const availableItems = computed(() => 
    items.value.filter(i => i.available)
  )

  function getItemById(id: string) {
    return items.value.find(i => i.id === id)
  }

  return { items, availableItems, getItemById }
})
