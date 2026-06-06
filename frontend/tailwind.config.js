/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        'primary-hover': '#2563EB',
        secondary: '#60A5FA',
        accent: '#DC2626',
        'accent-hover': '#B91C1C',
        bg: '#0A0A0F',
        surface: '#111827',
        card: '#1F2937',
        border: '#374151',
        'text-base': '#F9FAFB',
        'text-muted': '#9CA3AF',
        success: '#10B981',
        warning: '#F59E0B',
        'error-color': '#EF4444',
        processing: '#8B5CF6',
      },
      fontFamily: {
        sans: ['"Fira Sans"', 'system-ui', 'sans-serif'],
        mono: ['"Fira Code"', 'monospace'],
      },
    },
  },
  plugins: [],
}
