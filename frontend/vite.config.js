import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/static/',  // This ensures assets are loaded from the correct path
  build: {
    outDir: '../backend/static',  // Build directly to backend static directory
    emptyOutDir: true,
  }
})
