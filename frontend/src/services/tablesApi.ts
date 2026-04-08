/**
 * Tables API Module - Live Mode Only
 * 
 * Provides methods to interact with the backend tables and table groups API.
 * All methods return promises that resolve to typed data.
 */

import { api } from './api'

// Import type definitions
import type {
  PhysicalTable,
  TableGroup,
  MenuItem,
  MenuItemCreateRequest,
  MenuItemUpdateRequest,
  OrderConfirmRequest,
  OrderConfirmResponse,
  Waiter,
  WaiterCreateRequest,
  WaiterUpdateRequest,
  SessionCreateRequest,
  ActorSession,
  BillBreakdown,
  BillAdjustment,
  BillAdjustmentCreateRequest,
  OrderItem,
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
    return api.post<TableGroup>(`/tables/${id}/start-service`)
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
    return api.post<void>(`/table-groups/${id}/request-bill`)
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
    return api.post<void>(`/table-groups/${id}/mark-paid`)
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
    return api
      .post<void>(`/table-groups/${groupId}/tables/add`, {
        physical_table_id: physicalTableId,
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
    return api
      .post<void>(`/table-groups/${groupId}/tables/remove`, {
        physical_table_id: physicalTableId,
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
    return api
      .post<void>(`/table-groups/${groupId}/switch`, {
        from_table_id: fromTableId,
        to_table_id: toTableId,
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
    return api
      .post<void>('/table-groups/merge', {
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
    return api
      .post<TableGroup>(`/table-groups/${id}/split`, {
        physical_table_ids: physicalTableIds,
      })
  },
}

// ==========================================
// Orders API
// ==========================================

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
    return api.post<OrderConfirmResponse>(`/tables/${tableId}/orders/confirm`, request)
  },
}

// ==========================================
// Order Items API
// ==========================================

/**
 * API methods for order items
 */
export const orderItemsApi = {
  getByTable: (tableId: string): Promise<OrderItem[]> =>
    api.get<OrderItem[]>(`/order-items/table/${tableId}`),

  getByTableGroup: (tableGroupId: string): Promise<OrderItem[]> =>
    api.get<OrderItem[]>(`/table-groups/${tableGroupId}/order-items`),

  void: (id: string): Promise<void> =>
    api.post<void>(`/order-items/${id}/void`),

  /**
   * Mark order item as served
   * 
   * POST /order-items/{id}/mark-served
   * 
   * @param id - Order item ID
   */
  markServed: (id: string): Promise<void> => {
    return api.post<void>(`/order-items/${id}/mark-served`)
  },

  /**
   * Reprint an order item to kitchen
   * 
   * POST /order-items/{id}/reprint
   * 
   * @param id - Order item ID
   */
  reprint: (id: string): Promise<void> => {
    return api.post<void>(`/order-items/${id}/reprint`)
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
    return api.get<MenuItem[]>('/menu-items')
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
    return api.post<MenuItem>('/menu-items', request)
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
    return api.patch<MenuItem>(`/menu-items/${id}`, request)
  },

  /**
   * Retire a menu item
   * 
   * POST /menu-items/{id}/retire
   * 
   * @param id - Menu item ID
   */
  retire: (id: string): Promise<void> => {
    return api.post<void>(`/menu-items/${id}/retire`)
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
    const formData = new FormData()
    formData.append('file', file)
    return api.post<MenuItem>(`/menu-items/${id}/image`, formData as unknown)
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
   * POST /auth/login
   * 
   * @param request - Login request with username and pin
   * @returns Created ActorSession with token
   */
  create: async (request: {
    actorType: 'waiter' | 'admin'
    username: string
    pin: string
  }): Promise<ActorSession> => {
    const response = await api.post<{
      token: string
      user_id: string
      username: string
      role: string
      expires_at: string
    }>('/auth/login', {
      username: request.username,
      pin: request.pin,
    })

    // Map backend response to ActorSession
    return {
      id: response.user_id,
      actorType: response.role as any,
      actorId: request.username,
      actorName: response.username,
      startedAt: new Date().toISOString(),
      token: response.token,
    }
  },

  /**
   * End a session (logout)
   * 
   * POST /sessions/{id}/end
   * 
   * @param id - Session ID
   */
  end: (id: string): Promise<void> => {
    return api.post<void>(`/sessions/${id}/end`)
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
    return api.get<Waiter[]>('/waiters')
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
    return api.post<Waiter>('/waiters', request)
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
    return api.patch<Waiter>(`/waiters/${id}`, request)
  },
}

// ==========================================
// Bill Management API
// ==========================================

/**
 * API methods for bill management
 */
export const billingApi = {
  /**
   * Get bill breakdown for a table group
   * 
   * GET /table-groups/{id}/bill
   * 
   * @param id - Table group ID
   * @returns BillBreakdown object
   */
  getBill: (id: string): Promise<BillBreakdown> => {
    return api.get<BillBreakdown>(`/table-groups/${id}/bill`)
  },

  /**
   * Add adjustment to a bill
   *
   * POST /table-groups/{id}/bill-adjustments
   *
   * @param id - Table group ID
   * @param request - Adjustment creation request
   * @returns Created BillAdjustment
   */
  addAdjustment: (
    id: string,
    request: BillAdjustmentCreateRequest
  ): Promise<BillAdjustment> => {
    return api.post<BillAdjustment>(`/table-groups/${id}/bill-adjustments`, request)
  },

  /**
   * Print bill receipt
   * 
   * POST /table-groups/{id}/print
   * 
   * @param id - Table group ID
   */
  printBill: (id: string): Promise<void> => {
    return api.post<void>(`/table-groups/${id}/print`)
  },
}
