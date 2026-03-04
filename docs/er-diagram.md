# ER Diagram (Phase 1)

## Core Tables
- PhysicalTable
- TableGroup
- TableGroupPhysicalTable (join)
- Order
- OrderItem
- BillAdjustment
- BillPrintEvent

## Relationships
```
TableGroup 1 ────< Order 1 ────< OrderItem
     |
     |
     └────< TableGroupPhysicalTable >──── PhysicalTable

TableGroup 1 ────< BillAdjustment
OrderItem  0..1 ────< BillAdjustment (optional reference)

TableGroup 1 ────< BillPrintEvent
OrderItem  1 ────< OrderItemPrintEvent
```

## Notes
- OrderItem stores menu name and price snapshots.
- OrderItem status: ACTIVE or VOIDED.
- BillAdjustments do not affect OrderItem lifecycle or serving state.
- OrderItemPrintEvent includes print_type (ORIGINAL or DUPLICATE).
- PhysicalTable state is derived from TableGroup association.
