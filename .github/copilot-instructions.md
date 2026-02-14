# GitHub Copilot Instructions for MFHelper

## Project Overview
MFHelper is a professional mutual fund portfolio management application using a **light theme** design system with **green accents** (#7FC04C). All pages must maintain strict consistency in navigation, styling, and accessibility.

---

## Critical Rules for HTML Page Creation

### 1. Theme & Color System
- **ALWAYS use LIGHT THEME** - Never create dark theme pages
- **ONLY use CSS variables** from `/css/design-system.css` - Never hardcode colors
- Primary brand color: `var(--primary-green)` (#7FC04C)
- Background: `var(--bg-primary)` (white) or `var(--bg-secondary)` (off-white)
- Text: `var(--text-primary)` (dark gray)

```css
/* CORRECT */
background: var(--bg-primary);
color: var(--text-primary);
border: 1px solid var(--border-color);

/* WRONG - Never do this */
background: #151926;  /* Dark theme - FORBIDDEN */
color: #FFFFFF;
background: #1E2330;
```

### 2. Navigation Bar (MANDATORY)

**Every HTML page MUST include this exact navigation structure** - copy this verbatim:

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

**Navigation Order - NEVER CHANGE:**
1. Home
2. Tools (dropdown with all 6 tools + divider + All Tools)
3. Goal Planning
4. Portfolio
5. Blog
6. Get Started (button)

### 3. HTML Template Structure

Use this as the base template for ALL new pages:

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
    <title>[Page Title] - MFHelper</title>
    <meta name="description" content="[SEO description]">
    
    <link rel="stylesheet" href="/css/design-system.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="/js/analytics.js"></script>
    <script src="/js/navbar-auth.js" defer></script>
    <script src="/js/toast.js" defer></script>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
            padding-top: 90px; /* For fixed navbar */
        }

        /* Page-specific styles here */
    </style>
</head>
<body>
    <!-- Google Tag Manager (noscript) -->
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-5RBTST8N"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
    <!-- End Google Tag Manager (noscript) -->
    
    <!-- Navigation (use standard nav from above) -->
    
    <!-- Page Content -->
    <main class="container">
        <!-- Your content here -->
    </main>
    
    <!-- Scripts -->
    <script>
        // Page-specific JavaScript
    </script>
</body>
</html>
```

### 4. Required Includes

**Every page MUST include:**
- `/css/design-system.css` (first CSS file)
- Google Inter font
- `/js/navbar-auth.js` (with `defer`)
- `/js/analytics.js`
- `/js/toast.js` (with `defer`)
- Google Tag Manager snippet (head + body)

### 5. Accessibility Requirements

**Always include:**
- `role="navigation"` on `<nav>`
- `aria-label="Main navigation"` on `<nav>`
- `role="list"` on navigation `<ul>`
- `aria-label` on logo link
- `role="button"` on hamburger menu
- `aria-label="Toggle navigation menu"` on hamburger
- `tabindex="0"` on clickable non-link elements
- `aria-current="page"` on active page links
- Each input must have a `<label>`
- Proper heading hierarchy (h1 → h2 → h3)
- Minimum 4.5:1 color contrast ratio

### 6. Component Patterns

#### Primary Button
```css
.btn-primary {
    background: linear-gradient(135deg, var(--primary-green), var(--primary-green-dark));
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

#### Card Component
```css
.card {
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
}
```

#### Input Field
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

### 7. CSS Variable Reference

**ALWAYS use these variables - NEVER hardcode values:**

```css
/* Colors */
--primary-green: #7FC04C;
--primary-green-dark: #6BA83C;
--primary-green-light: #9ED670;

/* Backgrounds */
--bg-primary: #FFFFFF;
--bg-secondary: #F9FAFB;
--bg-light: #F9FAFB;

/* Text */
--text-primary: #111827;
--text-secondary: #6B7280;
--text-tertiary: #9CA3AF;

/* Borders */
--border-color: #E5E7EB;

/* Status */
--success: #10B981;
--warning: #F59E0B;
--error: #DC3545;
--info: #3B82F6;

/* Shadows */
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
```

### 8. Layout Standards

```css
/* Container */
.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}

/* Navbar */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 70px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    z-index: 1000;
    border-bottom: 1px solid var(--border-color);
}

/* Body spacing for fixed navbar */
body {
    padding-top: 90px;
}
```

### 9. Typography

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

/* Headings */
h1 { font-size: 2.5rem; font-weight: 800; }
h2 { font-size: 2rem; font-weight: 700; }
h3 { font-size: 1.5rem; font-weight: 700; }

/* Body */
body { font-size: 1rem; line-height: 1.6; }
```

---

## Code Generation Guidelines

### When Creating New HTML Pages:

1. **Start with the base template** provided above
2. **Copy navigation verbatim** - never modify or simplify
3. **Use light theme only** - white/off-white backgrounds
4. **Reference CSS variables** for all styling
5. **Include all required scripts** (analytics, navbar-auth, toast)
6. **Add accessibility attributes** to all interactive elements
7. **Test responsive design** with mobile-first approach
8. **Follow component patterns** for buttons, cards, inputs
9. **Maintain consistent spacing** using standard padding/margins
10. **Include proper meta tags** for SEO

### When Creating Components:

- Use semantic HTML5 elements
- Add ARIA labels for screen readers
- Ensure keyboard navigation works
- Follow established component patterns
- Use CSS Grid or Flexbox for layouts
- Keep specificity low (avoid deep nesting)
- Use BEM naming for complex components

### Common Mistakes to Prevent:

❌ Creating dark theme pages  
❌ Modifying navigation order or structure  
❌ Hardcoding colors instead of using CSS variables  
❌ Missing accessibility attributes  
❌ Omitting navbar-auth.js or other required scripts  
❌ Using different button styles  
❌ Changing navbar height or behavior  
❌ Forgetting mobile responsiveness  
❌ Not using design-system.css  

### Example Reference Files:

- **Complete pages**: `index.html`, `portfolio.html`, `dashboard.html`
- **Tool pages**: `overlap-analysis.html`, `sip-calculator.html`
- **Design system**: `css/design-system.css`
- **Style guide**: `STYLE_GUIDE.md`

---

## Questions During Development?

1. **Check** `STYLE_GUIDE.md` for detailed specifications
2. **Reference** existing pages for patterns
3. **Validate** against accessibility checklist
4. **Review** CSS variables in design-system.css
5. **Test** keyboard navigation and screen readers

---

## Version & Updates

**Version**: 1.0  
**Last Updated**: February 14, 2026

**When updating instructions:**
- Document breaking changes clearly
- Update version number
- Test with actual Copilot generations
- Communicate changes to team

---

**Remember: Consistency is key. When in doubt, copy from existing working pages rather than creating new patterns.**
