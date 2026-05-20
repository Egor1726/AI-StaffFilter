import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const proxyConfig = {
  '/api': {
    target: 'http://127.0.0.1:8080',
    changeOrigin: true,
    timeout: 600000,
    proxyTimeout: 600000,
  }
}

export default defineConfig({
  plugins: [react()],
  base: './',
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true,
    proxy: proxyConfig,
  },
  preview: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true,
    proxy: proxyConfig,
  }
})
