import { useCallback, useEffect, useState } from 'react'

function currentTheme() {
  if (typeof document === 'undefined') return 'light'
  return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light'
}

/**
 * Track and switch the app theme. The initial value is applied by an inline
 * script in index.html before paint; this hook keeps React state in sync and
 * persists explicit choices to localStorage.
 */
export default function useTheme() {
  const [theme, setTheme] = useState(currentTheme)

  useEffect(() => {
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const onChange = (e) => {
      // Follow the system only while the user hasn't made an explicit choice.
      try {
        if (!localStorage.getItem('theme')) setTheme(e.matches ? 'dark' : 'light')
      } catch {
        setTheme(e.matches ? 'dark' : 'light')
      }
    }
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])

  const set = useCallback((next) => {
    document.documentElement.dataset.theme = next
    try {
      localStorage.setItem('theme', next)
    } catch {
      // storage unavailable — still applies for this session
    }
    setTheme(next)
  }, [])

  const toggle = useCallback(() => {
    set(theme === 'dark' ? 'light' : 'dark')
  }, [theme, set])

  return { theme, set, toggle }
}
