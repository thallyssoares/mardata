<template>
  <div class="flex h-screen">
    <!-- Sidebar -->
    <div class="w-1/4 border-r p-4 flex flex-col">
      <h2 class="text-lg font-semibold mb-4">Data Sources</h2>
      <FileUpload @files-uploaded="handleFilesUploaded" />
      <div v-if="uploadedFiles.length > 0" class="mt-4">
        <h3 class="text-md font-medium mb-2">Uploaded Files:</h3>
        <ul class="list-disc list-inside text-sm text-muted-foreground">
          <li v-for="file in uploadedFiles" :key="file.name">{{ file.name }}</li>
        </ul>
      </div>
    </div>

    <!-- Chat Area -->
    <div class="flex-1 flex flex-col">
      <ChatMessages :messages="messages" />
      <ChatInput
        :is-loading="isLoading"
        :session-id="sessionId"
        @send-message="sendMessage"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FileUpload from '@/components/FileUpload.vue'
import ChatMessages from '@/components/ChatMessages.vue'
import ChatInput from '@/components/ChatInput.vue'

const messages = ref([
  { id: 1, sender: 'AI', text: 'Hello! How can I help you with your data today?' },
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
    text: `Uploaded ${data.files.length} file(s): ${data.files.map(f => f.name).join(', ')}`,
  })
  messages.value.push({
    id: Date.now() + 2,
    sender: 'AI',
    text: data.aiInsight,
  })
}

async function sendChatMessage(question, currentSessionId) {
  try {
    isLoading.value = true;
    const response = await fetch(`http://localhost:8000/api/chat/${currentSessionId}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      },
    )

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Failed to get AI response')
    }

    const result = await response.json()
    messages.value.push({ id: Date.now() + 1, sender: 'AI', text: result.answer })
  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.push({
      id: Date.now() + 1,
      sender: 'System',
      text: `Error: ${error.message}`,
    })
  } finally {
    isLoading.value = false;
  }
}

async function sendMessage(userMessageText) {
  if (userMessageText.trim() === '') return
  if (!sessionId.value) {
    alert('Please upload a file and get initial analysis first.')
    return
  }

  messages.value.push({ id: Date.now(), sender: 'User', text: userMessageText })

  await sendChatMessage(userMessageText, sessionId.value);
}
</script>
