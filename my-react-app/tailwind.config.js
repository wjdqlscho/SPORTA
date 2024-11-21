module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'],
  theme: {
    extend: {
      colors: {
        primary: '#4F46E5', // 메인 색상 (보라색)
        secondary: '#818CF8', // 서브 색상
        accent: '#F59E0B', // 강조 색상
        background: '#F3F4F6', // 배경색
        dark: '#1E293B', // 다크 모드 색상
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'], // 기본 폰트
      },
      spacing: {
        128: '32rem',
        144: '36rem',
      },
      animation: {
        gradient: 'gradient 6s ease infinite', // 배경 움직이는 애니메이션
      },
      keyframes: {
        gradient: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography'), require('@tailwindcss/forms')],
};
