<script setup lang="ts">
import { useRoute } from 'vue-router'

interface NavLink {
  to: string
  label: string
  description: string
}

const links: NavLink[] = [
  {
    to: '/admin/table-groups',
    label: 'Table Groups',
    description: 'Seat management & table merging'
  },
  {
    to: '/admin/billing',
    label: 'Billing & Payments',
    description: 'Invoices, bill requests, and closures'
  }
]

const route = useRoute()

function isActive(path: string) {
  if (path === '/admin/billing') {
    return route.path.startsWith('/admin/billing')
  }
  if (path === '/admin/table-groups') {
    return route.path.startsWith('/admin/table-groups')
  }
  return route.path === path
}
</script>

<template>
  <nav class="admin-nav">
    <RouterLink
      v-for="link in links"
      :key="link.to"
      :to="link.to"
      class="nav-link"
      :class="{ active: isActive(link.to) }"
    >
      <span class="link-label">{{ link.label }}</span>
      <span class="link-description">{{ link.description }}</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.admin-nav {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.nav-link {
  border: 1px solid var(--pos-border);
  border-radius: 10px;
  padding: 1rem;
  background: white;
  text-decoration: none;
  color: var(--pos-text);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.nav-link:hover {
  border-color: var(--pos-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.nav-link.active {
  border-color: var(--pos-primary);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.2);
}

.link-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.link-description {
  font-size: 0.85rem;
  color: var(--pos-text-muted);
}
</style>
