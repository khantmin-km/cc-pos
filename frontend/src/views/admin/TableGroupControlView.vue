<script setup lang="ts">
/**
 * Table Group Control View (Admin)
 * 
 * Admin interface for managing table groups.
 * Allows creating, splitting, merging, and dissolving groups.
 */

// Vue core imports
import {
  ref,
  computed,
  onMounted,
} from 'vue'

// Store imports
import { useTablesStore } from '@/stores/tables'
import { useTableGroupsStore } from '@/stores/tableGroups'

// Type imports
import type {
  Table,
  TableGroupUI,
} from '@/types/pos'

// Component imports
import AdminCard from '@/components/admin/AdminCard.vue'
import StatusBadge from '@/components/admin/StatusBadge.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'

// --------------------------------
// Setup
// --------------------------------

// Initialize stores
const tablesStore = useTablesStore()
const tableGroupsStore = useTableGroupsStore()

// --------------------------------
// State
// --------------------------------

/** Show create group modal */
const showCreateModal = ref(false)

/** Show split group modal */
const showSplitModal = ref(false)

/** Show merge groups modal */
const showMergeModal = ref(false)

/** Show dissolve group modal */
const showDissolveModal = ref(false)

/** Currently selected group for operations */
const selectedGroup = ref<TableGroupUI | null>(null)

/** Name input for new/split groups */
const newGroupName = ref('')

/** Currently dragged table for DnD */
const draggedTable = ref<Table | null>(null)

/** Selected table IDs for split operation */
const splitTableIds = ref<string[]>([])

// --------------------------------
// Computed
// --------------------------------

/** All table groups */
const allGroups = computed(() => {
  return tableGroupsStore.tableGroups
})

/** Tables not in any group */
const ungroupedTables = computed(() => {
  return tableGroupsStore.ungroupedTables
})

/** Confirmation message for dissolve */
const dissolveMessage = computed(() => {
  const name = selectedGroup.value?.name ?? ''
  return `Dissolve ${name}? Tables will be ungrouped.`
})

// --------------------------------
// Lifecycle
// --------------------------------

/**
 * Load data on mount
 */
onMounted(async () => {
  await tablesStore.fetchTables()
  await tableGroupsStore.fetchOpenGroups()
})

// --------------------------------
// Helper Functions
// --------------------------------

/**
 * Get tables belonging to a group
 * 
 * @param groupId - Group ID
 */
function getTablesForGroup(groupId: string) {
  const group = tableGroupsStore.getTableGroupById(
    groupId
  )

  if (!group) return []

  return group.tableIds
    .map((id) => tablesStore.getTableById(id))
    .filter((t): t is Table => t !== undefined)
}

// --------------------------------
// Action Handlers
// --------------------------------

/**
 * Create a new table group
 */
async function handleCreateGroup() {
  const hasName = newGroupName.value.trim()
  const hasTables = ungroupedTables.value.length > 0

  if (hasName && hasTables) {
    // Get first ungrouped table
    const tableId = ungroupedTables.value[0]?.id

    if (tableId) {
      // Create group by starting service
      await tablesStore.startService(tableId)
    }

    // Reset form
    newGroupName.value = ''
    showCreateModal.value = false
  }
}

/**
 * Split a table group
 */
async function handleSplitGroup() {
  const hasGroup = selectedGroup.value
  const hasName = newGroupName.value.trim()
  const hasTables = splitTableIds.value.length > 0

  if (hasGroup && hasName && hasTables) {
    await tableGroupsStore.splitTableGroup(
      selectedGroup.value.id,
      splitTableIds.value
    )

    // Reset form
    selectedGroup.value = null
    splitTableIds.value = []
    newGroupName.value = ''
    showSplitModal.value = false
  }
}

/**
 * Merge two groups
 * 
 * @param groupId1 - Source group
 * @param groupId2 - Target group
 */
async function handleMergeGroups(
  groupId1: string,
  groupId2: string
) {
  await tableGroupsStore.mergeTableGroups(
    groupId1,
    groupId2
  )
  showMergeModal.value = false
}

/**
 * Dissolve a group
 */
async function handleDissolveGroup() {
  if (selectedGroup.value) {
    await tableGroupsStore.closeTableGroup(
      selectedGroup.value.id
    )
    selectedGroup.value = null
    showDissolveModal.value = false
  }
}

// --------------------------------
// Drag and Drop Handlers
// --------------------------------

/**
 * Start dragging a table
 * 
 * @param table - Table being dragged
 */
function handleDragStart(table: Table) {
  draggedTable.value = table
}

/**
 * Drop table onto a group (or ungrouped area)
 * 
 * @param groupId - Target group ID (null for ungroup)
 */
async function handleDrop(groupId: string | null) {
  if (!draggedTable.value) return

  if (groupId) {
    // Add to target group
    await tableGroupsStore.addTableToGroup(
      groupId,
      draggedTable.value.id
    )
  } else {
    // Remove from current group
    const currentGroup = tableGroupsStore
      .getTableGroupByTableId(
        draggedTable.value.id
      )

    if (currentGroup) {
      await tableGroupsStore.removeTableFromGroup(
        currentGroup.id,
        draggedTable.value.id
      )
    }
  }

  draggedTable.value = null
}

// --------------------------------
// UI Helpers
// --------------------------------

/**
 * Toggle table selection for split
 * 
 * @param tableId - Table ID to toggle
 */
function toggleSplitTable(tableId: string) {
  const index = splitTableIds.value.indexOf(tableId)

  if (index > -1) {
    // Remove from selection
    splitTableIds.value.splice(index, 1)
  } else {
    // Add to selection
    splitTableIds.value.push(tableId)
  }
}

/**
 * Toggle waiter workflow override
 * 
 * @param groupId - Group ID
 */
function toggleWaiterWorkflow(groupId: string) {
  const group = tableGroupsStore.getTableGroupById(
    groupId
  )

  if (group) {
    const newValue = !group.waiterWorkflowOverride
    tableGroupsStore.setWaiterWorkflowOverride(
      groupId,
      newValue
    )
  }
}

/**
 * Open split modal for a group
 * 
 * @param group - Group to split
 */
function openSplitModalForGroup(group: TableGroupUI) {
  selectedGroup.value = group
  showSplitModal.value = true
  splitTableIds.value = []
}

/**
 * Open dissolve modal for a group
 * 
 * @param group - Group to dissolve
 */
function openDissolveModalForGroup(group: TableGroupUI) {
  selectedGroup.value = group
  showDissolveModal.value = true
}
</script>

<template>
  <div class="admin-view">
    <div class="admin-container">
      <!-- Header -->
      <div class="admin-header">
        <h2>
          Table & Table Group Control
        </h2>
      </div>

      <!-- Main Grid -->
      <div class="admin-grid">
        <!-- Ungrouped Tables -->
        <AdminCard title="Ungrouped Tables">
          <div
            class="table-list"
            @drop.prevent="handleDrop(null)"
            @dragover.prevent
          >
            <div
              v-for="table in ungroupedTables"
              :key="table.id"
              class="table-item"
              draggable="true"
              @dragstart="handleDragStart(table)"
            >
              <span class="table-number">
                Table {{ table.number }}
              </span>
              <StatusBadge
                :status="table.status"
                type="table"
              />
            </div>

            <p
              v-if="ungroupedTables.length === 0"
              class="empty-state"
            >
              No ungrouped tables
            </p>
          </div>
        </AdminCard>

        <!-- Table Groups -->
        <AdminCard
          v-for="group in allGroups"
          :key="group.id"
          :title="group.name"
        >
          <!-- Group Header -->
          <div class="group-header">
            <StatusBadge
              :status="group.billingStatus"
              type="billing"
            />
            <div class="group-actions">
              <button
                type="button"
                class="btn-small"
                @click="openSplitModalForGroup(group)"
              >
                Split
              </button>
              <button
                type="button"
                class="btn-small"
                @click="openDissolveModalForGroup(group)"
              >
                Dissolve
              </button>
              <label class="toggle-label">
                <input
                  type="checkbox"
                  :checked="group.waiterWorkflowOverride"
                  @change="toggleWaiterWorkflow(group.id)"
                />
                Override Waiter
              </label>
            </div>
          </div>

          <!-- Group Tables -->
          <div
            class="table-list"
            @drop.prevent="handleDrop(group.id)"
            @dragover.prevent
          >
            <div
              v-for="table in getTablesForGroup(group.id)"
              :key="table.id"
              class="table-item"
              draggable="true"
              @dragstart="handleDragStart(table)"
            >
              <span class="table-number">
                Table {{ table.number }}
              </span>
              <StatusBadge
                :status="table.status"
                type="table"
              />
            </div>
          </div>
        </AdminCard>

        <!-- Create New Group -->
        <AdminCard title="Create New Group">
          <button
            type="button"
            class="btn-primary"
            :disabled="ungroupedTables.length === 0"
            @click="showCreateModal = true"
          >
            Create Table Group
          </button>
        </AdminCard>
      </div>
    </div>

    <!-- Create Group Modal -->
    <div
      v-if="showCreateModal"
      class="modal-overlay"
      @click.self="showCreateModal = false"
    >
      <div class="modal-content">
        <h3 class="modal-title">
          Create Table Group
        </h3>
        <p class="modal-message">
          Create group with {{ ungroupedTables.length }} table(s)?
        </p>
        <div class="modal-form">
          <input
            v-model="newGroupName"
            type="text"
            placeholder="Group name"
            class="input-field"
          />
        </div>
        <div class="modal-actions">
          <button
            type="button"
            class="btn btn-cancel"
            @click="showCreateModal = false"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-confirm"
            :disabled="!newGroupName.trim()"
            @click="handleCreateGroup"
          >
            Create
          </button>
        </div>
      </div>
    </div>

    <!-- Split Group Modal -->
    <div
      v-if="showSplitModal && selectedGroup"
      class="modal-overlay"
      @click.self="showSplitModal = false"
    >
      <div class="modal-content">
        <h3 class="modal-title">
          Split Group: {{ selectedGroup.name }}
        </h3>
        <p class="modal-message">
          Select tables to move to new group:
        </p>
        <div class="table-selection">
          <label
            v-for="tableId in selectedGroup.tableIds"
            :key="tableId"
            class="table-checkbox"
          >
            <input
              type="checkbox"
              :checked="splitTableIds.includes(tableId)"
              @change="toggleSplitTable(tableId)"
            />
            Table {{ tablesStore.getTableById(tableId)?.number }}
          </label>
        </div>
        <input
          v-model="newGroupName"
          type="text"
          placeholder="New group name"
          class="input-field"
        />
        <div class="modal-actions">
          <button
            type="button"
            class="btn btn-cancel"
            @click="showSplitModal = false"
          >
            Cancel
          </button>
          <button
            type="button"
            class="btn btn-confirm"
            :disabled="splitTableIds.length === 0"
            @click="handleSplitGroup"
          >
            Split
          </button>
        </div>
      </div>
    </div>

    <!-- Dissolve Modal -->
    <ConfirmModal
      v-if="showDissolveModal"
      title="Dissolve Table Group"
      :message="dissolveMessage"
      confirm-text="Dissolve"
      danger
      @confirm="handleDissolveGroup"
      @cancel="showDissolveModal = false"
    />
  </div>
</template>

<style scoped>
.admin-view {
  min-height: 100vh;
  background: var(--pos-background);
}

.admin-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
}

.admin-header {
  margin-bottom: 2rem;
}

.admin-header h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--pos-text);
  margin: 0;
}

.admin-grid {
  display: grid;
  grid-template-columns: repeat(
    auto-fill,
    minmax(300px, 1fr)
  );
  gap: 1.5rem;
}

.table-list {
  min-height: 100px;
  padding: 0.5rem;
}

.table-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: var(--pos-card-bg);
  border-radius: 6px;
  cursor: move;
  transition: background 0.2s;
}

.table-item:hover {
  background: #e5e7eb;
}

.table-number {
  font-weight: 600;
  color: var(--pos-text);
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--pos-border);
}

.group-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-small {
  padding: 0.25rem 0.75rem;
  background: var(--pos-primary);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
}

.btn-primary {
  width: 100%;
  padding: 0.75rem;
  background: var(--pos-primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  cursor: pointer;
}

.empty-state {
  text-align: center;
  color: var(--pos-text-muted);
  padding: 2rem;
}

.modal-form {
  margin-bottom: 1rem;
}

.input-field {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--pos-border);
  border-radius: 6px;
  font-size: 0.9rem;
}

.table-selection {
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 1rem;
}

.table-checkbox {
  display: block;
  padding: 0.5rem;
  cursor: pointer;
}

.table-checkbox:hover {
  background: var(--pos-card-bg);
}

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
  border-radius: 8px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--pos-text);
}

.modal-message {
  color: var(--pos-text-muted);
  margin-bottom: 1rem;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: #e5e7eb;
  color: var(--pos-text);
}

.btn-confirm {
  background: var(--pos-primary);
  color: white;
}

@media (max-width: 768px) {
  .admin-grid {
    grid-template-columns: 1fr;
  }
}
</style>
