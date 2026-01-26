/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Kid-friendly color palette
        sunshine: '#FFD93D',
        coral: '#FF6B6B',
        sky: '#4ECDC4',
        lavender: '#A78BFA',
        mint: '#6EE7B7',
        bubblegum: '#F472B6',
      },
      fontFamily: {
        fun: ['Comic Neue', 'Comic Sans MS', 'cursive'],
      },
    },
  },
  plugins: [],
}
