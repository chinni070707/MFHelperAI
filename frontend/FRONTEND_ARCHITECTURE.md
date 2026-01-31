# MFHelper Frontend - Modular TypeScript Architecture

## 🏗️ Project Structure

```
frontend/
├── src/                          # TypeScript source files
│   ├── types/                    # Type definitions
│   │   └── portfolio.ts          # Portfolio data types
│   ├── services/                 # API and external services
│   │   └── api.ts                # Centralized API client
│   ├── utils/                    # Utility functions
│   │   ├── toast.ts              # Toast notifications
│   │   ├── formatter.ts          # Number/date formatting
│   │   └── storage.ts            # LocalStorage manager
│   ├── components/               # Reusable components
│   │   └── charts.ts             # Chart.js & Plotly wrappers
│   └── dashboard.ts              # Main dashboard controller
│
├── css/                          # Stylesheets
│   ├── design-system.css         # Design tokens & variables
│   └── components.css            # Component styles
│
├── js/                           # Legacy JavaScript (to be migrated)
│   ├── toast.js
│   ├── errorHandler.js
│   ├── responsive.js
│   ├── components.js
│   └── overlap.js
│
├── www/                          # Build output directory
├── android/                      # Capacitor Android project
├── tsconfig.json                 # TypeScript configuration
├── vite.config.ts                # Vite build configuration
└── package.json                  # Dependencies & scripts

```

## 🚀 Getting Started

### Install Dependencies

```bash
cd frontend
npm install
```

### Development Mode

```bash
npm run dev
```

Runs Vite dev server on `http://localhost:3000` with:
- Hot module replacement (HMR)
- TypeScript type checking
- API proxy to backend (port 8000)

### Build for Production

```bash
npm run build
```

Compiles TypeScript and bundles for production in `www/` directory.

### Type Checking

```bash
npm run type-check
```

Runs TypeScript compiler without emitting files (checks for type errors).

## 📦 Key Modules

### API Service (`src/services/api.ts`)

Centralized API client with typed responses:

```typescript
import { api } from '@services/api';

// Upload Excel file
const portfolio = await api.uploadExcel(file);

// Get portfolio
const data = await api.getPortfolio('user_id');

// Calculate analytics
const allocation = await api.calculateAllocation(holdings);
```

### Toast Notifications (`src/utils/toast.ts`)

Type-safe toast notifications:

```typescript
import { toast } from '@utils/toast';

toast.success('Portfolio saved!');
toast.error('Upload failed', 5000);
toast.warning('Low balance detected');
toast.info('Syncing data...');
```

### Formatter (`src/utils/formatter.ts`)

Consistent number and date formatting:

```typescript
import { Formatter } from '@utils/formatter';

Formatter.currency(125000);         // ₹1,25,000
Formatter.numberIndian(2500000);    // ₹25.00 L
Formatter.percentage(15.5);         // 15.50%
Formatter.date('2026-02-01');       // Feb 1, 2026
```

### Storage Manager (`src/utils/storage.ts`)

Type-safe localStorage wrapper:

```typescript
import { storage } from '@utils/storage';

storage.set('portfolio', portfolioData);
const data = storage.get<Portfolio>('portfolio');
storage.remove('portfolio');
storage.clear(); // Clear all app data
```

### Chart Manager (`src/components/charts.ts`)

Unified chart API for Chart.js and Plotly:

```typescript
import { chartManager } from '@components/charts';

// Pie chart
chartManager.createPieChart('chart-id', labels, values);

// Bar chart
chartManager.createBarChart('chart-id', labels, values, 'Title');

// Treemap (Plotly)
chartManager.createTreemap('chart-id', labels, parents, values);

// Clean up
chartManager.destroyChart('chart-id');
chartManager.destroyAll();
```

### Dashboard Controller (`src/dashboard.ts`)

Main application logic:

```typescript
import { DashboardController } from '@/dashboard';

// Auto-initializes on page load
// Handles:
// - Portfolio loading
// - File uploads
// - Chart rendering
// - UI updates
```

## 🎯 TypeScript Benefits

### Type Safety

```typescript
// Compile-time error prevention
const portfolio: Portfolio = await api.getPortfolio();
// portfolio.holdngs // ❌ TypeScript error: Property 'holdngs' does not exist
portfolio.holdings // ✅ Correct
```

### IntelliSense & Autocomplete

Full IDE support with type hints, method signatures, and documentation.

### Refactoring Support

Rename symbols, find all usages, safe refactoring across the codebase.

## 📂 Path Aliases

Configured in `tsconfig.json` and `vite.config.ts`:

```typescript
import { api } from '@services/api';        // Instead of '../../../services/api'
import { toast } from '@utils/toast';       // Instead of '../../utils/toast'
import type { Portfolio } from '@types/portfolio';
```

## 🔄 Migration Strategy

### Phase 1: Infrastructure ✅
- [x] Set up TypeScript & Vite
- [x] Create type definitions
- [x] Build API service layer
- [x] Create utility modules
- [x] Create chart components

### Phase 2: Dashboard Refactoring (In Progress)
- [ ] Extract HTML components
- [ ] Migrate inline scripts to modules
- [ ] Update HTML to use new modules
- [ ] Test all functionality

### Phase 3: Complete Migration
- [ ] Migrate remaining JS files
- [ ] Add unit tests for TypeScript modules
- [ ] Optimize bundle size
- [ ] Add code splitting

## 🎨 Code Style

### Naming Conventions
- **Classes**: PascalCase (`DashboardController`, `ToastManager`)
- **Functions/Methods**: camelCase (`loadPortfolio`, `renderCharts`)
- **Constants**: UPPER_SNAKE_CASE (`API_BASE`, `MAX_FILE_SIZE`)
- **Types/Interfaces**: PascalCase (`Portfolio`, `Holding`)

### File Organization
- One class/module per file
- Export singleton instances where appropriate
- Use named exports for utilities
- Default export for main class

## 📊 Bundle Size

Target bundle sizes:
- Main JS bundle: <100KB (gzipped)
- Vendor bundles: <200KB (gzipped)
- Total initial load: <300KB

Use code splitting for charts and heavy libraries.

## 🐛 Debugging

### Development Console Logs
TypeScript source maps are enabled in development for easy debugging.

### Type Errors
Run `npm run type-check` to catch type errors before building.

## 🚢 Deployment

Build outputs to `www/` directory, ready for:
- Static hosting (Vercel, Netlify)
- FastAPI static file serving
- Capacitor mobile app bundling

## 📝 Next Steps

1. Complete dashboard HTML refactoring
2. Migrate remaining legacy JS files
3. Add unit tests with Vitest
4. Optimize bundle with dynamic imports
5. Add E2E tests with Playwright

---

**Benefits of This Architecture:**
- ✅ Type safety prevents runtime errors
- ✅ Modular code is easier to maintain
- ✅ Reusable components across pages
- ✅ Better IDE support and refactoring
- ✅ Smaller bundle sizes with tree-shaking
- ✅ Modern development workflow
