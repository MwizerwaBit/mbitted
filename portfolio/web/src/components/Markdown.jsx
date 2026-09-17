import { useMemo } from 'react'
import { marked } from 'marked'

export default function Markdown({ text }) {
  const html = useMemo(() => marked.parse(text || ''), [text])
  return <div className="markdown" dangerouslySetInnerHTML={{ __html: html }} />
}
