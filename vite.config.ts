import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [
    react(),
    {
      name: 'html-transform',
      transformIndexHtml(html) {
        // Transform index.html to use Vite's module system in dev
        return html.replace(
          /<script src="\/static\/dist\/bundle\.js"><\/script>/,
          '<script type="module" src="/src/main.tsx"></script>'
        ).replace(
          /href="\/static\/css\/styles\.css"/,
          'href="/css/styles.css"'
        );
      },
    },
  ],
  root: 'static',
  build: {
    outDir: 'dist',
    emptyOutDir: false, // Don't empty to preserve bundle.js
  },
  server: {
    port: 5173,
    open: false,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
});


