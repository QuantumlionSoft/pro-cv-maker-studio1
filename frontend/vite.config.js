import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const API_TARGET = process.env.VITE_API_TARGET || 'http://127.0.0.1:8000'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    allowedHosts: true,
    proxy: {
      // The browser talks only to the Vite origin. Requests are forwarded to Django.
      // Origin is rewritten to the Django origin so Django's CSRF origin check passes
      // whether the app is opened on localhost or through a forwarded preview host.
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
        configure(proxy) {
          proxy.on('proxyReq', (proxyReq) => {
            if (proxyReq.getHeader('origin')) proxyReq.setHeader('origin', API_TARGET)
          })
        },
      },
    },
  },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.test.js'],
  },
})
