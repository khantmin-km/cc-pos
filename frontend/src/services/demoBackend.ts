import type {
  PhysicalTable,
  TableGroup,
  MenuItem,
  Waiter,
  Order,
  OrderItem,
  ActorSession,
  BillBreakdown,
  BillAdjustment,
} from '@/types/pos'

type DemoState = {
  tables: PhysicalTable[]
  groups: TableGroup[]
  menuItems: MenuItem[]
  waiters: Waiter[]
  orders: Order[]
  orderItems: OrderItem[]
  sessions: ActorSession[]
  billAdjustments: BillAdjustment[]
}

const KEY = 'ccpos_demo_state_v1'
const DEMO_WAITER_ID = 'demo-waiter'
const DEMO_WAITER_NAME = 'Demo Waiter'

function nowIso() {
  return new Date().toISOString()
}

function normalizeState(input: Partial<DemoState>): DemoState {
  const state: DemoState = {
    tables: input.tables ?? [],
    groups: input.groups ?? [],
    menuItems: input.menuItems ?? [],
    waiters: input.waiters ?? [],
    orders: input.orders ?? [],
    orderItems: input.orderItems ?? [],
    sessions: input.sessions ?? [],
    billAdjustments: input.billAdjustments ?? [],
  }

  // Guarantee one built-in waiter so login always has an option.
  const hasDemoWaiter = state.waiters.some((w) => w.id === DEMO_WAITER_ID)
  if (!hasDemoWaiter) {
    state.waiters.unshift({
      id: DEMO_WAITER_ID,
      name: DEMO_WAITER_NAME,
      active: true,
      createdAt: nowIso(),
    })
  }

  return state
}

function load(): DemoState {
  const raw = localStorage.getItem(KEY)
  if (raw) {
    try {
      const parsed = JSON.parse(raw) as Partial<DemoState>
      const normalized = normalizeState(parsed)
      save(normalized)
      return normalized
    } catch {
      // fall through
    }
  }

  const tables: PhysicalTable[] = Array.from({ length: 12 }).map((_, i) => {
    const n = i + 1
    return {
      id: crypto.randomUUID(),
      table_code: `T-${n}`,
      current_table_group_id: null,
    }
  })

  const menuItems: MenuItem[] = [
    { id: crypto.randomUUID(), name: 'Pad Thai', price: 120, category: 'Noodles', available: true },
    { id: crypto.randomUUID(), name: 'Green Curry', price: 150, category: 'Curry', available: true },
    { id: crypto.randomUUID(), name: 'Tom Yum Soup', price: 100, category: 'Soup', available: true },
    { id: crypto.randomUUID(), name: 'Spring Rolls', price: 80, category: 'Appetizer', available: true },
    { id: crypto.randomUUID(), name: 'Fried Rice', price: 110, category: 'Rice', available: true },
  ]

  const waiters: Waiter[] = [
    { id: DEMO_WAITER_ID, name: DEMO_WAITER_NAME, active: true, createdAt: nowIso() },
  ]

  const state = normalizeState({
    tables,
    groups: [],
    menuItems,
    waiters,
    orders: [],
    orderItems: [],
    sessions: [],
    billAdjustments: [],
  })
  save(state)
  return state
}

function save(state: DemoState) {
  localStorage.setItem(KEY, JSON.stringify(state))
}

export const demoTablesApi = {
  list: async (): Promise<PhysicalTable[]> => {
    return load().tables
  },

  startService: async (physicalTableId: string): Promise<TableGroup> => {
    const state = load()
    const table = state.tables.find((t) => t.id === physicalTableId)
    if (!table) {
      throw new Error('Table not found (demo)')
    }
    if (table.current_table_group_id) {
      throw new Error('Table already occupied (demo)')
    }

    const group: TableGroup = {
      id: crypto.randomUUID(),
      state: 'open',
      physical_table_ids: [table.id],
      opened_at: nowIso(),
      closed_at: null,
    }

    table.current_table_group_id = group.id
    state.groups.unshift(group)
    save(state)
    return group
  },
}

export const demoTableGroupsApi = {
  listOpen: async (): Promise<TableGroup[]> => {
    const state = load()
    return state.groups.filter((g) => g.state !== 'closed')
  },

  get: async (id: string): Promise<TableGroup> => {
    const state = load()
    const g = state.groups.find((x) => x.id === id)
    if (!g) throw new Error('Group not found (demo)')
    return g
  },

  requestBill: async (id: string): Promise<void> => {
    const state = load()
    const g = state.groups.find((x) => x.id === id)
    if (!g) throw new Error('Group not found (demo)')
    g.state = 'bill_requested'
    save(state)
  },

  markPaid: async (id: string): Promise<void> => {
    const state = load()
    const g = state.groups.find((x) => x.id === id)
    if (!g) throw new Error('Group not found (demo)')
    g.state = 'paid'
    save(state)
  },

  close: async (id: string): Promise<void> => {
    const state = load()
    const g = state.groups.find((x) => x.id === id)
    if (!g) throw new Error('Group not found (demo)')
    g.state = 'closed'
    g.closed_at = nowIso()
    // unassign tables
    for (const tid of g.physical_table_ids) {
      const t = state.tables.find((x) => x.id === tid)
      if (t) t.current_table_group_id = null
    }
    save(state)
  },

  addTable: async (groupId: string, physicalTableId: string): Promise<void> => {
    const state = load()
    const g = state.groups.find((x) => x.id === groupId)
    const t = state.tables.find((x) => x.id === physicalTableId)
    if (!g) throw new Error('Group not found (demo)')
    if (!t) throw new Error('Table not found (demo)')
    if (t.current_table_group_id && t.current_table_group_id !== groupId) {
      throw new Error('Table belongs to another group (demo)')
    }
    if (!g.physical_table_ids.includes(t.id)) g.physical_table_ids.push(t.id)
    t.current_table_group_id = groupId
    save(state)
  },

  removeTable: async (groupId: string, physicalTableId: string): Promise<void> => {
    const state = load()
    const g = state.groups.find((x) => x.id === groupId)
    const t = state.tables.find((x) => x.id === physicalTableId)
    if (!g) throw new Error('Group not found (demo)')
    if (!t) throw new Error('Table not found (demo)')
    g.physical_table_ids = g.physical_table_ids.filter((id) => id !== t.id)
    t.current_table_group_id = null
    save(state)
  },

  switchTable: async (
    groupId: string,
    fromTableId: string,
    toTableId: string
  ): Promise<void> => {
    const state = load()
    const g = state.groups.find((x) => x.id === groupId)
    if (!g) throw new Error('Group not found (demo)')
    await demoTableGroupsApi.removeTable(groupId, fromTableId)
    await demoTableGroupsApi.addTable(groupId, toTableId)
  },

  merge: async (sourceId: string, targetId: string): Promise<void> => {
    const state = load()
    const src = state.groups.find((x) => x.id === sourceId)
    const dst = state.groups.find((x) => x.id === targetId)
    if (!src || !dst) throw new Error('Group not found (demo)')
    for (const tid of src.physical_table_ids) {
      await demoTableGroupsApi.addTable(targetId, tid)
    }
    src.state = 'closed'
    src.closed_at = nowIso()
    save(state)
  },

  split: async (id: string, physicalTableIds: string[]): Promise<TableGroup> => {
    const state = load()
    const g = state.groups.find((x) => x.id === id)
    if (!g) throw new Error('Group not found (demo)')

    const move = new Set(physicalTableIds)
    const kept = g.physical_table_ids.filter((tid) => !move.has(tid))
    const moved = g.physical_table_ids.filter((tid) => move.has(tid))
    if (moved.length === 0) throw new Error('No tables selected (demo)')
    g.physical_table_ids = kept

    const newGroup: TableGroup = {
      id: crypto.randomUUID(),
      state: 'open',
      physical_table_ids: moved,
      opened_at: nowIso(),
      closed_at: null,
    }
    state.groups.unshift(newGroup)
    for (const tid of moved) {
      const t = state.tables.find((x) => x.id === tid)
      if (t) t.current_table_group_id = newGroup.id
    }
    save(state)
    return newGroup
  },
}

// Menu Items
export const demoMenuItemsApi = {
  list: async (): Promise<MenuItem[]> => {
    return load().menuItems.filter((m) => m.available)
  },

  create: async (name: string, price: number, category: string): Promise<MenuItem> => {
    const state = load()
    const item: MenuItem = {
      id: crypto.randomUUID(),
      name,
      price,
      category,
      available: true,
    }
    state.menuItems.push(item)
    save(state)
    return item
  },

  update: async (id: string, name: string, price: number, category: string): Promise<MenuItem> => {
    const state = load()
    const item = state.menuItems.find((m) => m.id === id)
    if (!item) throw new Error('Menu item not found (demo)')
    item.name = name
    item.price = price
    item.category = category
    save(state)
    return item
  },

  uploadImage: async (id: string, file: File): Promise<MenuItem> => {
    const state = load()
    const item = state.menuItems.find((m) => m.id === id)
    if (!item) throw new Error('Menu item not found (demo)')

    const dataUrl = await new Promise<string>((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = () => reject(new Error('Failed to read image file'))
      reader.readAsDataURL(file)
    })

    item.image = dataUrl
    save(state)
    return item
  },

  retire: async (id: string): Promise<void> => {
    const state = load()
    const item = state.menuItems.find((m) => m.id === id)
    if (!item) throw new Error('Menu item not found (demo)')
    item.available = false
    save(state)
  },
}

// Waiters
export const demoWaitersApi = {
  list: async (): Promise<Waiter[]> => {
    return load().waiters
  },

  create: async (name: string): Promise<Waiter> => {
    const state = load()
    const waiter: Waiter = {
      id: crypto.randomUUID(),
      name,
      active: true,
      createdAt: nowIso(),
    }
    state.waiters.push(waiter)
    save(state)
    return waiter
  },

  update: async (id: string, name: string, active: boolean): Promise<Waiter> => {
    const state = load()
    const waiter = state.waiters.find((w) => w.id === id)
    if (!waiter) throw new Error('Waiter not found (demo)')
    waiter.name = name
    waiter.active = active
    save(state)
    return waiter
  },
}

// Sessions (Demo)
export const demoSessionsApi = {
  create: async (role: string, actorId: string): Promise<ActorSession> => {
    const state = load()
    const session: ActorSession = {
      id: crypto.randomUUID(),
      actorType: role as 'waiter' | 'admin',
      actorId,
      actorName: role === 'admin' ? 'Admin User' : state.waiters.find((w) => w.id === actorId)?.name || 'Unknown',
      token: crypto.randomUUID(),
      startedAt: nowIso(),
    }
    state.sessions.push(session)
    save(state)
    return session
  },

  end: async (sessionId: string): Promise<void> => {
    const state = load()
    state.sessions = state.sessions.filter((s) => s.id !== sessionId)
    save(state)
  },
}

// Orders (Demo)
export const demoOrdersApi = {
  confirm: async (tableGroupId: string, request?: any) => {
    const state = load()
    const order: Order = {
      id: crypto.randomUUID(),
      tableId: '',
      tableGroupId,
      createdAt: nowIso(),
      items: [],
    }
    state.orders.push(order)
    save(state)
    return {
      orderId: order.id,
      orderItemIds: [],
      tableGroupId,
    }
  },
}

// Order Items (Demo)
export const demoOrderItemsApi = {
  void: async (orderItemId: string): Promise<void> => {
    // Demo only
  },

  markServed: async (orderItemId: string): Promise<void> => {
    // Demo only
  },

  reprint: async (orderItemId: string): Promise<void> => {
    // Just a no-op in demo
  },
}

// Billing (Demo)
export const demoBillingApi = {
  getBillBreakdown: async (tableGroupId: string) => {
    return {
      tableGroupId,
      items: [],
      subtotal: 0,
      tax: 0,
      serviceCharge: 0,
      adjustments: [],
      total: 0,
    }
  },

  createAdjustment: async (tableGroupId: string, description: string, amount: number): Promise<BillAdjustment> => {
    const state = load()
    const adjustment: BillAdjustment = {
      id: crypto.randomUUID(),
      description,
      amount,
      reason: 'admin',
      category: amount > 0 ? 'surcharge' : 'discount',
      createdBy: 'admin',
      createdAt: nowIso(),
    }
    state.billAdjustments.push(adjustment)
    save(state)
    return adjustment
  },
}

