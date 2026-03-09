<script setup lang="ts">
defineProps<{
  title: string
  message: string
  confirmText?: string
  danger?: boolean
}>()

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()
</script>

<template>
  <div class="overlay" @click.self="emit('cancel')">
    <div class="modal">
      <h3 class="title">
        {{ title }}
      </h3>
      <p class="msg">
        {{ message }}
      </p>
      <div class="actions">
        <button type="button" class="btn btn-cancel" @click="emit('cancel')">
          Cancel
        </button>
        <button
          type="button"
          class="btn"
          :class="danger ? 'btn-danger' : 'btn-primary'"
          @click="emit('confirm')"
        >
          {{ confirmText ?? 'Confirm' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.55);
  display: grid;
  place-items: center;
  z-index: 50;
}

.modal {
  width: min(520px, calc(100% - 2rem));
  background: white;
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid var(--pos-border);
}

.title {
  margin: 0 0 0.5rem;
}

.msg {
  margin: 0 0 1rem;
  color: var(--pos-text-muted);
  line-height: 1.45;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.btn {
  border: none;
  border-radius: 10px;
  padding: 0.5rem 0.9rem;
  font-weight: 800;
  cursor: pointer;
}

.btn-cancel {
  background: #e5e7eb;
  color: #0f172a;
}

.btn-primary {
  background: var(--pos-primary);
  color: white;
}

.btn-danger {
  background: #ef4444;
  color: white;
}
</style>

