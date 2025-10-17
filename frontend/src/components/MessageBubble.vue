<template>
  <div
    :class="[
      'flex mb-4',
      isUser ? 'justify-end' : 'justify-start',
    ]"
  >
    <div
      :class="[
        'flex items-end max-w-[70%]',
        isUser ? 'flex-row-reverse' : 'flex-row',
      ]"
    >
      <Avatar :class="['h-8 w-8', isUser ? 'ml-2' : 'mr-2']">
        <AvatarImage :src="avatarSrc" :alt="message.role" />
        <AvatarFallback :class="avatarFallbackClass">
          {{ avatarFallbackText }}
        </AvatarFallback>
      </Avatar>

      <div :class="['flex flex-col', isUser ? 'items-end' : 'items-start']">
        <Card :class="bubbleClasses">
          <CardContent class="p-3">
            <div v-if="isAssistant">
              <MarkdownRenderer :markdown="message.content" />
            </div>
            <p v-else class="text-sm whitespace-pre-wrap leading-relaxed">
              {{ message.content }}
            </p>
          </CardContent>
        </Card>
        <span class="text-xs text-foam-500 mt-1 px-2">
          {{ formatTime(message.created_at) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import MarkdownRenderer from './MarkdownRenderer.vue'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
})

const isUser = computed(() => props.message.role === 'user')
const isAssistant = computed(() => props.message.role === 'assistant')
const isSystem = computed(() => props.message.role === 'system')

const avatarSrc = computed(() => {
  if (isUser.value) {
    return 'https://github.com/radix-vue.png' // Placeholder for user avatar
  }
  // AI/System avatar
  return 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y' 
})

const avatarFallbackText = computed(() => {
  if (isUser.value) return 'U'
  if (isAssistant.value) return 'AI'
  if (isSystem.value) return 'S'
  return ''
})

const avatarFallbackClass = computed(() => {
  if (isUser.value) {
    return 'bg-ocean-gradient text-white font-semibold'
  }
  if (isSystem.value) {
    return 'bg-foam-300 text-foam-700'
  }
  // Assistant
  return 'ocean-gradient text-white font-semibold'
})

const bubbleClasses = computed(() => {
  const base = 'shadow-ocean-sm transition-all duration-200'
  if (isUser.value) {
    return `${base} bg-ocean-600 text-white border-ocean-600`
  }
  if (isSystem.value) {
    return `${base} bg-foam-100 text-foam-700 border-foam-200`
  }
  // Assistant
  return `${base} bg-white text-foam-900 border-ocean-100 hover:shadow-ocean-md`
})

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>
