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

  /** Current status */
  status: TableStatus

  /** Physical area location (optional for Phase 1) */
  area?: TableArea

  /** Group ID if table is in a group */
  tableGroupId?: string
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

/**
 * Backend MenuItem - From backend API
 * Matches `GET /menu-items`
 */
export interface BackendMenuItem {
  id: string
  name: string
  price: string | number
  status: 'AVAILABLE' | 'UNAVAILABLE' | 'RETIRED'
  created_at: string
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
