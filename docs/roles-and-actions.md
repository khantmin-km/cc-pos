# Roles and Actions (Phase 1)

## Waiter
### Visibility
- Can view all PhysicalTables and their status
- Can view open TableGroups via PhysicalTables
- Can view Orders and OrderItems (informational)
- Can view serving state (read-only)
- Can see waiter attribution on OrderItems

### Allowed Actions
- Start service on a FREE PhysicalTable
- Confirm Orders via PhysicalTable when TableGroup is OPEN
- Attach a FREE PhysicalTable to an OPEN TableGroup
- Switch an OPEN TableGroup from one PhysicalTable to another FREE PhysicalTable
- Merge two OPEN TableGroups
- Request bill

### Restricted Actions
- Cannot split TableGroups
- Cannot close or reopen TableGroups
- Cannot mark payment as PAID
- Cannot void OrderItems
- Cannot print/reprint OrderItems
- Cannot change serving state

## Admin
### Table & TableGroup Control
- Create, split, merge, and dissolve TableGroups
- Attach/detach PhysicalTables to TableGroups
- Reopen PAID TableGroups to OPEN for dispute
- Close TableGroups after payment

### Order Oversight
- Void OrderItems while TableGroup is OPEN
- Confirm Orders (same rules as waiter)
- Override table operations as needed

### Serving & Kitchen Coordination
- Reprint OrderItems
- Mark OrderItems as SERVED

### Billing & Payment
- Request bill
- Apply BillAdjustments in BILL_REQUESTED
- Mark payment as PAID

### Menu Management
- Create, update, retire, and manage availability of MenuItems

## Non-Interactive Actors
- Kitchen: receives printed tickets only
- Customer: no system interaction
