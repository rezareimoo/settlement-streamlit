#!/bin/bash
# Project Structure Verification Script

echo "🔍 Settlement 360 - Project Structure Verification"
echo "=================================================="
echo ""

# Check lib folder
echo "✅ Checking lib/ folder..."
if [ -d "lib" ]; then
    echo "   ✓ lib/ exists"
    for file in db.ts queries.ts utils.ts; do
        if [ -f "lib/$file" ]; then
            lines=$(wc -l < "lib/$file")
            echo "   ✓ lib/$file exists ($lines lines)"
        else
            echo "   ✗ lib/$file MISSING!"
        fi
    done
else
    echo "   ✗ lib/ folder MISSING!"
fi
echo ""

# Check types folder
echo "✅ Checking types/ folder..."
if [ -d "types" ]; then
    echo "   ✓ types/ exists"
    if [ -f "types/index.ts" ]; then
        lines=$(wc -l < "types/index.ts")
        echo "   ✓ types/index.ts exists ($lines lines)"
    else
        echo "   ✗ types/index.ts MISSING!"
    fi
else
    echo "   ✗ types/ folder MISSING!"
fi
echo ""

# Check API routes
echo "✅ Checking API routes..."
api_routes=$(find app/api -name "route.ts" 2>/dev/null | wc -l)
echo "   ✓ Found $api_routes API route files"
find app/api -name "route.ts" 2>/dev/null | sed 's/^/   - /'
echo ""

# Check components
echo "✅ Checking components..."
tab_components=$(find components/tabs -name "*.tsx" 2>/dev/null | wc -l)
ui_components=$(find components/ui -name "*.tsx" 2>/dev/null | wc -l)
echo "   ✓ Found $tab_components tab components"
echo "   ✓ Found $ui_components UI components"
echo ""

# Check .env.local
echo "✅ Checking environment configuration..."
if [ -f ".env.local" ]; then
    echo "   ✓ .env.local exists"
    if grep -q "DB_HOST" .env.local; then
        echo "   ✓ Database credentials configured"
    fi
else
    echo "   ✗ .env.local MISSING!"
fi
echo ""

# Check key dependencies
echo "✅ Checking key dependencies..."
if [ -f "package.json" ]; then
    if grep -q '"pg"' package.json; then
        echo "   ✓ pg (PostgreSQL) installed"
    fi
    if grep -q '"recharts"' package.json; then
        echo "   ✓ recharts installed"
    fi
    if grep -q '"@radix-ui"' package.json; then
        echo "   ✓ Radix UI installed"
    fi
fi
echo ""

echo "=================================================="
echo "✨ Verification Complete!"
echo ""
echo "To start the app:"
echo "  npm run dev"
echo ""
