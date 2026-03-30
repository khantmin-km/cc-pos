# API Reference (Current)

All endpoints require `Authorization: Bearer <session_token>` unless noted otherwise.

## Auth
### POST /auth/login
Request:
```json
{
  "username": "string",
  "pin": "string"
}
```
Response:
```json
{
  "token": "string",
  "user_id": "uuid",
  "username": "string",
  "role": "ADMIN|WAITER",
  "expires_at": "datetime"
}
```

## Physical Tables
### GET /tables
Response:
```json
[
  {
    "id": "uuid",
    "table_code": "string",
    "current_table_group_id": "uuid|null"
  }
]
```

### GET /tables/overview
Response:
```json
[
  {
    "id": "uuid",
    "table_code": "string",
    "current_table_group_id": "uuid|null",
    "current_table_group_state": "OPEN|BILL_REQUESTED|PAID|CLOSED|null"
  }
]
```

### POST /tables/{physicalTableId}/start-service
Response:
```json
{
  "id": "uuid",
  "state": "OPEN|BILL_REQUESTED|PAID|CLOSED",
  "physical_table_ids": ["uuid"],
  "opened_at": "datetime",
  "closed_at": "datetime|null"
}
```

## Table Groups
### GET /table-groups/open
Response:
```json
[
  {
    "id": "uuid",
    "state": "OPEN|BILL_REQUESTED|PAID|CLOSED",
    "physical_table_ids": ["uuid"],
    "opened_at": "datetime",
    "closed_at": "datetime|null"
  }
]
```

### GET /table-groups/{tableGroupId}
Response:
```json
{
  "id": "uuid",
  "state": "OPEN|BILL_REQUESTED|PAID|CLOSED",
  "physical_table_ids": ["uuid"],
  "opened_at": "datetime",
  "closed_at": "datetime|null"
}
```

### GET /table-groups/{tableGroupId}/order-items
Query params:
- `served`: `all|served|unserved` (default `all`)
- `include_voided`: `true|false` (default `true`)

Response:
```json
[
  {
    "id": "uuid",
    "order_id": "uuid",
    "physical_table_id": "uuid",
    "table_code": "string",
    "menu_item_id": "uuid|null",
    "menu_item_name": "string",
    "unit_price": "decimal",
    "note": "string|null",
    "status": "ACTIVE|VOIDED",
    "served_at": "datetime|null",
    "created_at": "datetime",
    "voided_at": "datetime|null"
  }
]
```

### POST /table-groups/{tableGroupId}/request-bill
Response: `200 OK` (empty body)

### POST /table-groups/{tableGroupId}/mark-paid
Response: `200 OK` (empty body)

### POST /table-groups/{tableGroupId}/close
Response: `200 OK` (empty body)

### POST /table-groups/{tableGroupId}/tables/add
Request:
```json
{
  "physical_table_id": "uuid"
}
```
Response: `200 OK` (empty body)

### POST /table-groups/{tableGroupId}/tables/remove
Request:
```json
{
  "physical_table_id": "uuid"
}
```
Response: `200 OK` (empty body)

### POST /table-groups/{tableGroupId}/switch
Request:
```json
{
  "from_table_id": "uuid",
  "to_table_id": "uuid"
}
```
Response: `200 OK` (empty body)

### POST /table-groups/merge
Request:
```json
{
  "source_group_id": "uuid",
  "target_group_id": "uuid"
}
```
Response: `200 OK` (empty body)

### POST /table-groups/{tableGroupId}/split
Request:
```json
{
  "physical_table_ids": ["uuid"]
}
```
Response:
```json
{
  "id": "uuid",
  "state": "OPEN|BILL_REQUESTED|PAID|CLOSED",
  "physical_table_ids": ["uuid"],
  "opened_at": "datetime",
  "closed_at": "datetime|null"
}
```

## Orders
### POST /tables/{physicalTableId}/orders/confirm
Request:
```json
{
  "idempotency_key": "string",
  "items": [
    {
      "menu_item_id": "uuid",
      "quantity": 1,
      "note": "string|null"
    }
  ]
}
```
Response:
```json
{
  "order_id": "uuid",
  "table_group_id": "uuid",
  "order_item_ids": ["uuid"]
}
```

## Order Items (admin only)
### POST /order-items/{orderItemId}/void
Response: `204 No Content`

### POST /order-items/{orderItemId}/mark-served
Response: `204 No Content`

### POST /order-items/{orderItemId}/reprint
Response: `204 No Content`

## Billing (admin only)
### GET /table-groups/{tableGroupId}/bill
Response:
```json
{
  "table_group_id": "uuid",
  "table_group_state": "OPEN|BILL_REQUESTED|PAID|CLOSED",
  "items_total": "decimal",
  "adjustments_total": "decimal",
  "subtotal": "decimal",
  "tax_total": "decimal",
  "final_total": "decimal"
}
```

### POST /table-groups/{tableGroupId}/bill-adjustments
Request:
```json
{
  "amount": "decimal",
  "description": "string",
  "reason": "string|null",
  "reference_order_item_id": "uuid|null",
  "category": "string|null"
}
```
Response:
```json
{
  "id": "uuid",
  "table_group_id": "uuid",
  "amount": "decimal",
  "description": "string",
  "reason": "string|null",
  "category": "string|null",
  "created_by": "string",
  "created_at": "datetime",
  "reference_order_item_id": "uuid|null"
}
```

## Menu Items (admin only for writes)
### GET /menu-items
Response:
```json
[
  {
    "id": "uuid",
    "name": "string",
    "price": "decimal",
    "category": "string",
    "status": "AVAILABLE|UNAVAILABLE|RETIRED",
    "image_url": "string|null",
    "created_at": "datetime"
  }
]
```

### POST /menu-items
Request:
```json
{
  "name": "string",
  "price": "decimal",
  "category": "string"
}
```
Response:
```json
{
  "id": "uuid",
  "name": "string",
  "price": "decimal",
  "category": "string",
  "status": "AVAILABLE|UNAVAILABLE|RETIRED",
  "image_url": "string|null",
  "created_at": "datetime"
}
```

### PATCH /menu-items/{menuItemId}
Request:
```json
{
  "name": "string|null",
  "price": "decimal|null",
  "category": "string|null",
  "status": "AVAILABLE|UNAVAILABLE|RETIRED|null"
}
```
Response:
```json
{
  "id": "uuid",
  "name": "string",
  "price": "decimal",
  "category": "string",
  "status": "AVAILABLE|UNAVAILABLE|RETIRED",
  "image_url": "string|null",
  "created_at": "datetime"
}
```

### POST /menu-items/{menuItemId}/retire
Response:
```json
{
  "id": "uuid",
  "name": "string",
  "price": "decimal",
  "category": "string",
  "status": "AVAILABLE|UNAVAILABLE|RETIRED",
  "image_url": "string|null",
  "created_at": "datetime"
}
```

### POST /menu-items/{menuItemId}/image
Request: `multipart/form-data` with file field `file`

Response:
```json
{
  "id": "uuid",
  "name": "string",
  "price": "decimal",
  "category": "string",
  "status": "AVAILABLE|UNAVAILABLE|RETIRED",
  "image_url": "string|null",
  "created_at": "datetime"
}
```
