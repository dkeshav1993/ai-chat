<script setup lang="ts">
useHead({ title: 'Booking Confirmation — NexTrip AI' })
</script>

<template>
  <div class="page-root">
    <div class="bg-orb bg-orb-1" />
    <div class="bg-orb bg-orb-2" />

    <!-- Header -->
    <header class="app-header">
      <div class="header-inner">
        <NuxtLink to="/" class="back-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          Back to Search
        </NuxtLink>
        <div class="header-brand">
          <img src="/tc-logo.png" alt="Thomas Cook India" class="tc-logo-img" />
          <div>
            <span class="brand-name">NexTrip AI</span>
            <span class="brand-sub">powered by Thomas Cook India</span>
          </div>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="content-wrap">

        <!-- Icon -->
        <div class="icon-ring">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>

        <!-- Status badge -->
        <div class="status-badge">
          <span class="badge-dot" />
          Work in Progress
        </div>

        <!-- Heading -->
        <h1 class="confirm-title">Booking Received!</h1>
        <p class="confirm-sub">
          Thank you for your interest in booking with NexTrip AI.
        </p>

        <!-- Card -->
        <div class="confirm-card">
          <div class="card-icon-row">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <span class="card-icon-label">Booking Flow — Coming Soon</span>
          </div>
          <p class="card-body">
            The booking flow is currently <strong>work in progress</strong>. Our team is actively building
            the reservation, payment, and confirmation pipeline.
          </p>
          <p class="card-body">
            Please check back later — full end-to-end booking will be available soon!
          </p>
          <div class="card-divider" />
          <ul class="feature-list">
            <li class="feature-item">
              <span class="feature-dot feature-dot-done" />
              Hotel search &amp; AI recommendations
            </li>
            <li class="feature-item">
              <span class="feature-dot feature-dot-done" />
              Room availability &amp; details
            </li>
            <li class="feature-item">
              <span class="feature-dot feature-dot-soon" />
              Prebook &amp; payment processing
            </li>
            <li class="feature-item">
              <span class="feature-dot feature-dot-soon" />
              Booking confirmation &amp; e-voucher
            </li>
          </ul>
        </div>

        <!-- CTA -->
        <div class="cta-row">
          <NuxtLink to="/" class="cta-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            Start New Search
          </NuxtLink>
        </div>

      </div>
    </main>
  </div>
</template>

<style scoped>
.page-root {
  min-height: 100vh;
  background: var(--app-bg, #0A0F1E);
  display: flex; flex-direction: column;
  position: relative; overflow: hidden;
}
.bg-orb {
  position: fixed; border-radius: 50%;
  filter: blur(90px); pointer-events: none; z-index: 0;
}
.bg-orb-1 {
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(99,102,241,0.12) 0%, transparent 70%);
  top: -200px; right: -150px;
}
.bg-orb-2 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(245,158,11,0.09) 0%, transparent 70%);
  bottom: -100px; left: -150px;
}

.app-header {
  position: sticky; top: 0; z-index: 50;
  background: rgba(10,15,30,0.75);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.header-inner {
  max-width: 620px; margin: 0 auto; padding: 0 20px;
  height: 56px; display: flex; align-items: center; justify-content: space-between;
}
.back-btn {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 0.875rem; font-weight: 600;
  color: rgba(148,163,184,0.9); text-decoration: none; transition: color 0.2s;
}
.back-btn:hover { color: white; }
.header-brand {
  display: flex; align-items: center; gap: 8px;
  color: white;
}
.tc-logo-img { height: 30px; width: auto; object-fit: contain; flex-shrink: 0; filter: brightness(1.05) drop-shadow(0 0 3px rgba(255,255,255,0.12)); }
.brand-name { display: block; font-size: 0.9rem; font-weight: 700; color: white; line-height: 1.1; }
.brand-sub { display: block; font-size: 0.6rem; color: rgba(148,163,184,0.8); line-height: 1; }

.main-content {
  flex: 1; position: relative; z-index: 1;
  display: flex; align-items: center; justify-content: center;
  padding: 40px 20px;
}
.content-wrap {
  max-width: 520px; width: 100%;
  text-align: center;
}

/* Icon ring */
.icon-ring {
  width: 88px; height: 88px; margin: 0 auto 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #34D399, #059669);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 0 16px rgba(52,211,153,0.1), 0 0 0 32px rgba(52,211,153,0.04);
  animation: pulse-ring 2.5s ease-in-out infinite;
}
@keyframes pulse-ring {
  0%, 100% { box-shadow: 0 0 0 16px rgba(52,211,153,0.1), 0 0 0 32px rgba(52,211,153,0.04); }
  50% { box-shadow: 0 0 0 22px rgba(52,211,153,0.14), 0 0 0 40px rgba(52,211,153,0.06); }
}

.status-badge {
  display: inline-flex; align-items: center; gap: 7px;
  font-size: 0.72rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: #F59E0B;
  background: rgba(245,158,11,0.1);
  border: 1px solid rgba(245,158,11,0.25);
  padding: 4px 12px; border-radius: 20px;
  margin-bottom: 16px;
}
.badge-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #F59E0B;
  animation: badge-pulse 1.5s ease-in-out infinite;
}
@keyframes badge-pulse {
  0%, 100% { opacity: 1; } 50% { opacity: 0.4; }
}

.confirm-title {
  font-size: 2rem; font-weight: 800; color: white; margin: 0 0 8px;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.confirm-sub {
  font-size: 0.95rem; color: rgba(148,163,184,0.8);
  margin: 0 0 28px; line-height: 1.6;
}

/* Card */
.confirm-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 20px;
  backdrop-filter: blur(12px);
  padding: 24px; text-align: left;
  margin-bottom: 28px;
}
.card-icon-row {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 14px;
}
.card-icon-label {
  font-size: 0.9rem; font-weight: 700; color: #F59E0B;
}
.card-body {
  font-size: 0.875rem; color: rgba(203,213,225,0.85);
  line-height: 1.7; margin: 0 0 10px;
}
.card-body strong { color: white; }
.card-divider {
  border: none; border-top: 1px solid rgba(255,255,255,0.08);
  margin: 16px 0;
}
.feature-list {
  list-style: none; margin: 0; padding: 0;
  display: flex; flex-direction: column; gap: 10px;
}
.feature-item {
  display: flex; align-items: center; gap: 10px;
  font-size: 0.85rem; color: rgba(203,213,225,0.8);
}
.feature-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.feature-dot-done { background: #34D399; }
.feature-dot-soon { background: rgba(148,163,184,0.4); }

/* CTA */
.cta-row { display: flex; justify-content: center; }
.cta-primary {
  display: inline-flex; align-items: center; gap: 8px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: white; text-decoration: none;
  font-size: 0.9rem; font-weight: 700;
  padding: 14px 28px; border-radius: 12px;
  transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s;
  box-shadow: 0 4px 16px rgba(99,102,241,0.35);
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.cta-primary:hover { opacity: 0.9; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(99,102,241,0.5); }
.cta-primary:active { transform: translateY(0); }

@media (max-width: 768px) {
  .main-content { padding: 24px 12px; }
  .content-wrap { max-width: 100%; }
}
</style>

