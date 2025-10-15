import { ref } from 'vue'

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

  const sendMessage = async (text, sessionId) => {
    if (!text.trim()) return

    addMessage('User', text)
    isLoading.value = true

    try {
      const response = await fetch(`http://localhost:8000/api/chat/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: text }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to get AI response')
      }

      const result = await response.json()
      addMessage('AI', result.answer)
    } catch (error) {
      console.error('Error sending message:', error)
      addMessage('System', `Error: ${error.message}`)
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
