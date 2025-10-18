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
        <AvatarImage :src="avatarSrc" :alt="message.sender" />
        <AvatarFallback :class="avatarFallbackClass">
          {{ message.sender.substring(0, 2) }}
        </AvatarFallback>
      </Avatar>

      <div :class="['flex flex-col', isUser ? 'items-end' : 'items-start']">
        <Card :class="bubbleClasses">
          <CardContent class="p-3">
            <div v-if="message.sender === 'AI'">
              <MarkdownRenderer :markdown="message.text" />
            </div>
            <p v-else class="text-sm whitespace-pre-wrap leading-relaxed">
              {{ message.text }}
            </p>
          </CardContent>
        </Card>
        <span class="text-xs text-foam-500 mt-1 px-2">
          {{ formatTime(message.timestamp) }}
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

const isUser = computed(() => props.message.sender === 'User')
const isSystem = computed(() => props.message.sender === 'System')

const avatarSrc = computed(() => {
  if (isUser.value) {
    return 'https://github.com/radix-vue.png'
  }
  return 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y'
})

const avatarFallbackClass = computed(() => {
  if (isUser.value) {
    return 'bg-ocean-gradient text-white font-semibold'
  }
  if (isSystem.value) {
    return 'bg-foam-300 text-foam-700'
  }
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
