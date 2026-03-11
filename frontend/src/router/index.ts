import { createRouter, createWebHistory } from 'vue-router'

import TableSelectionView from '@/views/TableSelectionView.vue'
import PlaceholderView from '@/views/PlaceholderView.vue'
import MenuView from '@/views/MenuView.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import AdminDashboardView from '@/views/admin/AdminDashboardView.vue'
import TableGroupControlView from '@/views/admin/TableGroupControlView.vue'
import BillingPaymentView from '@/views/admin/BillingPaymentView.vue'
import AdminPlaceholderView from '@/views/admin/AdminPlaceholderView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'waiter', component: TableSelectionView },
    { path: '/menu/:tableId', name: 'menu', component: MenuView },
    { path: '/orders/:tableId', name: 'orders', component: PlaceholderView },
    {
      path: '/admin',
      component: AdminLayout,
      children: [
        { path: '', name: 'admin', component: AdminDashboardView },
        { path: 'table-groups', name: 'admin-table-groups', component: TableGroupControlView },
        { path: 'billing', name: 'admin-billing', component: BillingPaymentView },
        {
          path: 'orders',
          name: 'admin-orders',
          component: AdminPlaceholderView,
          props: { title: 'Order Oversight' },
        },
        {
          path: 'kitchen',
          name: 'admin-kitchen',
          component: AdminPlaceholderView,
          props: { title: 'Kitchen & Serving' },
        },
        {
          path: 'menu',
          name: 'admin-menu',
          component: AdminPlaceholderView,
          props: { title: 'Menu Management' },
        },
      ],
    },
  ],
})

export default router

