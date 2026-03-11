import { api, ApiError } from '@/services/api'
import type { BackendMenuItem } from '@/types/pos'
import { getRuntimeMode, setRuntimeMode } from '@/services/runtimeMode'

export type MenuCategory = 'all' | 'main' | 'dessert' | 'beverage'

function demoMenu(): BackendMenuItem[] {
  const now = new Date().toISOString()
  return [
    { id: crypto.randomUUID(), name: 'Fried Chicken With Ice-Cream', price: 1000, status: 'AVAILABLE', created_at: now },
    { id: crypto.randomUUID(), name: 'A Kyaw Sone', price: 2500, status: 'AVAILABLE', created_at: now },
    { id: crypto.randomUUID(), name: 'Tea Leaf Salad', price: 750, status: 'AVAILABLE', created_at: now },
    { id: crypto.randomUUID(), name: 'Fried Ice-Cream', price: 0, status: 'AVAILABLE', created_at: now },
    { id: crypto.randomUUID(), name: 'Mango Sticky Rice', price: 1200, status: 'AVAILABLE', created_at: now },
    { id: crypto.randomUUID(), name: 'Brownie with Vanilla Ice-Cream', price: 1500, status: 'AVAILABLE', created_at: now },
    { id: crypto.randomUUID(), name: 'Fresh Orange Juice', price: 800, status: 'AVAILABLE', created_at: now },
    { id: crypto.randomUUID(), name: 'Iced Latte', price: 1500, status: 'AVAILABLE', created_at: now },
    { id: crypto.randomUUID(), name: 'Green Tea', price: 500, status: 'AVAILABLE', created_at: now },
  ]
}

export const menuApi = {
  list: (): Promise<BackendMenuItem[]> => {
    if (getRuntimeMode() === 'demo') return Promise.resolve(demoMenu())

    return api.get<BackendMenuItem[]>('/menu-items').catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoMenu()
    })
  },
}

