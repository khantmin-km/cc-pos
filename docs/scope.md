# Scope (Phase 1)

## 1. Restaurant & Deployment Scope
- Single restaurant, single branch only
- Single physical location
- No multi-branch or franchise support
- No cloud dependency
- System operates on local network only
- One Windows laptop acts as the server and admin workstation

## 2. Actors in Scope
- Admin: system operator and single point of control
- Waiter: takes orders using shared access via personal devices
- Kitchen: receives printed tickets only (no system interaction)
- Customer: no direct interaction with the system

## 3. Ordering Model
### Core Entities
- PhysicalTable: real-world table with a fixed identifier
- TableGroup: logical container for ordering and billing
- Orders and bills belong to TableGroups, never directly to PhysicalTables
- A TableGroup may contain one or more PhysicalTables
- PhysicalTables may move between TableGroups during service

### Order Characteristics
- Orders are created only at confirmation time (no server-side drafts)
- Orders are immutable after confirmation
- OrderItems are the smallest operational unit
- OrderItems have immutable economic attributes
- OrderItem lifecycle state can change (ACTIVE -> VOIDED) only while OPEN

## 4. Item Lifecycle (High-Level)
- All food is represented as OrderItems
- Quantity changes are implemented as VOID + ADD
- VOIDED OrderItems are hidden operationally but kept historically
- Serving state is tracked per OrderItem
- Printing is a side effect; it does not change OrderItem lifecycle state

## 5. Kitchen Communication
- Kitchen receives orders via printed tickets only
- Printed tickets contain item information only (no table, pricing, or billing data)
- Printing is asynchronous and treated as a logical event
- Reprints require explicit admin action and are marked as duplicates

## 6. Billing & Payment
- Single bill per TableGroup
- Billing is based on ACTIVE OrderItems and BillAdjustments
- Bill totals are computed dynamically, not frozen
- Payment methods supported: PromptPay (external) and Cash
- Payment confirmation is manual

### BILL_REQUESTED Rules
- Order confirmation is blocked
- OrderItem mutation is blocked
- BillAdjustments are allowed
- Bill recomputes after BillAdjustments

## 7. Order Closure & Corrections
- TableGroups can be closed only after payment is marked
- CLOSED is terminal and immutable
- Closed records are stored indefinitely
- Corrections after BILL_REQUESTED are financial only (BillAdjustments)

## 8. Waiter Identity (Phase 1)
- Soft identity only (selection-based)
- No authentication, passwords, or access control
- Identity is used for attribution only, not enforcement

## 9. Data & Reporting
- All TableGroups and OrderItems (open and closed) are persisted
- No analytics, dashboards, summaries, or KPIs in Phase 1
- No exports or reporting tools included

## 10. Explicit Exclusions
- No online payment gateway integration
- No customer self-ordering UI
- No inventory or stock tracking
- No ingredient management
- No staff scheduling or shift tracking
- No user authentication or permissions
- No offline sync or multi-device conflict resolution
- No cloud hosting or remote access
