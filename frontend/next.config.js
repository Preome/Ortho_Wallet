/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  // Disable static optimization for dynamic routes
  trailingSlash: true,
  // Increase build timeouts
  staticPageGenerationTimeout: 120,
  // Ignore TypeScript build errors
  typescript: {
    ignoreBuildErrors: true,
  },
  // Ignore ESLint build errors
  eslint: {
    ignoreDuringBuilds: true,
  },
}

module.exports = nextConfig