# API Contracts (Phase 1)

## Enumerations
### TableGroupState
```
OPEN
BILL_REQUESTED
PAID
CLOSED
```

### OrderState
```
CONFIRMED
```

### OrderItemStatus
```
ACTIVE
VOIDED
```

### ServingState
```
PENDING
SERVED
```

## Physical Tables
### GET /tables
List all PhysicalTables with their current TableGroup association.

### GET /tables/overview
List all PhysicalTables with their current TableGroup association and state.

## Table Groups
### POST /tables/{physicalTableId}/start-service
Start service on a FREE PhysicalTable.

**Effects:**
- Create TableGroup in OPEN
- Associate PhysicalTable to TableGroup

### GET /table-groups/open
List all non-closed TableGroups.

### GET /table-groups/{tableGroupId}
Fetch TableGroup state.

### GET /table-groups/{tableGroupId}/order-items
List OrderItems for a TableGroup.

**Query params (optional):**
- served: `all|served|unserved` (default `all`)
- include_voided: `true|false` (default `true`)

### POST /table-groups/{tableGroupId}/request-bill
Transition OPEN -> BILL_REQUESTED.

### POST /table-groups/{tableGroupId}/mark-paid
Transition BILL_REQUESTED -> PAID.

### POST /table-groups/{tableGroupId}/close
Transition PAID -> CLOSED and release tables.

### POST /table-groups/{tableGroupId}/tables/add
Attach FREE PhysicalTable to OPEN TableGroup.

### POST /table-groups/{tableGroupId}/tables/remove
Detach PhysicalTable from OPEN TableGroup.

### POST /table-groups/{tableGroupId}/switch
Switch a TableGroup from one PhysicalTable to another FREE PhysicalTable.

**Request (conceptual):**
- from_table_id
- to_table_id

### POST /table-groups/merge
Merge two OPEN TableGroups into a target group.

### POST /table-groups/{tableGroupId}/split
Split an OPEN TableGroup only when it has zero OrderItems.

## Orders
### POST /tables/{physicalTableId}/orders/confirm
Confirm an Order (no server-side drafts).

**Request (conceptual):**
- items[] (menu_item_id, quantity)
- idempotency_key

**Effects:**
- Create Order in CONFIRMED state
- Create OrderItems
- Queue print jobs for created OrderItems

**Notes:**
- Original kitchen printing is an internal side effect; no public endpoint records ORIGINAL prints.

## Order Items
### POST /order-items/{orderItemId}/void
Void an OrderItem.

**Preconditions:**
- OrderItem status = ACTIVE
- TableGroup state = OPEN

### POST /order-items/{orderItemId}/serving
Update serving state.

**Preconditions:**
- OrderItem status = ACTIVE
- TableGroup state = OPEN

### POST /order-items/{orderItemId}/reprint
Reprint an OrderItem (admin only).

**Preconditions:**
- OrderItem status = ACTIVE

**Effects:**
- Attempt physical print
- On success, record print event with print_type = DUPLICATE

## Billing
### GET /table-groups/{tableGroupId}/bill
Compute the current bill.

**Notes:**
- Billing is always computed at TableGroup level.
- No individual or per-table bill split operation is supported.

### POST /table-groups/{tableGroupId}/print-bill
Generate printable bill output.

**Effects:**
- Record bill print event

### POST /table-groups/{tableGroupId}/bill-adjustments
Create a BillAdjustment.

**Preconditions:**
- TableGroup state = BILL_REQUESTED

**Request (conceptual):**
- amount (positive or negative)
- description
- reference_order_item_id (optional)
- reason (required if negative)
- category (optional: WAIVER | MANUAL)

## Menu Items
### GET /menu-items
List menu items.

### POST /menu-items
Create a menu item (admin only).

**Request (conceptual):**
- name
- price
- category

### PATCH /menu-items/{menuItemId}
Update name, price, status, or category (admin only).

### POST /menu-items/{menuItemId}/retire
Retire a menu item (admin only).

## Audit Events
### GET /audit-events
List audit events (admin only).
