<script setup lang="ts">
/**
 * Root App Component
 * 
 * Main application shell with router view.
 */
</script>

<template>
  <RouterView />
</template>

<style>
/* Global styles */
:root {
  --pos-primary: #3b82f6;
  --pos-background: #f3f4f6;
  --pos-card-bg: #ffffff;
  --pos-text: #1f2937;
  --pos-text-muted: #6b7280;
  --pos-border: #e5e7eb;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--pos-background);
  color: var(--pos-text);
}
</style>
