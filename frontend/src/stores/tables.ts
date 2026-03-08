/**
 * Tables Store (Pinia)
 * 
 * Manages physical table data from the backend API.
 * Provides computed properties for UI-friendly table objects.
 */

// Vue imports
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// Type imports
import type {
  PhysicalTable,
  Table,
  TableStatus,
  TableArea,
} from '../types/pos'

// API imports
import { tablesApi } from '../services/tablesApi'

// ==========================================
// Helper Functions
// ==========================================

/**
 * Convert backend PhysicalTable to frontend Table
 * 
 * @param pt - PhysicalTable from backend API
 * @returns Table object for UI display
 */
function mapPhysicalTableToTable(
  pt: PhysicalTable
): Table {
  // Extract table number from code (e.g., "T-5" -> 5)
  const match = pt.table_code.match(/\d+/)
  const number = match
    ? parseInt(match[0], 10)
    : 0

  // Determine status based on group membership
  const status: TableStatus =
    pt.current_table_group_id
      ? 'occupied'
      : 'available'

  // Build and return the Table object
  return {
    id: pt.id,
    number,
    status,
    area: 'indoor' as TableArea,
    tableGroupId: pt.current_table_group_id || undefined,
  }
}

// ==========================================
// Store Definition
// ==========================================

/**
 * Tables Store
 */
export const useTablesStore = defineStore(
  'tables',
  () => {
    // --------------------------------
    // State
    // --------------------------------

    /** Raw table data from backend */
    const physicalTables = ref<PhysicalTable[]>([])

    /** Currently selected area filter */
    const currentArea = ref<TableArea>('indoor')

    /** Loading state for async operations */
    const loading = ref(false)

    /** Error message from last operation */
    const error = ref<string | null>(null)

    // --------------------------------
    // Getters (Computed)
    // --------------------------------

    /** Tables formatted for UI display */
    const tables = computed<Table[]>(() => {
      return physicalTables.value.map(
        mapPhysicalTableToTable
      )
    })

    /** Tables filtered by current area */
    const tablesByArea = computed(() => {
      return tables.value.filter((t) => {
        return t.area === currentArea.value
      })
    })

    // --------------------------------
    // Helper Functions
    // --------------------------------

    /**
     * Find table by ID
     * @param id - Table ID to find
     */
    const getTableById = (id: string) => {
      return tables.value.find((t) => t.id === id)
    }

    /**
     * Change the current area filter
     * @param area - New area to filter by
     */
    const setCurrentArea = (area: TableArea) => {
      currentArea.value = area
    }

    // --------------------------------
    // API Actions
    // --------------------------------

    /**
     * Fetch all tables from backend
     */
    const fetchTables = async () => {
      // Set loading state
      loading.value = true

      // Clear previous error
      error.value = null

      try {
        // Call API
        const data = await tablesApi.list()

        // Update state with response
        physicalTables.value = data
      } catch (e) {
        // Handle error
        const message = e instanceof Error
          ? e.message
          : 'Failed to fetch tables'

        error.value = message

        console.error('Failed to fetch tables:', e)
      } finally {
        // Clear loading state
        loading.value = false
      }
    }

    /**
     * Start service for a table
     * Creates a new table group
     * 
     * @param tableId - Table ID to start service
     */
    const startService = async (tableId: string) => {
      try {
        // Call API to create group
        const newGroup = await tablesApi.startService(
          tableId
        )

        // Refresh tables to get updated state
        await fetchTables()

        return newGroup
      } catch (e) {
        // Handle error
        const message = e instanceof Error
          ? e.message
          : 'Failed to start service'

        error.value = message

        console.error('Failed to start service:', e)

        throw e
      }
    }

    // --------------------------------
    // Return Store Interface
    // --------------------------------

    return {
      // State
      physicalTables,
      tables,
      currentArea,
      loading,
      error,

      // Getters
      tablesByArea,
      getTableById,

      // Actions
      setCurrentArea,
      fetchTables,
      startService,
    }
  }
)
