<script setup lang="ts">
/**
 * Admin Dashboard View
 *
 * Landing page for administrative tools. Provides quick access to
 * table management and billing workflows.
 */

import { RouterLink } from 'vue-router'

import AdminCard from '@/components/admin/AdminCard.vue'
import AdminNavTabs from '@/components/admin/AdminNavTabs.vue'
</script>

<template>
  <div class="admin-dashboard">
    <header class="dashboard-header">
      <div>
        <p class="eyebrow">Control Center</p>
        <h1>Administrator Access</h1>
        <p class="subtitle">
          Monitor active table groups, manage seating, and process billing
          from a single control surface.
        </p>
      </div>
      <RouterLink to="/" class="back-link">
        ← Return to waiter view
      </RouterLink>
    </header>

    <div class="nav-section">
      <AdminNavTabs />
    </div>

    <div class="dashboard-grid">
      <AdminCard title="Table Group Control">
        <p>
          Create, split, merge, or dissolve table groups. Drag-and-drop tables
          between groups and monitor seating availability.
        </p>
        <RouterLink to="/admin/table-groups" class="action-btn">
          Manage table groups
        </RouterLink>
      </AdminCard>

      <AdminCard title="Billing & Payments">
        <p>
          Review outstanding bills, mark payments, and close groups once all
          charges have been settled.
        </p>
        <RouterLink to="/admin/billing" class="action-btn">
          Open billing panel
        </RouterLink>
      </AdminCard>
    </div>
  </div>
</template>

<style scoped>
.admin-dashboard {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dashboard-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.75rem;
  color: var(--pos-text-muted);
  margin-bottom: 0.25rem;
}

h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: var(--pos-text);
}

.subtitle {
  color: var(--pos-text-muted);
  max-width: 540px;
  line-height: 1.6;
}

.back-link {
  font-size: 0.95rem;
  color: var(--pos-primary);
  text-decoration: none;
  font-weight: 600;
}

.back-link:hover {
  text-decoration: underline;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.25rem;
}

.nav-section {
  margin-bottom: 0.5rem;
}

.dashboard-grid p {
  margin-bottom: 1rem;
  line-height: 1.5;
  color: var(--pos-text-muted);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.25rem;
  background: var(--pos-primary);
  color: white;
  border-radius: 6px;
  font-weight: 600;
  text-decoration: none;
}

.action-btn:hover {
  opacity: 0.9;
}

@media (max-width: 640px) {
  .admin-dashboard {
    padding: 1.5rem 1rem;
  }

  h1 {
    font-size: 1.5rem;
  }
}
</style>
