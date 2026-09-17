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
 * Set the document title and meta description/OG/twitter tags for the current
 * page. Keeps the tab title and social previews correct without a router plugin.
 * Pass `type: 'article'` and an `image` URL to emit richer cards for blog posts.
 */
export default function useSeo({ title, description, type = 'website', image }) {
  useEffect(() => {
    const full = title ? `${title} — ${SITE}` : `${SITE} — Full-stack SaaS engineer`
    document.title = full
    setMeta('name', 'description', description)
    setMeta('property', 'og:title', full)
    setMeta('property', 'og:description', description)
    setMeta('property', 'og:url', window.location.href)
    setMeta('property', 'og:type', type)
    setMeta('property', 'og:image', image)
    setMeta('name', 'twitter:card', image ? 'summary_large_image' : 'summary')
    setMeta('name', 'twitter:title', full)
    setMeta('name', 'twitter:description', description)
    setMeta('name', 'twitter:image', image)
  }, [title, description, type, image])
}
