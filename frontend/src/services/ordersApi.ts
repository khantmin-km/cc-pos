/**
 * Orders API Module
 * 
 * Provides methods to interact with the backend orders and order items API.
 * Handles order confirmation and order item operations.
 */

import { api } from './api'

// ==========================================
// Orders API
// ==========================================

export interface OrderItem {
  menu_item_id: string | null
  menu_item_name_snap: string
  unit_price_snap: number
  quantity: number
}

export interface OrderConfirmRequest {
  idempotency_key: string
  items: OrderItem[]
}

export interface OrderConfirmResponse {
  order_id: string
  table_group_id: string
  order_item_ids: string[]
}

/**
 * API methods for orders
 */
export const ordersApi = {
  /**
   * Confirm a new order for a table
   * 
   * POST /tables/{physical_table_id}/orders/confirm
   * 
   * @param tableId - Physical table ID (UUID)
   * @param request - OrderConfirmRequest with idempotency_key and items
   * @returns OrderConfirmResponse with order details
   */
  confirm: async (
    tableId: string,
    request: OrderConfirmRequest
  ): Promise<OrderConfirmResponse> => {
    return await api.post<OrderConfirmResponse>(
      `/tables/${tableId}/orders/confirm`,
      request
    )
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
   * Void an order item (mark as cancelled/voided)
   * 
   * POST /order-items/{order_item_id}/void
   * 
   * @param orderItemId - Order item ID (UUID)
   */
  void: async (orderItemId: string): Promise<void> => {
    return await api.post<void>(`/order-items/${orderItemId}/void`)
  },

  /**
   * Mark an order item as served/completed
   * 
   * POST /order-items/{order_item_id}/mark-served
   * 
   * @param orderItemId - Order item ID (UUID)
   */
  markServed: async (orderItemId: string): Promise<void> => {
    return await api.post<void>(`/order-items/${orderItemId}/mark-served`)
  },

  /**
   * Reprint an order item (send to kitchen printer again)
   * 
   * POST /order-items/{order_item_id}/reprint
   * 
   * @param orderItemId - Order item ID (UUID)
   */
  reprint: async (orderItemId: string): Promise<void> => {
    return await api.post<void>(`/order-items/${orderItemId}/reprint`)
  },
}
