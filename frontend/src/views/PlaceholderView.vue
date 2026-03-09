<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="placeholder">
    <h2 class="title">
      Coming soon
    </h2>
    <p class="desc">
      This route exists so the app can run end-to-end while screens are being built.
    </p>
    <pre class="route">{{ route.fullPath }}</pre>
  </div>
</template>

<style scoped>
.placeholder {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  border: 1px solid var(--pos-border);
  border-radius: 12px;
  padding: 1rem;
}

.title {
  margin: 0 0 0.5rem;
}

.desc {
  margin: 0 0 1rem;
  color: var(--pos-text-muted);
}

.route {
  background: #0b1020;
  color: #e5e7eb;
  padding: 0.75rem;
  border-radius: 8px;
  overflow: auto;
}
</style>

