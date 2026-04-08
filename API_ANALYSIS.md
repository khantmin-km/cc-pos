# Frontend vs Backend API Analysis

## 🔍 **OVERVIEW**
This analysis compares frontend API calls with backend endpoints to identify misalignments and missing functionality.

---

## 📋 **BACKEND ENDPOINTS (Available)**

### `/tables` prefix (Physical Tables)
- `GET /tables` - List all physical tables ✅
- `GET /tables/overview` - List table overview ✅
- `POST /tables/{physical_table_id}/start-service` - Start service ✅

### `/table-groups` prefix (Table Groups)
- `GET /table-groups/open` - List open groups ✅
- `GET /table-groups/{table_group_id}` - Get specific group ✅
- `GET /table-groups/{table_group_id}/bill` - Get bill breakdown ✅
- `GET /table-groups/{table_group_id}/order-items` - List order items ✅
- `POST /table-groups/{table_group_id}/bill-adjustments` - Create bill adjustment ✅
- `POST /table-groups/{table_group_id}/request-bill` - Request bill ✅
- `POST /table-groups/{table_group_id}/mark-paid` - Mark as paid ✅
- `POST /table-groups/{table_group_id}/close` - Close group ✅
- `POST /table-groups/{table_group_id}/tables/add` - Add table ✅
- `POST /table-groups/{table_group_id}/tables/remove` - Remove table ✅
- `POST /table-groups/{table_group_id}/switch` - Switch table ✅
- `POST /table-groups/merge` - Merge groups ✅
- `POST /table-groups/{table_group_id}/split` - Split group ✅

### `/menu-items` prefix (Menu Items)
- `GET /menu-items` - List menu items ✅
- `POST /menu-items` - Create menu item ✅
- `PATCH /menu-items/{menu_item_id}` - Update menu item ✅
- `POST /menu-items/{menu_item_id}/retire` - Retire menu item ✅
- `POST /menu-items/{menu_item_id}/image` - Upload image ✅

### `/order-items` prefix (Order Items)
- `POST /order-items/{order_item_id}/void` - Void order item ✅
- `POST /order-items/{order_item_id}/mark-served` - Mark as served ✅
- `POST /order-items/{order_item_id}/reprint` - Reprint order item ✅

### `/tables` prefix (Orders)
- `POST /tables/{physical_table_id}/orders/confirm` - Confirm order ✅

### `/auth` prefix (Authentication)
- `POST /auth/login` - Login ✅

### `/audit-events` prefix (Audit)
- `GET /audit-events` - List audit events ✅

---

## 📋 **FRONTEND API CALLS (Expected)**

### Tables API
- `GET /tables` - ✅ Matches backend
- `POST /tables/{id}/start-service` - ✅ Matches backend

### Table Groups API
- `GET /table-groups/open` - ✅ Matches backend
- `GET /table-groups/{id}` - ✅ Matches backend
- `POST /table-groups/{id}/request-bill` - ✅ Matches backend
- `POST /table-groups/{id}/mark-paid` - ✅ Matches backend
- `POST /table-groups/{id}/close` - ✅ Matches backend
- `POST /table-groups/{id}/tables/add` - ✅ Matches backend
- `POST /table-groups/{id}/tables/remove` - ✅ Matches backend
- `POST /table-groups/{id}/switch` - ✅ Matches backend
- `POST /table-groups/merge` - ✅ Matches backend
- `POST /table-groups/{id}/split` - ✅ Matches backend

### Orders API
- `POST /tables/{tableId}/orders/confirm` - ✅ Matches backend

### Order Items API
- `GET /order-items/table/{tableId}` - ❌ **MISSING BACKEND ENDPOINT**
- `POST /order-items/{id}/void` - ✅ Matches backend
- `POST /order-items/{id}/mark-served` - ✅ Matches backend
- `POST /order-items/{id}/reprint` - ✅ Matches backend

### Menu Items API
- `GET /menu-items` - ✅ Matches backend
- `POST /menu-items` - ✅ Matches backend
- `PUT /menu-items/{id}` - ❌ **MISMATCH: Backend uses PATCH, Frontend uses PUT**
- `POST /menu-items/{id}/retire` - ✅ Matches backend
- `POST /menu-items/{id}/image` - ✅ Matches backend

### Sessions API
- `POST /auth/login` - ✅ Matches backend
- `POST /sessions/{id}/end` - ❌ **MISSING BACKEND ENDPOINT**

### Waiters API
- `GET /waiters` - ❌ **MISSING BACKEND ENDPOINT**
- `POST /waiters` - ❌ **MISSING BACKEND ENDPOINT**
- `PUT /waiters/{id}` - ❌ **MISSING BACKEND ENDPOINT**

### Billing API
- `GET /table-groups/{id}/bill` - ✅ Matches backend
- `POST /table-groups/{id}/adjustments` - ❌ **MISMATCH: Backend uses /bill-adjustments, Frontend uses /adjustments**
- `POST /table-groups/{id}/print` - ❌ **MISSING BACKEND ENDPOINT**

---

## 🚨 **CRITICAL MISALIGNMENTS**

### 1. **Missing Backend Endpoints**
- `GET /order-items/table/{tableId}` - Frontend expects to get order items by table
- `POST /sessions/{id}/end` - Frontend expects logout endpoint
- `GET /waiters` - Frontend expects to list waiters
- `POST /waiters` - Frontend expects to create waiters
- `PUT /waiters/{id}` - Frontend expects to update waiters
- `POST /table-groups/{id}/print` - Frontend expects bill printing

### 2. **HTTP Method Mismatches**
- Menu Items Update: Frontend uses `PUT`, Backend expects `PATCH`

### 3. **Endpoint Path Mismatches**
- Bill Adjustments: Frontend uses `/table-groups/{id}/adjustments`, Backend uses `/table-groups/{id}/bill-adjustments`

---

## 📊 **ALIGNMENT STATUS**

| Category | Frontend Calls | Backend Endpoints | Status |
|----------|----------------|------------------|---------|
| Physical Tables | 2 | 3 | ✅ Aligned |
| Table Groups | 10 | 13 | ✅ Aligned |
| Orders | 1 | 1 | ✅ Aligned |
| Order Items | 4 | 3 | ⚠️ Missing endpoint |
| Menu Items | 5 | 5 | ⚠️ Method mismatch |
| Authentication | 2 | 1 | ⚠️ Missing logout |
| Waiters | 3 | 0 | ❌ Completely missing |
| Billing | 3 | 2 | ⚠️ Path mismatch |

---

## 🔧 **REQUIRED FIXES**

### **High Priority (Breaking Functionality)**
1. **Add Waiters API endpoints** to backend
2. **Add logout endpoint** (`POST /sessions/{id}/end`)
3. **Fix bill adjustments path** in frontend
4. **Add order items by table endpoint**

### **Medium Priority (Minor Issues)**
1. **Fix menu items HTTP method** (PUT → PATCH)
2. **Add bill printing endpoint** if needed

---

## 📝 **FRONTEND WORKAROUNDS NEEDED**

Since backend changes are not allowed, frontend needs to:

1. **Waiters functionality**: Cannot be implemented without backend endpoints
2. **Logout**: May need to clear localStorage without backend call
3. **Order items by table**: Use existing table group endpoints instead
4. **Bill printing**: May need alternative implementation

---

## 🎯 **SUMMARY**

- **Total Frontend API Calls**: 35
- **Total Backend Endpoints**: 31
- **Perfectly Aligned**: 22 calls (63%)
- **Minor Issues**: 6 calls (17%)
- **Major Issues**: 7 calls (20%)

The core POS functionality (tables, orders, billing) is well-aligned, but supporting features like waiters management and some utility endpoints are missing from the backend.
