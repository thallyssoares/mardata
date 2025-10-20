import { ref } from 'vue'
import apiClient from '@/lib/apiClient'

export function useChat() {
  const messages = ref([])
  const isLoading = ref(false)

  const setMessages = (newMessages) => {
    messages.value = newMessages;
  }

  const addMessage = (sender, text) => {
    messages.value.push({
      id: Date.now() + Math.random(),
      sender,
      text,
      timestamp: new Date().toISOString(),
    })
  }

  const sendMessage = async (text, notebookId, statisticalSummary, loadNotebook) => { 
    if (!text.trim()) return

    isLoading.value = true

    try {
      await apiClient.post(`/chat/${notebookId}`, {
        question: text,
        chat_history: messages.value, 
        statistical_summary: statisticalSummary, 
      })
      if(loadNotebook) {
        await loadNotebook();
      }
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
    setMessages,
    sendMessage,
    clearMessages,
  }
}

