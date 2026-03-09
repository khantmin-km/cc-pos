<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<template>
  <div class="wrap">
    <div class="card">
      <h2 class="h2">{{ title }}</h2>
      <p class="p">
        This screen is wired into the navigation and will be implemented next.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap {
  max-width: 1100px;
}

.card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  padding: 16px;
}

.h2 {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 900;
}

.p {
  margin: 0;
  color: #6b7280;
  font-weight: 600;
}
</style>

