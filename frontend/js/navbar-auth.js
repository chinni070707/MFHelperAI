/**
 * Navbar Authentication State Handler
 * Updates navbar based on user authentication status
 */

(function() {
    'use strict';

    function updateNavbarAuth() {
        const authToken = localStorage.getItem('authToken');
        const userInfoStr = localStorage.getItem('userInfo');
        
        // Find all nav menus on the page
        const navMenus = document.querySelectorAll('.nav-menu');
        
        navMenus.forEach(navMenu => {
            // Find the Sign In and Get Started items
            const signInItem = navMenu.querySelector('a[href="/login.html"], a[href="/auth.html"]')?.parentElement;
            const getStartedItem = navMenu.querySelector('a[href="/signup.html"], a[href*="/auth.html?tab=signup"]')?.parentElement;
            
            if (authToken && userInfoStr) {
                try {
                    const userInfo = JSON.parse(userInfoStr);
                    const userName = userInfo.full_name || userInfo.email.split('@')[0];
                    
                    // Hide Sign In and Get Started
                    if (signInItem) signInItem.style.display = 'none';
                    if (getStartedItem) getStartedItem.style.display = 'none';
                    
                    // Check if user dropdown already exists
                    let userDropdownItem = navMenu.querySelector('.user-dropdown-item');
                    
                    if (!userDropdownItem) {
                        // Create user dropdown
                        userDropdownItem = document.createElement('li');
                        userDropdownItem.className = 'user-dropdown-item';
                        userDropdownItem.innerHTML = `
                            <div class="user-dropdown">
                                <button class="user-button" onclick="toggleUserDropdown(event)">
                                    <span class="user-avatar">${userName.charAt(0).toUpperCase()}</span>
                                    <span class="user-name">${userName}</span>
                                    <svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                                        <path d="M6 9L1 4h10L6 9z"/>
                                    </svg>
                                </button>
                                <div class="user-dropdown-menu">
                                    <a href="/portfolio.html" class="dropdown-item">
                                        <span>📊</span> Portfolio
                                    </a>
                                    <a href="/goal-planning.html" class="dropdown-item">
                                        <span>🎯</span> Goals
                                    </a>
                                    <a href="/dashboard.html" class="dropdown-item">
                                        <span>📈</span> Analytics
                                    </a>
                                    <div class="dropdown-divider"></div>
                                    <a href="#" onclick="handleLogout(event)" class="dropdown-item logout-item">
                                        <span>🚪</span> Logout
                                    </a>
                                </div>
                            </div>
                        `;
                        navMenu.appendChild(userDropdownItem);
                    }
                } catch (e) {
                    console.error('Error parsing user info:', e);
                }
            } else {
                // User not logged in - show Sign In and Get Started
                if (signInItem) signInItem.style.display = '';
                if (getStartedItem) getStartedItem.style.display = '';
                
                // Remove user dropdown if it exists
                const userDropdownItem = navMenu.querySelector('.user-dropdown-item');
                if (userDropdownItem) {
                    userDropdownItem.remove();
                }
            }
        });
    }

    // Toggle user dropdown
    window.toggleUserDropdown = function(event) {
        event.stopPropagation();
        const dropdown = event.currentTarget.nextElementSibling;
        const isOpen = dropdown.classList.contains('show');
        
        // Close all dropdowns first
        document.querySelectorAll('.user-dropdown-menu').forEach(menu => {
            menu.classList.remove('show');
        });
        
        // Toggle current dropdown
        if (!isOpen) {
            dropdown.classList.add('show');
        }
    };

    // Close dropdown when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.user-dropdown')) {
            document.querySelectorAll('.user-dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });

    // Handle logout
    window.handleLogout = function(event) {
        event.preventDefault();
        
        // Clear auth data
        localStorage.removeItem('authToken');
        localStorage.removeItem('userInfo');
        
        // Show toast if available
        if (window.toast) {
            toast.success('Logged out successfully');
        }
        
        // Redirect to home
        setTimeout(() => {
            window.location.href = '/';
        }, 500);
    };

    // Add styles for user dropdown
    const style = document.createElement('style');
    style.textContent = `
        .user-dropdown {
            position: relative;
        }

        .user-button {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: transparent;
            border: 2px solid var(--primary-green, #7FC04C);
            border-radius: 50px;
            color: var(--text-primary, #212529);
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .user-button:hover {
            background: var(--primary-green, #7FC04C);
            color: white;
        }

        .user-avatar {
            width: 28px;
            height: 28px;
            background: var(--primary-green, #7FC04C);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.9rem;
        }

        .user-name {
            font-size: 0.95rem;
            max-width: 120px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .dropdown-arrow {
            transition: transform 0.3s ease;
        }

        .user-button:hover .dropdown-arrow {
            transform: rotate(180deg);
        }

        .user-dropdown-menu {
            position: absolute;
            top: calc(100% + 10px);
            right: 0;
            min-width: 200px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
            padding: 0.5rem 0;
            opacity: 0;
            visibility: hidden;
            transform: translateY(-10px);
            transition: all 0.3s ease;
            z-index: 1000;
        }

        .user-dropdown-menu.show {
            opacity: 1;
            visibility: visible;
            transform: translateY(0);
        }

        .dropdown-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1.25rem;
            color: #212529;
            text-decoration: none;
            font-size: 0.95rem;
            transition: background 0.2s ease;
        }

        .dropdown-item:hover {
            background: #f8f9fa;
        }

        .dropdown-item span {
            font-size: 1.1rem;
        }

        .dropdown-divider {
            height: 1px;
            background: #e9ecef;
            margin: 0.5rem 0;
        }

        .logout-item {
            color: #dc3545;
        }

        .logout-item:hover {
            background: #fff5f5;
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
            .user-dropdown-menu {
                position: fixed;
                top: 70px;
                right: 10px;
                left: 10px;
                width: auto;
            }

            .user-name {
                display: none;
            }

            .user-button {
                padding: 0.5rem;
            }
        }
    `;
    document.head.appendChild(style);

    // Update navbar on page load
    document.addEventListener('DOMContentLoaded', updateNavbarAuth);
    
    // Update navbar when storage changes (e.g., login in another tab)
    window.addEventListener('storage', function(e) {
        if (e.key === 'authToken' || e.key === 'userInfo') {
            updateNavbarAuth();
        }
    });

    // Expose function for manual updates
    window.updateNavbarAuth = updateNavbarAuth;
})();
