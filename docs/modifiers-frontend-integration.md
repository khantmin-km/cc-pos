# Modifiers Integration Guide (Frontend)

Status: Spec-locked and approved for implementation planning.  
Implementation status:
- Implemented: modifier catalog endpoints, menu-item modifier config endpoints.
- Implemented: modifier-aware order confirm payload and validation error response.
- Implemented: grouped kitchen print payload rendering and table-group order-items response shape enhancements.

This document is the shared contract guide for frontend adaptation.

## 1. Core Domain Model

Three layers:

1. Modifier Catalog (global)
- `ModifierGroup` (e.g., Add-on, Noodle Type, Spicy Level)
- `ModifierOption` (e.g., Fried Egg, Glass Noodle, Medium)

2. Menu-item Modifier Configuration
- Attach groups to a menu item
- Configure `min_select` / `max_select` per attached group
- Select allowed option subset per attached group

3. Order Confirmation Selection
- Waiter submits selections per main line
- Backend validates and persists parent + child order-items

## 2. Hard Rules (Locked)

- `MenuItem` and modifier catalog are separate entities.
- Every `ModifierOption` belongs to exactly one `ModifierGroup`.
- Options cannot exist without a group.
- Options are not attached directly to menu items without group context.
- Modifier price comes only from global `ModifierOption.price_delta`.
- Modifier child direct void is forbidden.
- Correction flow is parent main-item `VOID + ADD`.
- Confirm payload uses one submitted line = one persisted main order item.
- No `quantity` in confirm payload.
- No backward compatibility mode for legacy aggregated quantity lines.

## 3. Archive Semantics (No Hard Delete)

For `ModifierGroup` and `ModifierOption`:
- archive by setting inactive status (`is_active=false`)
- no hard delete
- no cascading physical unlink

Effects:
- inactive groups/options cannot be used for future confirms
- existing link rows are kept
- historical order snapshots remain unchanged

Archiving a group does not automatically archive its options.

## 4. Implemented Endpoints

Global modifier catalog:

- `GET /modifier-groups`
- `POST /modifier-groups`
- `GET /modifier-groups/{modifierGroupId}`
- `PATCH /modifier-groups/{modifierGroupId}`
- `GET /modifier-groups/{modifierGroupId}/options`
- `POST /modifier-groups/{modifierGroupId}/options`
- `GET /modifier-options/{modifierOptionId}`
- `PATCH /modifier-options/{modifierOptionId}`

Menu-item modifier configuration:

- `GET /menu-items/{menuItemId}/modifiers`
- `PUT /menu-items/{menuItemId}/modifiers`

`PUT` is a full replacement payload for one menu item’s modifier config.

## 5. Menu-item Modifier Config Payload (Implemented)

```json
{
  "groups": [
    {
      "modifier_group_id": "uuid",
      "min_select": 1,
      "max_select": 3,
      "option_ids": ["uuid", "uuid"]
    }
  ]
}
```

## 6. Order Confirm Payload (Implemented)

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

Notes:
- `client_line_id` is required on each line.
- `items[]` must be expanded lines. Do not send aggregated `quantity`.

## 7. Validation Errors (Implemented)

When modifier validation fails:

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

Frontend should map `details[]` back to line-level UI errors.

## 8. Kitchen Printing Shape (Implemented)

Target kitchen output is nested and group-labeled:

```text
Thai Noodle
  Noodle Type: Glass Noodle
  Meat Type: Braised Pork, Minced Chicken
  Add-on: Pork Crackling
  Spicy Level: Medium
```

Modifier groups with many options should wrap safely for printer width.

## 9. Table-group Order-items Shape (Implemented, Flat)

`GET /table-groups/{tableGroupId}/order-items` remains flat and includes modifier relationship fields:

```json
{
  "id": "uuid",
  "kind": "MAIN|MODIFIER",
  "parent_order_item_id": "uuid|null",
  "modifier_group_name_snap": "string|null",
  "modifier_option_label_snap": "string|null"
}
```

## 10. Billing Behavior

Each selected modifier option becomes a child order-item.

Billing remains generic:
- sum all `ACTIVE` order-items
- includes both main and modifier child rows

No frontend-side final price authority is required.

## 11. Frontend UI Guidance

Recommended screens:

1. Modifier Catalog
- create/archive groups
- create/archive options under selected group

2. Menu Item Editor (Modifiers section)
- attach groups
- set `min_select` / `max_select`
- choose allowed options subset

Menu-item editor configures relationships only; it does not create group/option catalog entries inline.

## 12. Frontend Adaptation Checklist

- Remove confirm-line `quantity`.
- Send expanded lines with `client_line_id`.
- Build per-line modifier selection state.
- Enforce `min_select` / `max_select` before submit.
- Handle `MODIFIER_VALIDATION_FAILED` with line-level highlighting.
- Refresh config on confirm rejection when catalog changed during draft.
- Keep note input available regardless of modifier presence.
