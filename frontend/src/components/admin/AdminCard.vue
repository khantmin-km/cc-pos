<script setup lang="ts">
defineProps<{
  title: string
}>()
</script>

<template>
  <section class="card">
    <header class="hdr">
      <h3 class="title">
        {{ title }}
      </h3>
    </header>
    <div class="body">
      <slot />
    </div>
  </section>
</template>

<style scoped>
.card {
  background: white;
  border: 1px solid var(--pos-border);
  border-radius: 12px;
  overflow: hidden;
}

.hdr {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--pos-border);
  background: #ffffff;
}

.title {
  margin: 0;
  font-size: 1rem;
  font-weight: 800;
  color: var(--pos-text);
}

.body {
  padding: 1rem;
}
</style>

