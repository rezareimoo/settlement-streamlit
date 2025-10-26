# Quick Start Guide - Settlement 360

Get up and running in 3 minutes!

## 🚀 Fastest Way to Run

```bash
cd /workspace/settlement-nextjs
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

That's it! The database is already configured.

## 📁 Project Overview

```
settlement-nextjs/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Main dashboard (START HERE)
│   ├── layout.tsx         # Root layout
│   └── api/               # 11 API endpoints
├── components/
│   ├── tabs/              # 5 main tab components
│   └── ui/                # Reusable UI components
├── lib/
│   ├── db.ts              # Database connection
│   └── queries.ts         # All SQL queries
└── types/
    └── index.ts           # TypeScript types
```

## 🎯 Key Files to Understand

1. **`app/page.tsx`** - Main entry point with tab navigation
2. **`components/tabs/CasesTab.tsx`** - Cases tab (most complex)
3. **`lib/queries.ts`** - All database queries
4. **`app/api/*/route.ts`** - API endpoint handlers

## 🔧 Available Commands

```bash
npm run dev          # Start development server (port 3000)
npm run build        # Create production build
npm run start        # Run production server
npm run lint         # Check for code issues
```

## 📊 Features by Tab

### 1. Cases Tab
- View all settlement cases
- Filter by region and date
- Compare CMS vs FDP data
- Regional statistics

### 2. Case Lookup Tab
- Search for specific cases
- View detailed case information
- See all family members
- View custom assessment data

### 3. Member Lookup Tab
- Search jamati members
- View member details
- Full member table with filtering

### 4. Demographics Tab
- Country of origin distribution
- Age distribution
- Education level analysis

### 5. Children Tab
- View all children (18 and under)
- Regional statistics
- Education status
- Age and country distribution

## 🗄️ Database Schema

The app connects to these main tables:
- `SettlementCase` - Case records
- `JamatiMember` - Family members
- `Education` - Education data
- `Finance` - Financial information
- `PhysicalMentalHealth` - Health records
- `SocialInclusionAgency` - Social data
- `fdp_cases` - FDP data source
- `custom_data` - Quick assessments

## 🎨 UI Components

Built with Radix UI + Tailwind CSS:
- `<Tabs>` - Tab navigation
- `<Card>` - Content containers
- `<Button>` - Action buttons
- `<Select>` - Dropdowns
- `<Collapsible>` - Expandable sections

## 🔌 API Endpoints

All endpoints return JSON:

```
GET  /api/cases              # All cases
GET  /api/cases/[id]         # Single case
GET  /api/members            # All members
GET  /api/education          # Education data
GET  /api/finance            # Finance data
GET  /api/health             # Health data
GET  /api/social-inclusion   # Social data
GET  /api/fdp-cases          # FDP cases
GET  /api/custom-data/[id]   # Custom data
POST /api/custom-data        # Save custom data
DELETE /api/custom-data/[id] # Delete custom data
```

## 🐛 Common Issues

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
npm run dev
```

### Database Connection Error
- Check .env.local file exists
- Verify database credentials
- Ensure SSL is enabled

### Build Errors
```bash
rm -rf .next node_modules
npm install --legacy-peer-deps
npm run build
```

### Type Errors
```bash
npm run lint
# Fix reported issues
```

## 📝 Making Changes

### Add a New Tab
1. Create `components/tabs/YourTab.tsx`
2. Add tab in `app/page.tsx`
3. Create API route if needed

### Add a New API Endpoint
1. Create `app/api/your-endpoint/route.ts`
2. Add query function in `lib/queries.ts`
3. Add types in `types/index.ts`

### Modify UI
1. Edit component in `components/tabs/`
2. Use Tailwind CSS classes
3. Import UI components from `components/ui/`

## 🎓 Learning Resources

- **Next.js Docs:** https://nextjs.org/docs
- **TypeScript:** https://www.typescriptlang.org/docs
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Radix UI:** https://www.radix-ui.com/docs
- **Recharts:** https://recharts.org/en-US/

## 💡 Tips

1. **Hot Reload:** Changes auto-refresh in development
2. **Type Safety:** TypeScript catches errors before runtime
3. **API Routes:** All data fetching goes through `/api/*`
4. **Client Components:** Use `"use client"` for interactive components
5. **Server Components:** Default, can fetch data directly

## 🔒 Environment Variables

Located in `.env.local` (already configured):
```env
DB_HOST=settlementanalyticsdb.postgres.database.azure.com
DB_NAME=Settlement
DB_USER=settlementAdmin71125
DB_PASSWORD=SideHustle2025!
DB_PORT=5432
```

## 📈 Next Steps

1. ✅ Run `npm run dev` and explore the UI
2. ⭐ Review `components/tabs/` to understand each tab
3. 🎨 Customize styling with Tailwind classes
4. 📊 Add chart visualizations with Recharts
5. 🚀 Deploy to Vercel (see DEPLOYMENT.md)

## 🆘 Need Help?

1. Check README.md for detailed documentation
2. Review MIGRATION_SUMMARY.md for architecture
3. See DEPLOYMENT.md for production setup
4. Contact the development team

---

**You're all set!** Start the dev server and begin exploring. 🎉
