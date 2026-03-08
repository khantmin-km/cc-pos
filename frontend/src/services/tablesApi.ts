/**
 * Tables API Module
 * 
 * Provides methods to interact with the backend tables and table groups API.
 * All methods return promises that resolve to typed data.
 */

// Import base API client
import { api } from './api'

// Import type definitions
import type {
  PhysicalTable,
  TableGroup,
} from '../types/pos'

// ==========================================
// Physical Tables API
// ==========================================

/**
 * API methods for physical tables
 */
export const tablesApi = {
  /**
   * Get list of all physical tables
   * 
   * GET /tables
   * 
   * @returns Array of PhysicalTable objects
   */
  list: (): Promise<PhysicalTable[]> => {
    return api.get<PhysicalTable[]>('/tables')
  },

  /**
   * Start service for a table
   * Creates a new table group with the given table
   * 
   * POST /tables/{id}/start-service
   * 
   * @param id - Table ID (UUID)
   * @returns Newly created TableGroup
   */
  startService: (
    id: string
  ): Promise<TableGroup> => {
    return api.post<TableGroup>(
      `/tables/${id}/start-service`
    )
  },
}

// ==========================================
// Table Groups API
// ==========================================

/**
 * API methods for table groups
 */
export const tableGroupsApi = {
  /**
   * Get list of all open table groups
   * 
   * GET /table-groups/open
   * 
   * @returns Array of TableGroup objects
   */
  listOpen: (): Promise<TableGroup[]> => {
    return api.get<TableGroup[]>('/table-groups/open')
  },

  /**
   * Get a specific table group by ID
   * 
   * GET /table-groups/{id}
   * 
   * @param id - Table group ID (UUID)
   * @returns TableGroup object
   */
  get: (id: string): Promise<TableGroup> => {
    return api.get<TableGroup>(`/table-groups/${id}`)
  },

  /**
   * Request bill for a table group
   * Changes state to 'bill_requested'
   * 
   * POST /table-groups/{id}/request-bill
   * 
   * @param id - Table group ID
   */
  requestBill: (id: string): Promise<void> => {
    return api.post<void>(
      `/table-groups/${id}/request-bill`
    )
  },

  /**
   * Mark table group as paid
   * Changes state to 'paid'
   * 
   * POST /table-groups/{id}/mark-paid
   * 
   * @param id - Table group ID
   */
  markPaid: (id: string): Promise<void> => {
    return api.post<void>(
      `/table-groups/${id}/mark-paid`
    )
  },

  /**
   * Close a table group
   * Changes state to 'closed'
   * 
   * POST /table-groups/{id}/close
   * 
   * @param id - Table group ID
   */
  close: (id: string): Promise<void> => {
    return api.post<void>(`/table-groups/${id}/close`)
  },

  /**
   * Add a table to an existing group
   * 
   * POST /table-groups/{id}/tables/add
   * 
   * @param groupId - Table group ID
   * @param physicalTableId - Table ID to add
   */
  addTable: (
    groupId: string,
    physicalTableId: string
  ): Promise<void> => {
    return api.post<void>(
      `/table-groups/${groupId}/tables/add`,
      {
        physical_table_id: physicalTableId,
      }
    )
  },

  /**
   * Remove a table from a group
   * 
   * POST /table-groups/{id}/tables/remove
   * 
   * @param groupId - Table group ID
   * @param physicalTableId - Table ID to remove
   */
  removeTable: (
    groupId: string,
    physicalTableId: string
  ): Promise<void> => {
    return api.post<void>(
      `/table-groups/${groupId}/tables/remove`,
      {
        physical_table_id: physicalTableId,
      }
    )
  },

  /**
   * Switch a table from one group to another
   * 
   * POST /table-groups/{id}/switch
   * 
   * @param groupId - Current table group ID
   * @param fromTableId - Table ID to move
   * @param toTableId - Destination table ID
   */
  switchTable: (
    groupId: string,
    fromTableId: string,
    toTableId: string
  ): Promise<void> => {
    return api.post<void>(
      `/table-groups/${groupId}/switch`,
      {
        from_table_id: fromTableId,
        to_table_id: toTableId,
      }
    )
  },

  /**
   * Merge two table groups
   * Source group tables are moved to target group
   * 
   * POST /table-groups/merge
   * 
   * @param sourceId - Source group ID (will be dissolved)
   * @param targetId - Target group ID (will receive tables)
   */
  merge: (
    sourceId: string,
    targetId: string
  ): Promise<void> => {
    return api.post<void>('/table-groups/merge', {
      source_group_id: sourceId,
      target_group_id: targetId,
    })
  },

  /**
   * Split a table group
   * Creates a new group with specified tables
   * 
   * POST /table-groups/{id}/split
   * 
   * @param id - Source group ID
   * @param physicalTableIds - Array of table IDs to move to new group
   * @returns Newly created TableGroup
   */
  split: (
    id: string,
    physicalTableIds: string[]
  ): Promise<TableGroup> => {
    return api.post<TableGroup>(
      `/table-groups/${id}/split`,
      {
        physical_table_ids: physicalTableIds,
      }
    )
  },
}
