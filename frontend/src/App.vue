<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useSessionsStore } from '@/stores/sessions'

const sessionsStore = useSessionsStore()

onMounted(() => {
  sessionsStore.restoreSession()
})
</script>

<template>
  <RouterView />
</template>