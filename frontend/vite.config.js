import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Use BACKEND_URL from env if available (useful for docker), otherwise localhost
const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
const wsBackendUrl = backendUrl.replace('http://', 'ws://').replace('https://', 'wss://')

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: backendUrl,
        changeOrigin: true,
      },
      '/ws': {
        target: wsBackendUrl,
        ws: true,
        changeOrigin: true,
      },
    },
  },
})
