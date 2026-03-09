import type { PhysicalTable, TableGroup } from '@/types/pos'

type DemoState = {
  tables: PhysicalTable[]
  groups: TableGroup[]
}

const KEY = 'ccpos_demo_state_v1'

function nowIso() {
  return new Date().toISOString()
}

function load(): DemoState {
  const raw = localStorage.getItem(KEY)
  if (raw) {
    try {
      return JSON.parse(raw) as DemoState
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

  const state: DemoState = { tables, groups: [] }
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

