/**
 * Menu Items Store (Pinia)
 * 
 * Manages menu items data from the backend API.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

import type { MenuItem, MenuItemCreateRequest, MenuItemUpdateRequest } from '@/types/pos'
import { menuItemsApi } from '@/services/tablesApi'

/**
 * Menu Items Store
 */
export const useMenuItemsStore = defineStore('menuItems', () => {
  // --------------------------------
  // State
  // --------------------------------

  /** All menu items */
  const items = ref<MenuItem[]>([])

  /** Loading state */
  const loading = ref(false)

  /** Error message */
  const error = ref<string | null>(null)

  // --------------------------------
  // Getters (Computed)
  // --------------------------------

  /** Available (not retired) items */
  const availableItems = computed(() => {
    return items.value.filter((item) => item.available)
  })

  /** Items grouped by category */
  const itemsByCategory = computed(() => {
    const grouped: { [key: string]: MenuItem[] } = {}
    items.value.forEach((item) => {
      if (!grouped[item.category]) {
        grouped[item.category] = []
      }
      grouped[item.category].push(item)
    })
    return grouped
  })

  /** Get item by ID */
  const getItem = (id: string): MenuItem | undefined => {
    return items.value.find((item) => item.id === id)
  }

  // --------------------------------
  // Actions (Methods)
  // --------------------------------

  /**
   * Fetch all menu items from backend
   */
  async function fetchMenuItems() {
    loading.value = true
    error.value = null

    try {
      items.value = await menuItemsApi.list()
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to fetch menu items'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Create a new menu item
   */
  async function createMenuItem(request: MenuItemCreateRequest) {
    loading.value = true
    error.value = null

    try {
      const newItem = await menuItemsApi.create(request)
      items.value.push(newItem)
      return newItem
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to create menu item'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Update a menu item
   */
  async function updateMenuItem(id: string, request: MenuItemUpdateRequest) {
    loading.value = true
    error.value = null

    try {
      const updated = await menuItemsApi.update(id, request)
      const idx = items.value.findIndex((item) => item.id === id)
      if (idx >= 0) {
        items.value[idx] = updated
      }
      return updated
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to update menu item'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Retire a menu item
   */
  async function retireMenuItem(id: string) {
    loading.value = true
    error.value = null

    try {
      await menuItemsApi.retire(id)
      const idx = items.value.findIndex((item) => item.id === id)
      if (idx >= 0) {
        items.value[idx].available = false
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to retire menu item'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Upload image for menu item
   */
  async function uploadMenuItemImage(id: string, file: File) {
    loading.value = true
    error.value = null

    try {
      const updated = await menuItemsApi.uploadImage(id, file)
      const idx = items.value.findIndex((item) => item.id === id)
      if (idx >= 0) {
        items.value[idx] = updated
      }
      return updated
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to upload image'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    items,
    loading,
    error,

    // Getters
    availableItems,
    itemsByCategory,
    getItem,

    // Actions
    fetchMenuItems,
    createMenuItem,
    updateMenuItem,
    retireMenuItem,
    uploadMenuItemImage,
  }
})
