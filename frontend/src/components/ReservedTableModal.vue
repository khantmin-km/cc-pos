<script setup lang="ts">
defineProps<{
  tableNumber: number
}>()

defineEmits<{
  close: []
}>()
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>Table {{ tableNumber }} is Reserved</h3>
      <p>This table is currently reserved and cannot be selected.</p>
      <button @click="$emit('close')">OK</button>
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
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 400px;
  text-align: center;
}

button {
  margin-top: 1rem;
  padding: 0.5rem 2rem;
  background: var(--pos-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>
