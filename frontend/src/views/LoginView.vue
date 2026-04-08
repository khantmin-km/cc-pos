<script setup lang="ts">
/**
 * Login / Session Selection View
 * 
 * Allows users to select their role (waiter/admin)
 * and log in with username/PIN credentials.
 */

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/sessions'

// --------------------------------
// Setup
// --------------------------------

const router = useRouter()
const sessionsStore = useSessionsStore()

// --------------------------------
// State
// --------------------------------

const selectedRole = ref<'waiter' | 'admin'>('waiter')
const username = ref('')
const pin = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

// Demo credentials hint
const demoUsername = ref(false)

// --------------------------------
// Lifecycle
// --------------------------------

onMounted(async () => {
  // If already logged in, redirect to appropriate page
  if (sessionsStore.isLoggedIn) {
    const role = sessionsStore.actorType
    router.push(role === 'admin' ? '/admin' : '/waiter')
    return
  }

  // Restore session from localStorage if available
  sessionsStore.restoreSession()
  if (sessionsStore.isLoggedIn) {
    const role = sessionsStore.actorType
    router.push(role === 'admin' ? '/admin' : '/waiter')
  }
})

// --------------------------------
// Computed
// --------------------------------

const showDemoHint = () => {
  if (selectedRole.value === 'admin') {
    return '(Demo: PIN 1234)'
  } else {
    return '(Demo: waiter1, waiter2, waiter3 with PINs 1111, 2222, 3333)'
  }
}

// --------------------------------
// Event Handlers
// --------------------------------

async function handleLogin() {
  error.value = null
  loading.value = true

  try {
    if (selectedRole.value === 'waiter') {
      if (!username.value) {
        error.value = 'Please enter waiter username'
        return
      }
      if (!pin.value) {
        error.value = 'Please enter waiter PIN'
        return
      }

      // For waiter login, use the username and PIN combination
      await sessionsStore.login('waiter', username.value, pin.value)
      router.push('/waiter')
    } else {
      // Admin login
      if (!pin.value) {
        error.value = 'Please enter admin PIN'
        return
      }

      // For admin login, pass type and PIN
      await sessionsStore.login('admin', 'admin', pin.value)
      router.push('/admin')
    }
  } catch (e) {
    if (!error.value) {
      error.value = e instanceof Error ? e.message : 'Login failed'
    }
  } finally {
    loading.value = false
  }
}

async function handleRoleChange(role: 'waiter' | 'admin') {
  selectedRole.value = role
  error.value = null
  username.value = ''
  pin.value = ''
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">CC POS System</h1>
      <p class="subtitle">Login to continue</p>

      <!-- Role Selection -->
      <div class="role-selector">
        <button
          class="role-btn"
          :class="{ active: selectedRole === 'waiter' }"
          @click="handleRoleChange('waiter')"
          :disabled="loading"
        >
          👨‍🍳 Waiter
        </button>
        <button
          class="role-btn"
          :class="{ active: selectedRole === 'admin' }"
          @click="handleRoleChange('admin')"
          :disabled="loading"
        >
          🔑 Admin
        </button>
      </div>

      <!-- Waiter Login -->
      <div v-if="selectedRole === 'waiter'" class="form-group">
        <label>Waiter Username</label>
        <input
          v-model="username"
          type="text"
          placeholder="e.g., waiter1"
          class="text-input"
        />
        <small class="hint">{{ showDemoHint() }}</small>
      </div>

      <!-- PIN Input (for both Waiter and Admin) -->
      <div class="form-group">
        <label>{{ selectedRole === 'admin' ? 'Admin PIN' : 'Waiter PIN' }}</label>
        <input
          v-model="pin"
          type="password"
          placeholder="Enter PIN"
          class="pin-input"
          @keyup.enter="handleLogin"
        />
        <small v-if="selectedRole === 'admin'" class="hint">{{ showDemoHint() }}</small>
        <small v-else class="hint">{{ showDemoHint() }}</small>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <!-- Login Button -->
      <button class="login-btn" @click="handleLogin" :disabled="loading">
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.title {
  font-size: 32px;
  font-weight: 900;
  margin: 0 0 8px;
  color: #1e293b;
  text-align: center;
}

.subtitle {
  font-size: 14px;
  color: #64748b;
  text-align: center;
  margin: 0 0 32px;
}

.role-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 32px;
}

.role-btn {
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  font-size: 14px;
}

.role-btn:hover:not(:disabled) {
  border-color: #667eea;
  background: #f0f4ff;
}

.role-btn.active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.role-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1e293b;
  font-size: 14px;
}

.form-group select,
.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.text-input,
.pin-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.text-input:focus,
.pin-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.hint {
  display: block;
  margin-top: 6px;
  color: #64748b;
  font-size: 12px;
}

.form-group select:focus,
.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group select:disabled,
.form-group input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.help-text {
  display: block;
  margin-top: 6px;
  color: #64748b;
  font-size: 12px;
}

.error-message {
  background: #fee2e2;
  color: #dc2626;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 14px;
}

.login-btn {
  width: 100%;
  padding: 12px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 16px;
}

.login-btn:hover:not(:disabled) {
  background: #5568d3;
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
