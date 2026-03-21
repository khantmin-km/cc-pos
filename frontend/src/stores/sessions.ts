/**
 * Sessions Store (Pinia)
 * 
 * Manages user authentication and sessions.
 * Handles login/logout and current session state.
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

import type { ActorSession, SessionCreateRequest, UserRole } from '@/types/pos'
import { sessionsApi } from '@/services/tablesApi'

/**
 * Sessions Store
 */
export const useSessionsStore = defineStore('sessions', () => {
  // --------------------------------
  // State
  // --------------------------------

  /** Current active session */
  const currentSession = ref<ActorSession | null>(null)

  /** Loading state for async operations */
  const loading = ref(false)

  /** Error message from last operation */
  const error = ref<string | null>(null)

  // --------------------------------
  // Getters (Computed)
  // --------------------------------

  /** Check if user is logged in */
  const isLoggedIn = computed(() => currentSession.value !== null)

  /** Get current actor type */
  const actorType = computed<UserRole | null>(() => currentSession.value?.actorType ?? null)

  /** Get current actor name */
  const actorName = computed(() => currentSession.value?.actorName ?? 'Guest')

  /** Get current actor ID */
  const actorId = computed(() => currentSession.value?.actorId ?? null)

  // --------------------------------
  // Actions (Methods)
  // --------------------------------

  /**
   * Create a new session (login)
   * 
   * @param actorType - 'waiter' or 'admin'
   * @param actorId - Waiter/admin ID
   */
  async function login(actorType: UserRole, actorId: string) {
    loading.value = true
    error.value = null

    try {
      const session = await sessionsApi.create({
        actorType,
        actorId,
      })

      currentSession.value = session

      // Store in localStorage for persistence
      localStorage.setItem('currentSession', JSON.stringify(session))

      return session
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Login failed'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * End the current session (logout)
   */
  async function logout() {
    if (!currentSession.value) return

    loading.value = true
    error.value = null

    try {
      await sessionsApi.end(currentSession.value.id)
      currentSession.value = null
      localStorage.removeItem('currentSession')
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Logout failed'
      error.value = msg
      throw e
    } finally {
      loading.value = false
    }
  }

  /**
   * Restore session from localStorage
   */
  function restoreSession() {
    const stored = localStorage.getItem('currentSession')
    if (stored) {
      try {
        currentSession.value = JSON.parse(stored)
      } catch {
        localStorage.removeItem('currentSession')
      }
    }
  }

  /**
   * Clear session
   */
  function clearSession() {
    currentSession.value = null
    localStorage.removeItem('currentSession')
  }

  return {
    // State
    currentSession,
    loading,
    error,

    // Getters
    isLoggedIn,
    actorType,
    actorName,
    actorId,

    // Actions
    login,
    logout,
    restoreSession,
    clearSession,
  }
})
