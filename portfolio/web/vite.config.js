import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy API + syndication routes to the FastAPI backend during local
// development, so the footer's /feed.xml link (and /sitemap.xml) resolve.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/feed.xml': 'http://localhost:8000',
      '/sitemap.xml': 'http://localhost:8000',
    },
  },
})
