<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-header">
        <h1 class="auth-logo">RumorLens</h1>
        <p class="auth-tagline">Weibo Rumor Detection Platform</p>
      </div>
      <div class="auth-content">
        <RouterView />
      </div>
    </div>
    <div class="auth-decoration">
      <div class="decoration-text">
        <span class="decoration-number">01</span>
        <p class="decoration-label">Detect</p>
      </div>
      <div class="decoration-text">
        <span class="decoration-number">02</span>
        <p class="decoration-label">Analyze</p>
      </div>
      <div class="decoration-text">
        <span class="decoration-number">03</span>
        <p class="decoration-label">Verify</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
}

.auth-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: var(--space-16);
  max-width: 480px;
  margin: 0 auto;
}

.auth-header {
  margin-bottom: var(--space-12);
}

.auth-logo {
  font-family: var(--font-serif);
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-2);
}

.auth-tagline {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.auth-content {
  width: 100%;
}

.auth-decoration {
  background-color: var(--color-text);
  color: var(--color-bg);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: var(--space-16);
  gap: var(--space-12);
}

.decoration-text {
  display: flex;
  align-items: baseline;
  gap: var(--space-4);
}

.decoration-number {
  font-family: var(--font-serif);
  font-size: clamp(4rem, 8vw, 8rem);
  font-weight: var(--font-bold);
  opacity: 0.3;
  line-height: 1;
}

.decoration-label {
  font-size: var(--text-2xl);
  font-weight: var(--font-medium);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

@media (max-width: 768px) {
  .auth-layout {
    grid-template-columns: 1fr;
  }

  .auth-decoration {
    display: none;
  }

  .auth-container {
    padding: var(--space-8);
  }
}
</style>
