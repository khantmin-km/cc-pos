# API Reference (Current)

Modifier catalog and menu-item modifier configuration endpoints are implemented.
Planned (not yet implemented): modifier-aware order confirm payload and validation error contract (see `docs/modifiers-frontend-integration.md` and `docs/api-reference-planned-modifiers.md`).
Planned change highlights:
- table-group order-items response will add modifier hierarchy fields
- kitchen print rendering will group modifiers by group label

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
      "client_line_id": "string",
      "menu_item_id": "uuid",
      "note": "string|null",
      "modifier_selections": [
        {
          "modifier_group_id": "uuid",
          "selected_option_ids": ["uuid"]
        }
      ]
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

Validation error response (modifier rules):
```json
{
  "code": "MODIFIER_VALIDATION_FAILED",
  "message": "Modifier validation failed",
  "details": [
    {
      "client_line_id": "string",
      "modifier_group_id": "uuid",
      "reason": "MISSING_REQUIRED_SELECTION|TOO_MANY_SELECTIONS|OPTION_NOT_ALLOWED|OPTION_NOT_AVAILABLE|GROUP_NOT_CONFIGURED|DUPLICATE_SELECTION|DUPLICATE_GROUP_SELECTION"
    }
  ]
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

### GET /menu-items/{menuItemId}/modifiers
Response:
```json
{
  "groups": [
    {
      "modifier_group_id": "uuid",
      "group_name": "string",
      "min_select": 0,
      "max_select": 1,
      "option_ids": ["uuid"]
    }
  ]
}
```

### PUT /menu-items/{menuItemId}/modifiers
Request:
```json
{
  "groups": [
    {
      "modifier_group_id": "uuid",
      "min_select": 0,
      "max_select": 1,
      "option_ids": ["uuid"]
    }
  ]
}
```
Response:
```json
{
  "groups": [
    {
      "modifier_group_id": "uuid",
      "group_name": "string",
      "min_select": 0,
      "max_select": 1,
      "option_ids": ["uuid"]
    }
  ]
}
```

## Modifiers (admin only)
### GET /modifier-groups
Response:
```json
[
  {
    "id": "uuid",
    "code": "string",
    "name": "string",
    "is_active": true,
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

### POST /modifier-groups
Request:
```json
{
  "code": "string",
  "name": "string"
}
```
Response:
```json
{
  "id": "uuid",
  "code": "string",
  "name": "string",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### GET /modifier-groups/{modifierGroupId}
Response:
```json
{
  "id": "uuid",
  "code": "string",
  "name": "string",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### PATCH /modifier-groups/{modifierGroupId}
Request:
```json
{
  "name": "string|null",
  "is_active": "boolean|null"
}
```
Response:
```json
{
  "id": "uuid",
  "code": "string",
  "name": "string",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### GET /modifier-groups/{modifierGroupId}/options
Response:
```json
[
  {
    "id": "uuid",
    "modifier_group_id": "uuid",
    "code": "string",
    "label": "string",
    "price_delta": "decimal",
    "is_active": true,
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

### POST /modifier-groups/{modifierGroupId}/options
Request:
```json
{
  "code": "string",
  "label": "string",
  "price_delta": "decimal"
}
```
Response:
```json
{
  "id": "uuid",
  "modifier_group_id": "uuid",
  "code": "string",
  "label": "string",
  "price_delta": "decimal",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### GET /modifier-options/{modifierOptionId}
Response:
```json
{
  "id": "uuid",
  "modifier_group_id": "uuid",
  "code": "string",
  "label": "string",
  "price_delta": "decimal",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### PATCH /modifier-options/{modifierOptionId}
Request:
```json
{
  "label": "string|null",
  "price_delta": "decimal|null",
  "is_active": "boolean|null"
}
```
Response:
```json
{
  "id": "uuid",
  "modifier_group_id": "uuid",
  "code": "string",
  "label": "string",
  "price_delta": "decimal",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
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

## Audit Events (admin only)
### GET /audit-events
Query params:
- `event_type` (optional)
- `entity_type` (optional)
- `entity_id` (optional)
- `actor_user_id` (optional)
- `limit` (default 50, max 200)
- `offset` (default 0)

Response:
```json
[
  {
    "id": "uuid",
    "actor_user_id": "uuid",
    "actor_username": "string",
    "actor_role": "ADMIN|WAITER",
    "event_type": "string",
    "entity_type": "string",
    "entity_id": "uuid",
    "metadata": {},
    "created_at": "datetime"
  }
]
```
