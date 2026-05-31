# Modifiers Integration Guide (Frontend)

Status: Spec-locked and approved for implementation planning.  
Implementation status: Not implemented in backend yet.

This document explains the backend contract changes that frontend should prepare for.

## 1. Why This Change Exists

We are adding structured modifiers so:
- Kitchen tickets show modifiers under the correct main dish.
- Modifier price deltas are included in bill totals automatically.
- Corrections stay consistent with current `VOID + ADD` flow.

## 2. Core Domain Decisions

- `MenuItem` and modifier catalog are separate entities.
- Modifier catalog uses:
  - `ModifierGroup` (template group, e.g. Add-on, Spicy Level)
  - `ModifierOption` (options under group, e.g. Fried Egg, Medium)
- Menu-item-specific config uses:
  - group attachment to menu item
  - `min_select` / `max_select` per attached group
  - allowed option subset per attached group
- Modifier pricing comes from global `ModifierOption.price_delta` only.
- Order correction policy:
  - direct void of modifier child item is forbidden
  - void parent main item, then add corrected line (`VOID + ADD`)

## 3. Order Confirm Contract Change (Important)

Current backend accepts aggregated quantity and expands server-side.

New contract is a hard cutover:
- frontend sends one request line per main-item instance
- no aggregated quantity lines
- no backward compatibility fallback

Example (allowed):

```json
{
  "idempotency_key": "key-1",
  "items": [
    {
      "client_line_id": "line-1",
      "menu_item_id": "thai-noodle-id",
      "note": "less soup",
      "modifier_selections": [
        {
          "modifier_group_id": "noodle-type-group-id",
          "selected_option_ids": ["glass-noodle-id"]
        },
        {
          "modifier_group_id": "meat-type-group-id",
          "selected_option_ids": ["braised-pork-id", "minced-chicken-id"]
        }
      ]
    },
    {
      "client_line_id": "line-2",
      "menu_item_id": "thai-noodle-id",
      "note": "less soup",
      "modifier_selections": [
        {
          "modifier_group_id": "noodle-type-group-id",
          "selected_option_ids": ["glass-noodle-id"]
        },
        {
          "modifier_group_id": "meat-type-group-id",
          "selected_option_ids": ["braised-pork-id", "minced-chicken-id"]
        }
      ]
    }
  ]
}
```

Example (rejected):

```json
{
  "idempotency_key": "key-2",
  "items": [
    {
      "menu_item_id": "thai-noodle-id",
      "quantity": 2
    }
  ]
}
```

## 4. Validation Rules Frontend Must Respect

For each main line:
- selected options must belong to allowed option subset for that menu item/group
- selection count per group must satisfy `min_select <= count <= max_select`
- inactive group/option is rejected at confirm time

Draft safety note:
- if admin deactivates/changes menu or modifier options while waiter is drafting,
  confirm may reject; frontend should re-fetch menu/modifier config and prompt reselection.

## 5. Kitchen Ticket Shape

Kitchen output must stay nested by parent line, with group labels:

```text
Thai Noodle
  Noodle Type: Glass Noodle
  Meat Type: Braised Pork
  Meat Type: Minced Chicken
  Add-on: Pork Crackling
  Spicy Level: Medium
```

Flattened output is not acceptable.

## 6. Billing Behavior

Each selected modifier option becomes a child order item with its own `unit_price_snap` delta.

Billing stays generic:
- sum of all `ACTIVE` order items
- includes both main and modifier child items

No frontend-side price math is required for final authority.

## 7. Admin UI Workflow Recommendation

Recommended flow:

1. Manage global modifier catalog
- create/update `ModifierGroup`
- create/update `ModifierOption` under group

2. Configure each menu item
- attach groups to menu item
- set `min_select`/`max_select`
- choose allowed options subset

This is designed so the same group can be reused with different allowed subsets by menu item.

## 8. Endpoint Strategy (Planned)

Planned backend shape:

- Global catalog CRUD:
  - group endpoints
  - option endpoints
- Per-menu-item configuration:
  - bulk replace endpoint for one menu item's modifier config

Reason:
- frontend save UX is simpler with one payload for menu-item config
- catalog remains explicit and reusable

## 9. What Stays The Same

- Confirm is still idempotent with `idempotency_key`.
- OrderItems remain the unit of billing and history.
- Notes remain available for free-text customer requests.
- `BILL_REQUESTED` and later still block order-item mutation.

## 10. Frontend Adaptation Checklist

- Stop sending `quantity` in order confirm lines.
- Build per-line modifier selection UI and payload.
- Enforce `min_select`/`max_select` on client side before submit.
- Handle confirm-time rejections and refresh modifier config.
- Show nested parent+modifier lines in order review UI.
- Keep note input available regardless of modifiers.
