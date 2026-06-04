<template>
  <NuxtPage />
</template>

<style>
:root {
  --font-sans: 'Inter', system-ui, sans-serif;
  --font-heading: 'Plus Jakarta Sans', 'Inter', system-ui, sans-serif;
  --app-bg: #0A0F1E;
  --app-bg-2: #0D1526;
  --glass-bg: rgba(255, 255, 255, 0.04);
  --glass-border: rgba(255, 255, 255, 0.08);
  --primary: #6366F1;
  --primary-dark: #4F46E5;
}

*, *::before, *::after {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-sans);
  background-color: var(--app-bg);
  color: #E2E8F0;
  margin: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1, h2, h3, h4, h5 {
  font-family: var(--font-heading);
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(99, 102, 241, 0.35);
  border-radius: 6px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 102, 241, 0.6);
}

/* Focus ring */
:focus-visible {
  outline: 2px solid #6366F1;
  outline-offset: 2px;
}

/* Selection */
::selection {
  background-color: rgba(99, 102, 241, 0.3);
  color: #fff;
}
</style>
