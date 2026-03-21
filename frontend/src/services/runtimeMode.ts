export type RuntimeMode = 'live' | 'demo'

const KEY = 'ccpos_runtime_mode'

export function getRuntimeMode(): RuntimeMode {
  const v = localStorage.getItem(KEY)
  // Default to demo mode
  return v === 'live' ? 'live' : 'demo'
}

export function setRuntimeMode(mode: RuntimeMode) {
  localStorage.setItem(KEY, mode)
  window.dispatchEvent(new CustomEvent('ccpos:mode', { detail: mode }))
}

export function onRuntimeModeChange(cb: (mode: RuntimeMode) => void) {
  const handler = (e: Event) => {
    const ce = e as CustomEvent<RuntimeMode>
    cb(ce.detail)
  }
  window.addEventListener('ccpos:mode', handler)
  return () => window.removeEventListener('ccpos:mode', handler)
}

