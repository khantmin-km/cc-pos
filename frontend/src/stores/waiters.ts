/**
 * Waiters Store (Pinia)
 * 
 * Manages waiters data from the backend API.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

import type { Waiter, WaiterCreateRequest, WaiterUpdateRequest } from '@/types/pos'
import { waitersApi } from '@/services/tablesApi'

/**
 * Waiters Store
 */
export const useWaitersStore = defineStore('waiters', () => {
  // --------------------------------
  // State
  // --------------------------------

  /** All waiters */
  const waiters = ref<Waiter[]>([])

  /** Loading state */
  const loading = ref(false)

  /** Error message */
  const error = ref<string | null>(null)

  // --------------------------------
  // Getters (Computed)
  // --------------------------------

  /** Active waiters only */
  const activeWaiters = computed(() => {
    return waiters.value.filter((w) => w.active)
  })

  /** Get waiter by ID */
  const getWaiter = (id: string): Waiter | undefined => {
    return waiters.value.find((w) => w.id === id)
  }

  // --------------------------------
  // Actions (Methods)
  // --------------------------------

  /**
   * Fetch all waiters from backend
   * Falls back to demo waiters if endpoint is not available
   */
  async function fetchWaiters(includeInactive: boolean = false) {
    loading.value = true
    error.value = null

    try {
      waiters.value = await waitersApi.list(includeInactive)
    } catch (e) {
      // If endpoint doesn't exist (404), use demo waiters instead
      if (e instanceof Error && e.message.includes('404')) {
        console.warn('[Waiters] /waiters endpoint not available, using demo data')
        waiters.value = [
          { id: 'waiter-1', name: 'Waiter 1', active: true, created_at: new Date().toISOString() },
          { id: 'waiter-2', name: 'Waiter 2', active: true, created_at: new Date().toISOString() },
          { id: 'waiter-3', name: 'Waiter 3', active: false, created_at: new Date().toISOString() },
        ]
      } else {
        const msg = e instanceof Error ? e.message : 'Failed to fetch waiters'
        error.value = msg
        console.error('[Waiters] Failed to fetch waiters:', e)
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * Create a new waiter
   */
  async function createWaiter(request: WaiterCreateRequest) {
    loading.value = true
    error.value = null

    try {
      const waiter = await waitersApi.create(request)
      waiters.value.push(waiter)
      return waiter
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to create waiter'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Update a waiter
   */
  async function updateWaiter(id: string, request: WaiterUpdateRequest) {
    loading.value = true
    error.value = null

    try {
      const updated = await waitersApi.update(id, request)
      const idx = waiters.value.findIndex((w) => w.id === id)
      if (idx >= 0) {
        waiters.value[idx] = updated
      }
      return updated
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to update waiter'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    waiters,
    loading,
    error,

    // Getters
    activeWaiters,
    getWaiter,

    // Actions
    fetchWaiters,
    createWaiter,
    updateWaiter,
  }
})
