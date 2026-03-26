<script setup lang="ts">
/**
 * Waiter Management View (Admin)
 * 
 * Allows admin to manage staff:
 * - Create new waiters
 * - Edit waiter info
 * - Activate/deactivate waiters
 */

import { ref, computed, onMounted } from 'vue'
import { useWaitersStore } from '@/stores/waiters'

import type { Waiter, WaiterCreateRequest, WaiterUpdateRequest } from '@/types/pos'

// --------------------------------
// Setup
// --------------------------------

const waitersStore = useWaitersStore()

// --------------------------------
// State
// --------------------------------

const showCreateForm = ref(false)
const editingWaiterId = ref<string | null>(null)
const showInactive = ref(false)

const newWaiter = ref<WaiterCreateRequest>({
  name: '',
})

const editForm = ref<Partial<WaiterUpdateRequest>>({})
const loading = ref(false)
const error = ref<string | null>(null)
const successMsg = ref<string | null>(null)

// --------------------------------
// Computed
// --------------------------------

const displayWaiters = computed(() => {
  let waiters = showInactive.value
    ? waitersStore.waiters
    : waitersStore.activeWaiters

  return waiters.sort((a, b) => a.name.localeCompare(b.name))
})

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  try {
    await waitersStore.fetchWaiters(showInactive.value)
  } catch (e) {
    error.value = 'Failed to load waiters'
  }
})

// --------------------------------
// Event Handlers
// --------------------------------

async function handleCreateWaiter() {
  if (!newWaiter.value.name.trim()) {
    error.value = 'Please enter waiter name'
    return
  }

  loading.value = true
  error.value = null

  try {
    await waitersStore.createWaiter(newWaiter.value)
    successMsg.value = 'Waiter created successfully'
    showCreateForm.value = false
    newWaiter.value = { name: '' }
    setTimeout(() => (successMsg.value = null), 3000)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to create waiter'
  } finally {
    loading.value = false
  }
}

function handleEditWaiter(waiter: Waiter) {
  editingWaiterId.value = waiter.id
  editForm.value = {
    name: waiter.name,
    active: waiter.active,
  }
}

async function handleSaveEdit() {
  if (!editingWaiterId.value) return

  loading.value = true
  error.value = null

  try {
    await waitersStore.updateWaiter(editingWaiterId.value, editForm.value)
    successMsg.value = 'Waiter updated successfully'
    editingWaiterId.value = null
    setTimeout(() => (successMsg.value = null), 3000)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to update waiter'
  } finally {
    loading.value = false
  }
}

async function handleToggleActive(waiterId: string, currentStatus: boolean) {
  loading.value = true
  error.value = null

  try {
    await waitersStore.updateWaiter(waiterId, { active: !currentStatus })
    successMsg.value = 'Waiter status updated'
    setTimeout(() => (successMsg.value = null), 3000)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to update waiter'
  } finally {
    loading.value = false
  }
}

async function handleShowInactiveChange() {
  loading.value = true
  error.value = null

  try {
    await waitersStore.fetchWaiters(!showInactive.value)
    showInactive.value = !showInactive.value
  } catch (e) {
    error.value = 'Failed to load waiters'
  } finally {
    loading.value = false
  }
}

function cancelEdit() {
  editingWaiterId.value = null
  editForm.value = {}
}
</script>

<template>
  <div class="waiter-management">
    <!-- Header -->
    <div class="header">
      <div>
        <h2>Waiter Management</h2>
        <p>{{ displayWaiters.length }} waiter{{ displayWaiters.length !== 1 ? 's' : '' }}</p>
      </div>
      <button
        class="btn btn-primary"
        @click="showCreateForm = !showCreateForm"
        v-if="!showCreateForm"
      >
        + Add New Waiter
      </button>
    </div>

    <!-- Messages -->
    <div v-if="successMsg" class="message success">
      ✓ {{ successMsg }}
    </div>
    <div v-if="error" class="message error">
      ✗ {{ error }}
    </div>

    <!-- Create Form -->
    <div v-if="showCreateForm" class="form-card">
      <h3>Add New Waiter</h3>
      <form @submit.prevent="handleCreateWaiter">
        <div class="form-group">
          <label>Waiter Name</label>
          <input
            v-model="newWaiter.name"
            placeholder="Enter waiter name"
            required
            autofocus
          />
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Creating...' : 'Create Waiter' }}
          </button>
          <button type="button" class="btn btn-secondary" @click="showCreateForm = false">
            Cancel
          </button>
        </div>
      </form>
    </div>

    <!-- Filters -->
    <div class="filters">
      <label>
        <input
          type="checkbox"
          v-model="showInactive"
          @change="handleShowInactiveChange"
          :disabled="loading"
        />
        Show Inactive Waiters
      </label>
    </div>

    <!-- Waiters List -->
    <div class="waiters-list">
      <div v-if="displayWaiters.length === 0" class="empty-state">
        {{ showInactive ? 'No inactive waiters' : 'No active waiters' }}
      </div>

      <div v-for="waiter in displayWaiters" :key="waiter.id" class="waiter-row">
        <!-- Edit Mode -->
        <div v-if="editingWaiterId === waiter.id" class="waiter-edit">
          <div class="form-group">
            <label>Name</label>
            <input v-model="editForm.name" />
          </div>
          <div class="form-group">
            <label>
              <input v-model="editForm.active" type="checkbox" />
              Active
            </label>
          </div>
          <div class="actions">
            <button class="btn btn-small btn-primary" @click="handleSaveEdit" :disabled="loading">
              Save
            </button>
            <button class="btn btn-small btn-secondary" @click="cancelEdit">
              Cancel
            </button>
          </div>
        </div>

        <!-- View Mode -->
        <div v-else class="waiter-view">
          <div class="waiter-info">
            <h4>{{ waiter.name }}</h4>
            <p v-if="!waiter.active" class="status-inactive">Inactive</p>
            <p v-else class="status-active">Active</p>
          </div>
          <div class="actions">
            <button class="btn btn-small btn-secondary" @click="handleEditWaiter(waiter)">
              Edit
            </button>
            <button
              class="btn btn-small"
              :class="waiter.active ? 'btn-warning' : 'btn-success'"
              @click="handleToggleActive(waiter.id, waiter.active)"
              :disabled="loading"
            >
              {{ waiter.active ? 'Deactivate' : 'Activate' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.waiter-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  font-size: 24px;
}

.header p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 14px;
}

.message {
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-weight: 500;
}

.message.success {
  background: #dcfce7;
  color: #166534;
}

.message.error {
  background: #fee2e2;
  color: #dc2626;
}

.form-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.form-card h3 {
  margin: 0 0 16px;
  font-size: 18px;
}

.form-card form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 4px;
  font-weight: 600;
  font-size: 14px;
}

.form-group input[type='text'] {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.form-group input[type='checkbox'] {
  width: 16px;
  height: 16px;
  margin-right: 8px;
}

.form-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.filters {
  margin-bottom: 20px;
}

.filters label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: 500;
}

.filters input[type='checkbox'] {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  cursor: pointer;
}

.waiters-list {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #64748b;
}

.waiter-row {
  border-bottom: 1px solid #e2e8f0;
  padding: 16px 20px;
}

.waiter-row:last-child {
  border-bottom: none;
}

.waiter-view {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.waiter-info h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.waiter-info p {
  margin: 4px 0 0;
  font-size: 12px;
  font-weight: 600;
}

.status-active {
  color: #16a34a;
}

.status-inactive {
  color: #64748b;
}

.waiter-edit {
  display: grid;
  grid-template-columns: 1fr auto auto auto;
  gap: 12px;
  align-items: end;
}

.waiter-edit .form-group {
  margin: 0;
}

.waiter-edit .form-group label {
  font-size: 12px;
  margin-bottom: 2px;
}

.waiter-edit .form-group input[type='text'] {
  font-size: 12px;
  padding: 6px;
}

.waiter-edit .actions {
  display: flex;
  gap: 6px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
}

.btn-secondary {
  background: #f1f5f9;
  color: #1e293b;
}

.btn-secondary:hover:not(:disabled) {
  background: #e2e8f0;
}

.btn-success {
  background: #22c55e;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #16a34a;
}

.btn-warning {
  background: #ef4444;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #dc2626;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.actions {
  display: flex;
  gap: 8px;
}
</style>
