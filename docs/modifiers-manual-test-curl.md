# Modifiers Manual Test (curl + psql)

This runbook is for PR2 + PR3 + PR4 behavior:
- modifier catalog endpoints
- menu-item modifier config endpoint
- order confirm (expanded lines, no `quantity`)
- flat order-items response with modifier relationship fields
- parent-void cascade to modifier children

## 0. Setup

```bash
cd /Volumes/Workspace/Projects/Work/CC/backend

export DATABASE_URL='postgresql+psycopg2://khant@localhost:5432/cc_dev'
BASE='http://127.0.0.1:8000'
```

Verify runtime DB target:

```bash
echo "$DATABASE_URL"
```

Apply schema migrations (required before login/seed):

```bash
uv run alembic upgrade head
```

Optional sanity check:

```bash
psql -d cc_dev -U khant -c "\dt"
```

Get tokens:

```bash
ADMIN_TOKEN=$(curl -sS -X POST "$BASE/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","pin":"1234"}' | jq -r '.token')

WAITER_TOKEN=$(curl -sS -X POST "$BASE/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"waiter1","pin":"1111"}' | jq -r '.token')

echo "$ADMIN_TOKEN"
echo "$WAITER_TOKEN"
```

Pick a physical table:

```bash
TABLE_ID=$(curl -sS "$BASE/tables" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq -r '.[0].id')

echo "$TABLE_ID"
```

## 1. Create Menu Item

```bash
MENU_ID=$(curl -sS -X POST "$BASE/menu-items" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Thai Noodle","price":"50.00","category":"Noodle"}' | jq -r '.id')

echo "$MENU_ID"
```

## 2. Create Modifier Group + Options

```bash
GROUP_ID=$(curl -sS -X POST "$BASE/modifier-groups" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"ADDON","name":"Add-on"}' | jq -r '.id')

echo "$GROUP_ID"
```

```bash
EGG_ID=$(curl -sS -X POST "$BASE/modifier-groups/$GROUP_ID/options" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"EGG","label":"Boiled Egg","price_delta":"10.00"}' | jq -r '.id')

CRACKLING_ID=$(curl -sS -X POST "$BASE/modifier-groups/$GROUP_ID/options" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"CRACKLING","label":"Pork Crackling","price_delta":"15.00"}' | jq -r '.id')

echo "$EGG_ID"
echo "$CRACKLING_ID"
```

## 3. Attach Modifier Config to Menu Item

```bash
curl -sS -X PUT "$BASE/menu-items/$MENU_ID/modifiers" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"groups\": [
      {
        \"modifier_group_id\": \"$GROUP_ID\",
        \"min_select\": 0,
        \"max_select\": 3,
        \"option_ids\": [\"$EGG_ID\", \"$CRACKLING_ID\"]
      }
    ]
  }" | jq
```

Read back config:

```bash
curl -sS "$BASE/menu-items/$MENU_ID/modifiers" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

## 4. Start Service

```bash
GROUP_TABLE=$(curl -sS -X POST "$BASE/tables/$TABLE_ID/start-service" \
  -H "Authorization: Bearer $WAITER_TOKEN" | jq -r '.id')

echo "$GROUP_TABLE"
```

## 5. Confirm Order (Expanded Lines, No quantity)

Important: one `items[]` entry = one persisted `MAIN` order item.

```bash
curl -sS -X POST "$BASE/tables/$TABLE_ID/orders/confirm" \
  -H "Authorization: Bearer $WAITER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"idempotency_key\": \"mod-happy-001\",
    \"items\": [
      {
        \"client_line_id\": \"line-1\",
        \"menu_item_id\": \"$MENU_ID\",
        \"note\": \"less spicy\",
        \"modifier_selections\": [
          {
            \"modifier_group_id\": \"$GROUP_ID\",
            \"selected_option_ids\": [\"$EGG_ID\", \"$CRACKLING_ID\"]
          }
        ]
      },
      {
        \"client_line_id\": \"line-2\",
        \"menu_item_id\": \"$MENU_ID\",
        \"modifier_selections\": [
          {
            \"modifier_group_id\": \"$GROUP_ID\",
            \"selected_option_ids\": [\"$EGG_ID\"]
          }
        ]
      }
    ]
  }" | jq
```

## 6. Verify Flat Order-item Shape (PR4)

```bash
curl -sS "$BASE/table-groups/$GROUP_TABLE/order-items" \
  -H "Authorization: Bearer $WAITER_TOKEN" | jq
```

Show only relationship fields:

```bash
curl -sS "$BASE/table-groups/$GROUP_TABLE/order-items" \
  -H "Authorization: Bearer $WAITER_TOKEN" | jq '.[] | {
    id,
    kind,
    parent_order_item_id,
    menu_item_name,
    modifier_group_name_snap,
    modifier_option_label_snap,
    status
  }'
```

## 7. Verify Billing Includes Modifiers

```bash
curl -sS "$BASE/table-groups/$GROUP_TABLE/bill" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
```

## 8. Void MAIN and Check Cascade

Pick one main item:

```bash
MAIN_ID=$(curl -sS "$BASE/table-groups/$GROUP_TABLE/order-items" \
  -H "Authorization: Bearer $WAITER_TOKEN" | jq -r '.[] | select(.kind=="MAIN") | .id' | head -n 1)

echo "$MAIN_ID"
```

Void it:

```bash
curl -i -sS -X POST "$BASE/order-items/$MAIN_ID/void" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

Verify parent + child statuses:

```bash
curl -sS "$BASE/table-groups/$GROUP_TABLE/order-items" \
  -H "Authorization: Bearer $WAITER_TOKEN" | jq '.[] | {
    id, kind, parent_order_item_id, status
  }'
```

## 9. Negative Cases

### 9.1 Duplicate group selection in one line

```bash
curl -sS -X POST "$BASE/tables/$TABLE_ID/orders/confirm" \
  -H "Authorization: Bearer $WAITER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"idempotency_key\": \"mod-dup-group-001\",
    \"items\": [
      {
        \"client_line_id\": \"line-dup-group\",
        \"menu_item_id\": \"$MENU_ID\",
        \"modifier_selections\": [
          {\"modifier_group_id\": \"$GROUP_ID\", \"selected_option_ids\": [\"$EGG_ID\"]},
          {\"modifier_group_id\": \"$GROUP_ID\", \"selected_option_ids\": [\"$CRACKLING_ID\"]}
        ]
      }
    ]
  }" | jq
```

Expected: `code = MODIFIER_VALIDATION_FAILED`, reason includes `DUPLICATE_GROUP_SELECTION`.

### 9.2 Archive option then confirm with it

Archive option:

```bash
curl -sS -X PATCH "$BASE/modifier-options/$EGG_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active":false}' | jq
```

Try confirming with archived option:

```bash
curl -sS -X POST "$BASE/tables/$TABLE_ID/orders/confirm" \
  -H "Authorization: Bearer $WAITER_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"idempotency_key\": \"mod-option-inactive-001\",
    \"items\": [
      {
        \"client_line_id\": \"line-inactive-option\",
        \"menu_item_id\": \"$MENU_ID\",
        \"modifier_selections\": [
          {\"modifier_group_id\": \"$GROUP_ID\", \"selected_option_ids\": [\"$EGG_ID\"]}
        ]
      }
    ]
  }" | jq
```

Expected reason includes `OPTION_NOT_AVAILABLE`.

## 10. Optional Direct SQL Checks

```bash
psql -d cc_dev -U khant -c "
select
  id,
  kind,
  parent_order_item_id,
  menu_item_name_snap,
  modifier_group_name_snap,
  modifier_option_label_snap,
  unit_price_snap,
  status
from order_items
order by created_at desc
limit 30;
"
```
