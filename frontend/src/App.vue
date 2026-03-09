<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <RouterLink class="brand" to="/">
        CC POS
      </RouterLink>
      <nav class="nav">
        <RouterLink class="nav-link" to="/">
          Waiter
        </RouterLink>
        <RouterLink class="nav-link" to="/admin/table-groups">
          Admin: Groups
        </RouterLink>
        <RouterLink class="nav-link" to="/admin/billing">
          Admin: Billing
        </RouterLink>
      </nav>
    </header>

    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: var(--pos-background);
  color: var(--pos-text);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: white;
  border-bottom: 1px solid var(--pos-border);
}

.brand {
  font-weight: 800;
  letter-spacing: 0.02em;
  color: var(--pos-primary);
  text-decoration: none;
}

.nav {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.nav-link {
  color: var(--pos-text);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
}

.nav-link.router-link-active {
  color: var(--pos-primary);
}

.main {
  padding: 1rem;
}
</style>

