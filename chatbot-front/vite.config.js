import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        entryFileNames: `chat-widget.js`,
        chunkFileNames: `chat-widget.js`,
        assetFileNames: `chat-widget.[ext]`
      }
    }
  }
})