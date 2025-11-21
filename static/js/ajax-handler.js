/**
 * Enhanced AJAX Handler for CodeXam Platform
 * Provides robust AJAX functionality with comprehensive error handling,
 * retry logic, loading states, and user feedback.
 * 
 * @version 2.0.0
 * @author CodeXam Development Team
 */

class CodeXamAjax {
    constructor(options = {}) {
        this.config = {
            baseURL: '',
            timeout: 30000, // 30 seconds
            retryAttempts: 3,
            retryDelay: 1000, // 1 second
            showLoadingStates: true,
            showNotifications: true,
            csrfTokenName: 'csrf_token',
            ...options
        };
        
        this.state = {
            activeRequests: new Map(),
            requestCounter: 0,
            isOnline: navigator.onLine
        };
        
        this.init();
    }
    
    init() {
        this.setupNetworkMonitoring();
        this.setupGlobalErrorHandling();
        console.log('✅ CodeXamAjax initialized');
    }
    
    setupNetworkMonitoring() {
        window.addEventListener('online', () => {
            this.state.isOnline = true;
            this.showNotification('Connection restored', 'success');
            this.retryFailedRequests();
        });
        
        window.addEventListener('offline', () => {
            this.state.isOnline = false;
            this.showNotification('Connection lost. Requests will be retried when connection is restored.', 'warning');
        });
    }
    
    setupGlobalErrorHandling() {
        // Intercept fetch for global error handling
        const originalFetch = window.fetch;
        window.fetch = (...args) => {
            return originalFetch(...args).catch(error => {
                console.error('Global fetch error:', error);
                throw error;
            });
        };
    }
    
    /**
     * Make an AJAX request with comprehensive error handling
     * @param {string} url - Request URL
     * @param {Object} options - Request options
     * @returns {Promise} Request promise
     */
    async request(url, options = {}) {
        const requestId = ++this.state.requestCounter;
        const fullUrl = this.buildURL(url);
        
        const requestOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                ...options.headers
            },
            timeout: this.config.timeout,
            ...options
        };
        
        // Add CSRF token for state-changing requests
        if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(requestOptions.method.toUpperCase())) {
            this.addCSRFToken(requestOptions);
        }
        
        // Show loading state
        if (this.config.showLoadingStates && options.loadingElement) {
            this.showLoadingState(options.loadingElement);
        }
        
        // Track active request
        const controller = new AbortController();
        requestOptions.signal = controller.signal;
        this.state.activeRequests.set(requestId, { controller, url: fullUrl, options: requestOptions });
        
        try {
            const response = await this.executeRequest(fullUrl, requestOptions, requestId);
            return response;
        } catch (error) {
            throw error;
        } finally {
            // Cleanup
            this.state.activeRequests.delete(requestId);
            if (this.config.showLoadingStates && options.loadingElement) {
                this.hideLoadingState(options.loadingElement);
            }
        }
    }
    
    async executeRequest(url, options, requestId, attempt = 1) {
        try {
            // Check network status
            if (!this.state.isOnline) {
                throw new NetworkError('No internet connection');
            }
            
            // Create timeout promise
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new TimeoutError('Request timeout')), this.config.timeout);
            });
            
            // Execute request with timeout
            const response = await Promise.race([
                fetch(url, options),
                timeoutPromise
            ]);
            
            // Handle HTTP errors
            if (!response.ok) {
                throw new HTTPError(`HTTP ${response.status}: ${response.statusText}`, response.status, response);
            }
            
            // Parse response
            const data = await this.parseResponse(response);
            
            // Handle application-level errors
            if (data && data.status === 'error') {
                throw new ApplicationError(data.error?.message || 'Application error', data);
            }
            
            return {
                data,
                response,
                status: response.status,
                headers: response.headers
            };
            
        } catch (error) {
            console.error(`Request failed (attempt ${attempt}/${this.config.retryAttempts}):`, error);
            
            // Determine if we should retry
            if (this.shouldRetry(error, attempt)) {
                await this.delay(this.config.retryDelay * attempt);
                return this.executeRequest(url, options, requestId, attempt + 1);
            }
            
            // Handle different error types
            this.handleError(error, url, options);
            throw error;
        }
    }
    
    shouldRetry(error, attempt) {
        if (attempt >= this.config.retryAttempts) return false;
        
        // Retry on network errors, timeouts, and certain HTTP errors
        return (
            error instanceof NetworkError ||
            error instanceof TimeoutError ||
            (error instanceof HTTPError && [408, 429, 500, 502, 503, 504].includes(error.status))
        );
    }
    
    async parseResponse(response) {
        const contentType = response.headers.get('content-type');
        
        if (contentType?.includes('application/json')) {
            return await response.json();
        } else if (contentType?.includes('text/')) {
            return await response.text();
        } else {
            return await response.blob();
        }
    }
    
    handleError(error, url, options) {
        let message = 'An unexpected error occurred';
        let type = 'error';
        
        if (error instanceof NetworkError) {
            message = 'Network connection error. Please check your internet connection.';
        } else if (error instanceof TimeoutError) {
            message = 'Request timed out. Please try again.';
        } else if (error instanceof HTTPError) {
            switch (error.status) {
                case 400:
                    message = 'Invalid request. Please check your input.';
                    break;
                case 401:
                    message = 'Authentication required. Please log in.';
                    break;
                case 403:
                    message = 'Access denied. You do not have permission to perform this action.';
                    break;
                case 404:
                    message = 'The requested resource was not found.';
                    break;
                case 429:
                    message = 'Too many requests. Please wait before trying again.';
                    break;
                case 500:
                    message = 'Server error. Please try again later.';
                    break;
                default:
                    message = `Server error (${error.status}). Please try again.`;
            }
        } else if (error instanceof ApplicationError) {
            message = error.message;
        }
        
        if (this.config.showNotifications) {
            this.showNotification(message, type);
        }
        
        // Log detailed error information
        console.error('AJAX Error Details:', {
            url,
            error: error.message,
            stack: error.stack,
            options
        });
    }
    
    buildURL(url) {
        if (url.startsWith('http://') || url.startsWith('https://')) {
            return url;
        }
        
        const baseURL = this.config.baseURL || window.location.origin;
        return `${baseURL}${url.startsWith('/') ? '' : '/'}${url}`;
    }
    
    addCSRFToken(options) {
        const token = this.getCSRFToken();
        if (!token) return;
        
        if (options.body instanceof FormData) {
            options.body.append(this.config.csrfTokenName, token);
        } else if (options.headers['Content-Type']?.includes('application/json')) {
            const body = options.body ? JSON.parse(options.body) : {};
            body[this.config.csrfTokenName] = token;
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
        } else {
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'loading-overlay';
            loadingDiv.innerHTML = `
                <div class="loading-content">
                    <span class="loading-spinner" aria-hidden="true"></span>
                    <span>Loading...</span>
                </div>
            `;
            element.appendChild(loadingDiv);
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
        } else {
            const loadingOverlay = element.querySelector('.loading-overlay');
            if (loadingOverlay) {
                loadingOverlay.remove();
            }
        }
        
        delete element.dataset.originalContent;
    }
    
    showNotification(message, type = 'info') {
        // Use existing notification system or create one
        if (typeof showAlert === 'function') {
            showAlert(message, type);
        } else {
            this.createNotification(message, type);
        }
    }
    
    createNotification(message, type) {
        // Create notification container if it doesn't exist
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            container.setAttribute('aria-live', 'polite');
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
            <span class="notification-icon" aria-hidden="true">${icons[type] || icons.info}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" aria-label="Close notification">×</button>
        `;
        
        // Add to container
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        
        // Manual close
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
        
        // Animate in
        requestAnimationFrame(() => {
            notification.classList.add('notification-show');
        });
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    retryFailedRequests() {
        // This would retry requests that failed due to network issues
        // Implementation depends on specific requirements
        console.log('Retrying failed requests...');
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
            // Remove Content-Type header to let browser set it with boundary
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
    
    async put(url, data, options = {}) {
        return this.post(url, data, { ...options, method: 'PUT' });
    }
    
    async patch(url, data, options = {}) {
        return this.post(url, data, { ...options, method: 'PATCH' });
    }
    
    async delete(url, options = {}) {
        return this.request(url, { ...options, method: 'DELETE' });
    }
    
    // Form submission helper
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
    
    // Cancel all active requests
    cancelAllRequests() {
        this.state.activeRequests.forEach(({ controller }) => {
            controller.abort();
        });
        this.state.activeRequests.clear();
    }
    
    // Cancel specific request
    cancelRequest(requestId) {
        const request = this.state.activeRequests.get(requestId);
        if (request) {
            request.controller.abort();
            this.state.activeRequests.delete(requestId);
        }
    }
    
    // Get active request count
    getActiveRequestCount() {
        return this.state.activeRequests.size;
    }
}

// Custom error classes
class NetworkError extends Error {
    constructor(message) {
        super(message);
        this.name = 'NetworkError';
    }
}

class TimeoutError extends Error {
    constructor(message) {
        super(message);
        this.name = 'TimeoutError';
    }
}

class HTTPError extends Error {
    constructor(message, status, response) {
        super(message);
        this.name = 'HTTPError';
        this.status = status;
        this.response = response;
    }
}

class ApplicationError extends Error {
    constructor(message, data) {
        super(message);
        this.name = 'ApplicationError';
        this.data = data;
    }
}

// Global instance
const codexamAjax = new CodeXamAjax();

// Global convenience functions
window.ajax = {
    get: (url, options) => codexamAjax.get(url, options),
    post: (url, data, options) => codexamAjax.post(url, data, options),
    put: (url, data, options) => codexamAjax.put(url, data, options),
    patch: (url, data, options) => codexamAjax.patch(url, data, options),
    delete: (url, options) => codexamAjax.delete(url, options),
    submitForm: (form, options) => codexamAjax.submitForm(form, options),
    request: (url, options) => codexamAjax.request(url, options)
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CodeXamAjax, NetworkError, TimeoutError, HTTPError, ApplicationError };
}

console.log('✅ CodeXamAjax loaded successfully');