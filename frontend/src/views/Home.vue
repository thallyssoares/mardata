<template>
  <div class="min-h-screen bg-foam-50">
    <AppHeader />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 class="text-3xl sm:text-4xl font-bold text-ocean-800 mb-2">
            Meus Notebooks
          </h1>
          <p class="text-foam-600 text-base sm:text-lg">
            Análises de dados e insights inteligentes
          </p>
        </div>
        <Button
          @click="handleCreateNotebook"
          class="bg-ocean-600 hover:bg-ocean-700 text-white shadow-ocean-md w-full sm:w-auto"
        >
          <svg
            class="w-5 h-5 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            />
          </svg>
          Novo Notebook
        </Button>
      </div>

      <div v-if="notebooks.length > 0" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <NotebookCard
          v-for="notebook in notebooks"
          :key="notebook.id"
          :notebook="notebook"
          @click="openNotebook(notebook.id)"
        />
      </div>

      <EmptyState
        v-else
        title="Nenhum notebook ainda"
        description="Crie seu primeiro notebook para começar a analisar seus dados de tráfego pago com inteligência artificial"
        action-text="Criar Primeiro Notebook"
      >
        <template #action>
          <Button
            @click="handleCreateNotebook"
            class="bg-ocean-600 hover:bg-ocean-700 text-white"
          >
            <svg
              class="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
            Criar Primeiro Notebook
          </Button>
        </template>
      </EmptyState>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useNotebooks } from '@/composables/useNotebooks'
import AppHeader from '@/components/AppHeader.vue'
import NotebookCard from '@/components/NotebookCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import { Button } from '@/components/ui/button'

const router = useRouter()
const { notebooks } = useNotebooks()

function handleCreateNotebook() {
  router.push('/chat')
}

function openNotebook(id) {
  router.push('/chat')
}
</script>
