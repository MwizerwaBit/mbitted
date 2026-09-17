import { useEffect, useRef } from 'react'

/**
 * Thin fixed bar at the very top showing reading/scroll progress.
 * Uses a passive scroll listener + requestAnimationFrame (cheap, no layout
 * thrash). Purely decorative (aria-hidden) and disabled under reduced motion.
 */
export default function ScrollProgress() {
  const barRef = useRef(null)

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const bar = barRef.current
    if (!bar) return

    let ticking = false
    const update = () => {
      const doc = document.documentElement
      const max = doc.scrollHeight - doc.clientHeight
      const ratio = max > 0 ? doc.scrollTop / max : 0
      bar.style.transform = `scaleX(${ratio})`
      ticking = false
    }
    const onScroll = () => {
      if (!ticking) {
        ticking = true
        requestAnimationFrame(update)
      }
    }

    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onScroll)
    }
  }, [])

  return (
    <div className="scroll-progress" aria-hidden="true">
      <div ref={barRef} className="scroll-progress-bar" />
    </div>
  )
}
