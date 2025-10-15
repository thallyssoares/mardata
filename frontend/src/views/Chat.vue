<template>
  <div class="min-h-screen bg-foam-50 flex flex-col">
    <AppHeader />

    <div class="flex flex-1 overflow-hidden">
      <ChatSidebar
        :class="['hidden lg:flex']"
        :uploaded-files="uploadedFiles"
        @files-uploaded="handleFilesUploaded"
      />

      <div class="flex-1 flex flex-col bg-white">
        <div class="px-4 sm:px-6 py-4 border-b border-ocean-100 bg-white">
          <div class="flex items-center justify-between flex-wrap gap-3">
            <div>
              <h1 class="text-xl sm:text-2xl font-bold text-ocean-800">
                Análise de Dados
              </h1>
              <p class="text-xs sm:text-sm text-foam-600 mt-1">
                Converse com seus dados e extraia insights valiosos
              </p>
            </div>
            <div v-if="sessionId" class="flex items-center space-x-2 px-3 py-2 bg-ocean-50 rounded-lg">
              <div class="w-2 h-2 bg-ocean-500 rounded-full animate-pulse"></div>
              <span class="text-xs sm:text-sm font-medium text-ocean-700">Sessão Ativa</span>
            </div>
          </div>
        </div>

        <ChatMessages :messages="messages" />
        <ChatInput
          :is-loading="isLoading"
          :session-id="sessionId"
          @send-message="sendMessage"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import ChatSidebar from '@/components/ChatSidebar.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import ChatInput from '@/components/ChatInput.vue'

const messages = ref([
  {
    id: 1,
    sender: 'AI',
    text: 'Olá! Faça upload dos seus dados para começar a análise.',
    timestamp: new Date().toISOString(),
  },
])
const uploadedFiles = ref([])
const sessionId = ref(null)
const isLoading = ref(false)

async function handleFilesUploaded(data) {
  uploadedFiles.value = data.files
  sessionId.value = data.sessionId

  messages.value.push({
    id: Date.now() + 1,
    sender: 'System',
    text: `Upload concluído: ${data.files.length} arquivo(s) - ${data.files.map(f => f.name).join(', ')}`,
    timestamp: new Date().toISOString(),
  })
  messages.value.push({
    id: Date.now() + 2,
    sender: 'AI',
    text: data.aiInsight,
    timestamp: new Date().toISOString(),
  })
}

async function sendChatMessage(question, currentSessionId) {
  try {
    isLoading.value = true
    const response = await fetch(`http://localhost:8000/api/chat/${currentSessionId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Failed to get AI response')
    }

    const result = await response.json()
    messages.value.push({
      id: Date.now() + 1,
      sender: 'AI',
      text: result.answer,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.push({
      id: Date.now() + 1,
      sender: 'System',
      text: `Erro: ${error.message}`,
      timestamp: new Date().toISOString(),
    })
  } finally {
    isLoading.value = false
  }
}

async function sendMessage(userMessageText) {
  if (userMessageText.trim() === '') return
  if (!sessionId.value) {
    return
  }

  messages.value.push({
    id: Date.now(),
    sender: 'User',
    text: userMessageText,
    timestamp: new Date().toISOString(),
  })

  await sendChatMessage(userMessageText, sessionId.value)
}
</script>
