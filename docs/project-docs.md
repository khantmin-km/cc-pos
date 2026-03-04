# Scope 


#### 1. Restaurant & Deployment Scope

- Single restaurant, single branch only
- Single physical location
- No multi-branch or franchise support
- No cloud dependency
- System operates on local network only
- One Windows laptop acts as the server and admin workstation

#### 2. Actors in Scope

- **Admin**: system operator and single point of control
- **Waiter**: takes orders using shared access via personal devices
- **Kitchen**: receives printed tickets only (no system interaction)
- **Customer**: no direct interaction with the system

#### 3. Ordering Model

- Orders are created per table
- Multiple waiters may add items to the same table order
- Customers may add items at any time before billing
- Orders are item-based, not atomic
- Item-level serving is enforced

#### 4. Item Lifecycle (High-Level)

- Items exist independently within an order
- Item states are tracked at a minimum operational level
- Items are printed to kitchen individually or in batches
- Kitchen has no feedback channel into the system
- Admin manually updates item serving status

#### 5. Kitchen Communication

- Kitchen receives orders via printed tickets only
- Printed tickets contain item information only (no table or pricing)
- Printing an item marks it as sent to kitchen
- No kitchen-side confirmation, tracking, or delay management

#### 6. Billing & Payment

- Single bill per table
- Billing is based on ordered items, not serving completion
- Bill is generated on demand
- Payment methods supported:
    - PromptPay (QR-based, external)
    - Cash
- Payment confirmation is manual
- Payment slips may be captured manually outside the system

#### 7. Order Closure & Corrections

- Orders can be closed only after payment
- Closed orders are immutable
- Closed orders are stored indefinitely
- Admin can view closed orders for lookup and dispute handling
- Corrections are handled via adjustment records
- Original order data is never modified after closure

#### 8. Waiter Identity (Phase-1)

- Waiters use soft identity (selection-based)
- No authentication, passwords, or access control
- Waiter attribution is recorded for:
    - Item creation
    - Item cancellation (before kitchen)
- Identity is used for attribution only, not enforcement

#### 9. Data & Reporting

- All orders (open and closed) are persisted
- No analytics, dashboards, summaries, or KPIs in Phase-1
- No exports or reporting tools included

#### 10. Explicit Exclusions

- No online payment gateway integration
- No customer self-ordering UI
- No inventory or stock tracking
- No ingredient management
- No staff scheduling or shift tracking
- No user authentication or permissions
- No offline sync or multi-device conflict resolution
- No cloud hosting or remote access

---


# Scope (Phase 1)

## 1. Restaurant & Deployment Scope

- Single restaurant, single branch only
- Single physical location
- No multi-branch or franchise support
- No cloud dependency
- System operates on local network only
- One Windows laptop acts as the server and admin workstation

---

## 2. Actors in Scope

- **Admin**: system operator and single point of control
- **Waiter**: takes orders using shared access via personal devices
- **Kitchen**: receives printed tickets only (no system interaction)
- **Customer**: no direct interaction with the system

---

## 3. Ordering Model

### Core Entities

- A **Physical Table** is a real-world object with a fixed identifier (table number)
- A **Table Group** is the logical container for ordering and billing
- **Orders and bills always belong to Table Groups**, never directly to Physical Tables
- A Table Group may contain one or more Physical Tables
- Physical Tables may move between Table Groups during service

### Order Characteristics

- Orders are created within a Table Group
- Multiple waiters may add orders to the same Table Group
- Customers may add items at any time before billing
- Orders are item-based, not atomic
- Orders are **immutable after confirmation**
- Item-level serving is enforced

---

## 4. Item Lifecycle (High-Level)

- All food is represented as **OrderItems**
- OrderItems are the smallest operational unit in the system
- OrderItems exist independently within an order
- OrderItems may be added or removed only via adjustments
- Quantity changes are implemented as **REMOVE + ADD**
- Removed OrderItems are hidden operationally but kept historically
- All operational state (serving, billing inclusion) is evaluated at the **OrderItem level**

---

## 5. Kitchen Communication

- Kitchen receives orders via printed tickets only
- Printed tickets contain item information only (no table, pricing, or billing data)
- Each OrderItem can be printed **once**
- Printing an OrderItem marks it as sent to kitchen
- Reprints require admin override and produce a clearly marked **duplicate ticket**
- Kitchen has no feedback channel into the system
- No kitchen-side confirmation, tracking, or delay management

---

## 6. Billing & Payment

- Single bill per Table Group
- Billing is based on OrderItems, not serving completion
- Bill is generated on demand
- Bill totals are **computed dynamically**, not frozen
- Payment methods supported:
  - PromptPay (QR-based, external)
  - Cash
- Payment confirmation is manual
- Payment slips may be captured manually outside the system

### BILL_REQUESTED State Rules

At `BILL_REQUESTED`:

- Waiters **cannot add new orders**
- Admin **can add or remove OrderItems**
- Bill total remains dynamic
- Serving state continues unaffected

---

## 7. Order Closure & Corrections

- Table Groups can be closed only after payment is marked
- Closed Table Groups are immutable
- Closed orders are stored indefinitely
- Admin can view closed orders for lookup and dispute handling
- Corrections are handled via adjustment records
- Original OrderItems are never modified after closure

---

## 8. Waiter Identity (Phase 1)

- Waiters use soft identity (selection-based)
- No authentication, passwords, or access control
- Identity is used for attribution only, not enforcement
- Waiter attribution is recorded for:
  - OrderItem creation
  - OrderItem removal (before kitchen)

### Identity Correction Policy

- Incorrect waiter selection **cannot be corrected in-system**
- No retroactive reassignment is supported
- Errors are handled manually outside the system

---

## 9. Data & Reporting

- All Table Groups and OrderItems (open and closed) are persisted
- No analytics, dashboards, summaries, or KPIs in Phase 1
- No exports or reporting tools included

---

## 10. Explicit Exclusions

- No online payment gateway integration
- No customer self-ordering UI
- No inventory or stock tracking
- No ingredient management
- No staff scheduling or shift tracking
- No user authentication or permissions
- No offline sync or multi-device conflict resolution
- No cloud hosting or remote access


---


# Roles and Actions

# Waiter

## Visibility

- Can view all Physical Tables and their current status
- Can view open Table Groups via tables
- Can view all confirmed orders under an open Table Group
- Can view OrderItems and their serving state (read-only, informational)
- Can view item prices and order timestamps
- Can see soft waiter attribution on OrderItems

## Order Handling

- Can create a new order for a Table Group
- Can edit an order only before confirmation
- Can cancel an order only before confirmation
- Can add additional confirmed orders to an existing open Table Group at any time (until BILL_REQUESTED)

## Table Operations

- Can request table change
- Can request table merge
- Can continue adding orders to the Table Group while request is pending
- Cannot execute table changes or merges without admin approval

## Restrictions

- Cannot edit confirmed orders
- Cannot adjust or delete OrderItems post-confirmation
- Cannot modify menus, prices, taxes, or discounts
- Cannot see bill totals, tax, discount, or payment status
- **Cannot mark OrderItems as served
- Cannot print kitchen tickets
- Cannot close Table Groups or bills
- Cannot access closed Table Groups or historical orders

---

# Admin

## 1. Table & Table Group Control

### Admin CAN

- Create, split, merge, and dissolve Table Groups at any time
- Initiate table changes or merges without waiter request
- Move Physical Tables between Table Groups
- Resolve Table Groups automatically upon closure
- Correct table assignment mistakes directly

### Admin CANNOT

- Close a Table Group without marking payment

### Design Rules

- Physical Tables and Table Groups are distinct concepts
- Orders and bills always belong to Table Groups
- Table Groups are system-managed, not manually finalized
- Admin actions override waiter workflow

---

## 2. Order Oversight & Adjustments

### Admin CAN

- Add OrderItems to existing Table Groups
- Remove OrderItems from active orders
- Change quantities via REMOVE + ADD
- Correct pricing or item entry mistakes
- Perform adjustments both before and after BILL_REQUESTED

### Admin CANNOT

- Replace entire orders wholesale
- Modify historical OrderItems

### Design Rules

- OrderItems are the smallest mutable unit
- Adjustments only affect OrderItems
- Removed OrderItems are excluded from operations but retained historically

---

## 3. Item Serving & Kitchen Coordination

### Admin CAN

- Print OrderItems to kitchen
- View serving state of each OrderItem
- Mark OrderItems as served
- Override serving state if operationally required

### Admin CANNOT

- Serve removed OrderItems
- Mark serving completion at order or table level

### Design Rules

- Serving state applies only to active OrderItems
- Printing an OrderItem is a one-time action unless overridden

---

## 4. Billing & Payment Handling

### Admin CAN

- Request bill at any time
- Print bill multiple times
- Adjust OrderItems after BILL_REQUESTED
- Mark payment as completed manually
- Close Table Group after payment

### Admin CANNOT

- Freeze bill totals
- Close Table Groups without payment

### Design Rules

- BILL_REQUESTED blocks waiter ordering only
- Bill amount remains dynamic until closure
- Printing does not lock or finalize billing

---

## 5. Menu & Daily Operations

### Admin CAN

- Create, edit, and remove menu items
- Edit prices during service hours
- Add and remove daily specials
- Mark items as UNAVAILABLE

### Admin CANNOT

- Configure modifiers, variants, sizes, or add-ons

### Design Rules

- Daily specials are treated as standard menu items
- Waiters can order specials but do not manage them
- UNAVAILABLE is the only availability state

---

## 6. System & Access Control (Minimal)

### Admin CAN

- Access all operational screens

### Admin CANNOT

- Manage roles, permissions, or users

### Design Rules

- Single trusted admin model
- No audit logs or action history

---

## Phase 1 Guarantees

- Orders are immutable after confirmation
- OrderItems are the only operational unit
- Admin is the sole authority
- Manual workflows are acceptable
- No design decision blocks future expansion


# System State




This document defines **all system states**, their meanings, allowed transitions, and governing rules.

It is intentionally explicit to prevent misinterpretation after time has passed.

---

## **1. Core Design Principles (State Layer)**

These principles apply globally and override convenience decisions.

- **State reflects system intent, not physical reality**
- **Manual operations are acceptable and expected**
- **Printing is a side effect, never a source of truth**
- **All operational logic is evaluated at OrderItem level**
- **Admin authority overrides workflow rigidity**
- **Nothing is implicitly auto-corrected**

---

## **2. Entity Model (State-Carrying Objects)**

| **Entity**     | **Description**                            |
| -------------- | ------------------------------------------ |
| Physical Table | Real-world table, numbered                 |
| Table Group    | Logical container for ordering and billing |
| Order          | Immutable record of confirmed intent       |
| OrderItem      | Smallest operational unit                  |
| Bill           | Dynamic computation over OrderItems        |

---

## **3. Physical Table States**

Physical tables reflect **real-world seating**, not billing.

### **States**

- **IDLE**
    - Table is free
    - Not associated with any Table Group
- **OCCUPIED**
    - Table is assigned to a Table Group
    - Active service ongoing
- **MERGED**
    - Table is logically merged into a Table Group with others
    - Not independently billable

### **Rules**

- Physical tables **can move between Table Groups**
- Table state is **derived**, not manually finalized
- Tables do **not** carry billing state

---

## **4. Table Group States**

Table Groups are the **billing and ordering container**.

### **States**

#### **1.** 

#### **OPEN**

- Table Group is active
- Orders can be created
- Adjustments allowed
- Serving continues

#### **2.** 

#### **BILL_REQUESTED**

- Bill has been requested (by waiter or admin)
- **New orders are blocked**
- Adjustments are still allowed
- Bill remains dynamic
- Serving state continues unaffected

#### **3.** 

#### **PAID**

- Payment has been confirmed manually by admin
- Bill amount is informational only
- Corrections may still be required

#### **4.** 

#### **CLOSED**

- Table Group is finalized
- All data becomes immutable
- Table Group is archived

### **Transition Rules**

| **From**       | **To**         | **Trigger**                                    |
| -------------- | -------------- | ---------------------------------------------- |
| OPEN           | BILL_REQUESTED | Waiter or Admin                                |
| BILL_REQUESTED | PAID           | Admin marks payment confirmed                  |
| PAID           | CLOSED         | Admin closes Table Group                       |
| PAID           | OPEN           | Admin reopens due to dispute (manual override) |

### **Design Notes**

- **PAID ≠ CLOSED**
- PAID indicates **money exchange acknowledged**
- CLOSED indicates **operational finality**
- Separation allows dispute handling and overpayment correction

---

## **5. Order States**

Orders are **immutable after confirmation**.

### **States**

#### **DRAFT**

- Created by waiter
- Editable
- Cancellable

#### **CONFIRMED**

- Order intent is locked
- Items become operational OrderItems
- Cannot be edited or deleted

### **Rules**

- Orders belong to **Table Groups**, never tables
- Adjustments never mutate Orders
- Orders are historical records only

---

## **6. OrderItem States (Operational Core)**

OrderItems are the **smallest unit of truth**.

### **Lifecycle States**

#### **1.** 

#### **ACTIVE**

- Item is valid
- Included in bill
- Eligible for serving and printing

#### **2.** 

#### **VOIDED**

- Item has been cancelled via adjustment
- Hidden operationally
- Retained historically

> VOIDED items:

- > Do not print
- > Do not serve
- > Do not contribute to bill
- > Are never deleted

---

## **7. OrderItem Serving State**

Serving state is **orthogonal** to lifecycle.

### **Serving States**

- **PENDING**
- **SERVED**

### **Rules**

- Serving state only applies to ACTIVE OrderItems
- Removed items cannot be served
- Admin manually updates serving state
- No partial serving
- No kitchen acknowledgment

---

## **8. Printing State (OrderItem-Level)**

Printing is treated as a **logical event**, not a physical guarantee.

### **Print Attributes**

- printed_at (nullable)
- print_count (integer)

### **Rules**

- OrderItem becomes printable when ACTIVE
- Printing marks printed_at
- Each OrderItem is printable **once by default**
- Reprints require admin override
- Reprints produce a “DUPLICATE” ticket
- Printing success is **not verified**

---

## **9. Adjustment Rules (Critical)**

Adjustments operate only on OrderItems.

### **Allowed Actions**

- ADD OrderItem
- REMOVE OrderItem
- Quantity change = REMOVE + ADD

### **Forbidden Actions**

- Editing confirmed Orders
- Replacing Orders wholesale
- Editing historical OrderItems

### **Consequences**

- Adjustments increase OrderItem count
- Backend aggregation is required
- Serving and printing naturally adapt

---

## **10. Billing Computation Rules**

- Bill is **computed dynamically**
- Based only on ACTIVE OrderItems
- Serving state does not affect billing
- Printing does not freeze billing
- Adjustments after BILL_REQUESTED are allowed

---

## **11. Payment & Dispute Handling**

### **Payment Flow**

1. Bill requested
2. Bill printed
3. Payment handled externally
4. Admin marks PAID
5. Admin closes Table Group

### **Dispute Handling**

- Admin may reopen from PAID to OPEN
- Adjustments may be applied
- New bill printed
- Final close only after resolution

---

## **12. Explicit Non-Goals (Phase 1)**

- Printer delivery confirmation
- Inventory linkage
- Payment automation
- Refund workflows
- Audit trails
- Analytics
- Role enforcement

---

## **13. Non-Negotiable Invariants**

- Orders are immutable
- OrderItems are the unit of operation
- Printing never defines truth
- Admin is trusted
- Manual discipline is expected

---

This document is the **single source of truth for system states** in Phase 1.

Any future feature must **conform to these rules or explicitly revise them**.


---


# API Contracts



# API Contracts v0.1 — Core Dining System

> Scope: This document defines the authoritative HTTP API surface for Phase 1.
> It is the sole reference for frontend–backend integration.
> Any behavior not explicitly described here is undefined.

---

## 1. Enumerations

### TableGroupState

```
OPEN
BILL_REQUESTED
PAID
CLOSED
```

### OrderState

```
CREATED
CONFIRMED
```

### OrderItemStatus

```
ACTIVE
VOIDED
```

---

## 2. Physical Tables

### GET /tables

List all physical tables with their current assignment.

**Response (minimal):**

- tableId
- tableName
- currentTableGroupId (nullable)

**Notes:**

- Physical table state is derived from TableGroup assignment
- No table state transitions exist at this level

---

## 3. Table Groups

### POST /table-groups

Create a new TableGroup.

**Preconditions:**

- All provided physicalTableIds are unassigned

**Request:**

- physicalTableIds[]

**Response:**

- tableGroupId
- state = OPEN

---

### GET /table-groups/open

List all non-closed TableGroups.

**Response:**

- tableGroupId
- state
- physicalTableIds[]
- openedAt

---

### GET /table-groups/{tableGroupId}

Fetch full TableGroup state.

**Response (minimal):**

- tableGroupId
- state
- physicalTableIds[]
- openedAt

---

### POST /table-groups/{tableGroupId}/request-bill

Request billing for a TableGroup.

**Preconditions:**

- TableGroup state = OPEN

**Effects:**

- TableGroup state → BILL_REQUESTED

---

### POST /table-groups/{tableGroupId}/mark-paid

Mark a TableGroup as paid.

**Preconditions:**

- TableGroup state = BILL_REQUESTED

**Effects:**

- TableGroup state → PAID

---

### POST /table-groups/{tableGroupId}/close

Close a TableGroup.

**Preconditions:**

- TableGroup state = PAID

**Effects:**

- TableGroup state → CLOSED
- All physical tables are released

---

## 4. Table Assignment (Admin)

### POST /table-groups/{tableGroupId}/tables/add

Add a PhysicalTable to a TableGroup.

**Preconditions:**

- TableGroup state = OPEN
- PhysicalTable is unassigned

**Request:**

- physicalTableId

---

### POST /table-groups/{tableGroupId}/tables/remove

Remove a PhysicalTable from a TableGroup.

**Preconditions:**

- TableGroup state = OPEN
- TableGroup has more than one PhysicalTable

**Request:**

- physicalTableId

---

### POST /table-groups/merge

Merge multiple TableGroups into one.

**Preconditions:**

- All TableGroups state = OPEN

**Request:**

- sourceTableGroupIds[]
- targetTableGroupId

**Effects:**

- Target TableGroup remains OPEN
- Source TableGroups become CLOSED (merged)

---

### POST /table-groups/{tableGroupId}/split

Split a TableGroup into two.

**Preconditions:**

- TableGroup state = OPEN

**Request:**

- physicalTableIdsForNewGroup[]

**Effects:**

- New TableGroup created (OPEN)
- Orders remain with original TableGroup

---

## 5. Orders

### POST /table-groups/{tableGroupId}/orders

Create a draft Order.

**Preconditions:**

- TableGroup state = OPEN

**Response:**

- orderId
- state = CREATED

---

### POST /orders/{orderId}/confirm

Confirm an Order.

**Preconditions:**

- Order state = CREATED

**Effects:**

- Order state → CONFIRMED
- Order becomes immutable
- OrderItems become operationally active

---

### GET /table-groups/{tableGroupId}/orders

List all Orders for a TableGroup.

**Response:**

- orderId
- state
- createdAt

---

## 6. Order Items

### POST /orders/{orderId}/order-items

Add an OrderItem.

**Preconditions:**

- Order state = CONFIRMED
- TableGroup state ≠ CLOSED

**Effects:**

- New OrderItem created with status = ACTIVE

---

### POST /order-items/{orderItemId}/remove

Remove an OrderItem.

**Preconditions:**

- OrderItem status = ACTIVE
- TableGroup state ≠ CLOSED

**Effects:**

- OrderItem status → VOIDED

---

### POST /order-items/{orderItemId}/serving

Update serving state.

**Preconditions:**

- OrderItem status = ACTIVE

**Notes:**

- Serving state does not affect billing

---

### POST /order-items/{orderItemId}/printed

Mark an OrderItem as printed.

**Preconditions:**

- OrderItem status = ACTIVE

**Notes:**

- Printing has no state impact
- Reprints require override logic

---

### GET /table-groups/{tableGroupId}/order-items

List all OrderItems for a TableGroup.

**Response:**

- orderItemId
- status
- price
- servingState

---

## 7. Billing

### GET /table-groups/{tableGroupId}/bill

Compute the current bill.

**Preconditions:**

- TableGroup state ∈ { OPEN, BILL_REQUESTED, PAID }

**Rules:**

- Includes only ACTIVE OrderItems
- Bill is computed dynamically
- Result may change until TableGroup is CLOSED

**Response (conceptual):**

- lineItems[]
- subtotal
- tax
- total

---

### POST /table-groups/{tableGroupId}/print-bill

Generate printable bill output.

**Preconditions:**

- TableGroup state ∈ { BILL_REQUESTED, PAID }

**Notes:**

- Printing does not freeze billing
- Printed output may become outdated

---

## 8. Global Constraints

- No API allows mutation after TableGroup is CLOSED
- No API stores billing totals
- No API validates payments
- No API manages printer hardware
- All state transition validation is server-side

---



# ER Diagram



# ER Diagram Draft

> Purpose: Define the **authoritative data model** for Phase 1 based on locked API contracts and state definitions.
> This ER model prioritizes **correctness, clarity, and future extensibility** over optimization.

---

## **1. Design Principles (ER-Level)**

- Every table represents a **domain concept**, not a UI artifact
- Relationships encode **ownership**, not convenience
- States are stored explicitly where they are authoritative
- Derived states are **not stored** unless necessary
- No table exists without a clear lifecycle owner

---

## **2. Core Tables Overview**

```
PhysicalTable
TableGroup
TableGroupPhysicalTable (join)
Order
OrderItem
```

---

## **3. Table Definitions**

### **3.1 PhysicalTable**

Represents a real, numbered table in the restaurant.

```
PhysicalTable
-------------
id (PK)
code / number
is_active
created_at
```

Notes:

- No state column (state is derived)
- No billing or order linkage
- is_active allows soft retirement of tables

---

### **3.2 TableGroup**

Represents a dining session and the **billing container**.

```
TableGroup
----------
id (PK)
state (OPEN | BILL_REQUESTED | PAID | CLOSED)
opened_at
closed_at (nullable)
created_at
```

Notes:

- State is authoritative
- closed_at populated only on CLOSED
- No direct reference to PhysicalTable (via join table)

---

### **3.3 TableGroupPhysicalTable (Join Table)**

Maps PhysicalTables to TableGroups.

```
TableGroupPhysicalTable
----------------------
id (PK)
table_group_id (FK → TableGroup.id)
physical_table_id (FK → PhysicalTable.id)
created_at
```

Cardinality:

- One TableGroup → many PhysicalTables
- One PhysicalTable → zero or one active TableGroup (enforced at application level)

Notes:

- No historical tracking in Phase 1
- Rows removed when table is detached

---

### **3.4 Order**

Represents a confirmed submission by a waiter.

```
Order
-----
id (PK)
table_group_id (FK → TableGroup.id)
state (CREATED | CONFIRMED)
created_by
created_at
confirmed_at (nullable)
```

Notes:

- Immutable after CONFIRMED
- Always belongs to exactly one TableGroup

---

### **3.5 OrderItem**

Smallest operational and billable unit.

```
OrderItem
---------
id (PK)
order_id (FK → Order.id)
menu_item_id (nullable)
item_name_snapshot
unit_price_snapshot
quantity
status (ACTIVE | VOIDED)
served (boolean)
printed (boolean)
printed_at (nullable)
created_at
```

Notes:

- Price and name are snapshotted
- menu_item_id is optional (future-proofing)
- printed enforces one-print rule
- Removal is soft (status)

---

## **4. Relationships (Authoritative)**

```
TableGroup 1 ────< Order 1 ────< OrderItem
     |
     |
     └────< TableGroupPhysicalTable >──── PhysicalTable
```

Ownership rules:

- TableGroup owns Orders
- Order owns OrderItems
- PhysicalTables are assigned, not owned

---

## **5. Derived / Non-Stored Concepts**

These **must not** be stored as columns:

- PhysicalTable state (IDLE / OCCUPIED / MERGED)
- Bill totals
- Bill line items
- Payment method details
- Printer status

All are computed from authoritative data.

---

## **6. Explicit Phase-1 Omissions**

Intentionally not modeled yet:

- Payments table
- Refunds / credits
- Bill snapshots
- Audit logs
- Menu table (beyond snapshot fields)
- User / role tables

These may be added in later phases **without breaking this model**.

---

## **7. Validation Questions (For Discussion)**

- Do we need quantity on OrderItem or enforce 1-per-row?
- Should served be boolean or enum?
- Should printed be boolean or timestamp-only?
- Do we want to allow multiple prints with a counter later?

---

## **8. Stability Statement**

This ER model is suitable for:

- Phase 1 backend implementation
- Parallel frontend development
- Forward-compatible expansion

Breaking changes require:

- State model change, or
- Ownership rule change

Neither should happen casually.


---  


# Database Schema


## **1.** **physical_tables**

Represents real-world tables.

```
CREATE TABLE physical_tables (
    id              UUID PRIMARY KEY,
    table_code      VARCHAR(50) NOT NULL UNIQUE,
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);
```

### **Notes**

- No state column
- No availability flag
- Availability is derived from table_group_tables

This prevents **desynchronization bugs**.

---

## **2.** **table_groups**

Represents a dining session.

```
CREATE TABLE table_groups (
    id              UUID PRIMARY KEY,
    state           VARCHAR(20) NOT NULL,
    opened_at       TIMESTAMP NOT NULL DEFAULT now(),
    closed_at       TIMESTAMP NULL,

    CONSTRAINT table_group_state_check
        CHECK (state IN ('OPEN', 'BILL_REQUESTED', 'PAID', 'CLOSED'))
);
```

### **Critical rules**

- State is authoritative
- closed_at is nullable and only set when state = CLOSED
- No automatic transitions

---

## **3.** **table_group_tables** **(junction)**

Maps PhysicalTables to TableGroups.

```
CREATE TABLE table_group_tables (
    table_group_id  UUID NOT NULL,
    physical_table_id UUID NOT NULL,

    PRIMARY KEY (table_group_id, physical_table_id),

    CONSTRAINT fk_tgt_table_group
        FOREIGN KEY (table_group_id)
        REFERENCES table_groups(id),

    CONSTRAINT fk_tgt_physical_table
        FOREIGN KEY (physical_table_id)
        REFERENCES physical_tables(id)
);
```

### **Invariant (IMPORTANT)**

A PhysicalTable must not belong to more than one **non-closed** TableGroup.

This is enforced via **application logic in Phase 1**, not SQL (because it depends on TableGroup state).

Do **not** add a unique constraint here yet — it would block merges/splits incorrectly.

---

## **4.**  **orders**

Represents a confirmed waiter submission.

```
CREATE TABLE orders (
    id              UUID PRIMARY KEY,
    table_group_id  UUID NOT NULL,
    state           VARCHAR(20) NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    confirmed_at    TIMESTAMP NULL,

    CONSTRAINT fk_orders_table_group
        FOREIGN KEY (table_group_id)
        REFERENCES table_groups(id),

    CONSTRAINT order_state_check
        CHECK (state IN ('CREATED', 'CONFIRMED'))
);
```

### **Rules enforced by code**

- Orders can only be created when TableGroup = OPEN
- Once CONFIRMED, immutable
- Orders never move between TableGroups

---

## **5.**  **order_items**

This is the most important table.

```
CREATE TABLE order_items (
    id              UUID PRIMARY KEY,
    order_id        UUID NOT NULL,
    menu_item_id    UUID NOT NULL,
    price           DECIMAL(10,2) NOT NULL,
    state           VARCHAR(20) NOT NULL,
    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    removed_at      TIMESTAMP NULL,

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES orders(id),

    CONSTRAINT order_item_state_check
        CHECK (state IN ('ACTIVE', 'VOIDED'))
);
```

### **Locked design decisions**

- **No quantity**
- **One row = one unit**
- price is snapshotted (never trust menu price later)
- Removal is soft (state + timestamp)

This table alone handles:

- Adjustments
- Disputes
- Reprints
- Billing correctness

---

## **6.**  **order_item_serving**

Operational serving state.

```
CREATE TABLE order_item_serving (
    order_item_id  UUID PRIMARY KEY,
    served_at      TIMESTAMP NOT NULL,

    CONSTRAINT fk_serving_order_item
        FOREIGN KEY (order_item_id)
        REFERENCES order_items(id)
);
```

### **Why separate table?**

- Serving is optional
- Serving has operational meaning, not financial
- Keeps order_items clean and immutable in shape

---

## **7.**  **order_item_printing**

Tracks kitchen prints.

```
CREATE TABLE order_item_printing (
    order_item_id  UUID NOT NULL,
    printed_at     TIMESTAMP NOT NULL,
    printed_by     VARCHAR(50) NOT NULL,

    PRIMARY KEY (order_item_id, printed_at),

    CONSTRAINT fk_printing_order_item
        FOREIGN KEY (order_item_id)
        REFERENCES order_items(id)
);
```

### **Why multi-row?**

- Supports reprints
- Allows detection of duplicates
- No boolean flags

---

## **8. Indexes (Minimum Required)**

```
CREATE INDEX idx_orders_table_group
    ON orders(table_group_id);

CREATE INDEX idx_order_items_order
    ON order_items(order_id);

CREATE INDEX idx_order_items_state
    ON order_items(state);
```

---




