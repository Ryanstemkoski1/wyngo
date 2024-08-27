/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "templates/**/*.{html,js}",
    "accounts/templates/**/*.{html,js}",
    "shopper/templates/**/*.{html,js}",
    "articles/templates/**/*.{html,js}",
    "static/**/**/*.{js,css}",
  ],
  theme: {
    extend: {
      fontFamily: {
        mulish: ["Mulish", "sans-serif"],
      },
      colors: {
        "w-primary": "#59b293",
        "w-secondary": "#172a26",
        "w-blue": "#4852b3",
        "w-green": "#172a26",
        "w-dark-green": "#162b39",
        "w-indigo": "#4852b3",
        "w-light-gray": "#e0e0e0",
        "w-dark-gray": "#a6a6a6",
        "w-red": "#b25959",
        "w-yellow": "#fef8eb",
        "w-primary-dark": "#4d997e",
        "w-secondary-dark": "#4a4a4a",
        "w-grey": "#a6a6a6",
      },
    },
  },
  plugins: [require("daisyui"), require("@tailwindcss/forms"), require('@tailwindcss/typography')],
};
