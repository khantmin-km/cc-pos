<script setup lang="ts">
/**
 * Billing View (Admin)
 * 
 * Shows occupied tables with bill requests.
 * Admin can:
 * - View bills for occupied tables
 * - Print receipts
 * - Close tables
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
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'
import { useOrdersStore } from '@/stores/orders'

// API imports
import { billingApi } from '@/services/tablesApi'

// Type imports
import type { Table, TableGroup } from '@/types/pos'

// --------------------------------
// Setup
// --------------------------------

const router = useRouter()

// Initialize stores
const tablesStore = useTablesStore()
const tableGroupsStore = useTableGroupsStore()
const ordersStore = useOrdersStore()

// State
const loading = ref(false)
const error = ref<string | null>(null)

// Computed properties
const occupiedTables = computed(() => 
  tablesStore.tables.filter(table => table.status === 'occupied')
)

const occupiedTableGroups = computed(() => {
  const groupIds = [...new Set(occupiedTables.value.map(t => t.tableGroupId).filter(Boolean))]
  return groupIds.map(groupId => {
    const tables = occupiedTables.value.filter(t => t.tableGroupId === groupId)
    const tableNumbers = tables.map(t => t.number).sort((a, b) => a - b)
    return {
      id: groupId,
      tables,
      displayName: `Table ${tableNumbers.join(' + ')}`
    }
  })
})

// Get order items for a table group
const getOrderItemsForGroup = (groupId: string) => {
  if (!groupId) return []
  return ordersStore.orderItems.filter(item => item.tableGroupId === groupId)
}

// Calculate total for a table group
const calculateTotal = (items: any[]) => {
  return items.reduce((total, item) => {
    return total + (Number(item.unit_price_snap || 0) * item.quantity)
  }, 0)
}

// Check if table has bill request
const hasBillRequest = (groupId: string) => {
  if (!groupId) return false
  const group = tableGroupsStore.tableGroups.find(g => g.id === groupId)
  return group?.billingStatus === 'bill_requested' || false
}

// --------------------------------
// Event Handlers
// --------------------------------

function handleBackToDashboard() {
  router.push('/admin')
}

async function handlePrintBill(group: any) {
  if (!group?.id) return
  const items = getOrderItemsForGroup(group.id)
  const total = calculateTotal(items)
  
  try {
    loading.value = true
    await billingApi.printBill(group.id)
    alert(`✅ Bill printed successfully for ${group.displayName}\nTotal: $${total.toFixed(2)}\nItems: ${items.length}`)
  } catch (e) {
    console.error('Print failed:', e)
    alert(`❌ Failed to print bill: ${e instanceof Error ? e.message : 'Unknown error'}`)
  } finally {
    loading.value = false
  }
}

async function handleCloseTable(group: any) {
  if (!group?.id) return
  if (confirm(`Are you sure you want to close ${group.displayName}?\nThis will mark the table as available.`)) {
    try {
      await tableGroupsStore.closeTableGroup(group.id)
      alert(`✅ ${group.displayName} closed successfully!`)
      
      // Refresh data
      await tablesStore.fetchTables()
      await tableGroupsStore.fetchOpenGroups()
    } catch (e) {
      error.value = 'Failed to close table'
      console.error('Close table failed:', e)
    }
  }
}

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  try {
    loading.value = true
    
    // Load tables and groups
    await Promise.all([
      tablesStore.fetchTables(),
      tableGroupsStore.fetchOpenGroups(),
    ])
    
  } catch (e) {
    error.value = 'Failed to load billing data'
    console.error('Load failed:', e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="billing-view">
    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <h1>🧾 Billing Management</h1>
        <p>Manage bills and close occupied tables</p>
        <button class="nav-btn" @click="handleBackToDashboard">
          ← Back to Dashboard
        </button>
      </div>
    </header>

    <!-- Error Banner -->
    <div v-if="error" class="error-banner">
      {{ error }}
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading billing data...</p>
    </div>

    <!-- Billing Content -->
    <div v-else class="content">
      <div v-if="occupiedTableGroups.length === 0" class="empty-state">
        <h2>📋 No Active Bills</h2>
        <p>No occupied tables with active orders.</p>
      </div>

      <div v-else class="table-groups-grid">
        <div 
          v-for="group in occupiedTableGroups" 
          :key="group.id" 
          class="table-group-card"
        >
          <!-- Table Group Header -->
          <div class="group-header">
            <h3>{{ group.displayName }}</h3>
            <div class="status-badges">
              <span v-if="hasBillRequest(group.id)" class="bill-request-badge">
                🧾 Bill Requested
              </span>
              <span class="occupied-badge">
                🔴 Occupied
              </span>
            </div>
          </div>

          <!-- Order Items Summary -->
          <div class="items-summary">
            <div class="summary-stats">
              <span class="stat">
                📝 Items: {{ getOrderItemsForGroup(group.id).length }}
              </span>
              <span class="stat">
                💰 Total: ${{ calculateTotal(getOrderItemsForGroup(group.id)).toFixed(2) }}
              </span>
            </div>

            <!-- Sample Items Display -->
            <div class="items-preview">
              <div 
                v-for="item in getOrderItemsForGroup(group.id).slice(0, 3)" 
                :key="item.id" 
                class="preview-item"
              >
                <span class="item-name">{{ item.notes || `Item ${item.menuItemId}` }}</span>
                <span class="item-qty">×{{ item.quantity }}</span>
              </div>
              <div v-if="getOrderItemsForGroup(group.id).length > 3" class="more-items">
                +{{ getOrderItemsForGroup(group.id).length - 3 }} more items
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="actions">
            <button 
              class="action-btn print-btn" 
              @click="handlePrintBill(group)"
            >
              🖨 Print Receipt
            </button>
            <button 
              class="action-btn close-btn" 
              @click="handleCloseTable(group)"
            >
              🔒 Close Table
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.billing-view {
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

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-state h2 {
  margin: 0 0 16px 0;
  color: white;
  font-size: 24px;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 16px;
}

.table-groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.table-group-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.table-group-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.group-header {
  margin-bottom: 20px;
}

.group-header h3 {
  margin: 0 0 12px 0;
  color: #1f2937;
  font-size: 20px;
  font-weight: 700;
}

.status-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.bill-request-badge {
  background: #fef3c7;
  color: #92400e;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.occupied-badge {
  background: #fee2e2;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.items-summary {
  margin-bottom: 20px;
}

.summary-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.stat {
  background: #f8fafc;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.items-preview {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px solid #e5e7eb;
}

.preview-item:last-child {
  border-bottom: none;
}

.item-name {
  font-size: 14px;
  color: #374151;
}

.item-qty {
  background: #3b82f6;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
}

.more-items {
  text-align: center;
  padding: 8px;
  color: #6b7280;
  font-size: 12px;
  font-style: italic;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.action-btn {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
}

.print-btn {
  background: #22c55e;
  color: white;
}

.print-btn:hover {
  background: #16a34a;
}

.close-btn {
  background: #dc2626;
  color: white;
}

.close-btn:hover {
  background: #b91c1c;
}

@media (max-width: 768px) {
  .table-groups-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .summary-stats {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
