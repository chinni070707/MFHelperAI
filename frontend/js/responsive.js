/**
 * Responsive Design Utilities
 * Mobile-first responsive helpers
 */

// Breakpoints
const breakpoints = {
    mobile: 640,
    tablet: 768,
    laptop: 1024,
    desktop: 1280
};

// Check device type
const device = {
    isMobile: () => window.innerWidth < breakpoints.tablet,
    isTablet: () => window.innerWidth >= breakpoints.tablet && window.innerWidth < breakpoints.laptop,
    isDesktop: () => window.innerWidth >= breakpoints.laptop,
    isTouchDevice: () => 'ontouchstart' in window || navigator.maxTouchPoints > 0
};

// Viewport utilities
const viewport = {
    width: () => window.innerWidth,
    height: () => window.innerHeight,
    orientation: () => window.innerWidth > window.innerHeight ? 'landscape' : 'portrait'
};

// Add mobile-specific CSS
const responsiveStyles = document.createElement('style');
responsiveStyles.textContent = `
    /* Mobile-first responsive improvements */
    @media (max-width: 768px) {
        body {
            font-size: 14px;
        }

        .hero h1 {
            font-size: 2rem !important;
        }

        .hero p {
            font-size: 1rem !important;
        }

        .navbar {
            padding: 12px 15px !important;
            flex-wrap: wrap;
        }

        .logo {
            font-size: 1.2rem !important;
        }

        .nav-links {
            display: none; /* Hide on mobile, add hamburger menu later */
        }

        .upload-container {
            padding: 20px !important;
            margin: 20px 10px !important;
        }

        .btn {
            width: 100% !important;
            padding: 14px 20px !important;
            font-size: 16px !important;
        }

        /* Dashboard improvements */
        .summary-cards {
            grid-template-columns: 1fr !important;
            gap: 15px !important;
            padding: 15px !important;
        }

        .card {
            padding: 15px !important;
        }

        .card h3 {
            font-size: 0.85rem !important;
        }

        .card .value {
            font-size: 1.5rem !important;
        }

        /* Chart containers */
        .chart-container {
            padding: 15px !important;
            margin: 15px 10px !important;
        }

        .chart-container h2 {
            font-size: 1.1rem !important;
        }

        /* Tables */
        .holdings-table {
            font-size: 12px !important;
            overflow-x: auto;
        }

        .holdings-table th,
        .holdings-table td {
            padding: 8px 6px !important;
            white-space: nowrap;
        }

        /* Toast notifications */
        #toast-container {
            right: 10px !important;
            left: 10px !important;
            top: 10px !important;
        }

        .toast {
            min-width: auto !important;
            max-width: 100% !important;
        }

        /* Modal/Dialog */
        .modal-content {
            width: 95% !important;
            margin: 10px !important;
        }

        /* Rebalancing calculator */
        .rebalancing-inputs {
            grid-template-columns: 1fr !important;
        }

        /* Investment style boxes */
        .style-boxes {
            grid-template-columns: 1fr !important;
        }
    }

    /* Tablet improvements */
    @media (min-width: 768px) and (max-width: 1024px) {
        .summary-cards {
            grid-template-columns: repeat(2, 1fr) !important;
        }

        .chart-container {
            grid-template-columns: 1fr !important;
        }
    }

    /* Touch-friendly improvements */
    @media (hover: none) and (pointer: coarse) {
        button, .btn, a {
            min-height: 44px; /* Apple's recommended touch target */
            min-width: 44px;
        }

        input, select, textarea {
            font-size: 16px !important; /* Prevent zoom on iOS */
        }
    }

    /* Landscape mobile */
    @media (max-height: 500px) and (orientation: landscape) {
        .hero {
            padding: 40px 20px !important;
        }

        .hero h1 {
            font-size: 1.8rem !important;
        }
    }

    /* Loading spinner */
    .spinner {
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-top-color: #3b82f6;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }

    /* Skeleton loading */
    .skeleton {
        background: linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.05) 25%,
            rgba(255, 255, 255, 0.1) 50%,
            rgba(255, 255, 255, 0.05) 75%
        );
        background-size: 200% 100%;
        animation: skeleton-loading 1.5s ease-in-out infinite;
    }

    @keyframes skeleton-loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* Safe area for iOS notch */
    @supports (padding-top: env(safe-area-inset-top)) {
        .navbar {
            padding-top: calc(15px + env(safe-area-inset-top)) !important;
        }

        #toast-container {
            top: calc(20px + env(safe-area-inset-top)) !important;
        }
    }

    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }

    /* Focus states for accessibility */
    button:focus, input:focus, select:focus, textarea:focus {
        outline: 2px solid #3b82f6;
        outline-offset: 2px;
    }

    /* Reduced motion for accessibility */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* High contrast mode */
    @media (prefers-contrast: high) {
        .card, .chart-container {
            border: 2px solid rgba(255, 255, 255, 0.5) !important;
        }
    }

    /* Dark mode adjustments (PWA) */
    @media (prefers-color-scheme: light) {
        /* User has light mode preferred - adjust if needed */
    }
`;

document.head.appendChild(responsiveStyles);

// Handle orientation changes
let lastOrientation = viewport.orientation();
window.addEventListener('resize', () => {
    const currentOrientation = viewport.orientation();
    if (currentOrientation !== lastOrientation) {
        lastOrientation = currentOrientation;
        // Trigger re-render of charts if needed
        if (typeof window.refreshCharts === 'function') {
            setTimeout(() => window.refreshCharts(), 300);
        }
    }
});

// Expose utilities globally
window.device = device;
window.viewport = viewport;
window.breakpoints = breakpoints;
