<script setup lang="ts">
/**
 * Switch Table Modal
 * 
 * Allows waiter to switch ordered items from one table to another.
 * Shows source and target table selection with validation.
 */

// Vue imports
import { ref, computed } from 'vue'

// Type imports
import type { Table } from '@/types/pos'

// Props
interface Props {
  tables: Table[]
}

const props = defineProps<Props>()

// Emits
interface Emits {
  close: []
  switch: [payload: { fromTableId: string; toTableId: string }]
}

const emit = defineEmits<Emits>()

// State
const selectedSourceTable = ref<string>('')
const selectedTargetTable = ref<string>('')

// Computed
const availableTargetTables = computed(() => {
  return props.tables.filter(table => 
    table.id !== selectedSourceTable.value && table.status === 'occupied'
  )
})

const canSwitch = computed(() => {
  return selectedSourceTable.value && 
         selectedTargetTable.value && 
         selectedSourceTable.value !== selectedTargetTable.value
})

// Event handlers
function handleSwitch() {
  if (!canSwitch.value) return
  
  emit('switch', {
    fromTableId: selectedSourceTable.value,
    toTableId: selectedTargetTable.value
  })
  
  // Reset selection
  selectedSourceTable.value = ''
  selectedTargetTable.value = ''
  
  // Close modal
  emit('close')
}

function handleClose() {
  selectedSourceTable.value = ''
  selectedTargetTable.value = ''
  emit('close')
}
</script>

<template>
  <div class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>🔄 Switch Tables</h2>
        <p>Move ordered items from one table to another</p>
      </div>

      <div class="modal-body">
        <!-- Source Table Selection -->
        <div class="form-group">
          <label class="form-label">From Table:</label>
          <select 
            v-model="selectedSourceTable" 
            class="form-select"
          >
            <option value="">Select source table...</option>
            <option 
              v-for="table in props.tables.filter(t => t.status === 'occupied')"
              :key="table.id"
              :value="table.id"
            >
              Table {{ table.number }} (Occupied)
            </option>
          </select>
        </div>

        <!-- Target Table Selection -->
        <div class="form-group">
          <label class="form-label">To Table:</label>
          <select 
            v-model="selectedTargetTable" 
            class="form-select"
            :disabled="!selectedSourceTable"
          >
            <option value="">Select target table...</option>
            <option 
              v-for="table in availableTargetTables"
              :key="table.id"
              :value="table.id"
            >
              Table {{ table.number }} (Available)
            </option>
          </select>
        </div>

        <!-- Validation Message -->
        <div v-if="selectedSourceTable && selectedTargetTable && selectedSourceTable === selectedTargetTable" class="validation-error">
          ⚠️ Source and target tables cannot be the same
        </div>
      </div>

      <div class="modal-footer">
        <button 
          class="btn btn-cancel" 
          @click="handleClose"
        >
          Cancel
        </button>
        <button 
          class="btn btn-primary" 
          :disabled="!canSwitch"
          @click="handleSwitch"
        >
          🔄 Switch Tables
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  margin-bottom: 24px;
}

.modal-header h2 {
  margin: 0 0 8px 0;
  color: #1f2937;
  font-size: 24px;
  font-weight: 700;
}

.modal-header p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.modal-body {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #374151;
}

.form-select {
  width: 100%;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  background: white;
}

.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-select:disabled {
  background: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
}

.validation-error {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 12px;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 16px;
}

.modal-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-cancel:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn:disabled {
  background: #9ca3af;
  color: #6b7280;
  cursor: not-allowed;
}
</style>
