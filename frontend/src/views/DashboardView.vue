<script setup lang="ts">
/**
 * Dashboard View (Admin)
 * 
 * Shows sales trends and analytics.
 * Admin can:
 * - View sales data trends
 * - Filter by weekly/monthly
 * - See item sales statistics
 */

// Vue imports
import {
  ref,
  computed,
  onMounted,
} from 'vue'

// Router imports
import { useRouter } from 'vue-router'

// Store imports
import { useOrdersStore } from '@/stores/orders'
import { useTableGroupsStore } from '@/stores/tableGroups'

// Type imports
import type { OrderItem } from '@/types/pos'

// --------------------------------
// Setup
// --------------------------------

const router = useRouter()

// Initialize stores
const ordersStore = useOrdersStore()
const tableGroupsStore = useTableGroupsStore()

// State
const loading = ref(false)
const error = ref<string | null>(null)
const selectedPeriod = ref<'weekly' | 'monthly'>('weekly')

// Computed properties
const allOrderItems = computed(() => ordersStore.orderItems)

// Calculate sales data based on selected period
const salesData = computed(() => {
  const now = new Date()
  const items = allOrderItems.value.filter(item => !item.removed)
  
  if (selectedPeriod.value === 'weekly') {
    // Last 7 days
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    return items.filter(item => {
      const itemDate = new Date(item.created_at || Date.now())
      return itemDate >= weekAgo
    })
  } else {
    // Last 30 days
    const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
    return items.filter(item => {
      const itemDate = new Date(item.created_at || Date.now())
      return itemDate >= monthAgo
    })
  }
})

// Calculate total sales
const totalSales = computed(() => {
  return salesData.value.reduce((total, item) => {
    return total + (Number(item.unit_price_snap || 0) * item.quantity)
  }, 0)
})

// Group sales by menu item
const itemSales = computed(() => {
  const sales: Record<string, { quantity: number; revenue: number }> = {}
  
  salesData.value.forEach(item => {
    const key = item.menu_item_name_snap || `Item ${item.menuItemId}`
    if (!sales[key]) {
      sales[key] = { quantity: 0, revenue: 0 }
    }
    sales[key].quantity += item.quantity
    sales[key].revenue += Number(item.unit_price_snap || 0) * item.quantity
  })
  
  return Object.entries(sales)
    .map(([name, data]) => ({ name, ...data }))
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, 10) // Top 10 items
})

// Generate chart data points
const chartData = computed(() => {
  if (selectedPeriod.value === 'weekly') {
    // Group by day for last 7 days
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    return days.map((day, index) => {
      const dayStart = new Date()
      dayStart.setDate(dayStart.getDate() - (6 - index))
      dayStart.setHours(0, 0, 0, 0)
      
      const daySales = salesData.value.filter(item => {
        const itemDate = new Date(item.created_at || Date.now())
        return itemDate.toDateString() === dayStart.toDateString()
      })
      
      const dayTotal = daySales.reduce((sum, item) => 
        sum + (Number(item.unit_price_snap || 0) * item.quantity), 0
      )
      
      return {
        day,
        sales: dayTotal,
        orders: daySales.length
      }
    })
  } else {
    // Group by week for last 4 weeks
    const weeks = []
    for (let i = 3; i >= 0; i--) {
      const weekStart = new Date()
      weekStart.setDate(weekStart.getDate() - (i * 7))
      weekStart.setHours(0, 0, 0, 0)
      
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekEnd.getDate() + 6)
      
      const weekSales = salesData.value.filter(item => {
        const itemDate = new Date(item.created_at || Date.now())
        return itemDate >= weekStart && itemDate <= weekEnd
      })
      
      const weekTotal = weekSales.reduce((sum, item) => 
        sum + (Number(item.unit_price_snap || 0) * item.quantity), 0
      )
      
      weeks.push({
        week: `Week ${4 - i}`,
        sales: weekTotal,
        orders: weekSales.length
      })
    }
    return weeks
  }
})

// --------------------------------
// Event Handlers
// --------------------------------

function handleBackToMain() {
  router.push('/admin')
}

function handlePeriodChange(period: 'weekly' | 'monthly') {
  selectedPeriod.value = period
}

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  try {
    loading.value = true
    
    // Load data
    await Promise.all([
      ordersStore.fetchOrderItems('all'), // This would need a proper endpoint
      tableGroupsStore.fetchOpenGroups(),
    ])
    
  } catch (e) {
    error.value = 'Failed to load dashboard data'
    console.error('Load failed:', e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="dashboard-view">
    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <h1>📊 Dashboard</h1>
        <p>Sales trends and analytics</p>
        <button class="nav-btn" @click="handleBackToMain">
          ← Back to Main
        </button>
      </div>
    </header>

    <!-- Period Selector -->
    <div class="period-selector">
      <h2>📅 Sales Period</h2>
      <div class="period-buttons">
        <button 
          class="period-btn"
          :class="{ active: selectedPeriod === 'weekly' }"
          @click="handlePeriodChange('weekly')"
        >
          📅 Weekly
        </button>
        <button 
          class="period-btn"
          :class="{ active: selectedPeriod === 'monthly' }"
          @click="handlePeriodChange('monthly')"
        >
          📅 Monthly
        </button>
      </div>
    </div>

    <!-- Error Banner -->
    <div v-if="error" class="error-banner">
      {{ error }}
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading dashboard data...</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else class="content">
      <!-- Stats Overview -->
      <div class="stats-overview">
        <div class="stat-card">
          <h3>💰 Total Sales</h3>
          <div class="stat-value">${{ totalSales.toFixed(2) }}</div>
          <div class="stat-period">{{ selectedPeriod === 'weekly' ? 'Last 7 Days' : 'Last 30 Days' }}</div>
        </div>
        
        <div class="stat-card">
          <h3>📝 Total Orders</h3>
          <div class="stat-value">{{ salesData.length }}</div>
          <div class="stat-period">{{ selectedPeriod === 'weekly' ? 'Last 7 Days' : 'Last 30 Days' }}</div>
        </div>
        
        <div class="stat-card">
          <h3>🍽 Items Sold</h3>
          <div class="stat-value">{{ salesData.reduce((sum, item) => sum + item.quantity, 0) }}</div>
          <div class="stat-period">{{ selectedPeriod === 'weekly' ? 'Last 7 Days' : 'Last 30 Days' }}</div>
        </div>
      </div>

      <!-- Sales Chart -->
      <div class="chart-section">
        <h2>📈 Sales Trend</h2>
        <div class="chart-container">
          <div class="chart-bars">
            <div 
              v-for="(data, index) in chartData" 
              :key="data.day || data.week"
              class="chart-bar"
            >
              <div class="bar-info">
                <span class="bar-label">{{ data.day || data.week }}</span>
                <span class="bar-value">${{ data.sales.toFixed(2) }}</span>
              </div>
              <div 
                class="bar-fill" 
                :style="{ height: `${Math.max(10, (data.sales / Math.max(...chartData.map(d => d.sales))) * 100)}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Top Items -->
      <div class="top-items-section">
        <h2>🏆 Top Selling Items</h2>
        <div class="items-grid">
          <div 
            v-for="(item, index) in itemSales" 
            :key="item.name"
            class="item-card"
          >
            <div class="item-rank">#{{ index + 1 }}</div>
            <div class="item-info">
              <div class="item-name">{{ item.name }}</div>
              <div class="item-stats">
                <span class="stat">📝 {{ item.quantity }} sold</span>
                <span class="stat">💰 ${{ item.revenue.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.header {
  margin-bottom: 30px;
}

.header-content {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  margin: 0 0 16px 0;
  color: #1f2937;
  font-size: 28px;
  font-weight: 700;
}

.header-content p {
  margin: 0 0 20px 0;
  color: #6b7280;
  font-size: 16px;
}

.nav-btn {
  padding: 10px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: #2563eb;
}

.period-selector {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.period-selector h2 {
  margin: 0 0 16px 0;
  color: #1f2937;
  font-size: 20px;
  font-weight: 700;
}

.period-buttons {
  display: flex;
  gap: 12px;
}

.period-btn {
  padding: 12px 24px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.period-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.error-banner {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
}

.loading-state {
  text-align: center;
  padding: 40px;
  color: white;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { border-top-color: #3b82f6; }
  100% { border-top-color: #1f2937; }
}

.content {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 12px 0;
  color: #6b7280;
  font-size: 14px;
  font-weight: 600;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.stat-period {
  font-size: 12px;
  color: #9ca3af;
}

.chart-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.chart-section h2 {
  margin: 0 0 20px 0;
  color: #1f2937;
  font-size: 20px;
  font-weight: 700;
}

.chart-container {
  height: 300px;
}

.chart-bars {
  display: flex;
  align-items: end;
  height: 100%;
  gap: 8px;
}

.chart-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.bar-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 8px;
  z-index: 2;
}

.bar-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 600;
}

.bar-value {
  font-size: 14px;
  font-weight: 700;
  color: #1f2937;
}

.bar-fill {
  width: 100%;
  background: linear-gradient(to top, #3b82f6, #3b82f6);
  border-radius: 4px 4px 0 0;
  transition: height 0.3s ease;
  min-height: 10px;
}

.top-items-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.top-items-section h2 {
  margin: 0 0 20px 0;
  color: #1f2937;
  font-size: 20px;
  font-weight: 700;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.item-card {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #f9fafb;
  transition: transform 0.2s;
}

.item-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.item-rank {
  width: 40px;
  height: 40px;
  background: #fbbf24;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  margin-right: 16px;
}

.item-info {
  flex: 1;
}

.item-name {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
  font-size: 16px;
}

.item-stats {
  display: flex;
  gap: 16px;
}

.item-stats .stat {
  font-size: 14px;
  color: #6b7280;
}

@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .chart-bars {
    flex-direction: column;
    gap: 4px;
  }
  
  .items-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .item-stats {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
