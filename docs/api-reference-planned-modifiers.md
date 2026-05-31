# API Reference (Planned Modifiers Contract)

Status:
- Implemented now: modifier catalog endpoints, menu-item modifier configuration endpoints, and modifier-aware order confirm payload/validation.
- Planned next: table-group order-item shape extensions and grouped kitchen print rendering details.

This document defines the target API shapes for the modifiers feature, including both implemented and planned-next parts.

## Auth

All endpoints require `Authorization: Bearer <session_token>`.

## Modifier Groups (Admin)

### GET /modifier-groups
Response:
```json
[
  {
    "id": "uuid",
    "code": "ADDON",
    "name": "Add-on",
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
  "code": "ADDON",
  "name": "Add-on"
}
```
Response:
```json
{
  "id": "uuid",
  "code": "ADDON",
  "name": "Add-on",
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
  "code": "ADDON",
  "name": "Add-on",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### PATCH /modifier-groups/{modifierGroupId}
Request:
```json
{
  "name": "Add-on",
  "is_active": false
}
```
Response:
```json
{
  "id": "uuid",
  "code": "ADDON",
  "name": "Add-on",
  "is_active": false,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Modifier Options (Admin)

### GET /modifier-groups/{modifierGroupId}/options
Response:
```json
[
  {
    "id": "uuid",
    "modifier_group_id": "uuid",
    "code": "FRIED_EGG",
    "label": "Fried Egg",
    "price_delta": "10.00",
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
  "code": "FRIED_EGG",
  "label": "Fried Egg",
  "price_delta": "10.00"
}
```
Response:
```json
{
  "id": "uuid",
  "modifier_group_id": "uuid",
  "code": "FRIED_EGG",
  "label": "Fried Egg",
  "price_delta": "10.00",
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
  "code": "FRIED_EGG",
  "label": "Fried Egg",
  "price_delta": "10.00",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### PATCH /modifier-options/{modifierOptionId}
Request:
```json
{
  "label": "Fried Egg",
  "price_delta": "12.00",
  "is_active": false
}
```
Response:
```json
{
  "id": "uuid",
  "modifier_group_id": "uuid",
  "code": "FRIED_EGG",
  "label": "Fried Egg",
  "price_delta": "12.00",
  "is_active": false,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Menu-item Modifier Configuration (Admin)

### GET /menu-items/{menuItemId}/modifiers
Response:
```json
{
  "groups": [
    {
      "modifier_group_id": "uuid",
      "group_name": "Add-on",
      "min_select": 0,
      "max_select": 3,
      "option_ids": ["uuid", "uuid"]
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
      "max_select": 3,
      "option_ids": ["uuid", "uuid"]
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
      "group_name": "Add-on",
      "min_select": 0,
      "max_select": 3,
      "option_ids": ["uuid", "uuid"]
    }
  ]
}
```

## Orders (Planned Confirm Payload Change)

### POST /tables/{physicalTableId}/orders/confirm
Request:
```json
{
  "idempotency_key": "string",
  "items": [
    {
      "client_line_id": "line-1",
      "menu_item_id": "uuid",
      "note": "string|null",
      "modifier_selections": [
        {
          "modifier_group_id": "uuid",
          "selected_option_ids": ["uuid", "uuid"]
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
      "client_line_id": "line-1",
      "modifier_group_id": "uuid",
      "reason": "MISSING_REQUIRED_SELECTION"
    }
  ]
}
```

Supported `reason` values:
- `MISSING_REQUIRED_SELECTION`
- `TOO_MANY_SELECTIONS`
- `OPTION_NOT_ALLOWED`
- `OPTION_NOT_AVAILABLE`
- `GROUP_NOT_CONFIGURED`
- `DUPLICATE_SELECTION`
- `DUPLICATE_GROUP_SELECTION`

## Table-group Order Items (Planned Field Additions)

### GET /table-groups/{tableGroupId}/order-items
Response shape remains flat list. Planned additional fields:

```json
[
  {
    "id": "uuid",
    "kind": "MAIN|MODIFIER",
    "parent_order_item_id": "uuid|null",
    "menu_item_name": "string",
    "modifier_group_name_snap": "string|null",
    "modifier_option_label_snap": "string|null"
  }
]
```
