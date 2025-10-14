<script setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const messages = ref([
  { id: 1, sender: 'AI', text: 'Hello! How can I help you with your data today?' },
  { id: 2, sender: 'User', text: 'I want to understand why my sales dropped last week.' },
])
const newMessage = ref('')

function sendMessage() {
  if (newMessage.value.trim() !== '') {
    messages.value.push({ id: Date.now(), sender: 'User', text: newMessage.value })
    newMessage.value = ''
    // Here you would typically call the AI service
  }
}
</script>

<template>
  <div class="flex h-screen">
    <!-- Sidebar -->
    <div class="w-1/4 border-r p-4">
      <h2 class="text-lg font-semibold mb-4">Data Sources</h2>
      <!-- File upload will go here -->
    </div>

    <!-- Chat Area -->
    <div class="flex-1 flex flex-col">
      <div class="flex-1 p-4 overflow-y-auto">
        <Card v-for="message in messages" :key="message.id" class="mb-4">
          <CardHeader>
            <CardTitle>{{ message.sender }}</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{{ message.text }}</p>
          </CardContent>
        </Card>
      </div>

      <!-- Message Input -->
      <div class="p-4 border-t">
        <div class="flex items-center">
          <Textarea
            v-model="newMessage"
            placeholder="Type your message..."
            class="mr-2"
            @keydown.enter.prevent="sendMessage"
          />
          <Button @click="sendMessage">Send</Button>
        </div>
      </div>
    </div>
  </div>
</template>