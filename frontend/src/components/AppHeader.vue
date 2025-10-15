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
          <Button
            variant="ghost"
            size="sm"
            class="hidden md:flex text-foam-700 hover:text-ocean-600 hover:bg-ocean-50"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
              />
            </svg>
          </Button>

          <button
            @click="toggleMobileMenu"
            class="md:hidden p-2 text-foam-700 hover:text-ocean-600 hover:bg-ocean-50 rounded-lg"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

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
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { useAuth } from '@/composables/useAuth'
import { useRouter } from 'vue-router'

const { logout, isAuthenticated } = useAuth()
const router = useRouter()

function toggleMobileMenu() {
  // TODO: Implement mobile menu logic if needed
  console.log('Mobile menu toggle')
}

function handleLogout() {
  logout()
  router.push('/login')
}
</script>
