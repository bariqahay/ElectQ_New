/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/backend/templates/**/*.{html,js}'], // Fix di sini
  theme: {
    extend: {
      fontFamily: {
        poppins: ['Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
