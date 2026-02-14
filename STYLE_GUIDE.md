# MFHelper Style Guide & Design System

**Last Updated:** February 14, 2026  
**Version:** 1.0

## Table of Contents
1. [Brand Identity](#brand-identity)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Navigation Standards](#navigation-standards)
5. [Layout & Spacing](#layout--spacing)
6. [Component Patterns](#component-patterns)
7. [Accessibility Requirements](#accessibility-requirements)
8. [Code Conventions](#code-conventions)

---

## Brand Identity

### Design Philosophy
- **Professional & Growth-Focused**: Clean, modern interface emphasizing financial growth
- **User-Friendly**: Intuitive navigation with clear visual hierarchy
- **Consistent Experience**: Uniform styling across all pages and tools
- **Accessible**: WCAG 2.1 AA compliant with proper ARIA labels

### Theme
- **Primary Theme**: Light theme with white/off-white backgrounds
- **Accent Color**: Brand green (#7FC04C) - "Growth Green"
- **Style**: Professional finance application with modern card-based layouts

---

## Color Palette

### Primary Colors
```css
--primary-green: #7FC04C;        /* Main brand color */
--primary-green-dark: #6BA83C;   /* Hover states, darker accents */
--primary-green-light: #9ED670;  /* Light accents */
--primary-green-soft: #E8F5E0;   /* Very light backgrounds */
--accent-green: #5A9030;         /* Alternative green */
```

### Background Colors
```css
--bg-primary: #FFFFFF;           /* Main background (white) */
--bg-secondary: #F9FAFB;         /* Secondary bg (off-white) */
--bg-tertiary: #F3F4F6;          /* Tertiary backgrounds */
--bg-light: #F9FAFB;             /* Light backgrounds for cards */
```

### Text Colors
```css
--text-primary: #111827;         /* Main text (dark gray) */
--text-secondary: #6B7280;       /* Secondary text (medium gray) */
--text-tertiary: #9CA3AF;        /* Tertiary text (light gray) */
--text-inverse: #FFFFFF;         /* Text on dark backgrounds */
```

### Border & Dividers
```css
--border-color: #E5E7EB;         /* Standard borders */
--border-light: #F3F4F6;         /* Light borders */
--divider: rgba(0, 0, 0, 0.06);  /* Divider lines */
```

### Status Colors
```css
--success: #10B981;              /* Success states, positive values */
--warning: #F59E0B;              /* Warning states */
--error: #DC3545;                /* Error states, negative values */
--info: #3B82F6;                 /* Information states */
```

### Usage Guidelines
- **Never use dark theme** - All pages use light theme
- Use `--primary-green` for primary actions (buttons, links, highlights)
- Use `--text-secondary` for less important information
- Status colors for appropriate contexts (gains/losses, alerts)

---

## Typography

### Font Family
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
```

### Font Weights
- **300**: Light (rarely used)
- **400**: Regular (body text)
- **500**: Medium (emphasized text)
- **600**: Semi-bold (subheadings, labels)
- **700**: Bold (headings)
- **800**: Extra-bold (hero titles, page titles)

### Type Scale
```css
/* Headings */
h1: 2.5rem (40px) - font-weight: 800
h2: 2rem (32px) - font-weight: 700
h3: 1.5rem (24px) - font-weight: 700
h4: 1.25rem (20px) - font-weight: 600

/* Body */
body: 1rem (16px) - line-height: 1.6
small: 0.875rem (14px)
tiny: 0.75rem (12px)
```

---

## Navigation Standards

### Standard Navigation Structure

**ALL pages must include the exact same navigation bar:**

```html
<nav class="navbar" role="navigation" aria-label="Main navigation">
    <div class="nav-container">
        <a href="/" class="logo" aria-label="MFHelper Home">MFHelper</a>
        <ul class="nav-menu" role="list">
            <li><a href="/" class="nav-link">Home</a></li>
            <li class="nav-item has-dropdown">
                <a href="/tools.html" class="nav-link">Tools</a>
                <div class="dropdown-menu">
                    <a href="/overlap-analysis.html">
                        <span class="icon">🔄</span>
                        <span>Fund Overlap Analysis</span>
                    </a>
                    <a href="/portfolio.html">
                        <span class="icon">📊</span>
                        <span>Portfolio Analyzer</span>
                    </a>
                    <a href="/fund-comparison.html">
                        <span class="icon">⚖️</span>
                        <span>Fund Comparison</span>
                    </a>
                    <a href="/risk-analyzer.html">
                        <span class="icon">⚠️</span>
                        <span>Risk Analyzer</span>
                    </a>
                    <a href="/rebalancing-tool.html">
                        <span class="icon">⚙️</span>
                        <span>Rebalancing Tool</span>
                    </a>
                    <a href="/sip-calculator.html">
                        <span class="icon">🎯</span>
                        <span>SIP Calculator</span>
                    </a>
                    <div class="dropdown-divider"></div>
                    <a href="/tools.html">
                        <span class="icon">🧰</span>
                        <span>All Tools</span>
                    </a>
                </div>
            </li>
            <li><a href="/goal-planning.html" class="nav-link">Goal Planning</a></li>
            <li><a href="/portfolio.html" class="nav-link">Portfolio</a></li>
            <li><a href="/blog.html" class="nav-link">Blog</a></li>
            <li><a href="/auth.html?tab=signup" class="btn-primary" style="text-decoration: none; display: inline-block;">Get Started</a></li>
        </ul>
        <div class="hamburger" onclick="toggleMenu()" role="button" aria-label="Toggle navigation menu" tabindex="0">
            <span></span>
            <span></span>
            <span></span>
        </div>
    </div>
</nav>
```

### Navigation Order (MUST NOT CHANGE)
1. Home
2. Tools (dropdown)
3. Goal Planning
4. Portfolio
5. Blog
6. Get Started (button)

### Navbar Specifications
- **Height**: 70px fixed
- **Background**: `rgba(255, 255, 255, 0.95)` with backdrop blur
- **Position**: Fixed at top, z-index: 1000
- **Border**: 1px solid `var(--border-color)` at bottom
- **Shadow**: `0 2px 10px rgba(0,0,0,0.1)`

---

## Layout & Spacing

### Page Structure
```
body: padding-top: 90px (to account for fixed navbar)
```

### Container Widths
```css
max-width: 1400px;  /* Main content container */
margin: 0 auto;     /* Center alignment */
padding: 2rem;      /* Standard padding */
```

### Border Radius
```css
--radius-sm: 8px;   /* Small elements (buttons, inputs) */
--radius-md: 12px;  /* Medium elements (cards) */
--radius-lg: 16px;  /* Large elements (modals, sections) */
```

### Shadows (Elevation)
```css
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
```

### Spacing Scale
```
0.25rem (4px)   - xs
0.5rem (8px)    - sm
1rem (16px)     - md (base)
1.5rem (24px)   - lg
2rem (32px)     - xl
3rem (48px)     - 2xl
4rem (64px)     - 3xl
```

---

## Component Patterns

### Buttons

#### Primary Button
```css
.btn-primary {
    background: linear-gradient(135deg, var(--primary-green), var(--dark-green));
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    border: none;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.3s;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(127, 192, 76, 0.3);
}
```

#### Secondary Button
```css
.btn-secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 2px solid var(--border-color);
}
```

### Cards
```css
.card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
}
```

### Input Fields
```css
.input-field {
    width: 100%;
    padding: 0.75rem 1rem;
    background: var(--white);
    border: 2px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 1rem;
    transition: border-color 0.3s;
}

.input-field:focus {
    outline: none;
    border-color: var(--primary-green);
}
```

---

## Accessibility Requirements

### Mandatory Attributes

#### Navigation
- `role="navigation"`
- `aria-label="Main navigation"`
- `role="list"` on `<ul>`
- `aria-label` on logo link
- `role="button"` on hamburger menu
- `aria-label="Toggle navigation menu"` on hamburger
- `tabindex="0"` on interactive elements

#### Active Page Indication
```html
<a href="/current-page.html" class="nav-link" 
   style="color: var(--primary-green);" 
   aria-current="page">Current Page</a>
```

#### Links
- All links must have descriptive text
- Icon-only buttons need `aria-label`
- External links should indicate they open in new tab

#### Forms
- Every input must have an associated `<label>`
- Use `aria-describedby` for input hints
- Show validation errors clearly

### Keyboard Navigation
- All interactive elements must be keyboard accessible
- Proper tab order (no `tabindex` > 0)
- Visible focus indicators
- Skip navigation link for screen readers

### Color Contrast
- Text contrast ratio: minimum 4.5:1 (normal text)
- Large text contrast ratio: minimum 3:1
- Interactive elements: minimum 4.5:1

---

## Code Conventions

### HTML Structure

#### Required Meta Tags
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-5RBTST8N');</script>
    <!-- End Google Tag Manager -->
    
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title - MFHelper</title>
    <meta name="description" content="Page description for SEO">
    
    <link rel="stylesheet" href="/css/design-system.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="/js/analytics.js"></script>
    <script src="/js/navbar-auth.js" defer></script>
    <script src="/js/toast.js" defer></script>
</head>
```

#### CSS Variables
- **ALWAYS** use CSS variables from design-system.css
- **NEVER** hardcode colors directly
- Include design-system.css as first stylesheet

```css
/* DO THIS */
background: var(--bg-primary);
color: var(--text-primary);
border: 1px solid var(--border-color);

/* NOT THIS */
background: #FFFFFF;
color: #111827;
border: 1px solid #E5E7EB;
```

#### CSS Naming
- Use kebab-case for class names: `.nav-menu`, `.btn-primary`
- Semantic names over presentational: `.card-title` not `.text-large`
- BEM methodology for complex components

### File Organization
```
frontend/
├── css/
│   └── design-system.css    (Global variables & utilities)
├── js/
│   ├── navbar-auth.js       (Navigation authentication)
│   ├── analytics.js         (Google Analytics)
│   └── toast.js             (Toast notifications)
├── [page].html              (Individual pages)
```

### JavaScript
- Use vanilla JavaScript unless library is necessary
- Defer non-critical scripts
- Use `'use strict';`
- Add error handling for user interactions

---

## Design System Updates

### When to Update This Guide
- New component patterns are established
- Color palette changes
- Typography scale modifications
- New accessibility requirements
- Breaking changes to navigation structure

### Version Control
- Document all changes in git commits
- Update "Last Updated" date at top
- Increment version number for major changes
- Communicate changes to entire team

---

## Quick Reference

### Starting a New Page

1. **Copy template** from existing page (index.html recommended)
2. **Include standard navigation** (copy-paste, don't modify)
3. **Use design-system.css** for all styling
4. **Set page-specific styles** after standard navigation
5. **Test accessibility** (keyboard nav, screen reader, contrast)
6. **Validate HTML** before committing

### Common Mistakes to Avoid

❌ Using dark theme (use light theme only)  
❌ Modifying navigation order or structure  
❌ Hardcoding colors instead of CSS variables  
❌ Missing accessibility attributes  
❌ Inconsistent button styles  
❌ Not including navbar-auth.js  
❌ Forgetting mobile responsive design  

### Resources

- Design System CSS: `/css/design-system.css`
- Navigation Component: See "Navigation Standards" section above
- Color Palette: See "Color Palette" section above
- Example Pages: `index.html`, `portfolio.html`, `dashboard.html`

---

**For questions or suggestions, contact the development team.**
