/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        tarang: {
          bg: '#F7FAFC',
          navy: '#102A43',
          teal: '#087F8C',
          blue: '#3978CF',
          strong: '#168A5B',
          fair: '#D99C26',
          weak: '#D95D54',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
