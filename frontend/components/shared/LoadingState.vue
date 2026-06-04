<script setup lang="ts">
interface Props {
  message?: string
}

const props = withDefaults(defineProps<Props>(), {
  message: 'Loading...',
})
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-4 py-16">
    <div class="loader" />
    <p class="text-sm text-slate-400 font-medium tracking-wide">{{ props.message }}</p>
  </div>
</template>

<style scoped>
.loader {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, transparent 0%, #6366F1 100%);
  animation: spin 0.8s linear infinite;
  position: relative;
}
.loader::after {
  content: '';
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background: #0A0F1E;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
