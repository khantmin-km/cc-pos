# Audit Events

## Event Types
Recommended event types (enum enforced in DB and code):
- ORDER_ITEM_VOIDED
- ORDER_ITEM_SERVED
- ORDER_ITEM_REPRINTED
- ORDER_CONFIRMED
- BILL_REQUESTED
- BILL_MARKED_PAID
- TABLE_CLOSED
- BILL_ADJUSTMENT_CREATED
- TABLE_SWITCHED
- TABLE_MERGED
- TABLE_SPLIT
- TABLE_START_SERVICE

## Entity Types
Recommended entity types (enum enforced in DB and code):
- ORDER_ITEM
- ORDER
- TABLE_GROUP
- BILL_ADJUSTMENT
- PHYSICAL_TABLE

## Metadata Recommendations
Metadata is JSON and should include enough detail to understand the event without extra queries.

Examples:

### ORDER_ITEM_VOIDED
```json
{
  "menu_item_name": "Fried Rice",
  "unit_price": "7.50"
}
```

### BILL_ADJUSTMENT_CREATED
```json
{
  "amount": "-10.00",
  "description": "Complaint discount",
  "reason": "Cold food"
}
```

### TABLE_SWITCHED
```json
{
  "from_table_id": "uuid",
  "to_table_id": "uuid"
}
```

## Listing Behavior
The audit listing API returns the most recent events by default and supports filters on
event_type, entity_type, entity_id, actor_user_id, limit, and offset.
