# API Endpoints Comparison - Frontend vs Backend

## Overview
This document compares the API endpoints expected by the frontend with the actual endpoints implemented in the backend.

---

## 1. Authentication API

### Frontend Expectations
```typescript
POST /auth/login
- Request: { username: string, pin: string }
- Response: { token: string, user_id: string, username: string, role: string, expires_at: string }
```

### Backend Implementation
✅ **MATCH**
```python
@router.post("/login", prefix="/auth")
- Endpoint: POST /auth/login
- Request: LoginRequest { username, pin }
- Response: LoginResponse { token, user_id, username, role, expires_at }
```

---

## 2. Physical Tables API

### Frontend Expectations
```typescript
GET /tables
POST /tables/{id}/start-service
```

### Backend Implementation
✅ **MATCH**
```python
@router.get("", prefix="/tables")
  Endpoint: GET /tables
  
@router.post("/{physical_table_id}/start-service", prefix="/tables")
  Endpoint: POST /tables/{physical_table_id}/start-service
  
@router.get("/overview", prefix="/tables")
  Endpoint: GET /tables/overview (frontend doesn't use this)
```

---

## 3. Table Groups API

### Frontend Expectations
```typescript
GET /table-groups/open
GET /table-groups/{id}
POST /table-groups/{id}/request-bill
POST /table-groups/{id}/mark-paid
POST /table-groups/{id}/close
POST /table-groups/{id}/tables/add
POST /table-groups/{id}/tables/remove
POST /table-groups/{id}/switch
POST /table-groups/merge
POST /table-groups/{id}/split
```

### Backend Implementation
✅ **MATCH - ALL ENDPOINTS IMPLEMENTED**
```python
@router.get("/open", prefix="/table-groups")
@router.get("/{table_group_id}", prefix="/table-groups")
@router.post("/{table_group_id}/request-bill", prefix="/table-groups")
@router.post("/{table_group_id}/mark-paid", prefix="/table-groups")
@router.post("/{table_group_id}/close", prefix="/table-groups")
@router.post("/{table_group_id}/tables/add", prefix="/table-groups")
@router.post("/{table_group_id}/tables/remove", prefix="/table-groups")
@router.post("/{table_group_id}/switch", prefix="/table-groups")
@router.post("/merge", prefix="/table-groups")
@router.post("/{table_group_id}/split", prefix="/table-groups")
```

### Additional Backend Endpoints (not used by frontend)
```python
@router.get("/{table_group_id}/bill", prefix="/table-groups")
@router.get("/{table_group_id}/order-items", prefix="/table-groups")
@router.post("/{table_group_id}/bill-adjustments", prefix="/table-groups")
```

---

## 4. Orders API

### Frontend Expectations
```typescript
POST /tables/{tableId}/orders/confirm
```

### Backend Implementation
✅ **MATCH**
```python
@router.post("/{physical_table_id}/orders/confirm", prefix="/tables")
  Endpoint: POST /tables/{physical_table_id}/orders/confirm
```

---

## 5. Order Items API

### Frontend Expectations
```typescript
POST /order-items/{id}/void
POST /order-items/{id}/mark-served
POST /order-items/{id}/reprint
```

### Backend Implementation
✅ **MATCH**
```python
@router.post("/{order_item_id}/void", prefix="/order-items")
@router.post("/{order_item_id}/mark-served", prefix="/order-items")
@router.post("/{order_item_id}/reprint", prefix="/order-items")
```

---

## 6. Menu Items API

### Frontend Expectations (Currently Demo Only)
```typescript
GET /menu-items
POST /menu-items
PATCH /menu-items/{id}
POST /menu-items/{id}/retire
POST /menu-items/{id}/image
```

### Backend Implementation
✅ **MATCH**
```python
@router.get("", prefix="/menu-items")
  Endpoint: GET /menu-items
  
@router.post("", prefix="/menu-items")
  Endpoint: POST /menu-items
  
@router.patch("/{menu_item_id}", prefix="/menu-items")
  Endpoint: PATCH /menu-items/{menu_item_id}
  
@router.post("/{menu_item_id}/retire", prefix="/menu-items")
  Endpoint: POST /menu-items/{menu_item_id}/retire
  
@router.post("/{menu_item_id}/image", prefix="/menu-items")
  Endpoint: POST /menu-items/{menu_item_id}/image
```

**Note**: Frontend currently calls demo API only. Not integrated with live backend yet.

---

## 7. Audit Events API

### Frontend
⚠️ **NOT USED**

### Backend Implementation
```python
@router.get("", prefix="/audit-events")
  Endpoint: GET /audit-events
  Parameters: event_type, entity_type, entity_id, actor_user_id, limit, offset
```

---

## 8. Waiters API

### Frontend Expectations
```typescript
GET /waiters (used in WaiterManagementView)
```

### Backend Implementation
❌ **MISSING - NOT IMPLEMENTED**

The frontend expects a `/waiters` endpoint but it's not defined in the backend routers.

**Impact**: `GET /waiters` returns 404 error in live mode

---

## Summary

| API Group | Status | Notes |
|-----------|--------|-------|
| Authentication | ✅ OK | Login endpoint working |
| Physical Tables | ✅ OK | All required endpoints present |
| Table Groups | ✅ OK | All required endpoints present |
| Orders | ✅ OK | Confirm endpoint working |
| Order Items | ✅ OK | Void, mark-served, reprint working |
| Menu Items | ⚠️ Backend Ready | Frontend only uses demo API (needs to be switched to live) |
| Audit Events | ✅ OK | Implemented but not used by frontend |
| Waiters | ❌ MISSING | No endpoint in backend routers |

---

## Issues to Fix

1. **Create `/waiters` endpoint** in backend
   - Frontend requests: `GET /waiters`
   - Expected response: List of waiter objects

2. **Switch demo-only APIs to live mode** in frontend
   - Order Items: All calls use demo only (void, mark-served, reprint)
   - Menu Items: All calls use demo only (list, create, update, retire)
   - Waiters: All calls use demo only (list, create, update)
   - Sessions: Logout uses demo only
   
   Current live APIs:
   - ✅ Authentication (login)
   - ✅ Physical Tables (list, start-service)
   - ✅ Table Groups (all operations)
   - ✅ Orders (confirm)

3. **CORS Configuration** 
   - Ensure backend CORS allows frontend origin (localhost:5173)
   - All endpoints require authentication (Bearer token)

---

## Next Steps

1. ✅ Fix authentication token passing in API requests
2. ❌ Implement missing `/waiters` endpoint in backend
3. ⚠️ Switch menu items calls to live backend
4. Verify all endpoints return proper response types matching frontend expectations
