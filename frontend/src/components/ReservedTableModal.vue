<script setup lang="ts">
defineProps<{
  tableNumber: number
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()
</script>

<template>
  <div class="overlay" @click.self="emit('close')">
    <div class="modal">
      <h3 class="title">
        Table {{ tableNumber }} is reserved
      </h3>
      <p class="desc">
        Please select another table or ask the manager.
      </p>
      <div class="actions">
        <button type="button" class="btn" @click="emit('close')">
          OK
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
  width: min(480px, calc(100% - 2rem));
  background: white;
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid var(--pos-border);
}

.title {
  margin: 0 0 0.5rem;
}

.desc {
  margin: 0 0 1rem;
  color: var(--pos-text-muted);
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: 0.5rem 0.9rem;
  border-radius: 10px;
  border: none;
  background: var(--pos-primary);
  color: white;
  font-weight: 700;
  cursor: pointer;
}
</style>

