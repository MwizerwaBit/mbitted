import { useEffect } from 'react'

const SITE = 'MwizerwaBit'

function setMeta(attr, key, content) {
  let el = document.head.querySelector(`meta[${attr}="${key}"]`)
  if (!content) {
    if (el) el.remove()
    return
  }
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

/**
 * Set the document title and meta description/OG tags for the current page.
 * Keeps the tab title and social previews correct without a router plugin.
 */
export default function useSeo({ title, description }) {
  useEffect(() => {
    const full = title ? `${title} — ${SITE}` : `${SITE} — Full-stack SaaS engineer`
    document.title = full
    setMeta('name', 'description', description)
    setMeta('property', 'og:title', full)
    setMeta('property', 'og:description', description)
    setMeta('property', 'og:url', window.location.href)
  }, [title, description])
}
