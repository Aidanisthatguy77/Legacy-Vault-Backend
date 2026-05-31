/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: '#C8102E',
        'primary-hover': '#9e0c24',
        'deep-red': '#8B0000',
        'card-black': '#09090B',
      },
      fontFamily: {
        heading: ['Arial', 'sans-serif'],
      }
    },
  },
  plugins: [],
}