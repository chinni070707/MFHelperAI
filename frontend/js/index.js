/**
 * Index/Landing Page JavaScript - Extracted from inline JS for performance
 */

// Mobile Menu Toggle
function toggleMenu() {
    const menu = document.querySelector('.nav-menu');
    menu.classList.toggle('active');
}

// Navbar Scroll Effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Scroll Animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

// Observe all animated elements
document.querySelectorAll('.fade-in, .slide-in-left, .slide-in-right').forEach(el => {
    observer.observe(el);
});

// Stats Grid Observer
const statsGrid = document.querySelector('.stats-grid');
if (statsGrid) {
    observer.observe(statsGrid);
}

// Feature List Staggered Animation Observer
document.querySelectorAll('.feature-list').forEach(list => {
    observer.observe(list);
});

// Card Fan-Out Animation
const fanoutObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fan-out');
        } else {
            // Remove fan-out when scrolling away for re-animation
            entry.target.classList.remove('fan-out');
        }
    });
}, { threshold: 0.3 });

const featureCardsContainer = document.getElementById('featureCards');
if (featureCardsContainer) {
    fanoutObserver.observe(featureCardsContainer);
}

// Fan-out tab switching
document.querySelectorAll('.fanout-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        // Remove active from all tabs
        document.querySelectorAll('.fanout-tab').forEach(t => t.classList.remove('active'));
        // Add active to clicked tab
        this.classList.add('active');
        
        // Trigger re-animation
        if (featureCardsContainer) {
            featureCardsContainer.classList.remove('fan-out');
            setTimeout(() => {
                featureCardsContainer.classList.add('fan-out');
            }, 100);
        }
    });
});

// ========== FEATURES SHOWCASE ANIMATION ==========
// Observer for the showcase section - adds transition-engaged class
const showcaseWrapper = document.getElementById('showcaseWrapper');
if (showcaseWrapper) {
    const showcaseObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('transition-engaged');
            }
        });
    }, { threshold: 0.2 });
    
    showcaseObserver.observe(showcaseWrapper);
}

// Showcase Carousel Slide Change
let currentShowcaseSlide = 0;
const showcaseSlides = document.querySelectorAll('.showcase-slide');
const showcaseNavItems = document.querySelectorAll('.showcase-nav-item');

function changeShowcaseSlide(direction) {
    const totalSlides = showcaseSlides.length;
    
    // Remove active from current
    showcaseSlides[currentShowcaseSlide]?.classList.remove('active');
    showcaseNavItems[currentShowcaseSlide]?.classList.remove('active');
    
    // Calculate new index
    currentShowcaseSlide += direction;
    if (currentShowcaseSlide >= totalSlides) currentShowcaseSlide = 0;
    if (currentShowcaseSlide < 0) currentShowcaseSlide = totalSlides - 1;
    
    // Add active to new
    showcaseSlides[currentShowcaseSlide]?.classList.add('active');
    showcaseNavItems[currentShowcaseSlide]?.classList.add('active');
}

// Nav item click handling
showcaseNavItems.forEach((item, index) => {
    item.addEventListener('click', () => {
        showcaseSlides[currentShowcaseSlide]?.classList.remove('active');
        showcaseNavItems[currentShowcaseSlide]?.classList.remove('active');
        
        currentShowcaseSlide = index;
        
        showcaseSlides[currentShowcaseSlide]?.classList.add('active');
        showcaseNavItems[currentShowcaseSlide]?.classList.add('active');
    });
});

// Counter Animation for Stats
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        // Format based on value
        if (target >= 1000) {
            element.textContent = '₹' + Math.floor(current).toLocaleString() + 'Cr+';
        } else if (target >= 100) {
            element.textContent = Math.floor(current).toLocaleString() + '+';
        } else {
            element.textContent = Math.floor(current) + '%';
        }
    }, 16);
}

// Stats Counter Observer
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.dataset.animated) {
            entry.target.dataset.animated = 'true';
            
            // Animate each stat using data-target attribute
            const statItems = entry.target.querySelectorAll('.stat-item h3[data-target]');
            
            statItems.forEach((item, index) => {
                const target = parseInt(item.dataset.target);
                if (target) {
                    animateCounter(item, target, 2000 + (index * 200));
                }
            });
        }
    });
}, { threshold: 0.5 });

if (statsGrid) {
    statsObserver.observe(statsGrid);
}

// Parallax Effect on Scroll
let ticking = false;
window.addEventListener('scroll', () => {
    if (!ticking) {
        window.requestAnimationFrame(() => {
            const scrolled = window.pageYOffset;
            
            // Parallax for hero image
            const heroImage = document.querySelector('.hero-image');
            if (heroImage && scrolled < 800) {
                heroImage.style.transform = `translateY(${scrolled * 0.3}px)`;
            }
            
            // Fade hero text on scroll
            const heroText = document.querySelector('.hero-text');
            if (heroText && scrolled < 600) {
                heroText.style.opacity = 1 - (scrolled / 600);
                heroText.style.transform = `translateY(${scrolled * 0.2}px)`;
            }
            
            ticking = false;
        });
        ticking = true;
    }
});

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
            // Close mobile menu if open
            document.querySelector('.nav-menu').classList.remove('active');
        }
    });
});
