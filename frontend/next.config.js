/** @type {import('next').NextConfig} */
const withPWA = require('next-pwa')({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development', // Disable in dev for faster hot-reloading
  register: true,
  skipWaiting: true,
});

const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ["storage.googleapis.com"],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};

module.exports = withPWA(nextConfig);
