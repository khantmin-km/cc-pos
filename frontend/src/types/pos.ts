/**
 * Type Definitions for POS System
 * 
 * This file contains all TypeScript type definitions
 * used throughout the frontend application.
 */

// ==========================================
// Enums and Type Aliases
// ==========================================

/** Available states for a table */
export type TableStatus =
  | 'available'
  | 'reserved'
  | 'occupied'

/** Areas where tables can be located */
export type TableArea =
  | 'indoor'
  | 'outdoor'
  | 'garden'

/** Status of order items in the kitchen workflow */
export type OrderItemStatus =
  | 'pending'
  | 'kitchen_printed'
  | 'served'
  | 'removed'

/** Billing workflow states */
export type BillingStatus =
  | 'active'
  | 'bill_requested'
  | 'payment_completed'
  | 'closed'

/** User roles in the system */
export type UserRole =
  | 'waiter'
  | 'admin'

// ==========================================
// Backend API Types
// ==========================================

/**
 * Physical Table - From backend API
 * 
 * Represents a physical table in the restaurant.
 * Matches the backend database schema.
 */
export interface PhysicalTable {
  /** UUID of the table */
  id: string

  /** Display code like "T-1", "T-2" */
  table_code: string

  /** ID of current group or null if ungrouped */
  current_table_group_id: string | null
}

/**
 * Table Group - From backend API
 * 
 * Represents a group of tables that are combined
 * for a single dining session.
 */
export interface TableGroup {
  /** UUID of the group */
  id: string

  /** Current state: open, bill_requested, paid, closed */
  state: string

  /** Array of table IDs in this group */
  physical_table_ids: string[]

  /** ISO timestamp when group was opened */
  opened_at: string

  /** ISO timestamp when group was closed (null if open) */
  closed_at: string | null
}

// ==========================================
// Frontend UI Types
// ==========================================

/**
 * Table - Frontend UI Type
 *
 * Used for displaying tables in the UI.
 * Derived from PhysicalTable with computed fields.
 */
export interface Table {
  /** Table ID */
  id: string

  /** Table number (extracted from table_code) */
  number: number

  /** Original table code from backend (e.g., "T1", "Table3") */
  tableCode?: string

  /** Current status */
  status: TableStatus

  /** Physical area location */
  area: TableArea

  /** Group ID if table is in a group */
  tableGroupId?: string

  /** Alias for tableGroupId (used by some views) */
  groupId?: string

  /** Order items for this table (used by some admin views) */
  orderItems?: any[]
}

/**
 * TableGroupUI - Frontend UI Type
 * 
 * Enhanced table group with display properties.
 * Derived from backend TableGroup.
 */
export interface TableGroupUI {
  /** Group ID */
  id: string

  /** Display name for the group */
  name: string

  /** Array of table IDs */
  tableIds: string[]

  /** Current billing status */
  billingStatus: BillingStatus

  /** Whether waiter workflow is overridden */
  waiterWorkflowOverride?: boolean

  /** When the group was created */
  createdAt: Date
}

// ==========================================
// Menu Types
// ==========================================

/**
 * Menu Item
 * 
 * Represents a food or beverage item
 * available on the menu.
 */
export interface MenuItem {
  /** Item ID */
  id: string

  /** Item name */
  name: string

  /** Price in local currency */
  price: number

  /** Category for grouping (main, dessert, beverage) */
  category: string

  /** Optional image URL */
  image?: string

  /** Whether item is currently available */
  available: boolean

  /** Whether item is today's special */
  isDailySpecial?: boolean
}

// ==========================================
// Order Types
// ==========================================

/**
 * Order Item
 * 
 * Represents a single line item in an order.
 */
export interface OrderItem {
  /** Order item ID */
  id: string

  /** Reference to menu item */
  menuItemId: string

  /** Which table placed the order */
  tableId: string

  /** Which group the table belongs to */
  tableGroupId?: string

  /** Quantity ordered */
  quantity: number

  /** Special instructions */
  notes?: string

  /** Current status in workflow */
  status: OrderItemStatus

  /** Whether kitchen has printed this */
  kitchenPrinted: boolean

  /** Whether food has been served */
  served: boolean

  /** Whether item was removed/voided */
  removed: boolean

  /** Optional price override */
  priceOverride?: number

  /** Enriched menu item data (computed) */
  menuItem?: MenuItem
}

/**
 * Order
 * 
 * Represents a complete order for a table.
 */
export interface Order {
  /** Order ID */
  id: string

  /** Table that placed the order */
  tableId: string

  /** Table group the table belongs to */
  tableGroupId: string

  /** Array of order items */
  items: OrderItem[]

  /** When the order was placed */
  createdAt: string

  /** Whether order has been confirmed */
  confirmed: boolean

  /** Idempotency key for duplicate prevention */
  idempotencyKey?: string
}

/**
 * Order confirmation request
 */
export interface OrderConfirmRequest {
  /** Idempotency key to prevent duplicates */
  idempotencyKey: string

  /** Items to add to order */
  items: Array<{
    menuItemId: string
    quantity: number
    notes?: string
  }>
}

/**
 * Order confirmation response
 */
export interface OrderConfirmResponse {
  /** Created order ID */
  orderId: string

  /** Table group ID */
  tableGroupId: string

  /** IDs of created order items */
  orderItemIds: string[]
}

// ==========================================
// Session & Auth Types
// ==========================================

/**
 * Actor Session
 * 
 * Represents a logged-in user session.
 */
export interface ActorSession {
  /** Session ID */
  id: string

  /** Actor type (waiter or admin) */
  actorType: UserRole

  /** Actor ID (waiter ID or admin ID) */
  actorId: string

  /** Actor display name */
  actorName: string

  /** When session started */
  startedAt: string

  /** JWT token for authenticated requests */
  token?: string
}

/**
 * Session creation request
 */
export interface SessionCreateRequest {
  /** Actor type */
  actorType: UserRole

  /** Username for login */
  username: string

  /** PIN/password for login */
  pin: string
}

// ==========================================
// Waiter Types
// ==========================================

/**
 * Waiter
 * 
 * Represents a waiter/staff member.
 */
export interface Waiter {
  /** Waiter ID */
  id: string

  /** Waiter name */
  name: string

  /** Whether waiter is currently active */
  active: boolean

  /** When waiter was created */
  createdAt?: string
}

/**
 * Waiter creation request
 */
export interface WaiterCreateRequest {
  /** Waiter name */
  name: string
}

/**
 * Waiter update request
 */
export interface WaiterUpdateRequest {
  /** Waiter name */
  name?: string

  /** Active status */
  active?: boolean
}

// ==========================================
// Menu Item Types
// ==========================================

/**
 * Menu item creation request
 */
export interface MenuItemCreateRequest {
  /** Item name */
  name: string

  /** Item price */
  price: number

  /** Item category */
  category: string

  /** Whether item is available */
  available: boolean
}

/**
 * Menu item update request
 */
export interface MenuItemUpdateRequest {
  /** Item name */
  name?: string

  /** Item price */
  price?: number

  /** Item category */
  category?: string

  /** Available status */
  available?: boolean
}

// ==========================================
// Bill Types
// ==========================================

/**
 * Bill breakdown line item
 */
export interface BillLineItem {
  /** Order item ID */
  orderItemId: string

  /** Menu item name */
  itemName: string

  /** Quantity */
  quantity: number

  /** Unit price */
  unitPrice: number

  /** Line total */
  lineTotal: number
}

/**
 * Bill breakdown
 */
export interface BillBreakdown {
  /** Table group ID */
  tableGroupId: string

  /** Array of line items */
  items: BillLineItem[]

  /** Subtotal */
  subtotal: number

  /** Tax amount */
  tax: number

  /** Service charge */
  serviceCharge: number

  /** Adjustments/discounts */
  adjustments: BillAdjustment[]

  /** Total amount */
  total: number
}

/**
 * Bill adjustment (discount, surcharge, etc.)
 */
export interface BillAdjustment {
  /** Adjustment ID */
  id: string

  /** Adjustment amount (positive for surcharge, negative for discount) */
  amount: number

  /** Description of adjustment */
  description: string

  /** Reason category */
  reason: string

  /** Who created the adjustment */
  createdBy: string

  /** Reference to order item (optional) */
  referenceOrderItemId?: string

  /** Adjustment category */
  category: string

  /** When created */
  createdAt: string
}

/**
 * Bill adjustment creation request
 */
export interface BillAdjustmentCreateRequest {
  /** Adjustment amount */
  amount: number

  /** Description */
  description: string

  /** Reason */
  reason: string

  /** Who is creating it */
  createdBy: string

  /** Reference order item ID */
  referenceOrderItemId?: string

  /** Category */
  category: string
}
