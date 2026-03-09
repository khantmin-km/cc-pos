export type RuntimeMode = 'live' | 'demo'

const KEY = 'ccpos_runtime_mode'

export function getRuntimeMode(): RuntimeMode {
  const v = localStorage.getItem(KEY)
  return v === 'demo' ? 'demo' : 'live'
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

