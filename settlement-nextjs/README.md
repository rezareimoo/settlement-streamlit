# Settlement 360 - Next.js Migration

A modern, responsive web application for settlement case management and analytics, migrated from Streamlit to Next.js 14+.

## Features

- **Cases Management**: View and analyze settlement cases from CMS and FDP data sources
- **Case Lookup**: Detailed case information with family member profiles
- **Member Lookup**: Search and view jamati member details
- **Demographics**: Visual analysis of jamati member demographics
- **Children's Data**: Specialized view for children (18 and under) in the settlement program

## Tech Stack

- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Database**: PostgreSQL (Azure)
- **UI Components**: Radix UI + Tailwind CSS
- **Charts**: Recharts (integration ready)
- **Maps**: react-simple-maps (integration ready)

## Project Structure

```
settlement-nextjs/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Main dashboard with tabs
│   ├── globals.css             # Global styles
│   └── api/                    # API routes
│       ├── cases/              # Case data endpoints
│       ├── members/            # Member data endpoints
│       ├── education/          # Education data endpoints
│       ├── finance/            # Finance data endpoints
│       ├── health/             # Health data endpoints
│       ├── social-inclusion/   # Social inclusion data endpoints
│       ├── fdp-cases/          # FDP case data endpoints
│       └── custom-data/        # Custom assessment data endpoints
├── components/
│   ├── ui/                     # Reusable UI components
│   │   ├── tabs.tsx
│   │   ├── button.tsx
│   │   ├── select.tsx
│   │   ├── card.tsx
│   │   └── collapsible.tsx
│   └── tabs/                   # Tab-specific components
│       ├── CasesTab.tsx
│       ├── CaseLookupTab.tsx
│       ├── MemberLookupTab.tsx
│       ├── DemographicsTab.tsx
│       └── ChildrenTab.tsx
├── lib/
│   ├── db.ts                   # Database connection pool
│   ├── queries.ts              # SQL query functions
│   └── utils.ts                # Utility functions
├── types/
│   └── index.ts                # TypeScript type definitions
└── .env.local                  # Environment variables (not in git)
```

## Setup Instructions

### Prerequisites

- Node.js 18+ installed
- Access to the PostgreSQL database

### Installation

1. Navigate to the project directory:
```bash
cd settlement-nextjs
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:

The `.env.local` file is already configured with the database credentials:
```
DB_HOST=settlementanalyticsdb.postgres.database.azure.com
DB_NAME=Settlement
DB_USER=settlementAdmin71125
DB_PASSWORD=SideHustle2025!
DB_PORT=5432
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Development

### Running the App

```bash
npm run dev          # Development server
npm run build        # Production build
npm run start        # Start production server
npm run lint         # Run ESLint
```

### API Routes

All API routes follow REST conventions:

- `GET /api/cases` - Fetch all settlement cases
- `GET /api/cases/[id]` - Fetch specific case by ID
- `GET /api/members` - Fetch all jamati members
- `GET /api/education` - Fetch all education records
- `GET /api/finance` - Fetch all finance records
- `GET /api/health` - Fetch all health records
- `GET /api/social-inclusion` - Fetch all social inclusion records
- `GET /api/fdp-cases` - Fetch all FDP cases
- `GET /api/custom-data/[caseId]` - Fetch custom assessment data
- `POST /api/custom-data` - Save custom assessment data
- `DELETE /api/custom-data/[caseId]` - Delete custom assessment data

### Database Connection

The app uses a connection pool for efficient database access. The pool is configured in `lib/db.ts` with:
- Max connections: 20
- Idle timeout: 30 seconds
- Connection timeout: 10 seconds
- SSL enabled (Azure requirement)

## Migration Status

### ✅ Completed

- [x] Project setup with Next.js 14 + TypeScript
- [x] Database connection and types
- [x] All API routes
- [x] UI component library (Radix UI)
- [x] Cases tab (basic functionality)
- [x] Case Lookup tab
- [x] Member Lookup tab
- [x] Demographics tab
- [x] Children tab
- [x] Responsive layout
- [x] Data filtering (region, date range)

### 🚧 Next Steps

1. **Chart Integration**: Add Recharts visualizations
   - Pie charts for status distribution
   - US state choropleth maps
   - Stacked bar charts for regional analysis
   - Line charts for time-series data
   - Age histograms

2. **Enhanced Filtering**: Implement full date range filtering with state management

3. **FDP Data Integration**: Complete FDP data mapping and comparison views

4. **Quick Assessment Form**: Add the interactive form for custom data entry

5. **Camp Mosaic Eligibility**: Add eligibility checker in Member Lookup

6. **Data Tables**: Enhance with sorting, pagination, and advanced filtering

7. **Loading States**: Add skeleton loaders and better loading indicators

8. **Error Handling**: Implement comprehensive error boundaries

9. **Authentication**: Prepare for future auth integration (NextAuth.js recommended)

10. **Deployment**: Configure for Vercel deployment

## Key Differences from Streamlit

| Feature | Streamlit | Next.js |
|---------|-----------|---------|
| State Management | `st.session_state` | React state + URL params |
| Data Loading | Synchronous with `@st.cache` | Async with API routes |
| Components | `st.tabs`, `st.expander` | Radix UI components |
| Charts | Plotly | Recharts (to be integrated) |
| Forms | `st.form` | React forms with state |
| Styling | Built-in themes | Tailwind CSS |
| Performance | Single-threaded | Optimized with React Server Components |

## Database Schema

The app uses the following main tables:
- `SettlementCase` - Settlement case records
- `JamatiMember` - Family member information
- `Education` - Educational data
- `Finance` - Financial information
- `PhysicalMentalHealth` - Health records
- `SocialInclusionAgency` - Social inclusion data
- `fdp_cases` - FDP data source
- `custom_data` - Quick assessment custom fields

## Contributing

When adding new features:
1. Create types in `types/index.ts`
2. Add database queries in `lib/queries.ts`
3. Create API routes in `app/api/`
4. Build UI components in `components/`
5. Use TypeScript strictly for type safety

## Support

For issues or questions, contact the settlement analytics team.

## License

Internal use only - Settlement 360 Project
