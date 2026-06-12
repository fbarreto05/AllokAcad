import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: resolve(__dirname, '../AllokAcads/static'),
    emptyOutDir: false,
    rollupOptions: {
      output: {
        entryFileNames: 'js/chat-widget.js',
        chunkFileNames: 'js/chat-widget.js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name?.endsWith('.css')) return 'css/chat-widget.css'
          return 'assets/[name].[ext]'
        },
      },
    },
  },
})