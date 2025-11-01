#!/bin/bash
echo "🔍 Quick Location Check"
echo "======================"
echo ""
echo "Current directory:"
pwd
echo ""
echo "Is this /workspace/settlement-nextjs?"
if [ "$(pwd)" = "/workspace/settlement-nextjs" ]; then
    echo "✅ YES - You're in the correct location!"
    echo ""
    echo "Files present:"
    echo "  ✓ lib/db.ts: $(test -f lib/db.ts && echo "EXISTS" || echo "MISSING")"
    echo "  ✓ lib/queries.ts: $(test -f lib/queries.ts && echo "EXISTS" || echo "MISSING")"
    echo "  ✓ lib/utils.ts: $(test -f lib/utils.ts && echo "EXISTS" || echo "MISSING")"
    echo "  ✓ types/index.ts: $(test -f types/index.ts && echo "EXISTS" || echo "MISSING")"
    echo ""
    echo "✅ Ready to run: npm run dev"
else
    echo "❌ NO - You need to navigate to /workspace/settlement-nextjs"
    echo ""
    echo "Run this command:"
    echo "  cd /workspace/settlement-nextjs"
fi
