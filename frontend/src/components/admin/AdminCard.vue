<script setup lang="ts">
defineProps<{
  title?: string
  noPadding?: boolean
}>()
</script>

<template>
  <div class="admin-card">
    <h3 v-if="title" class="card-title">{{ title }}</h3>
    <div class="card-content" :class="{ 'no-padding': noPadding }">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.admin-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.card-title {
  padding: 1rem;
  margin: 0;
  border-bottom: 1px solid var(--pos-border);
  font-size: 1.1rem;
}

.card-content {
  padding: 1rem;
}

.card-content.no-padding {
  padding: 0;
}
</style>
