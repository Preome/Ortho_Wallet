#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting Next.js build process..."

# Install dependencies
echo "📦 Installing npm packages..."
npm ci --only=production || npm install

# Build the Next.js app
echo "🏗️ Building Next.js application..."
npm run build

echo "✅ Build completed successfully!"