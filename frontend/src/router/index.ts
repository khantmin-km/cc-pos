import { createRouter, createWebHistory } from 'vue-router'
import { useSessionsStore } from '@/stores/sessions'
import LoginView from '@/views/LoginView.vue'
import WaiterLayout from '@/layouts/WaiterLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import WaiterTablesView from '@/views/WaiterTablesView.vue'
import MenuOrderView from '@/views/MenuOrderView.vue'
import OrderItemsView from '@/views/OrderItemsView.vue'
import AdminDashboardView from '@/views/admin/AdminDashboardView.vue'
import AdminTablesManagementView from '@/views/admin/AdminTablesManagementView.vue'
import AdminBillingView from '@/views/admin/AdminBillingView.vue'
import TableGroupControlView from '@/views/admin/TableGroupControlView.vue'
import MenuManagementView from '@/views/admin/MenuManagementView.vue'
import WaiterManagementView from '@/views/admin/WaiterManagementView.vue'
import BillingOrdersView from '@/views/admin/BillingOrdersView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: LoginView, meta: { requiresAuth: false } },
    { path: '/', redirect: '/waiter' },
    { path: '/menu/:tableId', redirect: (to) => `/waiter/menu/${to.params.tableId}` },
    { path: '/orders/:tableId', redirect: (to) => `/waiter/orders/${to.params.tableId}` },
    {
      path: '/waiter',
      component: WaiterLayout,
      meta: { requiresAuth: true, roles: ['waiter'] },
      children: [
        { path: '', name: 'waiter', component: WaiterTablesView, meta: { requiresAuth: true, roles: ['waiter'] } },
        { path: 'menu/:tableId', name: 'waiter-menu', component: MenuOrderView, meta: { requiresAuth: true, roles: ['waiter'] } },
        { path: 'orders/:tableId', name: 'waiter-orders', component: OrderItemsView, meta: { requiresAuth: true, roles: ['waiter'] } },
      ],
    },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true, roles: ['admin'] },
      children: [
        { path: '', name: 'admin', component: AdminDashboardView, meta: { requiresAuth: true, roles: ['admin'] } },
        { path: 'table-groups', name: 'admin-table-groups', component: AdminTablesManagementView, meta: { requiresAuth: true, roles: ['admin'] } },
        { path: 'billing', name: 'admin-billing', component: AdminBillingView, meta: { requiresAuth: true, roles: ['admin'] } },
        { path: 'orders', name: 'admin-orders', component: AdminBillingView, meta: { requiresAuth: true, roles: ['admin'] } },
        { path: 'menu', name: 'admin-menu', component: MenuManagementView, meta: { requiresAuth: true, roles: ['admin'] } },
        { path: 'waiters', name: 'admin-waiters', component: WaiterManagementView, meta: { requiresAuth: true, roles: ['admin'] } },
      ],
    },
  ],
})

// Auth guards disabled - all routes accessible
router.beforeEach((to, from, next) => {
  next()
})

export default router

