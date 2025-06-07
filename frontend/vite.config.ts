import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import electron from 'vite-plugin-electron'
import renderer from 'vite-plugin-electron-renderer'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ command }) => {
  const isServe = command === 'serve'
  const isBuild = command === 'build'
  const isElectron = process.env.ELECTRON === 'true'

  return {
    plugins: [
      react(),
      // Only enable PWA for web builds, not Electron
      ...(!isElectron ? [
        VitePWA({
          registerType: 'autoUpdate',
          workbox: {
            globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}']
          },
          includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
          manifest: {
            name: 'Jenna Voice Assistant',
            short_name: 'Jenna',
            description: 'Commercial-grade desktop voice assistant',
            theme_color: '#1e40af',
            background_color: '#0f172a',
            display: 'standalone',
            orientation: 'portrait',
            scope: '/',
            start_url: '/',
            icons: [
              {
                src: 'pwa-192x192.png',
                sizes: '192x192',
                type: 'image/png'
              },
              {
                src: 'pwa-512x512.png',
                sizes: '512x512',
                type: 'image/png'
              },
              {
                src: 'pwa-512x512.png',
                sizes: '512x512',
                type: 'image/png',
                purpose: 'any maskable'
              }
            ]
          }
        })
      ] : []),
      // Add Electron support when building for Electron
      ...(isElectron ? [
        electron([
          {
            // Main process
            entry: 'electron/main.js',
            onstart({ startup }) {
              if (process.env.VITE_DEV_SERVER_URL) {
                startup()
              }
            },
            vite: {
              build: {
                outDir: 'dist_electron',
                minify: isBuild,
                rollupOptions: {
                  external: ['electron']
                }
              }
            }
          },
          {
            // Preload process
            entry: 'electron/preload.js',
            onstart({ reload }) {
              reload()
            },
            vite: {
              build: {
                outDir: 'dist_electron',
                minify: isBuild
              }
            }
          }
        ]),
        renderer()
      ] : [])
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        '@components': path.resolve(__dirname, './src/components'),
        '@pages': path.resolve(__dirname, './src/pages'),
        '@hooks': path.resolve(__dirname, './src/hooks'),
        '@utils': path.resolve(__dirname, './src/utils'),
        '@types': path.resolve(__dirname, './src/types'),
        '@store': path.resolve(__dirname, './src/store'),
        '@api': path.resolve(__dirname, './src/api'),
        '@assets': path.resolve(__dirname, './src/assets'),
        '@proto': path.resolve(__dirname, './src/proto')
      }
    },
    server: {
      port: 3000,
      host: true,
      proxy: {
        '/api': {
          target: 'http://localhost:8080',
          changeOrigin: true,
          secure: false
        },
        '/ws': {
          target: 'ws://localhost:8080',
          ws: true,
          changeOrigin: true
        }
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: process.env.NODE_ENV !== 'production',
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: process.env.NODE_ENV === 'production',
          drop_debugger: process.env.NODE_ENV === 'production'
        }
      },
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            router: ['react-router-dom'],
            ui: ['framer-motion', '@headlessui/react', '@heroicons/react'],
            utils: ['axios', 'date-fns', 'clsx', 'tailwind-merge']
          }
        }
      },
      chunkSizeWarningLimit: 1000
    },
    preview: {
      port: 3000,
      host: true
    },
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
      __BUILD_DATE__: JSON.stringify(new Date().toISOString()),
      __IS_ELECTRON__: isElectron
    }
  }
})