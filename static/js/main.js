/**
 * CodeXam Main JavaScript
 * Core functionality for the CodeXam platform
 */

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('CodeXam application initialized');
    
    // Initialize Bootstrap tooltips
    initializeTooltips();
    
    // Initialize any other components
    initializeComponents();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize other components
 */
function initializeComponents() {
    // Add any component initialization here
    console.log('Components initialized');
}

/**
 * Utility function to show alerts
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        console.warn('Alert container not found');
        return;
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Utility function for AJAX requests
 */
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    return fetch(url, finalOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('Request failed:', error);
            throw error;
        });
}
/**
 * 
Enhanced Interactive Features for CodeXam
 */

// Global state for animations and interactions
const CodeXamUI = {
    isAnimating: false,
    keyboardShortcuts: {},
    loadingStates: new Set(),
    observers: new Set(), // Track observers for cleanup
    eventListeners: new Map(), // Track event listeners for cleanup
    
    // Initialize enhanced features
    init() {
        this.setupAnimations();
        this.setupKeyboardNavigation();
        this.setupLoadingStates();
        this.setupMicroInteractions();
        this.setupAccessibility();
        console.log('Enhanced UI features initialized');
    },
    
    // Setup smooth animations and transitions
    setupAnimations() {
        // Add intersection observer for scroll animations
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-slide-up');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });
            
            // Track observer for cleanup
            this.observers.add(observer);
            
            // Observe elements that should animate on scroll
            document.querySelectorAll('.cyber-card, .ranking-item, .stat-card, .problem-card').forEach(el => {
                observer.observe(el);
            });
        }
        
        // Add hover effects for interactive elements
        this.setupHoverEffects();
    },
    
    // Setup hover effects
    setupHoverEffects() {
        // Enhanced hover effects for cards
        document.querySelectorAll('.cyber-card, .ranking-item, .stat-card, .problem-card').forEach(card => {
            card.addEventListener('mouseenter', (e) => {
                if (!this.isAnimating) {
                    e.target.style.transform = 'translateY(-4px)';
                    e.target.style.transition = 'all 0.3s ease';
                }
            });
            
            card.addEventListener('mouseleave', (e) => {
                e.target.style.transform = 'translateY(0)';
            });
        });
        
        // Glow effects for buttons
        document.querySelectorAll('.btn-cyber-primary, .cta-button').forEach(btn => {
            btn.addEventListener('mouseenter', (e) => {
                e.target.classList.add('animate-glow');
            });
            
            btn.addEventListener('mouseleave', (e) => {
                e.target.classList.remove('animate-glow');
            });
        });
    },
    
    // Setup keyboard navigation
    setupKeyboardNavigation() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Skip if user is typing in an input
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }
            
            switch(e.key) {
                case 'p':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.navigateTo('/problems');
                    }
                    break;
                case 's':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.navigateTo('/submissions');
                    }
                    break;
                case 'l':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.navigateTo('/leaderboard');
                    }
                    break;
                case 'h':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.navigateTo('/');
                    }
                    break;
                case 'Escape':
                    this.closeModals();
                    break;
                case '?':
                    if (!e.ctrlKey && !e.metaKey) {
                        this.showKeyboardShortcuts();
                    }
                    break;
            }
        });
        
        // Enhanced focus management
        this.setupFocusManagement();
    },
    
    // Setup focus management for accessibility
    setupFocusManagement() {
        // Trap focus in modals
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('shown.bs.modal', () => {
                const focusableElements = modal.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                if (focusableElements.length > 0) {
                    focusableElements[0].focus();
                }
            });
        });
        
        // Skip links for accessibility
        this.addSkipLinks();
    },
    
    // Add skip links for screen readers
    addSkipLinks() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.textContent = 'Skip to main content';
        skipLink.className = 'skip-link sr-only';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: var(--accent-primary);
            color: var(--bg-primary);
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 1000;
            transition: top 0.3s;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
            skipLink.classList.remove('sr-only');
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
            skipLink.classList.add('sr-only');
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
    },
    
    // Setup loading states
    setupLoadingStates() {
        // Intercept form submissions to show loading states
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    this.showLoadingState(submitBtn);
                }
            });
        });
        
        // Intercept AJAX requests
        this.interceptAjaxRequests();
    },
    
    // Show loading state on element
    showLoadingState(element, text = 'Loading...') {
        if (this.loadingStates.has(element)) return;
        
        this.loadingStates.add(element);
        const originalText = element.textContent;
        const originalDisabled = element.disabled;
        
        element.disabled = true;
        element.innerHTML = `
            <span class="loading-spinner"></span>
            ${text}
        `;
        element.classList.add('loading');
        
        // Store original state
        element._originalState = { text: originalText, disabled: originalDisabled };
    },
    
    // Hide loading state
    hideLoadingState(element) {
        if (!this.loadingStates.has(element)) return;
        
        this.loadingStates.delete(element);
        const originalState = element._originalState;
        
        if (originalState) {
            element.textContent = originalState.text;
            element.disabled = originalState.disabled;
            element.classList.remove('loading');
            delete element._originalState;
        }
    },
    
    // Setup micro-interactions
    setupMicroInteractions() {
        // Ripple effect for buttons
        document.querySelectorAll('.btn-cyber-primary, .cta-button').forEach(btn => {
            btn.addEventListener('click', this.createRippleEffect);
        });
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Auto-resize textareas
        document.querySelectorAll('textarea').forEach(textarea => {
            textarea.addEventListener('input', this.autoResizeTextarea);
        });
    },
    
    // Create ripple effect
    createRippleEffect(e) {
        const button = e.currentTarget;
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('span');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple 0.6s linear;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    },
    
    // Auto-resize textarea
    autoResizeTextarea(e) {
        const textarea = e.target;
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    },
    
    // Setup accessibility features
    setupAccessibility() {
        // Announce page changes to screen readers
        this.announcePageChanges();
        
        // Enhanced keyboard navigation for custom components
        this.setupCustomKeyboardNavigation();
        
        // High contrast mode detection
        this.detectHighContrastMode();
    },
    
    // Announce page changes
    announcePageChanges() {
        const announcer = document.createElement('div');
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.className = 'sr-only';
        announcer.id = 'page-announcer';
        document.body.appendChild(announcer);
        
        // Announce current page
        const pageTitle = document.title;
        setTimeout(() => {
            announcer.textContent = `Page loaded: ${pageTitle}`;
        }, 100);
    },
    
    // Setup custom keyboard navigation
    setupCustomKeyboardNavigation() {
        // Arrow key navigation for card grids
        document.querySelectorAll('.problems-grid, .rankings-list').forEach(grid => {
            const items = grid.querySelectorAll('.problem-card, .ranking-item');
            items.forEach((item, index) => {
                item.setAttribute('tabindex', index === 0 ? '0' : '-1');
                item.addEventListener('keydown', (e) => {
                    let newIndex = index;
                    
                    switch(e.key) {
                        case 'ArrowDown':
                        case 'ArrowRight':
                            e.preventDefault();
                            newIndex = Math.min(index + 1, items.length - 1);
                            break;
                        case 'ArrowUp':
                        case 'ArrowLeft':
                            e.preventDefault();
                            newIndex = Math.max(index - 1, 0);
                            break;
                        case 'Home':
                            e.preventDefault();
                            newIndex = 0;
                            break;
                        case 'End':
                            e.preventDefault();
                            newIndex = items.length - 1;
                            break;
                        case 'Enter':
                        case ' ':
                            e.preventDefault();
                            item.click();
                            break;
                    }
                    
                    if (newIndex !== index) {
                        items[index].setAttribute('tabindex', '-1');
                        items[newIndex].setAttribute('tabindex', '0');
                        items[newIndex].focus();
                    }
                });
            });
        });
    },
    
    // Detect high contrast mode
    detectHighContrastMode() {
        if (window.matchMedia('(prefers-contrast: high)').matches) {
            document.body.classList.add('high-contrast');
        }
        
        // Listen for changes
        window.matchMedia('(prefers-contrast: high)').addEventListener('change', (e) => {
            if (e.matches) {
                document.body.classList.add('high-contrast');
            } else {
                document.body.classList.remove('high-contrast');
            }
        });
    },
    
    // Intercept AJAX requests for loading states
    interceptAjaxRequests() {
        // Store original fetch for restoration during cleanup
        if (!window._originalFetch) {
            window._originalFetch = window.fetch;
        }
        
        const originalFetch = window._originalFetch;
        window.fetch = (...args) => {
            // Show global loading indicator with debouncing
            const loadingTimeout = setTimeout(() => {
                this.showGlobalLoading();
            }, 100); // Only show loading if request takes longer than 100ms
            
            return originalFetch(...args)
                .finally(() => {
                    clearTimeout(loadingTimeout);
                    this.hideGlobalLoading();
                })
                .catch(error => {
                    console.error('Fetch request failed:', error);
                    // Re-throw to maintain original behavior
                    throw error;
                });
        };
    },
    
    // Show global loading indicator
    showGlobalLoading() {
        let loader = document.getElementById('global-loader');
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'global-loader';
            loader.className = 'global-loading';
            loader.innerHTML = `
                <div class="loading-spinner-large"></div>
                <div class="loading-text">Processing...</div>
            `;
            document.body.appendChild(loader);
        }
        loader.style.display = 'flex';
    },
    
    // Hide global loading indicator
    hideGlobalLoading() {
        const loader = document.getElementById('global-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    },
    
    // Navigation helper
    navigateTo(url) {
        this.showGlobalLoading();
        window.location.href = url;
    },
    
    // Close modals
    closeModals() {
        document.querySelectorAll('.modal.show').forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
    },
    
    // Show keyboard shortcuts help
    showKeyboardShortcuts() {
        const shortcuts = [
            { key: 'Ctrl/Cmd + P', action: 'Go to Problems' },
            { key: 'Ctrl/Cmd + S', action: 'Go to Submissions' },
            { key: 'Ctrl/Cmd + L', action: 'Go to Leaderboard' },
            { key: 'Ctrl/Cmd + H', action: 'Go to Home' },
            { key: 'Escape', action: 'Close modals' },
            { key: '?', action: 'Show this help' },
            { key: 'Arrow keys', action: 'Navigate cards' },
            { key: 'Enter/Space', action: 'Activate focused element' }
        ];
        
        const helpContent = shortcuts.map(s => 
            `<div class="shortcut-item">
                <kbd class="keyboard-key">${s.key}</kbd>
                <span class="shortcut-description">${s.action}</span>
            </div>`
        ).join('');
        
        // Create or update help modal
        let helpModal = document.getElementById('keyboard-help-modal');
        if (!helpModal) {
            helpModal = document.createElement('div');
            helpModal.id = 'keyboard-help-modal';
            helpModal.className = 'modal fade';
            helpModal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Keyboard Shortcuts</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="shortcuts-list">${helpContent}</div>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(helpModal);
        }
        
        const modal = new bootstrap.Modal(helpModal);
        modal.show();
    },

    /**
     * Cleanup method to prevent memory leaks
     * Call this when the page is being unloaded or component is destroyed
     */
    cleanup() {
        // Disconnect all observers
        this.observers.forEach(observer => {
            if (observer && typeof observer.disconnect === 'function') {
                observer.disconnect();
            }
        });
        this.observers.clear();

        // Remove tracked event listeners
        this.eventListeners.forEach((listener, element) => {
            if (element && typeof element.removeEventListener === 'function') {
                element.removeEventListener(listener.event, listener.handler);
            }
        });
        this.eventListeners.clear();

        // Clear loading states
        this.loadingStates.clear();

        console.log('CodeXamUI cleanup completed');
    },

    /**
     * Helper method to track event listeners for cleanup
     * @param {HTMLElement} element - Element to add listener to
     * @param {string} event - Event type
     * @param {Function} handler - Event handler
     * @param {Object} options - Event listener options
     */
    addTrackedEventListener(element, event, handler, options = {}) {
        element.addEventListener(event, handler, options);
        this.eventListeners.set(element, { event, handler, options });
    },

    /**
     * Performance monitoring utilities
     */
    performance: {
        marks: new Map(),
        
        /**
         * Start performance measurement
         * @param {string} name - Measurement name
         */
        mark(name) {
            if ('performance' in window && performance.mark) {
                performance.mark(`${name}-start`);
                this.marks.set(name, performance.now());
            }
        },

        /**
         * End performance measurement and log result
         * @param {string} name - Measurement name
         */
        measure(name) {
            if ('performance' in window && performance.measure && this.marks.has(name)) {
                const startTime = this.marks.get(name);
                const endTime = performance.now();
                const duration = endTime - startTime;
                
                performance.mark(`${name}-end`);
                performance.measure(name, `${name}-start`, `${name}-end`);
                
                console.log(`Performance: ${name} took ${duration.toFixed(2)}ms`);
                this.marks.delete(name);
                
                return duration;
            }
            return 0;
        }
    },

    /**
     * Debounce utility function
     * @param {Function} func - Function to debounce
     * @param {number} wait - Wait time in milliseconds
     * @param {boolean} immediate - Execute immediately
     * @returns {Function} Debounced function
     */
    debounce(func, wait, immediate = false) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func.apply(this, args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func.apply(this, args);
        };
    },

    /**
     * Throttle utility function
     * @param {Function} func - Function to throttle
     * @param {number} limit - Time limit in milliseconds
     * @returns {Function} Throttled function
     */
    throttle(func, limit) {
        let inThrottle;
        return function executedFunction(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Initialize enhanced features when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    CodeXamUI.init();
});

// Add CSS for new interactive features
const interactiveStyles = document.createElement('style');
interactiveStyles.textContent = `
    /* Loading spinner */
    .loading-spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid var(--accent-primary);
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s linear infinite;
        margin-right: 8px;
    }
    
    .loading-spinner-large {
        width: 40px;
        height: 40px;
        border: 4px solid var(--accent-primary);
        border-top-color: transparent;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Global loading overlay */
    .global-loading {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(10, 10, 10, 0.8);
        display: none;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(4px);
    }
    
    .loading-text {
        color: var(--text-primary);
        margin-top: var(--space-4);
        font-family: var(--font-mono);
    }
    
    /* Ripple animation */
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    /* Keyboard shortcuts modal */
    .shortcuts-list {
        display: flex;
        flex-direction: column;
        gap: var(--space-3);
    }
    
    .shortcut-item {
        display: flex;
        align-items: center;
        gap: var(--space-4);
        padding: var(--space-2);
        border-radius: var(--radius-md);
        background: var(--bg-secondary);
    }
    
    .keyboard-key {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-sm);
        padding: var(--space-1) var(--space-2);
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        color: var(--accent-primary);
        min-width: 120px;
        text-align: center;
    }
    
    .shortcut-description {
        color: var(--text-secondary);
        flex: 1;
    }
    
    /* Enhanced focus styles */
    *:focus-visible {
        outline: 2px solid var(--accent-primary);
        outline-offset: 2px;
        border-radius: var(--radius-sm);
    }
    
    /* Skip link */
    .skip-link:focus {
        clip: auto !important;
        height: auto !important;
        width: auto !important;
        position: absolute !important;
        overflow: visible !important;
    }
    
    /* High contrast mode adjustments */
    .high-contrast {
        --accent-primary: #00ff00;
        --text-primary: #ffffff;
        --bg-primary: #000000;
        --border-primary: #ffffff;
    }
    
    /* Loading state for buttons */
    .loading {
        opacity: 0.7;
        cursor: not-allowed;
    }
    
    /* Smooth transitions for all interactive elements */
    .cyber-card,
    .ranking-item,
    .stat-card,
    .problem-card,
    .btn-cyber-primary,
    .cta-button {
        transition: all var(--transition-normal);
    }
    
    /* Enhanced hover states */
    .cyber-card:hover,
    .ranking-item:hover,
    .stat-card:hover,
    .problem-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px var(--accent-glow);
    }
    
    /* Touch-friendly interactions for mobile */
    @media (hover: none) and (pointer: coarse) {
        .cyber-card:active,
        .ranking-item:active,
        .stat-card:active,
        .problem-card:active {
            transform: scale(0.98);
        }
        
        .btn-cyber-primary:active,
        .cta-button:active {
            transform: scale(0.95);
        }
    }
`;

document.head.appendChild(interactiveStyles);

/**
 * Enhanced UI Initialization Module
 * Consolidates all DOM-ready initialization logic
 */
const UIEnhancementModule = {
    /**
     * Initialize all UI enhancements
     */
    init() {
        this.preventTransitionsOnLoad();
        this.enhanceDropdownHandling();
        this.setupNavigationEffects();
        this.setupPerformanceOptimizations();
    },

    /**
     * Prevent CSS transitions during page load for better performance
     */
    preventTransitionsOnLoad() {
        document.body.classList.add('preload');
        
        // Use requestAnimationFrame for better performance
        requestAnimationFrame(() => {
            setTimeout(() => {
                document.body.classList.remove('preload');
            }, 100);
        });
    },

    /**
     * Enhanced dropdown handling with proper event management
     */
    enhanceDropdownHandling() {
        const dropdownToggles = document.querySelectorAll('[data-bs-toggle="dropdown"]');
        
        dropdownToggles.forEach(toggle => {
            // Use more specific event handling
            toggle.addEventListener('shown.bs.dropdown', this.handleDropdownShown.bind(this));
            toggle.addEventListener('hidden.bs.dropdown', this.handleDropdownHidden.bind(this));
        });
    },

    /**
     * Handle dropdown shown event
     * @param {Event} event - Bootstrap dropdown event
     */
    handleDropdownShown(event) {
        const menu = event.target.nextElementSibling;
        if (menu && menu.classList.contains('dropdown-menu')) {
            menu.classList.add('show');
            // Add ARIA attributes for accessibility
            menu.setAttribute('aria-expanded', 'true');
        }
    },

    /**
     * Handle dropdown hidden event
     * @param {Event} event - Bootstrap dropdown event
     */
    handleDropdownHidden(event) {
        const menu = event.target.nextElementSibling;
        if (menu && menu.classList.contains('dropdown-menu')) {
            menu.classList.remove('show');
            menu.setAttribute('aria-expanded', 'false');
        }
    },

    /**
     * Setup navigation effects with performance optimization
     */
    setupNavigationEffects() {
        const navLinks = document.querySelectorAll('.nav-link');
        const navbar = document.querySelector('.cyber-navbar');
        
        if (!navbar) return; // Guard clause for missing navbar
        
        navLinks.forEach(link => {
            link.addEventListener('click', (event) => {
                // Only add loading state for actual navigation (not hash links)
                const href = link.getAttribute('href');
                if (href && !href.startsWith('#') && !event.defaultPrevented) {
                    this.addNavbarLoadingState(navbar);
                }
            });
        });
    },

    /**
     * Add loading state to navbar with cleanup
     * @param {HTMLElement} navbar - The navigation bar element
     */
    addNavbarLoadingState(navbar) {
        navbar.classList.add('navbar-loading');
        
        // Use a more reasonable timeout and ensure cleanup
        const timeoutId = setTimeout(() => {
            navbar.classList.remove('navbar-loading');
        }, 800); // Reduced from 1000ms for better UX
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            clearTimeout(timeoutId);
            navbar.classList.remove('navbar-loading');
        }, { once: true });
    },

    /**
     * Setup performance optimizations
     */
    setupPerformanceOptimizations() {
        // Debounce resize events
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });
    },

    /**
     * Handle window resize events
     */
    handleResize() {
        // Recalculate any dynamic layouts if needed
        console.log('Window resized - recalculating layouts');
    }
};

// Single consolidated DOMContentLoaded event listener
document.addEventListener('DOMContentLoaded', function() {
    console.log('CodeXam application initialized');
    
    // Initialize core functionality
    initializeTooltips();
    initializeComponents();
    
    // Initialize enhanced UI features
    CodeXamUI.init();
    
    // Initialize UI enhancements
    UIEnhancementModule.init();
});

// Cleanup on page unload to prevent memory leaks
window.addEventListener('beforeunload', () => {
    if (typeof CodeXamUI !== 'undefined' && CodeXamUI.cleanup) {
        CodeXamUI.cleanup();
    }
});// Sys
tem Info function for the Elite Journey section
function showSystemInfo() {
    const systemInfo = {
        platform: 'CodeXam Elite Arena',
        version: '2.1.0',
        status: 'ONLINE',
        challenges: '6 Active',
        users: '6 Elite Coders',
        uptime: '99.9%'
    };
    
    let infoText = 'SYSTEM INFORMATION\n';
    infoText += '==================\n\n';
    infoText += `Platform: ${systemInfo.platform}\n`;
    infoText += `Version: ${systemInfo.version}\n`;
    infoText += `Status: ${systemInfo.status}\n`;
    infoText += `Active Challenges: ${systemInfo.challenges}\n`;
    infoText += `Elite Coders: ${systemInfo.users}\n`;
    infoText += `Uptime: ${systemInfo.uptime}\n\n`;
    infoText += 'Ready for combat. Initialize when ready.';
    
    alert(infoText);
}// 
Enhanced System Info Modal
function showSystemInfo() {
    // Create modal backdrop
    const backdrop = document.createElement('div');
    backdrop.className = 'system-info-backdrop';
    backdrop.onclick = closeSystemInfo;
    
    // Create modal container
    const modal = document.createElement('div');
    modal.className = 'system-info-modal';
    modal.id = 'systemInfoModal';
    
    // Get current time
    const now = new Date();
    const timestamp = now.toISOString().replace('T', ' ').substring(0, 19);
    
    // System info data
    const systemData = {
        platform: 'CodeXam Elite Arena',
        version: 'v2.1.0',
        status: 'OPERATIONAL',
        uptime: '99.9%',
        challenges: '6 Active',
        users: '6 Elite Coders',
        submissions: '24 Today',
        success_rate: '48.2%',
        framework: 'Flask + Python',
        database: 'SQLite',
        security: 'SECURED',
        last_update: timestamp
    };
    
    modal.innerHTML = `
        <div class="system-terminal">
            <div class="terminal-header">
                <div class="terminal-controls">
                    <span class="control-dot red"></span>
                    <span class="control-dot yellow"></span>
                    <span class="control-dot green"></span>
                </div>
                <div class="terminal-title">system_diagnostics.exe</div>
                <button class="close-btn" onclick="closeSystemInfo()">×</button>
            </div>
            
            <div class="terminal-body">
                <div class="system-header">
                    <div class="ascii-art">
    ╔═══════════════════════════════════════╗
    ║         SYSTEM DIAGNOSTICS            ║
    ║    CodeXam Elite Arena v2.1.0         ║
    ╚═══════════════════════════════════════╝
                    </div>
                </div>
                
                <div class="system-sections">
                    <div class="system-section">
                        <div class="section-title">
                            <span class="section-icon">⚡</span>
                            <span>CORE SYSTEM</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Platform:</span>
                            <span class="sys-value">${systemData.platform}</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Version:</span>
                            <span class="sys-value">${systemData.version}</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Status:</span>
                            <span class="sys-value status-online">${systemData.status}</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Uptime:</span>
                            <span class="sys-value">${systemData.uptime}</span>
                        </div>
                    </div>
                    
                    <div class="system-section">
                        <div class="section-title">
                            <span class="section-icon">📊</span>
                            <span>COMBAT METRICS</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Active Challenges:</span>
                            <span class="sys-value">${systemData.challenges}</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Elite Coders:</span>
                            <span class="sys-value">${systemData.users}</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Submissions:</span>
                            <span class="sys-value">${systemData.submissions}</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Success Rate:</span>
                            <span class="sys-value">${systemData.success_rate}</span>
                        </div>
                    </div>
                    
                    <div class="system-section">
                        <div class="section-title">
                            <span class="section-icon">🔧</span>
                            <span>TECHNICAL STACK</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Framework:</span>
                            <span class="sys-value">${systemData.framework}</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Database:</span>
                            <span class="sys-value">${systemData.database}</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Security:</span>
                            <span class="sys-value status-secure">${systemData.security}</span>
                        </div>
                        <div class="system-line">
                            <span class="sys-key">Last Update:</span>
                            <span class="sys-value">${systemData.last_update}</span>
                        </div>
                    </div>
                </div>
                
                <div class="system-footer">
                    <div class="status-line">
                        <span class="status-indicator online"></span>
                        <span class="status-text">ALL SYSTEMS OPERATIONAL</span>
                    </div>
                    <div class="command-line">
                        <span class="prompt">admin@codexam:~$</span>
                        <span class="command">system_check --complete</span>
                        <span class="cursor">|</span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add to page
    backdrop.appendChild(modal);
    document.body.appendChild(backdrop);
    
    // Add animation
    setTimeout(() => {
        backdrop.classList.add('show');
        modal.classList.add('show');
    }, 10);
    
    // Add escape key listener
    document.addEventListener('keydown', handleSystemInfoEscape);
}

function closeSystemInfo() {
    const backdrop = document.querySelector('.system-info-backdrop');
    if (backdrop) {
        backdrop.classList.remove('show');
        setTimeout(() => {
            backdrop.remove();
        }, 300);
    }
    document.removeEventListener('keydown', handleSystemInfoEscape);
}

function handleSystemInfoEscape(e) {
    if (e.key === 'Escape') {
        closeSystemInfo();
    }
}