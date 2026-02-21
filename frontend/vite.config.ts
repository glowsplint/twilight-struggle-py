import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath } from 'url'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  base: '',
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    assetsDir: 'static',
    outDir: 'dist',
  },
  server: {
    port: 8080,
    proxy: {
      '/socket.io': {
        target: 'http://localhost:5000',
        ws: true,
      },
    },
  },
})
