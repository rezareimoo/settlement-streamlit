#!/bin/bash
# Quick script to run the Settlement 360 Next.js app

echo "🚀 Settlement 360 - Starting Application"
echo "========================================="
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Kill any existing Next.js processes
echo "🧹 Cleaning up old processes..."
pkill -f next 2>/dev/null
sleep 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install --legacy-peer-deps
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  WARNING: .env.local file not found!"
    echo "Creating .env.local with database credentials..."
    cat > .env.local << 'ENVEOF'
DB_HOST=settlementanalyticsdb.postgres.database.azure.com
DB_NAME=Settlement
DB_USER=settlementAdmin71125
DB_PASSWORD=SideHustle2025!
DB_PORT=5432
ENVEOF
    echo "✅ .env.local created"
fi

# Clean build if needed
if [ "$1" = "--clean" ]; then
    echo "🧹 Cleaning build cache..."
    rm -rf .next
fi

# Start the development server
echo ""
echo "✅ Starting development server..."
echo "📍 Project: /workspace/settlement-nextjs"
echo "🌐 URL: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

npm run dev
