import { ref } from 'vue'
import apiClient from '@/lib/apiClient'

export function useChat() {
  const messages = ref([])
  const isLoading = ref(false)

  const addMessage = (sender, text) => {
    messages.value.push({
      id: Date.now(),
      sender,
      text,
      timestamp: new Date().toISOString(),
    })
  }

  const sendMessage = async (text, notebookId) => {
    if (!text.trim()) return

    addMessage('User', text)
    isLoading.value = true

    try {
      const response = await apiClient.post(`/chat/${notebookId}`, { question: text })
      const result = response.data
      addMessage('AI', result.answer)
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = error.response?.data?.detail || error.message
      addMessage('System', `Error: ${errorMessage}`)
    } finally {
      isLoading.value = false
    }
  }

  const clearMessages = () => {
    messages.value = []
  }

  return {
    messages,
    isLoading,
    addMessage,
    sendMessage,
    clearMessages,
  }
}
