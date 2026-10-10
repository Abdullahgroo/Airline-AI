/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        skyBrand: '#0ea5e9',
        navyBrand: '#0f172a',
        accentBrand: '#f59e0b',
      },
      boxShadow: {
        soft: '0 10px 30px rgba(14, 165, 233, 0.18)',
      },
    },
  },
  plugins: [],
};
