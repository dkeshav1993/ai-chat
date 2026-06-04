<script setup lang="ts">
interface Props {
  title: string
  message: string
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  icon: '🏨',
})
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-4 py-20 text-center px-6 animate-fade-in">
    <div class="empty-icon">{{ props.icon }}</div>
    <div>
      <h3 class="text-lg font-semibold text-slate-200 mb-2">{{ props.title }}</h3>
      <p class="text-sm text-slate-400 max-w-sm leading-relaxed">{{ props.message }}</p>
    </div>
  </div>
</template>

<style scoped>
.empty-icon {
  font-size: 3.5rem;
  line-height: 1;
  filter: grayscale(0.3);
  animation: float 3s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}
</style>
