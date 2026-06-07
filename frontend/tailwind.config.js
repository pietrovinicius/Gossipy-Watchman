/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Tokens fixos — iguais em ambos os temas
        primary: '#3B82F6',
        'primary-hover': '#2563EB',
        secondary: '#60A5FA',
        accent: '#DC2626',
        'accent-hover': '#B91C1C',
        success: '#10B981',
        warning: '#F59E0B',
        'error-color': '#EF4444',
        processing: '#8B5CF6',
        // Tokens de superfície/texto/borda — derivam de CSS custom
        // properties que trocam de valor conforme .dark/.light em <html>
        // (ver index.css). Permite suporte dual sem migrar classes
        // arquivo a arquivo — toda a base já usa estes nomes semânticos.
        bg: 'rgb(var(--color-bg) / <alpha-value>)',
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        card: 'rgb(var(--color-card) / <alpha-value>)',
        border: 'rgb(var(--color-border) / <alpha-value>)',
        'text-base': 'rgb(var(--color-text-base) / <alpha-value>)',
        'text-muted': 'rgb(var(--color-text-muted) / <alpha-value>)',
      },
      fontFamily: {
        sans: ['"Fira Sans"', 'system-ui', 'sans-serif'],
        mono: ['"Fira Code"', 'monospace'],
      },
    },
  },
  plugins: [],
}
