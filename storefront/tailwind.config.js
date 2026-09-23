/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#F8F5F2',
        surface: '#FFFFFF',
        accent: '#D8B2A9',
      }
    },
  },
  plugins: [],
}
