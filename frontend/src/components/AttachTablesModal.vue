<script setup lang="ts">
/**
 * Attach Tables Modal
 * 
 * Allows waiter to attach multiple available tables to an occupied table.
 * Shows table selection with multi-select capability.
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
  attach: [payload: { baseTableId: string; attachTableIds: string[] }]
}

const emit = defineEmits<Emits>()

// State
const selectedBaseTable = ref<string>('')
const selectedAttachTables = ref<string[]>([])

// Computed
const occupiedTables = computed(() => {
  return props.tables.filter(table => table.status === 'occupied')
})

const availableTables = computed(() => {
  return props.tables.filter(table => table.status === 'available')
})

const canAttach = computed(() => {
  return selectedBaseTable.value && selectedAttachTables.value.length > 0
})

// Event handlers
function getTableNumber(tableId: string): number {
  const table = props.tables.find(t => t.id === tableId)
  return table ? table.number : 0
}

function toggleTable(tableId: string) {
  const index = selectedAttachTables.value.indexOf(tableId)
  if (index > -1) {
    selectedAttachTables.value.splice(index, 1)
  } else {
    selectedAttachTables.value.push(tableId)
  }
}

function handleAttach() {
  if (!canAttach.value) return
  
  emit('attach', {
    baseTableId: selectedBaseTable.value,
    attachTableIds: [...selectedAttachTables.value]
  })
  
  // Reset selection
  selectedBaseTable.value = ''
  selectedAttachTables.value = []
  
  // Close modal
  emit('close')
}

function handleClose() {
  selectedBaseTable.value = ''
  selectedAttachTables.value = []
  emit('close')
}
</script>

<template>
  <div class="modal-overlay" @click="handleClose">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>📎 Attach Tables</h2>
        <p>Combine multiple tables into a single table group</p>
      </div>

      <div class="modal-body">
        <!-- Base Table Selection -->
        <div class="form-group">
          <label class="form-label">Base Table (Occupied):</label>
          <select 
            v-model="selectedBaseTable" 
            class="form-select"
          >
            <option value="">Select base table...</option>
            <option 
              v-for="table in occupiedTables"
              :key="table.id"
              :value="table.id"
            >
              Table {{ table.number }}
            </option>
          </select>
        </div>

        <!-- Attach Tables Selection -->
        <div class="form-group">
          <label class="form-label">Tables to Attach (Available):</label>
          <div class="tables-grid">
            <div 
              v-for="table in availableTables"
              :key="table.id"
              class="table-checkbox"
              :class="{ selected: selectedAttachTables.includes(table.id) }"
              @click="toggleTable(table.id)"
            >
              <input 
                type="checkbox" 
                :checked="selectedAttachTables.includes(table.id)"
                class="checkbox"
              >
              <div class="table-info">
                <span class="table-number">Table {{ table.number }}</span>
                <span class="table-status">Available</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Selection Summary -->
        <div v-if="selectedBaseTable || selectedAttachTables.length > 0" class="selection-summary">
          <div v-if="selectedBaseTable" class="base-selection">
            Base: Table {{ selectedBaseTable ? getTableNumber(selectedBaseTable) : '' }}
          </div>
          <div v-if="selectedAttachTables.length > 0" class="attach-selection">
            Attach: {{ selectedAttachTables.length }} table(s)
          </div>
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
          :disabled="!canAttach"
          @click="handleAttach"
        >
          📎 Attach Tables
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
  max-width: 600px;
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
  margin-bottom: 12px;
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

.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
}

.table-checkbox {
  display: flex;
  align-items: center;
  padding: 8px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.table-checkbox:hover {
  background: #f9fafb;
  border-color: #3b82f6;
}

.table-checkbox.selected {
  background: #eff6ff;
  border-color: #3b82f6;
}

.checkbox {
  margin-right: 12px;
}

.table-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.table-number {
  font-weight: 600;
  color: #1f2937;
}

.table-status {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.selection-summary {
  background: #f8fafc;
  border: 1px solid #e0f2fe;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.base-selection {
  color: #1f2937;
  font-weight: 600;
  margin-bottom: 8px;
}

.attach-selection {
  color: #059669;
  font-weight: 600;
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
