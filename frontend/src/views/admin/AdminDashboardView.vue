<script setup lang="ts">
/**
 * Admin Dashboard View
 * 
 * Displays:
 * - Sales trend data (weekly/monthly)
 * - Item sales analysis
 * - Order statistics
 * - Key metrics and KPIs
 */

import { ref, computed, onMounted } from 'vue'
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'

// --------------------------------
// Setup
// --------------------------------

const tablesStore = useTablesStore()
const tableGroupsStore = useTableGroupsStore()

// --------------------------------
// State
// --------------------------------

/** Filter period */
const filterPeriod = ref<'weekly' | 'monthly'>('weekly')

/** Sales data */
const salesData = ref<Array<{ date: string; sales: number }>>([])

/** Item sales data */
const itemSalesData = ref<Array<{ name: string; count: number; revenue: number }>>([])

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  await tablesStore.fetchTables()
  await tableGroupsStore.fetchOpenGroups()
  // TODO: Load real sales data from backend
  updateChart()
})

// --------------------------------
// Computed
// --------------------------------

const tables = computed(() => tablesStore.tables || [])

const occupiedTableCount = computed(() => {
  return tables.value.filter(t => t.status === 'occupied').length
})

const availableTableCount = computed(() => {
  return tables.value.filter(t => t.status === 'available').length
})

const totalOrders = computed(() => {
  // TODO: Calculate from real order data
  return 0
})

const totalRevenue = computed(() => {
  // TODO: Calculate from real order data
  return 0
})

const topItems = computed(() => {
  return itemSalesData.value.slice(0, 5)
})

// --------------------------------
// Methods
// --------------------------------

/**
 * Generate demo sales data
 */
function generateDemoData() {
  // Generate weekly data
  const weeklyData = []
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    weeklyData.push({
      date: date.toLocaleDateString('en-US', { weekday: 'short' }),
      sales: Math.floor(Math.random() * 50000) + 30000,
    })
  }
  
  // Generate monthly data
  const monthlyData = []
  for (let i = 11; i >= 0; i--) {
    const date = new Date()
    date.setMonth(date.getMonth() - i)
    monthlyData.push({
      date: date.toLocaleDateString('en-US', { month: 'short' }),
      sales: Math.floor(Math.random() * 500000) + 300000,
    })
  }
  
  salesData.value = filterPeriod.value === 'weekly' ? weeklyData : monthlyData
  
  // Item sales data
  itemSalesData.value = [
    { name: 'Pad Thai', count: 45, revenue: 4500 },
    { name: 'Green Curry', count: 38, revenue: 4560 },
    { name: 'Tom Yum Soup', count: 52, revenue: 3640 },
    { name: 'Spring Rolls', count: 67, revenue: 2010 },
    { name: 'Mango Sticky Rice', count: 41, revenue: 2870 },
    { name: 'Thai Iced Tea', count: 89, revenue: 1780 },
  ]
}

/**
 * Update chart based on filter
 */
function updateChart() {
  // TODO: Load real sales data from backend based on filterPeriod
  // For now, show empty data
  salesData.value = []
  itemSalesData.value = []
}

/**
 * Get max sales value for scaling
 */
function getMaxSales(): number {
  return Math.max(...salesData.value.map(d => d.sales), 100000)
}

/**
 * Get bar height percentage
 */
function getBarHeightPercent(sales: number): number {
  return (sales / getMaxSales()) * 100
}

</script>

<template>
  <div class="admin-dashboard-view">
    <!-- Header -->
    <div class="header">
      <h1>Dashboard</h1>
      <p class="subtitle">Sales and Order Management Overview</p>
    </div>

    <!-- Key Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">🪑</div>
        <div class="metric-content">
          <p class="metric-label">Occupied Tables</p>
          <p class="metric-value">{{ occupiedTableCount }}</p>
          <p class="metric-detail">Active</p>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">✨</div>
        <div class="metric-content">
          <p class="metric-label">Available Tables</p>
          <p class="metric-value">{{ availableTableCount }}</p>
          <p class="metric-detail">Ready</p>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">📦</div>
        <div class="metric-content">
          <p class="metric-label">Total Orders</p>
          <p class="metric-value">{{ totalOrders }}</p>
          <p class="metric-detail">Items</p>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-icon">💰</div>
        <div class="metric-content">
          <p class="metric-label">Today's Revenue</p>
          <p class="metric-value">${{ totalRevenue.toFixed(0) }}</p>
          <p class="metric-detail">Total</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="content-grid">
      <!-- Sales Trend Chart -->
      <div class="chart-section sales-trends">
        <div class="section-header">
          <h2>Sales Trends</h2>
          <div class="filter-buttons">
            <button
              :class="{ active: filterPeriod === 'weekly' }"
              @click="filterPeriod = 'weekly'; updateChart()"
              class="btn-filter"
            >
              Weekly
            </button>
            <button
              :class="{ active: filterPeriod === 'monthly' }"
              @click="filterPeriod = 'monthly'; updateChart()"
              class="btn-filter"
            >
              Monthly
            </button>
          </div>
        </div>

        <div class="chart-container">
          <div class="chart bar-chart">
            <div class="chart-bars">
              <div v-for="(item, index) in salesData" :key="index" class="bar-group">
                <div class="bar-container">
                  <div
                    class="bar"
                    :style="{ height: getBarHeightPercent(item.sales) + '%' }"
                  >
                    <span class="bar-value">${{ (item.sales / 1000).toFixed(0) }}k</span>
                  </div>
                </div>
                <span class="bar-label">{{ item.date }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="chart-stats">
          <div class="stat">
            <span class="stat-label">Average:</span>
            <span class="stat-value">
              ${{ (salesData.reduce((sum, d) => sum + d.sales, 0) / salesData.length / 1000).toFixed(1) }}k
            </span>
          </div>
          <div class="stat">
            <span class="stat-label">Total:</span>
            <span class="stat-value">
              ${{ (salesData.reduce((sum, d) => sum + d.sales, 0) / 1000).toFixed(1) }}k
            </span>
          </div>
        </div>
      </div>

      <!-- Item Sales Analysis -->
      <div class="chart-section item-analysis">
        <div class="section-header">
          <h2>Top Items</h2>
        </div>

        <div class="items-list">
          <div v-for="item in itemSalesData" :key="item.name" class="item-row">
            <div class="item-info">
              <h4 class="item-name">{{ item.name }}</h4>
              <div class="item-metrics">
                <span class="metric">{{ item.count }} sold</span>
                <span class="metric">${{ item.revenue }}</span>
              </div>
            </div>
            <div class="item-bar">
              <div
                class="progress-bar"
                :style="{ width: (item.count / 100) * 100 + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Orders Today</h3>
        <p class="stat-number">{{ totalOrders }}</p>
      </div>

      <div class="stat-card">
        <h3>Tables In Use</h3>
        <p class="stat-number">{{ occupiedTableCount }}/{{ tables.length }}</p>
      </div>

      <div class="stat-card">
        <h3>Avg. Order Value</h3>
        <p class="stat-number">${{ totalOrders > 0 ? (totalRevenue / totalOrders).toFixed(2) : '0.00' }}</p>
      </div>

      <div class="stat-card">
        <h3>Service Rate</h3>
        <p class="stat-number">{{ tables.length > 0 ? Math.round((occupiedTableCount / tables.length) * 100) : 0 }}%</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-dashboard-view {
  background: #f9fafb;
  min-height: 100vh;
  padding: 30px;
  overflow-y: auto;
}

.header {
  margin-bottom: 30px;
}

.header h1 {
  margin: 0 0 5px 0;
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
}

.subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.metric-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3b82f6;
}

.metric-icon {
  font-size: 32px;
}

.metric-content {
  flex: 1;
}

.metric-label {
  margin: 0;
  font-size: 12px;
  color: #9ca3af;
  text-transform: uppercase;
  font-weight: 600;
}

.metric-value {
  margin: 5px 0;
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}

.metric-detail {
  margin: 0;
  font-size: 12px;
  color: #6b7280;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 40px;
}

.chart-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.section-header h2 {
  margin: 0;
  font-size: 18px;
  color: #1f2937;
}

.filter-buttons {
  display: flex;
  gap: 8px;
}

.btn-filter {
  padding: 6px 14px;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-filter:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.btn-filter.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

/* Chart */
.chart-container {
  margin-bottom: 20px;
}

.bar-chart {
  background: #f9fafb;
  border-radius: 8px;
  padding: 20px;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 250px;
  gap: 15px;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.bar-container {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  position: relative;
}

.bar {
  width: 80%;
  background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%);
  border-radius: 6px 6px 0 0;
  min-height: 20px;
  position: relative;
  transition: all 0.3s;
}

.bar:hover {
  background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.bar-value {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
}

.bar-label {
  font-size: 12px;
  color: #6b7280;
  margin-top: 10px;
  font-weight: 500;
}

.chart-stats {
  display: flex;
  gap: 30px;
  padding-top: 15px;
  border-top: 1px solid #e5e7eb;
}

.stat {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.stat-label {
  color: #6b7280;
  font-size: 13px;
}

.stat-value {
  font-weight: 700;
  color: #1f2937;
}

/* Item Analysis */
.items-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.item-row {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
}

.item-info {
  margin-bottom: 10px;
}

.item-name {
  margin: 0 0 6px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.item-metrics {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #6b7280;
}

.metric {
  display: flex;
  gap: 4px;
}

.item-bar {
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
  transition: width 0.3s;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-card h3 {
  margin: 0 0 10px 0;
  font-size: 13px;
  color: #6b7280;
  text-transform: uppercase;
  font-weight: 600;
}

.stat-number {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: #3b82f6;
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .chart-bars {
    height: 200px;
  }

  .bar-container {
    height: 150px;
  }
}

@media (max-width: 768px) {
  .admin-dashboard-view {
    padding: 15px;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }

  .metric-card {
    flex-direction: column;
    text-align: center;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .chart-bars {
    flex-wrap: wrap;
    gap: 10px;
  }

  .bar-group {
    flex: 0 0 calc(50% - 5px);
  }
}
</style>
