/**
 * Menu Store (Pinia)
 *
 * Fetches menu items from backend (`/menu-items`) and provides
 * category filtering for the waiter UI.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { BackendMenuItem, MenuItem } from '@/types/pos'
import { menuApi, type MenuCategory } from '@/services/menuApi'

export const useMenuStore = defineStore('menu', () => {
  const items = ref<MenuItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const category = ref<MenuCategory>('all')

  const categoryKey = 'ccpos_menu_category_by_id_v1'

  function loadCategoryMap(): Record<string, Exclude<MenuCategory, 'all'>> {
    const raw = localStorage.getItem(categoryKey)
    if (!raw) return {}
    try {
      return JSON.parse(raw) as Record<string, Exclude<MenuCategory, 'all'>>
    } catch {
      return {}
    }
  }

  function saveCategoryMap(map: Record<string, Exclude<MenuCategory, 'all'>>) {
    localStorage.setItem(categoryKey, JSON.stringify(map))
  }

  function guessCategory(name: string): Exclude<MenuCategory, 'all'> {
    const n = name.toLowerCase()
    if (/(tea|coffee|latte|juice|cola|soda|water)/.test(n)) return 'beverage'
    if (/(ice-?cream|cake|brownie|dessert|sticky rice|pudding)/.test(n)) return 'dessert'
    return 'main'
  }

  function toNumberPrice(p: BackendMenuItem['price']): number {
    if (typeof p === 'number') return p
    const n = Number(p)
    return Number.isFinite(n) ? n : 0
  }

  function mapBackendItem(b: BackendMenuItem, cat: Exclude<MenuCategory, 'all'>): MenuItem {
    return {
      id: b.id,
      name: b.name,
      price: toNumberPrice(b.price),
      category: cat,
      available: b.status === 'AVAILABLE',
    }
  }

  async function fetchMenuItems() {
    loading.value = true
    error.value = null
    try {
      const backend = await menuApi.list()
      const map = loadCategoryMap()
      items.value = backend.map((b) => {
        const cat = map[b.id] ?? guessCategory(b.name)
        return mapBackendItem(b, cat)
      })
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load menu'
    } finally {
      loading.value = false
    }
  }

  function setCategory(next: MenuCategory) {
    category.value = next
  }

  function setItemCategory(id: string, next: Exclude<MenuCategory, 'all'>) {
    const map = loadCategoryMap()
    map[id] = next
    saveCategoryMap(map)
    const item = items.value.find((x) => x.id === id)
    if (item) item.category = next
  }

  const availableItems = computed(() => items.value.filter((i) => i.available))

  const filteredItems = computed(() => {
    if (category.value === 'all') return availableItems.value
    return availableItems.value.filter((i) => i.category === category.value)
  })

  function getItemById(id: string) {
    return items.value.find((i) => i.id === id)
  }

  return {
    items,
    loading,
    error,
    category,
    availableItems,
    filteredItems,
    fetchMenuItems,
    setCategory,
    setItemCategory,
    getItemById,
  }
})
