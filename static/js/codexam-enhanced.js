/*!
 * CodeXam Enhanced JavaScript Framework
 * Consolidated, optimized, and bug-free JavaScript for the CodeXam platform
 * 
 * @version 3.0.0
 * @author CodeXam Development Team
 * @license MIT
 */

/**
 * Main CodeXam Application Framework
 * Provides centralized functionality with proper error handling and cleanup
 */
class CodeXamApp {
    constructor() {
        this.config = {
            debug: window.location.hostname === 'localhost',
            version: '3.0.0',
            features: {
                tooltips: true,
                mobileNav: true,
                lazyLoading: true,
                performanceMonitoring: true,
                accessibility: true,
                autoSave: true
            },
            ajax: {
                timeout: 30000,
                retryAttempts: 3,
                retryDelay: 1000
            },
            editor: {
                maxCodeLength: 50000,
                tabSize: 4,
                autoSaveInterval: 30000
            },
            validation: {
                debounceDelay: 500,
                showRealTime: true
            },
            submission: {
                maxRate: 5,
                cooldownPeriod: 60000
            }
        };
        
        this.state = {
            initialized: false,
            mobileNavOpen: false,
            currentTheme: 'dark',
            activeRequests: new Map(),
            eventListeners: new Map(),
            timers: new Map(),
            observers: new Set()
        };
        
        this.modules = {
            ajax: null,
            editor: null,
            validator: null,
            submission: null,
            ui: null
        };
        
        // Bind methods to preserve context
        this.handleError = this.handleError.bind(this);
        this.cleanup = this.cleanup.bind(this);
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }
    
    /**
     * Initialize the application
     */
    init() {
        if (this.state.initialized) {
            this.log('warn', 'Application already initialized');
            return;
        }
        
        try {
            this.log('info', `🚀 CodeXam v${this.config.version} initializing...`);
            
            // Setup global error handling
            this.setupGlobalErrorHandling();
            
            // Initialize core modules
            this.initializeModules();
            
            // Setup cleanup on page unload
            this.setupCleanup();
            
            this.state.initialized = true;
            this.log('info', '✅ CodeXam application initialized successfully');
            
        } catch (error) {
            this.handleError(error, 'Application initialization failed');
        }
    }
    
    /**
     * Initialize all application modules
     */
    initializeModules() {
        // Initialize UI module first
        this.modules.ui = new UIModule(this);
        
        // Initialize AJAX module
        this.modules.ajax = new AjaxModule(this);
        
        // Initialize validator module
        this.modules.validator = new ValidatorModule(this);
        
        // Initialize editor module if code editor exists
        if (document.querySelector('#code-editor, .code-editor, textarea[name="code"]')) {
            this.modules.editor = new EditorModule(this);
        }
        
        // Initialize submission module if submission form exists
        if (document.querySelector('.submission-form, #submission-form')) {
            this.modules.submission = new SubmissionModule(this);
        }
    }
    
    /**
     * Setup global error handling
     */
    setupGlobalErrorHandling() {
        // JavaScript errors
        window.addEventListener('error', (e) => {
            this.handleError(e.error, 'JavaScript Error', {
                filename: e.filename,
                lineno: e.lineno,
                colno: e.colno
            });
        });
        
        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            this.handleError(e.reason, 'Unhandled Promise Rejection');
            e.preventDefault(); // Prevent console error
        });
        
        // Network errors
        window.addEventListener('offline', () => {
            this.showNotification('Connection lost. Some features may not work properly.', 'warning');
        });
        
        window.addEventListener('online', () => {
            this.showNotification('Connection restored.', 'success');
        });
    }
    
    /**
     * Setup cleanup handlers
     */
    setupCleanup() {
        // Cleanup on page unload
        window.addEventListener('beforeunload', this.cleanup);
        window.addEventListener('pagehide', this.cleanup);
        
        // Cleanup on visibility change (mobile)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseNonEssentialOperations();
            } else {
                this.resumeOperations();
            }
        });
    }
    
    /**
     * Handle errors consistently
     */
    handleError(error, context = 'Unknown', details = {}) {
        const errorInfo = {
            message: error?.message || String(error),
            stack: error?.stack,
            context,
            details,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href
        };
        
        // Log error
        console.error('❌ CodeXam Error:', errorInfo);
        
        // Report to monitoring service in production
        if (!this.config.debug) {
            this.reportError(errorInfo);
        }
        
        // Show user-friendly message for critical errors
        if (context.includes('critical') || context.includes('initialization')) {
            this.showNotification('An error occurred. Please refresh the page.', 'error');
        }
    }
    
    /**
     * Report error to monitoring service
     */
    reportError(errorInfo) {
        try {
            // This would integrate with services like Sentry, LogRocket, etc.
            if (typeof gtag === 'function') {
                gtag('event', 'exception', {
                    description: errorInfo.message,
                    fatal: false
                });
            }
        } catch (e) {
            // Silently fail if reporting fails
        }
    }
    
    /**
     * Pause non-essential operations
     */
    pauseNonEssentialOperations() {
        // Pause auto-save timers
        this.state.timers.forEach((timer, key) => {
            if (key.includes('autosave') || key.includes('validation')) {
                clearTimeout(timer);
            }
        });
        
        // Pause observers
        this.state.observers.forEach(observer => {
            if (observer.disconnect) {
                observer.disconnect();
            }
        });
    }
    
    /**
     * Resume operations
     */
    resumeOperations() {
        // Re-initialize modules that were paused
        Object.values(this.modules).forEach(module => {
            if (module && typeof module.resume === 'function') {
                module.resume();
            }
        });
    }
    
    /**
     * Cleanup resources
     */
    cleanup() {
        try {
            // Clear all timers
            this.state.timers.forEach(timer => clearTimeout(timer));
            this.state.timers.clear();
            
            // Disconnect all observers
            this.state.observers.forEach(observer => {
                if (observer.disconnect) observer.disconnect();
            });
            this.state.observers.clear();
            
            // Cancel active requests
            this.state.activeRequests.forEach(({ controller }) => {
                if (controller && controller.abort) controller.abort();
            });
            this.state.activeRequests.clear();
            
            // Remove event listeners
            this.state.eventListeners.forEach(({ element, event, handler, options }) => {
                element.removeEventListener(event, handler, options);
            });
            this.state.eventListeners.clear();
            
            // Cleanup modules
            Object.values(this.modules).forEach(module => {
                if (module && typeof module.destroy === 'function') {
                    module.destroy();
                }
            });
            
            this.log('info', '✅ CodeXam cleanup completed');
            
        } catch (error) {
            console.error('Cleanup error:', error);
        }
    }
    
    /**
     * Add event listener with automatic cleanup tracking
     */
    addEventListener(element, event, handler, options = {}) {
        const key = `${element.tagName || 'window'}_${event}_${Date.now()}`;
        
        element.addEventListener(event, handler, options);
        
        this.state.eventListeners.set(key, {
            element,
            event,
            handler,
            options
        });
        
        return key;
    }
    
    /**
     * Remove tracked event listener
     */
    removeEventListener(key) {
        const listener = this.state.eventListeners.get(key);
        if (listener) {
            listener.element.removeEventListener(listener.event, listener.handler, listener.options);
            this.state.eventListeners.delete(key);
        }
    }
    
    /**
     * Set timer with automatic cleanup tracking
     */
    setTimeout(callback, delay, key = null) {
        const timerKey = key || `timer_${Date.now()}`;
        
        const timer = setTimeout(() => {
            callback();
            this.state.timers.delete(timerKey);
        }, delay);
        
        this.state.timers.set(timerKey, timer);
        return timerKey;
    }
    
    /**
     * Clear tracked timer
     */
    clearTimeout(key) {
        const timer = this.state.timers.get(key);
        if (timer) {
            clearTimeout(timer);
            this.state.timers.delete(key);
        }
    }
    
    /**
     * Show notification to user
     */
    showNotification(message, type = 'info', duration = 5000) {
        try {
            // Create notification container if it doesn't exist
            let container = document.getElementById('notification-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'notification-container';
                container.className = 'notification-container';
                container.setAttribute('aria-live', 'polite');
                container.setAttribute('aria-atomic', 'true');
                document.body.appendChild(container);
            }
            
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.setAttribute('role', 'alert');
            
            const icons = {
                success: '✅',
                error: '❌',
                warning: '⚠️',
                info: 'ℹ️'
            };
            
            notification.innerHTML = `
                <div class="notification-content">
                    <span class="notification-icon" aria-hidden="true">${icons[type] || icons.info}</span>
                    <span class="notification-message">${this.escapeHtml(message)}</span>
                    <button class="notification-close" aria-label="Close notification" type="button">
                        <span aria-hidden="true">×</span>
                    </button>
                </div>
            `;
            
            // Add to container
            container.appendChild(notification);
            
            // Auto-remove
            this.setTimeout(() => {
                if (notification.parentNode) {
                    notification.classList.add('notification-fade-out');
                    this.setTimeout(() => {
                        notification.remove();
                    }, 300);
                }
            }, duration);
            
            // Manual close
            const closeBtn = notification.querySelector('.notification-close');
            closeBtn.addEventListener('click', () => {
                notification.classList.add('notification-fade-out');
                this.setTimeout(() => {
                    notification.remove();
                }, 300);
            });
            
            // Animate in
            requestAnimationFrame(() => {
                notification.classList.add('notification-show');
            });
            
        } catch (error) {
            // Fallback to console if notification fails
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    /**
     * Announce message to screen readers
     */
    announceToScreenReader(message, priority = 'polite') {
        try {
            let liveRegion = document.getElementById('aria-live-region');
            if (!liveRegion) {
                liveRegion = document.createElement('div');
                liveRegion.id = 'aria-live-region';
                liveRegion.setAttribute('aria-live', priority);
                liveRegion.setAttribute('aria-atomic', 'true');
                liveRegion.className = 'visually-hidden';
                document.body.appendChild(liveRegion);
            }
            
            liveRegion.textContent = message;
            
            // Clear after announcement
            this.setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
            
        } catch (error) {
            this.handleError(error, 'Screen reader announcement failed');
        }
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Debounce function calls
     */
    debounce(func, wait, key = null) {
        const debounceKey = key || `debounce_${Date.now()}`;
        
        return (...args) => {
            this.clearTimeout(debounceKey);
            this.setTimeout(() => func.apply(this, args), wait, debounceKey);
        };
    }
    
    /**
     * Throttle function calls
     */
    throttle(func, limit) {
        let inThrottle;
        return (...args) => {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                this.setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    /**
     * Logging utility
     */
    log(level, message, data = null) {
        if (!this.config.debug && level === 'debug') return;
        
        const timestamp = new Date().toISOString();
        const logMessage = `[${timestamp}] ${message}`;
        
        switch (level) {
            case 'error':
                console.error(logMessage, data);
                break;
            case 'warn':
                console.warn(logMessage, data);
                break;
            case 'info':
                console.info(logMessage, data);
                break;
            case 'debug':
                console.debug(logMessage, data);
                break;
            default:
                console.log(logMessage, data);
        }
    }
    
    /**
     * Get module instance
     */
    getModule(name) {
        return this.modules[name];
    }
    
    /**
     * Check if feature is enabled
     */
    isFeatureEnabled(feature) {
        return this.config.features[feature] === true;
    }
}

/**
 * UI Module - Handles user interface interactions
 */
class UIModule {
    constructor(app) {
        this.app = app;
        this.init();
    }
    
    init() {
        if (this.app.isFeatureEnabled('tooltips')) {
            this.initializeTooltips();
        }
        
        if (this.app.isFeatureEnabled('mobileNav')) {
            this.initializeMobileNavigation();
        }
        
        if (this.app.isFeatureEnabled('lazyLoading')) {
            this.initializeLazyLoading();
        }
        
        if (this.app.isFeatureEnabled('accessibility')) {
            this.initializeAccessibility();
        }
        
        this.initializeInteractions();
    }
    
    initializeTooltips() {
        try {
            const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
            
            if (tooltipTriggerList.length === 0) return;
            
            tooltipTriggerList.forEach(tooltipTriggerEl => {
                if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                    new bootstrap.Tooltip(tooltipTriggerEl, {
                        boundary: 'viewport',
                        fallbackPlacements: ['top', 'right', 'bottom', 'left']
                    });
                }
            });
            
            this.app.log('info', `✅ Initialized ${tooltipTriggerList.length} tooltips`);
            
        } catch (error) {
            this.app.handleError(error, 'Tooltip initialization failed');
        }
    }
    
    initializeMobileNavigation() {
        const navToggle = document.querySelector('.navbar-toggle, .navbar-toggler');
        const navMenu = document.querySelector('.navbar-nav, .navbar-collapse');
        
        if (!navToggle || !navMenu) return;
        
        // Toggle navigation
        this.app.addEventListener(navToggle, 'click', (e) => {
            e.preventDefault();
            this.toggleMobileNav();
        });
        
        // Close navigation when clicking outside
        this.app.addEventListener(document, 'click', (e) => {
            if (this.app.state.mobileNavOpen && 
                !navToggle.contains(e.target) && 
                !navMenu.contains(e.target)) {
                this.closeMobileNav();
            }
        });
        
        // Handle escape key
        this.app.addEventListener(document, 'keydown', (e) => {
            if (e.key === 'Escape' && this.app.state.mobileNavOpen) {
                this.closeMobileNav();
                navToggle.focus();
            }
        });
        
        // Close menu when clicking on nav links (mobile)
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            this.app.addEventListener(link, 'click', () => {
                if (window.innerWidth <= 768) {
                    this.closeMobileNav();
                }
            });
        });
        
        this.app.log('info', '✅ Mobile navigation initialized');
    }
    
    toggleMobileNav() {
        if (this.app.state.mobileNavOpen) {
            this.closeMobileNav();
        } else {
            this.openMobileNav();
        }
    }
    
    openMobileNav() {
        const navToggle = document.querySelector('.navbar-toggle, .navbar-toggler');
        const navMenu = document.querySelector('.navbar-nav, .navbar-collapse');
        
        if (!navToggle || !navMenu) return;
        
        navToggle.classList.add('active');
        navToggle.setAttribute('aria-expanded', 'true');
        navMenu.classList.add('show');
        
        this.app.state.mobileNavOpen = true;
        
        // Focus first menu item
        const firstMenuItem = navMenu.querySelector('.nav-link');
        if (firstMenuItem) {
            firstMenuItem.focus();
        }
    }
    
    closeMobileNav() {
        const navToggle = document.querySelector('.navbar-toggle, .navbar-toggler');
        const navMenu = document.querySelector('.navbar-nav, .navbar-collapse');
        
        if (!navToggle || !navMenu) return;
        
        navToggle.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
        navMenu.classList.remove('show');
        
        this.app.state.mobileNavOpen = false;
    }
    
    initializeLazyLoading() {
        if (!('IntersectionObserver' in window)) return;
        
        const lazyImages = document.querySelectorAll('img[data-src]');
        if (lazyImages.length === 0) return;
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    img.classList.add('lazy-loaded');
                    observer.unobserve(img);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
        this.app.state.observers.add(imageObserver);
        
        this.app.log('info', `✅ Lazy loading initialized for ${lazyImages.length} images`);
    }
    
    initializeAccessibility() {
        // Skip link functionality
        const skipLink = document.querySelector('.skip-link');
        if (skipLink) {
            this.app.addEventListener(skipLink, 'click', (e) => {
                e.preventDefault();
                const target = document.querySelector(skipLink.getAttribute('href'));
                if (target) {
                    target.focus();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }
        
        // Focus management for modals
        document.querySelectorAll('.modal').forEach(modal => {
            this.app.addEventListener(modal, 'shown.bs.modal', () => {
                const focusableElements = modal.querySelectorAll(
                    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                );
                if (focusableElements.length > 0) {
                    focusableElements[0].focus();
                }
            });
        });
        
        this.app.log('info', '✅ Accessibility features initialized');
    }
    
    initializeInteractions() {
        // Enhanced hover effects for cards
        document.querySelectorAll('.cyber-card, .ranking-item, .stat-card, .problem-card').forEach(card => {
            this.app.addEventListener(card, 'mouseenter', (e) => {
                if (!this.app.state.isAnimating) {
                    e.target.style.transform = 'translateY(-4px)';
                    e.target.style.transition = 'all 0.3s ease';
                }
            });
            
            this.app.addEventListener(card, 'mouseleave', (e) => {
                e.target.style.transform = 'translateY(0)';
            });
        });
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            this.app.addEventListener(link, 'click', (e) => {
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
            this.app.addEventListener(textarea, 'input', (e) => {
                const element = e.target;
                element.style.height = 'auto';
                element.style.height = element.scrollHeight + 'px';
            });
        });
    }
    
    destroy() {
        // Cleanup is handled by the main app
        this.app.log('info', '✅ UI module destroyed');
    }
}/**
 * A
JAX Module - Handles all HTTP requests with comprehensive error handling
 */
class AjaxModule {
    constructor(app) {
        this.app = app;
        this.requestCounter = 0;
        this.init();
    }
    
    init() {
        this.setupNetworkMonitoring();
        this.app.log('info', '✅ AJAX module initialized');
    }
    
    setupNetworkMonitoring() {
        this.app.addEventListener(window, 'online', () => {
            this.app.showNotification('Connection restored', 'success');
        });
        
        this.app.addEventListener(window, 'offline', () => {
            this.app.showNotification('Connection lost. Requests will be retried when connection is restored.', 'warning');
        });
    }
    
    async request(url, options = {}) {
        const requestId = ++this.requestCounter;
        const fullUrl = this.buildURL(url);
        
        const requestOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                ...options.headers
            },
            timeout: this.app.config.ajax.timeout,
            ...options
        };
        
        // Add CSRF token for state-changing requests
        if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(requestOptions.method.toUpperCase())) {
            this.addCSRFToken(requestOptions);
        }
        
        // Show loading state
        if (options.loadingElement) {
            this.showLoadingState(options.loadingElement);
        }
        
        // Track active request
        const controller = new AbortController();
        requestOptions.signal = controller.signal;
        this.app.state.activeRequests.set(requestId, { controller, url: fullUrl, options: requestOptions });
        
        try {
            const response = await this.executeRequest(fullUrl, requestOptions, requestId);
            return response;
        } catch (error) {
            this.handleRequestError(error, fullUrl);
            throw error;
        } finally {
            // Cleanup
            this.app.state.activeRequests.delete(requestId);
            if (options.loadingElement) {
                this.hideLoadingState(options.loadingElement);
            }
        }
    }
    
    async executeRequest(url, options, requestId, attempt = 1) {
        try {
            // Check network status
            if (!navigator.onLine) {
                throw new Error('No internet connection');
            }
            
            // Create timeout promise
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('Request timeout')), this.app.config.ajax.timeout);
            });
            
            // Execute request with timeout
            const response = await Promise.race([
                fetch(url, options),
                timeoutPromise
            ]);
            
            // Handle HTTP errors
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            // Parse response
            const data = await this.parseResponse(response);
            
            // Handle application-level errors
            if (data && data.status === 'error') {
                throw new Error(data.error?.message || 'Application error');
            }
            
            return {
                data,
                response,
                status: response.status,
                headers: response.headers
            };
            
        } catch (error) {
            this.app.log('error', `Request failed (attempt ${attempt}/${this.app.config.ajax.retryAttempts}):`, error);
            
            // Determine if we should retry
            if (this.shouldRetry(error, attempt)) {
                await this.delay(this.app.config.ajax.retryDelay * attempt);
                return this.executeRequest(url, options, requestId, attempt + 1);
            }
            
            throw error;
        }
    }
    
    shouldRetry(error, attempt) {
        if (attempt >= this.app.config.ajax.retryAttempts) return false;
        
        const retryableErrors = [
            'NetworkError',
            'TimeoutError',
            'Request timeout',
            'No internet connection'
        ];
        
        return retryableErrors.some(errorType => 
            error.message.includes(errorType) || error.name === errorType
        );
    }
    
    async parseResponse(response) {
        const contentType = response.headers.get('content-type');
        
        try {
            if (contentType?.includes('application/json')) {
                return await response.json();
            } else if (contentType?.includes('text/')) {
                return await response.text();
            } else {
                return await response.blob();
            }
        } catch (error) {
            this.app.log('warn', 'Failed to parse response:', error);
            return null;
        }
    }
    
    handleRequestError(error, url) {
        let message = 'An unexpected error occurred';
        let type = 'error';
        
        if (error.message.includes('No internet connection')) {
            message = 'Network connection error. Please check your internet connection.';
        } else if (error.message.includes('timeout')) {
            message = 'Request timed out. Please try again.';
        } else if (error.message.includes('HTTP 400')) {
            message = 'Invalid request. Please check your input.';
        } else if (error.message.includes('HTTP 401')) {
            message = 'Authentication required. Please log in.';
        } else if (error.message.includes('HTTP 403')) {
            message = 'Access denied. You do not have permission to perform this action.';
        } else if (error.message.includes('HTTP 404')) {
            message = 'The requested resource was not found.';
        } else if (error.message.includes('HTTP 429')) {
            message = 'Too many requests. Please wait before trying again.';
        } else if (error.message.includes('HTTP 5')) {
            message = 'Server error. Please try again later.';
        }
        
        this.app.showNotification(message, type);
        
        // Log detailed error information
        this.app.log('error', 'AJAX Error Details:', {
            url,
            error: error.message,
            stack: error.stack
        });
    }
    
    buildURL(url) {
        if (url.startsWith('http://') || url.startsWith('https://')) {
            return url;
        }
        
        const baseURL = window.location.origin;
        return `${baseURL}${url.startsWith('/') ? '' : '/'}${url}`;
    }
    
    addCSRFToken(options) {
        const token = this.getCSRFToken();
        if (!token) return;
        
        if (options.body instanceof FormData) {
            options.body.append('csrf_token', token);
        } else if (options.headers['Content-Type']?.includes('application/json')) {
            const body = options.body ? JSON.parse(options.body) : {};
            body.csrf_token = token;
            options.body = JSON.stringify(body);
        } else {
            options.headers['X-CSRFToken'] = token;
        }
    }
    
    getCSRFToken() {
        // Try multiple sources for CSRF token
        const metaToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        if (metaToken) return metaToken;
        
        const inputToken = document.querySelector('input[name="csrf_token"]')?.value;
        if (inputToken) return inputToken;
        
        const cookieMatch = document.cookie.match(/csrf_token=([^;]+)/);
        if (cookieMatch) return cookieMatch[1];
        
        return null;
    }
    
    showLoadingState(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;
        
        element.classList.add('loading');
        element.setAttribute('aria-busy', 'true');
        
        // Store original content
        if (!element.dataset.originalContent) {
            element.dataset.originalContent = element.innerHTML;
        }
        
        // Show loading indicator
        if (element.tagName === 'BUTTON') {
            element.disabled = true;
            element.innerHTML = `
                <span class="loading-spinner" aria-hidden="true"></span>
                Loading...
            `;
        }
    }
    
    hideLoadingState(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (!element) return;
        
        element.classList.remove('loading');
        element.removeAttribute('aria-busy');
        
        if (element.tagName === 'BUTTON') {
            element.disabled = false;
            element.innerHTML = element.dataset.originalContent || 'Submit';
        }
        
        delete element.dataset.originalContent;
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Convenience methods
    async get(url, options = {}) {
        return this.request(url, { ...options, method: 'GET' });
    }
    
    async post(url, data, options = {}) {
        const requestOptions = {
            ...options,
            method: 'POST'
        };
        
        if (data instanceof FormData) {
            requestOptions.body = data;
            delete requestOptions.headers?.['Content-Type'];
        } else if (typeof data === 'object') {
            requestOptions.body = JSON.stringify(data);
            requestOptions.headers = {
                'Content-Type': 'application/json',
                ...requestOptions.headers
            };
        } else {
            requestOptions.body = data;
        }
        
        return this.request(url, requestOptions);
    }
    
    async submitForm(form, options = {}) {
        if (typeof form === 'string') {
            form = document.querySelector(form);
        }
        
        if (!form) {
            throw new Error('Form not found');
        }
        
        const formData = new FormData(form);
        const url = form.action || window.location.pathname;
        const method = form.method || 'POST';
        
        return this.request(url, {
            method: method.toUpperCase(),
            body: formData,
            loadingElement: form.querySelector('button[type="submit"]'),
            ...options
        });
    }
    
    destroy() {
        this.app.log('info', '✅ AJAX module destroyed');
    }
}

/**
 * Validator Module - Handles form validation with real-time feedback
 */
class ValidatorModule {
    constructor(app) {
        this.app = app;
        this.validationRules = {
            code: {
                maxLength: app.config.editor.maxCodeLength,
                minLength: 1,
                required: true
            },
            language: {
                required: true,
                allowedValues: ['python', 'javascript', 'java', 'cpp']
            },
            problemId: {
                required: true,
                type: 'number',
                min: 1
            },
            userName: {
                maxLength: 50,
                minLength: 2,
                pattern: /^[a-zA-Z0-9\s\-_.]+$/,
                required: true
            }
        };
        
        this.securityPatterns = {
            python: [
                /import\s+(os|sys|subprocess|socket|urllib|requests|tempfile|shutil|pickle|marshal)/gi,
                /from\s+(os|sys|subprocess|socket|urllib|requests|tempfile|shutil|pickle|marshal)/gi,
                /(open|file|input|eval|exec|compile)\s*\(/gi
            ],
            javascript: [
                /require\s*\(['"][^'"]*fs['"]\)/gi,
                /require\s*\(['"][^'"]*child_process['"]\)/gi,
                /process\./gi,
                /(eval|Function|setTimeout|setInterval)\s*\(/gi,
                /__dirname|__filename/gi
            ],
            java: [
                /import\s+java\.io\./gi,
                /import\s+java\.nio\./gi,
                /Runtime\.getRuntime/gi,
                /ProcessBuilder/gi,
                /System\.(exit|gc)/gi
            ],
            cpp: [
                /#include\s*<(fstream|iostream|cstdlib|system)>/gi,
                /system\s*\(/gi,
                /popen\s*\(/gi,
                /exec\w*\s*\(/gi
            ]
        };
        
        this.init();
    }
    
    init() {
        this.setupFormValidation();
        this.setupRealTimeValidation();
        this.app.log('info', '✅ Validator module initialized');
    }
    
    setupFormValidation() {
        // Main submission form
        const submitForm = document.querySelector('#submission-form, .submission-form');
        if (submitForm) {
            this.app.addEventListener(submitForm, 'submit', (e) => {
                if (!this.validateSubmissionForm(submitForm)) {
                    e.preventDefault();
                }
            });
        }
        
        // User name form
        const nameForm = document.querySelector('#name-form, .name-form');
        if (nameForm) {
            this.app.addEventListener(nameForm, 'submit', (e) => {
                if (!this.validateNameForm(nameForm)) {
                    e.preventDefault();
                }
            });
        }
    }
    
    setupRealTimeValidation() {
        // Code editor validation
        const codeEditor = document.querySelector('#code-editor, .code-editor, textarea[name="code"]');
        if (codeEditor) {
            const debouncedValidation = this.app.debounce((editor) => {
                this.validateCodeInput(editor);
            }, this.app.config.validation.debounceDelay, 'code-validation');
            
            this.app.addEventListener(codeEditor, 'input', debouncedValidation);
            this.app.addEventListener(codeEditor, 'blur', () => {
                this.validateCodeInput(codeEditor);
            });
        }
        
        // Language selection validation
        const languageSelect = document.querySelector('select[name="language"], #language-select');
        if (languageSelect) {
            this.app.addEventListener(languageSelect, 'change', (e) => {
                this.validateLanguageSelection(languageSelect);
            });
        }
        
        // User name validation
        const nameInput = document.querySelector('input[name="user_name"], #user-name');
        if (nameInput) {
            const debouncedNameValidation = this.app.debounce((input) => {
                this.validateUserNameInput(input);
            }, this.app.config.validation.debounceDelay, 'name-validation');
            
            this.app.addEventListener(nameInput, 'input', debouncedNameValidation);
        }
    }
    
    validateSubmissionForm(form) {
        const data = new FormData(form);
        const code = data.get('code') || '';
        const language = data.get('language') || '';
        const problemId = data.get('problem_id') || '';
        
        let isValid = true;
        this.clearErrors(form);
        
        // Validate problem ID
        if (!this.validateProblemId(problemId)) {
            this.showError(form, 'problem_id', 'Invalid problem ID');
            isValid = false;
        }
        
        // Validate language
        if (!this.validateLanguage(language)) {
            this.showError(form, 'language', 'Please select a valid programming language');
            isValid = false;
        }
        
        // Validate code
        const codeValidation = this.validateCode(code, language);
        if (!codeValidation.valid) {
            this.showError(form, 'code', codeValidation.message);
            isValid = false;
        }
        
        // Security check
        const securityCheck = this.performSecurityCheck(code, language);
        if (!securityCheck.safe) {
            this.showError(form, 'code', securityCheck.message);
            isValid = false;
        }
        
        return isValid;
    }
    
    validateNameForm(form) {
        const data = new FormData(form);
        const name = data.get('user_name') || data.get('name') || '';
        
        let isValid = true;
        this.clearErrors(form);
        
        const nameValidation = this.validateUserName(name);
        if (!nameValidation.valid) {
            this.showError(form, 'user_name', nameValidation.message);
            isValid = false;
        }
        
        return isValid;
    }
    
    validateCode(code, language) {
        if (!code || code.trim().length === 0) {
            return { valid: false, message: 'Please enter your code before submitting' };
        }
        
        if (code.length > this.validationRules.code.maxLength) {
            return { 
                valid: false, 
                message: `Code exceeds maximum length of ${this.validationRules.code.maxLength.toLocaleString()} characters (current: ${code.length.toLocaleString()})` 
            };
        }
        
        return { valid: true };
    }
    
    validateLanguage(language) {
        return this.validationRules.language.allowedValues.includes(language);
    }
    
    validateProblemId(problemId) {
        const id = parseInt(problemId);
        return !isNaN(id) && id > 0;
    }
    
    validateUserName(name) {
        if (!name || name.trim().length === 0) {
            return { valid: false, message: 'Name is required' };
        }
        
        if (name.length < this.validationRules.userName.minLength) {
            return { valid: false, message: `Name must be at least ${this.validationRules.userName.minLength} characters long` };
        }
        
        if (name.length > this.validationRules.userName.maxLength) {
            return { valid: false, message: `Name cannot exceed ${this.validationRules.userName.maxLength} characters` };
        }
        
        if (!this.validationRules.userName.pattern.test(name)) {
            return { valid: false, message: 'Name can only contain letters, numbers, spaces, hyphens, underscores, and periods' };
        }
        
        return { valid: true };
    }
    
    performSecurityCheck(content, language) {
        const patterns = this.securityPatterns[language] || [];
        
        for (const pattern of patterns) {
            if (pattern.test(content)) {
                return {
                    safe: false,
                    message: 'Code contains restricted operations that are not allowed for security reasons'
                };
            }
        }
        
        return { safe: true };
    }
    
    validateCodeInput(element) {
        const code = element.value;
        const language = this.getCurrentLanguage();
        
        // Update character count
        this.updateCharacterCount(element, code);
        
        // Validate code
        const validation = this.validateCode(code, language);
        if (!validation.valid) {
            this.showFieldError(element, validation.message);
        } else {
            this.clearFieldError(element);
        }
        
        // Security check
        const securityCheck = this.performSecurityCheck(code, language);
        if (!securityCheck.safe) {
            this.showFieldWarning(element, securityCheck.message);
        }
    }
    
    validateLanguageSelection(element) {
        const language = element.value;
        
        if (!this.validateLanguage(language)) {
            this.showFieldError(element, 'Please select a valid programming language');
        } else {
            this.clearFieldError(element);
        }
    }
    
    validateUserNameInput(element) {
        const name = element.value;
        const validation = this.validateUserName(name);
        
        if (!validation.valid) {
            this.showFieldError(element, validation.message);
        } else {
            this.clearFieldError(element);
        }
    }
    
    getCurrentLanguage() {
        const languageSelect = document.querySelector('select[name="language"], #language-select');
        return languageSelect ? languageSelect.value : 'python';
    }
    
    updateCharacterCount(element, text) {
        const counter = element.parentElement.querySelector('.character-count');
        if (counter) {
            const maxLength = this.validationRules.code.maxLength;
            const currentLength = text.length;
            const percentage = (currentLength / maxLength) * 100;
            
            counter.textContent = `${currentLength.toLocaleString()} / ${maxLength.toLocaleString()} characters`;
            
            counter.className = 'character-count';
            if (percentage > 90) {
                counter.classList.add('text-danger');
            } else if (percentage > 75) {
                counter.classList.add('text-warning');
            } else {
                counter.classList.add('text-muted');
            }
        }
    }
    
    showError(form, fieldName, message) {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            this.showFieldError(field, message);
        }
    }
    
    showFieldError(field, message) {
        this.clearFieldError(field);
        
        field.classList.add('is-invalid');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        field.parentElement.appendChild(errorDiv);
    }
    
    showFieldWarning(field, message) {
        const existingWarning = field.parentElement.querySelector('.text-warning');
        if (existingWarning) return;
        
        const warningDiv = document.createElement('div');
        warningDiv.className = 'text-warning small mt-1';
        warningDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${this.app.escapeHtml(message)}`;
        
        field.parentElement.appendChild(warningDiv);
    }
    
    clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorFeedback = field.parentElement.querySelector('.invalid-feedback');
        if (errorFeedback) {
            errorFeedback.remove();
        }
        
        const warning = field.parentElement.querySelector('.text-warning');
        if (warning) {
            warning.remove();
        }
    }
    
    clearErrors(form) {
        const invalidFields = form.querySelectorAll('.is-invalid');
        invalidFields.forEach(field => {
            this.clearFieldError(field);
        });
    }
    
    destroy() {
        this.app.log('info', '✅ Validator module destroyed');
    }
}/**

 * Editor Module - Enhanced code editor with syntax highlighting and auto-completion
 */
class EditorModule {
    constructor(app) {
        this.app = app;
        this.state = {   };
}le
 odubmissionM        SuorModule,
    Edit
    e,atorModul   Validule,
      AjaxMod     Module,
          UI,
deXamApp      Co
   {xports =   module.erts) {
 pole.exed' && moduine !== 'undeftypeof modulsting
if (for tedules Export mo
// XamApp();
ode C = newppdeXamA.Coon
windowlicatize the app Initiali }
}

//  oyed');
 trodule desSubmission m('info', '✅ .log this.app);
       story(SubmissionHi  this.saveate
      ve final st   // Say() {
     
    destro    }
      }

      ion');ssssful submicceve su sa 'Failed torror,eError(eapp.handl       this.or) {
     } catch (err;
          }))         ring()
 ISOSte().toamp: new Dat    timest           result,
 esult: data. r           
    ge,anguaata.l: dnguage     la        
   e,a.cod: datcode            y({
    ON.stringifJSey, tem(kStorage.setI local       
     try {}`;
       nown'm_id || 'unk{data.probles_$m_succesdexa `cost key =   cona) {
     ission(datessfulSubm    saveSucc }
    
  }
   ');
      ion historyssave submi sFailed to 'rror(error,ndleEis.app.ha th         r) {
  rro} catch (e);
        ionHistory)submisss.state.(thi.stringify', JSONoryon_histam_submissi('codexe.setItemlStoragoca       l{
          try () {
   HistoryveSubmission    
    sa
    }
   }   );
  ory'on histsioad submiso l 'Failed trror,r(eropp.handleEr    this.a  r) {
      atch (erro} c}
                  aved);
  arse(sON.p= JSory ionHisttate.submiss this.s            aved) {
    (s       if   
  story');ssion_hi_submicodexamgetItem('calStorage.d = loconst save   {
         try   
      () {orynHistubmissioloadS
      }
    ory();
  ionHistubmissthis.saveS      
     
           }  
e(0, 50);tory.slicissionHisubmtate.shis.sHistory = tionsubmisss.state.thi    
        h > 50) {ngtory.leissionHiste.submtat if (this.s     ze
  siory ist  // Limit h
          n);
    (submissioiftistory.unshionHubmiss.state.sthis           
     };
      ring()
  .toISOStte(): new Dastamp time          
 age,esslt.data.message: resu           mlt,
 .resutalt.daesult: resu        r'),
    id'problem_get( formData.roblemId:           pnguage'),
 a.get('laage: formDatlangu         ),
   code'mData.get('de: for co    (),
       now id: Date.           n = {
bmissio const su
       t) {, resul(formDataHistoryubmission    addToS
    
 }
   + sizes[i]; ' ' ed(2)) +k, i)).toFix/ Math.pow(es (bytrseFloat( return pa
              ;
 g(k))Math.loog(bytes) / r(Math.l Math.flooi =const        B'];
 'MB', 'GB', tes', 'K = ['Byconst sizes;
        st k = 1024    con 
      
     ';'0 Bytes return  0)tes === (by       if{
 s) Bytes(byte    format   
}
    }
         ;
}, 3000)       }`);
     ase()owerClt.toL-${data.resusultve(`reremoassList.mitButton.cl         sub     
  Text;riginalent = on.textContButto submit           => {
     t(()setTimeouis.app.          th       
  }`);
     oLowerCase()t.tul${data.resadd(`result-n.classList.Buttosubmit       t}!`;
     a.resul`${datnt = onteton.textCubmitBut s           tContent;
exButton.titlText = submnaonst origi c          utton) {
 (submitB     if ');
   "]="submitypeton[tlector('butt.querySeon = documentButt submi    const   orarily
 emptton text tbmit bupdate su // U    
     0);
        }, 500tle;
      alTirigintitle = o document.       => {
     t(().setTimeouhis.app    t
    r 5 seconds title afte/ Reset     /      
   tle}`;
  {originalTisult} - $.re${data= `ment.title   docule;
      itcument.tlTitle = doginarinst oco        porarily
emtitle tate page // Upd{
        ultUI(data) pdateRes
    u   }
      }
    ing);
   ittisSubmmitting', subst.toggle('form.classLi         form) {
   if (  
          }
      
                }
          `;e
        mit Cod Sub                pan>
   /s>🚀<"trueia-hidden="on" arit-icsubm" class=an        <sp       `
     innerHTML = itButton.      subm         else {
         }
          `;      ...
     ting      Submit            ></span>
  "true"en=dd" aria-hierg-spinnss="loadinpan cla          <s         HTML = `
 tton.inner    submitBu            ng) {
(isSubmitti    if    ng;
     Submittiled = isdisabutton.     submitB       {
 itButton)  if (subm    
          -form');
ubmission, #s-formbmissionector('.sunt.querySelorm = docume fnst        cobmit"]');
type="suor('button[rySelectument.que = docitButtonubmnst s       co) {
 ittingI(isSubmissionU  updateSubm    
}
    }
          ');
iting dataoad rate limFailed to lor(error, 'andleErrs.app.h  thi        
  error) {catch (       } }
            ime || 0;
 ta.lastTe = danTimissioate.lastSubmis.st        th        0;
 ta.count ||nt = daounCubmissiotate.sis.s          th
      rse(saved); JSON.padata =   const            ed) {
  savif (         mit');
   exam_rate_litem('codStorage.getIaved = localnst s       coy {
          trorage
   Stcalta from loimiting daate l // Load r     g() {
  ateLimitin   setupR   
 
    }
    });
     ta'g dae limitinatave riled to s 'Far(error,.handleErrois.app    th      
  (error) {ch cat     } 
          }));   Time
  Submissionasts.state.lTime: thi   last           ount,
  .submissionCateis.st th    count:           ngify({
 , JSON.strilimit'rate_m('codexam_.setIteagelocalStor     {
           try data
     limiting e rateSav/     /    
    ow();
    e = Date.nissionTimate.lastSubmhis.st  t    +;
  onCount+missis.state.sub        thiit() {
imateRateL 
    upd }
   xRate;
   masubmission..config.this.appCount < ionubmiss.state.shiseturn t      r       
         }
  = 0;
 missionCount.state.sub        thisod) {
    downPeriolsion.cosubmisonfig.app.c> this.bmission inceLastSuimeSif (t  sed
       pasperiod haswn ooldonter if ceset cou/ R  / 
            ime;
 sionTmiste.lastSub this.stasion = now -astSubmiseLnst timeSinc  co
      w();w = Date.noconst no
        teLimit() {    checkRa
    

    }       `;   </div>
      >
         </div         ''}
    ` :            v>
             </di          
        _id}</span>bmission{data.su>#$e"tail-valudelass="    <span c                        n>
/spassion ID<">Submitail-labelass="de <span cl                      ">
     ss="detailiv cla   <d                      `
 ?mission_ida.sub{dat      $                  </div>
                }</span>
aleString()Date().toLoce">${new valudetail-ss="  <span cla                pan>
      /stted<abel">Submiil-llass="deta<span c              
          ail">ass="det<div cl              div>
               </  
         wn'}</span>noage || 'Unkta.languue">${daval="detail-span class    <                   pan>
 Language</sail-label"> class="det <span                    il">
   lass="deta      <div c           ">
   iddetails-griv class="          <d
      s">tailssion-debmisuass="div cl  <       
   return `
        ls(data) {nDetaiubmissioenderS r  
   
    }
     `;  >
         </div        </div>
            '}
       ` : '                </div>
               
        span>ed)}</memory_usta.es(datBytis.forma">${thvaluec-ss="metrian cla  <sp                    n>
      pay Used</s">Memorbel"metric-laass=cl    <span                 ">
        c="metriss    <div cla                    y_used ? `
emordata.m     ${                ''}
        ` :             </div>
                  
     s</span>}mution_time.exece">${dataric-valuss="met<span cla                      n>
      pa</s Timexecutionlabel">E"metric-n class=<spa                        c">
    ss="metrilav c    <di          
          n_time ? `executio   ${data.           
      rid">metrics-glass=" <div c              >
 formance</h4Per      <h4>      
    etrics">ance-m"perform <div class=        
    `     return
               }
  
  turn '';     re   d) {
    _usedata.memoryn_time && !.executio   if (!data   {
  cs(data) MetrierformanceenderP
    
    r   }    `;
 /div>
     <          iv>
  </d          )}
     n('' `).joi                  >
 /div    <             
       ` : ''}                        iv>
       </d                        iv>
     al)}</dt.actu(tespeHtmlsca{this.app.e>Got: $est-actual"="tss<div cla                             
       iv>ted)}</dtest.expecpeHtml(pp.escathis.ated: ${ted">Expec"test-expecs=v clas        <di                            ">
est-detailss="tlas c      <div                      l ? `
    t.actuacted && tesest.expeassed && t  ${!test.p                          </div>
                    >
             </span                          '}
 '❌ FAIL PASS' : .passed ? '✅${test                                   
 ">tatusst-sten class="  <spa                      n>
         + 1}</spaindexer">Test ${st-numb"tess= cla      <span                   >
       eader"="test-h<div class                  
          ailed'}">assed' : 'fsed ? 'p ${test.pas="test-case class <div                   
     => `est, index)ts.map((ttestResul    ${               ases">
 t-cclass="tesiv       <d         
 assed)</h4>talCount} p{tot}/$edCoun{passCases ($<h4>Test         ">
        lts="test-resu <div class            `
urn    ret  
         length;
 tResults.lCount = tes tota     const;
   d).length.passest => testts.filter(teResul= testssedCount t pacons           
    }
   
      ;  return ''       == 0) {
   ength =stResults.l| tetResults |    if (!tes) {
    esultslts(testRsunderTestRe    re

    
    } }, 500);     );
  te-in'sults-anima('ret.removeissLanel.clasltsP      resu{
      (() => etTimeout.app.s        this-in');
-animatedd('resultsssList.a.clatsPanelesul
        r animation    // Add
    ;
        rest' })neaock: ', blth'r: 'smoow({ behaviocrollIntoVietsPanel.s      resulesults
  l to rrol// Sc  
         `;
         
    ta)}Details(darSubmissionendethis.r  ${         ta)}
 ics(daMetrormanceerPerf${this.rend         )}
   sultsst_re.telts(dataesuTestRderthis.ren    ${
                    iv>
   </d         }</p>
e)data.messageHtml(s.app.escap">${thigeesult-messaclass="rp      <  
              </h3>       ult}
     ${data.res Result:bmissionSu                   /span>
 esultIcon}<">${rruehidden="t" aria-esult-iconan class="r     <sp            h3>
           <       lass}">
 {resultCder result-$ult-heas="res <div clas     
      L = `.innerHTMsultsPanel
        re    '❓';
    || sultClass]       }[re': '⚠️'
    'error
          '❌','fail':        
     ',: '✅pass'       '      = {
onsultIc   const re  );
   ase(oLowerCa.result.tat= dtClass nst resul    co
    
        
        }         }el);
   esultsPanld(rpendChi).apr, main'ine.contaelector('nt.querySme    docu            } else {
            ling);
ibainer.nextSitorContsPanel, edore(resulte.insertBefarentNodntainer.pCoorit       ed     {
     ontainer)torC (edi   if       iner');
  ditor-conta .code-ener,-contair('.editortoSelecment.querycutainer = doorCon edit  const       
       
        lts');mission Resuabel', 'Subaria-le('ributtAttltsPanel.se     resu  
     on');e', 'regiute('roltAttribel.setsPan    resul';
        resultssubmission-me = 'NaPanel.classultses           r'div');
 eateElement(document.cranel = sultsP       rel) {
     esultsPane      if (!rts');
  esul-rmissionector('.suberySel.qu= documentsultsPanel let re
        elesults pante rpda ureate or/ C       /data) {
 ts(onResulssiSubmisplay    di    

    }
e, 'error');agn(messcatioifishowNotpp.   this.a
          }
     
      n later.';e try agaierror. Pleasver e = 'Ser     messag {
       HTTP 5'))es('clud.message.inse if (error   } el.';
      againittinge subm beforwaitlease  requests. P'Too manyssage =     me        9')) {
P 42('HTTesssage.includ (error.me else if
        }.';ry againase tut. Pleimed oubmission tssage = 'S      me
      ut')) {('timeoesssage.includ.me(errorelse if      }    in.';
 try aga andtionecur conn check yo. Pleaseerror = 'Network  message     {
       ))connection'net interudes('No ncl.ir.message  if (erro       
      ';
 try again.d. Please ion faileubmiss= 'Sage  let mess
         ;
      ')failedsion 'Submisr(error, .handleErro this.app) {
       rorsionError(erandleSubmis h
      }
            }
 
y = false;.isDirtditor.state         e   {
 (editor)     if   );
 ule('editor'.app.getModitor = this    const edclean
    r as to // Mark edi    
   
         }      ata);
 bmission(dssfulSu.saveSucce       this
     = 'PASS') {lt ==.resu if (data    
   ionl submissessfuuccsave s  // Auto-          
 t}`);
   ta.resulResult: ${daccessfully. ubmitted su seader(`CodeeToScreenRannounchis.app.        trs
adeen ree to scre  // Announc 
      );
       taltUI(das.updateResuhi  t    t
   on resulate UI basedUpd  //       
        ta);
s(dasionResultubmisaySdispls. thi
       ltssued re detaillay // Disp        
    
   cess');ucresult}`, 's${data.ult: Res! ulcessfbmission sucication(`Supp.showNotif      this.a
  fication notihow success      // S
          ;
.data resultdata =      const t) {
  suluccess(resionSubmis    handleS    

    }esult;
urn r      ret       
  
 a, result);Dat(formistoryonHSubmissi.addTo this       ry
e in histo   // Stor     
 
       teLimit();Raates.upd      thiing
  ate limit Update r   //
         
         });it"]')
   e="submton[typector('butm.querySelement: forgEl loadin          {
  orm(form,ax.submitF= await ajnst result       co      
  ent);
  or.userAgt', navigat'user_agena.append(    formDat   );
 ing()ISOStrw Date().toime', nession_tend('submi.app   formData    etadata
 sion mdd submis  // A   
     );
      Data(formrmata = new Fo formD  const  
               }
    able');
 availmodule not AJAX Error('  throw new 
          if (!ajax) {        ('ajax');
etModule.gs.appt ajax = thi       cons{
 (form) c submitCodeyn   
    as }
    }
 );
       alsesionUI(fubmis.updateS   this     lse;
    faing = sSubmitt.state.ithis           
 ly {  } final     ror);
 ionError(ereSubmiss.handl      this
      rror) {  } catch (e   esult);
   nSuccess(rioleSubmissthis.hand          orm);
  de(ftCobmit this.su awaiult =res   const           try {
    
      rue);
     ssionUI(tdateSubmi this.up      e;
  trumitting =ate.isSub     this.st  
             }
 ;
         return)) {
      m(formbmissionForSuidatealidator.val& !validator &(v   if or');
     'validat.getModule(r = this.appatoid const vala
       te form datalida      // V       
 }
   ;
            return      ');
 ing 'warn.',gainmitting abefore subt ase waiissions. Pley submToo manon('ficatitihowNothis.app.s     ) {
       eLimit()s.checkRatif (!thik
        g checRate limitin   //  
       }
            
  return;           ning');
lete', 'war compubmission tohe current sait for tase wlen('Ptificatio.app.showNo   this         {
itting) ubmate.isS(this.st if ) {
       on(formsiSubmiseFormnc handl
    asy}
    ;
     })         }
      
    );n(e.targetubmissiohandleFormShis. t         ;
      ault().preventDef   e    
         ')) {rmbmission-foon-form, #suubmissi('.st.matchestarge if (e.           e) => {
'submit', (ent, er(documEventListen.add.appthis      
  nm submissio     // For
    {ners()Liste  setupEvent  
    
   }ized');
 dule initialission moo', '✅ Submapp.log('infs.      thi
       ();
   imiting.setupRateL       thisy();
 onHistorsiSubmis this.load
       ();Listenerss.setupEvent     thi {
     init()   
  ;
    }
 s.init()       thi   
   };
     : []
      rytosionHis submis       
    alse,ubmitting: f     isS       e: 0,
ionTimmiss   lastSub        t: 0,
 bmissionCoun     su
       e = { this.stat    app;
    this.app = ) {
       uctor(apptr
    consdule {SubmissionMolass k
 */
c feedbacndimiting awith rate lssions submiles code ndModule - Haion ss* Submi
}

/**
 ');
    } destroyeddule'✅ Editor mo('info', this.app.log
                     }
 
  );e(this.saveCod            irty) {
sD.is.state if (thi      ying
 rofore dest/ Save be        /roy() {
st
    de  }
    ();
  oSaves.setupAut    thies
     resumave when app-sume auto // Res
       me() {su  
    re
    }
  eturn null;   r   
   1];
       Match[turn urlMatch) re (url     if/);
   /(\d+)lem\rob/pme.match(/\ation.pathnaocndow.lwiMatch = const url 
             ;
  lueut.vanpemIdIroblut) return pInpemIdobl     if (pr
   "]');idroblem_="pt[nameor('inpulectment.querySeocut = dblemIdInpunst pro       coources
  various sD fromroblem It pry to ge/ T   /     Id() {
lemrob getP   
   
 ');
    }sedcuor-foitmove('edsList.relasnt?.carentEleme e.target.p     {
   andleBlur(e)  h 
    }
   ');
  edfocusditor-t.add('essLis?.claarentElement  e.target.p    us(e) {
     handleFoc}
    
 t');
    to subminter ft+Eve, Ctrl+Shil+S to sant, CtrndeUse Tab to ide editor. ', 'Coitlebute('tetAttrir.sito
        edion helpard navigat// Keybo
        
        'true');ne', ria-multilitribute('aor.setAt  edit
      e editor');l', 'Codia-labetribute('arr.setAt       editobox');
 ', 'textte('roletAttribuitor.se
        ed attributesARIA
        //        ;
 ents.editorthis.elem= ditor    const e   
  ty() {ssibilisetupAcce
    
       }');
 r-autosave, 'editoaveInterval  }, autoS;
      AutoSave()setups. thi
           eschedule R     //
                }Code();
     this.save          {
     ate.isDirty)f (this.st   i
          { =>out(().app.setTime    this    
       al;
 oSaveIntervuteditor.aonfig.s.app.c thinterval =SaveIautonst 
        co        ;
 returne'))toSavd('aureEnableapp.isFeatuf (!this.
        ive() {upAutoSa 
    set    }
      }

     );code' saved iled to loadr, 'FaleError(erroandhis.app.h t        
   ch (error) {  } cat       }
           }
             }
                  r);
     s.editomentelethis.eCodeInput(.validatatoralid  v                    or) {
  (validat      if             ;
  tor')dae('validul.getMo this.apptor =alidat v     cons            n
    validatioTrigger   //                        
              stamp;
Data.timevetSaved = saasthis.state.l                      }
             e;
     guagtLanenstate.curr = this.aluect.vguageSeleents.lanelemis.     th                  Select) {
 uagets.langenhis.elem      if (t             thon';
 'pylanguage || eData.savanguage = rrentLe.cus.stat   thi              e;
   cod saveData.or.value =nts.edithis.eleme   t             {
     (confirmed)         if );
       ?'tore ito reslike tyou  Would s problem.r thi fosaved codem('Found confirmed =  confir   const     
        m()) {ta.code.triDa&& saventProblemId urrelemId === coba.prf (saveDat  i         oblem
  same prt's for theload if iOnly /          /    
   );
        tProblemId(geId = this.rentProblem   const cur
         rse(saved);.paONData = JSonst save     c      
            n;
 ed) retur!savf (         iave');
   editor_sem('codexam_.getItageocalStor = led   const sav         try {
        
     rn;
   retu')) d('autoSaveeEnableturFeais.app.is if (!th  e() {
     avedCod 
    loadS }
         }
   ;
  error')ode', 'ave cto sd ('Faileificationp.showNot  this.ap          
ave code');ailed to sr(error, 'FrondleEr.hathis.app            or) {
ch (err    } cats');
    esaved', 'succon('Code sicatiwNotifhois.app.s     th      );
 now(e.= Datd astSavestate.l       this.lse;
     isDirty = fatate.is.s    th
        eData));savringify(ON.stsave', JSxam_editor_'codeage.setItem(   localStor     
    {   try      
        
      };  blemId()
his.getPro: tlemId      prob(),
       Date.nowtamp:mes       ti    ,
 entLanguageate.currs.stguage: thi         lane,
   od   c    {
      a =onst saveDat       ce;
 tor.valu.edimentsthis.ele= de cot    cons
             ;
eturn rutoSave'))eEnabled('aurp.isFeatis.ap!thf (  i      
aveCode() {   
    s }
 
   te');et to templabeen res has deReader('CocreennnounceToSs.app.a thi    fo');
   plate', 'inset to temon('Code retificaapp.showNoti     this.
   );ate(.loadTemplthis          
    urn;
  med) ret!confir   if (
     undone.');annot be ction chis ade? Tet your co to resntu waure yoyou snfirm('Are = cod rmeonst confi        c {
de()Co   reset }
    
    }
           }
       
  rm);sion(foisubmormShandleFon.ait submissi  aw            form) {
      if (   );
     on-form'm, #submissision-foror('.submis.querySelectdocumentform =       const {
      mission)   if (sub');
      ('submissiondules.app.getMoion = thiubmissconst s        itCode() {
  async subm }
    
     }
   ;
     editor)ts..element(thiseInpualidateCoddator.v   vali
         r) {if (validato  ');
      lidatore('vauls.app.getMod= thi validator      consttion
    valida/ Trigger 
        /      e;
 falsy = .isDirts.state    thite;
    ue = templavalditor..elements.e   this'';
     uage] || currentLang.state.lates[this this.tempplate =nst tem       colate() {
 adTemplo
    
        }e}`);
guago ${lan changed tr(`LanguagedeoScreenReapp.announceT  this.a      rs
reen readeounce to sc     // Ann
     ();
      loadTemplate    this.
     language;tLanguage =state.curren  this.
      
           }          }
n;
       retur         ;
       nguagerentLa.state.cur = thisalueageSelect.vngu.lais.elements      th          d) {
!confirme (       if`);
     ue?code. Continset your e will reanguag(`Changing lrmonfied = c confirm    const        ontent) {
f (hasC i          
 
    ength > 0;.trim().lvaluents.editor.is.elemet = thtent hasCon  cons
      
        rn;ge) retulanguauage === ntLange.curre.stat  if (thise) {
      (languagnguagegeLa  
    chan}
  ;
    r)udes(nextCha.incl ';']'}', ',',', ']', r) || [')Cha(next\s/.test| /Char |n !nextretur     ition);
   rAt(posvalue.chator.dir = enextChat    cons    
 sition) { pocket(editor,raseBAutoClould
    sho   
     }
  });
       editor }et:put({ targhis.handleIn           t
       
      t.length;selectedTex + rt + 1stand = ctionEtor.seletart = edionSor.selecti edit           wValue;
nevalue = or.      edit   
      
         ;tring(end).value.subseditor                         osing + 
  ext + clelectedT  e.key + s                          start) + 
substring(0,e.valuor. editnewValue =t       cons   
             ault();
  entDef e.prev          {
  ldAutoClose)  if (shou            

  r, start);toBracket(ediuldAutoClosehothis.s> 0 || h lengtelectedText. sose =AutoClnst should co       art, end);
substring(stor.value.Text = editelectednst s        coauto-close
f we should k i Chec       //       
 urn;
 ret (!closing) 
        ifey];[e.kpairs= t closing  cons        
     };
     "
     "'": "'  
          '"': '"',       
     : '}',      '{'   ': ']',
          '[      ')',
       '(':     s = {
pair    const       
    nEnd;
  r.selectioditond = e   const e
     nStart;ctioor.seleitednst start =     co   or;
 s.editlements.editor = thit econs{
        ) tInsertion(endleBracke   ha
    
 ;
    }, 0)      }itor });
  { target: edleInput(   this.hand        ength;
 indent.lewStart + tionEnd = nlecor.se editctionStart =.seleor    edit
        g(newStart);rinvalue.substt + editor. indenrt) +ng(0, newStastrialue.subeditor.vtor.value =     edi        tionStart;
leceditor.setart = ewS   const n         
) => {t((p.setTimeou    this.aptation
    ndenne with iewli n // Insert  
       
          };
    Size)g.editor.tabs.app.confirepeat(thi' '.indent +=      {
        ne))(currentLi.testger && trigggertri  if (    e];
  rentLanguags.state.cur[thiriggersentTr = indrigge  const t
        ;
       }/
       /{\s*$cpp:        ,
     va: /{\s*$/        ja$/,
    s*/{\script:         java
    :\s*$/,: /      python      rs = {
entTriggendonst i   crns
     n patteaiion for certdentatextra in// Add   
        
      : '';[1]  indentMatch ? indentMatchent =  let ind/);
      *)^(\stch(/rrentLine.mah = cuntMatcinde     const on
   tatidenlate in    // Calcu
         h - 1];
   ngtines.le[lLine = linesonst current  c    ');
  split('\ntart).ng(0, slue.substriitor.vanes = ed  const li      rt;
lectionSta.se= editorrt    const stator;
     ements.edi= this.elst editor    con
     ey(e) {andleEnterK    
    h    }
editor });
: targetput({ ndleIn    this.ha
       ze;
     editor.tabSionfig.pp.crt + this.aionEnd = staelect editor.sctionStart =leitor.seed    nd);
    ng(ealue.substrior.v edit) + spaces +ing(0, startvalue.substr= editor.alue tor.v  edi       

       bSize);itor.ta.ednfigcoapp.(this. '.repeataces = '    const sp
    nEnd;tioelec= editor.s  const end 
      nStart;tor.selectio = edionst start;
        cts.editor.elemenhiseditor = t     const ) {
   Tab(insert    
      }
    }
  }
              ak;
          bre        
      }                  etCode();
.res       this                t();
 ulventDefa.pre         e             tKey) {
  e.shif        if (      ':
           case 'r           
     break;           
           }          
   tCode();ubmis.s     thi                  efault();
 tD e.preven              {
         ) tKeyshifif (e.                   ter':
     case 'En               break;
        
         de();eCo.sav   this             t();
    ventDefaul  e.pre                  ase 's':
       c        ey) {
 itch (e.k     sw {
       e.metaKey)lKey || f (e.ctr        i      
       }
urn;
   et         ror) {
   lements.editthis.ement !== Eleveused && acti(isInputFocf         i        

.tagName);eElementudes(activECT'].inclTAREA', 'SELPUT', 'TEX && ['INeElement= activnputFocused isInst      coment;
   tiveElent.acmeocuElement = dst active        coned
 is focus other input nofocused oris editor n tcuts whe shornly handle O      // {
  e)n(lKeyDowndleGloba  
    ha
    }
  }       
 rtion(e);seeBracketInthis.handl          ey)) {
  udes(e.kincl"', "'"]. '{', '[','(', '  if ([
      chingket mat     // Brac
   
          }  );
    ey(edleEnterK   this.han     
     'Enter') {key ===e.        if (ndentation
   // Auto-i  
          
     }n;
          retur    ();
  tTabs.inser    thi       
 ntDefault();preve      e.') {
       'Tabkey ===e.   if (
     ab handling// T       ) {
 yDown(e    handleKe  }
    
      }
  
  target);CodeInput(e.idatealvalidator.v           ) {
 validator    if (
    lidator');dule('vaapp.getMoator = this.lid  const va   
   r moduleh validatohrougn tior validatge    // Trig     
    ue;
   isDirty = trstate.is.   th
     eInput(e) {handl    
     }
    });
   (e);
    lKeyDownGlobalehand this.        {
   e) => keydown', (t, 'er(documenentListenEvs.app.addhi  tcuts
      rtrd shoboa/ Key       /        
   });

               }alue;
   n e.returnV    retur          
  ;leave?'to want u sure you yo. Are geschanve unsaved = 'You hae .returnValu   e             t();
reventDefaul    e.p           ty) {
 isDirte.s.sta if (thi          {
  oad', (e) =>unlforedow, 'beer(winEventListenaddhis.app.    tvents
    Window e //      
  }
        
         });           ;
tCode()resethis.          t();
      ventDefaul    e.pre        > {
    ) =k', (en, 'clictotButnts.reseelemeis.(thstener.addEventLithis.app       n) {
     esetButtos.elements.rif (thi        on
 Reset butt//                
 }

               });alue);
    arget.v.tage(engueLachang   this.             ) => {
, (ege'chanect, 'uageSelements.langs.eltener(thiisentLddEv.a    this.app        {
 ct)geSelelanguaelements.if (this.n
        ge selectioangua      // L        
       });
r(e);
   Bluandlethis.h      {
        (e) =>'blur',nts.editor, lemeener(this.eddEventListpp.a    this.a   
        
 ;})
        ocus(e);eF this.handl        => {
    focus', (e).editor, 's.elementsner(thiistep.addEventL   this.ap      
    });
    
       (e);yDownandleKe      this.h {
      ', (e) =>'keydownts.editor, menner(this.eleisteaddEventLpp.    this.a     
    
     }););
      t(ehandleInpu  this.
           (e) => {'input',, itorents.edems.elr(thisteneddEventLip.as.ap   this
     eventinput   // Editor        {
steners()pEventLitu se
        };
    }

       ')eset-buttone, .rodt-cseor('#rectquerySele document.esetButton:       r   "]'),
  ype="submiton[ttor('butterySelecent.quocumitButton: dubm      s'),
      "language"]=t[namelect, selecseguage-tor('#lanySelecnt.querect: documeSelnguage     la),
       ode"]'="cxtarea[namee-editor, te .cod-editor,or('#codeelectrySument.queor: docedit          n {
       returts() {
      getElemen   
  }
 ized');
   ialinitmodule ditor fo', '✅ Einis.app.log('    th     
     ty();
  pAccessibilis.setuhi     te();
   avedCod  this.loadS();
      oSaveis.setupAut   th();
     enersstupEventLiset     this.     
         }
   
      return;    
    not found'); element itorde ed('warn', 'Cois.app.log      th     
  {r)ments.editohis.ele(!t  if      
 ();ents.getElem = thisents  this.elem  
    nit() {
    i}
      nit();
    this.i   
      
             };    }
};`
rn {};
   retuet) {
     argt tms, in& nuor<int>ion(vectint> solutor<  vect */
  t
    targem to hat sues tf indicctor o* @return Vesum
     get Target  tarram@pa   * ntegers
  ctor of iam nums Ve * @par
    
     * lution hereour so
     * Y  /**public:
  {
ion s Soluttd;

clasespace samor>
using nnclude <vect: `#i    cpp       
}`,
     } int[]{};
ewturn n        re{
) argetms, int t[] nun(intolutiot[] s in
    public*/
     to targett sum dices tharay of inurn Arret   * @
   Target sumrget ta  * @paramtegers
   y of inrra nums Aparam * @ * 
    n here
    utior sol    * You  /**
 
  n {tioclass Soluva: `public        ja     n [];
}`,
ur ret */
   get
    to tar sum ces thatindif ay oArr]} {number[eturns      * @r
- Target sumarget mber} t @param {nu
     * integersray of Ar nums -r[]}m {numbe * @para      * 
 ion here
  olut * Your s   /**
    ) {
 , targeton(numsoluti`function sipt: vascr   ja,
          pass`"""
    
   getto tar sum es thatic indof    List ns:
     
    Returm
   get suTar:       target  gers
f intet oms: Lisnu  rgs:
          A
    
rehe solution  Your   ""

    "t):nums, targeution( solthon: `defpy            lates = {
 this.temp
              
     };
    nulled: lastSav        alse,
    irty: f      isD',
      honytguage: 'pntLanreur   c
         