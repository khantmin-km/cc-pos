<script setup lang="ts">
/**
 * Menu Management View (Admin)
 * 
 * Allows admin to manage menu items:
 * - Create new items
 * - Edit existing items
 * - Retire items
 * - Upload images
 */

import { ref, computed, onMounted } from 'vue'
import { useMenuItemsStore } from '@/stores/menuItems'

import type { MenuItem, MenuItemCreateRequest, MenuItemUpdateRequest } from '@/types/pos'

// --------------------------------
// Setup
// --------------------------------

const menuStore = useMenuItemsStore()
const CATEGORY_OPTIONS = ['Main Dish', 'Side Dish', 'Appetizer', 'Beverages']

// --------------------------------
// State
// --------------------------------

const selectedCategory = ref<string>('all')
const showCreateForm = ref(false)
const editingItemId = ref<string | null>(null)
const searchQuery = ref('')

const newItem = ref<MenuItemCreateRequest>({
  name: '',
  price: 0,
  category: 'Main Dish',
  available: true,
})

const editForm = ref<Partial<MenuItemUpdateRequest>>({})
const loading = ref(false)
const error = ref<string | null>(null)
const successMsg = ref<string | null>(null)
const createImageFile = ref<File | null>(null)
const editImageFile = ref<File | null>(null)

// --------------------------------
// Computed
// --------------------------------

const displayItems = computed(() => {
  let items = menuStore.items
  
  if (selectedCategory.value !== 'all') {
    items = items.filter((item) => item.category === selectedCategory.value)
  }

  if (searchQuery.value) {
    items = items.filter((item) =>
      item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  return items
})

const categories = computed(() => {
  const cats = new Set(menuStore.items.map((item) => item.category))
  const all = [...CATEGORY_OPTIONS, ...Array.from(cats)]
  return Array.from(new Set(all))
})

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  try {
    await menuStore.fetchMenuItems()
  } catch (e) {
    error.value = 'Failed to load menu items'
  }
})

// --------------------------------
// Event Handlers
// --------------------------------

async function handleCreateItem() {
  if (!newItem.value.name || newItem.value.price <= 0) {
    error.value = 'Please fill in all fields correctly'
    return
  }

  loading.value = true
  error.value = null

  try {
    const created = await menuStore.createMenuItem(newItem.value)
    if (createImageFile.value) {
      await menuStore.uploadMenuItemImage(created.id, createImageFile.value)
    }
    successMsg.value = 'Menu item created successfully'
    showCreateForm.value = false
    newItem.value = {
      name: '',
      price: 0,
      category: 'Main Dish',
      available: true,
    }
    createImageFile.value = null
    setTimeout(() => (successMsg.value = null), 3000)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to create item'
  } finally {
    loading.value = false
  }
}

function handleEditItem(item: MenuItem) {
  editingItemId.value = item.id
  editImageFile.value = null
  editForm.value = {
    name: item.name,
    price: item.price,
    category: item.category,
    available: item.available,
  }
}

async function handleSaveEdit() {
  if (!editingItemId.value) return

  loading.value = true
  error.value = null

  try {
    await menuStore.updateMenuItem(editingItemId.value, editForm.value)
    if (editImageFile.value) {
      await menuStore.uploadMenuItemImage(editingItemId.value, editImageFile.value)
    }
    successMsg.value = 'Menu item updated successfully'
    editingItemId.value = null
    editImageFile.value = null
    setTimeout(() => (successMsg.value = null), 3000)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to update item'
  } finally {
    loading.value = false
  }
}

async function handleRetireItem(itemId: string) {
  if (!confirm('Are you sure you want to retire this item?')) return

  loading.value = true
  error.value = null

  try {
    await menuStore.retireMenuItem(itemId)
    successMsg.value = 'Menu item retired successfully'
    setTimeout(() => (successMsg.value = null), 3000)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to retire item'
  } finally {
    loading.value = false
  }
}

function cancelEdit() {
  editingItemId.value = null
  editForm.value = {}
  editImageFile.value = null
}

function handleCreateImageChange(event: Event) {
  const input = event.target as HTMLInputElement
  createImageFile.value = input.files?.[0] ?? null
}

function handleEditImageChange(event: Event) {
  const input = event.target as HTMLInputElement
  editImageFile.value = input.files?.[0] ?? null
}
</script>

<template>
  <div class="menu-management">
    <!-- Header -->
    <div class="header">
      <div>
        <h2>Menu Management</h2>
        <p>{{ displayItems.length }} items</p>
      </div>
      <button
        class="btn btn-primary"
        @click="showCreateForm = !showCreateForm"
        v-if="!showCreateForm"
      >
        + Add New Item
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
      <h3>Create New Menu Item</h3>
      <form @submit.prevent="handleCreateItem">
        <div class="form-group">
          <label>Item Name</label>
          <input v-model="newItem.name" placeholder="e.g., Pad Thai" required />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Price</label>
            <input v-model.number="newItem.price" type="number" step="0.01" required />
          </div>
          <div class="form-group">
            <label>Category</label>
            <select v-model="newItem.category" required>
              <option v-for="cat in CATEGORY_OPTIONS" :key="cat" :value="cat">
                {{ cat }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label>Menu Photo</label>
          <input type="file" accept="image/*" @change="handleCreateImageChange" />
        </div>

        <div class="form-group">
          <label>
            <input v-model="newItem.available" type="checkbox" />
            Available
          </label>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Creating...' : 'Create Item' }}
          </button>
          <button type="button" class="btn btn-secondary" @click="showCreateForm = false">
            Cancel
          </button>
        </div>
      </form>
    </div>

    <!-- Filters -->
    <div class="filters">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search items..."
        class="search-input"
      />
      <select v-model="selectedCategory">
        <option value="all">All Categories</option>
        <option v-for="cat in categories" :key="cat" :value="cat">
          {{ cat }}
        </option>
      </select>
    </div>

    <!-- Items List -->
    <div class="items-list">
      <div v-if="displayItems.length === 0" class="empty-state">
        No items found
      </div>

      <div v-for="item in displayItems" :key="item.id" class="item-row">
        <!-- Edit Mode -->
        <div v-if="editingItemId === item.id" class="item-edit">
          <div class="form-group">
            <label>Name</label>
            <input v-model="editForm.name" />
          </div>
          <div class="form-group">
            <label>Price</label>
            <input v-model.number="editForm.price" type="number" step="0.01" />
          </div>
          <div class="form-group">
            <label>Category</label>
            <select v-model="editForm.category">
              <option v-for="cat in CATEGORY_OPTIONS" :key="cat" :value="cat">
                {{ cat }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Photo</label>
            <input type="file" accept="image/*" @change="handleEditImageChange" />
          </div>
          <div class="form-group">
            <label>
              <input v-model="editForm.available" type="checkbox" />
              Available
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
        <div v-else class="item-view">
          <div class="item-details">
            <img
              v-if="item.image"
              :src="item.image"
              alt="Menu item"
              class="item-photo"
            />
            <h4>{{ item.name }}</h4>
            <p>{{ item.category }} | {{ item.price.toFixed(2) }}</p>
            <p v-if="!item.available" class="status-retired">Retired</p>
          </div>
          <div class="actions">
            <button
              class="btn btn-small btn-secondary"
              @click="handleEditItem(item)"
              v-if="item.available"
            >
              Edit
            </button>
            <button
              class="btn btn-small btn-danger"
              @click="handleRetireItem(item.id)"
              v-if="item.available"
              :disabled="loading"
            >
              Retire
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.menu-management {
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
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

.form-group input[type='text'],
.form-group input[type='number'],
.form-group select {
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
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.filters select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.items-list {
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

.item-row {
  border-bottom: 1px solid #e2e8f0;
  padding: 16px 20px;
}

.item-row:last-child {
  border-bottom: none;
}

.item-view {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-details h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.item-details p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 14px;
}

.status-retired {
  color: #dc2626;
  font-weight: 600;
}

.item-edit {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  align-items: end;
}

.item-edit .form-group {
  margin: 0;
}

.item-edit .form-group label {
  font-size: 12px;
  margin-bottom: 2px;
}

.item-edit .form-group input[type='text'],
.item-edit .form-group input[type='number'],
.item-edit .form-group select {
  font-size: 12px;
  padding: 6px;
}

.item-photo {
  width: 64px;
  height: 64px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 8px;
  border: 1px solid #e2e8f0;
}

.item-edit .actions {
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

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
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
