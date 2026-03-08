/**
 * Table Groups Store (Pinia)
 * 
 * Manages table group data from the backend API.
 * Provides computed properties for UI-friendly group objects.
 */

// Vue imports
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Type imports
import type {
  TableGroup,
  TableGroupUI,
  BillingStatus,
} from '../types/pos'

// Store imports
import { useTablesStore } from './tables'

// API imports
import { tableGroupsApi } from '../services/tablesApi'

// ==========================================
// Helper Functions
// ==========================================

/**
 * Convert backend TableGroup to UI format
 * 
 * @param backendGroup - TableGroup from API
 * @returns TableGroupUI for display
 */
function mapBackendToUI(
  backendGroup: TableGroup
): TableGroupUI {
  // Map backend state to frontend billing status
  const billingStatusMap: Record<string, BillingStatus> = {
    open: 'active',
    bill_requested: 'bill_requested',
    paid: 'payment_completed',
    closed: 'closed',
  }

  // Get status or default to active
  const normalizedState = backendGroup.state
    ? backendGroup.state.toLowerCase()
    : 'open'
  const status = billingStatusMap[normalizedState]
    || 'active'

  // Generate display name from ID suffix
  const name = `Group ${backendGroup.id.slice(-4)}`

  // Build and return UI object
  return {
    id: backendGroup.id,
    name,
    tableIds: backendGroup.physical_table_ids.map(
      (id) => id.toString()
    ),
    billingStatus: status,
    createdAt: new Date(backendGroup.opened_at),
  }
}

// ==========================================
// Store Definition
// ==========================================

export const useTableGroupsStore = defineStore(
  'tableGroups',
  () => {
    // --------------------------------
    // State
    // --------------------------------

    /** Raw group data from backend */
    const backendGroups = ref<TableGroup[]>([])

    /** Access to tables store */
    const tablesStore = useTablesStore()

    /** Loading state */
    const loading = ref(false)

    /** Error message */
    const error = ref<string | null>(null)

    // --------------------------------
    // Getters (Computed)
    // --------------------------------

    /** Groups formatted for UI */
    const tableGroups = computed<TableGroupUI[]>(() => {
      return backendGroups.value.map(mapBackendToUI)
    })

    /** All tables from tables store */
    const allTables = computed(() => {
      return tablesStore.tables
    })

    /** Tables not in any group */
    const ungroupedTables = computed(() => {
      // Collect all grouped table IDs
      const groupedIds = new Set<string>()

      for (const group of tableGroups.value) {
        for (const tableId of group.tableIds) {
          groupedIds.add(tableId)
        }
      }

      // Filter tables not in any group
      return allTables.value.filter((t) => {
        return !groupedIds.has(t.id)
      })
    })

    // --------------------------------
    // Helper Functions
    // --------------------------------

    /**
     * Find group by ID
     * @param id - Group ID
     */
    const getTableGroupById = (id: string) => {
      return tableGroups.value.find((tg) => tg.id === id)
    }

    /**
     * Find group containing a specific table
     * @param tableId - Table ID
     */
    const getTableGroupByTableId = (tableId: string) => {
      return tableGroups.value.find((tg) => {
        return tg.tableIds.includes(tableId)
      })
    }

    // --------------------------------
    // API Actions
    // --------------------------------

    /**
     * Fetch all open groups from backend
     */
    const fetchOpenGroups = async () => {
      loading.value = true
      error.value = null

      try {
        const data = await tableGroupsApi.listOpen()
        backendGroups.value = data
      } catch (e) {
        const msg = e instanceof Error
          ? e.message
          : 'Failed to fetch groups'
        error.value = msg
        console.error(msg, e)
      } finally {
        loading.value = false
      }
    }

    /**
     * Fetch a single group by ID
     * @param id - Group ID
     */
    const fetchGroup = async (id: string) => {
      try {
        const group = await tableGroupsApi.get(id)

        // Update in local list
        const index = backendGroups.value.findIndex(
          (g) => g.id === id
        )

        if (index >= 0) {
          backendGroups.value[index] = group
        } else {
          backendGroups.value.push(group)
        }

        return group
      } catch (e) {
        const msg = e instanceof Error
          ? e.message
          : 'Failed to fetch group'
        error.value = msg
        console.error(msg, e)
        throw e
      }
    }

    /**
     * Request bill for a group
     * @param groupId - Group ID
     */
    const requestBill = async (groupId: string) => {
      try {
        await tableGroupsApi.requestBill(groupId)
        await fetchOpenGroups()
      } catch (e) {
        const msg = e instanceof Error
          ? e.message
          : 'Failed to request bill'
        error.value = msg
        console.error(msg, e)
        throw e
      }
    }

    /**
     * Mark group as paid
     * @param groupId - Group ID
     */
    const markPaid = async (groupId: string) => {
      try {
        await tableGroupsApi.markPaid(groupId)
        await fetchOpenGroups()
      } catch (e) {
        const msg = e instanceof Error
          ? e.message
          : 'Failed to mark paid'
        error.value = msg
        console.error(msg, e)
        throw e
      }
    }

    /**
     * Close a table group
     * @param groupId - Group ID
     */
    const closeTableGroup = async (groupId: string) => {
      try {
        await tableGroupsApi.close(groupId)

        // Remove from list after closing
        backendGroups.value = backendGroups.value.filter(
          (g) => g.id !== groupId
        )
      } catch (e) {
        const msg = e instanceof Error
          ? e.message
          : 'Failed to close group'
        error.value = msg
        console.error(msg, e)
        throw e
      }
    }

    /**
     * Add table to group
     * @param groupId - Target group ID
     * @param tableId - Table to add
     */
    const addTableToGroup = async (
      groupId: string,
      tableId: string
    ) => {
      try {
        await tableGroupsApi.addTable(groupId, tableId)
        await fetchOpenGroups()
      } catch (e) {
        const msg = e instanceof Error
          ? e.message
          : 'Failed to add table'
        error.value = msg
        console.error(msg, e)
        throw e
      }
    }

    /**
     * Remove table from group
     * @param groupId - Source group ID
     * @param tableId - Table to remove
     */
    const removeTableFromGroup = async (
      groupId: string,
      tableId: string
    ) => {
      try {
        await tableGroupsApi.removeTable(groupId, tableId)
        await fetchOpenGroups()
      } catch (e) {
        const msg = e instanceof Error
          ? e.message
          : 'Failed to remove table'
        error.value = msg
        console.error(msg, e)
        throw e
      }
    }

    /**
     * Switch table between groups
     * @param groupId - Current group
     * @param fromTableId - Table to move
     * @param toTableId - Destination table
     */
    const switchTable = async (
      groupId: string,
      fromTableId: string,
      toTableId: string
    ) => {
      try {
        await tableGroupsApi.switchTable(
          groupId,
          fromTableId,
          toTableId
        )
        await fetchOpenGroups()
      } catch (e) {
        const msg = e instanceof Error
          ? e.message
          : 'Failed to switch table'
        error.value = msg
        console.error(msg, e)
        throw e
      }
    }

    /**
     * Merge two groups
     * @param sourceId - Group to dissolve
     * @param targetId - Group to keep
     */
    const mergeTableGroups = async (
      sourceId: string,
      targetId: string
    ) => {
      try {
        await tableGroupsApi.merge(sourceId, targetId)
        await fetchOpenGroups()
      } catch (e) {
        const msg = e instanceof Error
          ? e.message
          : 'Failed to merge groups'
        error.value = msg
        console.error(msg, e)
        throw e
      }
    }

    /**
     * Split a group
     * @param groupId - Source group
     * @param tableIdsToMove - Tables for new group
     */
    const splitTableGroup = async (
      groupId: string,
      tableIdsToMove: string[]
    ) => {
      try {
        const newGroup = await tableGroupsApi.split(
          groupId,
          tableIdsToMove
        )
        await fetchOpenGroups()
        return newGroup
      } catch (e) {
        const msg = e instanceof Error
          ? e.message
          : 'Failed to split group'
        error.value = msg
        console.error(msg, e)
        throw e
      }
    }

    // --------------------------------
    // Legacy UI Compatibility
    // --------------------------------

    /**
     * @deprecated Use startService instead
     */
    const createTableGroup = (
      name: string,
      tableIds: string[]
    ) => {
      console.warn(
        'createTableGroup deprecated,' +
        ' use tablesStore.startService'
      )
      return null
    }

    /**
     * @deprecated Use closeTableGroup instead
     */
    const dissolveTableGroup = (groupId: string) => {
      return closeTableGroup(groupId)
    }

    /**
     * @deprecated Use addTableToGroup/removeTableFromGroup
     */
    const moveTableToGroup = (
      tableId: string,
      targetGroupId: string | null
    ) => {
      console.warn(
        'moveTableToGroup deprecated,' +
        ' use addTableToGroup or removeTableFromGroup'
      )
      return false
    }

    /**
     * @deprecated Use requestBill or markPaid
     */
    const updateBillingStatus = (
      groupId: string,
      status: BillingStatus
    ) => {
      console.warn(
        'updateBillingStatus deprecated,' +
        ' use requestBill or markPaid'
      )
    }

    /**
     * Set waiter workflow override (local only)
     * @param groupId - Group ID
     * @param override - Override value
     */
    const setWaiterWorkflowOverride = (
      groupId: string,
      override: boolean
    ) => {
      const group = getTableGroupById(groupId)
      if (group) {
        group.waiterWorkflowOverride = override
      }
    }

    /**
     * Check if group can be closed
     * @param groupId - Group ID
     */
    const canCloseGroup = (groupId: string) => {
      const group = getTableGroupById(groupId)
      return (
        group?.billingStatus === 'payment_completed'
      )
    }

    // --------------------------------
    // Return Store Interface
    // --------------------------------

    return {
      // State
      tableGroups,
      backendGroups,
      loading,
      error,

      // Getters
      ungroupedTables,
      getTableGroupById,
      getTableGroupByTableId,

      // API Actions
      fetchOpenGroups,
      fetchGroup,
      requestBill,
      markPaid,
      closeTableGroup,
      addTableToGroup,
      removeTableFromGroup,
      switchTable,
      mergeTableGroups,
      splitTableGroup,

      // Legacy Actions
      createTableGroup,
      dissolveTableGroup,
      moveTableToGroup,
      updateBillingStatus,
      setWaiterWorkflowOverride,
      canCloseGroup,
    }
  }
)
