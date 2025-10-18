<template>
  <header class="bg-white border-b border-ocean-100 shadow-ocean-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <div class="flex items-center space-x-8">
          <router-link to="/" class="flex items-center space-x-2">
            <div class="w-10 h-10 ocean-gradient rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-xl">M</span>
            </div>
            <span class="text-2xl font-bold text-ocean-800">MarData</span>
          </router-link>

          <nav v-if="isAuthenticated" class="hidden md:flex space-x-6">
            <router-link
              to="/"
              class="text-foam-700 hover:text-ocean-600 font-medium transition-colors"
            >
              Dashboard
            </router-link>
            <router-link
              to="/chat"
              class="text-foam-700 hover:text-ocean-600 font-medium transition-colors"
            >
              Análises
            </router-link>
          </nav>
        </div>

        <div v-if="isAuthenticated" class="flex items-center space-x-4">
          <Button @click="handleCreateNotebook" class="hidden sm:flex bg-ocean-600 hover:bg-ocean-700 text-white">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            Novo Notebook
          </Button>
          <Avatar @click="handleLogout" title="Clique para sair" class="cursor-pointer ring-2 ring-ocean-200 hover:ring-ocean-400 transition-all">
            <AvatarImage src="https://github.com/radix-vue.png" alt="User" />
            <AvatarFallback class="bg-ocean-gradient text-white font-semibold">
              U
            </AvatarFallback>
          </Avatar>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'

const { logout, isAuthenticated } = useAuth()
const router = useRouter()

function handleLogout() {
  logout()
  router.push('/login')
}

function handleCreateNotebook() {
  router.push('/chat')
}
</script>
