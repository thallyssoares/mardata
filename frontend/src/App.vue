<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()

onMounted(() => {
  // Check for an existing session when the app loads
  authStore.checkSession()
  
  // Listen for changes in the authentication state (e.g., login/logout in another tab)
  authStore.listenForAuthStateChange()
})
</script>

<template>
  <RouterView />
</template>
