/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            },
            colors: {
                primary: '#4F46E5', // Indigo 600
                secondary: '#64748B', // Slate 500
                accent: '#0EA5E9', // Sky 500
            }
        },
    },
    plugins: [],
}
