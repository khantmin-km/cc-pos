import { api } from '@/services/api'
import type { BackendMenuItem } from '@/types/pos'

export type MenuCategory = 'all' | 'main' | 'dessert' | 'beverage'

export const menuApi = {
  list: (): Promise<BackendMenuItem[]> => {
    return api.get<BackendMenuItem[]>('/menu-items')
  },
}

