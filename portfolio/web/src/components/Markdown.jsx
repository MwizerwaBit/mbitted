import { useMemo } from 'react'
import { marked } from 'marked'

// Dependency-free syntax highlighting for fenced code blocks. A single
// alternation scans left-to-right so tokens are never double-matched; the
// order (string → comment → number → keyword → function) resolves overlaps.

const KEYWORDS = [
  'def', 'class', 'return', 'if', 'elif', 'else', 'for', 'while', 'import',
  'from', 'as', 'try', 'except', 'finally', 'with', 'lambda', 'pass', 'break',
  'continue', 'raise', 'yield', 'async', 'await', 'in', 'not', 'and', 'or',
  'is', 'None', 'True', 'False', 'self', 'const', 'let', 'var', 'function',
  'new', 'typeof', 'export', 'default', 'this', 'null', 'undefined',
].sort((a, b) => b.length - a.length)

const STRING = String.raw`"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'`
const COMMENT = String.raw`//[^\n]*|#[^\n]*`
const NUMBER = String.raw`\b\d+(?:\.\d+)?\b`
const KEYWORD = String.raw`\b(?:${KEYWORDS.join('|')})\b`
const FUNCTION = String.raw`[A-Za-z_][A-Za-z0-9_]*(?=\()`

const TOKEN_RE = new RegExp(
  `(${STRING})|(${COMMENT})|(${NUMBER})|(${KEYWORD})|(${FUNCTION})`,
  'g',
)

const HIGHLIGHTABLE = /^(py|python|js|javascript|ts|typescript|tsx|jsx|json|bash|sh|shell|css|html|sql)$/i

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

function highlight(src) {
  return escapeHtml(src).replace(TOKEN_RE, (m, str, com, num, kw) => {
    if (str) return `<span class="tok-str">${m}</span>`
    if (com) return `<span class="tok-com">${m}</span>`
    if (num) return `<span class="tok-num">${m}</span>`
    if (kw) return `<span class="tok-kw">${m}</span>`
    return `<span class="tok-fn">${m}</span>`
  })
}

// Custom code renderer for `marked` v12 (positional `code(text, lang)`).
const renderer = {
  code(code, lang) {
    const inner = HIGHLIGHTABLE.test(lang || '') ? highlight(code) : escapeHtml(code)
    return `<pre><code class="language-${escapeHtml(lang || '')}">${inner}</code></pre>`
  },
}

marked.use({ renderer })

export default function Markdown({ text }) {
  const html = useMemo(() => marked.parse(text || ''), [text])
  return <div className="markdown" dangerouslySetInnerHTML={{ __html: html }} />
}
