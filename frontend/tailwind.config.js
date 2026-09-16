/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: { extend: {
    colors: { ink: '#15211d', muted: '#6f7b76', line: '#e6e9e7', canvas: '#f5f7f6', brand: '#235c49', lime: '#d9f275', danger: '#dd5c54' },
    boxShadow: { card: '0 1px 2px rgba(18, 34, 28, .04), 0 10px 30px rgba(18, 34, 28, .035)' },
    fontFamily: { sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'] },
  } },
  plugins: [],
}
