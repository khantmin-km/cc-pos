/**
 * Vue Router Configuration
 * 
 * Defines routes for the POS application.
 */

import { createRouter, createWebHistory } from 'vue-router'

// View imports - using relative paths
import TableSelectionView from '../views/TableSelectionView.vue'

// Lazy-loaded admin views
const AdminDashboardView = () => import('../views/admin/AdminDashboardView.vue')
const TableGroupControlView = () => import('../views/admin/TableGroupControlView.vue')
const BillingPaymentView = () => import('../views/admin/BillingPaymentView.vue')

/**
 * Route definitions
 */
const routes = [
  {
    path: '/',
    name: 'tables',
    component: TableSelectionView
  },
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: AdminDashboardView
  },
  {
    path: '/admin/table-groups',
    name: 'table-groups',
    component: TableGroupControlView
  },
  {
    path: '/admin/billing',
    name: 'billing',
    component: BillingPaymentView
  }
]

/**
 * Router instance
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
