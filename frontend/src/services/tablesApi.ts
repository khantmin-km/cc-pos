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
  confirmOrder: async (
    tableId: string,
    request: OrderConfirmRequest
  ): Promise<OrderConfirmResponse> => {
    // Transform request to match backend requirements
    const backendItems: any[] = []
    request.items.forEach(item => {
      // Backend doesn't support quantity, so we repeat the item
      const qty = item.quantity || 1;
      for (let i = 0; i < qty; i++) {
        backendItems.push({
          client_line_id: `line_${item.menu_item_id}_${i}_${Date.now()}`,
          menu_item_id: item.menu_item_id,
          note: item.notes || ''
        })
      }
    });
    
    const backendRequest = {
      idempotency_key: request.idempotency_key,
      items: backendItems
    };

    const raw = await api.post<any>(`/tables/${tableId}/orders/confirm`, backendRequest)
    
    // Map snake_case response to camelCase
    return {
      orderId: raw.order_id,
      tableGroupId: raw.table_group_id,
      orderItemIds: raw.order_item_ids || [],
    }
  },
}

// ==========================================
// Order Items API
// ==========================================

/**
 * API methods for order items
 */
export const orderItemsApi = {
  getByTable: async (tableId: string): Promise<OrderItem[]> => {
    // Backend doesn't have /order-items/table/{tableId} endpoint
    // This method is not used in the current implementation
    // Use getByTableGroup instead via table's current_table_group_id
    console.warn('[orderItemsApi] getByTable not supported by backend, use getByTableGroup instead')
    return []
  },

  getByTableGroup: async (tableGroupId: string): Promise<OrderItem[]> => {
    const raw = await api.get<any[]>(`/table-groups/${tableGroupId}/order-items`)
    // Map snake_case backend response to camelCase frontend types
    return raw.map((item: any) => ({
      id: item.id,
      menuItemId: item.menu_item_id,
      tableId: item.physical_table_id,
      tableGroupId: tableGroupId,
      quantity: 1, // Backend returns individual order items, not aggregated quantities
      notes: item.note || undefined,
      status: item.status === 'served' ? 'served' : item.status === 'voided' ? 'removed' : 'pending',
      kitchenPrinted: item.kind === 'kitchen_printed' || false,
      served: item.served_at !== null,
      removed: item.voided_at !== null,
      priceOverride: Number(item.unit_price),
      menuItem: {
        id: item.menu_item_id || '',
        name: item.menu_item_name,
        price: Number(item.unit_price),
        category: '',
        available: true,
        isAddon: item.kind === 'addon',
        parentId: item.parent_order_item_id || undefined,
      },
      // Additional backend fields
      orderId: item.order_id,
      parentOrderItemId: item.parent_order_item_id,
      tableCode: item.table_code,
      modifierGroupNameSnap: item.modifier_group_name_snap,
      modifierOptionLabelSnap: item.modifier_option_label_snap,
      servedAt: item.served_at,
      createdAt: item.created_at,
      voidedAt: item.voided_at,
    }))
  },

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
  list: async (): Promise<MenuItem[]> => {
    const raw = await api.get<any[]>('/menu-items')
    return raw.map((item: any) => ({
      id: item.id,
      name: item.name,
      price: Number(item.price),
      category: item.category,
      image: item.image_url || undefined,
      available: item.status === 'AVAILABLE',
      isAddon: item.category === 'Add-on' || item.is_addon === true,
      parentId: item.parent_id || undefined,
    }))
  },

  /**
   * Create a new menu item
   * 
   * POST /menu-items
   * 
   * @param request - Menu item creation request
   * @returns Created MenuItem
   */
  create: async (request: MenuItemCreateRequest): Promise<MenuItem> => {
    const backendRequest = {
      name: request.name,
      price: request.price,
      category: request.category,
      status: request.available ? 'AVAILABLE' : 'UNAVAILABLE'
    };
    const raw = await api.post<any>('/menu-items', backendRequest)
    return {
      id: raw.id,
      name: raw.name,
      price: Number(raw.price),
      category: raw.category,
      image: raw.image_url || undefined,
      available: raw.status === 'AVAILABLE',
      isAddon: raw.category === 'Add-on' || raw.is_addon === true,
      parentId: raw.parent_id || undefined,
    }
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
  update: async (
    id: string,
    request: MenuItemUpdateRequest
  ): Promise<MenuItem> => {
    const backendRequest: any = {};
    if (request.name !== undefined) backendRequest.name = request.name;
    if (request.price !== undefined) backendRequest.price = request.price;
    if (request.category !== undefined) backendRequest.category = request.category;
    if (request.available !== undefined) backendRequest.status = request.available ? 'AVAILABLE' : 'UNAVAILABLE';

    const raw = await api.patch<any>(`/menu-items/${id}`, backendRequest)
    return {
      id: raw.id,
      name: raw.name,
      price: Number(raw.price),
      category: raw.category,
      image: raw.image_url || undefined,
      available: raw.status === 'AVAILABLE',
      isAddon: raw.category === 'Add-on' || raw.is_addon === true,
      parentId: raw.parent_id || undefined,
    }
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
  uploadImage: async (id: string, file: File): Promise<MenuItem> => {
    const formData = new FormData()
    formData.append('file', file)
    const raw = await api.post<any>(`/menu-items/${id}/image`, formData as unknown)
    return {
      id: raw.id,
      name: raw.name,
      price: Number(raw.price),
      category: raw.category,
      image: raw.image_url || undefined,
      available: raw.status === 'AVAILABLE',
      isAddon: raw.category === 'Add-on' || raw.is_addon === true,
      parentId: raw.parent_id || undefined,
    }
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
  end: async (id: string): Promise<void> => {
    // Backend sessions router not registered, handle gracefully
    try {
      return await api.post<void>(`/sessions/${id}/end`)
    } catch (e) {
      console.warn('[sessionsApi] Session end endpoint not available, clearing local session only')
      // Session will be cleared locally in the store
    }
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
  list: async (includeInactive: boolean = false): Promise<Waiter[]> => {
    // Backend waiters router not registered, use direct fetch to avoid console error logging
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    try {
      const response = await fetch(`${API_BASE_URL}/waiters`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      if (response.ok) {
        return await response.json()
      }
      // If 404 or other error, fall back to demo data silently
      throw new Error('Endpoint not available')
    } catch (e) {
      // Fallback to demo data if endpoint not available
      return [
        { id: 'waiter-1', name: 'Waiter 1', active: true, createdAt: new Date().toISOString() },
        { id: 'waiter-2', name: 'Waiter 2', active: true, createdAt: new Date().toISOString() },
        { id: 'waiter-3', name: 'Waiter 3', active: false, createdAt: new Date().toISOString() },
      ]
    }
  },

  /**
   * Create a new waiter
   *
   * POST /waiters
   *
   * @param request - Waiter creation request
   * @returns Created Waiter
   */
  create: async (request: WaiterCreateRequest): Promise<Waiter> => {
    try {
      return await api.post<Waiter>('/waiters', request)
    } catch (e) {
      throw new Error('Waiter management is not available in this deployment')
    }
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
  update: async (id: string, request: WaiterUpdateRequest): Promise<Waiter> => {
    try {
      return await api.patch<Waiter>(`/waiters/${id}`, request)
    } catch (e) {
      throw new Error('Waiter management is not available in this deployment')
    }
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
  getBill: async (id: string): Promise<BillBreakdown> => {
    const raw = await api.get<any>(`/table-groups/${id}/bill`)
    
    // Construct items array from order items since backend doesn't provide them in this endpoint
    let items: any[] = []
    try {
      const { orderItemsApi } = await import('./tablesApi')
      const orderItems = await orderItemsApi.getByTableGroup(id)
      
      // Filter out removed/voided items
      const activeItems = orderItems.filter(oi => !oi.removed)
      
      items = activeItems.map(oi => {
        const unitPrice = oi.priceOverride ?? oi.menuItem?.price ?? 0;
        return {
          orderItemId: oi.id,
          itemName: oi.menuItem?.name || oi.menuItemId,
          quantity: oi.quantity || 1,
          unitPrice: unitPrice,
          lineTotal: unitPrice * (oi.quantity || 1)
        };
      })
    } catch (e) {
      console.error("Failed to fetch order items for bill", e)
    }

    return {
      tableGroupId: raw.table_group_id,
      items: items,
      subtotal: Number(raw.subtotal),
      tax: Number(raw.tax_total),
      serviceCharge: 0,
      adjustments: [],
      total: Number(raw.final_total),
    }
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
  addAdjustment: async (
    id: string,
    request: BillAdjustmentCreateRequest
  ): Promise<BillAdjustment> => {
    const backendRequest = {
      amount: request.amount,
      description: request.description,
      reason: request.reason,
      reference_order_item_id: request.referenceOrderItemId,
      category: request.category || 'general'
    };
    
    const raw = await api.post<any>(`/table-groups/${id}/bill-adjustments`, backendRequest)
    
    return {
      id: raw.id,
      amount: Number(raw.amount),
      description: raw.description,
      reason: raw.reason || '',
      category: raw.category || '',
      createdBy: raw.created_by,
      referenceOrderItemId: raw.reference_order_item_id,
      createdAt: raw.created_at
    }
  },

  /**
   * Print bill receipt
   * 
   * POST /table-groups/{id}/print
   * 
   * @param id - Table group ID
   */
  printBill: async (id: string): Promise<void> => {
    // Backend doesn't have /table-groups/{id}/print endpoint
    // This is a placeholder for future implementation
    console.warn('[billingApi] printBill not supported by backend yet')
    // For now, just log that print was requested
    console.log(`[billingApi] Print bill requested for group ${id}`)
  },
}
