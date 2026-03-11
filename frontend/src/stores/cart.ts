import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import type { MenuItem } from '@/types/pos'

export type CartLine = {
  menuItemId: string
  qty: number
}

export const useCartStore = defineStore('cart', () => {
  const lines = ref<CartLine[]>([])

  const count = computed(() => lines.value.reduce((sum, l) => sum + l.qty, 0))

  function add(item: MenuItem) {
    const line = lines.value.find((l) => l.menuItemId === item.id)
    if (line) line.qty += 1
    else lines.value.unshift({ menuItemId: item.id, qty: 1 })
  }

  function dec(menuItemId: string) {
    const line = lines.value.find((l) => l.menuItemId === menuItemId)
    if (!line) return
    line.qty -= 1
    if (line.qty <= 0) {
      lines.value = lines.value.filter((l) => l.menuItemId !== menuItemId)
    }
  }

  function remove(menuItemId: string) {
    lines.value = lines.value.filter((l) => l.menuItemId !== menuItemId)
  }

  function clear() {
    lines.value = []
  }

  return { lines, count, add, dec, remove, clear }
})

