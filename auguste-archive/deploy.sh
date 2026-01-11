#!/bin/bash

# Deployment script for Auguste Archive
# This script helps deploy the application to production

set -e

echo "🚀 Auguste Archive Deployment Script"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the auguste-archive directory."
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

echo ""
echo "🏗️  Building production version..."
npm run build

echo ""
echo "✅ Build complete! Production files are in ./dist/"
echo ""
echo "Choose your deployment method:"
echo ""
echo "1️⃣  Deploy to Vercel (Recommended)"
echo "   Run: vercel --prod"
echo ""
echo "2️⃣  Deploy to Netlify"
echo "   Run: netlify deploy --prod"
echo ""
echo "3️⃣  Preview locally first"
echo "   Run: npm run preview"
echo "   Then visit: http://localhost:4173"
echo ""
echo "4️⃣  Manual deployment"
echo "   Upload the ./dist/ folder to your hosting provider"
echo ""
echo "📖 For detailed instructions, see DEPLOYMENT.md"
echo ""
echo "Would you like to preview the build locally? (y/n)"
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo ""
    echo "🌐 Starting preview server..."
    npm run preview
else
    echo ""
    echo "✨ All set! Choose one of the deployment options above."
fi
