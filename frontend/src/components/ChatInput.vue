<template>
  <div class="p-6 border-t border-ocean-100 bg-white shadow-ocean-sm">
    <div class="max-w-4xl mx-auto">
      <div class="flex items-end space-x-3">
        <div class="flex-1 relative">
          <Textarea
            v-model="newMessage"
            placeholder="Faça uma pergunta sobre seus dados..."
            class="min-h-[60px] resize-none border-ocean-200 focus:border-ocean-500 focus:ring-ocean-500 pr-16"
            @keydown.enter.prevent="handleSendMessage"
            :disabled="isLoading"
          />
          <div class="absolute bottom-3 right-3 text-xs text-foam-500">
            {{ newMessage.length }} / 500
          </div>
        </div>
        <Button
          @click="handleSendMessage"
          :disabled="!sessionId || isLoading || !newMessage.trim()"
          class="bg-ocean-600 hover:bg-ocean-700 text-white h-[60px] px-6 shadow-ocean-md"
        >
          <svg
            v-if="!isLoading"
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
          <svg
            v-else
            class="w-5 h-5 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        </Button>
      </div>

      <div v-if="!sessionId" class="mt-3 text-sm text-foam-600 flex items-center">
        <svg
          class="w-4 h-4 mr-2 text-ocean-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        Faça upload de um arquivo para começar a análise
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

const props = defineProps({
  sessionId: { type: String, default: null },
  isLoading: { type: Boolean, default: false },
})

const emits = defineEmits(['send-message'])

const newMessage = ref('')

function handleSendMessage() {
  if (newMessage.value.trim() !== '' && !props.isLoading) {
    emits('send-message', newMessage.value)
    newMessage.value = ''
  }
}
</script>
