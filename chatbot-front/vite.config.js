import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../AllokAcads/static',
    emptyOutDir: false,
    rollupOptions: {
      output: {
        entryFileNames: `js/chat-widget.js`,
        chunkFileNames: `js/chat-widget.js`,
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith('.css')) {
            return 'css/chat-widget.[ext]';
          }
          return 'assets/chat-widget.[ext]';
        }
      }
    }
  }
})