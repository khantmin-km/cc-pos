/**
 * Billing Store (Pinia)
 * 
 * Manages bill and billing adjustments.
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

import type { BillBreakdown, BillAdjustment, BillAdjustmentCreateRequest } from '@/types/pos'
import { billApi } from '@/services/tablesApi'

/**
 * Billing Store
 */
export const useBillingStore = defineStore('billing', () => {
  // --------------------------------
  // State
  // --------------------------------

  /** Current bill breakdown */
  const currentBill = ref<BillBreakdown | null>(null)

  /** Loading state */
  const loading = ref(false)

  /** Error message */
  const error = ref<string | null>(null)

  // --------------------------------
  // Actions (Methods)
  // --------------------------------

  /**
   * Fetch bill breakdown for a table group
   */
  async function fetchBillBreakdown(tableGroupId: string) {
    loading.value = true
    error.value = null

    try {
      currentBill.value = await billApi.getBillBreakdown(tableGroupId)
      return currentBill.value
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to fetch bill'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Create a bill adjustment
   */
  async function createAdjustment(
    tableGroupId: string,
    request: BillAdjustmentCreateRequest
  ) {
    loading.value = true
    error.value = null

    try {
      const adjustment = await billApi.createAdjustment(tableGroupId, request)

      if (currentBill.value) {
        currentBill.value.adjustments.push(adjustment)
        currentBill.value.total += adjustment.amount
      }

      return adjustment
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed to create adjustment'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Clear current bill
   */
  function clearBill() {
    currentBill.value = null
    error.value = null
  }

  return {
    // State
    currentBill,
    loading,
    error,

    // Actions
    fetchBillBreakdown,
    createAdjustment,
    clearBill,
  }
})
