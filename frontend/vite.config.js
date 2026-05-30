import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'sb-1sso8a9uvxux.vercel.run',
    ],
  },
});
