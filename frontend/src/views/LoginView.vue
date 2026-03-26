<script setup lang="ts">
/**
 * Login / Session Selection View
 * 
 * Allows users to select their role (waiter/admin)
 * and log in to the system.
 */

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSessionsStore } from '@/stores/sessions'
import { useWaitersStore } from '@/stores/waiters'

// --------------------------------
// Setup
// --------------------------------

const router = useRouter()
const sessionsStore = useSessionsStore()
const waitersStore = useWaitersStore()
const ADMIN_PASSWORD = 'admin123'

// --------------------------------
// State
// --------------------------------

const selectedRole = ref<'waiter' | 'admin'>('waiter')
const selectedWaiterId = ref<string>('')
const adminPassword = ref('')
const loading = ref(false)
const error = ref<string | null>(null)

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
    return
  }

  // Load waiters if switching to waiter role
  if (selectedRole.value === 'waiter') {
    await waitersStore.fetchWaiters()
    if (!selectedWaiterId.value && waitersStore.activeWaiters.length > 0) {
      selectedWaiterId.value = waitersStore.activeWaiters[0].id
    }
  }
})

// --------------------------------
// Event Handlers
// --------------------------------

async function handleLogin() {
  error.value = null
  loading.value = true

  try {
    if (selectedRole.value === 'waiter') {
      await waitersStore.fetchWaiters()
      if (!selectedWaiterId.value && waitersStore.activeWaiters.length > 0) {
        selectedWaiterId.value = waitersStore.activeWaiters[0].id
      }
      if (!selectedWaiterId.value) {
        error.value = 'Please select a waiter'
        return
      }

      await sessionsStore.login('waiter', selectedWaiterId.value)
      router.push('/waiter')
    } else {
      // Admin login
      if (!adminPassword.value) {
        error.value = 'Please enter admin password'
        return
      }
      if (adminPassword.value !== ADMIN_PASSWORD) {
        error.value = 'Invalid admin password'
        return
      }

      await sessionsStore.login('admin', 'admin')
      router.push('/admin')
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Login failed'
  } finally {
    loading.value = false
  }
}

async function handleRoleChange(role: 'waiter' | 'admin') {
  selectedRole.value = role
  error.value = null
  selectedWaiterId.value = ''
  adminPassword.value = ''

  if (role === 'waiter') {
    await waitersStore.fetchWaiters()
    if (waitersStore.activeWaiters.length > 0) {
      selectedWaiterId.value = waitersStore.activeWaiters[0].id
    }
  }
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
        <label>Select Waiter</label>
        <select v-model="selectedWaiterId" :disabled="loading">
          <option value="">-- Choose a waiter --</option>
          <option v-for="waiter in waitersStore.activeWaiters" :key="waiter.id" :value="waiter.id">
            {{ waiter.name }}
          </option>
        </select>
      </div>

      <!-- Admin Login -->
      <div v-if="selectedRole === 'admin'" class="form-group">
        <label>Admin Password</label>
        <input
          v-model="adminPassword"
          type="password"
          placeholder="Enter password"
          :disabled="loading"
          @keyup.enter="handleLogin"
        />
        <small class="help-text">
          Demo password: <b>{{ ADMIN_PASSWORD }}</b>
        </small>
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
