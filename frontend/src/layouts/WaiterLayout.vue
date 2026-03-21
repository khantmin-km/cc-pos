<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/sessions'

const router = useRouter()
const sessionsStore = useSessionsStore()

async function handleLogout() {
  try {
    await sessionsStore.logout()
  } catch (e) {
    console.error('Logout error:', e)
    sessionsStore.clearSession()
  } finally {
    router.push('/login')
  }
}
</script>

<template>
  <div class="waiter-shell">
    <header class="topbar">
      <div class="brand-wrap">
        <span class="brand">KAUNG KAUNG</span>
        <span class="pill">WAITER</span>
      </div>
      <nav class="nav">
        <RouterLink class="nav-link" to="/waiter">
          Tables
        </RouterLink>
      </nav>
      <button type="button" class="logout" @click="handleLogout">
        Logout
      </button>
    </header>

    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.waiter-shell {
  min-height: 100vh;
  background: var(--pos-background);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: #ffffff;
  border-bottom: 1px solid var(--pos-border);
}

.brand-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand {
  color: var(--pos-primary);
  font-weight: 900;
}

.pill {
  font-size: 12px;
  font-weight: 800;
  color: #166534;
  background: #dcfce7;
  border: 1px solid #bbf7d0;
  border-radius: 999px;
  padding: 2px 8px;
}

.nav {
  flex: 1;
  display: flex;
  justify-content: center;
}

.nav-link {
  text-decoration: none;
  color: #475569;
  font-weight: 700;
  padding: 8px 12px;
  border-radius: 8px;
}

.nav-link.router-link-active {
  color: #0f172a;
  background: #f1f5f9;
}

.logout {
  border: none;
  background: #ef4444;
  color: white;
  padding: 8px 14px;
  border-radius: 10px;
  font-weight: 800;
  cursor: pointer;
}

.main {
  padding: 8px;
}
</style>
