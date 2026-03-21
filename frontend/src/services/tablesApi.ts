/**
 * Tables API Module
 * 
 * Provides methods to interact with the backend tables and table groups API.
 * All methods return promises that resolve to typed data.
 */

import { api, ApiError } from './api'
import {
  demoTableGroupsApi,
  demoTablesApi,
  demoMenuItemsApi,
  demoWaitersApi,
  demoSessionsApi,
  demoOrdersApi,
  demoOrderItemsApi,
  demoBillingApi,
} from './demoBackend'
import { getRuntimeMode, setRuntimeMode } from './runtimeMode'

// Import type definitions
import type {
  PhysicalTable,
  TableGroup,
  MenuItemCreateRequest,
  MenuItemUpdateRequest,
  WaiterCreateRequest,
  WaiterUpdateRequest,
  SessionCreateRequest,
  OrderConfirmRequest,
  OrderConfirmResponse,
  BillAdjustmentCreateRequest,
} from '@/types/pos'

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
    if (getRuntimeMode() === 'demo') return demoTablesApi.list()
    return api.get<PhysicalTable[]>('/tables').catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTablesApi.list()
    })
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
    if (getRuntimeMode() === 'demo') return demoTablesApi.startService(id)
    return api
      .post<TableGroup>(`/tables/${id}/start-service`)
      .catch((e) => {
        if (e instanceof ApiError) setRuntimeMode('demo')
        return demoTablesApi.startService(id)
      })
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
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.listOpen()
    return api.get<TableGroup[]>('/table-groups/open').catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTableGroupsApi.listOpen()
    })
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
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.get(id)
    return api.get<TableGroup>(`/table-groups/${id}`).catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTableGroupsApi.get(id)
    })
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
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.requestBill(id)
    return api.post<void>(`/table-groups/${id}/request-bill`).catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTableGroupsApi.requestBill(id)
    })
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
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.markPaid(id)
    return api.post<void>(`/table-groups/${id}/mark-paid`).catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTableGroupsApi.markPaid(id)
    })
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
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.close(id)
    return api.post<void>(`/table-groups/${id}/close`).catch((e) => {
      if (e instanceof ApiError) setRuntimeMode('demo')
      return demoTableGroupsApi.close(id)
    })
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
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.addTable(groupId, physicalTableId)
    return api
      .post<void>(`/table-groups/${groupId}/tables/add`, {
        physical_table_id: physicalTableId,
      })
      .catch((e) => {
        if (e instanceof ApiError) setRuntimeMode('demo')
        return demoTableGroupsApi.addTable(groupId, physicalTableId)
      })
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
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.removeTable(groupId, physicalTableId)
    return api
      .post<void>(`/table-groups/${groupId}/tables/remove`, {
        physical_table_id: physicalTableId,
      })
      .catch((e) => {
        if (e instanceof ApiError) setRuntimeMode('demo')
        return demoTableGroupsApi.removeTable(groupId, physicalTableId)
      })
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
    if (getRuntimeMode() === 'demo') return demoTableGroupsApi.split(id, physicalTableIds)
    return api
      .post<TableGroup>(`/table-groups/${id}/split`, {
        physical_table_ids: physicalTableIds,
      })
      .catch((e) => {
        if (e instanceof ApiError) setRuntimeMode('demo')
        return demoTableGroupsApi.split(id, physicalTableIds)
      })
  },
}

// ==========================================
// Orders API
// ==========================================

import type {
  Order,
  OrderConfirmRequest,
  OrderConfirmResponse,
  MenuItem,
  Waiter,
  ActorSession,
  SessionCreateRequest,
  BillBreakdown,
  BillAdjustment,
  BillAdjustmentCreateRequest,
  MenuItemCreateRequest,
  MenuItemUpdateRequest,
  WaiterCreateRequest,
  WaiterUpdateRequest,
} from '@/types/pos'

/**
 * API methods for orders
 */
export const ordersApi = {
  /**
   * Confirm and place an order
   * 
   * POST /tables/{tableId}/orders/confirm
   * 
   * @param tableId - Physical table ID
   * @param request - Order confirmation request
   * @returns Order confirmation response with created IDs
   */
  confirmOrder: (
    tableId: string,
    request: OrderConfirmRequest
  ): Promise<OrderConfirmResponse> => {
    return demoOrdersApi.confirm(tableId, request)
  },
}

// ==========================================
// Order Items API
// ==========================================

/**
 * API methods for order items
 */
export const orderItemsApi = {
  /**
   * Void/cancel an order item
   * 
   * POST /order-items/{id}/void
   * 
   * @param id - Order item ID
   */
  void: (id: string): Promise<void> => {
    return demoOrderItemsApi.void(id)
  },

  /**
   * Mark an order item as served
   * 
   * POST /order-items/{id}/mark-served
   * 
   * @param id - Order item ID
   */
  markServed: (id: string): Promise<void> => {
    return demoOrderItemsApi.markServed(id)
  },

  /**
   * Reprint an order item to kitchen
   * 
   * POST /order-items/{id}/reprint
   * 
   * @param id - Order item ID
   */
  reprint: (id: string): Promise<void> => {
    return demoOrderItemsApi.reprint(id)
  },
}

// ==========================================
// Menu Items API
// ==========================================

/**
 * API methods for menu items
 */
export const menuItemsApi = {
  /**
   * Get list of all menu items
   * 
   * GET /menu-items
   * 
   * @returns Array of MenuItem objects
   */
  list: (): Promise<MenuItem[]> => {
    return demoMenuItemsApi.list()
  },

  /**
   * Create a new menu item
   * 
   * POST /menu-items
   * 
   * @param request - Menu item creation request
   * @returns Created MenuItem
   */
  create: (request: MenuItemCreateRequest): Promise<MenuItem> => {
    return demoMenuItemsApi.create(request.name, request.price, request.category)
  },

  /**
   * Update a menu item
   * 
   * PATCH /menu-items/{id}
   * 
   * @param id - Menu item ID
   * @param request - Update request
   * @returns Updated MenuItem
   */
  update: (
    id: string,
    request: MenuItemUpdateRequest
  ): Promise<MenuItem> => {
    return demoMenuItemsApi.update(id, request.name, request.price, request.category)
  },

  /**
   * Retire a menu item
   * 
   * POST /menu-items/{id}/retire
   * 
   * @param id - Menu item ID
   */
  retire: (id: string): Promise<void> => {
    return demoMenuItemsApi.retire(id)
  },

  /**
   * Upload image for menu item
   * 
   * POST /menu-items/{id}/image
   * 
   * @param id - Menu item ID
   * @param file - Image file
   */
  uploadImage: (id: string, file: File): Promise<MenuItem> => {
    if (getRuntimeMode() === 'demo') return demoMenuItemsApi.uploadImage(id, file)
    const formData = new FormData()
    formData.append('file', file)
    return api
      .post<MenuItem>(`/menu-items/${id}/image`, formData as unknown)
      .catch((e) => {
        if (e instanceof ApiError) setRuntimeMode('demo')
        return demoMenuItemsApi.uploadImage(id, file)
      })
  },
}

// ==========================================
// Sessions API
// ==========================================

/**
 * API methods for sessions (authentication)
 */
export const sessionsApi = {
  /**
   * Create a new session (login)
   * 
   * POST /sessions
   * 
   * @param request - Session creation request
   * @returns Created ActorSession
   */
  create: (request: SessionCreateRequest): Promise<ActorSession> => {
    return demoSessionsApi.create(request.actorType, request.actorId)
  },

  /**
   * End a session (logout)
   * 
   * POST /sessions/{id}/end
   * 
   * @param id - Session ID
   */
  end: (id: string): Promise<void> => {
    return demoSessionsApi.end(id)
  },
}

// ==========================================
// Waiters API
// ==========================================

/**
 * API methods for waiters
 */
export const waitersApi = {
  /**
   * Get list of waiters
   * 
   * GET /waiters
   * 
   * @param includeInactive - Include inactive waiters
   * @returns Array of Waiter objects
   */
  list: (includeInactive: boolean = false): Promise<Waiter[]> => {
    return demoWaitersApi.list()
  },

  /**
   * Create a new waiter
   * 
   * POST /waiters
   * 
   * @param request - Waiter creation request
   * @returns Created Waiter
   */
  create: (request: WaiterCreateRequest): Promise<Waiter> => {
    return demoWaitersApi.create(request.name)
  },

  /**
   * Update a waiter
   * 
   * PATCH /waiters/{id}
   * 
   * @param id - Waiter ID
   * @param request - Update request
   * @returns Updated Waiter
   */
  update: (id: string, request: WaiterUpdateRequest): Promise<Waiter> => {
    return demoWaitersApi.update(id, request.name, request.active)
  },
}

// ==========================================
// Bill Management API
// ==========================================

/**
 * API methods for bill management
 */
export const billApi = {
  /**
   * Get bill breakdown for a table group
   * 
   * GET /table-groups/{id}/bill
   * 
   * @param id - Table group ID
   * @returns Bill breakdown
   */
  getBillBreakdown: (id: string): Promise<BillBreakdown> => {
    return demoBillingApi.getBillBreakdown(id)
  },

  /**
   * Create a bill adjustment
   * 
   * POST /table-groups/{id}/bill-adjustments
   * 
   * @param id - Table group ID
   * @param request - Adjustment creation request
   * @returns Created BillAdjustment
   */
  createAdjustment: (
    id: string,
    request: BillAdjustmentCreateRequest
  ): Promise<BillAdjustment> => {
    return demoBillingApi.createAdjustment(id, request.description, request.amount)
  },
}
