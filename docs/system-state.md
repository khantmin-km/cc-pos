# System State

## Core Principles
- State reflects system intent, not physical reality
- Manual operations are expected
- Printing is a side effect, never a source of truth
- OrderItems are the unit of operation
- Admin authority can override workflow rigidity
- Nothing is implicitly auto-corrected

## Entity Model
- PhysicalTable
- TableGroup
- Order
- OrderItem
- BillAdjustment

## PhysicalTable State (Derived)
- FREE: no TableGroup association
- OCCUPIED: associated with a TableGroup (any state)

## TableGroup States
- OPEN
- BILL_REQUESTED
- PAID
- CLOSED

### Transitions
- OPEN -> BILL_REQUESTED (request bill)
- BILL_REQUESTED -> PAID (admin marks payment)
- PAID -> CLOSED (admin closes)
- PAID -> OPEN (admin reopen for dispute)

## Order State
- CONFIRMED (only state; created at confirm)

## OrderItem States
- ACTIVE
- VOIDED

## Serving State (OrderItem)
- PENDING
- SERVED

## Rules
- Orders are created only at confirm time
- OrderItems are created only from CONFIRMED Orders
- OrderItems are immutable in economic attributes
- OrderItems may be VOIDED only while TableGroup is OPEN
- Serving state changes are allowed only while TableGroup is OPEN
- Serving ignores OrderItem PhysicalTable attribution; it follows current TableGroup seating
- Printing does not change OrderItem lifecycle or serving state

## BILL_REQUESTED Behavior
- Order confirmation is blocked
- OrderItem mutation is blocked
- BillAdjustments are allowed
- Bill totals recompute after BillAdjustments

## PAID / CLOSED
- PAID: no Order or BillAdjustment mutation
- CLOSED: fully immutable and archived
