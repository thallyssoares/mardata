<template>
  <div class="prose max-w-none" v-html="renderedMarkdown"></div>
</template>

<script setup>
import { computed } from 'vue';
import { marked } from 'marked';

const props = defineProps({
  markdown: {
    type: String,
    required: true,
  },
});

const renderedMarkdown = computed(() => {
  if (props.markdown) {
    // Basic sanitization to prevent raw HTML injection, though `marked` is generally safe.
    // For production, consider a more robust sanitizer like DOMPurify.
    return marked(props.markdown, { breaks: true, gfm: true });
  }
  return '';
});
</script>

<style>
/* Add some basic styling for the rendered markdown */
.prose h1, .prose h2, .prose h3 {
  color: #1e3a8a; /* Example: a darker blue for headers */
}
.prose a {
  color: #3b82f6;
}
.prose a:hover {
  text-decoration: underline;
}
.prose ul {
    list-style-type: disc;
    padding-left: 1.5rem;
}
.prose ol {
    list-style-type: decimal;
    padding-left: 1.5rem;
}
</style>
