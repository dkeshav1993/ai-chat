<script setup lang="ts">
// No props — skeleton renders a fixed placeholder layout
</script>

<template>
  <div class="skel-card animate-pulse">
    <div class="skel-image" />
    <div class="skel-body">
      <div class="skel-line skel-line-lg" />
      <div class="skel-line skel-line-sm" />
      <div class="skel-line skel-line-md" />
      <div class="skel-btn" />
    </div>
  </div>
</template>

<style scoped>
.skel-card {
  background: rgba(255,255,255,0.06);
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.06);
}
.skel-image {
  height: 180px;
  background: rgba(255,255,255,0.08);
}
.skel-body {
  padding: 14px 16px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.skel-line {
  border-radius: 6px;
  background: rgba(255,255,255,0.08);
  height: 12px;
}
.skel-line-lg { width: 80%; height: 16px; }
.skel-line-md { width: 55%; }
.skel-line-sm { width: 35%; }
.skel-btn {
  height: 36px;
  border-radius: 10px;
  background: rgba(99,102,241,0.15);
  margin-top: 4px;
}
</style>
