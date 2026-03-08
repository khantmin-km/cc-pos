/**
 * Tables API Module
 * 
 * Provides methods to interact with the backend tables and table groups API.
 * All methods return promises that resolve to typed data.
 */

<<<<<<< HEAD
import { api, ApiError } from './api'
import { demoTableGroupsApi, demoTablesApi } from './demoBackend'
import { getRuntimeMode, setRuntimeMode } from './runtimeMode'
=======
// Import base API client
import { api } from './api'
>>>>>>> df712ff (frontend_backend)

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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') return demoTablesApi.list()
    return api.get<PhysicalTable[]>('/tables').catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTablesApi.list()
    })
=======
    return api.get<PhysicalTable[]>('/tables')
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') return demoTablesApi.startService(id)
    return api
      .post<TableGroup>(`/tables/${id}/start-service`)
      .catch((e) => {
        if (e instanceof ApiError) setRuntimeMode('demo')
        return demoTablesApi.startService(id)
      })
=======
    return api.post<TableGroup>(
      `/tables/${id}/start-service`
    )
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.listOpen()
    return api.get<TableGroup[]>('/table-groups/open').catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTableGroupsApi.listOpen()
    })
=======
    return api.get<TableGroup[]>('/table-groups/open')
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.get(id)
    return api.get<TableGroup>(`/table-groups/${id}`).catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTableGroupsApi.get(id)
    })
=======
    return api.get<TableGroup>(`/table-groups/${id}`)
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.requestBill(id)
    return api.post<void>(`/table-groups/${id}/request-bill`).catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTableGroupsApi.requestBill(id)
    })
=======
    return api.post<void>(
      `/table-groups/${id}/request-bill`
    )
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.markPaid(id)
    return api.post<void>(`/table-groups/${id}/mark-paid`).catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTableGroupsApi.markPaid(id)
    })
=======
    return api.post<void>(
      `/table-groups/${id}/mark-paid`
    )
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.close(id)
    return api.post<void>(`/table-groups/${id}/close`).catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTableGroupsApi.close(id)
    })
=======
    return api.post<void>(`/table-groups/${id}/close`)
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.addTable(groupId, physicalTableId)
    return api
      .post<void>(`/table-groups/${groupId}/tables/add`, {
        physical_table_id: physicalTableId,
      })
      .catch((e) => {
        if (e instanceof ApiError) setRuntimeMode('demo')
        return demoTableGroupsApi.addTable(groupId, physicalTableId)
      })
=======
    return api.post<void>(
      `/table-groups/${groupId}/tables/add`,
      {
        physical_table_id: physicalTableId,
      }
    )
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.removeTable(groupId, physicalTableId)
    return api
      .post<void>(`/table-groups/${groupId}/tables/remove`, {
        physical_table_id: physicalTableId,
      })
      .catch((e) => {
        if (e instanceof ApiError) setRuntimeMode('demo')
        return demoTableGroupsApi.removeTable(groupId, physicalTableId)
      })
=======
    return api.post<void>(
      `/table-groups/${groupId}/tables/remove`,
      {
        physical_table_id: physicalTableId,
      }
    )
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') {
      return demoTableGroupsApi.switchTable(groupId, fromTableId, toTableId)
    }
    return api
      .post<void>(`/table-groups/${groupId}/switch`, {
        from_table_id: fromTableId,
        to_table_id: toTableId,
      })
      .catch((e) => {
        if (e instanceof ApiError) setRuntimeMode('demo')
        return demoTableGroupsApi.switchTable(groupId, fromTableId, toTableId)
      })
=======
    return api.post<void>(
      `/table-groups/${groupId}/switch`,
      {
        from_table_id: fromTableId,
        to_table_id: toTableId,
      }
    )
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.merge(sourceId, targetId)
    return api
      .post<void>('/table-groups/merge', {
        source_group_id: sourceId,
        target_group_id: targetId,
      })
      .catch((e) => {
        if (e instanceof ApiError) setRuntimeMode('demo')
        return demoTableGroupsApi.merge(sourceId, targetId)
      })
=======
    return api.post<void>('/table-groups/merge', {
      source_group_id: sourceId,
      target_group_id: targetId,
    })
>>>>>>> df712ff (frontend_backend)
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
<<<<<<< HEAD
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.split(id, physicalTableIds)
    return api
      .post<TableGroup>(`/table-groups/${id}/split`, {
        physical_table_ids: physicalTableIds,
      })
      .catch((e) => {
        if (e instanceof ApiError) setRuntimeMode('demo')
        return demoTableGroupsApi.split(id, physicalTableIds)
      })
=======
    return api.post<TableGroup>(
      `/table-groups/${id}/split`,
      {
        physical_table_ids: physicalTableIds,
      }
    )
>>>>>>> df712ff (frontend_backend)
  },
}
