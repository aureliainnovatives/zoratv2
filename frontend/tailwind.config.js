/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#10a37f',
          hover: '#0e906f',
          dark: '#0d815f'
        },
        dark: {
          bg: '#202123',       // Main background
          panel: '#2d2d2d',    // Panel background
          border: '#4a4b4d',   // Border color
          text: '#c5c5d2',     // Regular text
          heading: '#ffffff'    // Headings
        },
        menu: {
          active: '#3dd6b3',    // Brighter teal for active state
          hover: '#34d399',     // Slightly dimmer teal for hover
          text: {
            light: '#666666',   // Brighter default text in light mode
            dark: '#f1f1f1',    // Brighter default text in dark mode
            active: '#10b981',  // Active text - vibrant teal
            hover: '#34d399'    // Hover text - softer teal
          },
          icon: {
            light: '#666666',   // Brighter default icon in light mode
            dark: '#A0A0A0',    // Brighter default icon in dark mode
            active: '#10b981',  // Active icon - vibrant teal
            hover: '#34d399'    // Hover icon - softer teal
          },
          bg: {
            active: 'rgba(16, 185, 129, 0.1)',  // Semi-transparent green for active background
            hover: 'rgba(52, 211, 153, 0.05)'   // Very subtle green for hover
          }
        }
      }
    }
  },
  plugins: [],
}

