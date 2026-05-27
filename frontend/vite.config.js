import { resolve } from 'path'
import tailwindcss from '@tailwindcss/vite'

export default {
  plugins: [tailwindcss()],
  build: {
    outDir: resolve(__dirname, '../assets/static'),
    emptyOutDir: false,
    rollupOptions: {
      input: {
        site:     resolve(__dirname, 'src/site.js'),
        workshop: resolve(__dirname, 'src/workshop.js'),
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name]-chunk.js',
        assetFileNames: '[name].[ext]',
      },
    },
  },
}
