const path = require('node:path');
const react = require('@vitejs/plugin-react');
const { defineConfig } = require('vitest/config.js');

const config = defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
      '@repo': path.resolve(__dirname, '../../packages'),
    },
  },
});

module.exports = config;
