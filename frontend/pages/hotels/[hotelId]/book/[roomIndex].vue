<script setup lang="ts">
import { useRoomDetails } from '~/composables/useRoomDetails'
import { useSessionId } from '~/composables/useSessionId'

const route = useRoute()
const hotelId = route.params.hotelId as string
const roomIndex = parseInt(route.params.roomIndex as string, 10)

const sessionId = ref('')
const { rooms, roomState, fetchRoomDetails } = useRoomDetails()

onMounted(() => {
  sessionId.value = useSessionId()
  fetchRoomDetails(hotelId, sessionId.value)
})

const selectedRoom = computed(() => rooms.value[roomIndex] ?? null)
const roomName = computed(() => selectedRoom.value?.standardName ?? `Room ${roomIndex + 1}`)

// ─── Form State ───────────────────────────────────────────────────────────────
const form = reactive({
  title: '',
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  dob: '',
  pan: '',
})

const panVerified = ref(false)
const panVerifying = ref(false)
const submitted = ref(false)

// ─── Validation Patterns ─────────────────────────────────────────────────────
const TITLES = ['Mr', 'Mrs', 'Ms', 'Dr', 'Prof']

const PATTERNS = {
  name:  /^[A-Za-z\s.\-']{1,255}$/,
  email: /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/,
  phone: /^[6-9]\d{9}$/,           // Indian mobile: 10 digits starting 6-9
  dob:   /^\d{4}-\d{2}-\d{2}$/,    // YYYY-MM-DD
  pan:   /^[A-Z]{5}[0-9]{4}[A-Z]$/,
}

const FIELD_LIMITS = {
  firstName: 255,
  lastName:  255,
  email:     254,
  phone:     10,
  pan:       10,
}

interface FieldErrors {
  title?: string
  firstName?: string
  lastName?: string
  email?: string
  phone?: string
  dob?: string
  pan?: string
}

const errors = reactive<FieldErrors>({})

function validateField(field: keyof FieldErrors) {
  switch (field) {
    case 'title':
      errors.title = form.title ? undefined : 'Title is required'
      break
    case 'firstName':
      if (!form.firstName.trim()) {
        errors.firstName = 'First name is required'
      } else if (!PATTERNS.name.test(form.firstName)) {
        errors.firstName = 'Only letters, spaces, hyphens and dots allowed (max 255)'
      } else {
        errors.firstName = undefined
      }
      break
    case 'lastName':
      if (!form.lastName.trim()) {
        errors.lastName = 'Last name is required'
      } else if (!PATTERNS.name.test(form.lastName)) {
        errors.lastName = 'Only letters, spaces, hyphens and dots allowed (max 255)'
      } else {
        errors.lastName = undefined
      }
      break
    case 'email':
      if (!form.email.trim()) {
        errors.email = 'Email is required'
      } else if (!PATTERNS.email.test(form.email)) {
        errors.email = 'Enter a valid email address'
      } else {
        errors.email = undefined
      }
      break
    case 'phone':
      if (!form.phone.trim()) {
        errors.phone = 'Mobile number is required'
      } else if (!PATTERNS.phone.test(form.phone)) {
        errors.phone = '10-digit Indian mobile number required (starts with 6-9)'
      } else {
        errors.phone = undefined
      }
      break
    case 'dob':
      if (!form.dob) {
        errors.dob = 'Date of birth is required'
      } else {
        const d = new Date(form.dob)
        const today = new Date()
        if (isNaN(d.getTime())) {
          errors.dob = 'Enter a valid date'
        } else if (d >= today) {
          errors.dob = 'Date of birth must be in the past'
        } else {
          errors.dob = undefined
        }
      }
      break
    case 'pan':
      if (!form.pan.trim()) {
        errors.pan = 'PAN number is required'
      } else if (!PATTERNS.pan.test(form.pan.toUpperCase())) {
        errors.pan = 'Invalid PAN format (e.g. ABCDE1234F)'
      } else {
        errors.pan = undefined
      }
      break
  }
}

function validateAll(): boolean {
  const fields: (keyof FieldErrors)[] = ['title', 'firstName', 'lastName', 'email', 'phone', 'dob', 'pan']
  fields.forEach(validateField)
  return !Object.values(errors).some(Boolean)
}

// PAN verify — placeholder for real API
async function verifyPan() {
  validateField('pan')
  if (errors.pan) return
  panVerifying.value = true
  await new Promise(r => setTimeout(r, 800))   // simulate API latency
  panVerifying.value = false
  panVerified.value = true
}

// Reset PAN verified when PAN changes
watch(() => form.pan, () => { panVerified.value = false })

function handleSubmit() {
  submitted.value = true
  if (!validateAll()) return
  navigateTo('/booking/confirmation')
}
</script>

<template>
  <div class="page-root">
    <div class="bg-orb bg-orb-1" />
    <div class="bg-orb bg-orb-2" />

    <!-- Header -->
    <header class="app-header">
      <div class="header-inner">
        <NuxtLink :to="`/hotels/${hotelId}/rooms`" class="back-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
          Back to Rooms
        </NuxtLink>
        <div class="header-brand">
          <div class="brand-icon">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="white"><path d="M21 16v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><rect x="6" y="16" width="12" height="5" rx="2" fill="white"/></svg>
          </div>
          <span>NexTrip AI</span>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="content-wrap">

        <!-- Page title -->
        <div class="page-heading">
          <div class="heading-badge">Step 1 of 2 · Traveller Details</div>
          <h1 class="page-title">Complete Your Booking</h1>
          <p v-if="roomName" class="page-sub">
            <span class="room-label">Selected Room:</span> {{ roomName }}
          </p>
        </div>

        <!-- Form card -->
        <div class="form-card">
          <div class="form-section-title">Lead Passenger Details</div>
          <p class="form-hint">All fields are mandatory. Enter details exactly as on your government ID.</p>

          <form novalidate @submit.prevent="handleSubmit">

            <!-- Title -->
            <div class="field-group">
              <label class="field-label">Title <span class="required">*</span></label>
              <div class="radio-row">
                <label
                  v-for="t in TITLES"
                  :key="t"
                  class="radio-option"
                  :class="{ selected: form.title === t }"
                >
                  <input
                    v-model="form.title"
                    type="radio"
                    :value="t"
                    class="radio-input"
                    @change="validateField('title')"
                  />
                  {{ t }}
                </label>
              </div>
              <p v-if="submitted && errors.title" class="field-error">{{ errors.title }}</p>
            </div>

            <!-- First + Last Name -->
            <div class="field-row">
              <div class="field-group">
                <label class="field-label" for="firstName">First Name <span class="required">*</span></label>
                <input
                  id="firstName"
                  v-model="form.firstName"
                  type="text"
                  class="field-input"
                  :class="{ 'field-error-input': submitted && errors.firstName }"
                  placeholder="e.g. Aanya"
                  maxlength="255"
                  autocomplete="given-name"
                  @blur="validateField('firstName')"
                />
                <p v-if="submitted && errors.firstName" class="field-error">{{ errors.firstName }}</p>
              </div>
              <div class="field-group">
                <label class="field-label" for="lastName">Last Name <span class="required">*</span></label>
                <input
                  id="lastName"
                  v-model="form.lastName"
                  type="text"
                  class="field-input"
                  :class="{ 'field-error-input': submitted && errors.lastName }"
                  placeholder="e.g. Sharma"
                  maxlength="255"
                  autocomplete="family-name"
                  @blur="validateField('lastName')"
                />
                <p v-if="submitted && errors.lastName" class="field-error">{{ errors.lastName }}</p>
              </div>
            </div>

            <!-- Email -->
            <div class="field-group">
              <label class="field-label" for="email">Email Address <span class="required">*</span></label>
              <input
                id="email"
                v-model="form.email"
                type="email"
                class="field-input"
                :class="{ 'field-error-input': submitted && errors.email }"
                placeholder="e.g. aanya@email.com"
                maxlength="254"
                autocomplete="email"
                @blur="validateField('email')"
              />
              <p v-if="submitted && errors.email" class="field-error">{{ errors.email }}</p>
            </div>

            <!-- Phone -->
            <div class="field-group">
              <label class="field-label" for="phone">Mobile Number <span class="required">*</span></label>
              <div class="phone-wrap">
                <span class="phone-prefix">+91</span>
                <input
                  id="phone"
                  v-model="form.phone"
                  type="tel"
                  class="field-input phone-input"
                  :class="{ 'field-error-input': submitted && errors.phone }"
                  placeholder="9876543210"
                  maxlength="10"
                  pattern="[6-9][0-9]{9}"
                  autocomplete="tel"
                  @blur="validateField('phone')"
                />
              </div>
              <p v-if="submitted && errors.phone" class="field-error">{{ errors.phone }}</p>
            </div>

            <!-- Date of Birth -->
            <div class="field-group">
              <label class="field-label" for="dob">Date of Birth <span class="required">*</span></label>
              <input
                id="dob"
                v-model="form.dob"
                type="date"
                class="field-input"
                :class="{ 'field-error-input': submitted && errors.dob }"
                :max="new Date().toISOString().split('T')[0]"
                autocomplete="bday"
                @blur="validateField('dob')"
              />
              <p v-if="submitted && errors.dob" class="field-error">{{ errors.dob }}</p>
            </div>

            <!-- PAN Number -->
            <div class="field-group">
              <label class="field-label" for="pan">PAN Number <span class="required">*</span></label>
              <div class="pan-wrap">
                <input
                  id="pan"
                  v-model="form.pan"
                  type="text"
                  class="field-input pan-input"
                  :class="{ 'field-error-input': submitted && errors.pan, 'field-verified': panVerified }"
                  placeholder="ABCDE1234F"
                  maxlength="10"
                  style="text-transform: uppercase"
                  @blur="validateField('pan')"
                />
                <button
                  v-if="!panVerified"
                  type="button"
                  class="pan-verify-btn"
                  :disabled="panVerifying"
                  @click="verifyPan"
                >
                  <span v-if="panVerifying" class="verify-spinner" />
                  <span v-else>Verify</span>
                </button>
                <span v-if="panVerified" class="pan-verified-badge">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                  Verified
                </span>
              </div>
              <p v-if="submitted && errors.pan" class="field-error">{{ errors.pan }}</p>
              <p class="field-hint">Format: 5 letters + 4 digits + 1 letter (e.g. ABCDE1234F)</p>
            </div>

            <!-- Submit -->
            <div class="submit-wrap">
              <button type="submit" class="book-now-btn">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                Book Now
              </button>
              <p class="submit-note">By continuing you agree to our terms of service and privacy policy.</p>
            </div>

          </form>
        </div>

      </div>
    </main>
  </div>
</template>

<style scoped>
.page-root {
  min-height: 100vh;
  background: var(--app-bg, #0A0F1E);
  position: relative;
  overflow-x: hidden;
}
.bg-orb {
  position: fixed; border-radius: 50%;
  filter: blur(80px); pointer-events: none; z-index: 0;
}
.bg-orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%);
  top: -150px; right: -100px;
}
.bg-orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(245,158,11,0.08) 0%, transparent 70%);
  bottom: 0; left: -100px;
}

.app-header {
  position: sticky; top: 0; z-index: 50;
  background: rgba(10,15,30,0.75);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.header-inner {
  max-width: 700px; margin: 0 auto; padding: 0 20px;
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
  font-size: 0.875rem; font-weight: 700; color: white;
}
.brand-icon {
  width: 28px; height: 28px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
}

.main-content {
  position: relative; z-index: 1;
  padding: 28px 20px 60px;
}
.content-wrap { max-width: 700px; margin: 0 auto; }

/* Heading */
.page-heading { margin-bottom: 24px; }
.heading-badge {
  display: inline-block;
  font-size: 0.72rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: #8B5CF6; background: rgba(139,92,246,0.12);
  border: 1px solid rgba(139,92,246,0.25);
  padding: 4px 12px; border-radius: 20px; margin-bottom: 10px;
}
.page-title {
  font-size: 1.75rem; font-weight: 800; color: white;
  margin: 0 0 6px; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.page-sub { font-size: 0.9rem; color: rgba(148,163,184,0.85); margin: 0; }
.room-label { font-weight: 600; color: #F59E0B; }

/* Form card */
.form-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  backdrop-filter: blur(12px);
  padding: 28px;
}
.form-section-title {
  font-size: 1rem; font-weight: 700;
  color: white; margin-bottom: 4px;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.form-hint {
  font-size: 0.8rem; color: rgba(148,163,184,0.7);
  margin: 0 0 24px; line-height: 1.5;
}

/* Fields */
.field-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
}
@media (max-width: 480px) {
  .field-row { grid-template-columns: 1fr; }
}
.field-group { margin-bottom: 18px; }
.field-label {
  display: block; font-size: 0.82rem; font-weight: 600;
  color: rgba(226,232,240,0.85); margin-bottom: 6px;
}
.required { color: #F87171; }
.field-input {
  width: 100%; box-sizing: border-box;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px;
  color: white; font-size: 0.9rem;
  padding: 10px 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: 'Inter', sans-serif;
  outline: none;
}
.field-input::placeholder { color: rgba(148,163,184,0.5); }
.field-input:focus {
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.18);
}
.field-error-input {
  border-color: #F87171 !important;
  box-shadow: 0 0 0 3px rgba(248,113,113,0.15) !important;
}
.field-verified {
  border-color: #34D399 !important;
  box-shadow: 0 0 0 3px rgba(52,211,153,0.15) !important;
}
.field-error {
  font-size: 0.75rem; color: #F87171;
  margin: 5px 0 0; line-height: 1.4;
}
.field-hint {
  font-size: 0.72rem; color: rgba(148,163,184,0.6);
  margin: 5px 0 0;
}

/* Title radios */
.radio-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 4px; }
.radio-option {
  display: inline-flex; align-items: center;
  cursor: pointer;
  border: 1.5px solid rgba(255,255,255,0.12);
  border-radius: 8px;
  padding: 7px 14px;
  font-size: 0.82rem; font-weight: 500;
  color: rgba(226,232,240,0.8);
  background: rgba(255,255,255,0.04);
  transition: all 0.2s;
  user-select: none;
}
.radio-option.selected {
  border-color: #6366F1;
  background: rgba(99,102,241,0.15);
  color: #A5B4FC;
}
.radio-input { display: none; }

/* Phone */
.phone-wrap { display: flex; align-items: center; }
.phone-prefix {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-right: none;
  border-radius: 10px 0 0 10px;
  padding: 10px 12px;
  font-size: 0.9rem; color: rgba(148,163,184,0.8);
  white-space: nowrap; flex-shrink: 0;
}
.phone-input { border-radius: 0 10px 10px 0 !important; }

/* PAN */
.pan-wrap { display: flex; align-items: center; gap: 10px; }
.pan-input { flex: 1; }
.pan-verify-btn {
  flex-shrink: 0;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: white; border: none; border-radius: 8px;
  padding: 10px 18px; font-size: 0.82rem; font-weight: 600;
  cursor: pointer; transition: opacity 0.2s;
  display: flex; align-items: center; gap: 6px;
  font-family: 'Inter', sans-serif;
  min-width: 80px; justify-content: center;
}
.pan-verify-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.pan-verify-btn:hover:not(:disabled) { opacity: 0.88; }
.verify-spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.pan-verified-badge {
  flex-shrink: 0;
  display: flex; align-items: center; gap: 5px;
  font-size: 0.82rem; font-weight: 600;
  color: #34D399;
  background: rgba(52,211,153,0.12);
  border: 1px solid rgba(52,211,153,0.3);
  border-radius: 8px;
  padding: 8px 14px;
  white-space: nowrap;
}

/* Submit */
.submit-wrap { margin-top: 8px; }
.book-now-btn {
  display: flex; align-items: center; justify-content: center; gap: 10px;
  width: 100%;
  background: linear-gradient(135deg, #F59E0B, #D97706);
  color: white; font-size: 1rem; font-weight: 700;
  padding: 16px; border-radius: 14px; border: none; cursor: pointer;
  transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s;
  font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
  box-shadow: 0 4px 16px rgba(245,158,11,0.35);
  letter-spacing: 0.01em;
}
.book-now-btn:hover { opacity: 0.93; transform: translateY(-2px); box-shadow: 0 8px 24px rgba(245,158,11,0.45); }
.book-now-btn:active { transform: translateY(0); }
.submit-note {
  text-align: center; font-size: 0.72rem;
  color: rgba(148,163,184,0.55); margin: 10px 0 0;
}
</style>
