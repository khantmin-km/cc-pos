<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'

import { getRuntimeMode, onRuntimeModeChange, setRuntimeMode } from '@/services/runtimeMode'
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'
import { useSessionsStore } from '@/stores/sessions'

const route = useRoute()
const router = useRouter()
const mode = ref(getRuntimeMode())
const sessionsStore = useSessionsStore()

onRuntimeModeChange(async (m) => {
  mode.value = m
  await Promise.allSettled([
    tablesStore.fetchTables(),
    groupsStore.fetchOpenGroups(),
  ])
})

const tablesStore = useTablesStore()
const groupsStore = useTableGroupsStore()

onMounted(async () => {
  await Promise.allSettled([tablesStore.fetchTables(), groupsStore.fetchOpenGroups()])
})

const nav = [
  { to: '/admin', label: 'Dashboard' },
  { to: '/admin/table-groups', label: 'Table & Table Group Control' },
  { to: '/admin/orders', label: 'Billing & Orders' },
  { to: '/admin/menu', label: 'Menu Management' },
  { to: '/admin/waiters', label: 'Waiter Management' },
]

const title = computed(() => {
  const m = nav.find((n) => route.path === n.to)
  return m?.label ?? 'Admin'
})

async function handleLogout() {
  try {
    await sessionsStore.logout()
    router.push('/login')
  } catch (e) {
    console.error('Logout error:', e)
    // Force logout even if API fails
    sessionsStore.clearSession()
    router.push('/login')
  }
}
</script>

<template>
  <div class="shell">
    <header class="topbar">
      <div class="brand">
        <span class="name">KAUNG KAUNG</span>
        <span class="pill">ADMIN</span>
      </div>

      <div class="right">
        <button
          type="button"
          class="mode"
          :data-mode="mode"
          @click="setRuntimeMode(mode === 'demo' ? 'live' : 'demo')"
        >
          Mode: {{ mode }}
        </button>
        <button type="button" class="logout" @click="handleLogout">
          Logout
        </button>
      </div>
    </header>

    <div class="content">
      <aside class="sidebar">
        <RouterLink
          v-for="n in nav"
          :key="n.to"
          class="side-item"
          :to="n.to"
        >
          {{ n.label }}
        </RouterLink>
      </aside>

      <main class="main">
        <div class="page-head">
          <h1 class="h1">
            {{ title }}
          </h1>
          <p class="sub">
            Manage your restaurant operations
          </p>
        </div>

        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
  background: #f6f8f7;
}

.topbar {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.name {
  color: #22c55e;
  font-weight: 900;
  letter-spacing: 0.03em;
}

.pill {
  font-size: 12px;
  font-weight: 800;
  color: #16a34a;
  background: #dcfce7;
  border: 1px solid #bbf7d0;
  padding: 2px 8px;
  border-radius: 999px;
}

.right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mode {
  border: 1px solid #e5e7eb;
  background: #fff;
  padding: 6px 10px;
  border-radius: 10px;
  font-weight: 800;
  cursor: pointer;
}

.mode[data-mode='demo'] {
  border-color: #f59e0b;
  color: #92400e;
  background: #fffbeb;
}

.logout {
  border: none;
  background: #ef4444;
  color: white;
  padding: 8px 14px;
  border-radius: 10px;
  font-weight: 900;
  cursor: pointer;
}

.content {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: calc(100vh - 56px);
}

.sidebar {
  background: #f3faf5;
  border-right: 1px solid #e5e7eb;
  padding: 14px 10px;
}

.side-item {
  display: block;
  padding: 10px 12px;
  border-radius: 10px;
  text-decoration: none;
  color: #64748b;
  font-weight: 700;
  font-size: 13px;
}

.side-item.router-link-active {
  color: #16a34a;
  background: #dcfce7;
  border: 1px solid #bbf7d0;
}

.main {
  padding: 22px;
}

.page-head {
  margin-bottom: 18px;
}

.h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 900;
  color: #111827;
}

.sub {
  margin: 6px 0 0;
  color: #6b7280;
  font-weight: 600;
}

@media (max-width: 900px) {
  .content {
    grid-template-columns: 1fr;
  }
  .sidebar {
    display: none;
  }
}
</style>

