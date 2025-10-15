<script setup>
import { ref, defineEmits } from 'vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

const props = defineProps({
  sessionId: { type: String, default: null },
  isLoading: { type: Boolean, default: false }, // New prop
})

const emits = defineEmits(['send-message'])

const newMessage = ref('')

function handleSendMessage() {
  if (newMessage.value.trim() !== '') {
    emits('send-message', newMessage.value)
    newMessage.value = ''
  }
}
</script>

<template>
  <div class="p-4 border-t bg-white">
    <div class="flex items-center">
      <Textarea
        v-model="newMessage"
        placeholder="Type your message..."
        class="mr-2"
        @keydown.enter.prevent="handleSendMessage"
        :disabled="isLoading"
      ></Textarea>
      <Button @click="handleSendMessage" :disabled="!sessionId || isLoading">Send</Button>
    </div>
  </div>
</template>
